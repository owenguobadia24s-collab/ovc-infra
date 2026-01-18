# OVC Threshold Registry Runbook (v0.1)

## Overview

The Threshold Registry provides deterministic, versioned configuration management for C3+ derived layers. It ensures that threshold packs are:

- **Immutable**: Once created, a `(pack_id, pack_version)` never changes.
- **Deterministic**: Same `config_json` always produces the same `config_hash`.
- **Auditable**: All changes are tracked with timestamps and provenance.
- **Replay-certifiable**: Any computation can be verified by replaying with the same pack version/hash.

## Schema

The registry uses the `ovc_cfg` schema with two tables:

| Table | Purpose |
|-------|---------|
| `ovc_cfg.threshold_pack` | Immutable versioned configs (append-only) |
| `ovc_cfg.threshold_pack_active` | Mutable pointers to active versions |

### Scope Hierarchy

Packs support three scope levels for hierarchical overrides:

| Scope | Requirements | Use Case |
|-------|--------------|----------|
| `GLOBAL` | `symbol=NULL`, `timeframe=NULL` | Default thresholds for all |
| `SYMBOL` | `symbol` required, `timeframe=NULL` | Symbol-specific overrides |
| `SYMBOL_TF` | Both `symbol` and `timeframe` required | Symbol+timeframe specific |

## Prerequisites

```powershell
# Ensure environment is set
$env:NEON_DSN = "postgresql://..."
# or
$env:DATABASE_URL = "postgresql://..."
```

## Step 1: Apply Migration

Run the SQL migration to create the `ovc_cfg` schema and tables:

```powershell
# From repo root
psql $env:NEON_DSN -f sql/04_threshold_registry_v0_1.sql
```

Expected output:
```
NOTICE:  Threshold registry schema (ovc_cfg) created successfully
```

Verify tables exist:
```powershell
psql $env:NEON_DSN -c "\dt ovc_cfg.*"
```

## Step 2: Create a Threshold Pack

Create a new pack in DRAFT status:

### Option A: Inline JSON

```powershell
python -m src.config.threshold_registry_cli create `
  --pack-id c3_reversal_thresholds `
  --version 1 `
  --scope GLOBAL `
  --config '{\"min_body_bp\": 5, \"max_wick_ratio_bp\": 250, \"lookback\": 20}'
```

### Option B: From Config File

```powershell
python -m src.config.threshold_registry_cli create `
  --pack-id c3_reversal_thresholds `
  --version 1 `
  --scope GLOBAL `
  --config-file configs/threshold_packs/c3_example_pack_v1.json
```

Example output:
```json
{
  "success": true,
  "action": "create",
  "pack": {
    "pack_id": "c3_reversal_thresholds",
    "pack_version": 1,
    "scope": "GLOBAL",
    "symbol": null,
    "timeframe": null,
    "config_json": {"lookback": 20, "max_wick_ratio_bp": 250, "min_body_bp": 5},
    "config_hash": "abc123...",
    "status": "DRAFT",
    "created_at": "2026-01-18T12:00:00+00:00"
  }
}
```

### Create Symbol-Specific Override

```powershell
python -m src.config.threshold_registry_cli create `
  --pack-id c3_reversal_thresholds `
  --version 1 `
  --scope SYMBOL `
  --symbol GBPUSD `
  --config '{\"min_body_bp\": 8, \"max_wick_ratio_bp\": 200, \"lookback\": 25}'
```

## Step 3: Activate a Pack

Activate a pack version for a specific selector:

```powershell
python -m src.config.threshold_registry_cli activate `
  --pack-id c3_reversal_thresholds `
  --version 1 `
  --scope GLOBAL
```

### With Hash Verification (Recommended)

```powershell
python -m src.config.threshold_registry_cli activate `
  --pack-id c3_reversal_thresholds `
  --version 1 `
  --scope GLOBAL `
  --expected-hash "abc123def456..."
```

## Step 4: Show Active Pack

### Show by Version

```powershell
python -m src.config.threshold_registry_cli show `
  --pack-id c3_reversal_thresholds `
  --version 1
```

### Show Active for Selector

```powershell
python -m src.config.threshold_registry_cli show `
  --pack-id c3_reversal_thresholds `
  --scope GLOBAL `
  --active
```

Example output:
```json
{
  "pack_id": "c3_reversal_thresholds",
  "pack_version": 1,
  "config_hash": "abc123...",
  "config_json": {"lookback": 20, "max_wick_ratio_bp": 250, "min_body_bp": 5},
  "scope": "GLOBAL",
  "symbol": null,
  "timeframe": null,
  "status": "ACTIVE"
}
```

## Step 5: List Packs

```powershell
# List all packs
python -m src.config.threshold_registry_cli list

