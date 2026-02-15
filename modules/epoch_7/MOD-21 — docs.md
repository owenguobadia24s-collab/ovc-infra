# MOD-21 — docs

## Purpose
This module consistently exists to capture commit activity for `MOD-21` across 3 selected sub-range(s), centered on `DIR:docs` basis tokens and co-changed paths `sql/option_c_v0_1.sql/`, `sql/option_c_run_report.sql/`, `sql/derived_v0_1.sql/`.

## Owned Paths
### OWNS
- `docs/` (evidence: 5 touches; example commits: `fab9e5b`, `607a8c5`)
### DOES NOT OWN
- `contracts/` (evidence: 3 touches; example commits: `fab9e5b`, `607a8c5`)
- `sql/` (evidence: 3 touches; example commits: `fab9e5b`, `607a8c5`)
- `./` (evidence: 2 touches; example commits: `fab9e5b`, `607a8c5`)
- `scripts/` (evidence: 2 touches; example commits: `fab9e5b`, `607a8c5`)
- `.github/` (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `src/` (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `tests/` (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
### AMBIGUOUS
- Boundary with co-changed paths `contracts`, `sql`, `./`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `sql/option_c_v0_1.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `sql/option_c_run_report.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `sql/derived_v0_1.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `scripts/verify_local.ps1` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)
- `scripts/run_option_c.sh` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `fab9e5b`, `607a8c5`)

## Invariants (Observed)
- INV-01: `MOD-21` is selected at support `5/9` under epoch `7` rules. (evidence: 4 commits; files: `sql/option_c_v0_1.sql`, `sql/option_c_run_report.sql`, `sql/derived_v0_1.sql`; example commits: `fab9e5b`, `607a8c5`)
- INV-02: Evidence scope is fixed to 3 sub-range(s) from `fab9e5ba3cac560c71c3f5d98f013fd223296559` to `13a589b968eedf3690c3d6103ef9de0f69094a8e`. (evidence: 4 commits; files: `sql/option_c_v0_1.sql`, `sql/option_c_run_report.sql`, `sql/derived_v0_1.sql`; example commits: `fab9e5b`, `607a8c5`)
- INV-03: Basis token(s) `docs` are explicitly encoded in selected candidate label `DIR:docs`. (evidence: 4 commits; files: `sql/option_c_v0_1.sql`, `sql/option_c_run_report.sql`, `sql/derived_v0_1.sql`; example commits: `fab9e5b`, `607a8c5`)

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
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
21: | 7 | 9 | docs | 55.56% | evidence_runs | 44.44% | OK |
979: #### MOD-21 — DIR:docs
984: - fab9e5ba3cac560c71c3f5d98f013fd223296559..fab9e5ba3cac560c71c3f5d98f013fd223296559
985: - 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6
986: - 13a589b968eedf3690c3d6103ef9de0f69094a8e..13a589b968eedf3690c3d6103ef9de0f69094a8e
1025: - INV-01: Candidate matches 5/9 commits. (support: 5/9)
```
- Anchor commits
```text
fab9e5b fab9e5ba3cac560c71c3f5d98f013fd223296559 2026-01-17T06:58:24Z Docs: normalize workflow + verification scripts
13a589b 13a589b968eedf3690c3d6103ef9de0f69094a8e 2026-01-17T18:02:40Z Option D
```
- Inventory summaries (>=2 threshold)
  - Directories
- NONE
  - Files
- NONE
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `evidence_runs` (3)
- `scripts_general` (2)
- `contracts` (2)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `fab9e5ba3cac560c71c3f5d98f013fd223296559..fab9e5ba3cac560c71c3f5d98f013fd223296559` (execution range: `fab9e5ba3cac560c71c3f5d98f013fd223296559^..fab9e5ba3cac560c71c3f5d98f013fd223296559`)
```text
git log --oneline fab9e5ba3cac560c71c3f5d98f013fd223296559^..fab9e5ba3cac560c71c3f5d98f013fd223296559
fab9e5b Docs: normalize workflow + verification scripts

git log --name-only --pretty=format: fab9e5ba3cac560c71c3f5d98f013fd223296559^..fab9e5ba3cac560c71c3f5d98f013fd223296559 | sort | uniq -c | sort -nr
   1 scripts/verify_local.ps1
   1 scripts/deploy_worker.ps1
   1 docs/WORKFLOW_STATUS.md
   1 docs/BRANCH_POLICY.md

git log --name-only --pretty=format: fab9e5ba3cac560c71c3f5d98f013fd223296559^..fab9e5ba3cac560c71c3f5d98f013fd223296559 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 scripts/verify_local.ps1/
   1 scripts/deploy_worker.ps1/
   1 docs/WORKFLOW_STATUS.md/
   1 docs/BRANCH_POLICY.md/

git log --pretty=format:%s fab9e5ba3cac560c71c3f5d98f013fd223296559^..fab9e5ba3cac560c71c3f5d98f013fd223296559 | sort | uniq -c | sort -nr
   1 Docs: normalize workflow + verification scripts
```
  - Sub-range 2: `72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6` (execution range: `72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6`)
```text
git log --oneline 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6
607a8c5 Evaluation + Feedback Layer (v0.1)
bacc7ff Define the Derived Metric Classes and the First Canonical Feature Set

git log --name-only --pretty=format: 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6 | sort | uniq -c | sort -nr
   1 sql/option_c_v0_1.sql
   1 sql/derived_v0_1.sql
   1 docs/research_views_option_c_v0.1.md
   1 docs/outcomes_definitions_v0.1.md
   1 docs/option_c_runbook.md
   1 docs/option_c_boundary.md
   1 docs/option_b_runbook.md
   1 docs/derived_metric_registry_v0.1.md
   1 docs/derived_layer_boundary.md
   1 docs/dashboard_mapping_v0.1.md
   1 contracts/eval_contract_v0.1.json
   1 contracts/derived_feature_set_v0.1.json

git log --name-only --pretty=format: 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 sql/option_c_v0_1.sql/
   1 sql/derived_v0_1.sql/
   1 docs/research_views_option_c_v0.1.md/
   1 docs/outcomes_definitions_v0.1.md/
   1 docs/option_c_runbook.md/
   1 docs/option_c_boundary.md/
   1 docs/option_b_runbook.md/
   1 docs/derived_metric_registry_v0.1.md/
   1 docs/derived_layer_boundary.md/
   1 docs/dashboard_mapping_v0.1.md/
   1 contracts/eval_contract_v0.1.json/
   1 contracts/derived_feature_set_v0.1.json/

git log --pretty=format:%s 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6 | sort | uniq -c | sort -nr
   1 Evaluation + Feedback Layer (v0.1)
   1 Define the Derived Metric Classes and the First Canonical Feature Set
```
  - Sub-range 3: `13a589b968eedf3690c3d6103ef9de0f69094a8e..13a589b968eedf3690c3d6103ef9de0f69094a8e` (execution range: `13a589b968eedf3690c3d6103ef9de0f69094a8e^..13a589b968eedf3690c3d6103ef9de0f69094a8e`)
```text
git log --oneline 13a589b968eedf3690c3d6103ef9de0f69094a8e^..13a589b968eedf3690c3d6103ef9de0f69094a8e
13a589b Option D

git log --name-only --pretty=format: 13a589b968eedf3690c3d6103ef9de0f69094a8e^..13a589b968eedf3690c3d6103ef9de0f69094a8e | sort | uniq -c | sort -nr
   1 sql/option_c_run_report.sql
   1 scripts/run_option_c.sh
   1 scripts/run_option_c.ps1
   1 docs/secrets_and_env.md
   1 docs/option_d_ops_boundary.md
   1 VERSION_OPTION_C
   1 .github/workflows/ovc_option_c_schedule.yml

git log --name-only --pretty=format: 13a589b968eedf3690c3d6103ef9de0f69094a8e^..13a589b968eedf3690c3d6103ef9de0f69094a8e | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 sql/option_c_run_report.sql/
   1 scripts/run_option_c.sh/
   1 scripts/run_option_c.ps1/
   1 docs/secrets_and_env.md/
   1 docs/option_d_ops_boundary.md/
   1 .github/workflows/
   1 ./

git log --pretty=format:%s 13a589b968eedf3690c3d6103ef9de0f69094a8e^..13a589b968eedf3690c3d6103ef9de0f69094a8e | sort | uniq -c | sort -nr
   1 Option D
```
- Ledger evidence
```text
   3 evidence_runs
   2 scripts_general
   2 contracts
```
