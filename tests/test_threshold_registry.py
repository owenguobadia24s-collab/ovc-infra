"""
Tests for OVC Threshold Registry (v0.1)

Test Coverage:
    1. Canonicalization stability: same JSON, different key order => same canonical + same hash
    2. NaN/Infinity rejection
    3. create_pack inserts DRAFT with correct hash
    4. activate_pack creates/updates active pointer correctly
    5. get_active_pack returns exact version/hash/config
    6. Scope enforcement (GLOBAL vs SYMBOL vs SYMBOL_TF)

Environment:
    NEON_DSN or DATABASE_URL: PostgreSQL connection string (for DB tests)

Run:
    python -m pytest tests/test_threshold_registry.py -v
"""

import hashlib
import json
import math
import sys
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Add src to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config.threshold_registry_v0_1 import (
    canonicalize_config,
    hash_config,
    validate_scope,
    ThresholdRegistry,
    ThresholdRegistryError,
    PackNotFoundError,
    DuplicatePackError,
    ScopeValidationError,
    ConfigValidationError,
    Scope,
    Status,
)


# ============================================================================
# Unit Tests (no DB required)
# ============================================================================

class TestCanonicalization(unittest.TestCase):
    """Test canonicalize_config() determinism and correctness."""
    
    def test_same_config_different_key_order(self):
        """Same config with different key order produces identical canonical JSON."""
        config1 = {"z_key": 1, "a_key": 2, "m_key": 3}
        config2 = {"a_key": 2, "m_key": 3, "z_key": 1}
        config3 = {"m_key": 3, "z_key": 1, "a_key": 2}
        
        canonical1 = canonicalize_config(config1)
        canonical2 = canonicalize_config(config2)
        canonical3 = canonicalize_config(config3)
        
        self.assertEqual(canonical1, canonical2)
        self.assertEqual(canonical2, canonical3)
        # Verify keys are sorted
        self.assertEqual(canonical1, '{"a_key":2,"m_key":3,"z_key":1}')
    
    def test_same_config_same_hash(self):
        """Same config (different key order) produces identical hash."""
        config1 = {"min_body_bp": 5, "max_wick_ratio_bp": 250, "lookback": 20}
        config2 = {"lookback": 20, "max_wick_ratio_bp": 250, "min_body_bp": 5}
        
        hash1 = hash_config(canonicalize_config(config1))
        hash2 = hash_config(canonicalize_config(config2))
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 hex = 64 chars
    
    def test_nested_dicts_sorted(self):
        """Nested dicts have keys sorted at all levels."""
        config1 = {"outer": {"z": 1, "a": 2}, "inner": {"y": 3, "b": 4}}
        config2 = {"inner": {"b": 4, "y": 3}, "outer": {"a": 2, "z": 1}}
        
        self.assertEqual(canonicalize_config(config1), canonicalize_config(config2))
    
    def test_arrays_preserved_order(self):
        """Arrays preserve element order (not sorted)."""
        config = {"items": [3, 1, 2]}
        canonical = canonicalize_config(config)
        self.assertEqual(canonical, '{"items":[3,1,2]}')
    
    def test_integer_preservation(self):
        """Integers remain integers (not floats)."""
        config = {"threshold": 100}
        canonical = canonicalize_config(config)
        self.assertEqual(canonical, '{"threshold":100}')
        self.assertNotIn(".0", canonical)
    
    def test_float_whole_number_becomes_int(self):
        """Float that is a whole number becomes integer."""
        config = {"value": 5.0}
        canonical = canonicalize_config(config)
        self.assertEqual(canonical, '{"value":5}')
    
    def test_float_fractional_preserved(self):
        """Float with fractional part is preserved."""
        config = {"ratio": 0.75}
        canonical = canonicalize_config(config)
        parsed = json.loads(canonical)
        self.assertAlmostEqual(parsed["ratio"], 0.75, places=6)
    
    def test_no_whitespace(self):
        """Canonical form has no extra whitespace."""
        config = {"a": 1, "b": 2}
        canonical = canonicalize_config(config)
        self.assertNotIn(" ", canonical)
        self.assertNotIn("\n", canonical)


