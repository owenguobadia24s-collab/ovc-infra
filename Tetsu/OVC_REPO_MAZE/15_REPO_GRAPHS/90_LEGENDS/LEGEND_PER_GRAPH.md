# Legend per Graph

This file lists node IDs used per graph. IDs and descriptions mirror each graph legend for consistency.

## GRAPH_10__OVERVIEW__DATA_FLOW.md

| Node ID | Description |
|---------|-------------|
| TV | TradingView alert source |
| OANDA | OANDA API source |
| A_WORKER | infra/ovc-webhook |
| A_BACKFILL | src/backfill_*.py |
| A_BLOCKS | ovc.ovc_blocks_v01_1_min |
| A_M15 | ovc.ovc_candles_m15_raw |
| A_R2 | R2 bucket archive |
| B_C1 | src/derived/compute_c1_v0_1.py |
| B_C2 | src/derived/compute_c2_v0_1.py |
| B_C3 | src/derived/compute_c3_regime_trend_v0_1.py (NOT INVOKED) |
| B_VIEWS | sql/derived/v_ovc_c*_features*.sql |
| B_TF | trajectory_families/ |
| C_RUNNER | scripts/run/run_option_c.sh |
| C_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 |
| D_PATH1 | scripts/path1/ |
| D_EVIDENCE | reports/path1/evidence/runs/ |
| D_SCORES | reports/path1/scores/ |
| D_NOTION | scripts/export/notion_sync.py |
| NEON | Neon PostgreSQL |
| NOTION | Notion databases |

## GRAPH_11__OVERVIEW__QA_GATES.md

| Node ID | Description |
|---------|-------------|
| A_BLOCKS | ovc.ovc_blocks_v01_1_min |
| B_VIEWS | derived.ovc_c*_features |
| C_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 |
| D_EVIDENCE | reports/path1/evidence/runs/ |
| VAL_DAY | src/validate_day.py |
| VAL_RANGE | src/validate_range.py |
| VAL_DERIVED | src/validate/validate_derived_range_v0_1.py |
| SQL_PACK | sql/qa_validation_pack*.sql |
| SQL_GATE2 | sql/90_verify_gate2.sql (NOT AUTOMATED) |
| PYTEST | tests/ directory |
| T_DERIVED | tests/test_derived_features.py |
| T_CONTRACT | tests/test_contract_equivalence.py |
| T_REPLAY | tests/test_path1_replay_structural.py |
| REPLAY | scripts/path1_replay/run_replay_verification.py |
| C_EXPORT | contracts/export_contract_v0.1.1_min.json |
| C_DERIVED | contracts/derived_feature_set_v0.1.json |
| C_ARTIFACT | contracts/run_artifact_spec_v0.1.json |
| RPT_VALID | reports/validation/ |
| RPT_VERIF | reports/verification/ |
| RPT_AUDIT | reports/pipeline_audit/ |
| CI_PYTEST | .github/workflows/ci_pytest.yml |
| CI_SCHEMA | .github/workflows/ci_schema_check.yml |
| CI_SANITY | .github/workflows/ci_workflow_sanity.yml |

## GRAPH_12__OVERVIEW__ORCHESTRATION.md

