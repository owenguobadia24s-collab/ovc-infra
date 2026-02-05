# OVC Governance Completeness Scorecard v0.2

**Version**: 0.2
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2.1 — Seal Promotion & Governance Closure
**Supersedes**: v0.1 (frozen, not modified)

---

## Change Log from v0.1

| Change | Description |
|--------|-------------|
| ADD | 4 new executable mappings (OP-QA07 through OP-QA10) |
| ADD | 1 new executable mapping (OP-QA11 Registry Delta Log Build — Phase 2.2.3) |
| ADD | 3 validator scripts (seal, schema, pointer) |
| ADD | 1 seal promotion script |
| ADD | 1 delta log builder (Phase 2.2.3) |
| RECALCULATE | All metrics |

---

## Executable Inventory

| Category | v0.1 Count | v0.2 Delta | v0.2 Count |
|----------|-----------|-----------|-----------|
| Python (.py) | 74 | +5 (validators + sealer + delta log builder) | 79 |
| PowerShell (.ps1) | 11 | 0 | 11 |
| Shell (.sh) | 2 | 0 | 2 |
| TypeScript (.ts) | 4 | 0 | 4 |
| SQL Infrastructure | 30 | 0 | 30 |
| SQL Path1 | 26 | 0 | 26 |
| Workflows (.yml) | 13 | 0 | 13 |
| Generated (~105 SQL) | ~105 | 0 | ~105 |
| **Governance-relevant** | **160** | **+5** | **165** |

---

## Governance Metrics

| Metric | v0.1 | v0.2 | Delta |
|--------|------|------|-------|
| **Executable Mapping Coverage** | 100.0% (160/160) | 100.0% (165/165) | Maintained |
| **Operation Evidence Coverage** | 100.0% (31/31) | 100.0% (36/36) | Maintained (+5 new ops, all with evidence) |
| **Enforcement Coverage (C3+)** | 83.9% (26/31) | **86.1% (31/36)** | +2.2pp |
| **Orphan Rate** | 0 | 0 | No change |
| **Weak Governance (C2)** | 5 (16.1%) | 5 (13.9%) | Percentage decreased |
| **Fully Governed (C5)** | 4 (12.9%) | 4 (11.1%) | Percentage decreased (dilution from new ops) |

---

## Registry Layer Metrics (New in v0.2)

| Metric | Count | Status |
|--------|-------|--------|
| **Total Registries** | 13 | All cataloged (12 + registry_delta_log) |
| **Registries with Schemas** | 13/13 | 100% |
| **Registries with Seals** | 9/13 | 69.2% (was 8/12 = 66.7% before Phase 2.2.3) |
| **Registries with Active Pointers (known)** | 8/13 | 61.5% (registry_delta_log has N/A active state) |
| **Registries with active_ref_known=unknown** | 4/13 | All justified as non-closable |
| **Seal Validations Passing** | 9/9 | 100% |
| **Pointer Validations Passing** | 12/12 | 100% (delta_log N/A) |

---

## Sealed Registries Detail

| Registry | Sealed? | Pointer Known? | Seal Source |
|----------|---------|---------------|-------------|
| run_registry | YES | YES | Phase 2.1 builder |
| op_status_table | YES | YES | Phase 2.1 builder |
| drift_signals | YES | YES | Phase 2.1 builder |
| migration_ledger | YES | YES | Phase 2.2.1 seal promotion |
| expected_versions | YES | YES | Phase 2.2.1 seal promotion |
| threshold_packs_file | YES | YES | Phase 2.2.1 seal promotion |
| fingerprint_index | YES | YES | Phase 2.2.1 seal promotion |
| derived_validation_reports | YES | YES | Phase 2.2.1 seal promotion |
| registry_delta_log | YES | N/A | Phase 2.2.3 builder (append-only memory, not control) |
| threshold_registry_db | NO | unknown | Non-closable (external DB) |
| validation_range_results | NO | unknown | Non-closable (collection registry) |
| evidence_pack_registry | NO | unknown | Non-closable (collection registry, individually sealed) |
| system_health_report | NO | unknown | Non-closable (presentation-only) |

---

## Known Gaps (Bounded, v0.2)

| Gap | Impact | Bounded? | Closable? |
|-----|--------|----------|-----------|
| 5 ops at C2 | No CI gate | YES | YES (future CI work) |
| C3 workflow args | C3 materialized via CI | YES | YES (workflow update) |
| Migration ledger entries UNVERIFIED | Cannot prove when applied | YES | YES (manual verification) |
| Worker deployment UNKNOWN | Cannot prove live ingest | YES | YES (external verification) |
| threshold_registry_db unverifiable | External system | YES | NO from repo alone |
| validation_range_results no single active | Collection registry | YES | NO (by design) |
| evidence_pack_registry no single active | Collection registry | YES | NO (by design) |
| system_health_report no single active | Presentation artifact | YES | NO (by design) |

---

## Phase 2.2.1/2.2.3 Improvements Over Phase 2.2

| Metric | Phase 2.2 | Phase 2.2.1 | Phase 2.2.3 | Improvement |
|--------|-----------|-------------|-------------|-------------|
| Sealed registries | 3/12 (25%) | 8/12 (66.7%) | 9/13 (69.2%) | +6 registries sealed |
| Known active pointers | 4/12 (33%) | 8/12 (66.7%) | 8/13 (61.5%) | +4 pointers resolved (delta_log N/A) |
| manifest_sha256 filled | 1/12 (8%) | 8/12 (66.7%) | 9/13 (69.2%) | +8 hashes resolved |
| Governance-mapped operations | 31 | 35 | 36 | +5 operations added |
| Enforcement C3+ | 83.9% | 85.7% | 86.1% | +2.2pp |

---

*End of Governance Completeness Scorecard v0.2*
