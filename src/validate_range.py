import argparse
import csv
import io
import json
import sys
import uuid
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg2
from psycopg2 import sql

from backfill_day import (
    COUNT_OUTCOMES_DEFAULT,
    load_env,
    parse_date,
    resolve_dsn,
    resolve_qualified_table,
)
from ovc_artifacts import make_run_dir, write_latest, write_meta
from ovc_ops.run_artifact import RunWriter, detect_trigger

PIPELINE_ID = "D-ValidationRange"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN|DATABASE_URL"]

REPO_ROOT = Path(__file__).resolve().parents[1]

COUNT_OVC_SQL = """
select count(*)
from ovc.ovc_blocks_v01_1_min
where sym = %s and date_ny = %s;
"""

MISSING_BLOCKS_SQL = """
with letters as (
  select chr(65 + idx) as block_letter
  from generate_series(0, 11) as idx
)
select l.block_letter
from letters l
left join ovc.ovc_blocks_v01_1_min m
  on m.sym = %s
 and m.date_ny = %s
 and m.block2h = l.block_letter
where m.block2h is null
order by l.block_letter;
"""

DURATION_GAP_SQL = """
with blocks as (
  select
    block_id,
    block2h as block_letter,
    to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as ts_start,
    to_timestamp(bar_close_ms / 1000.0) as ts_end
  from ovc.ovc_blocks_v01_1_min
  where sym = %s
    and date_ny = %s
),
ordered as (
  select
    *,
    lag(ts_end) over (order by ts_start) as prev_end
  from blocks
)
select count(*)
from ordered
where abs(extract(epoch from (ts_end - ts_start)) - 7200) > %s
   or (prev_end is not null and abs(extract(epoch from (ts_start - prev_end))) > %s);
"""

SCHEDULE_SQL = """
with params as (
  select %s::date as date_ny
),
day_start as (
  select
    (date_ny::timestamp + time '17:00') at time zone 'America/New_York' as start_ts
  from params
),
expected as (
  select
    chr(65 + idx) as block_letter,
    start_ts + (idx * interval '2 hours') as block_start_ny,
    start_ts + ((idx + 1) * interval '2 hours') as block_end_ny
  from day_start, generate_series(0, 11) as idx
),
blocks as (
  select
    block2h as block_letter,
    to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as ts_start,
    to_timestamp(bar_close_ms / 1000.0) as ts_end
  from ovc.ovc_blocks_v01_1_min
  where sym = %s
    and date_ny = %s
)
select count(*)
from expected e
left join blocks b
  on b.block_letter = e.block_letter
where b.block_letter is null
   or abs(extract(epoch from (b.ts_start - e.block_start_ny))) > %s
   or abs(extract(epoch from (b.ts_end - e.block_end_ny))) > %s;
"""

TV_ROWS_SQL = """
select count(*)
from ovc_qa.tv_ohlc_2h
where run_id = %s
  and symbol = %s
  and date_ny = %s;
"""

