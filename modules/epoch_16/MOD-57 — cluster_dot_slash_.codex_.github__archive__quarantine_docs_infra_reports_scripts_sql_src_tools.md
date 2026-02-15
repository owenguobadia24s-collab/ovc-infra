# MOD-57 — cluster_dot_slash_.codex_.github__archive__quarantine_docs_infra_reports_scripts_sql_src_tools

## Purpose
This module consistently exists to capture commit activity for `MOD-57` across 5 selected sub-range(s), centered on `CLUSTER:./|.codex|.github|_archive|_quarantine|docs|infra|reports|scripts|sql|src|tools` basis tokens and co-changed paths `reports/path1/`, `sql/path1/`, `./`.

## Owned Paths
### OWNS
- `./` (evidence: 6 touches; example commits: `3969606`, `12ef20f`)
- `.codex/` (evidence: 3 touches; example commits: `3969606`, `12ef20f`)
- `.github/` (evidence: 3 touches; example commits: `3969606`, `12ef20f`)
- `_archive/` (evidence: 3 touches; example commits: `3969606`, `12ef20f`)
- `_quarantine/` (evidence: 4 touches; example commits: `3969606`, `12ef20f`)
- `docs/` (evidence: 4 touches; example commits: `3969606`, `12ef20f`)
- `infra/` (evidence: UNKNOWN (no evidence); example commits: `3969606`, `12ef20f`)
- `reports/` (evidence: 6 touches; example commits: `3969606`, `12ef20f`)
- `scripts/` (evidence: UNKNOWN (no evidence); example commits: `3969606`, `12ef20f`)
- `sql/` (evidence: 7 touches; example commits: `3969606`, `12ef20f`)
- `src/` (evidence: 4 touches; example commits: `3969606`, `12ef20f`)
- `tools/` (evidence: 6 touches; example commits: `3969606`, `12ef20f`)
### DOES NOT OWN
- UNKNOWN (no evidence)
### AMBIGUOUS
- UNKNOWN (no evidence)

## Produced / Enforced Artifacts
- `reports/path1/evidence/INDEX.md` — changed in selected sub-range evidence. (evidence: 6 touches; example commits: `3969606`, `12ef20f`)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `3969606`, `12ef20f`)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `3969606`, `12ef20f`)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_dis_v1_1.sql` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `3969606`, `12ef20f`)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_res_v1_0.txt` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `3969606`, `12ef20f`)

