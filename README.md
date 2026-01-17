# ovc-infra

## Lock the Win (v0.1 ingest)

### Verify + Deploy + Post
- Local verify: `.\scripts\verify_local.ps1`
- Local post to wrangler dev: `curl.exe -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"`
- Deploy: `.\scripts\deploy_worker.ps1`
- Post to prod endpoint: `curl.exe -X POST https://ovc-webhook.owenguobadia24s.workers.dev/tv --data-binary "@tests/sample_exports/min_001.txt"`

### Neon confirm (SQL)
```sql
select block_id, sym, date_ny, bar_close_ms, ingest_ts
from ovc.ovc_blocks_v01_1_min
where block_id = '20260116-I-GBPUSD'
order by ingest_ts desc
limit 5;
```

### Release tag (manual)
```powershell
git checkout main
git pull
git tag -a ovc-v0.1-ingest-stable -m "OVC v0.1 ingest stable (MIN v0.1.1; /tv raw; ret semantics disabled)"
git push origin ovc-v0.1-ingest-stable
```

### Branch hygiene checklist (per `docs/BRANCH_POLICY.md`)
- [ ] Safe to delete now (merged into main): `pr/pine-min-export-v0.1_min_r1`, `origin/pr/pine-min-export-v0.1_min_r1`, `origin/wip/infra-contract-validation`, `origin/codex/complete-step-8b-hardening-for-ovc`, `origin/codex/create-ovc-current-workflow-documentation`, `origin/codex/fix-export_contract_v0.1_full.json`, `origin/codex/fix-min-contract-schema-in-exportmin`
- [ ] Keep for review (manual decision required): `pr/infra-min-v0.1.1`
- [ ] Local delete (manual, only after confirming merged):
  ```powershell
  git branch -d pr/pine-min-export-v0.1_min_r1
  ```
- [ ] Remote delete (manual, only after confirming merged):
  ```powershell
  git push origin --delete pr/pine-min-export-v0.1_min_r1
  git push origin --delete wip/infra-contract-validation
  git push origin --delete codex/complete-step-8b-hardening-for-ovc
  git push origin --delete codex/create-ovc-current-workflow-documentation
  git push origin --delete codex/fix-export_contract_v0.1_full.json
  git push origin --delete codex/fix-min-contract-schema-in-exportmin
  ```
