"""
DayFingerprint v0.1 Core Computation
====================================
Path 1 (Observation & Cataloging Only)

This module computes DayFingerprint v0.1 from trajectory data.
All computations follow the frozen spec exactly.
"""

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .schema import SCHEMA_VERSION, validate_fingerprint

# Constants from spec (Appendix A)
BLOCK_COUNT = 12
NUMERIC_PRECISION = 6
BLOCK_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


def load_params(params_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load frozen parameters from JSON file."""
    if params_path is None:
        params_path = Path(__file__).parent / "params_v0_1.json"
    with open(params_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_trajectory_csv(csv_path: Path) -> Tuple[List[Dict], str, str]:
    """
    Load trajectory data from CSV.

    Returns:
        (points, symbol, date_ny) tuple where points is list of dicts with
        keys: block, x, y, quadrant_id
    """
    points = []
    symbol = None
    date_ny = None

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            block = row.get("block2h", "").strip()
            block_id = row.get("block_id", "").strip()

            # Extract symbol and date from block_id (format: YYYYMMDD-X-SYMBOL)
            if block_id and symbol is None:
                parts = block_id.split("-")
                if len(parts) >= 3:
                    date_str = parts[0]
                    symbol = parts[2]
                    # Convert YYYYMMDD to YYYY-MM-DD
                    if len(date_str) == 8:
                        date_ny = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

            x_str = row.get("x_energy", "").strip()
            y_str = row.get("y_shift", "").strip()

            x = float(x_str) if x_str else None
            y = float(y_str) if y_str else None

            points.append({
                "block": block,
                "x": x,
                "y": y,
                "quadrant_id": row.get("quadrant_id", "").strip() or None,
            })

    return points, symbol, date_ny


def compute_quadrant_sequence(
    x_vals: List[Optional[float]],
    y_vals: List[Optional[float]],
    E_hi: float,
    S_hi: float,
) -> List[Optional[str]]:
    """
    Assign quadrant labels to each point.

    Q1 (Expansion):    x >= E_hi AND |y| <= S_hi
    Q2 (Consolidation): x <  E_hi AND |y| <= S_hi
    Q3 (Reversal):     x >= E_hi AND |y| >  S_hi
    Q4 (Retracement):  x <  E_hi AND |y| >  S_hi
    NULL: When x or y is null/missing
    """
    quadrants = []
    for x, y in zip(x_vals, y_vals):
        if x is None or y is None:
            quadrants.append(None)
            continue

        high_energy = x >= E_hi
        low_shift = abs(y) <= S_hi

        if high_energy and low_shift:
            quadrants.append("Q1")
        elif not high_energy and low_shift:
            quadrants.append("Q2")
        elif high_energy and not low_shift:
            quadrants.append("Q3")
        else:  # not high_energy and not low_shift
            quadrants.append("Q4")

    return quadrants


def compute_quadrant_counts(quadrants: List[Optional[str]]) -> Dict[str, int]:
    """Count time spent in each quadrant."""
    counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for q in quadrants:
        if q in counts:
            counts[q] += 1
    return counts


def compute_transition_counts(quadrants: List[Optional[str]]) -> Dict[str, int]:
    """
    Count transitions between quadrants.

    Returns dict with keys like "Q1_Q1", "Q1_Q2", etc.
    Only counts transitions between non-null quadrants.
    """
    # Initialize all 16 possible transitions to 0
    transitions = {}
    for q_from in ["Q1", "Q2", "Q3", "Q4"]:
        for q_to in ["Q1", "Q2", "Q3", "Q4"]:
            transitions[f"{q_from}_{q_to}"] = 0

    # Count transitions
    for i in range(len(quadrants) - 1):
        q_from = quadrants[i]
        q_to = quadrants[i + 1]
        if q_from is not None and q_to is not None:
            transitions[f"{q_from}_{q_to}"] += 1

    return transitions


def compute_quadrant_entropy(q_counts: Dict[str, int], precision: int) -> float:
    """
    Compute Shannon entropy of quadrant distribution (log base 2).

    Returns value in [0, 2] where 2 = uniform distribution.
    """
    total = sum(q_counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in q_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return round(entropy, precision)


def compute_max_run_length(quadrants: List[Optional[str]]) -> int:
    """
    Compute longest consecutive run in same quadrant.

    Returns at least 1 if any quadrant is non-null.
    """
    if not quadrants:
        return 1

    max_run = 0
    current_run = 0
    current_q = None

    for q in quadrants:
        if q is None:
            # Reset run on null
            if current_run > max_run:
                max_run = current_run
            current_run = 0
            current_q = None
        elif q == current_q:
            current_run += 1
        else:
            if current_run > max_run:
                max_run = current_run
            current_run = 1
            current_q = q

    # Check final run
    if current_run > max_run:
        max_run = current_run

    # Minimum of 1 per spec
    return max(1, max_run)


def safe_mean(values: List[Optional[float]]) -> float:
    """Compute mean of non-null, finite values. Returns 0.0 if no valid values."""
    valid = [v for v in values if v is not None and math.isfinite(v)]
    if not valid:
        return 0.0
    return sum(valid) / len(valid)


def safe_std(values: List[Optional[float]]) -> float:
    """Compute std dev of non-null, finite values. Returns 0.0 if insufficient values."""
    valid = [v for v in values if v is not None and math.isfinite(v)]
    if len(valid) < 2:
        return 0.0
    mean = sum(valid) / len(valid)
    variance = sum((v - mean) ** 2 for v in valid) / len(valid)
    return math.sqrt(variance)


def compute_path_length(
    x_vals: List[Optional[float]],
    y_vals: List[Optional[float]],
    precision: int,
) -> float:
    """
    Compute path length: sum of Euclidean distances between consecutive valid points.

    path_length = Σ ||p_t - p_{t-1}|| for t=B..L
    """
    path_length = 0.0
    prev_point = None

    for x, y in zip(x_vals, y_vals):
        if x is None or y is None:
            prev_point = None
            continue

        current = (x, y)
        if prev_point is not None:
            dx = current[0] - prev_point[0]
            dy = current[1] - prev_point[1]
            path_length += math.sqrt(dx * dx + dy * dy)
        prev_point = current

    return round(path_length, precision)


def compute_net_displacement(
    x_vals: List[Optional[float]],
    y_vals: List[Optional[float]],
    precision: int,
) -> float:
    """
    Compute net displacement: ||p_L - p_A|| (start to end distance).

    Uses first and last valid points.
    """
    first_point = None
    last_point = None

    for x, y in zip(x_vals, y_vals):
        if x is not None and y is not None:
            if first_point is None:
                first_point = (x, y)
            last_point = (x, y)

    if first_point is None or last_point is None:
        return 0.0

    dx = last_point[0] - first_point[0]
    dy = last_point[1] - first_point[1]
    return round(math.sqrt(dx * dx + dy * dy), precision)


def compute_turning(
    x_vals: List[Optional[float]],
    y_vals: List[Optional[float]],
    precision: int,
) -> float:
    """
    Compute total turning angle in radians.

    turning = Σ |angle(v_{t-1}, v_t)| for consecutive valid vectors.
    """
    # Build list of valid points
    valid_points = []
    for x, y in zip(x_vals, y_vals):
        if x is not None and y is not None:
            valid_points.append((x, y))

    if len(valid_points) < 3:
        return 0.0

    total_turning = 0.0

    for i in range(1, len(valid_points) - 1):
        p0 = valid_points[i - 1]
        p1 = valid_points[i]
        p2 = valid_points[i + 1]

        # Vector from p0 to p1
        v1x = p1[0] - p0[0]
        v1y = p1[1] - p0[1]

        # Vector from p1 to p2
        v2x = p2[0] - p1[0]
        v2y = p2[1] - p1[1]

        # Magnitudes
        mag1 = math.sqrt(v1x * v1x + v1y * v1y)
        mag2 = math.sqrt(v2x * v2x + v2y * v2y)

        if mag1 < 1e-10 or mag2 < 1e-10:
            continue

        # Dot product for angle
        dot = v1x * v2x + v1y * v2y
        cos_angle = dot / (mag1 * mag2)

        # Clamp to [-1, 1] to handle floating point errors
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle = math.acos(cos_angle)
        total_turning += abs(angle)

    return round(total_turning, precision)


def compute_jump_count(y_vals: List[Optional[float]], y_jump_threshold: float) -> int:
    """
    Count jumps where |Δy| > y_jump_threshold.

    Only counts between consecutive valid y values.
    """
    count = 0
    prev_y = None

    for y in y_vals:
        if y is None:
            prev_y = None
            continue

        if prev_y is not None:
            delta = abs(y - prev_y)
            if delta > y_jump_threshold:
                count += 1
        prev_y = y

    return count


def generate_fingerprint_id(symbol: str, date_ny: str, content_for_hash: str) -> str:
    """
    Generate unique fingerprint ID: fp_{SYMBOL}_{YYYYMMDD}_{hash8}

    The hash8 is derived from the content to ensure uniqueness.
    """
    date_compact = date_ny.replace("-", "")
    hash_full = hashlib.sha256(content_for_hash.encode("utf-8")).hexdigest()
    hash8 = hash_full[:8]
    return f"fp_{symbol}_{date_compact}_{hash8}"


def compute_content_hash(fingerprint: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of canonical fingerprint content.

    Excludes: generated_at, content_hash (to avoid circular dependency)
    """
    # Create copy without excluded fields
    hashable = {k: v for k, v in fingerprint.items() if k not in ("generated_at", "content_hash")}

    # Canonical JSON serialization
    canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_fingerprint(
    points: List[Dict[str, Any]],
    params: Dict[str, Any],
    source_artifacts: Dict[str, str],
    date_ny: str,
    symbol: str,
) -> Dict[str, Any]:
    """
    Compute DayFingerprint v0.1 from trajectory data.

    Args:
        points: List of 12 dicts with keys 'block', 'x', 'y'
        params: Parameter dict with fingerprint settings
        source_artifacts: Paths to source files
        date_ny: Session date (YYYY-MM-DD)
        symbol: Currency pair (e.g., GBPUSD)

    Returns:
        Dict conforming to DayFingerprint v0.1 schema

    Raises:
        ValueError: If input validation fails
    """
    fp_params = params.get("fingerprint", params)
    precision = fp_params.get("numeric_precision", NUMERIC_PRECISION)
    E_hi = fp_params["E_hi"]
    S_hi = fp_params["S_hi"]
    y_jump_thr = fp_params["y_jump_threshold"]

    # Validate input
    if len(points) != BLOCK_COUNT:
        raise ValueError(f"Expected {BLOCK_COUNT} points, got {len(points)}")

    # Check for NaN values (hard fail per spec)
    for i, p in enumerate(points):
        x, y = p.get("x"), p.get("y")
        if x is not None and not math.isfinite(x):
            raise ValueError(f"NaN/Inf x value at point {i}")
        if y is not None and not math.isfinite(y):
            raise ValueError(f"NaN/Inf y value at point {i}")

    # Extract coordinates
    x_vals = [p.get("x") for p in points]
    y_vals = [p.get("y") for p in points]

    # Compute quadrants
    quadrants = compute_quadrant_sequence(x_vals, y_vals, E_hi, S_hi)
    quadrant_string = " ".join(q if q else "NULL" for q in quadrants)

    # Compute path geometry
    path_length = compute_path_length(x_vals, y_vals, precision)
    net_displacement = compute_net_displacement(x_vals, y_vals, precision)
    efficiency = round(net_displacement / path_length, precision) if path_length > 0 else 0.0
    turning = compute_turning(x_vals, y_vals, precision)
    jump_count = compute_jump_count(y_vals, y_jump_thr)

    energy_mean = round(safe_mean(x_vals), precision)
    energy_std = round(safe_std(x_vals), precision)
    shift_mean = round(safe_mean(y_vals), precision)
    shift_std = round(safe_std(y_vals), precision)

    # Compute quadrant dynamics
    q_counts = compute_quadrant_counts(quadrants)
    q_transitions = compute_transition_counts(quadrants)
    q_entropy = compute_quadrant_entropy(q_counts, precision)
    q_runs_max = compute_max_run_length(quadrants)

    # Build points array with rounded values
    rounded_points = []
    for p in points:
        rounded_points.append({
            "block": p["block"],
            "x": round(p["x"], precision) if p.get("x") is not None else None,
            "y": round(p["y"], precision) if p.get("y") is not None else None,
        })

    # Build fingerprint (without ID and hash yet)
    fingerprint = {
        "schema_version": SCHEMA_VERSION,
        "fingerprint_id": "",  # Placeholder
        "date_ny": date_ny,
        "symbol": symbol,
        "timezone": "America/New_York",
        "block_labels": BLOCK_LABELS.copy(),
        "points": rounded_points,
        "quadrants": quadrants,
        "quadrant_string": quadrant_string,
        "path_geometry": {
            "path_length": path_length,
            "net_displacement": net_displacement,
            "efficiency": efficiency,
            "turning": turning,
            "jump_count": jump_count,
            "energy_mean": energy_mean,
            "energy_std": energy_std,
            "shift_mean": shift_mean,
            "shift_std": shift_std,
        },
        "quadrant_dynamics": {
            "q_counts": q_counts,
            "q_transitions": q_transitions,
            "q_entropy": q_entropy,
            "q_runs_max": q_runs_max,
        },
        "source_artifacts": source_artifacts,
        "params": {
            "state_plane_version": fp_params.get("state_plane_version", "v0.2"),
            "threshold_pack": fp_params.get("threshold_pack", "state_plane_v0_2_default_v1"),
            "E_hi": E_hi,
            "S_hi": S_hi,
            "y_jump_threshold": y_jump_thr,
            "numeric_precision": precision,
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Generate fingerprint ID using preliminary content
    preliminary_content = json.dumps(
        {k: v for k, v in fingerprint.items() if k not in ("fingerprint_id", "generated_at")},
        sort_keys=True,
        separators=(",", ":"),
    )
    fingerprint["fingerprint_id"] = generate_fingerprint_id(symbol, date_ny, preliminary_content)

    # Compute content hash (excludes generated_at and content_hash)
    fingerprint["content_hash"] = compute_content_hash(fingerprint)

    return fingerprint


def write_fingerprint_json(fingerprint: Dict[str, Any], output_path: Path) -> None:
    """
    Write fingerprint to JSON file with canonical formatting.

    Uses sort_keys=True and indent=2 as per spec.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Canonical JSON serialization per spec
    content = json.dumps(fingerprint, sort_keys=True, indent=2, separators=(",", ": "))
    output_path.write_text(content + "\n", encoding="utf-8")


def load_fingerprint_json(json_path: Path) -> Dict[str, Any]:
    """Load fingerprint from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_dominant_quadrant(quadrants: List[Optional[str]]) -> Optional[str]:
    """Get the most frequent quadrant (mode)."""
    counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for q in quadrants:
        if q in counts:
            counts[q] += 1

    if max(counts.values()) == 0:
        return None

    # Return first max in sorted order for determinism
    max_count = max(counts.values())
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        if counts[q] == max_count:
            return q
    return None
