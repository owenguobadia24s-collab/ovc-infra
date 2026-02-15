# MOD-45 — cluster_dot_slash_.github_.vscode_artifacts_docs_reports_scripts_sql_tests_tetsu

## Purpose
This module consistently exists to capture commit activity for `MOD-45` across 17 selected sub-range(s), centered on `CLUSTER:./|.github|.vscode|artifacts|docs|reports|scripts|sql|tests|tetsu` basis tokens and co-changed paths `reports/path1/`, `sql/path1/`, `docs/specs/`.

## Owned Paths
### OWNS
- `./` (evidence: 10 touches; example commits: `a512105`, `d2e8162`)
- `.github/` (evidence: 17 touches; example commits: `a512105`, `d2e8162`)
- `.vscode/` (evidence: 3 touches; example commits: `a512105`, `d2e8162`)
- `artifacts/` (evidence: 3 touches; example commits: `a512105`, `d2e8162`)
- `docs/` (evidence: 23 touches; example commits: `a512105`, `d2e8162`)
- `reports/` (evidence: 42 touches; example commits: `a512105`, `d2e8162`)
- `scripts/` (evidence: 23 touches; example commits: `a512105`, `d2e8162`)
- `sql/` (evidence: 27 touches; example commits: `a512105`, `d2e8162`)
- `tests/` (evidence: 5 touches; example commits: `a512105`, `d2e8162`)
- `tetsu/` (evidence: UNKNOWN (no evidence); example commits: `a512105`, `d2e8162`)
### DOES NOT OWN
- `Tetsu/` (evidence: 6 touches; example commits: `a512105`, `d2e8162`)
### AMBIGUOUS
- Boundary with co-changed paths `Tetsu`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `reports/path1/evidence/INDEX.md` — changed in selected sub-range evidence. (evidence: 20 touches; example commits: `a512105`, `d2e8162`)
- `reports/path1/evidence/RUN_QUEUE.csv` — changed in selected sub-range evidence. (evidence: 18 touches; example commits: `a512105`, `d2e8162`)
- `scripts/path1/run_evidence_queue.py` — changed in selected sub-range evidence. (evidence: 8 touches; example commits: `a512105`, `d2e8162`)
- `.github/workflows/path1_evidence_queue.yml` — changed in selected sub-range evidence. (evidence: 7 touches; example commits: `a512105`, `d2e8162`)
- `scripts/path1/validate_post_run.py` — changed in selected sub-range evidence. (evidence: 3 touches; example commits: `a512105`, `d2e8162`)

## Invariants (Observed)
- INV-01: `MOD-45` is selected at support `60/94` under epoch `13` rules. (evidence: 47 commits; files: `reports/path1/evidence/INDEX.md`, `reports/path1/evidence/RUN_QUEUE.csv`, `scripts/path1/run_evidence_queue.py`; example commits: `a512105`, `d2e8162`)
- INV-02: Evidence scope is fixed to 17 sub-range(s) from `1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8` to `f5318b3c33952781932b148d44c6909f78972a8e`. (evidence: 47 commits; files: `reports/path1/evidence/INDEX.md`, `reports/path1/evidence/RUN_QUEUE.csv`, `scripts/path1/run_evidence_queue.py`; example commits: `a512105`, `d2e8162`)
- INV-03: Basis token(s) `./, .github, .vscode, artifacts, docs, reports, scripts, sql, tests, tetsu` are explicitly encoded in selected candidate label `CLUSTER:./|.github|.vscode|artifacts|docs|reports|scripts|sql|tests|tetsu`. (evidence: 47 commits; files: `reports/path1/evidence/INDEX.md`, `reports/path1/evidence/RUN_QUEUE.csv`, `scripts/path1/run_evidence_queue.py`; example commits: `a512105`, `d2e8162`)

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
- UNKNOWN (no evidence)

## Evidence Appendix
- Target selection excerpt
```text
27: | 13 | 94 | reports | 51.06% | evidence_runs | 51.06% | OK |
2080: #### MOD-45 — CLUSTER:./|.github|.vscode|artifacts|docs|reports|scripts|sql|tests|tetsu
2085: - 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78
2086: - d2e816266340a2e57b9432a886c3d9fef230be28..d2e816266340a2e57b9432a886c3d9fef230be28
2087: - 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc
2088: - a67ef074544d1c75e30eb74759418ea197dfb5f0..a67ef074544d1c75e30eb74759418ea197dfb5f0
2089: - d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58
2090: - ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2
2091: - e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9
2092: - ee6eedeaae948218edeae3b98de8d640036a57ca..ee6eedeaae948218edeae3b98de8d640036a57ca
2093: - 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a
2094: - 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea
2095: - 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078
2096: - fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494
2097: - a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be
2098: - 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762
2099: - 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622
2100: - 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9
2101: - 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e
2155: - INV-01: Candidate matches 60/94 commits. (support: 60/94)
```
- Anchor commits
```text
1774ef5 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8 2026-01-20T10:19:30Z Path 1 Github Action Pipe
f5318b3 f5318b3c33952781932b148d44c6909f78972a8e 2026-02-02T06:44:44Z path1 evidence: p1_20260202_GBPUSD_20260201_len5d_31f19f8a
```
- Inventory summaries (>=2 threshold)
  - Directories
