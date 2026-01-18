# Tape Validation Harness (Single-Day)

Scope: validate OVC outputs vs TradingView 2H candles for a single NY trading day
(17:00 to 17:00 America/New_York). This harness writes validation artifacts to
`ovc_qa` only.

See `docs/ovc_logging_doctrine_v0.1.md` for the pipeline map and canonical paths.

## Env vars (set once)
Set one of these in `.env` at repo root. `validate_day.py` prefers `NEON_DSN` and
falls back to `DATABASE_URL`:
```
NEON_DSN=postgres://user:pass@host/db
DATABASE_URL=postgres://user:pass@host/db
```

## One-time setup
Create the QA schema:
```
psql -d $env:DATABASE_URL -f sql/qa_schema.sql
```

Ensure derived views exist (if not already applied):
```
psql -d $env:DATABASE_URL -f sql/derived_v0_1.sql
psql -d $env:DATABASE_URL -f sql/option_c_v0_1.sql
```

## Canonical run (from repo root)
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16
```
For first-pass sanity checks, use a weekday date (e.g., 2024-01-10) since weekend sessions can yield 0 candles.

Validation packs:
- Core pack always runs (facts/tape checks).
- Derived pack runs only if `derived.ovc_block_features_v0_1` exists; otherwise it prints a SKIPPED message.

Optional TradingView CSV load (2H export):
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16 --tv-csv C:\path\to\tv_export.csv
```
Expected headers include `time`, `open`, `high`, `low`, `close` (2H timeframe).

## HISTORICAL INGESTION (CSV) (EXPERIMENTAL - NON-CANONICAL)
Status: EXPERIMENTAL. This CSV path is not the canonical P2 workflow; canonical
P2 is `src/backfill_oanda_2h_checkpointed.py`.
Use this to backfill one NY trading day into `ovc.ovc_blocks_v01_1_min` before validation.

Steps:
1. Export a 2H TradingView CSV for the target day.
2. Run:
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16 --ingest-history-csv C:\path\to\tv_2h.csv
```
3. Expect `blocks_count=12`.

CSV locator (resilient path resolution):
- If the path is wrong, the tool searches common locations and can auto-pick the top match.
- Example with a placeholder filename:
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16 --ingest-history-csv "ovc_hist_test_2h.csv" --auto-pick
```
- Example using a search pattern:
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16 --csv-search "*hist*2h*.csv" --auto-pick
```

CSV timezone assumptions:
- CSV timestamps are treated as bar start times.
- Default CSV timezone is `America/New_York`.
- If your CSV uses a different timezone and `src/ingest_history_day.py` is present, run:
```
python .\src\ingest_history_day.py --symbol GBPUSD --date_ny 2026-01-16 --csv C:\path\to\tv_2h.csv --tz Europe/London
```
Then rerun `validate_day.py` without `--ingest-history-csv`.

Block letter mapping (NY 17:00 -> 17:00):
| Block | NY Time |
| --- | --- |
| A | 17:00-19:00 |
| B | 19:00-21:00 |
| C | 21:00-23:00 |
| D | 23:00-01:00 |
| E | 01:00-03:00 |
| F | 03:00-05:00 |
| G | 05:00-07:00 |
| H | 07:00-09:00 |
| I | 09:00-11:00 |
| J | 11:00-13:00 |
| K | 13:00-15:00 |
| L | 15:00-17:00 |

## Oanda-backed green run (no TradingView export)
Use the existing GitHub Actions workflow to fetch Oanda H1 data, export 12x 2H bars,
and run validation for a single NY day.

Workflow: `OVC FULL Ingest (manual)`
Inputs:
- symbol: GBPUSD
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD
- run_full_ingest: false
- run_validation: true
- validate_date_ny: YYYY-MM-DD (optional; defaults to start_date)

Local equivalent:
```
python .\scripts\oanda_export_2h_day.py --symbol GBPUSD --date-ny 2026-01-16
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16 --csv-search "*GBPUSD*dateNY_2026-01-16*2h*oanda*.csv" --auto-pick
```

Optional convenience wrapper:
```
.\scripts\validate_day.ps1 -DateNy 2026-01-16 -Symbol GBPUSD
```

The command prints the `run_id` and a ready-to-paste psql invocation. If `psql`
exists on PATH, it will run the validation pack automatically.

Derived/outcomes counts are optional: if the tables are missing, the harness
prints `SKIPPED` and continues. Use `--strict` to force a failure when those
tables are absent.

## Manual psql validation (PowerShell)
```
psql -d $env:DATABASE_URL `
  -v run_id='<uuid>' `
  -v symbol='GBPUSD' `
  -v date_ny='2026-01-16' `
  -v tolerance_seconds=10 `
  -v tolerance=0.00001 `
  -f sql/qa_validation_pack.sql
```
If you only set `NEON_DSN`, replace `$env:DATABASE_URL` with `$env:NEON_DSN`.

## Load TradingView OHLC manually (optional)
CSV columns:
`run_id,symbol,date_ny,block_letter,tv_open,tv_high,tv_low,tv_close,tv_ts_start_ny,source`

Example CSV row:
```
<uuid>,GBPUSD,2026-01-16,A,1.23456,1.23567,1.23321,1.23401,2026-01-16 17:00:00-05,csv
```

Load via psql:
```
\copy ovc_qa.tv_ohlc_2h (run_id,symbol,date_ny,block_letter,tv_open,tv_high,tv_low,tv_close,tv_ts_start_ny,source) from 'C:/path/to/tv_ohlc.csv' with (format csv, header true)
```

Manual insert (single row):
```
insert into ovc_qa.tv_ohlc_2h (
  run_id, symbol, date_ny, block_letter, tv_open, tv_high, tv_low, tv_close, tv_ts_start_ny, source
) values (
  '<uuid>', 'GBPUSD', '2026-01-16', 'A', 1.23456, 1.23567, 1.23321, 1.23401, '2026-01-16 17:00:00-05', 'manual'
);
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

## Common Errors
- Missing `NEON_DSN`/`DATABASE_URL`: add one to `.env` at repo root.
- Date format: use `YYYY-MM-DD`, for example `2026-01-16`.
- Running from the wrong directory: run from repo root or use `.\scripts\validate_day.ps1`.

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
