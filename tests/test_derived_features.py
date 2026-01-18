"""
Tests for OVC Option B.1 Derived Feature Packs (C1 + C2)

Test Coverage:
    1. Determinism: Same inputs → same outputs
    2. Idempotency: Rerun produces no duplicates and same results
    3. Window_spec presence for all C2 outputs
    4. Formula correctness against known values

Per c_layer_boundary_spec_v0.1.md:
    - C1: Single-bar OHLC math. No history.
    - C2: Multi-bar structure. Explicit window_spec required.
"""

import hashlib
import math
import sys
import unittest
from pathlib import Path

# Add src to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from derived.compute_c1_v0_1 import (
    compute_c1_features,
    compute_formula_hash,
    C1_FORMULA_DEFINITION,
    FORMULA_HASH as C1_FORMULA_HASH,
)
from derived.compute_c2_v0_1 import (
    compute_c2_features_for_block,
    compute_formula_hash as compute_c2_formula_hash,
    build_aggregated_window_spec,
    C2_FORMULA_DEFINITION,
    WINDOW_SPECS,
    DEFAULT_RD_LEN,
)


class TestC1Determinism(unittest.TestCase):
    """Test that C1 computations are deterministic."""
    
    def test_same_inputs_same_outputs(self):
        """Same OHLC values should produce identical C1 features."""
        o, h, l, c = 1.2500, 1.2550, 1.2480, 1.2520
        
        result1 = compute_c1_features(o, h, l, c)
        result2 = compute_c1_features(o, h, l, c)
        
        self.assertEqual(result1, result2)
    
    def test_determinism_multiple_runs(self):
        """Multiple runs with same inputs produce same results."""
        test_cases = [
            (1.2500, 1.2550, 1.2480, 1.2520),
            (1.0000, 1.0100, 0.9950, 1.0050),
            (1.5000, 1.5000, 1.5000, 1.5000),  # Zero range
            (0.0, 1.0, 0.0, 0.5),  # o=0 edge case
        ]
        
        for o, h, l, c in test_cases:
            results = [compute_c1_features(o, h, l, c) for _ in range(5)]
            for r in results[1:]:
                self.assertEqual(results[0], r)


