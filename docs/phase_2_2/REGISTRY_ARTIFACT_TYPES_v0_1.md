# Registry Artifact Types & Composition Rules v0.1

**Version**: 0.1
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2 — Registry Layer (Canonical Memory)

---

## 1. Artifact Types

### 1.1 `run_folder`

**Definition:** A directory containing a complete, sealed set of artifacts from a single build operation.

**Required contents:**
- `run.json` — run envelope
- `manifest.json` — file manifest
- `MANIFEST.sha256` — hash file with ROOT_SHA256

**Observed locations:**
- `.codex/RUNS/<run_id>/`
- `reports/runs/<run_id>/`
- `reports/path1/evidence/runs/<run_id>/`

**Examples:** Run registry builds, op status table builds, drift signal builds, evidence pack builds.

### 1.2 `jsonl_registry`

**Definition:** A JSONL file where each line is a self-contained JSON object conforming to a declared schema. Append-only semantics at the snapshot level (each build produces a complete new JSONL, not appended lines to an existing file).

**Observed instances:**
- `RUN_REGISTRY_v0_1.jsonl`
- `pack_build.jsonl`
- `validate_range_*_days.jsonl`

### 1.3 `json_snapshot`

**Definition:** A single JSON file containing a complete state snapshot. Immutable once sealed.

**Observed instances:**
- `OPERATION_STATUS_TABLE_v0_1.json` (JSON array)
- `DRIFT_SIGNALS_v0_1.json` (JSON object)
- `derived_validation_report.json` (JSON object)
- `EXPECTED_VERSIONS_v0_1.json` (JSON object)
- `applied_migrations.json` (JSON object)

### 1.4 `index`

**Definition:** A structured file (CSV or JSON) that maps identifiers to artifact locations. Serves as a lookup table.

**Observed instances:**
- `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`

### 1.5 `pointer`

**Definition:** A file whose sole purpose is to reference another artifact. The only intentionally mutable artifact type.

**Observed instances:**
- `ACTIVE_REGISTRY_POINTERS_v0_1.json` (Phase 2.2, canonical)
- `artifacts/derived_validation/LATEST.txt` (Phase 2.1, pre-canonical)

### 1.6 `manifest`

**Definition:** A file that lists and hashes the contents of an artifact set.

**Sub-types:**
- `manifest.json` — structured JSON manifest
- `MANIFEST.sha256` — text hash file
- `build_manifest.json` — build-specific manifest (evidence packs)
- `data_manifest.json` — data-specific manifest (evidence packs)
- `pack_sha256.txt` — pack-level hash (evidence packs)

---

## 2. Composition Rules

### 2.1 A Valid Sealed Registry Artifact Set Consists Of

```
<run_folder>/
  run.json              (mandatory — envelope)
  manifest.json         (mandatory — file listing)
  MANIFEST.sha256       (mandatory — hashes + ROOT_SHA256)
  <registry_artifact>   (mandatory — the actual registry data)
  <schema_artifact>     (optional — schema JSON for the registry)
  <additional_outputs>  (optional — any other files produced by the build)
```

### 2.2 Hierarchy

```
pointer
  └── references → run_folder
                      ├── manifest (seals the folder)
                      └── registry_artifact
                            └── conforms to → schema
```

### 2.3 Rebuild vs Authoritative Rules

| Situation | Rule |
|-----------|------|
| A registry is rebuilt | The new build produces a **new** run folder. The old run folder is never modified. |
| A schema is updated | A new schema version file is created. Old schemas remain. The registry catalog is updated to reference the new schema_id. |
| Two builds produce identical content | Both are valid sealed artifacts. The pointer selects which is active. Content identity does not collapse builds. |
| A registry depends on another registry | The dependent registry MUST reference the active pointer of its input (not a hardcoded path). Build order is defined in the Runbook. |

### 2.4 Authoritative vs Derived

| Authority Class | Meaning | Mutability |
|----------------|---------|------------|
| `primary` | Source of truth. Not derived from another artifact. | Immutable once sealed (or mutable only via governance for non-sealed governance artifacts). |
| `derived` | Computed from primary sources. Deterministically reproducible. | Immutable once sealed. Rebuild produces new artifact. |

---

## 3. How Phase 2.2 Reads Phase 2.1 Outputs

### 3.1 Non-Modification Guarantee

Phase 2.2 artifacts sit **on top of** Phase 2.1 artifacts. The following guarantees hold:

1. **No Phase 2.1 file is modified** by Phase 2.2. All Phase 2.2 outputs are new files in `docs/phase_2_2/`.
2. **Phase 2.1 sealed run folders** are read-only inputs. Their `manifest.json`, `MANIFEST.sha256`, and `run.json` files are consumed but never written to.
3. **Phase 2.2 schemas formalize** what Phase 2.1 builders already produce. They do not add new fields to Phase 2.1 outputs.
4. **Active pointers** reference Phase 2.1 run folders by `run_id` and `run_root`. The Phase 2.1 run folder structure is the canonical storage format.

### 3.2 Reading Pattern

```
Phase 2.2 Pointer
  → resolves to Phase 2.1 run_folder (by run_id + run_root)
    → reads registry artifact (JSONL, JSON, etc.)
    → validates against Phase 2.2 schema
    → verified by Phase 2.2 seal validator
```

### 3.3 What Phase 2.2 Adds (Not Replaces)

| Phase 2.2 Artifact | What It Adds |
|--------------------|--------------|
| `REGISTRY_CATALOG_v0_1.json` | Discovery and inventory of all registries |
| `schemas/REGISTRY_*.schema.json` | Formal schemas for each registry |
| `REGISTRY_SEAL_CONTRACT_v0_1.md` | Formal seal validity definition |
| `ACTIVE_REGISTRY_POINTERS_v0_1.json` | Explicit active state selection |
| `REGISTRY_LAYER_RUNBOOK_v0_1.md` | Workflow contract |
| `REGISTRY_ARTIFACT_TYPES_v0_1.md` | This document |
| `validators/` | Validation harness proposals |

---

*End of Registry Artifact Types & Composition Rules v0.1*
