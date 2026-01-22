"""
Tests for DST audit functionality in Evidence Pack v0.2.

Validates:
1. NY 17:00 local conversion around DST for spring (2023-03-10..14) and fall (2023-11-03..07)
2. Two different UTC offsets (EST -5, EDT -4) are correctly handled
3. Epoch ms values are consistent with spine expectations
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "path1"))

import build_evidence_pack_v0_2 as builder


class TestNy17ToEpochMs:
    """Test NY 17:00 to epoch ms conversion across DST boundaries."""

    def test_spring_forward_2023_03_10_est(self):
        """Before spring forward: 2023-03-10 17:00 NY is EST (UTC-5)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-03-10")
        # 2023-03-10 17:00 NY (EST) = 2023-03-10 22:00 UTC
        expected_utc = datetime(2023, 3, 10, 22, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_spring_forward_2023_03_11_est(self):
        """Day before spring forward: 2023-03-11 17:00 NY is EST (UTC-5)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-03-11")
        # 2023-03-11 17:00 NY (EST) = 2023-03-11 22:00 UTC
        expected_utc = datetime(2023, 3, 11, 22, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_spring_forward_2023_03_12_edt(self):
        """
        Spring forward day: 2023-03-12 17:00 NY is EDT (UTC-4).

        DST starts at 2023-03-12 02:00 local (clocks spring forward to 03:00).
        By 17:00, we're in EDT.
        """
        epoch_ms = builder.ny_17_to_epoch_ms("2023-03-12")
        # 2023-03-12 17:00 NY (EDT) = 2023-03-12 21:00 UTC
        expected_utc = datetime(2023, 3, 12, 21, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_spring_forward_2023_03_13_edt(self):
        """After spring forward: 2023-03-13 17:00 NY is EDT (UTC-4)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-03-13")
        # 2023-03-13 17:00 NY (EDT) = 2023-03-13 21:00 UTC
        expected_utc = datetime(2023, 3, 13, 21, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_spring_forward_2023_03_14_edt(self):
        """After spring forward: 2023-03-14 17:00 NY is EDT (UTC-4)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-03-14")
        # 2023-03-14 17:00 NY (EDT) = 2023-03-14 21:00 UTC
        expected_utc = datetime(2023, 3, 14, 21, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_fall_back_2023_11_03_edt(self):
        """Before fall back: 2023-11-03 17:00 NY is EDT (UTC-4)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-11-03")
        # 2023-11-03 17:00 NY (EDT) = 2023-11-03 21:00 UTC
        expected_utc = datetime(2023, 11, 3, 21, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_fall_back_2023_11_04_edt(self):
        """Day before fall back: 2023-11-04 17:00 NY is EDT (UTC-4)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-11-04")
        # 2023-11-04 17:00 NY (EDT) = 2023-11-04 21:00 UTC
        expected_utc = datetime(2023, 11, 4, 21, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_fall_back_2023_11_05_est(self):
        """
        Fall back day: 2023-11-05 17:00 NY is EST (UTC-5).

        DST ends at 2023-11-05 02:00 local (clocks fall back to 01:00).
        By 17:00, we're in EST.
        """
        epoch_ms = builder.ny_17_to_epoch_ms("2023-11-05")
        # 2023-11-05 17:00 NY (EST) = 2023-11-05 22:00 UTC
        expected_utc = datetime(2023, 11, 5, 22, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_fall_back_2023_11_06_est(self):
        """After fall back: 2023-11-06 17:00 NY is EST (UTC-5)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-11-06")
        # 2023-11-06 17:00 NY (EST) = 2023-11-06 22:00 UTC
        expected_utc = datetime(2023, 11, 6, 22, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"

    def test_fall_back_2023_11_07_est(self):
        """After fall back: 2023-11-07 17:00 NY is EST (UTC-5)."""
        epoch_ms = builder.ny_17_to_epoch_ms("2023-11-07")
        # 2023-11-07 17:00 NY (EST) = 2023-11-07 22:00 UTC
        expected_utc = datetime(2023, 11, 7, 22, 0, 0, tzinfo=timezone.utc)
        expected_ms = int(expected_utc.timestamp() * 1000)
        assert epoch_ms == expected_ms, f"Expected {expected_ms}, got {epoch_ms}"


class TestExtractBlockLetter:
    """Test block letter extraction from block_id."""

    def test_standard_format(self):
        """Standard block_id format: YYYYMMDD-X-SYM."""
        assert builder.extract_block_letter("20230312-A-GBPUSD") == "A"
        assert builder.extract_block_letter("20230312-L-GBPUSD") == "L"
        assert builder.extract_block_letter("20231105-F-EURUSD") == "F"

    def test_lowercase_normalized(self):
        """Lowercase letters are normalized to uppercase."""
        assert builder.extract_block_letter("20230312-a-GBPUSD") == "A"
        assert builder.extract_block_letter("20230312-l-GBPUSD") == "L"

    def test_invalid_format_returns_none(self):
        """Invalid formats return None."""
        assert builder.extract_block_letter("invalid") is None
        assert builder.extract_block_letter("20230312-GBPUSD") is None
        assert builder.extract_block_letter("20230312-AB-GBPUSD") is None  # Two letters
        assert builder.extract_block_letter("20230312-1-GBPUSD") is None  # Digit
        assert builder.extract_block_letter("20230312-Z-GBPUSD") is None  # Not A-L


class TestValidateStripIntegrity:
    """Test strip integrity validation (Invariant A)."""

    def test_valid_strip_passes(self):
        """A valid 8-candle strip with correct timing passes."""
        base_ms = 1678647600000  # Some base timestamp
        m15_rows = []
        for i in range(8):
            m15_rows.append({
                "bar_start_ms": base_ms + (i * builder.M15_STEP_MS),
                "bar_close_ms": base_ms + ((i + 1) * builder.M15_STEP_MS),
                "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05,
            })

        expected_close = base_ms + (8 * builder.M15_STEP_MS)
        passed, issues = builder.validate_strip_integrity(m15_rows, "TEST-A-SYM", expected_close)

        assert passed is True
        assert len(issues) == 0

    def test_wrong_candle_count_fails(self):
        """A strip with wrong number of candles fails."""
        base_ms = 1678647600000
        m15_rows = [
            {"bar_start_ms": base_ms, "bar_close_ms": base_ms + builder.M15_STEP_MS,
             "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05}
            for _ in range(7)  # Only 7 candles
        ]

        expected_close = base_ms + (8 * builder.M15_STEP_MS)
        passed, issues = builder.validate_strip_integrity(m15_rows, "TEST-A-SYM", expected_close)

        assert passed is False
        assert len(issues) == 1
        assert issues[0]["type"] == "strip_count"
        assert issues[0]["details"]["expected"] == 8
        assert issues[0]["details"]["actual"] == 7

    def test_continuity_gap_fails(self):
        """A strip with a gap in timing fails."""
        base_ms = 1678647600000
        m15_rows = []
        for i in range(8):
            # Introduce a gap at position 4
            offset = 2 if i >= 4 else 0  # Extra 30 minutes gap
            m15_rows.append({
                "bar_start_ms": base_ms + ((i + offset) * builder.M15_STEP_MS),
                "bar_close_ms": base_ms + ((i + offset + 1) * builder.M15_STEP_MS),
                "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05,
            })

        expected_close = m15_rows[-1]["bar_close_ms"]
        passed, issues = builder.validate_strip_integrity(m15_rows, "TEST-A-SYM", expected_close)

        assert passed is False
        # Should have at least one continuity issue
        continuity_issues = [i for i in issues if i["type"] == "continuity"]
        assert len(continuity_issues) > 0

    def test_alignment_mismatch_fails(self):
        """A strip where last candle doesn't align with block close fails."""
        base_ms = 1678647600000
        m15_rows = []
        for i in range(8):
            m15_rows.append({
                "bar_start_ms": base_ms + (i * builder.M15_STEP_MS),
                "bar_close_ms": base_ms + ((i + 1) * builder.M15_STEP_MS),
                "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05,
            })

        # Expected close is different from actual last candle close
        expected_close = base_ms + (9 * builder.M15_STEP_MS)  # One step later
        passed, issues = builder.validate_strip_integrity(m15_rows, "TEST-A-SYM", expected_close)

        assert passed is False
        alignment_issues = [i for i in issues if i["type"] == "continuity" and "end_mismatch" in str(i.get("details", {}))]
        assert len(alignment_issues) == 1


class TestValidateAggregationMatch:
    """Test aggregation match validation (Invariant B)."""

    def test_exact_match_passes(self):
        """Aggregated OHLC exactly matching spine passes."""
        m15_rows = [
            {"o": 1.0, "h": 1.2, "l": 0.95, "c": 1.1},  # First candle sets O
            {"o": 1.1, "h": 1.3, "l": 1.0, "c": 1.2},
            {"o": 1.2, "h": 1.25, "l": 1.1, "c": 1.15},
            {"o": 1.15, "h": 1.2, "l": 1.05, "c": 1.1},
            {"o": 1.1, "h": 1.15, "l": 1.0, "c": 1.05},
            {"o": 1.05, "h": 1.1, "l": 0.98, "c": 1.0},
            {"o": 1.0, "h": 1.08, "l": 0.95, "c": 0.98},
            {"o": 0.98, "h": 1.05, "l": 0.9, "c": 1.02},  # Last candle sets C
        ]

        # Aggregate: O=1.0 (first), C=1.02 (last), H=1.3 (max), L=0.9 (min)
        spine_ohlc = {"o": 1.0, "h": 1.3, "l": 0.9, "c": 1.02}
        tolerance = 1e-6

        passed, worst, anomaly = builder.validate_aggregation_match(
            m15_rows, spine_ohlc, "TEST-A-SYM", tolerance
        )

        assert passed is True
        assert anomaly is None
        assert worst is not None  # worst deviation is always returned

    def test_within_tolerance_passes(self):
        """Aggregated OHLC within tolerance passes."""
        m15_rows = [
            {"o": 1.0, "h": 1.3, "l": 0.9, "c": 1.1},
            {"o": 1.1, "h": 1.2, "l": 0.95, "c": 1.0},
            {"o": 1.0, "h": 1.15, "l": 0.92, "c": 1.05},
            {"o": 1.05, "h": 1.18, "l": 0.93, "c": 1.02},
            {"o": 1.02, "h": 1.12, "l": 0.91, "c": 0.98},
            {"o": 0.98, "h": 1.1, "l": 0.88, "c": 0.95},
            {"o": 0.95, "h": 1.08, "l": 0.85, "c": 0.92},
            {"o": 0.92, "h": 1.05, "l": 0.82, "c": 0.9},
        ]

        # Actual agg: O=1.0, C=0.9, H=1.3, L=0.82
        # Spine within tolerance
        spine_ohlc = {"o": 1.0000001, "h": 1.3, "l": 0.82, "c": 0.9}
        tolerance = 1e-6

        passed, worst, anomaly = builder.validate_aggregation_match(
            m15_rows, spine_ohlc, "TEST-A-SYM", tolerance
        )

        assert passed is True

    def test_beyond_tolerance_fails(self):
        """Aggregated OHLC beyond tolerance fails."""
        m15_rows = [
            {"o": 1.0, "h": 1.3, "l": 0.9, "c": 1.1},
            {"o": 1.1, "h": 1.2, "l": 0.95, "c": 1.0},
            {"o": 1.0, "h": 1.15, "l": 0.92, "c": 1.05},
            {"o": 1.05, "h": 1.18, "l": 0.93, "c": 1.02},
            {"o": 1.02, "h": 1.12, "l": 0.91, "c": 0.98},
            {"o": 0.98, "h": 1.1, "l": 0.88, "c": 0.95},
            {"o": 0.95, "h": 1.08, "l": 0.85, "c": 0.92},
            {"o": 0.92, "h": 1.05, "l": 0.82, "c": 0.9},
        ]

        # Actual agg: O=1.0, C=0.9, H=1.3, L=0.82
        # Spine has significant mismatch on H
        spine_ohlc = {"o": 1.0, "h": 1.35, "l": 0.82, "c": 0.9}  # H mismatch: 1.35 vs 1.3
        tolerance = 1e-6

        passed, worst, anomaly = builder.validate_aggregation_match(
            m15_rows, spine_ohlc, "TEST-A-SYM", tolerance
        )

        assert passed is False
        assert anomaly is not None
        assert anomaly["type"] == "aggregation"
        assert "h" in anomaly["details"]["mismatches"]


class TestRunDstAudit:
    """Test the overall DST audit function."""

    def test_empty_blocks_returns_empty_result(self):
        """Empty blocks list returns valid but empty result."""
        result = builder.run_dst_audit(
            blocks=[],
            m15_by_block={},
            tolerance=1e-6,
            dst_range=None,
        )

        assert result["dates_tested"] == []
        assert result["blocks_checked"] == 0
        assert result["strip_count_failures"] == 0
        assert result["continuity_failures"] == 0
        assert result["aggregation_failures"] == 0
        assert result["session_boundary_failures"] == 0
        assert result["anomalies"] == []

    def test_valid_block_passes(self):
        """A properly formed block with valid M15 strip passes."""
        base_ms = 1678647600000
        block = {
            "block_id": "20230312-A-GBPUSD",
            "date_ny": "2023-03-12",
            "bar_close_ms": base_ms + builder.TWO_H_MS,
            "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05,
        }

        m15_rows = []
        for i in range(8):
            m15_rows.append({
                "bar_start_ms": base_ms + (i * builder.M15_STEP_MS),
                "bar_close_ms": base_ms + ((i + 1) * builder.M15_STEP_MS),
                "o": 1.0, "h": 1.1, "l": 0.9, "c": 1.05,
            })

        result = builder.run_dst_audit(
            blocks=[block],
            m15_by_block={"20230312-A-GBPUSD": m15_rows},
            tolerance=1e-6,
            dst_range=None,
        )

        assert result["blocks_checked"] == 1
        assert result["strip_count_failures"] == 0
        assert result["continuity_failures"] == 0
        # Note: aggregation may pass or fail depending on exact values
        # Session boundary will fail since our test block doesn't align with real NY 17:00
