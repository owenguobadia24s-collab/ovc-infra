#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations
from pathlib import Path
from typing import Any


UNRESOLVED_INPUT_FILE_MISSING = "INPUT_FILE_MISSING"
UNRESOLVED_INPUT_JSON_INVALID = "INPUT_JSON_INVALID"
UNRESOLVED_COMMIT_HASH_INVALID = "COMMIT_HASH_MISSING_OR_INVALID"
UNRESOLVED_EPOCH_COERCION_REQUIRED_STRICT = "EPOCH_COERCION_REQUIRED_STRICT"
UNRESOLVED_EPOCH_BOUNDARY_SHA_NOT_FOUND = "EPOCH_BOUNDARY_SHA_NOT_FOUND"
UNRESOLVED_EPOCH_BOUNDARY_REVERSED = "EPOCH_BOUNDARY_REVERSED"

TOP_SUBJECT_PHRASES_N = 10
RULE_THRESHOLD = Decimal("0.40")
CLUSTER_K = 3


@dataclass(frozen=True)
class LedgerCommit:
    idx: int
    sha: str
    subject: str
    dir_keys: frozenset[str]
    tag_keys: frozenset[str]


@dataclass(frozen=True)
class Candidate:
    rule: str
    key: str
    support_count: int
    earliest_match_idx: int
    match_indices: tuple[int, ...]
    cluster_nodes: tuple[str, ...] = ()
    cluster_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class EpochOutcome:
    epoch_id: str
    commit_count: int
    status: str
    unresolved_reason: str | None
    boundary_source: str | None
    start_idx: int | None
    end_idx: int | None
    candidates: tuple[Candidate, ...]
    dir_counts: Counter
    tag_counts: Counter
    subject_unigrams: Counter
    subject_bigrams: Counter
    slice_commits: tuple[LedgerCommit, ...]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Module Candidates v0.1 (deterministic evidence-only).")
    parser.add_argument(
        "--ledger",
        default="docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl",
        help="Path to DEV change ledger JSONL.",
    )
    parser.add_argument(
        "--macro-epochs",
        default="docs/catalogs/epoch_ranges.macro.v0.1.json",
        help="Path to macro epoch ranges JSON.",
    )
    parser.add_argument(
        "--micro-epochs",
        default="docs/catalogs/epoch_ranges.micro.v0.1.json",
        help="Path to micro epoch ranges JSON.",
    )
    parser.add_argument(
        "--micro-labels",
        default="docs/catalogs/micro_epoch_labels.v0.1.json",
        help="Path to optional micro epoch labels JSON.",
    )
    parser.add_argument(
        "--out",
        default="docs/baselines/MODULE_CANDIDATES_v0.1.md",
        help="Output markdown path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="If set, any required epoch field coercion marks epoch UNRESOLVED.",
    )
    return parser.parse_args(argv)


def write_text_utf8_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def format_pct(count: int, denom: int) -> str:
    if denom <= 0:
        return "0.00%"
    pct = (Decimal(count) * Decimal("100")) / Decimal(denom)
    pct = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{pct:.2f}%"


