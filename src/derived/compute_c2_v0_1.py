"""
OVC Option B.1: C2 Feature Pack Compute Script (v0.1)

Purpose: Compute multi-bar structure/context features (C2 tier) from B-layer facts + C1 outputs.

Tier Boundary (per c_layer_boundary_spec_v0.1.md):
    C2 = Multi-bar structure & context. Requires explicit window_spec.
    Inputs: B-layer OHLC sequence + C1 outputs.

C2 KEEP Set (per mapping_validation_report_v0.1.md Section 1.1 and 1.2):
    N=1:           gap, took_prev_high, took_prev_low
    session=date_ny: sess_high, sess_low, dist_sess_high, dist_sess_low
    N=12:          roll_avg_range_12, roll_std_logret_12, range_z_12, hh_12, ll_12
    parameterized=rd_len: rd_hi, rd_lo, rd_mid

Usage:
    python src/derived/compute_c2_v0_1.py [--dry-run] [--limit N] [--symbol SYM] [--rd-len N]

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Guarantees:
    - Deterministic: Same OHLC sequence + window_spec → same output
    - Idempotent: Reruns produce identical results (upsert on block_id)
    - Window_spec documented: All features have explicit window specification
"""

import argparse
import hashlib
import math
import os
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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
RUN_TYPE = "c2"
PIPELINE_ID = "B1-DerivedC2"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN"]

# Default rd_len parameter (to be versioned in threshold_registry later)
DEFAULT_RD_LEN = 12

# Window specifications per feature family
WINDOW_SPECS = {
    "gap": "N=1",
    "took_prev_high": "N=1",
    "took_prev_low": "N=1",
    "sess_high": "session=date_ny",
    "sess_low": "session=date_ny",
    "dist_sess_high": "session=date_ny",
    "dist_sess_low": "session=date_ny",
    "roll_avg_range_12": "N=12",
    "roll_std_logret_12": "N=12",
    "range_z_12": "N=12",
    "hh_12": "N=12",
    "ll_12": "N=12",
    "rd_hi": "parameterized=rd_len",
    "rd_lo": "parameterized=rd_len",
    "rd_mid": "parameterized=rd_len",
}

# Formula definition string for hash computation
C2_FORMULA_DEFINITION = """
C2_FEATURES_V0.1:
# N=1 lookback
gap = o - prev_c
took_prev_high = h > prev_h
took_prev_low = l < prev_l

# Session context (session=date_ny)
sess_high = running max(h) within date_ny session
sess_low = running min(l) within date_ny session
dist_sess_high = sess_high - c
dist_sess_low = c - sess_low

# Rolling 12-bar (N=12)
roll_avg_range_12 = avg(range) over 12 blocks (requires count >= 12)
roll_std_logret_12 = stddev(logret) over 12 blocks (requires count >= 12)
range_z_12 = (range - roll_avg_range_12) / roll_std_range_12 if std != 0

# Structure breaks (N=12)
hh_12 = h > max(h[-12:-1])
ll_12 = l < min(l[-12:-1])

# Range detector numeric (parameterized=rd_len)
rd_hi = highest(h, rd_len)
rd_lo = lowest(l, rd_len)
rd_mid = (rd_hi + rd_lo) / 2
"""


def compute_formula_hash(formula_def: str, rd_len: int) -> str:
    """Compute MD5 hash of formula definition including parameters."""
    full_def = f"{formula_def.strip()}\nrd_len={rd_len}"
    return hashlib.md5(full_def.encode("utf-8")).hexdigest()


def build_aggregated_window_spec(rd_len: int) -> str:
    """Build aggregated window_spec string for provenance."""
    return f"N=1;N=12;session=date_ny;rd_len={rd_len}"


def resolve_dsn() -> str:
    """Resolve database connection string from environment."""
    dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing NEON_DSN or DATABASE_URL in environment")
    return dsn


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Compute C2 (multi-bar structure) features from B-layer + C1."
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
        "--rd-len",
        type=int,
        default=DEFAULT_RD_LEN,
        help=f"Range detector lookback length (default: {DEFAULT_RD_LEN})",
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="Recompute all blocks (default: skip existing)",
    )
    return parser.parse_args()


# ---------- C2 Computation Functions ----------

