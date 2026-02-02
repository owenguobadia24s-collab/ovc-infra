# Graph 50 — Neon Schema Topology

**Question:** What canonical tables/views/config tables exist in Neon, and which options read/write them?


```mermaid
graph LR

  %% Options
  subgraph OPTS["Options"]
    OPT_A["OPT_A Option A"]
    OPT_B["OPT_B Option B"]
    OPT_C["OPT_C Option C"]
    OPT_D["OPT_D Option D"]
    OPT_QA["OPT_QA QA"]
  end

  %% Canonical tables
  subgraph OVC["ovc schema — canonical"]
    N_CANON_BLOCKS["N_CANON_BLOCKS ovc_blocks_v01_1_min"]
    N_CANON_M15["N_CANON_M15 ovc_candles_m15_raw"]
  end

  %% Derived tables
  subgraph DER_T["derived schema — tables"]
    N_DER_C1T["N_DER_C1T ovc_c1_features_v0_1"]
    N_DER_C2T["N_DER_C2T ovc_c2_features_v0_1"]
    N_DER_C3T["N_DER_C3T ovc_c3_regime_trend_v0_1 NOT INVOKED"]
  end

  %% Derived views
  subgraph DER_V["derived schema — views"]
    N_V_C1["N_V_C1 v_ovc_c1_features_v0_1"]
    N_V_C2["N_V_C2 v_ovc_c2_features_v0_1"]
    N_V_C3["N_V_C3 v_ovc_c3_features_v0_1 NOT INVOKED"]
    N_V_SP["N_V_SP v_ovc_state_plane_v0_2"]
    N_V_OUT["N_V_OUT v_ovc_c_outcomes_v0_1"]
  end

  %% Config tables
  subgraph CFG["ovc_cfg schema"]
    N_CFG_PACK["N_CFG_PACK threshold_pack"]
    N_CFG_ACTIVE["N_CFG_ACTIVE threshold_pack_active"]
  end

  %% QA tables
  subgraph QA["ovc_qa schema"]
    N_QA_RUN["N_QA_RUN validation_run"]
    N_QA_EXPECT["N_QA_EXPECT expected_blocks"]
    N_QA_TV["N_QA_TV tv_ohlc_2h"]
    N_QA_MISMATCH["N_QA_MISMATCH ohlc_mismatch"]
    N_QA_DERIVED["N_QA_DERIVED derived_validation_run"]
  end

  %% Path1 views
  subgraph PATH1["Path1 views — derived"]
    N_V_SCORE["N_V_SCORE v_ovc_b_scores_*"]
    N_V_EVID["N_V_EVID v_path1_evidence_*"]
  end

  %% Option A
  OPT_A -->|write| N_CANON_BLOCKS
  OPT_A -->|write| N_CANON_M15

  %% Option B
  OPT_B -->|read| N_CANON_BLOCKS
  OPT_B -->|write| N_DER_C1T
  OPT_B -->|write| N_DER_C2T
  OPT_B -.->|write NOT INVOKED| N_DER_C3T
  OPT_B -->|define| N_V_C1
  OPT_B -->|define| N_V_C2
  OPT_B -.->|define NOT INVOKED| N_V_C3
  OPT_B -->|define| N_V_SP
  OPT_B -->|read/write| N_CFG_PACK
  OPT_B -->|read/write| N_CFG_ACTIVE

  %% Option C
  OPT_C -->|read| N_V_C1
  OPT_C -->|read| N_V_C2
  OPT_C -->|read| N_V_C3
  OPT_C -->|define| N_V_OUT

  %% Option D
  OPT_D -->|read| N_V_OUT
  OPT_D -->|read| N_V_SCORE
  OPT_D -->|read| N_V_EVID

  %% QA
  OPT_QA -->|read| N_CANON_BLOCKS
  OPT_QA -->|read| N_V_C1
  OPT_QA -->|read| N_V_C2
  OPT_QA -->|write| N_QA_RUN
  OPT_QA -->|write| N_QA_EXPECT
  OPT_QA -->|write| N_QA_TV
  OPT_QA -->|write| N_QA_MISMATCH
  OPT_QA -->|write| N_QA_DERIVED

  %% View dependencies
  N_DER_C1T --> N_V_C1
  N_DER_C2T --> N_V_C2
  N_DER_C3T -.-> N_V_C3
  N_V_C1 --> N_V_OUT
  N_V_C2 --> N_V_OUT
  N_V_C3 --> N_V_OUT
  N_V_SCORE --> N_V_EVID
  N_V_OUT --> N_V_EVID
```

