# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study computes the `block_range_intensity` score and analyzes its distributional and structural properties. No outcomes are used. This is a sanity check, not a predictive analysis.

---

## ⚠️ NO OUTCOMES USED

This method deliberately excludes all Option C data. There are:
- No joins to `derived.ovc_outcomes_v0_1`
- No references to returns, MFE, MAE, or any forward-looking measure
- No predictive evaluation of any kind

---

## Step 1: Score Computation

**Purpose:** Generate score values using the score SQL definition

**Input:** `derived.ovc_block_features_v0_1` (filtered to GBPUSD, 2025)

**Output:** Score values for each block

**Method:** Execute `score_block_range_intensity_v1_0.sql` with appropriate filters (see `inputs.md`)

---

## Step 2: Distribution Analysis

**Purpose:** Characterize the overall distribution of score values

**Metrics computed:**

| Statistic | SQL Implementation |
|-----------|-------------------|
| Count | `COUNT(*)` |
| NULL count | `COUNT(*) FILTER (WHERE score_value IS NULL)` |
| Mean | `AVG(score_value)` |
| Std Dev | `STDDEV(score_value)` |
| Min | `MIN(score_value)` |
| Max | `MAX(score_value)` |
| Percentiles | `PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY score_value)` |

**Percentiles computed:** P1, P5, P10, P25, P50, P75, P90, P95, P99

```sql
-- Step 2: Distribution statistics
SELECT
    COUNT(*) AS n_total,
    COUNT(*) FILTER (WHERE score_value IS NULL) AS n_null,
    AVG(score_value) AS mean_score,
    STDDEV(score_value) AS std_score,
    MIN(score_value) AS min_score,
    MAX(score_value) AS max_score,
    PERCENTILE_CONT(0.01) WITHIN GROUP (ORDER BY score_value) AS p01,
    PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY score_value) AS p05,
    PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY score_value) AS p10,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY score_value) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score_value) AS p50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY score_value) AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY score_value) AS p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY score_value) AS p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY score_value) AS p99
FROM score_output;
```

---

## Step 3: Tail Analysis

**Purpose:** Examine extreme score values for anomalies

**Metrics computed:**

| Metric | Definition |
|--------|------------|
| Left tail count | `score_value < -3` |
| Right tail count | `score_value > 3` |
| Extreme left | `score_value < -4` |
| Extreme right | `score_value > 4` |

```sql
-- Step 3: Tail counts
SELECT
    COUNT(*) FILTER (WHERE score_value < -3) AS n_left_tail,
    COUNT(*) FILTER (WHERE score_value > 3) AS n_right_tail,
    COUNT(*) FILTER (WHERE score_value < -4) AS n_extreme_left,
    COUNT(*) FILTER (WHERE score_value > 4) AS n_extreme_right,
    COUNT(*) AS n_total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE score_value < -3) / COUNT(*), 2) AS pct_left_tail,
    ROUND(100.0 * COUNT(*) FILTER (WHERE score_value > 3) / COUNT(*), 2) AS pct_right_tail
FROM score_output;
```

**Expected (for normal z-score):**
- ~0.3% beyond ±3 σ
- ~0.006% beyond ±4 σ

---

## Step 4: Stability Analysis (Time-Sliced)

**Purpose:** Check for drift or structural changes over time

**Method:** Compute mean and std per calendar quarter

```sql
-- Step 4: Quarterly stability
SELECT
    DATE_TRUNC('quarter', ts) AS quarter,
    COUNT(*) AS n,
    AVG(score_value) AS mean_score,
    STDDEV(score_value) AS std_score,
    MIN(score_value) AS min_score,
    MAX(score_value) AS max_score
FROM score_output
GROUP BY DATE_TRUNC('quarter', ts)
ORDER BY quarter;
```

**Expected behavior:**
- Mean should be near 0 in each quarter
- Std should be near 1 in each quarter
- No systematic trend

**Note:** Because z-score is computed globally (over all data), quarterly means may deviate from 0 if the underlying `rng` distribution changes over time. This is expected and should be documented, not "fixed."

---

## Step 5: Data Quality Summary

**Purpose:** Document any issues found

**Checks:**
- NULL rate
- Duplicate block_id (should be 0)
- Missing timestamps
- Unexpected instrument values

```sql
-- Step 5: Data quality
SELECT
    COUNT(*) AS n_total,
    COUNT(DISTINCT block_id) AS n_unique_blocks,
    COUNT(*) - COUNT(DISTINCT block_id) AS n_duplicate_blocks,
    COUNT(*) FILTER (WHERE score_value IS NULL) AS n_null_scores,
    COUNT(DISTINCT instrument) AS n_instruments
FROM score_output;
```

---

## NOT Included in Method

- ❌ Joins to Option C outcomes
- ❌ Correlation with returns, MFE, MAE
- ❌ Predictive analysis of any kind
- ❌ Thresholding or regime classification
- ❌ Backtesting or performance evaluation
- ❌ Statistical significance testing against outcomes

---

## Reproducibility

### Environment

| Component | Version/Value |
|-----------|---------------|
| Canonical release | `ovc-v0.1-spine` |
| Score version | `v1.0` |
| PostgreSQL | 15+ (Neon) |

### Random Seeds

| Purpose | Seed Value |
|---------|------------|
| N/A | No randomization in this study |

### Query Hash

```
sha256: [to be computed after query finalization]
```

---

## Validation Checks

- [ ] Method produces identical results on re-run
- [ ] No Option C data used (verified)
- [ ] All statistics computed as documented
- [ ] Category error checklist passed

### Category Error Checklist (Pre-Execution)

| Check | Pass? |
|-------|-------|
| Does this join to outcomes? | ✅ NO |
| Does this evaluate predictive power? | ✅ NO |
| Does this define trading rules? | ✅ NO |
| Does this threshold the score? | ✅ NO |
| Does this reference `ovc-v0.1-spine`? | ✅ YES |
| Are all inputs explicitly documented? | ✅ YES |
| Is the method deterministic? | ✅ YES |
