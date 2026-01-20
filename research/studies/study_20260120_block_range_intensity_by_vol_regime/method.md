# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study describes how the association between `block_range_intensity` score and forward outcomes
varies across volatility regimes (LOW/MID/HIGH). Regimes are defined by fixed percentile cutoffs
(P33, P66) of the canonical `rng` feature computed over the full sample. No optimization or
threshold tuning is performed.

---

## Transformations

### Step A: Extract Base Sample

**Purpose:** Retrieve GBPUSD blocks within the study window with non-null `rng`.

**Input:** `derived.ovc_block_features_v0_1`

**Output:** `block_id`, `ts`, `instrument`, `rng`

```sql
WITH base AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng
    FROM derived.ovc_block_features_v0_1
    WHERE instrument = 'GBPUSD'
      AND ts >= '2025-01-01T00:00:00Z'
      AND ts < '2026-01-01T00:00:00Z'
      AND rng IS NOT NULL
)
```

### Step B: Compute Volatility Regime Thresholds

**Purpose:** Calculate P33 and P66 percentiles of `rng` over the full sample to define regime boundaries.

**Input:** `base` CTE

**Output:** Scalar values `p33_rng`, `p66_rng`

```sql
thresholds AS (
    SELECT
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY rng) AS p33_rng,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY rng) AS p66_rng
    FROM base
)
```

**Note:** Percentiles are computed once over the full sample, not per-regime or per-bucket.

### Step C: Assign Volatility Regime per Block

**Purpose:** Label each block with its volatility regime based on `rng` relative to thresholds.

**Input:** `base`, `thresholds`

**Output:** `block_id`, `ts`, `instrument`, `rng`, `vol_regime`

```sql
labeled AS (
    SELECT
        b.block_id,
        b.ts,
        b.instrument,
        b.rng,
        CASE
            WHEN b.rng <= t.p33_rng THEN 'LOW'
            WHEN b.rng <= t.p66_rng THEN 'MID'
            ELSE 'HIGH'
        END AS vol_regime
    FROM base b
    CROSS JOIN thresholds t
)
```

### Step D: Compute block_range_intensity Score

**Purpose:** Calculate the z-score of `rng` per instrument (using full-sample statistics).

**Input:** `labeled`

**Output:** `block_id`, ..., `score_value`

```sql
global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng
    FROM labeled
    GROUP BY instrument
),

score_calc AS (
    SELECT
        l.block_id,
        l.ts,
        l.instrument,
        l.rng,
        l.vol_regime,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (l.rng - g.mean_rng) / g.std_rng
        END AS score_value
    FROM labeled l
    JOIN global_stats g USING (instrument)
)
```

**Note:** Score statistics (mean, std) are computed over the full sample, not per-regime.

### Step E: Join to Outcomes

**Purpose:** Attach forward outcomes to scored blocks.

**Input:** `score_calc`, `derived.ovc_outcomes_v0_1`

**Output:** `block_id`, `vol_regime`, `score_value`, `fwd_ret_3`, `mfe_3`, `mae_3`

```sql
joined_outcomes AS (
    SELECT
        s.block_id,
        s.ts,
        s.instrument,
        s.rng,
        s.vol_regime,
        s.score_value,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3
    FROM score_calc s
    INNER JOIN derived.ovc_outcomes_v0_1 o
        ON s.block_id = o.block_id
    WHERE s.score_value IS NOT NULL
)
```

### Step F: Compute Regime Summaries

**Purpose:** Within each volatility regime, compute:
- Correlation between score_value and each outcome
- Bucket summaries using fixed global score percentile edges

**Input:** `joined_outcomes`

**Output:** Correlation table, bucket summary table, sample counts

---

## Statistical Methods

### Primary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| Pearson correlation | Measure linear association between score and outcomes | `CORR(score_value, outcome)` grouped by `vol_regime` |
| Bucket summaries | Describe outcome distributions within score buckets | `GROUP BY vol_regime, score_bucket` |
| Sample counts | Report N per regime and per bucket | `COUNT(*)` |

### Bucket Definition

Score buckets are defined by **fixed percentile edges applied to the full sample**:

| Bucket Label | Percentile Range |
|--------------|------------------|
| `0-10` | 0th to 10th percentile |
| `10-25` | 10th to 25th percentile |
| `25-50` | 25th to 50th percentile |
| `50-75` | 50th to 75th percentile |
| `75-90` | 75th to 90th percentile |
| `90-100` | 90th to 100th percentile |

**Important:** Bucket edges are computed over the full sample once, then applied identically across all regimes. Buckets are NOT recomputed per-regime.

### Tail Comparison

Compare outcomes for:
- **Top decile:** score_value in 90-100 bucket
- **Bottom decile:** score_value in 0-10 bucket

Report mean outcomes for each tail, by regime.

---

## Primary Analysis SQL

