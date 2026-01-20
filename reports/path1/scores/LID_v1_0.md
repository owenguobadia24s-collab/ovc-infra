# LID-v1.0 — Liquidity Interaction Density

**Status:** NON-CANONICAL (Path 1 Research)  
**Created:** 2026-01-20  
**Score Library:** docs/path1/scores/SCORE_LIBRARY_v1.md

---

## 1. Score Definition Summary

### 1.1 Purpose (Descriptive Only)

LID measures the degree of wick activity relative to body, describing how much "back-and-forth" occurred during the bar. High LID indicates price interacted with both sides of the range; low LID indicates clean directional movement.

### 1.2 Formula

```
LID_raw = (upper_wick_ratio + lower_wick_ratio) / body_ratio

Where:
  upper_wick_ratio = (high - max(open, close)) / (high - low)
  lower_wick_ratio = (min(open, close) - low) / (high - low)
  body_ratio = |close - open| / (high - low)

Note: upper_wick_ratio + lower_wick_ratio + body_ratio = 1 (by construction)
Therefore: LID_raw = (1 - body_ratio) / body_ratio when body_ratio > 0
```

**Domain:** [0, ∞)

### 1.3 Canonical Input Columns

| Column | Source View | Description |
|--------|-------------|-------------|
| `block_id` | `derived.v_ovc_c1_features_v0_1` | Block identifier |
| `sym` | `derived.v_ovc_c1_features_v0_1` | Symbol |
| `upper_wick_ratio` | `derived.v_ovc_c1_features_v0_1` | Upper wick as fraction of range |
| `lower_wick_ratio` | `derived.v_ovc_c1_features_v0_1` | Lower wick as fraction of range |
| `body_ratio` | `derived.v_ovc_c1_features_v0_1` | Body as fraction of range |
| `bar_close_ms` | `derived.v_ovc_c2_features_v0_1` | Timestamp for ordering |

### 1.4 Z-Score Normalization

Per-instrument z-score: `(raw - mean) / stddev` over all available history per symbol.

---

## 2. Disclaimers

**THIS SCORE IS NOT PREDICTIVE.**

- LID does NOT predict future price behavior
- LID does NOT constitute a trading signal
- LID does NOT identify "liquidity pools" or similar concepts
- LID does NOT imply support/resistance levels

**ASSOCIATION ≠ PREDICTABILITY.** Any correlation observed between LID and forward outcomes describes historical co-occurrence only. This is NOT a strategy.

---

## 3. Sanity Distribution Tables

### 3.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/lid_sanity_distribution.sql
-- Execute the full query to get distribution statistics
```

### 3.2 Expected Results Format

| sym | n_total | n_valid | n_null | pct_valid | raw_min | raw_max | raw_mean | raw_stddev | raw_p10 | raw_p25 | raw_p50 | raw_p75 | raw_p90 | raw_p95 | raw_p99 |
|-----|---------|---------|--------|-----------|---------|---------|----------|------------|---------|---------|---------|---------|---------|---------|---------|
| GBPUSD | ... | ... | ... | ... | 0 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 3.3 Expected Behaviors

1. `raw_score` ≥ 0 for all non-NULL values
2. **Asymmetric distribution** with right tail (high values for doji-like bars)
3. Higher NULL rate due to `body_ratio = 0` exclusion
4. Pure body bars (no wicks): `raw_score = 0`
5. Equal wick and body: `raw_score = 1`
6. Near-doji bars: `raw_score` can be very large

### 3.4 Distribution Shape Notes

LID has an **asymmetric, right-skewed distribution** because:
- Minimum is bounded at 0 (no wicks)
- Maximum approaches infinity as body_ratio → 0
- Most bars have some body, so median is typically < 2

---

## 4. Outcome Association Tables

### 4.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/lid_vs_outcomes_bucketed.sql
-- Execute the full query to get bucketed outcome associations
```

### 4.2 Expected Results Format

| sym | z_bucket | n | mean_fwd_ret_1_bps | mean_fwd_ret_3_bps | mean_fwd_ret_6_bps | med_fwd_ret_1_bps | ... | mean_rvol_6_bps |
|-----|----------|---|--------------------|--------------------|--------------------|--------------------|-----|-----------------|
| GBPUSD | 1 | ... | ... | ... | ... | ... | ... | ... |
| GBPUSD | 2 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| GBPUSD | 10 | ... | ... | ... | ... | ... | ... | ... |

### 4.3 Interpretation Notes

- **z_bucket 1** = Extreme low LID (full-body bars, no wicks)
- **z_bucket 10** = Extreme high LID (wick-heavy, doji-like bars)
- All returns expressed in basis points (× 10000)
- **Any patterns observed are DESCRIPTIVE ONLY**

---

## 5. Stability Tables

### 5.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/lid_stability_quarterly.sql
-- Execute the full query to get quarterly stability metrics
```

### 5.2 Expected Results Format

| sym | quarter | z_bucket | n | pct_of_quarter | mean_raw | stddev_raw | mean_z | stddev_z |
|-----|---------|----------|---|----------------|----------|------------|--------|----------|
| GBPUSD | 2025-Q4 | 1 | ... | ... | ... | ... | ... | ... |
| GBPUSD | 2025-Q4 | 2 | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### 5.3 Stability Indicators

- `pct_of_quarter` should be similar across quarters for same bucket
- `mean_z` should be consistent within bucket across quarters
- Large distribution shifts may indicate regime changes (descriptive only)

---

## 6. Null Rates and Coverage

### 6.1 NULL Conditions

| Condition | Result |
|-----------|--------|
| `upper_wick_ratio IS NULL` | `raw_score = NULL` |
| `lower_wick_ratio IS NULL` | `raw_score = NULL` |
| `body_ratio IS NULL` | `raw_score = NULL` |
| `body_ratio = 0` | `raw_score = NULL` (divide-by-zero) |

### 6.2 Expected NULL Rate

- Higher NULL rate than DIS due to `body_ratio = 0` exclusion
- Doji bars (body_ratio ≈ 0) contribute to NULL count
- Zero-range bars also contribute to NULL count
- Check `n_null / n_total` in sanity distribution

---

## 7. SQL File References

| Purpose | File |
|---------|------|
| Score computation | `sql/path1/scores/score_lid_v1_0.sql` |
| Sanity distribution | `sql/path1/studies/lid_sanity_distribution.sql` |
| Outcome association | `sql/path1/studies/lid_vs_outcomes_bucketed.sql` |
| Temporal stability | `sql/path1/studies/lid_stability_quarterly.sql` |

---

## 8. Execution Instructions

### 8.1 Prerequisites

- Access to Neon database with canonical views deployed
- Database URL configured in environment

### 8.2 Running Studies

```powershell
# Connect to Neon and run study SQL files
# Example using psql:
psql $env:DATABASE_URL -f sql/path1/studies/lid_sanity_distribution.sql
psql $env:DATABASE_URL -f sql/path1/studies/lid_vs_outcomes_bucketed.sql
psql $env:DATABASE_URL -f sql/path1/studies/lid_stability_quarterly.sql
```

### 8.3 Results Collection

Copy query outputs into this report's tables above for documentation.

---

**FINAL DISCLAIMER:** This score and all associated studies are for descriptive research only. They do NOT constitute trading signals, strategies, or actionable information. Association with outcomes does NOT imply predictability.
