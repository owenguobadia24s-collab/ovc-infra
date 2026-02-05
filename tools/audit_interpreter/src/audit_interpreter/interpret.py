"""
Phase 4 Audit Interpreter - Main Orchestrator

Orchestrates the interpretation pipeline:
1. Load run context
2. Detect seal
3. Scan artifacts
4. Parse artifacts
5. Classify failures
6. Build report
7. Validate report
8. Emit report

NON-AUTHORITATIVE: This interpreter is read-only and derived.
Truth resides in source artifacts.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

from .pipeline.load_run import load_run, LoadResult
from .pipeline.detect_seal import detect_seal, SealStatus
from .pipeline.scan_artifacts import scan_artifacts, ScanResult
from .pipeline.parse_artifacts import parse_artifacts, ParseResult
from .pipeline.classify_failures import classify_failures, ClassificationResult
from .pipeline.build_report import build_report
from .pipeline.validate_report import validate_report, ValidationResult


# Canonical paths
DEFAULT_RUNS_ROOT = Path(".codex/RUNS")
SCHEMA_PATH = Path("docs/contracts/schemas/AUDIT_INTERPRETATION_REPORT_v0.1.json")
OUTPUT_FILENAME = "audit_interpretation_v0.1.json"


@dataclass
class InterpretResult:
    """Result of interpretation."""
    success: bool
    report: Optional[Dict[str, Any]]
    output_path: Optional[Path]
    errors: list[str]


def get_config_dir() -> Path:
    """Get the config directory path."""
    return Path(__file__).parent / "config"


def interpret_run(
    run_id: str,
    runs_root: Optional[Path] = None,
    schema_path: Optional[Path] = None,
    stdout: bool = False,
    strict: bool = False,
    repo_root: Optional[Path] = None
) -> InterpretResult:
    """
    Interpret a Phase 3 run folder and emit a canonical report.

    Args:
        run_id: The run identifier (folder name)
        runs_root: Path to runs root (default: .codex/RUNS)
        schema_path: Path to schema file (default: docs/contracts/schemas/...)
        stdout: If True, print report to stdout instead of writing file
        strict: If True, treat unknown artifacts as OUT_OF_SCOPE non-claims
        repo_root: Repository root for resolving paths (default: cwd)

    Returns:
        InterpretResult with success status, report, and any errors
    """
    errors = []

    # Resolve paths
    if repo_root is None:
        repo_root = Path.cwd()

    if runs_root is None:
        runs_root = repo_root / DEFAULT_RUNS_ROOT

    if schema_path is None:
        schema_path = repo_root / SCHEMA_PATH

    config_dir = get_config_dir()

    # =========================================================================
    # PIPELINE STEP 1: Load Run Context
    # =========================================================================
    load_result = load_run(run_id, runs_root)

    if not load_result.success:
        errors.extend(load_result.errors)
        return InterpretResult(
            success=False,
            report=None,
            output_path=None,
            errors=errors
        )

    context = load_result.context
    errors.extend(load_result.errors)

    # =========================================================================
    # PIPELINE STEP 2: Detect Seal
    # =========================================================================
    seal_status = detect_seal(context)
    errors.extend(seal_status.errors)

    # =========================================================================
    # PIPELINE STEP 3: Scan Artifacts
    # =========================================================================
    scan_result = scan_artifacts(context, config_dir)
    errors.extend(scan_result.errors)

    # =========================================================================
    # PIPELINE STEP 4: Parse Artifacts
    # =========================================================================
    parse_result = parse_artifacts(context, scan_result.artifacts)
    errors.extend(parse_result.errors)

    # =========================================================================
    # PIPELINE STEP 5: Classify Failures
    # =========================================================================
    classification = classify_failures(
        context,
        seal_status,
        scan_result.artifacts,
        parse_result,
        strict_mode=strict
    )

    # =========================================================================
    # PIPELINE STEP 6: Build Report
    # =========================================================================
    report = build_report(
        context,
        seal_status,
        scan_result.artifacts,
        classification,
        notes=None
    )

    # =========================================================================
    # PIPELINE STEP 7: Validate Report
    # =========================================================================
    validation = validate_report(report, schema_path)

    if not validation.is_valid:
        errors.extend(validation.errors)
        return InterpretResult(
            success=False,
            report=report,
            output_path=None,
            errors=errors
        )

    # =========================================================================
    # PIPELINE STEP 8: Emit Report
    # =========================================================================
    output_path = None

    if stdout:
        # Print to stdout
        print(json.dumps(report, indent=2))
    else:
        # Write to canonical path
        output_path = context.run_folder / OUTPUT_FILENAME

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
        except OSError as e:
            errors.append(f"WRITE_ERROR: Could not write report to {output_path}: {e}")
            return InterpretResult(
                success=False,
                report=report,
                output_path=None,
                errors=errors
            )

    return InterpretResult(
        success=True,
        report=report,
        output_path=output_path,
        errors=errors
    )
