# OVC R1 Closure Decision

**Decision:** PASS_WITH_CARRIED_UNRESOLVED_ITEMS  
**Decision date:** 2026-07-16  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`  
**R1 status:** CLOSED

## Approved Findings

- The separation between current authority and proposed supersession is
  approved.
- PS-01 and PS-11 conditions are accepted as not met.
- PS-12 is accepted as the only effective artifact-level supersession.
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` is authoritative for
  current data-flow claims.
- `docs/workflows/WORKFLOW_CATALOG_v0_2.md` is authoritative for current
  workflow inventory and execution-disposition claims.

## Operations Catalog Decision

`docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md` is ratified as an
additive extension to v0.1:

- OP-QA07 is approved with recorded limitations.
- OP-QA09 is approved with recorded limitations, including its carried
  dependency on conditional OP-QA08 output.
- OP-QA11 is approved with recorded limitations.
- OP-QA08 remains conditional pending path-contract correction.
- OP-QA10 remains deferred pending contract/output-name correction.

The v0.1 catalog remains authoritative for its existing entries. This
partial extension does not create an artifact-level supersession.

## Carried Unresolved Items

- Option C v1 contract ratification remains separate. The B-backed
  `derived.v_ovc_c_outcomes_v0_1` remains the required new-operation target
  but is not fully `AUTHORITATIVE`.
- OP-QA08 path-contract correction and ratification remain open.
- OP-QA10 contract/output-name correction and ratification remain open.
- PS-01 and PS-11 remain conditional and not effective.
- All implementation, deployment, workflow, schema, database, and external
  service conflicts documented by R1 remain carried unless explicitly
  resolved by this decision.

## R2 Decision Boundary

R2 is not authorized by R1 closure.

Starting R2 requires a separate, explicit operator authorization made after
this closure decision. No status, catalog, or authority classification in the
R1 packet may be interpreted as implicit R2 authorization.

