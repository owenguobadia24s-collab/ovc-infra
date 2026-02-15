# MOD-74 — .github

## Purpose
This module consistently exists to capture commit activity for `MOD-74` across 1 selected sub-range(s), centered on `DIR:.github` basis tokens and co-changed paths `.github/pull_request_template.md/`.

## Owned Paths
### OWNS
- `.github/` (evidence: 1 touches; example commits: `2a68adf`)
### DOES NOT OWN
- UNKNOWN (no evidence)
### AMBIGUOUS
- UNKNOWN (no evidence)

## Produced / Enforced Artifacts
- `.github/pull_request_template.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `2a68adf`)

## Invariants (Observed)
- INV-01: `MOD-74` is selected at support `1/1` under epoch `18` rules. (evidence: 1 commits; files: `.github/pull_request_template.md`; example commits: `2a68adf`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `2a68adf9762ff6910ea1883a6d5cf1f999cf7dae` to `2a68adf9762ff6910ea1883a6d5cf1f999cf7dae`. (evidence: 1 commits; files: `.github/pull_request_template.md`; example commits: `2a68adf`)
- INV-03: Basis token(s) `.github` are explicitly encoded in selected candidate label `DIR:.github`. (evidence: 1 commits; files: `.github/pull_request_template.md`; example commits: `2a68adf`)

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
- Support tie resolved by `document_order` among `MOD-74`, `MOD-75`.

## Evidence Appendix
- Target selection excerpt
```text
32: | 18 | 1 | .github | 100.00% | ci_workflows | 100.00% | OK |
3617: #### MOD-74 — DIR:.github
3622: - 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae
3645: - INV-01: Candidate matches 1/1 commits. (support: 1/1)
```
- Anchor commits
```text
2a68adf 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae 2026-02-07T18:29:46Z docs(pr): add change classification section to PR template
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
  - Sub-range 1: `2a68adf9762ff6910ea1883a6d5cf1f999cf7dae..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae` (execution range: `2a68adf9762ff6910ea1883a6d5cf1f999cf7dae^..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae`)
```text
git log --oneline 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae^..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae
2a68adf docs(pr): add change classification section to PR template

git log --name-only --pretty=format: 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae^..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae | sort | uniq -c | sort -nr
   1 .github/pull_request_template.md

git log --name-only --pretty=format: 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae^..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 .github/pull_request_template.md/

git log --pretty=format:%s 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae^..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae | sort | uniq -c | sort -nr
   1 docs(pr): add change classification section to PR template
```
- Ledger evidence
```text
NONE
```
