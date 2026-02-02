# Legend Master

Master mapping of all node IDs used across graphs. Items labeled "Cross" in source maps are assigned to QA ownership here for consistency.

| Node ID | Full path / canonical name | Owning Option | Category | Status |
|---------|----------------------------|---------------|----------|--------|
| AC_RPT | artifacts/option_c/run_report_sanity_local.json | C | artifact | SUPPORTING |
| AC_SANITY | artifacts/option_c/sanity_local/ | C | artifact | SUPPORTING |
| AC_SPOT | artifacts/option_c/spotchecks_sanity_local.txt | C | artifact | SUPPORTING |
| AU_DATE | reports/pipeline_audit/2026-01-19/ | QA | artifact | SUPPORTING |
| A_BACKFILL | src/backfill_*.py | A | pipeline | SUPPORTING |
| A_BLOCKS | ovc.ovc_blocks_v01_1_min | A | store | CANONICAL |
| A_DERIVED | artifacts/derived_validation/ | B | artifact | SUPPORTING |
| A_M15 | ovc.ovc_candles_m15_raw | A | store | CANONICAL |
| A_R2 | R2 bucket archive | External | store | SUPPORTING |
| A_REPLAY | artifacts/path1_replay_report.json | D | artifact | SUPPORTING |
| A_REPORT | artifacts/option_c/run_report_sanity_local.json | C | artifact | SUPPORTING |
| A_SANITY | artifacts/option_c/sanity_local/ | C | artifact | SUPPORTING |
| A_SPOT | artifacts/option_c/spotchecks_sanity_local.txt | C | artifact | SUPPORTING |
| A_WORKER | infra/ovc-webhook | A | subsystem | SUPPORTING |
| B_C1 | src/derived/compute_c1_v0_1.py | B | pipeline | SUPPORTING |
| B_C2 | src/derived/compute_c2_v0_1.py | B | pipeline | SUPPORTING |
| B_C3 | src/derived/compute_c3_regime_trend_v0_1.py (NOT INVOKED) | B | pipeline | NOT INVOKED |
| B_CLAYER | docs/contracts/c_layer_boundary_spec_v0.1.md | C | contract | SUPPORTING |
| B_DERIVED | docs/contracts/derived_layer_boundary.md | B | contract | SUPPORTING |
| B_INGEST | docs/contracts/ingest_boundary.md | A | contract | SUPPORTING |
| B_PATH2 | docs/contracts/PATH2_CONTRACT_v1_0.md | QA | contract | IMPLIED |
| B_TF | trajectory_families/ | B | model | SUPPORTING |
| B_VIEWS | sql/derived/v_ovc_c*_features*.sql | B | store | SUPPORTING |
| CI_PYTEST | .github/workflows/ci_pytest.yml | QA | pipeline | SUPPORTING |
| CI_SANITY | .github/workflows/ci_workflow_sanity.yml | QA | pipeline | SUPPORTING |
| CI_SCHEMA | .github/workflows/ci_schema_check.yml | QA | pipeline | SUPPORTING |
| CI_VERIFY | scripts/ci/verify_schema_objects.py | QA | pipeline | SUPPORTING |
| C_A | docs/contracts/option_a_ingest_contract_v1.md | A | contract | SUPPORTING |
| C_ARTIFACT | contracts/run_artifact_spec_v0.1.json | D | contract | SUPPORTING |
| C_B | docs/contracts/option_b_derived_contract_v1.md | B | contract | SUPPORTING |
| C_C | docs/contracts/option_c_outcomes_contract_v1.md | C | contract | SUPPORTING |
| C_D | docs/contracts/option_d_evidence_contract_v1.md | D | contract | SUPPORTING |
| C_DERIVED | contracts/derived_feature_set_v0.1.json | B | contract | SUPPORTING |
| C_EVAL | contracts/eval_contract_v0.1.json | C | contract | SUPPORTING |
| C_EXPORT | contracts/export_contract_v0.1.1_min.json | D | contract | SUPPORTING |
| C_MASTER | docs/contracts/A_TO_D_CONTRACT_v1.md | QA | contract | SUPPORTING |
| C_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 | C | store | CANONICAL |
| C_QA | docs/contracts/qa_validation_contract_v1.md | QA | contract | SUPPORTING |
| C_RUNNER | scripts/run/run_option_c.sh | C | pipeline | SUPPORTING |
| DV_DATA | artifacts/derived_validation/run_id/*.jsonl | B | artifact | SUPPORTING |
| DV_LATEST | artifacts/derived_validation/LATEST.txt | B | artifact | SUPPORTING |
| DV_META | artifacts/derived_validation/run_id/meta.json | B | artifact | SUPPORTING |
| DV_RUN | artifacts/derived_validation/run_id/ | B | artifact | SUPPORTING |
| DV_RUNS | artifacts/derived_validation/run_id/ | B | artifact | SUPPORTING |
| D_EVIDENCE | reports/path1/evidence/runs/ | D | artifact | SUPPORTING |
| D_NOTION | scripts/export/notion_sync.py | D | pipeline | SUPPORTING |
| D_PATH1 | scripts/path1/ | D | pipeline | SUPPORTING |
| D_RAW | data/raw/tradingview/ | A | store | SUPPORTING |
| D_SCORES | reports/path1/scores/ | D | artifact | SUPPORTING |
| EV_DIS | reports/path1/evidence/runs/p1_*/DIS_v1_1_evidence.md | D | artifact | SUPPORTING |
| EV_LID | reports/path1/evidence/runs/p1_*/LID_v1_0_evidence.md | D | artifact | SUPPORTING |
| EV_OUT | reports/path1/evidence/runs/p1_*/outputs/ | D | artifact | SUPPORTING |
| EV_QUEUE | reports/path1/evidence/RUN_QUEUE.csv | D | artifact | SUPPORTING |
| EV_RES | reports/path1/evidence/runs/p1_*/RES_v1_0_evidence.md | D | artifact | SUPPORTING |
| EV_RUNS | reports/path1/evidence/runs/p1_*/ | D | artifact | SUPPORTING |
| EV_RUN_MD | reports/path1/evidence/runs/p1_*/RUN.md | D | artifact | SUPPORTING |
| EXT_ART_C | artifacts/option_c/ | C | artifact | SUPPORTING |
| EXT_ART_DERIVED | artifacts/derived_validation/ | B | artifact | SUPPORTING |
| EXT_ART_REPLAY | artifacts/path1_replay_report.json | D | artifact | SUPPORTING |
| EXT_NOTION | Notion databases (sync target) | External | store | SUPPORTING |
| EXT_R2 | R2 raw archive (reports in Option A: tv/YYYY-MM-DD/) | External | store | SUPPORTING |
| EXT_RPT_AUDIT | reports/pipeline_audit/ | QA | artifact | SUPPORTING |
| EXT_RPT_OPTC | reports/run_report_*.json; reports/spotchecks_*.txt | C | artifact | SUPPORTING |
| EXT_RPT_PATH1 | reports/path1/evidence/; reports/path1/scores/; reports/path1/trajectory_families/ | D | artifact | SUPPORTING |
| EXT_RPT_RUNS | reports/runs/run_id/ | D | artifact | SUPPORTING |
| EXT_RPT_VALID | reports/validation/ | QA | artifact | SUPPORTING |
| EXT_RPT_VERIF | reports/verification/ | QA | artifact | SUPPORTING |
| EXT_VERIF | data/verification_private/ (local/private verification store) | QA | store | SUPPORTING |
| E_CI_PYTEST | .github/workflows/ci_pytest.yml | QA | pipeline | SUPPORTING |
| E_CI_SCHEMA | .github/workflows/ci_schema_check.yml | QA | pipeline | SUPPORTING |
| E_PARSE | infra/ovc-webhook/src/index.ts (parseExport function) | A | subsystem | SUPPORTING |
| E_SQL_GATE2 | sql/90_verify_gate2.sql | QA | store | SUPPORTING |
| E_SQL_PACK | sql/qa_validation_pack*.sql | QA | store | SUPPORTING |
| E_T_CONTRACT | tests/test_contract_equivalence.py | QA | contract | SUPPORTING |
| E_T_DERIVED | tests/test_derived_features.py | QA | pipeline | SUPPORTING |
| E_T_MIN | tests/test_min_contract_validation.py | QA | contract | SUPPORTING |
| E_T_REPLAY | tests/test_path1_replay_structural.py | QA | pipeline | SUPPORTING |
| E_VALIDATE | tools/validate_contract.py | QA | contract | SUPPORTING |
| G_BRANCH | docs/governance/BRANCH_POLICY.md | QA | contract | SUPPORTING |
| G_DOCTRINE | docs/doctrine/OVC_DOCTRINE.md | QA | contract | SUPPORTING |
| G_GATES | docs/doctrine/GATES.md | QA | contract | SUPPORTING |
| G_IMMUT | docs/doctrine/IMMUTABILITY_NOTICE.md | QA | contract | SUPPORTING |
| G_RULES | docs/governance/GOVERNANCE_RULES_v0.1.md | QA | contract | SUPPORTING |
| I_BLOCKS | ovc.ovc_blocks_v01_1_min | A | store | CANONICAL |
| I_DERIVED | derived.ovc_c*_features | B | store | SUPPORTING |
| I_EVIDENCE | reports/path1/evidence/runs/ | D | artifact | SUPPORTING |
| I_OUTCOMES | derived.v_ovc_c_outcomes | C | store | CANONICAL |
| I_TF | trajectory_families/ | B | model | SUPPORTING |
| I_VIEWS | derived.v_ovc_c*_features | B | store | SUPPORTING |
| J_ARTIFACT | contracts/run_artifact_spec_v0.1.json | D | contract | SUPPORTING |
| J_DERIVED | contracts/derived_feature_set_v0.1.json | B | contract | SUPPORTING |
| J_EVAL | contracts/eval_contract_v0.1.json | C | contract | SUPPORTING |
| J_EXPORT_FULL | contracts/export_contract_v0.1_full.json | D | contract | SUPPORTING |
| J_EXPORT_MIN | contracts/export_contract_v0.1.1_min.json | D | contract | SUPPORTING |
| NEON | Neon PostgreSQL | External | store | SUPPORTING |
| NOTION | Notion databases | External | store | SUPPORTING |
| N_CANON_BLOCKS | ovc.ovc_blocks_v01_1_min (sql/01_tables_min.sql) | A | store | CANONICAL |
| N_CANON_M15 | ovc.ovc_candles_m15_raw (sql/path1/db_patches/patch_m15_raw_20260122.sql) | A | store | CANONICAL |
| N_CFG_ACTIVE | ovc_cfg.threshold_pack_active (sql/04_threshold_registry_v0_1.sql) | B | store | SUPPORTING |
| N_CFG_PACK | ovc_cfg.threshold_pack (sql/04_threshold_registry_v0_1.sql) | B | store | SUPPORTING |
| N_DER_C1T | derived.ovc_c1_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql) | B | store | CANONICAL |
| N_DER_C2T | derived.ovc_c2_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql) | B | store | CANONICAL |
| N_DER_C3T | derived.ovc_c3_regime_trend_v0_1 (sql/05_c3_regime_trend_v0_1.sql) (NOT INVOKED) | B | store | NOT INVOKED |
| N_QA_DERIVED | ovc_qa.derived_validation_run (sql/03_qa_derived_validation_v0_1.sql) | QA | store | SUPPORTING |
| N_QA_EXPECT | ovc_qa.expected_blocks (sql/qa_schema.sql) | QA | store | SUPPORTING |
| N_QA_MISMATCH | ovc_qa.ohlc_mismatch (sql/qa_schema.sql) | QA | store | SUPPORTING |
| N_QA_RUN | ovc_qa.validation_run (sql/qa_schema.sql) | QA | store | SUPPORTING |
| N_QA_TV | ovc_qa.tv_ohlc_2h (sql/qa_schema.sql) | QA | store | SUPPORTING |
| N_V_C1 | derived.v_ovc_c1_features_v0_1 (sql/derived/v_ovc_c1_features_v0_1.sql) | B | store | CANONICAL |
| N_V_C2 | derived.v_ovc_c2_features_v0_1 (sql/derived/v_ovc_c2_features_v0_1.sql) | B | store | CANONICAL |
| N_V_C3 | derived.v_ovc_c3_features_v0_1 (sql/derived/v_ovc_c3_features_v0_1.sql) (NOT INVOKED) | B | store | NOT INVOKED |
| N_V_EVID | derived.v_path1_evidence_dis_v1_1; derived.v_path1_evidence_res_v1_0; derived.v_path1_evidence_lid_v1_0 (sql/path1/db_patches/patch_create_evidence_views_20260120.sql) | D | store | SUPPORTING |
| N_V_OUT | derived.v_ovc_c_outcomes_v0_1 (sql/derived/v_ovc_c_outcomes_v0_1.sql) | C | store | CANONICAL |
| N_V_SCORE | derived.v_ovc_b_scores_dis_v1_1; derived.v_ovc_b_scores_res_v1_0; derived.v_ovc_b_scores_lid_v1_0 (sql/path1/db_patches/patch_create_score_views_20260120.sql) | D | store | SUPPORTING |
| N_V_SP | derived.v_ovc_state_plane_v0_2 (sql/derived/v_ovc_state_plane_v0_2.sql) | B | store | SUPPORTING |
| OANDA | OANDA API source | External | store | SUPPORTING |
| OPT_A | Option A (canonical ingest) | A | subsystem | CANONICAL |
| OPT_B | Option B (derived features) | B | subsystem | SUPPORTING |
| OPT_C | Option C (outcomes) | C | subsystem | SUPPORTING |
| OPT_D | Option D (Path1/bridge) | D | subsystem | SUPPORTING |
| OPT_QA | QA (validation/governance) | QA | subsystem | SUPPORTING |
| O_BLOCKS | ovc.ovc_blocks_v01_1_min | A | store | CANONICAL |
| O_C1 | derived.ovc_c1_features | B | store | CANONICAL |
| O_C2 | derived.ovc_c2_features | B | store | CANONICAL |
| O_C3 | derived.ovc_c3_features | B | store | CANONICAL |
| O_M15 | ovc.ovc_candles_m15_raw | A | store | CANONICAL |
| O_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 | C | store | CANONICAL |
| O_R2 | R2 bucket: tv/YYYY-MM-DD/ | External | store | SUPPORTING |
| PYTEST | tests/ directory | QA | pipeline | SUPPORTING |
| P_BACKFILL | src/backfill_*.py | A | pipeline | SUPPORTING |
| P_DERIVED | src/derived/compute_c*.py | B | pipeline | SUPPORTING |
| P_OPTC | scripts/run/run_option_c.sh | C | pipeline | SUPPORTING |
| P_PATH1 | scripts/path1/build_evidence_pack_v0_2.py | D | pipeline | SUPPORTING |
| P_TF | scripts/path1/run_trajectory_families.py | D | pipeline | SUPPORTING |
| RA_CLI | src/ovc_ops/run_artifact_cli.py | D | pipeline | SUPPORTING |
| RA_CODE | src/ovc_ops/run_artifact.py | D | pipeline | SUPPORTING |
| RA_RPT | artifacts/path1_replay_report.json | D | artifact | SUPPORTING |
| RA_SPEC | contracts/run_artifact_spec_v0.1.json | D | contract | SUPPORTING |
| REPLAY | scripts/path1_replay/run_replay_verification.py | D | pipeline | SUPPORTING |
| RPT_AUDIT | reports/pipeline_audit/ | QA | artifact | SUPPORTING |
| RPT_C1 | reports/validation/C1_v0_1_validation.md | QA | artifact | SUPPORTING |
| RPT_C2 | reports/validation/C2_v0_1_validation.md | QA | artifact | SUPPORTING |
| RPT_C3 | reports/validation/C3_v0_1_validation.md | QA | artifact | SUPPORTING |
| RPT_RANGE | reports/validation/validate_range_* | QA | artifact | SUPPORTING |
| RPT_VALID | reports/validation/ | QA | artifact | SUPPORTING |
| RPT_VERIF | reports/verification/ | QA | artifact | SUPPORTING |
| RUN_CHECKS | reports/runs/run_id/checks.json | D | artifact | SUPPORTING |
| RUN_JSON | reports/runs/run_id/run.json | D | artifact | SUPPORTING |
| RUN_LOG | reports/runs/run_id/run.log | D | artifact | SUPPORTING |
| R_AUDIT | reports/pipeline_audit/ | QA | artifact | SUPPORTING |
| R_CODE | src/config/threshold_registry_v0_1.py | B | pipeline | SUPPORTING |
| R_DB | ovc_cfg.threshold_packs | B | store | SUPPORTING |
| R_LIB | scripts/path1_replay/lib.py | D | subsystem | SUPPORTING |
| R_P1_EV | reports/path1/evidence/runs/ | D | artifact | SUPPORTING |
| R_P1_SC | reports/path1/scores/ | D | artifact | SUPPORTING |
| R_P1_TF | reports/path1/trajectory_families/ | D | artifact | SUPPORTING |
| R_PACKS | configs/threshold_packs/*.json | B | store | SUPPORTING |
| R_QUEUE | reports/path1/evidence/RUN_QUEUE.csv | D | artifact | SUPPORTING |
| R_REPORT | reports/run_report_*.json | C | artifact | SUPPORTING |
| R_RUNS | reports/runs/run_id/ | D | artifact | SUPPORTING |
| R_SCRIPT | scripts/path1_replay/run_replay_verification.py | D | pipeline | SUPPORTING |
| R_SPOT | reports/spotchecks_*.txt | C | artifact | SUPPORTING |
| R_VALID | reports/validation/ | QA | artifact | SUPPORTING |
| R_VERIF | reports/verification/ | QA | artifact | SUPPORTING |
| SCH_MIG | schema/applied_migrations.json | QA | store | UNVERIFIED |
| SCH_OBJ | schema/required_objects.txt | QA | store | SUPPORTING |
| SC_DIS | reports/path1/scores/DIS_v1_1.md | D | artifact | SUPPORTING |
| SC_LID | reports/path1/scores/LID_v1_0.md | D | artifact | SUPPORTING |
| SC_RES | reports/path1/scores/RES_v1_0.md | D | artifact | SUPPORTING |
| SQL_C1C2 | sql/02_derived_c1_c2_tables_v0_1.sql | B | store | SUPPORTING |
| SQL_C3 | sql/05_c3_regime_trend_v0_1.sql | B | store | SUPPORTING |
| SQL_CORE | sql/qa_validation_pack_core.sql | QA | store | SUPPORTING |
| SQL_DERIVED | sql/03_qa_derived_validation_v0_1.sql | QA | store | SUPPORTING |
| SQL_DRV | sql/qa_validation_pack_derived.sql | QA | store | SUPPORTING |
| SQL_EV | sql/path1/evidence/v_path1_evidence_*.sql | D | store | SUPPORTING |
| SQL_GATE | sql/90_verify_gate2.sql | QA | store | SUPPORTING |
| SQL_GATE2 | sql/90_verify_gate2.sql (NOT AUTOMATED) | QA | store | SUPPORTING |
| SQL_OPTC | sql/option_c_v0_1.sql | C | store | SUPPORTING |
| SQL_OUT | sql/derived/v_ovc_c_outcomes_v0_1.sql | C | store | SUPPORTING |
| SQL_PACK | sql/qa_validation_pack*.sql | QA | store | SUPPORTING |
| SQL_PATCH | sql/path1/db_patches/patch_*.sql | D | store | SUPPORTING |
| SQL_QA | sql/qa_schema.sql | QA | store | SUPPORTING |
| SQL_REG | sql/04_threshold_registry_v0_1.sql | B | store | SUPPORTING |
| SQL_RPT | sql/option_c_run_report.sql | C | store | SUPPORTING |
| SQL_RUNS | sql/path1/evidence/runs/p1_*/ | D | store | SUPPORTING |
| SQL_SC | sql/path1/scores/score_*.sql | D | store | SUPPORTING |
| SQL_SCHEMA | sql/00_schema.sql | A | store | SUPPORTING |
| SQL_SNAP | sql/path1/evidence/runs/p1_*/ | D | store | SUPPORTING |
| SQL_SP | sql/06_state_plane_threshold_pack_v0_2.sql | B | store | SUPPORTING |
| SQL_ST | sql/path1/studies/*.sql | D | store | SUPPORTING |
| SQL_TABLES | sql/01_tables_min.sql | A | store | SUPPORTING |
| SQ_CORE | sql/qa_validation_pack_core.sql | QA | store | SUPPORTING |
| SQ_DRV | sql/qa_validation_pack_derived.sql | QA | store | SUPPORTING |
| SQ_GATE | sql/90_verify_gate2.sql | QA | store | SUPPORTING |
| SQ_PACK | sql/qa_validation_pack.sql | QA | store | SUPPORTING |
| S_ART | scripts/run/run_option_c_with_artifact.sh | C | pipeline | SUPPORTING |
| S_ART_CLI | src/ovc_ops/run_artifact_cli.py | D | pipeline | SUPPORTING |
| S_BACKFILL_2H | src/backfill_oanda_2h_checkpointed.py | A | pipeline | SUPPORTING |
| S_BACKFILL_M15 | src/backfill_oanda_m15_checkpointed.py | A | pipeline | SUPPORTING |
| S_C1 | src/derived/compute_c1_v0_1.py | B | pipeline | SUPPORTING |
| S_C2 | src/derived/compute_c2_v0_1.py | B | pipeline | SUPPORTING |
| S_C3 | src/derived/compute_c3_regime_trend_v0_1.py | B | pipeline | NOT INVOKED |
| S_GEN_Q | scripts/path1/generate_queue_resolved.py | D | pipeline | SUPPORTING |
| S_INGEST | src/ingest_history_day.py | A | pipeline | SUPPORTING |
| S_MIG | scripts/run/run_migration.py | C | pipeline | SUPPORTING |
| S_NOTION | scripts/export/notion_sync.py | D | pipeline | SUPPORTING |
| S_OANDA | scripts/export/oanda_export_2h_day.py | D | pipeline | SUPPORTING |
| S_OBJECTS | schema/required_objects.txt | QA | store | SUPPORTING |
| S_OPTC | scripts/run/run_option_c.sh | C | pipeline | SUPPORTING |
| S_OVERLAY | scripts/path1/overlays_v0_3.py | D | pipeline | SUPPORTING |
| S_PACK | scripts/path1/build_evidence_pack_v0_2.py | D | pipeline | SUPPORTING |
| S_POST | scripts/path1/validate_post_run.py | QA | pipeline | SUPPORTING |
| S_PS1 | scripts/run/run_option_c.ps1 | C | pipeline | SUPPORTING |
| S_QUEUE | scripts/path1/run_evidence_queue.py | D | pipeline | SUPPORTING |
| S_RANGE | scripts/path1/run_evidence_range.py | D | pipeline | SUPPORTING |
| S_REPLAY | scripts/path1_replay/run_replay_verification.py | D | pipeline | SUPPORTING |
| S_REPLAY_LIB | scripts/path1_replay/lib.py | D | subsystem | SUPPORTING |
| S_SEAL | scripts/path1_seal/run_seal_manifests.py | D | pipeline | SUPPORTING |
| S_SEAL_LIB | scripts/path1_seal/lib.py | D | subsystem | SUPPORTING |
| S_SH | scripts/run/run_option_c.sh | C | pipeline | SUPPORTING |
| S_SP | scripts/path1/run_state_plane.py | D | pipeline | SUPPORTING |
| S_STUB | src/derived/compute_c3_stub_v0_1.py | B | pipeline | SUPPORTING |
| S_TF | scripts/path1/run_trajectory_families.py | D | pipeline | SUPPORTING |
| S_TV_CSV | src/history_sources/tv_csv.py | A | pipeline | SUPPORTING |
| S_WRAPPER | scripts/run/run_option_c_wrapper.py | C | pipeline | SUPPORTING |
| TF_CLUSTER | trajectory_families/clustering.py | B | model | SUPPORTING |
| TF_FP | trajectory_families/fingerprint.py | B | model | SUPPORTING |
| TF_INDEX | reports/path1/trajectory_families/v0.1/fingerprints/index.csv | D | artifact | SUPPORTING |
| TF_PARAMS | trajectory_families/params_v0_1.json | B | model | SUPPORTING |
| TF_V01 | reports/path1/trajectory_families/v0.1/ | D | artifact | SUPPORTING |
| TL_MAZE | tools/maze/gen_repo_maze*.py | QA | subsystem | SUPPORTING |
| TL_PARSE | tools/parse_export.py | QA | subsystem | SUPPORTING |
| TL_VAL | tools/validate_contract.py | QA | contract | SUPPORTING |
| TV | TradingView alert source | External | store | SUPPORTING |
| T_C3 | tests/test_c3_regime_trend.py | QA | pipeline | SUPPORTING |
| T_CONTRACT | tests/test_contract_equivalence.py | QA | contract | SUPPORTING |
| T_DERIVED | tests/test_derived_features.py | QA | pipeline | SUPPORTING |
| T_FIX | tests/fixtures/ | QA | pipeline | SUPPORTING |
| T_FP | tests/test_fingerprint.py | QA | pipeline | SUPPORTING |
| T_MIN | tests/test_min_contract_validation.py | QA | contract | SUPPORTING |
| T_REG | tests/test_threshold_registry.py | QA | pipeline | SUPPORTING |
| T_REPLAY | tests/test_path1_replay_structural.py | QA | pipeline | SUPPORTING |
| VAL_DAY | src/validate_day.py | QA | pipeline | SUPPORTING |
| VAL_DERIVED | src/validate/validate_derived_range_v0_1.py | QA | pipeline | SUPPORTING |
| VAL_PS1 | scripts/validate/validate_day.ps1 | QA | pipeline | SUPPORTING |
| VAL_RANGE | src/validate_range.py | QA | pipeline | SUPPORTING |
| VAL_STATUS | scripts/validate/pipeline_status.py | QA | pipeline | SUPPORTING |
| VF_ANCHOR | reports/verification/EVIDENCE_ANCHOR_v0_1.md | QA | artifact | SUPPORTING |
| VF_DATE | reports/verification/2026-01-19/ | QA | artifact | SUPPORTING |
| VF_REPRO | reports/verification/REPRO_REPORT_* | QA | artifact | SUPPORTING |
| VP_CMD | data/verification_private/2026-01-19/commands_run.txt | QA | store | SUPPORTING |
| VP_DATE | data/verification_private/2026-01-19/ | QA | store | SUPPORTING |
| VP_OUT | data/verification_private/2026-01-19/outputs/ | QA | store | SUPPORTING |
| V_C1 | sql/derived/v_ovc_c1_features_v0_1.sql | B | store | SUPPORTING |
| V_C2 | sql/derived/v_ovc_c2_features_v0_1.sql | B | store | SUPPORTING |
| V_C3 | sql/derived/v_ovc_c3_features_v0_1.sql | B | store | SUPPORTING |
| V_DAY | src/validate_day.py | QA | pipeline | SUPPORTING |
| V_DERIVED | src/validate/validate_derived_range_v0_1.py | QA | pipeline | SUPPORTING |
| V_RANGE | src/validate_range.py | QA | pipeline | SUPPORTING |
| V_SP | sql/derived/v_ovc_state_plane_v0_2.sql | B | store | SUPPORTING |
| WF_BACKFILL | .github/workflows/backfill.yml | A | pipeline | SUPPORTING |
| WF_INGEST | .github/workflows/ovc_full_ingest.yml | A | pipeline | DORMANT |
| WF_M15 | .github/workflows/backfill_m15.yml | A | pipeline | SUPPORTING |
| WF_NOTION | .github/workflows/notion_sync.yml | D | pipeline | SUPPORTING |
| WF_OPTC | .github/workflows/ovc_option_c_schedule.yml | C | pipeline | SUPPORTING |
| WF_P1 | .github/workflows/path1_evidence.yml | D | pipeline | SUPPORTING |
| WF_P1Q | .github/workflows/path1_evidence_queue.yml | D | pipeline | SUPPORTING |
| WF_PYTEST | .github/workflows/ci_pytest.yml | QA | pipeline | SUPPORTING |
| WF_REPLAY | .github/workflows/path1_replay_verify.yml | D | pipeline | SUPPORTING |
| WF_SANITY | .github/workflows/ci_workflow_sanity.yml | QA | pipeline | SUPPORTING |
| WF_SCHEMA | .github/workflows/ci_schema_check.yml | QA | pipeline | SUPPORTING |
| WF_VALIDATE | .github/workflows/backfill_then_validate.yml | B | pipeline | DORMANT |
| W_INDEX | infra/ovc-webhook/src/index.ts | A | subsystem | SUPPORTING |
| W_WRANGLER | infra/ovc-webhook/wrangler.jsonc | A | subsystem | SUPPORTING |
## ADDITIONS (from graph_node_missing_legend_ids) — 2026-02-02 21:10:38


## CANONICAL_NODEID_APPEND — 2026-02-02T21:20:53Z

| Node ID | Full path / canonical name | Owning Option | Category | Status |
|---------|----------------------------|---------------|----------|--------|
| A_BACKFILL_2H | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_BACKFILL_M15 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_INGEST | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_RAW | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_SCHEMA | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_TV_CSV | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_WF_BACKFILL | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_WF_FULL | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| A_WF_M15 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_CLUSTER | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_FP | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_PARAMS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_REG | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_STUB | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_TH_C3 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_TH_SP | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_V_C1 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_V_C2 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_V_C3 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_V_SP | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| B_WF_VALIDATE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| C_SANITY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| C_SH | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| C_SQL | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| C_WF | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| C_WRAPPER | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_ARTIFACT | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_OVERLAYS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_P1_EV | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_P1_SCORES | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_P1_TF | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_PACK | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_PINE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_QUEUE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_RANGE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_REPLAY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_RUNS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SEAL | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SP | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SQL_EV | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SQL_PATCH | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SQL_SC | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_SQL_ST | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_TF | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_WF_NOTION | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_WF_P1 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_WF_Q | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_WF_REPLAY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| D_WORKER | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_A_DERIVED | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_C_ARTIFACT | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_C_DERIVED | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_C_EXPORT | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_D_CONTRACTS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_D_DOCTRINE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_D_GOVERN | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_FIXTURES | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_MAZE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_MIGRATIONS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_OBJECTS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_PYTEST | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_R_AUDIT | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_R_VALID | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_R_VERIF | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_SANITY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_SCHEMA | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_SQL_GATE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_SQL_QA | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_T_C3 | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_T_CONTRACT | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_T_DERIVED | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_T_FP | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_T_REPLAY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_VALIDATE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_VAL_DAY | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_VAL_DERIVED | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| QA_VAL_RANGE | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |
| TESTS | TODO: define | UNKNOWN | UNKNOWN | UNKNOWN |

