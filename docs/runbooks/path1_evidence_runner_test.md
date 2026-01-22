# Path1 Evidence Runner - End-to-End Test Protocol

This runbook validates the Path1 Evidence Runner workflow end-to-end: evidence branch creation, PR creation/merge, artifact upload, and ledger updates on `main`.

## Prerequisites
- GitHub CLI authenticated with access to the repo.
- Permissions to dispatch workflows and view PRs/artifacts.
- Local clone of the repo with `origin` pointing to the GitHub repository.

## 1) Trigger the workflow
UI steps:
1. Go to Actions → "Path1 Evidence Runner".
2. Click "Run workflow".
3. Select branch `main` and run.

CLI:
Command: `gh workflow run "Path1 Evidence Runner" --ref main`

## 2) Locate the run
UI steps:
1. In Actions → "Path1 Evidence Runner", open the newest run.
2. Confirm the run is for branch `main` and note the run ID.

CLI:
Command: `gh run list --workflow "Path1 Evidence Runner" --branch main --limit 5`
Then: `gh run view <RUN_ID>`

## 3) Verify evidence branch creation
UI steps:
1. Open the run logs.
2. Confirm the step "Create evidence branch" ran.
3. Confirm "Push ledger" ran when changes exist.

CLI:
Command: `gh run view <RUN_ID> --log | rg "Create evidence branch|Push ledger"`
Then: `gh api repos/:owner/:repo/branches/evidence/path1-<run_id>`

## 4) Verify PR creation and merge/auto-merge
UI steps:
1. Open the PR created by the run.
2. Confirm base is `main`, head is `evidence/path1-<run_id>`.
3. Confirm it is merged or auto-merge is enabled.

CLI:
Command: `gh pr list --state all --search "path1: ledger update" --limit 5`
Then: `gh pr view <PR_NUMBER> --json title,baseRefName,headRefName,state,autoMergeRequest,mergeCommit`

## 5) Verify branch deletion
After merge, confirm the evidence branch is deleted.

CLI:
Command: `gh api repos/:owner/:repo/branches/evidence/path1-<run_id>`
Expect a 404 if deleted.

## 6) Verify ledger changes landed on `main`
Fetch the latest `main` and inspect the commit log:
Command: `git fetch origin main`
Then: `git log origin/main -n 5 --oneline`

Confirm the ledger update commit:
Command: `git log origin/main -n 20 --oneline | rg "path1: ledger update"`

Inspect the files in the merge commit:
Command: `git show --name-only <MERGE_COMMIT_SHA>`

## 7) Download and inspect artifacts
UI steps:
1. Open the run page.
2. Download the artifact named `path1-ledger-run-<run_id>`.

CLI:
Command: `gh run download <RUN_ID> -n path1-ledger-run-<run_id>`

Inspect:
- `git_status.txt`
- `git_diff_name_only.txt`
- `runner.log`
- `path1_summary.json` (if present)

## 8) Validate no-change behavior
If the run produced no ledger changes:
- No PR should exist for the run.
- The run should still upload artifacts.

CLI:
Command: `gh pr list --state all --search "path1: ledger update (run <RUN_ID>)"`
Then: `gh run view <RUN_ID> --json artifacts`

## Notes
- If the runner fails but ledger changes exist, the PR should still be created and auto-merged.
- If the runner fails and no ledger changes exist, the workflow should complete successfully with a warning in logs.