- `reports/path1/` (259)
- `sql/path1/` (61)
- `docs/specs/` (22)
- `docs/history/` (20)
- `docs/contracts/` (18)
- `Tetsu/OVC_REPO_MAZE/` (18)
- `scripts/path1/` (16)
- `.github/workflows/` (16)
- `./` (12)
- `docs/operations/` (11)
- `docs/runbooks/` (10)
- `docs/governance/` (10)
- `docs/REPO_MAP/` (10)
- `docs/architecture/` (9)
- `Tetsu/.obsidian/` (9)
- `scripts/run/` (7)
- `docs/validation/` (5)
- `docs/pipeline/` (4)
- `docs/doctrine/` (4)
- `scripts/path1_replay/` (3)
- `reports/verification/` (3)
- `tests/fixtures/` (2)
- `sql/derived/` (2)
- `scripts/validate/` (2)
- `scripts/path1_seal/` (2)
- `scripts/export/` (2)
- `scripts/dev/` (2)
- `infra/ovc-webhook/` (2)
- `docs/state_plane/` (2)
- `docs/path2/` (2)
- `docs/path1/` (2)
- `docs/evidence_pack_overlays_v0_3.md/` (2)
- `docs/OVERLAY_V0_3_TESTING.md/` (2)
- `docs/OVERLAY_V0_3_HARDENING_SUMMARY.md/` (2)
- `artifacts/option_c/` (2)
- `.vscode/settings.json/` (2)
  - Files
- `reports/path1/evidence/INDEX.md` (20)
- `reports/path1/evidence/RUN_QUEUE.csv` (18)
- `scripts/path1/run_evidence_queue.py` (8)
- `.github/workflows/path1_evidence_queue.yml` (7)
- `scripts/path1/validate_post_run.py` (3)
- `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md` (3)
- `docs/history/path1/EVIDENCE_RUNS_HOWTO.md` (3)
- `.gitignore` (3)
- `.github/workflows/main.yml` (3)
- `scripts/run/run_option_c.sh` (2)
- `scripts/run/run_option_c.ps1` (2)
- `infra/ovc-webhook/ovc-infra.code-workspace` (2)
- `docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md` (2)
- `docs/runbooks/option_b_runbook.md` (2)
- `docs/path2/ROADMAP_v0_1.md` (2)
- `docs/history/path1/scores/SCORE_LIBRARY_v1.md` (2)
- `docs/history/path1/research_views_option_c_v0.1.md` (2)
- `docs/history/path1/SCORE_INVENTORY_v1.md` (2)
- `docs/history/path1/RUN_CONVENTIONS.md` (2)
- `docs/history/path1/README.md` (2)
- `docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md` (2)
- `docs/history/path1/OPTION_B_PATH1_STATUS.md` (2)
- `docs/evidence_pack_overlays_v0_3.md` (2)
- `docs/OVERLAY_V0_3_TESTING.md` (2)
- `docs/OVERLAY_V0_3_HARDENING_SUMMARY.md` (2)
- `Tetsu/.obsidian/workspace.json` (2)
- `.vscode/settings.json` (2)
  - Repeated commit subjects (exact)
- `Path1: automated evidence run` (10)
- `Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra` (3)
  - Repeated ledger tags
- `evidence_runs` (33)
- `scripts_general` (19)
- `ci_workflows` (14)
- `validation` (5)
- `tests` (5)
- `governance_contracts` (5)
- `repo_maze` (3)
- `operations` (2)
- `infra` (2)
- `artifacts` (2)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78` (execution range: `1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78`)
```text
git log --oneline 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78
a512105 Path1: add RUN_QUEUE.csv and update gitignore for path1 reports

git log --name-only --pretty=format: 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78 | sort | uniq -c | sort -nr
   1 reports/path1/evidence/RUN_QUEUE.csv
   1 .gitignore

git log --name-only --pretty=format: 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 reports/path1/
   1 ./

git log --pretty=format:%s 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78 | sort | uniq -c | sort -nr
   1 Path1: add RUN_QUEUE.csv and update gitignore for path1 reports
```
  - Sub-range 2: `d2e816266340a2e57b9432a886c3d9fef230be28..d2e816266340a2e57b9432a886c3d9fef230be28` (execution range: `d2e816266340a2e57b9432a886c3d9fef230be28^..d2e816266340a2e57b9432a886c3d9fef230be28`)
```text
git log --oneline d2e816266340a2e57b9432a886c3d9fef230be28^..d2e816266340a2e57b9432a886c3d9fef230be28
d2e8162 Path1: fix CSV comment parsing + add INDEX.md for existing runs

git log --name-only --pretty=format: d2e816266340a2e57b9432a886c3d9fef230be28^..d2e816266340a2e57b9432a886c3d9fef230be28 | sort | uniq -c | sort -nr
   1 scripts/path1/run_evidence_queue.py
   1 reports/path1/evidence/README.md
   1 reports/path1/evidence/INDEX.md
   1 reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md

git log --name-only --pretty=format: d2e816266340a2e57b9432a886c3d9fef230be28^..d2e816266340a2e57b9432a886c3d9fef230be28 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   3 reports/path1/
   1 scripts/path1/

git log --pretty=format:%s d2e816266340a2e57b9432a886c3d9fef230be28^..d2e816266340a2e57b9432a886c3d9fef230be28 | sort | uniq -c | sort -nr
   1 Path1: fix CSV comment parsing + add INDEX.md for existing runs
```
  - Sub-range 3: `4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc` (execution range: `4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc`)
```text
git log --oneline 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc
19ae34b Patch Path 1 Evidence Queue: Add concurrency control and artifact verification steps

git log --name-only --pretty=format: 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc | sort | uniq -c | sort -nr
   1 scripts/path1/run_evidence_queue.py
   1 .github/workflows/path1_evidence_queue.yml

git log --name-only --pretty=format: 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 scripts/path1/
   1 .github/workflows/

git log --pretty=format:%s 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc | sort | uniq -c | sort -nr
   1 Patch Path 1 Evidence Queue: Add concurrency control and artifact verification steps
