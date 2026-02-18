# FAILURE_REPORT.md

## Missing inputs
- Expected selector keys: `status`, `run_ts`, `run_id`
- Observed ledger keys (single record): artifacts_path, generated_utc, head_commit, manifest_sha256, ruleset_id, ruleset_sha256, run_fingerprint, run_id, seal_sha256, summary_counts, tracked_list_sha256, untracked_visible_list_sha256
- Missing selector keys: status, run_ts
- Selection failure reasons:
  - Required selector key missing in ledger row: status
  - Required selector key missing in ledger row: run_ts

## Invalid seals
- UNKNOWN (no evidence)

## Policy violations
- UNKNOWN (no evidence)

## Recovery guidance (non-executable)
- Update ledger writer to include `status` + `run_ts`; rerun cartographer; reattempt Phase-B.