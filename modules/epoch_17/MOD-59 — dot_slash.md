# MOD-59 — dot_slash

## Purpose
This module consistently exists to capture commit activity for `MOD-59` across 1 selected sub-range(s), centered on `DIR:./` basis tokens and co-changed paths `docs/catalogs/`, `scripts/governance/`, `tools/dev_catalog/`.

## Owned Paths
### OWNS
- `./` (evidence: 1 touches; example commits: `ff1564d`)
### DOES NOT OWN
- `.github/` (evidence: 1 touches; example commits: `ff1564d`)
- `.vscode/` (evidence: 1 touches; example commits: `ff1564d`)
- `artifacts/` (evidence: 1 touches; example commits: `ff1564d`)
- `docs/` (evidence: 1 touches; example commits: `ff1564d`)
- `scripts/` (evidence: 1 touches; example commits: `ff1564d`)
- `tests/` (evidence: 1 touches; example commits: `ff1564d`)
- `tools/` (evidence: 1 touches; example commits: `ff1564d`)
### AMBIGUOUS
- Boundary with co-changed paths `.github`, `.vscode`, `artifacts`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `tools/dev_catalog/git2dev_change_ledger.py` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `ff1564d`)
- `tests/test_change_classifier.py` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `ff1564d`)
- `scripts/governance/install_precommit_change_classifier.sh` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `ff1564d`)
- `scripts/governance/classify_change.py` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `ff1564d`)
- `docs/governance/CHANGE_TAXONOMY_v0_1.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `ff1564d`)

## Invariants (Observed)
- INV-01: `MOD-59` is selected at support `1/1` under epoch `17` rules. (evidence: 1 commits; files: `tools/dev_catalog/git2dev_change_ledger.py`, `tests/test_change_classifier.py`, `scripts/governance/install_precommit_change_classifier.sh`; example commits: `ff1564d`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `ff1564dd8e4cd61b5bbc76db3aebbba48852abdb` to `ff1564dd8e4cd61b5bbc76db3aebbba48852abdb`. (evidence: 1 commits; files: `tools/dev_catalog/git2dev_change_ledger.py`, `tests/test_change_classifier.py`, `scripts/governance/install_precommit_change_classifier.sh`; example commits: `ff1564d`)
- INV-03: Basis token(s) `./` are explicitly encoded in selected candidate label `DIR:./`. (evidence: 1 commits; files: `tools/dev_catalog/git2dev_change_ledger.py`, `tests/test_change_classifier.py`, `scripts/governance/install_precommit_change_classifier.sh`; example commits: `ff1564d`)

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
- Support tie resolved by `document_order` among `MOD-59`, `MOD-60`, `MOD-61`, `MOD-62`, `MOD-63`, `MOD-64`, `MOD-65`, `MOD-66`, `MOD-67`, `MOD-68`, `MOD-69`, `MOD-70`, `MOD-71`, `MOD-72`, `MOD-73`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
31: | 17 | 1 | ./ | 100.00% | artifacts | 100.00% | OK |
2878: #### MOD-59 — DIR:./
2883: - ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb
2924: - INV-01: Candidate matches 1/1 commits. (support: 1/1)
```
- Anchor commits
```text
ff1564d ff1564dd8e4cd61b5bbc76db3aebbba48852abdb 2026-02-07T18:26:34Z Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation
```
- Inventory summaries (>=2 threshold)
  - Directories
- `docs/catalogs/` (3)
- `scripts/governance/` (2)
  - Files
- NONE
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- NONE
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb` (execution range: `ff1564dd8e4cd61b5bbc76db3aebbba48852abdb^..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb`)
```text
git log --oneline ff1564dd8e4cd61b5bbc76db3aebbba48852abdb^..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb
ff1564d Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation

git log --name-only --pretty=format: ff1564dd8e4cd61b5bbc76db3aebbba48852abdb^..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb | sort | uniq -c | sort -nr
   1 tools/dev_catalog/git2dev_change_ledger.py
   1 tests/test_change_classifier.py
   1 scripts/governance/install_precommit_change_classifier.sh
   1 scripts/governance/classify_change.py
   1 docs/governance/CHANGE_TAXONOMY_v0_1.md
   1 docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json
   1 docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.sha256
   1 docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.json
   1 docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl
   1 artifacts/change_classifier.json
   1 .vscode/settings.json
   1 .gitignore
   1 .github/workflows/change_classifier.yml

git log --name-only --pretty=format: ff1564dd8e4cd61b5bbc76db3aebbba48852abdb^..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   3 docs/catalogs/
   2 scripts/governance/
   1 tools/dev_catalog/
   1 tests/test_change_classifier.py/
   1 docs/governance/
   1 docs/contracts/
   1 artifacts/change_classifier.json/
   1 .vscode/settings.json/
   1 .github/workflows/
   1 ./

git log --pretty=format:%s ff1564dd8e4cd61b5bbc76db3aebbba48852abdb^..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb | sort | uniq -c | sort -nr
   1 Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation
```
- Ledger evidence
```text
NONE
```