```
  - Sub-range 4: `a67ef074544d1c75e30eb74759418ea197dfb5f0..a67ef074544d1c75e30eb74759418ea197dfb5f0` (execution range: `a67ef074544d1c75e30eb74759418ea197dfb5f0^..a67ef074544d1c75e30eb74759418ea197dfb5f0`)
```text
git log --oneline a67ef074544d1c75e30eb74759418ea197dfb5f0^..a67ef074544d1c75e30eb74759418ea197dfb5f0
a67ef07 Add post-run validation script and update README with usage instructions

git log --name-only --pretty=format: a67ef074544d1c75e30eb74759418ea197dfb5f0^..a67ef074544d1c75e30eb74759418ea197dfb5f0 | sort | uniq -c | sort -nr
   1 scripts/path1/validate_post_run.py
   1 docs/path1/README.md

git log --name-only --pretty=format: a67ef074544d1c75e30eb74759418ea197dfb5f0^..a67ef074544d1c75e30eb74759418ea197dfb5f0 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 scripts/path1/
   1 docs/path1/

git log --pretty=format:%s a67ef074544d1c75e30eb74759418ea197dfb5f0^..a67ef074544d1c75e30eb74759418ea197dfb5f0 | sort | uniq -c | sort -nr
   1 Add post-run validation script and update README with usage instructions
```
  - Sub-range 5: `d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58` (execution range: `d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58`)
```text
git log --oneline d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58
83f3d21 Enhance evidence run queue management: add status updates and actual date tracking for completed runs
fcbe946 Merge pull request #8 from owenguobadia24s-collab/evidence-run-20260120-123211

git log --name-only --pretty=format: d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58 | sort | uniq -c | sort -nr
   1 scripts/path1/run_evidence_queue.py
   1 reports/path1/evidence/RUN_QUEUE.csv

git log --name-only --pretty=format: d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 scripts/path1/
   1 reports/path1/

git log --pretty=format:%s d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58 | sort | uniq -c | sort -nr
   1 Merge pull request #8 from owenguobadia24s-collab/evidence-run-20260120-123211
   1 Enhance evidence run queue management: add status updates and actual date tracking for completed runs
```
  - Sub-range 6: `ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2` (execution range: `ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2`)
```text
git log --oneline ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2
66ecada Enhance PR creation process: use PAT for auto-merge and add validation for OVC_PR_BOT_TOKEN secret
3245965 Enhance evidence run management: generate RUN_QUEUE_RESOLVED.csv for queue reconciliation and update workflow for automated PR creation
221a982 Merge pull request #10 from owenguobadia24s-collab/evidence-run-20260120-141256
7cb0896 Path 1 Evidence Run(s) - Automated
d4b1a6e Enhance evidence run scripts: add warnings for local queue status and validation scope

git log --name-only --pretty=format: ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2 | sort | uniq -c | sort -nr
   3 .github/workflows/path1_evidence_queue.yml
   1 sql/path1/evidence/runs/p1_20260120_015/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_015/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_015/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_014/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_014/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_014/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_013/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_013/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_013/study_dis_v1_1.sql
   1 scripts/path1/validate_post_run.py
   1 scripts/path1/run_evidence_queue.py
   1 scripts/path1/generate_queue_resolved.py
   1 reports/path1/evidence/runs/p1_20260120_015/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_015/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_015/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_015/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_015/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_015/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_015/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_014/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_014/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_014/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_014/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_014/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_014/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_014/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_013/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_013/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_013/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_013/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_013/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_013/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_013/DIS_v1_1_evidence.md
   1 reports/path1/evidence/RUN_QUEUE_RESOLVED.csv
   1 reports/path1/evidence/RUN_QUEUE.csv
   1 reports/path1/evidence/INDEX.md

git log --name-only --pretty=format: ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  24 reports/path1/
   9 sql/path1/
   3 scripts/path1/
   3 .github/workflows/

git log --pretty=format:%s ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2 | sort | uniq -c | sort -nr
   1 Path 1 Evidence Run(s) - Automated
   1 Merge pull request #10 from owenguobadia24s-collab/evidence-run-20260120-141256
   1 Enhance evidence run scripts: add warnings for local queue status and validation scope
   1 Enhance evidence run management: generate RUN_QUEUE_RESOLVED.csv for queue reconciliation and update workflow for automated PR creation
   1 Enhance PR creation process: use PAT for auto-merge and add validation for OVC_PR_BOT_TOKEN secret
```
  - Sub-range 7: `e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9` (execution range: `e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9`)
```text
git log --oneline e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9
bf51650 Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs; add backfill_m15 workflow; ignore pytest temp dirs
b092afc Quadrant state plane evidence runner and related SQL views
27354e7 Repo-restructuring

