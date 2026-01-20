# Study Inputs

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Canonical Release

```
ovc-v0.1-spine
```

---

## Canonical Tables / Views

### Primary Feature Source

| Object | Schema | Description |
|--------|--------|-------------|
| `ovc_block_features_v0_1` | `derived` | Option B block features |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key, join key to outcomes |
| `ts` | timestamptz | Block timestamp (UTC) |
| `instrument` | text | Trading pair (e.g., GBPUSD) |
| `rng` | numeric | Block range (high - low), used for score and regime |

### Outcome Source

| Object | Schema | Description |
|--------|--------|-------------|
| `ovc_outcomes_v0_1` | `derived` | Option C forward outcomes |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Foreign key to features (join key) |
| `fwd_ret_3` | numeric | 3-bar forward return |
| `mfe_3` | numeric | Max favorable excursion over 3 bars |
| `mae_3` | numeric | Max adverse excursion over 3 bars |

### Score Source

| Object | Location | Description |
|--------|----------|-------------|
| `block_range_intensity` | `research/scores/score_block_range_intensity_v1_0.sql` | Z-score of rng (read-only definition) |

**Score Computation:**
- Input: `rng` from `derived.ovc_block_features_v0_1`
- Method: Per-instrument z-score: `(rng - mean(rng)) / stddev(rng)`
- Output: `score_value` (numeric, unbounded)

---

## Join Key

| Key | Source A | Source B | Type |
|-----|----------|----------|------|
| `block_id` | `derived.ovc_block_features_v0_1` | `derived.ovc_outcomes_v0_1` | INNER JOIN |

**Expected Match Rate:**
- Features and outcomes should have ~100% match for blocks within the window.
- Blocks without outcomes (e.g., at end of window, insufficient forward data) will be excluded via INNER JOIN.

**Handling of Missing Rows:**
- Missing `rng`: Excluded (NULL `rng` filtered out in score computation)
- Missing outcomes: Excluded (INNER JOIN drops blocks without outcome rows)
- Missing `block_id`: Not applicable (PK in both tables)

---

## Sampling Window

| Parameter | Value |
|-----------|-------|
| Start (inclusive) | `2025-01-01T00:00:00Z` |
| End (exclusive) | `2026-01-01T00:00:00Z` |
| Instrument | GBPUSD |
| Total bars (approx) | ~4,380 blocks (365 days × 12 blocks/day, minus weekends/holidays) |

---

## Filters Applied

```sql
WHERE instrument = 'GBPUSD'
  AND ts >= '2025-01-01T00:00:00Z'
  AND ts < '2026-01-01T00:00:00Z'
  AND rng IS NOT NULL
```

---

## External Inputs

| Source | Description | Justification |
|--------|-------------|---------------|
| None | — | This study uses only canonical Option B features and Option C outcomes |

---

## Data Quality Notes

- [ ] Confirmed no NULL values in `block_id`, `ts`, `instrument`
- [ ] Confirmed no NULL values in `rng` (after filter)
- [ ] Confirmed no duplicate `block_id` values
- [ ] Confirmed time window has expected bar count
- [ ] Confirmed canonical release matches expected schema
- [ ] Confirmed outcomes exist for majority of feature rows

---

## Query for Input Extraction

```sql
-- Base feature extraction with score computation
-- Join key: block_id

SELECT
    f.block_id,
    f.ts,
    f.instrument,
    f.rng,
    o.fwd_ret_3,
    o.mfe_3,
    o.mae_3
FROM derived.ovc_block_features_v0_1 f
INNER JOIN derived.ovc_outcomes_v0_1 o
    ON f.block_id = o.block_id
WHERE f.instrument = 'GBPUSD'
  AND f.ts >= '2025-01-01T00:00:00Z'
  AND f.ts < '2026-01-01T00:00:00Z'
  AND f.rng IS NOT NULL;
```
