#!/usr/bin/env python3
"""
Phase 2.2.3 — Registry Delta Log Builder v0.1

Produces an append-only JSONL delta log that records registry deltas
derived from successive sealed snapshots.

Inputs:
  - root path to runs (default: .codex/RUNS)
  - ACTIVE_REGISTRY_POINTERS_v0_1.json
  - REGISTRY_CATALOG_v0_1.json + REGISTRY_CATALOG_ADDENDUM_v0_1__phase_2_2_3.json

Outputs (in new run folder):
  - REGISTRY_DELTA_LOG_v0_1.jsonl
  - run.json
  - manifest.json
  - MANIFEST.sha256

Hard constraints:
  - Append-only: new records are appended only.
  - Derived from sealed truth only: uses manifest.json + MANIFEST.sha256.
  - Deterministic: same sealed inputs → identical delta output.
  - Sort ordering: by registry_id, then by to_ref.run_id lexicographically.
  - No third-party deps — stdlib only.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DELTA_VERSION = "0.1"
RUNS_ROOT = Path(".codex/RUNS")
PHASE_2_2_DIR = Path("docs/phase_2_2")

POINTERS_FILE = PHASE_2_2_DIR / "ACTIVE_REGISTRY_POINTERS_v0_1.json"
CATALOG_FILE = PHASE_2_2_DIR / "REGISTRY_CATALOG_v0_1.json"
ADDENDUM_FILE = PHASE_2_2_DIR / "REGISTRY_CATALOG_ADDENDUM_v0_1__phase_2_2_3.json"

# Eligible registries for delta logging (have sealed manifests, snapshot-like)
ELIGIBLE_REGISTRY_IDS = {
    "run_registry",
    "op_status_table",
    "drift_signals",
    "migration_ledger",
    "expected_versions",
    "threshold_packs_file",
    "derived_validation_reports",
    "fingerprint_index",
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_manifest_json(folder: Path) -> list[dict] | None:
    """Load manifest.json from a run folder. Returns list of entries or None."""
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        data = load_json(manifest_path)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Discover sealed snapshots for registries
# ---------------------------------------------------------------------------


def discover_sealed_snapshots(runs_root: Path, pointers: dict) -> dict[str, list[dict]]:
    """
    For each eligible registry, discover all sealed snapshots in runs_root.
    
    Returns: {registry_id: [list of snapshot refs sorted by run_id lexicographically]}
    
    Each snapshot ref: {run_id, run_root, relpath, manifest_sha256, manifest_entries}
    
    Ordering: by run_id lexicographically (ascending). This provides deterministic
    ordering based on the timestamp-prefixed run_id format (YYYY-MM-DD__HHMMSS__tag).
    """
    # Build a mapping of registry_id -> list of run_ids from pointers
    pointer_map = {}
    for ptr in pointers.get("pointers", []):
        reg_id = ptr.get("registry_id")
        if reg_id in ELIGIBLE_REGISTRY_IDS:
            active_ref = ptr.get("active_ref", {})
            pointer_map[reg_id] = active_ref
    
    # Scan runs_root for all run folders with manifest.json
    registry_snapshots: dict[str, list[dict]] = {rid: [] for rid in ELIGIBLE_REGISTRY_IDS}
    
    if not runs_root.is_dir():
        return registry_snapshots
    
    for entry in sorted(runs_root.iterdir()):
        if not entry.is_dir():
            continue
        
        manifest_path = entry / "manifest.json"
        manifest_sha_path = entry / "MANIFEST.sha256"
        
        if not manifest_path.is_file() or not manifest_sha_path.is_file():
            continue
        
        manifest_entries = load_manifest_json(entry)
        if manifest_entries is None:
            continue
        
        root_sha256 = extract_root_sha256(manifest_sha_path)
        if root_sha256 is None:
            continue
        
        run_id = entry.name
        run_root = runs_root.as_posix()
        
        # Identify which registry this run belongs to based on files present
        registry_id = identify_registry_from_manifest(manifest_entries, run_id)
        
        if registry_id and registry_id in ELIGIBLE_REGISTRY_IDS:
            # Determine relpath from catalog or manifest
            relpath = get_relpath_for_registry(registry_id, manifest_entries)
            
            snapshot_ref = {
                "run_id": run_id,
                "run_root": run_root,
                "relpath": relpath,
                "manifest_sha256": root_sha256,
                "manifest_entries": manifest_entries,  # kept for diff computation
            }
            registry_snapshots[registry_id].append(snapshot_ref)
    
    # Sort each list by run_id (already sorted by iterdir, but ensure determinism)
    for rid in registry_snapshots:
        registry_snapshots[rid].sort(key=lambda x: x["run_id"])
    
    return registry_snapshots


def identify_registry_from_manifest(entries: list[dict], run_id: str) -> str | None:
    """
    Identify which registry a run folder belongs to based on manifest entries.
    Returns registry_id or None if not identified.
    """
    file_names = {e.get("relpath", "") for e in entries}
    
    # Pattern matching based on known registry artifacts
    if "RUN_REGISTRY_v0_1.jsonl" in file_names:
        return "run_registry"
    if "OPERATION_STATUS_TABLE_v0_1.json" in file_names:
        return "op_status_table"
    if "DRIFT_SIGNALS_v0_1.json" in file_names:
        return "drift_signals"
    if "applied_migrations_snapshot.json" in file_names:
        return "migration_ledger"
    if "EXPECTED_VERSIONS_v0_1_snapshot.json" in file_names:
        return "expected_versions"
    if any("threshold" in f.lower() and f.endswith(".json") for f in file_names):
        # Check for threshold pack files
        pack_files = {"c3_example_pack_v1.json", "c3_regime_trend_v1.json", "state_plane_v0_2_default_v1.json"}
        if file_names & pack_files:
            return "threshold_packs_file"
    if "derived_validation_report.json" in file_names:
        return "derived_validation_reports"
    if "fingerprint_index_snapshot.csv" in file_names:
        return "fingerprint_index"
    
    # Also check run_id patterns for Phase 2.2.1 seal promotions
    if "seal_migration_ledger" in run_id:
        return "migration_ledger"
    if "seal_expected_versions" in run_id:
        return "expected_versions"
    if "seal_threshold_packs" in run_id:
        return "threshold_packs_file"
    if "seal_derived_validation" in run_id:
        return "derived_validation_reports"
    if "seal_fingerprint_index" in run_id:
        return "fingerprint_index"
    
    return None


def get_relpath_for_registry(registry_id: str, manifest_entries: list[dict]) -> str | None:
    """Get the primary artifact relpath for a registry, or None for multi-file registries."""
    relpath_map = {
        "run_registry": "RUN_REGISTRY_v0_1.jsonl",
        "op_status_table": "OPERATION_STATUS_TABLE_v0_1.json",
        "drift_signals": "DRIFT_SIGNALS_v0_1.json",
        "migration_ledger": "applied_migrations_snapshot.json",
        "expected_versions": "EXPECTED_VERSIONS_v0_1_snapshot.json",
        "derived_validation_reports": "derived_validation_report.json",
        "fingerprint_index": "fingerprint_index_snapshot.csv",
    }
    
    expected = relpath_map.get(registry_id)
    if expected:
        # Verify it exists in manifest
        file_names = {e.get("relpath", "") for e in manifest_entries}
        if expected in file_names:
            return expected
    
    # threshold_packs_file is multi-file, relpath is null
    if registry_id == "threshold_packs_file":
        return None
    
    return None


# ---------------------------------------------------------------------------
# Delta computation
# ---------------------------------------------------------------------------


def compute_manifest_diff(
    from_entries: list[dict] | None,
    to_entries: list[dict]
) -> tuple[list[str], list[str], list[str]]:
    """
    Compute diff between two manifest entry lists.
    
    Returns: (added_paths, removed_paths, modified_paths) — all sorted.
    """
    if from_entries is None:
        # Bootstrap: all files are "added"
        added = sorted(e.get("relpath", "") for e in to_entries)
        return added, [], []
    
    from_map = {e.get("relpath", ""): e.get("sha256", "") for e in from_entries}
    to_map = {e.get("relpath", ""): e.get("sha256", "") for e in to_entries}
    
    from_paths = set(from_map.keys())
    to_paths = set(to_map.keys())
    
    added = sorted(to_paths - from_paths)
    removed = sorted(from_paths - to_paths)
    
    common = from_paths & to_paths
    modified = sorted(p for p in common if from_map[p] != to_map[p])
    
    return added, removed, modified


# ---------------------------------------------------------------------------
# Build delta log
# ---------------------------------------------------------------------------


def build_delta_log(runs_root: Path, pointers: dict, derivation_run_id: str, created_utc: str) -> list[dict]:
    """
    Build delta log records for all eligible registries.
    
    Returns list of delta records, sorted by (registry_id, to_ref.run_id).
    """
    snapshots = discover_sealed_snapshots(runs_root, pointers)
    
    records: list[dict] = []
    
    for registry_id in sorted(ELIGIBLE_REGISTRY_IDS):
        snap_list = snapshots.get(registry_id, [])
        
        if not snap_list:
            continue
        
        prev_snapshot = None
        
        for snap in snap_list:
            from_entries = prev_snapshot.get("manifest_entries") if prev_snapshot else None
            to_entries = snap.get("manifest_entries", [])
            
            added, removed, modified = compute_manifest_diff(from_entries, to_entries)
            
            # Build from_ref
            if prev_snapshot:
                from_ref = {
                    "run_id": prev_snapshot["run_id"],
                    "run_root": prev_snapshot["run_root"],
                    "relpath": prev_snapshot["relpath"],
                    "manifest_sha256": prev_snapshot["manifest_sha256"],
                }
            else:
                from_ref = None
            
            # Build to_ref
            to_ref = {
                "run_id": snap["run_id"],
                "run_root": snap["run_root"],
                "relpath": snap["relpath"],
                "manifest_sha256": snap["manifest_sha256"],
            }
            
            record = {
                "delta_version": DELTA_VERSION,
                "registry_id": registry_id,
                "from_ref": from_ref,
                "to_ref": to_ref,
                "delta_basis": "manifest_diff",
                "added_paths": added,
                "removed_paths": removed,
                "modified_paths": modified,
                "counts": {
                    "added": len(added),
                    "removed": len(removed),
                    "modified": len(modified),
                },
                "created_utc": created_utc,
                "derivation_run_id": derivation_run_id,
            }
            
            records.append(record)
            prev_snapshot = snap
    
    # Sort by (registry_id, to_ref.run_id) for determinism
    records.sort(key=lambda r: (r["registry_id"], r["to_ref"]["run_id"]))
    
    return records


# ---------------------------------------------------------------------------
# Sealing
# ---------------------------------------------------------------------------


def build_manifest(output_dir: Path, file_names: list[str]) -> None:
    """Create manifest.json and MANIFEST.sha256 for the delta-log build run."""
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
    manifest_sha_path.write_text("\n".join(sorted(sha_lines[:-1])) + f"\nROOT_SHA256  {root_hash}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    # Verify inputs exist
    if not RUNS_ROOT.is_dir():
        print(f"ERROR: {RUNS_ROOT} not found.", file=sys.stderr)
        return 1
    
    if not POINTERS_FILE.is_file():
        print(f"ERROR: {POINTERS_FILE} not found.", file=sys.stderr)
        return 1
    
    # Load pointers
    pointers = load_json(POINTERS_FILE)
    
    # Create output run folder
    build_tag = "registry_delta_log_build"
    run_id = make_run_id(build_tag)
    output_dir = RUNS_ROOT / run_id
    output_dir.mkdir(parents=True, exist_ok=False)
    
    created_utc = utcnow_iso()
    
    # Build delta log
    records = build_delta_log(RUNS_ROOT, pointers, run_id, created_utc)
    
    # Write REGISTRY_DELTA_LOG_v0_1.jsonl
    jsonl_path = output_dir / "REGISTRY_DELTA_LOG_v0_1.jsonl"
    lines = []
    for rec in records:
        lines.append(json.dumps(rec, separators=(",", ":"), sort_keys=False))
    jsonl_path.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")
    
    # Capture git state
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
    
    # Count registries covered
    registries_covered = sorted(set(r["registry_id"] for r in records))
    registries_skipped = sorted(ELIGIBLE_REGISTRY_IDS - set(registries_covered))
    
    # Write run.json
    run_json_data = {
        "run_id": run_id,
        "created_utc": created_utc,
        "run_type": "registry_delta_log_build",
        "operation_id": "OP-QA11",
        "option": "QA",
        "delta_version": DELTA_VERSION,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "inputs": {
            "runs_root": RUNS_ROOT.as_posix(),
            "pointers_file": POINTERS_FILE.as_posix(),
        },
        "outputs": [
            "REGISTRY_DELTA_LOG_v0_1.jsonl",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
        "summary": {
            "total_delta_records": len(records),
            "registries_covered": registries_covered,
            "registries_skipped": registries_skipped,
        },
    }
    run_json_path = output_dir / "run.json"
    run_json_path.write_text(
        json.dumps(run_json_data, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    
    # Seal with manifest
    build_manifest(output_dir, [
        "REGISTRY_DELTA_LOG_v0_1.jsonl",
        "run.json",
    ])
    
    # Summary output
    print("=" * 60)
    print("  Phase 2.2.3 — Registry Delta Log Build Complete")
    print("=" * 60)
    print(f"  total_delta_records:    {len(records)}")
    print(f"  registries_covered:     {len(registries_covered)}")
    print(f"    {registries_covered}")
    print(f"  registries_skipped:     {len(registries_skipped)}")
    print(f"    {registries_skipped}")
    print(f"  output_run_folder:      {output_dir}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
