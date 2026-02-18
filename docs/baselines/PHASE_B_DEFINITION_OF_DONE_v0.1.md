# PHASE_B_DEFINITION_OF_DONE v0.1

## Canonical Command Order

```bash
python scripts/repo_cartographer/cartographer.py run
python scripts/repo_cartographer/cartographer.py verify
python scripts/repo_cartographer/phase_b_latest_ok_run.py --strict-verify
python scripts/repo_cartographer/phase_b6_publish_latest_ownership_summary.py
python scripts/repo_cartographer/phase_b7_unknown_frontier.py
```

## Fail-Closed Rule

- The chain is strictly ordered.
- Any non-zero step fails the chain immediately.
- Fail-closed exit code is `2`.

## Stable Output Paths (Case-Sensitive)

- `docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json`
- `docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.md`
- `docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.receipt.json`
- `docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json`
- `docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt`

## Pointer Contract Keys

- `LATEST_OK_RUN_ID`
- `LATEST_OK_RUN_TS`
- `ok`
- `ledger_manifest_match`
- `ledger_seal_match`
- `manifest_sidecar_match` (`MANIFEST.sha256` sidecar)
- `seal_sidecar_match` (`SEAL.sha256` sidecar)

## Required Ledger Fields For Gate-Open Runs

- `manifest_sha256`
- `seal_sha256`

## Non-Goals

- No cartographer semantic redesign.
- No pipeline step reordering.
- No weakened verification or pointer gates.
- No fallback selectors or inferred substitutions.

## No Backfill Policy

- Historical ledger lines are not rewritten.
- Phase B completion is forward-only correctness for new runs.

## Phase B Completion Proof

Evidence artifacts:

- Run artifacts directory: `artifacts/repo_cartographer/<run_id>/`
- Run ledger row in: `docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl`
- Latest-OK pointer: `docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json`
- Published ownership summary + receipt:
  - `docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.md`
  - `docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.receipt.json`
- Published unknown frontier:
  - `docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json`
  - `docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt`