```sql
-- ============================================================================
-- REGIME-CONDITIONED SCORE-OUTCOME ANALYSIS
-- Study: block_range_intensity by volatility regime
-- ============================================================================

WITH

-- ----------------------------------------------------------------------------
-- BASE: Extract GBPUSD blocks in study window
-- ----------------------------------------------------------------------------
base AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng
    FROM derived.ovc_block_features_v0_1
    WHERE instrument = 'GBPUSD'
      AND ts >= '2025-01-01T00:00:00Z'
      AND ts < '2026-01-01T00:00:00Z'
      AND rng IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- THRESHOLDS: Compute P33 and P66 of rng for regime definition
-- ----------------------------------------------------------------------------
thresholds AS (
    SELECT
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY rng) AS p33_rng,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY rng) AS p66_rng
    FROM base
),

-- ----------------------------------------------------------------------------
-- LABELED: Assign volatility regime to each block
-- ----------------------------------------------------------------------------
labeled AS (
    SELECT
        b.block_id,
        b.ts,
        b.instrument,
        b.rng,
        CASE
            WHEN b.rng <= t.p33_rng THEN 'LOW'
            WHEN b.rng <= t.p66_rng THEN 'MID'
            ELSE 'HIGH'
        END AS vol_regime
    FROM base b
    CROSS JOIN thresholds t
),

-- ----------------------------------------------------------------------------
-- GLOBAL_STATS: Per-instrument mean/std for z-score (full sample)
-- ----------------------------------------------------------------------------
global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng
    FROM labeled
    GROUP BY instrument
),

-- ----------------------------------------------------------------------------
-- SCORE_CALC: Compute block_range_intensity z-score
-- ----------------------------------------------------------------------------
score_calc AS (
    SELECT
        l.block_id,
        l.ts,
        l.instrument,
        l.rng,
        l.vol_regime,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (l.rng - g.mean_rng) / g.std_rng
        END AS score_value
    FROM labeled l
    JOIN global_stats g USING (instrument)
),

-- ----------------------------------------------------------------------------
-- SCORE_PERCENTILES: Compute score bucket edges (full sample)
-- ----------------------------------------------------------------------------
score_percentiles AS (
    SELECT
        PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY score_value) AS p10,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY score_value) AS p25,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score_value) AS p50,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY score_value) AS p75,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY score_value) AS p90
    FROM score_calc
    WHERE score_value IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- JOINED_OUTCOMES: Attach outcomes to scored blocks
-- ----------------------------------------------------------------------------
joined_outcomes AS (
    SELECT
        s.block_id,
        s.ts,
        s.instrument,
        s.rng,
        s.vol_regime,
        s.score_value,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3,
        CASE
            WHEN s.score_value <= sp.p10 THEN '0-10'
            WHEN s.score_value <= sp.p25 THEN '10-25'
            WHEN s.score_value <= sp.p50 THEN '25-50'
            WHEN s.score_value <= sp.p75 THEN '50-75'
            WHEN s.score_value <= sp.p90 THEN '75-90'
            ELSE '90-100'
        END AS score_bucket
    FROM score_calc s
    INNER JOIN derived.ovc_outcomes_v0_1 o ON s.block_id = o.block_id
    CROSS JOIN score_percentiles sp
    WHERE s.score_value IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- REGIME_SUMMARIES: Correlations and counts per regime
-- ----------------------------------------------------------------------------
regime_summaries AS (
    SELECT
        vol_regime,
        COUNT(*) AS n_blocks,
        CORR(score_value, fwd_ret_3) AS corr_fwd_ret_3,
        CORR(score_value, mfe_3) AS corr_mfe_3,
        CORR(score_value, mae_3) AS corr_mae_3,
        AVG(fwd_ret_3) AS mean_fwd_ret_3,
        AVG(mfe_3) AS mean_mfe_3,
        AVG(mae_3) AS mean_mae_3
    FROM joined_outcomes
    GROUP BY vol_regime
),

-- ----------------------------------------------------------------------------
-- BUCKET_SUMMARIES: Outcome stats per regime × score bucket
-- ----------------------------------------------------------------------------
bucket_summaries AS (
    SELECT
        vol_regime,
        score_bucket,
        COUNT(*) AS n,
        AVG(fwd_ret_3) AS mean_fwd_ret_3,
        AVG(mfe_3) AS mean_mfe_3,
        AVG(mae_3) AS mean_mae_3,
        STDDEV(fwd_ret_3) AS std_fwd_ret_3,
        STDDEV(mfe_3) AS std_mfe_3,
        STDDEV(mae_3) AS std_mae_3
    FROM joined_outcomes
    GROUP BY vol_regime, score_bucket
)

-- Output: Select which summary to display
-- Option 1: Regime thresholds
-- SELECT * FROM thresholds;

-- Option 2: Regime-level correlations
-- SELECT * FROM regime_summaries ORDER BY vol_regime;

-- Option 3: Bucket summaries
SELECT * FROM bucket_summaries ORDER BY vol_regime, score_bucket;
```

---

## NOT Included in Method

- ❌ Entry/exit rule definitions
- ❌ Position sizing logic
- ❌ PnL optimization
- ❌ Parameter search for trading performance
- ❌ Regime cutoff optimization
- ❌ Per-regime score bucket re-fitting
- ❌ Statistical significance testing (descriptive only)
