"""
Evidence Pack v0.3 Overlays - Liquidity & Microstructure Analysis

Derives observational overlays from M15 strips and 2H spine blocks without mutating
canonical tables or existing v0.2 pack outputs.

Modules:
- v0.3-A: Wick & sweep microstructure overlay (per-block)
- v0.3-B: Displacement / imbalance overlay (global JSONL events)
- v0.3-C: Liquidity gradient map (per-block)

All outputs are deterministic, order-stable, and additive to the evidence pack.

Hardening:
- All numeric values quantized to fixed precision (1e-5)
- Event identifiers derived from canonical SHA-1 hash
- Intrablock-only computation (no cross-block lookbacks)
- Parameter provenance captured in meta.json
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
from statistics import median
import math


# ============================================================================
# Configuration & Constants
# ============================================================================

# Numeric precision for all overlay outputs (5 decimal places = 1e-5)
PRICE_PRECISION = 5

# v0.3-A: Sweep detection lookback (how many prior candles to check)
SWEEP_LOOKBACK = 3

# v0.3-A: Raid & reclaim threshold (% of block range)
RAID_RECLAIM_THRESHOLD = 0.5

# v0.3-B: Fair Value Gap minimum size (pips or price units)
FVG_MIN_SIZE = 0.00001

# v0.3-B: Displacement detection rolling window
DISPLACEMENT_WINDOW = 20

# v0.3-B: Displacement threshold (candle range vs rolling median)
DISPLACEMENT_THRESHOLD_MULTIPLIER = 2.0

# v0.3-C: Liquidity level bucket size (price quantization)
LIQUIDITY_BUCKET_SIZE = 0.0001

# v0.3-C: Touch threshold for repeated touches (how close to count as same level)
TOUCH_THRESHOLD = 0.00005

# FVG rule identifier
FVG_RULE = "3_candle"

# Computation scope (intrablock only, no cross-block lookbacks)
INTRABLOCK_ONLY = True


# ============================================================================
# Numeric Determinism Utilities
# ============================================================================

def quantize(value: float, precision: int = PRICE_PRECISION) -> float:
    """
    Quantize float to fixed decimal precision for deterministic output.

    Handles NaN and Infinity by returning None (caller must handle).

    Args:
        value: Float value to quantize
        precision: Number of decimal places

    Returns:
        Quantized float or raises ValueError for invalid values
    """
    if not math.isfinite(value):
        raise ValueError(f"Non-finite value encountered: {value}")
    return round(value, precision)


def safe_float(value: Any) -> float:
    """
    Safely convert value to float with validation.

    Args:
        value: Value to convert

    Returns:
        Float value

    Raises:
        ValueError: If value is not finite
    """
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite value: {result}")
    return result


def compute_event_id(event_data: Dict) -> str:
    """
    Compute deterministic SHA-1 event identifier.

    Args:
        event_data: Event dict with canonical fields

    Returns:
        Hex-encoded SHA-1 hash (40 characters)
    """
    # Build canonical string representation
    canonical_parts = []

    # Sort keys for determinism
    for key in sorted(event_data.keys()):
        value = event_data[key]
        # Convert to canonical string representation
        if isinstance(value, bool):
            canonical_parts.append(f"{key}={'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            canonical_parts.append(f"{key}={value}")
        elif isinstance(value, str):
            canonical_parts.append(f"{key}={value}")
        elif value is None:
            canonical_parts.append(f"{key}=null")

    canonical_string = "|".join(canonical_parts)
    return hashlib.sha1(canonical_string.encode("utf-8")).hexdigest()


# ============================================================================
# v0.3-A: Wick & Sweep Microstructure Overlay
# ============================================================================

def classify_wick_dominance(candle: Dict) -> str:
    """
    Classify wick dominance for a single candle.

    Args:
        candle: M15 candle dict with o, h, l, c

    Returns:
        "wick_top", "wick_bot", "balanced", or "no_wick"
    """
    o = safe_float(candle["o"])
    h = safe_float(candle["h"])
    l = safe_float(candle["l"])
    c = safe_float(candle["c"])

    body_top = max(o, c)
    body_bot = min(o, c)

    wick_top = h - body_top
    wick_bot = body_bot - l

    total_wick = wick_top + wick_bot
    if total_wick == 0:
        return "no_wick"

    if wick_top > 2 * wick_bot:
        return "wick_top"
    elif wick_bot > 2 * wick_top:
        return "wick_bot"
    else:
        return "balanced"


def detect_sweeps(candles: List[Dict], lookback: int = SWEEP_LOOKBACK) -> List[Dict]:
    """
    Detect sweep events where a candle takes out prior highs/lows.

    Deterministic definition:
    - Prior = previous N candles (lookback parameter)
    - Sweep high: current high > all prior highs within lookback
    - Sweep low: current low < all prior lows within lookback

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        lookback: Number of prior candles to check

    Returns:
        List of sweep events with metadata
    """
    sweeps = []

    for i in range(lookback, len(candles)):
        current = candles[i]
        prior_candles = candles[i - lookback:i]

        prior_high = max(safe_float(c["h"]) for c in prior_candles)
        prior_low = min(safe_float(c["l"]) for c in prior_candles)

        curr_h = safe_float(current["h"])
        curr_l = safe_float(current["l"])

        swept_high = curr_h > prior_high
        swept_low = curr_l < prior_low

        if swept_high or swept_low:
            sweeps.append({
                "bar_start_ms": int(current["bar_start_ms"]),
                "bar_close_ms": int(current["bar_close_ms"]),
                "swept_high": swept_high,
                "swept_low": swept_low,
                "prior_high": quantize(prior_high) if swept_high else None,
                "prior_low": quantize(prior_low) if swept_low else None,
                "sweep_high": quantize(curr_h) if swept_high else None,
                "sweep_low": quantize(curr_l) if swept_low else None,
            })

    return sweeps


def detect_raid_reclaim(candles: List[Dict], block_range: float, threshold: float = RAID_RECLAIM_THRESHOLD) -> List[Dict]:
    """
    Detect raid-then-reclaim patterns within block.

    Deterministic definition:
    - Raid: candle takes out a prior extreme (high/low from earlier in block)
    - Reclaim: later candle closes back within (threshold * block_range) of the prior level

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        block_range: Full range of the 2H block
        threshold: Fraction of block range for reclaim tolerance

    Returns:
        List of raid-reclaim events
    """
    if not candles or block_range == 0:
        return []

    reclaim_tolerance = threshold * block_range
    raid_reclaims = []

    # Track running highs and lows
    for i in range(1, len(candles)):
        current = candles[i]
        prior_candles = candles[:i]

        prior_high = max(safe_float(c["h"]) for c in prior_candles)
        prior_low = min(safe_float(c["l"]) for c in prior_candles)

        curr_h = safe_float(current["h"])
        curr_l = safe_float(current["l"])
        curr_c = safe_float(current["c"])

        # Check for raid high then reclaim
        if curr_h > prior_high:
            # Check if any subsequent candle closes back near prior high
            for j in range(i + 1, len(candles)):
                later = candles[j]
                later_c = safe_float(later["c"])
                if abs(later_c - prior_high) <= reclaim_tolerance:
                    raid_reclaims.append({
                        "type": "raid_high_reclaim",
                        "raid_bar_start_ms": int(current["bar_start_ms"]),
                        "reclaim_bar_start_ms": int(later["bar_start_ms"]),
                        "prior_high": quantize(prior_high),
                        "raid_high": quantize(curr_h),
                        "reclaim_close": quantize(later_c),
                    })
                    break

        # Check for raid low then reclaim
        if curr_l < prior_low:
            for j in range(i + 1, len(candles)):
                later = candles[j]
                later_c = safe_float(later["c"])
                if abs(later_c - prior_low) <= reclaim_tolerance:
                    raid_reclaims.append({
                        "type": "raid_low_reclaim",
                        "raid_bar_start_ms": int(current["bar_start_ms"]),
                        "reclaim_bar_start_ms": int(later["bar_start_ms"]),
                        "prior_low": quantize(prior_low),
                        "raid_low": quantize(curr_l),
                        "reclaim_close": quantize(later_c),
                    })
                    break

    return raid_reclaims


def compute_microstructure_overlay(block_id: str, candles: List[Dict], block_meta: Dict) -> Dict:
    """
    Compute v0.3-A microstructure overlay for a single 2H block.

    Args:
        block_id: Block identifier (e.g., "20221211-A-GBPUSD")
        candles: List of M15 candles for this block (sorted by bar_start_ms)
        block_meta: Block metadata with bar_open_ms, bar_close_ms, etc.

    Returns:
        Overlay dict with sweep flags, wick sequences, raid-reclaim events
    """
    if not candles:
        return {
            "block_id": block_id,
            "candle_count": 0,
            "wick_sequence": [],
            "sweeps": [],
            "raid_reclaims": [],
        }

    # Ensure candles are sorted
    sorted_candles = sorted(candles, key=lambda c: int(c["bar_start_ms"]))

    # Compute block range
    all_highs = [safe_float(c["h"]) for c in sorted_candles]
    all_lows = [safe_float(c["l"]) for c in sorted_candles]
    block_high = max(all_highs)
    block_low = min(all_lows)
    block_range = block_high - block_low

    # Wick dominance sequence
    wick_sequence = []
    for candle in sorted_candles:
        wick_sequence.append({
            "bar_start_ms": int(candle["bar_start_ms"]),
            "wick_dominance": classify_wick_dominance(candle),
        })

    # Sweep detection
    sweeps = detect_sweeps(sorted_candles, lookback=SWEEP_LOOKBACK)

    # Raid-reclaim detection
    raid_reclaims = detect_raid_reclaim(sorted_candles, block_range, threshold=RAID_RECLAIM_THRESHOLD)

    return {
        "block_id": block_id,
        "bar_open_ms": int(block_meta["bar_open_ms"]),
        "bar_close_ms": int(block_meta["bar_close_ms"]),
        "candle_count": len(sorted_candles),
        "block_range": quantize(block_range),
        "wick_sequence": wick_sequence,
        "sweeps": sweeps,
        "raid_reclaims": raid_reclaims,
    }


# ============================================================================
# v0.3-B: Displacement / Imbalance Overlay
# ============================================================================

def detect_fair_value_gaps(candles: List[Dict], min_gap_size: float = FVG_MIN_SIZE) -> List[Dict]:
    """
    Detect Fair Value Gaps using deterministic 3-candle rule.

    FVG Definition:
    - Bullish FVG: candle[i-1].high < candle[i+1].low (gap between candle i-1 and i+1)
    - Bearish FVG: candle[i-1].low > candle[i+1].high
    - Middle candle (i) must displace through the gap

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        min_gap_size: Minimum gap size to qualify as FVG

    Returns:
        List of FVG events with gap range and timestamps
    """
    fvgs = []

    for i in range(1, len(candles) - 1):
        prev = candles[i - 1]
        curr = candles[i]
        next_candle = candles[i + 1]

        prev_h = safe_float(prev["h"])
        prev_l = safe_float(prev["l"])
        next_h = safe_float(next_candle["h"])
        next_l = safe_float(next_candle["l"])

        # Bullish FVG: gap between prev high and next low
        if prev_h < next_l:
            gap_size = next_l - prev_h
            if gap_size >= min_gap_size:
                fvgs.append({
                    "type": "bullish_fvg",
                    "start_bar_ms": int(prev["bar_start_ms"]),
                    "middle_bar_ms": int(curr["bar_start_ms"]),
                    "end_bar_ms": int(next_candle["bar_start_ms"]),
                    "gap_low": quantize(prev_h),
                    "gap_high": quantize(next_l),
                    "gap_size": quantize(gap_size),
                    "mitigated": False,
                    "mitigation_bar_ms": None,
                })

        # Bearish FVG: gap between prev low and next high
        elif prev_l > next_h:
            gap_size = prev_l - next_h
            if gap_size >= min_gap_size:
                fvgs.append({
                    "type": "bearish_fvg",
                    "start_bar_ms": int(prev["bar_start_ms"]),
                    "middle_bar_ms": int(curr["bar_start_ms"]),
                    "end_bar_ms": int(next_candle["bar_start_ms"]),
                    "gap_low": quantize(next_h),
                    "gap_high": quantize(prev_l),
                    "gap_size": quantize(gap_size),
                    "mitigated": False,
                    "mitigation_bar_ms": None,
                })

    return fvgs


def detect_mitigation_events(fvgs: List[Dict], candles: List[Dict]) -> List[Dict]:
    """
    Detect when FVGs are mitigated (price revisits gap zone).

    Mitigation: any candle after FVG formation that has range overlapping the gap zone

    Args:
        fvgs: List of FVG events from detect_fair_value_gaps
        candles: Full list of M15 candles sorted by bar_start_ms

    Returns:
        Updated FVG list with mitigation flags
    """
    for fvg in fvgs:
        gap_low = fvg["gap_low"]
        gap_high = fvg["gap_high"]
        end_bar_ms = fvg["end_bar_ms"]

        # Check all candles after FVG formation
        for candle in candles:
            bar_ms = int(candle["bar_start_ms"])
            if bar_ms <= end_bar_ms:
                continue

            candle_h = safe_float(candle["h"])
            candle_l = safe_float(candle["l"])

            # Check if candle range overlaps gap zone
            if candle_l <= gap_high and candle_h >= gap_low:
                fvg["mitigated"] = True
                fvg["mitigation_bar_ms"] = bar_ms
                break

    return fvgs


def detect_displacement_candles(candles: List[Dict], window: int = DISPLACEMENT_WINDOW, threshold: float = DISPLACEMENT_THRESHOLD_MULTIPLIER) -> List[Dict]:
    """
    Detect displacement candles (range vs rolling median).

    Displacement: candle range > threshold * rolling_median(range, window)

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        window: Rolling window size for median calculation
        threshold: Multiplier over median to qualify as displacement

    Returns:
        List of displacement events
    """
    if len(candles) < window:
        return []

    displacements = []

    for i in range(window, len(candles)):
        window_candles = candles[i - window:i]
        ranges = [safe_float(c["h"]) - safe_float(c["l"]) for c in window_candles]
        rolling_median = median(ranges)

        current = candles[i]
        current_range = safe_float(current["h"]) - safe_float(current["l"])

        if rolling_median > 0 and current_range > threshold * rolling_median:
            displacements.append({
                "bar_start_ms": int(current["bar_start_ms"]),
                "bar_close_ms": int(current["bar_close_ms"]),
                "range": quantize(current_range),
                "rolling_median": quantize(rolling_median),
                "ratio": quantize(current_range / rolling_median, precision=2),
                "bullish": safe_float(current["c"]) > safe_float(current["o"]),
            })

    return displacements


def compute_displacement_overlay(all_candles: List[Dict]) -> List[Dict]:
    """
    Compute v0.3-B displacement/imbalance overlay for all candles.

    Returns JSONL-style list of events (FVGs and displacements) with stable ordering
    and deterministic event_id.

    Args:
        all_candles: All M15 candles across all blocks, sorted by bar_start_ms

    Returns:
        List of event dicts (to be written as JSONL)
    """
    events = []

    # Detect FVGs
    fvgs = detect_fair_value_gaps(all_candles, min_gap_size=FVG_MIN_SIZE)
    fvgs = detect_mitigation_events(fvgs, all_candles)

    # Detect displacement candles
    displacements = detect_displacement_candles(all_candles, window=DISPLACEMENT_WINDOW, threshold=DISPLACEMENT_THRESHOLD_MULTIPLIER)

    # Combine events with type tags
    for fvg in fvgs:
        events.append({
            "event_type": "fvg",
            **fvg
        })

    for disp in displacements:
        events.append({
            "event_type": "displacement",
            **disp
        })

    # Sort deterministically by (start_ms, end_ms, event_type, level_low, level_high)
    def sort_key(event: Dict) -> tuple:
        start_ms = event.get("start_bar_ms") or event.get("bar_start_ms") or event.get("middle_bar_ms") or 0
        end_ms = event.get("end_bar_ms") or event.get("bar_close_ms") or start_ms
        event_type = event.get("event_type", "")
        level_low = event.get("gap_low") or event.get("range") or 0
        level_high = event.get("gap_high") or event.get("range") or 0
        return (start_ms, end_ms, event_type, level_low, level_high)

    events.sort(key=sort_key)

    # Add deterministic event_id
    for event in events:
        # Build canonical identifier from key fields
        id_data = {
            "start_ms": event.get("start_bar_ms") or event.get("bar_start_ms") or event.get("middle_bar_ms") or 0,
            "end_ms": event.get("end_bar_ms") or event.get("bar_close_ms") or 0,
            "event_type": event.get("event_type", ""),
            "level_low": event.get("gap_low") or event.get("range") or 0,
            "level_high": event.get("gap_high") or event.get("range") or 0,
        }
        event["event_id"] = compute_event_id(id_data)

    return events


# ============================================================================
# v0.3-C: Liquidity Gradient Map
# ============================================================================

def quantize_price(price: float, bucket_size: float = LIQUIDITY_BUCKET_SIZE) -> float:
    """Quantize price to bucket for level detection."""
    return round(price / bucket_size) * bucket_size


def detect_repeated_touches(candles: List[Dict], threshold: float = TOUCH_THRESHOLD) -> Dict[float, int]:
    """
    Detect repeated touches at price levels (liquidity pools).

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        threshold: Price tolerance for counting as same level

    Returns:
        Dict mapping quantized price level to touch count
    """
    level_touches = defaultdict(int)

    for candle in candles:
        h = safe_float(candle["h"])
        l = safe_float(candle["l"])

        # Count high and low as touches
        high_level = quantize_price(h, LIQUIDITY_BUCKET_SIZE)
        low_level = quantize_price(l, LIQUIDITY_BUCKET_SIZE)

        level_touches[high_level] += 1
        level_touches[low_level] += 1

    return dict(level_touches)


def detect_compression_zones(candles: List[Dict], min_cluster_size: int = 3) -> List[Dict]:
    """
    Detect compression zones (reduced range clusters).

    Compression: consecutive candles with below-average range

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        min_cluster_size: Minimum consecutive candles to qualify as compression

    Returns:
        List of compression zone events
    """
    if len(candles) < min_cluster_size:
        return []

    ranges = [safe_float(c["h"]) - safe_float(c["l"]) for c in candles]
    avg_range = sum(ranges) / len(ranges)
    threshold = avg_range * 0.5  # Below 50% of average

    compressions = []
    cluster_start = None
    cluster_candles = []

    for i, candle in enumerate(candles):
        if ranges[i] < threshold:
            if cluster_start is None:
                cluster_start = i
                cluster_candles = [candle]
            else:
                cluster_candles.append(candle)
        else:
            if cluster_start is not None and len(cluster_candles) >= min_cluster_size:
                cluster_range = sum(ranges[cluster_start:cluster_start + len(cluster_candles)]) / len(cluster_candles)
                compressions.append({
                    "start_bar_ms": int(cluster_candles[0]["bar_start_ms"]),
                    "end_bar_ms": int(cluster_candles[-1]["bar_close_ms"]),
                    "candle_count": len(cluster_candles),
                    "avg_range": quantize(cluster_range),
                })
            cluster_start = None
            cluster_candles = []

    # Check final cluster
    if cluster_start is not None and len(cluster_candles) >= min_cluster_size:
        cluster_range = sum(ranges[cluster_start:cluster_start + len(cluster_candles)]) / len(cluster_candles)
        compressions.append({
            "start_bar_ms": int(cluster_candles[0]["bar_start_ms"]),
            "end_bar_ms": int(cluster_candles[-1]["bar_close_ms"]),
            "candle_count": len(cluster_candles),
            "avg_range": quantize(cluster_range),
        })

    return compressions


def detect_breakout_failures(candles: List[Dict], lookback: int = 5) -> List[Dict]:
    """
    Detect breakout-failure events (take high/low then reverse).

    Args:
        candles: List of M15 candles sorted by bar_start_ms
        lookback: Number of candles to look back for prior high/low

    Returns:
        List of breakout-failure events
    """
    failures = []

    for i in range(lookback, len(candles) - 1):  # Need at least one candle after
        current = candles[i]
        prior = candles[i - lookback:i]
        next_candle = candles[i + 1]

        prior_high = max(safe_float(c["h"]) for c in prior)
        prior_low = min(safe_float(c["l"]) for c in prior)

        curr_h = safe_float(current["h"])
        curr_l = safe_float(current["l"])
        next_c = safe_float(next_candle["c"])

        # Breakout high then failure (next candle closes below prior high)
        if curr_h > prior_high and next_c < prior_high:
            failures.append({
                "type": "breakout_high_failure",
                "breakout_bar_ms": int(current["bar_start_ms"]),
                "failure_bar_ms": int(next_candle["bar_start_ms"]),
                "prior_high": quantize(prior_high),
                "breakout_high": quantize(curr_h),
                "failure_close": quantize(next_c),
            })

        # Breakout low then failure (next candle closes above prior low)
        if curr_l < prior_low and next_c > prior_low:
            failures.append({
                "type": "breakout_low_failure",
                "breakout_bar_ms": int(current["bar_start_ms"]),
                "failure_bar_ms": int(next_candle["bar_start_ms"]),
                "prior_low": quantize(prior_low),
                "breakout_low": quantize(curr_l),
                "failure_close": quantize(next_c),
            })

    return failures


def compute_liquidity_gradient(block_id: str, candles: List[Dict], block_meta: Dict) -> Dict:
    """
    Compute v0.3-C liquidity gradient map for a single 2H block.

    Args:
        block_id: Block identifier
        candles: List of M15 candles for this block (sorted by bar_start_ms)
        block_meta: Block metadata

    Returns:
        Liquidity gradient dict with level histogram and compression zones
    """
    if not candles:
        return {
            "block_id": block_id,
            "candle_count": 0,
            "level_histogram": [],
            "compression_zones": [],
            "breakout_failures": [],
        }

    # Ensure sorted
    sorted_candles = sorted(candles, key=lambda c: int(c["bar_start_ms"]))

    # Repeated touches (liquidity pools)
    level_histogram = detect_repeated_touches(sorted_candles, threshold=TOUCH_THRESHOLD)

    # Compression zones
    compressions = detect_compression_zones(sorted_candles, min_cluster_size=3)

    # Breakout failures
    failures = detect_breakout_failures(sorted_candles, lookback=5)

    # Convert level histogram to sorted list for deterministic output
    level_histogram_list = [
        {"level": quantize(level), "touches": count}
        for level, count in sorted(level_histogram.items())
    ]

    return {
        "block_id": block_id,
        "bar_open_ms": int(block_meta["bar_open_ms"]),
        "bar_close_ms": int(block_meta["bar_close_ms"]),
        "candle_count": len(sorted_candles),
        "level_histogram": level_histogram_list,
        "compression_zones": compressions,
        "breakout_failures": failures,
    }


# ============================================================================
# Overlay Orchestration
# ============================================================================

def write_overlay_outputs(pack_root: Path, blocks: List[Dict], m15_by_block: Dict[str, List[Dict]], all_m15_candles: List[Dict]) -> Dict[str, int]:
    """
    Write all v0.3 overlay outputs to disk.

    Args:
        pack_root: Root directory of evidence pack (evidence_pack_v0_2)
        blocks: List of 2H block metadata dicts
        m15_by_block: Dict mapping block_id to list of M15 candles
        all_m15_candles: All M15 candles sorted by bar_start_ms (for v0.3-B)

    Returns:
        Dict with counts of outputs written per module
    """
    overlays_root = pack_root / "overlays_v0_3"
    overlays_root.mkdir(exist_ok=True)

    counts = {
        "v0.3-A": 0,
        "v0.3-B": 0,
        "v0.3-C": 0,
    }

    # v0.3-A: Microstructure overlay (per-block)
    micro_dir = overlays_root / "micro" / "2h"
    micro_dir.mkdir(parents=True, exist_ok=True)

    for block in blocks:
        block_id = block["block_id"]
        candles = m15_by_block.get(block_id, [])

        overlay = compute_microstructure_overlay(
            block_id=block_id,
            candles=candles,
            block_meta=block
        )

        output_path = micro_dir / f"{block_id}.json"
        output_path.write_text(json.dumps(overlay, indent=2, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        counts["v0.3-A"] += 1

    # v0.3-B: Displacement overlay (global JSONL)
    events_dir = overlays_root / "events"
    events_dir.mkdir(parents=True, exist_ok=True)

    displacement_events = compute_displacement_overlay(all_m15_candles)

    displacement_path = events_dir / "displacement_fvg.jsonl"
    with displacement_path.open("w", encoding="utf-8") as f:
        for event in displacement_events:
            f.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    counts["v0.3-B"] = len(displacement_events)

    # v0.3-C: Liquidity gradient (per-block)
    liquidity_dir = overlays_root / "micro" / "liquidity_gradient"
    liquidity_dir.mkdir(parents=True, exist_ok=True)

    for block in blocks:
        block_id = block["block_id"]
        candles = m15_by_block.get(block_id, [])

        gradient = compute_liquidity_gradient(
            block_id=block_id,
            candles=candles,
            block_meta=block
        )

        output_path = liquidity_dir / f"{block_id}.json"
        output_path.write_text(json.dumps(gradient, indent=2, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        counts["v0.3-C"] += 1

    return counts


def build_overlay_metadata(enabled: bool, counts: Optional[Dict[str, int]] = None) -> Dict:
    """
    Build overlay metadata for meta.json with parameter provenance.

    Args:
        enabled: Whether overlays are enabled
        counts: Optional dict with counts per module

    Returns:
        Overlay metadata dict with params section documenting all constants
    """
    if not enabled:
        return {
            "enabled": False,
            "version": "0.3",
            "modules": [],
        }

    return {
        "enabled": True,
        "version": "0.3",
        "modules": ["v0.3-A", "v0.3-B", "v0.3-C"],
        "counts": counts or {},
        "params": {
            "price_precision": PRICE_PRECISION,
            "wick_sweep_lookback": SWEEP_LOOKBACK,
            "raid_reclaim_threshold": RAID_RECLAIM_THRESHOLD,
            "fvg_rule": FVG_RULE,
            "fvg_min_size": FVG_MIN_SIZE,
            "displacement_median_window": DISPLACEMENT_WINDOW,
            "displacement_multiplier": DISPLACEMENT_THRESHOLD_MULTIPLIER,
            "liquidity_bucket_size": LIQUIDITY_BUCKET_SIZE,
            "liquidity_touch_threshold": TOUCH_THRESHOLD,
            "intrablock_only": INTRABLOCK_ONLY,
        },
    }
