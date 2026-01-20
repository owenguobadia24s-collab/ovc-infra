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
| `{{CANONICAL_FEATURE_VIEW}}` | `derived` | Option B block features |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `ts` | timestamptz | Block timestamp |
| `instrument` | text | Trading pair |
| `[column]` | [type] | [description] |
| `[column]` | [type] | [description] |

### Outcome Source

| Object | Schema | Description |
|--------|--------|-------------|
| `{{CANONICAL_OUTCOME_VIEW}}` | `derived` | Option C outcomes |

**Columns Used:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Foreign key to features |
| `fwd_ret_1` | numeric | 1-bar forward return |
| `fwd_ret_3` | numeric | 3-bar forward return |
| `fwd_ret_6` | numeric | 6-bar forward return |
| `mfe_3` | numeric | Max favorable excursion (3 bars) |
| `mfe_6` | numeric | Max favorable excursion (6 bars) |
| `mae_3` | numeric | Max adverse excursion (3 bars) |
| `mae_6` | numeric | Max adverse excursion (6 bars) |
| `rvol_6` | numeric | Realized volatility (6 bars) |

---

## Sampling Window

| Parameter | Value |
|-----------|-------|
| Start (inclusive) | `YYYY-MM-DDTHH:MM:SSZ` |
| End (exclusive) | `YYYY-MM-DDTHH:MM:SSZ` |
| Total bars (approx) | [number] |

---

## Filters Applied

```sql
WHERE instrument IN ('GBPUSD', 'EURUSD')
  AND ts >= '2025-01-01'
  AND ts < '2026-01-15'
  AND [additional filters]
```

---

## External Inputs

| Source | Description | Justification |
|--------|-------------|---------------|
| None | — | — |

_If external data is used, document source, retrieval date, and how it joins to canonical data._

---

## Data Quality Notes

- [ ] Confirmed no NULL values in key columns
- [ ] Confirmed no duplicate `block_id` values
- [ ] Confirmed time window has expected bar count
- [ ] Confirmed canonical release matches expected schema

---

## Query for Input Extraction

```sql
-- Replace placeholders with actual canonical object names
-- Query hash: [sha256:...]

SELECT
    f.block_id,
    f.ts,
    f.instrument,
    -- feature columns
    o.fwd_ret_3,
    o.mfe_3,
    o.mae_3
FROM {{CANONICAL_FEATURE_VIEW}} f
JOIN {{CANONICAL_OUTCOME_VIEW}} o USING (block_id)
WHERE f.ts >= '{{WINDOW_START}}'
  AND f.ts < '{{WINDOW_END}}'
  AND f.instrument IN ({{INSTRUMENTS}})
ORDER BY f.ts;
```
