# OVC Allowed Operations Catalog v0.2

**Version**: 0.2
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2.1 — Seal Promotion & Governance Closure
**Supersedes**: v0.1 (frozen, not modified)

---

## Change Log from v0.1

| Change | Description |
|--------|-------------|
| ADD OP-QA07 | Run Registry Build |
| ADD OP-QA08 | Operation Status Table Build |
| ADD OP-QA09 | Drift Signals Build |
| ADD OP-QA10 | System Health Render |

v0.1 operations (OP-A01 through OP-QA06, OP-NC01 through OP-NC29) are unchanged and inherited verbatim.

---

## New Operations (Phase 2.1/2.2 Registry Builders)

### OP-QA07 — Run Registry Build

| Field | Value |
|-------|-------|
| **Operation ID** | OP-QA07 |
| **Option** | QA |
| **Purpose** | Scan all run roots and produce an append-only JSONL registry of all discovered runs |
| **Bound Executables** | `tools/run_registry/build_run_registry_v0_1.py` |
| **Inputs** | `.codex/RUNS/`, `reports/runs/`, `reports/path1/evidence/runs/` (filesystem scan) |
| **Outputs** | `RUN_REGISTRY_v0_1.jsonl`, `RUN_REGISTRY_v0_1.schema.json`, `run.json`, `manifest.json`, `MANIFEST.sha256` |
| **Determinism** | YES — same filesystem state produces identical output (excluding timestamp in run.json) |
| **Failure Modes** | Filesystem read error; malformed run.json in scanned folder |
| **Enforcement Surfaces** | E1 (schema), E2 (builder validation), E5 (sealed artifact), E6 (runbook), E7 (run.json) |
| **Evidence Anchors** | `.codex/RUNS/<run_id>/RUN_REGISTRY_v0_1.jsonl` |
| **Dependencies** | None (first in build chain) |

### OP-QA08 — Operation Status Table Build

| Field | Value |
|-------|-------|
| **Operation ID** | OP-QA08 |
| **Option** | QA |
| **Purpose** | Derive per-operation health/freshness/drift status from the run registry and governance documents |
| **Bound Executables** | `tools/run_registry/build_op_status_table_v0_1.py` |
| **Inputs** | `RUN_REGISTRY_v0_1.jsonl` (active), `OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md`, `OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md` |
| **Outputs** | `OPERATION_STATUS_TABLE_v0_1.json`, `OPERATION_STATUS_TABLE_v0_1.schema.json`, `OPERATION_STATUS_TABLE_v0_1.meta.json`, `run.json`, `manifest.json`, `MANIFEST.sha256` |
| **Determinism** | YES |
| **Failure Modes** | Missing run registry; malformed governance documents |
| **Enforcement Surfaces** | E1 (schema), E2 (builder validation), E5 (sealed artifact), E6 (runbook), E7 (run.json) |
| **Evidence Anchors** | `.codex/RUNS/<run_id>/OPERATION_STATUS_TABLE_v0_1.json` |
| **Dependencies** | OP-QA07 (run registry must exist) |

### OP-QA09 — Drift Signals Build

| Field | Value |
|-------|-------|
| **Operation ID** | OP-QA09 |
| **Option** | QA |
| **Purpose** | Detect schema version drift, threshold pack drift, and per-operation drift signals |
| **Bound Executables** | `tools/run_registry/build_drift_signals_v0_1.py` |
| **Inputs** | `OPERATION_STATUS_TABLE_v0_1.json` (active), `RUN_REGISTRY_v0_1.jsonl` (active), `docs/governance/EXPECTED_VERSIONS_v0_1.json`, `configs/threshold_packs/*.json` |
| **Outputs** | `DRIFT_SIGNALS_v0_1.json`, `DRIFT_SIGNALS_v0_1.schema.json`, `run.json`, `manifest.json`, `MANIFEST.sha256` |
| **Determinism** | YES |
| **Failure Modes** | Missing expected versions; missing op status table |
| **Enforcement Surfaces** | E1 (schema), E2 (builder validation), E5 (sealed artifact), E6 (runbook), E7 (run.json) |
| **Evidence Anchors** | `.codex/RUNS/<run_id>/DRIFT_SIGNALS_v0_1.json` |
| **Dependencies** | OP-QA08 (op status table must exist), OP-QA07 |

### OP-QA10 — System Health Render

| Field | Value |
|-------|-------|
| **Operation ID** | OP-QA10 |
| **Option** | QA |
| **Purpose** | Render a human-readable system health report from registry data |
| **Bound Executables** | `tools/run_registry/render_system_health_v0_1.py` |
| **Inputs** | `OPERATION_STATUS_TABLE_v0_1.json` (active), `DRIFT_SIGNALS_v0_1.json` (active), `RUN_REGISTRY_v0_1.jsonl` (active) |
| **Outputs** | `SYSTEM_HEALTH_v0_1.md`, `SYSTEM_HEALTH_SUMMARY_v0_1.json`, `run.json`, `manifest.json`, `MANIFEST.sha256` |
| **Determinism** | YES (presentation-only derivation) |
| **Failure Modes** | Missing input registries |
| **Enforcement Surfaces** | E2 (builder validation), E5 (sealed artifact), E6 (runbook), E7 (run.json) |
| **Evidence Anchors** | `.codex/RUNS/<run_id>/SYSTEM_HEALTH_v0_1.md` |
| **Dependencies** | OP-QA09, OP-QA08, OP-QA07 |

---

## Summary

| Metric | v0.1 | v0.2 |
|--------|------|------|
| Total Canonical Operations | 31 | 35 |
| Non-Canonical Entries | 29 | 29 (unchanged) |
| New QA Operations | — | 4 (OP-QA07 through OP-QA10) |

---

*End of Allowed Operations Catalog v0.2*
