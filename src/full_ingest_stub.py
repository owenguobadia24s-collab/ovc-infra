import argparse
import json
import os
from datetime import datetime, timedelta, timezone

import psycopg2

SCHEMA_VER = "v0.1-min"
FULL_SCHEMA = "OVC_FULL_V01"
CONTRACT_VERSION = "1.0.0"
BLOCK_TYPE = "2H"
SOURCE = "oanda"

INSERT_SQL = """
INSERT INTO ovc_blocks_detail_v01
(symbol, block_start, block_type, schema_ver, full_schema, contract_version, full_payload)
VALUES (%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (symbol, block_start, block_type, schema_ver)
DO UPDATE SET
  full_schema = EXCLUDED.full_schema,
  contract_version = EXCLUDED.contract_version,
  full_payload = EXCLUDED.full_payload,
  ingested_at = now();
"""


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def build_payload(symbol: str, block_start: datetime) -> dict:
    return {
        "schema": FULL_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "note": "stub",
        "source": SOURCE,
        "block": {
            "symbol": symbol,
            "block_start": block_start.isoformat(),
            "block_type": BLOCK_TYPE,
        },
        "ohlc": {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": None,
        },
    }


def iter_blocks(start_dt: datetime, end_dt: datetime):
    current = start_dt
    while current < end_dt:
        yield current
        current += timedelta(hours=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="OVC FULL ingest stub")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    args = parser.parse_args()

    neon_dsn = os.environ.get("NEON_DSN")
    if not neon_dsn:
        raise SystemExit("Missing NEON_DSN")

    start_dt = parse_date(args.start_date)
    end_dt = parse_date(args.end_date) + timedelta(days=1)

    rows = []
    for block_start in iter_blocks(start_dt, end_dt):
        payload = build_payload(args.symbol, block_start)
        rows.append(
            (
                args.symbol,
                block_start,
                BLOCK_TYPE,
                SCHEMA_VER,
                FULL_SCHEMA,
                CONTRACT_VERSION,
                json.dumps(payload),
            )
        )

    if not rows:
        print("No rows to insert.")
        return 0

    with psycopg2.connect(neon_dsn) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, rows)

    print(f"Inserted/updated {len(rows)} full-detail blocks for {args.symbol}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
