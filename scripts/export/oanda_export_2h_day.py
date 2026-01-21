import argparse
import csv
import os
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import oandapyV20
import oandapyV20.endpoints.instruments as instruments

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from backfill_day import load_env, parse_date

NY_TZ = ZoneInfo("America/New_York")


def symbol_to_instrument(symbol: str) -> str:
    if "_" in symbol:
        return symbol
    symbol = symbol.upper()
    if len(symbol) == 6:
        return f"{symbol[:3]}_{symbol[3:]}"
    raise SystemExit(f"Cannot infer OANDA instrument from symbol '{symbol}'.")


def _parse_oanda_time(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def fetch_oanda_h1(
    instrument: str,
    start_utc: datetime,
    end_utc: datetime,
    token: str,
    env: str,
) -> list[dict]:
    api = oandapyV20.API(
        access_token=token,
        environment="practice" if env == "practice" else "live",
    )
    params = {
        "from": start_utc.isoformat().replace("+00:00", "Z"),
        "to": end_utc.isoformat().replace("+00:00", "Z"),
        "granularity": "H1",
        "price": "M",
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    api.request(r)
    candles = r.response.get("candles", [])

    rows: list[dict] = []
    for candle in candles:
        if not candle.get("complete"):
            continue
        mid = candle["mid"]
        rows.append(
            {
                "ts_utc": _parse_oanda_time(candle["time"]),
                "open": float(mid["o"]),
                "high": float(mid["h"]),
                "low": float(mid["l"]),
                "close": float(mid["c"]),
            }
        )
    return rows


def build_2h_bars(rows: list[dict], session_start_ny: datetime) -> list[dict]:
    session_end_ny = session_start_ny + timedelta(hours=24)
    hour_rows = []
    for row in rows:
        ts_ny = row["ts_utc"].astimezone(NY_TZ)
        if ts_ny < session_start_ny or ts_ny >= session_end_ny:
            continue
        row["ts_ny"] = ts_ny
        hour_rows.append(row)

    hour_rows.sort(key=lambda item: item["ts_ny"])
    if len(hour_rows) != 24:
        raise SystemExit(f"Expected 24 H1 bars; found {len(hour_rows)}.")

    buckets: dict[int, list[dict]] = {idx: [] for idx in range(12)}
    for row in hour_rows:
        delta = row["ts_ny"] - session_start_ny
        hour_index, remainder = divmod(delta.total_seconds(), 3600)
        if abs(remainder) > 1e-6:
            raise SystemExit(f"Unexpected H1 timestamp alignment: {row['ts_ny']}")
        hour_index = int(hour_index)
        if hour_index < 0 or hour_index >= 24:
            continue
        buckets[hour_index // 2].append(row)

    bars = []
    for block_index in range(12):
        block_rows = buckets[block_index]
        if len(block_rows) != 2:
            raise SystemExit(f"Expected 2 H1 bars for block {block_index}; found {len(block_rows)}.")
        block_rows.sort(key=lambda item: item["ts_ny"])
        start_ts = session_start_ny + timedelta(hours=block_index * 2)
        bars.append(
            {
                "time": start_ts.isoformat(),
                "open": block_rows[0]["open"],
                "high": max(row["high"] for row in block_rows),
                "low": min(row["low"] for row in block_rows),
                "close": block_rows[-1]["close"],
            }
        )
    return bars


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "open", "high", "low", "close"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "time": row["time"],
                    "open": f"{row['open']:.5f}",
                    "high": f"{row['high']:.5f}",
                    "low": f"{row['low']:.5f}",
                    "close": f"{row['close']:.5f}",
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Export OANDA 2H CSV for a single NY trading day.")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--date-ny", required=True)
    parser.add_argument("--instrument")
    parser.add_argument("--output")
    args = parser.parse_args()

    load_env()
    token = os.environ.get("OANDA_API_TOKEN")
    env = os.environ.get("OANDA_ENV", "practice")
    if not token:
        raise SystemExit("Missing OANDA_API_TOKEN.")

    symbol = args.symbol.upper()
    instrument = args.instrument or symbol_to_instrument(symbol)
    date_ny = parse_date(args.date_ny)

    session_start_ny = datetime.combine(date_ny, time(17, 0), tzinfo=NY_TZ)
    session_end_ny = session_start_ny + timedelta(hours=24)
    start_utc = session_start_ny.astimezone(timezone.utc)
    end_utc = session_end_ny.astimezone(timezone.utc)

    rows = fetch_oanda_h1(instrument, start_utc, end_utc, token, env)
    bars_2h = build_2h_bars(rows, session_start_ny)

    if args.output:
        output_path = Path(args.output)
    else:
        filename = f"{symbol}__dateNY_{date_ny}__2h__oanda.csv"
        output_path = REPO_ROOT / "data" / "tv" / filename

    write_csv(bars_2h, output_path)
    print(f"oanda_csv_rows: {len(bars_2h)}")
    print(f"oanda_csv_path: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
