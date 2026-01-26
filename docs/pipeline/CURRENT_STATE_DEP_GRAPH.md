# CURRENT STATE: Dependency Graph

**Status: CURRENT_STATE (frozen on 2026-01-23)**

Text-based dependency graph showing: ingestion sources → tables → views/tables → scripts → workflows → committed artifacts.

---

## 1. Option A – Ingestion Dependencies

```
EXTERNAL SOURCES
================
┌─────────────────┐    ┌───────────────────┐    ┌────────────────────┐
│  TradingView    │    │   OANDA API       │    │  Historical CSV    │
│  (webhook)      │    │   (REST)          │    │  (local files)     │
└────────┬────────┘    └─────────┬─────────┘    └──────────┬─────────┘
         │                       │                         │
         ▼                       │                         │
┌─────────────────────┐          │                         │
│ infra/ovc-webhook/  │          │                         │
│ src/index.ts        │          │                         │
│ (Cloudflare Worker) │          │                         │
└────────┬────────────┘          │                         │
         │                       │                         │
         ▼                       │                         │
┌─────────────────────┐          │                         │
│ R2 Bucket           │          │                         │
│ tv/YYYY-MM-DD/...   │          │                         │
│ (raw request body)  │          │                         │
└─────────────────────┘          │                         │
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CANONICAL FACTS TABLE                            │
│                ovc.ovc_blocks_v01_1_min                              │
│                                                                     │
│  Columns (OHLC): block_id, sym, date_ny, bar_close_ms, o, h, l, c   │
│  Columns (DERIVED - BREACH): state_tag, trend_tag, pred_dir,        │
│                              bias_dir, struct_state, etc.           │
└─────────────────────────────────────────────────────────────────────┘
         ▲                       ▲                         ▲
         │                       │                         │
         │                       │                         │
┌────────┴────────┐    ┌────────┴────────┐    ┌───────────┴──────────┐
│ backfill.yml    │    │ backfill_m15.yml│    │ src/                 │
│ (2H checkpointed│    │ (M15 raw)       │    │ ingest_history_day.py│
│  backfill)      │    │                 │    │                      │
└─────────────────┘    └────────┬────────┘    └──────────────────────┘
                                │
                                ▼
                  ┌───────────────────────────┐
                  │ ovc.ovc_candles_m15_raw   │
                  │ (M15 raw cache)           │
                  │ via patch_m15_raw_        │
                  │ 20260122.sql              │
                  └───────────────────────────┘
```

---

## 2. Option B – Derived Features Dependencies

```
CANONICAL INPUT
===============
┌────────────────────────────────┐
│ ovc.ovc_blocks_v01_1_min       │
└───────────────┬────────────────┘
                │
    ┌───────────┴───────────┬────────────────────────────┐
    │                       │                            │
    ▼                       ▼                            ▼
┌─────────────────┐  ┌──────────────────┐  ┌────────────────────────┐
│ LEGACY VIEW     │  │ SPLIT VIEWS      │  │ THRESHOLD REGISTRY     │
│ derived.        │  │ (SQL definitions)│  │ ovc_cfg.threshold_pack │
│ ovc_block_      │  │                  │  │ ovc_cfg.threshold_pack │
│ features_v0_1   │  │                  │  │ _active                │
│                 │  │                  │  └────────────┬───────────┘
│ (sql/           │  │                  │               │
│  derived_v0_1.  │  │                  │               │
│  sql)           │  │                  │               │
└─────────────────┘  └───────┬──────────┘               │
                             │                          │
    ┌────────────────────────┼──────────────────────────┤
    │                        │                          │
    ▼                        ▼                          ▼
┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────┐
│ v_ovc_l1_       │  │ v_ovc_l2_       │  │ v_ovc_l3_features_     │
│ features_v0_1   │  │ features_v0_1   │  │ v0_1                   │
│ (sql/derived/)  │  │ (sql/derived/)  │  │ (sql/derived/)         │
└────────┬────────┘  └────────┬────────┘  └────────────┬───────────┘
         │                    │                        │
         ▼                    ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────┐
│ compute_l1_     │  │ compute_l2_     │  │ compute_l3_regime_     │
│ v0_1.py         │  │ v0_1.py         │  │ trend_v0_1.py          │
│ (INVOKED)       │  │ (INVOKED)       │  │ (UNUSED BY WORKFLOW)   │
└────────┬────────┘  └────────┬────────┘  └────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ derived.        │  │ derived.        │
│ ovc_l1_         │  │ ovc_l2_         │
│ features_v0_1   │  │ features_v0_1   │
│ (materialized)  │  │ (materialized)  │
└─────────────────┘  └─────────────────┘
         │                    │
         └──────────┬─────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ backfill_then_       │
         │ validate.yml         │
         │ (invokes L1, L2 only)│
         └──────────────────────┘
```

