from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

MAX_DIFF_LINES = 120
MAX_DIFF_CHARS = 12000


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _fixture_export_root() -> Path:
    return _repo_root() / "tests" / "fixtures" / "chat_export_golden" / "2026-02-21_export_raw"


def _expected_snapshot_path() -> Path:
    return _repo_root() / "tests" / "golden" / "design_record_engine" / "phase1" / "expected" / "evidence_nodes.jsonl"


def _run_phase1_pipeline(export_root: Path, artifacts_root: Path) -> subprocess.CompletedProcess[str]:
    clean_env = os.environ.copy()
    clean_env.pop("OPENAI_API_KEY", None)
    cmd = [
        "python",
        "scripts/design_record_engine/run_all.py",
        "--export-root",
        str(export_root),
        "--seal",
        "--artifacts-root",
        str(artifacts_root),
        "--stop-after-phase1",
    ]
    return subprocess.run(
        cmd,
        cwd=str(_repo_root()),
        env=clean_env,
        capture_output=True,
        text=True,
    )


def _assert_jsonl_invariants(path: Path) -> None:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [json.loads(line) for line in lines]
    node_ids = []
    for row in rows:
        assert "node_id" in row, "Missing node_id field in evidence_nodes.jsonl row"
        node_ids.append(row["node_id"])
    assert len(node_ids) == len(set(node_ids)), "node_id values must be unique"
    assert node_ids == sorted(node_ids), "node_id values must be lexicographically sorted"


def _format_diff(actual: bytes, expected: bytes, actual_name: str, expected_name: str) -> str:
    actual_lines = actual.decode("utf-8", errors="replace").splitlines(keepends=True)
    expected_lines = expected.decode("utf-8", errors="replace").splitlines(keepends=True)
    diff_lines = list(
        difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile=expected_name,
            tofile=actual_name,
            n=3,
        )
    )
    if not diff_lines:
        return "No line-level diff available; bytes differ."

    truncated = False
    if len(diff_lines) > MAX_DIFF_LINES:
        diff_lines = diff_lines[:MAX_DIFF_LINES]
        truncated = True

    text = "".join(diff_lines)
    if len(text) > MAX_DIFF_CHARS:
        text = text[:MAX_DIFF_CHARS]
        truncated = True

    if truncated:
        text += "\n... diff truncated ...\n"
    return text


def test_phase1_golden_snapshot(tmp_path: Path) -> None:
    export_root = tmp_path / "export_raw"
    artifacts_root = tmp_path / "artifacts_phase1"
    shutil.copytree(_fixture_export_root(), export_root)

    run = _run_phase1_pipeline(export_root=export_root, artifacts_root=artifacts_root)
    assert run.returncode == 0, f"stdout={run.stdout}\nstderr={run.stderr}"

    actual_path = artifacts_root / "evidence_nodes.jsonl"
    expected_path = _expected_snapshot_path()
    if not actual_path.is_file():
        pytest.skip("Phase 1 output evidence_nodes.jsonl not produced in this branch")
    if not expected_path.is_file():
        pytest.skip("Golden snapshot missing; generate after Phase 1 implementation")

    _assert_jsonl_invariants(actual_path)

    actual_bytes = actual_path.read_bytes()
    expected_bytes = expected_path.read_bytes()
    if actual_bytes != expected_bytes:
        diff_text = _format_diff(
            actual=actual_bytes,
            expected=expected_bytes,
            actual_name=str(actual_path),
            expected_name=str(expected_path),
        )
        pytest.fail("Phase 1 golden snapshot mismatch:\n" + diff_text)


def test_phase1_determinism_rerun(tmp_path: Path) -> None:
    export_a = tmp_path / "export_a"
    export_b = tmp_path / "export_b"
    artifacts_a = tmp_path / "artifacts_a"
    artifacts_b = tmp_path / "artifacts_b"
    shutil.copytree(_fixture_export_root(), export_a)
    shutil.copytree(_fixture_export_root(), export_b)

    run_a = _run_phase1_pipeline(export_root=export_a, artifacts_root=artifacts_a)
    assert run_a.returncode == 0, f"stdout={run_a.stdout}\nstderr={run_a.stderr}"
    run_b = _run_phase1_pipeline(export_root=export_b, artifacts_root=artifacts_b)
    assert run_b.returncode == 0, f"stdout={run_b.stdout}\nstderr={run_b.stderr}"

    file_a = artifacts_a / "evidence_nodes.jsonl"
    file_b = artifacts_b / "evidence_nodes.jsonl"
    if not file_a.is_file() or not file_b.is_file():
        pytest.skip("Phase 1 output evidence_nodes.jsonl not produced in this branch")

    _assert_jsonl_invariants(file_a)
    _assert_jsonl_invariants(file_b)

    bytes_a = file_a.read_bytes()
    bytes_b = file_b.read_bytes()
    if bytes_a != bytes_b:
        diff_text = _format_diff(
            actual=bytes_a,
            expected=bytes_b,
            actual_name=str(file_a),
            expected_name=str(file_b),
        )
        pytest.fail("Phase 1 rerun output mismatch:\n" + diff_text)