def looks_like_sha(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{7,40}", value))


def normalize_prefix(raw_path: Any) -> tuple[str, str]:
    path = str(raw_path).replace("\\", "/")
    if path in {"", ".", "/", "./"}:
        return "./", "./"
    while path.startswith("./"):
        path = path[2:]
    if path in {"", ".", "/", "./"}:
        return "./", "./"
    segments = [segment for segment in path.split("/") if segment]
    if not segments:
        return "./", "./"
    if len(segments) == 1:
        display = segments[0]
    else:
        display = f"{segments[0]}/{segments[1]}"
    return display.lower(), display


def normalize_tag(raw_tag: Any) -> tuple[str, str] | None:
    display = str(raw_tag).strip()
    if not display:
        return None
    return display.lower(), display


def tokenize_subject(subject: str) -> tuple[list[str], list[str]]:
    tokens = [token for token in re.split(r"[^a-z0-9]+", subject.lower()) if len(token) >= 3]
    bigrams = [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]
    return tokens, bigrams


def read_json_array(path: Path) -> list[Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {path.as_posix()}") from exc
    if not isinstance(payload, list):
        raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {path.as_posix()}")
    return payload


def build_ledger(
    ledger_path: Path,
) -> tuple[list[LedgerCommit], dict[str, int], dict[str, str], dict[str, str], set[int]]:
    commits: list[LedgerCommit] = []
    sha_to_first_idx: dict[str, int] = {}
    dir_display: dict[str, str] = {}
    tag_display: dict[str, str] = {}
    invalid_sha_indices: set[int] = set()

    for idx, raw_line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines()):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {ledger_path.as_posix()}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {ledger_path.as_posix()}")
        if not isinstance(payload.get("subject"), str):
            raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {ledger_path.as_posix()}")
        if not isinstance(payload.get("directories_touched"), list):
            raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {ledger_path.as_posix()}")
        if not isinstance(payload.get("tags"), list):
            raise ValueError(f"{UNRESOLVED_INPUT_JSON_INVALID}: {ledger_path.as_posix()}")

        commit_field = payload.get("commit")
        sha = ""
        if isinstance(commit_field, str):
            sha = commit_field
        elif isinstance(commit_field, dict):
            commit_hash = commit_field.get("hash")
            if isinstance(commit_hash, str):
                sha = commit_hash
        sha = sha.strip().lower()
        if not looks_like_sha(sha):
            invalid_sha_indices.add(idx)

        dir_set: set[str] = set()
        for raw_path in payload["directories_touched"]:
            dir_key, display = normalize_prefix(raw_path)
            dir_set.add(dir_key)
            current = dir_display.get(dir_key)
            if current is None or display < current:
                dir_display[dir_key] = display

        tag_set: set[str] = set()
        for raw_tag in payload["tags"]:
            normalized = normalize_tag(raw_tag)
            if normalized is None:
                continue
            tag_key, display = normalized
            tag_set.add(tag_key)
            current = tag_display.get(tag_key)
            if current is None or display < current:
                tag_display[tag_key] = display

        commit = LedgerCommit(
            idx=idx,
            sha=sha,
            subject=payload["subject"],
            dir_keys=frozenset(dir_set),
            tag_keys=frozenset(tag_set),
        )
        commits.append(commit)
        if looks_like_sha(sha) and sha not in sha_to_first_idx:
            sha_to_first_idx[sha] = idx

    return commits, sha_to_first_idx, dir_display, tag_display, invalid_sha_indices


def resolve_epoch_boundary(entry: dict[str, Any]) -> tuple[str, str, str, bool]:
    coerced = False

    if "epoch_id" in entry and entry["epoch_id"] is not None:
        epoch_id = str(entry["epoch_id"])
    elif "macro_epoch" in entry and entry["macro_epoch"] is not None:
        epoch_id = str(entry["macro_epoch"])
        coerced = True
    else:
        epoch_id = "UNSPECIFIED_EPOCH"
        coerced = True

    if "range_start" in entry and entry["range_start"] is not None:
        range_start = str(entry["range_start"]).strip().lower()
    elif "start_hash" in entry and entry["start_hash"] is not None:
        range_start = str(entry["start_hash"]).strip().lower()
        coerced = True
    else:
        range_start = ""

    if "range_end" in entry and entry["range_end"] is not None:
        range_end = str(entry["range_end"]).strip().lower()
    elif "end_hash" in entry and entry["end_hash"] is not None:
        range_end = str(entry["end_hash"]).strip().lower()
        coerced = True
    else:
        range_end = ""

    boundary_source = "coerced(start_hash/end_hash)" if coerced else "canonical(range_start/range_end)"
    return epoch_id, range_start, range_end, coerced


def connected_components(nodes: set[str], edges: set[tuple[str, str]]) -> list[tuple[str, ...]]:
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    components: list[tuple[str, ...]] = []
    visited: set[str] = set()
    for start in sorted(nodes):
        if start in visited:
            continue
        stack = [start]
        component: list[str] = []
        visited.add(start)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        has_edge = any(adjacency[node] for node in component)
        if has_edge and len(component) >= 2:
            components.append(tuple(sorted(component)))
    return components


def build_epoch_outcomes(
    ledger_commits: list[LedgerCommit],
    sha_to_first_idx: dict[str, int],
    invalid_sha_indices: set[int],
    macro_epochs: list[Any],
    strict: bool,
) -> list[EpochOutcome]:
    outcomes: list[EpochOutcome] = []

    idx_to_commit = {commit.idx: commit for commit in ledger_commits}

    for raw_epoch in macro_epochs:
        if not isinstance(raw_epoch, dict):
            raise ValueError(UNRESOLVED_INPUT_JSON_INVALID)

        epoch_id, range_start, range_end, coerced = resolve_epoch_boundary(raw_epoch)
        boundary_source = "coerced(start_hash/end_hash)" if coerced else None

        unresolved_reason: str | None = None
        start_idx: int | None = None
        end_idx: int | None = None
        slice_commits: tuple[LedgerCommit, ...] = ()
        dir_counts: Counter = Counter()
        tag_counts: Counter = Counter()
        subject_unigrams: Counter = Counter()
        subject_bigrams: Counter = Counter()
        candidates: tuple[Candidate, ...] = ()

        if unresolved_reason is None and strict and coerced:
            unresolved_reason = UNRESOLVED_EPOCH_COERCION_REQUIRED_STRICT

        if unresolved_reason is None:
            if range_start not in sha_to_first_idx or range_end not in sha_to_first_idx:
                unresolved_reason = UNRESOLVED_EPOCH_BOUNDARY_SHA_NOT_FOUND
            else:
                start_idx = sha_to_first_idx[range_start]
                end_idx = sha_to_first_idx[range_end]
                if start_idx > end_idx:
                    unresolved_reason = UNRESOLVED_EPOCH_BOUNDARY_REVERSED
                elif any(idx in invalid_sha_indices for idx in range(start_idx, end_idx + 1)):
                    unresolved_reason = UNRESOLVED_COMMIT_HASH_INVALID

        if unresolved_reason is None and start_idx is not None and end_idx is not None:
            epoch_commits: list[LedgerCommit] = []
            for idx in range(start_idx, end_idx + 1):
                commit = idx_to_commit.get(idx)
                if commit is not None:
                    epoch_commits.append(commit)
            slice_commits = tuple(epoch_commits)

            for commit in slice_commits:
                dir_counts.update(commit.dir_keys)
                tag_counts.update(commit.tag_keys)
                unigram_tokens, bigram_tokens = tokenize_subject(commit.subject)
                subject_unigrams.update(unigram_tokens)
                subject_bigrams.update(bigram_tokens)

            n_epoch = len(slice_commits)
            if n_epoch > 0:
                rule_candidates: list[Candidate] = []

                for dir_key, count in sorted(dir_counts.items(), key=lambda item: (-item[1], item[0])):
                    if (Decimal(count) / Decimal(n_epoch)) >= RULE_THRESHOLD:
                        match_indices = tuple(commit.idx for commit in slice_commits if dir_key in commit.dir_keys)
                        rule_candidates.append(
                            Candidate(
                                rule="A",
                                key=f"DIR:{dir_key}",
                                support_count=len(match_indices),
                                earliest_match_idx=min(match_indices),
                                match_indices=match_indices,
                            )
                        )

                for tag_key, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0])):
                    if (Decimal(count) / Decimal(n_epoch)) >= RULE_THRESHOLD:
                        match_indices = tuple(commit.idx for commit in slice_commits if tag_key in commit.tag_keys)
                        rule_candidates.append(
                            Candidate(
                                rule="B",
                                key=f"TAG:{tag_key}",
                                support_count=len(match_indices),
                                earliest_match_idx=min(match_indices),
                                match_indices=match_indices,
                            )
                        )

                pair_counts: Counter = Counter()
                nodes: set[str] = set()
                for commit in slice_commits:
                    basket = set(commit.dir_keys)
                    nodes.update(basket)
                    ordered = sorted(basket)
                    for left, right in combinations(ordered, 2):
                        pair_counts[(left, right)] += 1

                graph_edges = {
                    pair for pair, count in pair_counts.items() if count >= CLUSTER_K
                }
                for component_nodes in connected_components(nodes, graph_edges):
                    component_node_set = set(component_nodes)
                    component_edges = {
                        pair
                        for pair in graph_edges
                        if pair[0] in component_node_set and pair[1] in component_node_set
                    }
                    if not component_edges:
                        continue
                    match_indices_list: list[int] = []
                    for commit in slice_commits:
                        basket = set(commit.dir_keys)
                        matched = any(left in basket and right in basket for left, right in component_edges)
                        if matched:
                            match_indices_list.append(commit.idx)
                    if not match_indices_list:
                        continue
                    cluster_key = "CLUSTER:" + "|".join(component_nodes)
                    rule_candidates.append(
                        Candidate(
                            rule="C",
                            key=cluster_key,
                            support_count=len(match_indices_list),
                            earliest_match_idx=min(match_indices_list),
                            match_indices=tuple(match_indices_list),
                            cluster_nodes=component_nodes,
                            cluster_edges=tuple(sorted(component_edges)),
                        )
                    )

                dedup: dict[str, Candidate] = {}
                for candidate in rule_candidates:
                    existing = dedup.get(candidate.key)
                    if existing is None:
                        dedup[candidate.key] = candidate
                        continue
                    replacement_needed = False
                    if candidate.support_count > existing.support_count:
                        replacement_needed = True
                    elif candidate.support_count == existing.support_count and candidate.earliest_match_idx < existing.earliest_match_idx:
                        replacement_needed = True
                    if replacement_needed:
                        dedup[candidate.key] = candidate

                sorted_candidates = sorted(
                    dedup.values(),
                    key=lambda candidate: (
                        -candidate.support_count,
                        candidate.key,
                        candidate.earliest_match_idx,
                    ),
                )
                candidates = tuple(sorted_candidates)

        commit_count = len(slice_commits) if unresolved_reason is None else 0
        outcomes.append(
            EpochOutcome(
                epoch_id=epoch_id,
                commit_count=commit_count,
                status="UNRESOLVED" if unresolved_reason else "OK",
                unresolved_reason=unresolved_reason,
                boundary_source=boundary_source,
                start_idx=start_idx,
                end_idx=end_idx,
                candidates=candidates,
                dir_counts=dir_counts,
                tag_counts=tag_counts,
                subject_unigrams=subject_unigrams,
                subject_bigrams=subject_bigrams,
                slice_commits=slice_commits,
            )
        )

    return outcomes


