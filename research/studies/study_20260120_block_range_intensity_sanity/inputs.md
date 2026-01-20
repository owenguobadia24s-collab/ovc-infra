# Study Inputs

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Canonical Release

```
ovc-v0.1-spine
```

---

## ⚠️ NO OUTCOMES USED

**This study deliberately excludes all Option C outcomes.**

The following are NOT inputs to this study:
- ❌ `derived.ovc_outcomes_v0_1`
- ❌ `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_6`
- ❌ `mfe_3`, `mfe_6`
- ❌ `mae_3`, `mae_6`
- ❌ `rvol_6`

---

## Canonical Tables / Views

### Option B Feature Source

| Object | Schema | Description |
|--------|--------|-------------|
| `derived.ovc_block_features_v0_1` | `derived` | Option B block features (input to score) |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `ts` | timestamptz | Block timestamp |
| `instrument` | text | Trading pair |
| `rng` | numeric | Range (high - low) — score input |

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
```

---

## External Inputs

| Source | Description | Justification |
|--------|-------------|---------------|
| None | — | Study uses only canonical features and derived score |

---

## Data Quality Notes

Pre-execution checklist:

- [ ] Score SQL executes without error
- [ ] No unexpected NULL values in score_value
- [ ] Sample size matches expected (~2,000+ rows)
- [ ] Score output schema matches specification

---

## Query for Score Computation

```sql
-- Study: study_20260120_block_range_intensity_sanity
-- Canonical release: ovc-v0.1-spine
-- Purpose: Compute score for sanity analysis
-- NOTE: This is the score SQL with instrument/time filter applied

WITH

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
)

SELECT
    block_id,
    ts,
    instrument,
    'block_range_intensity'::text AS score_name,
    score_value,
    'v1.0'::text AS score_version
FROM score_calc
ORDER BY ts;
```
