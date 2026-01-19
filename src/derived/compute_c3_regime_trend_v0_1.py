"""
OVC C3 Regime Trend Classifier (v0.1)

================================================================================
REFERENCE IMPLEMENTATION FOR C3 TAGS
================================================================================
This script is the canonical reference for all future C3 classifiers.
New C3 tags MUST follow the same patterns for:
    - Threshold pack resolution (resolve once at start, not per-block)
    - C1/C2 data fetching (never query B-layer OHLC directly)
    - Classification logic structure (pure function of inputs + config)
    - Provenance column population (pack_id, version, hash from resolved pack)
    - Upsert mechanics (ON CONFLICT DO UPDATE for idempotence)

Before implementing a new C3 tag, read:
    - docs/c3_semantic_contract_v0_1.md (rules and invariants)
    - docs/c3_entry_checklist.md (required artifacts)
    - docs/option_threshold_registry_runbook.md (C3 Lifecycle section)
================================================================================

Purpose: Classify market regime as TREND or NON_TREND using C1/C2 features
         and versioned threshold packs from the registry.

Tier Boundary (per c_layer_boundary_spec_v0.1.md):
    C3 = Semantic tags derived from C1/C2 features + threshold packs.
    All semantic decisions come from versioned threshold packs.
    Every output row stores threshold provenance for replay certification.

C1/C2 Inputs Used:
    - direction (C1): +1/-1/0 for bullish/bearish/neutral
    - range (C1): h - l in price units
    - hh_12 (C2): Boolean, h > max(h[-12:-1])
    - ll_12 (C2): Boolean, l < min(l[-12:-1])

Classification Logic:
    TREND if ALL conditions met over lookback window:
        1. Average range >= min_range_bp (in basis points)
        2. Direction ratio >= min_direction_ratio_bp (bps of 1.0)
           where direction_ratio = abs(sum(direction)) / count
        3. hh_12 or ll_12 count >= min_hh_ll_count

    NON_TREND otherwise.

Usage:
    python src/derived/compute_c3_regime_trend_v0_1.py \\
        --symbol GBPUSD \\
        --threshold-pack c3_regime_trend \\
        --scope GLOBAL \\
        [--threshold-version 1] \\
        [--run-id <uuid>] \\
        [--dry-run] \\
        [--recompute]

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Guarantees:
    - Deterministic: Same C1/C2 inputs + same threshold pack => same outputs
    - Idempotent: Reruns produce identical results (upsert on symbol, ts)
    - Auditable: Every row stores threshold pack provenance
"""

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

# ---------- Add parent to path for local imports ----------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from config.threshold_registry_v0_1 import (
    ThresholdRegistry,
    PackNotFoundError,
    ScopeValidationError,
    get_active_pack,
    get_pack,
)

from ovc_ops.run_artifact import RunWriter, detect_trigger


# ---------- Tiny .env loader (matches B.1/B.2 convention) ----------
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
RUN_TYPE = "c3_regime_trend"
C3_TABLE = "derived.ovc_c3_regime_trend_v0_1"
PIPELINE_ID = "B1-DerivedC3"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN"]

# Price reference for basis point calculations (default for forex)
# 1 pip = 0.0001, 1 bp = 0.01% = 0.0001 for price ratio
# For range_bp, we use: range_bp = (range / price) * 10000
PRICE_SCALE = 10000  # Multiply by this to get basis points