| Node ID | Description | Status |
|---------|-------------|--------|
| WF_BACKFILL | .github/workflows/backfill.yml | SCHEDULED (cron: 17 */6 * * *) |
| WF_M15 | .github/workflows/backfill_m15.yml | SCHEDULED |
| WF_INGEST | .github/workflows/ovc_full_ingest.yml | DORMANT (workflow_dispatch only) |
| WF_VALIDATE | .github/workflows/backfill_then_validate.yml | DORMANT (workflow_dispatch only) |
| WF_OPTC | .github/workflows/ovc_option_c_schedule.yml | SCHEDULED (cron: 15 6 * * *) |
| WF_P1 | .github/workflows/path1_evidence.yml | MANUAL |
| WF_P1Q | .github/workflows/path1_evidence_queue.yml | MANUAL |
| WF_REPLAY | .github/workflows/path1_replay_verify.yml | MANUAL |
| WF_NOTION | .github/workflows/notion_sync.yml | SCHEDULED (cron: 17 */2 * * *) |
| WF_PYTEST | .github/workflows/ci_pytest.yml | CI (on push/PR) |
| WF_SCHEMA | .github/workflows/ci_schema_check.yml | CI (on push/PR) |
| WF_SANITY | .github/workflows/ci_workflow_sanity.yml | CI (on push/PR) |
| S_BACKFILL_2H | src/backfill_oanda_2h_checkpointed.py | Active |
| S_BACKFILL_M15 | src/backfill_oanda_m15_checkpointed.py | Active |
| S_C1 | src/derived/compute_c1_v0_1.py | Active |
| S_C2 | src/derived/compute_c2_v0_1.py | Active |
| S_C3 | src/derived/compute_c3_regime_trend_v0_1.py | NOT INVOKED |
| S_OPTC | scripts/run/run_option_c.sh | Active |
| S_PACK | scripts/path1/build_evidence_pack_v0_2.py | Active |
| S_QUEUE | scripts/path1/run_evidence_queue.py | Active |
| S_REPLAY | scripts/path1_replay/run_replay_verification.py | Active |
| S_NOTION | scripts/export/notion_sync.py | Active |

## GRAPH_20__OPT_A__PIPELINE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_BACKFILL | .github/workflows/backfill.yml | Orchestration |
| WF_M15 | .github/workflows/backfill_m15.yml | Orchestration |
| WF_INGEST | .github/workflows/ovc_full_ingest.yml | Orchestration (DORMANT) |
| W_INDEX | infra/ovc-webhook/src/index.ts | Sub-systems |
| W_WRANGLER | infra/ovc-webhook/wrangler.jsonc | Sub-systems |
| S_BACKFILL_2H | src/backfill_oanda_2h_checkpointed.py | Pipelines |
| S_BACKFILL_M15 | src/backfill_oanda_m15_checkpointed.py | Pipelines |
| S_INGEST | src/ingest_history_day.py | Pipelines |
| S_TV_CSV | src/history_sources/tv_csv.py | Data Stores |
| SQL_SCHEMA | sql/00_schema.sql | Data Stores |
| SQL_TABLES | sql/01_tables_min.sql | Data Stores |
| D_RAW | data/raw/tradingview/ | Data Stores |
| O_BLOCKS | ovc.ovc_blocks_v01_1_min | Data Stores (CANONICAL) |
| O_M15 | ovc.ovc_candles_m15_raw | Data Stores (CANONICAL) |
| O_R2 | R2 bucket: tv/YYYY-MM-DD/ | Data Stores |

