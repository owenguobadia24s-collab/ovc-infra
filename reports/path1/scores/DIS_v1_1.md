# DIS-v1.1 — Directional Imbalance Score

**Status:** NON-CANONICAL (Path 1 Research)  
**Created:** 2026-01-20  
**Updated:** 2026-01-20 — v1.1 removes directional_efficiency dependency  
**Score Library:** docs/path1/scores/SCORE_LIBRARY_v1.md

> **v1.1 Note:** DIS-v1.0 has been withdrawn. This version uses only `body_ratio`.

---

## 1. Score Definition Summary

### 1.1 Purpose (Descriptive Only)

DIS measures the degree of directional commitment within a bar relative to its total range. It quantifies how efficiently price moved in one direction during the bar formation.

### 1.2 Formula

```
DIS_raw = body_ratio

Where:
  body_ratio = |close - open| / (high - low)   ∈ [0, 1]
```

**Domain:** [0, 1]

### 1.3 Canonical Input Columns

| Column | Source View | Description |
|--------|-------------|-------------|
| `block_id` | `derived.v_ovc_l1_features_v0_1` | Block identifier |
| `sym` | `derived.v_ovc_l1_features_v0_1` | Symbol |
| `body_ratio` | `derived.v_ovc_l1_features_v0_1` | Body as fraction of range |
| `bar_close_ms` | `derived.v_ovc_l2_features_v0_1` | Timestamp for ordering |

### 1.4 Z-Score Normalization

Per-instrument z-score: `(raw - mean) / stddev` over all available history per symbol.

---

## 2. Disclaimers

**THIS SCORE IS NOT PREDICTIVE.**

- DIS does NOT predict future price movement
- DIS does NOT constitute a trading signal
- DIS does NOT imply edge, alpha, or tradability
- DIS does NOT distinguish bullish from bearish (direction-agnostic)

**ASSOCIATION ≠ PREDICTABILITY.** Any correlation observed between DIS and forward outcomes describes historical co-occurrence only. This is NOT a strategy.

---

## 3. Sanity Distribution Tables

### 3.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/dis_sanity_distribution.sql
-- Execute the full query to get distribution statistics
```

### 3.2 Expected Results Format

| sym | n_total | n_valid | n_null | pct_valid | raw_min | raw_max | raw_mean | raw_stddev | raw_p10 | raw_p25 | raw_p50 | raw_p75 | raw_p90 |
|-----|---------|---------|--------|-----------|---------|---------|----------|------------|---------|---------|---------|---------|---------|
| GBPUSD | ... | ... | ... | ... | 0 | 1 | ... | ... | ... | ... | ... | ... | ... |

### 3.3 Expected Behaviors

1. `raw_score` ∈ [0, 1] for all non-NULL values
2. NULL rate should be low (only zero-range bars)
3. Distribution should be right-skewed (more bars have some body)
4. Pure body bars: `raw_score = 1`
5. Pure doji bars: `raw_score ≈ 0`

---

## 4. Outcome Association Tables

### 4.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/dis_vs_outcomes_bucketed.sql
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

- **z_bucket 1** = Extreme low DIS (doji-like bars)
- **z_bucket 10** = Extreme high DIS (full-body bars)
- All returns expressed in basis points (× 10000)
- **Any patterns observed are DESCRIPTIVE ONLY**

---

## 5. Stability Tables

### 5.1 How to Generate

Run the following SQL against your Neon database:

```sql
-- File: sql/path1/studies/dis_stability_quarterly.sql
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
| `body_ratio IS NULL` | `raw_score = NULL` |
| Zero-range bar | `raw_score = NULL` (inherited from L1) |

### 6.2 Expected NULL Rate

- NULL rate should be **very low** (<1% typically)
- Zero-range bars are rare in FX markets
- Check `n_null / n_total` in sanity distribution

---

## 7. SQL File References

| Purpose | File |
|---------|------|
| Score computation | `sql/path1/scores/score_dis_v1_1.sql` |
| Sanity distribution | `sql/path1/studies/dis_sanity_distribution.sql` |
| Outcome association | `sql/path1/studies/dis_vs_outcomes_bucketed.sql` |
| Temporal stability | `sql/path1/studies/dis_stability_quarterly.sql` |

---

## 8. Execution Instructions

### 8.1 Prerequisites

- Access to Neon database with canonical views deployed
- Database URL configured in environment

### 8.2 Running Studies

```powershell
# Connect to Neon and run study SQL files
# Example using psql:
psql $env:DATABASE_URL -f sql/path1/studies/dis_sanity_distribution.sql
psql $env:DATABASE_URL -f sql/path1/studies/dis_vs_outcomes_bucketed.sql
psql $env:DATABASE_URL -f sql/path1/studies/dis_stability_quarterly.sql
```

### 8.3 Results Collection

Copy query outputs into this report's tables above for documentation.

---

**FINAL DISCLAIMER:** This score and all associated studies are for descriptive research only. They do NOT constitute trading signals, strategies, or actionable information. Association with outcomes does NOT imply predictability.
