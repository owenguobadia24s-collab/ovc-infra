#!/usr/bin/env python3
"""
OVC Threshold Registry CLI (v0.1)

CLI for managing threshold packs in the OVC configuration registry.

Commands:
    create      Create a new threshold pack (DRAFT status by default)
    activate    Activate a pack version for a selector
    show        Show pack details (by version or active selector)
    list        List packs with optional filters
    validate    Check registry integrity

Usage:
    python -m src.config.threshold_registry_cli create --pack-id l3_reversal --version 1 --scope GLOBAL --config '{"min_body_bp": 5}'
    python -m src.config.threshold_registry_cli activate --pack-id l3_reversal --version 1 --scope GLOBAL
    python -m src.config.threshold_registry_cli show --pack-id l3_reversal --version 1
    python -m src.config.threshold_registry_cli show --pack-id l3_reversal --scope GLOBAL --active
    python -m src.config.threshold_registry_cli list
    python -m src.config.threshold_registry_cli validate

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Exit Codes:
    0: Success
    1: Error (validation failure, not found, etc.)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Import registry module
from src.config.threshold_registry_v0_1 import (
    ThresholdRegistry,
    ThresholdRegistryError,
    PackNotFoundError,
    DuplicatePackError,
    ScopeValidationError,
    ConfigValidationError,
    Scope,
    Status,
    canonicalize_config,
    hash_config,
)


def json_serializer(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def print_json(data: Any, indent: int = 2) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=indent, default=json_serializer))


def error_exit(message: str, code: int = 1) -> None:
    """Print error message and exit with code."""
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def load_config_from_file(path: str) -> dict:
    """Load JSON config from file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        error_exit(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON in config file: {e}")


def parse_inline_config(config_str: str) -> dict:
    """Parse inline JSON config string."""
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON config: {e}")


# ---------- Command Handlers ----------

def cmd_create(args: argparse.Namespace) -> None:
    """Handle 'create' command."""
    # Load config from file or inline
    if args.config_file:
        config = load_config_from_file(args.config_file)
    elif args.config:
        config = parse_inline_config(args.config)
    else:
        error_exit("Either --config or --config-file is required")
    
    # Validate scope requirements
    scope = args.scope
    symbol = args.symbol
    timeframe = args.timeframe
    
    try:
        registry = ThresholdRegistry()
        result = registry.create_pack(
            pack_id=args.pack_id,
            pack_version=args.version,
            scope=scope,
            config=config,
            symbol=symbol,
            timeframe=timeframe,
            status=args.status or Status.DRAFT.value,
            created_by=args.created_by,
            note=args.note,
        )
        print_json({
            "success": True,
            "action": "create",
            "pack": result,
        })
    except (ScopeValidationError, ConfigValidationError, DuplicatePackError) as e:
        error_exit(str(e))
    except Exception as e:
        error_exit(f"Failed to create pack: {e}")


def cmd_activate(args: argparse.Namespace) -> None:
    """Handle 'activate' command."""
    try:
        registry = ThresholdRegistry()
        result = registry.activate_pack(
            pack_id=args.pack_id,
            scope=args.scope,
            version=args.version,
            symbol=args.symbol,
            timeframe=args.timeframe,
            expected_hash=args.expected_hash,
        )
        print_json({
            "success": True,
            "action": "activate",
            "pack": result,
        })
    except (PackNotFoundError, ScopeValidationError, ThresholdRegistryError) as e:
        error_exit(str(e))
    except Exception as e:
        error_exit(f"Failed to activate pack: {e}")


def cmd_show(args: argparse.Namespace) -> None:
    """Handle 'show' command."""
    try:
        registry = ThresholdRegistry()
        
        if args.active:
            # Show active pack for selector
            if not args.scope:
                error_exit("--scope is required when using --active")
            result = registry.get_active_pack(
                pack_id=args.pack_id,
                scope=args.scope,
                symbol=args.symbol,
                timeframe=args.timeframe,
            )
        else:
            # Show specific version
            if args.version is None:
                error_exit("--version is required (or use --active for active pack)")
            result = registry.get_pack(
                pack_id=args.pack_id,
                version=args.version,
            )
        
        print_json(result)
    except PackNotFoundError as e:
        error_exit(str(e))
    except Exception as e:
        error_exit(f"Failed to show pack: {e}")


def cmd_list(args: argparse.Namespace) -> None:
    """Handle 'list' command."""
    try:
        registry = ThresholdRegistry()
        results = registry.list_packs(
            pack_id=args.pack_id,
            status=args.status,
            scope=args.scope,
            symbol=args.symbol,
        )
        print_json({
            "count": len(results),
            "packs": results,
        })
    except Exception as e:
        error_exit(f"Failed to list packs: {e}")


def cmd_validate(args: argparse.Namespace) -> None:
    """Handle 'validate' command."""
    try:
        registry = ThresholdRegistry()
        result = registry.validate_integrity()
        print_json(result)
        
        if not result["valid"]:
            sys.exit(1)
    except Exception as e:
        error_exit(f"Failed to validate registry: {e}")


def cmd_hash(args: argparse.Namespace) -> None:
    """Handle 'hash' command - compute hash without DB interaction."""
    # Load config from file or inline
    if args.config_file:
        config = load_config_from_file(args.config_file)
    elif args.config:
        config = parse_inline_config(args.config)
    else:
        error_exit("Either --config or --config-file is required")
    
    try:
        canonical = canonicalize_config(config)
        config_hash = hash_config(canonical)
        print_json({
            "canonical": canonical,
            "hash": config_hash,
            "original": config,
        })
    except ConfigValidationError as e:
        error_exit(str(e))


# ---------- Main ----------

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="threshold_registry_cli",
        description="OVC Threshold Registry CLI - Manage versioned threshold packs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # ---------- create ----------
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new threshold pack",
    )
    create_parser.add_argument(
        "--pack-id",
        required=True,
        help="Pack identifier (e.g., l3_reversal_thresholds)",
    )
    create_parser.add_argument(
        "--version",
        type=int,
        required=True,
        help="Version number (integer)",
    )
    create_parser.add_argument(
        "--scope",
        required=True,
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Scope: GLOBAL, SYMBOL, or SYMBOL_TF",
    )
    create_parser.add_argument(
        "--config",
        help="Inline JSON config string",
    )
    create_parser.add_argument(
        "--config-file",
        help="Path to JSON config file",
    )
    create_parser.add_argument(
        "--symbol",
        help="Symbol (required for SYMBOL and SYMBOL_TF scopes)",
    )
    create_parser.add_argument(
        "--timeframe",
        help="Timeframe (required for SYMBOL_TF scope)",
    )
    create_parser.add_argument(
        "--status",
        choices=["DRAFT", "ACTIVE", "DEPRECATED"],
        default="DRAFT",
        help="Initial status (default: DRAFT)",
    )
    create_parser.add_argument(
        "--created-by",
        help="Creator identifier",
    )
    create_parser.add_argument(
        "--note",
        help="Note/description",
    )
    create_parser.set_defaults(func=cmd_create)
    
    # ---------- activate ----------
    activate_parser = subparsers.add_parser(
        "activate",
        help="Activate a pack version for a selector",
    )
    activate_parser.add_argument(
        "--pack-id",
        required=True,
        help="Pack identifier",
    )
    activate_parser.add_argument(
        "--version",
        type=int,
        required=True,
        help="Version to activate",
    )
    activate_parser.add_argument(
        "--scope",
        required=True,
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Scope for activation",
    )
    activate_parser.add_argument(
        "--symbol",
        help="Symbol (required for SYMBOL and SYMBOL_TF scopes)",
    )
    activate_parser.add_argument(
        "--timeframe",
        help="Timeframe (required for SYMBOL_TF scope)",
    )
    activate_parser.add_argument(
        "--expected-hash",
        help="Expected config hash (optional safety check)",
    )
    activate_parser.set_defaults(func=cmd_activate)
    
    # ---------- show ----------
    show_parser = subparsers.add_parser(
        "show",
        help="Show pack details",
    )
    show_parser.add_argument(
        "--pack-id",
        required=True,
        help="Pack identifier",
    )
    show_parser.add_argument(
        "--version",
        type=int,
        help="Version number (required unless --active)",
    )
    show_parser.add_argument(
        "--active",
        action="store_true",
        help="Show active pack for selector instead of specific version",
    )
    show_parser.add_argument(
        "--scope",
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Scope (required with --active)",
    )
    show_parser.add_argument(
        "--symbol",
        help="Symbol (for SYMBOL/SYMBOL_TF scope with --active)",
    )
    show_parser.add_argument(
        "--timeframe",
        help="Timeframe (for SYMBOL_TF scope with --active)",
    )
    show_parser.set_defaults(func=cmd_show)
    
    # ---------- list ----------
    list_parser = subparsers.add_parser(
        "list",
        help="List packs with optional filters",
    )
    list_parser.add_argument(
        "--pack-id",
        help="Filter by pack ID",
    )
    list_parser.add_argument(
        "--status",
        choices=["DRAFT", "ACTIVE", "DEPRECATED"],
        help="Filter by status",
    )
    list_parser.add_argument(
        "--scope",
        choices=["GLOBAL", "SYMBOL", "SYMBOL_TF"],
        help="Filter by scope",
    )
    list_parser.add_argument(
        "--symbol",
        help="Filter by symbol",
    )
    list_parser.set_defaults(func=cmd_list)
    
    # ---------- validate ----------
    validate_parser = subparsers.add_parser(
        "validate",
        help="Check registry integrity",
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # ---------- hash ----------
    hash_parser = subparsers.add_parser(
        "hash",
        help="Compute canonical hash without DB interaction",
    )
    hash_parser.add_argument(
        "--config",
        help="Inline JSON config string",
    )
    hash_parser.add_argument(
        "--config-file",
        help="Path to JSON config file",
    )
    hash_parser.set_defaults(func=cmd_hash)
    
    # Parse and dispatch
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