## GRAPH_21__OPT_B__PIPELINE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_VALIDATE | .github/workflows/backfill_then_validate.yml | Orchestration (DORMANT) |
| I_BLOCKS | ovc.ovc_blocks_v01_1_min | Input (Option A) |
| S_C1 | src/derived/compute_c1_v0_1.py | Pipelines |
| S_C2 | src/derived/compute_c2_v0_1.py | Pipelines |
| S_C3 | src/derived/compute_c3_regime_trend_v0_1.py | Pipelines (NOT INVOKED) |
| S_STUB | src/derived/compute_c3_stub_v0_1.py | Pipelines |
| V_C1 | sql/derived/v_ovc_c1_features_v0_1.sql | Data Stores |
| V_C2 | sql/derived/v_ovc_c2_features_v0_1.sql | Data Stores |
| V_C3 | sql/derived/v_ovc_c3_features_v0_1.sql | Data Stores |
| V_SP | sql/derived/v_ovc_state_plane_v0_2.sql | Data Stores |
| TF_FP | trajectory_families/fingerprint.py | Models |
| TF_CLUSTER | trajectory_families/clustering.py | Models |
| TF_PARAMS | trajectory_families/params_v0_1.json | Models |
| R_PACKS | configs/threshold_packs/*.json | Registries |
| R_CODE | src/config/threshold_registry_v0_1.py | Registries |
| R_DB | ovc_cfg.threshold_packs | Registries |
| SQL_C1C2 | sql/02_derived_c1_c2_tables_v0_1.sql | Data Stores |
| SQL_C3 | sql/05_c3_regime_trend_v0_1.sql | Data Stores |
| SQL_REG | sql/04_threshold_registry_v0_1.sql | Registries |
| SQL_SP | sql/06_state_plane_threshold_pack_v0_2.sql | Data Stores |
| O_C1 | derived.ovc_c1_features | Data Stores (CANONICAL) |
| O_C2 | derived.ovc_c2_features | Data Stores (CANONICAL) |
| O_C3 | derived.ovc_c3_features | Data Stores (CANONICAL) |

## GRAPH_22__OPT_C__PIPELINE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_OPTC | .github/workflows/ovc_option_c_schedule.yml | Orchestration |
| I_VIEWS | derived.v_ovc_c*_features | Input (Option B) |
| S_SH | scripts/run/run_option_c.sh | Orchestration |
| S_PS1 | scripts/run/run_option_c.ps1 | Orchestration |
| S_WRAPPER | scripts/run/run_option_c_wrapper.py | Orchestration |
| S_ART | scripts/run/run_option_c_with_artifact.sh | Orchestration |
| S_MIG | scripts/run/run_migration.py | Orchestration |
| SQL_OPTC | sql/option_c_v0_1.sql | Data Stores |
| SQL_RPT | sql/option_c_run_report.sql | Data Stores |
| SQL_OUT | sql/derived/v_ovc_c_outcomes_v0_1.sql | Data Stores |
| A_SANITY | artifacts/option_c/sanity_local/ | Artifacts |
| A_REPORT | artifacts/option_c/run_report_sanity_local.json | Artifacts |
| A_SPOT | artifacts/option_c/spotchecks_sanity_local.txt | Artifacts |
| O_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 | Data Stores (CANONICAL) |
| R_REPORT | reports/run_report_*.json | Artifacts |
| R_SPOT | reports/spotchecks_*.txt | Artifacts |

## GRAPH_23__OPT_D__PIPELINE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_P1 | .github/workflows/path1_evidence.yml | Orchestration |
| WF_P1Q | .github/workflows/path1_evidence_queue.yml | Orchestration |
| WF_REPLAY | .github/workflows/path1_replay_verify.yml | Orchestration |
| WF_NOTION | .github/workflows/notion_sync.yml | Orchestration |
| I_OUTCOMES | derived.v_ovc_c_outcomes | Input (Option C) |
| I_TF | trajectory_families/ | Input (Option B) |
| S_PACK | scripts/path1/build_evidence_pack_v0_2.py | Orchestration |
| S_QUEUE | scripts/path1/run_evidence_queue.py | Orchestration |
| S_RANGE | scripts/path1/run_evidence_range.py | Orchestration |
| S_SP | scripts/path1/run_state_plane.py | Orchestration |
| S_TF | scripts/path1/run_trajectory_families.py | Orchestration |
| S_OVERLAY | scripts/path1/overlays_v0_3.py | Orchestration |
| S_GEN_Q | scripts/path1/generate_queue_resolved.py | Orchestration |
| S_POST | scripts/path1/validate_post_run.py | QA |
| S_REPLAY | scripts/path1_replay/run_replay_verification.py | QA |
| S_REPLAY_LIB | scripts/path1_replay/lib.py | Sub-systems |
| S_SEAL | scripts/path1_seal/run_seal_manifests.py | Orchestration |
| S_SEAL_LIB | scripts/path1_seal/lib.py | Sub-systems |
| S_NOTION | scripts/export/notion_sync.py | Orchestration |
| S_OANDA | scripts/export/oanda_export_2h_day.py | Orchestration |
| S_ART | src/ovc_ops/run_artifact.py | Orchestration |
| S_ART_CLI | src/ovc_ops/run_artifact_cli.py | Orchestration |
| SQL_EV | sql/path1/evidence/v_path1_evidence_*.sql | Data Stores |
| SQL_SC | sql/path1/scores/score_*.sql | Data Stores |
| SQL_ST | sql/path1/studies/*.sql | Experiments |
| SQL_PATCH | sql/path1/db_patches/patch_*.sql | Orchestration |
| SQL_RUNS | sql/path1/evidence/runs/p1_*/ | Artifacts |
| R_RUNS | reports/runs/run_id/ | Artifacts |
| R_P1_EV | reports/path1/evidence/runs/ | Artifacts |
| R_P1_SC | reports/path1/scores/ | Artifacts |
| R_P1_TF | reports/path1/trajectory_families/ | Artifacts |
| R_QUEUE | reports/path1/evidence/RUN_QUEUE.csv | Artifacts |
| NOTION | Notion databases | External |

