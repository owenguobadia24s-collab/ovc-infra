# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study joins the `block_range_intensity` score with canonical outcomes and produces descriptive summaries: correlations and bucket-conditional statistics. No prediction, no thresholds for decisions.

---

## Important: Bucket Disclaimer

**Buckets are for reporting only.**

The bucket boundaries defined below are arbitrary percentile cutoffs used to summarize data. They are:

- NOT decision thresholds
- NOT trading rules
- NOT regime boundaries
- NOT recommendations

Any observed pattern within buckets does not imply exploitability.

---

## Step A: Compute Score

**Purpose:** Generate score values using the score SQL logic

**Input:** `derived.ovc_block_features_v0_1`

**Output:** Score value per block

**Method:** Inline CTE from `score_block_range_intensity_v1_0.sql`

```sql
-- Step A: Score computation (z-score of rng)
WITH base AS (
    SELECT block_id, ts, instrument, rng
    FROM derived.ovc_block_features_v0_1
    WHERE rng IS NOT NULL
      AND instrument = 'GBPUSD'
      AND ts >= '2025-01-01' AND ts < '2026-01-01'
),
global_stats AS (
    SELECT instrument, AVG(rng) AS mean_rng, STDDEV(rng) AS std_rng
    FROM base GROUP BY instrument
),
score_calc AS (
    SELECT b.block_id, b.ts, b.instrument,
           CASE WHEN g.std_rng = 0 THEN NULL
                ELSE (b.rng - g.mean_rng) / g.std_rng END AS score_value
    FROM base b JOIN global_stats g USING (instrument)
)
SELECT * FROM score_calc;
```

---

## Step B: Join to Outcomes

**Purpose:** Align score values with canonical outcomes

**Input:** Score output + `derived.ovc_outcomes_v0_1`

**Output:** Combined dataset with score + outcomes per block

```sql
-- Step B: Join score with outcomes
SELECT
    s.block_id,
    s.ts,
    s.instrument,
    s.score_value,
    o.fwd_ret_3,
    o.mfe_3,
    o.mae_3
FROM score_calc s
JOIN derived.ovc_outcomes_v0_1 o USING (block_id)
WHERE s.score_value IS NOT NULL;
```

---

## Step L1: Correlation Analysis

**Purpose:** Compute linear association between score and each outcome

**Method:** Pearson correlation coefficient

```sql
-- Step L1: Correlations
SELECT
    CORR(score_value, fwd_ret_3) AS corr_fwd_ret_3,
    CORR(score_value, mfe_3) AS corr_mfe_3,
    CORR(score_value, mae_3) AS corr_mae_3
FROM combined;
```

**Interpretation guide (descriptive only):**

| |r| | Interpretation |
|-----|----------------|
| < 0.1 | Negligible |
| 0.1 – 0.3 | Weak |
| 0.3 – 0.5 | Moderate |
| > 0.5 | Strong |

---

## Step L2: Bucket Summaries

**Purpose:** Summarize outcome distributions conditional on score percentile buckets

**Bucket Definitions:**

| Bucket | Percentile Range | Description |
|--------|------------------|-------------|
| 1 | 0 – 10 | Bottom decile |
| 2 | 10 – 25 | Low quartile |
| 3 | 25 – 50 | Below median |
| 4 | 50 – 75 | Above median |
| 5 | 75 – 90 | High quartile |
| 6 | 90 – 100 | Top decile |

**Method:** Assign bucket using `NTILE` or percentile boundaries, then aggregate

```sql
-- Step L2: Bucket summaries
WITH bucket_assignment AS (
    SELECT
        *,
        CASE
            WHEN score_pct <= 0.10 THEN '0-10'
            WHEN score_pct <= 0.25 THEN '10-25'
            WHEN score_pct <= 0.50 THEN '25-50'
            WHEN score_pct <= 0.75 THEN '50-75'
            WHEN score_pct <= 0.90 THEN '75-90'
            ELSE '90-100'
        END AS bucket
    FROM (
        SELECT *,
               PERCENT_RANK() OVER (ORDER BY score_value) AS score_pct
        FROM combined
    ) sub
)
SELECT
    bucket,
    COUNT(*) AS n,
    -- fwd_ret_3
    AVG(fwd_ret_3) AS mean_fwd_ret_3,
    STDDEV(fwd_ret_3) AS std_fwd_ret_3,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY fwd_ret_3) AS p25_fwd_ret_3,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY fwd_ret_3) AS p50_fwd_ret_3,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY fwd_ret_3) AS p75_fwd_ret_3,
    -- mfe_3
    AVG(mfe_3) AS mean_mfe_3,
    STDDEV(mfe_3) AS std_mfe_3,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mfe_3) AS p50_mfe_3,
    -- mae_3
    AVG(mae_3) AS mean_mae_3,
    STDDEV(mae_3) AS std_mae_3,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mae_3) AS p50_mae_3
FROM bucket_assignment
GROUP BY bucket
ORDER BY bucket;
```

---

## Step L3: Tail Comparison

**Purpose:** Compare top decile vs bottom decile outcome distributions (descriptive only)

**Method:** Extract statistics for bucket '0-10' and bucket '90-100', present side-by-side

```sql
-- Step L3: Tail comparison
SELECT
    bucket,
    COUNT(*) AS n,
    AVG(fwd_ret_3) AS mean_fwd_ret_3,
    AVG(mfe_3) AS mean_mfe_3,
    AVG(mae_3) AS mean_mae_3
FROM bucket_assignment
WHERE bucket IN ('0-10', '90-100')
GROUP BY bucket;
```

**Note:** This is a descriptive comparison. No statistical test is performed. Any observed difference does not imply exploitability.

---

## Statistical Methods Summary

| Method | Purpose | Implementation |
|--------|---------|----------------|
| Pearson correlation | Linear association | SQL `CORR(x, y)` |
| Percentile bucketing | Conditional summaries | `PERCENT_RANK()` + CASE |
| Descriptive statistics | Per-bucket characterization | AVG, STDDEV, PERCENTILE_CONT |

---

## NOT Included in Method

- ❌ Hypothesis testing for significance
- ❌ Predictive modeling
- ❌ Threshold optimization
- ❌ Strategy rules or entry/exit logic
- ❌ PnL simulation
- ❌ Out-of-sample validation

---

## Reproducibility

### Environment

| Component | Version/Value |
|-----------|---------------|
| Canonical release | `ovc-v0.1-spine` |
| Score version | `v1.0` |
| PostgreSQL | 15+ (Neon) |

### Parameters

| Parameter | Value |
|-----------|-------|
| Bucket edges (percentile) | [0, 10, 25, 50, 75, 90, 100] |

### Query Hash

```
sha256: [to be computed after finalization]
```

---

## Validation Checks

- [ ] Method produces identical results on re-run
- [ ] No look-ahead bias (outcomes are forward-looking by definition)
- [ ] All parameters documented
- [ ] Buckets are reporting-only (no decision logic)
- [ ] Category error checklist passed

### Category Error Checklist

| Check | Pass? |
|-------|-------|
| Does this define entry/exit rules? | ✅ NO |
| Does this recommend thresholds? | ✅ NO |
| Does this optimize for performance? | ✅ NO |
| Does this claim predictability? | ✅ NO |
| Does this reference `ovc-v0.1-spine`? | ✅ YES |
| Are all inputs documented? | ✅ YES |
| Is the method deterministic? | ✅ YES |
