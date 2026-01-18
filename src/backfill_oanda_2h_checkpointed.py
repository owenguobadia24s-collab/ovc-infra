import argparse
import os
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import psycopg2
from psycopg2.extras import Json

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

NEON_DSN = os.environ.get("NEON_DSN")
OANDA_API_TOKEN = os.environ.get("OANDA_API_TOKEN")
OANDA_ENV = os.environ.get("OANDA_ENV", "practice")

if not NEON_DSN:
    raise SystemExit("Missing NEON_DSN in .env")
if not OANDA_API_TOKEN:
    raise SystemExit("Missing OANDA_API_TOKEN in .env")

NY_TZ = ZoneInfo("America/New_York")

SYMBOL_DB = "GBPUSD"
INSTRUMENT = "GBP_USD"
SOURCE = "oanda"

DEFAULT_VER = "ovc_v0.1.0"
DEFAULT_PROFILE = "MIN"
DEFAULT_SCHEME_MIN = "export_contract_v0.1_min_r1"
DEFAULT_BUILD_ID = "oanda_backfill_v0.1"
DEFAULT_TEXT = "UNKNOWN"
CONTRACT_VERSION = "0.1.1"

BLOCK_LETTERS = "ABCDEFGHIJKL"
BLOCK4H = ("AB", "CD", "EF", "GH", "IJ", "KL")

DAYS_PER_RUN = int(os.environ.get("BACKFILL_DAYS_PER_RUN", "30"))
BACKFILL_DATE_NY = os.environ.get("BACKFILL_DATE_NY")

START_UTC_STR = os.environ.get("BACKFILL_START_UTC", "2005-01-01T00:00:00Z")
BACKFILL_START_UTC = pd.to_datetime(START_UTC_STR, utc=True).to_pydatetime()

EXPORT_FIELDS = [
    "ver",
    "profile",
    "scheme_min",
    "block_id",
    "sym",
    "tz",
    "date_ny",
    "bar_close_ms",
    "block2h",
    "block4h",
    "o",
    "h",
    "l",
    "c",
    "rng",
    "body",
    "dir",
    "ret",
    "state_tag",
    "value_tag",
    "event",
    "tt",
    "cp_tag",
    "tis",
    "rrc",
    "vrc",
    "trend_tag",
    "struct_state",
    "space_tag",
    "htf_stack",
    "with_htf",
    "rd_state",
    "regime_tag",
    "trans_risk",
    "bias_mode",
    "bias_dir",
    "perm_state",
    "rail_loc",
    "tradeable",
    "conf_l3",
    "play",
    "pred_dir",
    "pred_target",
    "timebox",
    "invalidation",
    "source",
    "build_id",
    "note",
    "ready",
]

INSERT_COLUMNS = [
    "block_id",
    "sym",
    "tz",
    "date_ny",
    "bar_close_ms",
    "block2h",
    "block4h",
    "ver",
    "profile",
    "scheme_min",
    "o",
    "h",
    "l",
    "c",
    "rng",
    "body",
    "dir",
    "ret",
    "state_tag",
    "value_tag",
    "event",
    "tt",
    "cp_tag",
    "tis",
    "rrc",
    "vrc",
    "trend_tag",
    "struct_state",
    "space_tag",
    "htf_stack",
    "with_htf",
    "rd_state",
    "regime_tag",
    "trans_risk",
    "bias_mode",
    "bias_dir",
    "perm_state",
    "rail_loc",
    "tradeable",
    "conf_l3",
    "play",
    "pred_dir",
    "pred_target",
    "timebox",
    "invalidation",
    "source",
    "build_id",
    "note",
    "ready",
    "state_key",
    "export_str",
    "payload",
]

INSERT_SQL = f"""
insert into ovc.ovc_blocks_v01_1_min (
  {", ".join(INSERT_COLUMNS)}, ingest_ts
)
values (
  {", ".join(["%s"] * len(INSERT_COLUMNS))}, now()
)
on conflict (block_id)
do update set
  {", ".join([f"{col} = excluded.{col}" for col in INSERT_COLUMNS])},
  ingest_ts = now();
"""


