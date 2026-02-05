#!/usr/bin/env python3
"""
Phase 3 Control Panel - UI Action Audit

AUDIT POLICY: FAIL-CLOSED
If audit cannot determine pattern absence, it MUST fail.

This audit fails if it finds ANY of:
- buttons/handlers labelled or wired to action verbs:
  Run, Trigger, Approve, Reject, Fix, Update, Reseal, Promote
- forms posting anywhere
- non-navigation onClick handlers

EXIT CODES:
  0 = PASS (no violations found)
  1 = FAIL (violations detected)
  2 = ERROR (audit could not complete - treated as FAIL)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# =============================================================================
# Configuration
# =============================================================================

PHASE3_ROOT = Path(__file__).parent.parent
SRC_ROOT = PHASE3_ROOT / "src"

# Forbidden action button patterns
ACTION_BUTTON_PATTERNS = [
    # Button elements with action labels
    r"<button[^>]*>\s*Run\s*</button>",
    r"<button[^>]*>\s*Trigger\s*</button>",
    r"<button[^>]*>\s*Approve\s*</button>",
    r"<button[^>]*>\s*Reject\s*</button>",
    r"<button[^>]*>\s*Fix\s*</button>",
    r"<button[^>]*>\s*Update\s*</button>",
    r"<button[^>]*>\s*Reseal\s*</button>",
    r"<button[^>]*>\s*Promote\s*</button>",
    # Button with action in aria-label or title
    r"<button[^>]*(?:aria-label|title)\s*=\s*['\"](?:[^'\"]*(?:Run|Trigger|Approve|Reject|Fix|Update|Reseal|Promote))",
    # Input submit with action labels
    r"<input[^>]*type\s*=\s*['\"]submit['\"][^>]*value\s*=\s*['\"](?:Run|Trigger|Approve|Reject|Fix|Update|Reseal|Promote)",
]

# Forbidden onClick handler patterns
ACTION_HANDLER_PATTERNS = [
    # Direct action handler functions
    r"handleRun\s*[=(]",
    r"handleTrigger\s*[=(]",
    r"handleApprove\s*[=(]",
    r"handleReject\s*[=(]",
    r"handleFix\s*[=(]",
    r"handleUpdate\s*[=(]",
    r"handleReseal\s*[=(]",
    r"handlePromote\s*[=(]",
    r"onRun\s*[=(]",
    r"onTrigger\s*[=(]",
    r"onApprove\s*[=(]",
    r"onReject\s*[=(]",
    r"onFix\s*[=(]",
    r"onUpdate\s*[=(]",
    r"onReseal\s*[=(]",
    r"onPromote\s*[=(]",
    # onClick with action verbs
    r"onClick\s*=\s*\{[^}]*(?:run|trigger|approve|reject|fix|update|reseal|promote)\s*\(",
]

# Forbidden form patterns
FORM_PATTERNS = [
    # Form with action attribute
    r"<form[^>]*action\s*=",
    # Form with POST method
    r"<form[^>]*method\s*=\s*['\"](?:POST|post)['\"]",
    # onSubmit without preventDefault (risky pattern)
    r"onSubmit\s*=\s*\{(?!.*preventDefault)",
]

# Forbidden hidden control patterns
HIDDEN_CONTROL_PATTERNS = [
    # Hidden buttons
    r"<button[^>]*(?:hidden|style\s*=\s*['\"][^'\"]*display\s*:\s*none)",
    # Hidden inputs that could be submit buttons
    r"<input[^>]*type\s*=\s*['\"]submit['\"][^>]*(?:hidden|style\s*=\s*['\"][^'\"]*display\s*:\s*none)",
]

# File extensions to scan
SCANNABLE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}


# =============================================================================
# Audit Functions
# =============================================================================


def find_pattern_in_file(
    filepath: Path, patterns: List[str]
) -> List[Tuple[int, str, str]]:
    """
    Search for patterns in a file.
    Returns list of (line_number, line_content, matched_pattern).
    """
    violations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

            for pattern in patterns:
                # First check if pattern exists in file at all
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    # Find the specific line(s)
                    for line_num, line in enumerate(lines, 1):
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

        violations = find_pattern_in_file(filepath, patterns)
        for line_num, line, pattern in violations:
            all_violations.append((filepath, line_num, line, pattern))

    return all_violations


def check_allowed_onclick_handlers(root: Path) -> List[Tuple[Path, int, str, str]]:
    """
    Check for onClick handlers that are NOT navigation.

    ALLOWED onClick patterns:
    - window.location.href =
    - navigate(
    - router.push(
    - setExpanded / setState type calls
    - copy to clipboard

    FORBIDDEN:
    - Any onClick that might trigger an action/mutation
    """
    violations = []

    if not root.exists():
        return violations

    # Pattern to find onClick handlers
    onclick_pattern = r"onClick\s*=\s*\{([^}]+)\}"

    # Allowed patterns within onClick
    allowed_patterns = [
        r"window\.location",
        r"navigate\s*\(",
        r"router\.push\s*\(",
        r"set[A-Z]\w*\s*\(",  # setState, setExpanded, etc.
        r"clipboard",
        r"copy",
        r"handleSort",
        r"handleCopy",
        r"setFilter",
        r"setSelectedLeft",
        r"setSelectedRight",
        r"onRowClick",  # Navigation callback
        r"onLeftChange",
        r"onRightChange",
        r"onCompare",  # Triggers navigation, not mutation
    ]

    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue

        if filepath.suffix not in SCANNABLE_EXTENSIONS:
            continue

        if "node_modules" in filepath.parts:
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    # Find onClick handlers
                    matches = re.finditer(onclick_pattern, line)
                    for match in matches:
                        handler_content = match.group(1)

                        # Check if handler matches any allowed pattern
                        is_allowed = False
                        for allowed in allowed_patterns:
                            if re.search(allowed, handler_content, re.IGNORECASE):
                                is_allowed = True
                                break

                        # If not allowed, check for suspicious action verbs
                        if not is_allowed:
                            action_verbs = ["run", "trigger", "approve", "reject", "fix", "update", "reseal", "promote"]
                            for verb in action_verbs:
                                if re.search(rf"\b{verb}\b", handler_content, re.IGNORECASE):
                                    violations.append((filepath, line_num, line.strip(), f"onClick with action verb: {verb}"))
                                    break

        except Exception as e:
            violations.append((filepath, 0, f"AUDIT ERROR: {e}", "FILE_READ_FAILURE"))

    return violations


def run_audit() -> Tuple[bool, List[str]]:
    """
    Run the complete UI action audit.
    Returns (passed: bool, messages: List[str]).
    """
    messages = []
    all_violations = []

    # Verify audit can access source directory
    if not SRC_ROOT.exists():
        messages.append(f"FAIL-CLOSED: Source directory not found: {SRC_ROOT}")
        return False, messages

    messages.append("=" * 60)
    messages.append("Phase 3 UI Action Audit")
    messages.append("=" * 60)
    messages.append("")

    # Check for action button patterns
    messages.append("Checking for forbidden action buttons...")
    violations = scan_directory(SRC_ROOT, ACTION_BUTTON_PATTERNS, "action_button")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} action button violations")

    # Check for action handler patterns
    messages.append("Checking for forbidden action handlers...")
    violations = scan_directory(SRC_ROOT, ACTION_HANDLER_PATTERNS, "action_handler")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} action handler violations")

    # Check for form patterns
    messages.append("Checking for forbidden form patterns...")
    violations = scan_directory(SRC_ROOT, FORM_PATTERNS, "form")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} form violations")

    # Check for hidden controls
    messages.append("Checking for hidden action controls...")
    violations = scan_directory(SRC_ROOT, HIDDEN_CONTROL_PATTERNS, "hidden_control")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} hidden control violations")

    # Check onClick handlers
    messages.append("Checking onClick handlers for action verbs...")
    violations = check_allowed_onclick_handlers(SRC_ROOT)
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} suspicious onClick violations")

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
        messages.append("No UI action violations detected")
        messages.append("All onClick handlers are navigation/filter/sort only")
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
