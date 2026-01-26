---
type: repo-maze-catalog
tags: [ovc, repo, maze, catalog]
---

# ANCHOR_CATALOG

A deterministic catalog of anchors by Option and Room. Same repo state => same ordering.

## OPT_A__CANONICAL_INGEST
### WORKFLOWS
- none found

### DOCS
- `docs/contracts/PATH2_CONTRACT_v1_0.md`
- `docs/contracts/c_layer_boundary_spec_v0.1.md`
- `docs/contracts/qa_validation_contract_v1.md`
- `docs/specs/OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_L2_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/contracts/derived_layer_boundary.md`
- `docs/contracts/ingest_boundary.md`
- `docs/contracts/option_a_ingest_contract_v1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `docs/contracts/option_d_evidence_contract_v1.md`
- `docs/contracts/outcomes_definitions_v0.1.md`
- `docs/architecture/metric_trial_log_noncanonical_v0.md`
- `docs/contracts/A_TO_D_CONTRACT_v1.md`
- `docs/contracts/l3_semantic_contract_v0_1.md`
- `docs/contracts/min_contract_alignment.md`
- `docs/contracts/option_c_boundary.md`
- `docs/contracts/option_d_ops_boundary.md`
- `docs/specs/OPTION_B_L1_FEATURES_v0.1.md`
- `docs/validation/pine_export_consistency.md`
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md`

### SQL
- `sql/00_schema.sql`
- `sql/qa_schema.sql`
- `sql/schema_v01.sql`
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `sql/derived/v_ovc_l1_features_v0_1.sql`
- `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`
- `sql/path1/db_patches/patch_m15_raw_20260122.sql`

### REPORTS
- `reports/validation/C1_v0_1_validation.md`
- `reports/verification/2026-01-19/outputs/l1_neon_schema_verification.txt`
- `reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2026/fp_GBPUSD_20260117_03c0d079.json`

### ARTIFACTS
- none found

## OPT_D__PATHS_BRIDGE
### WORKFLOWS
- none found

### DOCS
- `docs/history/path1/README.md`
- `docs/runbooks/path1_evidence_runner_test.md`
- `docs/history/path1/EVIDENCE_RUNS_HOWTO.md`
- `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md`
- `docs/evidence_pack_overlays_v0_3.md`
- `docs/evidence_pack_provenance.md`
- `docs/path1/UPSTREAM_TRAJECTORY_LOOKUP.md`
- `docs/path2/ROADMAP_v0_1.md`
- `docs/evidence_pack/EVIDENCE_PACK_v0_2.md`
- `docs/history/path1/OPTION_B_PATH1_STATUS.md`
- `docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md`
- `docs/history/path1/RUN_CONVENTIONS.md`
- `docs/history/path1/SCORE_INVENTORY_v1.md`
- `docs/history/path1/research_views_option_c_v0.1.md`
- `docs/specs/system/research_query_pack_v0.1.md`
- `docs/history/path1/scores/SCORE_LIBRARY_v1.md`