MISMATCH_SQL = """
select count(*)
from ovc.ovc_blocks_v01_1_min m
join ovc_qa.tv_ohlc_2h tv
  on tv.run_id = %s
 and tv.symbol = %s
 and tv.date_ny = %s
 and tv.block_letter = m.block2h
where m.sym = %s
  and m.date_ny = %s
  and (
    abs(m.o - tv.tv_open) > %s
    or abs(m.h - tv.tv_high) > %s
    or abs(m.l - tv.tv_low) > %s
    or abs(m.c - tv.tv_close) > %s
  );
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OVC multi-day validation runner (range).")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--start_ny", required=True)
    parser.add_argument("--end_ny", required=True)
    weekdays = parser.add_mutually_exclusive_group()
    weekdays.add_argument(
        "--weekdays_only",
        dest="weekdays_only",
        action="store_true",
        help="Process weekdays only (default).",
    )
    weekdays.add_argument(
        "--include_weekends",
        dest="weekdays_only",
        action="store_false",
        help="Include weekends in the validation range.",
    )
    parser.set_defaults(weekdays_only=True)
    parser.add_argument("--tolerance_seconds", type=int, default=10)
    parser.add_argument("--tolerance", default="0.00001")
    parser.add_argument("--strict_derived", action="store_true")
    parser.add_argument(
        "--missing_facts",
        choices=("fail", "skip"),
        default="fail",
        help=(
            "Behavior when no canonical MIN facts exist for an eligible weekday. "
            "'fail' (default) enforces backfill-before-validation; 'skip' marks the day as SKIP "
            "with reason 'facts_not_backfilled'."
        ),
    )
    parser.add_argument("--max_days", type=int, default=None)
    parser.add_argument("--out_dir", default="reports")
    parser.add_argument("--component_name", default="validation")
    return parser.parse_args()


def iter_dates(start_ny, end_ny):
    current = start_ny
    while current <= end_ny:
        yield current
        current += timedelta(days=1)


def build_range_run_id(
    symbol: str,
    start_ny,
    end_ny,
    weekdays_only: bool,
    tolerance_seconds: int,
    tolerance: Decimal,
    strict_derived: bool,
    missing_facts_policy: str,
) -> str:
    seed = (
        f"validate_range:{symbol}:{start_ny.isoformat()}:{end_ny.isoformat()}:"
        f"{weekdays_only}:{tolerance_seconds}:{tolerance}:{strict_derived}:{missing_facts_policy}"
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def build_day_run_id(range_run_id: str, symbol: str, date_ny) -> str:
    namespace = uuid.UUID(range_run_id)
    return str(uuid.uuid5(namespace, f"{symbol}:{date_ny.isoformat()}"))


def table_exists(cur, qualified_name: str) -> bool:
    cur.execute("select to_regclass(%s);", (qualified_name,))
    (regclass_name,) = cur.fetchone()
    return regclass_name is not None


def _shorten_message(message: str, limit: int = 160) -> str:
    raw = " ".join((message or "").split())
    if len(raw) > limit:
        return raw[: limit - 3] + "..."
    return raw


def run_validate_day(symbol: str, date_ny, run_id: str, tolerance: Decimal, strict_derived: bool):
    try:
        import validate_day
    except ImportError as exc:
        return 1, f"validate_day_import_error: {exc}"

    argv = [
        "validate_day.py",
        "--symbol",
        symbol,
        "--date_ny",
        date_ny.isoformat(),
        "--run-id",
        run_id,
        "--tolerance",
        str(tolerance),
    ]
    if strict_derived:
        argv.append("--strict")

    saved_argv = sys.argv
    output = io.StringIO()
    exit_code = 0
    message = ""
    try:
        sys.argv = argv
        with redirect_stdout(output), redirect_stderr(output):
            result = validate_day.main()
        if isinstance(result, int):
            exit_code = result
    except SystemExit as exc:
        if isinstance(exc.code, int):
            exit_code = exc.code
        else:
            exit_code = 1
            message = str(exc.code)
    except Exception as exc:  # noqa: BLE001
        exit_code = 1
        message = str(exc)
    finally:
        sys.argv = saved_argv

    if exit_code != 0 and not message:
        message = output.getvalue()

    return exit_code, _shorten_message(message)


def fetch_outcome_blocks(cur, symbol: str, date_ny, outcomes_table: str, outcomes_exists: bool):
    if not outcomes_exists:
        return None
    schema, table = outcomes_table.split(".", 1)
    query = sql.SQL("select count(*) from {}.{} where sym = %s and date_ny = %s;").format(
        sql.Identifier(schema),
        sql.Identifier(table),
    )
    cur.execute(query, (symbol, date_ny))
    (count,) = cur.fetchone()
    return int(count)


def evaluate_day(
    cur,
    symbol: str,
    date_ny,
    run_id: str,
    tolerance_seconds: int,
    tolerance: Decimal,
    tv_available: bool,
    outcomes_table: str,
    outcomes_exists: bool,
    missing_facts_policy: str,
):
    cur.execute(COUNT_OVC_SQL, (symbol, date_ny))
    (ovc_blocks,) = cur.fetchone()
    ovc_blocks = int(ovc_blocks)

    weekend = date_ny.weekday() >= 5
    outcome_blocks = fetch_outcome_blocks(cur, symbol, date_ny, outcomes_table, outcomes_exists)

    tv_rows = 0
    if tv_available:
        cur.execute(TV_ROWS_SQL, (run_id, symbol, date_ny))
        (tv_rows,) = cur.fetchone()
        tv_rows = int(tv_rows)

    if ovc_blocks == 0:
        reasons = []
        skip_reasons = []

        if weekend:
            skip_reasons.append("weekend_no_blocks")
        else:
            tag = "facts_not_backfilled"
            if missing_facts_policy == "skip":
                skip_reasons.append(tag)
            else:
                reasons.append(tag)

        if tv_available:
            if tv_rows == 0:
                skip_reasons.append("tv_ohlc_missing")
        else:
            skip_reasons.append("tv_table_missing")

        return {
            "expected_blocks": 12,
            "ovc_blocks": ovc_blocks,
            "outcome_blocks": outcome_blocks,
            "mismatch_count": None,
            "tv_rows": tv_rows,
            "missing_letters": [],
            "duration_issues": None,
            "schedule_issues": None,
            "reasons": reasons,
            "skip_reasons": skip_reasons,
        }

    cur.execute(MISSING_BLOCKS_SQL, (symbol, date_ny))
    missing_letters = [row[0] for row in cur.fetchall()]

    cur.execute(DURATION_GAP_SQL, (symbol, date_ny, tolerance_seconds, tolerance_seconds))
    (duration_issues,) = cur.fetchone()
    duration_issues = int(duration_issues)

    cur.execute(SCHEDULE_SQL, (date_ny, symbol, date_ny, tolerance_seconds, tolerance_seconds))
    (schedule_issues,) = cur.fetchone()
    schedule_issues = int(schedule_issues)

    mismatch_count = 0
    if tv_available:
        if tv_rows:
            cur.execute(
                MISMATCH_SQL,
                (run_id, symbol, date_ny, symbol, date_ny, tolerance, tolerance, tolerance, tolerance),
            )
            (mismatch_count,) = cur.fetchone()
            mismatch_count = int(mismatch_count)

    reasons = []
    skip_reasons = []

    if ovc_blocks != 12:
        reasons.append("block_count_mismatch")
    if missing_letters:
        reasons.append("missing_block_letters")
    if duration_issues:
        reasons.append("duration_gap_mismatch")
    if schedule_issues:
        reasons.append("schedule_mismatch")

    if tv_available:
        if tv_rows == 0:
            skip_reasons.append("tv_ohlc_missing")
        elif mismatch_count > 0:
            reasons.append("ohlc_mismatch")
    else:
        skip_reasons.append("tv_table_missing")

    return {
        "expected_blocks": 12,
        "ovc_blocks": ovc_blocks,
        "outcome_blocks": outcome_blocks,
        "mismatch_count": mismatch_count,
        "tv_rows": tv_rows,
        "missing_letters": missing_letters,
        "duration_issues": duration_issues,
        "schedule_issues": schedule_issues,
        "reasons": reasons,
        "skip_reasons": skip_reasons,
    }


def main(writer: RunWriter) -> int:
    args = parse_args()
    load_env()
    dsn, _ = resolve_dsn()

    start_ny = parse_date(args.start_ny)
    end_ny = parse_date(args.end_ny)
    if end_ny < start_ny:
        raise SystemExit("end_ny must be on or after start_ny.")
    
    writer.log(f"Validating {args.symbol} from {start_ny} to {end_ny}")
    writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")

    try:
        tolerance = Decimal(args.tolerance)
    except InvalidOperation as exc:
        raise SystemExit(f"Invalid tolerance value: {args.tolerance}") from exc

    if args.max_days is not None and args.max_days <= 0:
        raise SystemExit("max_days must be positive.")

    total_days = (end_ny - start_ny).days + 1
    if args.max_days is not None and total_days > args.max_days:
        raise SystemExit(f"Range has {total_days} days, exceeds --max_days {args.max_days}.")

    range_run_id = build_range_run_id(
        args.symbol,
        start_ny,
        end_ny,
        args.weekdays_only,
        args.tolerance_seconds,
        tolerance,
        args.strict_derived,
        args.missing_facts,
    )

    run_dir = make_run_dir(args.out_dir, args.component_name, range_run_id)
    jsonl_path = run_dir / "days.jsonl"
    csv_path = run_dir / "summary.csv"
    summary_path = run_dir / "summary.json"

    weekend_days = sum(1 for day in iter_dates(start_ny, end_ny) if day.weekday() >= 5)
    eligible_days = total_days - weekend_days if args.weekdays_only else total_days

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            qa_available = table_exists(cur, "ovc_qa.validation_run") and table_exists(
                cur, "ovc_qa.expected_blocks"
            )
            tv_available = table_exists(cur, "ovc_qa.tv_ohlc_2h")
            outcomes_table = resolve_qualified_table("OVC_OUTCOMES_TABLE", COUNT_OUTCOMES_DEFAULT)
            outcomes_exists = table_exists(cur, outcomes_table)

        totals = {"attempted": 0, "passed": 0, "failed": 0, "skipped": 0}
        coverage = {"ovc_block_days": 0, "tv_days": 0}
        failure_reasons: dict[str, int] = {}

        csv_fields = [
            "date_ny",
            "status",
            "expected_blocks",
            "ovc_blocks",
            "outcome_blocks",
            "mismatch_count",
            "reason",
        ]

        with jsonl_path.open("w", encoding="utf-8") as jsonl_handle, csv_path.open(
            "w", encoding="utf-8", newline=""
        ) as csv_handle:
            writer = csv.DictWriter(csv_handle, fieldnames=csv_fields)
            writer.writeheader()

            for date_ny in iter_dates(start_ny, end_ny):
                date_str = date_ny.isoformat()
                day_run_id = build_day_run_id(range_run_id, args.symbol, date_ny)

                if args.weekdays_only and date_ny.weekday() >= 5:
                    record = {
                        "range_run_id": range_run_id,
                        "day_run_id": None,
                        "symbol": args.symbol,
                        "date_ny": date_str,
                        "status": "SKIP",
                        "expected_blocks": 12,
                        "ovc_blocks": None,
                        "outcome_blocks": None,
                        "mismatch_count": None,
                        "reasons": ["weekend"],
                    }
                    totals["skipped"] += 1
                    jsonl_handle.write(json.dumps(record, ensure_ascii=True) + "\n")
                    writer.writerow(
                        {
                            "date_ny": date_str,
                            "status": "SKIP",
                            "expected_blocks": 12,
                            "ovc_blocks": "",
                            "outcome_blocks": "",
                            "mismatch_count": "",
                            "reason": "weekend",
                        }
                    )
                    continue

                validate_error = ""
                validate_error_severity = "fail"
                if qa_available:
                    exit_code, message = run_validate_day(
                        args.symbol, date_ny, day_run_id, tolerance, args.strict_derived
                    )
                    if exit_code != 0:
                        validate_error = message or "validate_day_failed"
                else:
                    validate_error = "qa_schema_missing"
                    validate_error_severity = "skip"

                with conn.cursor() as cur:
                    eval_result = evaluate_day(
                        cur,
                        args.symbol,
                        date_ny,
                        day_run_id,
                        args.tolerance_seconds,
                        tolerance,
                        tv_available,
                        outcomes_table,
                        outcomes_exists,
                        args.missing_facts,
                    )

                reasons = list(eval_result["reasons"])
                skip_reasons = list(eval_result["skip_reasons"])
                if validate_error:
                    tag = f"validate_day_error:{validate_error}"
                    if validate_error_severity == "skip":
                        skip_reasons.append(tag)
                    else:
                        reasons.append(tag)

                if reasons:
                    status = "FAIL"
                    totals["failed"] += 1
                    totals["attempted"] += 1
                    merged_reasons = reasons + skip_reasons
                    for reason in merged_reasons:
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                elif skip_reasons:
                    status = "SKIP"
                    totals["skipped"] += 1
                    merged_reasons = skip_reasons
                else:
                    status = "PASS"
                    totals["passed"] += 1
                    totals["attempted"] += 1
                    merged_reasons = []

                if eval_result["ovc_blocks"]:
                    coverage["ovc_block_days"] += 1
                if eval_result["tv_rows"]:
                    coverage["tv_days"] += 1

                record = {
                    "range_run_id": range_run_id,
                    "day_run_id": day_run_id,
                    "symbol": args.symbol,
                    "date_ny": date_str,
                    "status": status,
                    "expected_blocks": eval_result["expected_blocks"],
                    "ovc_blocks": eval_result["ovc_blocks"],
                    "outcome_blocks": eval_result["outcome_blocks"],
                    "mismatch_count": eval_result["mismatch_count"],
                    "reasons": merged_reasons,
                }
                jsonl_handle.write(json.dumps(record, ensure_ascii=True) + "\n")

                writer.writerow(
                    {
                        "date_ny": date_str,
                        "status": status,
                        "expected_blocks": eval_result["expected_blocks"],
                        "ovc_blocks": eval_result["ovc_blocks"],
                        "outcome_blocks": ""
                        if eval_result["outcome_blocks"] is None
                        else eval_result["outcome_blocks"],
                        "mismatch_count": ""
                        if eval_result["mismatch_count"] is None
                        else eval_result["mismatch_count"],
                        "reason": ";".join(merged_reasons),
                    }
                )

    top_failure_reasons = [
        {"reason": reason, "count": count}
        for reason, count in sorted(failure_reasons.items(), key=lambda item: (-item[1], item[0]))
    ]

    coverage_stats = {
        "total_days": total_days,
        "weekend_days": weekend_days,
        "eligible_days": eligible_days,
        "ovc_block_days": coverage["ovc_block_days"],
        "tv_days": coverage["tv_days"],
        "ovc_block_coverage_pct": round(
            100.0 * coverage["ovc_block_days"] / eligible_days, 2
        )
        if eligible_days
        else 0.0,
        "tv_coverage_pct": round(100.0 * coverage["tv_days"] / eligible_days, 2)
        if eligible_days
        else 0.0,
    }

    summary = {
        "run_id": range_run_id,
        "symbol": args.symbol,
        "start_ny": start_ny.isoformat(),
        "end_ny": end_ny.isoformat(),
        "weekdays_only": args.weekdays_only,
        "tolerance_seconds": args.tolerance_seconds,
        "tolerance": str(tolerance),
        "strict_derived": args.strict_derived,
        "missing_facts": args.missing_facts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validated_days": totals["attempted"],
        "skipped_days": totals["skipped"],
        "totals": totals,
        "coverage": coverage_stats,
        "top_failure_reasons": top_failure_reasons,
        "reports": {
            "jsonl": str(jsonl_path),
            "csv": str(csv_path),
        },
    }

    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    write_meta(
        run_dir,
        args.component_name,
        range_run_id,
        list(sys.argv),
        extra={
            "args": {
                "symbol": args.symbol,
                "start_ny": start_ny.isoformat(),
                "end_ny": end_ny.isoformat(),
                "weekdays_only": args.weekdays_only,
                "tolerance_seconds": args.tolerance_seconds,
                "tolerance": str(tolerance),
                "strict_derived": args.strict_derived,
                "missing_facts": args.missing_facts,
                "max_days": args.max_days,
                "out_dir": args.out_dir,
                "component_name": args.component_name,
            },
            "totals": totals,
            "coverage": coverage_stats,
        },
    )
    latest_path = write_latest(Path(args.out_dir) / args.component_name, range_run_id)

    print(f"range_run_id: {range_run_id}")
    print(f"summary_json: {summary_path}")
    print(f"summary_csv: {csv_path}")
    print(f"days_jsonl: {jsonl_path}")
    print(
        "totals: "
        f"attempted={totals['attempted']} passed={totals['passed']} "
        f"failed={totals['failed']} skipped={totals['skipped']}"
    )
    print(f"latest_path: {latest_path}")
    
    # Record outputs and checks in run artifact
    writer.add_output(type="file", ref=str(summary_path))
    writer.add_output(type="file", ref=str(csv_path))
    writer.add_output(type="file", ref=str(jsonl_path))
    
    writer.check(
        name="validation_pass_rate",
        status="pass" if totals["failed"] == 0 else "fail",
        evidence=f"passed={totals['passed']}, failed={totals['failed']}, skipped={totals['skipped']}",
    )

    return 2 if totals["failed"] else 0


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