git log --name-only --pretty=format: e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9 | sort | uniq -c | sort -nr
   2 docs/runbooks/option_b_runbook.md
   1 tests/test_evidence_pack_manifest.py
   1 tests/test_dst_audit.py
   1 src/backfill_oanda_m15_checkpointed.py
   1 sql/path1/evidence/runs/p1_20260120_031/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_031/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_031/study_dis_v1_1.sql
   1 sql/path1/db_patches/patch_m15_raw_20260122.sql
   1 sql/derived/v_ovc_state_plane_v0_2.sql
   1 sql/derived/v_ovc_state_plane_daypath_v0_2.sql
   1 sql/06_state_plane_threshold_pack_v0_2.sql
   1 scripts/validate/validate_day.ps1
   1 scripts/validate/pipeline_status.py
   1 scripts/run/run_option_c_wrapper.py
   1 scripts/run/run_option_c_with_artifact.sh
   1 scripts/run/run_option_c.sh
   1 scripts/run/run_option_c.ps1
   1 scripts/run/run_migration.py
   1 scripts/path1/validate_post_run.py
   1 scripts/path1/run_state_plane.py
   1 scripts/path1/run_evidence_queue.py
   1 scripts/path1/build_evidence_pack_v0_2.py
   1 scripts/local/verify_local.ps1
   1 scripts/export/oanda_export_2h_day.py
   1 scripts/export/notion_sync.py
   1 scripts/dev/check_dst_mapping.py
   1 scripts/deploy/deploy_worker.ps1
   1 reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2/trajectory.png
   1 reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2/trajectory.csv
   1 reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2/quadrant_string.txt
   1 reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2/path_metrics.json
   1 reports/path1/evidence/runs/p1_20260121_001/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_031/pack_build.jsonl
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-L-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-K-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-J-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-I-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-H-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-G-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-F-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-E-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-D-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-C-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-B-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221213-A-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-L-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-K-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-J-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-I-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-H-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-G-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-F-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-E-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-D-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-C-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-B-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-A-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-L-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-K-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-J-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-I-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-H-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-G-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-F-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-E-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-D-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-C-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-B-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-A-GBPUSD.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/qc_report.json
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/pack_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/meta.json
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/manifest_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/manifest.json
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/data_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/data_manifest_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/data_manifest.json
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/KL_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/KL_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/KL_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/IJ_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/IJ_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/IJ_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/GH_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/GH_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/GH_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/EF_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/EF_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/EF_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/CD_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/CD_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/CD_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/AB_2022-12-13.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/AB_2022-12-12.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/context/4h/AB_2022-12-11.csv
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/build_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/build_manifest_sha256.txt
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/build_manifest.json
   1 reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/backbone_2h.csv
   1 reports/path1/evidence/runs/p1_20260120_031/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_031/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_031/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_031/DIS_v1_1_evidence.md
   1 reports/path1/evidence/RUN_QUEUE.csv
   1 reports/path1/evidence/INDEX.md
   1 reports/README.md
   1 pytest.ini
   1 infra/ovc-webhook/ovc-infra.code-workspace
   1 docs/validation/tape_validation_harness.md
   1 docs/validation/pine_export_consistency.md
   1 docs/validation/mapping_validation_report_v0.1.md
   1 docs/validation/WORKFLOW_AUDIT_2026-01-20.md
   1 docs/validation/VERIFICATION_REPORT_v0.1.md
   1 docs/state_plane/STATE_PLANE_v0_2.md
   1 docs/state_plane/RUN_STATE_PLANE.md
   1 docs/specs/system/run_report_spec_v0.1.md
   1 docs/specs/system/research_sql_spec_v0.1.md
   1 docs/specs/system/research_query_pack_v0.1.md
   1 docs/specs/system/parsing_validation_rules_v0.1.md
   1 docs/specs/system/outcomes_system_v0.1.md
   1 docs/specs/system/outcome_sql_spec_v0.1.md
   1 docs/specs/system/dashboards_v0.1.md
   1 docs/specs/system/Quadrant State Plane v0.2.md
   1 docs/specs/OPTION_C_OUTCOMES_v0.1.md
   1 docs/specs/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/specs/OPTION_C_CHARTER_v0.1.md
   1 docs/specs/OPTION_B_CHARTER_v0.1.md
   1 docs/specs/OPTION_B_C3_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/specs/OPTION_B_C3_FEATURES_v0.1.md
   1 docs/specs/OPTION_B_C3_CHARTER_v0.1.md
   1 docs/specs/OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/specs/OPTION_B_C2_FEATURES_v0.1.md
   1 docs/specs/OPTION_B_C2_CHARTER_v0.1.md
   1 docs/specs/OPTION_B_C1_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/specs/OPTION_B_C1_FEATURES_v0.1.md
   1 docs/runbooks/option_threshold_registry_runbook.md
   1 docs/runbooks/option_c_runbook.md
   1 docs/runbooks/option_b2_runbook.md
   1 docs/runbooks/option_b1_runbook.md
   1 docs/runbooks/c3_entry_checklist.md
   1 docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md
   1 docs/runbooks/RUN_ARTIFACT_IMPLEMENTATION_NOTES.md
   1 docs/option_d/MODEL_REGISTRY_SPEC.md
   1 docs/operations/versioned_config_proposal_v0.1.md
   1 docs/operations/step8_readiness.md
   1 docs/operations/secrets_and_env.md
   1 docs/operations/ovc_current_workflow.md
   1 docs/operations/WORKFLOW_STATUS.md
   1 docs/operations/WORKER_PIPELINE.md
   1 docs/operations/OPERATING_BASE.validation.md
   1 docs/operations/OPERATING_BASE.md
   1 docs/operations/OPERATING_BASE.index.md
   1 docs/operations/NEON_STAGING.md
   1 docs/operations/BUILD_PHASE.md
   1 docs/history/path1/scores/SCORE_LIBRARY_v1.md
   1 docs/history/path1/research_views_option_c_v0.1.md
   1 docs/history/path1/SCORE_INVENTORY_v1.md
   1 docs/history/path1/RUN_CONVENTIONS.md
   1 docs/history/path1/README.md
   1 docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md
   1 docs/history/path1/OPTION_B_PATH1_STATUS.md
   1 docs/history/path1/EVIDENCE_RUNS_HOWTO.md
   1 docs/governance/decisions.md
   1 docs/governance/GOVERNANCE_RULES_v0.1.md
   1 docs/governance/BRANCH_POLICY.md
   1 docs/evidence_pack/EVIDENCE_PACK_v0_2.md
   1 docs/doctrine/ovc_logging_doctrine_v0.1.md
   1 docs/doctrine/OVC_DOCTRINE.md
   1 docs/doctrine/IMMUTABILITY_NOTICE.md
   1 docs/doctrine/GATES.md
   1 docs/contracts/outcomes_definitions_v0.1.md
   1 docs/contracts/option_d_ops_boundary.md
   1 docs/contracts/option_c_boundary.md
   1 docs/contracts/min_contract_alignment.md
   1 docs/contracts/ingest_boundary.md
   1 docs/contracts/derived_layer_boundary.md
   1 docs/contracts/c_layer_boundary_spec_v0.1.md
   1 docs/contracts/c3_semantic_contract_v0_1.md
   1 docs/contracts/PATH2_CONTRACT_v1_0.md
   1 docs/architecture/ovc_metric_architecture.md
   1 docs/architecture/metric_trial_log_noncanonical_v0.md
   1 docs/architecture/metric_map_pine_to_c_layers.md
   1 docs/architecture/derived_metric_registry_v0.1.md
   1 docs/architecture/dashboard_mapping_v0.1.md
   1 docs/architecture/PRUNING_CANDIDATES_v0.1.md
   1 docs/architecture/PIPELINE_REALITY_MAP_v0.1.md
   1 docs/architecture/PIPELINE_REALITY_MAP_v0.1.changelog.md
   1 docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md
   1 docs/README_ORG_NOTES.md
   1 configs/threshold_packs/state_plane_v0_2_default_v1.json
   1 artifacts/option_c/sanity_local/spotchecks_sanity_local.txt
   1 artifacts/option_c/sanity_local/run_report_sanity_local.json
   1 .gitignore
   1 .github/workflows/path1_evidence_queue.yml
   1 .github/workflows/backfill_m15.yml

