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
| `ts` | timestamptz | Block timestamp (UTC) — used for session derivation |
| `instrument` | text | Trading pair (e.g., GBPUSD) |
| `rng` | numeric | Block range (high - low), used for score computation |

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

## Session Derivation Logic

Sessions are derived from the `ts` column using the **UTC hour** of each block:

```sql
CASE
    WHEN EXTRACT(HOUR FROM ts) >= 0  AND EXTRACT(HOUR FROM ts) < 6  THEN 'SESSION_A'
    WHEN EXTRACT(HOUR FROM ts) >= 6  AND EXTRACT(HOUR FROM ts) < 12 THEN 'SESSION_B'
    WHEN EXTRACT(HOUR FROM ts) >= 12 AND EXTRACT(HOUR FROM ts) < 18 THEN 'SESSION_C'
    WHEN EXTRACT(HOUR FROM ts) >= 18 AND EXTRACT(HOUR FROM ts) < 24 THEN 'SESSION_D'
END AS session
```

| Session | UTC Hour Range | Blocks per Day (2H bars) |
|---------|----------------|--------------------------|
| SESSION_A | 00:00–05:59 | 3 blocks |
| SESSION_B | 06:00–11:59 | 3 blocks |
| SESSION_C | 12:00–17:59 | 3 blocks |
| SESSION_D | 18:00–23:59 | 3 blocks |

**Note:** Each 2H block's session is determined by its opening timestamp.

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
- Missing `ts`: Excluded (cannot derive session without timestamp)
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
- [ ] Confirmed all 4 sessions are represented in data

---

## Query for Input Extraction

```sql
-- Base feature extraction with session derivation
-- Join key: block_id

SELECT
    f.block_id,
    f.ts,
    f.instrument,
    f.rng,
    CASE
        WHEN EXTRACT(HOUR FROM f.ts) >= 0  AND EXTRACT(HOUR FROM f.ts) < 6  THEN 'SESSION_A'
        WHEN EXTRACT(HOUR FROM f.ts) >= 6  AND EXTRACT(HOUR FROM f.ts) < 12 THEN 'SESSION_B'
        WHEN EXTRACT(HOUR FROM f.ts) >= 12 AND EXTRACT(HOUR FROM f.ts) < 18 THEN 'SESSION_C'
        WHEN EXTRACT(HOUR FROM f.ts) >= 18 AND EXTRACT(HOUR FROM f.ts) < 24 THEN 'SESSION_D'
    END AS session,
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
