"""
OVC Option B.1: C1 Feature Pack Compute Script (v0.1)

Purpose: Compute single-bar OHLC primitives (C1 tier) from B-layer facts.

Tier Boundary (per c_layer_boundary_spec_v0.1.md):
    C1 = Single-bar OHLC math. No history, no lookback, no rolling windows.
    Inputs: ONLY {o, h, l, c} of current block.

C1 KEEP Set (per metric_trial_log_noncanonical_v0.md Section E.1):
    range, body, direction, ret, logret, body_ratio, close_pos,
    upper_wick, lower_wick, clv

Usage:
    python src/derived/compute_c1_v0_1.py [--dry-run] [--limit N] [--symbol SYM]

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Guarantees:
    - Deterministic: Same OHLC → same output, always
    - Idempotent: Reruns produce identical results (upsert on block_id)
    - Replayable: No external state required
"""

import argparse
import hashlib
import math
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

# ---------- Add parent to path for local imports ----------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ovc_ops.run_artifact import RunWriter, detect_trigger

# ---------- Tiny .env loader (matches backfill convention) ----------
def load_env(path: str = ".env") -> None:
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

# ---------- Constants ----------
VERSION = "v0.1"
RUN_TYPE = "c1"
PIPELINE_ID = "B1-DerivedC1"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN"]

# Formula definition string for hash computation
# This captures the exact computation logic; any change requires version bump
C1_FORMULA_DEFINITION = """
C1_FEATURES_V0.1:
range = h - l
body = abs(c - o)
direction = 1 if c > o else (-1 if c < o else 0)
ret = (c - o) / o if o != 0 else NULL
logret = ln(c / o) if o > 0 and c > 0 else NULL
body_ratio = body / range if range != 0 else NULL
close_pos = (c - l) / range if range != 0 else NULL
upper_wick = h - max(o, c)
lower_wick = min(o, c) - l
clv = ((c - l) - (h - c)) / (h - l) if (h - l) != 0 else NULL
range_zero = (range == 0)
inputs_valid = (o IS NOT NULL AND h IS NOT NULL AND l IS NOT NULL AND c IS NOT NULL)
"""


def compute_formula_hash(formula_def: str) -> str:
    """Compute MD5 hash of formula definition for provenance tracking."""
    return hashlib.md5(formula_def.strip().encode("utf-8")).hexdigest()


FORMULA_HASH = compute_formula_hash(C1_FORMULA_DEFINITION)


def resolve_dsn() -> str:
    """Resolve database connection string from environment."""
    dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing NEON_DSN or DATABASE_URL in environment")
    return dsn


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Compute C1 (single-bar OHLC) features from B-layer facts."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be computed without writing to DB",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of blocks to process (for testing)",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default=None,
        help="Filter by symbol (e.g., GBPUSD)",
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="Recompute all blocks (default: skip existing)",
    )
    return parser.parse_args()


# ---------- C1 Computation Functions ----------

def compute_c1_features(o: float, h: float, l: float, c: float) -> dict:
    """
    Compute C1 single-bar OHLC features.
    
    Per c_layer_boundary_spec_v0.1.md Section A (C1 — Single-Bar Primitives):
        "Formulas that operate on {o, h, l, c} of ONE block only.
        No lookback, no history, no rolling windows."
    
    Returns dict with all C1 features. NULL values are Python None.
    """
    # Validate inputs
    inputs_valid = all(x is not None for x in [o, h, l, c])
    if not inputs_valid:
        return {
            "range": None,
            "body": None,
            "direction": 0,
            "ret": None,
            "logret": None,
            "body_ratio": None,
            "close_pos": None,
            "upper_wick": None,
            "lower_wick": None,
            "clv": None,
            "range_zero": True,
            "inputs_valid": False,
        }
    
    # C1 primitives
    range_val = h - l
    body = abs(c - o)
    direction = 1 if c > o else (-1 if c < o else 0)
    
    # Return (may be None if o=0)
    ret = (c - o) / o if o != 0 else None
    
    # Log return (requires positive o and c)
    logret = None
    if o > 0 and c > 0:
        logret = math.log(c / o)
    
    # Ratios (may be None if range=0)
    range_zero = (range_val == 0)
    body_ratio = body / range_val if not range_zero else None
    close_pos = (c - l) / range_val if not range_zero else None
    
    # Wicks
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    
    # CLV (Close Location Value)
    clv = None
    if not range_zero:
        clv = ((c - l) - (h - c)) / (h - l)
    
    return {
        "range": range_val,
        "body": body,
        "direction": direction,
        "ret": ret,
        "logret": logret,
        "body_ratio": body_ratio,
        "close_pos": close_pos,
        "upper_wick": upper_wick,
        "lower_wick": lower_wick,
        "clv": clv,
        "range_zero": range_zero,
        "inputs_valid": inputs_valid,
    }


