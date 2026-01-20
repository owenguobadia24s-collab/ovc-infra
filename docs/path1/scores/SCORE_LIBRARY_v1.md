# Path 1 Score Library v1.0

**Status:** NON-CANONICAL (Research/Descriptive Only)  
**Created:** 2026-01-20  
**Governance:** docs/ops/GOVERNANCE_RULES_v0.1.md

---

## 1. Overview

This document defines three orthogonal, purely descriptive scores for Path 1 research. All scores are:

- **SELECT-only** (no data modification)
- **Outcome-agnostic** in construction
- **Independent** of each other
- **Computed solely from CANONICAL views**

### Canonical Source Views (READ-ONLY)

| View | Purpose |
|------|---------|
| `derived.v_ovc_c1_features_v0_1` | Single-bar features (ratios, positions, shapes) |
| `derived.v_ovc_c2_features_v0_1` | Multi-bar features (rolling, session, streak) |
| `derived.v_ovc_c3_features_v0_1` | Semantic features (regime, trend, structure) |
| `derived.v_ovc_c_outcomes_v0_1` | Forward outcomes (returns, excursions, vol) - **JOIN ONLY IN STUDIES** |

---

## 2. Score Definitions

---

### 2.1 DIS-v1.0 — Directional Imbalance Score

#### 2.1.1 Purpose (Descriptive Only)

DIS measures the degree of directional commitment within a bar relative to its total range. It quantifies how much of the bar's movement was "used" to achieve directional progress versus wasted in reversals (wicks).

**What DIS describes:**
- How efficiently price moved in one direction during the bar
- The balance between body (committed movement) and wicks (reversed movement)

**What DIS does NOT mean:**
- DIS is NOT a signal to trade
- DIS does NOT predict future direction
- DIS does NOT imply momentum continuation
- High DIS does NOT mean "good" and low DIS does NOT mean "bad"

#### 2.1.2 Canonical Input Columns

| Column | Source View | Type |
|--------|-------------|------|
| `block_id` | `v_ovc_c1_features_v0_1` | TEXT |
| `sym` | `v_ovc_c1_features_v0_1` | TEXT |
| `body_ratio` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `directional_efficiency` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `bar_close_ms` | `v_ovc_c2_features_v0_1` | BIGINT |

#### 2.1.3 Formula

```
DIS_raw = body_ratio × |directional_efficiency|

Where:
  body_ratio = |close - open| / (high - low)          ∈ [0, 1]
  directional_efficiency = (close - open) / (high - low)  ∈ [-1, 1]
  |directional_efficiency| = absolute value            ∈ [0, 1]
```

**Domain:** [0, 1]

**Interpretation (descriptive only):**
- DIS = 0: Bar has zero body (pure doji) or zero directional efficiency
- DIS = 1: Bar is pure body with no wicks, fully committed direction

The multiplication captures that:
1. Large body relative to range (high body_ratio) matters
2. Strong directional commitment (high |directional_efficiency|) matters
3. Both must be present for high DIS

#### 2.1.4 Null Handling

| Condition | Result |
|-----------|--------|
| `body_ratio IS NULL` | `raw_score = NULL` |
| `directional_efficiency IS NULL` | `raw_score = NULL` |
| Zero-range bar (rng = 0) | `raw_score = NULL` (inherited from C1) |

#### 2.1.5 Z-Score Normalization

Per-instrument z-score computed over all available history for that symbol:

```sql
z_score = (raw_score - AVG(raw_score) OVER (PARTITION BY sym)) 
        / NULLIF(STDDEV_POP(raw_score) OVER (PARTITION BY sym), 0)
```

If STDDEV = 0 (all values identical), z_score = NULL.

#### 2.1.6 Invariants

- DIS does NOT imply future price movement
- DIS does NOT distinguish bullish from bearish (direction-agnostic)
- Association with outcomes ≠ predictability
- This score is NOT a strategy component

---

### 2.2 RES-v1.0 — Rotation Efficiency Score

