# Option D: Evidence Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

---

## 1. Purpose

Option D generates evidence packs for Path1 (descriptive) and Path2 (interpretive). Evidence packs are deterministic, versioned, and traceable.

---

## 2. Inputs (Authoritative Sources)

### 2.1 Path1 Evidence Inputs

| Source | Table/View | Description |
|--------|------------|-------------|
| Outcomes | `derived.v_ovc_c_outcomes_v0_1` | Forward-looking outcomes |
| Evidence view | `derived.v_path1_evidence_dis_v1_1` | Joined scores + outcomes |
| Spine | `ovc.ovc_blocks_v01_1_min` | 2H block metadata |
| M15 overlay | `ovc.ovc_candles_m15_raw` | M15 candle strips |

### 2.2 Path2 Evidence Inputs

Path2 is not implemented in v1. Inputs TBD.

---

## 3. Outputs (Data Products)

### 3.1 Path1 Evidence Pack Structure

```
reports/path1/evidence/runs/<run_id>/
├── outputs/
│   └── evidence_pack_v0_2/
│       ├── backbone_2h.csv          # Block index
│       ├── strips/2h/               # M15 strips per block
│       │   └── {block_id}.csv
│       ├── context/4h/              # 4H context windows
│       │   └── {block4h}_{date_ny}.csv
│       ├── meta.json                # Pack metadata
│       ├── qc_report.json           # QC validation results
│       ├── data_manifest.json       # Deterministic data manifest
│       ├── data_sha256.txt          # Data hash (stable)
│       ├── build_manifest.json      # Full build manifest
│       ├── build_sha256.txt         # Build hash (may vary)
│       ├── manifest.json            # Legacy manifest
│       ├── pack_sha256.txt          # Legacy hash
│       └── dst_audit.json           # DST validation (optional)
└── pack_build.jsonl                 # Build ledger
```

### 3.2 Ledger Entry Schema

```json
{
  "event_type": "evidence_pack_build",
  "pack_version": "0.2",
  "run_id": "p1_20260123_001",
  "sym": "GBPUSD",
  "date_from": "2023-01-01",
  "date_to": "2023-12-31",
  "generated_at_utc": "2026-01-23T12:00:00Z",
  "status": "success",
  "git": {"commit": "abc1234", "dirty": false},
  "hashes": {
    "data_sha256": "...",
    "build_sha256": "..."
  }
}
```

---

## 4. Canonical vs Derived Rules

### 4.1 Option D MUST

- Read outcomes from `derived.v_ovc_c_outcomes_v0_1` (NOT deprecated view)
- Read spine from canonical table (for block metadata only)
- Read M15 from `ovc.ovc_candles_m15_raw`
- Produce deterministic data hashes for same inputs

### 4.2 Option D MUST NOT

- Read from `derived.ovc_outcomes_v0_1` (deprecated)
- Modify any source tables
- Produce evidence without run provenance

---

## 5. Versioning & Naming

### 5.1 Evidence Pack Version

```
evidence_pack_v{major}_{minor}
```

Current: `evidence_pack_v0_2`

### 5.2 Run ID Format

```
p1_{YYYYMMDD}_{seq}
```

Example: `p1_20260123_001`

---

## 6. Run Provenance

### 6.1 Required Metadata

| Field | Source | Description |
|-------|--------|-------------|
| `run_id` | CLI argument | Unique run identifier |
| `git.commit` | Git repo | Commit hash at build time |
| `git.dirty` | Git repo | Working tree status |
| `generated_at_utc` | System clock | Build timestamp |
| `data_sha256` | Computed | Hash of deterministic data files |

### 6.2 Ledger Location

All pack builds append to:
```
reports/path1/evidence/runs/<run_id>/pack_build.jsonl
```

---

## 7. Allowed Dependencies

| Dependency | Allowed |
|------------|---------|
| `derived.v_ovc_c_outcomes_v0_1` | ✅ |
| `derived.v_path1_evidence_dis_v1_1` | ✅ |
| `ovc.ovc_blocks_v01_1_min` (spine) | ✅ |
| `ovc.ovc_candles_m15_raw` | ✅ |
| `derived.ovc_outcomes_v0_1` | ❌ (PROHIBITED - deprecated) |
| Other Option C outputs | ❌ |

---

## 8. Determinism Requirements

### 8.1 Stable Hash Components

These files are included in `data_sha256`:
- `backbone_2h.csv`
- `strips/2h/*.csv`
- `context/4h/*.csv`

### 8.2 Unstable Components

These files may vary between builds:
- `meta.json` (contains timestamps)
- `qc_report.json` (contains timestamps)
- `build_manifest.json` (includes above files)

### 8.3 Determinism Test

For identical:
- Database state
- `run_id`, `sym`, `date_from`, `date_to`
- Code version

The `data_sha256.txt` MUST be identical.

---

## 9. Workflow Requirements

### 9.1 Path1 Workflows

| Workflow | Purpose |
|----------|---------|
| `path1_evidence.yml` | Single evidence pack build |
| `path1_evidence_queue.yml` | Queue-based batch build |
| `path1_replay_verify.yml` | Replay verification |

### 9.2 Required Gates

Before committing evidence pack:
1. `qc_report.json` shows no critical failures
2. M15 strip count matches expected (8 per 2H block)
3. Aggregation matches (M15 → 2H OHLC within tolerance)

---

## 10. Migration: Outcome Source Alignment

### 10.1 Current State

Evidence pack builder (`build_evidence_pack_v0_2.py`) reads from:
- `derived.v_path1_evidence_dis_v1_1` → which joins to `derived.v_ovc_c_outcomes_v0_1`

This is CORRECT per contract.

### 10.2 Verification

No change needed. Evidence already uses authoritative outcome view.

---

## 11. Compliance Checklist

| # | Requirement | Verified By |
|---|-------------|-------------|
| 1 | Reads from `v_ovc_c_outcomes_v0_1` | Code review |
| 2 | Does not read deprecated outcomes | Code review |
| 3 | `data_sha256` deterministic | Replay test |
| 4 | Run provenance in ledger | Ledger inspection |
| 5 | QC report produced | File existence |
| 6 | M15 strip integrity validated | `qc_report.json` |
