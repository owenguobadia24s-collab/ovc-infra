# Phase 3 Canon Schema Contract

**Version:** 0.1  
**Date:** 2026-02-05  
**Repo Path:** `tools/phase3_control_panel/docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.md`  
**Prime Invariant:** Sight without influence.

---

## Preamble

> **"Derived from artifacts, not artifacts bent to contract."**

This contract documents the observed, authoritative artifact schemas used by Phase 3 Control Panel parsing. It is a frozen, versioned specification derived entirely from evidence extracted from real artifacts under `PHASE3_REPO_ROOT`.

**CRITICAL:** This contract is read-only documentation; it does not grant authority. It does not modify runtime behavior, sorting, view meaning, UI affordances, or authority. It exists solely to record observed structure for validation and future compatibility checks.

---

## Artifacts in Scope (v0.1)

| Artifact | File Pattern | Discovery Path |
|----------|-------------|----------------|
| Run Registry | `RUN_REGISTRY_v0_1.jsonl` | `.codex/RUNS/*run_registry_build*/RUN_REGISTRY_v0_1.jsonl` (most recent) |
| Operation Status Table | `OPERATION_STATUS_TABLE_v0_1.json` | `.codex/RUNS/*op_status_table_build*/OPERATION_STATUS_TABLE_v0_1.json` (most recent) |
| Registry Delta Log | `REGISTRY_DELTA_LOG_v0_1.jsonl` | `.codex/RUNS/*registry_delta_log*/REGISTRY_DELTA_LOG_v0_1.jsonl` (most recent) |

---

## Evidence Anchors

### RUN_REGISTRY_v0_1.jsonl

- **Source Run:** `2026-02-05__000138__run_registry_build`
- **Total Entries:** 89
- **Sample Size:** 50 (first 50 lines)
- **Field Presence:** All fields present in 100% of sampled records
- **Extraction Method:** JSONL line-by-line parsing with field/null counting

### OPERATION_STATUS_TABLE_v0_1.json

- **Source Run:** `2026-02-05__000144__op_status_table_build`
- **Total Entries:** 31
- **Sample Size:** 31 (all entries)
- **Field Presence:** All fields present in 100% of sampled records
- **Extraction Method:** JSON array parsing with field/null counting

### REGISTRY_DELTA_LOG_v0_1.jsonl

- **Source Run:** `2026-02-05__031005__registry_delta_log_build`
- **Total Entries:** 22
- **Sample Size:** 22 (all entries)
- **Field Presence:** All fields present in 100% of sampled records
- **Extraction Method:** JSONL line-by-line parsing with field/null counting

---

## Schema Tables

### 1. RUN_REGISTRY_v0_1.jsonl — RunRegistryEntry

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `registry_version` | ✅ | ❌ | `string` | Always "0.1" in observed data |
| `run_id` | ✅ | ❌ | `string` | Unique run identifier |
| `run_root` | ✅ | ❌ | `string` | Root path for runs (e.g., ".codex/RUNS") |
| `run_key` | ✅ | ❌ | `string` | Composite key: `{run_root}::{run_id}` |
| `run_path` | ✅ | ❌ | `string` | Full path to run folder |
| `created_utc` | ✅ | ✅ | `string \| null` | ISO 8601 timestamp; null for legacy runs (28/50 null) |
| `run_type` | ✅ | ✅ | `string \| null` | Run type identifier; null for untyped runs (29/50 null) |
| `option` | ✅ | ✅ | `string \| null` | Option category (A/B/C/D/QA); null if unassigned (41/50 null) |
| `operation_id` | ✅ | ✅ | `string \| null` | Operation identifier (OP-XXX); null if untyped (48/50 null) |
| `git_commit` | ✅ | ✅ | `string \| null` | Git commit SHA; null for legacy runs (28/50 null) |
| `working_tree_state` | ✅ | ✅ | `string \| null` | "clean" or "dirty"; null for legacy runs (28/50 null) |
| `has_run_json` | ✅ | ❌ | `boolean` | Whether run.json exists |
| `has_manifest_sha256` | ✅ | ❌ | `boolean` | Whether MANIFEST.sha256 exists |
| `has_manifest_json` | ✅ | ❌ | `boolean` | Whether manifest.json exists |
| `manifest_root_sha256` | ✅ | ✅ | `string \| null` | Root hash; null if no manifest (29/50 null) |
| `files` | ✅ | ❌ | `array<FileEntry>` | Array of file metadata |
| `warnings` | ✅ | ❌ | `array<string>` | Array of warning messages |

#### Nested Type: FileEntry

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `relpath` | ✅ | ❌ | `string` | Relative path within run folder |
| `bytes` | ✅ | ❌ | `number` | File size in bytes |

---

### 2. OPERATION_STATUS_TABLE_v0_1.json — OperationStatusEntry

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `status_version` | ✅ | ❌ | `string` | Always "0.1" in observed data |
| `option` | ✅ | ❌ | `string` | Option category (A/B/C/D/QA) |
| `operation_id` | ✅ | ❌ | `string` | Operation identifier (OP-XXX) |
| `operation_name` | ✅ | ❌ | `string` | Human-readable operation name |
| `coverage_level` | ✅ | ❌ | `string` | Coverage level (C2/C3/C4/C5) |
| `last_run_id` | ✅ | ✅ | `string \| null` | Most recent run ID; null if no typed run (27/31 null) |
| `last_run_created_utc` | ✅ | ✅ | `string \| null` | ISO 8601 timestamp; null if no typed run (27/31 null) |
| `run_evidence_state` | ✅ | ❌ | `string` | "LEGACY_ONLY" or "OBSERVED" |
| `manifest_state` | ✅ | ❌ | `string` | "UNKNOWN" or "PRESENT" |
| `run_json_state` | ✅ | ❌ | `string` | "UNKNOWN" or "PRESENT" |
| `staleness_days` | ✅ | ✅ | `number \| null` | Days since last run; null if no typed run (27/31 null) |
| `op_drift` | ✅ | ✅ | `boolean \| null` | Drift detected flag; null if unknown (27/31 null) |
| `op_drift_reasons` | ✅ | ❌ | `array<string>` | Array of drift reason codes |
| `warnings` | ✅ | ❌ | `array<string>` | Array of warning messages |

