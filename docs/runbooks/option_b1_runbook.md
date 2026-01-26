# OVC Option B.1 Runbook: L1 & L2 Feature Packs

> **Version**: v0.1
> **Created**: 2026-01-18
> **Status**: ACTIVE
> **Scope**: Running L1 (single-bar) and L2 (multi-bar) derived feature computation

---

## 1. Overview

Option B.1 implements replayable, deterministic derived features computed from B-layer facts.

| Tier | Scope | Window_spec | Script |
|------|-------|-------------|--------|
| **L1** | Single-bar OHLC primitives | None (no history) | `src/derived/compute_l1_v0_1.py` |
| **L2** | Multi-bar structure/context | Required per feature | `src/derived/compute_l2_v0_1.py` |

**Key Guarantees**:
- **Determinism**: Same inputs → same outputs, always
- **Idempotency**: Reruns produce identical results (upsert on block_id)
- **Replayability**: All provenance tracked via run_id, formula_hash, window_spec

---

## 2. Prerequisites

### 2.1 Environment Setup

```powershell
# Required environment variables
$env:NEON_DSN = "postgresql://neondb_owner:npg_3h4uoZdcJHsy@ep-misty-resonance-aby1fuoy-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"  # or DATABASE_URL

# Verify connection
python -c "import psycopg2; psycopg2.connect('$env:NEON_DSN')"
```

### 2.2 Database Schema Setup

Run the migration to create derived tables:

```powershell
# From repo root
psql $env:NEON_DSN -f sql/02_derived_c1_c2_tables_v0_1.sql
```

This creates:
- `derived.derived_runs_v0_1` — Run metadata for provenance
- `derived.ovc_l1_features_v0_1` — L1 single-bar features
- `derived.ovc_l2_features_v0_1` — L2 multi-bar features

---

## 3. Running L1 Feature Computation

### 3.1 Basic Usage

```powershell
# From repo root
cd c:\Users\Owner\projects\ovc-infra

# Compute L1 for all new blocks (skip already computed)
python src/derived/compute_l1_v0_1.py

# Dry run (preview without writing)
python src/derived/compute_l1_v0_1.py --dry-run

# Filter by symbol
python src/derived/compute_l1_v0_1.py --symbol GBPUSD

# Limit blocks (for testing)
python src/derived/compute_l1_v0_1.py --limit 100

# Recompute all (overwrite existing)
python src/derived/compute_l1_v0_1.py --recompute
```

### 3.2 L1 Output

**Table**: `derived.ovc_l1_features_v0_1`

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | TEXT PK | Foreign key to B-layer |
| `run_id` | UUID | References derived_runs_v0_1 |
| `computed_at` | TIMESTAMPTZ | Computation timestamp |
| `formula_hash` | TEXT | MD5 of L1 formula definition |
| `range` | DOUBLE | h - l |
| `body` | DOUBLE | abs(c - o) |
| `direction` | INT | sign(c - o): 1, -1, 0 |
| `ret` | DOUBLE | (c - o) / o |
| `logret` | DOUBLE | ln(c / o) |
| `body_ratio` | DOUBLE | body / range |
| `close_pos` | DOUBLE | (c - l) / range |
| `upper_wick` | DOUBLE | h - max(o, c) |
| `lower_wick` | DOUBLE | min(o, c) - l |
| `clv` | DOUBLE | Close location value |

### 3.3 L1 Features (per c_layer_boundary_spec_v0.1.md)

All L1 features use **only** current block's {o, h, l, c}. No lookback.

---

## 4. Running L2 Feature Computation

### 4.1 Basic Usage

```powershell
# Compute L2 for all new blocks (requires L1 to exist)
python src/derived/compute_l2_v0_1.py

# Dry run
python src/derived/compute_l2_v0_1.py --dry-run

# Custom rd_len parameter (default: 12)
python src/derived/compute_l2_v0_1.py --rd-len 24

# Filter and limit
python src/derived/compute_l2_v0_1.py --symbol GBPUSD --limit 100

# Recompute all
python src/derived/compute_l2_v0_1.py --recompute
```

### 4.2 L2 Output

**Table**: `derived.ovc_l2_features_v0_1`