## GRAPH_24__QA__PIPELINE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_PYTEST | .github/workflows/ci_pytest.yml | Orchestration |
| WF_SCHEMA | .github/workflows/ci_schema_check.yml | Orchestration |
| WF_SANITY | .github/workflows/ci_workflow_sanity.yml | Orchestration |
| T_DERIVED | tests/test_derived_features.py | QA |
| T_C3 | tests/test_c3_regime_trend.py | QA |
| T_CONTRACT | tests/test_contract_equivalence.py | QA |
| T_MIN | tests/test_min_contract_validation.py | QA |
| T_REG | tests/test_threshold_registry.py | QA |
| T_FP | tests/test_fingerprint.py | QA |
| T_REPLAY | tests/test_path1_replay_structural.py | QA |
| T_FIX | tests/fixtures/ | QA |
| V_DAY | src/validate_day.py | QA |
| V_RANGE | src/validate_range.py | QA |
| V_DERIVED | src/validate/validate_derived_range_v0_1.py | QA |
| CI_VERIFY | scripts/ci/verify_schema_objects.py | QA |
| VAL_STATUS | scripts/validate/pipeline_status.py | QA |
| VAL_PS1 | scripts/validate/validate_day.ps1 | QA |
| SQL_QA | sql/qa_schema.sql | Data Stores |
| SQL_PACK | sql/qa_validation_pack.sql | Data Stores |
| SQL_CORE | sql/qa_validation_pack_core.sql | Data Stores |
| SQL_DRV | sql/qa_validation_pack_derived.sql | Data Stores |
| SQL_GATE | sql/90_verify_gate2.sql | Data Stores (NOT AUTOMATED) |
| SQL_DERIVED | sql/03_qa_derived_validation_v0_1.sql | Data Stores |
| SCH_MIG | schema/applied_migrations.json | Registries (UNVERIFIED) |
| SCH_OBJ | schema/required_objects.txt | Registries |
| C_EXPORT | contracts/export_contract_v0.1.1_min.json | Contracts |
| C_DERIVED | contracts/derived_feature_set_v0.1.json | Contracts |
| C_ARTIFACT | contracts/run_artifact_spec_v0.1.json | Contracts |
| C_EVAL | contracts/eval_contract_v0.1.json | Contracts |
| TL_VAL | tools/validate_contract.py | QA |
| TL_PARSE | tools/parse_export.py | QA |
| TL_MAZE | tools/maze/gen_repo_maze*.py | Documentation |
| A_DERIVED | artifacts/derived_validation/ | Artifacts |
| A_REPLAY | artifacts/path1_replay_report.json | Artifacts |
| R_VALID | reports/validation/ | Artifacts |
| R_VERIF | reports/verification/ | Artifacts |
| R_AUDIT | reports/pipeline_audit/ | Artifacts |

## GRAPH_30__CONTRACTS_MAP.md

