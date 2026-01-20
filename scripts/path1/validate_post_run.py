#!/usr/bin/env python3
"""
Path 1 Evidence Run Post-Run Validator

Validates the structural integrity and content sanity of a Path 1 evidence run.
Does NOT interpret results or query the database.

Usage:
    python scripts/path1/validate_post_run.py --run-id p1_20260120_001
    python scripts/path1/validate_post_run.py --run-id p1_20260120_001 --strict
    python scripts/path1/validate_post_run.py --run-id p1_20260120_001 --json

Exit Codes:
    0 = PASS (all checks passed)
    1 = FAIL (one or more integrity violations)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# =============================================================================
# Configuration: Expected Structure
# =============================================================================

EXPECTED_SCORES = {
    'DIS': 'v1_1',
    'RES': 'v1_0',
    'LID': 'v1_0',
}

# Minimum byte threshold for study output files
MIN_OUTPUT_BYTES = 200

# Fatal markers that indicate psql/execution failure
FATAL_MARKERS = [
    'ERROR:',
    'FATAL:',
    'psql: error:',
    'could not connect',
    'permission denied',
    'syntax error',
    'relation .* does not exist',
]

# Compile regex patterns
FATAL_PATTERNS = [re.compile(p, re.IGNORECASE) for p in FATAL_MARKERS]


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class Violation:
    """A single validation violation."""
    category: str  # 'structure', 'content', 'consistency', 'strict'
    path: str
    message: str
    
    def to_dict(self):
        return {
            'type': self.category,
            'path': self.path,
            'message': self.message,
        }


@dataclass
class ValidationResult:
    """Aggregated validation results."""
    run_id: str
    passed: bool = True
    files_checked: int = 0
    violations: list = field(default_factory=list)
    
    def add_violation(self, category: str, path: str, message: str):
        self.violations.append(Violation(category, path, message))
        self.passed = False
    
    def to_dict(self):
        return {
            'run_id': self.run_id,
            'status': 'PASS' if self.passed else 'FAIL',
            'files_checked': self.files_checked,
            'violation_count': len(self.violations),
            'violations': [v.to_dict() for v in self.violations],
        }


# =============================================================================
# Validators
# =============================================================================

def validate_structure(repo_root: Path, run_id: str, result: ValidationResult):
    """Step 2: Validate required directories and files exist."""
    
    report_dir = repo_root / 'reports' / 'path1' / 'evidence' / 'runs' / run_id
    output_dir = report_dir / 'outputs'
    sql_dir = repo_root / 'sql' / 'path1' / 'evidence' / 'runs' / run_id
    
    # A) Required directories
    required_dirs = [
        report_dir,
        output_dir,
        sql_dir,
    ]
    
    for d in required_dirs:
        if not d.exists():
            result.add_violation('structure', str(d), f'Required directory missing: {d.name}')
        elif not d.is_dir():
            result.add_violation('structure', str(d), f'Expected directory but found file: {d.name}')
    
    # B) Required files
    required_files = [
        report_dir / 'RUN.md',
    ]
    
    # Add score-specific files
    for score, version in EXPECTED_SCORES.items():
        required_files.append(report_dir / f'{score}_{version}_evidence.md')
        required_files.append(output_dir / f'study_{score.lower()}_{version}.txt')
        required_files.append(sql_dir / f'study_{score.lower()}_{version}.sql')
    
    for f in required_files:
        if not f.exists():
            result.add_violation('structure', str(f), f'Required file missing: {f.name}')
        elif not f.is_file():
            result.add_violation('structure', str(f), f'Expected file but found directory: {f.name}')
        else:
            result.files_checked += 1


def validate_output_content(repo_root: Path, run_id: str, result: ValidationResult):
    """Step 3a: Validate study output files for sanity."""
    
    output_dir = repo_root / 'reports' / 'path1' / 'evidence' / 'runs' / run_id / 'outputs'
    
    for score, version in EXPECTED_SCORES.items():
        output_file = output_dir / f'study_{score.lower()}_{version}.txt'
        
        if not output_file.exists():
            # Already reported in structure check
            continue
        
        try:
            content = output_file.read_text(encoding='utf-8')
        except Exception as e:
            result.add_violation('content', str(output_file), f'Cannot read file: {e}')
            continue
        
        file_size = output_file.stat().st_size
        
        # Check minimum size
        if file_size < MIN_OUTPUT_BYTES:
            result.add_violation(
                'content', str(output_file),
                f'File too small ({file_size} bytes < {MIN_OUTPUT_BYTES} min). Possibly empty or truncated.'
            )
            continue
        
        # Check for fatal markers
        for pattern in FATAL_PATTERNS:
            match = pattern.search(content)
            if match:
                # Extract context around match
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace('\n', ' ')
                result.add_violation(
                    'content', str(output_file),
                    f'Fatal marker detected: "{match.group()}" near: ...{context}...'
                )
                break
        
        # Check for table-like output (psql result indicator)
        has_pipe = '|' in content
        has_row_count = bool(re.search(r'\(\d+ rows?\)', content))
        
        if not has_pipe and not has_row_count:
            result.add_violation(
                'content', str(output_file),
                'No table delimiters (|) or row count markers found. Output may be malformed.'
            )


def validate_run_md(repo_root: Path, run_id: str, result: ValidationResult) -> dict:
    """Step 3b: Validate RUN.md content and extract metadata."""
    
    run_md = repo_root / 'reports' / 'path1' / 'evidence' / 'runs' / run_id / 'RUN.md'
    metadata = {}
    
    if not run_md.exists():
        return metadata
    
    try:
        content = run_md.read_text(encoding='utf-8')
    except Exception as e:
        result.add_violation('content', str(run_md), f'Cannot read file: {e}')
        return metadata
    
    # Required sections
    required_sections = [
        ('Run Metadata', r'##\s*Run Metadata'),
        ('Score Versions Used', r'###?\s*Score Versions Used'),
        ('Invariants Reminder', r'##\s*Invariants Reminder'),
        ('Artifacts', r'##\s*Artifacts(?:\s+Generated)?'),
    ]
    
    for section_name, pattern in required_sections:
        if not re.search(pattern, content, re.IGNORECASE):
            result.add_violation(
                'content', str(run_md),
                f'Missing required section: "{section_name}"'
            )
    
    # Check score versions are listed
    for score, version in EXPECTED_SCORES.items():
        version_display = version.replace('_', '.')
        pattern = rf'{score}\s*\|\s*v{version_display[1:]}'  # e.g., "DIS | v1.1"
        if not re.search(pattern, content, re.IGNORECASE):
            result.add_violation(
                'content', str(run_md),
                f'Missing score version entry: {score} {version_display}'
            )
    
    # Check artifact references
    for score, version in EXPECTED_SCORES.items():
        artifact_name = f'study_{score.lower()}_{version}.txt'
        if artifact_name not in content:
            result.add_violation(
                'content', str(run_md),
                f'Missing artifact reference: {artifact_name}'
            )
    
    # Extract metadata for cross-validation
    run_id_match = re.search(r'\|\s*`run_id`\s*\|\s*`([^`]+)`', content)
    if run_id_match:
        metadata['run_id'] = run_id_match.group(1)
    
    symbol_match = re.search(r'\|\s*`symbol\(s\)`\s*\|\s*`([^`]+)`', content)
    if symbol_match:
        metadata['symbol'] = symbol_match.group(1)
    
    n_obs_match = re.search(r'\|\s*`n_observations`\s*\|\s*`?(\d+)`?', content)
    if n_obs_match:
        metadata['n_observations'] = int(n_obs_match.group(1))
    
    date_start_match = re.search(r'\|\s*`date_range_start`\s*\|\s*`([^`]+)`', content)
    if date_start_match:
        metadata['date_start'] = date_start_match.group(1)
    
    date_end_match = re.search(r'\|\s*`date_range_end`\s*\|\s*`([^`]+)`', content)
    if date_end_match:
        metadata['date_end'] = date_end_match.group(1)
    
    return metadata


def validate_evidence_reports(repo_root: Path, run_id: str, result: ValidationResult):
    """Step 3c: Validate evidence report files."""
    
    report_dir = repo_root / 'reports' / 'path1' / 'evidence' / 'runs' / run_id
    
    for score, version in EXPECTED_SCORES.items():
        evidence_file = report_dir / f'{score}_{version}_evidence.md'
        
        if not evidence_file.exists():
            continue
        
        try:
            content = evidence_file.read_text(encoding='utf-8')
        except Exception as e:
            result.add_violation('content', str(evidence_file), f'Cannot read file: {e}')
            continue
        
        result.files_checked += 1
        
        # Check for invariants/disclaimer section (aligned with generated evidence reports)
        # Accept any of: "## Invariants" header, "Association ≠ Predictability", or "Correlation is not causation"
        has_invariants_header = bool(re.search(r'##\s*Invariants', content, re.IGNORECASE))
        has_association_warning = 'Association ≠ Predictability' in content
        has_causation_warning = 'correlation is not causation' in content.lower()
        
        if not (has_invariants_header or has_association_warning or has_causation_warning):
            result.add_violation(
                'content', str(evidence_file),
                'Missing invariants section or warning (expected: ## Invariants, "Association ≠ Predictability", or "Correlation is not causation")'
            )


def validate_consistency(repo_root: Path, run_id: str, metadata: dict, result: ValidationResult, strict: bool):
    """Step 4: Cross-file consistency checks."""
    
    # Check run_id matches folder name
    if 'run_id' in metadata and metadata['run_id'] != run_id:
        result.add_violation(
            'consistency', f'runs/{run_id}/RUN.md',
            f'run_id mismatch: folder={run_id}, RUN.md={metadata["run_id"]}'
        )
    
    # Check INDEX.md contains this run
    index_md = repo_root / 'reports' / 'path1' / 'evidence' / 'INDEX.md'
    
    if index_md.exists():
        try:
            index_content = index_md.read_text(encoding='utf-8')
            result.files_checked += 1
            
            # Look for run_id in index table
            index_pattern = rf'\|\s*{re.escape(run_id)}\s*\|'
            if not re.search(index_pattern, index_content):
                if strict:
                    result.add_violation(
                        'consistency', str(index_md),
                        f'Run ID {run_id} not found in INDEX.md'
                    )
                else:
                    # Non-strict: just warn via print, don't fail
                    print(f"WARN: Run ID {run_id} not found in INDEX.md (non-strict mode)")
            
            # Check link format
            link_pattern = rf'\[RUN\.md\]\(runs/{re.escape(run_id)}/RUN\.md\)'
            if re.search(index_pattern, index_content) and not re.search(link_pattern, index_content):
                result.add_violation(
                    'consistency', str(index_md),
                    f'Invalid link format for {run_id} in INDEX.md'
                )
        except Exception as e:
            result.add_violation('consistency', str(index_md), f'Cannot read INDEX.md: {e}')
    elif strict:
        result.add_violation(
            'consistency', str(index_md),
            'INDEX.md does not exist'
        )


def validate_strict(repo_root: Path, run_id: str, result: ValidationResult):
    """Step 5: Strict-mode additional checks."""
    
    sql_dir = repo_root / 'sql' / 'path1' / 'evidence' / 'runs' / run_id
    report_dir = repo_root / 'reports' / 'path1' / 'evidence' / 'runs' / run_id
    
    # Check SQL headers
    for score, version in EXPECTED_SCORES.items():
        sql_file = sql_dir / f'study_{score.lower()}_{version}.sql'
        
        if not sql_file.exists():
            continue
        
        try:
            content = sql_file.read_text(encoding='utf-8')
            result.files_checked += 1
            
            # Check for required header elements
            if 'Run ID:' not in content and run_id not in content:
                result.add_violation(
                    'strict', str(sql_file),
                    'SQL file missing Run ID in header'
                )
            
            if 'FROZEN SCORE VERSION' not in content.upper():
                result.add_violation(
                    'strict', str(sql_file),
                    'SQL file missing FROZEN SCORE VERSION declaration'
                )
            
            if 'SOURCE VIEW' not in content.upper():
                result.add_violation(
                    'strict', str(sql_file),
                    'SQL file missing SOURCE VIEW declaration'
                )
        except Exception as e:
            result.add_violation('strict', str(sql_file), f'Cannot read SQL file: {e}')
    
    # Check INDEX.md has Last Updated
    index_md = repo_root / 'reports' / 'path1' / 'evidence' / 'INDEX.md'
    if index_md.exists():
        try:
            content = index_md.read_text(encoding='utf-8')
            if 'Last Updated' not in content:
                result.add_violation(
                    'strict', str(index_md),
                    'INDEX.md missing "Last Updated" field'
                )
            elif re.search(r'Last Updated:\s*$', content, re.MULTILINE):
                result.add_violation(
                    'strict', str(index_md),
                    'INDEX.md "Last Updated" field is blank'
                )
        except Exception:
            pass  # Already reported elsewhere
    
    # Check no NOOP markers in run folder
    for noop_file in report_dir.glob('NOOP_*.txt'):
        result.add_violation(
            'strict', str(noop_file),
            f'NOOP marker file found in run folder (should not exist): {noop_file.name}'
        )


# =============================================================================
# Report Generation
# =============================================================================

def print_report(result: ValidationResult, json_output: bool):
    """Print validation report."""
    
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return
    
    # Human-readable format
    print()
    print("=" * 60)
    if result.passed:
        print(f"PASS: run_id={result.run_id}")
    else:
        print(f"FAIL: run_id={result.run_id}")
    print("=" * 60)
    
    print(f"\nSummary:")
    print(f"  Files checked: {result.files_checked}")
    print(f"  Violations: {len(result.violations)}")
    
    if result.violations:
        print(f"\nViolations by category:")
        
        # Group by category
        by_category = {}
        for v in result.violations:
            by_category.setdefault(v.category, []).append(v)
        
        for category, violations in sorted(by_category.items()):
            print(f"\n  [{category.upper()}] ({len(violations)} issues)")
            for v in violations:
                # Shorten path for display
                short_path = v.path.split('runs/')[-1] if 'runs/' in v.path else v.path.split('evidence/')[-1]
                print(f"    - {short_path}")
                print(f"      {v.message}")
    
    print()


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Validate Path 1 Evidence Run structural integrity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--run-id', required=True,
        help='Run ID to validate (e.g., p1_20260120_001)'
    )
    parser.add_argument(
        '--repo-root', default='.',
        help='Repository root directory (default: current directory)'
    )
    parser.add_argument(
        '--strict', action='store_true',
        help='Enable strict mode with additional checks'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output machine-readable JSON report'
    )
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    run_id = args.run_id
    
    # Validate repo root
    if not (repo_root / 'reports' / 'path1' / 'evidence').exists():
        print(f"ERROR: Invalid repo root or missing evidence directory: {repo_root}")
        sys.exit(1)
    
    # Initialize result
    result = ValidationResult(run_id=run_id)
    
    # Run validators
    if not args.json:
        print(f"Validating run: {run_id}")
        print(f"Repo root: {repo_root}")
        print(f"Strict mode: {args.strict}")
    
    # Step 2: Structure
    validate_structure(repo_root, run_id, result)
    
    # Step 3: Content
    validate_output_content(repo_root, run_id, result)
    metadata = validate_run_md(repo_root, run_id, result)
    validate_evidence_reports(repo_root, run_id, result)
    
    # Step 4: Consistency
    validate_consistency(repo_root, run_id, metadata, result, args.strict)
    
    # Step 5: Strict checks
    if args.strict:
        validate_strict(repo_root, run_id, result)
    
    # Output report
    print_report(result, args.json)
    
    # Exit code
    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
