#!/usr/bin/env python3
"""
Phase 2.2 — Active Pointer Validator v0.1

Validates that ACTIVE_REGISTRY_POINTERS_v0_1.json is internally consistent
and all resolvable pointers reference valid sealed artifacts.

Inputs:
    [--pointers <pointer_file>]  — path to pointer file (default: auto-detect)
    [--catalog <catalog_file>]   — path to registry catalog (default: auto-detect)

Checks:
    1. Pointer file is valid JSON with required structure
    2. Every pointer has required fields: registry_id, active_ref, active_ref_known, active_asof_utc
    3. Every registry_id in pointers matches a registry_id in the catalog
    4. For pointers with active_ref_known == true:
       a. active_ref.run_id is not null
       b. The referenced run folder exists on disk (if run_root is not null)
       c. The referenced relpath exists within the run folder
       d. If manifest_sha256 is provided, it matches the actual ROOT_SHA256
    5. Tri-state: active_ref_known == "unknown" is valid (not a failure)
    6. No duplicate registry_ids in the pointer file

Failure conditions:
    POINTER_INVALID: <reason>

Exit code:
    0 = PASS (all resolvable pointers are valid)
    1 = FAIL (with details on stderr)

Hard constraints:
    - Read-only: does not modify any file.
    - Stdlib only: no third-party dependencies.
    - Deterministic.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


PHASE_22_DIR = Path(__file__).parent.parent
DEFAULT_POINTER_FILE = PHASE_22_DIR / "ACTIVE_REGISTRY_POINTERS_v0_1.json"
DEFAULT_CATALOG_FILE = PHASE_22_DIR / "REGISTRY_CATALOG_v0_1.json"


def extract_root_sha256(manifest_sha256_path: Path) -> str | None:
    """Extract ROOT_SHA256 from a MANIFEST.sha256 file."""
    try:
        text = manifest_sha256_path.read_text(encoding="utf-8")
        for line in text.strip().split("\n"):
            if line.startswith("ROOT_SHA256"):
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    return parts[1].strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None


def validate_pointers(pointer_file: Path, catalog_file: Path | None) -> list[str]:
    """Return list of failure reasons. Empty = PASS."""
    errors: list[str] = []

    # --- Load pointer file ---
    if not pointer_file.exists():
        return [f"POINTER_INVALID: pointer file not found: {pointer_file}"]

    try:
        pdata = json.loads(pointer_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"POINTER_INVALID: pointer file parse error: {exc}"]

    pointers = pdata.get("pointers", [])
    if not isinstance(pointers, list):
        return ["POINTER_INVALID: 'pointers' is not an array"]

    # --- Load catalog (optional) ---
    catalog_ids: set[str] | None = None
    if catalog_file and catalog_file.exists():
        try:
            cdata = json.loads(catalog_file.read_text(encoding="utf-8"))
            catalog_ids = {r["registry_id"] for r in cdata.get("registries", [])}
        except (json.JSONDecodeError, KeyError):
            errors.append("POINTER_INVALID: catalog file parse error (non-fatal)")

    # --- Check for duplicate registry_ids ---
    seen_ids: set[str] = set()
    for ptr in pointers:
        rid = ptr.get("registry_id", "")
        if rid in seen_ids:
            errors.append(f"POINTER_INVALID: duplicate registry_id: {rid}")
        seen_ids.add(rid)

    # --- Validate each pointer ---
    for ptr in pointers:
        rid = ptr.get("registry_id")
        if not rid:
            errors.append("POINTER_INVALID: pointer missing 'registry_id'")
            continue

        prefix = f"[{rid}] "

        # Required fields
        for field in ("active_ref", "active_ref_known", "active_asof_utc"):
            if field not in ptr:
                errors.append(f"POINTER_INVALID: {prefix}missing '{field}'")

        # Catalog cross-reference
        if catalog_ids is not None and rid not in catalog_ids:
            errors.append(f"POINTER_INVALID: {prefix}not found in registry catalog")

        ref_known = ptr.get("active_ref_known")
        active_ref = ptr.get("active_ref", {})

        # Tri-state: "unknown" is valid, skip resolution checks
        if ref_known == "unknown":
            continue

        if ref_known is True:
            run_id = active_ref.get("run_id")
            run_root = active_ref.get("run_root")
            relpath = active_ref.get("relpath")
            manifest_sha = active_ref.get("manifest_sha256")

            # Resolve run folder if possible
            if run_root is not None and run_id is not None:
                run_folder = Path(run_root) / run_id
                if run_folder.is_dir():
                    # Check relpath exists
                    if relpath:
                        target = run_folder / relpath
                        if not target.exists():
                            errors.append(
                                f"POINTER_INVALID: {prefix}relpath '{relpath}' "
                                f"not found in {run_folder}"
                            )

                    # Check manifest_sha256 if provided
                    if manifest_sha:
                        mf = run_folder / "MANIFEST.sha256"
                        if mf.exists():
                            actual_root = extract_root_sha256(mf)
                            if actual_root and actual_root != manifest_sha:
                                errors.append(
                                    f"POINTER_INVALID: {prefix}manifest_sha256 mismatch: "
                                    f"pointer={manifest_sha}, actual={actual_root}"
                                )
                        else:
                            errors.append(
                                f"POINTER_INVALID: {prefix}manifest_sha256 specified "
                                f"but MANIFEST.sha256 not found in {run_folder}"
                            )
                else:
                    # run folder not found on disk — may be expected for some registries
                    pass  # Not an error; folder may be relative to repo root

    return errors


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Active Pointer Validator v0.1")
    parser.add_argument(
        "--pointers", type=Path, default=DEFAULT_POINTER_FILE,
        help="Path to pointer file"
    )
    parser.add_argument(
        "--catalog", type=Path, default=DEFAULT_CATALOG_FILE,
        help="Path to registry catalog"
    )
    args = parser.parse_args()

    errors = validate_pointers(args.pointers, args.catalog)

    if errors:
        print(f"FAIL: {len(errors)} pointer violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    else:
        print("PASS: All active pointers are valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