def resolve_dsn() -> str:
    """Resolve database connection string from environment."""
    dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing NEON_DSN or DATABASE_URL in environment")
    return dsn


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Compute C3 regime trend classifications from C1/C2 features."
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Symbol to process (e.g., GBPUSD)",
    )
    parser.add_argument(
        "--threshold-pack",
        required=True,
        help="Threshold pack ID (e.g., c3_regime_trend)",
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Scope for threshold pack resolution",
    )
    parser.add_argument(
        "--threshold-version",
        type=int,
        default=None,
        help="Override threshold pack version (default: use active)",
    )
    parser.add_argument(
        "--scope-symbol",
        default=None,
        help="Symbol for SYMBOL/SYMBOL_TF scope (defaults to --symbol)",
    )
    parser.add_argument(
        "--timeframe",
        default=None,
        help="Timeframe for SYMBOL_TF scope",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Override run ID (default: auto-generated UUIDv4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be computed without writing to DB",
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="Recompute all blocks (default: skip existing)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of blocks to process (for testing)",
    )
    return parser.parse_args()


def resolve_threshold_pack(
    pack_id: str,
    scope: str,
    symbol: Optional[str],
    timeframe: Optional[str],
    version_override: Optional[int],
) -> Dict[str, Any]:
    """
    Resolve threshold pack from registry.
    
    Args:
        pack_id: Threshold pack identifier.
        scope: GLOBAL, SYMBOL, or SYMBOL_TF.
        symbol: Symbol for SYMBOL/SYMBOL_TF scope.
        timeframe: Timeframe for SYMBOL_TF scope.
        version_override: If provided, fetch specific version instead of active.
        
    Returns:
        Dict with pack_id, pack_version, config_hash, config_json.
    """
    registry = ThresholdRegistry()
    
    if version_override is not None:
        # Fetch specific version
        pack = registry.get_pack(pack_id, version_override)
    else:
        # Fetch active version for selector
        pack = registry.get_active_pack(pack_id, scope, symbol, timeframe)
    
    return pack


def fetch_c1_c2_data(
    cur,
    symbol: str,
    recompute: bool,
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    """
    Fetch C1/C2 features for classification.
    
    Returns list of dicts with:
        block_id, symbol, ts, direction, range, hh_12, ll_12, c (for bp calc)
    """
    # Build query to join B, C1, C2
    # If not recompute, exclude blocks that already have C3 rows
    exclude_clause = ""
    if not recompute:
        exclude_clause = f"""
            AND NOT EXISTS (
                SELECT 1 FROM {C3_TABLE} c3 
                WHERE c3.block_id = b.block_id
            )
        """
    
    limit_clause = f"LIMIT {limit}" if limit else ""
    
    query = f"""
        SELECT 
            b.block_id,
            b.sym AS symbol,
            b.bar_close_ms,
            b.c,
            c1.direction,
            c1.range,
            c2.hh_12,
            c2.ll_12
        FROM ovc.ovc_blocks_v01_1_min b
        JOIN derived.ovc_c1_features_v0_1 c1 ON b.block_id = c1.block_id
        JOIN derived.ovc_c2_features_v0_1 c2 ON b.block_id = c2.block_id
        WHERE b.sym = %s
        {exclude_clause}
        ORDER BY b.bar_close_ms ASC
        {limit_clause}
    """
    
    cur.execute(query, (symbol,))
    
    rows = []
    for row in cur.fetchall():
        rows.append({
            "block_id": row[0],
            "symbol": row[1],
            "bar_close_ms": row[2],
            "c": float(row[3]) if row[3] is not None else None,
            "direction": row[4],
            "range": float(row[5]) if row[5] is not None else None,
            "hh_12": row[6],
            "ll_12": row[7],
        })
    
    return rows


def classify_regime_trend(
    blocks: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Classify each block as TREND or NON_TREND.
    
    Classification uses a rolling window approach:
        - For each block, look at the lookback window (including current)
        - Calculate metrics and compare against thresholds
    
    Args:
        blocks: List of block data dicts (must be sorted by ts).
        config: Threshold config from pack (lookback, min_range_bp, etc.).
        
    Returns:
        List of classification results with block_id, symbol, ts, c3_regime_trend.
    """
    lookback = config.get("lookback", 12)
    min_range_bp = config.get("min_range_bp", 30)
    min_direction_ratio_bp = config.get("min_direction_ratio_bp", 600)
    min_hh_ll_count = config.get("min_hh_ll_count", 3)
    
    results = []
    
    for i, block in enumerate(blocks):
        # Get lookback window (up to and including current block)
        window_start = max(0, i - lookback + 1)
        window = blocks[window_start:i + 1]
        
        # Calculate metrics over window
        directions = [b["direction"] for b in window if b["direction"] is not None]
        ranges = [b["range"] for b in window if b["range"] is not None]
        prices = [b["c"] for b in window if b["c"] is not None]
        hh_ll_count = sum(1 for b in window if b.get("hh_12") or b.get("ll_12"))
        
        # Default to NON_TREND if insufficient data
        if len(directions) < lookback // 2 or len(ranges) < lookback // 2:
            classification = "NON_TREND"
        else:
            # Calculate direction ratio (absolute sum / count)
            # A value of 1.0 (1000 bp) means all bars same direction
            direction_sum = sum(directions)
            direction_ratio = abs(direction_sum) / len(directions) if directions else 0
            direction_ratio_bp = int(direction_ratio * 1000)  # Convert to bp
            
            # Calculate average range in basis points
            avg_range = sum(ranges) / len(ranges) if ranges else 0
            avg_price = sum(prices) / len(prices) if prices else 1.0
            range_bp = int((avg_range / avg_price) * PRICE_SCALE) if avg_price > 0 else 0
            
            # Apply classification logic
            is_trend = (
                range_bp >= min_range_bp
                and direction_ratio_bp >= min_direction_ratio_bp
                and hh_ll_count >= min_hh_ll_count
            )
            
            classification = "TREND" if is_trend else "NON_TREND"
        
        # Convert bar_close_ms to timestamp
        ts = datetime.fromtimestamp(block["bar_close_ms"] / 1000, tz=timezone.utc)
        
        results.append({
            "block_id": block["block_id"],
            "symbol": block["symbol"],
            "ts": ts,
            "c3_regime_trend": classification,
        })
    
    return results


def write_c3_rows(
    cur,
    conn,
    results: List[Dict[str, Any]],
    pack_id: str,
    pack_version: int,
    pack_hash: str,
    run_id: str,
) -> int:
    """
    Write C3 classification rows to database.
    
    Uses upsert (ON CONFLICT DO UPDATE) for idempotency.
    
    Returns:
        Number of rows written.
    """
    if not results:
        return 0
    
    # Build insert values
    values = [
        (
            r["block_id"],
            r["symbol"],
            r["ts"],
            r["c3_regime_trend"],
            pack_id,
            pack_version,
            pack_hash,
            run_id,
        )
        for r in results
    ]
    
    insert_sql = f"""
        INSERT INTO {C3_TABLE} (
            block_id, symbol, ts, c3_regime_trend,
            threshold_pack_id, threshold_pack_version, threshold_pack_hash,
            run_id
        )
        VALUES %s
        ON CONFLICT (symbol, ts) DO UPDATE SET
            block_id = EXCLUDED.block_id,
            c3_regime_trend = EXCLUDED.c3_regime_trend,
            threshold_pack_id = EXCLUDED.threshold_pack_id,
            threshold_pack_version = EXCLUDED.threshold_pack_version,
            threshold_pack_hash = EXCLUDED.threshold_pack_hash,
            run_id = EXCLUDED.run_id,
            created_at = now()
    """
    
    execute_values(cur, insert_sql, values)
    conn.commit()
    
    return len(values)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    artifact_run_id = writer.start(trigger_type, trigger_source, actor)
    
    try:
        # Generate run ID if not provided
        run_id = args.run_id or str(uuid.uuid4())
        
        writer.log(f"[C3 Regime Trend v0.1] Starting classification")
        writer.log(f"  Symbol: {args.symbol}")
        writer.log(f"  Threshold Pack: {args.threshold_pack}")
        writer.log(f"  Scope: {args.scope}")
        writer.log(f"  Run ID: {run_id}")
        writer.log("")
        
        writer.add_input(type="neon_table", ref="derived.ovc_block_features_c1_v0_1")
        writer.add_input(type="neon_table", ref="derived.ovc_block_features_c2_v0_1")
        
        # Resolve threshold pack
        try:
            scope_symbol = args.scope_symbol if args.scope != "GLOBAL" else None
            if args.scope == "SYMBOL" and scope_symbol is None:
                scope_symbol = args.symbol
            
            pack = resolve_threshold_pack(
                pack_id=args.threshold_pack,
                scope=args.scope,
                symbol=scope_symbol,
                timeframe=args.timeframe,
                version_override=args.threshold_version,
            )
        except PackNotFoundError as e:
            writer.log(f"ERROR: {e}")
            writer.log("")
            writer.log("To create and activate the threshold pack, run:")
            writer.log(f'  python -m src.config.threshold_registry_cli create --pack-id {args.threshold_pack} --version 1 --scope {args.scope} --config-file configs/threshold_packs/c3_regime_trend_v1.json')
            writer.log(f'  python -m src.config.threshold_registry_cli activate --pack-id {args.threshold_pack} --version 1 --scope {args.scope}')
            writer.check("threshold_pack_resolved", "Threshold pack resolved", "fail", [])
            writer.finish("failed")
            sys.exit(1)
        except ScopeValidationError as e:
            writer.log(f"ERROR: {e}")
            writer.check("threshold_pack_resolved", "Threshold pack resolved", "fail", [])
            writer.finish("failed")
            sys.exit(1)
        
        pack_id = pack["pack_id"]
        pack_version = pack["pack_version"]
        pack_hash = pack["config_hash"]
        config = pack["config_json"]
        
        writer.log(f"Resolved threshold pack:")
        writer.log(f"  Pack ID: {pack_id}")
        writer.log(f"  Version: {pack_version}")
        writer.log(f"  Hash: {pack_hash}")
        writer.log(f"  Config: {config}")
        writer.log("")
        
        # Connect to database
        dsn = resolve_dsn()
        
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Fetch C1/C2 data
                writer.log(f"Fetching C1/C2 data for {args.symbol}...")
                blocks = fetch_c1_c2_data(
                    cur=cur,
                    symbol=args.symbol,
                    recompute=args.recompute,
                    limit=args.limit,
                )
                writer.log(f"  Found {len(blocks)} blocks to process")
                
                if not blocks:
                    writer.log("No blocks to process. Done.")
                    writer.check("blocks_available", "Blocks available for processing", "skip", [])
                    writer.finish("success")
                    return
                
                # Classify regime trend
                writer.log("Classifying regime trend...")
                results = classify_regime_trend(blocks, config)
                
                # Count classifications
                trend_count = sum(1 for r in results if r["c3_regime_trend"] == "TREND")
                non_trend_count = len(results) - trend_count
                writer.log(f"  TREND: {trend_count}")
                writer.log(f"  NON_TREND: {non_trend_count}")
                writer.log("")
                
                if args.dry_run:
                    writer.log("[DRY-RUN] Would write to database:")
                    writer.log(f"  Table: {C3_TABLE}")
                    writer.log(f"  Rows: {len(results)}")
                    writer.log(f"  Threshold pack: {pack_id} v{pack_version}")
                    writer.log("")
                    # Show sample rows
                    writer.log("Sample rows (first 5):")
                    for r in results[:5]:
                        writer.log(f"  {r['block_id']}: {r['c3_regime_trend']}")
                    writer.check("dry_run", "Dry run completed", "pass", [])
                    writer.finish("success")
                    return
                
                # Write to database
                writer.log(f"Writing to {C3_TABLE}...")
                rows_written = write_c3_rows(
                    cur=cur,
                    conn=conn,
                    results=results,
                    pack_id=pack_id,
                    pack_version=pack_version,
                    pack_hash=pack_hash,
                    run_id=run_id,
                )
                writer.log(f"  Wrote {rows_written} rows")
        
        writer.log("")
        writer.log(f"[C3 Regime Trend v0.1] Completed successfully")
        writer.log(f"  Run ID: {run_id}")
        writer.log(f"  Threshold pack: {pack_id} v{pack_version} ({pack_hash[:16]}...)")
        
        writer.add_output(type="neon_table", ref=C3_TABLE, rows_written=rows_written)
        writer.check("classification_complete", "C3 regime trend classification completed", "pass", ["run.json:$.outputs[0].rows_written"])
        writer.finish("success")
        
    except Exception as e:
        writer.log(f"ERROR: {type(e).__name__}: {e}")
        writer.check("execution_error", f"Execution failed: {type(e).__name__}", "fail", [])
        writer.finish("failed")
        raise


if __name__ == "__main__":
    main()
