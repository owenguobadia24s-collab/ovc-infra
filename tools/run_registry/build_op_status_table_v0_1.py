#!/usr/bin/env python3
"""
Phase 2.1 — Operation Status Table Builder v0.1

Read-only derivation from:
  - RUN_REGISTRY_v0_1.jsonl  (most recent registry build)
  - OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md
  - OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md

Produces per-OP health/freshness/drift status table.

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
import math
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_VERSION = "0.1"
RUNS_DIR = Path(".codex/RUNS")
CATALOG_PATH = Path("OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md")
MATRIX_PATH = Path("OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md")
DRIFT_FILENAME = "DRIFT_SIGNALS_v0_1.json"

# Canonical options in sort order
CANONICAL_OPTIONS = ("A", "B", "C", "D", "QA")

# ---------------------------------------------------------------------------
# Shared helpers (mirrors build_run_registry_v0_1.py patterns)
# ---------------------------------------------------------------------------


def utcnow_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


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
    """Create manifest.json and MANIFEST.sha256 for this build run."""
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


# ---------------------------------------------------------------------------
# Parse catalog (extract canonical ops)
# ---------------------------------------------------------------------------

def parse_catalog(path: Path) -> list[dict]:
    """
    Extract canonical operations from the Allowed Operations Catalog.
    Returns list of {operation_id, option, operation_name} sorted by option then id.
    Stops at NON_CANONICAL section.
    """
    text = path.read_text(encoding="utf-8")
    ops: list[dict] = []

    # Match ### OP-XXX: Name lines
    # Stop processing at NON_CANONICAL section
    lines = text.split("\n")
    current_option: str | None = None
    in_non_canonical = False

    for line in lines:
        stripped = line.strip()

        # Detect NON_CANONICAL boundary
        if "NON_CANONICAL" in stripped and stripped.startswith("#"):
            in_non_canonical = True
            break

        # Detect Option headers: ## Option A — ...
        option_match = re.match(r"^##\s+Option\s+(\w+)\s", stripped)
        if option_match:
            current_option = option_match.group(1)
            continue

        # Detect operation headers: ### OP-XXX: Name
        op_match = re.match(r"^###\s+(OP-\w+):\s+(.+)$", stripped)
        if op_match:
            op_id = op_match.group(1)
            op_name = op_match.group(2).strip()

            # Also look for explicit "Operation ID:" and "Option:" lines below
            # but use the header as primary source
            ops.append({
                "operation_id": op_id,
                "option": current_option,
                "operation_name": op_name,
            })
            continue

        # Fallback: explicit Operation ID line (overrides if found)
        if stripped.startswith("Operation ID:") and ops:
            explicit_id = stripped.split(":", 1)[1].strip()
            if explicit_id == ops[-1]["operation_id"]:
                pass  # consistent — no action
            # We trust the header match

        if stripped.startswith("Option:") and ops:
            explicit_opt = stripped.split(":", 1)[1].strip()
            ops[-1]["option"] = explicit_opt

    return ops


# ---------------------------------------------------------------------------
# Parse coverage matrix
# ---------------------------------------------------------------------------

def parse_coverage_matrix(path: Path) -> dict[str, str]:
    """
    Extract coverage levels from the Enforcement Coverage Matrix.
    Returns {operation_id: coverage_level} e.g. {"OP-A01": "C3"}.
    """
    text = path.read_text(encoding="utf-8")
    coverage: dict[str, str] = {}

    # Match table rows: | OP-XXX | Option | Surfaces | C# | Justification |
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # cells[0] is empty (before first |), cells[-1] is empty (after last |)
        if len(cells) < 6:
            continue
        op_id = cells[1]
        if not op_id.startswith("OP-"):
            continue
        coverage_cell = cells[4]
        cov_match = re.match(r"(C\d)", coverage_cell)
        if cov_match:
            coverage[op_id] = cov_match.group(1)

    return coverage


# ---------------------------------------------------------------------------
# Load registry
# ---------------------------------------------------------------------------

def find_latest_registry(runs_dir: Path) -> Path | None:
    """Find the most recent RUN_REGISTRY_v0_1.jsonl file."""
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "run_registry_build" in child.name:
            jsonl = child / "RUN_REGISTRY_v0_1.jsonl"
            if jsonl.is_file():
                candidates.append(jsonl)
    return candidates[-1] if candidates else None


def find_latest_drift_signals(runs_dir: Path) -> Path | None:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "drift_signals_build" in child.name:
            drift_path = child / DRIFT_FILENAME
            if drift_path.is_file():
                candidates.append(drift_path)
    return candidates[-1] if candidates else None


def load_registry(jsonl_path: Path) -> list[dict]:
    """Load all records from JSONL."""
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_registry_index(records: list[dict]) -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for rec in records:
        if not rec.get("has_run_json"):
            continue
        op_id = rec.get("operation_id")
        run_id = rec.get("run_id")
        if not op_id or not run_id:
            continue
        key = (op_id, run_id)
        current = index.get(key)
        if current is None:
            index[key] = rec
            continue
        current_key = (current.get("created_utc") or "", current.get("run_key") or "")
        new_key = (rec.get("created_utc") or "", rec.get("run_key") or "")
        if new_key > current_key:
            index[key] = rec
    return index


# ---------------------------------------------------------------------------
# Status derivation
# ---------------------------------------------------------------------------

def compute_staleness_days(last_utc: str | None, now: datetime.datetime) -> int | None:
    """Compute floor((now - last) / 86400) or None."""
    if last_utc is None:
        return None
    try:
        last_dt = datetime.datetime.fromisoformat(last_utc.replace("Z", "+00:00"))
        delta = now - last_dt
        return int(math.floor(delta.total_seconds() / 86400))
    except Exception:
        return None


def derive_op_status(
    op: dict,
    coverage_map: dict[str, str],
    registry_records: list[dict],
    now: datetime.datetime,
) -> dict:
    """Derive status record for a single canonical operation."""
    op_id = op["operation_id"]
    option = op["option"]
    op_name = op["operation_name"]
    warnings: list[str] = []

    # Coverage level from matrix
    coverage_level = coverage_map.get(op_id, "C0")

    # Find attributable runs: operation_id must match exactly and has_run_json must be true
    attributable = [
        r for r in registry_records
        if r.get("has_run_json") and r.get("operation_id") == op_id
    ]

    # Check if any runs exist at all (legacy/untyped)
    total_registry_runs = len(registry_records)

    # Determine run_evidence_state
    if len(attributable) > 0:
        run_evidence_state = "OBSERVED"
    elif total_registry_runs > 0:
        # Runs exist in the registry but none are attributable to this op
        # Only flag LEGACY_ONLY if there are untyped runs (no operation_id)
        has_untyped = any(
            r.get("has_run_json") and r.get("operation_id") is None
            for r in registry_records
        )
        has_legacy = any(not r.get("has_run_json") for r in registry_records)
        if has_untyped or has_legacy:
            run_evidence_state = "LEGACY_ONLY"
        else:
            run_evidence_state = "UNOBSERVED"
    else:
        run_evidence_state = "UNOBSERVED"

    # Last run fields
    last_run_id = None
    last_run_created_utc = None
    manifest_state = "UNKNOWN"
    run_json_state = "UNKNOWN"

    if attributable:
        # Sort by created_utc descending, tie-break by run_key
        sorted_attr = sorted(
            attributable,
            key=lambda r: (r.get("created_utc") or "", r.get("run_key") or ""),
            reverse=True,
        )
        latest = sorted_attr[0]
        last_run_id = latest["run_id"]
        last_run_created_utc = latest.get("created_utc")
        manifest_state = "PRESENT" if latest.get("has_manifest_sha256") else "MISSING"
        run_json_state = "PRESENT" if latest.get("has_run_json") else "MISSING"
    else:
        # No attributable runs
        manifest_state = "UNKNOWN"
        run_json_state = "UNKNOWN"

    staleness_days = compute_staleness_days(last_run_created_utc, now)

    # Warnings
    if run_evidence_state == "UNOBSERVED":
        warnings.append("no attributable runs observed")
    elif run_evidence_state == "LEGACY_ONLY":
        warnings.append("runs exist but are legacy/untyped")

    if attributable and manifest_state == "MISSING":
        warnings.append("missing manifest on latest run")

    if attributable:
        roots = {r.get("run_root") for r in attributable if r.get("run_root")}
        if len(roots) > 1:
            warnings.append("multiple run roots observed; using latest by created_utc")

    # Coverage warning
    cov_num = int(coverage_level[1]) if len(coverage_level) == 2 and coverage_level[1].isdigit() else 0
    if cov_num < 3:
        warnings.append(f"coverage level < C3 (actual: {coverage_level})")

    return {
        "status_version": STATUS_VERSION,
        "option": option,
        "operation_id": op_id,
        "operation_name": op_name,
        "coverage_level": coverage_level,
        "last_run_id": last_run_id,
        "last_run_created_utc": last_run_created_utc,
        "run_evidence_state": run_evidence_state,
        "manifest_state": manifest_state,
        "run_json_state": run_json_state,
        "staleness_days": staleness_days,
        "op_drift": None,
        "op_drift_reasons": [],
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

STATUS_TABLE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "OPERATION_STATUS_TABLE_v0_1",
    "description": "Schema for OPERATION_STATUS_TABLE_v0_1.json records",
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "status_version",
            "option",
            "operation_id",
            "operation_name",
            "coverage_level",
            "last_run_id",
            "last_run_created_utc",
            "run_evidence_state",
            "manifest_state",
            "run_json_state",
            "staleness_days",
            "op_drift",
            "op_drift_reasons",
            "warnings",
        ],
        "properties": {
            "status_version": {"type": "string", "const": "0.1"},
            "option": {
                "type": "string",
                "enum": ["A", "B", "C", "D", "QA"],
            },
            "operation_id": {"type": "string", "pattern": "^OP-"},
            "operation_name": {"type": "string"},
            "coverage_level": {
                "type": "string",
                "enum": ["C0", "C1", "C2", "C3", "C4", "C5"],
            },
            "last_run_id": {"type": ["string", "null"]},
            "last_run_created_utc": {"type": ["string", "null"]},
            "run_evidence_state": {
                "type": "string",
                "enum": ["OBSERVED", "UNOBSERVED", "LEGACY_ONLY"],
            },
            "manifest_state": {
                "type": "string",
                "enum": ["PRESENT", "MISSING", "UNKNOWN"],
            },
            "run_json_state": {
                "type": "string",
                "enum": ["PRESENT", "MISSING", "UNKNOWN"],
            },
            "staleness_days": {"type": ["integer", "null"]},
            "op_drift": {"type": ["boolean", "null"]},
            "op_drift_reasons": {
                "type": "array",
                "items": {"type": "string"},
            },
            "warnings": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "additionalProperties": False,
    },
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Validate inputs exist
    for p, label in [
        (RUNS_DIR, ".codex/RUNS/"),
        (CATALOG_PATH, "Allowed Operations Catalog"),
        (MATRIX_PATH, "Enforcement Coverage Matrix"),
    ]:
        if not p.exists():
            print(f"ERROR: {label} not found at {p}", file=sys.stderr)
            sys.exit(1)

    # Find latest registry
    registry_path = find_latest_registry(RUNS_DIR)
    if registry_path is None:
        print("ERROR: No RUN_REGISTRY_v0_1.jsonl found. Run build_run_registry_v0_1.py first.", file=sys.stderr)
        sys.exit(1)

    print(f"  Using registry: {registry_path}")

    # Parse inputs
    catalog_ops = parse_catalog(CATALOG_PATH)
    coverage_map = parse_coverage_matrix(MATRIX_PATH)
    registry_records = load_registry(registry_path)
    registry_index = build_registry_index(registry_records)

    git_commit = None
    working_tree_state = None
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        working_tree_state = "clean" if status_out == "" else "dirty"
    except Exception:
        pass

    system_drift = {
        "canon_dirty": None,
        "schema_drift": None,
        "threshold_drift": None,
    }
    drift_path = find_latest_drift_signals(RUNS_DIR)
    if drift_path is not None:
        try:
            drift_payload = json.loads(drift_path.read_text(encoding="utf-8"))
            payload_drift = drift_payload.get("system_drift")
            if isinstance(payload_drift, dict):
                system_drift = {
                    "canon_dirty": payload_drift.get("canon_dirty"),
                    "schema_drift": payload_drift.get("schema_drift"),
                    "threshold_drift": payload_drift.get("threshold_drift"),
                }
        except Exception:
            drift_path = None

    # Filter to canonical options only
    canonical_ops = [op for op in catalog_ops if op["option"] in CANONICAL_OPTIONS]

    if not canonical_ops:
        print("ERROR: No canonical operations found in catalog.", file=sys.stderr)
        sys.exit(1)

    # Sort: by option order (A, B, C, D, QA) then by operation_id
    option_order = {opt: i for i, opt in enumerate(CANONICAL_OPTIONS)}
    canonical_ops.sort(key=lambda op: (option_order.get(op["option"], 99), op["operation_id"]))

    now = utcnow()

    # Create output run folder
    run_id = make_run_id("op_status_table_build")
    output_dir = RUNS_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    created_utc = utcnow_iso()

    # Derive status for each op
    status_records = []
    for op in canonical_ops:
        rec = derive_op_status(op, coverage_map, registry_records, now)
        op_drift = None
        op_drift_reasons: list[str] = []
        last_run_id = rec.get("last_run_id")
        if last_run_id is not None:
            match = registry_index.get((rec.get("operation_id"), last_run_id))
            if match is not None:
                last_git = match.get("git_commit")
                last_state = match.get("working_tree_state")
                if last_git and git_commit and last_git != git_commit:
                    op_drift = True
                    op_drift_reasons.append("op_drift_commit_mismatch")
                    rec["warnings"].append("op_drift_commit_mismatch")
                elif last_state == "dirty":
                    op_drift = True
                    op_drift_reasons.append("op_drift_last_run_dirty")
                    rec["warnings"].append("op_drift_last_run_dirty")
                else:
                    op_drift = False
        rec["op_drift"] = op_drift
        rec["op_drift_reasons"] = op_drift_reasons
        status_records.append(rec)

    # --- Write OPERATION_STATUS_TABLE_v0_1.json ---
    status_path = output_dir / "OPERATION_STATUS_TABLE_v0_1.json"
    status_path.write_text(
        json.dumps(status_records, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    # --- Write schema ---
    schema_path = output_dir / "OPERATION_STATUS_TABLE_v0_1.schema.json"
    schema_path.write_text(
        json.dumps(STATUS_TABLE_SCHEMA, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    # --- Write metadata ---
    meta_path = output_dir / "OPERATION_STATUS_TABLE_v0_1.meta.json"
    meta_payload = {
        "generated_utc": created_utc,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "system_drift": system_drift,
        "drift_signals_run": str(drift_path) if drift_path is not None else None,
    }
    meta_path.write_text(
        json.dumps(meta_payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    # --- Write run.json ---
    run_json_data = {
        "run_id": run_id,
        "created_utc": created_utc,
        "run_type": "op_status_table_build",
        "status_version": STATUS_VERSION,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "input_sources": {
            "registry_jsonl": str(registry_path),
            "catalog": str(CATALOG_PATH),
            "coverage_matrix": str(MATRIX_PATH),
            "drift_signals": str(drift_path) if drift_path is not None else None,
        },
        "outputs": [
            "OPERATION_STATUS_TABLE_v0_1.json",
            "OPERATION_STATUS_TABLE_v0_1.schema.json",
            "OPERATION_STATUS_TABLE_v0_1.meta.json",
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

    # --- Seal ---
    build_manifest(output_dir, [
        "OPERATION_STATUS_TABLE_v0_1.json",
        "OPERATION_STATUS_TABLE_v0_1.schema.json",
        "OPERATION_STATUS_TABLE_v0_1.meta.json",
        "run.json",
    ])

    # --- Summary ---
    total_ops = len(status_records)
    observed = sum(1 for r in status_records if r["run_evidence_state"] == "OBSERVED")
    unobserved = sum(1 for r in status_records if r["run_evidence_state"] == "UNOBSERVED")
    legacy_only = sum(1 for r in status_records if r["run_evidence_state"] == "LEGACY_ONLY")
    below_c3 = sum(
        1 for r in status_records
        if r["coverage_level"] in ("C0", "C1", "C2")
    )

    print("=" * 60)
    print("  Phase 2.1 — Operation Status Table Build Complete")
    print("=" * 60)
    print(f"  total_canonical_ops:    {total_ops}")
    print(f"  observed:               {observed}")
    print(f"  unobserved:             {unobserved}")
    print(f"  legacy_only:            {legacy_only}")
    print(f"  coverage_below_c3:      {below_c3}")
    print(f"  output_run_folder:      {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
