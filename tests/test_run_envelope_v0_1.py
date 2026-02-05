import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ovc_ops.run_envelope_v0_1 import seal_dir, write_run_json  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def test_run_envelope_and_seal(tmp_path):
    run_dir = tmp_path / "run_1"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "alpha.txt").write_text("alpha", encoding="utf-8")
    (run_dir / "beta.txt").write_text("beta", encoding="utf-8")

    payload = {
        "run_id": "run_1",
        "created_utc": "2026-02-04T00:00:00Z",
        "run_type": "op_run",
        "option": "QA",
        "operation_id": "OP-QA06",
        "git_commit": None,
        "working_tree_state": None,
        "outputs": [
            "alpha.txt",
            "beta.txt",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
    }
    write_run_json(run_dir, payload)
    seal_dir(run_dir, ["alpha.txt", "beta.txt", "run.json"])

    data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    for key in [
        "run_id",
        "created_utc",
        "run_type",
        "option",
        "operation_id",
        "git_commit",
        "working_tree_state",
        "outputs",
    ]:
        assert key in data

    manifest_entries = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    entries_by_rel = {e["relpath"]: e for e in manifest_entries}
    for rel in ["alpha.txt", "beta.txt", "run.json"]:
        assert rel in entries_by_rel
        assert entries_by_rel[rel]["sha256"] == sha256_file(run_dir / rel)

    manifest_lines = [
        line.strip()
        for line in (run_dir / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    root_lines = [line for line in manifest_lines if line.startswith("ROOT_SHA256")]
    assert len(root_lines) == 1
    root_hash = root_lines[0].split()[-1]
    sha_lines = [line for line in manifest_lines if not line.startswith("ROOT_SHA256")]
    assert any(line.endswith("  manifest.json") for line in sha_lines)
    expected_root = sha256_bytes(("\n".join(sorted(sha_lines)) + "\n").encode("utf-8"))
    assert root_hash == expected_root


def test_seal_dir_strict_missing_file_raises(tmp_path):
    run_dir = tmp_path / "run_2"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "alpha.txt").write_text("alpha", encoding="utf-8")

    payload = {
        "run_id": "run_2",
        "created_utc": "2026-02-04T00:00:00Z",
        "run_type": "op_run",
        "option": "QA",
        "operation_id": "OP-QA06",
        "git_commit": None,
        "working_tree_state": None,
        "outputs": [
            "alpha.txt",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
    }
    write_run_json(run_dir, payload)

    with pytest.raises(FileNotFoundError):
        seal_dir(run_dir, ["alpha.txt", "MISSING.txt", "run.json"], strict=True)
