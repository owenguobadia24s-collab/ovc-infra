"""
Pipeline Step 1: Load Run Context

Reads run.json and indexes all files under the run folder.
Fail-closed on missing or malformed run envelope.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class RunContext:
    """Context loaded from a run folder."""
    run_id: str
    run_folder: Path
    run_json_path: Path
    run_json_content: Dict[str, Any]
    run_type: str
    run_created_utc: str
    all_files: List[Path]

    # Optional fields from run.json
    operation_id: Optional[str] = None
    option: Optional[str] = None
    git_commit: Optional[str] = None
    working_tree_state: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[List[str]] = None

    # Load status
    load_errors: List[str] = field(default_factory=list)


@dataclass
class LoadResult:
    """Result of loading a run context."""
    success: bool
    context: Optional[RunContext]
    errors: List[str]


def find_run_folder(run_id: str, runs_root: Path) -> Optional[Path]:
    """
    Locate the run folder for a given run_id.

    Searches in canonical location: .codex/RUNS/<run_id>/
    """
    run_folder = runs_root / run_id
    if run_folder.is_dir():
        return run_folder
    return None


def index_files(run_folder: Path) -> List[Path]:
    """
    Index all files in the run folder recursively.

    Walks the entire directory tree to capture nested artifacts.
    Returns absolute paths, deterministically sorted by full string path.
    Relative paths are computed at scan time.
    """
    files = []
    run_root = run_folder.resolve()
    if run_root.is_dir():
        for root, _dirs, filenames in os.walk(run_root):
            root_path = Path(root)
            for filename in filenames:
                files.append(root_path / filename)
    return sorted(files, key=lambda p: str(p))


def load_run_json(run_folder: Path) -> tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Load and parse run.json from the run folder.

    Returns (content, errors) tuple.
    """
    errors = []
    run_json_path = run_folder / "run.json"

    if not run_json_path.exists():
        errors.append(f"ARTIFACT_MISSING: run.json not found at {run_json_path}")
        return None, errors

    try:
        with open(run_json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"ARTIFACT_MALFORMED: run.json parse error: {e}")
        return None, errors
    except OSError as e:
        errors.append(f"ACCESS_DENIED: Cannot read run.json: {e}")
        return None, errors

    return content, errors


def validate_run_envelope(content: Dict[str, Any]) -> List[str]:
    """
    Validate run.json against RUN_ENVELOPE_STANDARD_v0_1.

    Required fields: run_id, created_utc, run_type
    """
    errors = []
    required_fields = ["run_id", "created_utc", "run_type"]

    for field_name in required_fields:
        if field_name not in content:
            errors.append(f"RUN_ENVELOPE_MALFORMED: Missing required field '{field_name}'")
        elif content[field_name] is None:
            errors.append(f"RUN_ENVELOPE_MALFORMED: Field '{field_name}' is null")

    return errors


def load_run(run_id: str, runs_root: Path) -> LoadResult:
    """
    Main entry point: Load run context for interpretation.

    This is a fail-closed operation. If the run cannot be loaded,
    the result will indicate failure with specific errors.
    """
    errors = []

    # Find run folder
    run_folder = find_run_folder(run_id, runs_root)
    if run_folder is None:
        errors.append(f"ARTIFACT_MISSING: Run folder not found for run_id '{run_id}' under {runs_root}")
        return LoadResult(success=False, context=None, errors=errors)

    # Index all files
    all_files = index_files(run_folder)

    # Load run.json
    run_json_path = run_folder / "run.json"
    content, load_errors = load_run_json(run_folder)
    errors.extend(load_errors)

    if content is None:
        return LoadResult(success=False, context=None, errors=errors)

    # Validate envelope structure
    validation_errors = validate_run_envelope(content)
    errors.extend(validation_errors)

    if validation_errors:
        # Critical validation errors - cannot proceed
        return LoadResult(success=False, context=None, errors=errors)

    # Build context
    context = RunContext(
        run_id=content["run_id"],
        run_folder=run_folder,
        run_json_path=run_json_path,
        run_json_content=content,
        run_type=content["run_type"],
        run_created_utc=content["created_utc"],
        all_files=all_files,
        operation_id=content.get("operation_id"),
        option=content.get("option"),
        git_commit=content.get("git_commit"),
        working_tree_state=content.get("working_tree_state"),
        inputs=content.get("inputs"),
        outputs=content.get("outputs"),
        load_errors=errors
    )

    return LoadResult(success=True, context=context, errors=errors)
