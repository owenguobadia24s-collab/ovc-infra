import argparse
import csv
import shutil
import subprocess
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from dateutil import parser as date_parser
import psycopg2

from backfill_day import load_env, parse_date, print_backfill_summary, resolve_dsn, run_backfill

REPO_ROOT = Path(__file__).resolve().parents[1]
SQL_PACK_PATH = REPO_ROOT / "sql" / "qa_validation_pack.sql"
NY_TZ = ZoneInfo("America/New_York")
PSQL_TOLERANCE_SECONDS = 10

TV_INSERT_SQL = """
insert into ovc_qa.tv_ohlc_2h (
  run_id,
  symbol,
  date_ny,
  block_letter,
  tv_open,
  tv_high,
  tv_low,
  tv_close,
  tv_ts_start_ny,
  source
)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


def _find_header(headers, options, label):
    for option in options:
        if option in headers:
            return headers[option]
    raise SystemExit(f"Missing {label} column in CSV. Expected one of: {', '.join(options)}")


def _parse_decimal(value: str, label: str, row_num: int) -> Decimal:
    raw = "" if value is None else str(value).strip()
    if not raw:
        raise SystemExit(f"Missing {label} value on CSV row {row_num}.")
    try:
        return Decimal(raw)
    except InvalidOperation as exc:
        raise SystemExit(f"Invalid {label} value on CSV row {row_num}: {raw}") from exc


def _parse_tv_timestamp(value: str, row_num: int) -> datetime:
    raw = "" if value is None else str(value).strip()
    if not raw:
        raise SystemExit(f"Missing timestamp on CSV row {row_num}.")
    if raw.replace(".", "", 1).isdigit():
        ts = float(raw)
        if ts > 1e10:
            ts /= 1000.0
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    else:
        try:
            dt = date_parser.parse(raw)
        except (ValueError, OverflowError) as exc:
            raise SystemExit(f"Unparseable timestamp on CSV row {row_num}: {raw}") from exc
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=NY_TZ)
    return dt.astimezone(NY_TZ)


def _load_tv_csv(csv_path: str, symbol: str, date_ny, run_id: str):
    path = Path(csv_path)
    if not path.exists():
        raise SystemExit(f"TradingView CSV not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit("TradingView CSV has no header row.")

        headers = {name.strip().lower(): name for name in reader.fieldnames}
        time_key = _find_header(
            headers,
            ["tv_ts_start_ny", "time", "timestamp", "date", "datetime"],
            "timestamp",
        )
        open_key = _find_header(headers, ["open"], "open")
        high_key = _find_header(headers, ["high"], "high")
        low_key = _find_header(headers, ["low"], "low")
        close_key = _find_header(headers, ["close"], "close")
        block_key = headers.get("block_letter")
        source_key = headers.get("source")

        start_ny = datetime.combine(date_ny, time(17, 0), tzinfo=NY_TZ)
        end_ny = start_ny + timedelta(hours=24)

        rows = []
        skipped = 0
        for row_num, row in enumerate(reader, start=2):
            ts_ny = _parse_tv_timestamp(row.get(time_key), row_num)
            if ts_ny < start_ny or ts_ny >= end_ny:
                skipped += 1
                continue

            if block_key:
                block_letter = str(row.get(block_key, "")).strip().upper()
                if not block_letter:
                    raise SystemExit(f"Missing block_letter on CSV row {row_num}.")
            else:
                block_index = int((ts_ny - start_ny).total_seconds() // 7200)
                if block_index < 0 or block_index > 11:
                    raise SystemExit(
                        f"Timestamp out of range for block letters on CSV row {row_num}: {ts_ny}"
                    )
                block_letter = chr(65 + block_index)

            tv_open = _parse_decimal(row.get(open_key), "open", row_num)
            tv_high = _parse_decimal(row.get(high_key), "high", row_num)
            tv_low = _parse_decimal(row.get(low_key), "low", row_num)
            tv_close = _parse_decimal(row.get(close_key), "close", row_num)

            source = "csv"
            if source_key:
                source_raw = str(row.get(source_key, "")).strip()
                if source_raw:
                    source = source_raw

            rows.append(
                (
                    run_id,
                    symbol,
                    date_ny,
                    block_letter,
                    tv_open,
                    tv_high,
                    tv_low,
                    tv_close,
                    ts_ny,
                    source,
                )
            )

    if not rows:
        raise SystemExit(f"No TradingView rows found for {date_ny} in {path}.")

    return rows, skipped


def _insert_tv_rows(dsn: str, rows) -> None:
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.executemany(TV_INSERT_SQL, rows)


def _build_psql_command(run_id: str, symbol: str, date_ny, tolerance, dsn: str, dsn_name: str):
    date_str = date_ny.isoformat()
    tolerance_value = str(tolerance)
    dsn_ref = f"$env:{dsn_name}"
    command = (
        "psql "
        f"-d {dsn_ref} "
        f"-v run_id='{run_id}' "
        f"-v symbol='{symbol}' "
        f"-v date_ny='{date_str}' "
        f"-v tolerance_seconds={PSQL_TOLERANCE_SECONDS} "
        f"-v tolerance={tolerance_value} "
        f"-f '{SQL_PACK_PATH}'"
    )
    args = [
        "psql",
        "-d",
        dsn,
        "-v",
        f"run_id='{run_id}'",
        "-v",
        f"symbol='{symbol}'",
        "-v",
        f"date_ny='{date_str}'",
        "-v",
        f"tolerance_seconds={PSQL_TOLERANCE_SECONDS}",
        "-v",
        f"tolerance={tolerance_value}",
        "-f",
        str(SQL_PACK_PATH),
    ]
    return command, args


def main() -> int:
    parser = argparse.ArgumentParser(description="OVC single-day validation harness entrypoint.")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--date_ny", required=True)
    parser.add_argument("--run-id", dest="run_id")
    parser.add_argument("--tolerance", default="0.00001")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--tv-csv", dest="tv_csv")
    args = parser.parse_args()

    load_env()
    dsn, dsn_name = resolve_dsn()
    date_ny = parse_date(args.date_ny)

    try:
        tolerance = Decimal(args.tolerance)
    except InvalidOperation as exc:
        raise SystemExit(f"Invalid tolerance value: {args.tolerance}") from exc

    result = run_backfill(
        symbol=args.symbol,
        date_ny=date_ny,
        run_id=args.run_id,
        strict=args.strict,
        dsn=dsn,
    )
    print_backfill_summary(result)

    if args.tv_csv:
        rows, skipped = _load_tv_csv(args.tv_csv, result.symbol, result.date_ny, result.run_id)
        _insert_tv_rows(dsn, rows)
        print(f"tv_ohlc_rows_inserted: {len(rows)}")
        if skipped:
            print(f"tv_ohlc_rows_skipped: {skipped}")

    psql_command, psql_args = _build_psql_command(
        result.run_id,
        result.symbol,
        result.date_ny,
        tolerance,
        dsn,
        dsn_name,
    )
    print("psql_command (PowerShell):")
    print(psql_command)

    if shutil.which("psql"):
        print("Running SQL validation pack via psql...")
        completed = subprocess.run(psql_args, check=False)
        if completed.returncode != 0:
            raise SystemExit(f"psql exited with code {completed.returncode}")
    else:
        print("psql not found; run the command above manually.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
