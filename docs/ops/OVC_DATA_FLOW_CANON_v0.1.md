# OVC Data Flow Canon v0.1

> **Created:** 2026-01-19  
> **Purpose:** Authoritative reference for data ownership, purpose, and downstream flows  
> **Status:** Canonical (DO NOT MODIFY without review)

---

## 1. Overview

The OVC system organizes data into four conceptual layers, each with distinct ownership and purpose:

1. **Canonical Facts (Schema: `ovc`)** — Immutable 2H block records ingested from TradingView or backfilled from OANDA. This is the single source of truth for market observations and is LOCKED (Option A). No human-facing dashboards should ever read directly from this layer.

2. **Derived Features (Schema: `derived`)** — Computed features (C1 single-bar, C2 multi-bar, C3 semantic tags) and forward-looking outcomes derived exclusively from canonical facts. These are replayable, versioned, and never contain interpretive human decisions.

3. **Evaluation / Outcomes (Schema: `derived`)** — Scoring views and outcome tracking that measure prediction accuracy against realized price action. This layer exists for quantitative evaluation, not human browsing.

4. **QA / Governance (Schemas: `ovc_qa`, `ovc_cfg`, `ops`)** — Validation artifacts, threshold configuration, and sync state used for pipeline health, audit trails, and replay certification.

**Critical Principle:** Notion is a *human decision surface*, not a data warehouse. It receives only evaluative summaries that inform human action (e.g., hit rates, run status). Raw facts, derived features, and intermediate calculations must never flow to Notion.

---

## 2. Neon Schema Inventory

### Schema: `ovc`

The `ovc` schema holds canonical facts. It is the **Option A** boundary and is **LOCKED**.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `ovc_blocks_v01_1_min` | table | P1 (Webhook) / P2 (Backfill) | Authoritative 2H block records with OHLC, tags, and export string | Derived pipeline | **NO** | Raw canonical facts are not human-actionable; too granular | Active |
| `ovc_run_reports_v01` | table | P1 (Webhook) / P2 (Backfill) | Run-level metadata for ingest/backfill jobs (counts, verdict) | QA / validation | **NO** | Pipeline telemetry, not decision data | Active |
| `ovc_outcomes_v01` | table | UNKNOWN | Legacy outcomes table with FK to blocks | None (planned / dormant) | **NO** | Superseded by `derived.ovc_outcomes_v0_1`; reference contains typo in FK | Orphaned |
| `v_ovc_min_events_norm` | view | sql/10_views_research_v0.1.sql | Normalized projection of MIN blocks for research | Research queries | **NO** | Research convenience view, not for dashboards | Active |
| `v_ovc_min_events_seq` | view | sql/10_views_research_v0.1.sql | Sequenced view with lag/lead for next-bar analysis | Research queries | **NO** | Research convenience view | Active |
| `v_pattern_outcomes_v01` | view | sql/10_views_research_v0.1.sql | Legacy pattern outcome aggregates (group by play/state_key) | Research queries | **NO** | Research only; superseded by derived equivalents | Active |
| `v_transition_stats_v01` | view | sql/10_views_research_v0.1.sql | State transition probability matrix | Research queries | **NO** | Research only | Active |
| `v_session_heatmap_v01` | view | sql/10_views_research_v0.1.sql | Time-of-day aggregates by block2h | Research queries | **NO** | Research only | Active |
| `v_data_quality_ohlc_basic` | view | sql/10_views_research_v0.1.sql | DQ checks for OHLC consistency | QA / validation | **NO** | Internal validation only | Active |

### Schema: `derived`

