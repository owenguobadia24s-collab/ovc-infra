# MOD-01 — tests

## Purpose
This module consistently exists to capture commit activity for `MOD-01` across 1 selected sub-range(s), centered on `DIR:tests` basis tokens and co-changed paths `./`, `tests/sample_exports/`.

## Owned Paths
### OWNS
- `tests/` (evidence: 4 touches; example commits: `e8c2537`, `c5574da`)
### DOES NOT OWN
- `tools/` (evidence: 2 touches; example commits: `e8c2537`, `c5574da`)
### AMBIGUOUS
- Boundary with co-changed paths `tools`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `"tools\\validate_contract.py"` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `e8c2537`, `c5574da`)
- `"\\tools\\validate_contract.py"` — changed in selected sub-range evidence. (evidence: 2 touches; example commits: `e8c2537`, `c5574da`)
- `tests/sample_exports/min_001.txt` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `e8c2537`, `c5574da`)
- `tests/sample_exports/full_001.txt` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `e8c2537`, `c5574da`)

## Invariants (Observed)
- INV-01: `MOD-01` is selected at support `4/5` under epoch `1` rules. (evidence: 7 commits; files: `"tools\\validate_contract.py"`, `"\\tools\\validate_contract.py"`, `tests/sample_exports/min_001.txt`; example commits: `e8c2537`, `c5574da`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `be09dd8b58769540fc16260529816f9baef514d6` to `e8c253791cb6b44febb0ba6ea70b5b4042c015f0`. (evidence: 7 commits; files: `"tools\\validate_contract.py"`, `"\\tools\\validate_contract.py"`, `tests/sample_exports/min_001.txt`; example commits: `e8c2537`, `c5574da`)
- INV-03: Basis token(s) `tests` are explicitly encoded in selected candidate label `DIR:tests`. (evidence: 7 commits; files: `"tools\\validate_contract.py"`, `"\\tools\\validate_contract.py"`, `tests/sample_exports/min_001.txt`; example commits: `e8c2537`, `c5574da`)

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
- Support tie resolved by `document_order` among `MOD-01`, `MOD-02`.

## Evidence Appendix
- Target selection excerpt
```text
15: | 1 | 5 | tests | 80.00% | tests | 80.00% | OK |
47: #### MOD-01 — DIR:tests
52: - be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0
80: - INV-01: Candidate matches 4/5 commits. (support: 4/5)
```
- Anchor commits
```text
be09dd8 be09dd8b58769540fc16260529816f9baef514d6 2026-01-14T08:36:08Z Add v0.1 export contracts, validation tools, and tests
e8c2537 e8c253791cb6b44febb0ba6ea70b5b4042c015f0 2026-01-14T09:37:00Z Update export string in full_001.txt
```
- Inventory summaries (>=2 threshold)
  - Directories
- `./` (4)
- `tests/sample_exports/` (2)
  - Files
- `"tools\\validate_contract.py"` (2)
- `"\\tools\\validate_contract.py"` (2)
  - Repeated commit subjects (exact)
- `Add contract validation functionality` (2)
  - Repeated ledger tags
- `tools_general` (3)
- `tests` (3)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0` (execution range: `be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0`)
```text
git log --oneline be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0
e8c2537 Update export string in full_001.txt
c5574da Add export string for MIN contract in min_001.txt
aad4983 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
b694a74 Delete tools\validate_contract.py
171cd22 Add contract validation functionality
40ed50f Delete \tools\validate_contract.py
8e1882c Add contract validation functionality

git log --name-only --pretty=format: be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0 | sort | uniq -c | sort -nr
   2 "tools\\validate_contract.py"
   2 "\\tools\\validate_contract.py"
   1 tests/sample_exports/min_001.txt
   1 tests/sample_exports/full_001.txt

git log --name-only --pretty=format: be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   4 ./
   2 tests/sample_exports/

git log --pretty=format:%s be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0 | sort | uniq -c | sort -nr
   2 Add contract validation functionality
   1 Update export string in full_001.txt
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 Delete tools\validate_contract.py
   1 Delete \tools\validate_contract.py
   1 Add export string for MIN contract in min_001.txt
```
- Ledger evidence
```text
   3 tools_general
   3 tests
```
