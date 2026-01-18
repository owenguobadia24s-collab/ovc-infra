import argparse
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import psycopg2
from psycopg2.extras import Json

from backfill_day import load_env, parse_date, resolve_dsn
from history_sources.tv_csv import load_tv_csv

NY_TZ = ZoneInfo("America/New_York")

DEFAULT_VER = "ovc_v0.1.0"
DEFAULT_PROFILE = "MIN"
DEFAULT_SCHEME_MIN = "export_contract_v0.1_min_r1"
DEFAULT_BUILD_ID = "history_ingest_v0.1"
DEFAULT_SOURCE = "tv_csv_history"
DEFAULT_TEXT = "UNKNOWN"
CONTRACT_VERSION = "0.1.1"

BLOCK_LETTERS = "ABCDEFGHIJKL"
BLOCK4H = ("AB", "CD", "EF", "GH", "IJ", "KL")

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


@dataclass(frozen=True)
class HistoryIngestResult:
    symbol: str
    date_ny: date
    row_count: int
    skipped: int


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


def _block_index(ts_start_ny: datetime, session_start: datetime) -> int:
    delta_seconds = (ts_start_ny - session_start).total_seconds()
    if delta_seconds < 0 or delta_seconds >= 24 * 3600:
        return -1
    block_index, remainder = divmod(delta_seconds, 7200)
    if abs(remainder) > 1e-6:
        raise SystemExit(f"Timestamp is not on a 2H boundary: {ts_start_ny}")
    return int(block_index)


def _build_payload(
    *,
    values: dict,
    csv_path: Path,
    csv_tz: str,
    ts_start_ny: datetime,
    ts_end_ny: datetime,
    row_num: int,
) -> dict:
    return {
        "schema": DEFAULT_SCHEME_MIN,
        "contract_version": CONTRACT_VERSION,
        "ingest_mode": "tv_csv_history",
        "csv": {
            "path": str(csv_path),
            "tz": csv_tz,
            "row_num": row_num,
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


def ingest_history_day(
    *,
    symbol: str,
    date_ny,
    csv_path: str,
    source: str,
    csv_tz: str,
    strict: bool,
    dsn: Optional[str] = None,
) -> HistoryIngestResult:
    if dsn is None:
        load_env()
        dsn, _ = resolve_dsn()

    records = load_tv_csv(csv_path, csv_tz)
    session_start = datetime.combine(date_ny, time(17, 0), tzinfo=NY_TZ)
    session_end = session_start + timedelta(hours=24)

    symbol = symbol.upper()
    seen_blocks = set()
    rows = []
    skipped = 0
    csv_path_obj = Path(csv_path)

    for record in records:
        ts_start_ny = record.ts_start.astimezone(NY_TZ)
        if ts_start_ny < session_start or ts_start_ny >= session_end:
            skipped += 1
            continue

        block_index = _block_index(ts_start_ny, session_start)
        if block_index < 0 or block_index > 11:
            raise SystemExit(f"Timestamp out of range for NY session: {ts_start_ny}")

        block_letter = BLOCK_LETTERS[block_index]
        if block_letter in seen_blocks:
            raise SystemExit(f"Duplicate block {block_letter} in CSV session window.")
        seen_blocks.add(block_letter)

        ts_end_ny = record.ts_end.astimezone(NY_TZ)
        if strict and ts_end_ny != session_start + timedelta(hours=(block_index + 1) * 2):
            raise SystemExit(f"Block {block_letter} end does not match NY schedule.")

        _ensure_ohlc_sane(record.o, record.h, record.l, record.c, f"row {record.row_num}")

        rng = record.h - record.l
        body = abs(record.c - record.o)
        direction = _bar_direction(record.o, record.c)
        ret = (record.c - record.o) / record.o if record.o else 0.0

        block4h = BLOCK4H[block_index // 2]
        block_id = f"{date_ny:%Y%m%d}-{block_letter}-{symbol}"
        bar_close_ms = int(ts_end_ny.astimezone(timezone.utc).timestamp() * 1000)

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
            "o": float(record.o),
            "h": float(record.h),
            "l": float(record.l),
            "c": float(record.c),
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
            "source": source,
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
                csv_path=csv_path_obj,
                csv_tz=csv_tz,
                ts_start_ny=ts_start_ny,
                ts_end_ny=ts_end_ny,
                row_num=record.row_num,
            )
        )

        rows.append((block_index, values))

    if strict and skipped:
        raise SystemExit(f"Strict mode: skipped {skipped} rows outside the NY session window.")

    if len(rows) != 12:
        raise SystemExit(f"Expected 12 rows for {date_ny}, found {len(rows)}.")

    rows.sort(key=lambda item: item[0])
    tuples = [tuple(values[col] for col in INSERT_COLUMNS) for _, values in rows]

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, tuples)

    return HistoryIngestResult(symbol=symbol, date_ny=date_ny, row_count=len(tuples), skipped=skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a single NY trading day from TradingView 2H CSV.")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--date_ny", required=True)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--tz", default=NY_TZ.key, dest="csv_tz")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    load_env()
    dsn, _ = resolve_dsn()
    date_ny = parse_date(args.date_ny)

    result = ingest_history_day(
        symbol=args.symbol,
        date_ny=date_ny,
        csv_path=args.csv,
        source=args.source,
        csv_tz=args.csv_tz,
        strict=args.strict,
        dsn=dsn,
    )

    print(f"symbol: {result.symbol}")
    print(f"date_ny: {result.date_ny}")
    print(f"history_blocks_ingested: {result.row_count}")
    if result.skipped:
        print(f"history_rows_skipped: {result.skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
