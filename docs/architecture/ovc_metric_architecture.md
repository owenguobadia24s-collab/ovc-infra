# OVC Metric Architecture v0.2

> Canonical reference for OVC's metric system, layer boundaries, and derivation roadmap.
> Last updated: 2026-01-18

---

## 1. SYSTEM OVERVIEW

### 1.1 Layered Architecture

OVC processes trading signal data through a layered architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOURCE PAYLOADS                              │
│  TradingView Alerts (POST /tv, /tv_secure)  │  OANDA API (H1)   │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CANONICAL FACTS (B LAYER)                       │
│           ovc.ovc_blocks_v01_1_min (2H blocks)                   │
│         OHLC + schedule keys + ingest metadata ONLY              │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DERIVED METRICS (C LAYER)                       │
│  L1: OHLC Primitives  │  L2: Structure  │  L3: Market Model      │
│  derived.ovc_block_features_v0_1  │  derived.tv_reference_*     │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VALIDATION / QA                              │
│              ovc_qa schema │ tape validation                     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Foundational Principles

| Principle | Description |
|-----------|-------------|
| **B facts are source-agnostic** | TradingView and OANDA produce identical canonical rows for the same 2H block |
| **C metrics are derived, versioned, and replayable** | Every C-layer output carries `version` and `formula_hash` |
| **TradingView is a reference engine** | Pine scripts implement metrics for real-time display; Python/SQL are authoritative for analysis |
| **Idempotent ingestion** | Both P1 (live) and P2 (backfill) use upsert on `block_id` PK |

### 1.3 Data Sources

| Source | Pipeline | Ingest Path | Status |
|--------|----------|-------------|--------|
| TradingView | P1 (Live) | `POST /tv` → R2 → Neon | PARTIAL |
| OANDA API | P2 (Backfill) | `backfill_oanda_2h_checkpointed.py` | PASS |

---

## 2. CANONICAL FACTS (B LAYER)

### 2.1 Definition

The B Layer stores **source-normalized 2H block facts** in `ovc.ovc_blocks_v01_1_min`. This table is the single source of truth for all downstream derived metrics.

**B-layer facts must be computable from raw price feeds (e.g., OANDA or TradingView OHLC) without interpretation.**

### 2.2 B-Layer Contract Fields

The canonical facts table (`ovc.ovc_blocks_v01_1_min`) contains ONLY these field categories:

#### Identity & Schedule Fields
| Field | Type | Description |
|-------|------|-------------|
| `block_id` | text (PK) | Canonical ID: `YYYYMMDD-{A-L}-{SYM}` |
| `sym` | text | Instrument symbol (e.g., `GBPUSD`) |
| `tz` | text | Export timezone (`America/New_York`) |
| `date_ny` | date | NY session date (17:00 anchor) |
| `bar_close_ms` | bigint | Block close timestamp (ms, UTC) |
| `block2h` | text | 2H segment letter `A-L` |
| `block4h` | text | 4H block label (`AB`, `CD`, etc.) |

#### OHLC Price Facts
| Field | Type | Description |
|-------|------|-------------|
| `o` | double | Open price |
| `h` | double | High price |
| `l` | double | Low price |
| `c` | double | Close price |

#### Ingest Metadata
| Field | Type | Description |
|-------|------|-------------|
| `source` | text | Source identifier (`tv`, `oanda`) |
| `build_id` | text | Build identifier / run_id |
| `ingest_ts` | timestamptz | Ingestion timestamp |

### 2.3 Fields Explicitly EXCLUDED from B-Layer

The following field categories are **architecturally C-layer** and do NOT belong in B-layer canonical facts:

| Category | Examples | Correct Layer |
|----------|----------|---------------|
| State/Structure Tags | `state_tag`, `value_tag`, `struct_state` | L2/L3 |
| Regime/Context Tags | `regime_tag`, `trend_tag`, `rd_state` | L3 |
| Transition/Risk Tags | `trans_risk`, `cp_tag` | L3 |
| Decision/Prediction | `bias_mode`, `bias_dir`, `play`, `pred_dir` | L3 |
| Derived OHLC Metrics | `rng`, `body`, `dir`, `ret` | L1 |
| TradingView Interpretations | `tt`, `tis`, `htf_stack`, `with_htf` | L2/L3 |

