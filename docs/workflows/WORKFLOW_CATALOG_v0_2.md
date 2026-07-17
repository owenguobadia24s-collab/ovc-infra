# Workflow Catalog v0.2

**Version:** 0.2  
**Status:** RATIFIED_CURRENT_CLAIMS_AUTHORITY  
**Date:** 2026-07-16  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`  
**Prior version:** `docs/workflows/WORKFLOW_CATALOG_v0_1.md`  
**Supersession scope:** Current inventory and execution-disposition claims
only. v0.1 remains historical evidence.

This catalog records repository workflow definitions and their R1 authority
disposition. It does not change a workflow or prove deployed GitHub trigger
state.

## Current Repository Inventory

| Workflow | Repository triggers | Bound surface | R1 disposition |
|---|---|---|---|
| `.github/workflows/append_sentinel.yml` | Manual; PR/push on `maintenance/sentinel` | `scripts/sentinel/append_sentinel.py --verify` | CONTROL / UNRESOLVED authority |
| `.github/workflows/backfill_m15.yml` | Manual | M15 checkpointed backfill | A support / manual |
| `.github/workflows/backfill_then_validate.yml` | Manual | A backfill, B compute, QA validation | Canonical manual path, DEGRADED because C3 arguments are incomplete |
| `.github/workflows/backfill.yml` | Manual; `17 */6 * * *` | Checkpointed 2H backfill | Canonical scheduled A operation |
| `.github/workflows/change_classifier.yml` | PR | Change classifier | CONTROL / IMPLEMENTED_UNRATIFIED pending PS-11 |
| `.github/workflows/ci_pytest.yml` | PR; push to `main` | Test suite | Canonical QA gate |
| `.github/workflows/ci_schema_check.yml` | PR; push to `main`; manual | Runtime object verification and migration-ledger syntax | QA gate with incomplete migration verification |
| `.github/workflows/ci_workflow_sanity.yml` | PR | Workflow syntax, permissions, and script references | QA gate; current repository still contains known workflow defects |
| `.github/workflows/design_record_engine_ci.yml` | None; file is zero bytes | No executable workflow definition | CONTROL scaffold / NOT ACTIVE / UNRESOLVED |
| `.github/workflows/main.yml` | Manual; `0 */6 * * *` | Queue-based Path1 runner | NONCONFORMING; scheduled production use rejected |
| `.github/workflows/notion_sync.yml` | Manual in contained repository state | Notion sync | NONCONFORMING; not authorized for new production execution |
| `.github/workflows/ovc_option_c_schedule.yml` | Manual in contained repository state | Option C runner | NONCONFORMING; not authorized for new production execution |
| `.github/workflows/path1_evidence_queue.yml` | Manual | Queue-based Path1 runner | Historical/manual recovery candidate only; no canonical queue mutation |
| `.github/workflows/path1_evidence.yml` | Manual; `15 3 * * *` | Range-based Path1 runner | Canonical Path1 production path |
| `.github/workflows/path1_replay_verify.yml` | Manual; `0 3 * * *` | Structural replay verification | Canonical support operation, runtime DEGRADED by latest R0 failure |
| `.github/workflows/repo_cartographer.yml` | Manual; PR/push on `main` and `maintenance/sentinel` | Repo Cartographer | CONTROL / UNRESOLVED authority; declared stable outputs incomplete |

## Production Scheduling Ruling

Authorized canonical schedules in repository governance:

| Workflow | Schedule | Authority |
|---|---|---|
| `.github/workflows/backfill.yml` | `17 */6 * * *` | Canonical Option A |
| `.github/workflows/path1_evidence.yml` | `15 3 * * *` | Canonical range-based Path1 |
| `.github/workflows/path1_replay_verify.yml` | `0 3 * * *` | Canonical replay support, currently degraded |

The `0 */6 * * *` schedule in `.github/workflows/main.yml` is not authorized
as a canonical production path. Its continued presence is implementation
nonconformance, not a second source of workflow authority.

Option C and Notion are manual-only in the contained repository state. R0
observed remote scheduled runs after local containment, so deployed trigger
state remains conflicting until verified.

## Historical and Recovery-Only Workflows

Queue-based workflows and files may be retained for historical analysis or a
future controlled recovery procedure. They must not:

- run on a production schedule;
- mutate canonical queue state;
- replace `scripts/path1/run_evidence_range.py`; or
- establish a ledger other than `reports/path1/evidence/INDEX.md`.

## New-Execution Gates

| Workflow | Gate before new production execution |
|---|---|
| `.github/workflows/ovc_option_c_schedule.yml` | Ratify Option C v1; bind runner to `derived.v_ovc_c_outcomes_v0_1`; align evaluation contract and QA |
| `.github/workflows/notion_sync.yml` | Invoke `scripts/export/notion_sync.py`; source outcomes from the B-backed C view; verify external projection schema |
| `.github/workflows/path1_evidence_queue.yml` | Controlled manual recovery contract only; no canonical queue mutation |
| `.github/workflows/main.yml` | Remove scheduled queue role in later authorized implementation work |

## Non-Authorization

This catalog does not edit workflows, alter schedules, resume automation,
deploy GitHub changes, or authorize R2.
