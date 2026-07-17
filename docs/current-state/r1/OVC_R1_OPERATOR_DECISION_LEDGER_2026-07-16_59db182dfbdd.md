# OVC R1 Operator Decision Ledger

**Status:** FINAL_OPERATOR_DECISIONS_RECORDED  
**Decision:** PASS_WITH_CARRIED_UNRESOLVED_ITEMS  
**Decision date:** 2026-07-16  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

This ledger records the operator rulings applied by the R1 correction pass.
It does not authorize R2, implementation repair, workflow mutation, schema
change, deployment, database mutation, or schedule resumption.

## Authority Rulings

| Ruling | Operator decision | R1 application | Remaining condition |
|---|---|---|---|
| Option C authority | `derived.v_ovc_c_outcomes_v0_1` is required for all new Option C outcome production and downstream Notion outcome projection | The B-backed view is recorded as the required target with `RATIFICATION_PENDING`; legacy direct-A outcomes are denied to new consumers | Ratify `docs/contracts/option_c_outcomes_contract_v1.md` before marking the replacement fully `AUTHORITATIVE` |
| Queue-based Path1 operation | Rejected as canonical | The range runner remains canonical; queue workflows are historical/manual-recovery only and are not authorized as scheduled production paths or canonical queue mutators | Remove scheduled production use and define a controlled recovery contract in later authorized work |
| Data-flow canon | Corrected version approved | `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` records current authority; v0.1 is retained as historical governance evidence | Implementation conformance remains later work |
| Option A semantic columns | Temporarily tolerated physical legacy | Columns may remain physically present, but are non-authoritative and denied to B, C, and D consumers | Physical removal requires a versioned migration with equivalence and rollback evidence |
| AOC v0.2 | Partial ratification approved | Formal additive catalog ratifies OP-QA07, OP-QA09, and OP-QA11 with limitations; OP-QA08 remains conditional and OP-QA10 deferred | QA08 and QA10 require separate correction and ratification decisions |

## Supersession Decisions

`Effective status` distinguishes an approved direction from a completed
authority transition.

| ID | Operator decision | Evidence check | Effective status | Historical retention and new execution |
|---|---|---|---|---|
| PS-01 | Approve only if the immutable replacement already satisfies the deprecation contract | NOT MET: no machine-readable deprecation record; v0.1.1 does not identify v0.1 as its prior object | CONDITIONAL_NOT_EFFECTIVE | v0.1 retained as supporting legacy; not represented as formally superseded |
| PS-02 | Defer until a versioned machine-readable replacement exists | Replacement machine contract does not exist | DEFERRED | Combined feature contract retained as supporting legacy; not new authority |
| PS-03 | Approve conditional on ratification of Option C v1 | v1 contract remains DRAFT | CONDITIONAL_NOT_EFFECTIVE | Old boundary retained historically; denied as authority for new Option C operations |
| PS-04 | Approve replacement direction; do not supersede before replacement exists | No new evaluation contract exists | DIRECTION_APPROVED_NOT_EFFECTIVE | v0.1 eval contract retained for historical replay only; not new-operation authority |
| PS-05 | Approve "no new operations"; retain for replay | Operator restriction is explicit; formal deprecation metadata remains absent | EXECUTION_RESTRICTION_EFFECTIVE | `sql/option_c_v0_1.sql` retained for historical replay; no new operations |
| PS-06 | Approve "no new consumers"; retain temporarily | Operator restriction is explicit; formal deprecation metadata remains absent | CONSUMER_RESTRICTION_EFFECTIVE | `derived.ovc_outcomes_v0_1` retained for replay and migration verification; no new consumers |
| PS-07 | Defer until replacements pass equivalence checks | No replacement projections or equivalence evidence exist | DEFERRED | Legacy projections remain conflicting; no replacement authority asserted |
| PS-08 | Approve creation of new workflow catalog; preserve v0.1 | `docs/workflows/WORKFLOW_CATALOG_v0_2.md` created by this correction | CURRENT_CLAIMS_REPLACED | v0.1 retained as historical inventory; v0.2 governs current inventory claims |
| PS-09 | Approve corrected data-flow canon; preserve v0.1 | `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` created by this correction | CURRENT_CLAIMS_REPLACED | v0.1 retained as historical governance evidence; v0.2 governs current flow claims |
| PS-10 | Reclassify frozen current-state documents as historical snapshots | R0 and R1 provide commit-bound current evidence | CURRENT_CLAIMS_REPLACED | Files remain preserved; only their current-state authority is withdrawn |
| PS-11 | Approve only if v0.2 implementation and ratification evidence are recorded | NOT MET: implementation and CI exist, but no ratification record exists | CONDITIONAL_NOT_EFFECTIVE | v0.1 retained as historical base; v0.2 remains implemented but unratified |
| PS-12 | Approve if active-pointer governance records the replacement | MET: `docs/phase_2_2/ACTIVE_REGISTRY_POINTERS_v0_1.json` explicitly selects the sealed replacement and marks `LATEST.txt` non-authoritative | EFFECTIVE | `artifacts/derived_validation/LATEST.txt` remains a backward-compatible historical pointer, not active authority |
| PS-13 | Approve incompleteness finding; defer artifact supersession | Filtered additive v0.2 catalog ratifies only QA07, QA09, and QA11 | PARTIAL_CATALOG_RATIFICATION_EFFECTIVE; ARTIFACT_SUPERSESSION_NOT_EFFECTIVE | v0.1 remains authority for existing entries; v0.2 adds only approved operations |

## Current Classification Rule

An artifact is not classified `SUPERSEDED` merely because:

- a newer file exists;
- an implementation has moved;
- a draft claims replacement; or
- an operator approves a future replacement direction.

Until all applicable conditions are met, the artifact is classified
`SUPPORTING`, `CONFLICTING`, or `UNRESOLVED`, with explicit retention and
new-execution restrictions.

## Final QA Operation Decisions

| Operation | Final decision |
|---|---|
| OP-QA07 | APPROVED_WITH_RECORDED_LIMITATIONS |
| OP-QA08 | CONDITIONAL_PENDING_PATH_CONTRACT_CORRECTION |
| OP-QA09 | APPROVED_WITH_RECORDED_LIMITATIONS |
| OP-QA10 | DEFERRED_PENDING_CONTRACT_OUTPUT_NAME_CORRECTION |
| OP-QA11 | APPROVED_WITH_RECORDED_LIMITATIONS |

## Review State

R1 is closed as `PASS_WITH_CARRIED_UNRESOLVED_ITEMS`.

R2 is not authorized. R2 requires a separate explicit operator decision.
Option C v1 ratification also remains a separate decision.
