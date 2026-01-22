# Path1 Replay Verification (Design Stub)

Structural-only implementation. Recompute is not implemented.

## Purpose

Prove reproducibility of the Path1 canonical ledger.
Reads Path1 ledger; never writes to it.

## Modes

- `structural`: validate folder layout + required files + metadata invariants (+ optional manifest presence)
- `recompute` (optional): rerun studies and compare outputs (expensive)

## Proposed CLI (sketch)

Entrypoint (proposed): `run_replay_verification.py`

Flags:
- `--repo-root <path>`: repository root
- `--run-id <id>` OR `--all`: select run(s) to verify
- `--strict`: fail on any deviation
- `--report-json <path>`: optional JSON output
- `--max-runs <n>`: limit runs when using `--all`

## Outputs

- Console: per-run OK/FAIL + summary counts
- Optional JSON report: run_id, mode, checks, failures, timestamps (observational only)

## Exit codes

- `0` = all checks passed
- `2` = verification failures (invariants broken)
- `3` = tooling/runtime error (missing inputs/crash)

## Windows pytest note

If pytest locks `.pytest-tmp`, use:
`python -m pytest -q --basetemp=.\.pytest-tmp2`

## Non-negotiables

- Never write into:
  - `reports/path1/evidence/INDEX.md`
  - `reports/path1/evidence/runs/**`
- Any manifests/hashes belong **inside run folders** only if/when spec allows, and must be append-only.
