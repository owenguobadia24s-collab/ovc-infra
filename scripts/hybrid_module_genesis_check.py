#!/usr/bin/env python3
"""
Deterministic GENESIS ↔ Hybrid Module carve consistency check.

- Reads GENESIS_LEDGER.tsv (tab-separated, header required).
- Optionally verifies each GENESIS path is tracked now via `git ls-files --error-unmatch`.
- Classifies each path using ordered module include/exclude globs (gitignore-like simplified glob).
- Writes deterministic reports:
  - artifacts/hybrid_genesis_check/SUMMARY.md
  - artifacts/hybrid_genesis_check/UNMATCHED_TOP_ROOTS.md
  - artifacts/hybrid_genesis_check/CONFLICTS.md
  - artifacts/hybrid_genesis_check/NOT_TRACKED_NOW.md (if any)
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# ----------------------------
# Config: module order (first-match-wins)
# ----------------------------
MODULE_ORDER: List[str] = [
    "MOD-A",
    "MOD-B",
    "MOD-C",
    "MOD-D",
    "MOD-GOV",
    "MOD-RUNOPS",
    "MOD-AUDIT",
    "MOD-CHANGE",
    "MOD-UI",
    "MOD-UTIL",
    "MOD-UNASSIGNED",
]


@dataclass(frozen=True)
class ModuleRules:
    module_id: str
    includes: List[str]
    excludes: List[str]


# ----------------------------
# IMPORTANT:
# Put your carve rules here OR load from a JSON file.
# For maximum determinism + reuse, I recommend loading from JSON.
# ----------------------------

def load_rules_from_json(path: Path) -> Dict[str, ModuleRules]:
    import json
    raw = json.loads(path.read_text(encoding="utf-8"))
    rules: Dict[str, ModuleRules] = {}
    for m in raw["modules"]:
        rules[m["module_id"]] = ModuleRules(
            module_id=m["module_id"],
            includes=list(m.get("includes", [])),
            excludes=list(m.get("excludes", [])),
        )
    return rules


# Fallback: minimal rules for sanity check (REPLACE with your full spec)
def minimal_rules() -> Dict[str, ModuleRules]:
    return {
        "MOD-AUDIT": ModuleRules(
            "MOD-AUDIT",
            includes=[".codex/CHECKS/**", ".codex/PROMPTS/**", "scripts/repo_cartographer/**"],
            excludes=[".codex/_scratch/**", "_archive/**"],
        ),
        "MOD-UNASSIGNED": ModuleRules("MOD-UNASSIGNED", includes=["**"], excludes=[]),
    }


# ----------------------------
# Glob matching (repo-root relative)
# We implement a deterministic subset:
# - patterns like "dir/**" match any file under dir/
# - patterns without ** use fnmatch
# ----------------------------

def match_glob(path: str, pattern: str) -> bool:
    # normalize
    p = path.lstrip("./")
    pat = pattern.lstrip("./")

    # Handle dir/** explicitly
    if pat.endswith("/**"):
        prefix = pat[:-3]
        return p == prefix or p.startswith(prefix + "/")

    # Handle ** in the middle (best-effort, deterministic via fnmatch)
    # fnmatch supports * and ?; it does not natively support ** semantics,
    # but in practice "**" behaves like "*" which is acceptable here if your
    # patterns are mostly "dir/**". Keep patterns simple.
    return fnmatch.fnmatch(p, pat)


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(match_glob(path, pat) for pat in patterns)


# ----------------------------
# Git tracked-now verification
# ----------------------------

def git_ls_files_error_unmatch(paths: List[str], repo_root: Path) -> Tuple[List[str], List[str]]:
    """
    Returns (tracked_now, not_tracked_now) lists.
    Calls git once per batch for determinism + speed.
    """
    tracked: List[str] = []
    not_tracked: List[str] = []

    # We must check each path individually to preserve exact failure info.
    # (git can check multiple, but error handling gets messy cross-platform)
    for p in paths:
        try:
            subprocess.run(
                ["git", "-c", "core.quotePath=false", "ls-files", "--error-unmatch", p],
                cwd=str(repo_root),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            tracked.append(p)
        except subprocess.CalledProcessError:
            not_tracked.append(p)

    return tracked, not_tracked


# ----------------------------
# Classification
# ----------------------------

def classify_path(path: str, rules: Dict[str, ModuleRules]) -> Tuple[Optional[str], List[str]]:
    """
    Returns (assigned_module, all_matching_modules).
    Matching module: matches include AND does NOT match exclude.
    Assignment: first-match-wins based on MODULE_ORDER.
    """
    matches: List[str] = []
    for mid in MODULE_ORDER:
        r = rules.get(mid)
        if r is None:
            continue
        if matches_any(path, r.includes) and not matches_any(path, r.excludes):
            matches.append(mid)

    if not matches:
        return None, []

    for mid in MODULE_ORDER:
        if mid in matches:
            return mid, matches

    # Should never happen if MODULE_ORDER covers all module IDs
    return matches[0], matches


def top_level_root(path: str) -> str:
    p = path.lstrip("./")
    if "/" not in p:
        return p
    return p.split("/", 1)[0]


# ----------------------------
# Reports
# ----------------------------

def write_lines(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genesis", default="GENESIS_LEDGER.tsv", help="Path to GENESIS_LEDGER.tsv")
    ap.add_argument("--repo-root", default=".", help="Repo root (where .git lives)")
    ap.add_argument("--rules-json", default="", help="Optional JSON rules file (recommended)")
    ap.add_argument("--outdir", default="artifacts/hybrid_genesis_check", help="Output directory")
    ap.add_argument("--skip-git-check", action="store_true", help="Skip tracked-now verification")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    genesis_path = Path(args.genesis).resolve()
    outdir = Path(args.outdir).resolve()

    if args.rules_json:
        rules = load_rules_from_json(Path(args.rules_json).resolve())
    else:
        rules = minimal_rules()

    # Preflight: ensure module rules exist for all MODULE_ORDER IDs you intend to use
    missing_rule_ids = [m for m in MODULE_ORDER if m not in rules]
    if missing_rule_ids:
        # Fail-closed: you can choose to allow MOD-UNASSIGNED-only runs,
        # but for real enforcement you want full rule coverage.
        raise SystemExit(f"FAIL-CLOSED: Missing rules for module IDs: {missing_rule_ids}")

    # Read genesis
    rows: List[Dict[str, str]] = []
    with genesis_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = {"path", "genesis_commit", "genesis_author_date", "genesis_subject"}
        if set(reader.fieldnames or []) != required:
            raise SystemExit(f"FAIL-CLOSED: Unexpected header: {reader.fieldnames} (expected {sorted(required)})")
        for row in reader:
            rows.append(row)

    genesis_paths = [r["path"].strip() for r in rows]
    if any(not p for p in genesis_paths):
        raise SystemExit("FAIL-CLOSED: Empty path row detected in GENESIS_LEDGER.tsv")

    tracked_now = genesis_paths
    not_tracked_now: List[str] = []
    if not args.skip_git_check:
        tracked_now, not_tracked_now = git_ls_files_error_unmatch(genesis_paths, repo_root)

    # Classify
    assigned: Dict[str, List[str]] = {m: [] for m in MODULE_ORDER}
    residual: List[str] = []
    conflicts: List[Tuple[str, List[str]]] = []

    for p in tracked_now:
        assigned_mod, matches = classify_path(p, rules)
        if assigned_mod is None:
            residual.append(p)
        else:
            assigned[assigned_mod].append(p)
            if len(matches) > 1:
                conflicts.append((p, matches))

    # Summaries
    total = len(genesis_paths)
    tracked_n = len(tracked_now)
    not_tracked_n = len(not_tracked_now)
    residual_n = len(residual)
    conflict_n = len(conflicts)

    # Unmatched roots
    residual_roots: Dict[str, int] = {}
    for p in residual:
        r = top_level_root(p)
        residual_roots[r] = residual_roots.get(r, 0) + 1
    residual_roots_sorted = sorted(residual_roots.items(), key=lambda x: (-x[1], x[0]))

    # Write reports
    summary_lines = [
        "# GENESIS ↔ HYBRID MODULE CARVE CHECK (Deterministic)",
        "",
        f"- Total genesis rows: {total}",
        f"- Tracked-now rows: {tracked_n}",
        f"- Not-tracked-now rows: {not_tracked_n}",
        f"- Residual (matched none): {residual_n}",
        f"- Conflicts (multi-match): {conflict_n}",
        "",
        "## Assigned counts by module",
    ]
    for m in MODULE_ORDER:
        summary_lines.append(f"- {m}: {len(assigned[m])}")

    write_lines(outdir / "SUMMARY.md", summary_lines)

    # Unmatched top roots
    unmatched_lines = ["# UNMATCHED TOP-LEVEL ROOTS (Residual)", ""]
    if residual_roots_sorted:
        for root, cnt in residual_roots_sorted:
            unmatched_lines.append(f"- {root}/ — {cnt} paths")
    else:
        unmatched_lines.append("- (none)")
    write_lines(outdir / "UNMATCHED_TOP_ROOTS.md", unmatched_lines)

    # Conflicts
    conflict_lines = ["# CONFLICTS (Paths matching >1 module)", ""]
    if conflicts:
        for p, ms in sorted(conflicts, key=lambda x: x[0]):
            conflict_lines.append(f"- {p}  :: matches={', '.join(ms)}")
    else:
        conflict_lines.append("- (none)")
    write_lines(outdir / "CONFLICTS.md", conflict_lines)

    # Not tracked now
    not_tracked_lines = ["# NOT TRACKED NOW (GENESIS paths missing from current index)", ""]
    if not_tracked_now:
        for p in sorted(not_tracked_now):
            not_tracked_lines.append(f"- {p}")
    else:
        not_tracked_lines.append("- (none)")
    write_lines(outdir / "NOT_TRACKED_NOW.md", not_tracked_lines)

    # Deterministic console summary block (optional)
    print(f"Total genesis rows: {total}")
    print(f"Tracked-now rows: {tracked_n}")
    print(f"Not-tracked-now rows: {not_tracked_n}")
    print(f"Residual (matched none): {residual_n}")
    print(f"Conflicts (multi-match): {conflict_n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())