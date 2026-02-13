import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SENTINEL_SCRIPT = REPO_ROOT / "scripts" / "sentinel" / "append_sentinel.py"
CLASSIFIER_SCRIPT = REPO_ROOT / "scripts" / "governance" / "classify_change.py"
LEDGER_REL = Path("docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl")
OVERLAY_REL = Path("docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl")
STATE_REL = Path("scripts/sentinel/sentinel_state.json")


def run_cmd(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode}): {' '.join(args)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def git(cwd: Path, *args: str) -> str:
    return run_cmd(["git", *args], cwd=cwd).stdout.strip()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def commit_file(repo: Path, rel_path: str, content: str, message: str) -> str:
    target = repo / rel_path
    write_text(target, content)
    git(repo, "add", rel_path)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def run_sentinel(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run_cmd(
        [sys.executable, str(SENTINEL_SCRIPT), "--state", str(STATE_REL), *extra],
        cwd=repo,
        check=False,
    )


def create_prepared_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    git(repo, "init")
    git(repo, "config", "user.name", "Sentinel Test")
    git(repo, "config", "user.email", "sentinel@example.com")

    write_text(repo / "README.md", "tmp repo\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "root commit")
    root_commit = git(repo, "rev-parse", "HEAD")

    (repo / "scripts" / "governance").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CLASSIFIER_SCRIPT, repo / "scripts" / "governance" / "classify_change.py")
    commit_file(
        repo,
        "reports/path1/evidence/runs/p1_0001/RUN.md",
        "run 1\n",
        "baseline commit 1",
    )

    write_text(repo / LEDGER_REL, "")
    write_text(repo / OVERLAY_REL, "")
    write_text(
        repo / STATE_REL,
        json.dumps(
            {
                "last_processed_commit": root_commit,
                "ledger_path": LEDGER_REL.as_posix(),
                "overlay_path": OVERLAY_REL.as_posix(),
            },
            indent=2,
        )
        + "\n",
    )

    first_run = run_sentinel(repo)
    assert first_run.returncode == 0, first_run.stderr
    return repo


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_noop_rerun_produces_no_diffs(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    commit_file(
        repo,
        "reports/path1/evidence/runs/p1_0002/RUN.md",
        "run 2\n",
        "baseline commit 2",
    )

    first = run_sentinel(repo)
    assert first.returncode == 0, first.stderr

    files = [
        repo / LEDGER_REL,
        repo / OVERLAY_REL,
        repo / LEDGER_REL.with_suffix(".seal.json"),
        repo / LEDGER_REL.with_suffix(".seal.sha256"),
        repo / OVERLAY_REL.with_suffix(".seal.json"),
        repo / OVERLAY_REL.with_suffix(".seal.sha256"),
        repo / STATE_REL,
    ]
    snapshots = {path: path.read_bytes() for path in files}

    second = run_sentinel(repo)
    assert second.returncode == 0, second.stderr
    for path in files:
        assert path.read_bytes() == snapshots[path]


def test_non_append_mutation_detection(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    ledger_path = repo / LEDGER_REL

    original = ledger_path.read_text(encoding="utf-8")
    mutated = original.replace("baseline commit 1", "baseline commit x", 1)
    assert mutated != original
    write_text(ledger_path, mutated)

    verify = run_sentinel(repo, "--verify")
    assert verify.returncode != 0
    assert "non-append mutation detected" in verify.stderr


def test_duplicate_sha_detection(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    ledger_path = repo / LEDGER_REL

    lines = [line for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    lines.append(lines[0])
    write_text(ledger_path, "\n".join(lines) + "\n")

    state = read_json(repo / STATE_REL)
    state["ledger_sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    write_text(repo / STATE_REL, json.dumps(state, indent=2, sort_keys=True) + "\n")

    verify = run_sentinel(repo, "--verify")
    assert verify.returncode != 0
    assert "duplicate commit sha in ledger" in verify.stderr


def test_overlay_determinism_check(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    commit_file(
        repo,
        "reports/path1/evidence/runs/p1_0003/RUN.md",
        "run 3\n",
        "baseline commit 3",
    )

    first = run_sentinel(repo)
    assert first.returncode == 0, first.stderr
    overlay_path = repo / OVERLAY_REL
    first_overlay = overlay_path.read_bytes()

    second = run_sentinel(repo)
    assert second.returncode == 0, second.stderr
    second_overlay = overlay_path.read_bytes()
    assert second_overlay == first_overlay


def test_sentinel_only_commit_skip_and_state_advancement(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    ledger_path = repo / LEDGER_REL
    before_lines = [line for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    sentinel_only_commit = commit_file(
        repo,
        "scripts/sentinel/local_note.txt",
        "managed-only change\n",
        "sentinel only change",
    )

    run_result = run_sentinel(repo)
    assert run_result.returncode == 0, run_result.stderr

    after_lines = [line for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert after_lines == before_lines

    state = read_json(repo / STATE_REL)
    assert state["last_processed_commit"] == sentinel_only_commit

    verify = run_sentinel(repo, "--verify")
    assert verify.returncode == 0, verify.stderr


def test_overlay_seal_enforced_without_state_hashes(tmp_path: Path):
    repo = create_prepared_repo(tmp_path)
    overlay_path = repo / OVERLAY_REL

    lines = [line for line in overlay_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    write_text(overlay_path, "\n".join(lines + [lines[0]]) + "\n")

    state = read_json(repo / STATE_REL)
    state.pop("ledger_sha256", None)
    state.pop("overlay_sha256", None)
    write_text(repo / STATE_REL, json.dumps(state, indent=2, sort_keys=True) + "\n")

    verify = run_sentinel(repo, "--verify")
    assert verify.returncode != 0
    assert "non-append mutation detected" in verify.stderr
