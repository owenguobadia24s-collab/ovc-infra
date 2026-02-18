import json
import hashlib
from pathlib import Path
import importlib.util
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE_B_PATH = REPO_ROOT / "scripts" / "repo_cartographer" / "phase_b_latest_ok_run.py"


def load_phase_b_module():
    spec = importlib.util.spec_from_file_location("phase_b_module", str(PHASE_B_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def write_sha256_sidecar(path: Path, artifact_name: str, content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()
    path.write_text(f"{digest}  {artifact_name}\n", encoding="utf-8")
    return digest


def test_select_latest_ok_run_picks_highest_run_ts():
    m = load_phase_b_module()
    rows = [
        m.LedgerRow({"run_id": "a", "run_ts": "2026-02-18T10:00:00Z", "status": "OK"}),
        m.LedgerRow({"run_id": "b", "run_ts": "2026-02-18T11:00:00Z", "status": "OK"}),
        m.LedgerRow({"run_id": "c", "run_ts": "2026-02-18T09:00:00Z", "status": "FAIL"}),
    ]
    picked = m.select_latest_ok_run(rows)
    assert picked.run_id == "b"


def test_select_latest_ok_ignores_missing_selector_fields():
    m = load_phase_b_module()
    rows = [
        m.LedgerRow({"run_id": "x", "status": "OK"}),  # missing run_ts
        m.LedgerRow({"run_ts": "2026-02-18T10:00:00Z", "status": "OK"}),  # missing run_id
        m.LedgerRow({"run_id": "y", "run_ts": "bad", "status": "OK"}),  # invalid run_ts
        m.LedgerRow({"run_id": "z", "run_ts": "2026-02-18T10:00:00Z", "status": "OK"}),
    ]
    picked = m.select_latest_ok_run(rows)
    assert picked.run_id == "z"


def test_verify_run_artifacts_ok_when_hashes_match(tmp_path: Path):
    m = load_phase_b_module()
    repo_root = tmp_path

    run_id = "run_1"
    run_dir = repo_root / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True)

    manifest_bytes = b'{"artifacts":{},"run_id":"run_1"}\n'
    seal_bytes = b'{"kind":"REPO_CARTOGRAPHER_RUN_SEAL","run_id":"run_1"}\n'
    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)

    manifest_sha = write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    seal_sha = write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)

    row = m.LedgerRow({
        "run_id": run_id,
        "run_ts": "2026-02-18T10:00:00Z",
        "status": "OK",
        "artifacts_path": f"artifacts/repo_cartographer/{run_id}",
        "manifest_sha256": manifest_sha,
        "seal_sha256": seal_sha,
    })

    result = m.verify_run_artifacts(repo_root, row)
    assert result["ok"] is True


def test_verify_run_artifacts_fail_when_ledger_hash_mismatch(tmp_path: Path):
    m = load_phase_b_module()
    repo_root = tmp_path

    run_id = "run_1"
    run_dir = repo_root / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True)

    manifest_bytes = b'{"artifacts":{},"run_id":"run_1"}\n'
    seal_bytes = b'{"kind":"REPO_CARTOGRAPHER_RUN_SEAL","run_id":"run_1"}\n'
    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)

    write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)

    row = m.LedgerRow({
        "run_id": run_id,
        "run_ts": "2026-02-18T10:00:00Z",
        "status": "OK",
        "artifacts_path": f"artifacts/repo_cartographer/{run_id}",
        "manifest_sha256": "0" * 64,  # mismatch
        "seal_sha256": "1" * 64,      # mismatch
    })

    result = m.verify_run_artifacts(repo_root, row)
    assert result["ok"] is False
    assert result["checks"]["ledger_manifest_match"] is False
    assert result["checks"]["ledger_seal_match"] is False


def test_main_writes_pointer_schema_when_write_enabled(tmp_path: Path, monkeypatch):
    m = load_phase_b_module()
    run_id = "run_1"
    run_ts = "2026-02-18T10:00:00Z"

    run_dir = tmp_path / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_bytes = b'{"artifacts":{},"run_id":"run_1"}\n'
    seal_bytes = b'{"kind":"REPO_CARTOGRAPHER_RUN_SEAL","run_id":"run_1"}\n'
    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)
    manifest_sha = write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    seal_sha = write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)

    ledger_row = {
        "run_id": run_id,
        "run_ts": run_ts,
        "status": "OK",
        "artifacts_path": f"artifacts/repo_cartographer/{run_id}",
        "manifest_sha256": manifest_sha,
        "seal_sha256": seal_sha,
    }
    ledger_path = tmp_path / "docs" / "catalogs" / "REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps(ledger_row, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(m, "get_repo_root", lambda: tmp_path)
    rc = m.main(
        [
            "--ledger",
            "docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl",
            "--out",
            "docs/catalogs/REPO_CARTOGRAPHER_LATEST_OK_RUN_v0.1.json",
            "--strict-verify",
        ]
    )
    assert rc == 0

    pointer_path = tmp_path / "docs" / "baselines" / "LATEST_OK_RUN_POINTER_v0.1.json"
    assert pointer_path.exists()
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert pointer["LATEST_OK_RUN_ID"] == run_id
    assert pointer["LATEST_OK_RUN_TS"] == run_ts
    assert pointer["ok"] is True
    assert pointer["ledger_manifest_match"] is True
    assert pointer["ledger_seal_match"] is True
    assert pointer["manifest_sidecar_match"] is True
    assert pointer["seal_sidecar_match"] is True

    legacy_out_path = tmp_path / "docs" / "catalogs" / "REPO_CARTOGRAPHER_LATEST_OK_RUN_v0.1.json"
    assert legacy_out_path.exists()
    legacy_payload = json.loads(legacy_out_path.read_text(encoding="utf-8"))
    assert legacy_payload["schema_version"] == "REPO_CARTOGRAPHER_LATEST_OK_RUN_v0.1"
    assert legacy_payload["selected"]["run_id"] == run_id


def test_main_fails_when_out_targets_pointer_path(tmp_path: Path, monkeypatch):
    m = load_phase_b_module()
    run_id = "run_1"
    run_ts = "2026-02-18T10:00:00Z"

    run_dir = tmp_path / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_bytes = b'{"artifacts":{},"run_id":"run_1"}\n'
    seal_bytes = b'{"kind":"REPO_CARTOGRAPHER_RUN_SEAL","run_id":"run_1"}\n'
    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)
    manifest_sha = write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    seal_sha = write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)

    ledger_row = {
        "run_id": run_id,
        "run_ts": run_ts,
        "status": "OK",
        "artifacts_path": f"artifacts/repo_cartographer/{run_id}",
        "manifest_sha256": manifest_sha,
        "seal_sha256": seal_sha,
    }
    ledger_path = tmp_path / "docs" / "catalogs" / "REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        json.dumps(ledger_row, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(m, "get_repo_root", lambda: tmp_path)
    rc = m.main(
        [
            "--ledger",
            "docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl",
            "--out",
            "docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json",
        ]
    )
    assert rc == 2
