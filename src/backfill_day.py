import argparse
import os
import uuid
from datetime import datetime

import psycopg2


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def resolve_contract_version() -> str:
    default_version = "v0.1"
    path = "VERSION_OPTION_C"
    if not os.path.exists(path):
        return default_version
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read().strip()
        return raw or default_version
    except OSError:
        return default_version


VALIDATION_RUN_SQL = """
insert into ovc_qa.validation_run (
  run_id,
  symbol,
  date_ny,
  ovc_contract_version,
  status,
  notes
)
values (%s, %s, %s, %s, %s, %s)
on conflict (run_id)
do update set
  symbol = excluded.symbol,
  date_ny = excluded.date_ny,
  ovc_contract_version = excluded.ovc_contract_version,
  status = excluded.status,
  notes = excluded.notes;
"""

DELETE_EXPECTED_SQL = """
delete from ovc_qa.expected_blocks
where run_id = %s;
"""

INSERT_EXPECTED_SQL = """
with params as (
  select %s::uuid as run_id, %s::text as symbol, %s::date as date_ny
),
day_start as (
  select
    run_id,
    symbol,
    date_ny,
    (date_ny::timestamp + time '17:00') at time zone 'America/New_York' as start_ts
  from params
),
blocks as (
  select
    run_id,
    symbol,
    date_ny,
    chr(65 + idx) as block_letter,
    start_ts + (idx * interval '2 hours') as block_start_ny,
    start_ts + ((idx + 1) * interval '2 hours') as block_end_ny
  from day_start, generate_series(0, 11) as idx
)
insert into ovc_qa.expected_blocks (
  run_id,
  symbol,
  date_ny,
  block_letter,
  block_start_ny,
  block_end_ny
)
select
  run_id,
  symbol,
  date_ny,
  block_letter,
  block_start_ny,
  block_end_ny
from blocks
order by block_letter;
"""

COUNT_MIN_SQL = """
select count(*)
from ovc.ovc_blocks_v01_1_min
where sym = %s and date_ny = %s;
"""

COUNT_DERIVED_SQL = """
select count(*)
from derived.ovc_block_features_v0_1
where sym = %s and date_ny = %s;
"""

COUNT_OUTCOMES_SQL = """
select count(*)
from derived.ovc_outcomes_v0_1
where sym = %s and date_ny = %s;
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="OVC single-day QA backfill (expected blocks + checks).")
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument("--date_ny", required=True)
    parser.add_argument("--run-id", dest="run_id")
    parser.add_argument("--ovc-contract-version", dest="contract_version")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--strict", action="store_true", help="fail if block count is not 12")
    args = parser.parse_args()

    load_env()
    neon_dsn = os.environ.get("NEON_DSN")
    if not neon_dsn:
        raise SystemExit("Missing NEON_DSN in .env")

    run_id = args.run_id or str(uuid.uuid4())
    contract_version = args.contract_version or resolve_contract_version()
    date_ny = parse_date(args.date_ny)

    with psycopg2.connect(neon_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                VALIDATION_RUN_SQL,
                (run_id, args.symbol, date_ny, contract_version, args.status, args.notes),
            )
            cur.execute(DELETE_EXPECTED_SQL, (run_id,))
            cur.execute(INSERT_EXPECTED_SQL, (run_id, args.symbol, date_ny))

            cur.execute(COUNT_MIN_SQL, (args.symbol, date_ny))
            (min_count,) = cur.fetchone()

            cur.execute(COUNT_DERIVED_SQL, (args.symbol, date_ny))
            (derived_count,) = cur.fetchone()

            cur.execute(COUNT_OUTCOMES_SQL, (args.symbol, date_ny))
            (outcome_count,) = cur.fetchone()

    print(f"run_id: {run_id}")
    print(f"symbol: {args.symbol}")
    print(f"date_ny: {date_ny}")
    print(f"expected_blocks: 12")
    print(f"ovc_blocks: {min_count}")
    print(f"derived_blocks: {derived_count}")
    print(f"outcome_blocks: {outcome_count}")

    if args.strict and int(min_count) != 12:
        raise SystemExit("Block count is not 12; run in non-strict mode to continue.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
