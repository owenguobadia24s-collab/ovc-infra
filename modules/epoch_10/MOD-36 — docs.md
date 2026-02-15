# MOD-36 — docs

## Purpose
This module consistently exists to capture commit activity for `MOD-36` across 1 selected sub-range(s), centered on `DIR:docs` basis tokens and co-changed paths `releases/ovc-v0.1-spine.md/`, `docs/WORKFLOW_STATUS.md/`, `docs/OVC_DOCTRINE.md/`.

## Owned Paths
### OWNS
- `docs/` (evidence: 1 touches; example commits: `88eff12`)
### DOES NOT OWN
- `releases/` (evidence: 1 touches; example commits: `88eff12`)
### AMBIGUOUS
- Boundary with co-changed paths `releases`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `releases/ovc-v0.1-spine.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `88eff12`)
- `docs/WORKFLOW_STATUS.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `88eff12`)
- `docs/OVC_DOCTRINE.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `88eff12`)
- `docs/IMMUTABILITY_NOTICE.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `88eff12`)

## Invariants (Observed)
- INV-01: `MOD-36` is selected at support `1/1` under epoch `10` rules. (evidence: 1 commits; files: `releases/ovc-v0.1-spine.md`, `docs/WORKFLOW_STATUS.md`, `docs/OVC_DOCTRINE.md`; example commits: `88eff12`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `88eff122fe893c14902013cedf36c25793e75e8f` to `88eff122fe893c14902013cedf36c25793e75e8f`. (evidence: 1 commits; files: `releases/ovc-v0.1-spine.md`, `docs/WORKFLOW_STATUS.md`, `docs/OVC_DOCTRINE.md`; example commits: `88eff12`)
- INV-03: Basis token(s) `docs` are explicitly encoded in selected candidate label `DIR:docs`. (evidence: 1 commits; files: `releases/ovc-v0.1-spine.md`, `docs/WORKFLOW_STATUS.md`, `docs/OVC_DOCTRINE.md`; example commits: `88eff12`)

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
- Support tie resolved by `document_order` among `MOD-36`, `MOD-37`, `MOD-38`.

## Evidence Appendix
- Target selection excerpt
```text
24: | 10 | 1 | docs | 100.00% | releases | 100.00% | OK |
1717: #### MOD-36 — DIR:docs
1722: - 88eff122fe893c14902013cedf36c25793e75e8f..88eff122fe893c14902013cedf36c25793e75e8f
1747: - INV-01: Candidate matches 1/1 commits. (support: 1/1)
```
- Anchor commits
```text
88eff12 88eff122fe893c14902013cedf36c25793e75e8f 2026-01-20T03:11:01Z  OVC Doctrine and Immutability Notice
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
  - Sub-range 1: `88eff122fe893c14902013cedf36c25793e75e8f..88eff122fe893c14902013cedf36c25793e75e8f` (execution range: `88eff122fe893c14902013cedf36c25793e75e8f^..88eff122fe893c14902013cedf36c25793e75e8f`)
```text
git log --oneline 88eff122fe893c14902013cedf36c25793e75e8f^..88eff122fe893c14902013cedf36c25793e75e8f
88eff12  OVC Doctrine and Immutability Notice

git log --name-only --pretty=format: 88eff122fe893c14902013cedf36c25793e75e8f^..88eff122fe893c14902013cedf36c25793e75e8f | sort | uniq -c | sort -nr
   1 releases/ovc-v0.1-spine.md
   1 docs/WORKFLOW_STATUS.md
   1 docs/OVC_DOCTRINE.md
   1 docs/IMMUTABILITY_NOTICE.md

git log --name-only --pretty=format: 88eff122fe893c14902013cedf36c25793e75e8f^..88eff122fe893c14902013cedf36c25793e75e8f | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 releases/ovc-v0.1-spine.md/
   1 docs/WORKFLOW_STATUS.md/
   1 docs/OVC_DOCTRINE.md/
   1 docs/IMMUTABILITY_NOTICE.md/

git log --pretty=format:%s 88eff122fe893c14902013cedf36c25793e75e8f^..88eff122fe893c14902013cedf36c25793e75e8f | sort | uniq -c | sort -nr
   1  OVC Doctrine and Immutability Notice
```
- Ledger evidence
```text
NONE
```
