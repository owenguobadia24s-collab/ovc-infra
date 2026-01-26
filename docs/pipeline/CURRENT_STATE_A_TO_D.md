# CURRENT STATE: Option A → Option D Pipeline

**Status: CURRENT_STATE (frozen on 2026-01-23)**

This document captures the observed (even if incorrect) state of the OVC pipeline from Option A (Ingest) through Option D (Evidence). It is a baseline snapshot for future deltas.

---

## 1. Execution Order (AS-IS)

### Option A – Ingest / Canonical Facts

| Step | Mechanism | Output |
|------|-----------|--------|
| 1a | Cloudflare Worker (`infra/ovc-webhook/src/index.ts`) receives TradingView export strings | Rows in `ovc.ovc_blocks_v01_1_min`; raw body to R2 bucket `tv/YYYY-MM-DD/` |
| 1b | OANDA backfill 2H (`scripts/backfill/backfill_oanda_2h_checkpointed.py`) | Rows in `ovc.ovc_blocks_v01_1_min` |
| 1c | OANDA backfill M15 (`scripts/backfill/backfill_oanda_m15_checkpointed.py`) | Rows in `ovc.ovc_candles_m15_raw` |
| 1d | Historical CSV ingest (`src/ingest_history_day.py`) | Rows in `ovc.ovc_blocks_v01_1_min` |

**Workflows**: `backfill.yml`, `backfill_m15.yml`, `ovc_full_ingest.yml`

### Option B – Derived Features

| Step | Mechanism | Output |
|------|-----------|--------|
| 2a-legacy | SQL view `derived.ovc_block_features_v0_1` in `sql/derived_v0_1.sql` | Live view over canonical facts |
| 2b-split-L1 | Python `src/derived/compute_l1_v0_1.py` + SQL view `sql/derived/v_ovc_l1_features_v0_1.sql` | Table `derived.ovc_l1_features_v0_1` |
| 2b-split-L2 | Python `src/derived/compute_l2_v0_1.py` + SQL view `sql/derived/v_ovc_l2_features_v0_1.sql` | Table `derived.ovc_l2_features_v0_1` |
| 2b-split-L3 | Python `src/derived/compute_l3_regime_trend_v0_1.py` (UNUSED) + SQL view `sql/derived/v_ovc_l3_features_v0_1.sql` | Table `derived.ovc_l3_regime_trend_v0_1` (if materialized) |

**Workflows**: `backfill_then_validate.yml` (invokes L1, L2 compute only; L3 compute unused)

### Option C – Outcomes

| Step | Mechanism | Output |
|------|-----------|--------|
| 3a-runner | `sql/option_c_v0_1.sql` via `scripts/run/run_option_c.sh` | View `derived.ovc_outcomes_v0_1`, `derived.ovc_scores_v0_1`; metadata in `derived.eval_runs` |
| 3b-alternate | SQL view `sql/derived/v_ovc_c_outcomes_v0_1.sql` | View `derived.v_ovc_c_outcomes_v0_1` (reads from L1/L2/L3 views, NOT canonical table) |

**Workflows**: `ovc_option_c_schedule.yml` (BROKEN: references nonexistent script path `scripts/run_option_c.sh`)

### Option D – Evidence & Paths

| Step | Mechanism | Output |
|------|-----------|--------|
| 4a-path1 | `scripts/path1/build_evidence_pack_v0_2.py` | Evidence packs in `reports/path1/evidence/runs/<run_id>/` |
| 4b-path1-queue | `scripts/path1/run_evidence_queue.py`, `run_evidence_range.py` | Queued evidence generation |
| 4c-path1-views | `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql` etc. | View `derived.v_path1_evidence_dis_v1_1` (joins to `derived.v_ovc_c_outcomes_v0_1`) |

**Workflows**: `path1_evidence.yml`, `path1_evidence_queue.yml`, `path1_replay_verify.yml`

### QA – Validation

| Step | Mechanism | Output |
|------|-----------|--------|
| QA-a | `src/validate_day.py`, `src/validate_range.py` | Validation reports |
| QA-b | `src/validate/validate_derived_range_v0_1.py`, `sql/03_qa_derived_validation_v0_1.sql` | Derived coverage checks |
| QA-c | `scripts/path1/run_replay_verification.py`, `run_seal_manifests.py` | Replay and sealing tests |
| QA-d | CI sanity: `.github/workflows/ci_workflow_sanity.yml` | YAML validation, script path checks |

