import ast
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_contract import validate_export_string  # noqa: E402


CONTRACT_PATH = ROOT / "contracts" / "export_contract_v0.1.1_min.json"
SAMPLE_PATH = ROOT / "tests" / "sample_exports" / "min_001.txt"


def _replace_value(sample: str, key: str, value: str) -> str:
    parts = sample.split("|")
    for idx, part in enumerate(parts):
        if part.startswith(f"{key}="):
            parts[idx] = f"{key}={value}"
            return "|".join(parts)
    raise ValueError(f"key not found: {key}")


def _remove_keys(sample: str, keys: list[str]) -> str:
    parts = sample.split("|")
    keep = [part for part in parts if not any(part.startswith(f"{key}=") for key in keys)]
    return "|".join(keep)


class TestMinContractValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.sample = SAMPLE_PATH.read_text(encoding="utf-8").strip()

    def test_min_sample_passes(self) -> None:
        errors = validate_export_string(self.sample, str(CONTRACT_PATH))
        self.assertEqual([], errors)

    def test_missing_keys_listed(self) -> None:
        sample = _remove_keys(self.sample, ["sym", "tz", "bar_close_ms"])
        errors = validate_export_string(sample, str(CONTRACT_PATH))
        missing_error = next((e for e in errors if e.startswith("missing required keys:")), "")
        self.assertTrue(missing_error, msg=f"missing error not found: {errors}")
        missing_list = ast.literal_eval(missing_error.split(":", 1)[1].strip())
        self.assertEqual(sorted(missing_list), ["bar_close_ms", "sym", "tz"])

    def test_type_errors_bool_and_int(self) -> None:
        sample = _replace_value(self.sample, "tradeable", "2")
        sample = _replace_value(sample, "bar_close_ms", "notint")
        errors = validate_export_string(sample, str(CONTRACT_PATH))
        self.assertTrue(any("tradeable: expected 0 or 1" in e for e in errors), msg=str(errors))
        self.assertTrue(any("bar_close_ms: expected int" in e for e in errors), msg=str(errors))

    def test_type_error_float(self) -> None:
        sample = _replace_value(self.sample, "rrc", "badfloat")
        errors = validate_export_string(sample, str(CONTRACT_PATH))
        self.assertTrue(any("rrc: expected float" in e for e in errors), msg=str(errors))

    def test_unknown_key_rejected(self) -> None:
        sample = self.sample + "|extra_key=surprise"
        errors = validate_export_string(sample, str(CONTRACT_PATH))
        self.assertTrue(any(e.startswith("unexpected keys:") and "extra_key" in e for e in errors), msg=str(errors))