| Node ID | Full Path | Owner |
|---------|-----------|-------|
| C_MASTER | docs/contracts/A_TO_D_CONTRACT_v1.md | Cross |
| C_A | docs/contracts/option_a_ingest_contract_v1.md | A |
| C_B | docs/contracts/option_b_derived_contract_v1.md | B |
| C_C | docs/contracts/option_c_outcomes_contract_v1.md | C |
| C_D | docs/contracts/option_d_evidence_contract_v1.md | D |
| C_QA | docs/contracts/qa_validation_contract_v1.md | QA |
| B_INGEST | docs/contracts/ingest_boundary.md | A |
| B_DERIVED | docs/contracts/derived_layer_boundary.md | B |
| B_CLAYER | docs/contracts/c_layer_boundary_spec_v0.1.md | C |
| B_PATH2 | docs/contracts/PATH2_CONTRACT_v1_0.md | Cross (NOT IMPLEMENTED) |
| J_EXPORT_MIN | contracts/export_contract_v0.1.1_min.json | D |
| J_EXPORT_FULL | contracts/export_contract_v0.1_full.json | D |
| J_DERIVED | contracts/derived_feature_set_v0.1.json | B |
| J_ARTIFACT | contracts/run_artifact_spec_v0.1.json | D |
| J_EVAL | contracts/eval_contract_v0.1.json | C |
| G_DOCTRINE | docs/doctrine/OVC_DOCTRINE.md | QA |
| G_GATES | docs/doctrine/GATES.md | QA |
| G_IMMUT | docs/doctrine/IMMUTABILITY_NOTICE.md | QA |
| G_RULES | docs/governance/GOVERNANCE_RULES_v0.1.md | QA |
| G_BRANCH | docs/governance/BRANCH_POLICY.md | QA |

## GRAPH_31__ENFORCEMENT_POINTS.md

| Node ID | Full Path |
|---------|-----------|
| C_EXPORT | contracts/export_contract_v0.1.1_min.json |
| C_DERIVED | contracts/derived_feature_set_v0.1.json |
| C_ARTIFACT | contracts/run_artifact_spec_v0.1.json |
| E_PARSE | infra/ovc-webhook/src/index.ts (parseExport function) |
| E_T_CONTRACT | tests/test_contract_equivalence.py |
| E_T_DERIVED | tests/test_derived_features.py |
| E_T_MIN | tests/test_min_contract_validation.py |
| E_T_REPLAY | tests/test_path1_replay_structural.py |
| E_CI_SCHEMA | .github/workflows/ci_schema_check.yml |
| E_CI_PYTEST | .github/workflows/ci_pytest.yml |
| E_SQL_GATE2 | sql/90_verify_gate2.sql |
| E_SQL_PACK | sql/qa_validation_pack*.sql |
| E_VALIDATE | tools/validate_contract.py |
| S_OBJECTS | schema/required_objects.txt |

## GRAPH_40__ARTIFACT_LIFECYCLE.md

