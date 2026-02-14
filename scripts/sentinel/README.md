# Append Sentinel v0.1

`append_sentinel.py` maintains an append-only commit ledger and deterministic overlay.

## Usage

```bash
python scripts/sentinel/append_sentinel.py
python scripts/sentinel/append_sentinel.py --verify
python scripts/sentinel/append_sentinel.py --allow-unknown
```

Install pre-push verification hook:

```bash
bash scripts/sentinel/install_pre_push_hook.sh
```

## Invariants

- Reads `scripts/sentinel/sentinel_state.json` for `last_processed_commit`, `ledger_path`, and `overlay_path`.
- State is an operational pointer, not part of the historical ledger of change.
- Processes `last_processed_commit..HEAD` via `git rev-list --reverse --topo-order`.
- Appends exactly one ledger row for each non-sentinel-only commit.
- Skips commits that touch only managed sentinel paths and advances state across those commits.
- Exception: commits that touch only `scripts/sentinel/sentinel_state.json` are excluded from state advancement to prevent a self-referential verify loop.
- Rebuilds overlay deterministically from the full ledger using current classifier rules.
- Fails hard on schema mismatch, duplicate SHA, non-append mutation, and blocked classification (unless `--allow-unknown`).
- `--verify` never writes files and fails if any file would change.
- `--verify` can fail even with no new commits if `scripts/governance/classify_change.py` changes, because overlay is reclassified from the full ledger on every run.
- Operational consequence: classifier rule changes require running sentinel and committing overlay/seal updates.
