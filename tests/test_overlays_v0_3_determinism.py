"""
Test suite for Evidence Pack v0.3 Overlay determinism and stability.

Tests use synthetic, in-memory M15 candle fixtures only.
No database access required.

Requirements:
- Bit-identical output across runs
- Stable sweep detection
- Deterministic FVG generation and mitigation
- Displacement threshold stability
- Liquidity gradient stability
"""

import json
import hashlib
from typing import Dict, List

# Import overlay module (handle both direct and package imports)
try:
    from scripts.path1 import overlays_v0_3
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "path1"))
    import overlays_v0_3


# ============================================================================
# Synthetic Fixtures
# ============================================================================

def make_candle(bar_start_ms: int, o: float, h: float, l: float, c: float) -> Dict:
    """Create a synthetic M15 candle."""
    return {
        "bar_start_ms": bar_start_ms,
        "bar_close_ms": bar_start_ms + (15 * 60 * 1000),  # M15 = 15 minutes
        "o": o,
        "h": h,
        "l": l,
        "c": c,
        "volume": 1000,
    }


def fixture_sweep_case() -> List[Dict]:
    """
    Fixture for sweep detection test.

    Candle 3 barely exceeds prior high by 1 tick (0.00001).
    """
    base_ms = 1670000000000
    return [
        make_candle(base_ms + 0, 1.2100, 1.2110, 1.2095, 1.2105),
        make_candle(base_ms + 900000, 1.2105, 1.2115, 1.2100, 1.2110),
        make_candle(base_ms + 1800000, 1.2110, 1.2120, 1.2105, 1.2115),
        # This candle sweeps the high by 1 tick
        make_candle(base_ms + 2700000, 1.2115, 1.21201, 1.2110, 1.2118),
    ]


def fixture_fvg_case() -> List[Dict]:
    """
    Fixture for FVG generation and mitigation.

    Creates a bullish FVG between candles 0 and 2.
    Candle 4 mitigates the gap.
    """
    base_ms = 1670000000000
    return [
        # Candle 0: high = 1.2100
        make_candle(base_ms + 0, 1.2095, 1.2100, 1.2090, 1.2098),
        # Candle 1: displacement candle (middle of FVG)
        make_candle(base_ms + 900000, 1.2098, 1.2130, 1.2098, 1.2128),
        # Candle 2: low = 1.2125 (creates gap from 1.2100 to 1.2125)
        make_candle(base_ms + 1800000, 1.2128, 1.2135, 1.2125, 1.2130),
        # Candle 3: no overlap with gap
        make_candle(base_ms + 2700000, 1.2130, 1.2140, 1.2128, 1.2135),
        # Candle 4: revisits gap (low = 1.2110 overlaps gap)
        make_candle(base_ms + 3600000, 1.2135, 1.2135, 1.2110, 1.2115),
    ]


def fixture_displacement_case() -> List[Dict]:
    """
    Fixture for displacement threshold stability.

    First 20 candles have median range ~0.0010.
    Candle 20 has range 0.0021 (exceeds 2.0x threshold).
    """
    base_ms = 1670000000000
    candles = []

    # First 20 candles with stable range around 0.0010
    for i in range(20):
        candles.append(make_candle(
            base_ms + i * 900000,
            1.2100 + i * 0.0001,
            1.2100 + i * 0.0001 + 0.0010,
            1.2100 + i * 0.0001,
            1.2100 + i * 0.0001 + 0.0005,
        ))

    # Candle 20: displacement (range = 0.0021, ratio = 2.1x)
    candles.append(make_candle(
        base_ms + 20 * 900000,
        1.2120,
        1.2141,
        1.2120,
        1.2140,
    ))

    return candles


def fixture_liquidity_gradient_case() -> List[Dict]:
    """
    Fixture for liquidity gradient stability.

    Multiple touches at 1.2100 and 1.2150 levels.
    """
    base_ms = 1670000000000
    return [
        # Touches at 1.2100 (low)
        make_candle(base_ms + 0, 1.2105, 1.2110, 1.2100, 1.2108),
        make_candle(base_ms + 900000, 1.2108, 1.2115, 1.2100, 1.2112),
        make_candle(base_ms + 1800000, 1.2112, 1.2118, 1.2100, 1.2115),

        # Touches at 1.2150 (high)
        make_candle(base_ms + 2700000, 1.2145, 1.2150, 1.2140, 1.2148),
        make_candle(base_ms + 3600000, 1.2148, 1.2150, 1.2143, 1.2146),
        make_candle(base_ms + 4500000, 1.2146, 1.2150, 1.2142, 1.2145),
    ]


