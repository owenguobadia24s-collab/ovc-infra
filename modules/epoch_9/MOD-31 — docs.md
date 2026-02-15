# MOD-31 — docs

## Purpose
This module consistently exists to capture commit activity for `MOD-31` across 4 selected sub-range(s), centered on `DIR:docs` basis tokens and co-changed paths `docs/ops/`, `docs/tape_validation_harness.md/`, `src/derived/`.

## Owned Paths
### OWNS
- `docs/` (evidence: 34 touches; example commits: `cd78072`, `23fcb19`)
### DOES NOT OWN
- `src/` (evidence: 17 touches; example commits: `cd78072`, `23fcb19`)
- `sql/` (evidence: 11 touches; example commits: `cd78072`, `23fcb19`)
- `scripts/` (evidence: 8 touches; example commits: `cd78072`, `23fcb19`)
- `.github/` (evidence: 7 touches; example commits: `cd78072`, `23fcb19`)
- `tests/` (evidence: 4 touches; example commits: `cd78072`, `23fcb19`)
- `./` (evidence: 2 touches; example commits: `cd78072`, `23fcb19`)
- `configs/` (evidence: 2 touches; example commits: `cd78072`, `23fcb19`)
- `artifacts/` (evidence: 1 touches; example commits: `cd78072`, `23fcb19`)
- `contracts/` (evidence: 1 touches; example commits: `cd78072`, `23fcb19`)
### AMBIGUOUS
- Boundary with co-changed paths `src`, `sql`, `scripts`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `docs/tape_validation_harness.md` — changed in selected sub-range evidence. (evidence: 12 touches; example commits: `cd78072`, `23fcb19`)
- `docs/WORKFLOW_STATUS.md` — changed in selected sub-range evidence. (evidence: 8 touches; example commits: `cd78072`, `23fcb19`)
- `src/validate_day.py` — changed in selected sub-range evidence. (evidence: 7 touches; example commits: `cd78072`, `23fcb19`)
- `src/validate_range.py` — changed in selected sub-range evidence. (evidence: 4 touches; example commits: `cd78072`, `23fcb19`)
- `src/backfill_oanda_2h_checkpointed.py` — changed in selected sub-range evidence. (evidence: 4 touches; example commits: `cd78072`, `23fcb19`)

## Invariants (Observed)
- INV-01: `MOD-31` is selected at support `34/37` under epoch `9` rules. (evidence: 31 commits; files: `docs/tape_validation_harness.md`, `docs/WORKFLOW_STATUS.md`, `src/validate_day.py`; example commits: `cd78072`, `23fcb19`)
- INV-02: Evidence scope is fixed to 4 sub-range(s) from `cd780720b768933334a53f0231c60b4227311e13` to `0197359d49adff54eedae2d3c60e160fe9ba183c`. (evidence: 31 commits; files: `docs/tape_validation_harness.md`, `docs/WORKFLOW_STATUS.md`, `src/validate_day.py`; example commits: `cd78072`, `23fcb19`)
- INV-03: Basis token(s) `docs` are explicitly encoded in selected candidate label `DIR:docs`. (evidence: 31 commits; files: `docs/tape_validation_harness.md`, `docs/WORKFLOW_STATUS.md`, `src/validate_day.py`; example commits: `cd78072`, `23fcb19`)

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
- UNKNOWN (no evidence)

## Evidence Appendix
- Target selection excerpt
```text
23: | 9 | 37 | docs | 91.89% | source_code | 48.65% | OK |
1404: #### MOD-31 — DIR:docs
1409: - cd780720b768933334a53f0231c60b4227311e13..cd780720b768933334a53f0231c60b4227311e13
1410: - 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448
1411: - 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e
1412: - 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c
1465: - INV-01: Candidate matches 34/37 commits. (support: 34/37)
```
- Anchor commits
```text
cd78072 cd780720b768933334a53f0231c60b4227311e13 2026-01-17T21:17:23Z Add Neon->Notion sync (ops watermark + script + CI workflow)
0197359 0197359d49adff54eedae2d3c60e160fe9ba183c 2026-01-20T03:05:49Z Option C
```
- Inventory summaries (>=2 threshold)
  - Directories