These fields are TradingView-computed interpretations and belong in `derived.*` schemas.

### 2.4 B-Layer Invariants

1. **Idempotent**: Upsert on `block_id` ensures no duplicates
2. **Deterministic**: Same source data produces identical rows
3. **Source-agnostic**: TradingView and OANDA produce equivalent canonical facts
4. **Immutable schema**: Option A is LOCKED; schema changes require new contract version
5. **No interpretation**: B-layer contains ONLY objective price observations, not derived classifications

### 2.5 Current State Clarification (v0.1)

> **Implementation Note**: In v0.1, some TradingView-derived tags may still be physically co-located with facts in `ovc.ovc_blocks_v01_1_min` for operational continuity during ingest pipeline development.
>
> **Architecturally, these tags belong to C-layer derived schemas.** Their presence in the facts table is a temporary implementation detail that does not invalidate the layered model. Migration to strict physical separation is planned and does not affect the correctness of current results.
>
> When querying for pure B-layer facts, reference only the fields defined in Section 2.2.

### 2.6 Implementation References

| Component | Path |
|-----------|------|
| Table DDL | `sql/01_tables_min.sql` |
| OANDA Backfill | `src/backfill_oanda_2h_checkpointed.py` |
| MIN Contract | `contracts/export_contract_v0.1.1_min.json` |
| Worker Ingest | `infra/ovc-webhook/src/index.ts` |

---

## 3. DERIVED METRIC TIERS (C LAYER OVERVIEW)

### 3.1 Tiering Model

| Tier | Name | Input Dependencies | Status |
|------|------|-------------------|--------|
| **L1** | OHLC Primitives | B-layer OHLC only | **IMPLEMENTED** |
| **L2** | Structure & Block Memory | B-layer + rolling context | **PARTIAL** |
| **L3** | Market Model & Regime | L1 + L2 evidence | **PARTIAL** (TV reference) |
| **L4** | Dual-Engine Parity | TV vs Python comparison | **PLANNED** |
| **C5** | True L3 / Orderflow | Tick data, volume profile | **FUTURE** |

### 3.2 TradingView Reference Tables (C-Layer)

TradingView-derived tags are stored in dedicated C-layer reference tables:

| Table | Content | Purpose |
|-------|---------|--------|
| `derived.tv_reference_c2_v0_1` | Structure & state tags (`state_tag`, `value_tag`, `struct_state`, `rrc`, `vrc`, `trend_tag`, `space_tag`, `htf_stack`, `with_htf`) | L2 reference for parity testing |
| `derived.tv_reference_c3_v0_1` | Market model & regime tags (`regime_tag`, `rd_state`, `trans_risk`, `bias_mode`, `bias_dir`, `perm_state`, `play`, `pred_dir`, `pred_target`, `tradeable`, `conf_l3`, `timebox`, `invalidation`) | L3 reference for parity testing |

**These tables hold TradingView outputs as a reference engine—derived, versioned, and non-canonical.** They are used for parity benchmarking and QA, not as ground truth.

### 3.3 Feasibility from OHLC

| Tier | Feasible from OHLC? | Notes |
|------|---------------------|-------|
| L1 | ✅ YES | Pure OHLC arithmetic |
| L2 | ✅ YES | Rolling windows over OHLC |
| L3 | ⚠️ PARTIAL | Tags derivable; some heuristics require calibration |
| L4 | ✅ YES | QA comparison layer |
| C5 | ❌ NO | Requires tick-level data |

---

## 4. L1 — OHLC PRIMITIVES (L1)

### 4.1 Definition

L1 metrics are purely derivable from B-layer OHLC facts (`o`, `h`, `l`, `c`) without external state or interpretation. They are deterministic, source-agnostic, and form the foundation for higher tiers.

