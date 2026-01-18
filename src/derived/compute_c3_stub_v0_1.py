"""
OVC Option C.3 Stub (v0.1)

Purpose: Demonstrate threshold registry plumbing for C3 tags.
This stub DOES NOT implement full C3 tagging logic - it only proves
that pack resolution works and produces deterministic metadata.

Usage:
    python src/derived/compute_c3_stub_v0_1.py --pack-id c3_example --scope GLOBAL

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Output:
    Prints resolved pack metadata (pack_id, version, hash, config)
    to demonstrate that the plumbing works.

When Full C3 is Implemented:
    - Replace stub logic with actual C3 tagging computations.
    - Store pack_id/version/hash with each tag row for replay certification.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from config.threshold_registry_v0_1 import (
    ThresholdRegistry,
    PackNotFoundError,
    ScopeValidationError,
    Scope,
)


# ---------- Tiny .env loader (matches B.1/B.2 convention) ----------
def load_env(path: str = ".env") -> None:
    """Load environment variables from .env file if it exists."""
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
RUN_TYPE = "c3_stub"


def json_serializer(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="C3 Stub: Demonstrate threshold registry plumbing"
    )
    parser.add_argument(
        "--pack-id",
        required=True,
        help="Pack identifier to resolve",
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Scope for pack resolution",
    )
    parser.add_argument(
        "--symbol",
        help="Symbol (required for SYMBOL/SYMBOL_TF scope)",
    )
    parser.add_argument(
        "--timeframe",
        help="Timeframe (required for SYMBOL_TF scope)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without actual processing",
    )
    return parser.parse_args()


def resolve_active_pack(
    pack_id: str,
    scope: str,
    symbol: str = None,
    timeframe: str = None,
) -> dict:
    """
    Resolve the active threshold pack for given selector.
    
    Returns:
        Dict with pack_id, pack_version, config_hash, config_json
        
    Raises:
        PackNotFoundError: If no active pack found.
        ScopeValidationError: If scope/symbol/timeframe combination invalid.
    """
    registry = ThresholdRegistry()
    return registry.get_active_pack(
        pack_id=pack_id,
        scope=scope,
        symbol=symbol,
        timeframe=timeframe,
    )


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    print(f"[C3 Stub v0.1] Resolving threshold pack...")
    print(f"  pack_id: {args.pack_id}")
    print(f"  scope: {args.scope}")
    if args.symbol:
        print(f"  symbol: {args.symbol}")
    if args.timeframe:
        print(f"  timeframe: {args.timeframe}")
    print()
    
    try:
        pack = resolve_active_pack(
            pack_id=args.pack_id,
            scope=args.scope,
            symbol=args.symbol,
            timeframe=args.timeframe,
        )
    except PackNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(file=sys.stderr)
        print("To create and activate a pack, run:", file=sys.stderr)
        print(f'  python -m src.config.threshold_registry_cli create --pack-id {args.pack_id} --version 1 --scope {args.scope} --config-file configs/threshold_packs/c3_example_pack_v1.json', file=sys.stderr)
        print(f'  python -m src.config.threshold_registry_cli activate --pack-id {args.pack_id} --version 1 --scope {args.scope}', file=sys.stderr)
        sys.exit(1)
    except ScopeValidationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("RESOLVED PACK (for replay certification)")
    print("=" * 60)
    print(json.dumps(pack, indent=2, default=json_serializer))
    print()
    
    # Extract provenance metadata that would be stored with C3 tags
    provenance = {
        "pack_id": pack["pack_id"],
        "pack_version": pack["pack_version"],
        "config_hash": pack["config_hash"],
        "resolved_at": datetime.now(timezone.utc).isoformat(),
    }
    
    print("=" * 60)
    print("PROVENANCE METADATA (store with each C3 tag row)")
    print("=" * 60)
    print(json.dumps(provenance, indent=2))
    print()
    
    if args.dry_run:
        print("[DRY-RUN] Would apply thresholds to C1/C2 data here.")
        print("[DRY-RUN] No actual processing performed.")
    else:
        print("[STUB] Full C3 tagging logic not implemented.")
        print("[STUB] This demonstrates that pack resolution works.")
        print()
        print("To implement full C3:")
        print("  1. Read C1/C2 data from derived tables")
        print("  2. Apply threshold logic using pack['config_json']")
        print("  3. Store tags with provenance (pack_id, version, hash)")
        print("  4. Ensure determinism: same pack + same data = same tags")
    
    print()
    print("[C3 Stub] Done.")


if __name__ == "__main__":
    main()