git log --name-only --pretty=format: e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  81 reports/path1/
  20 docs/specs/
  11 docs/operations/
   9 docs/runbooks/
   9 docs/contracts/
   9 docs/architecture/
   8 docs/history/
   5 scripts/run/
   5 docs/validation/
   4 sql/path1/
   4 scripts/path1/
   4 docs/doctrine/
   3 docs/governance/
   2 sql/derived/
   2 scripts/validate/
   2 scripts/export/
   2 docs/state_plane/
   2 artifacts/option_c/
   2 .github/workflows/
   2 ./
   1 tests/test_evidence_pack_manifest.py/
   1 tests/test_dst_audit.py/
   1 src/backfill_oanda_m15_checkpointed.py/
   1 sql/06_state_plane_threshold_pack_v0_2.sql/
   1 scripts/local/
   1 scripts/dev/
   1 scripts/deploy/
   1 reports/README.md/
   1 infra/ovc-webhook/
   1 docs/option_d/
   1 docs/evidence_pack/
   1 docs/README_ORG_NOTES.md/
   1 configs/threshold_packs/

git log --pretty=format:%s e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9 | sort | uniq -c | sort -nr
   1 Repo-restructuring
   1 Quadrant state plane evidence runner and related SQL views
   1 Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs; add backfill_m15 workflow; ignore pytest temp dirs
```
  - Sub-range 8: `ee6eedeaae948218edeae3b98de8d640036a57ca..ee6eedeaae948218edeae3b98de8d640036a57ca` (execution range: `ee6eedeaae948218edeae3b98de8d640036a57ca^..ee6eedeaae948218edeae3b98de8d640036a57ca`)
```text
git log --oneline ee6eedeaae948218edeae3b98de8d640036a57ca^..ee6eedeaae948218edeae3b98de8d640036a57ca
ee6eede Update RUN_QUEUE.csv to mark run_id 014 as complete; enhance run_evidence_queue.py with run completeness checks and quarantine functionality

git log --name-only --pretty=format: ee6eedeaae948218edeae3b98de8d640036a57ca^..ee6eedeaae948218edeae3b98de8d640036a57ca | sort | uniq -c | sort -nr
   1 scripts/path1/run_evidence_queue.py
   1 reports/path1/evidence/RUN_QUEUE.csv

git log --name-only --pretty=format: ee6eedeaae948218edeae3b98de8d640036a57ca^..ee6eedeaae948218edeae3b98de8d640036a57ca | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 scripts/path1/
   1 reports/path1/

git log --pretty=format:%s ee6eedeaae948218edeae3b98de8d640036a57ca^..ee6eedeaae948218edeae3b98de8d640036a57ca | sort | uniq -c | sort -nr
   1 Update RUN_QUEUE.csv to mark run_id 014 as complete; enhance run_evidence_queue.py with run completeness checks and quarantine functionality
```
  - Sub-range 9: `4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a` (execution range: `4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a`)
```text
git log --oneline 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a
2690330 Path1: evidence run p1_20260120_018
ca147a6 Path1: evidence run p1_20260120_017

git log --name-only --pretty=format: 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a | sort | uniq -c | sort -nr
   2 reports/path1/evidence/RUN_QUEUE.csv
   2 reports/path1/evidence/INDEX.md
   1 sql/path1/evidence/runs/p1_20260120_018/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_018/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_018/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_017/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_017/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_017/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260120_018/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_018/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_018/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_018/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_018/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_018/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_018/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_017/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_017/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_017/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_017/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_017/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_017/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_017/DIS_v1_1_evidence.md

git log --name-only --pretty=format: 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  18 reports/path1/
   6 sql/path1/

git log --pretty=format:%s 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a | sort | uniq -c | sort -nr
   1 Path1: evidence run p1_20260120_018
   1 Path1: evidence run p1_20260120_017
```
  - Sub-range 10: `35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea` (execution range: `35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea`)
```text
git log --oneline 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea
3c9fbb1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
ecdd8c7 Path1: automated evidence run
f10548b Path1: automated evidence run
ee6e3e3 feat: Introduce Path1 Sealing Protocol and Replay Verification
5ca5a32 Path1: automated evidence run
e696b83 Path1: automated evidence run
5393d43 Path1: automated evidence run
788fbba Path1: automated evidence run
119b9f2 Path1: automated evidence run
4a5588b Path1: automated evidence run
dbda28f Path1: automated evidence run
f506428 Path1: automated evidence run
9a7cb20 Add non-canonical summary generation for Path 1 evidence runs

