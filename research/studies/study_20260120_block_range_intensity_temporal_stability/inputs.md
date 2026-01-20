# Study Inputs

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Canonical Release

```
ovc-v0.1-spine
```

---

## Canonical Tables / Views

### Option B Feature Source

| Object | Schema | Description |
|--------|--------|-------------|
| `derived.ovc_block_features_v0_1` | `derived` | Option B block features |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `ts` | timestamptz | Block timestamp (used for time slicing) |
| `instrument` | text | Trading pair |
| `rng` | numeric | Range (high - low) — score input |

### Option C Outcome Source

| Object | Schema | Description |
|--------|--------|-------------|
| `derived.ovc_outcomes_v0_1` | `derived` | Option C forward-looking outcomes |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Foreign key to features |
| `fwd_ret_3` | numeric | 3-bar forward return |
| `mfe_3` | numeric | Maximum favorable excursion (3 bars) |
| `mae_3` | numeric | Maximum adverse excursion (3 bars) |

---

## Score Definition

| File | Path |
|------|------|
| `score_block_range_intensity_v1_0.sql` | `research/scores/score_block_range_intensity_v1_0.sql` |

**Note:** Score is computed once over the full window. The z-score normalization uses global (full-year) mean and std, NOT per-quarter statistics. This is intentional: we want to see how a fixed score behaves across time, not re-normalize per slice.

---

## Time Slicing Logic

### Quarterly Partitions

| Quarter | Filter Condition |
|---------|------------------|
| Q1 2025 | `ts >= '2025-01-01' AND ts < '2025-04-01'` |
| Q2 2025 | `ts >= '2025-04-01' AND ts < '2025-07-01'` |
| Q3 2025 | `ts >= '2025-07-01' AND ts < '2025-10-01'` |
| Q4 2025 | `ts >= '2025-10-01' AND ts < '2026-01-01'` |

### SQL Implementation

```sql
CASE
    WHEN ts >= '2025-01-01' AND ts < '2025-04-01' THEN 'Q1'
    WHEN ts >= '2025-04-01' AND ts < '2025-07-01' THEN 'Q2'
    WHEN ts >= '2025-07-01' AND ts < '2025-10-01' THEN 'Q3'
    WHEN ts >= '2025-10-01' AND ts < '2026-01-01' THEN 'Q4'
END AS quarter
```

---

## Bucket Definitions (Fixed)

Bucket edges are identical to `study_20260120_block_range_intensity_vs_outcomes`:

| Bucket | Percentile Range |
|--------|------------------|
| 0-10 | Bottom decile |
| 10-25 | Low quartile |
| 25-50 | Below median |
| 50-75 | Above median |
| 75-90 | High quartile |
| 90-100 | Top decile |

**Critical:** Buckets are computed using full-sample percentiles, NOT per-quarter percentiles. This ensures consistent bucket membership across time.

---

## Sampling Window

| Parameter | Value |
|-----------|-------|
| Start (inclusive) | `2025-01-01T00:00:00Z` |
| End (exclusive) | `2026-01-01T00:00:00Z` |
| Expected total bars | ~2,160 |
| Expected per quarter | ~540 |

---

## Filters Applied

```sql
WHERE instrument = 'GBPUSD'
  AND ts >= '2025-01-01T00:00:00Z'
  AND ts < '2026-01-01T00:00:00Z'
  AND score_value IS NOT NULL
```

---

## External Inputs

| Source | Description | Justification |
|--------|-------------|---------------|
| None | — | Study uses only canonical data and derived score |

---

## Data Quality Notes

Pre-execution checklist:

- [ ] All quarters have sufficient data (N ≥ 100)
- [ ] Score computation uses full-year normalization
- [ ] Bucket assignment uses full-sample percentiles
- [ ] No per-quarter re-optimization

---

## Query for Time-Sliced Dataset

```sql
-- Study: study_20260120_block_range_intensity_temporal_stability
-- Canonical release: ovc-v0.1-spine
-- Purpose: Prepare time-sliced dataset for stability analysis

WITH

-- Score computation (full-year normalization)
base AS (
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
),

-- Full-sample percentile ranks for bucket assignment
with_percentiles AS (
    SELECT *,
           PERCENT_RANK() OVER (ORDER BY score_value) AS score_pct
    FROM score_calc
    WHERE score_value IS NOT NULL
),

-- Bucket assignment (full-sample)
with_buckets AS (
    SELECT *,
           CASE
               WHEN score_pct <= 0.10 THEN '0-10'
               WHEN score_pct <= 0.25 THEN '10-25'
               WHEN score_pct <= 0.50 THEN '25-50'
               WHEN score_pct <= 0.75 THEN '50-75'
               WHEN score_pct <= 0.90 THEN '75-90'
               ELSE '90-100'
           END AS bucket
    FROM with_percentiles
),

-- Add quarter labels
with_quarters AS (
    SELECT *,
           CASE
               WHEN ts >= '2025-01-01' AND ts < '2025-04-01' THEN 'Q1'
               WHEN ts >= '2025-04-01' AND ts < '2025-07-01' THEN 'Q2'
               WHEN ts >= '2025-07-01' AND ts < '2025-10-01' THEN 'Q3'
               WHEN ts >= '2025-10-01' AND ts < '2026-01-01' THEN 'Q4'
           END AS quarter
    FROM with_buckets
),

-- Join with outcomes
combined AS (
    SELECT
        q.block_id,
        q.ts,
        q.instrument,
        q.quarter,
        q.score_value,
        q.bucket,
        o.fwd_ret_3,
        o.mfe_3,
        o.mae_3
    FROM with_quarters q
    JOIN derived.ovc_outcomes_v0_1 o USING (block_id)
)

SELECT * FROM combined ORDER BY ts;
```
