"""
Unit tests for DayFingerprint v0.1 computation.
Path 1 (Observation & Cataloging Only)
"""

import json
import math
import sys
from pathlib import Path

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from trajectory_families import (
    compute_fingerprint,
    compute_jump_count,
    compute_max_run_length,
    compute_net_displacement,
    compute_path_length,
    compute_quadrant_counts,
    compute_quadrant_entropy,
    compute_quadrant_sequence,
    compute_transition_counts,
    compute_turning,
    get_dominant_quadrant,
    is_valid_fingerprint,
    load_params,
    load_trajectory_csv,
    safe_mean,
    safe_std,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestQuadrantSequence:
    """Tests for compute_quadrant_sequence."""

    def test_q1_expansion(self):
        """Q1: x >= E_hi AND |y| <= S_hi."""
        x = [0.7]
        y = [0.1]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q1"]

    def test_q2_consolidation(self):
        """Q2: x < E_hi AND |y| <= S_hi."""
        x = [0.4]
        y = [0.1]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q2"]

    def test_q3_reversal(self):
        """Q3: x >= E_hi AND |y| > S_hi."""
        x = [0.7]
        y = [0.5]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q3"]

    def test_q4_retracement(self):
        """Q4: x < E_hi AND |y| > S_hi."""
        x = [0.4]
        y = [-0.5]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q4"]

    def test_null_handling(self):
        """NULL when x or y is None."""
        x = [0.5, None, 0.5]
        y = [0.1, 0.1, None]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q2", None, None]

    def test_boundary_e_hi(self):
        """x == E_hi should be in Q1 or Q3 (high energy)."""
        x = [0.6]
        y = [0.0]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q1"]

    def test_boundary_s_hi(self):
        """y == S_hi should be low shift (Q1 or Q2)."""
        x = [0.5]
        y = [0.35]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q2"]

    def test_negative_y(self):
        """Negative y with |y| > S_hi should be Q3 or Q4."""
        x = [0.7]
        y = [-0.5]
        result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
        assert result == ["Q3"]


class TestQuadrantCounts:
    """Tests for compute_quadrant_counts."""

    def test_all_same_quadrant(self):
        """All points in Q2."""
        quadrants = ["Q2"] * 12
        result = compute_quadrant_counts(quadrants)
        assert result == {"Q1": 0, "Q2": 12, "Q3": 0, "Q4": 0}

    def test_mixed_quadrants(self):
        """Mixed quadrants."""
        quadrants = ["Q1", "Q1", "Q2", "Q2", "Q2", "Q3", "Q3", "Q4", "Q4", "Q4", "Q4", "Q1"]
        result = compute_quadrant_counts(quadrants)
        assert result == {"Q1": 3, "Q2": 3, "Q3": 2, "Q4": 4}

    def test_with_nulls(self):
        """Nulls should not be counted."""
        quadrants = ["Q1", None, "Q2", None, "Q1"]
        result = compute_quadrant_counts(quadrants)
        assert result == {"Q1": 2, "Q2": 1, "Q3": 0, "Q4": 0}


class TestTransitionCounts:
    """Tests for compute_transition_counts."""

    def test_all_same_quadrant(self):
        """All self-transitions."""
        quadrants = ["Q2", "Q2", "Q2"]
        result = compute_transition_counts(quadrants)
        assert result["Q2_Q2"] == 2
        assert sum(result.values()) == 2

    def test_alternating(self):
        """Q1-Q2-Q1-Q2 alternation."""
        quadrants = ["Q1", "Q2", "Q1", "Q2"]
        result = compute_transition_counts(quadrants)
        assert result["Q1_Q2"] == 2
        assert result["Q2_Q1"] == 1

    def test_with_nulls(self):
        """Nulls break transition chains."""
        quadrants = ["Q1", None, "Q2"]
        result = compute_transition_counts(quadrants)
        # No transitions counted due to null
        assert sum(result.values()) == 0

    def test_all_16_keys_present(self):
        """All 16 transition keys should be present."""
        quadrants = ["Q1"]
        result = compute_transition_counts(quadrants)
        assert len(result) == 16
        for i in range(1, 5):
            for j in range(1, 5):
                assert f"Q{i}_Q{j}" in result


class TestQuadrantEntropy:
    """Tests for compute_quadrant_entropy."""

    def test_uniform_distribution(self):
        """Uniform distribution has max entropy = 2.0 (log2(4))."""
        q_counts = {"Q1": 3, "Q2": 3, "Q3": 3, "Q4": 3}
        result = compute_quadrant_entropy(q_counts, precision=6)
        assert abs(result - 2.0) < 0.0001

    def test_single_quadrant(self):
        """Single quadrant has zero entropy."""
        q_counts = {"Q1": 12, "Q2": 0, "Q3": 0, "Q4": 0}
        result = compute_quadrant_entropy(q_counts, precision=6)
        assert result == 0.0

    def test_empty_counts(self):
        """All zeros returns 0."""
        q_counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
        result = compute_quadrant_entropy(q_counts, precision=6)
        assert result == 0.0


class TestMaxRunLength:
    """Tests for compute_max_run_length."""

    def test_all_same(self):
        """All same quadrant = max run of 12."""
        quadrants = ["Q2"] * 12
        result = compute_max_run_length(quadrants)
        assert result == 12

    def test_alternating(self):
        """Alternating = max run of 1."""
        quadrants = ["Q1", "Q2", "Q1", "Q2"]
        result = compute_max_run_length(quadrants)
        assert result == 1

    def test_with_run_in_middle(self):
        """Run of 4 in middle."""
        quadrants = ["Q1", "Q2", "Q2", "Q2", "Q2", "Q1"]
        result = compute_max_run_length(quadrants)
        assert result == 4

    def test_null_breaks_run(self):
        """Null breaks the run."""
        quadrants = ["Q1", "Q1", None, "Q1", "Q1"]
        result = compute_max_run_length(quadrants)
        assert result == 2


class TestPathGeometry:
    """Tests for path geometry computations."""

    def test_path_length_straight_line(self):
        """Straight line path."""
        x = [0.0, 0.5, 1.0]
        y = [0.0, 0.0, 0.0]
        result = compute_path_length(x, y, precision=6)
        assert abs(result - 1.0) < 0.0001

    def test_path_length_diagonal(self):
        """Diagonal path."""
        x = [0.0, 1.0]
        y = [0.0, 1.0]
        result = compute_path_length(x, y, precision=6)
        expected = math.sqrt(2)
        assert abs(result - expected) < 0.0001

    def test_net_displacement(self):
        """Net displacement is start to end."""
        x = [0.0, 0.5, 0.3, 1.0]
        y = [0.0, 0.5, -0.5, 0.0]
        result = compute_net_displacement(x, y, precision=6)
        assert abs(result - 1.0) < 0.0001

    def test_net_displacement_zero(self):
        """Return to start = zero displacement."""
        x = [0.0, 1.0, 0.0]
        y = [0.0, 0.0, 0.0]
        result = compute_net_displacement(x, y, precision=6)
        assert result == 0.0

    def test_turning_straight_line(self):
        """Straight line has zero turning."""
        x = [0.0, 0.5, 1.0]
        y = [0.0, 0.0, 0.0]
        result = compute_turning(x, y, precision=6)
        assert result == 0.0

    def test_turning_90_degree(self):
        """90 degree turn."""
        x = [0.0, 1.0, 1.0]
        y = [0.0, 0.0, 1.0]
        result = compute_turning(x, y, precision=6)
        expected = math.pi / 2
        assert abs(result - expected) < 0.01

    def test_jump_count(self):
        """Count jumps exceeding threshold."""
        y = [0.0, 0.1, 0.4, 0.5, 0.2]  # Jump from 0.1 to 0.4 exceeds 0.25
        result = compute_jump_count(y, y_jump_threshold=0.25)
        assert result == 2  # 0.1->0.4 (0.3) and 0.5->0.2 (0.3)


class TestSafeMeanStd:
    """Tests for safe_mean and safe_std."""

    def test_safe_mean_normal(self):
        """Normal mean computation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = safe_mean(values)
        assert result == 3.0

    def test_safe_mean_with_nulls(self):
        """Nulls are ignored."""
        values = [1.0, None, 3.0, None, 5.0]
        result = safe_mean(values)
        assert result == 3.0

    def test_safe_mean_empty(self):
        """Empty returns 0."""
        values = [None, None]
        result = safe_mean(values)
        assert result == 0.0

    def test_safe_std_normal(self):
        """Normal std computation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = safe_std(values)
        # Population std of [1,2,3,4,5] = sqrt(2)
        expected = math.sqrt(2)
        assert abs(result - expected) < 0.0001

    def test_safe_std_single_value(self):
        """Single value returns 0."""
        values = [5.0]
        result = safe_std(values)
        assert result == 0.0


class TestDominantQuadrant:
    """Tests for get_dominant_quadrant."""

    def test_clear_dominant(self):
        """One quadrant clearly dominant."""
        quadrants = ["Q2", "Q2", "Q2", "Q1", "Q1"]
        result = get_dominant_quadrant(quadrants)
        assert result == "Q2"

    def test_tie_returns_first_sorted(self):
        """Tie returns first in sorted order (Q1 before Q2)."""
        quadrants = ["Q1", "Q1", "Q2", "Q2"]
        result = get_dominant_quadrant(quadrants)
        assert result == "Q1"

    def test_all_null(self):
        """All null returns None."""
        quadrants = [None, None, None]
        result = get_dominant_quadrant(quadrants)
        assert result is None


class TestGoldenFixture:
    """Test against golden fixture for determinism."""

    def test_fingerprint_matches_golden(self):
        """Computed fingerprint matches golden fixture."""
        # Load trajectory
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)

        # Load params
        params = load_params()

        # Compute fingerprint
        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts={
                "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
                "trajectory_png": "tests/fixtures/sample_trajectory.png",
            },
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Load golden
        golden_path = FIXTURES_DIR / "golden_fingerprint_v0_1.json"
        with open(golden_path, "r") as f:
            golden = json.load(f)

        # Compare all fields except generated_at
        for key in golden:
            if key == "generated_at":
                continue
            assert fp[key] == golden[key], f"Mismatch in field: {key}"

    def test_content_hash_matches_golden(self):
        """Content hash matches golden fixture."""
        # Load trajectory
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)

        # Load params
        params = load_params()

        # Compute fingerprint
        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts={
                "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
                "trajectory_png": "tests/fixtures/sample_trajectory.png",
            },
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Load golden
        golden_path = FIXTURES_DIR / "golden_fingerprint_v0_1.json"
        with open(golden_path, "r") as f:
            golden = json.load(f)

        assert fp["content_hash"] == golden["content_hash"]


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_valid_fingerprint_passes(self):
        """Valid fingerprint passes validation."""
        golden_path = FIXTURES_DIR / "golden_fingerprint_v0_1.json"
        with open(golden_path, "r") as f:
            fp = json.load(f)

        is_valid, errors = is_valid_fingerprint(fp)
        assert is_valid, f"Validation errors: {errors}"

    def test_missing_field_fails(self):
        """Missing required field fails validation."""
        golden_path = FIXTURES_DIR / "golden_fingerprint_v0_1.json"
        with open(golden_path, "r") as f:
            fp = json.load(f)

        del fp["quadrant_string"]
        is_valid, errors = is_valid_fingerprint(fp)
        assert not is_valid
        assert any("quadrant_string" in e for e in errors)

    def test_invalid_quadrant_fails(self):
        """Invalid quadrant value fails validation."""
        golden_path = FIXTURES_DIR / "golden_fingerprint_v0_1.json"
        with open(golden_path, "r") as f:
            fp = json.load(f)

        fp["quadrants"][0] = "Q5"  # Invalid
        is_valid, errors = is_valid_fingerprint(fp)
        assert not is_valid


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_path_length_zero_efficiency(self):
        """path_length=0 results in efficiency=0."""
        # All points at same location
        points = [{"block": chr(65 + i), "x": 0.5, "y": 0.0} for i in range(12)]
        params = load_params()

        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts={
                "trajectory_csv": "test.csv",
                "trajectory_png": "test.png",
            },
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        assert fp["path_geometry"]["path_length"] == 0.0
        assert fp["path_geometry"]["efficiency"] == 0.0

    def test_nan_raises_error(self):
        """NaN values raise ValueError."""
        points = [{"block": chr(65 + i), "x": 0.5, "y": 0.0} for i in range(12)]
        points[5]["x"] = float("nan")

        params = load_params()

        with pytest.raises(ValueError, match="NaN"):
            compute_fingerprint(
                points=points,
                params=params,
                source_artifacts={
                    "trajectory_csv": "test.csv",
                    "trajectory_png": "test.png",
                },
                date_ny="2022-12-12",
                symbol="GBPUSD",
            )

    def test_wrong_block_count_raises_error(self):
        """Non-12 block count raises ValueError."""
        points = [{"block": chr(65 + i), "x": 0.5, "y": 0.0} for i in range(10)]
        params = load_params()

        with pytest.raises(ValueError, match="Expected 12 points"):
            compute_fingerprint(
                points=points,
                params=params,
                source_artifacts={
                    "trajectory_csv": "test.csv",
                    "trajectory_png": "test.png",
                },
                date_ny="2022-12-12",
                symbol="GBPUSD",
            )