git log --name-only --pretty=format: 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea | sort | uniq -c | sort -nr
  10 reports/path1/evidence/RUN_QUEUE.csv
  10 reports/path1/evidence/INDEX.md
   1 tests/test_path1_replay_structural.py
   1 sql/path1/evidence/runs/p1_20260120_029/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_029/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_029/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_028/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_028/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_028/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_027/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_027/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_027/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_026/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_026/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_026/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_025/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_025/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_025/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_024/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_024/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_024/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_023/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_023/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_023/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_022/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_022/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_022/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_021/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_021/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_021/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_020/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_020/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_020/study_dis_v1_1.sql
   1 scripts/path1_seal/run_seal_manifests.py
   1 scripts/path1_seal/lib.py
   1 scripts/path1_replay/run_replay_verification.py
   1 scripts/path1_replay/lib.py
   1 scripts/path1_replay/README.md
   1 scripts/path1/run_evidence_queue.py
   1 reports/path1/evidence/runs/p1_20260120_029/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_029/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_029/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_029/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_029/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_029/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_029/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_028/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_028/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_028/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_028/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_028/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_028/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_028/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_027/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_027/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_027/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_027/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_027/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_027/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_027/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_026/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_026/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_026/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_026/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_026/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_026/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_026/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_025/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_025/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_025/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_025/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_025/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_025/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_025/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_024/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_024/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_024/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_024/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_024/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_024/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_024/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_023/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_023/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_023/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_023/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_023/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_023/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_023/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_022/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_022/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_022/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_022/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_022/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_022/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_022/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_021/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_021/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_021/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_021/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_021/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_021/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_021/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_020/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_020/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260120_020/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260120_020/RUN.md
   1 reports/path1/evidence/runs/p1_20260120_020/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_020/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260120_020/DIS_v1_1_evidence.md
   1 docs/path2/ROADMAP_v0_1.md
   1 docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md
   1 docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md
   1 docs/history/path1/EVIDENCE_RUNS_HOWTO.md
   1 .vscode/settings.json
   1 .gitignore
   1 .github/workflows/path1_replay_verify.yml
   1 .github/workflows/path1_evidence_queue.yml

git log --name-only --pretty=format: 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  90 reports/path1/
  30 sql/path1/
   3 scripts/path1_replay/
   3 docs/history/
   2 scripts/path1_seal/
   2 .github/workflows/
   1 tests/test_path1_replay_structural.py/
   1 scripts/path1/
   1 docs/path2/
   1 .vscode/settings.json/
   1 ./

git log --pretty=format:%s 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea | sort | uniq -c | sort -nr
  10 Path1: automated evidence run
   1 feat: Introduce Path1 Sealing Protocol and Replay Verification
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 Add non-canonical summary generation for Path 1 evidence runs
```
  - Sub-range 11: `04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078` (execution range: `04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078`)
```text
git log --oneline 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078
510823d fix: Enhance evidence runner with debugging and error handling for summary writing

git log --name-only --pretty=format: 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078 | sort | uniq -c | sort -nr
   1 scripts/path1/run_evidence_queue.py
   1 .github/workflows/path1_evidence_queue.yml
   1 .github/workflows/main.yml

git log --name-only --pretty=format: 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   2 .github/workflows/
   1 scripts/path1/

git log --pretty=format:%s 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078 | sort | uniq -c | sort -nr
   1 fix: Enhance evidence runner with debugging and error handling for summary writing
```
  - Sub-range 12: `fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494` (execution range: `fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494`)
```text
git log --oneline fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494
b7b0955 fix: enhance SQL file path resolution and add existence check in run scripts
851fbad feat: add initial implementation of trajectory families module
101e3b4 chore: remove reserved 'nul' file and rebuild index
edfe1bc fix: Improve change detection and logging in Path1 evidence runner

git log --name-only --pretty=format: fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494 | sort | uniq -c | sort -nr
   1 trajectory_families/schema.py
   1 trajectory_families/params_v0_1.json
   1 trajectory_families/fingerprint.py
   1 trajectory_families/__init__.py
   1 tests/test_pack_rebuild_equivalence.py
   1 tests/test_overlays_v0_3_determinism.py
   1 tests/test_fingerprint_determinism.py
   1 tests/test_fingerprint.py
   1 tests/fixtures/sample_trajectory.csv
   1 tests/fixtures/golden_fingerprint_v0_1.json
   1 scripts/run/run_option_c.sh
   1 scripts/run/run_option_c.ps1
   1 scripts/path1/run_trajectory_families.py
   1 scripts/path1/overlays_v0_3.py
   1 scripts/dev/pytest_win.ps1
   1 reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_20260122.md
   1 reports/verification/EVIDENCE_REPORT_TEMPLATE_v0_1.md
   1 reports/verification/EVIDENCE_ANCHOR_v0_1.md
   1 reports/path1/trajectory_families/v0.1/fingerprints/index.csv
   1 reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2026/fp_GBPUSD_20260117_03c0d079.json
   1 reports/path1/evidence/RUN_QUEUE.csv
   1 infra/ovc-webhook/ovc-infra.code-workspace
   1 docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md
   1 docs/runbooks/path1_evidence_runner_test.md
   1 docs/examples/overlay_v0_3_sample_outputs.md
   1 docs/evidence_pack_provenance.md
   1 docs/evidence_pack_overlays_v0_3.md
   1 docs/OVERLAY_V0_3_TESTING.md
   1 docs/OVERLAY_V0_3_HARDENING_SUMMARY.md
   1 CHANGELOG_overlays_v0_3_hardening.md
   1 CHANGELOG_overlays_v0_3.md
   1 CHANGELOG_evidence_pack_provenance.md
   1 .vscode/settings.json
   1 .github/workflows/main.yml