class TestSpecialValueRejection(unittest.TestCase):
    """Test rejection of NaN and Infinity values."""
    
    def test_nan_rejected(self):
        """NaN values raise ConfigValidationError."""
        config = {"value": float('nan')}
        with self.assertRaises(ConfigValidationError) as ctx:
            canonicalize_config(config)
        self.assertIn("NaN", str(ctx.exception))
    
    def test_infinity_rejected(self):
        """Infinity values raise ConfigValidationError."""
        config = {"value": float('inf')}
        with self.assertRaises(ConfigValidationError) as ctx:
            canonicalize_config(config)
        self.assertIn("Infinity", str(ctx.exception))
    
    def test_negative_infinity_rejected(self):
        """Negative infinity values raise ConfigValidationError."""
        config = {"value": float('-inf')}
        with self.assertRaises(ConfigValidationError) as ctx:
            canonicalize_config(config)
        self.assertIn("Infinity", str(ctx.exception))
    
    def test_nested_nan_rejected(self):
        """NaN in nested structure is rejected."""
        config = {"outer": {"inner": float('nan')}}
        with self.assertRaises(ConfigValidationError) as ctx:
            canonicalize_config(config)
        self.assertIn("NaN", str(ctx.exception))
        self.assertIn("outer.inner", str(ctx.exception))
    
    def test_array_nan_rejected(self):
        """NaN in array is rejected."""
        config = {"items": [1, 2, float('nan')]}
        with self.assertRaises(ConfigValidationError) as ctx:
            canonicalize_config(config)
        self.assertIn("NaN", str(ctx.exception))


class TestHashConfig(unittest.TestCase):
    """Test hash_config() function."""
    
    def test_sha256_hex_format(self):
        """Hash is 64-character lowercase hex (SHA256)."""
        result = hash_config('{"a":1}')
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))
    
    def test_deterministic_hash(self):
        """Same input always produces same hash."""
        canonical = '{"a":1,"b":2}'
        hashes = [hash_config(canonical) for _ in range(10)]
        self.assertTrue(all(h == hashes[0] for h in hashes))
    
    def test_known_hash_value(self):
        """Hash matches expected SHA256 value."""
        canonical = '{"test":"value"}'
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(hash_config(canonical), expected)


class TestScopeValidation(unittest.TestCase):
    """Test validate_scope() function."""
    
    def test_global_requires_no_symbol_or_timeframe(self):
        """GLOBAL scope requires symbol=None and timeframe=None."""
        # Valid
        validate_scope("GLOBAL", None, None)  # Should not raise
        
        # Invalid
        with self.assertRaises(ScopeValidationError):
            validate_scope("GLOBAL", "GBPUSD", None)
        with self.assertRaises(ScopeValidationError):
            validate_scope("GLOBAL", None, "2H")
        with self.assertRaises(ScopeValidationError):
            validate_scope("GLOBAL", "GBPUSD", "2H")
    
    def test_symbol_requires_symbol_no_timeframe(self):
        """SYMBOL scope requires symbol, no timeframe."""
        # Valid
        validate_scope("SYMBOL", "GBPUSD", None)  # Should not raise
        
        # Invalid
        with self.assertRaises(ScopeValidationError):
            validate_scope("SYMBOL", None, None)
        with self.assertRaises(ScopeValidationError):
            validate_scope("SYMBOL", "GBPUSD", "2H")
    
    def test_symbol_tf_requires_both(self):
        """SYMBOL_TF scope requires both symbol and timeframe."""
        # Valid
        validate_scope("SYMBOL_TF", "GBPUSD", "2H")  # Should not raise
        
        # Invalid
        with self.assertRaises(ScopeValidationError):
            validate_scope("SYMBOL_TF", None, "2H")
        with self.assertRaises(ScopeValidationError):
            validate_scope("SYMBOL_TF", "GBPUSD", None)
        with self.assertRaises(ScopeValidationError):
            validate_scope("SYMBOL_TF", None, None)
    
    def test_invalid_scope_rejected(self):
        """Invalid scope string is rejected."""
        with self.assertRaises(ScopeValidationError):
            validate_scope("INVALID", None, None)
    
    def test_scope_enum_accepted(self):
        """Scope enum values are accepted."""
        validate_scope(Scope.GLOBAL, None, None)  # Should not raise
        validate_scope(Scope.SYMBOL, "GBPUSD", None)  # Should not raise
        validate_scope(Scope.SYMBOL_TF, "GBPUSD", "2H")  # Should not raise


# ============================================================================
# Integration Tests (require DB connection)
# ============================================================================

def requires_db(func):
    """Decorator to skip test if DB is not available."""
    import os
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
        if not dsn:
            raise unittest.SkipTest("NEON_DSN or DATABASE_URL not set")
        return func(*args, **kwargs)
    return wrapper


