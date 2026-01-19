import argparse
import csv
import shutil
import subprocess
import sys
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from dateutil import parser as date_parser
import psycopg2

from backfill_day import load_env, parse_date, print_backfill_summary, resolve_dsn, run_backfill
from ingest_history_day import DEFAULT_SOURCE as HISTORY_DEFAULT_SOURCE, ingest_history_day
from ovc_ops.run_artifact import RunWriter, detect_trigger
from utils.csv_locator import resolve_csv_path, set_auto_pick
from validate_range import evaluate_day as evaluate_range_day, table_exists as pg_table_exists

PIPELINE_ID = "D-ValidationHarness"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN|DATABASE_URL"]

REPO_ROOT = Path(__file__).resolve().parents[1]
SQL_PACK_CORE_PATH = REPO_ROOT / "sql" / "qa_validation_pack_core.sql"
SQL_PACK_DERIVED_PATH = REPO_ROOT / "sql" / "qa_validation_pack_derived.sql"
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


def _build_psql_command(
    run_id: str,
    symbol: str,
    date_ny,
    tolerance,
    dsn: str,
    dsn_name: str,
    pack_path: Path,
):
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
        f"-f '{pack_path}'"
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
        str(pack_path),
    ]
    return command, args


def _derived_pack_exists(dsn: str) -> bool:
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select to_regclass('derived.ovc_block_features_v0_1') is not null;"
            )
            (exists,) = cur.fetchone()
    return bool(exists)


