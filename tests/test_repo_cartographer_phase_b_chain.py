import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def init_minimal_chain_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    scripts_dir = repo / "scripts" / "repo_cartographer"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for script_name in [
        "cartographer.py",
        "phase_b_latest_ok_run.py",
        "phase_b6_publish_latest_ownership_summary.py",
        "phase_b7_unknown_frontier.py",
    ]:
        shutil.copy2(REPO_ROOT / "scripts" / "repo_cartographer" / script_name, scripts_dir / script_name)

    rules_path = repo / "docs" / "baselines" / "MODULE_OWNERSHIP_RULES_v0.1.json"
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(
        json.dumps(
            {
                "ruleset_id": "MODULE_OWNERSHIP_RULES_v0.1",
                "modules": {
                    "MOD_TEST": {"display_name": "Test Module", "kind": "module"},
                    "MOD_GOV": {"display_name": "Governance Module", "kind": "module"},
                },
                "rules": [
                    {"pattern": "docs/", "type": "prefix", "owner_id": "MOD_GOV"},
                    {"pattern": "scripts/", "type": "prefix", "owner_id": "MOD_GOV"},
                    {"pattern": "src/", "type": "prefix", "owner_id": "MOD_TEST"},
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

    for cmd in [
        ["git", "init"],
        ["git", "config", "user.email", "cartographer-tests@example.com"],
        ["git", "config", "user.name", "Repo Cartographer Tests"],
        ["git", "add", "."],
        ["git", "commit", "-m", "init"],
    ]:
        proc = run_cmd(cmd, cwd=repo)
        assert proc.returncode == 0, proc.stderr or proc.stdout

    return repo


def test_phase_b_chain_success_path(tmp_path: Path):
    repo = init_minimal_chain_repo(tmp_path)
    run_id = "20260218_180000Z"

    commands = [
        [sys.executable, "scripts/repo_cartographer/cartographer.py", "run", "--run-id", run_id],
        [sys.executable, "scripts/repo_cartographer/cartographer.py", "verify"],
        [sys.executable, "scripts/repo_cartographer/phase_b_latest_ok_run.py", "--strict-verify"],
        [sys.executable, "scripts/repo_cartographer/phase_b6_publish_latest_ownership_summary.py"],
        [sys.executable, "scripts/repo_cartographer/phase_b7_unknown_frontier.py"],
    ]
    for command in commands:
        proc = run_cmd(command, cwd=repo)
        assert proc.returncode == 0, proc.stderr or proc.stdout

    pointer_path = repo / "docs" / "baselines" / "LATEST_OK_RUN_POINTER_v0.1.json"
    ownership_path = repo / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.md"
    receipt_path = repo / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.receipt.json"
    frontier_json_path = repo / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json"
    frontier_txt_path = repo / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt"

    for path in [pointer_path, ownership_path, receipt_path, frontier_json_path, frontier_txt_path]:
        assert path.exists()

    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert pointer["LATEST_OK_RUN_ID"] == run_id
    assert pointer["ok"] is True
    assert pointer["ledger_manifest_match"] is True
    assert pointer["ledger_seal_match"] is True
    assert pointer["manifest_sidecar_match"] is True
    assert pointer["seal_sidecar_match"] is True


def test_phase_b_chain_fail_closed_stops_before_consumers(tmp_path: Path):
    repo = init_minimal_chain_repo(tmp_path)
    run_id = "20260218_180100Z"

    step_1 = run_cmd(
        [sys.executable, "scripts/repo_cartographer/cartographer.py", "run", "--run-id", run_id],
        cwd=repo,
    )
    assert step_1.returncode == 0, step_1.stderr or step_1.stdout

    step_2 = run_cmd([sys.executable, "scripts/repo_cartographer/cartographer.py", "verify"], cwd=repo)
    assert step_2.returncode == 0, step_2.stderr or step_2.stdout

    sidecar_path = repo / "artifacts" / "repo_cartographer" / run_id / "MANIFEST.sha256"
    sidecar_path.write_text(f"{'0' * 64}  MANIFEST.json\n", encoding="utf-8")

    step_3 = run_cmd(
        [sys.executable, "scripts/repo_cartographer/phase_b_latest_ok_run.py", "--strict-verify"],
        cwd=repo,
    )
    assert step_3.returncode == 2

    assert not (repo / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.md").exists()
    assert not (repo / "docs" / "REPO_MAP" / "LATEST_OWNERSHIP_SUMMARY.receipt.json").exists()
    assert not (repo / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json").exists()
    assert not (repo / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt").exists()
