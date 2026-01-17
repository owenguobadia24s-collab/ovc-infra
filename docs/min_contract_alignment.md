# MIN Contract Alignment (v0.1.1)

## What changed
- MIN export in Pine now matches `contracts/export_contract_v0.1.1_min.json` field order, names, and types.
- String fields are sanitized for `|`, `=`, and newlines; derived fields are deterministic.
- Worker validation aligns with contract keys/types, rejects unknown keys, and reports all missing required keys at once.
- Validator and tests use the frozen v0.1.1 MIN contract and fixtures.

## Validate locally
PowerShell validator (single-line summary):
```
.\tools\validate_contract.ps1 -SampleExport tests\sample_exports\min_001.txt
```

Direct Python:
```
python tools\validate_contract.py contracts\export_contract_v0.1.1_min.json tests\sample_exports\min_001.txt
```

POST to worker (plain /tv):
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