The `derived` schema holds Option B (features) and Option C (outcomes) outputs. All objects are replayable and versioned.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `derived_runs` | table | sql/derived_v0_1.sql | Run metadata for derived feature computations (v0.1) | Evaluation logic | **NO** | Pipeline provenance, not human-actionable | Active |
| `derived_runs_v0_1` | table | sql/02_derived_c1_c2_tables_v0_1.sql | Extended run metadata with run_type, window_spec, threshold_version | Evaluation logic | **NO** | Pipeline provenance | Active |
| `eval_runs` | table | sql/option_c_v0_1.sql | Run metadata for Option C evaluation runs | Notion sync (eval_runs) | **YES** (limited) | Only `run_id`, `eval_version`, `computed_at` are synced | Active |
| `ovc_block_features_v0_1` | view | sql/derived_v0_1.sql | C1+C2 derived features (range, body, gaps, rolling stats) | Evaluation logic | **NO** | Feature vectors are intermediate calculations | Active |
| `ovc_c1_features_v0_1` | table | sql/02_derived_c1_c2_tables_v0_1.sql | Materialized C1 single-bar features | Evaluation logic | **NO** | Intermediate computation | Active |
| `ovc_c2_features_v0_1` | table | sql/02_derived_c1_c2_tables_v0_1.sql | Materialized C2 multi-bar features | Evaluation logic | **NO** | Intermediate computation | Active |
| `ovc_c3_regime_trend_v0_1` | table | sql/05_c3_regime_trend_v0_1.sql | C3 semantic regime tags (TREND/NON_TREND) with threshold provenance | Evaluation logic | **NO** | Semantic classification, not outcome | Active |
| `ovc_outcomes_v0_1` | view | sql/option_c_v0_1.sql | Row-level forward returns, MFE/MAE, hit flags at horizons 1,2,6,12 | Notion sync (outcomes) | **YES** (limited) | Only evaluative fields synced (hit rates, fwd_ret) | Active |
| `ovc_scores_v0_1` | view | sql/option_c_v0_1.sql | Aggregated scoring by bucket (range_pct, abs_ret) | Research / dashboards | **NO** | Aggregate research view, not per-block | Active |
| `v_pattern_outcomes_v01` | view | sql/option_c_v0_1.sql | Pattern outcome aggregates by state_key | Research queries | **NO** | Research aggregation | Active |
| `v_session_heatmap_v01` | view | sql/option_c_v0_1.sql | Session heatmap with hit rates by block2h | Research queries | **NO** | Research aggregation | Active |
| `v_transition_stats_v01` | view | sql/option_c_v0_1.sql | Struct_state transition stats with outcome metrics | Research queries | **NO** | Research aggregation | Active |

### Schema: `ovc_qa`

The `ovc_qa` schema holds validation artifacts used for governance, audit trails, and tape reconciliation.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `validation_run` | table | sql/qa_schema.sql | Metadata for tape validation runs | QA / validation | **NO** | Internal governance | Active |
| `expected_blocks` | table | sql/qa_schema.sql | Expected block letters for validation date range | QA / validation | **NO** | Validation scaffold | Active |
| `tv_ohlc_2h` | table | sql/qa_schema.sql | TradingView OHLC reference data for comparison | QA / validation | **NO** | Tape comparison reference | Active |
| `ohlc_mismatch` | table | sql/qa_schema.sql | Records of OHLC differences between OVC and TV | QA / validation | **NO** | Mismatch artifacts | Active |
| `derived_validation_run` | table | sql/03_qa_derived_validation_v0_1.sql | Validation results for C1/C2 derived features | QA / validation | **NO** | Derived layer QA | Active |

### Schema: `ovc_cfg`

The `ovc_cfg` schema holds versioned configuration for threshold packs used in C3+ computations.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `threshold_pack` | table | sql/04_threshold_registry_v0_1.sql | Immutable threshold pack versions (JSONB config + hash) | C3 compute scripts | **NO** | Configuration registry, not insight | Active |
| `threshold_pack_active` | table | sql/04_threshold_registry_v0_1.sql | Mutable pointers to currently active threshold versions | C3 compute scripts | **NO** | Activation pointers | Active |

### Schema: `ops`

The `ops` schema holds operational state for sync pipelines.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `notion_sync_state` | table | sql/04_ops_notion_sync.sql | Watermark tracking for incremental Notion sync | D-NotionSync script | **NO** | Sync cursor, not data | Active |

### Schema: `public` (Legacy / Orphaned)

These objects exist from earlier development phases and are not part of the active system.

