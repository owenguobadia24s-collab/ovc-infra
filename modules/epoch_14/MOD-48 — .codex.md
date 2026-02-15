# MOD-48 — .codex

## Purpose
This module consistently exists to capture commit activity for `MOD-48` across 2 selected sub-range(s), centered on `DIR:.codex` basis tokens and co-changed paths `.codex/CHECKS/`, `reports/path1/`, `sql/path1/`.

## Owned Paths
### OWNS
- `.codex/` (evidence: 8 touches; example commits: `44403d3`, `f5318b3`)
### DOES NOT OWN
- `Tetsu/` (evidence: 5 touches; example commits: `44403d3`, `f5318b3`)
- `./` (evidence: 3 touches; example commits: `44403d3`, `f5318b3`)
- `reports/` (evidence: 1 touches; example commits: `44403d3`, `f5318b3`)
- `sql/` (evidence: 1 touches; example commits: `44403d3`, `f5318b3`)
### AMBIGUOUS
- Boundary with co-changed paths `Tetsu`, `./`, `reports`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `.codex/CHECKS/rg_index.ps1` — changed in selected sub-range evidence. (evidence: 3 touches; example commits: `44403d3`, `f5318b3`)
- `Tetsu/.obsidian/workspace.json` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `44403d3`, `f5318b3`)
- `.codex/CHECKS/coverage_audit.py` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `44403d3`, `f5318b3`)
- `sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_res_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `44403d3`, `f5318b3`)
- `sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_lid_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `44403d3`, `f5318b3`)

## Invariants (Observed)
- INV-01: `MOD-48` is selected at support `8/9` under epoch `14` rules. (evidence: 7 commits; files: `.codex/CHECKS/rg_index.ps1`, `Tetsu/.obsidian/workspace.json`, `.codex/CHECKS/coverage_audit.py`; example commits: `44403d3`, `f5318b3`)
- INV-02: Evidence scope is fixed to 2 sub-range(s) from `4c245c6e90eec04733739f8879d1868e977f0257` to `3dc06d8df45105eb06284c476f32243021c2a8b9`. (evidence: 7 commits; files: `.codex/CHECKS/rg_index.ps1`, `Tetsu/.obsidian/workspace.json`, `.codex/CHECKS/coverage_audit.py`; example commits: `44403d3`, `f5318b3`)
- INV-03: Basis token(s) `.codex` are explicitly encoded in selected candidate label `DIR:.codex`. (evidence: 7 commits; files: `.codex/CHECKS/rg_index.ps1`, `Tetsu/.obsidian/workspace.json`, `.codex/CHECKS/coverage_audit.py`; example commits: `44403d3`, `f5318b3`)

## Interfaces
### Upstream
- `docs/baselines/MODULE_CANDIDATES_v0.1.md` — selected candidate and commit ranges.
- `git` commit history for selected sub-range(s) — mandatory evidence input.
- `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl` — tag evidence source.
### Downstream
- UNKNOWN (no evidence)

## Non-Goals
- UNKNOWN (no evidence)

## Ambiguities / Pressure Points
- Support tie resolved by `document_order` among `MOD-48`, `MOD-49`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
28: | 14 | 9 | .codex | 88.89% | codex_runtime | 88.89% | OK |
2322: #### MOD-48 — DIR:.codex
2327: - 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
2328: - 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9
2372: - INV-01: Candidate matches 8/9 commits. (support: 8/9)
```
- Anchor commits
```text
4c245c6 4c245c6e90eec04733739f8879d1868e977f0257 2026-02-02T14:36:41Z Add codex audit harness (prompts + checks); ignore runtime and runs
3dc06d8 3dc06d8df45105eb06284c476f32243021c2a8b9 2026-02-02T21:06:37Z codex: non-spec graph NodeID rename planner + applied safe renames
```
- Inventory summaries (>=2 threshold)
  - Directories
- `.codex/CHECKS/` (11)
- `reports/path1/` (9)
- `sql/path1/` (3)
- `Tetsu/.obsidian/` (2)
  - Files
- `.codex/CHECKS/rg_index.ps1` (3)
- `Tetsu/.obsidian/workspace.json` (2)
- `.codex/CHECKS/coverage_audit.py` (2)
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `codex_runtime` (6)
- `validation` (4)
- `repo_maze` (4)
- `evidence_runs` (2)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426` (execution range: `4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426`)
```text
git log --oneline 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
44403d3 Merge branches 'main' and 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
f5318b3 path1 evidence: p1_20260202_GBPUSD_20260201_len5d_31f19f8a

git log --name-only --pretty=format: 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426 | sort | uniq -c | sort -nr
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/meta.json
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/RUN.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md

git log --name-only --pretty=format: 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 reports/path1/
   3 sql/path1/

git log --pretty=format:%s 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260202_GBPUSD_20260201_len5d_31f19f8a
   1 Merge branches 'main' and 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```
  - Sub-range 2: `85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9` (execution range: `85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9`)
```text
git log --oneline 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9
3dc06d8 codex: non-spec graph NodeID rename planner + applied safe renames
f758bd1 Update timestamp generation in coverage_audit.py and refactor rg_index.ps1 for improved readability and functionality
b19cf71 Refactor rg_index.ps1 queries and update workspace.json for GRAPH_51__EXTERNAL_STORES; add preflight_parse.ps1 and config.toml for script validation
731fe26 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
d844f2e Audit Harness_V1

git log --name-only --pretty=format: 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9 | sort | uniq -c | sort -nr
   3 .codex/CHECKS/rg_index.ps1
   2 Tetsu/.obsidian/workspace.json
   2 .codex/CHECKS/coverage_audit.py
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/OPTION INTERNAL PIPELINE GRAPH.md
   1 .codex/config.toml
   1 .codex/PROMPTS/PASS_1_READONLY_GRAPH_AUDIT.md
   1 .codex/CHECKS/snapshot_tree.ps1
   1 .codex/CHECKS/run_graph_nodeid_rename_plan.ps1
   1 .codex/CHECKS/run_audit_pack.ps1
   1 .codex/CHECKS/preflight_parse.ps1
   1 .codex/CHECKS/plan_graph_nodeid_renames.py
   1 .codex/CHECKS/apply_graph_nodeid_renames.py

git log --name-only --pretty=format: 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  11 .codex/CHECKS/
   2 Tetsu/.obsidian/
   1 Tetsu/OVC_REPO_MAZE/
   1 .codex/config.toml/
   1 .codex/PROMPTS/

git log --pretty=format:%s 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9 | sort | uniq -c | sort -nr
   1 codex: non-spec graph NodeID rename planner + applied safe renames
   1 Update timestamp generation in coverage_audit.py and refactor rg_index.ps1 for improved readability and functionality
   1 Refactor rg_index.ps1 queries and update workspace.json for GRAPH_51__EXTERNAL_STORES; add preflight_parse.ps1 and config.toml for script validation
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 Audit Harness_V1
```
- Ledger evidence
```text
   6 codex_runtime
   4 validation
   4 repo_maze
   2 evidence_runs
```
