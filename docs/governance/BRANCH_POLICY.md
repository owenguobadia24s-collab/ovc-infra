# Branch Policy

## Safe to delete now (merged into main)
- local: `pr/pine-min-export-v0.1_min_r1` (merged via PR #6)
- remote: `origin/pr/pine-min-export-v0.1_min_r1` (merged into main)
- remote: `origin/wip/infra-contract-validation` (merged via PR #5)
- remote: `origin/codex/complete-step-8b-hardening-for-ovc` (merged into main)
- remote: `origin/codex/create-ovc-current-workflow-documentation` (merged into main)
- remote: `origin/codex/fix-export_contract_v0.1_full.json` (merged into main)
- remote: `origin/codex/fix-min-contract-schema-in-exportmin` (merged into main)

## Keep for review (not merged)
- `pr/infra-min-v0.1.1` (contains unmerged commits; review before merge/delete)

## Naming convention (new work)
- `pr/<area>-<topic>-vX.Y`
- `wip/<area>-<topic>`

## Rules
- Never develop directly on main; always work on PR branches.
- Never mix pine + infra in the same PR unless explicitly requested.
