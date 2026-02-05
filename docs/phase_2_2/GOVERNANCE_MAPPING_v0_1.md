# Registry Governance Mapping v0.1

**Version**: 0.1
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2 — Registry Layer (Canonical Memory)

---

## 1. Purpose

Map each registry build operation to the Phase 1.5 governance artifacts:
- Allowed Operations Catalog v0.1
- Enforcement Coverage Matrix v0.1
- Governance Completeness Scorecard v0.1

---

## 2. Mapping Table

| Registry | Build Tool | Allowed Op ID | Coverage Level | Enforcement Surfaces | Governance Status |
|----------|-----------|---------------|----------------|---------------------|-------------------|
| `run_registry` | `build_run_registry_v0_1.py` | **NOT MAPPED** | N/A | N/A | **GAP: No operation ID in Allowed Operations Catalog** |
| `op_status_table` | `build_op_status_table_v0_1.py` | **NOT MAPPED** | N/A | N/A | **GAP: No operation ID in Allowed Operations Catalog** |
| `drift_signals` | `build_drift_signals_v0_1.py` | **NOT MAPPED** | N/A | N/A | **GAP: No operation ID in Allowed Operations Catalog** |
| `system_health_report` | `render_system_health_v0_1.py` | **NOT MAPPED** | N/A | N/A | **GAP: No operation ID in Allowed Operations Catalog** |
| `migration_ledger` | Manual edit | **NOT MAPPED** | N/A | N/A | **GAP: Manual artifact, no operation** |
| `expected_versions` | Manual governance | **NOT MAPPED** | N/A | N/A | **GAP: Governance artifact, no operation** |
| `threshold_packs_file` | Manual file creation | OP-B07 | C3 | E1, E2, E3, E6 | **PARTIAL: OP-B07 covers DB registry, not file-based packs explicitly** |
| `threshold_registry_db` | `threshold_registry_v0_1.py` | OP-B07 | C3 | E1, E2, E3, E6 | COVERED |
| `validation_range_results` | Range validation runner | OP-D04 | C4 | E1, E2, E3, E4, E5, E6, E7 | COVERED |
| `derived_validation_reports` | Derived validation | OP-B08 | C5 | E1, E2, E3, E4, E5, E6, E7 | COVERED |
| `evidence_pack_registry` | `build_evidence_pack_v0_2.py` | OP-D01 | C4 | E1, E2, E3, E4, E5, E6, E7 | COVERED |
| `fingerprint_index` | Trajectory family builder | OP-D08 | C3 | E1, E2, E3, E6 | COVERED |

---

## 3. Gap Analysis

### 3.1 Registries Lacking Governance Coverage

The Phase 2.1 registry builders (`build_run_registry_v0_1.py`, `build_op_status_table_v0_1.py`, `build_drift_signals_v0_1.py`, `render_system_health_v0_1.py`) are **not listed** in the Allowed Operations Catalog v0.1.

**Impact:** These builders were introduced as Phase 2.1 tooling and are not yet incorporated into the governance framework established in Phase 1.5.

**Recommended Remediation:**

| Proposed Operation ID | Operation Name | Executables |
|----------------------|----------------|-------------|
| OP-QA07 | Run Registry Build | `tools/run_registry/build_run_registry_v0_1.py` |
| OP-QA08 | Operation Status Table Build | `tools/run_registry/build_op_status_table_v0_1.py` |
| OP-QA09 | Drift Signals Build | `tools/run_registry/build_drift_signals_v0_1.py` |
| OP-QA10 | System Health Render | `tools/run_registry/render_system_health_v0_1.py` |

These should be added to the Allowed Operations Catalog v0.2 (not v0.1, which is frozen under Phase 1.5 governance).

### 3.2 Governance Artifacts Without Operations

| Artifact | Nature | Recommendation |
|----------|--------|---------------|
| `migration_ledger` | Manual governance ledger | Document as governance artifact; no operation needed |
| `expected_versions` | Manual governance config | Document as governance artifact; no operation needed |

### 3.3 Scorecard Impact

If Phase 2.1 builders were added to the catalog:

| Metric | Current (Phase 1.5) | After Adding 2.1 Builders |
|--------|---------------------|--------------------------|
| Total Canonical Operations | 31 | 35 |
| Executable Mapping Coverage | 100% | 100% (if new ops are mapped) |
| Enforcement Coverage (C3+) | 83.9% (26/31) | TBD (depends on coverage assigned) |

---

## 4. Enforcement Coverage Matrix Extension (Proposed)

| Operation | E1 Contract | E2 Runtime | E3 Tests | E4 CI Gate | E5 Audit | E6 Doc | E7 Ledger |
|-----------|------------|-----------|---------|-----------|---------|--------|----------|
| OP-QA07 (Run Registry Build) | YES (schema) | YES (builder) | PARTIAL (test coverage TBD) | NO | YES (sealed) | YES (runbook) | YES (run.json) |
| OP-QA08 (Op Status Table Build) | YES (schema) | YES (builder) | PARTIAL | NO | YES (sealed) | YES (runbook) | YES (run.json) |
| OP-QA09 (Drift Signals Build) | YES (schema) | YES (builder) | PARTIAL | NO | YES (sealed) | YES (runbook) | YES (run.json) |
| OP-QA10 (System Health Render) | PARTIAL (stub schema) | YES (builder) | PARTIAL | NO | YES (sealed) | YES (runbook) | YES (run.json) |

**Projected coverage level:** C3 (CI gate not yet implemented for these builders).

---

## 5. Phase 2.2 Governance Completeness

| Check | Status |
|-------|--------|
| All registries discovered and cataloged | PASS |
| All registries with schemas | PASS (12/12) |
| All registries with seal contract | PASS (contract defined; 5 registries flagged as unsealed gaps) |
| All registries with active pointers | PASS (pointer file created; 4 registries with `active_ref_known: unknown`) |
| All registry builds mapped to operations | FAIL (4 Phase 2.1 builders not in Allowed Operations Catalog) |
| All registries with validators | PASS (validator proposals created) |
| No Phase 2.1 artifacts modified | PASS |

---

*End of Registry Governance Mapping v0.1*
