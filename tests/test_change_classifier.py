import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


def load_classifier_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "governance" / "classify_change.py"
    spec = importlib.util.spec_from_file_location("classify_change", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load classify_change.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


if __name__ == "__main__":
    unittest.main()
