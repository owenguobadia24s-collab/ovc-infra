import json
import shutil
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch
from pathlib import Path



REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_INTERPRETER_SRC = REPO_ROOT / "tools" / "audit_interpreter" / "src"
SCHEMA_PATH = REPO_ROOT / "docs" / "contracts" / "schemas" / "AUDIT_INTERPRETATION_REPORT_v0.1.json"

if str(AUDIT_INTERPRETER_SRC) not in sys.path:
    sys.path.insert(0, str(AUDIT_INTERPRETER_SRC))

from audit_interpreter.interpret import interpret_run  # noqa: E402
from audit_interpreter.pipeline.change_classifier import run_change_classifier  # noqa: E402


class TestAuditInterpreterChangeClassification(unittest.TestCase):
    def setUp(self) -> None:
        tmp_parent = REPO_ROOT / ".pytest-tmp"
        tmp_parent.mkdir(parents=True, exist_ok=True)
        self.tmp_root = Path(tempfile.mkdtemp(prefix="audit_cls_", dir=str(tmp_parent)))
        self.addCleanup(lambda: shutil.rmtree(self.tmp_root, ignore_errors=True))

    def _create_repo_with_run(self, run_id: str = "test_run_001") -> tuple[Path, Path, Path]:
        repo_root = self.tmp_root / "repo"
        runs_root = repo_root / ".codex" / "RUNS"
        run_folder = runs_root / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        run_json = {
            "run_id": run_id,
            "created_utc": "2026-02-07T00:00:00Z",
            "run_type": "smoke",
        }
        (run_folder / "run.json").write_text(json.dumps(run_json) + "\n", encoding="utf-8")
        return repo_root, runs_root, run_folder

    def _write_classifier_script(self, repo_root: Path, payload: dict, exit_code: int) -> Path:
        script_path = repo_root / "scripts" / "governance" / "classify_change.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_text = textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import json
            import sys

            payload = {json.dumps(payload, sort_keys=True)}
            classes = payload.get("classes", [])
            files = payload.get("files", 0)
            print("CLASS=" + ",".join(classes))
            print(f"FILES={{files}}")
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
            raise SystemExit({exit_code})
            """
        )
        script_path.write_text(script_text, encoding="utf-8")
        return script_path

    def test_report_includes_change_classification_and_writes_artifact(self) -> None:
        repo_root, runs_root, run_folder = self._create_repo_with_run()
        payload = {
            "classes": ["A", "C"],
            "required": {
                "A": "none",
                "C": "Audit pack required; Determinism required for generators/sealers",
            },
            "files": 2,
            "paths": ["reports/path1/example.txt", "scripts/path1/example.py"],
            "unknown_paths": [],
            "mode": "base",
            "base_ref": "origin/main",
        }
        self._write_classifier_script(repo_root, payload, exit_code=0)

        result = interpret_run(
            run_id="test_run_001",
            runs_root=runs_root,
            schema_path=SCHEMA_PATH,
            stdout=False,
            strict=False,
            repo_root=repo_root,
            base_ref=None,
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.report)
        notes = result.report["metadata"]["notes"]
        self.assertIn("Change Classification", notes)
        self.assertIn("CLASS=A,C", notes)
        self.assertIn("FILES=2", notes)
        self.assertIn("REQUIRED(A)=none", notes)
        self.assertIn("REQUIRED(C)=Audit pack required; Determinism required for generators/sealers", notes)
        self.assertIn("Artifact path:", notes)
        self.assertIn("invoked_cmd=", notes)
        self.assertNotIn("WARNING:", notes)

        artifact_path = run_folder / "change_classification.json"
        self.assertTrue(artifact_path.exists())
        artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact_payload["classes"], ["A", "C"])

        parsed_json, meta = run_change_classifier(
            base_ref="origin/main",
            repo_root=repo_root,
            output_dir=run_folder,
            fallback_output_dir=runs_root / ".audit_work" / "test_run_001",
        )
        self.assertIsNotNone(parsed_json)
        self.assertIn("--json", meta["invoked_cmd"])
        self.assertIn("--base", meta["invoked_cmd"])
        self.assertNotIn("--fail-on", meta["invoked_cmd"])

    def test_classifier_exit_2_is_non_fatal_and_warned(self) -> None:
        repo_root, runs_root, run_folder = self._create_repo_with_run()
        payload = {
            "classes": ["UNKNOWN"],
            "required": {"UNKNOWN": "Unmapped path patterns detected"},
            "files": 1,
            "paths": ["unknown/file.bin"],
            "unknown_paths": ["unknown/file.bin"],
            "mode": "base",
            "base_ref": "origin/main",
        }
        self._write_classifier_script(repo_root, payload, exit_code=2)

        result = interpret_run(
            run_id="test_run_001",
            runs_root=runs_root,
            schema_path=SCHEMA_PATH,
            stdout=False,
            strict=False,
            repo_root=repo_root,
            base_ref="origin/main",
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.report)
        notes = result.report["metadata"]["notes"]
        self.assertIn("CLASS=UNKNOWN", notes)
        self.assertIn("invoked_cmd=", notes)
        self.assertIn("WARNING: classifier exit_code=2", notes)
        self.assertTrue((run_folder / "change_classification.json").exists())

    def test_classifier_cannot_be_invoked_is_non_fatal_and_warned(self) -> None:
        repo_root, runs_root, run_folder = self._create_repo_with_run()

        with patch("audit_interpreter.pipeline.change_classifier.subprocess.run", side_effect=FileNotFoundError("python not found")):
            result = interpret_run(
                run_id="test_run_001",
                runs_root=runs_root,
                schema_path=SCHEMA_PATH,
                stdout=False,
                strict=False,
                repo_root=repo_root,
                base_ref=None,
            )

            self.assertTrue(result.success)
            self.assertIsNotNone(result.report)
            notes = result.report["metadata"]["notes"]
            self.assertIn("Change Classification", notes)
            self.assertIn("CLASS=UNAVAILABLE", notes)
            self.assertIn("Artifact path:", notes)
            self.assertIn("WARNING: classifier exit_code=", notes)
            self.assertIn("python not found", notes)
            self.assertFalse((run_folder / "change_classification.json").exists())
            self.assertFalse((runs_root / ".audit_work" / "test_run_001" / "change_classification.json").exists())

    def test_sealed_run_folder_does_not_crash_interpreter(self) -> None:
        repo_root, runs_root, run_folder = self._create_repo_with_run()
        payload = {
            "classes": ["A"],
            "required": {"A": "none"},
            "files": 1,
            "paths": ["reports/path1/example.txt"],
            "unknown_paths": [],
            "mode": "base",
            "base_ref": "origin/main",
        }
        self._write_classifier_script(repo_root, payload, exit_code=0)

        original_write_text = Path.write_text

        def raise_for_classification_artifact(path_obj: Path, data: str, *args, **kwargs):
            if path_obj == (run_folder / "change_classification.json"):
                raise PermissionError("simulated sealed run folder")
            return original_write_text(path_obj, data, *args, **kwargs)

        with patch(
            "audit_interpreter.pipeline.change_classifier.Path.write_text",
            autospec=True,
            side_effect=raise_for_classification_artifact,
        ):
            result = interpret_run(
                run_id="test_run_001",
                runs_root=runs_root,
                schema_path=SCHEMA_PATH,
                stdout=False,
                strict=False,
                repo_root=repo_root,
                base_ref=None,
            )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.report)
        notes = result.report["metadata"]["notes"]
        self.assertIn("Change Classification", notes)
        self.assertIn("Artifact path:", notes)
        self.assertIn("primary_write_error=", notes)
        self.assertIn("fallback_used=true", notes)
        self.assertIn(".audit_work", notes)
        self.assertNotIn(str(run_folder / "change_classification.json"), notes)
        self.assertFalse((run_folder / "change_classification.json").exists())
        self.assertTrue((runs_root / ".audit_work" / "test_run_001" / "change_classification.json").exists())


if __name__ == "__main__":
    unittest.main()
