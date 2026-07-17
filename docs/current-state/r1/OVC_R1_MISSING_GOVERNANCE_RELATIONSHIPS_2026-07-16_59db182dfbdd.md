# OVC R1 Missing Governance Relationships

**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

This is a gap list, not new doctrine.

| ID | Missing relationship | Evidence |
|---|---|---|
| MG-02 | Final authority for OP-QA08 and OP-QA10 | QA08 remains conditional; QA10 remains deferred |
| MG-03 | Operation IDs for Append Sentinel, Repo Cartographer, Design Record Engine CI, and Phase 3 control panel | Active components exist outside AOC v0.1/v0.2 |
| MG-04 | Explicit replacement chain from Option C legacy contract/view to B-backed outcomes view | Contract states resolution, but deprecation metadata is absent |
| MG-05 | Versioned machine eval contract for the authoritative outcomes view | `contracts/eval_contract_v0.1.json` describes legacy direct-A semantics |
| MG-06 | Notion implementation conformance and external projection schema evidence | Data-flow canon v0.2 binds the real path and required B-backed source; workflow/script remain nonconforming |
| MG-07 | Notion database schema and property-version evidence | Only secret names and code mappings are available |
| MG-08 | Live Cloudflare Worker version, deployment timestamp, and secret-name evidence | R0 Cloudflare access unavailable |
| MG-09 | R2 bucket live binding/retention authority | Wrangler config declares binding; runtime unverified |
| MG-10 | Verified migration-to-runtime signature ledger | Ledger has no hashes, actors, timestamps, or verified statuses |
| MG-11 | Migration records for state-plane views, RES/LID evidence views, score views, QA schema, Notion state, and C3 materialized objects | Files exist outside the current applied migration ledger |
| MG-12 | Runtime verification for materialized C1/C2/C3 and QA tables | R0 did not sample them |
| MG-13 | CI gate enforcing Option B denylist against A1 semantic legacy columns | Active Option B contract marks this deferred |
| MG-14 | CI gate enforcing C canonical-column allowlist | C feature freeze says policy-only |
| MG-15 | C3 workflow-to-threshold-pack binding | Workflow omits required selector arguments |
| MG-16 | Controlled manual-recovery contract for retained queue tooling and removal of scheduled production use | Operator rejected canonical queue production; implementation remains present |
| MG-19 | Decision records for major architecture transitions | `docs/governance/decisions.md` contains only one short 2026-01-14 entry |
| MG-20 | Versioned migration, equivalence, and rollback evidence for eventual Option A semantic-column removal | Operator decision now records temporary physical tolerance and downstream denial |
| MG-21 | Formal ADR for dual C3 models: inline-view reference semantics vs threshold-pack certified table | Freeze records mismatch but not a final convergence decision |
| MG-22 | Authority relationship for dashboard projections after legacy C deprecation | Dashboard specs still point to legacy projections |
| MG-23 | Schema-required object alignment for `derived.derived_runs` vs `derived.derived_runs_v0_1` | Required-object file and active B contract disagree |
| MG-24 | QA validation-pack authority for authoritative C view | Derived QA pack joins legacy outcomes |
| MG-25 | Repo Cartographer stable-output publication evidence | Phase B required outputs are absent |
| MG-26 | Branch-to-authority record for maintenance/sentinel vs main | Sentinel README declares branch-specific authority without AOC mapping |
| MG-28 | Formal ratification record for `docs/contracts/option_c_outcomes_contract_v1.md` | Required before the B-backed C view can be classified fully `AUTHORITATIVE` |
| MG-29 | Path-contract correction for OP-QA08 and contract/output-name correction for OP-QA10 | Required before separate ratification decisions |
| MG-30 | Ratification record for Change Taxonomy v0.2 | Implementation and CI exist, but PS-11 condition is not met |

## Relationships Closed by This Correction

| Former gap | Closure evidence |
|---|---|
| Current workflow inventory | `docs/workflows/WORKFLOW_CATALOG_v0_2.md` covers all 16 repository workflow files |
| Current data-flow authority | `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` records the approved Option C, queue, and Option A rulings |
| Current-state snapshot role | PS-10 classifies frozen current-state files as historical snapshots while R0/R1 remain commit-bound |
| Queue authority direction | Operator ledger rejects queue production and preserves range-based Path1 as canonical |
| Option A temporary retention decision | Operator ledger records physical tolerance, non-authority, and B/C/D denial |
| R1 operator acceptance | `docs/current-state/r1/OVC_R1_CLOSURE_DECISION_2026-07-16_59db182dfbdd.md` closes R1 as `PASS_WITH_CARRIED_UNRESOLVED_ITEMS` |
| Partial operations-catalog ratification | `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md` adds only OP-QA07, OP-QA09, and OP-QA11 |
