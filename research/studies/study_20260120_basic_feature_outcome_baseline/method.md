# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study performs a simple descriptive analysis: join canonical features with outcomes, compute summary statistics, and calculate pairwise correlations. No modeling, no prediction, no scoring.

---

## Transformations

### Step 1: Data Extraction

**Purpose:** Extract aligned features and outcomes for the study window

**Input:** Canonical views (`derived.ovc_block_features_v0_1`, `derived.ovc_outcomes_v0_1`)

**Output:** Single joined dataset with features and outcomes per block

```sql
-- Step 1: Join features with outcomes
WITH joined_data AS (
    SELECT
        f.block_id,
        f.ts,
        f.instrument,
        f.rng,
        f.body,
        f.dir,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3
    FROM derived.ovc_block_features_v0_1 f
    JOIN derived.ovc_outcomes_v0_1 o USING (block_id)
    WHERE f.instrument = 'GBPUSD'
      AND f.ts >= '2025-01-01'
      AND f.ts < '2026-01-01'
)
SELECT * FROM joined_data;
```

### Step 2: Summary Statistics

**Purpose:** Compute descriptive statistics for all numeric columns

**Input:** Joined dataset from Step 1

**Output:** Summary table (count, mean, std, min, percentiles, max)

```sql
-- Step 2: Compute summary statistics (example for one column)
SELECT
    COUNT(*) AS n,
    AVG(rng) AS mean_rng,
    STDDEV(rng) AS std_rng,
    MIN(rng) AS min_rng,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rng) AS p25_rng,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY rng) AS p50_rng,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rng) AS p75_rng,
    MAX(rng) AS max_rng
FROM joined_data;

-- Repeat for: body, dir, fwd_ret_3, mfe_3, mae_3
```

### Step 3: Correlation Matrix

**Purpose:** Compute pairwise Pearson correlations between features and outcomes

**Input:** Joined dataset from Step 1

**Output:** Correlation matrix (features × outcomes)

```sql
-- Step 3: Compute correlations (example)
SELECT
    CORR(rng, fwd_ret_3) AS corr_rng_fwd_ret_3,
    CORR(rng, mfe_3) AS corr_rng_mfe_3,
    CORR(rng, mae_3) AS corr_rng_mae_3,
    CORR(body, fwd_ret_3) AS corr_body_fwd_ret_3,
    CORR(body, mfe_3) AS corr_body_mfe_3,
    CORR(body, mae_3) AS corr_body_mae_3
FROM joined_data;
```

**Note:** `dir` is categorical (-1, 0, 1). For `dir`, compute mean outcomes per direction group instead of correlation.

---

## Statistical Methods

### Primary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| Descriptive statistics | Characterize distributions | SQL `AVG`, `STDDEV`, `PERCENTILE_CONT` |
| Pearson correlation | Measure linear relationship | SQL `CORR(x, y)` |
| Conditional means | Outcome by direction | `GROUP BY dir` |

### Secondary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| Histogram binning | Visualize distributions | Post-hoc in notebook (optional) |
| Spearman rank correlation | Check for non-linear monotonic relationships | Post-hoc if Pearson is weak |

---

## Scoring Definition

**Not applicable.** This study does not produce a score. It is purely descriptive.

---

## NOT Included in Method

- ❌ Entry/exit rule definitions
- ❌ Position sizing logic
- ❌ PnL optimization
- ❌ Parameter search for trading performance
- ❌ Regime classification
- ❌ Thresholding for decisions
- ❌ Predictive modeling
- ❌ Machine learning

---

## Reproducibility

### Environment

| Component | Version/Value |
|-----------|---------------|
| Canonical release | `ovc-v0.1-spine` |
| PostgreSQL | 15+ (Neon) |
| Python (if used) | 3.11+ |
| Key libraries | pandas, numpy (if post-processing) |

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
- [ ] No look-ahead bias in transformations (outcomes are forward-looking by definition; no additional bias introduced)
- [ ] All parameters explicitly documented (none in this study)
- [ ] Category error checklist passed (see below)

### Category Error Checklist (Pre-Execution)

| Check | Pass? |
|-------|-------|
| Does this define entry/exit rules? | ✅ NO |
| Does this compute position sizes? | ✅ NO |
| Does this optimize for PnL or Sharpe? | ✅ NO |
| Does this modify canonical tables? | ✅ NO |
| Does this redefine a canonical metric? | ✅ NO |
| Does this reference `ovc-v0.1-spine`? | ✅ YES |
| Are all inputs explicitly documented? | ✅ YES |
| Is the method deterministic and reproducible? | ✅ YES |
