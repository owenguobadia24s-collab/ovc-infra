"""
OVC Threshold Registry (v0.1)

Purpose: Deterministic, versioned threshold pack management for C3+ layers.

Design principles:
    - Immutable packs: Once created, a (pack_id, pack_version) never changes.
    - Deterministic hashing: Same config_json => same config_hash, always.
    - Scope hierarchy: GLOBAL < SYMBOL < SYMBOL_TF (most specific wins).
    - Auditable: All changes tracked with timestamps and provenance.

Usage:
    from src.config.threshold_registry_v0_1 import ThresholdRegistry
    
    registry = ThresholdRegistry()
    pack = registry.get_active_pack("c3_reversal", "GLOBAL")
    print(pack["config_json"], pack["config_hash"])

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string

Guarantees:
    - Deterministic: Same inputs + same threshold pack version/hash => same outputs.
    - Replayable: config_hash proves exact config used for any computation.
    - Idempotent: create_pack with same version + same config is safe (no-op).
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor

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
SCHEMA = "ovc_cfg"
TABLE_PACK = f"{SCHEMA}.threshold_pack"
TABLE_ACTIVE = f"{SCHEMA}.threshold_pack_active"


class Scope(str, Enum):
    """Valid scope values for threshold packs."""
    GLOBAL = "GLOBAL"
    SYMBOL = "SYMBOL"
    SYMBOL_TF = "SYMBOL_TF"


class Status(str, Enum):
    """Valid status values for threshold packs."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"


# ---------- Exceptions ----------
class ThresholdRegistryError(Exception):
    """Base exception for threshold registry operations."""
    pass


class ConfigValidationError(ThresholdRegistryError):
    """Raised when config validation fails."""
    pass


class PackNotFoundError(ThresholdRegistryError):
    """Raised when a requested pack does not exist."""
    pass


class DuplicatePackError(ThresholdRegistryError):
    """Raised when attempting to create a duplicate pack with different config."""
    pass


class ScopeValidationError(ThresholdRegistryError):
    """Raised when scope/symbol/timeframe combination is invalid."""
    pass


# ---------- Canonical JSON Normalization ----------

