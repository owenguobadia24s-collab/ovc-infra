# OVC Sentinel Atomic Commit Runbook v0.1

## Purpose
Execute the Sentinel v0.1 local workflow to produce a deterministic atomic commit containing sentinel system files and synced catalog/state/seal artifacts.

## Hard Invariants
- Use explicit script invocations:
  - `python scripts/sentinel/append_sentinel.py --allow-unknown`
  - `python scripts/sentinel/append_sentinel.py --verify`
  - `bash scripts/sentinel/install_pre_push_hook.sh`
- Stash unrelated edits by path:
  - `git stash push -m "stash: exclude Tetsu for sentinel atomic commit" -- Tetsu/`
- Keep `sentinel_blocked_push.log` local only (never stage it).
- Trip commit file must be outside managed paths:
  - `tools/_sentinel_pre_push_trip_marker.md`

## A) Preflight
1. `git status --porcelain`
2. `git rev-parse --show-toplevel`
3. `git branch --show-current`
4. `git stash push -m "stash: exclude Tetsu for sentinel atomic commit" -- Tetsu/`

## B) Mutate + Verify
1. `python scripts/sentinel/append_sentinel.py --allow-unknown`
2. `git status --porcelain`
3. `git diff --stat`
4. `python scripts/sentinel/append_sentinel.py --verify`

## C) Install Pre-Push Hook
1. `bash scripts/sentinel/install_pre_push_hook.sh`
2. `ls -la .git/hooks/pre-push`
3. Print first 80 lines of `.git/hooks/pre-push`.

## D) Prove Hook Blocks When Behind
1. `git switch -c test/prepush-sentinel`
2. `echo "trip hook" >> tools/_sentinel_pre_push_trip_marker.md`
3. `git add tools/_sentinel_pre_push_trip_marker.md`
4. `git commit -m "test: create non-sentinel commit to trip pre-push"`
5. `git push -u origin test/prepush-sentinel 2>&1 | tee sentinel_blocked_push.log`
6. Repair with:
   - `python scripts/sentinel/append_sentinel.py --allow-unknown`
   - `python scripts/sentinel/append_sentinel.py --verify`
7. Stage repair set:
   - `git add scripts/sentinel/sentinel_state.json docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.json docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.sha256 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.json docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.sha256`
8. `git commit -m "chore(sentinel): ingest commit ledger + rebuild overlay"`
9. `git push -u origin test/prepush-sentinel`
10. Return and clean branch:
   - `git switch <original-branch>`
   - `git branch -D test/prepush-sentinel`
   - `git push origin --delete test/prepush-sentinel`

## E) Atomic Sentinel Commit
1. Re-sync:
   - `python scripts/sentinel/append_sentinel.py --allow-unknown`
   - `python scripts/sentinel/append_sentinel.py --verify`
2. Stage exact set:
   - `git add scripts/sentinel/ .github/workflows/append_sentinel.yml tests/test_append_sentinel.py docs/runbooks/SENTINEL_COMMIT_RUNBOOK_v0.1.md docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.json docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.sha256 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.json docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.sha256`
3. Validate stage:
   - `git diff --cached --stat`
   - `git diff --cached`
4. Commit exact message:
   - `git commit -m "feat(sentinel): append-only commit ingestion + deterministic overlay (v0.1)"`
5. Final checks:
   - `python scripts/sentinel/append_sentinel.py --verify`
   - `git status --porcelain`
6. Push:
   - `git push`

## Deliverables
- Full command transcript.
- `git status --porcelain` snapshots after phases B, D, and E.
- Blocked push output (`sentinel_blocked_push.log`).
- Final atomic commit hash.
- Final verify pass confirmation.