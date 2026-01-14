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
OANDA_ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")  # not used for candle pulls, but keep stored
OANDA_ENV = os.environ.get("OANDA_ENV", "practice")

if not NEON_DSN:
    raise SystemExit("Missing NEON_DSN in .env")
if not OANDA_API_TOKEN:
    raise SystemExit("Missing OANDA_API_TOKEN in .env")

OANDA_HOST = "https://api-fxpractice.oanda.com" if OANDA_ENV == "practice" else "https://api-fxtrade.oanda.com"

SYMBOL_DB = "GBPUSD"         # what you store in Neon
INSTRUMENT = "GBP_USD"       # OANDA instrument name
SCHEMA_VER = "v0.1-min"
BLOCK_TYPE = "2H"
SOURCE = "oanda"

# ---------- fetch ----------
def fetch_oanda_m1(start_utc: datetime, end_utc: datetime) -> pd.DataFrame:
    client = oandapyV20.API(access_token=OANDA_API_TOKEN, environment="practice" if OANDA_ENV == "practice" else "live")
    # OANDA expects RFC3339 strings
    params = {
        "from": start_utc.isoformat().replace("+00:00", "Z"),
        "to": end_utc.isoformat().replace("+00:00", "Z"),
        "granularity": "M1",
        "price": "M",  # mid
    }

    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
    client.request(r)
    candles = r.response.get("candles", [])

    rows = []
    for c in candles:
        if not c.get("complete"):
            continue
        t = c["time"]
        mid = c["mid"]
        rows.append({
            "time": pd.to_datetime(t, utc=True),
            "open": float(mid["o"]),
            "high": float(mid["h"]),
            "low": float(mid["l"]),
            "close": float(mid["c"]),
            # tick volume
            "volume": int(c.get("volume", 0)),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("time").set_index("time")
    return df

# ---------- resample ----------
def resample_to_2h(df_m1: pd.DataFrame) -> pd.DataFrame:
    if df_m1.empty:
        return df_m1

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

# ---------- insert ----------
INSERT_SQL = """
INSERT INTO ovc_blocks_v01
(schema_ver, source, symbol, block_type, block_start, open, high, low, close, volume)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (symbol, block_start, block_type, schema_ver) DO NOTHING;
"""

def insert_blocks(df_blocks: pd.DataFrame) -> int:
    if df_blocks.empty:
        return 0
    tuples = [tuple(x) for x in df_blocks.to_numpy()]
    with psycopg2.connect(NEON_DSN) as conn:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, tuples)
            # cur.rowcount is unreliable with executemany for some drivers, so count via select diff is extra work.
    return len(tuples)

# ---------- main ----------
if __name__ == "__main__":
    end_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start_utc = end_utc - timedelta(days=3)

    print(f"Fetching OANDA M1: {start_utc.isoformat()} → {end_utc.isoformat()}")
    df_m1 = fetch_oanda_m1(start_utc, end_utc)
    print(f"M1 candles: {len(df_m1)}")

    df_2h = resample_to_2h(df_m1)
    print(f"2H blocks: {len(df_2h)}")

    n = insert_blocks(df_2h)
    print(f"Attempted inserts: {n} (rerun-safe via PK)")
    print("STEP 3 DONE (first real backfill slice).")
