"""
Trajectory Families v0.1
========================
Path 1 (Observation & Cataloging Only)

A deterministic taxonomy pipeline for cataloging recurring "shapes of motion"
through the state-plane.
"""

from .fingerprint import (
    compute_fingerprint,
    compute_content_hash,
    compute_jump_count,
    compute_max_run_length,
    compute_net_displacement,
    compute_path_length,
    compute_quadrant_counts,
    compute_quadrant_entropy,
    compute_quadrant_sequence,
    compute_transition_counts,
    compute_turning,
    generate_fingerprint_id,
    get_dominant_quadrant,
    load_fingerprint_json,
    load_params,
    load_trajectory_csv,
    safe_mean,
    safe_std,
    write_fingerprint_json,
)
from .schema import (
    SCHEMA_VERSION,
    ValidationError,
    is_valid_fingerprint,
    validate_fingerprint,
)

__version__ = "0.1.0"
__all__ = [
    # Core computation
    "compute_fingerprint",
    "compute_content_hash",
    "compute_jump_count",
    "compute_max_run_length",
    "compute_net_displacement",
    "compute_path_length",
    "compute_quadrant_counts",
    "compute_quadrant_entropy",
    "compute_quadrant_sequence",
    "compute_transition_counts",
    "compute_turning",
    "generate_fingerprint_id",
    "get_dominant_quadrant",
    "safe_mean",
    "safe_std",
    # I/O
    "load_fingerprint_json",
    "load_params",
    "load_trajectory_csv",
    "write_fingerprint_json",
    # Schema
    "SCHEMA_VERSION",
    "ValidationError",
    "is_valid_fingerprint",
    "validate_fingerprint",
]
