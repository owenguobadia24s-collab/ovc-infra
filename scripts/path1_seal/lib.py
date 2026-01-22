#!/usr/bin/env python3
"""
Path1 sealing helpers (pure functions).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

MAX_FILE_BYTES = 50 * 1024 * 1024


def relpath_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_excluded(path: Path) -> bool:
    name = path.name
    if name in {".DS_Store", "Thumbs.db"}:
        return True
    if name.endswith(".tmp"):
        return True
    parts = [p.lower() for p in path.parts]
    if any(p in {"cache", ".cache", "logs"} for p in parts):
        return True
    if name.endswith(".log"):
        return True
    return False


def list_output_files(outputs_dir: Path) -> Iterable[Path]:
    for path in outputs_dir.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded(path):
            continue
        yield path


def collect_included_files(run_dir: Path) -> Tuple[List[Path], List[str], List[str]]:
    warnings: List[str] = []
    failures: List[str] = []
    included: List[Path] = []
    seen: set[str] = set()

    run_md = run_dir / "RUN.md"
    if not run_md.exists():
        failures.append("run_md_missing")
        return [], warnings, failures

    def add_path(path: Path) -> None:
        rel = relpath_posix(path, run_dir)
        if rel in seen:
            failures.append(f"duplicate_path:{rel}")
            return
        seen.add(rel)
        included.append(path)

    add_path(run_md)

    for evidence in sorted(run_dir.glob("*_evidence.md")):
        if evidence.is_file():
            add_path(evidence)

    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists() and not outputs_dir.is_dir():
        failures.append("outputs_path_not_directory")
        return included, warnings, failures
    if outputs_dir.exists():
        for out_path in sorted(list_output_files(outputs_dir)):
            try:
                size = out_path.stat().st_size
            except OSError:
                failures.append(f"stat_failed:{relpath_posix(out_path, run_dir)}")
                continue
            if size > MAX_FILE_BYTES:
                warnings.append(f"skipped_large_file:{relpath_posix(out_path, run_dir)}")
                continue
            add_path(out_path)

    if len(included) == 1:
        warnings.append("no_optional_files")

    return included, warnings, failures


def build_manifest_lines(run_dir: Path, files: List[Path]) -> List[str]:
    lines: List[str] = []
    for path in sorted(files, key=lambda p: relpath_posix(p, run_dir)):
        rel = relpath_posix(path, run_dir)
        data = path.read_bytes()
        digest = sha256_bytes(data)
        lines.append(f"{digest}  {rel}")
    return lines


def json_dumps_deterministic(payload: Dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