- `docs/ops/` (23)
- `docs/tape_validation_harness.md/` (12)
- `src/derived/` (9)
- `docs/WORKFLOW_STATUS.md/` (8)
- `.github/workflows/` (8)
- `src/validate_day.py/` (7)
- `src/validate_range.py/` (4)
- `src/validate/` (4)
- `src/backfill_oanda_2h_checkpointed.py/` (4)
- `sql/derived/` (4)
- `docs/ovc_logging_doctrine_v0.1.md/` (4)
- `artifacts/derived_validation/` (4)
- `src/ovc_ops/` (3)
- `src/config/` (3)
- `docs/option_threshold_registry_runbook.md/` (3)
- `src/utils/` (2)
- `src/ingest_history_day.py/` (2)
- `src/history_sources/` (2)
- `src/backfill_day.py/` (2)
- `scripts/pipeline_status.py/` (2)
- `scripts/notion_sync.py/` (2)
- `docs/ovc_metric_architecture.md/` (2)
- `docs/option_b1_runbook.md/` (2)
- `configs/threshold_packs/` (2)
- `.github/copilot-instructions.md/` (2)
- `./` (2)
  - Files
- `docs/tape_validation_harness.md` (12)
- `docs/WORKFLOW_STATUS.md` (8)
- `src/validate_day.py` (7)
- `src/validate_range.py` (4)
- `src/backfill_oanda_2h_checkpointed.py` (4)
- `docs/ovc_logging_doctrine_v0.1.md` (4)
- `src/validate/validate_derived_range_v0_1.py` (3)
- `src/derived/compute_c3_regime_trend_v0_1.py` (3)
- `docs/option_threshold_registry_runbook.md` (3)
- `.github/workflows/backfill_then_validate.yml` (3)
- `src/ingest_history_day.py` (2)
- `src/derived/compute_c2_v0_1.py` (2)
- `src/derived/compute_c1_v0_1.py` (2)
- `src/backfill_day.py` (2)
- `scripts/pipeline_status.py` (2)
- `scripts/notion_sync.py` (2)
- `requirements.txt` (2)
- `docs/ovc_metric_architecture.md` (2)
- `docs/option_b1_runbook.md` (2)
- `docs/ops/PIPELINE_REALITY_MAP_v0.1.md` (2)
- `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` (2)
- `docs/ops/OPTION_B_CHARTER_v0.1.md` (2)
- `.github/workflows/notion_sync.yml` (2)
- `.github/copilot-instructions.md` (2)
  - Repeated commit subjects (exact)
- `DTV` (2)
  - Repeated ledger tags
- `validation` (16)
- `source_code` (16)
- `evidence_runs` (10)
- `ci_workflows` (8)
- `scripts_general` (7)
- `tests` (4)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `cd780720b768933334a53f0231c60b4227311e13..cd780720b768933334a53f0231c60b4227311e13` (execution range: `cd780720b768933334a53f0231c60b4227311e13^..cd780720b768933334a53f0231c60b4227311e13`)
```text
git log --oneline cd780720b768933334a53f0231c60b4227311e13^..cd780720b768933334a53f0231c60b4227311e13
cd78072 Add Neon->Notion sync (ops watermark + script + CI workflow)

git log --name-only --pretty=format: cd780720b768933334a53f0231c60b4227311e13^..cd780720b768933334a53f0231c60b4227311e13 | sort | uniq -c | sort -nr
   1 sql/04_ops_notion_sync.sql
   1 scripts/notion_sync.py
   1 requirements.txt
   1 docs/secrets_and_env.md
   1 .github/workflows/notion_sync.yml

git log --name-only --pretty=format: cd780720b768933334a53f0231c60b4227311e13^..cd780720b768933334a53f0231c60b4227311e13 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   1 sql/04_ops_notion_sync.sql/
   1 scripts/notion_sync.py/
   1 docs/secrets_and_env.md/
   1 .github/workflows/
   1 ./

git log --pretty=format:%s cd780720b768933334a53f0231c60b4227311e13^..cd780720b768933334a53f0231c60b4227311e13 | sort | uniq -c | sort -nr
   1 Add Neon->Notion sync (ops watermark + script + CI workflow)
```
  - Sub-range 2: `5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448` (execution range: `5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448`)