## Invariants (Observed)
- INV-01: `MOD-57` is selected at support `11/25` under epoch `16` rules. (evidence: 9 commits; files: `reports/path1/evidence/INDEX.md`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql`; example commits: `3969606`, `12ef20f`)
- INV-02: Evidence scope is fixed to 5 sub-range(s) from `02fc2accfe43f534e2cc305a216679be5e2a0b52` to `7021c84d722a6782d032dbeccfccc8aa81bd3353`. (evidence: 9 commits; files: `reports/path1/evidence/INDEX.md`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql`; example commits: `3969606`, `12ef20f`)
- INV-03: Basis token(s) `./, .codex, .github, _archive, _quarantine, docs, infra, reports, scripts, sql, src, tools` are explicitly encoded in selected candidate label `CLUSTER:./|.codex|.github|_archive|_quarantine|docs|infra|reports|scripts|sql|src|tools`. (evidence: 9 commits; files: `reports/path1/evidence/INDEX.md`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql`; example commits: `3969606`, `12ef20f`)

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
- Support tie resolved by `document_order` among `MOD-57`, `MOD-58`.

## Evidence Appendix
- Target selection excerpt
```text
30: | 16 | 25 | tools | 44.00% | validation | 36.00% | OK |
2739: #### MOD-57 — CLUSTER:./|.codex|.github|_archive|_quarantine|docs|infra|reports|scripts|sql|src|tools
2744: - 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2
2745: - 456567ea4a3a64b3a374152955b1ba150628216a..456567ea4a3a64b3a374152955b1ba150628216a
2746: - 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f
2747: - 8452511e7ae16af73801df8db9137a2fb429c466..8452511e7ae16af73801df8db9137a2fb429c466
2748: - 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353
2802: - INV-01: Candidate matches 11/25 commits. (support: 11/25)
```
- Anchor commits
```text
02fc2ac 02fc2accfe43f534e2cc305a216679be5e2a0b52 2026-02-04T20:14:03Z Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
7021c84 7021c84d722a6782d032dbeccfccc8aa81bd3353 2026-02-07T05:33:31Z path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
```
- Inventory summaries (>=2 threshold)
  - Directories
- `reports/path1/` (54)
- `sql/path1/` (18)
- `./` (6)
- `tools/run_registry/` (4)
- `src/ovc_ops/` (2)
- `scripts/path1/` (2)
  - Files
- `reports/path1/evidence/INDEX.md` (6)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql` (2)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql` (2)
- `sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_dis_v1_1.sql` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_res_v1_0.txt` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_lid_v1_0.txt` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_dis_v1_1.txt` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/meta.json` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RUN.md` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RES_v1_0_evidence.md` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/LID_v1_0_evidence.md` (2)
- `reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/DIS_v1_1_evidence.md` (2)
  - Repeated commit subjects (exact)
- `path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb` (2)
- `Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra` (2)
  - Repeated ledger tags
- `evidence_runs` (8)
- `validation` (4)
- `source_code` (3)
- `tools_general` (2)
- `scripts_general` (2)
- `infra` (2)
- `governance_contracts` (2)
- `codex_runtime` (2)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2` (execution range: `02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2`)
```text
git log --oneline 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2
3969606 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
12ef20f .continued
956982d path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2
11bba2c path1 evidence: p1_20260203_GBPUSD_20260202_len5d_8c35df6c

git log --name-only --pretty=format: 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2 | sort | uniq -c | sort -nr
   2 reports/path1/evidence/INDEX.md
   1 src/utils/_LIBRARY_ONLY.md
   1 src/ovc_ops/_LIBRARY_ONLY.md
   1 src/history_sources/_LIBRARY_ONLY.md
   1 src/_LIBRARY_ONLY.md
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/study_dis_v1_1.sql
   1 sql/_LIBRARY_ONLY.md
   1 reports/validation/canon_inspection_pass_b__explicit_links.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/meta.json
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/RUN.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/meta.json
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/RUN.md
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260203_GBPUSD_20260202_len5d_8c35df6c/DIS_v1_1_evidence.md
   1 infra/ovc-webhook/test/_LIBRARY_ONLY.md
   1 docs/governance/OVC_GOVERNANCE_REFERENCE_v0.1.md
   1 _quarantine/README.md
   1 _archive/README.md
   1 PRUNE_PLAN_v0.1.md
   1 PHASE_1_5_CLOSURE_DECLARATION.md
   1 OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md
   1 OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md
   1 OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md
   1 ARCHIVE_NON_CANONICAL_v0.1.md

git log --name-only --pretty=format: 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  18 reports/path1/
   6 sql/path1/
   6 ./
   1 src/utils/
   1 src/ovc_ops/
   1 src/history_sources/
   1 src/_LIBRARY_ONLY.md/
   1 sql/_LIBRARY_ONLY.md/
   1 reports/validation/
   1 infra/ovc-webhook/
   1 docs/governance/
   1 _quarantine/README.md/
   1 _archive/README.md/

git log --pretty=format:%s 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2
   1 path1 evidence: p1_20260203_GBPUSD_20260202_len5d_8c35df6c
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 .continued
```
  - Sub-range 2: `456567ea4a3a64b3a374152955b1ba150628216a..456567ea4a3a64b3a374152955b1ba150628216a` (execution range: `456567ea4a3a64b3a374152955b1ba150628216a^..456567ea4a3a64b3a374152955b1ba150628216a`)
```text
git log --oneline 456567ea4a3a64b3a374152955b1ba150628216a^..456567ea4a3a64b3a374152955b1ba150628216a
456567e feat(qa): add run envelope v0.1 + validation pack + registry tooling

git log --name-only --pretty=format: 456567ea4a3a64b3a374152955b1ba150628216a^..456567ea4a3a64b3a374152955b1ba150628216a | sort | uniq -c | sort -nr
   1 tools/run_registry/render_system_health_v0_1.py
   1 tools/run_registry/build_run_registry_v0_1.py
   1 tools/run_registry/build_op_status_table_v0_1.py
   1 tools/run_registry/build_drift_signals_v0_1.py
   1 tests/test_run_envelope_v0_1.py
   1 src/ovc_ops/run_envelope_v0_1.py
   1 scripts/validate/run_qa_validation_pack.py
   1 scripts/path1_seal/run_seal_manifests.py
   1 scripts/path1/run_state_plane.py
   1 scripts/path1/generate_queue_resolved.py
   1 .codex/CHECKS/run_audit_pack.ps1

git log --name-only --pretty=format: 456567ea4a3a64b3a374152955b1ba150628216a^..456567ea4a3a64b3a374152955b1ba150628216a | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   4 tools/run_registry/
   2 scripts/path1/
   1 tests/test_run_envelope_v0_1.py/
   1 src/ovc_ops/
   1 scripts/validate/
   1 scripts/path1_seal/
   1 .codex/CHECKS/

git log --pretty=format:%s 456567ea4a3a64b3a374152955b1ba150628216a^..456567ea4a3a64b3a374152955b1ba150628216a | sort | uniq -c | sort -nr
   1 feat(qa): add run envelope v0.1 + validation pack + registry tooling
```
  - Sub-range 3: `34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f` (execution range: `34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f`)
```text
git log --oneline 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f
07022ac path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb

git log --name-only --pretty=format: 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f | sort | uniq -c | sort -nr
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/meta.json
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RUN.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md

git log --name-only --pretty=format: 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 reports/path1/
   3 sql/path1/

git log --pretty=format:%s 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb
```
  - Sub-range 4: `8452511e7ae16af73801df8db9137a2fb429c466..8452511e7ae16af73801df8db9137a2fb429c466` (execution range: `8452511e7ae16af73801df8db9137a2fb429c466^..8452511e7ae16af73801df8db9137a2fb429c466`)
```text
git log --oneline 8452511e7ae16af73801df8db9137a2fb429c466^..8452511e7ae16af73801df8db9137a2fb429c466
8452511 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
07022ac path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb

git log --name-only --pretty=format: 8452511e7ae16af73801df8db9137a2fb429c466^..8452511e7ae16af73801df8db9137a2fb429c466 | sort | uniq -c | sort -nr
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/meta.json
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RUN.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260205_GBPUSD_20260204_len5d_34fb1bcb/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md

git log --name-only --pretty=format: 8452511e7ae16af73801df8db9137a2fb429c466^..8452511e7ae16af73801df8db9137a2fb429c466 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 reports/path1/
   3 sql/path1/

git log --pretty=format:%s 8452511e7ae16af73801df8db9137a2fb429c466^..8452511e7ae16af73801df8db9137a2fb429c466 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```
  - Sub-range 5: `9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353` (execution range: `9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353`)
```text
git log --oneline 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353
7021c84 path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
a317006 path1 evidence: p1_20260206_GBPUSD_20260205_len5d_cc78af78

git log --name-only --pretty=format: 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353 | sort | uniq -c | sort -nr
   2 reports/path1/evidence/INDEX.md
   1 sql/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/meta.json
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/RUN.md
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260207_GBPUSD_20260206_len5d_efde5bd5/DIS_v1_1_evidence.md
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/meta.json
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/RUN.md
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260206_GBPUSD_20260205_len5d_cc78af78/DIS_v1_1_evidence.md

git log --name-only --pretty=format: 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  18 reports/path1/
   6 sql/path1/

git log --pretty=format:%s 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
   1 path1 evidence: p1_20260206_GBPUSD_20260205_len5d_cc78af78
```
- Ledger evidence
```text
   8 evidence_runs
   4 validation
   3 source_code
   2 tools_general
   2 scripts_general
   2 infra
   2 governance_contracts
   2 codex_runtime
```