#### 2.2.1 Purpose (Descriptive Only)

RES measures how efficiently the current bar's range compares to the recent average range, weighted by body utilization. It describes whether the bar "used" its range efficiently in the context of recent volatility.

**What RES describes:**
- Range expansion/contraction relative to recent average
- Body utilization within that range context

**What RES does NOT mean:**
- RES is NOT a signal to trade
- RES does NOT predict future volatility
- RES does NOT imply breakout or reversal
- High RES does NOT mean "opportunity" and low RES does NOT mean "noise"

#### 2.2.2 Canonical Input Columns

| Column | Source View | Type |
|--------|-------------|------|
| `block_id` | `v_ovc_c1_features_v0_1` | TEXT |
| `sym` | `v_ovc_c1_features_v0_1` | TEXT |
| `rng` | `v_ovc_c1_features_v0_1` | NUMERIC |
| `body_ratio` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `rng_avg_6` | `v_ovc_c2_features_v0_1` | DOUBLE PRECISION |
| `bar_close_ms` | `v_ovc_c2_features_v0_1` | BIGINT |

#### 2.2.3 Formula

```
RES_raw = (rng / rng_avg_6) × body_ratio

Where:
  rng = current bar range (high - low)
  rng_avg_6 = 6-bar rolling average of rng
  body_ratio = |close - open| / (high - low)
```

**Domain:** [0, ∞) theoretically, but practically bounded by rng/rng_avg_6 ratio

**Interpretation (descriptive only):**
- RES < 1: Range below average AND/OR low body utilization
- RES ≈ 1: Typical range with typical body utilization
- RES > 1: Range above average AND/OR high body utilization

#### 2.2.4 Null Handling

| Condition | Result |
|-----------|--------|
| `rng IS NULL` | `raw_score = NULL` |
| `rng_avg_6 IS NULL` | `raw_score = NULL` |
| `rng_avg_6 = 0` | `raw_score = NULL` (divide-by-zero) |
| `body_ratio IS NULL` | `raw_score = NULL` |

#### 2.2.5 Z-Score Normalization

Per-instrument z-score computed over all available history for that symbol:

```sql
z_score = (raw_score - AVG(raw_score) OVER (PARTITION BY sym)) 
        / NULLIF(STDDEV_POP(raw_score) OVER (PARTITION BY sym), 0)
```

If STDDEV = 0, z_score = NULL.

#### 2.2.6 Invariants

- RES does NOT predict future range behavior
- RES does NOT distinguish expanding from contracting regimes meaningfully
- Association with outcomes ≠ predictability
- This score is NOT a strategy component

---

### 2.3 LID-v1.0 — Liquidity Interaction Density

#### 2.3.1 Purpose (Descriptive Only)

LID measures the degree of wick activity relative to body, describing how much "back-and-forth" occurred during the bar. High LID indicates price interacted with both sides of the range; low LID indicates clean directional movement.

**What LID describes:**
- The proportion of range consumed by wicks
- The "noisiness" or "contestedness" of the bar

**What LID does NOT mean:**
- LID is NOT a signal to trade
- LID does NOT predict future liquidity conditions
- LID does NOT imply support/resistance levels
- High LID does NOT mean "rejection" and low LID does NOT mean "acceptance"

#### 2.3.2 Canonical Input Columns

| Column | Source View | Type |
|--------|-------------|------|
| `block_id` | `v_ovc_c1_features_v0_1` | TEXT |
| `sym` | `v_ovc_c1_features_v0_1` | TEXT |
| `upper_wick_ratio` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `lower_wick_ratio` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `body_ratio` | `v_ovc_c1_features_v0_1` | DOUBLE PRECISION |
| `bar_close_ms` | `v_ovc_c2_features_v0_1` | BIGINT |

#### 2.3.3 Formula

