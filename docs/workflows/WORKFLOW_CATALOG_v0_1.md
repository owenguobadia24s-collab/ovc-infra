# Workflow Catalog v0.1

> **Governance**: Each workflow has a single, well-defined purpose. No duplicates. All workflows require explicit `permissions:` blocks and must produce verifiable outputs.

## Active Workflows

| Filename | Display Name | Purpose | Status | Classification |
|----------|--------------|---------|--------|----------------|
| `backfill_m15.yml` | OVC Backfill (M15 Raw) | Backfill M15 granularity OANDA data to Neon | GREEN | SUPPORT |
| `backfill_then_validate.yml` | OVC Backfill then Validate (Range) | Canonical backfill + validation + derived compute pipeline | GREEN | CORE |
| `ovc_option_c_schedule.yml` | OVC Option C Schedule | Run Option C automation and spotchecks | GREEN | CORE |
| `path1_evidence.yml` | Path 1 Evidence Runner | Generate Path1 evidence studies over date range, commit to ledger | GREEN | CORE |
| `path1_replay_verify.yml` | Path1 Replay Verification | Structural replay verification of Path1 runs | GREEN | SUPPORT |
| `ci_workflow_sanity.yml` | CI: Workflow Sanity Checks | Lint and validate workflow YAML on PR | GREEN | SUPPORT |

## Deleted Workflows (v0.1 Cleanup)

| Filename | Reason |
|----------|--------|
| `backfill.yml` | Subsumed by `backfill_then_validate.yml` |
| `notion_sync.yml` | Broken script reference, no permissions, likely dead |
| `ovc_full_ingest.yml` | Stub workflow, overlaps with backfill_then_validate |
| `main.yml` | Duplicate Path1 runner using deprecated queue approach |

---

## Workflow Details

### backfill_m15.yml — OVC Backfill (M15 Raw)

| Field | Value |
|-------|-------|
| **Triggers** | `workflow_dispatch` |
| **Inputs** | `sym` (symbol), `date_from`, `date_to`, `dry_run` |
| **Secrets** | `DATABASE_URL`, `OANDA_API_TOKEN`, `OANDA_ENV` |
| **Permissions** | `contents: read` |
| **Concurrency** | None |
| **Scripts** | `src/backfill_oanda_m15_checkpointed.py` |
| **Outputs** | Artifact: `backfill-m15-run-artifacts` |
| **Persistence** | Artifacts-only (ephemeral) |

---

### backfill_then_validate.yml — OVC Backfill then Validate (Range)

| Field | Value |
|-------|-------|
| **Triggers** | `workflow_dispatch` |
| **Inputs** | `start_date`, `end_date`, `strict`, `missing_facts` |
| **Secrets** | `NEON_DSN`, `OANDA_API_TOKEN`, `OANDA_ENV` |
| **Permissions** | `contents: read` |
| **Concurrency** | None |
| **Scripts** | `src/backfill_oanda_2h_checkpointed.py`, `src/validate_range.py`, `src/derived/compute_c1_v0_1.py`, `src/derived/compute_c2_v0_1.py`, `src/validate/validate_derived_range_v0_1.py` |
| **Outputs** | Artifact: `ovc-run-{run_id}`, `run-artifacts-{run_id}` |
| **Persistence** | Artifacts-only (ephemeral diagnostics) |

---

### ovc_option_c_schedule.yml — OVC Option C Schedule

| Field | Value |
|-------|-------|
| **Triggers** | `schedule` (daily 06:15 UTC), `workflow_dispatch` |
| **Inputs** | `strict`, `spotchecks_only` |
| **Secrets** | `DATABASE_URL` |
| **Permissions** | `contents: read` |
| **Concurrency** | None |
| **Scripts** | `scripts/run/run_option_c.sh` |
| **Outputs** | Artifact: `option-c-reports-{run_id}`, `option-c-run-artifacts-{run_id}` |
| **Persistence** | Artifacts-only |

---

### path1_evidence.yml — Path 1 Evidence Runner

| Field | Value |
|-------|-------|
| **Triggers** | `schedule` (daily 03:15 UTC), `workflow_dispatch` |
| **Inputs** | `symbol`, `start_date`, `end_date`, `length_days`, `commit_results` |
| **Secrets** | `DATABASE_URL`, `NEON_DSN` |
| **Permissions** | `contents: write` |
| **Concurrency** | `group: path1-evidence`, `cancel-in-progress: false` |
| **Scripts** | `scripts/path1/run_evidence_range.py` |
| **Outputs** | Files committed: `reports/path1/evidence/INDEX.md`, `reports/path1/evidence/runs/{run_id}/`, `sql/path1/evidence/runs/{run_id}/` |
| **Persistence** | PR+merge ledger write (direct-push to main) |

---

### path1_replay_verify.yml — Path1 Replay Verification

| Field | Value |
|-------|-------|
| **Triggers** | `schedule` (daily 03:00 UTC), `workflow_dispatch` |
| **Inputs** | `max_runs`, `strict`, `report_json` |
| **Secrets** | None |
| **Permissions** | `contents: read` |
| **Concurrency** | None |
| **Scripts** | `scripts/path1_replay/run_replay_verification.py` |
| **Outputs** | Artifact: `path1-replay-report-{run_number}` |
| **Persistence** | Artifacts-only |

---

### ci_workflow_sanity.yml — CI: Workflow Sanity Checks

| Field | Value |
|-------|-------|
| **Triggers** | `pull_request` (paths: `.github/workflows/**`, `scripts/**`) |
| **Inputs** | None |
| **Secrets** | None |
| **Permissions** | `contents: read` |
| **Concurrency** | `group: ci-sanity-${{ github.ref }}`, `cancel-in-progress: true` |
| **Scripts** | Inline YAML/script validation |
| **Outputs** | Pass/fail status |
| **Persistence** | None (CI gate) |

---

## Governance Checklist

All active workflows MUST have:

- [x] `permissions:` block (least privilege)
- [x] Clear `workflow_dispatch` inputs (if manually runnable)
- [x] Deterministic output persistence model
- [x] No queue mutation as primary mechanism
- [x] Failure on empty output when ledger write expected
