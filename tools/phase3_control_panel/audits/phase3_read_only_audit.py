#!/usr/bin/env python3
"""
Phase 3 Control Panel - Read-Only Audit

AUDIT POLICY: FAIL-CLOSED
If audit cannot determine pattern absence, it MUST fail.

This audit fails if it finds ANY of:
- open(..., "w"), writeFile, file writes
- database write verbs
- git write commands
- imports of sealing modules
- any path write under .codex/ / reports/ / registry roots

EXIT CODES:
  0 = PASS (no violations found)
  1 = FAIL (violations detected)
  2 = ERROR (audit could not complete - treated as FAIL)
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Tuple, Optional

# =============================================================================
# Configuration
# =============================================================================

PHASE3_ROOT = Path(__file__).parent.parent
SRC_ROOT = PHASE3_ROOT / "src"
CONFIG_ROOT = PHASE3_ROOT / "config"

# Patterns that indicate file write operations
FILE_WRITE_PATTERNS = [
    # Python file writes
    r"open\s*\([^)]*['\"][wa+x]['\"]",
    r"open\s*\([^)]*mode\s*=\s*['\"][wa+x]",
    r"\.write\s*\(",
    r"\.writelines\s*\(",
    # Node.js file writes
    r"writeFileSync",
    r"writeFile\s*\(",
    r"appendFileSync",
    r"appendFile\s*\(",
    r"fs\.write",
    r"createWriteStream",
    # Deno file writes
    r"Deno\.writeTextFile",
    r"Deno\.writeFile",
]

# Patterns that indicate subprocess execution
SUBPROCESS_PATTERNS = [
    r"subprocess\.run",
    r"subprocess\.call",
    r"subprocess\.Popen",
    r"os\.system",
    r"os\.popen",
    r"os\.exec",
    r"child_process",
    r"spawn\s*\(",
    r"execSync",
    r"spawnSync",
]

# Patterns that indicate git write commands
GIT_WRITE_PATTERNS = [
    r"git\s+push",
    r"git\s+commit",
    r"git\s+add",
    r"git\s+reset",
    r"git\s+checkout",
    r"git\s+merge",
    r"git\s+rebase",
]

# Patterns that indicate sealing module imports
# NOTE: "SealStatus" and "ManifestSeal" are display-only types, not sealing operations
SEALING_PATTERNS = [
    r"import\s+.*\bseal_run_folder\b",
    r"from\s+.*\bseal_run_folder\b",
    r"require\s*\([^)]*seal_run_folder",
    r"seal_run_folder\s*\(",
    r"compute_root_sha256\s*\(",
    r"MANIFEST\.sha256.*=.*write",
    r"manifest\.json.*=.*write",
    r"import\s+.*\bsealing\b",
    r"from\s+.*\bsealing\b",
]

# Patterns that indicate database write operations
# NOTE: "truncate" as a string method (e.g., truncateRunId) is NOT SQL TRUNCATE
DATABASE_WRITE_PATTERNS = [
    r"INSERT\s+INTO",
    r"UPDATE\s+\w+\s+SET",
    r"DELETE\s+FROM",
    r"DROP\s+TABLE",
    r"CREATE\s+TABLE",
    r"ALTER\s+TABLE",
    r"TRUNCATE\s+TABLE",
    r"\.execute\s*\([^)]*INSERT",
    r"\.execute\s*\([^)]*UPDATE",
    r"\.execute\s*\([^)]*DELETE",
]

# Forbidden path patterns (writes to canon paths)
FORBIDDEN_PATH_PATTERNS = [
    r"\.codex/",
    r"reports/",
    r"docs/phase_2_2/",
    r"docs/governance/",
]

# File extensions to scan
SCANNABLE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sh", ".ps1"}


# =============================================================================
# Audit Functions
# =============================================================================


def find_pattern_in_file(
    filepath: Path, patterns: List[str], pattern_name: str
) -> List[Tuple[int, str, str]]:
    """
    Search for patterns in a file.
    Returns list of (line_number, line_content, matched_pattern).
    """
    violations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip(), pattern))
    except Exception as e:
        # Fail-closed: if we can't read the file, that's a failure
        violations.append((0, f"AUDIT ERROR: {e}", "FILE_READ_FAILURE"))

    return violations


def scan_directory(
    root: Path, patterns: List[str], pattern_name: str
) -> List[Tuple[Path, int, str, str]]:
    """
    Scan a directory for pattern violations.
    Returns list of (file_path, line_number, line_content, matched_pattern).
    """
    all_violations = []

    if not root.exists():
        return all_violations

    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue

        if filepath.suffix not in SCANNABLE_EXTENSIONS:
            continue

        # Skip node_modules
        if "node_modules" in filepath.parts:
            continue

        violations = find_pattern_in_file(filepath, patterns, pattern_name)
        for line_num, line, pattern in violations:
            all_violations.append((filepath, line_num, line, pattern))

    return all_violations


def check_forbidden_path_writes(root: Path) -> List[Tuple[Path, int, str, str]]:
    """
    Check for writes to forbidden paths (.codex/, reports/, etc.).
    """
    violations = []

    # Patterns that combine write operations with forbidden paths
    combined_patterns = []
    for path_pattern in FORBIDDEN_PATH_PATTERNS:
        for write_pattern in FILE_WRITE_PATTERNS[:4]:  # File open patterns
            combined_patterns.append(f"{write_pattern}.*{path_pattern}")
            combined_patterns.append(f"{path_pattern}.*{write_pattern}")

    return scan_directory(root, combined_patterns, "forbidden_path_write")


def run_audit() -> Tuple[bool, List[str]]:
    """
    Run the complete read-only audit.
    Returns (passed: bool, messages: List[str]).
    """
    messages = []
    all_violations = []

    # Verify audit can access source directory
    if not SRC_ROOT.exists():
        messages.append(f"FAIL-CLOSED: Source directory not found: {SRC_ROOT}")
        return False, messages

    messages.append("=" * 60)
    messages.append("Phase 3 Read-Only Audit")
    messages.append("=" * 60)
    messages.append("")

    # Check for file write patterns
    messages.append("Checking for file write operations...")
    violations = scan_directory(SRC_ROOT, FILE_WRITE_PATTERNS, "file_write")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} file write violations")

    # Check for subprocess patterns
    messages.append("Checking for subprocess execution...")
    violations = scan_directory(SRC_ROOT, SUBPROCESS_PATTERNS, "subprocess")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} subprocess violations")

    # Check for git write patterns
    messages.append("Checking for git write commands...")
    violations = scan_directory(SRC_ROOT, GIT_WRITE_PATTERNS, "git_write")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} git write violations")

    # Check for sealing imports
    messages.append("Checking for sealing module imports...")
    violations = scan_directory(SRC_ROOT, SEALING_PATTERNS, "sealing")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} sealing violations")

    # Check for database writes
    messages.append("Checking for database write operations...")
    violations = scan_directory(SRC_ROOT, DATABASE_WRITE_PATTERNS, "database_write")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} database write violations")

    # Check for forbidden path writes
    messages.append("Checking for writes to forbidden paths...")
    violations = check_forbidden_path_writes(SRC_ROOT)
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} forbidden path violations")

    messages.append("")

    # Report violations
    if all_violations:
        messages.append("=" * 60)
        messages.append("VIOLATIONS DETECTED")
        messages.append("=" * 60)

        for filepath, line_num, line, pattern in all_violations:
            rel_path = filepath.relative_to(PHASE3_ROOT) if filepath.is_relative_to(PHASE3_ROOT) else filepath
            messages.append(f"")
            messages.append(f"File: {rel_path}")
            messages.append(f"Line: {line_num}")
            messages.append(f"Pattern: {pattern}")
            messages.append(f"Content: {line[:100]}{'...' if len(line) > 100 else ''}")

        messages.append("")
        messages.append("=" * 60)
        messages.append("AUDIT RESULT: FAIL")
        messages.append(f"Total violations: {len(all_violations)}")
        messages.append("=" * 60)

        return False, messages
    else:
        messages.append("=" * 60)
        messages.append("AUDIT RESULT: PASS")
        messages.append("No read-only violations detected")
        messages.append("=" * 60)

        return True, messages


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point. Returns exit code."""
    try:
        passed, messages = run_audit()

        for msg in messages:
            print(msg)

        if passed:
            return 0
        else:
            return 1

    except Exception as e:
        # Fail-closed: any exception is a failure
        print("=" * 60)
        print("AUDIT ERROR - FAIL-CLOSED")
        print("=" * 60)
        print(f"Error: {e}")
        print("")
        print("Audit could not complete. Treating as FAILURE.")
        print("=" * 60)
        return 2


if __name__ == "__main__":
    sys.exit(main())
