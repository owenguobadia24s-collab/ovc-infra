# Option Internal Pipeline Graph

```mermaid
%%─────────────────────────────────────────────────────────────────────────────
%% GRAPH 2 — OPTION INTERNAL PIPELINE GRAPH (BOX FORM)
%% Source: OPT_A/B/C/D/QA__ORG_MAP_DRAFT.md
%%─────────────────────────────────────────────────────────────────────────────
flowchart LR

  subgraph OPTA[Option A — Canonical Ingest]
    direction TB
    subgraph A_PIPES[Pipelines]
      A_WF_BACKFILL[.github/workflows/backfill.yml - cron: 17 */6 * * *]
      A_WF_M15[.github/workflows/backfill_m15.yml]
      A_WF_FULL[.github/workflows/ovc_full_ingest.yml - DORMANT]
    end
    subgraph A_SUBS[Sub-systems]
      A_WORKER[infra/ovc-webhook/src/index.ts]
      A_R2[wrangler.jsonc - R2 bucket binding]
    end
    subgraph A_SRC[src/ ingest]
      A_BACKFILL_2H[src/backfill_oanda_2h_checkpointed.py]
      A_BACKFILL_M15[src/backfill_oanda_m15_checkpointed.py]
      A_INGEST[src/ingest_history_day.py]
      A_TV_CSV[src/history_sources/tv_csv.py]
    end
    subgraph A_SQL[sql/ schema]
      A_SCHEMA[sql/00_schema.sql + sql/01_tables_min.sql]
    end
    subgraph A_DATA[data/]
      A_RAW[data/raw/tradingview/]
    end
  end

  subgraph OPTB[Option B — Derived Features]
    direction TB
    subgraph B_PIPES[Pipelines]
      B_WF_VALIDATE[.github/workflows/backfill_then_validate.yml - DORMANT]
    end
    subgraph B_SRC[src/derived/]
      B_C1[src/derived/compute_c1_v0_1.py]
      B_C2[src/derived/compute_c2_v0_1.py]
      B_C3[src/derived/compute_c3_regime_trend_v0_1.py - NOT INVOKED]
      B_STUB[src/derived/compute_c3_stub_v0_1.py]
    end
    subgraph B_SQL[sql/derived/]
      B_V_C1[sql/derived/v_ovc_c1_features_v0_1.sql]
      B_V_C2[sql/derived/v_ovc_c2_features_v0_1.sql]
      B_V_C3[sql/derived/v_ovc_c3_features_v0_1.sql]
      B_V_SP[sql/derived/v_ovc_state_plane_v0_2.sql]
    end
    subgraph B_MODELS[trajectory_families/]
      B_FP[trajectory_families/fingerprint.py]
      B_CLUSTER[trajectory_families/clustering.py]
      B_PARAMS[trajectory_families/params_v0_1.json]
    end
    subgraph B_CFG[configs/threshold_packs/]
      B_TH_C3[configs/threshold_packs/c3_regime_trend_v1.json]
      B_TH_SP[configs/threshold_packs/state_plane_v0_2_default_v1.json]
    end
    subgraph B_REG[src/config/]
      B_REG[src/config/threshold_registry_v0_1.py]
    end
  end

  subgraph OPTC[Option C — Outcomes]
    direction TB
    subgraph C_PIPES[Pipelines]
      C_WF[.github/workflows/ovc_option_c_schedule.yml - cron: 15 6 * * *]
    end
    subgraph C_SCRIPTS[scripts/run/]
      C_SH[scripts/run/run_option_c.sh]
      C_WRAPPER[scripts/run/run_option_c_wrapper.py]
    end
    subgraph C_SQL[sql/]
      C_SQL[sql/option_c_v0_1.sql + sql/option_c_run_report.sql]
      C_OUTCOMES[sql/derived/v_ovc_c_outcomes_v0_1.sql]
    end
    subgraph C_ART[artifacts/option_c/]
      C_SANITY[artifacts/option_c/sanity_local/]
    end
  end

  subgraph OPTD[Option D — Paths / Bridge]
    direction TB
    subgraph D_PIPES[Pipelines]
      D_WF_P1[.github/workflows/path1_evidence.yml]
      D_WF_Q[.github/workflows/path1_evidence_queue.yml]
      D_WF_REPLAY[.github/workflows/path1_replay_verify.yml]
      D_WF_NOTION[.github/workflows/notion_sync.yml - cron: 17 */2 * * *]
    end
    subgraph D_P1[scripts/path1/]
      D_PACK[scripts/path1/build_evidence_pack_v0_2.py]
      D_QUEUE[scripts/path1/run_evidence_queue.py]
      D_RANGE[scripts/path1/run_evidence_range.py]
      D_SP[scripts/path1/run_state_plane.py]
      D_TF[scripts/path1/run_trajectory_families.py]
      D_OVERLAYS[scripts/path1/overlays_v0_3.py]
    end
    subgraph D_REPLAY[scripts/path1_replay/]
      D_REPLAY[scripts/path1_replay/run_replay_verification.py]
    end
    subgraph D_SEAL[scripts/path1_seal/]
      D_SEAL[scripts/path1_seal/run_seal_manifests.py]
    end
    subgraph D_OPS[src/ovc_ops/]
      D_ARTIFACT[src/ovc_ops/run_artifact.py]
    end
    subgraph D_EXPORT[scripts/export/]
      D_NOTION[scripts/export/notion_sync.py]
    end
    subgraph D_REPORTS[reports/]
      D_RUNS[reports/runs/run_id/]
      D_P1_EV[reports/path1/evidence/runs/]
      D_P1_SCORES[reports/path1/scores/]
      D_P1_TF[reports/path1/trajectory_families/]
    end
    subgraph D_SQL[sql/path1/]
      D_SQL_EV[sql/path1/evidence/v_path1_evidence_*.sql]
      D_SQL_SC[sql/path1/scores/score_*.sql]
      D_SQL_ST[sql/path1/studies/*.sql]
      D_SQL_PATCH[sql/path1/db_patches/patch_*.sql]
    end
    subgraph D_INFRA[infra/ovc-webhook/]
      D_WORKER[infra/ovc-webhook/src/index.ts]
    end
    subgraph D_PINE[pine/]
      D_PINE[pine/OVC_v0_1.pine + pine/export_module_v0.1.pine]
    end
  end

  subgraph QA[QA — Validation & Governance]
    direction TB
    subgraph QA_CI[.github/workflows CI]
      QA_PYTEST[ci_pytest.yml]
      QA_SCHEMA[ci_schema_check.yml]
      QA_SANITY[ci_workflow_sanity.yml]
    end
    subgraph QA_TESTS[tests/]
      QA_T_DERIVED[test_derived_features.py]
      QA_T_C3[test_c3_regime_trend.py]
      QA_T_CONTRACT[test_contract_equivalence.py]
      QA_T_FP[test_fingerprint.py]
      QA_T_REPLAY[test_path1_replay_structural.py]
      QA_FIXTURES[fixtures/sample_exports/]
    end
    subgraph QA_VAL[Validation Harness]
      QA_VAL_DAY[src/validate_day.py]
      QA_VAL_RANGE[src/validate_range.py]
      QA_VAL_DERIVED[src/validate/validate_derived_range_v0_1.py]
    end
    subgraph QA_SQL[sql QA]
      QA_SQL_QA[sql/qa_schema.sql + sql/qa_validation_pack*.sql]
      QA_SQL_GATE[sql/90_verify_gate2.sql]
    end
    subgraph QA_SCHEMA[schema/]
      QA_MIGRATIONS[schema/applied_migrations.json - ALL UNVERIFIED]
      QA_OBJECTS[schema/required_objects.txt]
    end
    subgraph QA_CONTRACTS[contracts/]
      QA_C_EXPORT[export_contract_v0.1.1_min.json]
      QA_C_DERIVED[derived_feature_set_v0.1.json]
      QA_C_ARTIFACT[run_artifact_spec_v0.1.json]
    end
    subgraph QA_DOCS[docs/]
      QA_D_DOCTRINE[docs/doctrine/OVC_DOCTRINE.md]
      QA_D_GOVERN[docs/governance/GOVERNANCE_RULES_v0.1.md]
      QA_D_CONTRACTS[docs/contracts/A_TO_D_CONTRACT_v1.md]
    end
    subgraph QA_TOOLS[tools/]
      QA_VALIDATE[tools/validate_contract.py]
      QA_MAZE[tools/maze/gen_repo_maze*.py]
    end
    subgraph QA_REPORTS[reports QA]
      QA_R_VALID[reports/validation/]
      QA_R_VERIF[reports/verification/]
      QA_R_AUDIT[reports/pipeline_audit/]
    end
    subgraph QA_ART[artifacts QA]
      QA_A_DERIVED[artifacts/derived_validation/]
    end
  end

  %% Cross-cutting connections (script -> workflow)
  A_BACKFILL_2H --> A_WF_BACKFILL
  A_BACKFILL_M15 --> A_WF_M15
  B_C1 --> B_WF_VALIDATE
  B_C2 --> B_WF_VALIDATE
  C_SH --> C_WF
  D_QUEUE --> D_WF_Q
  D_PACK --> D_WF_P1
  D_REPLAY --> D_WF_REPLAY
  D_NOTION --> D_WF_NOTION

  %% src/ and sql/ cross references (conceptual)
  A_SCHEMA -.-> A_BACKFILL_2H
  B_V_C1 -.-> B_C1
  B_V_C2 -.-> B_C2
  C_OUTCOMES -.-> C_SH
  D_SQL_EV -.-> D_PACK

  %% Styling
  classDef dormant fill:#ffcdd2,stroke:#c62828,stroke-width:1px,stroke-dasharray:5
  classDef qaStyle fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

  class A_WF_FULL,B_WF_VALIDATE,B_C3 dormant
  class QA_CI,QA_TESTS,QA_VAL,QA_CONTRACTS,QA_DOCS qaStyle
```