| Node ID | Full Path | Category |
|---------|-----------|----------|
| P_BACKFILL | src/backfill_*.py | Pipelines |
| P_DERIVED | src/derived/compute_c*.py | Pipelines |
| P_OPTC | scripts/run/run_option_c.sh | Orchestration |
| P_PATH1 | scripts/path1/build_evidence_pack_v0_2.py | Orchestration |
| P_TF | scripts/path1/run_trajectory_families.py | Orchestration |
| RA_CODE | src/ovc_ops/run_artifact.py | Sub-systems |
| RA_CLI | src/ovc_ops/run_artifact_cli.py | Sub-systems |
| RA_SPEC | contracts/run_artifact_spec_v0.1.json | Contracts |
| RUN_JSON | reports/runs/run_id/run.json | Artifacts |
| RUN_LOG | reports/runs/run_id/run.log | Artifacts |
| RUN_CHECKS | reports/runs/run_id/checks.json | Artifacts |
| EV_RUNS | reports/path1/evidence/runs/p1_*/ | Artifacts |
| EV_RUN_MD | reports/path1/evidence/runs/p1_*/RUN.md | Artifacts |
| EV_DIS | reports/path1/evidence/runs/p1_*/DIS_v1_1_evidence.md | Artifacts |
| EV_LID | reports/path1/evidence/runs/p1_*/LID_v1_0_evidence.md | Artifacts |
| EV_RES | reports/path1/evidence/runs/p1_*/RES_v1_0_evidence.md | Artifacts |
| EV_OUT | reports/path1/evidence/runs/p1_*/outputs/ | Artifacts |
| EV_QUEUE | reports/path1/evidence/RUN_QUEUE.csv | Artifacts |
| SC_DIS | reports/path1/scores/DIS_v1_1.md | Artifacts |
| SC_LID | reports/path1/scores/LID_v1_0.md | Artifacts |
| SC_RES | reports/path1/scores/RES_v1_0.md | Artifacts |
| TF_V01 | reports/path1/trajectory_families/v0.1/ | Artifacts |
| TF_FP | reports/path1/trajectory_families/v0.1/fingerprints/ | Artifacts |
| TF_INDEX | reports/path1/trajectory_families/v0.1/fingerprints/index.csv | Artifacts |
| AC_SANITY | artifacts/option_c/sanity_local/ | Artifacts |
| AC_RPT | artifacts/option_c/run_report_sanity_local.json | Artifacts |
| AC_SPOT | artifacts/option_c/spotchecks_sanity_local.txt | Artifacts |
| DV_RUNS | artifacts/derived_validation/run_id/ | Artifacts |
| DV_META | artifacts/derived_validation/run_id/meta.json | Artifacts |
| DV_DATA | artifacts/derived_validation/run_id/*.jsonl | Artifacts |
| DV_LATEST | artifacts/derived_validation/LATEST.txt | Artifacts |
| SQL_SNAP | sql/path1/evidence/runs/p1_*/ | Artifacts |

## GRAPH_41__VALIDATION_CHAIN.md

| Node ID | Full Path |
|---------|-----------|
| I_BLOCKS | ovc.ovc_blocks_v01_1_min |
| I_DERIVED | derived.ovc_c*_features |
| I_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 |
| I_EVIDENCE | reports/path1/evidence/runs/ |
| V_DAY | src/validate_day.py |
| V_RANGE | src/validate_range.py |
| V_DERIVED | src/validate/validate_derived_range_v0_1.py |
| SQ_PACK | sql/qa_validation_pack.sql |
| SQ_CORE | sql/qa_validation_pack_core.sql |
| SQ_DRV | sql/qa_validation_pack_derived.sql |
| SQ_GATE | sql/90_verify_gate2.sql |
| R_SCRIPT | scripts/path1_replay/run_replay_verification.py |
| R_LIB | scripts/path1_replay/lib.py |
| RPT_C1 | reports/validation/C1_v0_1_validation.md |
| RPT_C2 | reports/validation/C2_v0_1_validation.md |
| RPT_C3 | reports/validation/C3_v0_1_validation.md |
| RPT_RANGE | reports/validation/validate_range_* |
| VF_DATE | reports/verification/2026-01-19/ |
| VF_ANCHOR | reports/verification/EVIDENCE_ANCHOR_v0_1.md |
| VF_REPRO | reports/verification/REPRO_REPORT_* |
| AU_DATE | reports/pipeline_audit/2026-01-19/ |
| DV_RUN | artifacts/derived_validation/run_id/ |
| DV_LATEST | artifacts/derived_validation/LATEST.txt |
| RA_RPT | artifacts/path1_replay_report.json |
| VP_DATE | data/verification_private/2026-01-19/ |
| VP_CMD | data/verification_private/2026-01-19/commands_run.txt |
| VP_OUT | data/verification_private/2026-01-19/outputs/ |

## GRAPH_50__NEON_SCHEMA_TOPOLOGY.md

