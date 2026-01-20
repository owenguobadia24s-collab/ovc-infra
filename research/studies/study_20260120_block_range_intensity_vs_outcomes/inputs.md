# Study Inputs

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Canonical Release

```
ovc-v0.1-spine
```

---

## Canonical Tables / Views

### Option B Feature Source (for Score Computation)

| Object | Schema | Description |
|--------|--------|-------------|
| `derived.ovc_block_features_v0_1` | `derived` | Option B block features |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `ts` | timestamptz | Block timestamp |
| `instrument` | text | Trading pair |
| `rng` | numeric | Range (high - low) — input to score |

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

### Score SQL File

| File | Path |
|------|------|
| `score_block_range_intensity_v1_0.sql` | `research/scores/score_block_range_intensity_v1_0.sql` |

**Score Output Schema:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `ts` | timestamptz | Block timestamp |
| `instrument` | text | Trading pair |
| `score_name` | text | Constant: 'block_range_intensity' |
| `score_value` | numeric | Z-score of range |
| `score_version` | text | Constant: 'v1.0' |

---

## Join Strategy

### Primary Join

```
score (by block_id) → outcomes (by block_id)
```

| Left | Right | Key | Type |
|------|-------|-----|------|
| Score output | `derived.ovc_outcomes_v0_1` | `block_id` | INNER JOIN |

### Expected Exclusions

| Reason | Expected Rate |
|--------|---------------|
| Score NULL (stddev = 0) | < 1% |
| Outcome missing for block | < 5% |
| Total exclusion | < 5% |

**Note:** Document actual exclusion rate in results.

---

## Sampling Window

| Parameter | Value |
|-----------|-------|
| Start (inclusive) | `2025-01-01T00:00:00Z` |
| End (exclusive) | `2026-01-01T00:00:00Z` |
| Total bars (approx) | ~2,160 (12 blocks/day × ~180 trading days) |

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

- [ ] Score computation executes without error
- [ ] Outcome join has high match rate (> 95%)
- [ ] No unexpected NULL values in outcomes after join
- [ ] Sample size within expected range (~2,000 rows)

---

## Query for Combined Dataset

```sql
-- Study: study_20260120_block_range_intensity_vs_outcomes
-- Canonical release: ovc-v0.1-spine
-- Purpose: Join score with outcomes for descriptive analysis

WITH

-- Score computation (inline from score SQL)
base AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng
    FROM derived.ovc_block_features_v0_1
    WHERE rng IS NOT NULL
      AND instrument = 'GBPUSD'
      AND ts >= '2025-01-01T00:00:00Z'
      AND ts < '2026-01-01T00:00:00Z'
),

global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng
    FROM base
    GROUP BY instrument
),

score_calc AS (
    SELECT
        b.block_id,
        b.ts,
        b.instrument,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (b.rng - g.mean_rng) / g.std_rng
        END AS score_value
    FROM base b
    JOIN global_stats g USING (instrument)
),

-- Join with outcomes
combined AS (
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
    WHERE s.score_value IS NOT NULL
)

SELECT * FROM combined
ORDER BY ts;
```
