import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "repo_cartographer" / "phase_b6_publish_latest_ownership_summary.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase_b6_module", str(SCRIPT_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_valid_pointer(run_id: str) -> dict:
    return {
        "LATEST_OK_RUN_ID": run_id,
        "LATEST_OK_RUN_TS": "2026-02-18T14:29:51Z",
        "ok": True,
        "ledger_manifest_match": True,
        "ledger_seal_match": True,
        "manifest_sidecar_match": True,
        "seal_sidecar_match": True,
    }


def create_source_summary(tmp_path: Path, run_id: str, content: bytes) -> Path:
    source_path = (
        tmp_path
        / "artifacts"
        / "repo_cartographer"
        / run_id
        / "MODULE_OWNERSHIP_SUMMARY_v0.1.md"
    )
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(content)
    return source_path


def pointer_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "baselines" / "LATEST_OK_RUN_POINTER_v0.1.json"


def dest_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.md"


def receipt_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.receipt.json"


def test_success_copy_and_receipt(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    source_bytes = b"# Ownership\r\n\r\n- line one\r\n"
    create_source_summary(tmp_path, run_id, source_bytes)

    summary = m.execute(tmp_path)

    assert summary.action == "COPIED"
    assert dest_path(tmp_path).read_bytes() == source_bytes
    assert receipt_path(tmp_path).exists()
    receipt = json.loads(receipt_path(tmp_path).read_text(encoding="utf-8"))
    assert receipt["selected_run_id"] == run_id
    assert receipt["source_path"] == f"artifacts/repo_cartographer/{run_id}/MODULE_OWNERSHIP_SUMMARY_v0.1.md"
    assert receipt["dest_path"] == "docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.md"
    assert "\\" not in receipt["source_path"]
    assert "\\" not in receipt["dest_path"]


def test_noop_identical(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    source_bytes = b"# Ownership\n\n- line one\n"
    create_source_summary(tmp_path, run_id, source_bytes)
    dest = dest_path(tmp_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source_bytes)

    summary = m.execute(tmp_path)

    assert summary.action == "NOOP_IDENTICAL"
    assert summary.sha256_source == summary.sha256_dest
    assert summary.byte_len_source == summary.byte_len_dest
    assert receipt_path(tmp_path).exists()


def test_fail_pointer_missing_no_receipt(tmp_path: Path):
    m = load_module()
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_POINTER_MISSING"
    assert not receipt_path(tmp_path).exists()


def test_fail_pointer_parse_no_receipt(tmp_path: Path):
    m = load_module()
    p = pointer_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not-json", encoding="utf-8")

    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_POINTER_PARSE"
    assert not receipt_path(tmp_path).exists()


@pytest.mark.parametrize(
    "field",
    [
        "ok",
        "ledger_manifest_match",
        "ledger_seal_match",
        "manifest_sidecar_match",
        "seal_sidecar_match",
    ],
)
def test_fail_pointer_gate_false(field: str, tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    payload = make_valid_pointer(run_id)
    payload[field] = False
    write_json(pointer_path(tmp_path), payload)

    summary = m.execute(tmp_path)
    assert summary.action == f"FAIL_POINTER_GATE_FALSE:{field}"
    assert not receipt_path(tmp_path).exists()


def test_fail_run_dir_missing(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))

    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_RUN_DIR_MISSING"


def test_fail_source_missing(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    run_dir = tmp_path / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_SOURCE_MISSING"
    assert summary.source_path_exists is False


def test_fail_atomic_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    create_source_summary(tmp_path, run_id, b"# Ownership\n")

    def fake_replace(_src: Path, _dest: Path) -> None:
        raise OSError("forced failure")

    monkeypatch.setattr(m.os, "replace", fake_replace)
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_ATOMIC_WRITE"
    assert not receipt_path(tmp_path).exists()


def test_fail_copy_hash_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    create_source_summary(tmp_path, run_id, b"# Ownership\n")

    original_digest_and_size = m.digest_and_size
    dest_abs = dest_path(tmp_path).resolve()

    def fake_digest_and_size(path: Path):
        digest, size = original_digest_and_size(path)
        if path.resolve() == dest_abs:
            return ("0" * 64, size)
        return (digest, size)

    monkeypatch.setattr(m, "digest_and_size", fake_digest_and_size)
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_COPY_HASH_MISMATCH"
    assert not receipt_path(tmp_path).exists()


def test_pointer_parse_when_required_id_missing(tmp_path: Path):
    m = load_module()
    payload = make_valid_pointer("20260218_142951Z")
    del payload["LATEST_OK_RUN_ID"]
    write_json(pointer_path(tmp_path), payload)

    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_POINTER_PARSE"
