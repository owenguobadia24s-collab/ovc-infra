# Threshold Registry Assessment v0.1

**Version**: 0.1
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2 — Registry Layer (Canonical Memory)

---

## 1. Threshold Registries Discovered

Two distinct threshold registry mechanisms exist in this repo:

### 1.1 File-Based Threshold Packs (`threshold_packs_file`)

**Location:** `configs/threshold_packs/`

**Observed packs:**

| Pack File | Pack Type | Fields | SHA256 |
|-----------|-----------|--------|--------|
| `c3_example_pack_v1.json` | C3 classification thresholds | `min_body_bp`, `max_wick_ratio_bp`, `lookback`, `min_range_bp`, `volatility_threshold_bp` | must be computed at seal time |
| `c3_regime_trend_v1.json` | C3 regime/trend thresholds | `lookback`, `min_range_bp`, `min_direction_ratio_bp`, `min_hh_ll_count` | must be computed at seal time |
| `state_plane_v0_2_default_v1.json` | State plane projection config | `version`, `scope`, `thresholds`, `weights`, `y_map`, `columns`, `source_views` | must be computed at seal time |

**Status:** Explicit threshold packs exist as files. NOT inferred.

### 1.2 Database-Backed Threshold Registry (`threshold_registry_db`)

**Implementation:** `src/config/threshold_registry_v0_1.py`
**Schema DDL:** `sql/04_threshold_registry_v0_1.sql`, `sql/06_state_plane_threshold_pack_v0_2.sql`
**Operation:** OP-B07 (Threshold Registry Management)

**Capabilities:**
- Immutable pack storage (pack_id, pack_version, config_json, config_hash)
- SHA256 of canonicalized config
- Scope hierarchy: GLOBAL < SYMBOL < SYMBOL_TF
- Active pointer via upsert (`activate_pack()`)
- Integrity validation (`validate_integrity()`)

**Status:** Explicit implementation exists. Active state managed via DB active pointer table. NOT verifiable from repo evidence alone (requires DB access).

---

## 2. Minimal Schema for Threshold Registry Catalog Entry

```json
{
  "pack_id": "<string — unique pack identifier>",
  "version": "<string — pack version>",
  "source_path": "<string — file path or 'database'>",
  "sha256": "<string — SHA256 of canonicalized config, or null if not computed>",
  "status": "<DRAFT | ACTIVE | DEPRECATED | unknown>",
  "pack_type": "<c3_example | c3_regime_trend | state_plane | unknown>"
}
```

### Observed Instances

| pack_id | version | source_path | sha256 | status |
|---------|---------|-------------|--------|--------|
| `c3_example_pack` | `v1` | `configs/threshold_packs/c3_example_pack_v1.json` | not yet computed | `unknown` — no active pointer in repo evidence |
| `c3_regime_trend` | `v1` | `configs/threshold_packs/c3_regime_trend_v1.json` | not yet computed | `unknown` — no active pointer in repo evidence |
| `state_plane_v0_2_default` | `v1` | `configs/threshold_packs/state_plane_v0_2_default_v1.json` | not yet computed | `unknown` — no active pointer in repo evidence |

---

## 3. Active Threshold Set Selection

### 3.1 File-Based Packs

**Current state:** No explicit active pointer for file-based packs. The drift signals builder (`build_drift_signals_v0_1.py`) observes version `v0.2` from `state_plane_v0_2_default_v1.json` but the expected version in `EXPECTED_VERSIONS_v0_1.json` is `null` (not yet defined).

**Gap:** Active selection for file-based threshold packs is IMPLICIT (determined by which pack the consuming operation reads). This violates the Phase 2.2 requirement of explicit active pointers.

**Remediation:** Add a threshold pack entry to `ACTIVE_REGISTRY_POINTERS_v0_1.json` that explicitly declares which pack file is active for each consuming operation.

### 3.2 Database-Backed Packs

**Current state:** Active selection via `activate_pack()` method which upserts into `ovc_cfg.threshold_active_pointers` table.

**Gap:** Cannot verify active state from repo evidence alone. The DB is an external system.

**Remediation:** The threshold registry's `validate_integrity()` output should be captured as a sealed run artifact, creating a repo-verifiable snapshot of the DB active state.

---

## 4. Gap Summary

| Gap | Severity | Bounded? |
|-----|----------|----------|
| File-based packs have no explicit active pointer | Medium | YES — only 3 packs exist, consumed by known operations |
| `expected.threshold_pack_version` is null in EXPECTED_VERSIONS | Low | YES — drift signals correctly reports `threshold_drift: null` (unknown, not false) |
| DB active state not verifiable from repo | Medium | YES — `validate_integrity()` exists but output is not captured as sealed artifact |
| File-based packs have no seal (manifest/hash) | Medium | YES — pack files are small, version-named, and not frequently updated |

---

*End of Threshold Registry Assessment v0.1*
