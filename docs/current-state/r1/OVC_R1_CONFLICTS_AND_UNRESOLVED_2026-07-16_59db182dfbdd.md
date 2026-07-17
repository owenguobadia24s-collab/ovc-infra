# OVC R1 Conflicts and Unresolved Authority

**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

## Operator Rulings Applied

The following authority questions are no longer open in R1:

- the B-backed `derived.v_ovc_c_outcomes_v0_1` is the required target for
  all new Option C and downstream Notion outcome operations;
- the range-based Path1 loop is canonical and queue-based production is
  rejected;
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` governs current data-flow
  claims while v0.1 is retained historically; and
- Option A semantic columns are temporarily tolerated physical legacy but
  are non-authoritative and denied to B, C, and D consumers.

These rulings resolve authority direction. They do not repair the
nonconforming implementation.

## Critical Conflicts

### R1-C01: Option C required authority is selected but not ratified or implemented

- Required target:
  `docs/contracts/option_c_outcomes_contract_v1.md` selects
  `derived.v_ovc_c_outcomes_v0_1`.
- Implementation:
  `scripts/run/run_option_c.sh` applies `sql/option_c_v0_1.sql`, and
  `sql/option_c_spotchecks.sql` plus `sql/option_c_run_report.sql` read
  `derived.ovc_outcomes_v0_1`.
- Machine contract:
  `contracts/eval_contract_v0.1.json` requires direct input from
  `ovc.ovc_blocks_v01_1_min`, including `pred_dir`.
- Deployed reality:
  R0 verified both outcomes views live.

The operator selected the B-backed view for all new operations. Full
`AUTHORITATIVE` classification remains blocked by the DRAFT v1 contract.
The legacy view and SQL are retained for replay and migration verification,
with no new operations or consumers.

### R1-C02: Notion projection path and source are both fractured

- `.github/workflows/notion_sync.yml` calls nonexistent
  `scripts/notion_sync.py`.
- The implementation exists at `scripts/export/notion_sync.py`.
- That implementation reads deprecated `derived.ovc_outcomes_v0_1`.
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` cites the stale script path
  and authorizes the same legacy outcomes source.
- R0 observed scheduled Notion failures on remote `main`.

`docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` corrects the governing
projection claim. The workflow and implementation remain nonconforming.

### R1-C03: R0 schedule containment is not live

- Local files retain only `workflow_dispatch` for Option C and Notion.
- R0 observed scheduled remote runs after those local edits.
- The current checkout is not remote default `main`.

R1 records local schedule state and deployed schedule state separately.

### R1-C04: Option A physical schema violates the declared canonical boundary

- `docs/contracts/A_TO_D_CONTRACT_v1.md` prohibits semantic fields in
  canonical tables.
- `docs/contracts/option_a1_bar_ingest_contract_v1.md` tolerates the same
  fields as non-authoritative physical legacy.
- R0 verified semantic columns including `state_tag`, `trend_tag`,
  `bias_mode`, `play`, and `pred_dir` in the live canonical table.
- The Worker still accepts and writes the MIN contract containing those
  fields.

No schema repair is made in R1.

### R1-C05: Worker run-report insert does not match deployed table schema

- `infra/ovc-webhook/src/index.ts` inserts `ended_at` and `meta`.
- `sql/02_tables_run_reports.sql` and R0 live evidence use `finished_at` and
  no `meta`.
- R0 verified zero live rows in `ovc.ovc_run_reports_v01`.
- Cloudflare deployment version is unverified.

### R1-C06: Rejected queue production path remains present and scheduled

- `docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md` bans mutable queue state.
- `.github/workflows/path1_evidence_queue.yml` is a queue runner.
- `.github/workflows/main.yml` schedules the queue path every six hours.
- `docs/workflows/WORKFLOW_CATALOG_v0_1.md` claims `main.yml` was deleted.
- R0 reported both Path1 range and queue workflows active.

The operator rejected queue-based Path1 as canonical. Queue files may remain
for historical analysis or controlled manual recovery only. The schedule in
`main.yml` and canonical queue mutation remain nonconforming implementation
state.

### R1-C07: C3 materialized automation cannot invoke its required contract

- `.github/workflows/backfill_then_validate.yml` supplies only `--symbol`.
- `src/derived/compute_c3_regime_trend_v0_1.py` requires
  `--threshold-pack` and `--scope`.
- `docs/contracts/option_b_derived_contract_v1.md` and
  `docs/contracts/c_feature_registry_freeze_v0_1.md` already record this
  conflict.

### R1-C08: Migration ledger exists but does not prove deployment

