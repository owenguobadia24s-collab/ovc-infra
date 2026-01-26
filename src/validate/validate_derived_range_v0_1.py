"""
OVC Option B.2: Derived Feature Pack Validator (v0.1)

Purpose: Validate L1/L2 derived feature packs against B-layer facts,
         with optional TradingView reference comparison.

Validation Checks:
    1. Coverage parity: count(B) == count(L1) == count(L2)
    2. Key uniqueness: no duplicate block_id in L1/L2
    3. Null/invalid checks: no NaN/Inf, deterministic nulls
    4. Window_spec enforcement: L2 has required window specs
    5. Determinism quickcheck: recompute sample blocks and verify

Usage:
    python src/validate/validate_derived_range_v0_1.py \\
        --symbol GBPUSD \\
        --start-date 2026-01-13 \\
        --end-date 2026-01-17 \\
        [--mode fail|skip] \\
        [--compare-tv] \\
        [--out artifacts]

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Artifacts Output:
    - derived_validation_report.json (machine-readable)
    - derived_validation_report.md (human-readable)
    - derived_validation_diffs.csv (if --compare-tv enabled)
"""

import argparse
import csv
import json
import math
import os
import random
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import psycopg2
from psycopg2.extras import RealDictCursor

# ---------- Add parent to path for local imports ----------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ovc_artifacts import make_run_dir, write_meta, write_latest
from ovc_ops.run_artifact import RunWriter, detect_trigger

# ---------- Tiny .env loader ----------
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
NY_TZ = ZoneInfo("America/New_York")
PIPELINE_ID = "B2-DerivedValidation"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["NEON_DSN"]

# Required window_spec components per L2 spec
REQUIRED_WINDOW_SPECS = ["N=1", "N=12", "session=date_ny", "rd_len="]

# L1 feature columns for null rate analysis
L1_FEATURE_COLUMNS = [
    "range", "body", "direction", "ret", "logret", 
    "body_ratio", "close_pos", "upper_wick", "lower_wick", "clv",
    "range_zero", "inputs_valid"
]

# L2 feature columns for null rate analysis
L2_FEATURE_COLUMNS = [
    "gap", "took_prev_high", "took_prev_low",
    "sess_high", "sess_low", "dist_sess_high", "dist_sess_low",
    "roll_avg_range_12", "roll_std_logret_12", "range_z_12",
    "hh_12", "ll_12", "rd_hi", "rd_lo", "rd_mid",
    "prev_block_exists", "sess_block_count", "roll_12_count", "rd_count"
]

# L3 classification tables and required provenance columns
L3_TABLES = {
    "l3_regime_trend": {
        "table": "derived.ovc_l3_regime_trend_v0_1",
        "classification_column": "l3_regime_trend",
        "valid_values": ["TREND", "NON_TREND"],
        "provenance_columns": ["threshold_pack_id", "threshold_pack_version", "threshold_pack_hash"],
    },
    # Future L3 classifiers can be added here
}

# L3 threshold pack configuration schema
C3_THRESHOLD_PACK_TABLE = "ovc_cfg.threshold_pack"
C3_THRESHOLD_PACK_ACTIVE_TABLE = "ovc_cfg.threshold_pack_active"


@dataclass
class ValidationResult:
    """Container for validation results."""
    run_id: str
    version: str
    symbol: str
    start_date: str
    end_date: str
    mode: str
    compare_tv: bool
    
    # Counts
    b_block_count: int = 0
    l1_row_count: int = 0
    l2_row_count: int = 0
    
    # Integrity checks
    coverage_parity: bool = True
    l1_duplicates: int = 0
    l2_duplicates: int = 0
    l1_null_rates: dict = field(default_factory=dict)
    l2_null_rates: dict = field(default_factory=dict)
    l2_window_spec_valid: bool = True
    l2_window_spec_errors: list = field(default_factory=list)
    
    # Determinism check
    determinism_sample_size: int = 0
    determinism_mismatches: int = 0
    determinism_details: list = field(default_factory=list)
    
    # TV comparison (optional)
    tv_comparison_enabled: bool = False
    tv_reference_available: bool = False
    tv_matched_blocks: int = 0
    tv_diff_summary: dict = field(default_factory=dict)
    tv_top_mismatches: list = field(default_factory=list)
    
    # L3 validation (per-classifier results)
    l3_enabled: bool = False
    l3_results: dict = field(default_factory=dict)  # {classifier_name: C3ValidationResult}
    
    # Overall status
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    status: str = "PASS"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class C3ValidationResult:
    """Container for per-classifier L3 validation results."""
    classifier_name: str
    table_name: str
    
    # Existence & counts
    table_exists: bool = False
    row_count: int = 0
    
    # Provenance validation
    provenance_null_count: int = 0
    provenance_columns_valid: bool = True
    
    # Registry integrity
    registry_packs_verified: int = 0
    registry_packs_missing: int = 0
    registry_hash_mismatches: int = 0
    registry_version_warnings: list = field(default_factory=list)
    
    # Classification value validation
    invalid_values: int = 0
    
    # Errors and warnings
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


