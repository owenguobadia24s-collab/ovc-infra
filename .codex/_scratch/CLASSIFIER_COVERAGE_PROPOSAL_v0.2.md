# Classifier Coverage Proposal v0.2

## Overview

This proposal extends the v0.1 classifier with additive path-pattern rules
to reduce UNKNOWN classifications for early-repo commits.
No existing rules are removed or modified. All mappings are justified by
structural similarity to paths already covered by the existing taxonomy.

## Methodology

1. Extracted all paths classified UNKNOWN under v0.1 (160 commits)
2. Clustered by top-level directory prefix (24 clusters)
3. For each cluster, compared path contents against existing class definitions
4. Proposed mapping to existing class only when structural role is unambiguous
5. Left as UNKNOWN when no clear single-class mapping exists

## Proposed Mappings

| # | Prefix | Proposed Class | New Pattern | Commits |
|---|--------|---------------|-------------|---------|
| 1 | `docs/` | **B** | `docs/**` | - |
| 2 | `contracts/` | **B** | `contracts/**` | - |
| 3 | `specs/` | **B** | `specs/**` | - |
| 4 | `reports/ (non-path1)` | **B** | `reports/** (excluding reports/path1/)` | - |
| 5 | `releases/` | **B** | `releases/**` | - |
| 6 | `(root) .md/.txt files` | **B** | `root-level doc-extension files` | - |
| 7 | `sql/ (non-path1)` | **C** | `sql/** (excluding sql/path1/)` | - |
| 8 | `.codex/` | **C** | `.codex/**` | - |
| 9 | `infra/` | **C** | `infra/**` | - |
| 10 | `pine/` | **C** | `pine/**` | - |
| 11 | `Tetsu/` | **C** | `Tetsu/**` | - |
| 12 | `trajectory_families/` | **C** | `trajectory_families/**` | - |
| 13 | `_archive/` | **C** | `_archive/**` | - |
| 14 | `_quarantine/` | **C** | `_quarantine/**` | - |
| 15 | `configs/` | **C** | `configs/**` | - |
| 16 | `schema/` | **C** | `schema/**` | - |
| 17 | `artifacts/` | **A** | `artifacts/**` | - |
| 18 | `.github/ (non-workflows)` | **E** | `.github/** (excluding .github/workflows/)` | - |
| 19 | `.vscode/` | **E** | `.vscode/**` | - |
| 20 | `ovc-webhook/` | **E** | `ovc-webhook/**` | - |

## Detailed Justifications

### `docs/` -> B

**Pattern**: `docs/**`

docs/ paths not already covered by B (docs/contracts/, docs/governance/, docs/phase_2_2/) include architecture specs, baselines, catalogs, doctrine, evidence packs, history, and operations documentation. All are documentation artifacts. Class B already covers three docs/ subdirectories. Extending B to all docs/ is consistent: the taxonomy defines B as documentation requiring ratification. Observed paths: docs/architecture/, docs/baselines/, docs/catalogs/, docs/doctrine/, docs/evidence_pack/, docs/history/, docs/operations/, docs/REPO_MAP/, etc.

### `contracts/` -> B

**Pattern**: `contracts/**`

contracts/ contains governance contract JSON files (derived_feature_set_v0.1.json, eval_contract_v0.1.json, export_contract_v0.1.json, run_artifact_spec_v0.1.json). Class B covers docs/contracts/ already. Top-level contracts/ serves the same structural role: machine-readable governance contract definitions.

### `specs/` -> B

**Pattern**: `specs/**`

specs/ contains specification documents (all .md): dashboards_v0.1.md, outcome_sql_spec_v0.1.md, research_query_pack_v0.1.md, etc. These are documentation artifacts structurally analogous to docs/ content covered by B.

### `reports/ (non-path1)` -> B

**Pattern**: `reports/** (excluding reports/path1/)`

reports/ paths outside reports/path1/ include validation reports (reports/validation/C1_v0_1_validation.md) and verification output captures (reports/verification/). These are documentation-class artifacts: textual reports and captured outputs for audit. reports/path1/ remains A.

### `releases/` -> B

**Pattern**: `releases/**`

releases/ contains release documentation (releases/ovc-v0.1-spine.md). Structurally analogous to docs/ documentation covered by B.

### `(root) .md/.txt files` -> B

**Pattern**: `root-level doc-extension files`

Root-level files with documentation extensions (e.g., README.md) are repo-level documentation artifacts. Class B covers documentation. .gitignore/.gitattributes already covered by E; remaining root docs -> B.

