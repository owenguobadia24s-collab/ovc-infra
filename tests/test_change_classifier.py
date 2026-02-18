import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER_SCRIPT = REPO_ROOT / "scripts" / "governance" / "classify_change.py"
SAMPLE_PATHS = [
    "reports/path1/evidence/runs/p1_1/RUN.md",
    "docs/governance/GOVERNANCE_RULES_v0.1.md",
    "scripts/governance/classify_change.py",
    ".github/workflows/change_classifier.yml",
    "tools/phase3_control_panel/src/app/page.tsx",
    "random/file.bin",
]


def load_classifier_module():
    module_path = CLASSIFIER_SCRIPT
    spec = importlib.util.spec_from_file_location("classify_change", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load classify_change.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_classifier_json(paths: list[str], allow_unknown: bool) -> subprocess.CompletedProcess[str]:
    stdin_payload = "\n".join(paths) + "\n"
    cmd = [
        sys.executable,
        str(CLASSIFIER_SCRIPT),
        "--paths-from-stdin",
        "--json",
    ]
    if allow_unknown:
        cmd.append("--allow-unknown")
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        input=stdin_payload,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_stdout_json(proc: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(proc.stdout)


def expected_review_tags(classes: list[str]) -> list[str]:
    tags = []
    if "B" in classes:
        tags.append("REVIEW_RATIFICATION")
    if "C" in classes:
        tags.append("REVIEW_AUDIT_PACK")
    if "D" in classes:
        tags.append("REVIEW_UI_AUDIT")
    if "E" in classes:
        tags.append("REVIEW_COMPATIBILITY")
    if classes == ["UNKNOWN"]:
        tags.append("REVIEW_UNKNOWN_PATH")
    return sorted(tags)


def classifications_by_path(payload: dict) -> dict[str, dict]:
    rows = payload.get("file_classifications")
    assert isinstance(rows, list)
    return {row["path"]: row for row in rows}


class TestChangeClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_classifier_module()

    def test_a_only(self):
        result = self.mod.classify_paths(
            ["reports/path1/evidence/runs/p1_1/RUN.md", "sql/path1/evidence/runs/p1_1/study_res_v1_0.sql"]
        )
        self.assertEqual(result["classes"], ["A"])
        self.assertEqual(result["required"]["A"], "none")

    def test_b_contract_edit(self):
        result = self.mod.classify_paths(["docs/contracts/option_c_outcomes_contract_v1.md"])
        self.assertEqual(result["classes"], ["B"])
        self.assertIn("Ratification required", result["required"]["B"])
        self.assertIn("Attach validator/audit outcome reference", result["required"]["B"])

    def test_workflow_is_c_and_e(self):
        result = self.mod.classify_paths([".github/workflows/x.yml"])
        self.assertEqual(result["classes"], ["C", "E"])

    def test_phase3_panel_is_c_and_d(self):
        result = self.mod.classify_paths(["tools/phase3_control_panel/src/app/page.tsx"])
        self.assertEqual(result["classes"], ["C", "D"])

    def test_tools_shim_is_c_and_e(self):
        result = self.mod.classify_paths(["tools/some_shim/compat.py"])
        self.assertEqual(result["classes"], ["C", "E"])

    def test_unknown_path(self):
        result = self.mod.classify_paths(["random/file.bin"])
        self.assertEqual(result["classes"], ["UNKNOWN"])
        self.assertEqual(result["unknown_paths"], ["random/file.bin"])

    def test_stable_class_order(self):
        result = self.mod.classify_paths(
            [
                "docs/governance/GOVERNANCE_RULES_v0.1.md",
                "reports/path1/evidence/runs/r1/RUN.md",
                ".github/workflows/ci.yml",
            ]
        )
        self.assertEqual(result["classes"], ["A", "B", "C", "E"])

    def test_exit_code_unknown_precedence(self):
        code = self.mod.determine_exit_code(classes=["B", "UNKNOWN"], allow_unknown=False, fail_on=["B"])
        self.assertEqual(code, 2)

    def test_exit_code_fail_on(self):
        code = self.mod.determine_exit_code(classes=["A", "B"], allow_unknown=True, fail_on=["B"])
        self.assertEqual(code, 3)

    def test_exit_code_success(self):
        code = self.mod.determine_exit_code(classes=["A"], allow_unknown=False, fail_on=["B"])
        self.assertEqual(code, 0)

    def test_parse_args_range_mode(self):
        args = self.mod.parse_args(["--range", "abc123..def456"])
        self.assertEqual(args.range_spec, "abc123..def456")
        self.assertIsNone(args.base)
        self.assertFalse(args.staged)

    def test_parse_args_range_mutually_exclusive_with_staged(self):
        with self.assertRaises(ValueError):
            self.mod.parse_args(["--staged", "--range", "abc..def"])

    def test_parse_args_range_mutually_exclusive_with_base(self):
        with self.assertRaises(ValueError):
            self.mod.parse_args(["--base", "main", "--range", "abc..def"])

    def test_collect_changed_paths_range_mode(self):
        with patch.object(self.mod, "run_git", return_value="a.txt\nb.txt\n") as run_git_mock:
            paths, mode, base_ref = self.mod.collect_changed_paths(
                staged=False,
                base_ref=None,
                range_spec="abc123..def456",
            )
        run_git_mock.assert_called_once_with(["diff", "--name-only", "abc123", "def456"])
        self.assertEqual(paths, ["a.txt", "b.txt"])
        self.assertEqual(mode, "range")
        self.assertEqual(base_ref, "abc123")

    def test_collect_changed_paths_range_mode_invalid_spec(self):
        with self.assertRaises(ValueError):
            self.mod.collect_changed_paths(staged=False, base_ref=None, range_spec="abc123")

    def test_collect_changed_paths_range_mode_rejects_triple_dot(self):
        with self.assertRaises(ValueError):
            self.mod.collect_changed_paths(staged=False, base_ref=None, range_spec="abc...def")


def test_v02_tags_deterministic_exact_and_review_derived():
    proc = run_classifier_json(SAMPLE_PATHS, allow_unknown=True)
    assert proc.returncode == 0
    assert proc.stderr == ""

    payload = parse_stdout_json(proc)
    by_path = classifications_by_path(payload)

    expected_exact = {
        "docs/governance/GOVERNANCE_RULES_v0.1.md": [
            "DET_HIGH",
            "POWER_NONE",
            "REVIEW_RATIFICATION",
            "SURFACE_DOCS",
            "SURFACE_GOVERNANCE",
        ],
        "scripts/governance/classify_change.py": [
            "DET_HIGH",
            "POWER_LOCAL",
            "REVIEW_AUDIT_PACK",
            "SURFACE_RUNTIME",
        ],
        "random/file.bin": [
            "DET_LOW",
            "POWER_LOCAL",
            "REVIEW_UNKNOWN_PATH",
        ],
        "reports/path1/evidence/runs/p1_1/RUN.md": [
            "DET_LOW",
            "POWER_NONE",
            "SURFACE_EVIDENCE",
        ],
    }
    for path, expected_tags in expected_exact.items():
        assert by_path[path]["tags"] == expected_tags

    edge_expected_non_review = {
        ".github/workflows/change_classifier.yml": [
            "DET_LOW",
            "POWER_CI_ENFORCING",
            "SURFACE_CI",
        ],
        "tools/phase3_control_panel/src/app/page.tsx": [
            "DET_MED",
            "POWER_LOCAL",
            "SURFACE_UI",
        ],
    }
    for path, expected_non_review in edge_expected_non_review.items():
        row = by_path[path]
        tags = row["tags"]
        classes = row["classes"]
        review_tags = sorted(tag for tag in tags if tag.startswith("REVIEW_"))
        non_review_tags = sorted(tag for tag in tags if not tag.startswith("REVIEW_"))
        assert non_review_tags == expected_non_review
        assert review_tags == expected_review_tags(classes)
        assert tags == sorted(tags)


def test_v02_power_det_exactly_one_invariants():
    proc = run_classifier_json(SAMPLE_PATHS, allow_unknown=True)
    assert proc.returncode == 0
    assert proc.stderr == ""
    payload = parse_stdout_json(proc)

    for row in payload["file_classifications"]:
        tags = row["tags"]
        power_tags = [tag for tag in tags if tag.startswith("POWER_")]
        det_tags = [tag for tag in tags if tag.startswith("DET_")]
        assert len(power_tags) == 1
        assert len(det_tags) == 1

    agg_tags = payload["tags"]
    assert agg_tags == sorted(agg_tags)
    assert any(tag.startswith("POWER_") for tag in agg_tags)
    assert any(tag.startswith("DET_") for tag in agg_tags)


def test_v02_json_only_output_when_unknown_exit_code():
    proc = run_classifier_json(SAMPLE_PATHS, allow_unknown=False)
    assert proc.returncode == 2
    assert proc.stderr == ""
    assert proc.stdout.strip().startswith("{")
    assert proc.stdout.strip().endswith("}")

    payload = parse_stdout_json(proc)
    assert "UNKNOWN" in payload["classes"]


if __name__ == "__main__":
    unittest.main()
