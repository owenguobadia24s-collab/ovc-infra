"""
Pipeline Step 4: Parse Known Artifacts

Parses artifacts using type-specific parsers.
Records parse failures as ARTIFACT_MALFORMED.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .load_run import RunContext
from .scan_artifacts import ArtifactEntry


@dataclass
class ParsedArtifact:
    """A parsed artifact with content."""
    artifact_path: str
    artifact_type: str
    parse_status: str  # SUCCESS, PARSE_ERROR, SKIPPED
    content: Optional[Any] = None
    parse_error: Optional[str] = None


@dataclass
class ParseResult:
    """Result of parsing artifacts."""
    parsed: Dict[str, ParsedArtifact]  # keyed by artifact_path
    parse_failures: List[str]
    errors: List[str]


def parse_json_file(file_path: Path) -> tuple[Optional[Any], Optional[str]]:
    """Parse a JSON file. Returns (content, error)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"
    except OSError as e:
        return None, f"Read error: {e}"


def parse_jsonl_file(file_path: Path) -> tuple[Optional[List[Any]], Optional[str]]:
    """Parse a JSONL file. Returns (list of objects, error)."""
    try:
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    return None, f"JSONL parse error at line {line_num}: {e}"
        return records, None
    except OSError as e:
        return None, f"Read error: {e}"


def parse_text_file(file_path: Path) -> tuple[Optional[List[str]], Optional[str]]:
    """Parse a text file as lines. Returns (lines, error)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n\r') for line in f.readlines()]
        return lines, None
    except OSError as e:
        return None, f"Read error: {e}"


def parse_artifact(
    artifact: ArtifactEntry,
    run_folder: Path
) -> ParsedArtifact:
    """
    Parse a single artifact based on its type.

    Uses type-specific parsers only.
    """
    file_path = run_folder / artifact.artifact_path

    # Skip if file not found or access denied
    if artifact.read_status != "SUCCESS":
        return ParsedArtifact(
            artifact_path=artifact.artifact_path,
            artifact_type=artifact.artifact_type,
            parse_status="SKIPPED",
            content=None,
            parse_error=f"Skipped due to read_status: {artifact.read_status}"
        )

    # Determine parser based on artifact type
    content = None
    parse_error = None

    if artifact.artifact_type in ("run_json", "manifest_json", "data_artifact"):
        # JSON files
        if artifact.artifact_path.endswith('.jsonl'):
            content, parse_error = parse_jsonl_file(file_path)
        elif artifact.artifact_path.endswith('.json'):
            content, parse_error = parse_json_file(file_path)
        else:
            # Try JSON first for data_artifact
            content, parse_error = parse_json_file(file_path)

    elif artifact.artifact_type == "manifest_sha256":
        # Text file with hash lines
        content, parse_error = parse_text_file(file_path)

    elif artifact.artifact_type == "audit_output":
        # Audit outputs can be JSON or text
        if artifact.artifact_path.endswith('.json'):
            content, parse_error = parse_json_file(file_path)
        else:
            content, parse_error = parse_text_file(file_path)

    elif artifact.artifact_type == "other":
        # Other files - try text parsing
        content, parse_error = parse_text_file(file_path)

    else:
        parse_error = f"Unknown artifact type: {artifact.artifact_type}"

    parse_status = "SUCCESS" if parse_error is None else "PARSE_ERROR"

    return ParsedArtifact(
        artifact_path=artifact.artifact_path,
        artifact_type=artifact.artifact_type,
        parse_status=parse_status,
        content=content,
        parse_error=parse_error
    )


def parse_artifacts(
    context: RunContext,
    artifacts: List[ArtifactEntry]
) -> ParseResult:
    """
    Main entry point: Parse all scanned artifacts.

    Type-specific parsers only. Parse failures are recorded
    but do not block processing of other artifacts.
    """
    errors = []
    parse_failures = []
    parsed: Dict[str, ParsedArtifact] = {}

    for artifact in artifacts:
        parsed_artifact = parse_artifact(artifact, context.run_folder)
        parsed[artifact.artifact_path] = parsed_artifact

        if parsed_artifact.parse_status == "PARSE_ERROR":
            parse_failures.append(
                f"ARTIFACT_MALFORMED: {artifact.artifact_path}: {parsed_artifact.parse_error}"
            )

    return ParseResult(
        parsed=parsed,
        parse_failures=parse_failures,
        errors=errors
    )