## Legend

| Node ID        | Full name / notes                                                                                                                                                       |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OPT_A          | Option A (canonical ingest)                                                                                                                                             |
| OPT_B          | Option B (derived features)                                                                                                                                             |
| OPT_C          | Option C (outcomes)                                                                                                                                                     |
| OPT_D          | Option D (Path1/bridge)                                                                                                                                                 |
| OPT_QA         | QA (validation/governance)                                                                                                                                              |
| N_CANON_BLOCKS | ovc.ovc_blocks_v01_1_min (sql/01_tables_min.sql)                                                                                                                        |
| N_CANON_M15    | ovc.ovc_candles_m15_raw (sql/path1/db_patches/patch_m15_raw_20260122.sql)                                                                                               |
| N_DER_C1T      | derived.ovc_c1_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql)                                                                                                     |
| N_DER_C2T      | derived.ovc_c2_features_v0_1 (sql/02_derived_c1_c2_tables_v0_1.sql)                                                                                                     |
| N_DER_C3T      | derived.ovc_c3_regime_trend_v0_1 (sql/05_c3_regime_trend_v0_1.sql) (NOT INVOKED)                                                                                        |
| N_V_C1         | derived.v_ovc_c1_features_v0_1 (sql/derived/v_ovc_c1_features_v0_1.sql)                                                                                                 |
| N_V_C2         | derived.v_ovc_c2_features_v0_1 (sql/derived/v_ovc_c2_features_v0_1.sql)                                                                                                 |
| N_V_C3         | derived.v_ovc_c3_features_v0_1 (sql/derived/v_ovc_c3_features_v0_1.sql) (NOT INVOKED)                                                                                   |
| N_V_SP         | derived.v_ovc_state_plane_v0_2 (sql/derived/v_ovc_state_plane_v0_2.sql)                                                                                                 |
| N_V_OUT        | derived.v_ovc_c_outcomes_v0_1 (sql/derived/v_ovc_c_outcomes_v0_1.sql)                                                                                                   |
| N_CFG_PACK     | ovc_cfg.threshold_pack (sql/04_threshold_registry_v0_1.sql)                                                                                                             |
| N_CFG_ACTIVE   | ovc_cfg.threshold_pack_active (sql/04_threshold_registry_v0_1.sql)                                                                                                      |
| N_QA_RUN       | ovc_qa.validation_run (sql/qa_schema.sql)                                                                                                                               |
| N_QA_EXPECT    | ovc_qa.expected_blocks (sql/qa_schema.sql)                                                                                                                              |
| N_QA_TV        | ovc_qa.tv_ohlc_2h (sql/qa_schema.sql)                                                                                                                                   |
| N_QA_MISMATCH  | ovc_qa.ohlc_mismatch (sql/qa_schema.sql)                                                                                                                                |
| N_QA_DERIVED   | ovc_qa.derived_validation_run (sql/03_qa_derived_validation_v0_1.sql)                                                                                                   |
| N_V_SCORE      | derived.v_ovc_b_scores_dis_v1_1; derived.v_ovc_b_scores_res_v1_0; derived.v_ovc_b_scores_lid_v1_0 (sql/path1/db_patches/patch_create_score_views_20260120.sql)          |
| N_V_EVID       | derived.v_path1_evidence_dis_v1_1; derived.v_path1_evidence_res_v1_0; derived.v_path1_evidence_lid_v1_0 (sql/path1/db_patches/patch_create_evidence_views_20260120.sql) |

