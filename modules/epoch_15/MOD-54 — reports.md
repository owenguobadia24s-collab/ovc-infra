# MOD-54 — reports

## Purpose
This module consistently exists to capture commit activity for `MOD-54` across 1 selected sub-range(s), centered on `DIR:reports` basis tokens and co-changed paths `reports/path1/`, `sql/path1/`.

## Owned Paths
### OWNS
- `reports/` (evidence: 2 touches; example commits: `956982d`)
### DOES NOT OWN
- `sql/` (evidence: 2 touches; example commits: `956982d`)
### AMBIGUOUS
- Boundary with co-changed paths `sql`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `956982d`)
- `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `956982d`)
- `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `956982d`)
- `reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_res_v1_0.txt` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `956982d`)
- `reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_lid_v1_0.txt` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `956982d`)

## Invariants (Observed)
- INV-01: `MOD-54` is selected at support `2/3` under epoch `15` rules. (evidence: 1 commits; files: `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql`; example commits: `956982d`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `11bba2ccaf601e48416c0558bd01328fd8ab33b3` to `956982dbb26f1db70741c3b2a207d1e65277afd1`. (evidence: 1 commits; files: `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql`; example commits: `956982d`)
- INV-03: Basis token(s) `reports` are explicitly encoded in selected candidate label `DIR:reports`. (evidence: 1 commits; files: `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql`, `sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql`; example commits: `956982d`)

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
- Support tie resolved by `document_order` among `MOD-54`, `MOD-55`, `MOD-56`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
29: | 15 | 3 | reports | 66.67% | evidence_runs | 66.67% | OK |
2636: #### MOD-54 — DIR:reports
2641: - 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1
2666: - INV-01: Candidate matches 2/3 commits. (support: 2/3)
```
- Anchor commits
```text
11bba2c 11bba2ccaf601e48416c0558bd01328fd8ab33b3 2026-02-03T06:08:18Z path1 evidence: p1_20260203_GBPUSD_20260202_len5d_8c35df6c
956982d 956982dbb26f1db70741c3b2a207d1e65277afd1 2026-02-04T06:05:33Z path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2
```
- Inventory summaries (>=2 threshold)
  - Directories
- `reports/path1/` (9)
- `sql/path1/` (3)
  - Files
- NONE
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- NONE
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1` (execution range: `11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1`)
```text
git log --oneline 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1
956982d path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2

git log --name-only --pretty=format: 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1 | sort | uniq -c | sort -nr
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/study_dis_v1_1.sql
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/meta.json
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/RUN.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260204_GBPUSD_20260203_len5d_c00576a2/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md

git log --name-only --pretty=format: 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 reports/path1/
   3 sql/path1/

git log --pretty=format:%s 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2
```
- Ledger evidence
```text
NONE
```