class TestThresholdRegistryDB(unittest.TestCase):
    """Integration tests for ThresholdRegistry (require DB)."""
    
    @classmethod
    def setUpClass(cls):
        """Check DB availability before running tests."""
        import os
        cls.dsn = os.environ.get("NEON_DSN") or os.environ.get("DATABASE_URL")
        if not cls.dsn:
            raise unittest.SkipTest("NEON_DSN or DATABASE_URL not set")
        cls.registry = ThresholdRegistry(cls.dsn)
        # Generate unique prefix to avoid conflicts with other tests
        cls.test_prefix = f"test_{uuid.uuid4().hex[:8]}"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test packs."""
        if hasattr(cls, 'registry') and hasattr(cls, 'test_prefix'):
            try:
                import psycopg2
                with psycopg2.connect(cls.dsn) as conn:
                    with conn.cursor() as cur:
                        # Clean up test data
                        cur.execute(
                            "DELETE FROM ovc_cfg.threshold_pack_active WHERE pack_id LIKE %s",
                            (f"{cls.test_prefix}%",)
                        )
                        cur.execute(
                            "DELETE FROM ovc_cfg.threshold_pack WHERE pack_id LIKE %s",
                            (f"{cls.test_prefix}%",)
                        )
                    conn.commit()
            except Exception as e:
                print(f"Warning: cleanup failed: {e}")
    
    @requires_db
    def test_create_pack_draft_status(self):
        """create_pack creates pack with DRAFT status by default."""
        pack_id = f"{self.test_prefix}_create_draft"
        config = {"threshold": 10}
        
        result = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        self.assertEqual(result["pack_id"], pack_id)
        self.assertEqual(result["pack_version"], 1)
        self.assertEqual(result["status"], "DRAFT")
        self.assertEqual(result["scope"], "GLOBAL")
        self.assertIsNone(result["symbol"])
        self.assertIsNone(result["timeframe"])
    
    @requires_db
    def test_create_pack_computes_hash(self):
        """create_pack computes correct config_hash."""
        pack_id = f"{self.test_prefix}_create_hash"
        config = {"a": 1, "b": 2}
        
        result = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        expected_hash = hash_config(canonicalize_config(config))
        self.assertEqual(result["config_hash"], expected_hash)
    
    @requires_db
    def test_create_pack_normalizes_config(self):
        """create_pack stores normalized config (sorted keys)."""
        pack_id = f"{self.test_prefix}_create_normalized"
        config = {"z": 3, "a": 1, "m": 2}
        
        result = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        # Config should be normalized (sorted keys)
        stored_config = result["config_json"]
        keys = list(stored_config.keys())
        self.assertEqual(keys, sorted(keys))
    
    @requires_db
    def test_create_pack_idempotent_same_config(self):
        """create_pack with same config is idempotent (no error)."""
        pack_id = f"{self.test_prefix}_create_idempotent"
        config = {"value": 42}
        
        result1 = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        # Same call again should succeed (idempotent)
        result2 = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        self.assertEqual(result1["config_hash"], result2["config_hash"])
    
    @requires_db
    def test_create_pack_rejects_different_config_same_version(self):
        """create_pack rejects different config for existing version."""
        pack_id = f"{self.test_prefix}_create_reject"
        
        self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config={"value": 1},
        )
        
        with self.assertRaises(DuplicatePackError):
            self.registry.create_pack(
                pack_id=pack_id,
                pack_version=1,
                scope="GLOBAL",
                config={"value": 2},  # Different config!
            )
    
    @requires_db
    def test_create_pack_scope_symbol(self):
        """create_pack with SYMBOL scope requires symbol."""
        pack_id = f"{self.test_prefix}_scope_symbol"
        
        result = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="SYMBOL",
            symbol="GBPUSD",
            config={"value": 1},
        )
        
        self.assertEqual(result["scope"], "SYMBOL")
        self.assertEqual(result["symbol"], "GBPUSD")
        self.assertIsNone(result["timeframe"])
    
    @requires_db
    def test_create_pack_scope_symbol_tf(self):
        """create_pack with SYMBOL_TF scope requires symbol and timeframe."""
        pack_id = f"{self.test_prefix}_scope_symbol_tf"
        
        result = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="SYMBOL_TF",
            symbol="GBPUSD",
            timeframe="2H",
            config={"value": 1},
        )
        
        self.assertEqual(result["scope"], "SYMBOL_TF")
        self.assertEqual(result["symbol"], "GBPUSD")
        self.assertEqual(result["timeframe"], "2H")
    
    @requires_db
    def test_activate_pack(self):
        """activate_pack sets status to ACTIVE and creates pointer."""
        pack_id = f"{self.test_prefix}_activate"
        config = {"threshold": 100}
        
        # Create pack
        created = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        # Activate
        activated = self.registry.activate_pack(
            pack_id=pack_id,
            scope="GLOBAL",
            version=1,
        )
        
        self.assertEqual(activated["status"], "ACTIVE")
        self.assertEqual(activated["pack_version"], 1)
        self.assertEqual(activated["config_hash"], created["config_hash"])
    
    @requires_db
    def test_activate_pack_with_expected_hash(self):
        """activate_pack verifies expected_hash if provided."""
        pack_id = f"{self.test_prefix}_activate_hash"
        config = {"value": 42}
        
        created = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        # Activate with correct hash
        self.registry.activate_pack(
            pack_id=pack_id,
            scope="GLOBAL",
            version=1,
            expected_hash=created["config_hash"],
        )
        
        # Activate with wrong hash should fail
        pack_id2 = f"{self.test_prefix}_activate_hash2"
        self.registry.create_pack(
            pack_id=pack_id2,
            pack_version=1,
            scope="GLOBAL",
            config={"other": 1},
        )
        
        with self.assertRaises(ThresholdRegistryError):
            self.registry.activate_pack(
                pack_id=pack_id2,
                scope="GLOBAL",
                version=1,
                expected_hash="0" * 64,  # Wrong hash
            )
    
    @requires_db
    def test_get_active_pack(self):
        """get_active_pack returns correct active pack."""
        pack_id = f"{self.test_prefix}_get_active"
        config = {"min": 5, "max": 100}
        
        # Create and activate
        self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        self.registry.activate_pack(
            pack_id=pack_id,
            scope="GLOBAL",
            version=1,
        )
        
        # Get active
        active = self.registry.get_active_pack(
            pack_id=pack_id,
            scope="GLOBAL",
        )
        
        self.assertEqual(active["pack_id"], pack_id)
        self.assertEqual(active["pack_version"], 1)
        self.assertEqual(active["config_json"]["min"], 5)
        self.assertEqual(active["config_json"]["max"], 100)
    
    @requires_db
    def test_get_active_pack_not_found(self):
        """get_active_pack raises PackNotFoundError if not found."""
        with self.assertRaises(PackNotFoundError):
            self.registry.get_active_pack(
                pack_id=f"{self.test_prefix}_nonexistent",
                scope="GLOBAL",
            )
    
    @requires_db
    def test_get_pack(self):
        """get_pack returns correct pack by ID and version."""
        pack_id = f"{self.test_prefix}_get_pack"
        config = {"value": 123}
        
        created = self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config=config,
        )
        
        retrieved = self.registry.get_pack(pack_id, 1)
        
        self.assertEqual(retrieved["pack_id"], pack_id)
        self.assertEqual(retrieved["pack_version"], 1)
        self.assertEqual(retrieved["config_hash"], created["config_hash"])
        self.assertEqual(retrieved["config_json"]["value"], 123)
    
    @requires_db
    def test_list_packs(self):
        """list_packs returns packs matching filters."""
        pack_id = f"{self.test_prefix}_list"
        
        # Create multiple versions
        self.registry.create_pack(
            pack_id=pack_id,
            pack_version=1,
            scope="GLOBAL",
            config={"v": 1},
        )
        self.registry.create_pack(
            pack_id=pack_id,
            pack_version=2,
            scope="GLOBAL",
            config={"v": 2},
        )
        
        # List by pack_id
        results = self.registry.list_packs(pack_id=pack_id)
        
        self.assertEqual(len(results), 2)
        versions = {r["pack_version"] for r in results}
        self.assertEqual(versions, {1, 2})
    
    @requires_db
    def test_validate_integrity(self):
        """validate_integrity returns correct results."""
        result = self.registry.validate_integrity()
        
        self.assertIn("valid", result)
        self.assertIn("errors", result)
        self.assertIn("warnings", result)
        self.assertIn("stats", result)


# ============================================================================
# Determinism Tests
# ============================================================================

class TestDeterminism(unittest.TestCase):
    """Test that the entire pipeline is deterministic."""
    
    def test_full_pipeline_determinism(self):
        """Same config always produces same canonical + hash, regardless of order."""
        configs = [
            {"a": 1, "b": 2, "c": 3},
            {"c": 3, "a": 1, "b": 2},
            {"b": 2, "c": 3, "a": 1},
        ]
        
        hashes = [hash_config(canonicalize_config(c)) for c in configs]
        
        # All hashes should be identical
        self.assertEqual(len(set(hashes)), 1)
    
    def test_nested_determinism(self):
        """Nested structures are deterministic."""
        config1 = {
            "thresholds": {"min": 5, "max": 100},
            "windows": {"short": 5, "long": 20},
        }
        config2 = {
            "windows": {"long": 20, "short": 5},
            "thresholds": {"max": 100, "min": 5},
        }
        
        self.assertEqual(
            hash_config(canonicalize_config(config1)),
            hash_config(canonicalize_config(config2)),
        )
    
    def test_float_precision_determinism(self):
        """Float values have deterministic precision."""
        # Same value, slightly different representations
        config1 = {"ratio": 0.333333}
        config2 = {"ratio": 0.3333330}
        
        # Both should normalize to same precision
        c1 = canonicalize_config(config1)
        c2 = canonicalize_config(config2)
        
        self.assertEqual(c1, c2)


if __name__ == "__main__":
    unittest.main()