| Node ID | Full name / notes |
|---------|-------------------|
| OPT_A | Option A (canonical ingest) |
| OPT_B | Option B (derived features) |
| OPT_C | Option C (outcomes) |
| OPT_D | Option D (Path1/bridge) |
| OPT_QA | QA (validation/governance) |
| N_CANON_BLOCKS | ovc.ovc_blocks_v01_1_min (sql/01_tables_min.sql) |
| N_CANON_M15 | ovc.ovc_candles_m15_raw (sql/path1/db_patches/patch_m15_raw_20260122.sql) |
| N_DER_C1T | derived.ovc_c1_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql) |
| N_DER_C2T | derived.ovc_c2_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql) |
| N_DER_C3T | derived.ovc_c3_regime_trend_v0_1 (sql/05_c3_regime_trend_v0_1.sql) (NOT INVOKED) |
| N_V_C1 | derived.v_ovc_c1_features_v0_1 (sql/derived/v_ovc_c1_features_v0_1.sql) |
| N_V_C2 | derived.v_ovc_c2_features_v0_1 (sql/derived/v_ovc_c2_features_v0_1.sql) |
| N_V_C3 | derived.v_ovc_c3_features_v0_1 (sql/derived/v_ovc_c3_features_v0_1.sql) (NOT INVOKED) |
| N_V_SP | derived.v_ovc_state_plane_v0_2 (sql/derived/v_ovc_state_plane_v0_2.sql) |
| N_V_OUT | derived.v_ovc_c_outcomes_v0_1 (sql/derived/v_ovc_c_outcomes_v0_1.sql) |
| N_CFG_PACK | ovc_cfg.threshold_pack (sql/04_threshold_registry_v0_1.sql) |
| N_CFG_ACTIVE | ovc_cfg.threshold_pack_active (sql/04_threshold_registry_v0_1.sql) |
| N_QA_RUN | ovc_qa.validation_run (sql/qa_schema.sql) |
| N_QA_EXPECT | ovc_qa.expected_blocks (sql/qa_schema.sql) |
| N_QA_TV | ovc_qa.tv_ohlc_2h (sql/qa_schema.sql) |
| N_QA_MISMATCH | ovc_qa.ohlc_mismatch (sql/qa_schema.sql) |
| N_QA_DERIVED | ovc_qa.derived_validation_run (sql/03_qa_derived_validation_v0_1.sql) |
| N_V_SCORE | derived.v_ovc_b_scores_dis_v1_1; derived.v_ovc_b_scores_res_v1_0; derived.v_ovc_b_scores_lid_v1_0 (sql/path1/db_patches/patch_create_score_views_20260120.sql) |
| N_V_EVID | derived.v_path1_evidence_dis_v1_1; derived.v_path1_evidence_res_v1_0; derived.v_path1_evidence_lid_v1_0 (sql/path1/db_patches/patch_create_evidence_views_20260120.sql) |

## GRAPH_51__EXTERNAL_STORES.md

| Node ID | Full name / notes |
|---------|-------------------|
| OPT_A | Option A (canonical ingest) |
| OPT_B | Option B (derived features) |
| OPT_C | Option C (outcomes) |
| OPT_D | Option D (Path1/bridge) |
| OPT_QA | QA (validation/governance) |
| EXT_R2 | R2 raw archive (reports in Option A: tv/YYYY-MM-DD/) |
| EXT_NOTION | Notion databases (sync target) |
| EXT_VERIF | data/verification_private/ (local/private verification store) |
| EXT_ART_C | artifacts/option_c/ |
| EXT_ART_DERIVED | artifacts/derived_validation/ |
| EXT_ART_REPLAY | artifacts/path1_replay_report.json |
| EXT_RPT_OPTC | reports/run_report_*.json; reports/spotchecks_*.txt |
| EXT_RPT_RUNS | reports/runs/run_id/ |
| EXT_RPT_PATH1 | reports/path1/evidence/; reports/path1/scores/; reports/path1/trajectory_families/ |
| EXT_RPT_VALID | reports/validation/ |
| EXT_RPT_VERIF | reports/verification/ |
| EXT_RPT_AUDIT | reports/pipeline_audit/ |

