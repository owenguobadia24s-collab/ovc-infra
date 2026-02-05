"""
Pipeline Step 7: Validate Report

Validates the built report against the JSON schema using jsonschema library (Draft-07).
On validation failure, report MUST NOT be emitted.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

import jsonschema
from jsonschema import Draft7Validator


@dataclass
class ValidationResult:
    """Result of report validation."""
    is_valid: bool
    errors: List[str]


def load_schema(schema_path: Path) -> tuple[Optional[Dict[str, Any]], List[str]]:
    """Load the JSON schema."""
    errors = []

    if not schema_path.exists():
        errors.append(f"SCHEMA_NOT_FOUND: {schema_path}")
        return None, errors

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        return schema, []
    except json.JSONDecodeError as e:
        errors.append(f"SCHEMA_PARSE_ERROR: {e}")
        return None, errors


def validate_report_semantics(report: Dict[str, Any]) -> List[str]:
    """
    Validate report semantic correctness beyond schema validation.

    - Failure count matches actual failures
    - Warning count matches actual warnings
    """
    errors = []

    # Validate failure count
    failures = report.get("failures", [])
    summary = report.get("interpretation_summary", {})

    actual_failure_count = len(failures)
    reported_failure_count = summary.get("failure_count", 0)
    if actual_failure_count != reported_failure_count:
        errors.append(f"failure_count mismatch: reported {reported_failure_count}, actual {actual_failure_count}")

    # Validate warning count
    actual_warning_count = sum(1 for f in failures if f.get("severity") == "WARNING")
    reported_warning_count = summary.get("warning_count", 0)
    if actual_warning_count != reported_warning_count:
        errors.append(f"warning_count mismatch: reported {reported_warning_count}, actual {actual_warning_count}")

    return errors


def validate_report(report: Dict[str, Any], schema_path: Path) -> ValidationResult:
    """
    Main entry point: Validate report against schema and semantics.

    Uses jsonschema library with Draft-07 for full schema validation
    including $defs and $ref support.

    On validation failure, report MUST NOT be emitted.
    """
    errors = []

    # Load schema
    schema, _load_errors = load_schema(schema_path)

    if schema is None:
        # Cannot validate without schema - fail closed
        return ValidationResult(
            is_valid=False,
            errors=["VALIDATION_FAILED: Schema could not be loaded"]
        )

    # JSON Schema validation using Draft-07
    try:
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema)
        schema_errors = list(validator.iter_errors(report))

        for error in schema_errors:
            # Build a human-readable path
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            errors.append(f"SCHEMA_VIOLATION at {path}: {error.message}")

    except jsonschema.exceptions.SchemaError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"INVALID_SCHEMA: {e.message}"]
        )

    # Semantic validation (only if schema validation passed)
    if not errors:
        semantic_errors = validate_report_semantics(report)
        errors.extend(semantic_errors)

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors)
