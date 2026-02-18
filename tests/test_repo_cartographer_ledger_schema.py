import hashlib
import importlib.util
import json
import subprocess
import sys
from types import SimpleNamespace
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


def run_cmd(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8")


def init_minimal_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    run_cmd(["git", "init"], cwd=repo)
    run_cmd(["git", "config", "user.email", "cartographer-tests@example.com"], cwd=repo)
    run_cmd(["git", "config", "user.name", "Repo Cartographer Tests"], cwd=repo)

    rules_path = repo / "docs" / "baselines" / "MODULE_OWNERSHIP_RULES_v0.1.json"
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(
        json.dumps(
            {
                "ruleset_id": "MODULE_OWNERSHIP_RULES_v0.1",
                "modules": {
                    "MOD_TEST": {
                        "display_name": "Test Module",
                        "kind": "module",
                    }
                },
                "rules": [
                    {
                        "pattern": "src/",
                        "type": "prefix",
                        "owner_id": "MOD_TEST",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    tracked_file = repo / "src" / "hello.py"
    tracked_file.parent.mkdir(parents=True, exist_ok=True)
    tracked_file.write_text("print('hello')\n", encoding="utf-8")

    run_cmd(["git", "add", "."], cwd=repo)
    run_cmd(["git", "commit", "-m", "init"], cwd=repo)
    return repo


def read_ledger_rows(repo_root: Path) -> list[dict]:
    ledger_path = repo_root / "docs" / "catalogs" / "REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl"
    if not ledger_path.exists():
        return []
    rows: list[dict] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


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


def test_cmd_run_appends_manifest_and_seal_hashes_with_expected_values(tmp_path: Path):
    module = load_cartographer_module()
    repo_root = init_minimal_git_repo(tmp_path)
    run_id = "20260218_170000Z"
    args = SimpleNamespace(
        rules="docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json",
        state="scripts/repo_cartographer/cartographer_state.json",
        run_id=run_id,
    )

    rc = module.cmd_run(repo_root, args)
    assert rc == 0

    rows = read_ledger_rows(repo_root)
    row = next(r for r in rows if r.get("run_id") == run_id)

    run_dir = repo_root / "artifacts" / "repo_cartographer" / run_id
    manifest_sha = hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest()
    seal_sha = hashlib.sha256((run_dir / "SEAL.json").read_bytes()).hexdigest()

    assert row["manifest_sha256"] == manifest_sha
    assert row["seal_sha256"] == seal_sha


def test_cmd_run_returns_2_and_writes_no_ledger_row_when_manifest_unreadable(
    tmp_path: Path,
    monkeypatch,
):
    module = load_cartographer_module()
    repo_root = init_minimal_git_repo(tmp_path)
    run_id = "20260218_170100Z"
    args = SimpleNamespace(
        rules="docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json",
        state="scripts/repo_cartographer/cartographer_state.json",
        run_id=run_id,
    )

    manifest_path = (repo_root / "artifacts" / "repo_cartographer" / run_id / "MANIFEST.json").resolve()
    original_read_bytes = module.Path.read_bytes
    read_counts: dict[Path, int] = {}

    def fake_read_bytes(path_obj):
        resolved = path_obj.resolve()
        read_counts[resolved] = read_counts.get(resolved, 0) + 1
        if resolved == manifest_path and read_counts[resolved] >= 3:
            return b""
        return original_read_bytes(path_obj)

    monkeypatch.chdir(repo_root)
    monkeypatch.setattr(module.Path, "read_bytes", fake_read_bytes)

    rc = module.main(
        [
            "--rules",
            "docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json",
            "--state",
            "scripts/repo_cartographer/cartographer_state.json",
            "run",
            "--run-id",
            run_id,
        ]
    )
    assert rc == 2

    rows = read_ledger_rows(repo_root)
    assert all(row.get("run_id") != run_id for row in rows)