def fixture_block_meta() -> Dict:
    """Fixture for block metadata."""
    return {
        "block_id": "test-block",
        "bar_open_ms": 1670000000000,
        "bar_close_ms": 1670007200000,  # 2H later
    }


# ============================================================================
# Test A — Bit-identical output
# ============================================================================

def test_bit_identical_output():
    """
    Test that running overlay computation twice produces identical results.
    """
    candles = fixture_fvg_case()
    block_meta = fixture_block_meta()

    # Run v0.3-A twice
    result1 = overlays_v0_3.compute_microstructure_overlay(
        block_id="test-block",
        candles=candles,
        block_meta=block_meta
    )
    result2 = overlays_v0_3.compute_microstructure_overlay(
        block_id="test-block",
        candles=candles,
        block_meta=block_meta
    )

    # Serialize and compare
    json1 = json.dumps(result1, sort_keys=True, separators=(",", ":"))
    json2 = json.dumps(result2, sort_keys=True, separators=(",", ":"))

    assert json1 == json2, "v0.3-A output is not bit-identical"

    # Verify SHA-256 hash is identical
    hash1 = hashlib.sha256(json1.encode("utf-8")).hexdigest()
    hash2 = hashlib.sha256(json2.encode("utf-8")).hexdigest()

    assert hash1 == hash2, "v0.3-A SHA-256 hashes do not match"

    # Run v0.3-C twice
    gradient1 = overlays_v0_3.compute_liquidity_gradient(
        block_id="test-block",
        candles=candles,
        block_meta=block_meta
    )
    gradient2 = overlays_v0_3.compute_liquidity_gradient(
        block_id="test-block",
        candles=candles,
        block_meta=block_meta
    )

    json_grad1 = json.dumps(gradient1, sort_keys=True, separators=(",", ":"))
    json_grad2 = json.dumps(gradient2, sort_keys=True, separators=(",", ":"))

    assert json_grad1 == json_grad2, "v0.3-C output is not bit-identical"

    print("PASS: Test A - Bit-identical output")


# ============================================================================
# Test B — Sweep determinism
# ============================================================================

def test_sweep_determinism():
    """
    Test that sweep detection is deterministic and stable.

    - Fixture where candle i barely exceeds prior high by 1 tick
    - Assert sweep=true
    - Reduce that tick by 1 unit
    - Assert sweep=false
    """
    candles_with_sweep = fixture_sweep_case()

    # Detect sweeps (should find one)
    sweeps = overlays_v0_3.detect_sweeps(candles_with_sweep, lookback=3)
    assert len(sweeps) == 1, f"Expected 1 sweep, got {len(sweeps)}"
    assert sweeps[0]["swept_high"] is True, "Expected swept_high=True"

    # Now reduce the high by 1 tick (should eliminate sweep)
    candles_without_sweep = candles_with_sweep.copy()
    candles_without_sweep[3] = make_candle(
        candles_with_sweep[3]["bar_start_ms"],
        candles_with_sweep[3]["o"],
        1.2120,  # Reduced from 1.21201 to 1.2120 (equal to prior high)
        candles_with_sweep[3]["l"],
        candles_with_sweep[3]["c"],
    )

    sweeps_no_trigger = overlays_v0_3.detect_sweeps(candles_without_sweep, lookback=3)
    assert len(sweeps_no_trigger) == 0, f"Expected 0 sweeps after reduction, got {len(sweeps_no_trigger)}"

    print("PASS: Test B - Sweep determinism")


# ============================================================================
# Test C — FVG generation and mitigation
# ============================================================================

