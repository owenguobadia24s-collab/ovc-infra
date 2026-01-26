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
| `ovc_block_features_v0_1` | `derived` | Option B block features (includes L1/L2/L3 columns) |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key, join key to outcomes |
| `ts` | timestamptz | Block timestamp (UTC) |
| `instrument` | text | Trading pair (e.g., GBPUSD) |
| `rng` | numeric | Block range (high - low), used for score computation |
| `l3_trend_bias` | text/categorical | Canonical L3 trend bias state (taken as-is) |

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

## Conditioning Variable: l3_trend_bias

**Source:** `derived.ovc_block_features_v0_1.l3_trend_bias`

**Usage:**
- This field is taken **as-is** from the canonical L3 layer.
- This study does NOT define, compute, or modify the trend bias logic.
- The underlying derivation (from L2 inputs such as `dir_streak`, `dir_change`) is specified in L3 documentation.

**Observed Categories:**
- Categories will be documented at execution time; no assumptions are made about specific values.
- Expected categories may include labels like `bullish`, `bearish`, `neutral`, `mixed`, etc., but the actual values depend on canonical L3 implementation.

**NULL Handling:**
- Blocks with NULL `l3_trend_bias` are excluded from category-specific analysis.
- NULL rate will be documented in results.

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
- Missing `l3_trend_bias`: Documented as NULL rate; excluded from per-category analysis
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

**Note:** `l3_trend_bias IS NOT NULL` filter applied only for per-category analysis; NULL count reported separately.

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
- [ ] Documented NULL rate for `l3_trend_bias`
- [ ] Documented observed categories for `l3_trend_bias`

---

## Query for Input Extraction

```sql
-- Base feature extraction with l3_trend_bias
-- Join key: block_id

SELECT
    f.block_id,
    f.ts,
    f.instrument,
    f.rng,
    f.l3_trend_bias,
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