def resolve_dsn() -> str:
    """Resolve database connection string from environment."""
    dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing NEON_DSN or DATABASE_URL in environment")
    return dsn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate L1/L2 derived feature packs against B-layer facts."
    )
    parser.add_argument("--symbol", default="GBPUSD", help="Symbol to validate")
    parser.add_argument("--start-date", required=True, help="Start date (NY, YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (NY, YYYY-MM-DD, inclusive)")
    parser.add_argument(
        "--mode",
        choices=["fail", "skip"],
        default="fail",
        help="Behavior for missing facts/rows (default: fail)"
    )
    parser.add_argument(
        "--compare-tv",
        action="store_true",
        help="Enable TradingView reference comparison (if available)"
    )
    parser.add_argument(
        "--tv-source",
        default=None,
        help="TradingView reference source (table or file path)"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=50,
        help="Number of blocks to sample for determinism check (default: 50)"
    )
    parser.add_argument(
        "--out",
        default="artifacts",
        help="Output directory for artifacts (default: artifacts)"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Override run ID (default: auto-generated)"
    )
    parser.add_argument(
        "--validate-c3",
        action="store_true",
        help="Enable L3 classifier validation (threshold provenance, registry integrity)"
    )
    parser.add_argument(
        "--c3-classifiers",
        nargs="+",
        default=None,
        help="Specific L3 classifiers to validate (default: all known classifiers)"
    )
    return parser.parse_args()


