# OVC R1 Supersession Decision Register

**Status:** OPERATOR_DECISIONS_APPLIED_DOCUMENTATION_ONLY  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

This register separates operator direction from effective supersession.
Artifacts remain historically preserved. A direction marked approved is not
an effective authority transition unless its stated conditions are met.

| ID | Existing artifact or claim | Replacement direction | Operator decision | R1 effective state | Current classification |
|---|---|---|---|---|---|
| PS-01 | `contracts/export_contract_v0.1_min.json` | `contracts/export_contract_v0.1.1_min.json` | Conditional approval | NOT EFFECTIVE: compliant deprecation record absent | SUPPORTING historical |
| PS-02 | `contracts/derived_feature_set_v0.1.json` | Versioned machine-readable split C1/C2/C3 contract | Deferred | NOT EFFECTIVE: replacement absent | SUPPORTING legacy |
| PS-03 | `docs/contracts/option_c_boundary.md` | `docs/contracts/option_c_outcomes_contract_v1.md` | Conditional approval | NOT EFFECTIVE: v1 remains DRAFT | CONFLICTING historical boundary |
| PS-04 | `contracts/eval_contract_v0.1.json` for new runs | New B-backed evaluation contract | Direction approved | NOT EFFECTIVE: replacement absent | CONFLICTING; historical replay only |
| PS-05 | `sql/option_c_v0_1.sql` for new operations | `sql/derived/v_ovc_c_outcomes_v0_1.sql` | No-new-operations restriction approved | EXECUTION RESTRICTION EFFECTIVE; formal deprecation not asserted | SUPPORTING legacy / replay only |
| PS-06 | `derived.ovc_outcomes_v0_1` for new consumers | `derived.v_ovc_c_outcomes_v0_1` | No-new-consumers restriction approved | CONSUMER RESTRICTION EFFECTIVE; full replacement pending v1 ratification | SUPPORTING legacy / replay and migration verification only |
| PS-07 | Legacy dashboard projections | Versioned B-backed projections | Deferred | NOT EFFECTIVE: replacements and equivalence evidence absent | CONFLICTING |
| PS-08 | Current-inventory claims in `docs/workflows/WORKFLOW_CATALOG_v0_1.md` | `docs/workflows/WORKFLOW_CATALOG_v0_2.md` | New version approved | CURRENT CLAIMS REPLACED | v0.1 SUPPORTING historical; v0.2 AUTHORITATIVE current inventory |
| PS-09 | Current-flow claims in `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` | `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` | New version approved | CURRENT CLAIMS REPLACED | v0.1 SUPPORTING historical; v0.2 AUTHORITATIVE current claims |
| PS-10 | Current-state authority of `docs/pipeline/CURRENT_STATE_A_TO_D.md` and `docs/pipeline/CURRENT_STATE_INVARIANTS.md` | Commit-bound R0/R1 evidence | Reclassify claims | CURRENT CLAIMS REPLACED; files retained | SUPPORTING historical snapshots |
| PS-11 | Current classification authority of `docs/governance/CHANGE_TAXONOMY_v0_1.md` | `docs/governance/CHANGE_TAXONOMY_v0_2.md` | Conditional approval | NOT EFFECTIVE: ratification record absent | v0.1 SUPPORTING; v0.2 UNRESOLVED / IMPLEMENTED_UNRATIFIED |
| PS-12 | `artifacts/derived_validation/LATEST.txt` as active authority | `docs/phase_2_2/ACTIVE_REGISTRY_POINTERS_v0_1.json` | Conditional approval | EFFECTIVE: active-pointer record explicitly names the replacement | `LATEST.txt` SUPERSEDED as active pointer, retained for compatibility |
| PS-13 | AOC v0.1 as complete current inventory | Formal filtered additive catalog | Incompleteness finding approved; artifact supersession deferred | PARTIAL CATALOG RATIFICATION EFFECTIVE: QA07, QA09, and QA11 added; artifact supersession NOT EFFECTIVE | v0.1 remains authority for existing entries; v0.2 adds only approved operations |

## Effective Supersession Scope

Only PS-12 establishes a fully evidenced artifact-level supersession in this
correction.

PS-08, PS-09, and PS-10 replace current claims while preserving prior files
as historical evidence. PS-05 and PS-06 impose effective restrictions on new
execution and consumption without claiming that formal deprecation metadata
already exists.

The PS-13 additive catalog decision creates new operation authority without
creating a second effective artifact-level supersession.

All other proposals remain conditional, directional, or deferred.

## Non-Deletion Rule

No SQL file, table, view, workflow, contract, snapshot, or historical
governance document is deleted or rewritten by this register.
