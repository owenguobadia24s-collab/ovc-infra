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
| `derived.ovc_block_features_v0_1` | `derived` | Option B block features (C1/C2/C3) |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key (format: YYYYMMDD-{A-L}-{SYM}) |
| `ts` | timestamptz | Block timestamp (bar close time, UTC) |
| `instrument` | text | Trading pair (e.g., GBPUSD) |
| `rng` | numeric | Range: high - low (placeholder; confirm from canonical schema) |
| `body` | numeric | Body: abs(close - open) (placeholder; confirm from canonical schema) |
| `dir` | int | Direction: 1 (up), -1 (down), 0 (doji) (placeholder; confirm from canonical schema) |

**Note:** The specific feature columns (`rng`, `body`, `dir`) are placeholders based on expected MIN contract fields. Confirm against actual `derived.ovc_block_features_v0_1` schema before execution.

### Outcome Source

| Object | Schema | Description |
|--------|--------|-------------|
| `derived.ovc_outcomes_v0_1` | `derived` | Option C forward-looking outcomes |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Foreign key to features |
| `fwd_ret_3` | numeric | 3-bar forward return |
| `mfe_3` | numeric | Maximum favorable excursion over 3 bars |
| `mae_3` | numeric | Maximum adverse excursion over 3 bars |

---

## Sampling Window

| Parameter | Value |
|-----------|-------|
| Start (inclusive) | `2025-01-01T00:00:00Z` |
| End (exclusive) | `2026-01-01T00:00:00Z` |
| Total bars (approx) | ~2,160 (12 blocks/day × ~180 trading days) |

**Note:** Actual count depends on data availability and excludes weekends/holidays with no market data.

---

## Filters Applied

```sql
WHERE instrument = 'GBPUSD'
  AND ts >= '2025-01-01T00:00:00Z'
  AND ts < '2026-01-01T00:00:00Z'
```

No additional filters. All GBPUSD blocks within the window are included.

---

## External Inputs

| Source | Description | Justification |
|--------|-------------|---------------|
| None | — | Study uses only canonical data |

---

## Data Quality Notes

Pre-execution checklist:

- [ ] Confirmed no NULL values in key columns (`block_id`, `ts`, `instrument`)
- [ ] Confirmed no duplicate `block_id` values
- [ ] Confirmed time window has expected bar count (within 20% of estimate)
- [ ] Confirmed canonical release matches expected schema
- [ ] Confirmed join between features and outcomes has high match rate (>95%)

---

## Query for Input Extraction

```sql
-- Study: study_20260120_basic_feature_outcome_baseline
-- Canonical release: ovc-v0.1-spine
-- Purpose: Extract features and outcomes for descriptive analysis
-- Query hash: [to be computed after finalization]

SELECT
    f.block_id,
    f.ts,
    f.instrument,
    -- Feature columns (confirm against actual schema)
    f.rng,
    f.body,
    f.dir,
    -- Outcome columns
    o.fwd_ret_3,
    o.mfe_3,
    o.mae_3
FROM derived.ovc_block_features_v0_1 f
JOIN derived.ovc_outcomes_v0_1 o USING (block_id)
WHERE f.instrument = 'GBPUSD'
  AND f.ts >= '2025-01-01T00:00:00Z'
  AND f.ts < '2026-01-01T00:00:00Z'
ORDER BY f.ts;
```

**Note:** This query uses INNER JOIN. Rows without matching outcomes are excluded. Document any exclusion rate in results.
