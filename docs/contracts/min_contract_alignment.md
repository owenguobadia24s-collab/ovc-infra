# MIN Contract Alignment v0.1.1 (Infra)

## End-to-end flow
TradingView (Pine) export string → local validator → Cloudflare Worker `/tv` → Neon table `ovc.ovc_blocks_v01_1_min`.

## Validate locally
Python validator:
```
python tools/validate_contract.py contracts/export_contract_v0.1.1_min.json tests/sample_exports/min_001.txt
```

PowerShell wrapper:
```
.\tools\validate_contract.ps1 -SampleExport tests\sample_exports\min_001.txt
```

POST to worker:
```
curl -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"
```

## Verify ingestion in Neon
```
select block_id, sym, date_ny, bar_close_ms, state_key, ingest_ts
from ovc.ovc_blocks_v01_1_min
where block_id = '20260116-I-GBPUSD'
order by ingest_ts desc
limit 5;
```