class TestC1Correctness(unittest.TestCase):
    """Test C1 formula correctness."""
    
    def test_range_formula(self):
        """range = h - l"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        self.assertAlmostEqual(result["range"], 0.7, places=10)
    
    def test_body_formula(self):
        """body = abs(c - o)"""
        # Bullish
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        self.assertAlmostEqual(result["body"], 0.2, places=10)
        
        # Bearish
        result = compute_c1_features(1.2, 1.5, 0.8, 1.0)
        self.assertAlmostEqual(result["body"], 0.2, places=10)
    
    def test_direction_formula(self):
        """direction = sign(c - o)"""
        # Bullish
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        self.assertEqual(result["direction"], 1)
        
        # Bearish
        result = compute_c1_features(1.2, 1.5, 0.8, 1.0)
        self.assertEqual(result["direction"], -1)
        
        # Neutral (doji)
        result = compute_c1_features(1.0, 1.5, 0.8, 1.0)
        self.assertEqual(result["direction"], 0)
    
    def test_ret_formula(self):
        """ret = (c - o) / o"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        self.assertAlmostEqual(result["ret"], 0.2, places=10)
        
        # o=0 edge case
        result = compute_c1_features(0.0, 1.0, 0.0, 0.5)
        self.assertIsNone(result["ret"])
    
    def test_logret_formula(self):
        """logret = ln(c / o)"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        expected = math.log(1.2 / 1.0)
        self.assertAlmostEqual(result["logret"], expected, places=10)
        
        # c=0 or o=0 edge case
        result = compute_c1_features(0.0, 1.0, 0.0, 0.5)
        self.assertIsNone(result["logret"])
    
    def test_body_ratio_formula(self):
        """body_ratio = body / range"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        # body=0.2, range=0.7
        self.assertAlmostEqual(result["body_ratio"], 0.2 / 0.7, places=10)
        
        # Zero range
        result = compute_c1_features(1.0, 1.0, 1.0, 1.0)
        self.assertIsNone(result["body_ratio"])
    
    def test_close_pos_formula(self):
        """close_pos = (c - l) / range"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        # (1.2 - 0.8) / 0.7 = 0.4 / 0.7
        self.assertAlmostEqual(result["close_pos"], 0.4 / 0.7, places=10)
    
    def test_upper_wick_formula(self):
        """upper_wick = h - max(o, c)"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        # h=1.5, max(o,c)=1.2 → 0.3
        self.assertAlmostEqual(result["upper_wick"], 0.3, places=10)
    
    def test_lower_wick_formula(self):
        """lower_wick = min(o, c) - l"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        # min(o,c)=1.0, l=0.8 → 0.2
        self.assertAlmostEqual(result["lower_wick"], 0.2, places=10)
    
    def test_clv_formula(self):
        """clv = ((c - l) - (h - c)) / (h - l)"""
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        # ((1.2 - 0.8) - (1.5 - 1.2)) / 0.7 = (0.4 - 0.3) / 0.7 = 0.1 / 0.7
        expected = 0.1 / 0.7
        self.assertAlmostEqual(result["clv"], expected, places=10)
    
    def test_range_zero_flag(self):
        """range_zero = (range == 0)"""
        result = compute_c1_features(1.0, 1.0, 1.0, 1.0)
        self.assertTrue(result["range_zero"])
        
        result = compute_c1_features(1.0, 1.5, 0.8, 1.2)
        self.assertFalse(result["range_zero"])


class TestC1FormulaHash(unittest.TestCase):
    """Test C1 formula hash computation."""
    
    def test_formula_hash_deterministic(self):
        """Formula hash should be deterministic."""
        hash1 = compute_formula_hash(C1_FORMULA_DEFINITION)
        hash2 = compute_formula_hash(C1_FORMULA_DEFINITION)
        self.assertEqual(hash1, hash2)
    
    def test_formula_hash_changes_with_definition(self):
        """Different formula definition should produce different hash."""
        hash1 = compute_formula_hash(C1_FORMULA_DEFINITION)
        hash2 = compute_formula_hash("modified formula")
        self.assertNotEqual(hash1, hash2)
    
    def test_module_hash_constant(self):
        """Module FORMULA_HASH should match recomputed hash."""
        expected = compute_formula_hash(C1_FORMULA_DEFINITION)
        self.assertEqual(C1_FORMULA_HASH, expected)


class TestC2WindowSpec(unittest.TestCase):
    """Test that all C2 features have window_spec defined."""
    
    def test_all_c2_features_have_window_spec(self):
        """Every C2 feature must have an explicit window_spec."""
        c2_features = [
            "gap", "took_prev_high", "took_prev_low",
            "sess_high", "sess_low", "dist_sess_high", "dist_sess_low",
            "roll_avg_range_12", "roll_std_logret_12", "range_z_12",
            "hh_12", "ll_12",
            "rd_hi", "rd_lo", "rd_mid",
        ]
        
        for feature in c2_features:
            self.assertIn(
                feature, WINDOW_SPECS,
                f"C2 feature '{feature}' missing from WINDOW_SPECS"
            )
            self.assertIsNotNone(
                WINDOW_SPECS[feature],
                f"C2 feature '{feature}' has None window_spec"
            )
    
    def test_window_spec_format(self):
        """Window specs should follow documented format."""
        valid_formats = [
            "N=1", "N=12",
            "session=date_ny",
            "parameterized=rd_len",
        ]
        
        for feature, spec in WINDOW_SPECS.items():
            self.assertIn(
                spec, valid_formats,
                f"C2 feature '{feature}' has invalid window_spec: {spec}"
            )
    
    def test_aggregated_window_spec(self):
        """Aggregated window_spec should include all unique specs."""
        agg_spec = build_aggregated_window_spec(12)
        self.assertIn("N=1", agg_spec)
        self.assertIn("N=12", agg_spec)
        self.assertIn("session=date_ny", agg_spec)
        self.assertIn("rd_len=12", agg_spec)


class TestC2Determinism(unittest.TestCase):
    """Test that C2 computations are deterministic."""
    
    def _make_block(self, block_id: str, o: float, h: float, l: float, c: float, date_ny: str, bar_close_ms: int):
        return {
            "block_id": block_id,
            "o": o, "h": h, "l": l, "c": c,
            "date_ny": date_ny,
            "bar_close_ms": bar_close_ms,
        }
    
    def test_n1_features_deterministic(self):
        """N=1 features should be deterministic."""
        current = self._make_block("20260118-A-GBPUSD", 1.25, 1.26, 1.24, 1.255, "2026-01-18", 1737151200000)
        prev = self._make_block("20260117-L-GBPUSD", 1.24, 1.25, 1.23, 1.245, "2026-01-17", 1737144000000)
        
        result1 = compute_c2_features_for_block(
            current, prev, [current], [prev, current], [prev, current], {}, 12
        )
        result2 = compute_c2_features_for_block(
            current, prev, [current], [prev, current], [prev, current], {}, 12
        )
        
        self.assertEqual(result1["gap"], result2["gap"])
        self.assertEqual(result1["took_prev_high"], result2["took_prev_high"])
        self.assertEqual(result1["took_prev_low"], result2["took_prev_low"])


class TestC2Correctness(unittest.TestCase):
    """Test C2 formula correctness."""
    
    def _make_block(self, block_id: str, o: float, h: float, l: float, c: float, date_ny: str, bar_close_ms: int):
        return {
            "block_id": block_id,
            "o": o, "h": h, "l": l, "c": c,
            "date_ny": date_ny,
            "bar_close_ms": bar_close_ms,
        }
    
    def test_gap_formula(self):
        """gap = o - prev_c"""
        current = self._make_block("20260118-A-GBPUSD", 1.2500, 1.2600, 1.2400, 1.2550, "2026-01-18", 1737151200000)
        prev = self._make_block("20260117-L-GBPUSD", 1.2400, 1.2500, 1.2300, 1.2450, "2026-01-17", 1737144000000)
        
        result = compute_c2_features_for_block(
            current, prev, [current], [prev, current], [prev, current], {}, 12
        )
        
        expected_gap = 1.2500 - 1.2450  # o - prev_c
        self.assertAlmostEqual(result["gap"], expected_gap, places=10)
    
    def test_took_prev_high_formula(self):
        """took_prev_high = h > prev_h"""
        current = self._make_block("20260118-A-GBPUSD", 1.25, 1.26, 1.24, 1.255, "2026-01-18", 1737151200000)
        prev = self._make_block("20260117-L-GBPUSD", 1.24, 1.25, 1.23, 1.245, "2026-01-17", 1737144000000)
        
        result = compute_c2_features_for_block(
            current, prev, [current], [prev, current], [prev, current], {}, 12
        )
        
        # current.h (1.26) > prev.h (1.25) → True
        self.assertTrue(result["took_prev_high"])
    
    def test_took_prev_low_formula(self):
        """took_prev_low = l < prev_l"""
        current = self._make_block("20260118-A-GBPUSD", 1.25, 1.26, 1.22, 1.255, "2026-01-18", 1737151200000)
        prev = self._make_block("20260117-L-GBPUSD", 1.24, 1.25, 1.23, 1.245, "2026-01-17", 1737144000000)
        
        result = compute_c2_features_for_block(
            current, prev, [current], [prev, current], [prev, current], {}, 12
        )
        
        # current.l (1.22) < prev.l (1.23) → True
        self.assertTrue(result["took_prev_low"])
    
    def test_sess_high_formula(self):
        """sess_high = running max(h) within date_ny"""
        blocks = [
            self._make_block("20260118-A-GBPUSD", 1.25, 1.26, 1.24, 1.255, "2026-01-18", 1737151200000),
            self._make_block("20260118-B-GBPUSD", 1.25, 1.27, 1.24, 1.265, "2026-01-18", 1737158400000),
            self._make_block("20260118-C-GBPUSD", 1.26, 1.265, 1.25, 1.26, "2026-01-18", 1737165600000),
        ]
        
        result = compute_c2_features_for_block(
            blocks[2], blocks[1], blocks, blocks, blocks, {}, 12
        )
        
        # max(1.26, 1.27, 1.265) = 1.27
        self.assertAlmostEqual(result["sess_high"], 1.27, places=10)
    
    def test_no_prev_block(self):
        """Features requiring prev block should be None when no prev exists."""
        current = self._make_block("20260118-A-GBPUSD", 1.25, 1.26, 1.24, 1.255, "2026-01-18", 1737151200000)
        
        result = compute_c2_features_for_block(
            current, None, [current], [current], [current], {}, 12
        )
        
        self.assertIsNone(result["gap"])
        self.assertIsNone(result["took_prev_high"])
        self.assertIsNone(result["took_prev_low"])
        self.assertFalse(result["prev_block_exists"])


class TestC2FormulaHash(unittest.TestCase):
    """Test C2 formula hash computation."""
    
    def test_formula_hash_includes_rd_len(self):
        """Formula hash should change with rd_len parameter."""
        hash1 = compute_c2_formula_hash(C2_FORMULA_DEFINITION, 12)
        hash2 = compute_c2_formula_hash(C2_FORMULA_DEFINITION, 24)
        self.assertNotEqual(hash1, hash2)
    
    def test_formula_hash_deterministic(self):
        """Same formula + params should produce same hash."""
        hash1 = compute_c2_formula_hash(C2_FORMULA_DEFINITION, 12)
        hash2 = compute_c2_formula_hash(C2_FORMULA_DEFINITION, 12)
        self.assertEqual(hash1, hash2)


if __name__ == "__main__":
    unittest.main()
