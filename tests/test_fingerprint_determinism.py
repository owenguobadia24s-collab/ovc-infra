"""
Determinism tests for DayFingerprint v0.1.
Path 1 (Observation & Cataloging Only)

Verifies that re-running fingerprint computation produces identical outputs.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from trajectory_families import (
    compute_content_hash,
    compute_fingerprint,
    compute_quadrant_sequence,
    compute_transition_counts,
    load_params,
    load_trajectory_csv,
    write_fingerprint_json,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestComputationDeterminism:
    """Tests that all computations are deterministic."""

    def test_fingerprint_repeated_computation(self):
        """Same inputs produce identical fingerprints (except generated_at)."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        # Compute fingerprint multiple times
        fps = []
        for _ in range(5):
            fp = compute_fingerprint(
                points=points,
                params=params,
                source_artifacts=source_artifacts,
                date_ny="2022-12-12",
                symbol="GBPUSD",
            )
            fps.append(fp)

        # Compare all fields except generated_at
        for i in range(1, len(fps)):
            for key in fps[0]:
                if key == "generated_at":
                    continue
                assert fps[i][key] == fps[0][key], f"Run {i} differs in field: {key}"

    def test_content_hash_determinism(self):
        """Content hash is identical across runs."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        hashes = []
        for _ in range(5):
            fp = compute_fingerprint(
                points=points,
                params=params,
                source_artifacts=source_artifacts,
                date_ny="2022-12-12",
                symbol="GBPUSD",
            )
            hashes.append(fp["content_hash"])

        # All hashes should be identical
        assert len(set(hashes)) == 1, f"Got different hashes: {set(hashes)}"

    def test_fingerprint_id_determinism(self):
        """Fingerprint ID is identical across runs."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        ids = []
        for _ in range(5):
            fp = compute_fingerprint(
                points=points,
                params=params,
                source_artifacts=source_artifacts,
                date_ny="2022-12-12",
                symbol="GBPUSD",
            )
            ids.append(fp["fingerprint_id"])

        # All IDs should be identical
        assert len(set(ids)) == 1, f"Got different IDs: {set(ids)}"

    def test_quadrant_sequence_determinism(self):
        """Quadrant sequence is deterministic."""
        x = [0.42, 0.55, 0.62, 0.70, 0.75, 0.52, 0.48, 0.58, 0.66, 0.63, 0.57, 0.40]
        y = [-0.10, -0.20, -0.15, 0.10, 0.45, 0.50, 0.30, -0.40, -0.55, -0.20, 0.05, 0.15]

        results = []
        for _ in range(10):
            result = compute_quadrant_sequence(x, y, E_hi=0.6, S_hi=0.35)
            results.append(tuple(result))

        assert len(set(results)) == 1

    def test_transition_counts_determinism(self):
        """Transition counts are deterministic."""
        quadrants = ["Q2", "Q2", "Q1", "Q1", "Q3", "Q4", "Q2", "Q4", "Q3", "Q1", "Q2", "Q2"]

        results = []
        for _ in range(10):
            result = compute_transition_counts(quadrants)
            # Convert to sorted tuple for comparison
            sorted_items = tuple(sorted(result.items()))
            results.append(sorted_items)

        assert len(set(results)) == 1


class TestOutputDeterminism:
    """Tests that output files are deterministic."""

    def test_json_output_byte_identical(self):
        """JSON output is byte-identical across writes."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Write to multiple temp files
        contents = []
        for _ in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                temp_path = Path(f.name)

            write_fingerprint_json(fp, temp_path)
            content = temp_path.read_text(encoding="utf-8")
            contents.append(content)
            temp_path.unlink()

        # All contents should be identical
        assert len(set(contents)) == 1

    def test_json_key_ordering(self):
        """JSON keys are consistently sorted."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Serialize and check key order
        json_str = json.dumps(fp, sort_keys=True)
        parsed = json.loads(json_str)

        # Top-level keys should be sorted
        keys = list(parsed.keys())
        assert keys == sorted(keys)

        # Nested keys should also be sorted
        pg_keys = list(parsed["path_geometry"].keys())
        assert pg_keys == sorted(pg_keys)

        qd_keys = list(parsed["quadrant_dynamics"].keys())
        assert qd_keys == sorted(qd_keys)


class TestNumericPrecision:
    """Tests for numeric precision and rounding."""

    def test_precision_6_decimals(self):
        """All floats are rounded to 6 decimals."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Check path geometry floats
        pg = fp["path_geometry"]
        for key in ["path_length", "net_displacement", "efficiency", "turning",
                    "energy_mean", "energy_std", "shift_mean", "shift_std"]:
            value = pg[key]
            # Convert to string and check decimal places
            str_val = f"{value:.10f}"
            # After 6 decimals, should be zeros
            decimal_part = str_val.split(".")[1]
            assert decimal_part[6:] == "0000", f"{key} has more than 6 decimal places: {value}"

        # Check point coordinates
        for point in fp["points"]:
            if point["x"] is not None:
                str_val = f"{point['x']:.10f}"
                decimal_part = str_val.split(".")[1]
                assert decimal_part[6:] == "0000"
            if point["y"] is not None:
                str_val = f"{point['y']:.10f}"
                decimal_part = str_val.split(".")[1]
                assert decimal_part[6:] == "0000"

    def test_integer_fields_are_integers(self):
        """Integer fields remain integers, not floats."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        # Check integer fields
        assert isinstance(fp["path_geometry"]["jump_count"], int)
        assert isinstance(fp["quadrant_dynamics"]["q_runs_max"], int)

        for q in ["Q1", "Q2", "Q3", "Q4"]:
            assert isinstance(fp["quadrant_dynamics"]["q_counts"][q], int)

        for key in fp["quadrant_dynamics"]["q_transitions"]:
            assert isinstance(fp["quadrant_dynamics"]["q_transitions"][key], int)


class TestInputVariation:
    """Tests that different inputs produce different outputs."""

    def test_different_dates_different_ids(self):
        """Different dates produce different fingerprint IDs."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp1 = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        fp2 = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-13",  # Different date
            symbol="GBPUSD",
        )

        assert fp1["fingerprint_id"] != fp2["fingerprint_id"]
        assert fp1["content_hash"] != fp2["content_hash"]

    def test_different_symbols_different_ids(self):
        """Different symbols produce different fingerprint IDs."""
        trajectory_path = FIXTURES_DIR / "sample_trajectory.csv"
        points, symbol, date_ny = load_trajectory_csv(trajectory_path)
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "tests/fixtures/sample_trajectory.csv",
            "trajectory_png": "tests/fixtures/sample_trajectory.png",
        }

        fp1 = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        fp2 = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="EURUSD",  # Different symbol
        )

        assert fp1["fingerprint_id"] != fp2["fingerprint_id"]
        assert fp1["content_hash"] != fp2["content_hash"]

    def test_different_points_different_hash(self):
        """Different point values produce different content hash."""
        params = load_params()

        source_artifacts = {
            "trajectory_csv": "test.csv",
            "trajectory_png": "test.png",
        }

        points1 = [{"block": chr(65 + i), "x": 0.5, "y": 0.0} for i in range(12)]
        points2 = [{"block": chr(65 + i), "x": 0.5, "y": 0.0} for i in range(12)]
        points2[5]["x"] = 0.6  # Change one point

        fp1 = compute_fingerprint(
            points=points1,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        fp2 = compute_fingerprint(
            points=points2,
            params=params,
            source_artifacts=source_artifacts,
            date_ny="2022-12-12",
            symbol="GBPUSD",
        )

        assert fp1["content_hash"] != fp2["content_hash"]
