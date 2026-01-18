# OVC Option B.2 Runbook: Derived Feature Validation

> **Version**: v0.1
> **Created**: 2026-01-18
> **Status**: ACTIVE
> **Scope**: Validating C1/C2 derived feature packs against B-layer facts

---

## 1. Overview

Option B.2 implements validation tooling for derived feature packs (C1/C2), ensuring data integrity and optionally comparing against TradingView reference outputs.

| Check | Purpose | Failure Mode |
|-------|---------|--------------|
| **Coverage Parity** | count(B) == count(C1) == count(C2) | FAIL or WARN |
| **Key Uniqueness** | No duplicate block_id in C1/C2 | FAIL |
| **Null/Invalid Checks** | No NaN/Inf, deterministic nulls | FAIL |
| **Window_spec Enforcement** | C2 rows have required specs | FAIL |
| **Determinism Quickcheck** | Recompute sample matches stored | FAIL |
| **TV Comparison** (opt) | Match against TradingView reference | WARN |

**Key Guarantees**:
- Deterministic run IDs for reproducibility
- Artifact generation (JSON, Markdown, CSV)
- QA schema storage for historical tracking

---

## 2. Prerequisites

### 2.1 Environment Setup

```powershell
# Required environment variables
$env:NEON_DSN = "postgresql://..."  # or DATABASE_URL

# Verify connection
python -c "import psycopg2; psycopg2.connect('$env:NEON_DSN')"
```

### 2.2 Database Schema Setup

Run the QA schema migration:

```powershell
# From repo root
psql $env:NEON_DSN -f sql/03_qa_derived_validation_v0_1.sql
```

This creates:
- `ovc_qa.derived_validation_run` — Validation run metadata

### 2.3 Ensure C1/C2 Features Computed

Validation requires C1/C2 features to exist. Run compute scripts first if needed:

```powershell
python src/derived/compute_c1_v0_1.py
python src/derived/compute_c2_v0_1.py
```

---

## 3. Running Validation

### 3.1 Basic Usage

```powershell
# From repo root
cd c:\Users\Owner\projects\ovc-infra

# Validate a date range
python src/validate/validate_derived_range_v0_1.py \
    --symbol GBPUSD \
    --start-date 2026-01-13 \
    --end-date 2026-01-17

# With TradingView comparison (if available)
python src/validate/validate_derived_range_v0_1.py \
    --symbol GBPUSD \
    --start-date 2026-01-13 \
    --end-date 2026-01-17 \
    --compare-tv
```

### 3.2 Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--symbol` | GBPUSD | Symbol to validate |
| `--start-date` | Required | Start date (NY, YYYY-MM-DD) |
| `--end-date` | Required | End date (NY, inclusive) |
| `--mode` | fail | Behavior for issues: `fail` or `skip` |
| `--compare-tv` | Off | Enable TV reference comparison |
| `--sample-size` | 50 | Blocks to sample for determinism |
| `--out` | artifacts | Output directory |
| `--run-id` | Auto | Override deterministic run ID |

### 3.3 Skip Mode vs Fail Mode

**Fail mode** (default): Missing features or mismatches cause validation to FAIL.

```powershell
# Strict validation - any issue is failure
python src/validate/validate_derived_range_v0_1.py \
    --mode fail --start-date 2026-01-13 --end-date 2026-01-17
```

**Skip mode**: Missing features logged as warnings, validation can PASS_WITH_WARNINGS.

```powershell
# Lenient validation - issues are warnings
python src/validate/validate_derived_range_v0_1.py \
    --mode skip --start-date 2026-01-13 --end-date 2026-01-17
```

---

## 4. Validation Checks

### 4.1 Coverage Parity

Verifies that the number of B-layer blocks equals C1 and C2 row counts.

```sql
-- What validation checks
SELECT COUNT(*) FROM ovc.ovc_blocks_v01_1_min WHERE sym = ? AND date_ny BETWEEN ? AND ?;
SELECT COUNT(*) FROM derived.ovc_c1_features_v0_1 c1 JOIN ovc.ovc_blocks_v01_1_min b ON c1.block_id = b.block_id WHERE b.sym = ? AND b.date_ny BETWEEN ? AND ?;
SELECT COUNT(*) FROM derived.ovc_c2_features_v0_1 c2 JOIN ovc.ovc_blocks_v01_1_min b ON c2.block_id = b.block_id WHERE b.sym = ? AND b.date_ny BETWEEN ? AND ?;
```

**Expected**: All three counts equal. Mismatch indicates missing feature computation.

### 4.2 Key Uniqueness

Checks that `block_id` is unique in C1 and C2 tables (no duplicates).

**Expected**: 0 duplicates. Duplicates indicate data corruption or insert bug.

### 4.3 Null/Invalid Checks

Calculates null rates for each feature column and checks for NaN/Inf values.

**Expected null patterns**:
- `ret`, `logret`: NULL when open = 0 (expected)
- `body_ratio`, `close_pos`, `clv`: NULL when range = 0 (expected)
- C2 lookback features: NULL for insufficient history (expected)

**Unexpected**: NaN or Inf values should never occur.

### 4.4 Window_spec Enforcement

Validates that C2 `window_spec` column:
1. Is never NULL
2. Contains all required components: `N=1`, `N=12`, `session=date_ny`, `rd_len=`

**Expected**: All C2 rows have complete window_spec.

### 4.5 Determinism Quickcheck

Samples N random blocks, recomputes C1 values, and compares to stored values.

```python
# Recompute and compare
stored_range = ...  # from DB
computed_range = h - l  # from B-layer OHLC
assert abs(stored_range - computed_range) < 1e-9
```

