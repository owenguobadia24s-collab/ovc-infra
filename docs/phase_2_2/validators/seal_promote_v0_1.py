#!/usr/bin/env python3
"""
Phase 2.2.1 — Seal Promotion Script v0.1

Creates new sealed run folders for registries that were identified as
unsealed in Phase 2.2 REGISTRY_SEAL_CONTRACT_v0_1.md Section 8.

Promotable registries (snapshot-sealable from repo evidence):
  1. migration_ledger       — schema/applied_migrations.json
  2. expected_versions      — docs/governance/EXPECTED_VERSIONS_v0_1.json
  3. threshold_packs_file   — configs/threshold_packs/*.json (3 files)
  4. fingerprint_index      — reports/path1/trajectory_families/v0.1/fingerprints/index.csv
  5. derived_validation_reports — artifacts/derived_validation/<uuid>/ (3 files)

Non-promotable (cannot seal deterministically from repo alone):
  - validation_range_results — multiple independent JSONL files, no single snapshot
  - threshold_registry_db   — external database, not repo-resident
  - evidence_pack_registry  — already individually sealed at run level
  - system_health_report    — presentation-only, no single active artifact

Hard constraints:
  - No mutation of any existing file.
  - New run folders only.
  - Deterministic hashing per REGISTRY_SEAL_CONTRACT_v0_1.
  - Stdlib only.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RUNS_DIR = REPO_ROOT / ".codex" / "RUNS"

GIT_COMMIT: str | None = None
WORKING_TREE_STATE: str | None = None


def utcnow_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_run_id(tag: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d__%H%M%S")
    return f"{ts}__{tag}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_state() -> tuple[str | None, str | None]:
    global GIT_COMMIT, WORKING_TREE_STATE
    if GIT_COMMIT is not None:
        return GIT_COMMIT, WORKING_TREE_STATE
    try:
        GIT_COMMIT = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        WORKING_TREE_STATE = "clean" if not status else "dirty"
    except Exception:
        GIT_COMMIT = None
        WORKING_TREE_STATE = None
    return GIT_COMMIT, WORKING_TREE_STATE


def write_sealed_run(
    run_id: str,
    run_type: str,
    files: dict[str, bytes],
    extra_run_json: dict | None = None,
) -> tuple[Path, str]:
    """
    Create a sealed run folder with the given files.
    Returns (run_folder_path, root_sha256).
    """
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    git_commit, wt_state = get_git_state()

    # Write all payload files
    for relpath, content in sorted(files.items()):
        p = run_dir / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)

    # Build run.json
    run_json = {
        "run_id": run_id,
        "created_utc": utcnow_iso(),
        "run_type": run_type,
        "git_commit": git_commit,
        "working_tree_state": wt_state,
        "outputs": sorted(list(files.keys()) + ["run.json", "manifest.json", "MANIFEST.sha256"]),
    }
    if extra_run_json:
        run_json.update(extra_run_json)

    run_json_bytes = json.dumps(run_json, indent=2, sort_keys=True).encode("utf-8")
    (run_dir / "run.json").write_bytes(run_json_bytes)

    # Build manifest.json — per Phase 2.1 convention, manifest.json does NOT
    # include itself. Only MANIFEST.sha256 includes the manifest.json hash.
    all_files = sorted(list(files.keys()) + ["run.json"])
    manifest_entries = []
    sha_lines = []
    for rp in sorted(all_files):
        fp = run_dir / rp
        h = sha256_file(fp)
        size = fp.stat().st_size
        manifest_entries.append({
            "relpath": rp,
            "bytes": size,
            "sha256": h,
        })
        sha_lines.append(f"{h}  {rp}")

    # Write manifest.json (does not reference itself)
    manifest_bytes = json.dumps(manifest_entries, indent=2, sort_keys=False).encode("utf-8") + b"\n"
    (run_dir / "manifest.json").write_bytes(manifest_bytes)

    # Include manifest.json hash in MANIFEST.sha256
    mj_hash = sha256_bytes(manifest_bytes)
    sha_lines.append(f"{mj_hash}  manifest.json")

    # ROOT_SHA256 = hash of all sha lines (sorted) joined with newline + trailing newline
    root_input = "\n".join(sorted(sha_lines)) + "\n"
    root_sha256 = sha256_bytes(root_input.encode("utf-8"))
    sha_lines.append(f"ROOT_SHA256  {root_sha256}")

    # Write MANIFEST.sha256
    sha256_text = "\n".join(sorted(sha_lines[:-1])) + f"\nROOT_SHA256  {root_sha256}\n"
    (run_dir / "MANIFEST.sha256").write_bytes(sha256_text.encode("utf-8"))

    return run_dir, root_sha256


def seal_migration_ledger() -> dict:
    src = REPO_ROOT / "schema" / "applied_migrations.json"
    content = src.read_bytes()
    run_id = make_run_id("seal_migration_ledger")
    run_dir, root_sha = write_sealed_run(
        run_id=run_id,
        run_type="seal_promotion",
        files={"applied_migrations_snapshot.json": content},
        extra_run_json={
            "seal_promotion": True,
            "source_registry": "migration_ledger",
            "source_path": "schema/applied_migrations.json",
        },
    )
    return {
        "registry_id": "migration_ledger",
        "run_id": run_id,
        "run_root": ".codex/RUNS",
        "relpath": "applied_migrations_snapshot.json",
        "manifest_sha256": root_sha,
        "run_dir": str(run_dir),
    }


def seal_expected_versions() -> dict:
    src = REPO_ROOT / "docs" / "governance" / "EXPECTED_VERSIONS_v0_1.json"
    content = src.read_bytes()
    run_id = make_run_id("seal_expected_versions")
    run_dir, root_sha = write_sealed_run(
        run_id=run_id,
        run_type="seal_promotion",
        files={"EXPECTED_VERSIONS_v0_1_snapshot.json": content},
        extra_run_json={
            "seal_promotion": True,
            "source_registry": "expected_versions",
            "source_path": "docs/governance/EXPECTED_VERSIONS_v0_1.json",
        },
    )
    return {
        "registry_id": "expected_versions",
        "run_id": run_id,
        "run_root": ".codex/RUNS",
        "relpath": "EXPECTED_VERSIONS_v0_1_snapshot.json",
        "manifest_sha256": root_sha,
        "run_dir": str(run_dir),
    }


def seal_threshold_packs() -> dict:
    pack_dir = REPO_ROOT / "configs" / "threshold_packs"
    files = {}
    for p in sorted(pack_dir.glob("*.json")):
        files[p.name] = p.read_bytes()

    run_id = make_run_id("seal_threshold_packs")
    run_dir, root_sha = write_sealed_run(
        run_id=run_id,
        run_type="seal_promotion",
        files=files,
        extra_run_json={
            "seal_promotion": True,
            "source_registry": "threshold_packs_file",
            "source_path": "configs/threshold_packs/",
            "pack_count": len(files),
        },
    )
    return {
        "registry_id": "threshold_packs_file",
        "run_id": run_id,
        "run_root": ".codex/RUNS",
        "relpath": None,
        "manifest_sha256": root_sha,
        "run_dir": str(run_dir),
    }


def seal_fingerprint_index() -> dict:
    src = REPO_ROOT / "reports" / "path1" / "trajectory_families" / "v0.1" / "fingerprints" / "index.csv"
    content = src.read_bytes()
    run_id = make_run_id("seal_fingerprint_index")
    run_dir, root_sha = write_sealed_run(
        run_id=run_id,
        run_type="seal_promotion",
        files={"fingerprint_index_snapshot.csv": content},
        extra_run_json={
            "seal_promotion": True,
            "source_registry": "fingerprint_index",
            "source_path": "reports/path1/trajectory_families/v0.1/fingerprints/index.csv",
        },
    )
    return {
        "registry_id": "fingerprint_index",
        "run_id": run_id,
        "run_root": ".codex/RUNS",
        "relpath": "fingerprint_index_snapshot.csv",
        "manifest_sha256": root_sha,
        "run_dir": str(run_dir),
    }


def seal_derived_validation() -> dict:
    uuid_dir = REPO_ROOT / "artifacts" / "derived_validation" / "1dfb7850-2cdd-5dd0-9cd5-dd7758d19439"
    files = {}
    for p in sorted(uuid_dir.iterdir()):
        if p.is_file():
            files[p.name] = p.read_bytes()

    run_id = make_run_id("seal_derived_validation")
    run_dir, root_sha = write_sealed_run(
        run_id=run_id,
        run_type="seal_promotion",
        files=files,
        extra_run_json={
            "seal_promotion": True,
            "source_registry": "derived_validation_reports",
            "source_run_id": "1dfb7850-2cdd-5dd0-9cd5-dd7758d19439",
            "source_path": "artifacts/derived_validation/1dfb7850-2cdd-5dd0-9cd5-dd7758d19439/",
        },
    )
    return {
        "registry_id": "derived_validation_reports",
        "run_id": run_id,
        "run_root": ".codex/RUNS",
        "relpath": "derived_validation_report.json",
        "manifest_sha256": root_sha,
        "run_dir": str(run_dir),
    }


def main() -> int:
    results = []
    for sealer in [
        seal_migration_ledger,
        seal_expected_versions,
        seal_threshold_packs,
        seal_fingerprint_index,
        seal_derived_validation,
    ]:
        try:
            r = sealer()
            results.append(r)
            print(f"SEALED: {r['registry_id']} -> {r['run_id']} (ROOT_SHA256={r['manifest_sha256']})")
        except Exception as exc:
            print(f"FAILED: {sealer.__name__}: {exc}", file=sys.stderr)
            results.append({"registry_id": sealer.__name__, "error": str(exc)})

    # Write summary
    summary_path = REPO_ROOT / "docs" / "phase_2_2" / "SEAL_PROMOTION_RESULTS.json"
    summary_path.write_text(
        json.dumps(results, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"\nSummary written to {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
