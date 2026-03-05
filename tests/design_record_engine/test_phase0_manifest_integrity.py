from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

SELF_PLACEHOLDER = "0" * 64


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _phase0_script() -> Path:
    return _repo_root() / "scripts" / "design_record_engine" / "phase0_chat_seal.ps1"


def _fixture_export_root() -> Path:
    return _repo_root() / "tests" / "fixtures" / "chat_export_golden" / "2026-02-21_export_raw"


def _run_phase0(export_root: Path, verify_only: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [
        "pwsh",
        "-NoProfile",
        "-File",
        str(_phase0_script()),
        "-ExportRoot",
        str(export_root),
    ]
    if verify_only:
        cmd.append("-VerifyOnly")
    return subprocess.run(cmd, cwd=str(_repo_root()), capture_output=True, text=True)


def _copy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "export"
    shutil.copytree(_fixture_export_root(), target)
    return target


def _manifest_entries(export_root: Path) -> list[tuple[str, str]]:
    manifest_path = export_root / "MANIFEST.sha256"
    entries: list[tuple[str, str]] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64}) (.+)", line)
        assert match is not None, f"Invalid manifest line: {line!r}"
        entries.append((match.group(1), match.group(2)))
    return entries


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_success(process: subprocess.CompletedProcess[str]) -> None:
    assert process.returncode == 0, f"stdout={process.stdout}\nstderr={process.stderr}"


def test_phase0_manifest_sorted_self_hash_and_verify_only(tmp_path: Path) -> None:
    export_root = _copy_fixture(tmp_path)

    _assert_success(_run_phase0(export_root=export_root))

    entries = _manifest_entries(export_root)
    paths = [path for _, path in entries]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert "MANIFEST.sha256" in paths
    assert "EXPORT_METADATA.json" in paths
    assert "SEAL_README.md" in paths
    assert all("\\" not in path for path in paths)

    entry_map = {path: digest for digest, path in entries}
    for path in paths:
        if path == "MANIFEST.sha256":
            continue
        actual = _sha256_file(export_root / path)
        assert actual == entry_map[path]

    zeroed = dict(entry_map)
    zeroed["MANIFEST.sha256"] = SELF_PLACEHOLDER
    zeroed_text = "".join(f"{zeroed[path]} {path}\n" for path in sorted(zeroed))
    assert hashlib.sha256(zeroed_text.encode("utf-8")).hexdigest() == entry_map["MANIFEST.sha256"]

    _assert_success(_run_phase0(export_root=export_root, verify_only=True))


def test_phase0_verify_only_fails_on_tamper(tmp_path: Path) -> None:
    export_root = _copy_fixture(tmp_path)

    _assert_success(_run_phase0(export_root=export_root))

    target = export_root / "conversations-000.json"
    target.write_text(target.read_text(encoding="utf-8") + "\nTAMPER\n", encoding="utf-8", newline="\n")

    process = _run_phase0(export_root=export_root, verify_only=True)
    assert process.returncode != 0


def test_phase0_verify_only_is_read_only(tmp_path: Path) -> None:
    export_root = _copy_fixture(tmp_path)

    _assert_success(_run_phase0(export_root=export_root))

    tracked = ["MANIFEST.sha256", "EXPORT_METADATA.json", "SEAL_README.md"]
    before_bytes = {name: (export_root / name).read_bytes() for name in tracked}
    before_mtime = {name: (export_root / name).stat().st_mtime_ns for name in tracked}

    _assert_success(_run_phase0(export_root=export_root, verify_only=True))

    after_bytes = {name: (export_root / name).read_bytes() for name in tracked}
    after_mtime = {name: (export_root / name).stat().st_mtime_ns for name in tracked}
    assert before_bytes == after_bytes
    assert before_mtime == after_mtime