**Inputs**: B-layer facts only (`ovc.ovc_blocks_v01_1_min` OHLC columns)  
**Outputs**: `derived.ovc_block_features_v0_1`

### 4.2 Implemented Metrics (SQL)

**Source**: `derived.ovc_block_features_v0_1` in `sql/derived_v0_1.sql`

#### Bar Geometry
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `range` | `h - l` | DBF | IMPLEMENTED |
| `body` | `abs(c - o)` | DBF | IMPLEMENTED |
| `upper_wick` | `h - greatest(o, c)` | DBF | IMPLEMENTED |
| `lower_wick` | `least(o, c) - l` | DBF | IMPLEMENTED |
| `body_ratio` | `body / range` (null if range=0) | DBF | IMPLEMENTED |
| `upper_wick_ratio` | `upper_wick / range` | DBF | IMPLEMENTED |
| `lower_wick_ratio` | `lower_wick / range` | DBF | IMPLEMENTED |
| `close_pos` | `(c - l) / range` | DBF | IMPLEMENTED |

#### Returns & Direction
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `direction` | `sign(c - o)` → `1`, `-1`, `0` | DBF | IMPLEMENTED |
| `ret` | `(c / o) - 1` (null if o=0) | DBF | IMPLEMENTED |
| `logret` | `ln(c / o)` (null if c≤0 or o≤0) | DBF | IMPLEMENTED |
| `gap` | `o - lag(c, 1)` | WDF | IMPLEMENTED |

#### Session Context
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `sess_high` | Running max(h) within date_ny | WDF | IMPLEMENTED |
| `sess_low` | Running min(l) within date_ny | WDF | IMPLEMENTED |
| `dist_sess_high` | `sess_high - c` | WDF | IMPLEMENTED |
| `dist_sess_low` | `c - sess_low` | WDF | IMPLEMENTED |

#### Rolling Statistics (N=12)
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `roll_avg_range_12` | `avg(range)` over 12 blocks | WDF | IMPLEMENTED |
| `roll_std_logret_12` | `stddev_samp(logret)` over 12 blocks | WDF | IMPLEMENTED |
| `range_z_12` | `(range - roll_avg_range_12) / stddev` | WDF | IMPLEMENTED |

#### Structural Breaks (12-block lookback)
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `hh_12` | `h > max(h)` over prior 12 blocks | WDF | IMPLEMENTED |
| `ll_12` | `l < min(l)` over prior 12 blocks | WDF | IMPLEMENTED |
| `took_prev_high` | `h > lag(h, 1)` | WDF | IMPLEMENTED |
| `took_prev_low` | `l < lag(l, 1)` | WDF | IMPLEMENTED |

#### Quality Flags
| Metric | Formula | Class | Status |
|--------|---------|-------|--------|
| `range_zero` | `range = 0` | QAF | IMPLEMENTED |
| `any_missing_inputs` | `o or h or l or c is null` | QAF | IMPLEMENTED |
| `ret_extreme_flag` | `abs(ret) >= 0.05` | QAF | IMPLEMENTED |
| `range_extreme_flag` | `abs(range_z_12) >= 3.0` | QAF | IMPLEMENTED |

### 4.3 L1 Guarantees

- **Deterministic**: Same OHLC input → same output
- **Source-agnostic**: Works identically on TradingView and OANDA data
- **Window spec**: `N=12; session=date_ny`
- **Formula hash**: `md5('derived.ovc_block_features_v0_1:v0.1:block_physics')`

---

## 5. L2 — STRUCTURE & BLOCK MEMORY (L2)

### 5.1 Definition

L2 metrics track structural patterns, swing relationships, and rolling memory over blocks. They require lookback windows beyond the current bar.

**Inputs**: B-layer facts + L1 derived features + rolling context  
**Outputs**: `derived.ovc_block_structure_v0_1` (planned), `derived.tv_reference_c2_v0_1` (TV reference)

### 5.2 Metric Groups