```text
git log --oneline 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448
23fcb19 Pipeline Reality Map
d348c04 C3 lifecycle documentation and entry checklist
e43ee24 (c3_regime_trend): Implement C3 regime trend classifier (v0.1)
961738b OVC Option C.3 Stub and unit tests for Threshold Registry
ab9daed Option B.2 Implemented
cbb8bfc Option B.1 Implementation
bc1782d Add Metric Trial Log v0 and Versioned Config Proposal documents
2116934 OVC MA
6dd44ac feat: add canonical OVC metric architecture documentation
d9a89c0 feat: add backfill-then-validate GitHub Action (range support)
b1e87b4 Option B Sealed
46f691a Enhance validation scripts to support multi-day range reporting and add metadata handling
f09687d Add multi-day validation script and update pipeline status checks
407d99a Update workflow and logging doctrine documentation to reflect current validation statuses and next phase requirements
201fd6c Update documentation and SQL validation packs for enhanced pipeline status and derived data validation
71072aa Refactor backfill scripts and update documentation for P2 workflow alignment
01ec28f Add pipeline status harness and logging doctrine documentation
a36a2b9 Enhance OANDA ingestion workflow with validation options and add OANDA 2H CSV export script
1759c44 Implement CSV path resolution with auto-pick functionality in ingestion and validation scripts
99d030e Add historical ingestion functionality for TradingView CSV data
c9d506c DTV
e4fb8f4 DTV

git log --name-only --pretty=format: 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448 | sort | uniq -c | sort -nr
  12 docs/tape_validation_harness.md
   6 src/validate_day.py
   4 docs/ovc_logging_doctrine_v0.1.md
   3 src/validate_range.py
   3 src/backfill_oanda_2h_checkpointed.py
   3 docs/option_threshold_registry_runbook.md
   3 docs/WORKFLOW_STATUS.md
   2 src/validate/validate_derived_range_v0_1.py
   2 src/ingest_history_day.py
   2 src/derived/compute_c3_regime_trend_v0_1.py
   2 src/backfill_day.py
   2 scripts/pipeline_status.py
   2 docs/ovc_metric_architecture.md
   2 docs/option_b1_runbook.md
   2 .github/workflows/backfill_then_validate.yml
   2 .github/copilot-instructions.md
   1 tests/test_validate_derived.py
   1 tests/test_threshold_registry.py
   1 tests/test_derived_features.py
   1 tests/test_c3_regime_trend.py
   1 src/validate/__init__.py
   1 src/utils/csv_locator.py
   1 src/utils/__init__.py
   1 src/ovc_artifacts.py
   1 src/history_sources/tv_csv.py
   1 src/history_sources/__init__.py
   1 src/derived/compute_c3_stub_v0_1.py
   1 src/derived/compute_c2_v0_1.py
   1 src/derived/compute_c1_v0_1.py
   1 src/derived/__init__.py
   1 src/config/threshold_registry_v0_1.py
   1 src/config/threshold_registry_cli.py
   1 src/config/__init__.py
   1 src/backfill_oanda_2h.py
   1 sql/qa_validation_pack_derived.sql
   1 sql/qa_validation_pack_core.sql
   1 sql/qa_validation_pack.sql
   1 sql/05_c3_regime_trend_v0_1.sql
   1 sql/04_threshold_registry_v0_1.sql
   1 sql/03_qa_derived_validation_v0_1.sql
   1 sql/02_derived_c1_c2_tables_v0_1.sql
   1 scripts/validate_day.ps1
   1 scripts/run_migration.py
   1 scripts/oanda_export_2h_day.py
   1 requirements.txt
   1 infra/ovc-webhook/ovc-infra.code-workspace
   1 docs/versioned_config_proposal_v0.1.md
   1 docs/option_b2_runbook.md
   1 docs/ops/PIPELINE_REALITY_MAP_v0.1.md
   1 docs/metric_trial_log_noncanonical_v0.md
   1 docs/metric_map_pine_to_c_layers.md
   1 docs/mapping_validation_report_v0.1.md
   1 docs/c_layer_boundary_spec_v0.1.md
   1 docs/c3_semantic_contract_v0_1.md
   1 docs/c3_entry_checklist.md
   1 configs/threshold_packs/c3_regime_trend_v1.json
   1 configs/threshold_packs/c3_example_pack_v1.json
   1 artifacts/derived_validation/LATEST.txt
   1 artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/meta.json
   1 artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.md
   1 artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.json
   1 .github/workflows/ovc_full_ingest.yml

git log --name-only --pretty=format: 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  12 docs/tape_validation_harness.md/
   6 src/validate_day.py/
   6 src/derived/
   4 docs/ovc_logging_doctrine_v0.1.md/
   4 artifacts/derived_validation/
   3 src/validate_range.py/
   3 src/validate/
   3 src/config/
   3 src/backfill_oanda_2h_checkpointed.py/
   3 docs/option_threshold_registry_runbook.md/
   3 docs/WORKFLOW_STATUS.md/
   3 .github/workflows/
   2 src/utils/
   2 src/ingest_history_day.py/
   2 src/history_sources/
   2 src/backfill_day.py/
   2 scripts/pipeline_status.py/
   2 docs/ovc_metric_architecture.md/
   2 docs/option_b1_runbook.md/
   2 configs/threshold_packs/
   2 .github/copilot-instructions.md/
   1 tests/test_validate_derived.py/
   1 tests/test_threshold_registry.py/
   1 tests/test_derived_features.py/
   1 tests/test_c3_regime_trend.py/
   1 src/ovc_artifacts.py/
   1 src/backfill_oanda_2h.py/
   1 sql/qa_validation_pack_derived.sql/
   1 sql/qa_validation_pack_core.sql/
   1 sql/qa_validation_pack.sql/
   1 sql/05_c3_regime_trend_v0_1.sql/
   1 sql/04_threshold_registry_v0_1.sql/
   1 sql/03_qa_derived_validation_v0_1.sql/
   1 sql/02_derived_c1_c2_tables_v0_1.sql/
   1 scripts/validate_day.ps1/
   1 scripts/run_migration.py/
   1 scripts/oanda_export_2h_day.py/
   1 infra/ovc-webhook/
   1 docs/versioned_config_proposal_v0.1.md/
   1 docs/option_b2_runbook.md/
   1 docs/ops/
   1 docs/metric_trial_log_noncanonical_v0.md/
   1 docs/metric_map_pine_to_c_layers.md/
   1 docs/mapping_validation_report_v0.1.md/
   1 docs/c_layer_boundary_spec_v0.1.md/
   1 docs/c3_semantic_contract_v0_1.md/
   1 docs/c3_entry_checklist.md/
   1 ./

git log --pretty=format:%s 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448 | sort | uniq -c | sort -nr
   2 DTV
   1 feat: add canonical OVC metric architecture documentation
   1 feat: add backfill-then-validate GitHub Action (range support)
   1 Update workflow and logging doctrine documentation to reflect current validation statuses and next phase requirements
   1 Update documentation and SQL validation packs for enhanced pipeline status and derived data validation
   1 Refactor backfill scripts and update documentation for P2 workflow alignment
   1 Pipeline Reality Map
   1 Option B.2 Implemented
   1 Option B.1 Implementation
   1 Option B Sealed
   1 OVC Option C.3 Stub and unit tests for Threshold Registry
   1 OVC MA
   1 Implement CSV path resolution with auto-pick functionality in ingestion and validation scripts
   1 Enhance validation scripts to support multi-day range reporting and add metadata handling
   1 Enhance OANDA ingestion workflow with validation options and add OANDA 2H CSV export script
   1 C3 lifecycle documentation and entry checklist
   1 Add pipeline status harness and logging doctrine documentation
   1 Add multi-day validation script and update pipeline status checks
   1 Add historical ingestion functionality for TradingView CSV data
   1 Add Metric Trial Log v0 and Versioned Config Proposal documents
   1 (c3_regime_trend): Implement C3 regime trend classifier (v0.1)
```
  - Sub-range 3: `2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e` (execution range: `2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e`)
