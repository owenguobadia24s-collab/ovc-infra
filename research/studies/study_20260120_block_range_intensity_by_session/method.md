# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

This study describes how the association between `block_range_intensity` score and forward outcomes
varies across fixed time-of-day sessions (SESSION_A through SESSION_D). Sessions are defined by
fixed UTC hour bins. No optimization or threshold tuning is performed.

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

### Step B: Derive Session Label from Timestamp

**Purpose:** Assign each block to a fixed UTC session based on its timestamp hour.

**Input:** `base` CTE

**Output:** `block_id`, `ts`, `instrument`, `rng`, `session`

```sql
session_labeled AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng,
        CASE
            WHEN EXTRACT(HOUR FROM ts) >= 0  AND EXTRACT(HOUR FROM ts) < 6  THEN 'SESSION_A'
            WHEN EXTRACT(HOUR FROM ts) >= 6  AND EXTRACT(HOUR FROM ts) < 12 THEN 'SESSION_B'
            WHEN EXTRACT(HOUR FROM ts) >= 12 AND EXTRACT(HOUR FROM ts) < 18 THEN 'SESSION_C'
            WHEN EXTRACT(HOUR FROM ts) >= 18 AND EXTRACT(HOUR FROM ts) < 24 THEN 'SESSION_D'
        END AS session
    FROM base
)
```

**Note:** Session bins are fixed and not subject to optimization.

### Step C: Compute block_range_intensity Score

**Purpose:** Calculate the z-score of `rng` per instrument (using full-sample statistics).

**Input:** `session_labeled`

**Output:** `block_id`, ..., `score_value`

```sql
global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng
    FROM session_labeled
    GROUP BY instrument
),

score_calc AS (
    SELECT
        s.block_id,
        s.ts,
        s.instrument,
        s.rng,
        s.session,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (s.rng - g.mean_rng) / g.std_rng
        END AS score_value
    FROM session_labeled s
    JOIN global_stats g USING (instrument)
)
```

**Note:** Score statistics (mean, std) are computed over the full sample, not per-session.

### Step D: Join to Outcomes

**Purpose:** Attach forward outcomes to scored blocks.

**Input:** `score_calc`, `derived.ovc_outcomes_v0_1`

**Output:** `block_id`, `session`, `score_value`, `fwd_ret_3`, `mfe_3`, `mae_3`

```sql
joined_outcomes AS (
    SELECT
        sc.block_id,
        sc.ts,
        sc.instrument,
        sc.rng,
        sc.session,
        sc.score_value,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3
    FROM score_calc sc
    INNER JOIN derived.ovc_outcomes_v0_1 o
        ON sc.block_id = o.block_id
    WHERE sc.score_value IS NOT NULL
)
```

### Step E: Compute Session Summaries

**Purpose:** Within each session, compute:
- Correlation between score_value and each outcome
- Bucket summaries using fixed global score percentile edges

**Input:** `joined_outcomes`

**Output:** Correlation table, bucket summary table, sample counts

---

## Statistical Methods

### Primary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| Pearson correlation | Measure linear association between score and outcomes | `CORR(score_value, outcome)` grouped by `session` |
| Bucket summaries | Describe outcome distributions within score buckets | `GROUP BY session, score_bucket` |
| Sample counts | Report N per session and per bucket | `COUNT(*)` |

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

**Important:** Bucket edges are computed over the full sample once, then applied identically across all sessions. Buckets are NOT recomputed per-session.

### Tail Comparison

Compare outcomes for:
- **Top decile:** score_value in 90-100 bucket
- **Bottom decile:** score_value in 0-10 bucket

Report mean outcomes for each tail, by session.

---

## Primary Analysis SQL