---

### 3. REGISTRY_DELTA_LOG_v0_1.jsonl — DeltaLogEntry

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `delta_version` | ✅ | ❌ | `string` | Always "0.1" in observed data |
| `registry_id` | ✅ | ❌ | `string` | Registry identifier |
| `from_ref` | ✅ | ✅ | `DeltaRef \| null` | Previous state; null for bootstrap (8/22 null) |
| `to_ref` | ✅ | ❌ | `DeltaRef` | Current state reference |
| `delta_basis` | ✅ | ❌ | `string` | Basis for delta computation (e.g., "manifest_diff") |
| `added_paths` | ✅ | ❌ | `array<string>` | List of added file paths |
| `removed_paths` | ✅ | ❌ | `array<string>` | List of removed file paths |
| `modified_paths` | ✅ | ❌ | `array<string>` | List of modified file paths |
| `counts` | ✅ | ❌ | `DeltaCounts` | Summary counts object |
| `created_utc` | ✅ | ❌ | `string` | ISO 8601 timestamp of delta creation |
| `derivation_run_id` | ✅ | ❌ | `string` | Run ID that produced this delta |

#### Nested Type: DeltaRef

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `run_id` | ✅ | ❌ | `string` | Run identifier |
| `run_root` | ✅ | ❌ | `string` | Run root path |
| `relpath` | ✅ | ✅ | `string \| null` | Relative path to artifact; null in some cases |
| `manifest_sha256` | ✅ | ❌ | `string` | Manifest root hash |

#### Nested Type: DeltaCounts

| Field | Required | Nullable | Type | Notes |
|-------|----------|----------|------|-------|
| `added` | ✅ | ❌ | `number` | Count of added files |
| `removed` | ✅ | ❌ | `number` | Count of removed files |
| `modified` | ✅ | ❌ | `number` | Count of modified files |

---

## Compatibility Rules

### Unknown Keys
- **Policy:** ALLOWED unless explicitly forbidden.
- Unknown keys in parsed objects are silently ignored by validators.
- Validators must not fail on presence of unrecognized keys.

### Field Semantics

| Term | Definition |
|------|------------|
| **Required** | Field present in 100% of observed records. Validators expect key to exist. |
| **Optional** | Field present in some records but not all. (Not observed in v0.1 scope.) |
| **Nullable** | Field key is always present, but value may be `null`. |
| **Type** | The observed value type(s). Union types (e.g., `string \| null`) indicate nullable fields. |

### Validation Behavior

- Validators return `false` (invalid) if a required field is missing.
- Validators return `false` (invalid) if a field has wrong type.
- Validators return `true` (valid) if all required fields present with correct types.
- Debug explainers (when `PHASE3_DEBUG_SCHEMA=1`) report first mismatch.

---

## Change Control

### Contract Versioning

- This contract is versioned as `v0.1`.
- Any schema change (new required field, type change, nullability change) **requires a contract bump** (v0.2, v0.3, etc.).
- Minor documentation clarifications do not require a bump.

### Bump Requirements

A contract bump **must include**:

1. **Updated evidence extraction** from current canonical artifacts.
2. **Schema table updates** reflecting new field structure.
3. **Migration notes** explaining what changed and why.
4. **Validator updates** (if runtime validators need adjustment).
5. **Phase 3.1 audits must still pass** after changes.

### Bump Triggers

| Change Type | Requires Bump? |
|-------------|----------------|
| New required field added | ✅ YES |
| Required field removed | ✅ YES |
| Field type changed | ✅ YES |
| Field nullability changed | ✅ YES |
| New optional field added | ❌ NO (unknown keys allowed) |
| Documentation clarification | ❌ NO |

---

## Attestation

> Contract frozen at v0.1.  
> Evidence-derived from artifacts dated 2026-02-05.  
> No runtime meaning, ordering, or authority changes.  
> This document is read-only documentation.

---

## Appendix: Discovery Path Rules

The following path rules are implemented in `sources.ts` for locating artifacts:

```
RUN_REGISTRY:
  1. List directories in {REPO_ROOT}/.codex/RUNS/
  2. Filter to directories containing "run_registry_build"
  3. Sort lexicographically descending (most recent timestamp first)
  4. Select first match
  5. Read RUN_REGISTRY_v0_1.jsonl from that directory

OPERATION_STATUS_TABLE:
  1. List directories in {REPO_ROOT}/.codex/RUNS/
  2. Filter to directories containing "op_status_table_build"
  3. Sort lexicographically descending (most recent timestamp first)
  4. Select first match
  5. Read OPERATION_STATUS_TABLE_v0_1.json from that directory

REGISTRY_DELTA_LOG:
  1. List directories in {REPO_ROOT}/.codex/RUNS/
  2. Filter to directories containing "registry_delta_log"
  3. Sort lexicographically descending (most recent timestamp first)
  4. Select first match
  5. Read REGISTRY_DELTA_LOG_v0_1.jsonl from that directory
```

---

*End of contract.*