- `schema/applied_migrations.json` marks every entry `UNVERIFIED`.
- It references missing `sql/derived_v0_1.sql`.
- CI validates JSON syntax but not hashes, timestamps, actors, or applied
  definitions.
- R0 verified only a subset of runtime objects directly.

### R1-C09: Draft operations catalog was only partially ratified

- `docs/phase_2_2/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md` says it supersedes
  v0.1 but is DRAFT.
- Phase 2.3 explicitly states v0.1 remains authoritative.
- OP-QA07 through OP-QA11 exist in code and evidence but have no ratified
  operational authority.

The five operations were reviewed individually in
`docs/current-state/r1/OVC_R1_QA07_QA11_RATIFICATION_REVIEW_2026-07-16_59db182dfbdd.md`.
The operator approved OP-QA07, OP-QA09, and OP-QA11 with recorded
limitations. They are ratified by
`docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md`.

OP-QA08 remains conditional pending path-contract correction. OP-QA10
remains deferred pending contract/output-name correction.

### R1-C10: Historical workflow catalog does not describe current repository

`docs/workflows/WORKFLOW_CATALOG_v0_1.md` says `backfill.yml`,
`notion_sync.yml`, and `main.yml` were deleted. All three exist, and R0
reported them active.

`docs/workflows/WORKFLOW_CATALOG_v0_2.md` now governs current inventory
claims. v0.1 remains historical evidence.

## Significant Conflicts

| ID | Conflict |
|---|---|
| R1-C11 | Historical `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` contains internally inconsistent Notion rules. v0.2 replaces its current claims without modifying the file. |
| R1-C12 | `docs/architecture/dashboard_mapping_v0.1.md` and `docs/specs/system/dashboards_v0.1.md` project legacy Option C views that the Option C v1 contract deprecates. |
| R1-C13 | `schema/required_objects.txt` requires `derived.derived_runs`, while the active Option B contract deprecates it in favor of `derived.derived_runs_v0_1`. |
| R1-C14 | `sql/qa_validation_pack_derived.sql` joins the deprecated outcomes view, while the QA contract names the authoritative B-backed view. |
| R1-C15 | The Option B contract says no C3 test exists, but `tests/test_c3_regime_trend.py` exists. The implementation evidence is newer than the narrative. |
| R1-C16 | Repo Cartographer Phase B declares stable output paths that are absent from the current worktree. |
| R1-C17 | `docs/governance/OVC_GOVERNANCE_REFERENCE_v0.1.md` cites missing or moved paths including `PATH1_EXECUTION_MODEL.md` and `docs/ops/*`. |
| R1-C18 | `docs/operations/WORKFLOW_STATUS.md` declares Option B/C frozen and schedules active using stale paths and schedule state. |
| R1-C19 | Change Taxonomy v0.2 is implemented and CI-enforced but has no ratification record; PS-11 is not effective. |
| R1-C20 | `.github/workflows/design_record_engine_ci.yml` is zero bytes, so prior claims of active Design Record Engine CI were incorrect. |

## Unresolved Authority

| Object | Why unresolved |
|---|---|
| OP-QA08 | Conditional pending correction of its governance path contract. |
| OP-QA10 | Deferred pending correction of the contract/output-name mismatch. |
| Append Sentinel workflow and accounting branch | R1 records it as CONTROL/UNRESOLVED because its README policy is outside the authoritative operation catalog. |
| Repo Cartographer workflow and ownership outputs | R1 records it as CONTROL/UNRESOLVED because operational catalog authority and required outputs are incomplete. |
| Design Record Engine | Scripts and tests exist, but its named CI file is zero bytes and no ratified control authority exists. |
| Phase 3 control panel | R1 records it as CONTROL/UNRESOLVED because its local read-only contract has no placement in the operational governance spine. |
| Cloudflare Worker deployment | R0 could not verify live version, timestamp, or secrets. |
| R2 bucket `ovc-raw-events` | Declared in Wrangler config; live binding and contents unverified. |
| Notion databases | Secret names are known; schema, active projection state, and last successful sync are unverified. |
| Materialized B tables and QA tables | Repository DDL exists; R0 did not verify live deployment. |
| RES/LID evidence views and state-plane views | Repository definitions exist; R0 verified only the DIS evidence view. |

## Closure State

Authority rulings are recorded in
`docs/current-state/r1/OVC_R1_OPERATOR_DECISION_LEDGER_2026-07-16_59db182dfbdd.md`.
No implementation conflict is silently treated as repaired. R1 is closed as
`PASS_WITH_CARRIED_UNRESOLVED_ITEMS`.

R2 remains unauthorized pending a separate operator decision. Option C v1
ratification also remains separate.