#### 5.2.1 Micro Reference (RR2) — 2-bar lookback
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `rr` | `max(h[1], h[2]) - min(l[1], l[2])` | h, l | Pine only |
| `rm` | `(rr_high + rr_low) / 2` | rr | Pine only |
| `q1` | `rr_low + 0.25 * rr` | rr | Pine only |
| `q3` | `rr_low + 0.75 * rr` | rr | Pine only |
| `band` | Close quartile 0-3 | c, rr | Pine only |

#### 5.2.2 State Metrics
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `rer` | Range expansion ratio: `range / rr` | rng, rr | Pine only |
| `or` | Overlap ratio vs micro range | h, l, rr | Pine only |
| `clv` | Signed close location: `2*(c-l)/range - 1` | c, l, rng | Pine only |
| `brb` | Body-to-range ratio: `body / range` | body, rng | SQL: `body_ratio` |
| `bodyrr` | Body-to-rr ratio: `body / rr` | body, rr | Pine only |

#### 5.2.3 Value Metrics
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `sd` | Signed distance to rm in rr units | c, rm, rr | Pine only |
| `oa` | Outside acceptance (signed) | c, rr_high, rr_low | Pine only |
| `mc` | Midcross flag: `l <= rm <= h` | l, h, rm | Pine only |
| `mc3` | 3-bar rolling sum of mc | mc | Pine only |
| `vflip` | Value flip flag: sd sign change | sd, sd[1] | Pine only |
| `vf3` | 3-bar rolling sum of vflip | vflip | Pine only |

#### 5.2.4 Liquidity Sweeps
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `swhi` | Sweep high magnitude in rr units | h, rr_high, rr | Pine only |
| `swlo` | Sweep low magnitude in rr units | l, rr_low, rr | Pine only |
| `took_hi` | TookHigh flag: `swhi > 0` | swhi | Pine only |
| `took_lo` | TookLow flag: `swlo > 0` | swlo | Pine only |
| `hi_ran` | High ran: took_hi AND c >= rr_high | took_hi, c | Pine only |
| `hi_rev` | High rev: took_hi AND c < rr_high | took_hi, c | Pine only |
| `lo_ran` | Low ran: took_lo AND c <= rr_low | took_lo, c | Pine only |
| `lo_rev` | Low rev: took_lo AND c > rr_low | took_lo, c | Pine only |

#### 5.2.5 Context Unit (RRc)
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `rrc` | Context range: SMA of rr over rrcLen | rr | TV Reference → `derived.tv_reference_c2_v0_1` |
| `vrc` | Volatility ratio: `rr / rrc` | rr, rrc | TV Reference → `derived.tv_reference_c2_v0_1` |

#### 5.2.6 Structure State
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `lastpivot` | Last pivot label (Hi/Lo) | pivot detection | Pine only |
| `swingdir` | Swing direction from last pivot | lastpivot | Pine only |
| `phidr` | Distance to pivot high in RRc units | lastPH, c, rrc | Pine only |
| `plodr` | Distance to pivot low in RRc units | lastPL, c, rrc | Pine only |
| `struct` | Raw structure: HH/HL/LH/LL | pivot pairs | Pine only |
| `struct_state` | Alias of struct (MIN key) | struct | TV Reference → `derived.tv_reference_c2_v0_1` |
| `ss` | Simplified structure: UP/DN/MIX | struct | Pine only |

#### 5.2.7 Trend
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `rmdrift` | Drift of dayRM over driftN in RRc units | dayRM, rrc | Pine only |
| `dirrun` | Length of micro direction run | sd, dir | Pine only |
| `trend_tag` | Trend classification from drift + run | rmdrift, dirrun | TV Reference → `derived.tv_reference_c2_v0_1` |

#### 5.2.8 Space
| Metric | Rule | Inputs | Status |
|--------|------|--------|--------|
| `space_up` | Nearest upward target in RRc units | targets, rrc | Pine only |
| `space_dn` | Nearest downward target in RRc units | targets, rrc | Pine only |
| `space_min` | `min(space_up, space_dn)` | space_up, space_dn | Pine only |
| `space_tag` | Space classification: HIGH/MID/LOW | space_min | TV Reference → `derived.tv_reference_c2_v0_1` |

