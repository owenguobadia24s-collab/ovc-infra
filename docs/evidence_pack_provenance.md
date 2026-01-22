# Evidence Pack v0.2 Provenance & Citation

## Overview

Evidence Pack v0.2 outputs are now formalized as **research-grade, reproducible citation objects** with comprehensive provenance tracking and deterministic integrity verification.

## Key Features

### 1. Manifest with File Integrity

**File:** `manifest.json`

The manifest lists every file in the evidence pack (recursive) with:
- `relative_path`: POSIX-style path relative to pack root
- `sha256`: SHA-256 hash (hex) for file integrity verification
- `byte_size`: File size in bytes
- `row_count`: Number of data rows for CSV files (excluding header)

**Example:**
```json
{
  "files": [
    {
      "relative_path": "backbone_2h.csv",
      "sha256": "96cd332b4f4b3282b7ba77273cf0b0bae88777f3c2480fab90f066b0f4914596",
      "byte_size": 2456,
      "row_count": 36
    },
    {
      "relative_path": "strips/2h/20221211-A-GBPUSD.csv",
      "sha256": "4d088731bb393b66bee2c260244e34574644af30487a204576cc22a5351ad9cb",
      "byte_size": 750,
      "row_count": 8
    }
  ]
}
```

**Manifest Exclusions:**

To prevent circular dependencies, manifests MUST exclude:
- `manifest.json`, `data_manifest.json`, `build_manifest.json`
- `pack_sha256.txt`, `build_sha256.txt`, `data_sha256.txt`
- `manifest_sha256.txt`, `data_manifest_sha256.txt`, `build_manifest_sha256.txt`
- Any other `*_sha256.txt` hash files

Additionally, `meta.json` is excluded from all manifests because it is written last and contains the final pack hash values.

### 2. Provenance Metadata

**File:** `meta.json`

Enhanced with provenance tracking:

```json
{
  "version": "evidence_pack_v0_2",
  "run_id": "p1_20260120_031",
  "symbol": "GBPUSD",
  "date_from": "2022-12-12",
  "date_to": "2022-12-14",
  "generated_at": "2026-01-22T03:15:21Z",

  "git_commit_sha": "edfe1bc...",
  "neon_db": {
    "host": "ep-XXX.us-east-2.aws.neon.tech",
    "database": "neondb",
    "schema": "ovc"
  },
  "m15_ingest_bounds": {
    "min_ingest_ts": "2022-12-11T17:00:00Z",
    "max_ingest_ts": "2022-12-14T17:00:00Z"
  },
  "source_provenance": null,

  "pack_sha256": "0123abcd...",
  "data_sha256": "deadbeef...",

  "counts": { ... },
  "sources": { ... },
  "tolerance": 1e-06,
  "m15_scope": { ... }
}
```

#### Provenance Fields

- **`git_commit_sha`**: Git commit hash of the codebase that generated this pack
- **`neon_db`**: Database connection info (non-secret: host, database, schema)
- **`m15_ingest_bounds`**: Actual ingest timestamp bounds from M15 data used in pack
- **`source_provenance`**: Placeholder for upstream provenance (e.g., oanda_build_id)
- **`data_sha256`**: **CANONICAL CITATION HASH** — Deterministic hash of data files only (backbone, strips, context). Stable across rebuilds if source candle data is unchanged.
- **`pack_sha256`**: **BUILD INTEGRITY HASH** — Deterministic hash of all pack files (excluding manifests and meta.json). MAY change due to metadata updates (timestamps, audits, provenance).

### 3. Deterministic Pack Hash

**Canonical Definition:**

The `pack_sha256` hash is computed as follows:

1. Sort manifest entries lexicographically by `relative_path`
2. Build a UTF-8 string consisting of lines in the format:
   ```
   {sha256}  {relative_path}\n
   ```
   (SHA-256 hash, two spaces, relative path, newline)
3. Compute SHA-256 hash over the concatenated UTF-8 string

**Stored in:**
- `pack_sha256.txt` (single line)
- `meta.json` → `pack_sha256` field

**Data vs Build Hash:**
- **`data_sha256`** (Citation Hash): Hash of deterministic candle data files only (backbone, strips, context CSVs). This is the **canonical identifier** for citing evidence packs in research. It remains stable across rebuilds when source candle data is unchanged.
- **`pack_sha256`** (Build Hash): Hash of all pack files including qc_report.json and dst_audit.json (but excluding manifests and meta.json). This verifies build integrity but MAY change due to timestamps, audit results, or provenance updates.

## Pack Rebuild Equivalence

Identical inputs MUST produce identical `data_sha256` values across rebuilds. The `pack_sha256` hash MAY vary when metadata timestamps change, but rebuild equivalence is judged by the data hash. An integration test (`tests/test_pack_rebuild_equivalence.py`) enforces this invariant. Rebuild equivalence is required for citation validity, because `data_sha256` is the canonical citation identifier.

### 4. Dual Manifest System

Two manifests are generated:

