# Tape Validation Harness (Single-Day)

Scope: validate OVC outputs vs TradingView 2H candles for a single NY trading day
(17:00 to 17:00 America/New_York). This harness writes validation artifacts to
`ovc_qa` only.

## One-time setup
1) Create the QA schema:
```
psql -d $env:DATABASE_URL -f sql/qa_schema.sql
```

2) Ensure derived views exist (if not already applied):
```
psql -d $env:DATABASE_URL -f sql/derived_v0_1.sql
psql -d $env:DATABASE_URL -f sql/option_c_v0_1.sql
```

## Create a validation_run
Option A (script creates it automatically):
```
python src/backfill_day.py --symbol GBPUSD --date_ny 2026-01-16
```
The script prints a `run_id`. Keep it for all SQL and CSV loads.

Option B (manual SQL):
```
insert into ovc_qa.validation_run (run_id, symbol, date_ny, ovc_contract_version, status, notes)
values ('<uuid>', 'GBPUSD', '2026-01-16', 'v0.1', 'pending', 'manual');
```

## Single-day backfill (expected blocks + checks)
```
python src/backfill_day.py --symbol GBPUSD --date_ny 2026-01-16 --run-id <uuid> --strict
```
This seeds 12 expected blocks (A-L) in `ovc_qa.expected_blocks` and prints
counts for OVC blocks, derived features, and outcomes.

## Load TradingView OHLC (CSV or manual)
CSV columns:
`run_id,symbol,date_ny,block_letter,tv_open,tv_high,tv_low,tv_close,tv_ts_start_ny,source`

Example CSV row:
```
<uuid>,GBPUSD,2026-01-16,A,1.23456,1.23567,1.23321,1.23401,2026-01-16 17:00:00-05,csv
```

Load via psql:
```
\copy ovc_qa.tv_ohlc_2h (run_id,symbol,date_ny,block_letter,tv_open,tv_high,tv_low,tv_close,tv_ts_start_ny,source) \
  from 'C:/path/to/tv_ohlc.csv' with (format csv, header true)
```

Manual insert (single row):
```
insert into ovc_qa.tv_ohlc_2h (
  run_id, symbol, date_ny, block_letter, tv_open, tv_high, tv_low, tv_close, tv_ts_start_ny, source
) values (
  '<uuid>', 'GBPUSD', '2026-01-16', 'A', 1.23456, 1.23567, 1.23321, 1.23401, '2026-01-16 17:00:00-05', 'manual'
);
```

## Run the SQL validation pack
```
psql -d $env:DATABASE_URL \
  -v run_id=<uuid> \
  -v symbol=GBPUSD \
  -v date_ny=2026-01-16 \
  -v tolerance_seconds=10 \
  -v tolerance=0.00001 \
  -f sql/qa_validation_pack.sql
```

## Interpret PASS vs FAIL
PASS when:
- Count is 12 and no missing block letters.
- Boundary checks return zero rows (duration and schedule).
- `ovc_qa.ohlc_mismatch` contains only `is_match = true`.

FAIL when any of the above checks return rows or `is_match = false`.

Update the run status once validation is complete:
```
update ovc_qa.validation_run
set status = 'pass', notes = 'all checks ok'
where run_id = '<uuid>';
```

## Notion tape validation DB structure
Required properties:
- Run ID
- Symbol
- date_ny
- block_id
- block_letter
- Screenshot
- TradingView link
- What I see
- OVC says
- Verdict

Screenshot filename convention:
`GBPUSD__dateNY_YYYY-MM-DD__BLK_A__blockid_<id>.png`