### 5.3 Implementation Status Summary

| Category | Total Metrics | IMPLEMENTED (SQL) | TV Reference (C-layer) | NOT YET (Python) |
|----------|---------------|-------------------|------------------------|------------------|
| Micro Reference | 5 | 0 | 0 | 5 |
| State Metrics | 5 | 1 (`body_ratio`) | 0 | 4 |
| Value Metrics | 6 | 0 | 0 | 6 |
| Liquidity Sweeps | 8 | 0 | 0 | 8 |
| Context Unit | 2 | 0 | 2 (`rrc`, `vrc`) → `derived.tv_reference_c2_v0_1` | 0 |
| Structure State | 6 | 0 | 1 (`struct_state`) → `derived.tv_reference_c2_v0_1` | 5 |
| Trend | 3 | 0 | 1 (`trend_tag`) → `derived.tv_reference_c2_v0_1` | 2 |
| Space | 4 | 0 | 1 (`space_tag`) → `derived.tv_reference_c2_v0_1` | 3 |

---

## 6. L3 — MARKET MODEL & REGIME TAGS (L2–L2.5)

### 6.1 Definition

L3 metrics synthesize L1/L2 evidence into higher-order classifications: regime states, function tags, and tradability assessments.

**Inputs**: L1 + L2 derived features  
**Outputs**: `derived.ovc_market_model_v0_1` (planned), `derived.tv_reference_c3_v0_1` (TV reference)

### 6.2 Composite Tags

#### 6.2.1 L1 Tags (Evidence-Based)
| Tag | Evidence Used | Deterministic | Status |
|-----|---------------|---------------|--------|
| `state_tag` | OR, RER, CLV, thresholds | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `value_tag` | SD, thresholds | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `event` | took_hi, took_lo, oa | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `cp_tag` | OR, mc3, vf3, wick weight | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `tt` | SD, OR, RER, CLV, OA, sweeps, flip | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `tis` | barssince(state_tag change) | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |

#### 6.2.2 L2 Context Tags
| Tag | Evidence Used | Deterministic | Status |
|-----|---------------|---------------|--------|
| `trend_tag` | rmdrift, dirrun, thresholds | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `space_tag` | space_min, thresholds | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `htf_stack` | sd4, sdd, microDir alignment | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |
| `with_htf` | microDir == sd4 direction | Yes | TV Reference → `derived.tv_reference_c2_v0_1` |

#### 6.2.3 Regime Tags (BlockStack)
| Tag | Evidence Used | Deterministic | Status |
|-----|---------------|---------------|--------|
| `regime_tag` | pCampaign, pRDRange, pChop, avgDrift | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `regime_dir` | BiasDir counts over bs_N | Yes | Pine only |
| `regime_conf` | pCampaign, pRDRange, pChop, pSplit | Yes | Pine only |
| `trans_risk` | flip_rate thresholds | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |

#### 6.2.4 Range Detector (RD)
| Tag | Evidence Used | Deterministic | Status |
|-----|---------------|---------------|--------|
| `rd_state` | rd_w_rrc, RMdrift, StateTag, thresholds | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `rd_brkdir` | close vs rd_hi/rd_lo, StateTag, TT | Yes | Pine only |

### 6.3 L3 Decision Objects

All L3 decision fields are TradingView-derived interpretations stored in `derived.tv_reference_c3_v0_1`:

| Field | Evidence Used | Deterministic | Status |
|-------|---------------|---------------|--------|
| `bias_mode` | TrendTag, HTFStack, SS, StateTag, CPTag, TT, RD_State | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `bias_dir` | BiasMode, TrendTag, SS, HTFStack, WithHTF, mDir, RMdrift | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `perm_state` | BiasMode, HTFStack, SpaceTag, KTag2, StateTag, CPTag, TT | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `rail_loc` | close, RangeHi, RangeLo, thresholds | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `tradeable` | PermissionState, BiasDir, RailLoc, targets | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `conf_l3` | PermissionState, SpaceTag, KTag2, Play | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `play` | PermissionState, BiasDir, RailLoc, DominantEvent | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `pred_dir` | BiasDir, RailLoc, Play | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `pred_target` | UpSrc/UpLvl, DnSrc/DnLvl, PredDir | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `timebox` | PermissionState, Play | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |
| `invalidation` | PermissionState, Play, targets | Yes | TV Reference → `derived.tv_reference_c3_v0_1` |