def top_count_items(counter: Counter, limit: int = 10) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]


def render_count_table(
    header: tuple[str, str, str],
    rows: list[tuple[str, int]],
    denom: int,
    display_map: dict[str, str],
) -> list[str]:
    out = [
        f"| {header[0]} | {header[1]} | {header[2]} |",
        "| --- | ---: | ---: |",
    ]
    if not rows:
        out.append(f"| — | 0 | {format_pct(0, denom)} |")
        return out
    for key, count in rows:
        display = display_map.get(key, key)
        out.append(f"| {display} | {count} | {format_pct(count, denom)} |")
    return out


def top_phrases_for_candidate(
    subject_unigrams: Counter,
    subject_bigrams: Counter,
) -> list[tuple[str, int]]:
    repeated_bigrams = [(phrase, count) for phrase, count in subject_bigrams.items() if count >= 2]
    if repeated_bigrams:
        pool = repeated_bigrams
    else:
        pool = [(phrase, count) for phrase, count in subject_unigrams.items() if count >= 2]
    pool.sort(key=lambda item: (-item[1], item[0]))
    return pool[:TOP_SUBJECT_PHRASES_N]


def commit_ranges(match_indices: tuple[int, ...], idx_to_sha: dict[int, str]) -> list[str]:
    if not match_indices:
        return []
    ordered = sorted(match_indices)
    ranges: list[tuple[int, int]] = []
    start = ordered[0]
    prev = ordered[0]
    for current in ordered[1:]:
        if current == prev + 1:
            prev = current
            continue
        ranges.append((start, prev))
        start = current
        prev = current
    ranges.append((start, prev))
    return [f"{idx_to_sha[first]}..{idx_to_sha[last]}" for first, last in ranges]