| Object Name | Type | Created By | Purpose | Primary Consumer | Should Flow to Notion? | If NO, Why Not | Status |
|-------------|------|------------|---------|------------------|------------------------|----------------|--------|
| `ovc_blocks_v01` | table | sql/schema_v01.sql | Legacy MIN table with different PK structure | None | **NO** | Superseded by `ovc.ovc_blocks_v01_1_min` | Orphaned |
| `ovc_blocks_detail_v01` | table | infra/ovc-webhook/sql/ | Legacy detail table from early webhook | None | **NO** | Never integrated into current pipelines | Orphaned |

---

## 3. Neon → Notion Boundary (Critical Section)

### What Is Allowed to Flow Into Notion (and Why)

Notion serves as a **human decision surface**. Only data that directly informs human action should reach Notion.

#### Allowed Sources

| Source Object | Fields Synced | Justification |
|---------------|---------------|---------------|
| `ovc.ovc_blocks_v01_1_min` | `block_id`, `sym`, `date_ny`, `block_start`, `ingest_ts`, `export_str` | Block identity and ingest timestamp for tracking which blocks have been captured |
| `derived.ovc_outcomes_v0_1` | `block_id`, `run_id`, `eval_version`, `fwd_ret_1/2/6/12`, `mfe_1`, `mae_1`, `hit_1/2/6/12` | Evaluative outcomes that answer "was the prediction correct?" |
| `derived.eval_runs` | `run_id`, `eval_version`, `formula_hash`, `computed_at` | Run provenance for audit trail |

#### Forbidden Categories

The following categories **must never** flow to Notion:

1. **Raw OHLC values** — Prices are canonical facts, not decisions. (`o`, `h`, `l`, `c` from any table)
2. **Derived features** — Features like `body_ratio`, `range_z_12`, `clv` are intermediate math, not actionable.
3. **C3 semantic tags** — Tags like `c3_regime_trend` are classifier outputs, not human labels.
4. **QA artifacts** — Validation results exist for audit, not dashboards.
5. **Configuration** — Threshold packs and sync cursors are infrastructure.

#### Rule of Thumb

> **"If a human cannot act differently after seeing this field, it must not go to Notion."**

Examples:
- ✅ "Hit rate = 62%" → Human adjusts trading confidence
- ✅ "Fwd ret 1 = +0.12%" → Human evaluates prediction quality
- ❌ "body_ratio = 0.34" → Human cannot act on this alone
- ❌ "range_z_12 = 1.8" → Statistical artifact, not decision input

---

## 4. Current Notion Sync Mapping

Based on [scripts/notion_sync.py](../../scripts/notion_sync.py), the following mappings are currently active:

### `sync_blocks` (blocks_min watermark)

| Neon Field | Notion Property | Layer | Assessment |
|------------|-----------------|-------|------------|
| `block_id` | Block ID (title) | Fact | ✅ Correct — identity |
| `sym` | Symbol (select) | Fact | ✅ Correct — identity |
| `date_ny` | Date NY (date) | Fact | ✅ Correct — identity |
| `block_start` | Block Start (date) | Derived from `bar_close_ms` | ✅ Correct — timing |
| `ingest_ts` | Ingest TS (date) | Metadata | ✅ Correct — tracking |
| `export_str` | Export Str (text) | Fact | ⚠️ Reconsider — raw export string is debugging data, not human-actionable |

### `sync_outcomes` (outcomes watermark)

