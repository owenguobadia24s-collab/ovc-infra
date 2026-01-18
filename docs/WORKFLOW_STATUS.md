# Workflow Status (OVC v0.1.1 ingest)

## Current state (main + branches)
- main enforces MIN v0.1.1 in `infra/ovc-webhook/src/index.ts` (strict key order/type checks, /tv accepts raw exports, /tv_secure requires JSON). The ret semantic check is disabled for ingest stability.
- MIN contract validation is wired through `tools/validate_contract.py`, `tools/validate_contract.ps1`, and `tests/test_min_contract_validation.py`.
- Pine MIN export alignment is documented in `docs/pine_export_consistency.md`.
- Branches still carrying unmerged commits: `pr/infra-min-v0.1.1` (contains two commits not on main; review before merge/delete).
- Branches already merged into main: `pr/pine-min-export-v0.1_min_r1` and `origin/wip/infra-contract-validation`.

## Option A status (Logging Foundations & Validation Normalization)
- Status: COMPLETE and LOCKED.
- Guarantees: canonical MIN facts land in `ovc.ovc_blocks_v01_1_min` via P1/P2; core validation always runs; derived validation is conditional and skipped when absent.
- Not covered: derived features, new pipelines, or any Option B meaning layers; no changes to ingestion logic or Neon schemas.

## Pipeline status summary
- P1: PARTIAL (env-dependent, structurally sound).
- P2: PASS (canonical backfill writes to `ovc.ovc_blocks_v01_1_min`).
- P3: OPTIONAL / PARTIAL (derived, non-blocking).
- P4: PASS (core validation always runs; derived conditional).

## Validation pack behavior
- Core validation is unconditional.
- Derived validation is conditional and skipped when absent.

## Next Phase: Option B
- Allowed inputs: canonical facts in `ovc.ovc_blocks_v01_1_min`, raw capture ledger, and existing validation artifacts.
- Prohibited: mutating or reclassifying canonical facts.
- Requirement: all meaning layers must be replayable and fully derived from canonical inputs.

## Source of truth paths
- Worker: `infra/ovc-webhook/src/index.ts`
- Contract: `contracts/export_contract_v0.1.1_min.json`
- Validator: `tools/validate_contract.py`, `tools/validate_contract.ps1`
- Fixtures: `tests/sample_exports/min_001.txt`
- Logging doctrine: `docs/ovc_logging_doctrine_v0.1.md`
- Pipeline status harness: `scripts/pipeline_status.py`

## What changed today
- Added/locked MIN v0.1.1 contract + fixture sample (scheme_min = `export_contract_v0.1_min_r1`).
- Tightened MIN validation and tests to match the v0.1.1 contract.
- Documented Pine export alignment for the MIN contract.
- Disabled ret semantic check in the Worker for v0.1 ingest stability.

## Canonical commands (PowerShell)

### Repeatable local verification (validator + optional tests)
```powershell
.\scripts\verify_local.ps1
```

### Pipeline status harness (detect-only)
```powershell
python .\scripts\pipeline_status.py --mode detect
```

### P2 weekday green run (canonical backfill + validation)
```powershell
$env:BACKFILL_DATE_NY="2024-01-10"
python .\src\backfill_oanda_2h_checkpointed.py
python .\scripts\pipeline_status.py --mode detect --ignore-unknown
python .\src\validate_day.py --symbol GBPUSD --date_ny 2024-01-10
```
Idempotency check: rerun the backfill command; expect `inserted_est=0`.

### Validate an export locally
```powershell
python -m tools.validate_contract contracts/export_contract_v0.1.1_min.json tests/sample_exports/min_001.txt
```
```powershell
.\tools\validate_contract.ps1 -SampleExport tests\sample_exports\min_001.txt
```

### Deploy the worker
```powershell
.\scripts\deploy_worker.ps1
```

### POST a sample export to /tv
```powershell
curl.exe -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"
```

### Confirm insert in Neon (SQL)
```sql
select block_id, sym, date_ny, bar_close_ms, ingest_ts
from ovc.ovc_blocks_v01_1_min
where block_id = '20260116-I-GBPUSD'
order by ingest_ts desc
limit 5;
```

## If you see X error, do Y
- "contract not found" or "No line starting with 'ver='" -> run from repo root or use `scripts\verify_local.ps1`.
- "wrangler deploy" fails with entrypoint errors -> run from `infra/ovc-webhook` and confirm `wrangler.jsonc` has `"main": "src/index.ts"`.
- "column does not exist" from Neon -> compare the insert column list in `infra/ovc-webhook/src/index.ts` to your `ovc.ovc_blocks_v01_1_min` schema.
- `curl: (26) Failed to open/read local data` -> use `curl.exe` and the relative path `@tests/sample_exports/min_001.txt`.
- "Invalid export: ... key order mismatch/unknown keys" -> validate against `contracts/export_contract_v0.1.1_min.json` and confirm `scheme_min=export_contract_v0.1_min_r1` in the export string.