```text
git log --oneline 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e
ee46496 RUN_ARTIFACT_IMPLEMENTATION

git log --name-only --pretty=format: 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e | sort | uniq -c | sort -nr
   1 src/validate_range.py
   1 src/validate_day.py
   1 src/validate/validate_derived_range_v0_1.py
   1 src/ovc_ops/run_artifact_cli.py
   1 src/ovc_ops/run_artifact.py
   1 src/ovc_ops/__init__.py
   1 src/derived/compute_c3_regime_trend_v0_1.py
   1 src/derived/compute_c2_v0_1.py
   1 src/derived/compute_c1_v0_1.py
   1 src/backfill_oanda_2h_checkpointed.py
   1 scripts/run_option_c_wrapper.py
   1 scripts/run_option_c_with_artifact.sh
   1 scripts/notion_sync.py
   1 docs/ops/RUN_ARTIFACT_SPEC_v0.1.md
   1 docs/ops/RUN_ARTIFACT_IMPLEMENTATION_NOTES.md
   1 contracts/run_artifact_spec_v0.1.json
   1 .github/workflows/ovc_option_c_schedule.yml
   1 .github/workflows/notion_sync.yml
   1 .github/workflows/backfill_then_validate.yml
   1 .github/workflows/backfill.yml

git log --name-only --pretty=format: 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   4 .github/workflows/
   3 src/ovc_ops/
   3 src/derived/
   2 docs/ops/
   1 src/validate_range.py/
   1 src/validate_day.py/
   1 src/validate/
   1 src/backfill_oanda_2h_checkpointed.py/
   1 scripts/run_option_c_wrapper.py/
   1 scripts/run_option_c_with_artifact.sh/
   1 scripts/notion_sync.py/
   1 contracts/run_artifact_spec_v0.1.json/

git log --pretty=format:%s 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e | sort | uniq -c | sort -nr
   1 RUN_ARTIFACT_IMPLEMENTATION
```
  - Sub-range 4: `800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c` (execution range: `800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c`)
