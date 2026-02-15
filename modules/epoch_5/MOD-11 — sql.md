# MOD-11 — sql

## Purpose
This module consistently exists to capture commit activity for `MOD-11` across 1 selected sub-range(s), centered on `DIR:sql` basis tokens and co-changed paths `sql/10_views_research_v0.1.sql/`, `sql/90_verify_gate2.sql/`, `sql/01_tables_min.sql/`.

## Owned Paths
### OWNS
- `sql/` (evidence: 4 touches; example commits: `8553d26`, `02abc80`)
### DOES NOT OWN
- `./` (evidence: 1 touches; example commits: `8553d26`, `02abc80`)
- `contracts/` (evidence: 1 touches; example commits: `8553d26`, `02abc80`)
- `docs/` (evidence: 1 touches; example commits: `8553d26`, `02abc80`)
- `specs/` (evidence: 1 touches; example commits: `8553d26`, `02abc80`)
### AMBIGUOUS
- Boundary with co-changed paths `./`, `contracts`, `docs`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `sql/10_views_research_v0.1.sql` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `8553d26`, `02abc80`)
- `sql/90_verify_gate2.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `8553d26`, `02abc80`)
- `sql/01_tables_min.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `8553d26`, `02abc80`)

## Invariants (Observed)
- INV-01: `MOD-11` is selected at support `4/4` under epoch `5` rules. (evidence: 3 commits; files: `sql/10_views_research_v0.1.sql`, `sql/90_verify_gate2.sql`, `sql/01_tables_min.sql`; example commits: `8553d26`, `02abc80`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `15353b9226cdc441cca675eda7cdb0cb91ade68d` to `8553d26409513c1b2abbe55a56c2d9da620777ae`. (evidence: 3 commits; files: `sql/10_views_research_v0.1.sql`, `sql/90_verify_gate2.sql`, `sql/01_tables_min.sql`; example commits: `8553d26`, `02abc80`)
- INV-03: Basis token(s) `sql` are explicitly encoded in selected candidate label `DIR:sql`. (evidence: 3 commits; files: `sql/10_views_research_v0.1.sql`, `sql/90_verify_gate2.sql`, `sql/01_tables_min.sql`; example commits: `8553d26`, `02abc80`)

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
- Support tie resolved by `document_order` among `MOD-11`, `MOD-12`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
19: | 5 | 4 | sql | 100.00% | evidence_runs | 100.00% | OK |
479: #### MOD-11 — DIR:sql
484: - 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae
519: - INV-01: Candidate matches 4/4 commits. (support: 4/4)
```
- Anchor commits
```text
15353b9 15353b9226cdc441cca675eda7cdb0cb91ade68d 2026-01-16T21:16:53Z Gate1: lock MIN contract + specs + SQL v0.1
8553d26 8553d26409513c1b2abbe55a56c2d9da620777ae 2026-01-16T22:36:02Z Fix date column references in events views for consistency
```
- Inventory summaries (>=2 threshold)
  - Directories
- `sql/10_views_research_v0.1.sql/` (2)
  - Files
- `sql/10_views_research_v0.1.sql` (2)
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `evidence_runs` (3)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae` (execution range: `15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae`)
```text
git log --oneline 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae
8553d26 Fix date column references in events views for consistency
02abc80 Fix table reference in events view SQL script for accuracy
043271a Fix table name references in SQL scripts for consistency

git log --name-only --pretty=format: 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae | sort | uniq -c | sort -nr
   2 sql/10_views_research_v0.1.sql
   1 sql/90_verify_gate2.sql
   1 sql/01_tables_min.sql

git log --name-only --pretty=format: 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   2 sql/10_views_research_v0.1.sql/
   1 sql/90_verify_gate2.sql/
   1 sql/01_tables_min.sql/

git log --pretty=format:%s 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae | sort | uniq -c | sort -nr
   1 Fix table reference in events view SQL script for accuracy
   1 Fix table name references in SQL scripts for consistency
   1 Fix date column references in events views for consistency
```
- Ledger evidence
```text
   3 evidence_runs
```
