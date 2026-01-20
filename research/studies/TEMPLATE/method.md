# Study Method

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Overview

_Brief description of the analytical approach (2-3 sentences)._

---

## Transformations

### Step 1: [Name]

**Purpose:** [What this step accomplishes]

**Input:** [Source table/CTE]

**Output:** [Resulting columns or structure]

```sql
-- Example transformation
WITH step_1 AS (
    SELECT
        block_id,
        ts,
        instrument,
        [derived_column] AS [name]
    FROM {{INPUT}}
    WHERE [conditions]
)
```

### Step 2: [Name]

**Purpose:** [What this step accomplishes]

**Input:** [Source from Step 1]

**Output:** [Resulting columns or structure]

```sql
-- Example transformation
```

---

## Statistical Methods

### Primary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| [e.g., Pearson correlation] | [e.g., Measure linear relationship] | [e.g., `corr(x, y)`] |
| [e.g., Distribution fitting] | [e.g., Characterize score distribution] | [e.g., histogram + KDE] |

### Secondary Analysis

| Method | Purpose | Implementation |
|--------|---------|----------------|
| [e.g., Conditional means] | [e.g., Score performance by regime] | [e.g., `GROUP BY regime`] |

---

## Scoring Definition (If Applicable)

_If this study produces a score, define it precisely._

**Score Name:** `[score_name]`

**Formula:**

```
score = f(feature_1, feature_2, ..., feature_n)
```

**Parameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| [param_1] | [value] | [why] |
| [param_2] | [value] | [why] |

**Output Schema:**

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | text | Primary key |
| `score_value` | numeric | Computed score |
| `score_percentile` | numeric | Score percentile (optional) |

---

## NOT Included in Method

- ❌ Entry/exit rule definitions
- ❌ Position sizing logic
- ❌ PnL optimization
- ❌ Parameter search for trading performance

---

## Reproducibility

### Environment

| Component | Version/Value |
|-----------|---------------|
| Canonical release | `ovc-v0.1-spine` |
| PostgreSQL | [version] |
| Python (if used) | [version] |
| Key libraries | [list] |

### Random Seeds

| Purpose | Seed Value |
|---------|------------|
| [e.g., Bootstrap sampling] | [value or N/A] |

### Query Hash

```
sha256:[hash of primary analysis query]
```

---

## Validation Checks

- [ ] Method produces identical results on re-run
- [ ] No look-ahead bias in transformations
- [ ] All parameters explicitly documented
- [ ] Category error checklist passed