| Neon Field | Notion Property | Layer | Assessment |
|------------|-----------------|-------|------------|
| `block_id` | Block ID (title) | Fact | ✅ Correct — identity |
| `run_id` | Run ID (text) | Metadata | ✅ Correct — provenance |
| `eval_version` | Eval Version (text) | Metadata | ✅ Correct — version tracking |
| `fwd_ret_1` | Fwd Ret 1 (number) | Outcome | ✅ Correct — evaluative |
| `fwd_ret_2` | Fwd Ret 2 (number) | Outcome | ✅ Correct — evaluative |
| `fwd_ret_6` | Fwd Ret 6 (number) | Outcome | ✅ Correct — evaluative |
| `fwd_ret_12` | Fwd Ret 12 (number) | Outcome | ✅ Correct — evaluative |
| `mfe_1` | MFE (number) | Outcome | ✅ Correct — evaluative |
| `mae_1` | MAE (number) | Outcome | ✅ Correct — evaluative |
| `hit_1` | Hit 1 (checkbox) | Outcome | ✅ Correct — evaluative |
| `hit_2` | Hit 2 (checkbox) | Outcome | ✅ Correct — evaluative |
| `hit_6` | Hit 6 (checkbox) | Outcome | ✅ Correct — evaluative |
| `hit_12` | Hit 12 (checkbox) | Outcome | ✅ Correct — evaluative |

### `sync_eval_runs` (eval_runs watermark, optional)

| Neon Field | Notion Property | Layer | Assessment |
|------------|-----------------|-------|------------|
| `run_id` | Run ID (title) | Metadata | ✅ Correct — provenance |
| `eval_version` | Eval Version (text) | Metadata | ✅ Correct |
| `formula_hash` | Formula Hash (text) | Metadata | ✅ Correct — audit |
| `computed_at` | Computed At (date) | Metadata | ✅ Correct |

### Summary

The current Notion sync is **mostly correct**. The only questionable field is `export_str`, which contains the raw pipe-delimited export string. This is useful for debugging but not for human decision-making. Consider removing it in a future iteration.

---

## 5. Orphan & Pruning Candidates

The following objects appear unused or superseded. **No deletion is recommended at this time** — only classification for future review.

| Object | Schema | Classification | Notes |
|--------|--------|----------------|-------|
| `ovc_blocks_v01` | public | **Safe to deprecate** | Superseded by `ovc.ovc_blocks_v01_1_min`; different PK structure |
| `ovc_blocks_detail_v01` | public | **Safe to deprecate** | Early webhook artifact; never integrated |
| `ovc_outcomes_v01` | ovc | **Intentionally dormant** | Contains FK syntax error (`ovc_blocks_v01.1_min` — missing underscore); superseded by `derived.ovc_outcomes_v0_1` |
| `derived_runs` | derived | **Coexists with `derived_runs_v0_1`** | May be redundant; confirm which is authoritative before pruning |

### Confirmation Required

Before any removal:
1. Query each table for row counts
2. Verify no active scripts reference them (grep complete)
3. Archive DDL to `sql/archive/` before DROP

---

## 6. Canonical Rules (Non-Negotiable)

These rules govern all data flow decisions in OVC:

1. **Canonical facts never go to Notion.**  
   Raw OHLC, timestamps, and export strings are not human decisions.

2. **Derived features never go to Notion.**  
   Features like `body_ratio`, `range_z_12`, and `clv` are intermediate calculations.

3. **Only evaluative outcomes may reach humans.**  
   Hit rates, forward returns, MFE/MAE answer "was I right?" — humans can act on this.

4. **QA tables exist for governance, not insight.**  
   Validation artifacts prove correctness; they do not inform trading.

5. **Configuration is infrastructure.**  
   Threshold packs, sync cursors, and activation pointers are not data.

6. **Storage volume is irrelevant; intent is everything.**  
   A 1KB field that violates boundaries is worse than a 1GB table that respects them.

7. **When in doubt, do not sync.**  
   It is always safer to withhold data from Notion than to pollute the decision surface.

---

## Appendix: Schema Ownership Summary

| Schema | Layer | Owner Pipeline(s) | Writes Allowed From |
|--------|-------|-------------------|---------------------|
| `ovc` | Canonical Facts | A-Ingest, P2-Backfill | Option A only (LOCKED) |
| `derived` | Features + Outcomes | B1-Derived*, C-Eval | Option B/C scripts |
| `ovc_qa` | Validation | D-ValidationHarness | Validation scripts |
| `ovc_cfg` | Configuration | Manual / B1-DerivedC3 | Config tools |
| `ops` | Sync State | D-NotionSync | Sync scripts |
| `public` | Legacy / Orphaned | None | None (deprecate) |

---

*End of Document*
