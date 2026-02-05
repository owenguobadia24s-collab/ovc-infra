#!/usr/bin/env python3
"""
Evidence Envelope v0.1 helpers (stdlib-only).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Iterable, Tuple


def _utcnow_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def make_run_id(tag: str) -> str:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d__%H%M%S")
    tag = (tag or "").strip().replace(" ", "_")
    return f"{ts}__{tag}" if tag else ts


def ensure_run_dir(base_dir: Path, run_id: str) -> Path:
    run_dir = base_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    if not run_dir.is_dir():
        raise OSError(f"Run dir is not a directory: {run_dir}")
    return run_dir


def write_run_json(run_dir: Path, payload: dict) -> None:
    data = dict(payload)
    data.setdefault("run_id", run_dir.name)
    data.setdefault("created_utc", _utcnow_iso())
    run_json_path = run_dir / "run.json"
    run_json_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def seal_dir(run_dir: Path, include: Iterable[str], strict: bool = False) -> None:
    manifest_entries = []
    sha_lines = []
    seen = set()

    for rel in sorted(include):
        rel_path = Path(rel).as_posix()
        if rel_path in seen:
            continue
        seen.add(rel_path)
        fpath = run_dir / rel_path
        if not fpath.is_file():
            if strict:
                raise FileNotFoundError(rel_path)
            continue
        digest = _sha256_file(fpath)
        size = fpath.stat().st_size
        manifest_entries.append({
            "relpath": rel_path,
            "bytes": size,
            "sha256": digest,
        })
        sha_lines.append(f"{digest}  {rel_path}")

    manifest_json_path = run_dir / "manifest.json"
    manifest_json_bytes = json.dumps(
        manifest_entries, indent=2, sort_keys=False
    ).encode("utf-8") + b"\n"
    manifest_json_path.write_bytes(manifest_json_bytes)

    manifest_hash = _sha256_bytes(manifest_json_bytes)
    sha_lines.append(f"{manifest_hash}  manifest.json")

    all_lines = "\n".join(sorted(sha_lines)) + "\n"
    root_hash = _sha256_bytes(all_lines.encode("utf-8"))
    sha_lines.append(f"ROOT_SHA256  {root_hash}")

    manifest_sha_path = run_dir / "MANIFEST.sha256"
    manifest_sha_path.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


def get_git_state() -> Tuple[str | None, str | None]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        state = "clean" if status_out == "" else "dirty"
        return commit, state
    except Exception:
        return None, None