### 6.4 Explainability Principle

All L3 tags are **evidence-backed**:
- Each tag can be traced to specific L1/L2 inputs
- Thresholds and weights are explicit (Pine script parameters)
- No black-box heuristics

---

## 7. TRADINGVIEW METRICS AS REFERENCE ENGINE

### 7.1 Role of TradingView

TradingView Pine scripts serve as the **reference implementation** for OVC metrics:
- Real-time computation and display
- Alert-based export to webhook
- Visual debugging and development

**TradingView outputs are derived, versioned, and non-canonical.** They are used for:
- Parity benchmarking against Python/SQL implementations
- QA and validation during development
- Real-time operational display

**TradingView is NOT the source of truth** for analysis. Python/SQL implementations are authoritative.

### 7.2 Metrics Exported from TradingView (MIN Profile)

All TradingView-derived metrics belong in C-layer tables, not B-layer facts:

| Category | Metrics | C-Tier | Target Table |
|----------|---------|--------|--------------|
| OHLC (raw) | `o`, `h`, `l`, `c` | B-layer | `ovc.ovc_blocks_v01_1_min` |
| OHLC (derived) | `rng`, `body`, `dir`, `ret` | L1 | `derived.ovc_block_features_v0_1` |
| L1 Tags | `state_tag`, `value_tag`, `event`, `tt`, `cp_tag`, `tis` | L2/L3 | `derived.tv_reference_c2_v0_1` |
| L2 Context | `rrc`, `vrc`, `trend_tag`, `struct_state`, `space_tag` | L2 | `derived.tv_reference_c2_v0_1` |
| L2 HTF | `htf_stack`, `with_htf` | L2 | `derived.tv_reference_c2_v0_1` |
| Regime | `rd_state`, `regime_tag`, `trans_risk` | L3 | `derived.tv_reference_c3_v0_1` |
| L3 Decision | `bias_mode`, `bias_dir`, `perm_state`, `rail_loc`, `tradeable`, `conf_l3`, `play`, `pred_dir`, `pred_target`, `timebox`, `invalidation` | L3 | `derived.tv_reference_c3_v0_1` |

### 7.3 TradingView Limitations

| What TV Cannot Provide | Reason |
|------------------------|--------|
| True L3 (orderflow) | No tick data access |
| Volume profile | Limited volume data |
| Cross-instrument correlation | Single chart context |
| Historical replay | Forward-only computation |

---

## 8. GAP ANALYSIS

### 8.1 Metrics in Pine but NOT in Python/SQL

| Metric | Pine Module | C-Tier | Priority |
|--------|-------------|--------|----------|
| `rr`, `rm`, `q1`, `q3`, `band` | L1_REF | L2 | HIGH |
| `rer`, `or`, `bodyrr` | L1_STATE | L2 | HIGH |
| `sd`, `oa`, `mc`, `mc3`, `vflip`, `vf3` | L1_VALUE | L2 | HIGH |
| `swhi`, `swlo`, `took_hi`, `took_lo`, `hi_ran`, `hi_rev`, `lo_ran`, `lo_rev` | L1_LIQ | L2 | MEDIUM |
| `d2rm`, `d2q1`, `d2q3`, `d2rrh`, `d2rrl` | L1_D2K | L2 | LOW |
| `out_ready`, `rtrm`, `nxtext`, `nxtsd`, `hint1`, `hint2` | L1_OUT | L2 | LOW |
| KLS metrics (`near_lvl`, `near_dr`, `conf_l1`, `kscore_l1`, etc.) | L1_KLS, L2_KLS | L2 | LOW |
| `lastpivot`, `swingdir`, `phidr`, `plodr`, `struct`, `ss` | L2_STRUCT | L2 | MEDIUM |
| `rmdrift`, `dirrun` | L2_TREND | L2 | MEDIUM |
| `space_up`, `space_dn`, `up_src`, `dn_src`, `up_lvl`, `dn_lvl` | L2_SPACE | L2 | MEDIUM |
| `sd4`, `sdd`, `htf4`, `htfd`, `mdir` | L2_HTF | L2 | LOW |
| RD metrics (`rd_brkdir`, `rd_w_rrc`, `rd_hi`, `rd_lo`, `rd_mid`, `rd_why`) | RD | L3 | MEDIUM |
| BlockStack fractions (`p_campaign`, `p_rdrange`, `p_confmove`, etc.) | BLOCKSTACK | L3 | LOW |
| L3 rationale (`bias_why`, `blocker`, `reasons`) | L3 | L3 | LOW |