**Expected**: Zero mismatches. Any mismatch indicates non-determinism.

---

## 5. TradingView Reference Comparison

### 5.1 Enabling TV Comparison

```powershell
python src/validate/validate_derived_range_v0_1.py \
    --compare-tv \
    --start-date 2026-01-13 --end-date 2026-01-17
```

### 5.2 How It Works

Compares C1 derived values against TV-sourced values in B-layer:

| C1 Field | TV Field | Join Key |
|----------|----------|----------|
| `range` | `rng` | block_id |
| `body` | `body` | block_id |
| `direction` | `dir` | block_id |
| `ret` | `ret` | block_id |

### 5.3 Diff Metrics

| Metric | Description |
|--------|-------------|
| Mean Abs Diff | Average absolute difference |
| Max Diff | Largest single difference |
| Mismatch Rate | % of rows with diff > 1e-6 |

**Expected**: High agreement (mismatch rate < 1%) for TV-sourced blocks.

---

## 6. Artifacts

### 6.1 Output Structure

```
artifacts/
└── derived_validation/
    ├── LATEST                          # Pointer to latest run
    └── {run_id}/
        ├── meta.json                   # Run metadata
        ├── derived_validation_report.json   # Machine-readable
        ├── derived_validation_report.md     # Human-readable
        └── derived_validation_diffs.csv     # TV diffs (optional)
```

### 6.2 Report JSON Schema

```json
{
  "run_id": "uuid",
  "version": "v0.1",
  "symbol": "GBPUSD",
  "start_date": "2026-01-13",
  "end_date": "2026-01-17",
  "mode": "fail",
  "b_block_count": 60,
  "c1_row_count": 60,
  "c2_row_count": 60,
  "coverage_parity": true,
  "c1_duplicates": 0,
  "c2_duplicates": 0,
  "c1_null_rates": {"ret": 0.0, "logret": 0.0, ...},
  "c2_null_rates": {"gap": 0.1, ...},
  "c2_window_spec_valid": true,
  "determinism_sample_size": 50,
  "determinism_mismatches": 0,
  "status": "PASS",
  "errors": [],
  "warnings": []
}
```

### 6.3 Reading Latest Report

```powershell
# Get latest run ID
$latestRunId = Get-Content artifacts/derived_validation/LATEST

# Read report
Get-Content "artifacts/derived_validation/$latestRunId/derived_validation_report.md"
```

---

## 7. QA Schema Storage

### 7.1 Table: ovc_qa.derived_validation_run

| Column | Type | Description |
|--------|------|-------------|
| `run_id` | UUID PK | Deterministic run ID |
| `created_at` | TIMESTAMPTZ | Validation timestamp |
| `symbol` | TEXT | Validated symbol |
| `start_date` | DATE | Start of range |
| `end_date` | DATE | End of range |
| `b_block_count` | INT | B-layer blocks in range |
| `c1_row_count` | INT | C1 rows in range |
| `c2_row_count` | INT | C2 rows in range |
| `coverage_parity` | BOOL | B == C1 == C2 |
| `status` | TEXT | PASS, FAIL, PASS_WITH_WARNINGS |
| `errors` | JSONB | Error messages |
| `warnings` | JSONB | Warning messages |

### 7.2 Querying Validation History

```sql
-- Recent validation runs
SELECT run_id, symbol, start_date, end_date, status, created_at
FROM ovc_qa.derived_validation_run
ORDER BY created_at DESC
LIMIT 10;

-- Failed validations
SELECT * FROM ovc_qa.derived_validation_run
WHERE status = 'FAIL'
ORDER BY created_at DESC;

-- Coverage issues
SELECT * FROM ovc_qa.derived_validation_run
WHERE NOT coverage_parity;
```

---

## 8. Integration with CI/CD

### 8.1 GitHub Actions Workflow

Add validation step after compute in `.github/workflows/backfill_then_validate.yml`:

```yaml
- name: Compute C1/C2 features
  run: |
    python src/derived/compute_c1_v0_1.py --symbol GBPUSD
    python src/derived/compute_c2_v0_1.py --symbol GBPUSD

- name: Validate derived features
  run: |
    python src/validate/validate_derived_range_v0_1.py \
      --symbol GBPUSD \
      --start-date ${{ env.START_DATE }} \
      --end-date ${{ env.END_DATE }} \
      --mode fail
```

### 8.2 Full Pipeline Order

```
1. Backfill OANDA → B-layer
2. Validate B-layer (validate_range.py)
3. Compute C1 features
4. Compute C2 features
5. Validate C1/C2 (validate_derived_range_v0_1.py)
```

---

## 9. Testing

### 9.1 Run Unit Tests

```powershell
# From repo root
pytest tests/test_validate_derived.py -v
```

### 9.2 Test Coverage

| Test Class | Coverage |
|------------|----------|
| `TestComputeC1Inline` | C1 recomputation logic |
| `TestValuesMatch` | Float comparison tolerance |
| `TestBuildRunId` | Deterministic run ID |
| `TestParseDate` | Date parsing |
| `TestValidationResult` | Result dataclass |
| `TestEdgeCases` | Zero/negative/small prices |

---

## 10. Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Missing NEON_DSN" | Env var not set | `$env:NEON_DSN = '...'` |
| "C1 table not found" | Migration not run | Run `sql/02_derived_c1_c2_tables_v0_1.sql` |
| Coverage mismatch | Compute not run | Run compute_c1 and compute_c2 |
| Determinism failures | Formula changed | Re-run compute with `--recompute` |
| TV not available | No TV-sourced blocks | Use `--mode skip` or omit `--compare-tv` |

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-01-18 | Initial derived validation |

---

*Runbook complements docs/option_b1_runbook.md*