### `sql/ (non-path1)` -> C

**Pattern**: `sql/** (excluding sql/path1/)`

sql/ paths outside sql/path1/ contain schema definitions and query files (sql/schema_v01.sql, sql/derived_v0_1.sql). Class C covers code artifacts (scripts/, src/). SQL schema files are code-adjacent. sql/path1/ remains A.

### `.codex/` -> C

**Pattern**: `.codex/**`

.codex/ paths outside CHECKS/ are governance tooling infrastructure. .codex/CHECKS/ is already class C. All .codex/ content serves the same structural role. Observed: .codex/CHECKS/ (already C), .codex/_scratch/ and other governance infra paths.

### `infra/` -> C

**Pattern**: `infra/**`

infra/ contains infrastructure code: TypeScript source (infra/ovc-webhook/src/index.ts), test files, package.json, SQL migrations, tsconfig. These are code artifacts structurally analogous to src/ and scripts/ covered by C.

### `pine/` -> C

**Pattern**: `pine/**`

pine/ contains PineScript code files (OVC_v0_1.pine, export_module_v0.1.pine). These are executable script artifacts structurally analogous to src/ code covered by C.

### `Tetsu/` -> C

**Pattern**: `Tetsu/**`

Tetsu/ contains code files across 58 unique paths and 16 commits. Structurally resembles a code/tool directory analogous to src/ or scripts/ covered by C.

### `trajectory_families/` -> C

**Pattern**: `trajectory_families/**`

trajectory_families/ contains Python modules (__init__.py, clustering.py, distance.py, features.py, etc.). These are source code artifacts directly analogous to src/ covered by C.

### `_archive/` -> C

**Pattern**: `_archive/**`

_archive/ contains archived code artifacts: scripts, SQL, checks, deploy scripts. These are code artifacts that have been archived but retain their structural role as code (analogous to scripts/, src/, .codex/CHECKS/).

### `_quarantine/` -> C

**Pattern**: `_quarantine/**`

_quarantine/ contains quarantined code: GitHub workflow YAML, SQL views, Python stubs. These are code artifacts under quarantine but structurally analogous to src/, scripts/, .github/workflows/ covered by C.

### `configs/` -> C

**Pattern**: `configs/**`

configs/ contains JSON configuration files used by code (threshold_packs/c3_example_pack_v1.json, etc.). Configuration files are code-adjacent artifacts structurally analogous to content under scripts/ or src/ covered by C.

### `schema/` -> C

**Pattern**: `schema/**`

schema/ contains database schema definitions (applied_migrations.json, required_objects.txt). These are code-adjacent infrastructure artifacts analogous to sql/ schemas covered by C.

### `artifacts/` -> A

**Pattern**: `artifacts/**`

artifacts/ contains evidence and validation outputs: derived_validation_report.json, path1_replay_report.json, change_classifier.json. These are evidence artifacts structurally analogous to reports/path1/ output covered by A.

### `.github/ (non-workflows)` -> E

**Pattern**: `.github/** (excluding .github/workflows/)`

.github/ paths outside workflows/ include copilot-instructions.md, copilot-instructions.txt, pull_request_template.md. These are repo configuration files structurally analogous to .gitignore/.gitattributes covered by E.

### `.vscode/` -> E

**Pattern**: `.vscode/**`

.vscode/ contains editor configuration (settings.json). This is repo/editor configuration structurally analogous to .gitignore covered by E.

### `ovc-webhook/` -> E

**Pattern**: `ovc-webhook/**`

ovc-webhook/vscode/settings.json is an editor configuration artifact analogous to .vscode/ or .gitignore covered by E.

## Clusters Remaining UNKNOWN

### `research/`

research/ contains 55 unique paths across 9 commits mixing documentation, exploratory code, and data. No single existing class covers this mixed role. Remains UNKNOWN pending possible new class definition.

### `CLAIMS/`

CLAIMS/ has only 2 commits and 2 paths (ANCHOR_INDEX_v0_1.csv, CLAIM_BINDING_v0_1.md). Too few data points and the structural role (claim bindings) does not clearly map to an existing class. Remains UNKNOWN.

### `Work Timeline/`

Work Timeline/ has only 1 commit and 1 path (020226.txt). Insufficient data. Does not clearly map to any existing class. Remains UNKNOWN.

## Compatibility Notes

- All v0.1 rules remain unchanged
- v0.2 rules are additive: they can only add classes, never remove
- A path that matched class X under v0.1 will still match X under v0.2
- UNKNOWN is only removed when at least one non-UNKNOWN class is assigned