| Column | Type | Window_spec | Description |
|--------|------|-------------|-------------|
| `block_id` | TEXT PK | — | Foreign key to B-layer |
| `run_id` | UUID | — | References derived_runs_v0_1 |
| `window_spec` | TEXT | — | Aggregated window specs |
| `gap` | DOUBLE | N=1 | o - prev_c |
| `took_prev_high` | BOOL | N=1 | h > prev_h |
| `took_prev_low` | BOOL | N=1 | l < prev_l |
| `sess_high` | DOUBLE | session=date_ny | Running max(h) in session |
| `sess_low` | DOUBLE | session=date_ny | Running min(l) in session |
| `dist_sess_high` | DOUBLE | session=date_ny | sess_high - c |
| `dist_sess_low` | DOUBLE | session=date_ny | c - sess_low |
| `roll_avg_range_12` | DOUBLE | N=12 | avg(range) over 12 blocks |
| `roll_std_logret_12` | DOUBLE | N=12 | stddev(logret) over 12 |
| `range_z_12` | DOUBLE | N=12 | (range - avg) / std |
| `hh_12` | BOOL | N=12 | h > max(h[-12:-1]) |
| `ll_12` | BOOL | N=12 | l < min(l[-12:-1]) |
| `rd_hi` | DOUBLE | param=rd_len | highest(h, rd_len) |
| `rd_lo` | DOUBLE | param=rd_len | lowest(l, rd_len) |
| `rd_mid` | DOUBLE | param=rd_len | (rd_hi + rd_lo) / 2 |

### 4.3 Dependency Order

**L2 depends on L1**. Always run L1 first:

```powershell
# Correct order
python src/derived/compute_l1_v0_1.py
python src/derived/compute_l2_v0_1.py
```

---

## 5. Provenance Tracking

### 5.1 Run ID Generation

Each compute run generates a unique UUID v4:

```python
import uuid
run_id = uuid.uuid4()
```

The run_id is recorded in:
- `derived.derived_runs_v0_1` (master record)
- Each feature row in L1/L2 tables (foreign key)

### 5.2 Formula Hash Computation

Formula hash is the MD5 of the literal formula definition string:

```python
import hashlib

C1_FORMULA_DEFINITION = """
C1_FEATURES_V0.1:
range = h - l
body = abs(c - o)
...
"""

formula_hash = hashlib.md5(C1_FORMULA_DEFINITION.strip().encode()).hexdigest()
```

For L2, the hash includes parameters:

```python
formula_hash = hashlib.md5(f"{C2_FORMULA_DEFINITION}\nrd_len={rd_len}".encode()).hexdigest()
```

**Rule**: Any change to the formula definition or parameters MUST result in a new hash.

### 5.3 Querying Run History

```sql
-- Recent runs
SELECT run_id, run_type, version, formula_hash, block_count, status, started_at
FROM derived.derived_runs_v0_1
ORDER BY started_at DESC
LIMIT 10;

-- Blocks computed in a specific run
SELECT block_id, computed_at
FROM derived.ovc_l1_features_v0_1
WHERE run_id = 'your-run-id-here';
```

---

## 6. Testing

### 6.1 Run Unit Tests

```powershell
# From repo root
pytest tests/test_derived_features.py -v
```

### 6.2 Test Coverage

| Test Class | Coverage |
|------------|----------|
| `TestC1Determinism` | Same inputs → same outputs |
| `TestC1Correctness` | Formula accuracy |
| `TestC1FormulaHash` | Hash stability |
| `TestC2WindowSpec` | All features have window_spec |
| `TestC2Determinism` | Multi-bar determinism |
| `TestC2Correctness` | L2 formula accuracy |

### 6.3 Manual Verification

```sql
-- Verify L1 computed correctly
SELECT 
    b.block_id, b.o, b.h, b.l, b.c,
    c1.range, c1.body, c1.direction
FROM ovc.ovc_blocks_v01_1_min b
JOIN derived.ovc_l1_features_v0_1 c1 ON b.block_id = c1.block_id
LIMIT 5;

-- Verify L2 with context
SELECT 
    c2.block_id, c2.gap, c2.sess_high, c2.roll_avg_range_12, c2.rd_hi
FROM derived.ovc_l2_features_v0_1 c2
LIMIT 5;
```

---

## 7. Idempotency Verification

Reruns should produce identical results:

```powershell
# First run
python src/derived/compute_l1_v0_1.py --recompute

# Second run (should produce same feature values)
python src/derived/compute_l1_v0_1.py --recompute

# Verify no changes
psql $env:NEON_DSN -c "
SELECT COUNT(*) FROM derived.ovc_l1_features_v0_1;
"
```

The `ON CONFLICT DO UPDATE` ensures:
- No duplicates created
- Values overwritten with identical values
- `computed_at` timestamp updated (only metadata change)

---

## 8. Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Missing NEON_DSN" | Env var not set | `$env:NEON_DSN = '...'` |
| "relation does not exist" | Schema not created | Run `sql/02_derived_c1_c2_tables_v0_1.sql` |
| L2 produces NULL values | Insufficient history | Need 12+ blocks for N=12 features |
| Different formula_hash | Formula definition changed | Version bump required |

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-01-18 | Initial L1/L2 feature packs |

---

*Runbook generated per docs/c_layer_boundary_spec_v0.1.md*
