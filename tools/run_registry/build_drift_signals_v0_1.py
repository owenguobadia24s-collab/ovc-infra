#!/usr/bin/env python3
"""
Phase 2.1 — Drift Signals Builder v0.1

Read-only derivation of drift signals:
- schema version vs expected
- threshold pack version vs expected
- canon hash vs working tree
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple


DRIFT_VERSION = "0.1"
RUNS_DIR = Path(".codex/RUNS")
EXPECTED_VERSIONS_PATH = Path("docs/governance/EXPECTED_VERSIONS_v0_1.json")

STATUS_TABLE_FILENAME = "OPERATION_STATUS_TABLE_v0_1.json"
REGISTRY_FILENAME = "RUN_REGISTRY_v0_1.jsonl"

THRESHOLD_EXPECTED_SOURCES = [
    Path("configs/threshold_packs/state_plane_v0_2_default_v1.json"),
    Path("configs/threshold_packs/c3_regime_trend_v1.json"),
    Path("configs/threshold_packs/c3_example_pack_v1.json"),
    Path("docs/runbooks/option_threshold_registry_runbook.md"),
]
THRESHOLD_OBSERVED_SOURCES = THRESHOLD_EXPECTED_SOURCES

VERSION_PATTERNS = [
    re.compile(r"(?im)^\*\*Version\*\*:\s*([A-Za-z0-9_.\-]+)"),
    re.compile(r"(?im)^Version:\s*([A-Za-z0-9_.\-]+)"),
    re.compile(r"(?im)\bSCHEMA_VERSION\b.*?['\"]([A-Za-z0-9_.\-]+)['\"]"),
    re.compile(r"(?im)\b[A-Z0-9_]*_VERSION\b\s*=\s*['\"]([A-Za-z0-9_.\-]+)['\"]"),
]


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


def build_manifest(output_dir: Path, file_names: list[str]) -> None:
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

    manifest_json_path = output_dir / "manifest.json"
    manifest_json_bytes = json.dumps(manifest_entries, indent=2, sort_keys=False).encode("utf-8") + b"\n"
    manifest_json_path.write_bytes(manifest_json_bytes)

    mj_hash = sha256_bytes(manifest_json_bytes)
    sha_lines.append(f"{mj_hash}  manifest.json")

    all_lines = "\n".join(sorted(sha_lines)) + "\n"
    root_hash = sha256_bytes(all_lines.encode("utf-8"))
    sha_lines.append(f"ROOT_SHA256  {root_hash}")

    manifest_sha_path = output_dir / "MANIFEST.sha256"
    manifest_sha_path.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


def find_latest_status_table(runs_dir: Path) -> Optional[Path]:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "op_status_table_build" in child.name:
            status_path = child / STATUS_TABLE_FILENAME
            if status_path.is_file():
                candidates.append(status_path)
    return candidates[-1] if candidates else None


def find_latest_registry(runs_dir: Path) -> Optional[Path]:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "run_registry_build" in child.name:
            jsonl = child / REGISTRY_FILENAME
            if jsonl.is_file():
                candidates.append(jsonl)
    return candidates[-1] if candidates else None


def git_commit_and_state() -> Tuple[Optional[str], Optional[str]]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        working_tree_state = "clean" if status_out == "" else "dirty"
        return commit, working_tree_state
    except Exception:
        return None, None


def iter_tracked_files() -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z"])
    paths = output.split(b"\x00")
    files = [p.decode("utf-8", errors="strict") for p in paths if p]
    return files


def canon_tree_hash(repo_root: Path) -> str:
    lines = []
    for rel in iter_tracked_files():
        path = repo_root / rel
        digest = sha256_file(path)
        norm_rel = rel.replace("\\", "/")
        lines.append(f"{digest} {norm_rel}")
    lines.sort()
    joined = "\n".join(lines) + "\n"
    return sha256_bytes(joined.encode("utf-8"))


def extract_version_from_text(text: str) -> Optional[str]:
    for pattern in VERSION_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def extract_version_from_json(path: Path) -> Optional[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(data, dict):
        value = data.get("version")
        if isinstance(value, str):
            return value
    return None


def scan_version_source(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    if path.is_file():
        if path.suffix.lower() == ".json":
            version = extract_version_from_json(path)
            if version:
                return version
        text = path.read_text(encoding="utf-8", errors="ignore")
        return extract_version_from_text(text)
    if path.is_dir():
        files = sorted([p for p in path.rglob("*") if p.is_file()])
        for file_path in files:
            version = scan_version_source(file_path)
            if version:
                return version
    return None


def find_expected_version(sources: Iterable[Path]) -> tuple[Optional[str], Optional[str]]:
    for path in sources:
        version = scan_version_source(path)
        if version:
            return version, path.as_posix()
    return None, None


def load_expected_versions(path: Path) -> tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, None, None
    if not isinstance(data, dict):
        return None, None, None
    expected = data.get("expected")
    if not isinstance(expected, dict):
        return None, None, None
    schema_version = expected.get("schema_version")
    if not isinstance(schema_version, str):
        schema_version = None
    threshold_version = expected.get("threshold_pack_version")
    if not isinstance(threshold_version, str):
        threshold_version = None
    return schema_version, threshold_version, path.as_posix()


def observed_registry_version(registry_path: Optional[Path]) -> Optional[str]:
    if registry_path is None or not registry_path.exists():
        return None
    with registry_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            version = rec.get("registry_version")
            if isinstance(version, str):
                return version
    return None


def observed_status_version(status_path: Optional[Path]) -> Optional[str]:
    if status_path is None or not status_path.exists():
        return None
    try:
        records = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(records, list):
        for rec in records:
            version = rec.get("status_version")
            if isinstance(version, str):
                return version
    return None


def run_envelope_version() -> Optional[str]:
    path = Path("docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md")
    return "0.1" if path.exists() else None


def main() -> int:
    if not RUNS_DIR.is_dir():
        print(f"ERROR: {RUNS_DIR} not found.", file=sys.stderr)
        return 1

    repo_root = Path(".").resolve()
    run_id = make_run_id("drift_signals_build")
    output_dir = RUNS_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    generated_utc = utcnow_iso()
    git_commit, working_tree_state = git_commit_and_state()
    tree_hash = canon_tree_hash(repo_root)

    warnings = []

    expected_schema_version = None
    expected_threshold_version = None
    expected_versions_source = EXPECTED_VERSIONS_PATH.as_posix()
    loaded_schema, loaded_threshold, loaded_source = load_expected_versions(EXPECTED_VERSIONS_PATH)
    if loaded_source is None:
        warnings.append("expected_versions_missing_or_unreadable")
    expected_schema_version = loaded_schema
    expected_threshold_version = loaded_threshold
    if expected_threshold_version is None:
        warnings.append("expected_threshold_null")

    status_path = find_latest_status_table(RUNS_DIR)
    registry_path = find_latest_registry(RUNS_DIR)

    observed_registry = observed_registry_version(registry_path) or "0.1"
    observed_status = observed_status_version(status_path) or "0.1"
    observed_envelope = run_envelope_version()
    observed_threshold, _ = find_expected_version(THRESHOLD_OBSERVED_SOURCES)
    if observed_threshold is None:
        warnings.append("observed_threshold_version_not_found")

    schema_drift_computed = (
        expected_schema_version is not None
        and observed_registry is not None
        and observed_status is not None
        and observed_envelope is not None
    )
    schema_drift: bool | None = None
    if schema_drift_computed:
        observed_values = [observed_registry, observed_status, observed_envelope]
        schema_drift = any(v != expected_schema_version for v in observed_values)
    else:
        warnings.append("schema_drift_unknown")

    threshold_drift_computed = (
        expected_threshold_version is not None and observed_threshold is not None
    )
    threshold_drift: bool | None = None
    if threshold_drift_computed:
        threshold_drift = expected_threshold_version != observed_threshold
    else:
        warnings.append("threshold_drift_unknown")

    drift_payload = {
        "drift_version": DRIFT_VERSION,
        "expected_versions_source": expected_versions_source,
        "generated_utc": generated_utc,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "canon_tree_hash": tree_hash,
        "expected": {
            "schema_version": {
                "expected": expected_schema_version,
                "computed": schema_drift_computed,
                "observed": {
                    "run_registry": observed_registry,
                    "op_status_table": observed_status,
                    "run_envelope": observed_envelope,
                },
                "drift": schema_drift,
                "source_path": expected_versions_source,
            },
            "threshold_pack": {
                "expected": expected_threshold_version,
                "computed": threshold_drift_computed,
                "observed": observed_threshold,
                "drift": threshold_drift,
                "source_path": expected_versions_source,
            },
        },
        "system_drift": {
            "canon_dirty": working_tree_state == "dirty",
            "schema_drift": schema_drift,
            "threshold_drift": threshold_drift,
            "threshold_drift_computed": threshold_drift_computed,
        },
        "op_drift_policy": {
            "op_drift_requires_evidence": True,
            "rules": [
                "mark op_drift true if last_run.git_commit != current git_commit (when both present)",
                "mark op_drift true if last_run.working_tree_state == 'dirty' (evidence captured dirty)",
                "do not mark op_drift based on system_drift alone",
            ],
        },
        "warnings": warnings,
    }

    drift_path = output_dir / "DRIFT_SIGNALS_v0_1.json"
    drift_path.write_text(json.dumps(drift_payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "DRIFT_SIGNALS_v0_1",
        "type": "object",
        "required": [
            "drift_version",
            "expected_versions_source",
            "generated_utc",
            "git_commit",
            "working_tree_state",
            "canon_tree_hash",
            "expected",
            "system_drift",
            "op_drift_policy",
            "warnings",
        ],
        "properties": {
            "drift_version": {"type": "string"},
            "expected_versions_source": {"type": "string"},
            "generated_utc": {"type": "string"},
            "git_commit": {"type": ["string", "null"]},
            "working_tree_state": {"type": ["string", "null"]},
            "canon_tree_hash": {"type": "string"},
            "expected": {
                "type": "object",
                "required": ["schema_version", "threshold_pack"],
                "properties": {
                    "schema_version": {
                        "type": "object",
                        "required": ["expected", "computed", "observed", "drift", "source_path"],
                        "properties": {
                            "expected": {"type": ["string", "null"]},
                            "computed": {"type": "boolean"},
                            "observed": {
                                "type": "object",
                                "required": ["run_registry", "op_status_table", "run_envelope"],
                                "properties": {
                                    "run_registry": {"type": ["string", "null"]},
                                    "op_status_table": {"type": ["string", "null"]},
                                    "run_envelope": {"type": ["string", "null"]},
                                },
                                "additionalProperties": False,
                            },
                            "drift": {"type": ["boolean", "null"]},
                            "source_path": {"type": ["string", "null"]},
                        },
                        "additionalProperties": False,
                    },
                    "threshold_pack": {
                        "type": "object",
                        "required": ["expected", "computed", "observed", "drift", "source_path"],
                        "properties": {
                            "expected": {"type": ["string", "null"]},
                            "computed": {"type": "boolean"},
                            "observed": {"type": ["string", "null"]},
                            "drift": {"type": ["boolean", "null"]},
                            "source_path": {"type": ["string", "null"]},
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
            "system_drift": {
                "type": "object",
                "required": [
                    "canon_dirty",
                    "schema_drift",
                    "threshold_drift",
                    "threshold_drift_computed",
                ],
                "properties": {
                    "canon_dirty": {"type": "boolean"},
                    "schema_drift": {"type": ["boolean", "null"]},
                    "threshold_drift": {"type": ["boolean", "null"]},
                    "threshold_drift_computed": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            "op_drift_policy": {
                "type": "object",
                "required": ["op_drift_requires_evidence", "rules"],
                "properties": {
                    "op_drift_requires_evidence": {"type": "boolean"},
                    "rules": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "warnings": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "additionalProperties": False,
    }

    schema_path = output_dir / "DRIFT_SIGNALS_v0_1.schema.json"
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    run_json_payload = {
        "run_id": run_id,
        "created_utc": generated_utc,
        "run_type": "drift_signals_build",
        "option": "QA",
        "operation_id": None,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "outputs": [
            "DRIFT_SIGNALS_v0_1.json",
            "DRIFT_SIGNALS_v0_1.schema.json",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
    }
    run_json_path = output_dir / "run.json"
    run_json_path.write_text(json.dumps(run_json_payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    build_manifest(output_dir, [
        "DRIFT_SIGNALS_v0_1.json",
        "DRIFT_SIGNALS_v0_1.schema.json",
        "run.json",
    ])

    print("=" * 60)
    print("  Phase 2.1 — Drift Signals Build Complete")
    print("=" * 60)
    print(f"  output_run_folder:      {output_dir}")
    print(f"  canon_tree_hash:        {tree_hash}")
    print(f"  working_tree_state:     {working_tree_state}")
    print(f"  schema_drift:           {schema_drift}")
    print(f"  threshold_drift:        {threshold_drift}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
