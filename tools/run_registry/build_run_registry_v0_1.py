#!/usr/bin/env python3
"""
Phase 2.1 — Run Registry Builder v0.1

Read-only scan of .codex/RUNS/ folders. Produces:
  - RUN_REGISTRY_v0_1.jsonl   (one JSON object per indexed run)
  - RUN_REGISTRY_v0_1.schema.json
  - run.json                  (evidence envelope for the registry-build itself)
  - manifest.json + MANIFEST.sha256  (sealing)

Hard constraints:
  - No mutation of any existing run folder.
  - No network / DB calls.
  - Deterministic output given the same filesystem state.
  - Only stdlib — no third-party deps.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGISTRY_VERSION = "0.1"
RUNS_DIR = Path(".codex/RUNS")
RUN_ROOTS = [
    Path(".codex/RUNS"),
    Path("reports/runs"),
    Path("reports/path1/evidence/runs"),
]

KNOWN_RUN_JSON_KEYS = {
    "created_utc", "created_at",
    "git_commit", "working_tree_state",
    "option", "operation_id", "run_type",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def utcnow_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def make_run_id(tag: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d__%H%M%S")
    return f"{ts}__{tag}"


def read_json_safe(path: Path) -> tuple[Any | None, str | None]:
    """Return (parsed, None) on success or (None, warning_str) on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:
        return None, f"Failed to parse {path.name}: {exc}"


