# A→D Pipeline Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

Master contract governing the flow from Option A (Ingest) through Option D (Evidence).

---

## 1. Purpose

This contract defines:
1. The single authoritative data flow from ingestion to evidence generation
2. Canonical vs derived boundaries
3. Naming conventions and versioning rules
4. Run provenance requirements
5. Dependency constraints per Option

---

## 2. Option Overview

| Option | Purpose | Canonical Grain |
|--------|---------|-----------------|
| **A** | Ingest raw external data into canonical facts | M15 (raw), 2H (blocks) |
| **B** | Compute derived features from canonical facts | 2H blocks |
| **C** | Compute forward-looking outcomes from derived features | 2H blocks |
| **QA** | Validate correctness, coverage, determinism | All layers |
| **D** | Generate evidence packs for Path1/Path2 | 2H blocks + M15 overlay |

---

## 3. Canonical vs Derived Rules

### 3.1 Canonical Data

Canonical data is:
- **Immutable** once ingested (no post-hoc modifications)
- **Raw** (no computed/derived fields)
- **Source-attributable** (traceable to external system)

**v1 Canonical Tables**:
| Table | Grain | Allowed Fields |
|-------|-------|----------------|
| `ovc.ovc_blocks_v01_1_min` | 2H blocks | `block_id`, `sym`, `date_ny`, `block2h`, `block4h`, `bar_close_ms`, `o`, `h`, `l`, `c`, `rng`, `ret`, `volume` |
| `ovc.ovc_candles_m15_raw` | M15 candles | `bar_start_ms`, `bar_close_ms`, `sym`, `o`, `h`, `l`, `c`, `volume` |

**PROHIBITED in canonical tables**: `state_tag`, `trend_tag`, `pred_dir`, `bias_dir`, `struct_state`, or any computed classifier output.

### 3.2 Derived Data

Derived data is:
- **Recomputable** from canonical inputs + configuration
- **Versioned** with explicit formula hash
- **Tracked** with run provenance

**v1 Derived Schema**: `derived.*`

### 3.3 Boundary Enforcement

- Option A → MUST NOT write derived fields to canonical tables
- Option B → MUST read ONLY from canonical tables
- Option C → MUST read ONLY from Option B outputs
- Option D → MUST read ONLY from Option C outputs (for outcomes)

---

## 4. Time Resolution Rules

### 4.1 Canonical Grain

| Grain | Resolution | Table |
|-------|------------|-------|
| M15 | 15 minutes | `ovc.ovc_candles_m15_raw` |
| 2H | 2 hours (block) | `ovc.ovc_blocks_v01_1_min` |

### 4.2 Derived Aggregation

| Aggregation | Source | Output |
|-------------|--------|--------|
| 4H | 2x 2H blocks | Computed in views |
| Daily (D) | 12x 2H blocks | Computed in views |

**Rule**: Aggregations above 2H are ALWAYS derived, never canonical.

---

## 5. Versioning & Naming Conventions

### 5.1 Table/View Naming

```
{schema}.{entity}_{version}
```

Examples:
- `ovc.ovc_blocks_v01_1_min` (canonical)
- `derived.ovc_c1_features_v0_1` (derived table)
- `derived.v_ovc_c_outcomes_v0_1` (derived view, prefix `v_`)

### 5.2 Script Naming

```
{action}_{entity}_{version}.{ext}
```

Examples:
- `compute_c1_v0_1.py`
- `build_evidence_pack_v0_2.py`

### 5.3 Version Bumping

| Change Type | Version Bump |
|-------------|--------------|
| Breaking schema change | MAJOR (v1 → v2) |
| New field (additive) | MINOR (v0.1 → v0.2) |
| Bug fix (same semantics) | PATCH (documented in changelog) |

---

## 6. Run Provenance Rules

### 6.1 Run ID Format

```
{option}_{YYYYMMDD}_{seq}_{commit_short}
```

Examples:
- `c_20260123_001_abc1234` (Option C run)
- `p1_20260123_001_abc1234` (Path1 evidence run)

### 6.2 Required Manifests

Every automated run MUST produce:
- `run_id` in output metadata
- Git commit hash
- Timestamp (UTC)
- Input hash/checksum where applicable

### 6.3 Determinism Requirements

For the same:
- Input data
- Configuration (thresholds, parameters)
- Code version

The output MUST be bit-for-bit identical (within defined tolerance for floats).

---

## 7. Allowed Dependencies (Read Matrix)

| Layer | May Read From |
|-------|---------------|
| Option A | External sources only |
| Option B | `ovc.ovc_blocks_v01_1_min`, `ovc_cfg.threshold_*` |
| Option C | `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1`, `derived.v_ovc_c3_features_v0_1` |
| QA | All layers (read-only validation) |
| Option D (Path1) | `derived.v_ovc_c_outcomes_v0_1`, `ovc.ovc_blocks_v01_1_min` (spine), `ovc.ovc_candles_m15_raw` (overlay) |

**PROHIBITED reads**:
- Option C MUST NOT read from `ovc.ovc_blocks_v01_1_min` directly
- Option D MUST NOT read from `derived.ovc_outcomes_v0_1` (use `v_ovc_c_outcomes_v0_1`)

---

## 8. Schema/Migration Certainty

### 8.1 Migration Ledger

A file `schema/applied_migrations.json` MUST track:
```json
{
  "migrations": [
    {"file": "sql/00_schema.sql", "applied_at": "2026-01-15T00:00:00Z", "sha256": "..."},
    {"file": "sql/01_tables_min.sql", "applied_at": "2026-01-15T00:00:00Z", "sha256": "..."}
  ]
}
```

### 8.2 CI Schema Check

CI MUST verify that expected tables/views exist by running a deterministic query set:
- `90_verify_gate2.sql` or equivalent
- Query each required table/view and assert existence

---

## 9. Individual Option Contracts

See linked documents for detailed specifications:

- [Option A: Ingest Contract](option_a_ingest_contract_v1.md)
- [Option B: Derived Contract](option_b_derived_contract_v1.md)
- [Option C: Outcomes Contract](option_c_outcomes_contract_v1.md)
- [QA: Validation Contract](qa_validation_contract_v1.md)
- [Option D: Evidence Contract](option_d_evidence_contract_v1.md)

---

## 10. Compliance Checklist (Master)

| # | Requirement | How Verified |
|---|-------------|--------------|
| 1 | No derived fields in canonical tables | Schema inspection |
| 2 | Option C reads from B views only | Code/SQL review |
| 3 | Path1 evidence uses `v_ovc_c_outcomes_v0_1` | View definition |
| 4 | Run provenance on all automated runs | Manifest check |
| 5 | CI runs pytest suite | Workflow inspection |
| 6 | CI verifies schema objects exist | Gate query execution |
| 7 | All workflows reference existing scripts | `ci_workflow_sanity.yml` |
| 8 | Single source of truth for each layer | Documentation review |
