# MOD-27 — pine

## Purpose
This module consistently exists to capture commit activity for `MOD-27` across 1 selected sub-range(s), centered on `DIR:pine` basis tokens and co-changed paths `sql/schema_v01.sql/`, `sql/01_tables_min.sql/`, `pine/OVC_v0_1.pine/`.

## Owned Paths
### OWNS
- `pine/` (evidence: 1 touches; example commits: `e3b80fc`)
### DOES NOT OWN
- `sql/` (evidence: 1 touches; example commits: `e3b80fc`)
### AMBIGUOUS
- Boundary with co-changed paths `sql`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `sql/schema_v01.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `e3b80fc`)
- `sql/01_tables_min.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `e3b80fc`)
- `pine/OVC_v0_1.pine` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `e3b80fc`)

## Invariants (Observed)
- INV-01: `MOD-27` is selected at support `1/1` under epoch `8` rules. (evidence: 1 commits; files: `sql/schema_v01.sql`, `sql/01_tables_min.sql`, `pine/OVC_v0_1.pine`; example commits: `e3b80fc`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `e3b80fc3cebdf11218409ce368e85a5b9192f923` to `e3b80fc3cebdf11218409ce368e85a5b9192f923`. (evidence: 1 commits; files: `sql/schema_v01.sql`, `sql/01_tables_min.sql`, `pine/OVC_v0_1.pine`; example commits: `e3b80fc`)
- INV-03: Basis token(s) `pine` are explicitly encoded in selected candidate label `DIR:pine`. (evidence: 1 commits; files: `sql/schema_v01.sql`, `sql/01_tables_min.sql`, `pine/OVC_v0_1.pine`; example commits: `e3b80fc`)

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
- Support tie resolved by `document_order` among `MOD-27`, `MOD-28`, `MOD-29`, `MOD-30`.

## Evidence Appendix
- Target selection excerpt
```text
22: | 8 | 1 | pine | 100.00% | evidence_runs | 100.00% | OK |
1264: #### MOD-27 — DIR:pine
1269: - e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923
1295: - INV-01: Candidate matches 1/1 commits. (support: 1/1)
```
- Anchor commits
```text
e3b80fc e3b80fc3cebdf11218409ce368e85a5b9192f923 2026-01-17T20:40:32Z Option A -> D Audit
```
- Inventory summaries (>=2 threshold)
  - Directories
- NONE
  - Files
- NONE
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- NONE
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923` (execution range: `e3b80fc3cebdf11218409ce368e85a5b9192f923^..e3b80fc3cebdf11218409ce368e85a5b9192f923`)
```text
git log --oneline e3b80fc3cebdf11218409ce368e85a5b9192f923^..e3b80fc3cebdf11218409ce368e85a5b9192f923
e3b80fc Option A -> D Audit

git log --name-only --pretty=format: e3b80fc3cebdf11218409ce368e85a5b9192f923^..e3b80fc3cebdf11218409ce368e85a5b9192f923 | sort | uniq -c | sort -nr
   1 sql/schema_v01.sql
   1 sql/01_tables_min.sql
   1 pine/OVC_v0_1.pine

git log --name-only --pretty=format: e3b80fc3cebdf11218409ce368e85a5b9192f923^..e3b80fc3cebdf11218409ce368e85a5b9192f923 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 sql/schema_v01.sql/
   1 sql/01_tables_min.sql/
   1 pine/OVC_v0_1.pine/

git log --pretty=format:%s e3b80fc3cebdf11218409ce368e85a5b9192f923^..e3b80fc3cebdf11218409ce368e85a5b9192f923 | sort | uniq -c | sort -nr
   1 Option A -> D Audit
```
- Ledger evidence
```text
NONE
```
