import argparse
import os
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import psycopg2
from psycopg2.extras import Json

# Add parent to path for local imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ovc_ops.run_artifact import RunWriter, detect_trigger

# ---------- tiny .env loader ----------
def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_env()

if not os.environ.get("DATABASE_URL") and os.environ.get("NEON_DSN"):
    os.environ["DATABASE_URL"] = os.environ["NEON_DSN"]

DB_DSN = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
OANDA_API_TOKEN = os.environ.get("OANDA_API_TOKEN")
OANDA_ENV = os.environ.get("OANDA_ENV", "practice")

# Pipeline metadata
PIPELINE_ID = "P2-Backfill-M15"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["DATABASE_URL", "OANDA_API_TOKEN", "OANDA_ENV"]

# Check required env vars (moved to run_artifact handling)
_missing_env = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
if _missing_env and "--help" not in sys.argv and "-h" not in sys.argv:
    # Create run artifacts even on env failure
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    writer.start(trigger_type, trigger_source, actor)
    writer.log(f"ERROR: Missing required environment variables: {_missing_env}")
    writer.finish("failed")
    raise SystemExit(f"Missing required env vars: {_missing_env}")

NY_TZ = ZoneInfo("America/New_York")

DEFAULT_SYMBOL_DB = os.environ.get("OANDA_SYMBOL_DB", "GBPUSD")
DEFAULT_INSTRUMENT = os.environ.get("OANDA_INSTRUMENT", "GBP_USD")
SOURCE = "oanda"
DEFAULT_BUILD_ID = os.environ.get("OANDA_BUILD_ID", "oanda_backfill_m15_v0.1")

DAYS_PER_RUN = int(os.environ.get("BACKFILL_DAYS_PER_RUN", "30"))
BACKFILL_DATE_NY = os.environ.get("BACKFILL_DATE_NY")

START_UTC_STR = os.environ.get("BACKFILL_START_UTC", "2005-01-01T00:00:00Z")
BACKFILL_START_UTC = pd.to_datetime(START_UTC_STR, utc=True).to_pydatetime()

INSERT_COLUMNS = [
    "sym",
    "tz",
    "bar_start_ms",
    "bar_close_ms",
    "o",
    "h",
    "l",
    "c",
    "volume",
    "source",
    "build_id",
    "payload",
]

INSERT_SQL = f"""
insert into ovc.ovc_candles_m15_raw (
  {", ".join(INSERT_COLUMNS)}, ingest_ts
)
values (
  {", ".join(["%s"] * len(INSERT_COLUMNS))}, now()
)
on conflict (sym, bar_start_ms)
do update set
  bar_close_ms = excluded.bar_close_ms,
  o = excluded.o,
  h = excluded.h,
  l = excluded.l,
  c = excluded.c,
  volume = excluded.volume,
  source = excluded.source,
  build_id = excluded.build_id,
  payload = excluded.payload,
  ingest_ts = now();
"""


def parse_date(value: str):
    if value == "YYYY-MM-DD":
        raise SystemExit("You must pass a real date like 2026-01-16")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD, e.g. 2026-01-16.") from exc


