# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study partitions the data by calendar quarter and repeats the correlation and bucket analyses from `study_20260120_block_range_intensity_vs_outcomes`. We assess whether associations are stable, drifting, or regime-dependent.

---

## Critical Design Decisions

### 1. Score Normalization: Full-Year

The z-score is computed using **full-year** mean and std, NOT per-quarter. This ensures:
- Score values are comparable across quarters
- We observe how a fixed score behaves over time
- No per-quarter re-optimization

### 2. Bucket Assignment: Full-Sample Percentiles

Buckets are assigned using **full-sample** percentiles, NOT per-quarter. This ensures:
- Bucket membership is consistent across time
- We can compare "top decile" in Q1 vs Q4 meaningfully
- No moving goalposts

### 3. No Selection of "Best" Periods

We report all quarters equally. We do NOT:
- Exclude quarters with weak results
- Highlight quarters with strong results
- Optimize window boundaries

---

## Step A: Compute Score (Full-Year Normalization)

**Purpose:** Generate score values using global statistics

**Method:** Same as prior studies; z-score using full-year mean/std

```sql
-- Score computed with full-year normalization
-- (See inputs.md for full query)
```

---

## Step B: Join to Outcomes

**Purpose:** Align score with canonical outcomes

**Method:** INNER JOIN on block_id

---

## Step C: Partition by Quarter

**Purpose:** Assign each block to a calendar quarter

**Method:** CASE statement on `ts`

| Quarter | Period |
|---------|--------|
| Q1 | 2025-01-01 to 2025-03-31 |
| Q2 | 2025-04-01 to 2025-06-30 |
| Q3 | 2025-07-01 to 2025-09-30 |
| Q4 | 2025-10-01 to 2025-12-31 |

---

## Step D1: Per-Quarter Correlations

**Purpose:** Compute score–outcome correlations for each quarter

```sql
-- Step D1: Correlations by quarter
SELECT
    quarter,
    COUNT(*) AS n,
    CORR(score_value, fwd_ret_3) AS corr_fwd_ret_3,
    CORR(score_value, mfe_3) AS corr_mfe_3,
    CORR(score_value, mae_3) AS corr_mae_3
FROM combined
GROUP BY quarter
ORDER BY quarter;
```

---

## Step D2: Per-Quarter Bucket Summaries

**Purpose:** Compute bucket-conditional outcome statistics for each quarter

```sql
-- Step D2: Bucket summaries by quarter
SELECT
    quarter,
    bucket,
    COUNT(*) AS n,
    AVG(fwd_ret_3) AS mean_fwd_ret_3,
    STDDEV(fwd_ret_3) AS std_fwd_ret_3,
    AVG(mfe_3) AS mean_mfe_3,
    AVG(mae_3) AS mean_mae_3
FROM combined
GROUP BY quarter, bucket
ORDER BY quarter, bucket;
```

**Bucket edges (fixed):** [0, 10, 25, 50, 75, 90, 100] percentile

---

## Step E: Stability Comparison

### E1: Slice-to-Slice Variation

**Purpose:** Quantify how much correlations vary across quarters

**Metrics:**

| Metric | Computation |
|--------|-------------|
| Correlation range | max(r) - min(r) across quarters |
| Correlation std | std(r) across quarters |
| Sign consistency | Do all quarters have same sign? |

```sql
-- Example: Correlation variability
WITH quarterly_corrs AS (
    SELECT quarter, CORR(score_value, fwd_ret_3) AS r
    FROM combined GROUP BY quarter
)
SELECT
    MAX(r) - MIN(r) AS corr_range,
    STDDEV(r) AS corr_std,
    COUNT(DISTINCT SIGN(r)) AS n_signs  -- 1 = consistent, 2 = sign flip
FROM quarterly_corrs;
```

### E2: Directional Consistency

**Purpose:** Check if bucket gradients point the same direction across quarters

**Method:** Compare mean outcome for top decile vs bottom decile per quarter

```sql
-- Example: Tail comparison by quarter
SELECT
    quarter,
    AVG(fwd_ret_3) FILTER (WHERE bucket = '90-100') AS mean_top,
    AVG(fwd_ret_3) FILTER (WHERE bucket = '0-10') AS mean_bottom,
    AVG(fwd_ret_3) FILTER (WHERE bucket = '90-100') -
        AVG(fwd_ret_3) FILTER (WHERE bucket = '0-10') AS tail_diff
FROM combined
GROUP BY quarter
ORDER BY quarter;
```

### E3: Tail Persistence

**Purpose:** Check if extreme score values predict extreme outcomes consistently

**Method:** Count proportion of top/bottom decile blocks with extreme outcomes per quarter

---

## Statistical Methods Summary

| Method | Purpose | Per-Quarter? |
|--------|---------|--------------|
| Pearson correlation | Linear association | Yes |
| Bucket means | Conditional summaries | Yes |
| Correlation range/std | Variability measure | Across quarters |
| Sign consistency | Directional stability | Across quarters |
| Tail difference | Extreme comparison | Yes |

---

## NOT Included in Method

- ❌ Per-quarter re-normalization of score
- ❌ Per-quarter re-definition of buckets
- ❌ Selection of "best" quarter
- ❌ Optimization of window boundaries
- ❌ Hypothesis testing for significance
- ❌ Predictive modeling

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
| Time slicing | Quarterly (calendar) |
| Bucket edges (percentile) | [0, 10, 25, 50, 75, 90, 100] |
| Score normalization | Full-year |
| Bucket assignment | Full-sample percentiles |

### Query Hash

```
sha256: [to be computed after finalization]
```

---

## Validation Checks

- [ ] All quarters have N ≥ 100
- [ ] Bucket edges are fixed across quarters
- [ ] Score uses full-year normalization
- [ ] No per-quarter optimization
- [ ] Category error checklist passed

### Category Error Checklist

| Check | Pass? |
|-------|-------|
| Does this select "best" periods? | ✅ NO |
| Does this optimize windows? | ✅ NO |
| Does this claim any period is tradable? | ✅ NO |
| Does this modify bucket definitions per quarter? | ✅ NO |
| Does this reference `ovc-v0.1-spine`? | ✅ YES |
| Are all parameters fixed a priori? | ✅ YES |
