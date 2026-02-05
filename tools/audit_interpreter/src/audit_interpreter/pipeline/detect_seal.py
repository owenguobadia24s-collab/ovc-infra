"""
Pipeline Step 2: Detect Seal Status

Checks for manifest.json + MANIFEST.sha256 and validates seal integrity.
Per RUN_ENVELOPE_STANDARD_v0_1:
- manifest.json: array of entries with relpath, bytes, sha256
- MANIFEST.sha256: one line per file as "SHA256  relpath" plus ROOT_SHA256 line
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .load_run import RunContext


@dataclass
class SealStatus:
    """Seal status for a run folder."""
    is_sealed: bool
    seal_valid: Optional[bool]  # None if not sealed
    root_sha256: Optional[str]  # None if not sealed or invalid

    # Detailed status
    manifest_json_present: bool = False
    manifest_sha256_present: bool = False
    manifest_json_content: Optional[List[Dict[str, Any]]] = None
    manifest_sha256_lines: Optional[List[str]] = None

    # Validation details
    hash_mismatches: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def load_manifest_json(run_folder: Path) -> tuple[Optional[List[Dict[str, Any]]], List[str]]:
    """Load and parse manifest.json."""
    errors = []
    manifest_path = run_folder / "manifest.json"

    if not manifest_path.exists():
        return None, []  # Not an error, just not sealed

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"ARTIFACT_MALFORMED: manifest.json parse error: {e}")
        return None, errors
    except OSError as e:
        errors.append(f"ACCESS_DENIED: Cannot read manifest.json: {e}")
        return None, errors

    if not isinstance(content, list):
        errors.append("ARTIFACT_MALFORMED: manifest.json must be an array")
        return None, errors

    return content, errors


def load_manifest_sha256(run_folder: Path) -> tuple[Optional[List[str]], List[str]]:
    """Load MANIFEST.sha256 file."""
    errors = []
    sha256_path = run_folder / "MANIFEST.sha256"

    if not sha256_path.exists():
        return None, []  # Not an error, just not sealed

    try:
        with open(sha256_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except OSError as e:
        errors.append(f"ACCESS_DENIED: Cannot read MANIFEST.sha256: {e}")
        return None, errors

    return lines, errors


def compute_file_sha256(file_path: Path) -> Optional[str]:
    """Compute SHA256 hash of a file."""
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except OSError:
        return None


def parse_sha256_line(line: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse a MANIFEST.sha256 line.

    Format: "SHA256  relpath" or "ROOT_SHA256  hash"
    Returns (hash, relpath) or (None, None) if invalid.
    """
    parts = line.split('  ', 1)  # Two spaces
    if len(parts) != 2:
        return None, None

    if parts[0] == "ROOT_SHA256":
        return parts[1], "ROOT_SHA256"
    else:
        return parts[0], parts[1]