```text
git log --oneline 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c
0197359 Option C
abc32d7 Add C3 Implementation Contract and SQL View for C3 Features
9cf0060 Add initial implementation contract and SQL view for C2 features
44d409e Add initial implementation contract and SQL view for C1 features
c0a56dc feat(docs): Update Pipeline Reality Map and OVC Current Workflow
f884014 Add OVC Data Flow Canon v0.1 as authoritative reference for data ownership and downstream flows
468a2b1 Add Verification Report v0.1 detailing deployment and workflow statuses

git log --name-only --pretty=format: 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c | sort | uniq -c | sort -nr
   5 docs/WORKFLOW_STATUS.md
   2 docs/ops/OVC_DATA_FLOW_CANON_v0.1.md
   2 docs/ops/OPTION_B_CHARTER_v0.1.md
   1 sql/derived/v_ovc_c_outcomes_v0_1.sql
   1 sql/derived/v_ovc_c3_features_v0_1.sql
   1 sql/derived/v_ovc_c2_features_v0_1.sql
   1 sql/derived/v_ovc_c1_features_v0_1.sql
   1 docs/validation/C_v0_1_validation.md
   1 docs/ovc_current_workflow.md
   1 docs/ops/WORKFLOW_AUDIT_2026-01-20.md
   1 docs/ops/VERIFICATION_REPORT_v0.1.md
   1 docs/ops/PRUNING_CANDIDATES_v0.1.md
   1 docs/ops/PIPELINE_REALITY_MAP_v0.1.md
   1 docs/ops/OPTION_C_OUTCOMES_v0.1.md
   1 docs/ops/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/ops/OPTION_C_CHARTER_v0.1.md
   1 docs/ops/OPTION_B_C3_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/ops/OPTION_B_C3_FEATURES_v0.1.md
   1 docs/ops/OPTION_B_C3_CHARTER_v0.1.md
   1 docs/ops/OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/ops/OPTION_B_C2_FEATURES_v0.1.md
   1 docs/ops/OPTION_B_C2_CHARTER_v0.1.md
   1 docs/ops/OPTION_B_C1_IMPLEMENTATION_CONTRACT_v0.1.md
   1 docs/ops/OPTION_B_C1_FEATURES_v0.1.md
   1 docs/ops/GOVERNANCE_RULES_v0.1.md

git log --name-only --pretty=format: 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  20 docs/ops/
   5 docs/WORKFLOW_STATUS.md/
   4 sql/derived/
   1 docs/validation/
   1 docs/ovc_current_workflow.md/

git log --pretty=format:%s 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c | sort | uniq -c | sort -nr
   1 feat(docs): Update Pipeline Reality Map and OVC Current Workflow
   1 Option C
   1 Add initial implementation contract and SQL view for C2 features
   1 Add initial implementation contract and SQL view for C1 features
   1 Add Verification Report v0.1 detailing deployment and workflow statuses
   1 Add OVC Data Flow Canon v0.1 as authoritative reference for data ownership and downstream flows
   1 Add C3 Implementation Contract and SQL View for C3 Features
```
- Ledger evidence
```text
  16 validation
  16 source_code
  10 evidence_runs
   8 ci_workflows
   7 scripts_general
   4 tests
```
