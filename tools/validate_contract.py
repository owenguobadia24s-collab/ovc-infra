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

def _norm(value: str) -> str:
    # Treat TradingView/Pine "na" as empty
    if value is None:
        return ""
    v = value.strip()
    if v.lower() == "na":
        return ""
    return v


def _check_type(value: str, field: Dict) -> Tuple[bool, str]:
    value = _norm(value)
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

    # ✅ Accept either 0/1 OR true/false in one type
    if field_type == "bool_any":
        if value in ("0", "1", "true", "false"):
            return True, ""
        return False, "expected 0/1 or true/false"



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

def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate an OVC export string against a contract JSON."
    )
    parser.add_argument(
        "contract_json",
        help="Path to contract JSON (e.g. contracts/export_contract_v0.1_min.json)",
    )
    parser.add_argument(
        "sample_export",
        help="Path to sample export .txt (tests/sample_exports/min_001.txt)",
    )
    args = parser.parse_args(argv)

    # Load export text file (supports the 'contract=MIN' header convention)
    with open(args.sample_export, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    def _clean_line(s: str) -> str:
     return s.strip().lstrip("<").lstrip('"').lstrip("'").strip()
    export_line = next((_clean_line(ln) for ln in lines if _clean_line(ln).startswith("ver=")), "")
    if not export_line:
        print("ERROR: No line starting with 'ver=' found.")
    return 2


    errors = validate_export_string(export_line, args.contract_json)

    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