def _check_for_special_floats(obj: Any, path: str = "") -> None:
    """
    Recursively check for NaN/Infinity which are not JSON-serializable.
    
    Raises:
        ConfigValidationError: If NaN or Infinity found.
    """
    if isinstance(obj, float):
        if obj != obj:  # NaN check
            raise ConfigValidationError(f"NaN value found at {path or 'root'}")
        if obj == float('inf') or obj == float('-inf'):
            raise ConfigValidationError(f"Infinity value found at {path or 'root'}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _check_for_special_floats(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_for_special_floats(v, f"{path}[{i}]")


def _normalize_value(v: Any) -> Any:
    """
    Normalize a value for canonical JSON.
    
    Rules:
        - Integers remain integers.
        - Floats that are whole numbers become integers.
        - Floats with decimals are formatted with fixed precision (6 decimals).
        - Decimals are converted to their string representation then to float/int.
        - Dicts and lists are recursively normalized.
    """
    if isinstance(v, bool):
        return v
    elif isinstance(v, int):
        return v
    elif isinstance(v, float):
        # If it's a whole number, return as int
        if v == int(v):
            return int(v)
        # Format with fixed precision to avoid floating point repr differences
        # Use Decimal for precise rounding
        d = Decimal(str(v)).quantize(Decimal("0.000001"))
        normalized = float(d)
        # Check again if it became whole after rounding
        if normalized == int(normalized):
            return int(normalized)
        return normalized
    elif isinstance(v, Decimal):
        # Convert Decimal to float/int
        if v == int(v):
            return int(v)
        return float(v.quantize(Decimal("0.000001")))
    elif isinstance(v, str):
        return v
    elif isinstance(v, dict):
        return {k: _normalize_value(val) for k, val in v.items()}
    elif isinstance(v, (list, tuple)):
        return [_normalize_value(item) for item in v]
    elif v is None:
        return None
    else:
        # Convert unknown types to string
        return str(v)


def canonicalize_config(obj: Any) -> str:
    """
    Convert a config object to canonical JSON string.
    
    Canonical form:
        - Keys sorted recursively.
        - No extra whitespace (separators: ',' and ':').
        - Consistent numeric formatting.
        - NaN/Infinity rejected.
    
    Args:
        obj: Config object (dict, list, or primitive).
        
    Returns:
        Canonical JSON string.
        
    Raises:
        ConfigValidationError: If NaN or Infinity values present.
    """
    # Reject special float values
    _check_for_special_floats(obj)
    
    # Normalize values
    normalized = _normalize_value(obj)
    
    # Serialize with sorted keys and no whitespace
    return json.dumps(normalized, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def hash_config(canonical_str: str) -> str:
    """
    Compute SHA256 hash of canonical config string.
    
    Args:
        canonical_str: Canonical JSON string (from canonicalize_config).
        
    Returns:
        64-character lowercase hex string.
    """
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


# ---------- Scope Validation ----------

def validate_scope(scope: Union[str, Scope], symbol: Optional[str], timeframe: Optional[str]) -> None:
    """
    Validate that scope/symbol/timeframe combination is valid.
    
    Rules:
        - GLOBAL: symbol and timeframe must be None.
        - SYMBOL: symbol must be set, timeframe must be None.
        - SYMBOL_TF: both symbol and timeframe must be set.
    
    Raises:
        ScopeValidationError: If combination is invalid.
    """
    scope_str = scope.value if isinstance(scope, Scope) else scope
    
    if scope_str not in [s.value for s in Scope]:
        raise ScopeValidationError(f"Invalid scope: {scope_str}. Must be one of: GLOBAL, SYMBOL, SYMBOL_TF")
    
    if scope_str == Scope.GLOBAL.value:
        if symbol is not None or timeframe is not None:
            raise ScopeValidationError("GLOBAL scope requires symbol=None and timeframe=None")
    elif scope_str == Scope.SYMBOL.value:
        if symbol is None:
            raise ScopeValidationError("SYMBOL scope requires symbol to be set")
        if timeframe is not None:
            raise ScopeValidationError("SYMBOL scope requires timeframe=None")
    elif scope_str == Scope.SYMBOL_TF.value:
        if symbol is None:
            raise ScopeValidationError("SYMBOL_TF scope requires symbol to be set")
        if timeframe is None:
            raise ScopeValidationError("SYMBOL_TF scope requires timeframe to be set")


# ---------- Database Connection ----------

def resolve_dsn() -> str:
    """Resolve database connection string from environment."""
    dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing NEON_DSN or DATABASE_URL in environment")
    return dsn


def get_connection():
    """Get a database connection."""
    return psycopg2.connect(resolve_dsn())


# ---------- Threshold Registry Class ----------

class ThresholdRegistry:
    """
    Threshold pack registry for deterministic configuration management.
    
    Provides CRUD operations for threshold packs with:
        - Immutable versioned configs.
        - Deterministic hashing.
        - Scope-based activation.
    """
    
    def __init__(self, dsn: Optional[str] = None):
        """
        Initialize registry.
        
        Args:
            dsn: PostgreSQL connection string. If None, uses NEON_DSN or DATABASE_URL.
        """
        self.dsn = dsn or resolve_dsn()
    
    def _get_conn(self):
        """Get a database connection."""
        return psycopg2.connect(self.dsn)
    
    def create_pack(
        self,
        pack_id: str,
        pack_version: int,
        scope: Union[str, Scope],
        config: Dict[str, Any],
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        status: Union[str, Status] = Status.DRAFT,
        created_by: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new threshold pack.
        
        Args:
            pack_id: Logical identifier for the pack.
            pack_version: Version number (must be unique per pack_id).
            scope: GLOBAL, SYMBOL, or SYMBOL_TF.
            config: Configuration dict (will be canonicalized).
            symbol: Required for SYMBOL and SYMBOL_TF scopes.
            timeframe: Required for SYMBOL_TF scope.
            status: Initial status (default: DRAFT).
            created_by: Optional creator identifier.
            note: Optional note/description.
            
        Returns:
            Dict with pack details including config_hash.
            
        Raises:
            ScopeValidationError: If scope/symbol/timeframe invalid.
            DuplicatePackError: If version exists with different config.
            ConfigValidationError: If config contains NaN/Infinity.
        """
        scope_str = scope.value if isinstance(scope, Scope) else scope
        status_str = status.value if isinstance(status, Status) else status
        
        # Validate scope
        validate_scope(scope_str, symbol, timeframe)
        
        # Canonicalize and hash
        canonical = canonicalize_config(config)
        config_hash = hash_config(canonical)
        
        # Parse canonical back to ensure we store normalized form
        config_normalized = json.loads(canonical)
        
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check for existing version
                cur.execute(
                    f"""
                    SELECT config_hash FROM {TABLE_PACK}
                    WHERE pack_id = %s AND pack_version = %s
                    """,
                    (pack_id, pack_version)
                )
                existing = cur.fetchone()
                
                if existing:
                    if existing["config_hash"] != config_hash:
                        raise DuplicatePackError(
                            f"Pack {pack_id} version {pack_version} already exists with different config. "
                            f"Existing hash: {existing['config_hash']}, new hash: {config_hash}"
                        )
                    # Idempotent: same config, return existing
                    cur.execute(
                        f"""
                        SELECT pack_id, pack_version, scope, symbol, timeframe,
                               config_json, config_hash, status, created_at, created_by, note
                        FROM {TABLE_PACK}
                        WHERE pack_id = %s AND pack_version = %s
                        """,
                        (pack_id, pack_version)
                    )
                    return dict(cur.fetchone())
                
                # Insert new pack
                cur.execute(
                    f"""
                    INSERT INTO {TABLE_PACK}
                        (pack_id, pack_version, scope, symbol, timeframe,
                         config_json, config_hash, status, created_by, note)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING pack_id, pack_version, scope, symbol, timeframe,
                              config_json, config_hash, status, created_at, created_by, note
                    """,
                    (pack_id, pack_version, scope_str, symbol, timeframe,
                     json.dumps(config_normalized), config_hash, status_str, created_by, note)
                )
                result = dict(cur.fetchone())
                conn.commit()
                return result
    
    def activate_pack(
        self,
        pack_id: str,
        scope: Union[str, Scope],
        version: int,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        expected_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Activate a threshold pack version for a given selector.
        
        This:
            1. Verifies the target pack exists.
            2. Sets the pack status to ACTIVE.
            3. Upserts a pointer in threshold_pack_active.
        
        Args:
            pack_id: Pack identifier.
            scope: GLOBAL, SYMBOL, or SYMBOL_TF.
            version: Version to activate.
            symbol: Required for SYMBOL and SYMBOL_TF scopes.
            timeframe: Required for SYMBOL_TF scope.
            expected_hash: If provided, verify hash matches before activation.
            
        Returns:
            Dict with activated pack details.
            
        Raises:
            PackNotFoundError: If pack doesn't exist.
            ScopeValidationError: If scope/symbol/timeframe invalid.
            ThresholdRegistryError: If expected_hash doesn't match.
        """
        scope_str = scope.value if isinstance(scope, Scope) else scope
        
        # Validate scope
        validate_scope(scope_str, symbol, timeframe)
        
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get the pack
                cur.execute(
                    f"""
                    SELECT pack_id, pack_version, scope, symbol, timeframe,
                           config_json, config_hash, status
                    FROM {TABLE_PACK}
                    WHERE pack_id = %s AND pack_version = %s
                    """,
                    (pack_id, version)
                )
                pack = cur.fetchone()
                
                if not pack:
                    raise PackNotFoundError(f"Pack {pack_id} version {version} not found")
                
                # Verify hash if provided
                if expected_hash and pack["config_hash"] != expected_hash:
                    raise ThresholdRegistryError(
                        f"Hash mismatch. Expected: {expected_hash}, actual: {pack['config_hash']}"
                    )
                
                # Update pack status to ACTIVE
                cur.execute(
                    f"""
                    UPDATE {TABLE_PACK}
                    SET status = %s
                    WHERE pack_id = %s AND pack_version = %s
                    """,
                    (Status.ACTIVE.value, pack_id, version)
                )
                
                # Upsert active pointer
                # Use empty string for NULL values (active table uses NOT NULL with defaults)
                symbol_db = symbol or ''
                timeframe_db = timeframe or ''
                cur.execute(
                    f"""
                    INSERT INTO {TABLE_ACTIVE}
                        (pack_id, scope, symbol, timeframe, active_version, active_hash, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (pack_id, scope, symbol, timeframe)
                    DO UPDATE SET
                        active_version = EXCLUDED.active_version,
                        active_hash = EXCLUDED.active_hash,
                        updated_at = NOW()
                    RETURNING pack_id, scope, symbol, timeframe, active_version, active_hash, updated_at
                    """,
                    (pack_id, scope_str, symbol_db, timeframe_db, version, pack["config_hash"])
                )
                active_result = dict(cur.fetchone())
                
                conn.commit()
                
                # Return combined info
                return {
                    "pack_id": pack_id,
                    "pack_version": version,
                    "scope": scope_str,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "config_json": pack["config_json"],
                    "config_hash": pack["config_hash"],
                    "status": Status.ACTIVE.value,
                    "updated_at": active_result["updated_at"],
                }
    
    def get_active_pack(
        self,
        pack_id: str,
        scope: Union[str, Scope],
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the currently active pack for a selector.
        
        Args:
            pack_id: Pack identifier.
            scope: GLOBAL, SYMBOL, or SYMBOL_TF.
            symbol: Required for SYMBOL and SYMBOL_TF scopes.
            timeframe: Required for SYMBOL_TF scope.
            
        Returns:
            Dict with pack_id, pack_version, config_hash, config_json, scope, symbol, timeframe.
            
        Raises:
            PackNotFoundError: If no active pack for selector.
            ScopeValidationError: If scope/symbol/timeframe invalid.
        """
        scope_str = scope.value if isinstance(scope, Scope) else scope
        
        # Validate scope
        validate_scope(scope_str, symbol, timeframe)
        
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get active pointer (use empty string for NULL matching)
                symbol_db = symbol or ''
                timeframe_db = timeframe or ''
                cur.execute(
                    f"""
                    SELECT a.pack_id, a.active_version, a.active_hash, a.scope, a.symbol, a.timeframe,
                           p.config_json, p.status
                    FROM {TABLE_ACTIVE} a
                    JOIN {TABLE_PACK} p ON p.pack_id = a.pack_id AND p.pack_version = a.active_version
                    WHERE a.pack_id = %s
                      AND a.scope = %s
                      AND a.symbol = %s
                      AND a.timeframe = %s
                    """,
                    (pack_id, scope_str, symbol_db, timeframe_db)
                )
                result = cur.fetchone()
                
                if not result:
                    selector = f"pack_id={pack_id}, scope={scope_str}"
                    if symbol:
                        selector += f", symbol={symbol}"
                    if timeframe:
                        selector += f", timeframe={timeframe}"
                    raise PackNotFoundError(f"No active pack found for selector: {selector}")
                
                # Convert empty strings back to None for API consistency
                return {
                    "pack_id": result["pack_id"],
                    "pack_version": result["active_version"],
                    "config_hash": result["active_hash"],
                    "config_json": result["config_json"],
                    "scope": result["scope"],
                    "symbol": result["symbol"] or None,
                    "timeframe": result["timeframe"] or None,
                    "status": result["status"],
                }
    
    def get_pack(self, pack_id: str, version: int) -> Dict[str, Any]:
        """
        Get a specific pack by ID and version.
        
        Args:
            pack_id: Pack identifier.
            version: Version number.
            
        Returns:
            Dict with full pack details.
            
        Raises:
            PackNotFoundError: If pack doesn't exist.
        """
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT pack_id, pack_version, scope, symbol, timeframe,
                           config_json, config_hash, status, created_at, created_by, note
                    FROM {TABLE_PACK}
                    WHERE pack_id = %s AND pack_version = %s
                    """,
                    (pack_id, version)
                )
                result = cur.fetchone()
                
                if not result:
                    raise PackNotFoundError(f"Pack {pack_id} version {version} not found")
                
                return dict(result)
    
    def list_packs(
        self,
        pack_id: Optional[str] = None,
        status: Optional[Union[str, Status]] = None,
        scope: Optional[Union[str, Scope]] = None,
        symbol: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List packs with optional filters.
        
        Args:
            pack_id: Filter by pack ID.
            status: Filter by status (DRAFT, ACTIVE, DEPRECATED).
            scope: Filter by scope (GLOBAL, SYMBOL, SYMBOL_TF).
            symbol: Filter by symbol.
            
        Returns:
            List of pack dicts.
        """
        conditions = []
        params = []
        
        if pack_id:
            conditions.append("pack_id = %s")
            params.append(pack_id)
        
        if status:
            status_str = status.value if isinstance(status, Status) else status
            conditions.append("status = %s")
            params.append(status_str)
        
        if scope:
            scope_str = scope.value if isinstance(scope, Scope) else scope
            conditions.append("scope = %s")
            params.append(scope_str)
        
        if symbol:
            conditions.append("symbol = %s")
            params.append(symbol)
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT pack_id, pack_version, scope, symbol, timeframe,
                           config_json, config_hash, status, created_at, created_by, note
                    FROM {TABLE_PACK}
                    WHERE {where_clause}
                    ORDER BY pack_id, pack_version DESC
                    """,
                    params
                )
                return [dict(row) for row in cur.fetchall()]
    
    def validate_integrity(self) -> Dict[str, Any]:
        """
        Validate registry integrity.
        
        Checks:
            - All active pointers resolve to existing packs.
            - All active pointers have matching hashes.
            - No orphaned active pointers.
        
        Returns:
            Dict with validation results.
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {},
        }
        
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Count packs by status
                cur.execute(f"""
                    SELECT status, COUNT(*) as cnt
                    FROM {TABLE_PACK}
                    GROUP BY status
                """)
                results["stats"]["packs_by_status"] = {
                    row["status"]: row["cnt"] for row in cur.fetchall()
                }
                
                # Count active pointers
                cur.execute(f"SELECT COUNT(*) as cnt FROM {TABLE_ACTIVE}")
                results["stats"]["active_pointers"] = cur.fetchone()["cnt"]
                
                # Check for orphaned active pointers
                cur.execute(f"""
                    SELECT a.pack_id, a.scope, a.symbol, a.timeframe, a.active_version
                    FROM {TABLE_ACTIVE} a
                    LEFT JOIN {TABLE_PACK} p 
                        ON p.pack_id = a.pack_id AND p.pack_version = a.active_version
                    WHERE p.pack_id IS NULL
                """)
                orphans = cur.fetchall()
                if orphans:
                    results["valid"] = False
                    for o in orphans:
                        results["errors"].append(
                            f"Orphaned active pointer: {o['pack_id']} v{o['active_version']} "
                            f"(scope={o['scope']}, symbol={o['symbol']}, timeframe={o['timeframe']})"
                        )
                
                # Check for hash mismatches
                cur.execute(f"""
                    SELECT a.pack_id, a.active_version, a.active_hash, p.config_hash
                    FROM {TABLE_ACTIVE} a
                    JOIN {TABLE_PACK} p 
                        ON p.pack_id = a.pack_id AND p.pack_version = a.active_version
                    WHERE a.active_hash != p.config_hash
                """)
                mismatches = cur.fetchall()
                if mismatches:
                    results["valid"] = False
                    for m in mismatches:
                        results["errors"].append(
                            f"Hash mismatch for {m['pack_id']} v{m['active_version']}: "
                            f"active_hash={m['active_hash']}, config_hash={m['config_hash']}"
                        )
                
                return results


# ---------- Convenience Functions ----------

def get_active_pack(
    pack_id: str,
    scope: Union[str, Scope],
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to get active pack without instantiating registry.
    """
    registry = ThresholdRegistry()
    return registry.get_active_pack(pack_id, scope, symbol, timeframe)


def get_pack(pack_id: str, version: int) -> Dict[str, Any]:
    """
    Convenience function to get pack by ID and version.
    """
    registry = ThresholdRegistry()
    return registry.get_pack(pack_id, version)


# ---------- Module Test ----------

if __name__ == "__main__":
    # Quick sanity check
    test_config = {"min_body_bp": 5, "max_wick_ratio_bp": 250, "lookback": 20}
    canonical = canonicalize_config(test_config)
    print(f"Canonical: {canonical}")
    print(f"Hash: {hash_config(canonical)}")
    
    # Test key order independence
    test_config2 = {"lookback": 20, "max_wick_ratio_bp": 250, "min_body_bp": 5}
    canonical2 = canonicalize_config(test_config2)
    print(f"Same hash with different key order: {canonical == canonical2}")