---

## 3. Option C – Outcomes Dependencies

```
TWO PARALLEL OUTCOME PATHS (MISMATCH)
=====================================

PATH A: Option C Runner
-----------------------
┌────────────────────────────────┐
│ ovc.ovc_blocks_v01_1_min       │
│ (canonical + derived fields)   │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ sql/option_c_v0_1.sql          │
│ (defines outcomes view)        │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐      ┌─────────────────────────────┐
│ derived.ovc_outcomes_v0_1      │      │ derived.ovc_scores_v0_1     │
│ derived.eval_runs              │      │ derived.v_pattern_outcomes  │
│                                │      │ derived.v_session_heatmap   │
└───────────────┬────────────────┘      └─────────────────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ scripts/run/run_option_c.sh    │
│ scripts/run/run_option_c.ps1   │
│ scripts/run/                   │
│ run_option_c_wrapper.py        │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ ovc_option_c_schedule.yml      │
│ (BROKEN: references            │
│  scripts/run_option_c.sh       │
│  - DOES NOT EXIST)             │
└────────────────────────────────┘


PATH B: Feature-Based Outcomes View
-----------------------------------
┌────────────────────────────────┐
│ derived.v_ovc_l1_features_v0_1 │
│ derived.v_ovc_l2_features_v0_1 │
│ derived.v_ovc_l3_features_v0_1 │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ sql/derived/                   │
│ v_ovc_c_outcomes_v0_1.sql      │
│                                │
│ (reads from L1/L2/L3 views,    │
│  NOT canonical table)          │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ derived.v_ovc_c_outcomes_v0_1  │◄──── Used by Path1 evidence
└────────────────────────────────┘
```

---

## 4. Option D – Evidence Dependencies

```
PATH 1 EVIDENCE
===============
┌────────────────────────────────┐      ┌────────────────────────────┐
│ derived.v_ovc_c_outcomes_v0_1  │      │ derived.v_ovc_b_scores_    │
│ (feature-based outcomes)       │      │ dis_v1_1                   │
└───────────────┬────────────────┘      └───────────────┬────────────┘
                │                                       │
                └───────────────────┬───────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │ sql/path1/evidence/                    │
                │ v_path1_evidence_dis_v1_1.sql          │
                │ v_path1_evidence_lid_v1_0.sql          │
                │ v_path1_evidence_res_v1_0.sql          │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │ derived.v_path1_evidence_dis_v1_1      │
                │ (joins scores + outcomes)              │
                └───────────────────┬────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐  ┌────────────────────────┐  ┌────────────────────┐
│ ovc.ovc_blocks_   │  │ ovc.ovc_candles_m15_   │  │ scripts/path1/     │
│ v01_1_min         │  │ raw                    │  │ build_evidence_    │
│ (spine table)     │  │ (M15 cache)            │  │ pack_v0_2.py       │
└───────────────────┘  └────────────────────────┘  └─────────┬──────────┘
                                                             │
                                                             ▼
                                            ┌────────────────────────────┐
                                            │ reports/path1/evidence/    │
                                            │ runs/<run_id>/             │
                                            │   outputs/evidence_pack_   │
                                            │   v0_2/                    │
                                            │     backbone_2h.csv        │
                                            │     strips/2h/*.csv        │
                                            │     context/4h/*.csv       │
                                            │     manifest.json          │
                                            │     data_sha256.txt        │
                                            └────────────────────────────┘
                                                             │
        ┌────────────────────────────────────────────────────┤
        │                                                    │
        ▼                                                    ▼
┌───────────────────────┐                  ┌───────────────────────────┐
│ path1_evidence.yml    │                  │ path1_evidence_queue.yml  │
│ path1_replay_verify.  │                  │                           │
│ yml                   │                  │                           │
└───────────────────────┘                  └───────────────────────────┘


PATH 2 EVIDENCE
===============
┌────────────────────────────────┐
│ DOCUMENTATION ONLY             │
│ - docs/path2/PATH2_CONTRACT_   │
│   v1_0.md                      │
│ - docs/path2/ROADMAP_v0_1.md   │
│                                │
│ NO CODE OR WORKFLOWS           │
└────────────────────────────────┘
```