### 8.2 Metrics Computable from OHLC but NOT Yet Implemented

| Metric | Formula | Priority | Reason for Gap |
|--------|---------|----------|----------------|
| `rr` (micro range) | `max(h[1..2]) - min(l[1..2])` | HIGH | Foundation for L2 |
| `rm` (micro midpoint) | `(rr_high + rr_low) / 2` | HIGH | Foundation for SD |
| `sd` (signed distance) | `(c - rm) / rr` | HIGH | Core L1 metric |
| `rer` (range expansion) | `range / rr` | HIGH | State classification |
| `or` (overlap ratio) | overlap with rr | HIGH | State classification |
| Pivot detection | Standard zigzag logic | MEDIUM | Structure tracking |
| `rmdrift` | Rolling rm change | MEDIUM | Trend detection |

### 8.3 Metrics Requiring Additional Data (Future)

| Metric | Required Data | Tier |
|--------|---------------|------|
| Volume profile | Tick volume by price | C5 |
| Orderflow imbalance | Bid/ask volume | C5 |
| Tick-based microstructure | Raw tick stream | C5 |
| Cross-pair correlation | Multi-instrument data | C5 |

---

## 9. IMPLEMENTATION ROADMAP

### Stage 1: L1 Feature Pack v0.1 ✅ COMPLETE

**Scope**: OHLC-derived primitives  
**Inputs**: `ovc.ovc_blocks_v01_1_min` (OHLC only)  
**Outputs**: `derived.ovc_block_features_v0_1`

| Deliverable | Status |
|-------------|--------|
| Bar geometry (range, body, wicks, ratios) | ✅ DONE |
| Returns (ret, logret, direction) | ✅ DONE |
| Session context (sess_high, sess_low, dist) | ✅ DONE |
| Rolling stats (avg_range_12, std_logret_12, range_z_12) | ✅ DONE |
| Structural breaks (hh_12, ll_12, took_prev_high/low) | ✅ DONE |
| Quality flags (range_zero, ret_extreme, range_extreme) | ✅ DONE |

**Definition of Done**: View deployable, formula_hash stable, tests pass.

---

### Stage 2: L2 Structure & Memory 🔜 NEXT

**Scope**: Micro reference, value metrics, structure tracking  
**Inputs**: `derived.ovc_block_features_v0_1` + rolling windows  
**Outputs**: `derived.ovc_block_structure_v0_1` (planned)

| Deliverable | Priority | Status |
|-------------|----------|--------|
| Micro reference (`rr`, `rm`, `q1`, `q3`) | HIGH | NOT STARTED |
| State metrics (`rer`, `or`, `clv`) | HIGH | NOT STARTED |
| Value metrics (`sd`, `oa`, `mc`, `vflip`) | HIGH | NOT STARTED |
| Sweep metrics (`swhi`, `swlo`, `took_hi/lo`) | MEDIUM | NOT STARTED |
| Pivot detection (`lastpivot`, `swingdir`, `struct`) | MEDIUM | NOT STARTED |
| Distance-to-key metrics (`d2rm`, `d2q1`, `d2q3`) | LOW | NOT STARTED |

