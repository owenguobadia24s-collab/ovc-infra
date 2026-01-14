import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import psycopg2
import oandapyV20
import oandapyV20.endpoints.instruments as instruments

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

SYMBOL_DB = "GBPUSD"
INSTRUMENT = "GBP_USD"
SCHEMA_VER = "v0.1-min"
BLOCK_TYPE = "2H"
SOURCE = "oanda"

DAYS_PER_RUN = int(os.environ.get("BACKFILL_DAYS_PER_RUN", "30"))

START_UTC_STR = os.environ.get("BACKFILL_START_UTC", "2005-01-01T00:00:00Z")
BACKFILL_START_UTC = pd.to_datetime(START_UTC_STR, utc=True).to_pydatetime()

# ---- OANDA fetch (single window) ----
def fetch_oanda_m1(start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
    api = oandapyV20.API(
        access_token=OANDA_API_TOKEN,
        environment="practice" if OANDA_ENV == "practice" else "live"
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
            all_rows.append({
                "time": pd.to_datetime(c["time"], utc=True),
                "open": float(mid["o"]),
                "high": float(mid["h"]),
                "low": float(mid["l"]),
                "close": float(mid["c"]),
                "volume": int(c.get("volume", 0)),
            })

        print(f"Fetched slice {cur_start.isoformat()} → {cur_end.isoformat()} | candles={len(candles)}")
        cur_start = cur_end

    df = pd.DataFrame(all_rows)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["time"]).sort_values("time").set_index("time")


def resample_to_2h(df_m1: pd.DataFrame) -> pd.DataFrame:
    if df_m1.empty:
        return df_m1

    # Use uppercase "H" to avoid pandas deprecation warning
    df_2h = df_m1.resample("2H", closed="left", label="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna()

    df_2h = df_2h.reset_index().rename(columns={"time": "block_start"})
    df_2h["schema_ver"] = SCHEMA_VER
    df_2h["source"] = SOURCE
    df_2h["symbol"] = SYMBOL_DB
    df_2h["block_type"] = BLOCK_TYPE
    return df_2h[["schema_ver","source","symbol","block_type","block_start","open","high","low","close","volume"]]

INSERT_SQL = """
INSERT INTO ovc_blocks_v01
(schema_ver, source, symbol, block_type, block_start, open, high, low, close, volume)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (symbol, block_start, block_type, schema_ver) DO NOTHING;
"""

def get_min_block_start() -> datetime | None:
    sql = """
    SELECT MIN(block_start)
    FROM ovc_blocks_v01
    WHERE symbol=%s AND block_type=%s AND schema_ver=%s;
    """
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SYMBOL_DB, BLOCK_TYPE, SCHEMA_VER))
            (min_ts,) = cur.fetchone()
    return min_ts

def count_blocks_between(start_utc: datetime, end_utc: datetime) -> int:
    sql = """
    SELECT COUNT(*)
    FROM ovc_blocks_v01
    WHERE symbol=%s AND block_type=%s AND schema_ver=%s
      AND block_start >= %s AND block_start < %s;
    """
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (SYMBOL_DB, BLOCK_TYPE, SCHEMA_VER, start_utc, end_utc))
            (n,) = cur.fetchone()
    return int(n)

def insert_blocks(df_blocks: pd.DataFrame):
    if df_blocks.empty:
        return
    tuples = [tuple(x) for x in df_blocks.to_numpy()]
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, tuples)

if __name__ == "__main__":
    min_ts = get_min_block_start()

    now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    if min_ts is None:
        end_utc = now_utc
        start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
        mode = "seed (DB empty)"
    else:
        end_utc = min_ts
        start_utc = end_utc - timedelta(days=DAYS_PER_RUN)
        mode = "backfill (extend into past)"

    # Stop if we've reached (or passed) target start
    if end_utc <= BACKFILL_START_UTC:
        print(f"STOP: DB already at/earlier than BACKFILL_START_UTC ({BACKFILL_START_UTC.isoformat()})")
        raise SystemExit(0)

    if start_utc < BACKFILL_START_UTC:
        start_utc = BACKFILL_START_UTC

    print(f"MODE: {mode}")
    print(f"WINDOW: {start_utc.isoformat()} → {end_utc.isoformat()} (days={DAYS_PER_RUN})")

    before = count_blocks_between(start_utc, end_utc)
    df_m1 = fetch_oanda_m1(start_utc, end_utc)
    print(f"M1 candles fetched: {len(df_m1)}")

    df_2h = resample_to_2h(df_m1)
    print(f"2H blocks computed: {len(df_2h)}")

    insert_blocks(df_2h)

    after = count_blocks_between(start_utc, end_utc)
    inserted_est = after - before

    print(f"DB blocks in window before={before} after={after} inserted_est={inserted_est}")
    print("STEP 4 RUN COMPLETE (rerun-safe).")