def compute_c2_features_for_block(
    block: dict,
    prev_block: Optional[dict],
    session_blocks: list,
    roll_12_blocks: list,
    rd_blocks: list,
    c1_features: dict,
    rd_len: int,
) -> dict:
    """
    Compute C2 multi-bar features for a single block.
    
    Per c_layer_boundary_spec_v0.1.md Section A (C2 — Multi-Bar Structure):
        "Features requiring lookback to prior blocks, rolling aggregations,
        or session context. Window specification must be explicit and versioned."
    
    Args:
        block: Current block {block_id, o, h, l, c, date_ny, bar_close_ms}
        prev_block: Previous block (for N=1 features) or None
        session_blocks: All blocks in current session up to current block (for session features)
        roll_12_blocks: Last 12 blocks including current (for N=12 features)
        rd_blocks: Last rd_len blocks including current (for RD features)
        c1_features: C1 computed features for current block {range, logret, ...}
        rd_len: Range detector lookback parameter
    
    Returns dict with all C2 features.
    """
    result = {
        "block_id": block["block_id"],
        "prev_block_exists": prev_block is not None,
        "sess_block_count": len(session_blocks),
        "roll_12_count": len(roll_12_blocks),
        "rd_count": len(rd_blocks),
    }
    
    # ----- N=1 Features: 1-bar lookback -----
    if prev_block:
        # gap = o - prev_c
        result["gap"] = block["o"] - prev_block["c"]
        # took_prev_high = h > prev_h
        result["took_prev_high"] = block["h"] > prev_block["h"]
        # took_prev_low = l < prev_l
        result["took_prev_low"] = block["l"] < prev_block["l"]
    else:
        result["gap"] = None
        result["took_prev_high"] = None
        result["took_prev_low"] = None
    
    # ----- Session Features: session=date_ny -----
    if session_blocks:
        highs = [b["h"] for b in session_blocks]
        lows = [b["l"] for b in session_blocks]
        result["sess_high"] = max(highs)
        result["sess_low"] = min(lows)
        result["dist_sess_high"] = result["sess_high"] - block["c"]
        result["dist_sess_low"] = block["c"] - result["sess_low"]
    else:
        result["sess_high"] = None
        result["sess_low"] = None
        result["dist_sess_high"] = None
        result["dist_sess_low"] = None
    
    # ----- N=12 Features: Rolling 12-bar stats -----
    if len(roll_12_blocks) >= 12:
        # roll_avg_range_12 = avg(range) over 12 blocks
        ranges = [b["h"] - b["l"] for b in roll_12_blocks[-12:]]
        result["roll_avg_range_12"] = sum(ranges) / 12
        
        # roll_std_range_12 (for z-score)
        avg_range = result["roll_avg_range_12"]
        variance = sum((r - avg_range) ** 2 for r in ranges) / (12 - 1)  # sample stddev
        std_range = math.sqrt(variance) if variance > 0 else 0
        
        # roll_std_logret_12 = stddev(logret) over 12 blocks
        logreturns = []
        for b in roll_12_blocks[-12:]:
            if b["o"] > 0 and b["c"] > 0:
                logreturns.append(math.log(b["c"] / b["o"]))
        
        if len(logreturns) >= 12:
            avg_logret = sum(logreturns) / len(logreturns)
            var_logret = sum((lr - avg_logret) ** 2 for lr in logreturns) / (len(logreturns) - 1)
            result["roll_std_logret_12"] = math.sqrt(var_logret) if var_logret > 0 else 0
        else:
            result["roll_std_logret_12"] = None
        
        # range_z_12 = (range - avg) / std
        current_range = c1_features.get("range", block["h"] - block["l"])
        if std_range > 0:
            result["range_z_12"] = (current_range - avg_range) / std_range
        else:
            result["range_z_12"] = None
        
        # hh_12 = h > max(h[-12:-1])
        # ll_12 = l < min(l[-12:-1])
        if len(roll_12_blocks) >= 2:
            prior_blocks = roll_12_blocks[-13:-1] if len(roll_12_blocks) > 12 else roll_12_blocks[:-1]
            if len(prior_blocks) >= 12:
                prior_highs = [b["h"] for b in prior_blocks[-12:]]
                prior_lows = [b["l"] for b in prior_blocks[-12:]]
                result["hh_12"] = block["h"] > max(prior_highs)
                result["ll_12"] = block["l"] < min(prior_lows)
            else:
                result["hh_12"] = None
                result["ll_12"] = None
        else:
            result["hh_12"] = None
            result["ll_12"] = None
    else:
        result["roll_avg_range_12"] = None
        result["roll_std_logret_12"] = None
        result["range_z_12"] = None
        result["hh_12"] = None
        result["ll_12"] = None
    
    # ----- RD Features: parameterized=rd_len -----
    result["rd_len_used"] = rd_len
    if len(rd_blocks) >= rd_len:
        rd_window = rd_blocks[-rd_len:]
        rd_highs = [b["h"] for b in rd_window]
        rd_lows = [b["l"] for b in rd_window]
        result["rd_hi"] = max(rd_highs)
        result["rd_lo"] = min(rd_lows)
        result["rd_mid"] = (result["rd_hi"] + result["rd_lo"]) / 2
    else:
        result["rd_hi"] = None
        result["rd_lo"] = None
        result["rd_mid"] = None
    
    return result