def candidate_match_commit_set(candidate: Candidate) -> set[int]:
    return set(candidate.match_indices)


def build_invariants(
    candidate: Candidate,
    matched_commits: list[LedgerCommit],
    n_epoch: int,
    dir_display: dict[str, str],
) -> list[str]:
    matched_total = len(matched_commits)
    inv_lines: list[str] = []
    inv_lines.append(
        f"INV-01: Candidate matches {matched_total}/{n_epoch} commits. (support: {matched_total}/{n_epoch})"
    )
    if matched_total == 0:
        inv_lines.append("INV-02: No matched commits. (support: 0/0)")
        return inv_lines

    pair_counter: Counter = Counter()
    for commit in matched_commits:
        ordered = sorted(set(commit.dir_keys))
        for left, right in combinations(ordered, 2):
            pair_counter[(left, right)] += 1
    if pair_counter:
        (left, right), count = sorted(pair_counter.items(), key=lambda item: (-item[1], item[0]))[0]
        left_display = dir_display.get(left, left)
        right_display = dir_display.get(right, right)
        inv_lines.append(
            f"INV-02: Directory pair {left_display} + {right_display} co-occurs in {count}/{matched_total} matched commits. (support: {count}/{matched_total})"
        )
        return inv_lines

    dir_counter: Counter = Counter()
    for commit in matched_commits:
        dir_counter.update(commit.dir_keys)
    if dir_counter:
        dir_key, count = sorted(dir_counter.items(), key=lambda item: (-item[1], item[0]))[0]
        dir_display_name = dir_display.get(dir_key, dir_key)
        inv_lines.append(
            f"INV-02: Directory {dir_display_name} appears in {count}/{matched_total} matched commits. (support: {count}/{matched_total})"
        )
    else:
        inv_lines.append("INV-02: No directory evidence in matched commits. (support: 0/0)")
    return inv_lines