**Definition of Done**: Python/SQL implementation matches Pine output for validation dataset.

---

### Stage 3: L3 Market Model 📋 PLANNED

**Scope**: Tag derivation from L1/L2 evidence  
**Inputs**: `derived.ovc_block_structure_v0_1`  
**Outputs**: `derived.ovc_market_model_v0_1` (planned)

| Deliverable | Priority | Status |
|-------------|----------|--------|
| `state_tag` derivation | HIGH | TV REFERENCE |
| `value_tag` derivation | HIGH | TV REFERENCE |
| `event` derivation | HIGH | TV REFERENCE |
| `trend_tag` derivation | MEDIUM | TV REFERENCE |
| `space_tag` derivation | MEDIUM | TV REFERENCE |
| `regime_tag` derivation | LOW | TV REFERENCE |
| `bias_mode` / `bias_dir` derivation | LOW | TV REFERENCE |

**Definition of Done**: Python-derived tags match TV-exported tags ≥95% of the time.

---

### Stage 4: TV vs Python Parity (QA) 📋 PLANNED

**Scope**: Dual-engine validation  
**Inputs**: TV exports + Python-derived metrics  
**Outputs**: `ovc_qa.parity_report_v0_1` (planned)

| Deliverable | Status |
|-------------|--------|
| Side-by-side comparison framework | NOT STARTED |
| Deviation detection and reporting | NOT STARTED |
| Threshold-based alerting | NOT STARTED |

**Definition of Done**: Automated CI check flags deviations > threshold.

---

### Stage 5: Optional L3 / Orderflow 🔮 FUTURE

**Scope**: True Level 3 metrics requiring tick data  
**Inputs**: External tick feed (not yet available)  
**Outputs**: TBD

| Deliverable | Status |
|-------------|--------|
| Volume profile integration | FUTURE |
| Orderflow imbalance | FUTURE |
| Microstructure metrics | FUTURE |

**Definition of Done**: N/A (requires data source decision).

---

## Appendix A: Metric Classification Legend

| Class | Name | Description |
|-------|------|-------------|
| **DBF** | Deterministic Bar Features | Bar-local or micro 2-bar reference |
| **WDF** | Windowed Derived Features | Explicit lookbacks, rolling sums, pivots, HTF |
| **CIX** | Composite Indexes | Weighted or normalized scores |
| **EVO** | Event/Decision Outputs | Tags, categorical states, decisions |
| **QAF** | Quality/Assurance Flags | Readiness or guard rails |
| **PMETA** | Process/Identity Metadata | IDs, versioning, config inputs |

---

## Appendix B: File References

| Component | Path |
|-----------|------|
| B-layer canonical table DDL | `sql/01_tables_min.sql` |
| L1 derived features SQL | `sql/derived_v0_1.sql` |
| L2 TV reference SQL | `sql/tv_reference_c2_v0_1.sql` (planned) |
| L3 TV reference SQL | `sql/tv_reference_c3_v0_1.sql` (planned) |
| Option C outcomes SQL | `sql/option_c_v0_1.sql` |
| Research views SQL | `sql/10_views_research_v0.1.sql` |
| OANDA backfill script | `src/backfill_oanda_2h_checkpointed.py` |
| MIN contract | `contracts/export_contract_v0.1.1_min.json` |
| Derived feature set contract | `contracts/derived_feature_set_v0.1.json` |
| Pine export module | `pine/export_module_v0.1.pine` |
| Pine main script | `pine/OVC_v0_1.pine` |
| Metric registry | `docs/derived_metric_registry_v0.1.md` |
| Option C boundary | `docs/option_c_boundary.md` |
| Derived layer boundary | `docs/derived_layer_boundary.md` |
| Outcomes definitions | `docs/outcomes_definitions_v0.1.md` |

---

## Appendix C: Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-01-18 | Initial canonical document |
| v0.2 | 2026-01-18 | Architectural correction: B-layer restricted to OHLC + schedule + metadata; TV-derived tags moved to C-layer reference tables |
