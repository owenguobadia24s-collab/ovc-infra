import os
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_contract import validate_export_string  # noqa: E402


CONTRACTS = {
    "MIN": ROOT / "contracts" / "export_contract_v0.1.1_min.json",
    "FULL": ROOT / "contracts" / "export_contract_v0.1_full.json",
}


def _profile_from_filename(name: str) -> str:
    lower = name.lower()
    if "min" in lower and "full" in lower:
        raise ValueError("filename contains both 'min' and 'full'")
    if "min" in lower:
        return "MIN"
    if "full" in lower:
        return "FULL"
    return ""


def _profile_from_header(line: str) -> str:
    lower = line.lower()
    if not (lower.startswith("contract") or lower.startswith("profile")):
        return ""
    if "=" in line:
        _, value = line.split("=", 1)
    elif ":" in line:
        _, value = line.split(":", 1)
    else:
        raise ValueError("header must use '=' or ':'")
    value = value.strip().upper()
    if value in ("MIN", "FULL"):
        return value
    raise ValueError(f"unknown contract profile '{value}'")

def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "y", "on")


def _load_sample(path: Path) -> tuple:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    lines = [line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("#")]
    if not lines:
        raise ValueError("sample is empty")

    profile = _profile_from_header(lines[0])
    if profile:
        if len(lines) < 2:
            raise ValueError("missing export string after header")
        export_str = lines[1]
        if len(lines) > 2:
            raise ValueError("multiple export strings found")
        return profile, export_str

    profile = _profile_from_filename(path.name)
    if not profile:
        raise ValueError("could not determine contract profile")
    if len(lines) > 1:
        raise ValueError("multiple export strings found")
    return profile, lines[0]


class TestContractEquivalence(unittest.TestCase):
    def test_sample_exports(self) -> None:
        sample_dir = ROOT / "tests" / "sample_exports"
        sample_files = [
            path
            for path in sample_dir.iterdir()
            if path.is_file() and path.name != "README.md"
        ]
        if not sample_files:
            self.skipTest("no sample exports found")

        include_full = _env_true("OVC_VALIDATE_FULL")
        noted_full_skip = False
        for path in sample_files:
            with self.subTest(sample=path.name):
                profile, export_str = _load_sample(path)
                if profile == "FULL" and not include_full:
                    if not noted_full_skip:
                        print("NOTE: FULL fixtures are opt-in; set OVC_VALIDATE_FULL=1 to include")
                        noted_full_skip = True
                    continue
                contract_path = CONTRACTS[profile]
                errors = validate_export_string(export_str, str(contract_path))
                self.assertEqual([], errors, msg=f"{path}: {errors}")