def parse_utc(value: str) -> datetime:
    if value in ("YYYY-MM-DDTHH:MM:SSZ", "YYYY-MM-DDTHH:MM:SS+00:00"):
        raise SystemExit("You must pass a real UTC timestamp like 2026-01-16T00:00:00Z")
    try:
        ts = pd.to_datetime(value, utc=True)
    except Exception as exc:
        raise SystemExit("Invalid UTC timestamp. Use ISO-8601, e.g. 2026-01-16T00:00:00Z") from exc
    if pd.isna(ts):
        raise SystemExit("Invalid UTC timestamp. Use ISO-8601, e.g. 2026-01-16T00:00:00Z")
    return ts.to_pydatetime()


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments (optional). Env vars take precedence for backward compatibility."""
    parser = argparse.ArgumentParser(
        description="OVC OANDA M15 backfill (checkpointed). Uses BACKFILL_DATE_NY or CLI args."
    )
    parser.add_argument(
        "--start_ny",
        type=str,
        default=None,
        help="Start date (NY, YYYY-MM-DD). If set with --end_ny, overrides env vars.",
    )
    parser.add_argument(
        "--end_ny",
        type=str,
        default=None,
        help="End date (NY, YYYY-MM-DD, inclusive). If set with --start_ny, overrides env vars.",
    )
    parser.add_argument(
        "--start_utc",
        type=str,
        default=None,
        help="Start timestamp (UTC ISO-8601). Must be paired with --end_utc.",
    )
    parser.add_argument(
        "--end_utc",
        type=str,
        default=None,
        help="End timestamp (UTC ISO-8601, exclusive). Must be paired with --start_utc.",
    )
    parser.add_argument(
        "--sym",
        type=str,
        default=None,
        help="Symbol for DB storage (e.g., GBPUSD).",
    )
    parser.add_argument(
        "--instrument",
        type=str,
        default=None,
        help="OANDA instrument (e.g., GBP_USD).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and build rows but skip inserts.",
    )
    return parser.parse_args()


def _ensure_ohlc_sane(o: float, h: float, l: float, c: float, label: str) -> None:
    if h < l:
        raise SystemExit(f"Invalid OHLC on {label}: high < low.")
    if h < max(o, c) or l > min(o, c):
        raise SystemExit(f"Invalid OHLC on {label}: open/close outside range.")


def _build_payload(
    *,
    instrument: str,
    granularity: str,
    ts_start_utc: datetime,
    ts_close_utc: datetime,
    values: dict,
) -> dict:
    return {
        "ingest_mode": "oanda_backfill_m15",
        "oanda": {
            "instrument": instrument,
            "granularity": granularity,
        },
        "normalized": {
            "ts_start_utc": ts_start_utc.isoformat(),
            "ts_close_utc": ts_close_utc.isoformat(),
            "bar_start_ms": values.get("bar_start_ms"),
            "bar_close_ms": values.get("bar_close_ms"),
        },
        "parsed": {
            "sym": values.get("sym"),
            "o": values.get("o"),
            "h": values.get("h"),
            "l": values.get("l"),
            "c": values.get("c"),
            "volume": values.get("volume"),
            "source": values.get("source"),
        },
    }


# ---- OANDA fetch (single window) ----
def fetch_oanda_m15(start_utc: datetime, end_utc: datetime, instrument: str) -> pd.DataFrame:
    api = oandapyV20.API(
        access_token=OANDA_API_TOKEN,
        environment="practice" if OANDA_ENV == "practice" else "live",
    )
    slice_days = int(os.environ.get("OANDA_SLICE_DAYS", "3"))
    step = timedelta(days=slice_days)

    cur_start = start_utc
    all_rows = []

    while cur_start < end_utc:
        cur_end = min(cur_start + step, end_utc)

        params = {
            "from": cur_start.isoformat().replace("+00:00", "Z"),
            "to": cur_end.isoformat().replace("+00:00", "Z"),
            "granularity": "M15",
            "price": "M",
        }

        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        api.request(r)
        candles = r.response.get("candles", [])

        for c in candles:
            if not c.get("complete"):
                continue
            mid = c["mid"]
            volume_raw = c.get("volume")
            all_rows.append(
                {
                    "time": pd.to_datetime(c["time"], utc=True),
                    "open": float(mid["o"]),
                    "high": float(mid["h"]),
                    "low": float(mid["l"]),
                    "close": float(mid["c"]),
                    "volume": int(volume_raw) if volume_raw is not None else None,
                }
            )

        print(f"Fetched slice {cur_start.isoformat()} -> {cur_end.isoformat()} | candles={len(candles)}")
        cur_start = cur_end

    df = pd.DataFrame(all_rows)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["time"]).sort_values("time").set_index("time")


def build_rows(
    df_m15: pd.DataFrame,
    symbol: str,
    instrument: str,
    build_id: str,
) -> list[tuple]:
    if df_m15.empty:
        return []

    rows = []
    symbol = symbol.upper()

    for row in df_m15.itertuples():
        ts_start_utc = row.Index.to_pydatetime()
        if ts_start_utc.tzinfo is None:
            ts_start_utc = ts_start_utc.replace(tzinfo=timezone.utc)
        ts_close_utc = ts_start_utc + timedelta(minutes=15)

        bar_start_ms = int(ts_start_utc.timestamp() * 1000)
        bar_close_ms = int(ts_close_utc.timestamp() * 1000)

        o = float(row.open)
        h = float(row.high)
        l = float(row.low)
        c = float(row.close)
        _ensure_ohlc_sane(o, h, l, c, f"{symbol} {ts_start_utc.isoformat()}")

        volume = row.volume
        if pd.isna(volume):
            volume = None
        elif volume is not None:
            volume = int(volume)

        values = {
            "sym": symbol,
            "tz": NY_TZ.key,
            "bar_start_ms": bar_start_ms,
            "bar_close_ms": bar_close_ms,
            "o": o,
            "h": h,
            "l": l,
            "c": c,
            "volume": volume,
            "source": SOURCE,
            "build_id": build_id,
        }
        values["payload"] = Json(
            _build_payload(
                instrument=instrument,
                granularity="M15",
                ts_start_utc=ts_start_utc,
                ts_close_utc=ts_close_utc,
                values=values,
            )
        )
        rows.append(tuple(values[col] for col in INSERT_COLUMNS))

    return rows


def get_min_bar_start(symbol: str) -> datetime | None:
    sql = """
    SELECT MIN(bar_start_ms)
    FROM ovc.ovc_candles_m15_raw
    WHERE sym=%s;
    """
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (symbol,))
            (min_ms,) = cur.fetchone()
    if min_ms is None:
        return None
    return datetime.fromtimestamp(min_ms / 1000, tz=timezone.utc)


def count_candles_between(start_utc: datetime, end_utc: datetime, symbol: str) -> int:
    start_ms = int(start_utc.timestamp() * 1000)
    end_ms = int(end_utc.timestamp() * 1000)
    sql = """
    SELECT COUNT(*)
    FROM ovc.ovc_candles_m15_raw
    WHERE sym=%s
      AND bar_start_ms >= %s
      AND bar_start_ms < %s;
    """
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (symbol, start_ms, end_ms))
            (n,) = cur.fetchone()
    return int(n)


def insert_rows(rows: list[tuple]) -> None:
    if not rows:
        return
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, rows)


if __name__ == "__main__":
    args = parse_args()

    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    run_id = writer.start(trigger_type, trigger_source, actor)

    symbol_db = (args.sym or DEFAULT_SYMBOL_DB).upper()
    instrument = args.instrument or DEFAULT_INSTRUMENT
    build_id = DEFAULT_BUILD_ID
    dry_run = args.dry_run

    single_date_mode = False
    range_mode = False
    total_rows_written = 0

    try:
        # UTC range mode (--start_utc + --end_utc) takes precedence
        if args.start_utc and args.end_utc:
            range_mode = True
            start_utc = parse_utc(args.start_utc)
            end_utc = parse_utc(args.end_utc)
            if end_utc <= start_utc:
                raise SystemExit("--end_utc must be > --start_utc")

            writer.add_input(type="oanda", ref=instrument, range=f"{start_utc} to {end_utc}")

            before = count_candles_between(start_utc, end_utc, symbol_db)
            df_m15 = fetch_oanda_m15(start_utc, end_utc, instrument)
            rows = build_rows(df_m15, symbol_db, instrument, build_id)
            if dry_run:
                writer.log(f"[DRY RUN] UTC range would insert {len(rows)} rows")
                after = before
                inserted_est = 0
            else:
                insert_rows(rows)
                after = count_candles_between(start_utc, end_utc, symbol_db)
                inserted_est = after - before
            total_rows_written = inserted_est

            writer.log(f"UTC RANGE BACKFILL COMPLETE: {start_utc} to {end_utc}, inserted_est={inserted_est}")
            writer.add_output(
                type="neon_table",
                ref="ovc.ovc_candles_m15_raw",
                rows_written=total_rows_written,
            )
            writer.check("oanda_fetch_success", "OANDA API fetch succeeded", "pass", [])
            writer.check(
                "rows_inserted",
                "Rows inserted to Neon",
                "skip" if dry_run else "pass",
                ["run.json:$.outputs[0].rows_written"],
            )
            writer.finish("success")
            raise SystemExit(0)

        # NY range mode (--start_ny + --end_ny)
        if args.start_ny and args.end_ny:
            range_mode = True
            start_date_ny = parse_date(args.start_ny)
            end_date_ny = parse_date(args.end_ny)
            if end_date_ny < start_date_ny:
                raise SystemExit("--end_ny must be >= --start_ny")

            writer.add_input(type="oanda", ref=instrument, range=f"{start_date_ny} to {end_date_ny}")

            current_date = start_date_ny
            total_inserted = 0
            while current_date <= end_date_ny:
                session_start_ny = datetime.combine(current_date, time(17, 0), tzinfo=NY_TZ)
                day_start_utc = session_start_ny.astimezone(timezone.utc)
                day_end_utc = (session_start_ny + timedelta(hours=24)).astimezone(timezone.utc)

                if day_end_utc <= BACKFILL_START_UTC:
                    writer.log(f"SKIP: {current_date} is before BACKFILL_START_UTC")
                    current_date += timedelta(days=1)
                    continue

                before = count_candles_between(day_start_utc, day_end_utc, symbol_db)
                df_m15 = fetch_oanda_m15(day_start_utc, day_end_utc, instrument)
                rows = build_rows(df_m15, symbol_db, instrument, build_id)
                if dry_run:
                    writer.log(f"[DRY RUN] {current_date} would insert {len(rows)} rows")
                    after = before
                    inserted_est = 0
                else:
                    insert_rows(rows)
                    after = count_candles_between(day_start_utc, day_end_utc, symbol_db)
                    inserted_est = after - before
                total_inserted += inserted_est
                total_rows_written += inserted_est
                writer.log(f"{current_date}: M15={len(df_m15)} inserted_est={inserted_est}")
                current_date += timedelta(days=1)

            writer.log(f"NY RANGE BACKFILL COMPLETE: {start_date_ny} to {end_date_ny}, total_inserted_est={total_inserted}")
            writer.add_output(
                type="neon_table",
                ref="ovc.ovc_candles_m15_raw",
                rows_written=total_rows_written,
            )
            writer.check("oanda_fetch_success", "OANDA API fetch succeeded", "pass", [])
            writer.check(
                "rows_inserted",
                "Rows inserted to Neon",
                "skip" if dry_run else "pass",
                ["run.json:$.outputs[0].rows_written"],
            )
            writer.finish("success")
            raise SystemExit(0)

        # Single-date mode via env var (existing behavior)
        if BACKFILL_DATE_NY:
            single_date_mode = True
            date_ny = parse_date(BACKFILL_DATE_NY)
            session_start_ny = datetime.combine(date_ny, time(17, 0), tzinfo=NY_TZ)
            start_utc = session_start_ny.astimezone(timezone.utc)
            end_utc = (session_start_ny + timedelta(hours=24)).astimezone(timezone.utc)
            mode = f"single-date ({date_ny})"
            writer.add_input(type="oanda", ref=instrument, range=str(date_ny))
        else:
            min_ts = get_min_bar_start(symbol_db)
            now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

            if min_ts is None:
                end_utc = now_utc
                start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
                mode = "seed (DB empty)"
            else:
                end_utc = min_ts
                start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
                mode = "backfill (extend into past)"

            writer.add_input(
                type="oanda",
                ref=instrument,
                range=f"{start_utc.date()} to {end_utc.date()}",
            )

        if end_utc <= BACKFILL_START_UTC:
            writer.log(f"STOP: DB already at/earlier than BACKFILL_START_UTC ({BACKFILL_START_UTC.isoformat()})")
            writer.check("backfill_needed", "Backfill window valid", "skip", [])
            writer.finish("success")
            raise SystemExit(0)

        if start_utc < BACKFILL_START_UTC:
            if single_date_mode:
                writer.log(f"STOP: Requested date is earlier than BACKFILL_START_UTC ({BACKFILL_START_UTC.isoformat()})")
                writer.check("backfill_needed", "Backfill window valid", "skip", [])
                writer.finish("success")
                raise SystemExit(0)
            start_utc = BACKFILL_START_UTC

        writer.log(f"MODE: {mode}")
        writer.log(f"WINDOW: {start_utc.isoformat()} -> {end_utc.isoformat()} (days={DAYS_PER_RUN})")

        before = count_candles_between(start_utc, end_utc, symbol_db)
        df_m15 = fetch_oanda_m15(start_utc, end_utc, instrument)
        writer.log(f"M15 candles fetched: {len(df_m15)}")

        rows = build_rows(df_m15, symbol_db, instrument, build_id)
        if dry_run:
            writer.log(f"[DRY RUN] window would insert {len(rows)} rows")
            after = before
            inserted_est = 0
        else:
            insert_rows(rows)
            after = count_candles_between(start_utc, end_utc, symbol_db)
            inserted_est = after - before
        total_rows_written = inserted_est

        writer.log(f"DB candles in window before={before} after={after} inserted_est={inserted_est}")
        writer.log("M15 BACKFILL COMPLETE (rerun-safe).")

        writer.add_output(
            type="neon_table",
            ref="ovc.ovc_candles_m15_raw",
            rows_written=total_rows_written,
        )
        writer.check("oanda_fetch_success", "OANDA API fetch succeeded", "pass", [])
        writer.check(
            "rows_inserted",
            "Rows inserted to Neon",
            "skip" if dry_run else "pass",
            ["run.json:$.outputs[0].rows_written"],
        )
        writer.finish("success")

    except SystemExit:
        raise
    except Exception as e:
        writer.log(f"ERROR: {type(e).__name__}: {e}")
        writer.check("execution_error", f"Execution failed: {type(e).__name__}", "fail", [])
        writer.finish("failed")
        raise