def validate_seal(
    run_folder: Path,
    manifest_json: List[Dict[str, Any]],
    manifest_sha256_lines: List[str]
) -> tuple[bool, Optional[str], List[str], List[str]]:
    """
    Validate seal integrity.

    Per RUN_ENVELOPE_STANDARD_v0_1:
    - Verify manifest.json entries match actual file hashes
    - Verify MANIFEST.sha256 entries match manifest.json
    - Verify ROOT_SHA256 is correct

    Returns (is_valid, root_sha256, hash_mismatches, errors)
    """
    errors = []
    hash_mismatches = []
    root_sha256 = None

    # Build hash map from manifest.json
    manifest_hashes: Dict[str, str] = {}
    for entry in manifest_json:
        if "relpath" in entry and "sha256" in entry:
            manifest_hashes[entry["relpath"]] = entry["sha256"]

    # Parse MANIFEST.sha256 lines
    sha256_hashes: Dict[str, str] = {}
    for line in manifest_sha256_lines:
        hash_val, relpath = parse_sha256_line(line)
        if hash_val and relpath:
            if relpath == "ROOT_SHA256":
                root_sha256 = hash_val
            else:
                sha256_hashes[relpath] = hash_val

    # Verify file hashes against manifest.json
    for entry in manifest_json:
        relpath = entry.get("relpath")
        expected_hash = entry.get("sha256")
        if relpath and expected_hash:
            file_path = run_folder / relpath
            if file_path.exists():
                actual_hash = compute_file_sha256(file_path)
                if actual_hash and actual_hash != expected_hash:
                    hash_mismatches.append(
                        f"Hash mismatch for {relpath}: expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
                    )
            else:
                errors.append(f"ARTIFACT_MISSING: File in manifest not found: {relpath}")

    # Verify MANIFEST.sha256 matches manifest.json
    for relpath, hash_val in sha256_hashes.items():
        if relpath in manifest_hashes:
            if hash_val != manifest_hashes[relpath]:
                hash_mismatches.append(
                    f"MANIFEST.sha256 hash mismatch for {relpath}"
                )
        elif relpath != "manifest.json":
            # Files in MANIFEST.sha256 should be in manifest.json too
            pass  # Not an error per spec

    # Verify ROOT_SHA256
    if root_sha256:
        # ROOT_SHA256 = SHA256 of all sha lines (sorted lexicographically) joined with \n + trailing newline
        sha_lines = []
        for line in manifest_sha256_lines:
            hash_val, relpath = parse_sha256_line(line)
            if hash_val and relpath and relpath != "ROOT_SHA256":
                sha_lines.append(f"{hash_val}  {relpath}")

        sha_lines_sorted = sorted(sha_lines)
        sha_content = '\n'.join(sha_lines_sorted) + '\n'
        computed_root = hashlib.sha256(sha_content.encode('utf-8')).hexdigest()

        if computed_root != root_sha256:
            hash_mismatches.append(
                f"ROOT_SHA256 mismatch: expected {root_sha256[:16]}..., computed {computed_root[:16]}..."
            )

    is_valid = len(hash_mismatches) == 0 and len(errors) == 0
    return is_valid, root_sha256, hash_mismatches, errors


def detect_seal(context: RunContext) -> SealStatus:
    """
    Main entry point: Detect and validate seal status.

    A run is considered sealed if both manifest.json and MANIFEST.sha256 are present.
    Seal validity is checked only for sealed runs.
    """
    run_folder = context.run_folder
    errors = []

    # Load manifest.json
    manifest_json, json_errors = load_manifest_json(run_folder)
    errors.extend(json_errors)
    manifest_json_present = manifest_json is not None

    # Load MANIFEST.sha256
    manifest_sha256_lines, sha256_errors = load_manifest_sha256(run_folder)
    errors.extend(sha256_errors)
    manifest_sha256_present = manifest_sha256_lines is not None

    # Determine if sealed
    is_sealed = manifest_json_present and manifest_sha256_present

    if not is_sealed:
        # Not sealed - no validation needed
        return SealStatus(
            is_sealed=False,
            seal_valid=None,
            root_sha256=None,
            manifest_json_present=manifest_json_present,
            manifest_sha256_present=manifest_sha256_present,
            manifest_json_content=manifest_json,
            manifest_sha256_lines=manifest_sha256_lines,
            errors=errors
        )

    # Validate seal
    seal_valid, root_sha256, hash_mismatches, validation_errors = validate_seal(
        run_folder, manifest_json, manifest_sha256_lines
    )
    errors.extend(validation_errors)

    return SealStatus(
        is_sealed=True,
        seal_valid=seal_valid,
        root_sha256=root_sha256 if seal_valid else None,
        manifest_json_present=True,
        manifest_sha256_present=True,
        manifest_json_content=manifest_json,
        manifest_sha256_lines=manifest_sha256_lines,
        hash_mismatches=hash_mismatches,
        errors=errors
    )