def main(writer: RunWriter) -> int:
    parser = argparse.ArgumentParser(description="OVC single-day validation harness entrypoint.")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--date_ny", required=True)
    parser.add_argument("--run-id", dest="run_id")
    parser.add_argument("--tolerance", default="0.00001")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--missing_facts",
        choices=("fail", "skip"),
        default="fail",
        help=(
            "Behavior when no canonical MIN facts exist for the date. "
            "'fail' (default) enforces backfill-before-validation; 'skip' exits 0 after printing "
            "status=SKIP and reason=facts_not_backfilled."
        ),
    )
    parser.add_argument("--tv-csv", dest="tv_csv")
    parser.add_argument("--ingest-history-csv", dest="ingest_history_csv")
    parser.add_argument("--auto-pick", action="store_true")
    parser.add_argument("--csv-search", dest="csv_search")
    args = parser.parse_args()

    load_env()
    dsn, dsn_name = resolve_dsn()
    date_ny = parse_date(args.date_ny)
    
    writer.log(f"Validating {args.symbol} for {date_ny}")
    writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")

    try:
        tolerance = Decimal(args.tolerance)
    except InvalidOperation as exc:
        raise SystemExit(f"Invalid tolerance value: {args.tolerance}") from exc

    if args.ingest_history_csv or args.csv_search:
        set_auto_pick(args.auto_pick)
        csv_path = resolve_csv_path(
            args.ingest_history_csv,
            args.csv_search,
            args.symbol,
            timeframe_hint="2h",
        )
        ingest_result = ingest_history_day(
            symbol=args.symbol,
            date_ny=date_ny,
            csv_path=csv_path,
            source=HISTORY_DEFAULT_SOURCE,
            csv_tz=NY_TZ.key,
            strict=args.strict,
            dsn=dsn,
        )
        print(f"history_blocks_ingested: {ingest_result.row_count}")
        if ingest_result.skipped:
            print(f"history_rows_skipped: {ingest_result.skipped}")

    result = run_backfill(
        symbol=args.symbol,
        date_ny=date_ny,
        run_id=args.run_id,
        strict=args.strict,
        dsn=dsn,
    )
    print_backfill_summary(result)
    derived_summary = "SKIPPED" if result.derived_count is None else str(result.derived_count)
    outcomes_summary = "SKIPPED" if result.outcome_count is None else str(result.outcome_count)
    print(f"blocks_count: {result.min_count}")
    print(f"derived_count: {derived_summary}")
    print(f"outcomes_count: {outcomes_summary}")

    if args.tv_csv:
        rows, skipped = _load_tv_csv(args.tv_csv, result.symbol, result.date_ny, result.run_id)
        _insert_tv_rows(dsn, rows)
        print(f"tv_ohlc_rows_inserted: {len(rows)}")
        if skipped:
            print(f"tv_ohlc_rows_skipped: {skipped}")

    if result.min_count == 0:
        if date_ny.weekday() >= 5:
            print("status: SKIP")
            print("skip_reason: weekend_no_blocks")
            return 0

        if args.missing_facts == "skip":
            print("status: SKIP")
            print("skip_reason: facts_not_backfilled")
            print("skip_reason_code: FACTS_NOT_BACKFILLED")
            return 0

        raise SystemExit(
            "No canonical MIN facts found for this weekday (facts_not_backfilled). "
            "Run canonical backfill first, or pass --missing_facts skip."
        )

    psql_command, psql_args = _build_psql_command(
        result.run_id,
        result.symbol,
        result.date_ny,
        tolerance,
        dsn,
        dsn_name,
        SQL_PACK_CORE_PATH,
    )
    derived_pack_exists = _derived_pack_exists(dsn)
    derived_command = None
    derived_args = None
    if derived_pack_exists:
        derived_command, derived_args = _build_psql_command(
            result.run_id,
            result.symbol,
            result.date_ny,
            tolerance,
            dsn,
            dsn_name,
            SQL_PACK_DERIVED_PATH,
        )
    else:
        print("derived: SKIPPED (missing derived.ovc_block_features_v0_1)")

    print("psql_command_core (PowerShell):")
    print(psql_command)
    if derived_command:
        print("psql_command_derived (PowerShell):")
        print(derived_command)

    if shutil.which("psql"):
        print("Running SQL validation pack (core) via psql...")
        completed = subprocess.run(psql_args, check=False)
        if completed.returncode != 0:
            raise SystemExit(f"psql exited with code {completed.returncode}")
        if derived_args:
            print("Running SQL validation pack (derived) via psql...")
            completed = subprocess.run(derived_args, check=False)
            if completed.returncode != 0:
                raise SystemExit(f"psql exited with code {completed.returncode}")
    else:
        print("psql not found; run the command above manually.")

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            tv_available = pg_table_exists(cur, "ovc_qa.tv_ohlc_2h")
            outcomes_exists = pg_table_exists(cur, result.outcomes_table)
            eval_result = evaluate_range_day(
                cur,
                result.symbol,
                result.date_ny,
                result.run_id,
                PSQL_TOLERANCE_SECONDS,
                tolerance,
                tv_available,
                result.outcomes_table,
                outcomes_exists,
                args.missing_facts,
            )

    reasons = list(eval_result["reasons"])
    skip_reasons = list(eval_result["skip_reasons"])
    if reasons:
        status = "FAIL"
        merged = reasons + skip_reasons
    elif skip_reasons:
        status = "SKIP"
        merged = skip_reasons
    else:
        status = "PASS"
        merged = []

    print(f"status: {status}")
    if merged:
        print(f"reasons: {';'.join(merged)}")
    
    # Record checks in run artifact
    writer.check(
        name="validation_status",
        status="pass" if status == "PASS" else ("skip" if status == "SKIP" else "fail"),
        evidence=f"status={status}",
    )
    if merged:
        writer.check(
            name="validation_reasons",
            status="pass" if not reasons else "fail",
            evidence=f"reasons={';'.join(merged)}",
        )

    return 0


if __name__ == "__main__":
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    writer.start(trigger_type=trigger_type, trigger_source=trigger_source, actor=actor)
    
    exit_code = 0
    try:
        exit_code = main(writer)
        writer.finish(status="success" if exit_code == 0 else "failed")
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
        writer.log(f"SystemExit: {e}")
        writer.finish(status="failed" if exit_code != 0 else "success")
        raise
    except Exception as e:
        writer.log(f"Exception: {e}")
        writer.finish(status="failed")
        raise
    
    sys.exit(exit_code)