def render_report(
    outcomes: list[EpochOutcome],
    ledger_path: Path,
    macro_path: Path,
    micro_path: Path,
    micro_labels_path: Path,
    dir_display: dict[str, str],
    tag_display: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append("# Module Candidates v0.1")
    lines.append("")
    lines.append("## 1. Scope & Canonical Sources")
    lines.append("")
    lines.append(f"- Change Ledger: `{ledger_path.as_posix()}`")
    lines.append(f"- Macro Epoch Ranges: `{macro_path.as_posix()}`")
    lines.append(f"- Micro Epoch Ranges: `{micro_path.as_posix()}`")
    if micro_labels_path.exists():
        lines.append(f"- Micro Epoch Labels: `{micro_labels_path.as_posix()}` (present, optional enrichment only)")
    else:
        lines.append(f"- Micro Epoch Labels: `{micro_labels_path.as_posix()}` (not provided, optional)")
    lines.append("")
    lines.append("## 2. Epoch Summary Table")
    lines.append("")
    lines.append("| Epoch ID | Commit Count | Top Directory | % | Top Tag | % | Status |")
    lines.append("| --- | ---: | --- | ---: | --- | ---: | --- |")
    for outcome in outcomes:
        if outcome.status == "OK":
            top_dir_items = top_count_items(outcome.dir_counts, limit=1)
            if top_dir_items:
                top_dir_key, top_dir_count = top_dir_items[0]
                top_dir_display = dir_display.get(top_dir_key, top_dir_key)
            else:
                top_dir_display, top_dir_count = "—", 0
            top_tag_items = top_count_items(outcome.tag_counts, limit=1)
            if top_tag_items:
                top_tag_key, top_tag_count = top_tag_items[0]
                top_tag_display = tag_display.get(top_tag_key, top_tag_key)
            else:
                top_tag_display, top_tag_count = "—", 0
            lines.append(
                f"| {outcome.epoch_id} | {outcome.commit_count} | {top_dir_display} | {format_pct(top_dir_count, outcome.commit_count)} | {top_tag_display} | {format_pct(top_tag_count, outcome.commit_count)} | {outcome.status} |"
            )
        else:
            lines.append(f"| {outcome.epoch_id} | 0 | — | 0.00% | — | 0.00% | {outcome.status} |")

    lines.append("")
    lines.append("## 3. Module Candidates (Grouped by Epoch)")
    lines.append("")

    idx_to_sha: dict[int, str] = {}
    for outcome in outcomes:
        for commit in outcome.slice_commits:
            idx_to_sha[commit.idx] = commit.sha

    module_rows: list[tuple[str, str, str]] = []
    module_counter = 1

    for outcome in outcomes:
        lines.append(f"### Epoch {outcome.epoch_id}")
        lines.append("")
        if outcome.boundary_source is not None:
            lines.append(f"Epoch Boundary Source: {outcome.boundary_source}")
            lines.append("")
        if outcome.status == "UNRESOLVED":
            lines.append(f"Unresolved Reason: {outcome.unresolved_reason}")
            lines.append("")
            continue

        if not outcome.candidates:
            lines.append("No stable module candidate detected for this epoch.")
            lines.append("")
            continue

        n_epoch = outcome.commit_count
        for candidate in outcome.candidates:
            mod_id = f"MOD-{module_counter:02d}"
            module_counter += 1
            lines.append(f"#### {mod_id} — {candidate.key}")
            lines.append(f"Epoch: {outcome.epoch_id}")
            lines.append("")
            lines.append("Commit Ranges")
            lines.append("")
            ranges = commit_ranges(candidate.match_indices, idx_to_sha)
            if ranges:
                for sha_range in ranges:
                    lines.append(f"- {sha_range}")
            else:
                lines.append("- —")
            lines.append("")

            match_set = candidate_match_commit_set(candidate)
            matched_commits = [commit for commit in outcome.slice_commits if commit.idx in match_set]
            module_dir_counts: Counter = Counter()
            module_tag_counts: Counter = Counter()
            for commit in matched_commits:
                module_dir_counts.update(commit.dir_keys)
                module_tag_counts.update(commit.tag_keys)

            lines.append("Dominant Directories")
            lines.append("")
            lines.extend(
                render_count_table(
                    header=("Directory", "Count", "%"),
                    rows=top_count_items(module_dir_counts, limit=10),
                    denom=n_epoch,
                    display_map=dir_display,
                )
            )
            lines.append("")

            lines.append("Dominant Tags")
            lines.append("")
            lines.extend(
                render_count_table(
                    header=("Tag", "Count", "%"),
                    rows=top_count_items(module_tag_counts, limit=10),
                    denom=n_epoch,
                    display_map=tag_display,
                )
            )
            lines.append("")

            lines.append("Purpose (Evidence-Only)")
            lines.append("")
            lines.append("Repeated subject phrases:")
            phrase_unigrams: Counter = Counter()
            phrase_bigrams: Counter = Counter()
            for commit in matched_commits:
                unigram_tokens, bigram_tokens = tokenize_subject(commit.subject)
                phrase_unigrams.update(unigram_tokens)
                phrase_bigrams.update(bigram_tokens)
            phrases = top_phrases_for_candidate(phrase_unigrams, phrase_bigrams)
            if phrases:
                for phrase, _count in phrases:
                    lines.append(f"- \"{phrase}\"")
            else:
                lines.append("- \"none\"")
            lines.append("Representative paths:")
            rep_paths = [dir_display.get(key, key) for key, _count in top_count_items(module_dir_counts, limit=5)]
            if rep_paths:
                for path_value in rep_paths:
                    lines.append(f"- {path_value}")
            else:
                lines.append("- —")
            lines.append("")

            lines.append("Draft Invariants")
            lines.append("")
            for invariant in build_invariants(candidate, matched_commits, n_epoch, dir_display):
                lines.append(f"- {invariant}")
            lines.append("")

            visual_dirs = ", ".join(rep_paths[:3]) if rep_paths else "—"
            rep_tags = [tag_display.get(key, key) for key, _count in top_count_items(module_tag_counts, limit=3)]
            visual_tags = ", ".join(rep_tags) if rep_tags else "—"
            module_rows.append((mod_id, visual_dirs, visual_tags))

    lines.append("## 4. Visual Summary (Digestible, Not Decorative)")
    lines.append("")
    lines.append("| Module | Directories | Tags |")
    lines.append("| --- | --- | --- |")
    if module_rows:
        for mod_id, dirs_text, tags_text in module_rows:
            lines.append(f"| {mod_id} | {dirs_text} | {tags_text} |")
    else:
        lines.append("| — | — | — |")

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        ledger_path = Path(args.ledger)
        macro_path = Path(args.macro_epochs)
        micro_path = Path(args.micro_epochs)
        micro_labels_path = Path(args.micro_labels)
        out_path = Path(args.out)

        if not ledger_path.exists() or not macro_path.exists() or not micro_path.exists():
            print(f"ERROR: {UNRESOLVED_INPUT_FILE_MISSING}", file=sys.stderr)
            return 1

        try:
            macro_epochs = read_json_array(macro_path)
            _ = read_json_array(micro_path)
        except ValueError as exc:
            if str(exc).startswith(UNRESOLVED_INPUT_JSON_INVALID):
                print(f"ERROR: {UNRESOLVED_INPUT_JSON_INVALID}", file=sys.stderr)
                return 1
            raise

        try:
            ledger_commits, sha_to_first_idx, dir_display, tag_display, invalid_sha_indices = build_ledger(ledger_path)
        except ValueError as exc:
            if str(exc).startswith(UNRESOLVED_INPUT_JSON_INVALID):
                print(f"ERROR: {UNRESOLVED_INPUT_JSON_INVALID}", file=sys.stderr)
                return 1
            raise

        outcomes = build_epoch_outcomes(
            ledger_commits=ledger_commits,
            sha_to_first_idx=sha_to_first_idx,
            invalid_sha_indices=invalid_sha_indices,
            macro_epochs=macro_epochs,
            strict=args.strict,
        )
        markdown = render_report(
            outcomes=outcomes,
            ledger_path=ledger_path,
            macro_path=macro_path,
            micro_path=micro_path,
            micro_labels_path=micro_labels_path,
            dir_display=dir_display,
            tag_display=tag_display,
        )
        write_text_utf8_lf(out_path, markdown)
        return 0
    except Exception as exc:  # pragma: no cover - fatal guardrail
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
