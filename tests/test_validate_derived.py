"""
Unit tests for OVC Option B.2 Derived Feature Validation

Tests the validate_derived_range_v0_1 module's core logic without
requiring database connectivity.
"""

import math
import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "validate"))

from validate_derived_range_v0_1 import (
    compute_l1_inline,
    values_match,
    build_run_id,
    parse_date,
    ValidationResult,
)


# ---------- compute_l1_inline Tests ----------

class TestComputeC1Inline:
    """Tests for L1 feature computation logic."""

    def test_bullish_bar_direction(self):
        """Bullish bar (close > open) should have direction = 1."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.8, c=1.3)
        assert result["direction"] == 1

    def test_bearish_bar_direction(self):
        """Bearish bar (close < open) should have direction = -1."""
        result = compute_l1_inline(o=1.3, h=1.5, l=0.8, c=1.0)
        assert result["direction"] == -1

    def test_doji_bar_direction(self):
        """Doji bar (close == open) should have direction = 0."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.8, c=1.0)
        assert result["direction"] == 0

    def test_range_calculation(self):
        """Range should be high - low."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.2)
        assert result["range"] == pytest.approx(1.0)

    def test_body_calculation(self):
        """Body should be abs(close - open)."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.3)
        assert result["body"] == pytest.approx(0.3)
        
        # Bearish bar
        result = compute_l1_inline(o=1.3, h=1.5, l=0.5, c=1.0)
        assert result["body"] == pytest.approx(0.3)

    def test_ret_calculation(self):
        """Return should be (close - open) / open."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.1)
        assert result["ret"] == pytest.approx(0.1)

    def test_ret_with_zero_open(self):
        """Return should be None when open is zero."""
        result = compute_l1_inline(o=0.0, h=1.5, l=0.0, c=1.0)
        assert result["ret"] is None

    def test_logret_calculation(self):
        """Log return should be log(close / open)."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=2.0)
        assert result["logret"] == pytest.approx(math.log(2.0))

    def test_logret_with_zero_open(self):
        """Log return should be None when open is zero."""
        result = compute_l1_inline(o=0.0, h=1.5, l=0.0, c=1.0)
        assert result["logret"] is None

    def test_logret_with_zero_close(self):
        """Log return should be None when close is zero."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.0, c=0.0)
        assert result["logret"] is None

    def test_body_ratio_calculation(self):
        """Body ratio should be body / range."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.3)
        # body = 0.3, range = 1.0
        assert result["body_ratio"] == pytest.approx(0.3)

    def test_body_ratio_zero_range(self):
        """Body ratio should be None when range is zero."""
        result = compute_l1_inline(o=1.0, h=1.0, l=1.0, c=1.0)
        assert result["body_ratio"] is None

    def test_close_pos_calculation(self):
        """Close position should be (close - low) / range."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.0)
        # (1.0 - 0.5) / 1.0 = 0.5
        assert result["close_pos"] == pytest.approx(0.5)

    def test_close_pos_zero_range(self):
        """Close position should be None when range is zero."""
        result = compute_l1_inline(o=1.0, h=1.0, l=1.0, c=1.0)
        assert result["close_pos"] is None

    def test_upper_wick_calculation(self):
        """Upper wick should be high - max(open, close)."""
        # Bullish bar
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.3)
        assert result["upper_wick"] == pytest.approx(0.2)
        
        # Bearish bar
        result = compute_l1_inline(o=1.3, h=1.5, l=0.5, c=1.0)
        assert result["upper_wick"] == pytest.approx(0.2)

    def test_lower_wick_calculation(self):
        """Lower wick should be min(open, close) - low."""
        # Bullish bar
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.3)
        assert result["lower_wick"] == pytest.approx(0.5)
        
        # Bearish bar
        result = compute_l1_inline(o=1.3, h=1.5, l=0.5, c=1.0)
        assert result["lower_wick"] == pytest.approx(0.5)

    def test_clv_calculation(self):
        """CLV should be ((close-low) - (high-close)) / (high-low)."""
        result = compute_l1_inline(o=1.0, h=1.5, l=0.5, c=1.3)
        # ((1.3-0.5) - (1.5-1.3)) / (1.5-0.5)
        # (0.8 - 0.2) / 1.0 = 0.6
        assert result["clv"] == pytest.approx(0.6)

    def test_clv_zero_range(self):
        """CLV should be None when range is zero."""
        result = compute_l1_inline(o=1.0, h=1.0, l=1.0, c=1.0)
        assert result["clv"] is None

    def test_determinism(self):
        """Same inputs should always produce same outputs."""
        o, h, l, c = 1.2345, 1.5678, 0.9876, 1.4321
        
        results = [compute_l1_inline(o, h, l, c) for _ in range(10)]
        
        for key in results[0].keys():
            values = [r[key] for r in results]
            assert all(v == values[0] for v in values), f"Non-deterministic: {key}"


# ---------- values_match Tests ----------

class TestValuesMatch:
    """Tests for value comparison with tolerance."""

    def test_both_none(self):
        """Both None should match."""
        assert values_match(None, None) is True

    def test_one_none(self):
        """One None should not match."""
        assert values_match(None, 1.0) is False
        assert values_match(1.0, None) is False

    def test_exact_integers(self):
        """Exact integers should match."""
        assert values_match(1, 1) is True
        assert values_match(0, 0) is True

    def test_different_integers(self):
        """Different integers should not match."""
        assert values_match(1, 2) is False

    def test_floats_within_tolerance(self):
        """Floats within tolerance should match."""
        assert values_match(1.0, 1.0 + 1e-10) is True

    def test_floats_outside_tolerance(self):
        """Floats outside tolerance should not match."""
        assert values_match(1.0, 1.0 + 1e-8) is False

    def test_custom_tolerance(self):
        """Custom tolerance should be respected."""
        assert values_match(1.0, 1.001, tolerance=0.01) is True
        assert values_match(1.0, 1.1, tolerance=0.01) is False


# ---------- build_run_id Tests ----------

class TestBuildRunId:
    """Tests for deterministic run ID generation."""

    def test_determinism(self):
        """Same inputs should produce same run ID."""
        id1 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        id2 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        assert id1 == id2

    def test_different_symbols(self):
        """Different symbols should produce different run IDs."""
        id1 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        id2 = build_run_id("EURUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        assert id1 != id2

    def test_different_dates(self):
        """Different dates should produce different run IDs."""
        id1 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        id2 = build_run_id("GBPUSD", date(2026, 1, 14), date(2026, 1, 17), "fail", False)
        assert id1 != id2

    def test_different_modes(self):
        """Different modes should produce different run IDs."""
        id1 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        id2 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "skip", False)
        assert id1 != id2

    def test_different_tv_flag(self):
        """Different TV comparison flag should produce different run IDs."""
        id1 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        id2 = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", True)
        assert id1 != id2

    def test_returns_valid_uuid(self):
        """Run ID should be a valid UUID string."""
        run_id = build_run_id("GBPUSD", date(2026, 1, 13), date(2026, 1, 17), "fail", False)
        parsed = uuid.UUID(run_id)
        assert str(parsed) == run_id


# ---------- parse_date Tests ----------

class TestParseDate:
    """Tests for date parsing."""

    def test_valid_date(self):
        """Valid YYYY-MM-DD should parse correctly."""
        result = parse_date("2026-01-15")
        assert result == date(2026, 1, 15)

    def test_invalid_format(self):
        """Invalid format should raise SystemExit."""
        with pytest.raises(SystemExit):
            parse_date("01-15-2026")

    def test_invalid_date(self):
        """Invalid date should raise SystemExit."""
        with pytest.raises(SystemExit):
            parse_date("2026-02-30")


# ---------- ValidationResult Tests ----------

class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_default_values(self):
        """Default values should be set correctly."""
        result = ValidationResult(
            run_id="test-id",
            version="v0.1",
            symbol="GBPUSD",
            start_date="2026-01-13",
            end_date="2026-01-17",
            mode="fail",
            compare_tv=False,
        )
        
        assert result.b_block_count == 0
        assert result.l1_row_count == 0
        assert result.l2_row_count == 0
        assert result.coverage_parity is True
        assert result.l1_duplicates == 0
        assert result.l2_duplicates == 0
        assert result.status == "PASS"
        assert result.errors == []
        assert result.warnings == []

    def test_to_dict(self):
        """to_dict should return all fields."""
        result = ValidationResult(
            run_id="test-id",
            version="v0.1",
            symbol="GBPUSD",
            start_date="2026-01-13",
            end_date="2026-01-17",
            mode="fail",
            compare_tv=False,
        )
        result.b_block_count = 100
        result.errors = ["error1"]
        
        d = result.to_dict()
        
        assert d["run_id"] == "test-id"
        assert d["b_block_count"] == 100
        assert d["errors"] == ["error1"]


# ---------- Window Spec Validation Logic Tests ----------

class TestWindowSpecValidation:
    """Tests for window_spec validation logic."""

    def test_required_components(self):
        """Required components list should be correct."""
        from validate_derived_range_v0_1 import REQUIRED_WINDOW_SPECS
        
        assert "N=1" in REQUIRED_WINDOW_SPECS
        assert "N=12" in REQUIRED_WINDOW_SPECS
        assert "session=date_ny" in REQUIRED_WINDOW_SPECS
        assert "rd_len=" in REQUIRED_WINDOW_SPECS


# ---------- Column Lists Tests ----------

class TestColumnLists:
    """Tests for feature column lists."""

    def test_l1_columns(self):
        """L1 columns should match compute_c1 output."""
        from validate_derived_range_v0_1 import C1_FEATURE_COLUMNS
        
        expected = [
            "range", "body", "direction", "ret", "logret",
            "body_ratio", "close_pos", "upper_wick", "lower_wick", "clv",
            "range_zero", "inputs_valid"
        ]
        assert set(C1_FEATURE_COLUMNS) == set(expected)

    def test_l2_columns(self):
        """L2 columns should include all documented features."""
        from validate_derived_range_v0_1 import C2_FEATURE_COLUMNS
        
        # Key features that must exist
        assert "gap" in C2_FEATURE_COLUMNS
        assert "sess_high" in C2_FEATURE_COLUMNS
        assert "sess_low" in C2_FEATURE_COLUMNS
        assert "roll_avg_range_12" in C2_FEATURE_COLUMNS
        assert "hh_12" in C2_FEATURE_COLUMNS
        assert "ll_12" in C2_FEATURE_COLUMNS
        assert "rd_hi" in C2_FEATURE_COLUMNS
        assert "rd_lo" in C2_FEATURE_COLUMNS
        assert "rd_mid" in C2_FEATURE_COLUMNS


# ---------- Edge Cases ----------

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_price_bar(self):
        """All zeros should not crash."""
        result = compute_l1_inline(o=0, h=0, l=0, c=0)
        assert result["range"] == 0
        assert result["body"] == 0
        assert result["direction"] == 0

    def test_negative_prices(self):
        """Negative prices (shouldn't occur but shouldn't crash)."""
        result = compute_l1_inline(o=-1.0, h=0.0, l=-2.0, c=-0.5)
        assert result["range"] == pytest.approx(2.0)
        assert result["direction"] == 1  # -0.5 > -1.0

    def test_very_small_range(self):
        """Very small range should still compute correctly."""
        result = compute_l1_inline(o=1.0, h=1.0001, l=0.9999, c=1.00005)
        assert result["range"] == pytest.approx(0.0002)
        assert result["body_ratio"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