def test_fvg_generation_and_mitigation():
    """
    Test FVG detection and mitigation tracking.

    - Fixture with known 3-candle FVG
    - Later candle revisits the gap
    - Assert exactly one FVG event emitted
    - Assert mitigation recorded exactly once
    """
    candles = fixture_fvg_case()

    # Detect FVGs
    fvgs = overlays_v0_3.detect_fair_value_gaps(candles, min_gap_size=0.00001)
    assert len(fvgs) == 1, f"Expected 1 FVG, got {len(fvgs)}"

    fvg = fvgs[0]
    assert fvg["type"] == "bullish_fvg", "Expected bullish FVG"
    assert fvg["gap_low"] == 1.21000, f"Expected gap_low=1.21000, got {fvg['gap_low']}"
    assert fvg["gap_high"] == 1.21250, f"Expected gap_high=1.21250, got {fvg['gap_high']}"

    # Detect mitigation
    fvgs_mitigated = overlays_v0_3.detect_mitigation_events(fvgs, candles)
    assert len(fvgs_mitigated) == 1, "Expected 1 FVG after mitigation check"
    assert fvgs_mitigated[0]["mitigated"] is True, "Expected FVG to be mitigated"
    assert fvgs_mitigated[0]["mitigation_bar_ms"] is not None, "Expected mitigation timestamp"

    print("PASS: Test C - FVG generation and mitigation")


# ============================================================================
# Test D — Displacement threshold stability
# ============================================================================

def test_displacement_threshold_stability():
    """
    Test displacement detection threshold stability.

    - Fixture with known rolling median
    - Assert displacement triggers only when range >= multiplier * median
    """
    candles = fixture_displacement_case()

    # Detect displacements
    displacements = overlays_v0_3.detect_displacement_candles(
        candles,
        window=20,
        threshold=2.0
    )

    assert len(displacements) == 1, f"Expected 1 displacement, got {len(displacements)}"

    disp = displacements[0]
    assert disp["range"] > disp["rolling_median"] * 2.0, "Displacement range should exceed 2x median"
    assert disp["ratio"] >= 2.0, f"Expected ratio >= 2.0, got {disp['ratio']}"

    # Verify no displacement detected with higher threshold
    displacements_strict = overlays_v0_3.detect_displacement_candles(
        candles,
        window=20,
        threshold=2.5
    )

    assert len(displacements_strict) == 0, "Expected 0 displacements with threshold=2.5"

    print("PASS: Test D - Displacement threshold stability")


# ============================================================================
# Test E — Liquidity gradient stability
# ============================================================================

def test_liquidity_gradient_stability():
    """
    Test liquidity gradient histogram stability.

    - Fixture with repeated touches at same rounded price level
    - Assert histogram bins and counts are deterministic
    """
    candles = fixture_liquidity_gradient_case()
    block_meta = fixture_block_meta()

    # Compute liquidity gradient
    gradient = overlays_v0_3.compute_liquidity_gradient(
        block_id="test-block",
        candles=candles,
        block_meta=block_meta
    )

    level_histogram = gradient["level_histogram"]

    # Verify histogram structure
    assert isinstance(level_histogram, list), "level_histogram should be a list"
    assert len(level_histogram) > 0, "level_histogram should not be empty"

    # Find 1.2100 level (should have 3 touches from lows)
    level_1_2100 = [entry for entry in level_histogram if entry["level"] == 1.21000]
    assert len(level_1_2100) == 1, f"Expected 1 entry for 1.21000, got {len(level_1_2100)}"
    assert level_1_2100[0]["touches"] == 3, f"Expected 3 touches at 1.21000, got {level_1_2100[0]['touches']}"

    # Find 1.2150 level (should have 3 touches from highs)
    level_1_2150 = [entry for entry in level_histogram if entry["level"] == 1.21500]
    assert len(level_1_2150) == 1, f"Expected 1 entry for 1.21500, got {len(level_1_2150)}"
    assert level_1_2150[0]["touches"] == 3, f"Expected 3 touches at 1.21500, got {level_1_2150[0]['touches']}"

    # Verify sorting
    levels = [entry["level"] for entry in level_histogram]
    assert levels == sorted(levels), "level_histogram should be sorted by level"

    print("PASS: Test E - Liquidity gradient stability")


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all determinism tests."""
    print("Running v0.3 overlay determinism tests...")
    print("=" * 70)

    test_bit_identical_output()
    test_sweep_determinism()
    test_fvg_generation_and_mitigation()
    test_displacement_threshold_stability()
    test_liquidity_gradient_stability()

    print("=" * 70)
    print("All tests passed!")


if __name__ == "__main__":
    run_all_tests()