```sql
-- ============================================================================
-- SESSION-CONDITIONED SCORE-OUTCOME ANALYSIS
-- Study: block_range_intensity by time-of-day session
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
-- SESSION_LABELED: Assign session based on UTC hour
-- ----------------------------------------------------------------------------
session_labeled AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng,
        CASE
            WHEN EXTRACT(HOUR FROM ts) >= 0  AND EXTRACT(HOUR FROM ts) < 6  THEN 'SESSION_A'
            WHEN EXTRACT(HOUR FROM ts) >= 6  AND EXTRACT(HOUR FROM ts) < 12 THEN 'SESSION_B'
            WHEN EXTRACT(HOUR FROM ts) >= 12 AND EXTRACT(HOUR FROM ts) < 18 THEN 'SESSION_C'
            WHEN EXTRACT(HOUR FROM ts) >= 18 AND EXTRACT(HOUR FROM ts) < 24 THEN 'SESSION_D'
        END AS session
    FROM base
),

-- ----------------------------------------------------------------------------
-- GLOBAL_STATS: Per-instrument mean/std for z-score (full sample)
-- ----------------------------------------------------------------------------
global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng
    FROM session_labeled
    GROUP BY instrument
),

-- ----------------------------------------------------------------------------
-- SCORE_CALC: Compute block_range_intensity z-score
-- ----------------------------------------------------------------------------
score_calc AS (
    SELECT
        s.block_id,
        s.ts,
        s.instrument,
        s.rng,
        s.session,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (s.rng - g.mean_rng) / g.std_rng
        END AS score_value
    FROM session_labeled s
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
-- JOINED_OUTCOMES: Attach outcomes to scored blocks with bucket assignment
-- ----------------------------------------------------------------------------
joined_outcomes AS (
    SELECT
        sc.block_id,
        sc.ts,
        sc.instrument,
        sc.rng,
        sc.session,
        sc.score_value,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3,
        CASE
            WHEN sc.score_value <= sp.p10 THEN '0-10'
            WHEN sc.score_value <= sp.p25 THEN '10-25'
            WHEN sc.score_value <= sp.p50 THEN '25-50'
            WHEN sc.score_value <= sp.p75 THEN '50-75'
            WHEN sc.score_value <= sp.p90 THEN '75-90'
            ELSE '90-100'
        END AS score_bucket
    FROM score_calc sc
    INNER JOIN derived.ovc_outcomes_v0_1 o ON sc.block_id = o.block_id
    CROSS JOIN score_percentiles sp
    WHERE sc.score_value IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- SESSION_SUMMARIES: Correlations and counts per session
-- ----------------------------------------------------------------------------
session_summaries AS (
    SELECT
        session,
        COUNT(*) AS n_blocks,
        CORR(score_value, fwd_ret_3) AS corr_fwd_ret_3,
        CORR(score_value, mfe_3) AS corr_mfe_3,
        CORR(score_value, mae_3) AS corr_mae_3,
        AVG(fwd_ret_3) AS mean_fwd_ret_3,
        AVG(mfe_3) AS mean_mfe_3,
        AVG(mae_3) AS mean_mae_3
    FROM joined_outcomes
    GROUP BY session
),

-- ----------------------------------------------------------------------------
-- BUCKET_SUMMARIES: Outcome stats per session × score bucket
-- ----------------------------------------------------------------------------
bucket_summaries AS (
    SELECT
        session,
        score_bucket,
        COUNT(*) AS n,
        AVG(fwd_ret_3) AS mean_fwd_ret_3,
        AVG(mfe_3) AS mean_mfe_3,
        AVG(mae_3) AS mean_mae_3,
        STDDEV(fwd_ret_3) AS std_fwd_ret_3,
        STDDEV(mfe_3) AS std_mfe_3,
        STDDEV(mae_3) AS std_mae_3
    FROM joined_outcomes
    GROUP BY session, score_bucket
)

-- Output: Select which summary to display
-- Option 1: Session-level correlations
-- SELECT * FROM session_summaries ORDER BY session;

-- Option 2: Bucket summaries
SELECT * FROM bucket_summaries ORDER BY session, score_bucket;
```

---

## NOT Included in Method

- ❌ Entry/exit rule definitions
- ❌ Position sizing logic
- ❌ PnL optimization
- ❌ Parameter search for trading performance
- ❌ Session ranking or recommendations
- ❌ Per-session score bucket re-fitting
- ❌ Statistical significance testing (descriptive only)
