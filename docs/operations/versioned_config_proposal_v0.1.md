# Versioned Config Proposal (Doc Only)

> **Status**: PROPOSAL — requires approval before implementation
> **Purpose**: Define how threshold parameters and configs are versioned for C3 replay
> **Scope**: Threshold registry, version mechanism, replay metadata

---

## 1. Problem Statement

C3 metrics depend on threshold parameters (e.g., `th_move_OR`, `cp_hi`, `rd_width_th`) that are currently:
- Defined as Pine script inputs (user-configurable)
- Not persisted alongside computed metrics
- Not versioned or documented

This undermines the **replay guarantee**: the same formula with different thresholds produces different categorical outputs. Without parameter versioning, C3 metrics cannot be deterministically reproduced.

---

## 2. Configs Requiring Versioning

### 2.1 — State/Value Tag Thresholds

| Parameter | Used By | Type | Current Source |
|-----------|---------|------|----------------|
| `th_move_OR` | `state_tag` | float | Pine input |
| `th_move_RER` | `state_tag` | float | Pine input |
| `th_accept_SD` | `value_tag` | float | Pine input |
| `th_clv_extreme` | `state_tag` | float | Pine input |

### 2.2 — Candle Profile Thresholds

| Parameter | Used By | Type | Current Source |
|-----------|---------|------|----------------|
| `cp_hi` | `cp_tag` | float | Pine input |
| `cp_lo` | `cp_tag` | float | Pine input |
| `cp_wick_th` | `cp_tag` | float | Pine input |

### 2.3 — Range Detector Parameters

| Parameter | Used By | Type | Current Source |
|-----------|---------|------|----------------|
| `rd_len` | `rd_hi`, `rd_lo` | int | Pine input |
| `rd_width_th` | `rd_state` | float | Pine input |
| `rd_drift_th` | `rd_state` | float | Pine input |

### 2.4 — Trade Trigger Parameters

| Parameter | Used By | Type | Current Source |
|-----------|---------|------|----------------|
| `tt_min_score` | `tt` | int | Pine input |
| `tt_flip_weight` | `tt` | float | Pine input |
| `tt_sweep_weight` | `tt` | float | Pine input |

### 2.5 — Window Lengths

| Parameter | Used By | Type | Current Source |
|-----------|---------|------|----------------|
| `rm_len` | rolling mean | int | Hardcoded/Pine |
| `sd_len` | stddev | int | Hardcoded/Pine |
| `roll_n` | rolling stats | int | SQL: 12 |
| `kls_lookback` | KLS features | int | Pine input |
| `htf_resolution` | HTF features | string | Pine input |
| `bs_depth` | BlockStack | int | Pine input |

---

## 3. Proposed Storage Path

### 3.1 — Schema Location

```
derived.threshold_registry_v0_1
```

**Rationale**: Thresholds are part of the derived computation process, not canonical facts. They belong in the `derived` schema alongside formula definitions.

### 3.2 — Proposed Table Structure

```sql
-- Threshold registry for C3 replay
CREATE TABLE derived.threshold_registry (
    threshold_version   TEXT PRIMARY KEY,  -- e.g., 'th_v0.1.0'
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    description         TEXT,
    
    -- State/Value tag thresholds
    th_move_or          NUMERIC(6,4),
    th_move_rer         NUMERIC(6,4),
    th_accept_sd        NUMERIC(6,4),
    th_clv_extreme      NUMERIC(6,4),
    
    -- Candle profile thresholds
    cp_hi               NUMERIC(6,4),
    cp_lo               NUMERIC(6,4),
    cp_wick_th          NUMERIC(6,4),
    
    -- Range detector parameters
    rd_len              INTEGER,
    rd_width_th         NUMERIC(6,4),
    rd_drift_th         NUMERIC(6,4),
    
    -- Trade trigger parameters
    tt_min_score        INTEGER,
    tt_flip_weight      NUMERIC(6,4),
    tt_sweep_weight     NUMERIC(6,4),
    
    -- Window lengths
    rm_len              INTEGER,
    sd_len              INTEGER,
    roll_n              INTEGER,
    kls_lookback        INTEGER,
    htf_resolution      TEXT,
    bs_depth            INTEGER,
    
    -- Metadata
    param_hash          TEXT NOT NULL  -- Hash of all parameter values
);
```

### 3.3 — Alternative: JSON Column

```sql
CREATE TABLE derived.threshold_registry_json (
    threshold_version   TEXT PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    description         TEXT,
    params              JSONB NOT NULL,     -- All parameters as JSON
    param_hash          TEXT NOT NULL       -- Hash of params for validation
);
```

**Trade-off**: JSON is more flexible but harder to query/validate. Recommend typed columns for v0.1, migrate to JSON if parameter set grows.

---

## 4. Hash/Version Mechanism

### 4.1 — Version String Format

```
th_v<MAJOR>.<MINOR>.<PATCH>

Examples:
  th_v0.1.0  -- Initial threshold set
  th_v0.1.1  -- Patch: adjusted cp_hi
  th_v0.2.0  -- Minor: added new RD threshold
  th_v1.0.0  -- Major: restructured threshold model
```

### 4.2 — Parameter Hash Calculation

```python
import hashlib
import json

def compute_param_hash(params: dict) -> str:
    """
    Compute deterministic hash of parameter values.
    Keys must be sorted for consistency.
    """
    sorted_json = json.dumps(params, sort_keys=True, separators=(',', ':'))
    return hashlib.md5(sorted_json.encode()).hexdigest()
```

