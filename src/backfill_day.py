import argparse
import os
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_env_fallback(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)


def load_env(path=None) -> bool:
    env_path = Path(path) if path else REPO_ROOT / ".env"
    if not env_path.exists():
        return False
    try:
        from dotenv import load_dotenv
    except ImportError:
        _load_env_fallback(env_path)
    else:
        load_dotenv(env_path, override=False)
    return True


def parse_date(value: str):
    if value == "YYYY-MM-DD":
        raise SystemExit("You must pass a real date like 2026-01-16")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD, e.g. 2026-01-16.") from exc


def resolve_contract_version() -> str:
    default_version = "v0.1"
    path = REPO_ROOT / "VERSION_OPTION_C"
    if not path.exists():
        return default_version
    try:
        with path.open("r", encoding="utf-8") as handle:
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


def resolve_dsn():
    neon_dsn = os.environ.get("NEON_DSN")
    if neon_dsn:
        return neon_dsn, "NEON_DSN"
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url, "DATABASE_URL"
    raise SystemExit(
        "Missing NEON_DSN or DATABASE_URL. Add one to .env, for example:\n"
        "NEON_DSN=postgres://user:pass@host/db\n"
        "DATABASE_URL=postgres://user:pass@host/db"
    )


@dataclass(frozen=True)
class BackfillResult:
    run_id: str
    symbol: str
    date_ny: date
    min_count: int
    derived_count: int
    outcome_count: int


def seed_expected_blocks(cur, run_id: str, symbol: str, date_ny) -> None:
    cur.execute(DELETE_EXPECTED_SQL, (run_id,))
    cur.execute(INSERT_EXPECTED_SQL, (run_id, symbol, date_ny))


def fetch_counts(cur, symbol: str, date_ny):
    cur.execute(COUNT_MIN_SQL, (symbol, date_ny))
    (min_count,) = cur.fetchone()

    cur.execute(COUNT_DERIVED_SQL, (symbol, date_ny))
    (derived_count,) = cur.fetchone()

    cur.execute(COUNT_OUTCOMES_SQL, (symbol, date_ny))
    (outcome_count,) = cur.fetchone()

    return int(min_count), int(derived_count), int(outcome_count)


def run_backfill(
    *,
    symbol: str,
    date_ny,
    run_id: str = None,
    contract_version: str = None,
    status: str = "pending",
    notes: str = None,
    strict: bool = False,
    dsn: str = None,
) -> BackfillResult:
    if dsn is None:
        dsn, _ = resolve_dsn()
    run_id = run_id or str(uuid.uuid4())
    contract_version = contract_version or resolve_contract_version()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                VALIDATION_RUN_SQL,
                (run_id, symbol, date_ny, contract_version, status, notes),
            )
            seed_expected_blocks(cur, run_id, symbol, date_ny)
            min_count, derived_count, outcome_count = fetch_counts(cur, symbol, date_ny)

    result = BackfillResult(
        run_id=run_id,
        symbol=symbol,
        date_ny=date_ny,
        min_count=min_count,
        derived_count=derived_count,
        outcome_count=outcome_count,
    )

    if strict and result.min_count != 12:
        raise SystemExit("Block count is not 12; run in non-strict mode to continue.")

    return result


def print_backfill_summary(result: BackfillResult) -> None:
    print(f"run_id: {result.run_id}")
    print(f"symbol: {result.symbol}")
    print(f"date_ny: {result.date_ny}")
    print("expected_blocks: 12")
    print(f"ovc_blocks: {result.min_count}")
    print(f"derived_blocks: {result.derived_count}")
    print(f"outcome_blocks: {result.outcome_count}")


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
    dsn, _ = resolve_dsn()
    date_ny = parse_date(args.date_ny)

    result = run_backfill(
        symbol=args.symbol,
        date_ny=date_ny,
        run_id=args.run_id,
        contract_version=args.contract_version,
        status=args.status,
        notes=args.notes,
        strict=args.strict,
        dsn=dsn,
    )
    print_backfill_summary(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
