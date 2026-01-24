---
type: repo-maze-layer
tags: [ovc, repo, maze, governance, qa]
---

# QA_GOVERNANCE

## Definition
System-wide QA/Governance layer (referee for A/B/C/D).

## System Invariants
- PASS/FAIL gates
- Allowed drift thresholds
- Determinism hashes
- Boundary contracts

## QA Anchors (real repo paths)
### WORKFLOWS
- none found

### DOCS
- `docs/contracts/PATH2_CONTRACT_v1_0.md`
- `docs/contracts/c_layer_boundary_spec_v0.1.md`
- `docs/contracts/qa_validation_contract_v1.md`
- `docs/specs/OPTION_B_C1_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_C3_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/contracts/derived_layer_boundary.md`
- `docs/contracts/ingest_boundary.md`
- `docs/contracts/option_a_ingest_contract_v1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `docs/contracts/option_d_evidence_contract_v1.md`
- `docs/contracts/outcomes_definitions_v0.1.md`
- `docs/specs/system/parsing_validation_rules_v0.1.md`
- `docs/contracts/A_TO_D_CONTRACT_v1.md`
- `docs/contracts/c3_semantic_contract_v0_1.md`
- `docs/contracts/min_contract_alignment.md`
- `docs/contracts/option_c_boundary.md`
- `docs/contracts/option_d_ops_boundary.md`
- `docs/operations/OPERATING_BASE.validation.md`
- `docs/validation/C_v0_1_validation.md`
- `docs/validation/VERIFICATION_REPORT_v0.1.md`
- `docs/validation/WORKFLOW_AUDIT_2026-01-20.md`
- `docs/validation/mapping_validation_report_v0.1.md`

### SQL
- `sql/03_qa_derived_validation_v0_1.sql`
- `sql/qa_validation_pack_derived.sql`
- `sql/qa_validation_pack.sql`
- `sql/qa_validation_pack_core.sql`

### REPORTS
- `reports/validation/C1_v0_1_validation.md`
- `reports/validation/C2_v0_1_validation.md`
- `reports/validation/C3_v0_1_validation.md`
- `reports/validation/C_v0_1_promotion.md`
- `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`
- `reports/validation/validate_range_1d5152cf-0d3e-5a8c-8419-a063f3b79692_summary.json`
- `reports/validation/validate_range_2750e41d-3648-5b65-b61e-d847eb14855d_summary.json`
- `reports/runs/20260120T175601Z__D-ValidationHarness__ee6a769/checks.json`
- `reports/runs/20260120T175601Z__D-ValidationHarness__ee6a769/run.json`
- `reports/runs/20260120T175633Z__D-ValidationHarness__ee6a769/checks.json`
- `reports/runs/20260120T175633Z__D-ValidationHarness__ee6a769/run.json`
- `reports/validation/validate_range_1d5152cf-0d3e-5a8c-8419-a063f3b79692_summary.csv`
- `reports/validation/validate_range_2750e41d-3648-5b65-b61e-d847eb14855d_summary.csv`
- `reports/validation/validate_range_1d5152cf-0d3e-5a8c-8419-a063f3b79692_days.jsonl`
- `reports/validation/validate_range_2750e41d-3648-5b65-b61e-d847eb14855d_days.jsonl`
- `reports/runs/20260120T175601Z__D-ValidationHarness__ee6a769/run.log`
- `reports/runs/20260120T175633Z__D-ValidationHarness__ee6a769/run.log`
- `reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2022/fp_GBPUSD_20220926_893a3890.json`
- `reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2026/fp_GBPUSD_20260117_03c0d079.json`
- `reports/pipeline_audit/2026-01-19/results.md`
- `reports/pipeline_audit/2026-01-19/commands_run.txt`
- `reports/pipeline_audit/2026-01-19/inventory.txt`
- `reports/verification/2026-01-19/outputs/gh_section_b_13_backfill_validate_runs.txt`
- `reports/verification/2026-01-19/outputs/gh_section_b_14_backfill_validate_details.txt`
- `reports/verification/2026-01-19/outputs/gh_section_b_15_backfill_validate_artifacts.txt`

### ARTIFACTS
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.md`
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.json`
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/meta.json`
- `artifacts/derived_validation/LATEST.txt`

## Applies to
- [[OPT_A__CANONICAL_INGEST]]
- [[OPT_D__PATHS_BRIDGE]]
- [[OPT_B__DERIVED_LAYERS]]
- [[OPT_C__OUTCOMES_EVAL]]

## Key corridors
- A<->D: resample alignment, workflow ordering, hash normalization
- [[A_D_BOUNDARY]]
