import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = REPO_ROOT / "scripts" / "governance" / "build_change_classification_overlay_v0_1.py"
LEDGER_PATH = REPO_ROOT / "docs" / "catalogs" / "DEV_CHANGE_LEDGER_v0.1.jsonl"
CLASSIFIER_PATH = REPO_ROOT / "scripts" / "governance" / "classify_change.py"
TEST_OUTPUT_ROOT = REPO_ROOT / "testdir" / "change_overlay_builder"


def load_jsonl(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def run_builder(out_path: Path) -> tuple[Path, Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    seal_json_path = out_path.with_suffix(".seal.json")
    seal_sha256_path = out_path.with_suffix(".seal.sha256")
    proc = subprocess.run(
        [
            sys.executable,
            str(BUILDER_PATH),
            "--out",
            str(out_path),
            "--ledger",
            str(LEDGER_PATH),
            "--classifier",
            str(CLASSIFIER_PATH),
            "--seal-json",
            str(seal_json_path),
            "--seal-sha256",
            str(seal_sha256_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.returncode == 0, f"builder failed: stdout={proc.stdout}\nstderr={proc.stderr}"
    return seal_json_path, seal_sha256_path


def test_overlay_line_count_matches_ledger():
    overlay_path = TEST_OUTPUT_ROOT / "line_count" / "overlay.jsonl"
    run_builder(overlay_path)

    ledger_lines = load_jsonl(LEDGER_PATH)
    overlay_lines = load_jsonl(overlay_path)
    assert len(overlay_lines) == len(ledger_lines)


def test_overlay_commit_alignment_and_schema():
    overlay_path = TEST_OUTPUT_ROOT / "alignment_schema" / "overlay.jsonl"
    run_builder(overlay_path)

    ledger_lines = load_jsonl(LEDGER_PATH)
    overlay_lines = load_jsonl(overlay_path)
    assert len(overlay_lines) == len(ledger_lines)

    required_fields = {"commit", "classes", "unknown", "ambiguous", "files", "base"}
    for ledger_line, overlay_line in zip(ledger_lines, overlay_lines):
        assert required_fields.issubset(set(overlay_line.keys()))
        assert overlay_line["commit"] == ledger_line["commit"]["hash"]
        assert isinstance(overlay_line["classes"], list)
        assert overlay_line["classes"]
        assert isinstance(overlay_line["files"], int)
        assert overlay_line["files"] >= 0
        assert overlay_line["base"] == f"{overlay_line['commit']}^"
        assert overlay_line["ambiguous"] == (len(overlay_line["classes"]) > 1)
        if overlay_line["unknown"]:
            assert overlay_line["classes"] == ["UNKNOWN"]


def test_builder_deterministic_rerun():
    overlay_path = TEST_OUTPUT_ROOT / "deterministic_rerun" / "overlay.jsonl"
    seal_json_path, seal_sha256_path = run_builder(overlay_path)

    overlay_first = overlay_path.read_bytes()
    seal_json_first = seal_json_path.read_bytes()
    seal_sha256_first = seal_sha256_path.read_bytes()

    run_builder(overlay_path)

    assert overlay_path.read_bytes() == overlay_first
    assert seal_json_path.read_bytes() == seal_json_first
    assert seal_sha256_path.read_bytes() == seal_sha256_first


def test_seal_contains_required_hash_inputs():
    overlay_path = TEST_OUTPUT_ROOT / "seal_inputs" / "overlay.jsonl"
    seal_json_path, seal_sha256_path = run_builder(overlay_path)

    seal = json.loads(seal_json_path.read_text(encoding="utf-8"))
    artifacts = seal["artifacts"]

    assert any(key.endswith(overlay_path.name) for key in artifacts)
    assert any(key.endswith("DEV_CHANGE_LEDGER_v0.1.jsonl") for key in artifacts)
    assert any(key.endswith("build_change_classification_overlay_v0_1.py") for key in artifacts)
    assert any(key.endswith("classify_change.py") for key in artifacts)

    for artifact in artifacts.values():
        assert "sha256" in artifact
        assert "bytes" in artifact

    ledger_lines = load_jsonl(LEDGER_PATH)
    assert seal["range"]["from"] == ledger_lines[0]["commit"]["hash"]
    assert seal["range"]["to"] == ledger_lines[-1]["commit"]["hash"]

    expected_seal_hash = hashlib.sha256(seal_json_path.read_bytes()).hexdigest()
    expected_sha_line = f"{expected_seal_hash}  {seal_json_path.name}"
    assert seal_sha256_path.read_text(encoding="utf-8").strip() == expected_sha_line
