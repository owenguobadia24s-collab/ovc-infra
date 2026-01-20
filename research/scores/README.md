# Scores Layer

> ⚠️ **NON-CANONICAL** — Scores are downstream research artifacts only.  
> **NO FEEDBACK INTO CANONICAL** — Scores do not modify or redefine Option B/C metrics.

## Purpose

Scores are **descriptive compressions** of canonical data. They summarize multiple features into a single numeric value for analytical convenience.

**Scores are NOT:**
- Trading signals
- Entry/exit triggers
- Predictive models with thresholds
- Replacements for canonical metrics

## Requirements

Every score file **MUST**:

### 1. Declare Canonical Release

```sql
-- canonical_release: ovc-v0.1-spine
```

### 2. Declare Required Inputs

```sql
-- inputs:
--   - derived.ovc_block_features_v0_1 (block_id, ts, instrument, ...)
--   - derived.ovc_outcomes_v0_1 (block_id, fwd_ret_3, ...)
```

### 3. Produce Deterministic Output Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `ts` | timestamptz | Yes | Block timestamp |
| `block_id` | text | Yes | Block identifier |
| `instrument` | text | Yes | Trading pair |
| `score_name` | text | Yes | Name of this score |
| `score_value` | numeric | Yes | Computed score value |
| `metadata_json` | jsonb | No | Additional context |

### 4. Use CTE Structure

Scores must follow the standard CTE pattern:

```sql
WITH
base AS (...),
features AS (...),
joins_outcomes AS (...),
score_calc AS (...),
final AS (...)
SELECT * FROM final;
```

## Forbidden in Scores

❌ Thresholding for entries/exits (e.g., `IF score > 0.7 THEN buy`)  
❌ Position sizing logic  
❌ References to PnL, equity, or account state  
❌ Optimization for trading performance  
❌ Mutations to canonical schemas  

## Naming Convention

```
score_<name>_v<major>_<minor>.sql
```

- `name`: lowercase, underscore-separated descriptor
- `major`: increment for breaking changes (output schema change)
- `minor`: increment for non-breaking changes (parameter tweaks)

**Examples:**
- `score_trend_strength_v1_0.sql`
- `score_volatility_regime_v2_1.sql`
- `score_momentum_composite_v1_3.sql`

## Usage

Scores are intended for:

1. **Exploratory analysis** — Understanding data distributions
2. **Study inputs** — Conditioning analysis on score buckets
3. **Visualization** — Charting score evolution over time
4. **Documentation** — Describing market regimes

Scores are **NOT** intended for:

1. Live trading decisions
2. Backtesting engines
3. Strategy optimization

## Versioning

If a score's output schema changes (columns added/removed/renamed), increment the **major** version.

If parameters change but output schema is stable, increment the **minor** version.

Old versions should be preserved for reproducibility; do not delete prior versions.

## Template

See [score_template.sql](score_template.sql) for the standard skeleton.
