# OVC Enforcement Coverage Matrix v0.2

**Version**: 0.2
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2.1 — Seal Promotion & Governance Closure
**Supersedes**: v0.1 (frozen, not modified)

---

## Change Log from v0.1

| Change | Description |
|--------|-------------|
| ADD | OP-QA07 through OP-QA11 rows |
| RECALCULATE | Coverage percentages |

All v0.1 rows are unchanged and inherited verbatim.

---

## New Operation Coverage (Phase 2.1/2.2 Registry Builders)

| Operation | E1 Contract/Schema | E2 Runtime Validation | E3 Tests | E4 CI Gate | E5 Audit Harness | E6 Documentation | E7 Run Artifact | Coverage Level |
|-----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| OP-QA07 Run Registry Build | Y | Y | — | — | Y | Y | Y | **C3** |
| OP-QA08 Op Status Table Build | Y | Y | — | — | Y | Y | Y | **C3** |
| OP-QA09 Drift Signals Build | Y | Y | — | — | Y | Y | Y | **C3** |
| OP-QA10 System Health Render | P | Y | — | — | Y | Y | Y | **C3** |
| OP-QA11 Registry Delta Log Build | Y | Y | — | — | Y | Y | Y | **C3** |

**Legend:** Y = Yes, P = Partial, — = Not present

**Notes:**
- E1 (Contract/Schema): All have Phase 2.2 schemas. OP-QA10 is Partial because system_health_report has a stub schema (markdown artifact).
- E3 (Tests): No dedicated unit tests for these builders yet. Existing test_run_envelope_v0_1.py covers envelope helpers but not builder-specific logic.
- E4 (CI Gate): No CI workflow triggers these builders. Manual invocation only.
- E5 (Audit Harness): All produce sealed run folders validated by validate_registry_seals_v0_1.py.
- E6 (Documentation): REGISTRY_LAYER_RUNBOOK_v0_1.md covers all four operations.
- E7 (Run Artifact): All produce run.json with full envelope.

---

## Updated Coverage Summary

| Level | v0.1 Count | v0.2 Count | v0.2 Operations |
|-------|-----------|-----------|-----------------|
| C5 (Fully Governed) | 4 | 4 | OP-B01, OP-B02, OP-B08, OP-D03 |
| C4 (Gated + Artifacts) | 8 | 8 | OP-A02, OP-A04, OP-B04, OP-C02, OP-D01, OP-D02, OP-D11, OP-QA01 |
| C3 (CI/Audit Gated) | 14 | 19 | v0.1 C3 ops + OP-QA07, OP-QA08, OP-QA09, OP-QA10, OP-QA11 |
| C2 (Runtime, not gated) | 5 | 5 | OP-D06, OP-D07, OP-D10, OP-QA05, OP-QA06 |
| C1 | 0 | 0 | — |
| C0 | 0 | 0 | — |

| Metric | v0.1 | v0.2 |
|--------|------|------|
| Total Canonical Operations | 31 | 36 |
| Enforcement Coverage (C3+) | 83.9% (26/31) | **86.1% (31/36)** |
| C2 (Weak) Operations | 5 (16.1%) | 5 (13.9%) |

---

## Enforcement Notes

### Phase 2.3 — Maintenance Contracts

| Property | Value |
|----------|-------|
| **Classification** | Normative / Non-Executable |
| **Enforcement** | Documentation-only |
| **Rationale** | Defines law governing change; introduces no runtime enforcement surfaces. |

The four Maintenance Contracts (Upgrade, Deprecation, Recovery, Health) are normative governance artifacts. They define what shall, must, and may not occur during state transitions — but they do not introduce execution code, CI gates, validators, or runtime checks. Enforcement is by reference during manual or automated operations that invoke state changes.

No new enforcement levels are added by Phase 2.3.

---

*End of Enforcement Coverage Matrix v0.2*