def parse_date(value: str):
    """Parse YYYY-MM-DD date string."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit(f"Invalid date format: {value}. Use YYYY-MM-DD.") from exc


def build_run_id(symbol: str, start_date, end_date, mode: str, compare_tv: bool) -> str:
    """Build deterministic run ID for reproducibility."""
    seed = f"validate_derived:{symbol}:{start_date}:{end_date}:{mode}:{compare_tv}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def table_exists(cur, qualified_name: str) -> bool:
    """Check if a table exists in the database."""
    cur.execute("SELECT to_regclass(%s);", (qualified_name,))
    (regclass,) = cur.fetchone()
    return regclass is not None


# ---------- Validation Check Functions ----------

def check_coverage_parity(cur, symbol: str, start_date, end_date) -> dict:
    """
    Check that B, L1, and L2 have matching block counts.
    """
    # Count B-layer blocks
    cur.execute("""
        SELECT COUNT(*) FROM ovc.ovc_blocks_v01_1_min
        WHERE sym = %s AND date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    b_count = cur.fetchone()[0]
    
    # Count L1 rows
    cur.execute("""
        SELECT COUNT(*) FROM derived.ovc_l1_features_v0_1 c1
        JOIN ovc.ovc_blocks_v01_1_min b ON c1.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    l1_count = cur.fetchone()[0]
    
    # Count L2 rows
    cur.execute("""
        SELECT COUNT(*) FROM derived.ovc_l2_features_v0_1 c2
        JOIN ovc.ovc_blocks_v01_1_min b ON c2.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    l2_count = cur.fetchone()[0]
    
    return {
        "b_count": b_count,
        "l1_count": l1_count,
        "l2_count": l2_count,
        "parity": b_count == l1_count == l2_count,
    }


def check_duplicates(cur, table: str, symbol: str, start_date, end_date) -> int:
    """Check for duplicate block_id values in derived table."""
    cur.execute(f"""
        SELECT COUNT(*) - COUNT(DISTINCT d.block_id) as duplicates
        FROM {table} d
        JOIN ovc.ovc_blocks_v01_1_min b ON d.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    return cur.fetchone()[0]


def check_null_rates(cur, table: str, columns: list, symbol: str, start_date, end_date) -> dict:
    """
    Calculate null rates for each column in the specified table.
    Returns dict of {column: null_rate}.
    """
    null_rates = {}
    
    # Build query to count nulls for each column
    col_cases = ", ".join([
        f"SUM(CASE WHEN d.{col} IS NULL THEN 1 ELSE 0 END) as null_{col}"
        for col in columns
    ])
    
    cur.execute(f"""
        SELECT COUNT(*) as total, {col_cases}
        FROM {table} d
        JOIN ovc.ovc_blocks_v01_1_min b ON d.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    
    row = cur.fetchone()
    total = row[0] if row[0] > 0 else 1  # Avoid division by zero
    
    for i, col in enumerate(columns):
        null_count = row[i + 1] or 0
        null_rates[col] = round(null_count / total, 4)
    
    return null_rates


def check_nan_inf(cur, table: str, columns: list, symbol: str, start_date, end_date) -> list:
    """Check for NaN or Inf values in numeric columns."""
    issues = []
    
    for col in columns:
        # Check for special float values
        cur.execute(f"""
            SELECT COUNT(*) FROM {table} d
            JOIN ovc.ovc_blocks_v01_1_min b ON d.block_id = b.block_id
            WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
            AND (d.{col} = 'NaN'::float OR d.{col} = 'Infinity'::float OR d.{col} = '-Infinity'::float)
        """, (symbol, start_date, end_date))
        count = cur.fetchone()[0]
        if count > 0:
            issues.append(f"{table}.{col}: {count} NaN/Inf values")
    
    return issues


def check_window_spec(cur, symbol: str, start_date, end_date) -> dict:
    """
    Validate that L2 rows have window_spec populated and contain required components.
    """
    # Check for NULL window_spec
    cur.execute("""
        SELECT COUNT(*) FROM derived.ovc_l2_features_v0_1 c2
        JOIN ovc.ovc_blocks_v01_1_min b ON c2.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
        AND c2.window_spec IS NULL
    """, (symbol, start_date, end_date))
    null_count = cur.fetchone()[0]
    
    # Get distinct window_specs
    cur.execute("""
        SELECT DISTINCT c2.window_spec FROM derived.ovc_l2_features_v0_1 c2
        JOIN ovc.ovc_blocks_v01_1_min b ON c2.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
        AND c2.window_spec IS NOT NULL
    """, (symbol, start_date, end_date))
    window_specs = [row[0] for row in cur.fetchall()]
    
    # Validate each window_spec contains required components
    errors = []
    for ws in window_specs:
        for req in REQUIRED_WINDOW_SPECS:
            if req not in ws:
                errors.append(f"window_spec '{ws}' missing required component '{req}'")
    
    return {
        "null_count": null_count,
        "distinct_specs": window_specs,
        "errors": errors,
        "valid": null_count == 0 and len(errors) == 0,
    }


def determinism_quickcheck(cur, symbol: str, start_date, end_date, sample_size: int) -> dict:
    """
    Sample blocks and recompute L1 values to verify determinism.
    Compare stored values vs freshly computed values.
    """
    # Fetch sample of blocks with B-layer OHLC and stored L1 values
    cur.execute("""
        SELECT 
            b.block_id, b.o, b.h, b.l, b.c,
            c1.range, c1.body, c1.direction, c1.ret, c1.logret,
            c1.body_ratio, c1.close_pos, c1.upper_wick, c1.lower_wick, c1.clv
        FROM ovc.ovc_blocks_v01_1_min b
        JOIN derived.ovc_l1_features_v0_1 c1 ON b.block_id = c1.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
        ORDER BY RANDOM()
        LIMIT %s
    """, (symbol, start_date, end_date, sample_size))
    
    samples = cur.fetchall()
    mismatches = []
    
    for row in samples:
        block_id, o, h, l, c = row[0], row[1], row[2], row[3], row[4]
        stored = {
            "range": row[5], "body": row[6], "direction": row[7],
            "ret": row[8], "logret": row[9], "body_ratio": row[10],
            "close_pos": row[11], "upper_wick": row[12], "lower_wick": row[13],
            "clv": row[14]
        }
        
        # Recompute L1 values
        computed = compute_l1_inline(o, h, l, c)
        
        # Compare with tolerance
        for key in ["range", "body", "upper_wick", "lower_wick"]:
            if not values_match(stored[key], computed[key]):
                mismatches.append({
                    "block_id": block_id,
                    "field": key,
                    "stored": stored[key],
                    "computed": computed[key],
                })
        
        # Integer comparison for direction
        if stored["direction"] != computed["direction"]:
            mismatches.append({
                "block_id": block_id,
                "field": "direction",
                "stored": stored["direction"],
                "computed": computed["direction"],
            })
        
        # Float comparisons with None handling
        for key in ["ret", "logret", "body_ratio", "close_pos", "clv"]:
            if not values_match(stored[key], computed[key]):
                mismatches.append({
                    "block_id": block_id,
                    "field": key,
                    "stored": stored[key],
                    "computed": computed[key],
                })
    
    return {
        "sample_size": len(samples),
        "mismatches": len(mismatches),
        "details": mismatches[:20],  # Limit to first 20
    }


def compute_l1_inline(o: float, h: float, l: float, c: float) -> dict:
    """
    Compute L1 features inline for determinism verification.
    Must match logic in compute_l1_v0_1.py exactly.
    """
    range_val = h - l
    body = abs(c - o)
    direction = 1 if c > o else (-1 if c < o else 0)
    
    ret = (c - o) / o if o != 0 else None
    logret = math.log(c / o) if o > 0 and c > 0 else None
    
    range_zero = (range_val == 0)
    body_ratio = body / range_val if not range_zero else None
    close_pos = (c - l) / range_val if not range_zero else None
    
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    
    clv = ((c - l) - (h - c)) / (h - l) if not range_zero else None
    
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
    }


def values_match(stored, computed, tolerance: float = 1e-9) -> bool:
    """Compare two values with tolerance for floats and None handling."""
    if stored is None and computed is None:
        return True
    if stored is None or computed is None:
        return False
    if isinstance(stored, (int, float)) and isinstance(computed, (int, float)):
        return abs(stored - computed) < tolerance
    return stored == computed


# ---------- TV Reference Comparison ----------

def check_tv_reference(cur, symbol: str, start_date, end_date) -> dict:
    """
    Compare L1/L2 derived features against TradingView reference data.
    TV data is in ovc.ovc_blocks_v01_1_min (rng, body, dir, ret fields).
    """
    # Check what TV-sourced blocks exist
    cur.execute("""
        SELECT COUNT(*) FROM ovc.ovc_blocks_v01_1_min
        WHERE sym = %s AND date_ny BETWEEN %s AND %s
        AND source = 'tv'
    """, (symbol, start_date, end_date))
    tv_count = cur.fetchone()[0]
    
    if tv_count == 0:
        return {
            "available": False,
            "message": "REFERENCE_NOT_AVAILABLE: No TV-sourced blocks in range",
        }
    
    # Compare L1 features against TV-stored values (rng, body, dir, ret)
    cur.execute("""
        SELECT 
            c1.block_id,
            b.rng as tv_range, c1.range as l1_range,
            b.body as tv_body, c1.body as l1_body,
            b.dir as tv_dir, c1.direction as l1_dir,
            b.ret as tv_ret, c1.ret as l1_ret
        FROM derived.ovc_l1_features_v0_1 c1
        JOIN ovc.ovc_blocks_v01_1_min b ON c1.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
        AND b.source = 'tv'
    """, (symbol, start_date, end_date))
    
    rows = cur.fetchall()
    
    # Calculate diff statistics
    diffs = {
        "range": {"sum_abs_diff": 0, "max_diff": 0, "mismatches": 0},
        "body": {"sum_abs_diff": 0, "max_diff": 0, "mismatches": 0},
        "direction": {"mismatches": 0},
        "ret": {"sum_abs_diff": 0, "max_diff": 0, "mismatches": 0},
    }
    
    top_mismatches = []
    
    for row in rows:
        block_id = row[0]
        tv_range, l1_range = row[1], row[2]
        tv_body, l1_body = row[3], row[4]
        tv_dir, l1_dir = row[5], row[6]
        tv_ret, l1_ret = row[7], row[8]
        
        # Range diff
        if tv_range is not None and l1_range is not None:
            diff = abs(tv_range - l1_range)
            diffs["range"]["sum_abs_diff"] += diff
            diffs["range"]["max_diff"] = max(diffs["range"]["max_diff"], diff)
            if diff > 1e-6:
                diffs["range"]["mismatches"] += 1
                top_mismatches.append({
                    "block_id": block_id,
                    "field": "range",
                    "tv": tv_range,
                    "l1": l1_range,
                    "diff": diff,
                })
        
        # Body diff
        if tv_body is not None and l1_body is not None:
            diff = abs(tv_body - l1_body)
            diffs["body"]["sum_abs_diff"] += diff
            diffs["body"]["max_diff"] = max(diffs["body"]["max_diff"], diff)
            if diff > 1e-6:
                diffs["body"]["mismatches"] += 1
                top_mismatches.append({
                    "block_id": block_id,
                    "field": "body",
                    "tv": tv_body,
                    "l1": l1_body,
                    "diff": diff,
                })
        
        # Direction diff
        if tv_dir is not None and l1_dir is not None:
            if tv_dir != l1_dir:
                diffs["direction"]["mismatches"] += 1
                top_mismatches.append({
                    "block_id": block_id,
                    "field": "direction",
                    "tv": tv_dir,
                    "l1": l1_dir,
                    "diff": abs(tv_dir - l1_dir),
                })
        
        # Ret diff
        if tv_ret is not None and l1_ret is not None:
            diff = abs(tv_ret - l1_ret)
            diffs["ret"]["sum_abs_diff"] += diff
            diffs["ret"]["max_diff"] = max(diffs["ret"]["max_diff"], diff)
            if diff > 1e-6:
                diffs["ret"]["mismatches"] += 1
                top_mismatches.append({
                    "block_id": block_id,
                    "field": "ret",
                    "tv": tv_ret,
                    "l1": l1_ret,
                    "diff": diff,
                })
    
    # Calculate mean abs diff
    n = len(rows) if rows else 1
    for key in ["range", "body", "ret"]:
        diffs[key]["mean_abs_diff"] = diffs[key]["sum_abs_diff"] / n
        diffs[key]["mismatch_rate"] = diffs[key]["mismatches"] / n
    diffs["direction"]["mismatch_rate"] = diffs["direction"]["mismatches"] / n
    
    # Sort top mismatches by diff (descending)
    top_mismatches.sort(key=lambda x: x.get("diff", 0), reverse=True)
    
    return {
        "available": True,
        "matched_blocks": len(rows),
        "diff_summary": diffs,
        "top_mismatches": top_mismatches[:50],
    }


# ---------- L3 Validation Functions ----------

def validate_l3_classifier(
    cur,
    classifier_name: str,
    config: dict,
    symbol: str,
    start_date,
    end_date
) -> C3ValidationResult:
    """
    Validate a single L3 classifier table.
    
    Checks:
    1. Table exists
    2. Row count matches expected (based on B-layer or L1)
    3. No NULL provenance columns (threshold_pack_id, version, hash)
    4. All referenced threshold packs exist in ovc_cfg.threshold_pack
    5. Stored hash matches registry hash
    6. Classification values are valid (in allowed set)
    """
    table = config["table"]
    classification_col = config["classification_column"]
    valid_values = config["valid_values"]
    provenance_cols = config["provenance_columns"]
    
    result = C3ValidationResult(
        classifier_name=classifier_name,
        table_name=table,
    )
    
    # 1. Check table exists
    result.table_exists = table_exists(cur, table)
    if not result.table_exists:
        result.errors.append(f"Table {table} does not exist")
        return result
    
    # 2. Count rows in range
    cur.execute(f"""
        SELECT COUNT(*) FROM {table} c3
        JOIN ovc.ovc_blocks_v01_1_min b ON c3.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    result.row_count = cur.fetchone()[0]
    
    if result.row_count == 0:
        result.warnings.append(f"No L3 rows found for {symbol} in date range")
        return result
    
    # 3. Check for NULL provenance columns
    for prov_col in provenance_cols:
        cur.execute(f"""
            SELECT COUNT(*) FROM {table} c3
            JOIN ovc.ovc_blocks_v01_1_min b ON c3.block_id = b.block_id
            WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
            AND c3.{prov_col} IS NULL
        """, (symbol, start_date, end_date))
        null_count = cur.fetchone()[0]
        if null_count > 0:
            result.provenance_null_count += null_count
            result.provenance_columns_valid = False
            result.errors.append(f"{prov_col} has {null_count} NULL values")
    
    # 4. Check classification values are valid
    valid_values_sql = ", ".join([f"'{v}'" for v in valid_values])
    cur.execute(f"""
        SELECT COUNT(*) FROM {table} c3
        JOIN ovc.ovc_blocks_v01_1_min b ON c3.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
        AND c3.{classification_col} NOT IN ({valid_values_sql})
    """, (symbol, start_date, end_date))
    result.invalid_values = cur.fetchone()[0]
    if result.invalid_values > 0:
        result.errors.append(f"{result.invalid_values} rows have invalid {classification_col} values")
    
    # 5. Verify threshold packs exist in registry and hashes match
    # First check if registry tables exist
    if not table_exists(cur, C3_THRESHOLD_PACK_TABLE):
        result.warnings.append("Threshold registry table not found, skipping pack verification")
        return result
    
    # Get distinct (pack_id, version, hash) from L3 data
    cur.execute(f"""
        SELECT DISTINCT 
            c3.threshold_pack_id,
            c3.threshold_pack_version,
            c3.threshold_pack_hash
        FROM {table} c3
        JOIN ovc.ovc_blocks_v01_1_min b ON c3.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    
    l3_packs = cur.fetchall()
    
    for pack_id, pack_version, l3_hash in l3_packs:
        # Check pack exists in registry
        cur.execute("""
            SELECT config_hash FROM ovc_cfg.threshold_pack
            WHERE pack_id = %s AND version = %s
        """, (pack_id, pack_version))
        registry_row = cur.fetchone()
        
        if registry_row is None:
            result.registry_packs_missing += 1
            result.errors.append(f"Threshold pack {pack_id} v{pack_version} not found in registry")
            continue
        
        result.registry_packs_verified += 1
        registry_hash = registry_row[0]
        
        # Verify hash matches
        if l3_hash != registry_hash:
            result.registry_hash_mismatches += 1
            result.errors.append(
                f"Hash mismatch for {pack_id} v{pack_version}: "
                f"L3={l3_hash[:16]}... registry={registry_hash[:16]}..."
            )
        
        # Optionally check if version equals active version (warning only)
        if table_exists(cur, C3_THRESHOLD_PACK_ACTIVE_TABLE):
            cur.execute("""
                SELECT version FROM ovc_cfg.threshold_pack_active
                WHERE pack_id = %s
            """, (pack_id,))
            active_row = cur.fetchone()
            
            if active_row and active_row[0] != pack_version:
                result.registry_version_warnings.append(
                    f"{pack_id}: using v{pack_version}, active is v{active_row[0]}"
                )
    
    return result


def check_c3_coverage_parity(cur, l3_table: str, symbol: str, start_date, end_date) -> dict:
    """
    Check that L3 rows match B-layer block count.
    Similar to L1/L2 parity but for L3.
    """
    # Count B-layer blocks
    cur.execute("""
        SELECT COUNT(*) FROM ovc.ovc_blocks_v01_1_min
        WHERE sym = %s AND date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    b_count = cur.fetchone()[0]
    
    # Count L3 rows
    cur.execute(f"""
        SELECT COUNT(*) FROM {l3_table} c3
        JOIN ovc.ovc_blocks_v01_1_min b ON c3.block_id = b.block_id
        WHERE b.sym = %s AND b.date_ny BETWEEN %s AND %s
    """, (symbol, start_date, end_date))
    l3_count = cur.fetchone()[0]
    
    return {
        "b_count": b_count,
        "l3_count": l3_count,
        "parity": b_count == l3_count,
    }


# ---------- QA Storage ----------

def store_validation_run(cur, result: ValidationResult) -> None:
    """Store validation run summary in ovc_qa schema."""
    cur.execute("""
        INSERT INTO ovc_qa.derived_validation_run (
            run_id, created_at, symbol, start_date, end_date,
            b_block_count, l1_row_count, l2_row_count,
            coverage_parity, l1_duplicates, l2_duplicates,
            l2_window_spec_valid, determinism_sample_size, determinism_mismatches,
            tv_comparison_enabled, tv_reference_available, tv_matched_blocks,
            status, errors, warnings
        ) VALUES (
            %s, NOW(), %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (run_id) DO UPDATE SET
            created_at = NOW(),
            b_block_count = EXCLUDED.b_block_count,
            l1_row_count = EXCLUDED.l1_row_count,
            l2_row_count = EXCLUDED.l2_row_count,
            coverage_parity = EXCLUDED.coverage_parity,
            status = EXCLUDED.status,
            errors = EXCLUDED.errors,
            warnings = EXCLUDED.warnings
    """, (
        result.run_id, result.symbol, result.start_date, result.end_date,
        result.b_block_count, result.l1_row_count, result.l2_row_count,
        result.coverage_parity, result.l1_duplicates, result.l2_duplicates,
        result.l2_window_spec_valid, result.determinism_sample_size, result.determinism_mismatches,
        result.tv_comparison_enabled, result.tv_reference_available, result.tv_matched_blocks,
        result.status, json.dumps(result.errors), json.dumps(result.warnings),
    ))


# ---------- Artifact Generation ----------

def generate_report_json(result: ValidationResult, out_path: Path) -> Path:
    """Generate machine-readable JSON report."""
    json_path = out_path / "derived_validation_report.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, default=str)
    return json_path


def generate_report_md(result: ValidationResult, out_path: Path) -> Path:
    """Generate human-readable Markdown report."""
    md_path = out_path / "derived_validation_report.md"
    
    lines = [
        f"# OVC Derived Validation Report",
        f"",
        f"**Run ID**: `{result.run_id}`",
        f"**Version**: {result.version}",
        f"**Symbol**: {result.symbol}",
        f"**Date Range**: {result.start_date} to {result.end_date}",
        f"**Mode**: {result.mode}",
        f"**Status**: **{result.status}**",
        f"",
        f"---",
        f"",
        f"## 1. Coverage Parity",
        f"",
        f"| Layer | Count |",
        f"|-------|-------|",
        f"| B-layer blocks | {result.b_block_count} |",
        f"| L1 rows | {result.l1_row_count} |",
        f"| L2 rows | {result.l2_row_count} |",
        f"",
        f"**Parity**: {'✅ PASS' if result.coverage_parity else '❌ FAIL'}",
        f"",
        f"## 2. Key Uniqueness",
        f"",
        f"| Table | Duplicates |",
        f"|-------|------------|",
        f"| L1 | {result.l1_duplicates} |",
        f"| L2 | {result.l2_duplicates} |",
        f"",
        f"## 3. Null Rates (L1)",
        f"",
        f"| Column | Null Rate |",
        f"|--------|-----------|",
    ]
    
    # Sort by null rate descending (top offenders first)
    sorted_c1_nulls = sorted(result.l1_null_rates.items(), key=lambda x: x[1], reverse=True)
    for col, rate in sorted_c1_nulls[:10]:
        lines.append(f"| {col} | {rate:.2%} |")
    
    lines.extend([
        f"",
        f"## 4. Null Rates (L2)",
        f"",
        f"| Column | Null Rate |",
        f"|--------|-----------|",
    ])
    
    sorted_c2_nulls = sorted(result.l2_null_rates.items(), key=lambda x: x[1], reverse=True)
    for col, rate in sorted_c2_nulls[:10]:
        lines.append(f"| {col} | {rate:.2%} |")
    
    lines.extend([
        f"",
        f"## 5. Window Spec Enforcement (L2)",
        f"",
        f"**Valid**: {'✅ PASS' if result.l2_window_spec_valid else '❌ FAIL'}",
        f"",
    ])
    
    if result.l2_window_spec_errors:
        lines.append("**Errors**:")
        for err in result.l2_window_spec_errors[:10]:
            lines.append(f"- {err}")
    
    lines.extend([
        f"",
        f"## 6. Determinism Quickcheck",
        f"",
        f"- Sample Size: {result.determinism_sample_size}",
        f"- Mismatches: {result.determinism_mismatches}",
        f"- **Result**: {'✅ PASS' if result.determinism_mismatches == 0 else '❌ FAIL'}",
        f"",
    ])
    
    if result.determinism_details:
        lines.append("**Top Mismatches**:")
        lines.append("| Block ID | Field | Stored | Computed |")
        lines.append("|----------|-------|--------|----------|")
        for d in result.determinism_details[:10]:
            lines.append(f"| {d['block_id']} | {d['field']} | {d['stored']} | {d['computed']} |")
    
    if result.tv_comparison_enabled:
        lines.extend([
            f"",
            f"## 7. TradingView Reference Comparison",
            f"",
            f"**Enabled**: Yes",
            f"**Reference Available**: {'Yes' if result.tv_reference_available else 'No'}",
            f"**Matched Blocks**: {result.tv_matched_blocks}",
            f"",
        ])
        
        if result.tv_diff_summary:
            lines.append("**Diff Summary**:")
            lines.append("| Field | Mean Abs Diff | Max Diff | Mismatch Rate |")
            lines.append("|-------|---------------|----------|---------------|")
            for field, stats in result.tv_diff_summary.items():
                mean = stats.get("mean_abs_diff", 0)
                max_d = stats.get("max_diff", 0)
                rate = stats.get("mismatch_rate", 0)
                lines.append(f"| {field} | {mean:.6f} | {max_d:.6f} | {rate:.2%} |")
    
    # L3 Classifier Validation Section
    if result.l3_enabled and result.l3_results:
        section_num = 8 if result.tv_comparison_enabled else 7
        lines.extend([
            f"",
            f"## {section_num}. L3 Classifier Validation",
            f"",
        ])
        
        for classifier_name, l3_data in result.l3_results.items():
            lines.extend([
                f"### {classifier_name}",
                f"",
                f"- **Table**: `{l3_data.get('table_name', 'unknown')}`",
                f"- **Table Exists**: {'✅' if l3_data.get('table_exists', False) else '❌'}",
            ])
            
            if l3_data.get('table_exists', False):
                lines.extend([
                    f"- **Row Count**: {l3_data.get('row_count', 0)}",
                    f"- **Provenance Valid**: {'✅' if l3_data.get('provenance_columns_valid', False) else '❌'}",
                    f"",
                    f"**Registry Integrity**:",
                    f"- Packs Verified: {l3_data.get('registry_packs_verified', 0)}",
                    f"- Packs Missing: {l3_data.get('registry_packs_missing', 0)}",
                    f"- Hash Mismatches: {l3_data.get('registry_hash_mismatches', 0)}",
                    f"- Invalid Classification Values: {l3_data.get('invalid_values', 0)}",
                    f"",
                ])
                
                # Version warnings
                version_warnings = l3_data.get('registry_version_warnings', [])
                if version_warnings:
                    lines.append("**Version Warnings**:")
                    for vw in version_warnings[:5]:
                        lines.append(f"- ⚠️ {vw}")
                    lines.append("")
            else:
                lines.append("")
    
    lines.extend([
        f"",
        f"---",
        f"",
        f"## Errors",
        f"",
    ])
    
    if result.errors:
        for e in result.errors:
            lines.append(f"- ❌ {e}")
    else:
        lines.append("None")
    
    lines.extend([
        f"",
        f"## Warnings",
        f"",
    ])
    
    if result.warnings:
        for w in result.warnings:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("None")
    
    lines.extend([
        f"",
        f"---",
        f"*Generated: {datetime.now(timezone.utc).isoformat()}*",
    ])
    
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def generate_diffs_csv(result: ValidationResult, out_path: Path) -> Optional[Path]:
    """Generate CSV of TV comparison diffs (if enabled and available)."""
    if not result.tv_comparison_enabled or not result.tv_reference_available:
        return None
    
    if not result.tv_top_mismatches:
        return None
    
    csv_path = out_path / "derived_validation_diffs.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["block_id", "field", "tv", "l1", "diff"])
        writer.writeheader()
        writer.writerows(result.tv_top_mismatches)
    
    return csv_path


# ---------- Main ----------

def main() -> int:
    args = parse_args()
    
    # Initialize run artifact writer
    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    artifact_run_id = writer.start(trigger_type, trigger_source, actor)
    
    try:
        start_date = parse_date(args.start_date)
        end_date = parse_date(args.end_date)
        
        if end_date < start_date:
            writer.log("ERROR: end-date must be on or after start-date")
            writer.check("date_range_valid", "Date range valid", "fail", [])
            writer.finish("failed")
            raise SystemExit("end-date must be on or after start-date")
        
        run_id = args.run_id or build_run_id(
            args.symbol, start_date, end_date, args.mode, args.compare_tv
        )
        
        result = ValidationResult(
            run_id=run_id,
            version=VERSION,
            symbol=args.symbol,
            start_date=str(start_date),
            end_date=str(end_date),
            mode=args.mode,
            compare_tv=args.compare_tv,
            tv_comparison_enabled=args.compare_tv,
        )
        
        writer.log(f"OVC Derived Validation v{VERSION}")
        writer.log(f"Run ID: {run_id}")
        writer.log(f"Symbol: {args.symbol}")
        writer.log(f"Range: {start_date} to {end_date}")
        writer.log(f"Mode: {args.mode}")
        writer.log(f"Compare TV: {args.compare_tv}")
        writer.log("")
        
        writer.add_input(type="neon_table", ref="derived.ovc_l1_features_v0_1")
        writer.add_input(type="neon_table", ref="derived.ovc_l2_features_v0_1")
        
        dsn = resolve_dsn()
    
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Check required tables exist
                if not table_exists(cur, "derived.ovc_l1_features_v0_1"):
                    result.errors.append("Table derived.ovc_l1_features_v0_1 does not exist")
                    result.status = "FAIL"
                    print("ERROR: L1 table not found")
                    return 1
                
                if not table_exists(cur, "derived.ovc_l2_features_v0_1"):
                    result.errors.append("Table derived.ovc_l2_features_v0_1 does not exist")
                    result.status = "FAIL"
                    print("ERROR: L2 table not found")
                    return 1
                
                # 1. Coverage parity
                print("Checking coverage parity...")
                coverage = check_coverage_parity(cur, args.symbol, start_date, end_date)
                result.b_block_count = coverage["b_count"]
                result.l1_row_count = coverage["l1_count"]
                result.l2_row_count = coverage["l2_count"]
                result.coverage_parity = coverage["parity"]
                
                if not coverage["parity"]:
                    msg = f"Coverage mismatch: B={coverage['b_count']}, L1={coverage['l1_count']}, L2={coverage['l2_count']}"
                    if args.mode == "fail":
                        result.errors.append(msg)
                    else:
                        result.warnings.append(msg)
                
                print(f"  B={coverage['b_count']}, L1={coverage['l1_count']}, L2={coverage['l2_count']}")
                
                # 2. Key uniqueness
                print("Checking key uniqueness...")
                result.l1_duplicates = check_duplicates(
                    cur, "derived.ovc_l1_features_v0_1", args.symbol, start_date, end_date
                )
                result.l2_duplicates = check_duplicates(
                    cur, "derived.ovc_l2_features_v0_1", args.symbol, start_date, end_date
                )
                
                if result.l1_duplicates > 0:
                    result.errors.append(f"L1 has {result.l1_duplicates} duplicate block_ids")
                if result.l2_duplicates > 0:
                    result.errors.append(f"L2 has {result.l2_duplicates} duplicate block_ids")
                
                print(f"  L1 duplicates: {result.l1_duplicates}, L2 duplicates: {result.l2_duplicates}")
                
                # 3. Null rates
                print("Checking null rates...")
                result.l1_null_rates = check_null_rates(
                    cur, "derived.ovc_l1_features_v0_1", L1_FEATURE_COLUMNS,
                    args.symbol, start_date, end_date
                )
                result.l2_null_rates = check_null_rates(
                    cur, "derived.ovc_l2_features_v0_1", L2_FEATURE_COLUMNS,
                    args.symbol, start_date, end_date
                )
                
                # Check for NaN/Inf
                nan_issues = check_nan_inf(
                    cur, "derived.ovc_l1_features_v0_1",
                    ["range", "body", "ret", "logret", "body_ratio", "close_pos", "upper_wick", "lower_wick", "clv"],
                    args.symbol, start_date, end_date
                )
                nan_issues.extend(check_nan_inf(
                    cur, "derived.ovc_l2_features_v0_1",
                    ["gap", "sess_high", "sess_low", "roll_avg_range_12", "roll_std_logret_12", "range_z_12", "rd_hi", "rd_lo", "rd_mid"],
                    args.symbol, start_date, end_date
                ))
                
                for issue in nan_issues:
                    result.errors.append(issue)
                
                print(f"  L1 columns with >10% null: {sum(1 for r in result.l1_null_rates.values() if r > 0.1)}")
                print(f"  L2 columns with >10% null: {sum(1 for r in result.l2_null_rates.values() if r > 0.1)}")
                
                # 4. Window_spec enforcement
                print("Checking window_spec enforcement...")
                ws_result = check_window_spec(cur, args.symbol, start_date, end_date)
                result.l2_window_spec_valid = ws_result["valid"]
                result.l2_window_spec_errors = ws_result["errors"]
                
                if not ws_result["valid"]:
                    if ws_result["null_count"] > 0:
                        result.errors.append(f"L2 has {ws_result['null_count']} rows with NULL window_spec")
                    for err in ws_result["errors"]:
                        result.errors.append(err)
                
                print(f"  Window_spec valid: {ws_result['valid']}")
                
                # 5. Determinism quickcheck
                print(f"Running determinism quickcheck (sample={args.sample_size})...")
                det_result = determinism_quickcheck(cur, args.symbol, start_date, end_date, args.sample_size)
                result.determinism_sample_size = det_result["sample_size"]
                result.determinism_mismatches = det_result["mismatches"]
                result.determinism_details = det_result["details"]
                
                if det_result["mismatches"] > 0:
                    result.errors.append(f"Determinism check failed: {det_result['mismatches']} mismatches in {det_result['sample_size']} samples")
                
                print(f"  Sampled: {det_result['sample_size']}, Mismatches: {det_result['mismatches']}")
                
                # 6. TV comparison (optional)
                if args.compare_tv:
                    print("Checking TV reference comparison...")
                    tv_result = check_tv_reference(cur, args.symbol, start_date, end_date)
                    result.tv_reference_available = tv_result.get("available", False)
                    
                    if result.tv_reference_available:
                        result.tv_matched_blocks = tv_result.get("matched_blocks", 0)
                        result.tv_diff_summary = tv_result.get("diff_summary", {})
                        result.tv_top_mismatches = tv_result.get("top_mismatches", [])
                        print(f"  TV blocks matched: {result.tv_matched_blocks}")
                    else:
                        result.warnings.append(tv_result.get("message", "TV reference not available"))
                        print(f"  {tv_result.get('message', 'TV reference not available')}")
                
                # 7. L3 validation (optional)
                if args.validate_c3:
                    result.l3_enabled = True
                    print("\n--- L3 Classifier Validation ---")
                    
                    # Determine which classifiers to validate
                    classifiers_to_check = args.l3_classifiers or list(L3_TABLES.keys())
                    
                    for classifier_name in classifiers_to_check:
                        if classifier_name not in L3_TABLES:
                            result.warnings.append(f"Unknown L3 classifier: {classifier_name}")
                            print(f"  WARN: Unknown classifier '{classifier_name}', skipping")
                            continue
                        
                        config = L3_TABLES[classifier_name]
                        print(f"\n  Validating {classifier_name} ({config['table']})...")
                        
                        l3_result = validate_l3_classifier(
                            cur, classifier_name, config,
                            args.symbol, start_date, end_date
                        )
                        
                        # Store result
                        result.l3_results[classifier_name] = l3_result.to_dict()
                        
                        # Print summary
                        if not l3_result.table_exists:
                            print(f"    Table not found: {config['table']}")
                        else:
                            print(f"    Rows: {l3_result.row_count}")
                            print(f"    Provenance valid: {l3_result.provenance_columns_valid}")
                            print(f"    Registry packs verified: {l3_result.registry_packs_verified}")
                            print(f"    Registry packs missing: {l3_result.registry_packs_missing}")
                            print(f"    Hash mismatches: {l3_result.registry_hash_mismatches}")
                            print(f"    Invalid values: {l3_result.invalid_values}")
                        
                        # Propagate errors/warnings to main result
                        for err in l3_result.errors:
                            result.errors.append(f"[L3:{classifier_name}] {err}")
                        for warn in l3_result.warnings:
                            result.warnings.append(f"[L3:{classifier_name}] {warn}")
                        
                        # Version warnings are informational
                        for vw in l3_result.registry_version_warnings:
                            result.warnings.append(f"[L3:{classifier_name}] Version warning: {vw}")
                
                # Determine final status
                if result.errors:
                    result.status = "FAIL"
                elif result.warnings:
                    result.status = "PASS_WITH_WARNINGS"
                else:
                    result.status = "PASS"
                
                # Store in QA schema if available
                if table_exists(cur, "ovc_qa.derived_validation_run"):
                    print("Storing validation run in QA schema...")
                    store_validation_run(cur, result)
                    conn.commit()
                else:
                    print("QA table not found, skipping storage")
        
        # Generate artifacts
        print("\nGenerating artifacts...")
        out_dir = Path(args.out) / "derived_validation" / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = generate_report_json(result, out_dir)
        md_path = generate_report_md(result, out_dir)
        csv_path = generate_diffs_csv(result, out_dir)
        
        # Write meta
        write_meta(out_dir, "derived_validation", run_id, sys.argv, {
            "status": result.status,
            "b_count": result.b_block_count,
            "l1_count": result.l1_row_count,
            "l2_count": result.l2_row_count,
        })
        
        # Write LATEST pointer
        component_root = Path(args.out) / "derived_validation"
        write_latest(component_root, run_id)
        
        writer.log(f"  JSON: {json_path}")
        writer.log(f"  Markdown: {md_path}")
        if csv_path:
            writer.log(f"  Diffs CSV: {csv_path}")
        
        writer.log(f"\n{'=' * 50}")
        writer.log(f"VALIDATION RESULT: {result.status}")
        writer.log(f"{'=' * 50}")
        
        if result.errors:
            writer.log("\nErrors:")
            for e in result.errors:
                writer.log(f"  - {e}")
        
        if result.warnings:
            writer.log("\nWarnings:")
            for w in result.warnings:
                writer.log(f"  - {w}")
        
        # Record output and checks
        writer.add_output(type="artifact", ref=str(out_dir))
        
        if result.status == "FAIL":
            writer.check("validation_passed", "Derived validation passed", "fail", [])
            writer.finish("failed")
        else:
            writer.check("validation_passed", "Derived validation passed", "pass", [])
            writer.finish("success")
        
        return 0 if result.status != "FAIL" else 1
        
    except Exception as e:
        writer.log(f"ERROR: {type(e).__name__}: {e}")
        writer.check("execution_error", f"Execution failed: {type(e).__name__}", "fail", [])
        writer.finish("failed")
        raise


if __name__ == "__main__":
    sys.exit(main())
