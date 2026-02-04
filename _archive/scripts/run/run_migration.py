"""Run a SQL migration file against Neon database."""
import os
import sys
from pathlib import Path

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

import psycopg2

dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
if not dsn:
    print("ERROR: Missing NEON_DSN or DATABASE_URL")
    sys.exit(1)

sql_file = sys.argv[1] if len(sys.argv) > 1 else "sql/03_qa_derived_validation_v0_1.sql"
sql_path = Path(__file__).resolve().parents[1] / sql_file

print(f"Running migration: {sql_path}")
with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute(sql_path.read_text())
    conn.commit()
print("Migration complete")
