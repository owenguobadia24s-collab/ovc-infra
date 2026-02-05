"""
Pipeline Step 3: Scan Artifacts

Identifies and classifies artifacts using known_artifact_patterns.json.
Records all artifacts in evidence_index format.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .load_run import RunContext


@dataclass
class ArtifactEntry:
    """An indexed artifact."""
    artifact_path: str  # Relative path within run folder
    artifact_type: str  # One of: run_json, manifest_json, manifest_sha256, audit_output, data_artifact, other
    read_status: str    # One of: SUCCESS, NOT_FOUND, PARSE_ERROR, ACCESS_DENIED
    sha256: Optional[str] = None
    file_size: Optional[int] = None
    pattern_matched: Optional[str] = None


@dataclass
class ScanResult:
    """Result of artifact scanning."""
    artifacts: List[ArtifactEntry]
    errors: List[str]


def load_patterns(config_path: Path) -> tuple[List[Dict[str, Any]], List[str]]:
    """Load artifact patterns from config file."""
    errors = []

    if not config_path.exists():
        errors.append(f"CONFIG_MISSING: known_artifact_patterns.json not found at {config_path}")
        return [], errors

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"CONFIG_MALFORMED: known_artifact_patterns.json parse error: {e}")
        return [], errors

    patterns = config.get("patterns", [])
    return patterns, errors


def match_artifact_type(rel_path: str, patterns: List[Dict[str, Any]]) -> tuple[str, Optional[str]]:
    """
    Match a relative path against known patterns.

    Tries to match against the full relative path first,
    then falls back to matching just the filename.

    Returns (artifact_type, matched_pattern).
    Falls back to "other" if no pattern matches.
    """
    filename = Path(rel_path).name

    for pattern_def in patterns:
        pattern = pattern_def.get("pattern", "")
        artifact_type = pattern_def.get("artifact_type", "other")

        try:
            # Try matching full relative path first, then filename
            if re.match(pattern, rel_path) or re.match(pattern, filename):
                return artifact_type, pattern
        except re.error:
            continue

    return "other", None


def compute_sha256(file_path: Path) -> Optional[str]:
    """Compute SHA256 hash of a file."""
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except OSError:
        return None


def get_file_size(file_path: Path) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return file_path.stat().st_size
    except OSError:
        return None


def scan_artifacts(context: RunContext, config_dir: Path) -> ScanResult:
    """
    Main entry point: Scan and index all artifacts in the run folder.

    Uses known_artifact_patterns.json to classify artifacts by type.
    Records read_status and sha256 for each artifact.
    """
    errors = []
    artifacts = []
    run_root = context.run_folder.resolve()

    # Load patterns config
    patterns_path = config_dir / "known_artifact_patterns.json"
    patterns, pattern_errors = load_patterns(patterns_path)
    errors.extend(pattern_errors)

    if not patterns:
        # Use minimal fallback patterns
        patterns = [
            {"pattern": "^run\\.json$", "artifact_type": "run_json"},
            {"pattern": "^manifest\\.json$", "artifact_type": "manifest_json"},
            {"pattern": "^MANIFEST\\.sha256$", "artifact_type": "manifest_sha256"},
            {"pattern": ".*", "artifact_type": "other"},
        ]

    # Scan all files in run folder (recursive)
    for file_path in context.all_files:
        # Compute run-relative path using POSIX-style forward slashes
        try:
            resolved_file = file_path.resolve()
            rel_path = resolved_file.relative_to(run_root).as_posix()
        except Exception:
            errors.append(f"PATH_OUTSIDE_RUN: {file_path}")
            continue

        # Match artifact type
        artifact_type, matched_pattern = match_artifact_type(rel_path, patterns)

        # Determine read status and compute hash
        read_status = "SUCCESS"
        sha256 = None
        file_size = None

        if not file_path.exists():
            read_status = "NOT_FOUND"
        else:
            try:
                sha256 = compute_sha256(file_path)
                file_size = get_file_size(file_path)
                if sha256 is None:
                    read_status = "ACCESS_DENIED"
            except PermissionError:
                read_status = "ACCESS_DENIED"
            except Exception:
                read_status = "ACCESS_DENIED"

        artifact = ArtifactEntry(
            artifact_path=rel_path,
            artifact_type=artifact_type,
            read_status=read_status,
            sha256=sha256,
            file_size=file_size,
            pattern_matched=matched_pattern
        )
        artifacts.append(artifact)

    return ScanResult(artifacts=artifacts, errors=errors)