git log --name-only --pretty=format: fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   3 reports/verification/
   3 reports/path1/
   3 ./
   2 tests/fixtures/
   2 scripts/run/
   2 scripts/path1/
   1 trajectory_families/schema.py/
   1 trajectory_families/params_v0_1.json/
   1 trajectory_families/fingerprint.py/
   1 trajectory_families/__init__.py/
   1 tests/test_pack_rebuild_equivalence.py/
   1 tests/test_overlays_v0_3_determinism.py/
   1 tests/test_fingerprint_determinism.py/
   1 tests/test_fingerprint.py/
   1 scripts/dev/
   1 infra/ovc-webhook/
   1 docs/specs/
   1 docs/runbooks/
   1 docs/examples/
   1 docs/evidence_pack_provenance.md/
   1 docs/evidence_pack_overlays_v0_3.md/
   1 docs/OVERLAY_V0_3_TESTING.md/
   1 docs/OVERLAY_V0_3_HARDENING_SUMMARY.md/
   1 .vscode/settings.json/
   1 .github/workflows/

git log --pretty=format:%s fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494 | sort | uniq -c | sort -nr
   1 fix: enhance SQL file path resolution and add existence check in run scripts
   1 fix: Improve change detection and logging in Path1 evidence runner
   1 feat: add initial implementation of trajectory families module
   1 chore: remove reserved 'nul' file and rebuild index
```
  - Sub-range 13: `a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be` (execution range: `a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be`)
```text
git log --oneline a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be
d628060 Refactor documentation for Evidence Pack v0.3 Overlays and Path 1 Execution Model

git log --name-only --pretty=format: a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be | sort | uniq -c | sort -nr
   1 reports/path1/evidence/INDEX.md
   1 docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md
   1 docs/path2/ROADMAP_v0_1.md
   1 docs/path1/UPSTREAM_TRAJECTORY_LOOKUP.md
   1 docs/history/path1/scores/SCORE_LIBRARY_v1.md
   1 docs/history/path1/research_views_option_c_v0.1.md
   1 docs/history/path1/SCORE_INVENTORY_v1.md
   1 docs/history/path1/RUN_CONVENTIONS.md
   1 docs/history/path1/README.md
   1 docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md
   1 docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md
   1 docs/history/path1/OPTION_B_PATH1_STATUS.md
   1 docs/history/path1/EVIDENCE_RUNS_HOWTO.md
   1 docs/evidence_pack_overlays_v0_3.md
   1 docs/OVERLAY_V0_3_TESTING.md
   1 docs/OVERLAY_V0_3_HARDENING_SUMMARY.md
   1 README.md
   1 PATH1_EXECUTION_MODEL.md

git log --name-only --pretty=format: a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 docs/history/
   2 ./
   1 reports/path1/
   1 docs/specs/
   1 docs/path2/
   1 docs/path1/
   1 docs/evidence_pack_overlays_v0_3.md/
   1 docs/OVERLAY_V0_3_TESTING.md/
   1 docs/OVERLAY_V0_3_HARDENING_SUMMARY.md/

git log --pretty=format:%s a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be | sort | uniq -c | sort -nr
   1 Refactor documentation for Evidence Pack v0.3 Overlays and Path 1 Execution Model
```
  - Sub-range 14: `0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762` (execution range: `0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762`)
```text
git log --oneline 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762
064339b Add comprehensive documentation and schema verification for OVC pipeline
2f375f2 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
86c5680 feat: enhance ledger update process in Path1 workflow

git log --name-only --pretty=format: 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762 | sort | uniq -c | sort -nr
   1 scripts/ci/verify_schema_objects.py
   1 schema/required_objects.txt
   1 schema/applied_migrations.json
   1 docs/pipeline/CURRENT_STATE_TRUST_MAP.md
   1 docs/pipeline/CURRENT_STATE_INVARIANTS.md
   1 docs/pipeline/CURRENT_STATE_DEP_GRAPH.md
   1 docs/pipeline/CURRENT_STATE_A_TO_D.md
   1 docs/contracts/qa_validation_contract_v1.md
   1 docs/contracts/option_d_evidence_contract_v1.md
   1 docs/contracts/option_c_outcomes_contract_v1.md
   1 docs/contracts/option_b_derived_contract_v1.md
   1 docs/contracts/option_a_ingest_contract_v1.md
   1 docs/contracts/A_TO_D_CONTRACT_v1.md
   1 .github/workflows/ovc_option_c_schedule.yml
   1 .github/workflows/main.yml
   1 .github/workflows/ci_schema_check.yml
   1 .github/workflows/ci_pytest.yml
   1 .github/workflows/backfill_then_validate.yml

git log --name-only --pretty=format: 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   6 docs/contracts/
   5 .github/workflows/
   4 docs/pipeline/
   1 scripts/ci/
   1 schema/required_objects.txt/
   1 schema/applied_migrations.json/

git log --pretty=format:%s 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762 | sort | uniq -c | sort -nr
   1 feat: enhance ledger update process in Path1 workflow
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 Add comprehensive documentation and schema verification for OVC pipeline
```
  - Sub-range 15: `51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622` (execution range: `51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622`)
```text
git log --oneline 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622
380e199 Remove obsolete governance documents and prompts; update maze generation script output path

git log --name-only --pretty=format: 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622 | sort | uniq -c | sort -nr
   1 tools/maze/gen_repo_maze.py
   1 docs/governance/PROMPTS/VS_CODE_PREFLIGHT_WRAPPERS.md
   1 docs/governance/PROMPTS/P8_SESSION_CLOSEOUT_LEDGER_APPEND.md
   1 docs/governance/PROMPTS/OVC_PROMPT_CATALOG.md
   1 docs/governance/OVC_RULEBOOK.md
   1 docs/governance/CHANGELOG_APPEND_ONLY.md
   1 docs/governance/AUDITS/AUDIT_RULEBOOK_VIOLATIONS_CURRENT_STATE.md
   1 docs/governance/AGENTS/OVC_AGENT_SYSTEM.md
   1 CODEX.md
   1 CLAUDE.md
   1 AGENTS.md