1. **`data_manifest.json`**: Includes only deterministic candle data files
   - backbone_2h.csv
   - strips/2h/*.csv
   - context/4h/*.csv
   - Hash: `data_sha256`

2. **`build_manifest.json`** (aka `manifest.json`): Includes all pack files
   - All data files (backbone, strips, context)
   - qc_report.json
   - dst_audit.json (if present)
   - **Excludes:** meta.json (written after manifests), manifest files, hash files
   - Hash: `pack_sha256`

**Meta.json Handling:**

`meta.json` is written LAST in the build flow and is excluded from all manifests. This is because meta.json contains the final `pack_sha256` and `data_sha256` values computed from the manifests. Writing meta.json before computing hashes would create a circular dependency.

This separation allows verification of data integrity independent of metadata timestamps.

## File Order Stability

To ensure deterministic hashing, implementations MUST enforce the following ordering:

1. **CSV rows**: MUST be emitted in stable sort order by `bar_start_ms` ascending
2. **JSON output**: MUST use `sort_keys=True` for canonical key ordering
3. **Manifest files**: File entries MUST be sorted lexicographically by `relative_path`

Violations of these ordering requirements will produce non-deterministic hashes and break reproducibility.

## Validation

### Post-Run Validator

```bash
python scripts/path1/validate_post_run.py --run-id p1_20260120_031 --strict
```

**In strict mode:**
- Verifies manifest.json exists and is valid JSON
- Checks all file entries have required fields (relative_path, sha256, byte_size)
- Verifies CSV files have `row_count` field
- Validates pack_sha256 computation matches stored value
- Checks meta.json contains all provenance fields

**Non-strict mode:**
- Warns about missing provenance fields but doesn't fail validation

### Manual Verification

Verify pack integrity:
```bash
cd reports/path1/evidence/runs/{run_id}/outputs/evidence_pack_v0_2

# Verify individual file
sha256sum strips/2h/20221211-A-GBPUSD.csv
# Compare with manifest.json entry

# Verify pack hash
cat manifest.json | python -c "
import json, sys, hashlib
m = json.load(sys.stdin)
lines = [f\"{e['sha256']}  {e['relative_path']}\n\" for e in m['files']]
print(hashlib.sha256(''.join(lines).encode()).hexdigest())
"
# Compare with pack_sha256.txt
```

## Citation Format

When citing an evidence pack in research, you MUST use `data_sha256` as the primary identifier. This hash is stable across rebuilds when source candle data is unchanged, making it suitable for reproducible citation.

**Canonical Format:**
```
OVC Evidence Pack v0.2: {symbol} {date_from}..{date_to}
Run ID: {run_id}
Data Hash (Citation): {data_sha256}
Pack Hash (Build): {pack_sha256}
Git Commit: {git_commit_sha}
Generated: {generated_at}
```

**Example:**
```
OVC Evidence Pack v0.2: GBPUSD 2022-12-12..2022-12-14
Run ID: p1_20260120_031
Data Hash (Citation): deadbeef0123456789abcdef0123456789abcdef0123456789abcdef01234567
Pack Hash (Build): 0123abcd456789ef0123456789abcdef0123456789abcdef0123456789abcdef
Git Commit: edfe1bc7a4d3b2e1f9c8a7b6d5e4f3c2b1a0987654321fedcba9876543210
Generated: 2026-01-22T03:15:21Z
```

**Citation Hash Policy:**

- **`data_sha256`** is the canonical citation identifier
- **`pack_sha256`** is optional supplemental integrity information
- Use `data_sha256` when referencing evidence packs in papers, reports, or datasets
- `pack_sha256` may be included to verify build integrity but should not be the primary citation key

## Security Considerations

**What MUST be included:**
- Git commit SHA (public identifier)
- Database host and database name (non-secret connection metadata)
- Ingest timestamp bounds (data provenance)

**What MUST NOT be included:**
- Database credentials (username, password)
- API keys or authentication tokens
- Internal network information beyond public hostnames

**Policy:** The `neon_db` object MUST contain only connection metadata needed for reproducibility. It MUST NOT contain authentication secrets. Implementations MUST ensure credentials are stripped from DSN parsing.

## Implementation Details

### Helper Functions

- **`count_csv_rows(path)`**: Robust CSV row counter using csv.reader
- **`extract_neon_db_info(dsn)`**: Parse DSN to extract host, database, schema
- **`compute_m15_ingest_bounds(conn, m15_rows)`**: Query actual ingest timestamps
- **`build_manifest(pack_root, data_only)`**: Generate manifest with file metadata
- **`compute_pack_sha256(manifest)`**: Deterministic hash computation

### Build Flow

1. Write all data files (backbone, strips, context)
2. Write qc_report.json
3. Run DST audit (if requested) → dst_audit.json
4. Compute provenance info (git_commit_sha, neon_db, m15_ingest_bounds)
5. Write manifest files (data_manifest.json, build_manifest.json) → compute hashes (data_sha256, pack_sha256)
6. Build meta.json object with provenance + data_sha256 + pack_sha256
7. Write meta.json LAST

**Critical:** `meta.json` MUST be written last because it contains the final hash values. Writing it before manifests would create a circular dependency. Manifests exclude meta.json for this reason.

## Backward Compatibility

Legacy files are maintained for compatibility:
- `manifest.json` = `build_manifest.json`
- `pack_sha256.txt` = `build_sha256.txt`
- `manifest_sha256.txt` = `build_manifest_sha256.txt`

New deployments should prefer the explicit data/build separation.

## Future Enhancements

**Non-Normative:** The following are potential future additions and are NOT part of the current canonical specification:

- `source_provenance.oanda_build_id`: Link to upstream data build
- `source_provenance.request_id`: API request tracking
- `m15_table_schema_hash`: Schema fingerprint for version tracking
- `pack_signature`: Cryptographic signature for authenticity

These enhancements may be considered in future versions but are not required for Evidence Pack v0.2 compliance.

---

## Specification Status

**Version:** Evidence Pack v0.2 with Provenance (2026-01)
**Status:** **CANONICAL** — This specification is finalized and frozen
**Compliance:** Research-grade reproducible citation object

**Normative Language:**
- **MUST** indicates absolute requirements
- **SHOULD** indicates recommended best practices
- **MAY** indicates optional features

This document is the authoritative specification for Evidence Pack v0.2 provenance and citation behavior.