def extract_root_sha256(manifest_path: Path) -> str | None:
    """Extract ROOT_SHA256 value from MANIFEST.sha256 if present."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ROOT_SHA256"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[-1]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------


def list_files_in_folder(folder: Path) -> list[dict]:
    """Return sorted list of {relpath, bytes} for all files (not dirs) in folder."""
    entries = []
    try:
        for item in sorted(folder.iterdir()):
            if item.is_file():
                try:
                    size = item.stat().st_size
                except OSError:
                    size = -1
                entries.append({"relpath": item.name, "bytes": size})
    except OSError:
        pass
    return entries


def index_run_folder(folder: Path, run_root: str) -> dict:
    """Build a single registry record for one run folder."""
    run_id = folder.name
    run_root_norm = Path(run_root).as_posix()
    run_path = f"{run_root_norm}/{run_id}/"
    run_key = f"{run_root_norm}::{run_id}"
    warnings: list[str] = []

    has_run_json = (folder / "run.json").is_file()
    has_manifest_sha256 = (folder / "MANIFEST.sha256").is_file()
    has_manifest_json = (folder / "manifest.json").is_file()

    # Defaults
    created_utc = None
    run_type = None
    option = None
    operation_id = None
    git_commit = None
    working_tree_state = None

    if has_run_json:
        data, warn = read_json_safe(folder / "run.json")
        if warn:
            warnings.append(warn)
        if isinstance(data, dict):
            created_utc = data.get("created_utc") or data.get("created_at") or None
            run_type = data.get("run_type") or None
            option = data.get("option") or None
            operation_id = data.get("operation_id") or None
            git_commit = data.get("git_commit") or None
            working_tree_state = data.get("working_tree_state") or None
        elif data is not None:
            warnings.append("run.json top-level is not an object")
    else:
        warnings.append("missing run.json")

    manifest_root_sha256 = None
    if has_manifest_sha256:
        manifest_root_sha256 = extract_root_sha256(folder / "MANIFEST.sha256")
    else:
        warnings.append("missing MANIFEST.sha256")

    if not has_manifest_json:
        warnings.append("missing manifest.json")

    files = list_files_in_folder(folder)

    return {
        "registry_version": REGISTRY_VERSION,
        "run_id": run_id,
        "run_root": run_root_norm,
        "run_key": run_key,
        "run_path": run_path,
        "created_utc": created_utc,
        "run_type": run_type,
        "option": option,
        "operation_id": operation_id,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "has_run_json": has_run_json,
        "has_manifest_sha256": has_manifest_sha256,
        "has_manifest_json": has_manifest_json,
        "manifest_root_sha256": manifest_root_sha256,
        "files": files,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

REGISTRY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "RUN_REGISTRY_v0_1 Record",
    "description": "Schema for one line of RUN_REGISTRY_v0_1.jsonl",
    "type": "object",
    "required": [
        "registry_version",
        "run_id",
        "run_root",
        "run_key",
        "run_path",
        "has_run_json",
        "has_manifest_sha256",
        "has_manifest_json",
        "files",
        "warnings",
    ],
    "properties": {
        "registry_version": {"type": "string", "const": "0.1"},
        "run_id": {"type": "string"},
        "run_root": {"type": "string"},
        "run_key": {"type": "string"},
        "run_path": {"type": "string"},
        "created_utc": {"type": ["string", "null"]},
        "run_type": {"type": ["string", "null"]},
        "option": {"type": ["string", "null"]},
        "operation_id": {"type": ["string", "null"]},
        "git_commit": {"type": ["string", "null"]},
        "working_tree_state": {"type": ["string", "null"]},
        "has_run_json": {"type": "boolean"},
        "has_manifest_sha256": {"type": "boolean"},
        "has_manifest_json": {"type": "boolean"},
        "manifest_root_sha256": {"type": ["string", "null"]},
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["relpath", "bytes"],
                "properties": {
                    "relpath": {"type": "string"},
                    "bytes": {"type": "integer"},
                },
                "additionalProperties": False,
            },
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Sealing
# ---------------------------------------------------------------------------


def build_manifest(output_dir: Path, file_names: list[str]) -> None:
    """Create manifest.json and MANIFEST.sha256 for the registry-build run."""
    manifest_entries = []
    sha_lines = []

    for name in sorted(file_names):
        fpath = output_dir / name
        if not fpath.is_file():
            continue
        h = sha256_file(fpath)
        size = fpath.stat().st_size
        manifest_entries.append({
            "relpath": name,
            "bytes": size,
            "sha256": h,
        })
        sha_lines.append(f"{h}  {name}")

    # manifest.json
    manifest_json_path = output_dir / "manifest.json"
    manifest_json_bytes = json.dumps(manifest_entries, indent=2, sort_keys=False).encode("utf-8") + b"\n"
    manifest_json_path.write_bytes(manifest_json_bytes)

    # include manifest.json itself in MANIFEST.sha256
    mj_hash = sha256_bytes(manifest_json_bytes)
    sha_lines.append(f"{mj_hash}  manifest.json")

    # ROOT_SHA256 = hash of all sha lines joined
    all_lines = "\n".join(sorted(sha_lines)) + "\n"
    root_hash = sha256_bytes(all_lines.encode("utf-8"))
    sha_lines.append(f"ROOT_SHA256  {root_hash}")

    manifest_sha_path = output_dir / "MANIFEST.sha256"
    manifest_sha_path.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not RUNS_DIR.is_dir():
        print(f"ERROR: {RUNS_DIR} not found.", file=sys.stderr)
        sys.exit(1)

    # Create the output run folder
    build_tag = "run_registry_build"
    run_id = make_run_id(build_tag)
    output_dir = RUNS_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    created_utc = utcnow_iso()

    # Enumerate run folders (immediate children only) across run roots
    records: list[dict] = []
    for root in RUN_ROOTS:
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if not entry.is_dir():
                continue
            if root == RUNS_DIR and entry.name == run_id:
                continue  # skip self
            rec = index_run_folder(entry, root.as_posix())
            records.append(rec)

    # Sort: by created_utc ascending (nulls last), then by run_id
    def sort_key(r: dict) -> tuple:
        c = r["created_utc"]
        if c is not None:
            return (r["run_root"], 0, c, r["run_id"])
        return (r["run_root"], 1, "", r["run_id"])

    records.sort(key=sort_key)

    # --- Write RUN_REGISTRY_v0_1.jsonl ---
    jsonl_path = output_dir / "RUN_REGISTRY_v0_1.jsonl"
    lines = []
    for rec in records:
        lines.append(json.dumps(rec, separators=(",", ":"), sort_keys=False))
    jsonl_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- Write schema ---
    schema_path = output_dir / "RUN_REGISTRY_v0_1.schema.json"
    schema_path.write_text(
        json.dumps(REGISTRY_SCHEMA, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    # --- Write run.json for the registry-build itself ---
    git_commit = None
    working_tree_state = None
    try:
        import subprocess
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        working_tree_state = "clean" if status_out == "" else "dirty"
    except Exception:
        pass

    run_json_data = {
        "run_id": run_id,
        "created_utc": created_utc,
        "run_type": "run_registry_build",
        "registry_version": REGISTRY_VERSION,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "outputs": [
            "RUN_REGISTRY_v0_1.jsonl",
            "RUN_REGISTRY_v0_1.schema.json",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
    }
    run_json_path = output_dir / "run.json"
    run_json_path.write_text(
        json.dumps(run_json_data, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    # --- Seal with manifest ---
    build_manifest(output_dir, [
        "RUN_REGISTRY_v0_1.jsonl",
        "RUN_REGISTRY_v0_1.schema.json",
        "run.json",
    ])

    # --- Summary ---
    total = len(records)
    missing_run_json = sum(1 for r in records if not r["has_run_json"])
    missing_manifests = sum(
        1 for r in records
        if not r["has_manifest_sha256"] and not r["has_manifest_json"]
    )

    print("=" * 60)
    print("  Phase 2.1 — Run Registry Build Complete")
    print("=" * 60)
    print(f"  total_runs_indexed:     {total}")
    print(f"  runs_missing_run_json:  {missing_run_json}")
    print(f"  runs_missing_manifests: {missing_manifests}")
    print(f"  output_run_folder:      {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
