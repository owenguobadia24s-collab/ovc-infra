#!/usr/bin/env python3
"""
Classifier coverage analysis pipeline.
Reads input files, produces all deliverables under .codex/_scratch/.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRATCH = Path(".codex/_scratch")
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}
CLASS_ORDER = ["A", "B", "C", "D", "E", "UNKNOWN"]


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def normalize_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def classify_path_v01(path: str) -> set[str]:
    """Exact replica of v0.1 classify_path from classify_change.py"""
    classes: set[str] = set()
    lower = path.lower()

    if path.startswith("reports/path1/") or path.startswith("sql/path1/"):
        classes.add("A")

    if (
        path.startswith("docs/contracts/")
        or path.startswith("docs/governance/")
        or path.startswith("docs/phase_2_2/")
    ):
        classes.add("B")

    if (
        path.startswith("scripts/")
        or path.startswith("src/")
        or path.startswith("tests/")
        or path.startswith(".github/workflows/")
        or path.startswith(".codex/CHECKS/")
    ):
        classes.add("C")

    # tools non-doc
    if lower.startswith("tools/"):
        suffix = Path(lower).suffix
        is_doc = suffix in DOC_EXTENSIONS
        parts = lower.split("/")
        is_doc = is_doc or ("docs" in parts[1:-1])
        if not is_doc:
            classes.add("C")

    if path.startswith("tools/phase3_control_panel/"):
        classes.add("D")

    if (
        path == ".gitattributes"
        or path == ".gitignore"
        or path.startswith(".github/workflows/")
    ):
        classes.add("E")

    # shim check
    if lower.startswith("tools/"):
        if any("shim" in part for part in lower.split("/") if part):
            classes.add("E")

    if not classes:
        classes.add("UNKNOWN")

    return classes


def load_data():
    with open(SCRATCH / "history_metrics.backfill.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    overlay = []
    with open(SCRATCH / "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                overlay.append(json.loads(line))

    return metrics, overlay


# ============================================================================
# STEP 1
# ============================================================================
def step1_snapshot():
    print("=" * 60)
    print("STEP 1: Snapshot classifier rules")
    print("=" * 60)

    classifier_rules = {
        "version": "0.1",
        "source": "scripts/governance/classify_change.py",
        "class_order": CLASS_ORDER,
        "doc_extensions": sorted(DOC_EXTENSIONS),
        "rules": [
            {
                "class": "A",
                "patterns": ["reports/path1/**", "sql/path1/**"],
                "description": "Path1 evidence runs and SQL",
            },
            {
                "class": "B",
                "patterns": [
                    "docs/contracts/**",
                    "docs/governance/**",
                    "docs/phase_2_2/**",
                ],
                "description": "Governance contracts and phase documentation",
            },
            {
                "class": "C",
                "patterns": [
                    "scripts/**",
                    "src/**",
                    "tests/**",
                    ".github/workflows/**",
                    ".codex/CHECKS/**",
                    "tools/** (excluding pure docs)",
                ],
                "description": "Code, scripts, tests, CI, tools (non-doc)",
            },
            {
                "class": "D",
                "patterns": ["tools/phase3_control_panel/**"],
                "description": "Phase3 control panel",
            },
            {
                "class": "E",
                "patterns": [
                    ".gitattributes",
                    ".gitignore",
                    ".github/workflows/**",
                    "tools/**/shim/**",
                ],
                "description": "Repo config, CI, compat shims",
            },
            {
                "class": "UNKNOWN",
                "patterns": ["(default when no other rule matches)"],
                "description": "Unmapped path patterns",
            },
        ],
        "evaluation_logic": (
            "Each path is tested against all rules independently (set accumulation). "
            "A path can trigger multiple classes. If no class matches, UNKNOWN is added. "
            "Per-commit classification is the union of all per-path classes."
        ),
        "default_behavior": "UNKNOWN when no other pattern matches",
        "special_functions": {
            "is_tools_pure_doc": (
                "tools/ files with doc extensions (.md,.txt,.rst,.adoc) "
                "or containing docs/ in subpath -> excluded from C"
            ),
            "is_tools_compat_shim": "tools/ files with shim in path segment -> triggers E",
        },
    }

    write_json(SCRATCH / "classifier_rules.snapshot.json", classifier_rules)
    print("  -> classifier_rules.snapshot.json written")
    return classifier_rules


# ============================================================================
# STEP 2
# ============================================================================
def step2_isolate_unknowns(metrics, overlay):
    print("=" * 60)
    print("STEP 2: Isolate UNKNOWN commits")
    print("=" * 60)

    commit_index = {c["hash"]: c for c in metrics["commits"]}
    unknown_commits = [r for r in overlay if "UNKNOWN" in r["classes"]]
    unknown_count = len(unknown_commits)

    # INVARIANT
    if unknown_count != 160:
        print(f"  INVARIANT FAIL: expected 160 UNKNOWN, got {unknown_count}")
        sys.exit(1)
    print(f"  INVARIANT PASS: {unknown_count} == 160")

    top_dir_counter = Counter()
    prefix_2_counter = Counter()
    tag_counter = Counter()
    dates = []

    for ov in unknown_commits:
        m = commit_index.get(ov["commit"], {})
        for d in m.get("top_level_dirs", []):
            top_dir_counter[d] += 1
        for p in m.get("touched_paths", []):
            parts = normalize_path(p).split("/")
            prefix = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
            prefix_2_counter[prefix] += 1
        for t in m.get("tags", []):
            tag_counter[t] += 1
        date_str = m.get("date", "")
        if date_str:
            dates.append(date_str[:10])

    dates.sort()
    date_counter = Counter(dates)

    unknown_analysis = {
        "total_unknown_commits": unknown_count,
        "invariant_check": f"PASS ({unknown_count} == 160)",
        "by_top_level_dir": dict(top_dir_counter.most_common()),
        "by_normalized_prefix_2seg": dict(prefix_2_counter.most_common()),
        "by_tag": dict(tag_counter.most_common()),
        "by_date": dict(date_counter.most_common()),
        "earliest_unknown_date": dates[0] if dates else None,
        "latest_unknown_date": dates[-1] if dates else None,
    }

    write_json(SCRATCH / "CLASSIFIER_UNKNOWN_ANALYSIS.json", unknown_analysis)
    print(f"  -> CLASSIFIER_UNKNOWN_ANALYSIS.json written")
    print(f"  Date range: {dates[0]} to {dates[-1]}")
    print(f"  Top dirs: {top_dir_counter.most_common(8)}")
    return commit_index, unknown_commits


# ============================================================================
# STEP 3
# ============================================================================
def step3_cluster(commit_index, unknown_commits):
    print("=" * 60)
    print("STEP 3: Cluster UNKNOWN path families")
    print("=" * 60)

    # Gather all UNKNOWN paths from UNKNOWN commits
    unknown_path_items = []
    for ov in unknown_commits:
        m = commit_index.get(ov["commit"], {})
        for p in m.get("touched_paths", []):
            np = normalize_path(p)
            path_classes = classify_path_v01(np)
            if "UNKNOWN" in path_classes:
                unknown_path_items.append({
                    "commit": ov["commit"],
                    "path": np,
                    "date": m.get("date", ""),
                })

    # Group by top-level prefix
    prefix_groups = defaultdict(list)
    for item in unknown_path_items:
        parts = item["path"].split("/")
        if len(parts) >= 2:
            prefix = parts[0] + "/"
        elif "/" not in item["path"]:
            prefix = "(root)"
        else:
            prefix = parts[0] + "/"
        prefix_groups[prefix].append(item)

    clusters = []
    for prefix in sorted(prefix_groups.keys(), key=lambda k: -len(prefix_groups[k])):
        items = prefix_groups[prefix]
        commit_set = set(i["commit"] for i in items)
        path_set = sorted(set(i["path"] for i in items))
        item_dates = sorted(set(i["date"][:10] for i in items if i["date"]))

        cluster_tags = Counter()
        for c in commit_set:
            m = commit_index.get(c, {})
            for t in m.get("tags", []):
                cluster_tags[t] += 1

        clusters.append({
            "prefix": prefix,
            "total_unknown_paths": len(items),
            "unique_paths": len(path_set),
            "commits_affected": len(commit_set),
            "earliest": item_dates[0] if item_dates else None,
            "latest": item_dates[-1] if item_dates else None,
            "dominant_tags": dict(cluster_tags.most_common(5)),
            "sample_paths": path_set[:15],
            "all_paths": path_set,
        })

    significant = [c for c in clusters if c["commits_affected"] >= 3 or c["total_unknown_paths"] >= 5]

    write_json(SCRATCH / "UNKNOWN_PATH_CLUSTERS.json", {
        "clusters": clusters,
        "significant_clusters": [c["prefix"] for c in significant],
    })

    print(f"  -> UNKNOWN_PATH_CLUSTERS.json written ({len(clusters)} clusters, {len(significant)} significant)")
    for c in significant:
        print(f"     {c['prefix']}: {c['commits_affected']} commits, {c['unique_paths']} unique paths")

    return clusters, significant


# ============================================================================
# STEP 4: MAP CLUSTERS TO EXISTING CLASSES
# ============================================================================
def step4_map_clusters(clusters, significant):
    print("=" * 60)
    print("STEP 4: Map clusters to existing classes")
    print("=" * 60)

    # Build mapping proposals based on path analysis
    proposals = []

    for cluster in clusters:
        prefix = cluster["prefix"]
        paths = cluster["all_paths"]
        commits = cluster["commits_affected"]

        proposal = {
            "prefix": prefix,
            "commits_affected": commits,
            "unique_paths": cluster["unique_paths"],
        }

        # Decision logic based on existing taxonomy definitions only
        if prefix == "docs/":
            # Check what docs/ paths exist
            sub_prefixes = Counter()
            for p in paths:
                parts = p.split("/")
                if len(parts) >= 2:
                    sub_prefixes[parts[1]] += 1

            # docs/contracts, docs/governance, docs/phase_2_2 -> B
            # Other docs/ paths: check if they resemble B patterns
            b_like = []
            remaining = []
            for p in paths:
                if (p.startswith("docs/contracts/") or
                    p.startswith("docs/governance/") or
                    p.startswith("docs/phase_2_2/")):
                    b_like.append(p)
                else:
                    remaining.append(p)

            # Remaining docs/ paths: docs/baselines/, docs/operations/, docs/REPO_MAP/, etc.
            # These are documentation artifacts. Class B covers governance/contract docs.
            # General docs that are not contracts/governance/phase_2_2 are structurally
            # similar to B (documentation artifacts) but outside the explicit B patterns.
            # Map to B: docs/ is the documentation tree; B covers docs/ subdirectories
            # for governance purposes. Non-governance docs under docs/ share the same
            # structural role (documentation, no executable code).
            proposal["proposed_class"] = "B"
            proposal["reasoning"] = (
                "docs/ paths not already covered by B (docs/contracts/, docs/governance/, "
                "docs/phase_2_2/) are structurally analogous: documentation artifacts under "
                "the docs/ tree. Class B already covers multiple docs/ subdirectories. "
                "Extending B to docs/** is consistent with the taxonomy definition of B "
                "as documentation requiring ratification."
            )
            proposal["new_pattern"] = "docs/**"
            proposals.append(proposal)

        elif prefix == "research/":
            # research/ contains exploratory artifacts
            # No existing class covers research/ directly
            # Class C covers scripts/, src/, tests/ (code-adjacent)
            # research/ may contain code-like artifacts but is structurally separate
            # Check path extensions
            extensions = Counter()
            for p in paths:
                ext = Path(p).suffix.lower()
                extensions[ext] += 1

            proposal["path_extensions"] = dict(extensions.most_common())
            proposal["proposed_class"] = "UNKNOWN"
            proposal["reasoning"] = (
                "research/ paths do not clearly map to any existing class. Class C covers "
                "scripts/src/tests (production code paths). research/ is structurally separate "
                "and its contents may mix documentation with exploratory code. No existing class "
                "covers general research artifacts. Remains UNKNOWN pending new class definition."
            )
            proposals.append(proposal)

        elif prefix == "pine/":
            # pine/ - check contents
            extensions = Counter()
            for p in paths:
                ext = Path(p).suffix.lower()
                extensions[ext] += 1

            proposal["path_extensions"] = dict(extensions.most_common())
            # pine/ appears to be a code/tool directory similar to src/
            # But it is not under scripts/ or src/ or tests/
            # Class C covers code artifacts. pine/ could be code.
            has_code = any(ext in [".py", ".js", ".ts", ".sh"] for ext in extensions)
            if has_code and commits >= 3:
                proposal["proposed_class"] = "C"
                proposal["reasoning"] = (
                    "pine/ contains code files (e.g., .py). Class C covers scripts/, src/, "
                    "tests/ and code-adjacent artifacts. pine/ structurally resembles a "
                    "code/tool directory and its path role is analogous to src/ or scripts/."
                )
                proposal["new_pattern"] = "pine/**"
            else:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = (
                    "pine/ contents do not clearly contain executable code artifacts. "
                    "Cannot map to an existing class based on path structure alone."
                )
            proposals.append(proposal)

        elif prefix == "Tetsu/":
            extensions = Counter()
            for p in paths:
                ext = Path(p).suffix.lower()
                extensions[ext] += 1

            proposal["path_extensions"] = dict(extensions.most_common())
            has_code = any(ext in [".py", ".js", ".ts", ".sh", ".sql"] for ext in extensions)
            if has_code and commits >= 3:
                proposal["proposed_class"] = "C"
                proposal["reasoning"] = (
                    "Tetsu/ contains code files. Class C covers code-adjacent artifacts "
                    "(scripts/, src/, tests/). Tetsu/ structurally resembles a code directory "
                    "with scripts and tools."
                )
                proposal["new_pattern"] = "Tetsu/**"
            else:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = (
                    "Tetsu/ does not contain clear code artifacts or has too few commits "
                    "for confident mapping."
                )
            proposals.append(proposal)

        elif prefix == ".codex/":
            # .codex/CHECKS/ is already C. Other .codex/ paths?
            non_checks = [p for p in paths if not p.startswith(".codex/CHECKS/")]
            if non_checks:
                # .codex/ non-CHECKS paths: likely governance/infra artifacts
                proposal["non_checks_paths"] = non_checks[:10]
                proposal["proposed_class"] = "C"
                proposal["reasoning"] = (
                    ".codex/ paths outside CHECKS/ are infrastructure/governance tooling "
                    "artifacts. .codex/CHECKS/ is already class C. Extending C to .codex/** "
                    "is consistent: all .codex/ content serves the same structural role "
                    "(governance tooling infrastructure)."
                )
                proposal["new_pattern"] = ".codex/**"
            else:
                proposal["proposed_class"] = "C"
                proposal["reasoning"] = ".codex/CHECKS/ already covered by C; no additional paths."
            proposals.append(proposal)

        elif prefix == "sql/":
            # sql/path1/ -> A. Other sql/ paths?
            non_path1 = [p for p in paths if not p.startswith("sql/path1/")]
            if non_path1:
                proposal["non_path1_paths"] = non_path1[:10]
                # sql/ contains database schema and query artifacts
                # sql/path1/ is A. Other sql/ could be general DB artifacts.
                # Class C covers scripts/code. SQL files are code-adjacent.
                proposal["proposed_class"] = "C"
                proposal["reasoning"] = (
                    "sql/ paths outside sql/path1/ contain database schema and query "
                    "artifacts (e.g., schema definitions). Class C covers code and "
                    "code-adjacent artifacts. SQL schemas are structurally analogous to "
                    "source code under src/."
                )
                proposal["new_pattern"] = "sql/**"
                proposal["note"] = "sql/path1/ remains A (higher precedence, checked first)"
            else:
                proposal["proposed_class"] = "A"
                proposal["reasoning"] = "Only sql/path1/ paths found, already covered by A."
            proposals.append(proposal)

        elif prefix == "(root)":
            # Root-level files like README.md
            proposal["sample_paths"] = paths[:10]
            # Root files: README.md, etc.
            # .gitignore/.gitattributes -> E. README.md -> no class.
            # Root docs (.md) are repo-level documentation.
            doc_files = [p for p in paths if Path(p).suffix.lower() in DOC_EXTENSIONS]
            non_doc = [p for p in paths if Path(p).suffix.lower() not in DOC_EXTENSIONS]

            if doc_files and not non_doc:
                proposal["proposed_class"] = "B"
                proposal["reasoning"] = (
                    "Root-level documentation files (e.g., README.md) are repo-level "
                    "documentation artifacts. Class B covers documentation. Root .md files "
                    "serve the same structural role as docs/ documentation."
                )
                proposal["new_pattern"] = "*.md (root level)"
            elif non_doc:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = (
                    "Root-level files include non-documentation files that do not clearly "
                    "map to existing classes."
                )
            else:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = "Empty or ambiguous root-level paths."
            proposals.append(proposal)

        elif prefix == "data/" or prefix == "logs/":
            proposal["proposed_class"] = "UNKNOWN"
            proposal["reasoning"] = (
                f"{prefix} paths contain runtime data/log artifacts. No existing class "
                "covers data storage or log output. These are operationally distinct from "
                "code (C), documentation (B), or evidence (A)."
            )
            proposals.append(proposal)

        else:
            # Generic fallback for other prefixes
            extensions = Counter()
            for p in paths:
                ext = Path(p).suffix.lower()
                extensions[ext] += 1

            proposal["path_extensions"] = dict(extensions.most_common())

            # Check if primarily doc extensions
            total_paths = len(paths)
            doc_count = sum(1 for p in paths if Path(p).suffix.lower() in DOC_EXTENSIONS)

            if doc_count == total_paths and total_paths > 0:
                proposal["proposed_class"] = "B"
                proposal["reasoning"] = (
                    f"{prefix} contains only documentation files. Structurally analogous "
                    "to docs/ documentation covered by class B."
                )
                proposal["new_pattern"] = f"{prefix}**"
            elif commits < 3 and cluster["unique_paths"] < 5:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = (
                    f"{prefix} has too few commits ({commits}) and paths "
                    f"({cluster['unique_paths']}) for confident classification."
                )
            else:
                proposal["proposed_class"] = "UNKNOWN"
                proposal["reasoning"] = (
                    f"{prefix} does not clearly match any existing class definition."
                )
            proposals.append(proposal)

    return proposals


# ============================================================================
# STEP 4b: Generate proposal markdown
# ============================================================================
def step4b_write_proposal(proposals, clusters):
    print("  Writing CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md")

    lines = []
    lines.append("# Classifier Coverage Proposal v0.2")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("This proposal extends the v0.1 classifier with additive rules to reduce")
    lines.append("UNKNOWN classifications for early-repo commits. No existing rules are modified.")
    lines.append("")
    lines.append("## Cluster Analysis and Proposals")
    lines.append("")

    proposed_mappings = []
    remaining_unknown = []

    for p in proposals:
        prefix = p["prefix"]
        proposed = p["proposed_class"]
        lines.append(f"### `{prefix}`")
        lines.append("")
        lines.append(f"- **Commits affected**: {p['commits_affected']}")
        lines.append(f"- **Unique UNKNOWN paths**: {p['unique_paths']}")
        if "path_extensions" in p:
            lines.append(f"- **Extensions**: {p['path_extensions']}")
        if "sample_paths" in p:
            lines.append(f"- **Sample paths**: {p.get('sample_paths', [])[:5]}")
        if "non_checks_paths" in p:
            lines.append(f"- **Non-CHECKS paths**: {p['non_checks_paths'][:5]}")
        if "non_path1_paths" in p:
            lines.append(f"- **Non-path1 paths**: {p['non_path1_paths'][:5]}")
        lines.append(f"- **Proposed class**: **{proposed}**")
        lines.append(f"- **Reasoning**: {p['reasoning']}")
        if "new_pattern" in p:
            lines.append(f"- **New pattern**: `{p['new_pattern']}`")
        if "note" in p:
            lines.append(f"- **Note**: {p['note']}")
        lines.append("")

        if proposed != "UNKNOWN" and "new_pattern" in p:
            proposed_mappings.append(p)
        else:
            remaining_unknown.append(p)

    lines.append("## Summary of Proposed Mappings")
    lines.append("")
    lines.append("| Prefix | Proposed Class | New Pattern |")
    lines.append("|--------|---------------|-------------|")
    for p in proposed_mappings:
        lines.append(f"| `{p['prefix']}` | {p['proposed_class']} | `{p.get('new_pattern', 'N/A')}` |")
    lines.append("")

    lines.append("## Clusters Remaining UNKNOWN")
    lines.append("")
    for p in remaining_unknown:
        lines.append(f"- `{p['prefix']}`: {p['reasoning']}")
    lines.append("")

    write_text(SCRATCH / "CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md", "\n".join(lines) + "\n")
    print(f"  -> {len(proposed_mappings)} mappings proposed, {len(remaining_unknown)} remain UNKNOWN")
    return proposed_mappings


# ============================================================================
# STEP 5: GENERATE DIFF PREVIEW
# ============================================================================
def step5_diff_preview(proposed_mappings):
    print("=" * 60)
    print("STEP 5: Generate additive classifier patch preview")
    print("=" * 60)

    lines = []
    lines.append("=" * 70)
    lines.append("PROPOSED ADDITIVE EXTENSION - CLASSIFIER v0.2 (PREVIEW ONLY)")
    lines.append("DO NOT APPLY - This is a preview for review.")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Changes to: scripts/governance/classify_change.py")
    lines.append("Type: ADDITIVE ONLY (no existing rules removed or modified)")
    lines.append("")

    # Build the new rules in the classify_path function
    new_rules = []
    for p in proposed_mappings:
        prefix = p["prefix"]
        cls = p["proposed_class"]
        pattern = p.get("new_pattern", "")

        if prefix == "docs/":
            new_rules.append({
                "class": cls,
                "code": '    if path.startswith("docs/"):\n        classes.add("B")',
                "comment": "# v0.2: Extend B to all docs/ (contracts/governance/phase_2_2 already matched above)",
                "insert_after": "docs/phase_2_2/ block",
            })
        elif prefix == ".codex/":
            new_rules.append({
                "class": cls,
                "code": '    if path.startswith(".codex/"):\n        classes.add("C")',
                "comment": "# v0.2: Extend C to all .codex/ (CHECKS/ already matched above)",
                "insert_after": ".codex/CHECKS/ block",
            })
        elif prefix == "sql/":
            new_rules.append({
                "class": cls,
                "code": '    if path.startswith("sql/") and not path.startswith("sql/path1/"):\n        classes.add("C")',
                "comment": "# v0.2: sql/ non-path1 -> C (schema/query code artifacts)",
                "insert_after": "sql/path1/ block",
            })
        elif prefix == "pine/":
            new_rules.append({
                "class": cls,
                "code": '    if path.startswith("pine/"):\n        classes.add("C")',
                "comment": "# v0.2: pine/ code directory -> C",
                "insert_after": "src/ block",
            })
        elif prefix == "Tetsu/":
            new_rules.append({
                "class": cls,
                "code": '    if path.startswith("Tetsu/"):\n        classes.add("C")',
                "comment": "# v0.2: Tetsu/ code directory -> C",
                "insert_after": "src/ block",
            })
        elif prefix == "(root)" and cls == "B":
            new_rules.append({
                "class": cls,
                "code": (
                    '    if "/" not in path and Path(path).suffix.lower() in DOC_EXTENSIONS:\n'
                    '        classes.add("B")'
                ),
                "comment": "# v0.2: Root-level doc files (.md, .txt, etc.) -> B",
                "insert_after": "docs/ block",
            })

    lines.append("--- a/scripts/governance/classify_change.py")
    lines.append("+++ b/scripts/governance/classify_change.py")
    lines.append("")
    lines.append("In function classify_path(path: str) -> set[str]:")
    lines.append("")

    for rule in new_rules:
        lines.append(f"+ {rule['comment']}")
        for code_line in rule["code"].split("\n"):
            lines.append(f"+ {code_line}")
        lines.append(f"  (insert after: {rule['insert_after']})")
        lines.append("")

    lines.append("=" * 70)
    lines.append("END OF PREVIEW")
    lines.append("=" * 70)

    write_text(SCRATCH / "CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt", "\n".join(lines) + "\n")
    print(f"  -> CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt written ({len(new_rules)} new rules)")
    return new_rules


# ============================================================================
# STEP 6: SIMULATE RECLASSIFICATION
# ============================================================================
def classify_path_v02(path: str, proposed_mappings: list) -> set[str]:
    """v0.1 rules + v0.2 additive rules"""
    classes = classify_path_v01(path)

    # Remove UNKNOWN if it was the only class (we may reclassify)
    # But we need to recheck: if UNKNOWN was added because nothing matched,
    # we try new rules and if they match, remove UNKNOWN.
    lower = path.lower()

    new_matches = set()

    # v0.2 additive rules
    # docs/ -> B
    if path.startswith("docs/"):
        new_matches.add("B")

    # .codex/ -> C
    if path.startswith(".codex/"):
        new_matches.add("C")

    # sql/ non-path1 -> C
    if path.startswith("sql/") and not path.startswith("sql/path1/"):
        new_matches.add("C")

    # pine/ -> C (only if proposed)
    pattern_prefixes = {p.get("new_pattern", ""): p["proposed_class"] for p in proposed_mappings if p.get("new_pattern")}

    if path.startswith("pine/"):
        for pm in proposed_mappings:
            if pm["prefix"] == "pine/" and pm["proposed_class"] != "UNKNOWN":
                new_matches.add(pm["proposed_class"])

    if path.startswith("Tetsu/"):
        for pm in proposed_mappings:
            if pm["prefix"] == "Tetsu/" and pm["proposed_class"] != "UNKNOWN":
                new_matches.add(pm["proposed_class"])

    # Root-level doc files -> B
    if "/" not in path and Path(path).suffix.lower() in DOC_EXTENSIONS:
        for pm in proposed_mappings:
            if pm["prefix"] == "(root)" and pm["proposed_class"] != "UNKNOWN":
                new_matches.add(pm["proposed_class"])

    if new_matches:
        classes.update(new_matches)
        classes.discard("UNKNOWN")

    return classes


def step6_simulate(metrics, overlay, proposed_mappings):
    print("=" * 60)
    print("STEP 6: Simulate reclassification")
    print("=" * 60)

    commit_index = {c["hash"]: c for c in metrics["commits"]}

    # Reclassify all commits
    simulated_records = []
    changes = []

    for ov in overlay:
        commit_hash = ov["commit"]
        m = commit_index.get(commit_hash, {})
        paths = m.get("touched_paths", [])

        # Classify with v0.2
        new_class_set = set()
        new_unknown_paths = []
        for p in paths:
            np = normalize_path(p)
            if not np:
                continue
            pc = classify_path_v02(np, proposed_mappings)
            new_class_set.update(pc)
            if "UNKNOWN" in pc:
                new_unknown_paths.append(np)

        if not new_class_set:
            new_class_set.add("UNKNOWN")

        ordered = [c for c in CLASS_ORDER if c in new_class_set]
        unknown = ordered == ["UNKNOWN"]
        ambiguous = len(ordered) > 1

        record = {
            "commit": commit_hash,
            "classes": ordered,
            "unknown": unknown,
            "ambiguous": ambiguous,
            "files": ov["files"],
            "base": ov["base"],
        }
        simulated_records.append(record)

        old_classes = ov["classes"]
        if ordered != old_classes:
            changes.append({
                "commit": commit_hash,
                "old_classes": old_classes,
                "new_classes": ordered,
            })

    # Write simulated overlay
    sim_lines = []
    for r in simulated_records:
        sim_lines.append(json.dumps(r, sort_keys=True, separators=(",", ":")))
    write_text(
        SCRATCH / "DEV_CHANGE_CLASSIFICATION_OVERLAY_SIMULATED_v0.2.jsonl",
        "\n".join(sim_lines) + "\n",
    )

    # INVARIANTS
    total = len(simulated_records)
    assert total == 264, f"INVARIANT FAIL: total commits {total} != 264"

    # Check no commit loses existing non-UNKNOWN classification
    violations = []
    for ov_old, ov_new in zip(overlay, simulated_records):
        old_non_unknown = set(ov_old["classes"]) - {"UNKNOWN"}
        new_non_unknown = set(ov_new["classes"]) - {"UNKNOWN"}
        lost = old_non_unknown - new_non_unknown
        if lost:
            violations.append({
                "commit": ov_old["commit"],
                "lost_classes": sorted(lost),
            })

    if violations:
        print(f"  INVARIANT FAIL: {len(violations)} commits lost non-UNKNOWN classes")
        for v in violations[:5]:
            print(f"    {v['commit']}: lost {v['lost_classes']}")
        sys.exit(1)

    # Check only UNKNOWN -> known transitions
    bad_transitions = []
    for change in changes:
        old_set = set(change["old_classes"])
        new_set = set(change["new_classes"])
        # New classes should be a superset of old non-UNKNOWN classes
        old_non_unk = old_set - {"UNKNOWN"}
        new_non_unk = new_set - {"UNKNOWN"}
        if not old_non_unk.issubset(new_non_unk):
            bad_transitions.append(change)

    if bad_transitions:
        print(f"  INVARIANT FAIL: {len(bad_transitions)} bad transitions")
        sys.exit(1)

    # Compute stats
    old_class_counts = Counter()
    new_class_counts = Counter()
    old_unknown_total = 0
    new_unknown_total = 0

    for ov in overlay:
        for c in ov["classes"]:
            old_class_counts[c] += 1
        if "UNKNOWN" in ov["classes"]:
            old_unknown_total += 1

    for r in simulated_records:
        for c in r["classes"]:
            new_class_counts[c] += 1
        if "UNKNOWN" in r["classes"]:
            new_unknown_total += 1

    stats = {
        "total_commits": total,
        "invariants": {
            "total_unchanged": total == 264,
            "no_lost_non_unknown": len(violations) == 0,
            "only_unknown_to_known": len(bad_transitions) == 0,
        },
        "unknown_before": old_unknown_total,
        "unknown_after": new_unknown_total,
        "unknown_reduction": old_unknown_total - new_unknown_total,
        "unknown_reduction_pct": round((old_unknown_total - new_unknown_total) / old_unknown_total * 100, 1) if old_unknown_total else 0,
        "class_counts_before": dict(sorted(old_class_counts.items())),
        "class_counts_after": dict(sorted(new_class_counts.items())),
        "commits_changed": len(changes),
        "changed_commits": changes,
    }

    write_json(SCRATCH / "CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json", stats)

    print(f"  INVARIANTS: ALL PASS")
    print(f"  Total commits: {total}")
    print(f"  UNKNOWN before: {old_unknown_total}")
    print(f"  UNKNOWN after: {new_unknown_total}")
    print(f"  Reduction: {old_unknown_total - new_unknown_total} ({stats['unknown_reduction_pct']}%)")
    print(f"  Commits changed: {len(changes)}")

    return stats


# ============================================================================
# MAIN
# ============================================================================
def main():
    metrics, overlay = load_data()

    # Step 1
    step1_snapshot()

    # Step 2
    commit_index, unknown_commits = step2_isolate_unknowns(metrics, overlay)

    # Step 3
    clusters, significant = step3_cluster(commit_index, unknown_commits)

    # Step 4
    proposals = step4_map_clusters(clusters, significant)
    proposed_mappings = step4b_write_proposal(proposals, clusters)

    # Step 5
    new_rules = step5_diff_preview(proposed_mappings)

    # Step 6
    stats = step6_simulate(metrics, overlay, proposed_mappings)

    # Step 7: Summary
    print("")
    print("=" * 70)
    print("STEP 7: SUMMARY")
    print("=" * 70)
    print(f"  UNKNOWN count before: {stats['unknown_before']}")
    print(f"  UNKNOWN count after:  {stats['unknown_after']}")
    print(f"  % reduction:          {stats['unknown_reduction_pct']}%")
    print(f"  Commits reclassified: {stats['commits_changed']}")
    print("")
    print("  Top path families newly classified:")
    for p in proposed_mappings:
        print(f"    {p['prefix']} -> {p['proposed_class']} (via pattern: {p.get('new_pattern', 'N/A')})")
    print("")
    print("  Confirmation: No existing classified commits changed class.")
    print("")
    print("  Scratch deliverables:")
    deliverables = [
        "CLASSIFIER_UNKNOWN_ANALYSIS.json",
        "CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md",
        "CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt",
        "CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json",
        "classifier_rules.snapshot.json",
        "UNKNOWN_PATH_CLUSTERS.json",
        "DEV_CHANGE_CLASSIFICATION_OVERLAY_SIMULATED_v0.2.jsonl",
    ]
    for d in deliverables:
        path = SCRATCH / d
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        print(f"    {'OK' if exists else 'MISSING'} {d} ({size:,} bytes)")


if __name__ == "__main__":
    main()