# ---------- Database Operations ----------

def create_run_record(conn, run_id: uuid.UUID, config: dict) -> None:
    """Insert a run record into derived_runs_v0_1."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO derived.derived_runs_v0_1 (
                run_id, run_type, version, formula_hash, window_spec,
                threshold_version, started_at, status, config_snapshot
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(run_id),
            RUN_TYPE,
            VERSION,
            FORMULA_HASH,
            None,  # C1 has no window_spec
            None,  # C1 has no threshold_version
            datetime.now(timezone.utc),
            "running",
            psycopg2.extras.Json(config),
        ))
    conn.commit()


def complete_run_record(conn, run_id: uuid.UUID, block_count: int, status: str, error: str = None) -> None:
    """Update run record with completion status."""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE derived.derived_runs_v0_1
            SET completed_at = %s, block_count = %s, status = %s, error_message = %s
            WHERE run_id = %s
        """, (
            datetime.now(timezone.utc),
            block_count,
            status,
            error,
            str(run_id),
        ))
    conn.commit()


def fetch_blocks(conn, symbol: str = None, limit: int = None, recompute: bool = False) -> list:
    """
    Fetch B-layer blocks for C1 computation.
    
    Returns list of (block_id, o, h, l, c) tuples.
    """
    query = """
        SELECT b.block_id, b.o, b.h, b.l, b.c
        FROM ovc.ovc_blocks_v01_1_min b
    """
    conditions = []
    params = []
    
    if not recompute:
        query = """
            SELECT b.block_id, b.o, b.h, b.l, b.c
            FROM ovc.ovc_blocks_v01_1_min b
            LEFT JOIN derived.ovc_c1_features_v0_1 c1 ON b.block_id = c1.block_id
        """
        conditions.append("c1.block_id IS NULL")
    
    if symbol:
        conditions.append("b.sym = %s")
        params.append(symbol.upper())
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY b.bar_close_ms"
    
    if limit:
        query += f" LIMIT {limit}"
    
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def upsert_c1_features(conn, run_id: uuid.UUID, features_batch: list) -> int:
    """
    Upsert computed C1 features to derived.ovc_c1_features_v0_1.
    
    Uses ON CONFLICT DO UPDATE for idempotency.
    Returns count of rows upserted.
    """
    if not features_batch:
        return 0
    
    sql = """
        INSERT INTO derived.ovc_c1_features_v0_1 (
            block_id, run_id, computed_at, formula_hash, derived_version,
            range, body, direction, ret, logret, body_ratio, close_pos,
            upper_wick, lower_wick, clv, range_zero, inputs_valid
        ) VALUES %s
        ON CONFLICT (block_id) DO UPDATE SET
            run_id = EXCLUDED.run_id,
            computed_at = EXCLUDED.computed_at,
            formula_hash = EXCLUDED.formula_hash,
            derived_version = EXCLUDED.derived_version,
            range = EXCLUDED.range,
            body = EXCLUDED.body,
            direction = EXCLUDED.direction,
            ret = EXCLUDED.ret,
            logret = EXCLUDED.logret,
            body_ratio = EXCLUDED.body_ratio,
            close_pos = EXCLUDED.close_pos,
            upper_wick = EXCLUDED.upper_wick,
            lower_wick = EXCLUDED.lower_wick,
            clv = EXCLUDED.clv,
            range_zero = EXCLUDED.range_zero,
            inputs_valid = EXCLUDED.inputs_valid
    """
    
    now = datetime.now(timezone.utc)
    values = [
        (
            f["block_id"],
            str(run_id),
            now,
            FORMULA_HASH,
            VERSION,
            f["range"],
            f["body"],
            f["direction"],
            f["ret"],
            f["logret"],
            f["body_ratio"],
            f["close_pos"],
            f["upper_wick"],
            f["lower_wick"],
            f["clv"],
            f["range_zero"],
            f["inputs_valid"],
        )
        for f in features_batch
    ]
    
    with conn.cursor() as cur:
        execute_values(cur, sql, values)
    
    return len(values)