def parse_date(value: str):
    if value == "YYYY-MM-DD":
        raise SystemExit("You must pass a real date like 2026-01-16")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD, e.g. 2026-01-16.") from exc


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments (optional). Env vars take precedence for backward compatibility."""
    parser = argparse.ArgumentParser(
        description="OVC OANDA 2H backfill (checkpointed). Uses BACKFILL_DATE_NY env var or CLI args."
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
    return parser.parse_args()


def _build_state_key(values: dict) -> str:
    parts = [
        values.get("trend_tag"),
        values.get("struct_state"),
        values.get("space_tag"),
        values.get("bias_mode"),
        values.get("bias_dir"),
        values.get("perm_state"),
        values.get("play"),
        values.get("pred_dir"),
        values.get("timebox"),
    ]
    return "|".join("" if value is None else str(value) for value in parts)


def _format_export_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _build_export_str(values: dict) -> str:
    parts = [f"{key}={_format_export_value(values.get(key))}" for key in EXPORT_FIELDS]
    return "|".join(parts)


def _ensure_ohlc_sane(o: float, h: float, l: float, c: float, label: str) -> None:
    if h < l:
        raise SystemExit(f"Invalid OHLC on {label}: high < low.")
    if h < max(o, c) or l > min(o, c):
        raise SystemExit(f"Invalid OHLC on {label}: open/close outside range.")


def _bar_direction(o: float, c: float) -> int:
    if c > o:
        return 1
    if c < o:
        return -1
    return 0


def _build_payload(
    *,
    values: dict,
    ts_start_ny: datetime,
    ts_end_ny: datetime,
) -> dict:
    return {
        "schema": DEFAULT_SCHEME_MIN,
        "contract_version": CONTRACT_VERSION,
        "ingest_mode": "oanda_backfill_2h",
        "oanda": {
            "instrument": INSTRUMENT,
            "granularity": "H1",
        },
        "normalized": {
            "ts_start_ny": ts_start_ny.isoformat(),
            "ts_end_ny": ts_end_ny.isoformat(),
        },
        "parsed": {
            "block_id": values.get("block_id"),
            "sym": values.get("sym"),
            "date_ny": values.get("date_ny").isoformat(),
            "block2h": values.get("block2h"),
            "block4h": values.get("block4h"),
            "bar_close_ms": values.get("bar_close_ms"),
            "o": values.get("o"),
            "h": values.get("h"),
            "l": values.get("l"),
            "c": values.get("c"),
            "source": values.get("source"),
        },
    }


# ---- OANDA fetch (single window) ----
def fetch_oanda_h1(start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
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
            "granularity": "H1",
            "price": "M",
        }

        r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
        api.request(r)
        candles = r.response.get("candles", [])

        for c in candles:
            if not c.get("complete"):
                continue
            mid = c["mid"]
            all_rows.append(
                {
                    "time": pd.to_datetime(c["time"], utc=True),
                    "open": float(mid["o"]),
                    "high": float(mid["h"]),
                    "low": float(mid["l"]),
                    "close": float(mid["c"]),
                    "volume": int(c.get("volume", 0)),
                }
            )

        print(f"Fetched slice {cur_start.isoformat()} -> {cur_end.isoformat()} | candles={len(candles)}")
        cur_start = cur_end

    df = pd.DataFrame(all_rows)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["time"]).sort_values("time").set_index("time")


def resample_to_2h_ny(df_h1: pd.DataFrame) -> pd.DataFrame:
    if df_h1.empty:
        return df_h1

    df = df_h1.sort_index().copy()
    df["ts_start_ny"] = df.index.tz_convert(NY_TZ)

    session_start = df["ts_start_ny"].dt.normalize() + pd.Timedelta(hours=17)
    session_start = session_start.where(df["ts_start_ny"].dt.hour >= 17, session_start - pd.Timedelta(days=1))
    df["session_start_ny"] = session_start

    df["block_index"] = ((df["ts_start_ny"] - df["session_start_ny"]).dt.total_seconds() // 7200).astype(int)
    df = df[(df["block_index"] >= 0) & (df["block_index"] < 12)]

    df["block_start_ny"] = df["session_start_ny"] + pd.to_timedelta(df["block_index"] * 2, unit="h")
    df["date_ny"] = df["session_start_ny"].dt.date

    grouped = df.groupby(["block_start_ny", "date_ny", "block_index"], sort=True)
    df_2h = grouped.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
        candle_count=("open", "size"),
    ).reset_index()

    df_2h = df_2h[df_2h["candle_count"] == 2].drop(columns=["candle_count"])
    return df_2h


def build_min_rows(df_2h: pd.DataFrame) -> list[tuple]:
    if df_2h.empty:
        return []

    symbol = SYMBOL_DB.upper()
    rows = []

    for row in df_2h.itertuples(index=False):
        ts_start_ny = row.block_start_ny
        ts_end_ny = ts_start_ny + timedelta(hours=2)
        block_index = int(row.block_index)
        if block_index < 0 or block_index > 11:
            continue

        block_letter = BLOCK_LETTERS[block_index]
        block4h = BLOCK4H[block_index // 2]
        date_ny = row.date_ny
        block_id = f"{date_ny:%Y%m%d}-{block_letter}-{symbol}"
        bar_close_ms = int(ts_end_ny.astimezone(timezone.utc).timestamp() * 1000)

        o = float(row.open)
        h = float(row.high)
        l = float(row.low)
        c = float(row.close)
        _ensure_ohlc_sane(o, h, l, c, f"{block_id}")

        rng = h - l
        body = abs(c - o)
        direction = _bar_direction(o, c)
        ret = (c - o) / o if o else 0.0

        values = {
            "block_id": block_id,
            "sym": symbol,
            "tz": NY_TZ.key,
            "date_ny": date_ny,
            "bar_close_ms": bar_close_ms,
            "block2h": block_letter,
            "block4h": block4h,
            "ver": DEFAULT_VER,
            "profile": DEFAULT_PROFILE,
            "scheme_min": DEFAULT_SCHEME_MIN,
            "o": o,
            "h": h,
            "l": l,
            "c": c,
            "rng": float(rng),
            "body": float(body),
            "dir": direction,
            "ret": float(ret),
            "state_tag": DEFAULT_TEXT,
            "value_tag": DEFAULT_TEXT,
            "event": DEFAULT_TEXT,
            "tt": 0,
            "cp_tag": DEFAULT_TEXT,
            "tis": 0,
            "rrc": 0.0,
            "vrc": 0.0,
            "trend_tag": DEFAULT_TEXT,
            "struct_state": DEFAULT_TEXT,
            "space_tag": DEFAULT_TEXT,
            "htf_stack": DEFAULT_TEXT,
            "with_htf": False,
            "rd_state": DEFAULT_TEXT,
            "regime_tag": DEFAULT_TEXT,
            "trans_risk": DEFAULT_TEXT,
            "bias_mode": DEFAULT_TEXT,
            "bias_dir": "NEUTRAL",
            "perm_state": DEFAULT_TEXT,
            "rail_loc": DEFAULT_TEXT,
            "tradeable": False,
            "conf_l3": DEFAULT_TEXT,
            "play": DEFAULT_TEXT,
            "pred_dir": "NEUTRAL",
            "pred_target": DEFAULT_TEXT,
            "timebox": DEFAULT_TEXT,
            "invalidation": DEFAULT_TEXT,
            "source": SOURCE,
            "build_id": DEFAULT_BUILD_ID,
            "note": DEFAULT_TEXT,
            "ready": True,
        }

        state_key = _build_state_key(values)
        values["state_key"] = state_key
        values["export_str"] = _build_export_str(values)
        values["payload"] = Json(
            _build_payload(
                values=values,
                ts_start_ny=ts_start_ny,
                ts_end_ny=ts_end_ny,
            )
        )

        rows.append(tuple(values[col] for col in INSERT_COLUMNS))

    return rows


def get_min_block_start() -> datetime | None:
    sql = """
    SELECT MIN(bar_close_ms)
    FROM ovc.ovc_blocks_v01_1_min
    WHERE sym=%s;
    """
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SYMBOL_DB,))
            (min_ms,) = cur.fetchone()
    if min_ms is None:
        return None
    return datetime.fromtimestamp(min_ms / 1000, tz=timezone.utc) - timedelta(hours=2)


def count_blocks_between(start_utc: datetime, end_utc: datetime) -> int:
    start_ms = int(start_utc.timestamp() * 1000)
    end_ms = int(end_utc.timestamp() * 1000)
    sql = """
    SELECT COUNT(*)
    FROM ovc.ovc_blocks_v01_1_min
    WHERE sym=%s
      AND (bar_close_ms - 7200000) >= %s
      AND (bar_close_ms - 7200000) < %s;
    """
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SYMBOL_DB, start_ms, end_ms))
            (n,) = cur.fetchone()
    return int(n)


def insert_blocks(rows: list[tuple]):
    if not rows:
        return
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, rows)


if __name__ == "__main__":
    args = parse_args()
    single_date_mode = False
    range_mode = False

    # CLI range mode (--start_ny + --end_ny) takes precedence
    if args.start_ny and args.end_ny:
        range_mode = True
        start_date_ny = parse_date(args.start_ny)
        end_date_ny = parse_date(args.end_ny)
        if end_date_ny < start_date_ny:
            raise SystemExit("--end_ny must be >= --start_ny")
        # Process each day in range
        current_date = start_date_ny
        total_inserted = 0
        while current_date <= end_date_ny:
            session_start_ny = datetime.combine(current_date, time(17, 0), tzinfo=NY_TZ)
            day_start_utc = session_start_ny.astimezone(timezone.utc)
            day_end_utc = (session_start_ny + timedelta(hours=24)).astimezone(timezone.utc)

            if day_end_utc <= BACKFILL_START_UTC:
                print(f"SKIP: {current_date} is before BACKFILL_START_UTC")
                current_date += timedelta(days=1)
                continue

            before = count_blocks_between(day_start_utc, day_end_utc)
            df_h1 = fetch_oanda_h1(day_start_utc, day_end_utc)
            df_2h = resample_to_2h_ny(df_h1)
            rows = build_min_rows(df_2h)
            insert_blocks(rows)
            after = count_blocks_between(day_start_utc, day_end_utc)
            inserted_est = after - before
            total_inserted += inserted_est
            print(f"{current_date}: H1={len(df_h1)} 2H={len(df_2h)} inserted_est={inserted_est}")
            current_date += timedelta(days=1)

        print(f"RANGE BACKFILL COMPLETE: {start_date_ny} to {end_date_ny}, total_inserted_est={total_inserted}")
        raise SystemExit(0)

    # Single-date mode via env var (existing behavior)
    if BACKFILL_DATE_NY:
        single_date_mode = True
        date_ny = parse_date(BACKFILL_DATE_NY)
        session_start_ny = datetime.combine(date_ny, time(17, 0), tzinfo=NY_TZ)
        start_utc = session_start_ny.astimezone(timezone.utc)
        end_utc = (session_start_ny + timedelta(hours=24)).astimezone(timezone.utc)
        mode = f"single-date ({date_ny})"
    else:
        min_ts = get_min_block_start()
        now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

        if min_ts is None:
            end_utc = now_utc
            start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
            mode = "seed (DB empty)"
        else:
            end_utc = min_ts
            start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
            mode = "backfill (extend into past)"

    if end_utc <= BACKFILL_START_UTC:
        print(f"STOP: DB already at/earlier than BACKFILL_START_UTC ({BACKFILL_START_UTC.isoformat()})")
        raise SystemExit(0)

    if start_utc < BACKFILL_START_UTC:
        if single_date_mode:
            print(f"STOP: Requested date is earlier than BACKFILL_START_UTC ({BACKFILL_START_UTC.isoformat()})")
            raise SystemExit(0)
        start_utc = BACKFILL_START_UTC

    print(f"MODE: {mode}")
    print(f"WINDOW: {start_utc.isoformat()} -> {end_utc.isoformat()} (days={DAYS_PER_RUN})")

    before = count_blocks_between(start_utc, end_utc)
    df_h1 = fetch_oanda_h1(start_utc, end_utc)
    print(f"H1 candles fetched: {len(df_h1)}")

    df_2h = resample_to_2h_ny(df_h1)
    print(f"2H blocks computed: {len(df_2h)}")

    rows = build_min_rows(df_2h)
    insert_blocks(rows)

    after = count_blocks_between(start_utc, end_utc)
    inserted_est = after - before

    print(f"DB blocks in window before={before} after={after} inserted_est={inserted_est}")
    print("STEP 4 RUN COMPLETE (rerun-safe).")