**Gap**: No pytest execution in CI workflows.

---

## 2. Fracture Points (from audit)

| ID | Fracture | Classification |
|----|----------|----------------|
| F1 | **Option boundary breach (A→B)**: Canonical table `ovc.ovc_blocks_v01_1_min` contains derived fields (`state_tag`, `trend_tag`, `pred_dir`, `bias_dir`, etc.) | Contractual |
| F2 | **Multiple sources of truth (B)**: Legacy `derived.ovc_block_features_v0_1` AND split L1/L2/L3 tables/views coexist | Structural |
| F3 | **Unused L3 compute path**: `compute_l3_regime_trend_v0_1.py` exists but no workflow invokes it | Operational |
| F4 | **Option C scheduling mismatch**: `ovc_option_c_schedule.yml` references `scripts/run_option_c.sh` (does not exist); actual path is `scripts/run/run_option_c.sh` | Operational |
| F5 | **Outcome view mismatch**: Path1 evidence uses `derived.v_ovc_c_outcomes_v0_1` but Option C runner creates `derived.ovc_outcomes_v0_1` | Structural |
| F6 | **M15 vs 2H resampling boundary**: No clear derivation from `ovc.ovc_candles_m15_raw` to 2H canonical facts; Option B consumes only 1-min canonical | Structural |
| F7 | **Worker telemetry schema drift**: Worker writes `ended_at`, `meta` to `ovc.ovc_run_reports_v01`; table definition has `finished_at`, no `meta` | Contractual |
| F8 | **QA vs CI gap**: Validation scripts exist but no CI workflow runs pytest or validation gates | Operational |
| F9 | **Ambiguous migration state**: No ledger tracking which SQL patches are applied to Neon DB | Documentary |

---

## 3. TRUST MAP Summary

### Canonical and trustworthy
- R2 raw ingests (`tv/YYYY-MM-DD/...`)
- `ovc.ovc_blocks_v01_1_min` OHLC fields, timestamps, block_id (NOT derived fields)
- `ovc.ovc_candles_m15_raw`
- `ovc_cfg.threshold_pack`, `ovc_cfg.threshold_pack_active`

### Derived but valid (regenerable)
- `derived.ovc_l1_features_v0_1`, `derived.ovc_l2_features_v0_1` (Python-computed)
- Option B SQL views (`v_ovc_l1_features_v0_1.sql`, `v_ovc_l2_features_v0_1.sql`, `v_ovc_l3_features_v0_1.sql`)
- Option C outcomes/scores when run manually (`derived.ovc_outcomes_v0_1`, `derived.ovc_scores_v0_1`)
- Path1 evidence packs (when built from correct views)

### Ambiguous
- `state_tag`, `trend_tag`, `pred_dir`, `bias_dir` in canonical table
- Dual derived implementations (legacy vs split)
- L3 regime classification (compute script unused)
- Outcome view mismatch (which is authoritative?)

### Invalid / unsafe
- `ovc_option_c_schedule.yml` (broken script path)
- Worker telemetry table definitions (schema drift)
- Any guarantee of Option separation
- Path2 evidence (no code exists)

---

## 4. CONTRACT VIOLATIONS (from audit)

1. Canonical facts table stores derived fields (violates A/B boundary)
2. Option C scheduled workflow does not execute (broken path)
3. Path1 evidence consumes different outcome product than Option C runner produces
4. L3 compute script is not invoked by any workflow
5. No migration ledger to verify DB schema matches repo
6. No pytest or validation gates in CI
7. Worker telemetry columns mismatch table definition

---

## 5. UNKNOWN / UNDOCUMENTED AREAS (from audit)

1. How `ovc.ovc_candles_m15_raw` relates to 2H blocks derivation pipeline
2. Which derived implementation (legacy vs split) is authoritative
3. Which outcome view (runner's vs feature-based) is the official Option C product
4. What migrations have been applied to the Neon database
5. How Path2 will be implemented (only docs exist)
