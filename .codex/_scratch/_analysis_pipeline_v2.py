#!/usr/bin/env python3
"""
Classifier coverage analysis pipeline v2 - refined mappings.
Produces all deliverables under .codex/_scratch/.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRATCH = Path(".codex/_scratch")
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}
CLASS_ORDER = ["A", "B", "C", "D", "E", "UNKNOWN"]


def write_json(path: Path, data) -> None:
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

    if lower.startswith("tools/"):
        if any("shim" in part for part in lower.split("/") if part):
            classes.add("E")

    if not classes:
        classes.add("UNKNOWN")

    return classes


def classify_path_v02(path: str) -> set[str]:
    """v0.1 rules + v0.2 additive rules. Never removes a v0.1 match."""
    classes = classify_path_v01(path)
    lower = path.lower()

    # ---- v0.2 ADDITIVE RULES ----

    # B: docs/ (all subdirs — contracts/governance/phase_2_2 already B via v0.1)
    if path.startswith("docs/"):
        classes.add("B")

    # B: contracts/ (top-level governance contracts)
    if path.startswith("contracts/"):
        classes.add("B")

    # B: specs/ (specification documents, all .md)
    if path.startswith("specs/"):
        classes.add("B")

    # B: reports/ non-path1 (validation/verification reports)
    # reports/path1/ already A via v0.1; other reports/ are documentation artifacts
    if path.startswith("reports/") and not path.startswith("reports/path1/"):
        classes.add("B")

    # B: releases/ (release documentation)
    if path.startswith("releases/"):
        classes.add("B")

    # B: root-level documentation files
    if "/" not in path and Path(path).suffix.lower() in DOC_EXTENSIONS:
        classes.add("B")

    # C: sql/ non-path1 (schema/query code)
    if path.startswith("sql/") and not path.startswith("sql/path1/"):
        classes.add("C")

    # C: .codex/ (all — CHECKS/ already C via v0.1)
    if path.startswith(".codex/"):
        classes.add("C")

    # C: infra/ (infrastructure code: TypeScript, SQL, configs, tests)
    if path.startswith("infra/"):
        classes.add("C")

    # C: pine/ (PineScript code files)
    if path.startswith("pine/"):
        classes.add("C")

    # C: Tetsu/ (code directory with scripts)
    if path.startswith("Tetsu/"):
        classes.add("C")

    # C: trajectory_families/ (Python modules)
    if path.startswith("trajectory_families/"):
        classes.add("C")

    # C: _archive/ (archived code artifacts)
    if path.startswith("_archive/"):
        classes.add("C")

    # C: _quarantine/ (quarantined code artifacts)
    if path.startswith("_quarantine/"):
        classes.add("C")

    # C: configs/ (configuration files used by code)
    if path.startswith("configs/"):
        classes.add("C")

    # C: schema/ (database schema definitions)
    if path.startswith("schema/"):
        classes.add("C")

    # A: artifacts/ (evidence/validation artifacts)
    if path.startswith("artifacts/"):
        classes.add("A")

    # E: .github/ non-workflows (repo config: copilot-instructions, PR template)
    # .github/workflows/ already C+E via v0.1; other .github/ are repo config
    if path.startswith(".github/") and not path.startswith(".github/workflows/"):
        classes.add("E")

    # E: .vscode/ (editor/repo configuration)
    if path.startswith(".vscode/"):
        classes.add("E")

    # E: ovc-webhook/ (.vscode settings leaked into subdir)
    if path.startswith("ovc-webhook/"):
        classes.add("E")

    # Remove UNKNOWN if any real class was assigned
    if classes - {"UNKNOWN"}:
        classes.discard("UNKNOWN")

    return classes


def load_data():
    with open(SCRATCH / "history_metrics.backfill.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    overlay = []
    with open(
        SCRATCH / "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.jsonl", "r", encoding="utf-8"
    ) as f:
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

    unknown_analysis = {
        "total_unknown_commits": unknown_count,
        "invariant_check": f"PASS ({unknown_count} == 160)",
        "by_top_level_dir": dict(top_dir_counter.most_common()),
        "by_normalized_prefix_2seg": dict(prefix_2_counter.most_common()),
        "by_tag": dict(tag_counter.most_common()),
        "by_date": dict(Counter(dates).most_common()),
        "earliest_unknown_date": dates[0] if dates else None,
        "latest_unknown_date": dates[-1] if dates else None,
    }

    write_json(SCRATCH / "CLASSIFIER_UNKNOWN_ANALYSIS.json", unknown_analysis)
    print(f"  -> CLASSIFIER_UNKNOWN_ANALYSIS.json written")
    print(f"  Date range: {dates[0]} to {dates[-1]}")
    return commit_index, unknown_commits


# ============================================================================
# STEP 3
# ============================================================================
def step3_cluster(commit_index, unknown_commits):
    print("=" * 60)
    print("STEP 3: Cluster UNKNOWN path families")
    print("=" * 60)

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

    print(f"  -> UNKNOWN_PATH_CLUSTERS.json ({len(clusters)} clusters, {len(significant)} significant)")
    for c in significant:
        print(f"     {c['prefix']}: {c['commits_affected']} commits, {c['unique_paths']} paths")

    return clusters, significant


# ============================================================================
# STEP 4: Mapping proposals (manual, evidence-based)
# ============================================================================
PROPOSALS = [
    {
        "prefix": "docs/",
        "proposed_class": "B",
        "new_pattern": "docs/**",
        "reasoning": (
            "docs/ paths not already covered by B (docs/contracts/, docs/governance/, "
            "docs/phase_2_2/) include architecture specs, baselines, catalogs, doctrine, "
            "evidence packs, history, and operations documentation. All are documentation "
            "artifacts. Class B already covers three docs/ subdirectories. Extending B to "
            "all docs/ is consistent: the taxonomy defines B as documentation requiring "
            "ratification. Observed paths: docs/architecture/, docs/baselines/, "
            "docs/catalogs/, docs/doctrine/, docs/evidence_pack/, docs/history/, "
            "docs/operations/, docs/REPO_MAP/, etc."
        ),
    },
    {
        "prefix": "contracts/",
        "proposed_class": "B",
        "new_pattern": "contracts/**",
        "reasoning": (
            "contracts/ contains governance contract JSON files "
            "(derived_feature_set_v0.1.json, eval_contract_v0.1.json, "
            "export_contract_v0.1.json, run_artifact_spec_v0.1.json). "
            "Class B covers docs/contracts/ already. Top-level contracts/ serves the "
            "same structural role: machine-readable governance contract definitions."
        ),
    },
    {
        "prefix": "specs/",
        "proposed_class": "B",
        "new_pattern": "specs/**",
        "reasoning": (
            "specs/ contains specification documents (all .md): dashboards_v0.1.md, "
            "outcome_sql_spec_v0.1.md, research_query_pack_v0.1.md, etc. These are "
            "documentation artifacts structurally analogous to docs/ content covered by B."
        ),
    },
    {
        "prefix": "reports/ (non-path1)",
        "proposed_class": "B",
        "new_pattern": "reports/** (excluding reports/path1/)",
        "reasoning": (
            "reports/ paths outside reports/path1/ include validation reports "
            "(reports/validation/C1_v0_1_validation.md) and verification output captures "
            "(reports/verification/). These are documentation-class artifacts: textual "
            "reports and captured outputs for audit. reports/path1/ remains A."
        ),
    },
    {
        "prefix": "releases/",
        "proposed_class": "B",
        "new_pattern": "releases/**",
        "reasoning": (
            "releases/ contains release documentation (releases/ovc-v0.1-spine.md). "
            "Structurally analogous to docs/ documentation covered by B."
        ),
    },
    {
        "prefix": "(root) .md/.txt files",
        "proposed_class": "B",
        "new_pattern": "root-level doc-extension files",
        "reasoning": (
            "Root-level files with documentation extensions (e.g., README.md) are "
            "repo-level documentation artifacts. Class B covers documentation. "
            ".gitignore/.gitattributes already covered by E; remaining root docs -> B."
        ),
    },
    {
        "prefix": "sql/ (non-path1)",
        "proposed_class": "C",
        "new_pattern": "sql/** (excluding sql/path1/)",
        "reasoning": (
            "sql/ paths outside sql/path1/ contain schema definitions and query files "
            "(sql/schema_v01.sql, sql/derived_v0_1.sql). Class C covers code artifacts "
            "(scripts/, src/). SQL schema files are code-adjacent. sql/path1/ remains A."
        ),
    },
    {
        "prefix": ".codex/",
        "proposed_class": "C",
        "new_pattern": ".codex/**",
        "reasoning": (
            ".codex/ paths outside CHECKS/ are governance tooling infrastructure. "
            ".codex/CHECKS/ is already class C. All .codex/ content serves the same "
            "structural role. Observed: .codex/CHECKS/ (already C), .codex/_scratch/ "
            "and other governance infra paths."
        ),
    },
    {
        "prefix": "infra/",
        "proposed_class": "C",
        "new_pattern": "infra/**",
        "reasoning": (
            "infra/ contains infrastructure code: TypeScript source (infra/ovc-webhook/src/index.ts), "
            "test files, package.json, SQL migrations, tsconfig. These are code artifacts "
            "structurally analogous to src/ and scripts/ covered by C."
        ),
    },
    {
        "prefix": "pine/",
        "proposed_class": "C",
        "new_pattern": "pine/**",
        "reasoning": (
            "pine/ contains PineScript code files (OVC_v0_1.pine, export_module_v0.1.pine). "
            "These are executable script artifacts structurally analogous to src/ code "
            "covered by C."
        ),
    },
    {
        "prefix": "Tetsu/",
        "proposed_class": "C",
        "new_pattern": "Tetsu/**",
        "reasoning": (
            "Tetsu/ contains code files across 58 unique paths and 16 commits. "
            "Structurally resembles a code/tool directory analogous to src/ or scripts/ "
            "covered by C."
        ),
    },
    {
        "prefix": "trajectory_families/",
        "proposed_class": "C",
        "new_pattern": "trajectory_families/**",
        "reasoning": (
            "trajectory_families/ contains Python modules (__init__.py, clustering.py, "
            "distance.py, features.py, etc.). These are source code artifacts directly "
            "analogous to src/ covered by C."
        ),
    },
    {
        "prefix": "_archive/",
        "proposed_class": "C",
        "new_pattern": "_archive/**",
        "reasoning": (
            "_archive/ contains archived code artifacts: scripts, SQL, checks, deploy "
            "scripts. These are code artifacts that have been archived but retain their "
            "structural role as code (analogous to scripts/, src/, .codex/CHECKS/)."
        ),
    },
    {
        "prefix": "_quarantine/",
        "proposed_class": "C",
        "new_pattern": "_quarantine/**",
        "reasoning": (
            "_quarantine/ contains quarantined code: GitHub workflow YAML, SQL views, "
            "Python stubs. These are code artifacts under quarantine but structurally "
            "analogous to src/, scripts/, .github/workflows/ covered by C."
        ),
    },
    {
        "prefix": "configs/",
        "proposed_class": "C",
        "new_pattern": "configs/**",
        "reasoning": (
            "configs/ contains JSON configuration files used by code "
            "(threshold_packs/c3_example_pack_v1.json, etc.). Configuration files are "
            "code-adjacent artifacts structurally analogous to content under scripts/ "
            "or src/ covered by C."
        ),
    },
    {
        "prefix": "schema/",
        "proposed_class": "C",
        "new_pattern": "schema/**",
        "reasoning": (
            "schema/ contains database schema definitions (applied_migrations.json, "
            "required_objects.txt). These are code-adjacent infrastructure artifacts "
            "analogous to sql/ schemas covered by C."
        ),
    },
    {
        "prefix": "artifacts/",
        "proposed_class": "A",
        "new_pattern": "artifacts/**",
        "reasoning": (
            "artifacts/ contains evidence and validation outputs: "
            "derived_validation_report.json, path1_replay_report.json, "
            "change_classifier.json. These are evidence artifacts structurally "
            "analogous to reports/path1/ output covered by A."
        ),
    },
    {
        "prefix": ".github/ (non-workflows)",
        "proposed_class": "E",
        "new_pattern": ".github/** (excluding .github/workflows/)",
        "reasoning": (
            ".github/ paths outside workflows/ include copilot-instructions.md, "
            "copilot-instructions.txt, pull_request_template.md. These are repo "
            "configuration files structurally analogous to .gitignore/.gitattributes "
            "covered by E."
        ),
    },
    {
        "prefix": ".vscode/",
        "proposed_class": "E",
        "new_pattern": ".vscode/**",
        "reasoning": (
            ".vscode/ contains editor configuration (settings.json). This is repo/editor "
            "configuration structurally analogous to .gitignore covered by E."
        ),
    },
    {
        "prefix": "ovc-webhook/",
        "proposed_class": "E",
        "new_pattern": "ovc-webhook/**",
        "reasoning": (
            "ovc-webhook/vscode/settings.json is an editor configuration artifact "
            "analogous to .vscode/ or .gitignore covered by E."
        ),
    },
    # REMAINING UNKNOWN
    {
        "prefix": "research/",
        "proposed_class": "UNKNOWN",
        "reasoning": (
            "research/ contains 55 unique paths across 9 commits mixing documentation, "
            "exploratory code, and data. No single existing class covers this mixed role. "
            "Remains UNKNOWN pending possible new class definition."
        ),
    },
    {
        "prefix": "CLAIMS/",
        "proposed_class": "UNKNOWN",
        "reasoning": (
            "CLAIMS/ has only 2 commits and 2 paths (ANCHOR_INDEX_v0_1.csv, "
            "CLAIM_BINDING_v0_1.md). Too few data points and the structural role "
            "(claim bindings) does not clearly map to an existing class. Remains UNKNOWN."
        ),
    },
    {
        "prefix": "Work Timeline/",
        "proposed_class": "UNKNOWN",
        "reasoning": (
            "Work Timeline/ has only 1 commit and 1 path (020226.txt). Insufficient "
            "data. Does not clearly map to any existing class. Remains UNKNOWN."
        ),
    },
]


def step4_write_proposal():
    print("=" * 60)
    print("STEP 4: Map clusters to existing classes")
    print("=" * 60)

    mapped = [p for p in PROPOSALS if p["proposed_class"] != "UNKNOWN"]
    unmapped = [p for p in PROPOSALS if p["proposed_class"] == "UNKNOWN"]

    lines = []
    lines.append("# Classifier Coverage Proposal v0.2")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("This proposal extends the v0.1 classifier with additive path-pattern rules")
    lines.append("to reduce UNKNOWN classifications for early-repo commits.")
    lines.append("No existing rules are removed or modified. All mappings are justified by")
    lines.append("structural similarity to paths already covered by the existing taxonomy.")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("1. Extracted all paths classified UNKNOWN under v0.1 (160 commits)")
    lines.append("2. Clustered by top-level directory prefix (24 clusters)")
    lines.append("3. For each cluster, compared path contents against existing class definitions")
    lines.append("4. Proposed mapping to existing class only when structural role is unambiguous")
    lines.append("5. Left as UNKNOWN when no clear single-class mapping exists")
    lines.append("")
    lines.append("## Proposed Mappings")
    lines.append("")
    lines.append("| # | Prefix | Proposed Class | New Pattern | Commits |")
    lines.append("|---|--------|---------------|-------------|---------|")
    for i, p in enumerate(mapped, 1):
        lines.append(
            f"| {i} | `{p['prefix']}` | **{p['proposed_class']}** | "
            f"`{p.get('new_pattern', 'N/A')}` | - |"
        )
    lines.append("")

    lines.append("## Detailed Justifications")
    lines.append("")
    for p in mapped:
        lines.append(f"### `{p['prefix']}` -> {p['proposed_class']}")
        lines.append("")
        lines.append(f"**Pattern**: `{p.get('new_pattern', 'N/A')}`")
        lines.append("")
        lines.append(f"{p['reasoning']}")
        lines.append("")

    lines.append("## Clusters Remaining UNKNOWN")
    lines.append("")
    for p in unmapped:
        lines.append(f"### `{p['prefix']}`")
        lines.append("")
        lines.append(f"{p['reasoning']}")
        lines.append("")

    lines.append("## Compatibility Notes")
    lines.append("")
    lines.append("- All v0.1 rules remain unchanged")
    lines.append("- v0.2 rules are additive: they can only add classes, never remove")
    lines.append("- A path that matched class X under v0.1 will still match X under v0.2")
    lines.append("- UNKNOWN is only removed when at least one non-UNKNOWN class is assigned")
    lines.append("")

    write_text(SCRATCH / "CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md", "\n".join(lines) + "\n")
    print(f"  -> CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md ({len(mapped)} mapped, {len(unmapped)} UNKNOWN)")
    return mapped


# ============================================================================
# STEP 5: DIFF PREVIEW
# ============================================================================
def step5_diff_preview(mapped_proposals):
    print("=" * 60)
    print("STEP 5: Generate additive classifier patch preview")
    print("=" * 60)

    lines = []
    lines.append("=" * 70)
    lines.append("PROPOSED ADDITIVE EXTENSION - CLASSIFIER v0.2 (PREVIEW ONLY)")
    lines.append("DO NOT APPLY - This is a preview for review.")
    lines.append("=" * 70)
    lines.append("")
    lines.append("File: scripts/governance/classify_change.py")
    lines.append("Type: ADDITIVE ONLY - no existing rules removed or modified")
    lines.append("Location: Inside classify_path() function, BEFORE the final UNKNOWN check")
    lines.append("")
    lines.append("--- a/scripts/governance/classify_change.py")
    lines.append("+++ b/scripts/governance/classify_change.py")
    lines.append("")
    lines.append(" def classify_path(path: str) -> set[str]:")
    lines.append("     classes: set[str] = set()")
    lines.append("     ... (existing v0.1 rules unchanged) ...")
    lines.append("")
    lines.append("+    # ---- v0.2 additive rules (BEGIN) ----")
    lines.append("+")
    lines.append('+    # B: all docs/ (contracts/governance/phase_2_2 already matched above)')
    lines.append('+    if path.startswith("docs/"):')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # B: top-level contracts/')
    lines.append('+    if path.startswith("contracts/"):')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # B: specs/')
    lines.append('+    if path.startswith("specs/"):')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # B: reports/ non-path1 (path1 already A above)')
    lines.append('+    if path.startswith("reports/") and not path.startswith("reports/path1/"):')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # B: releases/')
    lines.append('+    if path.startswith("releases/"):')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # B: root-level documentation files')
    lines.append('+    if "/" not in path and Path(path).suffix.lower() in DOC_EXTENSIONS:')
    lines.append('+        classes.add("B")')
    lines.append("+")
    lines.append('+    # C: sql/ non-path1 (path1 already A above)')
    lines.append('+    if path.startswith("sql/") and not path.startswith("sql/path1/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: all .codex/ (CHECKS/ already matched above)')
    lines.append('+    if path.startswith(".codex/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: infra/')
    lines.append('+    if path.startswith("infra/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: pine/')
    lines.append('+    if path.startswith("pine/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: Tetsu/')
    lines.append('+    if path.startswith("Tetsu/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: trajectory_families/')
    lines.append('+    if path.startswith("trajectory_families/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: _archive/')
    lines.append('+    if path.startswith("_archive/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: _quarantine/')
    lines.append('+    if path.startswith("_quarantine/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: configs/')
    lines.append('+    if path.startswith("configs/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # C: schema/')
    lines.append('+    if path.startswith("schema/"):')
    lines.append('+        classes.add("C")')
    lines.append("+")
    lines.append('+    # A: artifacts/ (evidence/validation outputs)')
    lines.append('+    if path.startswith("artifacts/"):')
    lines.append('+        classes.add("A")')
    lines.append("+")
    lines.append('+    # E: .github/ non-workflows (repo config)')
    lines.append('+    if path.startswith(".github/") and not path.startswith(".github/workflows/"):')
    lines.append('+        classes.add("E")')
    lines.append("+")
    lines.append('+    # E: .vscode/')
    lines.append('+    if path.startswith(".vscode/"):')
    lines.append('+        classes.add("E")')
    lines.append("+")
    lines.append('+    # E: ovc-webhook/ (editor config)')
    lines.append('+    if path.startswith("ovc-webhook/"):')
    lines.append('+        classes.add("E")')
    lines.append("+")
    lines.append("+    # ---- v0.2 additive rules (END) ----")
    lines.append("")
    lines.append("     if not classes:")
    lines.append('         classes.add("UNKNOWN")')
    lines.append("")
    lines.append("     return classes")
    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF PREVIEW")
    lines.append("=" * 70)

    write_text(SCRATCH / "CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt", "\n".join(lines) + "\n")
    print("  -> CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt written")


# ============================================================================
# STEP 6: SIMULATE
# ============================================================================
def step6_simulate(metrics, overlay):
    print("=" * 60)
    print("STEP 6: Simulate reclassification")
    print("=" * 60)

    commit_index = {c["hash"]: c for c in metrics["commits"]}
    simulated_records = []
    changes = []

    for ov in overlay:
        m = commit_index.get(ov["commit"], {})
        paths = m.get("touched_paths", [])

        new_class_set = set()
        new_unknown_paths = []
        for p in paths:
            np = normalize_path(p)
            if not np:
                continue
            pc = classify_path_v02(np)
            new_class_set.update(pc)
            if "UNKNOWN" in pc:
                new_unknown_paths.append(np)

        if not new_class_set:
            new_class_set.add("UNKNOWN")

        # Remove UNKNOWN if any real class exists
        if new_class_set - {"UNKNOWN"}:
            new_class_set.discard("UNKNOWN")

        ordered = [c for c in CLASS_ORDER if c in new_class_set]
        unknown = ordered == ["UNKNOWN"]
        ambiguous = len(ordered) > 1

        record = {
            "commit": ov["commit"],
            "classes": ordered,
            "unknown": unknown,
            "ambiguous": ambiguous,
            "files": ov["files"],
            "base": ov["base"],
        }
        simulated_records.append(record)

        if ordered != ov["classes"]:
            changes.append({
                "commit": ov["commit"],
                "old_classes": ov["classes"],
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

    # INVARIANT 1: total unchanged
    total = len(simulated_records)
    if total != 264:
        print(f"  INVARIANT FAIL: total commits {total} != 264")
        sys.exit(1)

    # INVARIANT 2: no commit loses existing non-UNKNOWN class
    violations = []
    for ov_old, ov_new in zip(overlay, simulated_records):
        old_non_unknown = set(ov_old["classes"]) - {"UNKNOWN"}
        new_non_unknown = set(ov_new["classes"]) - {"UNKNOWN"}
        lost = old_non_unknown - new_non_unknown
        if lost:
            violations.append({
                "commit": ov_old["commit"],
                "lost_classes": sorted(lost),
                "old": ov_old["classes"],
                "new": ov_new["classes"],
            })

    if violations:
        print(f"  INVARIANT FAIL: {len(violations)} commits lost non-UNKNOWN classes")
        for v in violations[:5]:
            print(f"    {v['commit'][:12]}: {v['old']} -> {v['new']} (lost {v['lost_classes']})")
        sys.exit(1)

    # INVARIANT 3: only UNKNOWN -> known transitions
    bad_transitions = []
    for change in changes:
        old_set = set(change["old_classes"])
        new_set = set(change["new_classes"])
        old_non_unk = old_set - {"UNKNOWN"}
        new_non_unk = new_set - {"UNKNOWN"}
        if not old_non_unk.issubset(new_non_unk):
            bad_transitions.append(change)

    if bad_transitions:
        print(f"  INVARIANT FAIL: {len(bad_transitions)} bad transitions")
        for bt in bad_transitions[:5]:
            print(f"    {bt['commit'][:12]}: {bt['old_classes']} -> {bt['new_classes']}")
        sys.exit(1)

    # Stats
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
            "total_unchanged": True,
            "no_lost_non_unknown": True,
            "only_unknown_to_known": True,
        },
        "unknown_before": old_unknown_total,
        "unknown_after": new_unknown_total,
        "unknown_reduction": old_unknown_total - new_unknown_total,
        "unknown_reduction_pct": round(
            (old_unknown_total - new_unknown_total) / old_unknown_total * 100, 1
        ),
        "class_counts_before": {k: old_class_counts[k] for k in CLASS_ORDER if old_class_counts[k]},
        "class_counts_after": {k: new_class_counts[k] for k in CLASS_ORDER if new_class_counts[k]},
        "commits_reclassified": len(changes),
        "changed_commits": changes,
    }

    write_json(SCRATCH / "CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json", stats)

    print("  ALL INVARIANTS PASS")
    print(f"  Total commits: {total}")
    print(f"  UNKNOWN before: {old_unknown_total}")
    print(f"  UNKNOWN after:  {new_unknown_total}")
    print(f"  Reduction: {old_unknown_total - new_unknown_total} ({stats['unknown_reduction_pct']}%)")
    print(f"  Commits reclassified: {len(changes)}")

    return stats


# ============================================================================
# STEP 7: SUMMARY
# ============================================================================
def step7_summary(stats, mapped_proposals):
    print("")
    print("=" * 70)
    print("STEP 7: SUMMARY")
    print("=" * 70)
    print(f"")
    print(f"  UNKNOWN count before: {stats['unknown_before']}")
    print(f"  UNKNOWN count after:  {stats['unknown_after']}")
    print(f"  % reduction:          {stats['unknown_reduction_pct']}%")
    print(f"  Commits reclassified: {stats['commits_reclassified']}")
    print(f"")
    print(f"  Class counts BEFORE -> AFTER:")
    for cls in CLASS_ORDER:
        before = stats["class_counts_before"].get(cls, 0)
        after = stats["class_counts_after"].get(cls, 0)
        delta = after - before
        sign = "+" if delta > 0 else ""
        print(f"    {cls}: {before} -> {after} ({sign}{delta})")
    print(f"")
    print(f"  Top path families newly classified:")
    for p in mapped_proposals:
        print(f"    {p['prefix']} -> {p['proposed_class']}")
    print(f"")
    print(f"  Confirmation: No existing classified commits changed class")
    print(f"    (all transitions are UNKNOWN -> known additions only)")
    print(f"")
    print(f"  Scratch deliverables:")
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


def main():
    metrics, overlay = load_data()
    step1_snapshot()
    commit_index, unknown_commits = step2_isolate_unknowns(metrics, overlay)
    clusters, significant = step3_cluster(commit_index, unknown_commits)
    mapped = step4_write_proposal()
    step5_diff_preview(mapped)
    stats = step6_simulate(metrics, overlay)
    step7_summary(stats, mapped)


if __name__ == "__main__":
    main()