```
LID_raw = (upper_wick_ratio + lower_wick_ratio) / NULLIF(body_ratio, 0)

Where:
  upper_wick_ratio = (high - max(open, close)) / (high - low)
  lower_wick_ratio = (min(open, close) - low) / (high - low)
  body_ratio = |close - open| / (high - low)
  
Note: upper_wick_ratio + lower_wick_ratio + body_ratio = 1 (by construction)
Therefore: LID_raw = (1 - body_ratio) / body_ratio when body_ratio > 0
```

**Domain:** [0, ∞)

**Interpretation (descriptive only):**
- LID = 0: No wicks (pure body bar)
- LID = 1: Wicks equal body
- LID → ∞: Tiny body, large wicks (doji-like)

#### 2.3.4 Null Handling

| Condition | Result |
|-----------|--------|
| `upper_wick_ratio IS NULL` | `raw_score = NULL` |
| `lower_wick_ratio IS NULL` | `raw_score = NULL` |
| `body_ratio IS NULL` | `raw_score = NULL` |
| `body_ratio = 0` | `raw_score = NULL` (divide-by-zero) |

#### 2.3.5 Z-Score Normalization

Per-instrument z-score computed over all available history for that symbol:

```sql
z_score = (raw_score - AVG(raw_score) OVER (PARTITION BY sym)) 
        / NULLIF(STDDEV_POP(raw_score) OVER (PARTITION BY sym), 0)
```

If STDDEV = 0, z_score = NULL.

#### 2.3.6 Invariants

- LID does NOT predict future price behavior
- LID does NOT identify "liquidity pools" or similar concepts
- Association with outcomes ≠ predictability
- This score is NOT a strategy component

---

## 3. Disclaimers

### 3.1 General Disclaimers

**THESE SCORES ARE NOT PREDICTIVE.** All three scores (DIS, RES, LID) are purely descriptive measures of past bar characteristics. They:

- Do NOT predict future price movement
- Do NOT constitute trading signals
- Do NOT imply edge, alpha, or tradability
- Do NOT suggest any particular action

**ASSOCIATION ≠ PREDICTABILITY.** Any correlation observed between these scores and forward outcomes in study queries describes historical co-occurrence only. Correlation does not imply:

- Causation
- Future persistence
- Statistical significance
- Economic significance
- Actionable information

### 3.2 Usage Restrictions

These scores are governed by Path 1 rules:

- **No thresholds, tuning, or optimization** based on outcome association
- **No strategy language** (signal, edge, alpha, tradability, PnL, Sharpe, etc.)
- **No composites, weighting, ranking, or decision logic**
- **No INSERT / UPDATE / DELETE operations**

---

## 4. Blocked Concepts

The following score concepts were considered but **CANNOT be implemented** due to missing canonical columns:

| Concept | Missing Data | Notes |
|---------|--------------|-------|
| Volume-weighted scores | No volume data in canonical views | Would require volume from source |
| Spread-based scores | No bid/ask spread data | Would require tick data |
| Time-in-range scores | No sub-bar timing | Would require tick data |
| Cross-instrument correlation | Would require synchronization | Current views are per-sym |

---

## 5. File Manifest

### Score SQL Files
- `sql/path1/scores/score_dis_v1_0.sql`
- `sql/path1/scores/score_res_v1_0.sql`
- `sql/path1/scores/score_lid_v1_0.sql`

### Study SQL Files
- `sql/path1/studies/dis_sanity_distribution.sql`
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql`
- `sql/path1/studies/dis_stability_quarterly.sql`
- `sql/path1/studies/res_sanity_distribution.sql`
- `sql/path1/studies/res_vs_outcomes_bucketed.sql`
- `sql/path1/studies/res_stability_quarterly.sql`
- `sql/path1/studies/lid_sanity_distribution.sql`
- `sql/path1/studies/lid_vs_outcomes_bucketed.sql`
- `sql/path1/studies/lid_stability_quarterly.sql`

### Report Files
- `reports/path1/scores/DIS_v1_0.md`
- `reports/path1/scores/RES_v1_0.md`
- `reports/path1/scores/LID_v1_0.md`

---

## 6. Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-01-20 | Initial creation of DIS, RES, LID scores |