# Filter by pack_id
python -m src.config.threshold_registry_cli list --pack-id c3_reversal_thresholds

# Filter by status
python -m src.config.threshold_registry_cli list --status ACTIVE

# Filter by scope
python -m src.config.threshold_registry_cli list --scope GLOBAL
```

## Step 6: Validate Registry Integrity

Check for orphaned pointers and hash mismatches:

```powershell
python -m src.config.threshold_registry_cli validate
```

Expected output (healthy):
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "stats": {
    "packs_by_status": {"DRAFT": 2, "ACTIVE": 1},
    "active_pointers": 1
  }
}
```

## Step 7: Run Tests

```powershell
python -m pytest tests/test_threshold_registry.py -v
```

## C3 Integration

When implementing C3 tagging, reference the active pack metadata:

```python
from src.config.threshold_registry_v0_1 import get_active_pack

# Resolve active pack
pack = get_active_pack(
    pack_id="c3_reversal_thresholds",
    scope="GLOBAL",
)

# Extract provenance for storage
provenance = {
    "pack_id": pack["pack_id"],
    "pack_version": pack["pack_version"],
    "config_hash": pack["config_hash"],
}

# Apply thresholds
thresholds = pack["config_json"]
min_body_bp = thresholds["min_body_bp"]
# ... apply logic ...

# Store tags with provenance (enables replay certification)
insert_c3_tag(
    block_id=block_id,
    tag="reversal",
    **provenance,  # pack_id, pack_version, config_hash
)
```

### Replay Certification

To verify a C3 computation was deterministic:

1. Retrieve stored `pack_id`, `pack_version`, `config_hash` from tag row.
2. Load the exact pack version: `get_pack(pack_id, version)`.
3. Verify hash matches: `stored_hash == pack["config_hash"]`.
4. Recompute with same inputs + same config.
5. Compare outputs.

## Versioning Workflow

### Creating a New Version

```powershell
# Create v2 with updated thresholds
python -m src.config.threshold_registry_cli create `
  --pack-id c3_reversal_thresholds `
  --version 2 `
  --scope GLOBAL `
  --config '{\"min_body_bp\": 7, \"max_wick_ratio_bp\": 300, \"lookback\": 20}'

# Activate v2 (v1 remains for historical replay)
python -m src.config.threshold_registry_cli activate `
  --pack-id c3_reversal_thresholds `
  --version 2 `
  --scope GLOBAL
```

### Key Rules

1. **Never modify existing packs** - create a new version instead.
2. **Config hash is immutable** - same version always has same hash.
3. **Store provenance with outputs** - enables replay verification.
4. **Use expected_hash on activate** - prevents accidental wrong version.

## Compute Hash Without DB

To preview the canonical hash before creating a pack:

```powershell
python -m src.config.threshold_registry_cli hash `
  --config-file configs/threshold_packs/c3_example_pack_v1.json
```

Output:
```json
{
  "canonical": "{\"lookback\":20,\"max_wick_ratio_bp\":250,...}",
  "hash": "abc123def456...",
  "original": {"min_body_bp": 5, ...}
}
```

## Troubleshooting

### "No active pack found"

```powershell
# Check if pack exists
python -m src.config.threshold_registry_cli list --pack-id YOUR_PACK_ID

# Activate if it exists but isn't active
python -m src.config.threshold_registry_cli activate ...
```

### "NEON_DSN or DATABASE_URL not set"

```powershell
$env:NEON_DSN = "postgresql://user:pass@host/db?sslmode=require"
```

### Hash Mismatch on Activate

This means the pack's stored config_hash doesn't match your expected_hash:
- Verify you're activating the correct version.
- Use `show --version N` to inspect the actual hash.

## Files Reference

| File | Purpose |
|------|---------|
| `sql/04_threshold_registry_v0_1.sql` | Schema migration |
| `src/config/threshold_registry_v0_1.py` | Registry module |
| `src/config/threshold_registry_cli.py` | CLI interface |
| `tests/test_threshold_registry.py` | Test suite |
| `configs/threshold_packs/` | Sample pack configs |
| `src/derived/compute_c3_stub_v0_1.py` | Integration stub |

## CLI Reference

