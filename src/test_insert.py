import os
from datetime import datetime, timezone
import psycopg2

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

DSN = os.environ.get("NEON_DSN")
if not DSN:
    raise SystemExit("Missing NEON_DSN in .env")

row = {
    "schema_ver": "v0.1-min",
    "source": "manual-test",
    "symbol": "GBPUSD",
    "block_type": "2H",
    "block_start": datetime(2026, 1, 13, 0, 0, tzinfo=timezone.utc),
    "open": 1.25000,
    "high": 1.25500,
    "low": 1.24500,
    "close": 1.25250,
    "volume": 12345,
}

SQL = """
INSERT INTO ovc_blocks_v01
(schema_ver, source, symbol, block_type, block_start, open, high, low, close, volume)
VALUES (%(schema_ver)s, %(source)s, %(symbol)s, %(block_type)s, %(block_start)s,
        %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s)
ON CONFLICT (symbol, block_start, block_type, schema_ver)
DO NOTHING;
"""

SELECT_ONE = """
SELECT schema_ver, source, symbol, block_type, block_start, open, high, low, close, volume
FROM ovc_blocks_v01
WHERE symbol = %(symbol)s
  AND block_start = %(block_start)s
  AND block_type = %(block_type)s
  AND schema_ver = %(schema_ver)s;
"""

def run_once(label: str):
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL, row)
            inserted = cur.rowcount  # 1 if inserted, 0 if conflict/do nothing
            cur.execute(SELECT_ONE, row)
            got = cur.fetchone()
    print(f"{label}: inserted={inserted}, row_exists={got is not None}")

if __name__ == "__main__":
    run_once("FIRST RUN")
    run_once("SECOND RUN (should be 0)")