# ---------- Main Entry Point ----------

def main() -> None:
    args = parse_args()
    
    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    artifact_run_id = writer.start(trigger_type, trigger_source, actor)
    
    try:
        dsn = resolve_dsn()
        
        writer.log(f"OVC C1 Feature Compute v{VERSION}")
        writer.log(f"Formula hash: {FORMULA_HASH}")
        writer.log(f"Dry run: {args.dry_run}")
        if args.symbol:
            writer.log(f"Symbol filter: {args.symbol}")
        if args.limit:
            writer.log(f"Limit: {args.limit}")
        writer.log("")
        
        writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")
        
        run_id = uuid.uuid4()
        config = {
            "dry_run": args.dry_run,
            "limit": args.limit,
            "symbol": args.symbol,
            "recompute": args.recompute,
            "formula_hash": FORMULA_HASH,
            "version": VERSION,
        }
        
        conn = psycopg2.connect(dsn)
        
        try:
            if not args.dry_run:
                create_run_record(conn, run_id, config)
                writer.log(f"Run ID: {run_id}")
            
            # Fetch blocks to process
            blocks = fetch_blocks(conn, args.symbol, args.limit, args.recompute)
            writer.log(f"Blocks to process: {len(blocks)}")
            
            if not blocks:
                writer.log("No blocks to process.")
                if not args.dry_run:
                    complete_run_record(conn, run_id, 0, "completed")
                writer.check("blocks_available", "Blocks available for processing", "skip", [])
                writer.finish("success")
                return
            
            # Compute C1 features
            features_batch = []
            for block_id, o, h, l, c in blocks:
                features = compute_c1_features(o, h, l, c)
                features["block_id"] = block_id
                features_batch.append(features)
            
            if args.dry_run:
                writer.log("\nSample computed features (first 3):")
                for f in features_batch[:3]:
                    writer.log(f"  {f['block_id']}: range={f['range']:.5f}, body={f['body']:.5f}, "
                          f"dir={f['direction']}, ret={f['ret']:.6f if f['ret'] else 'NULL'}")
                writer.log(f"\nDry run complete. Would upsert {len(features_batch)} rows.")
                writer.check("dry_run", "Dry run completed", "pass", [])
                writer.finish("success")
                return
            
            # Upsert in batches
            batch_size = 1000
            total_upserted = 0
            for i in range(0, len(features_batch), batch_size):
                batch = features_batch[i:i + batch_size]
                count = upsert_c1_features(conn, run_id, batch)
                total_upserted += count
                conn.commit()
                writer.log(f"  Upserted batch {i // batch_size + 1}: {count} rows")
            
            complete_run_record(conn, run_id, total_upserted, "completed")
            writer.log(f"\nCompleted. Total rows upserted: {total_upserted}")
            
            writer.add_output(type="neon_table", ref="derived.ovc_block_features_c1_v0_1", rows_written=total_upserted)
            writer.check("features_computed", "C1 features computed", "pass", ["run.json:$.outputs[0].rows_written"])
            writer.finish("success")
            
        except Exception as e:
            if not args.dry_run:
                complete_run_record(conn, run_id, 0, "failed", str(e))
            raise
        finally:
            conn.close()
            
    except Exception as e:
        writer.log(f"ERROR: {type(e).__name__}: {e}")
        writer.check("execution_error", f"Execution failed: {type(e).__name__}", "fail", [])
        writer.finish("failed")
        raise


if __name__ == "__main__":
    main()
