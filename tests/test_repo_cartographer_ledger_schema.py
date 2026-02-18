import hashlib
import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CARTOGRAPHER_PATH = REPO_ROOT / "scripts" / "repo_cartographer" / "cartographer.py"


def load_cartographer_module():
    spec = importlib.util.spec_from_file_location("repo_cartographer_module", str(CARTOGRAPHER_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def write_sha256_sidecar(path: Path, artifact_name: str, content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()
    path.write_text(f"{digest}  {artifact_name}\n", encoding="utf-8")
    return digest


def make_valid_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "artifacts" / "repo_cartographer" / "run_1"
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_bytes = b'{"artifacts":{},"run_id":"run_1"}\n'
    seal_bytes = b'{"kind":"REPO_CARTOGRAPHER_RUN_SEAL","run_id":"run_1"}\n'

    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)
    write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)
    return run_dir


def test_build_ledger_line_includes_run_ts_and_status():
    module = load_cartographer_module()

    line = module.build_ledger_line(
        run_id="20260218_134926Z",
        run_ts="2026-02-18T13:49:26Z",
        status="OK",
        run_fingerprint="f" * 64,
        generated_utc="2026-02-18T13:49:26Z",
        head_commit="a" * 40,
        ruleset_id="MODULE_OWNERSHIP_RULES_v0.1",
        tracked_list_sha256="b" * 64,
        untracked_visible_list_sha256="c" * 64,
        ruleset_sha256="d" * 64,
        manifest_sha256="e" * 64,
        seal_sha256="f" * 64,
        summary_counts={"total": 1, "tracked": 1, "unknown": 0, "untracked_visible": 0},
        artifacts_path="artifacts/repo_cartographer/20260218_134926Z",
    )

    assert line["run_id"] == "20260218_134926Z"
    assert line["run_ts"] == "2026-02-18T13:49:26Z"
    assert line["status"] == "OK"


def test_compute_ledger_status_ok_when_hashes_match(tmp_path: Path):
    module = load_cartographer_module()
    run_dir = make_valid_run_dir(tmp_path)

    assert module.compute_ledger_status(run_dir) == "OK"


def test_compute_ledger_status_fail_when_required_file_missing(tmp_path: Path):
    module = load_cartographer_module()
    run_dir = make_valid_run_dir(tmp_path)
    (run_dir / "SEAL.sha256").unlink()

    assert module.compute_ledger_status(run_dir) == "FAIL"


def test_compute_ledger_status_fail_when_hash_mismatch(tmp_path: Path):
    module = load_cartographer_module()
    run_dir = make_valid_run_dir(tmp_path)
    (run_dir / "MANIFEST.sha256").write_text(
        f"{'0' * 64}  MANIFEST.json\n",
        encoding="utf-8",
    )

    assert module.compute_ledger_status(run_dir) == "FAIL"


def test_derive_run_ts_prefers_valid_generated_utc():
    module = load_cartographer_module()
    generated_utc = "2026-02-18T13:49:26Z"

    assert module.derive_run_ts(generated_utc) == generated_utc


def test_derive_run_ts_falls_back_for_invalid_generated_utc():
    module = load_cartographer_module()
    run_ts = module.derive_run_ts("invalid-timestamp")

    assert run_ts != "invalid-timestamp"
    assert module.is_utc_iso_timestamp(run_ts)