### 4.3 — Hash Validation Rule

For any derived metric row with `threshold_version`:

```sql
-- Validation query
SELECT 
    d.block_id,
    d.threshold_version,
    t.param_hash AS expected_hash,
    md5(t.params::text) AS computed_hash
FROM derived.ovc_c3_features_v0_1 d
JOIN derived.threshold_registry t ON d.threshold_version = t.threshold_version
WHERE t.param_hash != md5(t.params::text);
```

---

## 5. Required Metadata Per Computed Run

### 5.1 — C2 Run Metadata

```sql
-- Added to derived_runs table
run_id              UUID PRIMARY KEY
derived_version     TEXT            -- 'v0.1'
formula_hash        TEXT            -- MD5 of SQL/formula
window_spec         TEXT            -- 'N=12;session=date_ny'
computed_at         TIMESTAMPTZ
block_range_start   TEXT            -- First block_id processed
block_range_end     TEXT            -- Last block_id processed
row_count           INTEGER
```

### 5.2 — C3 Run Metadata (Extended)

```sql
-- Additional columns for C3 runs
threshold_version   TEXT REFERENCES derived.threshold_registry(threshold_version)
c2_dependency_hash  TEXT            -- Hash of C2 inputs used
```

### 5.3 — Full Provenance Record

For each C3 computed block, the following must be reconstructable:

| Field | Source | Purpose |
|-------|--------|---------|
| `block_id` | B-layer | Identity |
| `derived_version` | Run metadata | Formula version |
| `formula_hash` | Run metadata | Exact computation |
| `threshold_version` | Run metadata | Parameter snapshot |
| `window_spec` | Run metadata | Lookback specification |
| `c2_dependency_hash` | Run metadata | Input data hash |
| `computed_at` | Run metadata | Timestamp |

---

## 6. Replay Workflow

### 6.1 — Forward Computation (Production)

```
1. Load threshold_version from config (e.g., 'th_v0.1.0')
2. Fetch parameter values from threshold_registry
3. Compute C3 metrics using those parameters
4. Store results with threshold_version reference
```

### 6.2 — Replay Verification

```
1. Load block with C3 metrics
2. Extract threshold_version from metadata
3. Fetch original parameters from threshold_registry
4. Recompute C3 metrics using original parameters
5. Compare: if mismatch, flag as replay failure
```

### 6.3 — Parameter Change Protocol

```
1. Create new threshold_version (bump minor/patch)
2. Insert new row in threshold_registry
3. Update config to use new version
4. New computations use new version
5. Old blocks retain old threshold_version (immutable)
```

---

## 7. Integration Points

### 7.1 — Python Backfill Script

```python
# src/backfill_c3.py (pseudocode)

THRESHOLD_VERSION = "th_v0.1.0"

def load_thresholds(conn, version: str) -> dict:
    """Load threshold parameters from registry."""
    row = conn.execute(
        "SELECT * FROM derived.threshold_registry WHERE threshold_version = %s",
        [version]
    ).fetchone()
    return dict(row)

def compute_state_tag(block: dict, thresholds: dict) -> str:
    """Compute state_tag using versioned thresholds."""
    if block['or'] > thresholds['th_move_or']:
        return 'OB' if block['dir'] > 0 else 'OS'
    # ... rest of logic
```

### 7.2 — SQL View (If Inline Parameters)

```sql
-- Option: Inline parameters in view definition
CREATE OR REPLACE VIEW derived.ovc_c3_features_v0_1 AS
WITH params AS (
    SELECT * FROM derived.threshold_registry
    WHERE threshold_version = 'th_v0.1.0'
),
c2_data AS (
    SELECT * FROM derived.ovc_block_features_v0_1
)
SELECT
    c2.*,
    CASE 
        WHEN c2.or_ratio > p.th_move_or AND c2.direction > 0 THEN 'OB'
        WHEN c2.or_ratio > p.th_move_or AND c2.direction < 0 THEN 'OS'
        ELSE 'EQ'
    END AS state_tag,
    'th_v0.1.0' AS threshold_version
FROM c2_data c2
CROSS JOIN params p;
```

### 7.3 — Pine Script (Export for Validation)

```pine
// Export threshold values with block for validation
exp_th_move_or = str.tostring(th_move_OR)
exp_th_move_rer = str.tostring(th_move_RER)
// ... include in export payload
```

---

## 8. Open Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Should thresholds be per-symbol? | (a) Global; (b) Per-symbol | Start global, add symbol column if needed |
| 2 | How to handle threshold drift in Pine? | (a) Export with block; (b) Ignore Pine | Export with block for validation |
| 3 | Should old threshold versions be deletable? | (a) Never; (b) After retention period | Never delete, immutable history |
| 4 | Who can create new threshold versions? | (a) Admin only; (b) Any analyst | Admin only via PR review |

---

## 9. Implementation Checklist (Deferred)

> **NOTE**: This section is for reference after design approval. NO IMPLEMENTATION until approved.

- [ ] Create `derived.threshold_registry` table
- [ ] Insert initial `th_v0.1.0` row with documented values
- [ ] Add `threshold_version` column to C3 output tables
- [ ] Update Python scripts to load parameters from registry
- [ ] Add replay verification tests
- [ ] Document threshold change protocol in runbook

---

*Proposal Version: v0.1 | Status: DRAFT | Implementation: DEFERRED*
