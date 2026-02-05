#!/usr/bin/env python3
"""
Phase 2.2 — Registry Schema Validator v0.1

Validates that registry artifacts conform to their declared schemas.

Inputs:
    <run_folder>  — path to a run folder
    [--schema <schema_file>]  — optional explicit schema path

Detection logic:
    If no --schema is given, auto-detects the registry type from files present:
      - RUN_REGISTRY_v0_1.jsonl  → REGISTRY_run_registry_v0_1.schema.json
      - OPERATION_STATUS_TABLE_v0_1.json → REGISTRY_op_status_table_v0_1.schema.json
        (if top-level is an array, uses REGISTRY_op_status_table_v0_1.array.schema.json)
      - DRIFT_SIGNALS_v0_1.json  → REGISTRY_drift_signals_v0_1.schema.json

Checks:
    1. Registry artifact file exists
    2. Schema file exists (bundled or explicit)
    3. Required fields present in each record
    4. Field types match declared types
    5. Enum values are within declared enums
    6. Tri-state fields preserve null semantics (null ≠ absent)

Failure conditions:
    SCHEMA_INVALID: <reason>

Exit code:
    0 = PASS
    1 = FAIL (with details on stderr)

Hard constraints:
    - Read-only: does not modify any file.
    - Stdlib only: no third-party dependencies.
    - Deterministic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# Registry artifact → schema file mapping
REGISTRY_MAP = {
    "RUN_REGISTRY_v0_1.jsonl": {
        "registry_id": "run_registry",
        "schema": "REGISTRY_run_registry_v0_1.schema.json",
    },
    "OPERATION_STATUS_TABLE_v0_1.json": {
        "registry_id": "op_status_table",
        "schema": "REGISTRY_op_status_table_v0_1.schema.json",
        "schema_array": "REGISTRY_op_status_table_v0_1.array.schema.json",
    },
    "DRIFT_SIGNALS_v0_1.json": {
        "registry_id": "drift_signals",
        "schema": "REGISTRY_drift_signals_v0_1.schema.json",
    },
}

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"


def load_schema(schema_path: Path) -> dict:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def check_type(value: Any, type_spec: Any) -> bool:
    """Check if value matches a JSON Schema type spec (string or array of strings)."""
    if isinstance(type_spec, str):
        types = [type_spec]
    elif isinstance(type_spec, list):
        types = type_spec
    else:
        return True  # cannot validate complex type specs with stdlib

    for t in types:
        if t == "string" and isinstance(value, str):
            return True
        if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if t == "boolean" and isinstance(value, bool):
            return True
        if t == "null" and value is None:
            return True
        if t == "array" and isinstance(value, list):
            return True
        if t == "object" and isinstance(value, dict):
            return True
    return False


def validate_record(record: dict, schema: dict, path_prefix: str = "") -> list[str]:
    """Validate a single record against a schema. Returns list of errors."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # Check required fields
    for field in required:
        if field not in record:
            errors.append(f"SCHEMA_INVALID: {path_prefix}missing required field '{field}'")

    # Check field types
    for field, value in record.items():
        if field in properties:
            prop = properties[field]
            type_spec = prop.get("type")
            if type_spec and not check_type(value, type_spec):
                errors.append(
                    f"SCHEMA_INVALID: {path_prefix}field '{field}' has type "
                    f"{type(value).__name__}, expected {type_spec}"
                )
            # Check enum
            enum_values = prop.get("enum")
            if enum_values is not None and value not in enum_values:
                errors.append(
                    f"SCHEMA_INVALID: {path_prefix}field '{field}' value "
                    f"{value!r} not in enum {enum_values}"
                )
            # Check const
            const_value = prop.get("const")
            if const_value is not None and value != const_value:
                errors.append(
                    f"SCHEMA_INVALID: {path_prefix}field '{field}' value "
                    f"{value!r} does not match const {const_value!r}"
                )

    return errors


def validate_jsonl(artifact_path: Path, schema: dict) -> list[str]:
    """Validate a JSONL file line by line."""
    errors: list[str] = []
    with open(artifact_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"SCHEMA_INVALID: line {i} JSON parse error: {exc}")
                continue
            errors.extend(validate_record(record, schema, path_prefix=f"line {i}: "))
    return errors


def validate_json_array(artifact_path: Path, schema: dict) -> list[str]:
    """Validate a JSON array file (each element against schema)."""
    errors: list[str] = []
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        errors.append("SCHEMA_INVALID: expected JSON array at top level")
        return errors
    # Schema for array items would be the schema itself (items schema)
    item_schema = schema.get("items", schema)
    for i, record in enumerate(data):
        errors.extend(validate_record(record, item_schema, path_prefix=f"[{i}]: "))
    return errors


def validate_json_object(artifact_path: Path, schema: dict) -> list[str]:
    """Validate a JSON object file."""
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ["SCHEMA_INVALID: expected JSON object at top level"]
    return validate_record(data, schema)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Registry Schema Validator v0.1")
    parser.add_argument("run_folder", type=Path, help="Path to run folder")
    parser.add_argument("--schema", type=Path, default=None, help="Explicit schema file")
    args = parser.parse_args()

    run_folder: Path = args.run_folder
    if not run_folder.is_dir():
        print(f"ERROR: {run_folder} is not a directory", file=sys.stderr)
        return 1

    # Auto-detect registry type
    detected = None
    registry_id = None
    schema_name = None
    schema_array_name = None
    for artifact_name, meta in REGISTRY_MAP.items():
        if (run_folder / artifact_name).exists():
            detected = artifact_name
            registry_id = meta.get("registry_id")
            schema_name = meta.get("schema")
            schema_array_name = meta.get("schema_array")
            break

    if detected is None and args.schema is None:
        print("ERROR: Could not auto-detect registry type. Use --schema.", file=sys.stderr)
        return 1

    artifact_name = detected or ""
    artifact_path = run_folder / artifact_name

    if args.schema:
        schema_path = args.schema
    elif registry_id == "op_status_table" and schema_array_name:
        try:
            root = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"ERROR: {artifact_path} parse error: {exc}", file=sys.stderr)
            return 1
        if isinstance(root, list):
            schema_path = SCHEMA_DIR / schema_array_name
        else:
            schema_path = SCHEMA_DIR / schema_name
    else:
        schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        print(f"ERROR: Schema not found: {schema_path}", file=sys.stderr)
        return 1

    schema = load_schema(schema_path)

    # Validate based on file type
    if artifact_name.endswith(".jsonl"):
        errors = validate_jsonl(artifact_path, schema)
    elif artifact_name.endswith(".json"):
        # Determine if array or object from schema type
        if schema.get("type") == "array" or (
            isinstance(schema.get("type"), list) and "array" in schema["type"]
        ):
            errors = validate_json_array(artifact_path, schema)
        else:
            errors = validate_json_object(artifact_path, schema)
    else:
        errors = [f"SCHEMA_INVALID: unsupported artifact format: {artifact_name}"]

    if errors:
        print(f"FAIL: {len(errors)} schema violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    else:
        print(f"PASS: {artifact_path.name} conforms to schema.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