# ---------- Database Operations ----------

def create_run_record(conn, run_id: uuid.UUID, formula_hash: str, window_spec: str, config: dict) -> None:
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
            formula_hash,
            window_spec,
            None,  # C2 has no threshold_version
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


def fetch_blocks_with_context(conn, symbol: str = None, limit: int = None, recompute: bool = False) -> list:
    """
    Fetch B-layer blocks with ordering for C2 computation.
    
    Returns list of dicts with block data, ordered by symbol then bar_close_ms.
    """
    query = """
        SELECT 
            b.block_id, b.sym, b.date_ny, b.bar_close_ms,
            b.o, b.h, b.l, b.c
        FROM ovc.ovc_blocks_v01_1_min b
    """
    conditions = []
    params = []
    
    if not recompute:
        query = """
            SELECT 
                b.block_id, b.sym, b.date_ny, b.bar_close_ms,
                b.o, b.h, b.l, b.c
            FROM ovc.ovc_blocks_v01_1_min b
            LEFT JOIN derived.ovc_c2_features_v0_1 c2 ON b.block_id = c2.block_id
        """
        conditions.append("c2.block_id IS NULL")
    
    if symbol:
        conditions.append("b.sym = %s")
        params.append(symbol.upper())
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY b.sym, b.bar_close_ms"
    
    if limit:
        query += f" LIMIT {limit}"
    
    with conn.cursor() as cur:
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_c1_features(conn, block_ids: list) -> dict:
    """Fetch C1 features for given block_ids."""
    if not block_ids:
        return {}
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT block_id, range, logret
            FROM derived.ovc_c1_features_v0_1
            WHERE block_id = ANY(%s)
        """, (block_ids,))
        return {row[0]: {"range": row[1], "logret": row[2]} for row in cur.fetchall()}


def upsert_c2_features(conn, run_id: uuid.UUID, formula_hash: str, window_spec: str, features_batch: list) -> int:
    """
    Upsert computed C2 features to derived.ovc_c2_features_v0_1.
    
    Uses ON CONFLICT DO UPDATE for idempotency.
    Returns count of rows upserted.
    """
    if not features_batch:
        return 0
    
    sql = """
        INSERT INTO derived.ovc_c2_features_v0_1 (
            block_id, run_id, computed_at, formula_hash, derived_version, window_spec,
            gap, took_prev_high, took_prev_low,
            sess_high, sess_low, dist_sess_high, dist_sess_low,
            roll_avg_range_12, roll_std_logret_12, range_z_12,
            hh_12, ll_12,
            rd_len_used, rd_hi, rd_lo, rd_mid,
            prev_block_exists, sess_block_count, roll_12_count, rd_count
        ) VALUES %s
        ON CONFLICT (block_id) DO UPDATE SET
            run_id = EXCLUDED.run_id,
            computed_at = EXCLUDED.computed_at,
            formula_hash = EXCLUDED.formula_hash,
            derived_version = EXCLUDED.derived_version,
            window_spec = EXCLUDED.window_spec,
            gap = EXCLUDED.gap,
            took_prev_high = EXCLUDED.took_prev_high,
            took_prev_low = EXCLUDED.took_prev_low,
            sess_high = EXCLUDED.sess_high,
            sess_low = EXCLUDED.sess_low,
            dist_sess_high = EXCLUDED.dist_sess_high,
            dist_sess_low = EXCLUDED.dist_sess_low,
            roll_avg_range_12 = EXCLUDED.roll_avg_range_12,
            roll_std_logret_12 = EXCLUDED.roll_std_logret_12,
            range_z_12 = EXCLUDED.range_z_12,
            hh_12 = EXCLUDED.hh_12,
            ll_12 = EXCLUDED.ll_12,
            rd_len_used = EXCLUDED.rd_len_used,
            rd_hi = EXCLUDED.rd_hi,
            rd_lo = EXCLUDED.rd_lo,
            rd_mid = EXCLUDED.rd_mid,
            prev_block_exists = EXCLUDED.prev_block_exists,
            sess_block_count = EXCLUDED.sess_block_count,
            roll_12_count = EXCLUDED.roll_12_count,
            rd_count = EXCLUDED.rd_count
    """
    
    now = datetime.now(timezone.utc)
    values = [
        (
            f["block_id"],
            str(run_id),
            now,
            formula_hash,
            VERSION,
            window_spec,
            f["gap"],
            f["took_prev_high"],
            f["took_prev_low"],
            f["sess_high"],
            f["sess_low"],
            f["dist_sess_high"],
            f["dist_sess_low"],
            f["roll_avg_range_12"],
            f["roll_std_logret_12"],
            f["range_z_12"],
            f["hh_12"],
            f["ll_12"],
            f["rd_len_used"],
            f["rd_hi"],
            f["rd_lo"],
            f["rd_mid"],
            f["prev_block_exists"],
            f["sess_block_count"],
            f["roll_12_count"],
            f["rd_count"],
        )
        for f in features_batch
    ]
    
    with conn.cursor() as cur:
        execute_values(cur, sql, values)
    
    return len(values)


# ---------- Main Computation Logic ----------

def compute_all_c2_features(blocks: list, c1_features: dict, rd_len: int) -> list:
    """
    Compute C2 features for all blocks with proper context windows.
    
    Processes blocks in order, maintaining rolling windows per symbol.
    """
    # Group blocks by symbol
    blocks_by_symbol = defaultdict(list)
    for block in blocks:
        blocks_by_symbol[block["sym"]].append(block)
    
    # Sort each symbol's blocks by timestamp
    for sym in blocks_by_symbol:
        blocks_by_symbol[sym].sort(key=lambda b: b["bar_close_ms"])
    
    # Compute features for all blocks
    results = []
    
    for sym, sym_blocks in blocks_by_symbol.items():
        # Track context windows
        all_blocks_history = []  # All blocks seen for this symbol
        session_blocks = []      # Blocks in current session (date_ny)
        current_date_ny = None
        
        for i, block in enumerate(sym_blocks):
            # Reset session if date changed
            if block["date_ny"] != current_date_ny:
                session_blocks = []
                current_date_ny = block["date_ny"]
            
            # Add current block to session
            session_blocks.append(block)
            
            # Get previous block (N=1)
            prev_block = all_blocks_history[-1] if all_blocks_history else None
            
            # Build context windows
            all_blocks_history.append(block)
            
            # Rolling 12 blocks (including current)
            roll_12_blocks = all_blocks_history[-13:] if len(all_blocks_history) > 1 else all_blocks_history
            
            # RD blocks (including current)
            rd_blocks = all_blocks_history[-(rd_len + 1):] if len(all_blocks_history) > 1 else all_blocks_history
            
            # Get C1 features for current block
            c1 = c1_features.get(block["block_id"], {})
            
            # Compute C2 features
            features = compute_c2_features_for_block(
                block=block,
                prev_block=prev_block,
                session_blocks=session_blocks,
                roll_12_blocks=roll_12_blocks,
                rd_blocks=rd_blocks,
                c1_features=c1,
                rd_len=rd_len,
            )
            
            results.append(features)
    
    return results


# ---------- Main Entry Point ----------

def main() -> None:
    args = parse_args()
    
    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    artifact_run_id = writer.start(trigger_type, trigger_source, actor)
    
    try:
        dsn = resolve_dsn()
        
        rd_len = args.rd_len
        formula_hash = compute_formula_hash(C2_FORMULA_DEFINITION, rd_len)
        window_spec = build_aggregated_window_spec(rd_len)
        
        writer.log(f"OVC C2 Feature Compute v{VERSION}")
        writer.log(f"Formula hash: {formula_hash}")
        writer.log(f"Window spec: {window_spec}")
        writer.log(f"RD length: {rd_len}")
        writer.log(f"Dry run: {args.dry_run}")
        if args.symbol:
            writer.log(f"Symbol filter: {args.symbol}")
        if args.limit:
            writer.log(f"Limit: {args.limit}")
        writer.log("")
        
        writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")
        writer.add_input(type="neon_table", ref="derived.ovc_block_features_c1_v0_1")
        
        run_id = uuid.uuid4()
        config = {
            "dry_run": args.dry_run,
            "limit": args.limit,
            "symbol": args.symbol,
            "recompute": args.recompute,
            "rd_len": rd_len,
            "formula_hash": formula_hash,
            "window_spec": window_spec,
            "version": VERSION,
        }
        
        conn = psycopg2.connect(dsn)
        
        try:
            if not args.dry_run:
                create_run_record(conn, run_id, formula_hash, window_spec, config)
                writer.log(f"Run ID: {run_id}")
            
            # Fetch blocks to process
            blocks = fetch_blocks_with_context(conn, args.symbol, args.limit, args.recompute)
            writer.log(f"Blocks to process: {len(blocks)}")
            
            if not blocks:
                writer.log("No blocks to process.")
                if not args.dry_run:
                    complete_run_record(conn, run_id, 0, "completed")
                writer.check("blocks_available", "Blocks available for processing", "skip", [])
                writer.finish("success")
                return
            
            # Fetch C1 features for these blocks
            block_ids = [b["block_id"] for b in blocks]
            c1_features = fetch_c1_features(conn, block_ids)
            writer.log(f"C1 features loaded: {len(c1_features)}")
            
            # For complete context, we need ALL blocks for the symbol (for rolling windows)
            # Fetch full history for symbols in our block set
            symbols = list(set(b["sym"] for b in blocks))
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        block_id, sym, date_ny, bar_close_ms,
                        o, h, l, c
                    FROM ovc.ovc_blocks_v01_1_min
                    WHERE sym = ANY(%s)
                    ORDER BY sym, bar_close_ms
                """, (symbols,))
                columns = [desc[0] for desc in cur.description]
                all_blocks = [dict(zip(columns, row)) for row in cur.fetchall()]
            
            writer.log(f"Total blocks with history: {len(all_blocks)}")
            
            # Fetch C1 features for all blocks (needed for rolling calcs)
            all_block_ids = [b["block_id"] for b in all_blocks]
            c1_features = fetch_c1_features(conn, all_block_ids)
            
            # Compute C2 features
            all_c2_features = compute_all_c2_features(all_blocks, c1_features, rd_len)
            
            # Filter to only blocks we want to upsert
            target_block_ids = set(block_ids)
            features_batch = [f for f in all_c2_features if f["block_id"] in target_block_ids]
            
            if args.dry_run:
                writer.log("\nSample computed features (first 3):")
                for f in features_batch[:3]:
                    writer.log(f"  {f['block_id']}:")
                    writer.log(f"    gap={f['gap']}, took_prev_high={f['took_prev_high']}")
                    writer.log(f"    sess_high={f['sess_high']}, roll_avg_range_12={f['roll_avg_range_12']}")
                    writer.log(f"    hh_12={f['hh_12']}, rd_hi={f['rd_hi']}")
                writer.log(f"\nDry run complete. Would upsert {len(features_batch)} rows.")
                writer.check("dry_run", "Dry run completed", "pass", [])
                writer.finish("success")
                return
            
            # Upsert in batches
            batch_size = 1000
            total_upserted = 0
            for i in range(0, len(features_batch), batch_size):
                batch = features_batch[i:i + batch_size]
                count = upsert_c2_features(conn, run_id, formula_hash, window_spec, batch)
                total_upserted += count
                conn.commit()
                writer.log(f"  Upserted batch {i // batch_size + 1}: {count} rows")
            
            complete_run_record(conn, run_id, total_upserted, "completed")
            writer.log(f"\nCompleted. Total rows upserted: {total_upserted}")
            
            writer.add_output(type="neon_table", ref="derived.ovc_block_features_c2_v0_1", rows_written=total_upserted)
            writer.check("features_computed", "C2 features computed", "pass", ["run.json:$.outputs[0].rows_written"])
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