---

## 5. QA Validation Dependencies

```
VALIDATION SCRIPTS
==================
┌────────────────────────────────┐
│ ovc.ovc_blocks_v01_1_min       │
│ (canonical facts)              │
└───────────────┬────────────────┘
                │
    ┌───────────┴───────────┬─────────────────────────┐
    │                       │                         │
    ▼                       ▼                         ▼
┌───────────────┐  ┌──────────────────┐  ┌─────────────────────────┐
│ src/          │  │ src/validate/    │  │ scripts/path1/          │
│ validate_day. │  │ validate_derived │  │ run_replay_             │
│ py            │  │ _range_v0_1.py   │  │ verification.py         │
│               │  │                  │  │ run_seal_manifests.py   │
│ src/          │  │ sql/03_qa_       │  │ validate_post_run.py    │
│ validate_     │  │ derived_         │  │                         │
│ range.py      │  │ validation_v0_1. │  │                         │
│               │  │ sql              │  │                         │
└───────────────┘  └──────────────────┘  └─────────────────────────┘


CI SANITY (EXISTING)
====================
┌────────────────────────────────┐
│ .github/workflows/             │
│ ci_workflow_sanity.yml         │
│                                │
│ Checks:                        │
│ - YAML syntax validation       │
│ - permissions block presence   │
│ - Referenced script existence  │
│ - Duplicate workflow names     │
│                                │
│ MISSING:                       │
│ - pytest execution             │
│ - Validation gate execution    │
└────────────────────────────────┘


TESTS (NOT IN CI)
=================
┌────────────────────────────────┐
│ tests/                         │
│   test_min_contract_           │
│     validation.py              │
│   test_contract_equivalence.py │
│   test_validate_derived.py     │
│   test_threshold_registry.py   │
│   test_path1_replay_           │
│     structural.py              │
│   test_fingerprint.py          │
│   test_fingerprint_            │
│     determinism.py             │
│   test_overlays_v0_3_          │
│     determinism.py             │
│   test_l3_regime_trend.py      │
│   test_derived_features.py     │
│   test_dst_audit.py            │
│   test_evidence_pack_          │
│     manifest.py                │
│   test_pack_rebuild_           │
│     equivalence.py             │
└────────────────────────────────┘
```

---

## 6. Named Objects Summary

| Object | Type | Location | Used By |
|--------|------|----------|---------|
| `ovc.ovc_blocks_v01_1_min` | Table | Neon DB | Everything |
| `ovc.ovc_candles_m15_raw` | Table | Neon DB | Path1 evidence pack builder |
| `ovc.ovc_run_reports_v01` | Table | Neon DB | Worker telemetry (schema drift) |
| `derived.ovc_block_features_v0_1` | View | `sql/derived_v0_1.sql` | Legacy derived features |
| `derived.ovc_l1_features_v0_1` | Table | Python compute | Split L1 features |
| `derived.ovc_l2_features_v0_1` | Table | Python compute | Split L2 features |
| `derived.ovc_l3_regime_trend_v0_1` | Table | (Unused compute) | Split L3 features |
| `derived.v_ovc_l1_features_v0_1` | View | `sql/derived/` | L1 view definition |
| `derived.v_ovc_l2_features_v0_1` | View | `sql/derived/` | L2 view definition |
| `derived.v_ovc_l3_features_v0_1` | View | `sql/derived/` | L3 view definition |
| `derived.ovc_outcomes_v0_1` | View | `sql/option_c_v0_1.sql` | Option C runner output |
| `derived.ovc_scores_v0_1` | View | `sql/option_c_v0_1.sql` | Option C runner output |
| `derived.v_ovc_c_outcomes_v0_1` | View | `sql/derived/v_ovc_c_outcomes_v0_1.sql` | Path1 evidence (via evidence views) |
| `derived.v_path1_evidence_dis_v1_1` | View | `sql/path1/evidence/` | Path1 evidence pack builder |
| `derived.eval_runs` | Table | `sql/option_c_v0_1.sql` | Option C run metadata |
| `ovc_cfg.threshold_pack` | Table | `sql/04_threshold_registry_v0_1.sql` | L3 regime classification |
| `ovc_cfg.threshold_pack_active` | Table | `sql/04_threshold_registry_v0_1.sql` | Active threshold selection |
