import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from dateutil import parser as date_parser


@dataclass(frozen=True)
class TvCsvRecord:
    ts_start: datetime
    ts_end: datetime
    o: float
    h: float
    l: float
    c: float
    row_num: int


def _find_header(headers, options, label):
    for option in options:
        if option in headers:
            return headers[option]
    raise SystemExit(f"Missing {label} column in CSV. Expected one of: {', '.join(options)}")


def _parse_float(value: str, label: str, row_num: int) -> float:
    raw = "" if value is None else str(value).strip()
    if not raw:
        raise SystemExit(f"Missing {label} value on CSV row {row_num}.")
    try:
        return float(raw.replace(",", ""))
    except ValueError as exc:
        raise SystemExit(f"Invalid {label} value on CSV row {row_num}: {raw}") from exc


def _parse_timestamp(value: str, row_num: int, tzinfo: ZoneInfo) -> datetime:
    raw = "" if value is None else str(value).strip()
    if not raw:
        raise SystemExit(f"Missing timestamp on CSV row {row_num}.")

    if raw.replace(".", "", 1).isdigit():
        ts = float(raw)
        if ts > 1e10:
            ts /= 1000.0
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.astimezone(tzinfo)

    try:
        dt = date_parser.parse(raw)
    except (ValueError, OverflowError) as exc:
        raise SystemExit(f"Unparseable timestamp on CSV row {row_num}: {raw}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    else:
        dt = dt.astimezone(tzinfo)

    return dt


def load_tv_csv(csv_path: str, tz_name: str) -> list[TvCsvRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise SystemExit(f"TradingView CSV not found: {path}")

    try:
        tzinfo = ZoneInfo(tz_name)
    except Exception as exc:
        raise SystemExit(f"Invalid CSV timezone: {tz_name}") from exc

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit("TradingView CSV has no header row.")

        headers = {name.strip().lower(): name for name in reader.fieldnames}
        time_key = _find_header(
            headers,
            ["time", "timestamp", "date", "datetime", "bar_start", "start"],
            "timestamp",
        )
        open_key = _find_header(headers, ["open", "o"], "open")
        high_key = _find_header(headers, ["high", "h"], "high")
        low_key = _find_header(headers, ["low", "l"], "low")
        close_key = _find_header(headers, ["close", "c"], "close")

        rows: list[TvCsvRecord] = []
        for row_num, row in enumerate(reader, start=2):
            ts_start = _parse_timestamp(row.get(time_key), row_num, tzinfo)
            o = _parse_float(row.get(open_key), "open", row_num)
            h = _parse_float(row.get(high_key), "high", row_num)
            l = _parse_float(row.get(low_key), "low", row_num)
            c = _parse_float(row.get(close_key), "close", row_num)

            ts_end = ts_start + timedelta(hours=2)
            rows.append(
                TvCsvRecord(
                    ts_start=ts_start,
                    ts_end=ts_end,
                    o=o,
                    h=h,
                    l=l,
                    c=c,
                    row_num=row_num,
                )
            )

    if not rows:
        raise SystemExit(f"No TradingView rows found in {path}.")

    return rows
