import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from tools.parse_export import parse_export_string


_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+(\.\d+)?$")


def load_contract(contract_path: str) -> Dict:
    path = Path(contract_path)
    if not path.is_file():
        raise FileNotFoundError(f"contract not found: {contract_path}")
    with path.open("r", encoding="utf-8") as handle:
        contract = json.load(handle)
    if "fields" not in contract:
        raise ValueError(f"missing fields in contract: {contract_path}")
    return contract


def _ordered_fields(contract: Dict) -> List[Dict]:
    fields = contract.get("fields", [])
    return sorted(fields, key=lambda field: field.get("order", 0))


def _expected_keys(fields: List[Dict]) -> List[str]:
    return [field["key"] for field in fields]


def _check_type(value: str, field: Dict) -> Tuple[bool, str]:
    field_type = field.get("type", "string")

    if field_type == "string":
        if value == "":
            return False, "expected non-empty string"
        return True, ""
    if field_type == "string_or_empty":
        return True, ""
    if field_type == "int":
        if _INT_RE.match(value):
            return True, ""
        return False, "expected int"
    if field_type == "int_or_empty":
        if value == "":
            return True, ""
        if _INT_RE.match(value):
            return True, ""
        return False, "expected int or empty"
    if field_type == "float":
        if _FLOAT_RE.match(value):
            return True, ""
        return False, "expected float"
    if field_type == "number_or_empty":
        if value == "":
            return True, ""
        if _FLOAT_RE.match(value):
            return True, ""
        return False, "expected number or empty"
    if field_type == "enum":
        enum_values = field.get("enum", [])
        if value in enum_values:
            return True, ""
        return False, f"expected enum {enum_values}"
    if field_type == "bool_str":
        if value in ("true", "false"):
            return True, ""
        return False, "expected bool string 'true' or 'false'"
    if field_type == "bool_01":
        if value in ("0", "1"):
            return True, ""
        return False, "expected 0 or 1"

    return False, f"unknown field type '{field_type}'"


def validate_export_string(export_str: str, contract_path: str) -> List[str]:
    contract = load_contract(contract_path)
    delimiter = contract.get("delimiter", "|")
    kv_separator = contract.get("kv_separator", "=")
    ordered_fields = _ordered_fields(contract)
    expected_keys = _expected_keys(ordered_fields)
    required_keys = {field["key"] for field in ordered_fields if field.get("required", False)}

    errors: List[str] = []

    try:
        keys, values = parse_export_string(
            export_str,
            delimiter=delimiter,
            kv_separator=kv_separator,
        )
    except ValueError as exc:
        return [f"parse_error: {exc}"]

    missing = sorted(required_keys - set(values.keys()))
    if missing:
        errors.append(f"missing required keys: {missing}")

    extras = sorted(set(keys) - set(expected_keys))
    if extras:
        errors.append(f"unexpected keys: {extras}")

    if keys != expected_keys:
        errors.append("key order mismatch")

    for field in ordered_fields:
        key = field["key"]
        if key not in values:
            continue
        ok, message = _check_type(values[key], field)
        if not ok:
            errors.append(f"{key}: {message}")

    return errors