```
threshold_registry_cli <command> [options]

Commands:
  create    Create a new threshold pack (DRAFT status)
  activate  Activate a pack version for a selector
  show      Show pack details (by version or active)
  list      List packs with optional filters
  validate  Check registry integrity
  hash      Compute canonical hash (no DB)

Global Options:
  --pack-id       Pack identifier
  --version       Version number
  --scope         GLOBAL | SYMBOL | SYMBOL_TF
  --symbol        Symbol (for SYMBOL/SYMBOL_TF)
  --timeframe     Timeframe (for SYMBOL_TF)
  --config        Inline JSON string
  --config-file   Path to JSON file
```

---

## First Real C3 Tag: c3_regime_trend

The first fully implemented C3 classifier is **c3_regime_trend**, which classifies market regime as `TREND` or `NON_TREND` based on C1/C2 features.

### Classification Logic

The classifier evaluates a lookback window and returns `TREND` if ALL conditions are met:

1. **Average range** ≥ `min_range_bp` (basis points)
2. **Direction ratio** ≥ `min_direction_ratio_bp`
   - `direction_ratio = abs(sum(direction)) / count * 1000`
3. **HH/LL count** ≥ `min_hh_ll_count`
   - Count of blocks where `hh_12 = true` OR `ll_12 = true`

Otherwise, returns `NON_TREND`.

### Threshold Pack Config

Located at `configs/threshold_packs/c3_regime_trend_v1.json`:

```json
{
  "lookback": 12,
  "min_range_bp": 30,
  "min_direction_ratio_bp": 600,
  "min_hh_ll_count": 3
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `lookback` | int | Number of preceding blocks to analyze |
| `min_range_bp` | int | Minimum average range (basis points) |
| `min_direction_ratio_bp` | int | Min direction ratio (60% = 600bp) |
| `min_hh_ll_count` | int | Min count of HH or LL signals |

### End-to-End Setup

```powershell
# 1. Apply C3 table migration
psql $env:NEON_DSN -f sql/05_c3_regime_trend_v0_1.sql

# 2. Create threshold pack in registry
python -m src.config.threshold_registry_cli create `
  --pack-id c3_regime_trend `
  --version 1 `
  --scope GLOBAL `
  --config-file configs/threshold_packs/c3_regime_trend_v1.json

# 3. Activate the pack
python -m src.config.threshold_registry_cli activate `
  --pack-id c3_regime_trend `
  --version 1 `
  --scope GLOBAL

# 4. Run C3 compute for a symbol
python src/derived/compute_c3_regime_trend_v0_1.py `
  --symbol GBPUSD `
  --threshold-pack c3_regime_trend `
  --scope GLOBAL

# 5. Validate with B.2 validator (includes C3 checks)
python src/validate/validate_derived_range_v0_1.py `
  --symbol GBPUSD `
  --start-date 2026-01-13 `
  --end-date 2026-01-17 `
  --validate-c3
```

### C3 Table Schema

Table: `derived.ovc_c3_regime_trend_v0_1`

| Column | Type | Description |
|--------|------|-------------|
| `block_id` | TEXT | FK to B-layer |
| `symbol` | TEXT | Trading symbol |
| `ts` | TIMESTAMPTZ | Block timestamp |
| `c3_regime_trend` | TEXT | `TREND` or `NON_TREND` |
| `threshold_pack_id` | TEXT | Pack ID from registry |
| `threshold_pack_version` | INT | Pack version used |
| `threshold_pack_hash` | TEXT | SHA256 hash (64 hex) |
| `run_id` | UUID | Compute run ID |
| `created_at` | TIMESTAMPTZ | Row creation time |

Primary Key: `(symbol, ts)`

### Validation Checks

The B.2 validator (`--validate-c3` flag) performs these C3-specific checks:

1. **Table existence**: Verify C3 table exists
2. **Provenance validation**: No NULL `threshold_pack_*` columns
3. **Registry integrity**: All referenced packs exist in `ovc_cfg.threshold_pack`
4. **Hash verification**: Stored hash matches registry hash
5. **Value validation**: Only `TREND` or `NON_TREND` values
6. **Version warnings**: Flag if using non-active pack versions

### Testing

```powershell
# Run unit tests
python -m pytest tests/test_c3_regime_trend.py -v

# Run with coverage
python -m pytest tests/test_c3_regime_trend.py --cov=src/derived --cov-report=term-missing
```

### Files Reference

| File | Purpose |
|------|---------|
| `sql/05_c3_regime_trend_v0_1.sql` | C3 table migration |
| `src/derived/compute_c3_regime_trend_v0_1.py` | C3 compute script |
| `configs/threshold_packs/c3_regime_trend_v1.json` | Default threshold pack |
| `tests/test_c3_regime_trend.py` | Test suite |
| `src/validate/validate_derived_range_v0_1.py` | Validator with C3 support |
