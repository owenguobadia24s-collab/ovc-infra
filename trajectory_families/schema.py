"""
DayFingerprint v0.1 Schema Definition and Validation
=====================================================
Path 1 (Observation & Cataloging Only)
"""

import re
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "day_fingerprint_v0.1"

# Regex patterns from spec
FINGERPRINT_ID_PATTERN = re.compile(r"^fp_[A-Z]{6}_[0-9]{8}_[a-f0-9]{8}$")
SYMBOL_PATTERN = re.compile(r"^[A-Z]{6}$")
BLOCK_PATTERN = re.compile(r"^[A-L]$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
QUADRANT_STRING_PATTERN = re.compile(r"^(Q[1-4]|NULL)( (Q[1-4]|NULL)){11}$")
CONTENT_HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")

VALID_QUADRANTS = {"Q1", "Q2", "Q3", "Q4", None}
REQUIRED_BLOCK_LABELS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


class ValidationError(Exception):
    """Raised when fingerprint validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_fingerprint(fp: Dict[str, Any]) -> List[str]:
    """
    Validate a DayFingerprint v0.1 dictionary against the schema.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Required top-level fields
    required_fields = [
        "schema_version",
        "fingerprint_id",
        "date_ny",
        "symbol",
        "timezone",
        "block_labels",
        "points",
        "quadrants",
        "quadrant_string",
        "path_geometry",
        "quadrant_dynamics",
        "source_artifacts",
        "params",
        "generated_at",
    ]

    for field in required_fields:
        if field not in fp:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors  # Stop early if missing required fields

    # schema_version
    if fp["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be '{SCHEMA_VERSION}', got '{fp['schema_version']}'")

    # fingerprint_id
    if not FINGERPRINT_ID_PATTERN.match(fp["fingerprint_id"]):
        errors.append(f"fingerprint_id does not match pattern: {fp['fingerprint_id']}")

    # date_ny
    if not DATE_PATTERN.match(fp["date_ny"]):
        errors.append(f"date_ny must be YYYY-MM-DD: {fp['date_ny']}")

    # symbol
    if not SYMBOL_PATTERN.match(fp["symbol"]):
        errors.append(f"symbol must be 6 uppercase letters: {fp['symbol']}")

    # timezone
    if fp["timezone"] != "America/New_York":
        errors.append(f"timezone must be 'America/New_York': {fp['timezone']}")

    # block_labels
    if fp["block_labels"] != REQUIRED_BLOCK_LABELS:
        errors.append(f"block_labels must be {REQUIRED_BLOCK_LABELS}")

    # points
    errors.extend(_validate_points(fp["points"]))

    # quadrants
    errors.extend(_validate_quadrants(fp["quadrants"]))

    # quadrant_string
    if not QUADRANT_STRING_PATTERN.match(fp["quadrant_string"]):
        errors.append(f"quadrant_string does not match pattern: {fp['quadrant_string']}")

    # path_geometry
    errors.extend(_validate_path_geometry(fp["path_geometry"]))

    # quadrant_dynamics
    errors.extend(_validate_quadrant_dynamics(fp["quadrant_dynamics"]))

    # source_artifacts
    errors.extend(_validate_source_artifacts(fp["source_artifacts"]))

    # params
    errors.extend(_validate_params(fp["params"]))

    # content_hash (optional but validated if present)
    if "content_hash" in fp:
        if not CONTENT_HASH_PATTERN.match(fp["content_hash"]):
            errors.append(f"content_hash does not match SHA-256 pattern: {fp['content_hash']}")

    return errors


def _validate_points(points: Any) -> List[str]:
    """Validate the points array."""
    errors = []

    if not isinstance(points, list):
        return ["points must be a list"]

    if len(points) != 12:
        errors.append(f"points must have exactly 12 items, got {len(points)}")
        return errors

    for i, p in enumerate(points):
        if not isinstance(p, dict):
            errors.append(f"points[{i}] must be a dict")
            continue

        if "block" not in p:
            errors.append(f"points[{i}] missing 'block'")
        elif not BLOCK_PATTERN.match(str(p["block"])):
            errors.append(f"points[{i}].block must be A-L: {p['block']}")

        if "x" not in p:
            errors.append(f"points[{i}] missing 'x'")
        elif p["x"] is not None:
            if not isinstance(p["x"], (int, float)):
                errors.append(f"points[{i}].x must be number or null")
            elif not (0 <= p["x"] <= 1):
                errors.append(f"points[{i}].x must be in [0, 1]: {p['x']}")

        if "y" not in p:
            errors.append(f"points[{i}] missing 'y'")
        elif p["y"] is not None:
            if not isinstance(p["y"], (int, float)):
                errors.append(f"points[{i}].y must be number or null")
            elif not (-1 <= p["y"] <= 1):
                errors.append(f"points[{i}].y must be in [-1, 1]: {p['y']}")

    return errors


def _validate_quadrants(quadrants: Any) -> List[str]:
    """Validate the quadrants array."""
    errors = []

    if not isinstance(quadrants, list):
        return ["quadrants must be a list"]

    if len(quadrants) != 12:
        errors.append(f"quadrants must have exactly 12 items, got {len(quadrants)}")
        return errors

    for i, q in enumerate(quadrants):
        if q not in VALID_QUADRANTS:
            errors.append(f"quadrants[{i}] must be Q1-Q4 or null: {q}")

    return errors


def _validate_path_geometry(pg: Any) -> List[str]:
    """Validate path_geometry object."""
    errors = []

    if not isinstance(pg, dict):
        return ["path_geometry must be a dict"]

    required = [
        "path_length",
        "net_displacement",
        "efficiency",
        "turning",
        "jump_count",
        "energy_mean",
        "energy_std",
        "shift_mean",
        "shift_std",
    ]

    for field in required:
        if field not in pg:
            errors.append(f"path_geometry.{field} is required")

    if "path_length" in pg and pg["path_length"] is not None:
        if not isinstance(pg["path_length"], (int, float)) or pg["path_length"] < 0:
            errors.append("path_geometry.path_length must be >= 0")

    if "net_displacement" in pg and pg["net_displacement"] is not None:
        if not isinstance(pg["net_displacement"], (int, float)) or pg["net_displacement"] < 0:
            errors.append("path_geometry.net_displacement must be >= 0")

    if "efficiency" in pg and pg["efficiency"] is not None:
        if not isinstance(pg["efficiency"], (int, float)) or not (0 <= pg["efficiency"] <= 1):
            errors.append("path_geometry.efficiency must be in [0, 1]")

    if "turning" in pg and pg["turning"] is not None:
        if not isinstance(pg["turning"], (int, float)) or pg["turning"] < 0:
            errors.append("path_geometry.turning must be >= 0")

    if "jump_count" in pg:
        if not isinstance(pg["jump_count"], int) or not (0 <= pg["jump_count"] <= 11):
            errors.append("path_geometry.jump_count must be integer in [0, 11]")

    if "energy_mean" in pg and pg["energy_mean"] is not None:
        if not isinstance(pg["energy_mean"], (int, float)) or not (0 <= pg["energy_mean"] <= 1):
            errors.append("path_geometry.energy_mean must be in [0, 1]")

    if "energy_std" in pg and pg["energy_std"] is not None:
        if not isinstance(pg["energy_std"], (int, float)) or pg["energy_std"] < 0:
            errors.append("path_geometry.energy_std must be >= 0")

    if "shift_mean" in pg and pg["shift_mean"] is not None:
        if not isinstance(pg["shift_mean"], (int, float)) or not (-1 <= pg["shift_mean"] <= 1):
            errors.append("path_geometry.shift_mean must be in [-1, 1]")

    if "shift_std" in pg and pg["shift_std"] is not None:
        if not isinstance(pg["shift_std"], (int, float)) or pg["shift_std"] < 0:
            errors.append("path_geometry.shift_std must be >= 0")

    return errors


def _validate_quadrant_dynamics(qd: Any) -> List[str]:
    """Validate quadrant_dynamics object."""
    errors = []

    if not isinstance(qd, dict):
        return ["quadrant_dynamics must be a dict"]

    required = ["q_counts", "q_transitions", "q_entropy", "q_runs_max"]

    for field in required:
        if field not in qd:
            errors.append(f"quadrant_dynamics.{field} is required")

    # q_counts
    if "q_counts" in qd:
        qc = qd["q_counts"]
        if not isinstance(qc, dict):
            errors.append("quadrant_dynamics.q_counts must be a dict")
        else:
            for q in ["Q1", "Q2", "Q3", "Q4"]:
                if q not in qc:
                    errors.append(f"quadrant_dynamics.q_counts.{q} is required")
                elif not isinstance(qc[q], int) or not (0 <= qc[q] <= 12):
                    errors.append(f"quadrant_dynamics.q_counts.{q} must be integer in [0, 12]")

    # q_transitions
    if "q_transitions" in qd:
        qt = qd["q_transitions"]
        if not isinstance(qt, dict):
            errors.append("quadrant_dynamics.q_transitions must be a dict")
        else:
            expected_keys = {f"Q{i}_Q{j}" for i in range(1, 5) for j in range(1, 5)}
            for key in qt:
                if key not in expected_keys:
                    errors.append(f"quadrant_dynamics.q_transitions has invalid key: {key}")
                elif not isinstance(qt[key], int) or qt[key] < 0:
                    errors.append(f"quadrant_dynamics.q_transitions.{key} must be non-negative integer")

    # q_entropy
    if "q_entropy" in qd:
        if not isinstance(qd["q_entropy"], (int, float)) or not (0 <= qd["q_entropy"] <= 2):
            errors.append("quadrant_dynamics.q_entropy must be in [0, 2]")

    # q_runs_max
    if "q_runs_max" in qd:
        if not isinstance(qd["q_runs_max"], int) or not (1 <= qd["q_runs_max"] <= 12):
            errors.append("quadrant_dynamics.q_runs_max must be integer in [1, 12]")

    return errors


def _validate_source_artifacts(sa: Any) -> List[str]:
    """Validate source_artifacts object."""
    errors = []

    if not isinstance(sa, dict):
        return ["source_artifacts must be a dict"]

    required = ["trajectory_csv", "trajectory_png"]
    for field in required:
        if field not in sa:
            errors.append(f"source_artifacts.{field} is required")
        elif not isinstance(sa[field], str):
            errors.append(f"source_artifacts.{field} must be a string")

    return errors


def _validate_params(params: Any) -> List[str]:
    """Validate params object."""
    errors = []

    if not isinstance(params, dict):
        return ["params must be a dict"]

    required = [
        "state_plane_version",
        "threshold_pack",
        "E_hi",
        "S_hi",
        "y_jump_threshold",
        "numeric_precision",
    ]

    for field in required:
        if field not in params:
            errors.append(f"params.{field} is required")

    if "E_hi" in params:
        if not isinstance(params["E_hi"], (int, float)):
            errors.append("params.E_hi must be a number")

    if "S_hi" in params:
        if not isinstance(params["S_hi"], (int, float)):
            errors.append("params.S_hi must be a number")

    if "y_jump_threshold" in params:
        if not isinstance(params["y_jump_threshold"], (int, float)):
            errors.append("params.y_jump_threshold must be a number")

    if "numeric_precision" in params:
        if not isinstance(params["numeric_precision"], int):
            errors.append("params.numeric_precision must be an integer")

    return errors


def is_valid_fingerprint(fp: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check if a fingerprint is valid.

    Returns (is_valid, errors) tuple.
    """
    errors = validate_fingerprint(fp)
    return len(errors) == 0, errors
