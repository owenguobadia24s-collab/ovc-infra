# OVC Validation Package
"""
Package for validating OVC data layers (Option B.2).

Modules:
    validate_derived_range_v0_1: Validate L1/L2 derived feature packs

Usage:
    python -m validate.validate_derived_range_v0_1 \\
        --symbol GBPUSD \\
        --start-date 2026-01-13 \\
        --end-date 2026-01-17

Validation Checks:
    1. Coverage parity: count(B) == count(L1) == count(L2)
    2. Key uniqueness: no duplicate block_id in L1/L2
    3. Null/invalid checks: no NaN/Inf, deterministic nulls
    4. Window_spec enforcement: L2 has required window specs
    5. Determinism quickcheck: recompute sample and verify
    6. TV comparison (optional): compare against TradingView reference

Artifacts:
    - derived_validation_report.json
    - derived_validation_report.md
    - derived_validation_diffs.csv (if --compare-tv)

See docs/option_b2_runbook.md for full documentation.
"""

from .validate_derived_range_v0_1 import (
    ValidationResult,
    check_coverage_parity,
    check_duplicates,
    check_null_rates,
    check_window_spec,
    determinism_quickcheck,
    compute_l1_inline,
    values_match,
    build_run_id,
)

__all__ = [
    "ValidationResult",
    "check_coverage_parity",
    "check_duplicates",
    "check_null_rates",
    "check_window_spec",
    "determinism_quickcheck",
    "compute_l1_inline",
    "values_match",
    "build_run_id",
]