### SQL
- `sql/path1/db_patches/patch_create_evidence_views_20260120.sql`
- `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql`
- `sql/path1/evidence/v_path1_evidence_lid_v1_0.sql`
- `sql/path1/evidence/v_path1_evidence_res_v1_0.sql`
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql`
- `sql/path1/studies/lid_vs_outcomes_bucketed.sql`
- `sql/path1/studies/res_vs_outcomes_bucketed.sql`
- `sql/path1/evidence/studies/study_dis_v1_1_distribution.sql`
- `sql/path1/evidence/studies/study_lid_v1_0_distribution.sql`
- `sql/path1/evidence/studies/study_res_v1_0_distribution.sql`
- `sql/path1/evidence/runs/p1_20260120_001/run_config.sql`
- `sql/path1/evidence/runs/p1_20260120_001/study_dis_v1_1.sql`
- `sql/path1/evidence/runs/p1_20260120_001/study_lid_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_001/study_res_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_002/run_config.sql`
- `sql/path1/evidence/runs/p1_20260120_002/study_dis_v1_1.sql`
- `sql/path1/evidence/runs/p1_20260120_002/study_lid_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_002/study_res_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_003/run_config.sql`
- `sql/path1/evidence/runs/p1_20260120_003/study_dis_v1_1.sql`
- `sql/path1/evidence/runs/p1_20260120_003/study_lid_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_003/study_res_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_004/study_dis_v1_1.sql`
- `sql/path1/evidence/runs/p1_20260120_004/study_lid_v1_0.sql`
- `sql/path1/evidence/runs/p1_20260120_004/study_res_v1_0.sql`

### REPORTS
- `reports/path1/evidence/README.md`
- `reports/path1/evidence/INDEX.md`
- `reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md`
- `reports/path1/evidence/runs/p1_20260120_001/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_002/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_003/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_004/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_005/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_006/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_006/LID_v1_0_evidence.md`

### ARTIFACTS
- `artifacts/path1_replay_report.json`

## OPT_B__DERIVED_LAYERS
### WORKFLOWS
- none found

### DOCS
- `docs/architecture/derived_metric_registry_v0.1.md`
- `docs/contracts/c_layer_boundary_spec_v0.1.md`
- `docs/specs/OPTION_B_L2_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/contracts/derived_layer_boundary.md`
- `docs/contracts/ingest_boundary.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/option_d/MODEL_REGISTRY_SPEC.md`
- `docs/architecture/metric_trial_log_noncanonical_v0.md`
- `docs/runbooks/option_threshold_registry_runbook.md`
- `docs/contracts/l3_semantic_contract_v0_1.md`
- `docs/contracts/option_c_boundary.md`
- `docs/contracts/option_d_ops_boundary.md`
- `docs/specs/OPTION_B_L1_FEATURES_v0.1.md`
- `docs/specs/OPTION_B_L2_CHARTER_v0.1.md`
- `docs/specs/OPTION_B_L2_FEATURES_v0.1.md`
- `docs/specs/OPTION_B_L3_CHARTER_v0.1.md`
- `docs/specs/OPTION_B_L3_FEATURES_v0.1.md`
- `docs/architecture/metric_map_pine_to_c_layers.md`
- `docs/architecture/ovc_metric_architecture.md`
- `docs/runbooks/l3_entry_checklist.md`

### SQL
- `sql/03_qa_derived_validation_v0_1.sql`
- `sql/qa_validation_pack_derived.sql`
- `sql/04_threshold_registry_v0_1.sql`
- `sql/derived/v_ovc_c_outcomes_v0_1.sql`
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `sql/derived_v0_1.sql`
- `sql/06_state_plane_threshold_pack_v0_2.sql`
- `sql/derived/v_ovc_l1_features_v0_1.sql`
- `sql/derived/v_ovc_l2_features_v0_1.sql`
- `sql/derived/v_ovc_l3_features_v0_1.sql`
- `sql/derived/v_ovc_state_plane_daypath_v0_2.sql`
- `sql/derived/v_ovc_state_plane_v0_2.sql`
- `sql/05_c3_regime_trend_v0_1.sql`

### REPORTS
- `reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2/path_metrics.json`
- `reports/path1/evidence/runs/p1_20260122_003/outputs/state_plane_v0_2/path_metrics.json`
- `reports/path1/evidence/runs/p1_20260122_004/outputs/state_plane_v0_2/path_metrics.json`
- `reports/validation/C2_v0_1_validation.md`
- `reports/validation/C3_v0_1_validation.md`

### ARTIFACTS
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.md`
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.json`
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/meta.json`
- `artifacts/derived_validation/LATEST.txt`

## OPT_C__OUTCOMES_EVAL
### WORKFLOWS
- none found

### DOCS
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `docs/contracts/outcomes_definitions_v0.1.md`
- `docs/specs/OPTION_C_OUTCOMES_v0.1.md`
- `docs/specs/system/outcome_sql_spec_v0.1.md`
- `docs/specs/system/outcomes_system_v0.1.md`
- `docs/validation/VERIFICATION_REPORT_v0.1.md`
- `docs/validation/mapping_validation_report_v0.1.md`
- `docs/specs/system/run_report_spec_v0.1.md`

### SQL
- `sql/derived/v_ovc_c_outcomes_v0_1.sql`
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql`
- `sql/path1/studies/lid_vs_outcomes_bucketed.sql`
- `sql/path1/studies/res_vs_outcomes_bucketed.sql`
- `sql/03_tables_outcomes.sql`
- `sql/02_tables_run_reports.sql`
- `sql/option_c_run_report.sql`

### REPORTS
- `reports/path1/evidence/README.md`
- `reports/path1/evidence/INDEX.md`
- `reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md`
- `reports/README.md`
- `reports/path1/evidence/runs/p1_20260120_001/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_001/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_002/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_002/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_003/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_003/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_004/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_004/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_005/DIS_v1_1_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/LID_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/RES_v1_0_evidence.md`
- `reports/path1/evidence/runs/p1_20260120_005/RUN.md`
- `reports/path1/evidence/runs/p1_20260120_006/DIS_v1_1_evidence.md`

### ARTIFACTS
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.md`
- `artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/derived_validation_report.json`
- `artifacts/path1_replay_report.json`
- `artifacts/option_c/sanity_local/run_report_sanity_local.json`

## QA / Governance
### WORKFLOWS
- none found

### DOCS
- `docs/contracts/PATH2_CONTRACT_v1_0.md`
- `docs/contracts/c_layer_boundary_spec_v0.1.md`
- `docs/contracts/qa_validation_contract_v1.md`
- `docs/specs/OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_L2_IMPLEMENTATION_CONTRACT_v0.1.md`
- `docs/specs/OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md`
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
- `docs/contracts/l3_semantic_contract_v0_1.md`
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

## Cross-Option Corridors
Candidates only — these are not asserted boundaries, just high-signal paths to inspect.

### A<->D corridor anchors
- [[A_D_BOUNDARY]]
- `docs/contracts/min_contract_alignment.md`
- `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`
- `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`
- `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/backbone_2h.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-A-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-B-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-C-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-D-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-E-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-F-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-G-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-H-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-I-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-J-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-K-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-L-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-A-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-B-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221212-C-GBPUSD.csv`

### A<->D corridor workflows (filename match)
- none found
