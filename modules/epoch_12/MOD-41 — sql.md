# MOD-41 — sql

## Purpose
This module consistently exists to capture commit activity for `MOD-41` across 1 selected sub-range(s), centered on `DIR:sql` basis tokens and co-changed paths `sql/path1/`, `docs/path1/`.

## Owned Paths
### OWNS
- `sql/` (evidence: 6 touches; example commits: `fb2bbd3`, `49e8139`)
### DOES NOT OWN
- `docs/` (evidence: 4 touches; example commits: `fb2bbd3`, `49e8139`)
### AMBIGUOUS
- Boundary with co-changed paths `docs`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `docs/path1/OPTION_B_PATH1_STATUS.md` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `fb2bbd3`, `49e8139`)
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fb2bbd3`, `49e8139`)
- `sql/path1/studies/dis_stability_quarterly.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fb2bbd3`, `49e8139`)
- `sql/path1/studies/dis_sanity_distribution.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fb2bbd3`, `49e8139`)
- `sql/path1/scores/score_dis_v1_1.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fb2bbd3`, `49e8139`)

## Invariants (Observed)
- INV-01: `MOD-41` is selected at support `6/7` under epoch `12` rules. (evidence: 5 commits; files: `docs/path1/OPTION_B_PATH1_STATUS.md`, `sql/path1/studies/dis_vs_outcomes_bucketed.sql`, `sql/path1/studies/dis_stability_quarterly.sql`; example commits: `fb2bbd3`, `49e8139`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d` to `fb2bbd3b4513e5b61840519dc3053785300a00c2`. (evidence: 5 commits; files: `docs/path1/OPTION_B_PATH1_STATUS.md`, `sql/path1/studies/dis_vs_outcomes_bucketed.sql`, `sql/path1/studies/dis_stability_quarterly.sql`; example commits: `fb2bbd3`, `49e8139`)
- INV-03: Basis token(s) `sql` are explicitly encoded in selected candidate label `DIR:sql`. (evidence: 5 commits; files: `docs/path1/OPTION_B_PATH1_STATUS.md`, `sql/path1/studies/dis_vs_outcomes_bucketed.sql`, `sql/path1/studies/dis_stability_quarterly.sql`; example commits: `fb2bbd3`, `49e8139`)

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
- Support tie resolved by `document_order` among `MOD-41`, `MOD-42`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
26: | 12 | 7 | sql | 85.71% | evidence_runs | 85.71% | OK |
1904: #### MOD-41 — DIR:sql
1909: - 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2
1943: - INV-01: Candidate matches 6/7 commits. (support: 6/7)
```
- Anchor commits
```text
04d95ab 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d 2026-01-20T06:41:53Z Add new studies for DIS, LID, and RES scores focusing on stability and outcome associations
fb2bbd3 fb2bbd3b4513e5b61840519dc3053785300a00c2 2026-01-20T10:06:54Z feat: Add Path 1 Evidence Protocol and SQL studies for DIS, LID, and RES scores
```
- Inventory summaries (>=2 threshold)
  - Directories
- `sql/path1/` (25)
- `docs/path1/` (8)
  - Files
- `docs/path1/OPTION_B_PATH1_STATUS.md` (2)
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `evidence_runs` (5)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2` (execution range: `04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2`)
```text
git log --oneline 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2
fb2bbd3 feat: Add Path 1 Evidence Protocol and SQL studies for DIS, LID, and RES scores
49e8139 Evidence Run 002
b073138 feat: Add operational guide and SQL patches for Path 1 evidence runs
a04f8b2 Add distributional analysis studies for DIS-v1.1, LID-v1.0, and RES-v1.0 scores with corresponding views
0f85361 Update DIS score to v1.1, removing directional_efficiency dependency; add documentation and status files for Path 1 freeze

git log --name-only --pretty=format: 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2 | sort | uniq -c | sort -nr
   2 docs/path1/OPTION_B_PATH1_STATUS.md
   1 sql/path1/studies/dis_vs_outcomes_bucketed.sql
   1 sql/path1/studies/dis_stability_quarterly.sql
   1 sql/path1/studies/dis_sanity_distribution.sql
   1 sql/path1/scores/score_dis_v1_1.sql
   1 sql/path1/evidence/v_path1_evidence_res_v1_0.sql
   1 sql/path1/evidence/v_path1_evidence_lid_v1_0.sql
   1 sql/path1/evidence/v_path1_evidence_dis_v1_1.sql
   1 sql/path1/evidence/studies/study_res_v1_0_distribution.sql
   1 sql/path1/evidence/studies/study_lid_v1_0_distribution.sql
   1 sql/path1/evidence/studies/study_dis_v1_1_distribution.sql
   1 sql/path1/evidence/runs/p1_20260120_003/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_003/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_003/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_003/run_config.sql
   1 sql/path1/evidence/runs/p1_20260120_002/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_002/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_002/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_002/run_config.sql
   1 sql/path1/evidence/runs/p1_20260120_001/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_001/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260120_001/study_dis_v1_1.sql
   1 sql/path1/evidence/runs/p1_20260120_001/run_config.sql
   1 sql/path1/db_patches/patch_create_score_views_20260120.sql
   1 sql/path1/db_patches/patch_create_evidence_views_20260120.sql
   1 sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql
   1 docs/path1/scores/SCORE_LIBRARY_v1.md
   1 docs/path1/SCORE_INVENTORY_v1.md
   1 docs/path1/RUN_CONVENTIONS.md
   1 docs/path1/README.md
   1 docs/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md
   1 docs/path1/EVIDENCE_RUNS_HOWTO.md

git log --name-only --pretty=format: 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  25 sql/path1/
   8 docs/path1/

git log --pretty=format:%s 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2 | sort | uniq -c | sort -nr
   1 feat: Add operational guide and SQL patches for Path 1 evidence runs
   1 feat: Add Path 1 Evidence Protocol and SQL studies for DIS, LID, and RES scores
   1 Update DIS score to v1.1, removing directional_efficiency dependency; add documentation and status files for Path 1 freeze
   1 Evidence Run 002
   1 Add distributional analysis studies for DIS-v1.1, LID-v1.0, and RES-v1.0 scores with corresponding views
```
- Ledger evidence
```text
   5 evidence_runs
```