git log --name-only --pretty=format: 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   7 docs/governance/
   3 ./
   1 tools/maze/

git log --pretty=format:%s 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622 | sort | uniq -c | sort -nr
   1 Remove obsolete governance documents and prompts; update maze generation script output path
```
  - Sub-range 16: `536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9` (execution range: `536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9`)
```text
git log --oneline 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9
d271e38 Add draft for QA Organization Map detailing folder structure, roles, and governance

git log --name-only --pretty=format: 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9 | sort | uniq -c | sort -nr
   1 docs/REPO_MAP/QA__ORG_MAP_DRAFT.md
   1 docs/REPO_MAP/OPT_D__ORG_MAP_DRAFT.md
   1 docs/REPO_MAP/OPT_C__ORG_MAP_DRAFT.md
   1 docs/REPO_MAP/OPT_B__ORG_MAP_DRAFT.md
   1 docs/REPO_MAP/OPT_A__ORG_MAP_DRAFT.md
   1 docs/REPO_MAP/OPTION INTERNAL PIPELINE GRAPH.svg
   1 docs/REPO_MAP/OPTION INTERNAL PIPELINE GRAPH.mmd
   1 docs/REPO_MAP/OPTION FLOW GRAPH.mmd
   1 docs/REPO_MAP/CATEGORY_PROCESS_APPENDIX_DRAFT.md
   1 docs/REPO_MAP/A&C FLOW GRAPH.mmd
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/OPTION INTERNAL PIPELINE GRAPH.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/OPTION FLOW GRAPH.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/A&C FLOW GRAPH.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/40_ARTIFACTS_VALIDATION/GRAPH_41__VALIDATION_CHAIN.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/40_ARTIFACTS_VALIDATION/GRAPH_40__ARTIFACT_LIFECYCLE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_24__QA__PIPELINE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_23__OPT_D__PIPELINE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_22__OPT_C__PIPELINE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_21__OPT_B__PIPELINE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_20__OPT_A__PIPELINE.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_12__OVERVIEW__ORCHESTRATION.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_11__OVERVIEW__QA_GATES.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/02_CANVAS__OVC_ATLAS.canvas
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/01_CANVAS_LAYOUT_SPEC.md
   1 Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/00_README__GRAPH_ATLAS.md
   1 Tetsu/.obsidian/workspace.json
   1 Tetsu/.obsidian/plugins/mermaid-tools/styles.css
   1 Tetsu/.obsidian/plugins/mermaid-tools/manifest.json
   1 Tetsu/.obsidian/plugins/mermaid-tools/main.js
   1 Tetsu/.obsidian/plugins/mermaid-tools/data.json
   1 Tetsu/.obsidian/core-plugins.json
   1 Tetsu/.obsidian/community-plugins.json
   1 Tetsu/.obsidian/app.json

git log --name-only --pretty=format: 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  18 Tetsu/OVC_REPO_MAZE/
  10 docs/REPO_MAP/
   8 Tetsu/.obsidian/

git log --pretty=format:%s 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9 | sort | uniq -c | sort -nr
   1 Add draft for QA Organization Map detailing folder structure, roles, and governance
```
  - Sub-range 17: `739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e` (execution range: `739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e`)
```text
git log --oneline 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e
f5318b3 path1 evidence: p1_20260202_GBPUSD_20260201_len5d_31f19f8a
53a3c0b Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
f1688f9 Update workspace configuration and add new contracts for feature registry and TradingView reference
316384b path1 evidence: p1_20260201_GBPUSD_20260131_len5d_475dd734
57bd17b path1 evidence: p1_20260131_GBPUSD_20260130_len5d_687bafa3
615c796 path1 evidence: p1_20260130_GBPUSD_20260129_len5d_78e22c92

git log --name-only --pretty=format: 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e | sort | uniq -c | sort -nr
   4 reports/path1/evidence/INDEX.md
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/meta.json
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/RUN.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260202_GBPUSD_20260201_len5d_31f19f8a/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/meta.json
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/RUN.md
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260201_GBPUSD_20260131_len5d_475dd734/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/meta.json
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/RUN.md
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260131_GBPUSD_20260130_len5d_687bafa3/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/meta.json
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/RUN.md
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260130_GBPUSD_20260129_len5d_78e22c92/DIS_v1_1_evidence.md
   1 docs/contracts/tradingview_reference_contract_v0_1.md
   1 docs/contracts/c_feature_registry_freeze_v0_1.md
   1 docs/contracts/README.md
   1 Tetsu/.obsidian/workspace.json

git log --name-only --pretty=format: 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  36 reports/path1/
  12 sql/path1/
   3 docs/contracts/
   1 Tetsu/.obsidian/

git log --pretty=format:%s 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260202_GBPUSD_20260201_len5d_31f19f8a
   1 path1 evidence: p1_20260201_GBPUSD_20260131_len5d_475dd734
   1 path1 evidence: p1_20260131_GBPUSD_20260130_len5d_687bafa3
   1 path1 evidence: p1_20260130_GBPUSD_20260129_len5d_78e22c92
   1 Update workspace configuration and add new contracts for feature registry and TradingView reference
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```
- Ledger evidence
```text
  33 evidence_runs
  19 scripts_general
  14 ci_workflows
   5 validation
   5 tests
   5 governance_contracts
   3 repo_maze
   2 operations
   2 infra
   2 artifacts
```
