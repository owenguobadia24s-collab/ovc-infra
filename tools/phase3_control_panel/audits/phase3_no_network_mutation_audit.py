#!/usr/bin/env python3
"""
Phase 3 Control Panel - No Network Mutation Audit

AUDIT POLICY: FAIL-CLOSED
If audit cannot determine pattern absence, it MUST fail.

This audit fails if it finds ANY of:
- fetch/axios with methods other than GET
- websocket connections
- GitHub API clients
- presence of workflow dispatch logic

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

# Forbidden HTTP mutation patterns
HTTP_MUTATION_PATTERNS = [
    # fetch with non-GET methods
    r"fetch\s*\([^)]*method\s*:\s*['\"]POST",
    r"fetch\s*\([^)]*method\s*:\s*['\"]PUT",
    r"fetch\s*\([^)]*method\s*:\s*['\"]PATCH",
    r"fetch\s*\([^)]*method\s*:\s*['\"]DELETE",
    # axios mutation methods
    r"axios\.post\s*\(",
    r"axios\.put\s*\(",
    r"axios\.patch\s*\(",
    r"axios\.delete\s*\(",
    # Generic HTTP client mutations
    r"\.post\s*\(['\"]http",
    r"\.put\s*\(['\"]http",
    r"\.patch\s*\(['\"]http",
    r"\.delete\s*\(['\"]http",
    # Request method configuration
    r"method\s*:\s*['\"]POST['\"]",
    r"method\s*:\s*['\"]PUT['\"]",
    r"method\s*:\s*['\"]PATCH['\"]",
    r"method\s*:\s*['\"]DELETE['\"]",
]

# Forbidden WebSocket patterns
WEBSOCKET_PATTERNS = [
    r"new\s+WebSocket\s*\(",
    r"WebSocket\s*\(",
    r"import.*WebSocket",
    r"require.*WebSocket",
    r"socket\.io",
    r"io\s*\(['\"]",  # socket.io client
    r"ws://",
    r"wss://",
]

# Forbidden GitHub API patterns
GITHUB_API_PATTERNS = [
    r"@octokit/",
    r"octokit",
    r"import.*Octokit",
    r"require.*octokit",
    r"api\.github\.com",
    r"GITHUB_TOKEN",
    r"github\.token",
    r"gh\s+api",
    r"workflow_dispatch",
    r"repository_dispatch",
]

# Forbidden GitHub workflow patterns
WORKFLOW_DISPATCH_PATTERNS = [
    r"workflow_dispatch",
    r"repository_dispatch",
    r"/dispatches",
    r"actions/workflows/",
    r"\.dispatch\s*\(",
    r"triggerWorkflow",
    r"runWorkflow",
]

# Forbidden AI/Agent patterns
AI_AGENT_PATTERNS = [
    r"import\s+openai",
    r"from\s+openai",
    r"import\s+anthropic",
    r"from\s+anthropic",
    r"import\s+langchain",
    r"from\s+langchain",
    r"ChatGPT",
    r"GPT\-4",
    r"Claude\s*\(",
    r"LLM\s*\(",
    r"Agent\s*\(",
    r"AutoGPT",
]

# File extensions to scan
SCANNABLE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".json"}


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

        violations = find_pattern_in_file(filepath, patterns)
        for line_num, line, pattern in violations:
            all_violations.append((filepath, line_num, line, pattern))

    return all_violations


def check_package_json(root: Path) -> List[Tuple[Path, int, str, str]]:
    """
    Check package.json for forbidden dependencies.
    """
    violations = []
    package_json = root / "package.json"

    if not package_json.exists():
        # Not having a package.json is fine
        return violations

    forbidden_deps = [
        "axios",
        "node-fetch",
        "got",
        "request",
        "superagent",
        "@octokit/rest",
        "@octokit/core",
        "socket.io",
        "socket.io-client",
        "ws",
        "openai",
        "anthropic",
        "langchain",
    ]

    try:
        import json

        with open(package_json, "r", encoding="utf-8") as f:
            pkg = json.load(f)

        for dep_type in ["dependencies", "devDependencies"]:
            if dep_type in pkg:
                for dep in pkg[dep_type]:
                    for forbidden in forbidden_deps:
                        if forbidden in dep.lower():
                            violations.append(
                                (
                                    package_json,
                                    0,
                                    f"{dep_type}: {dep}",
                                    f"Forbidden dependency: {forbidden}",
                                )
                            )

    except Exception as e:
        violations.append((package_json, 0, f"AUDIT ERROR: {e}", "FILE_READ_FAILURE"))

    return violations


def check_env_files(root: Path) -> List[Tuple[Path, int, str, str]]:
    """
    Check for environment files that might contain write credentials.
    """
    violations = []

    # Environment files that shouldn't exist in Phase 3
    env_files = [".env", ".env.local", ".env.production"]

    # Patterns that indicate write credentials
    credential_patterns = [
        r"GITHUB_TOKEN",
        r"GH_TOKEN",
        r"GITHUB_PAT",
        r"DATABASE_URL.*(?:postgres|mysql)",
        r"DB_.*_PASSWORD",
        r"API_KEY",
        r"SECRET_KEY",
        r"WRITE_.*",
        r"ADMIN_.*",
    ]

    for env_file in env_files:
        env_path = root / env_file
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in credential_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                # Redact the value
                                key = line.split("=")[0].strip() if "=" in line else line.strip()
                                violations.append(
                                    (
                                        env_path,
                                        line_num,
                                        f"{key}=***REDACTED***",
                                        f"Write credential detected: {pattern}",
                                    )
                                )
            except Exception as e:
                violations.append((env_path, 0, f"AUDIT ERROR: {e}", "FILE_READ_FAILURE"))

    return violations


def run_audit() -> Tuple[bool, List[str]]:
    """
    Run the complete network mutation audit.
    Returns (passed: bool, messages: List[str]).
    """
    messages = []
    all_violations = []

    # Verify audit can access source directory
    if not SRC_ROOT.exists():
        messages.append(f"FAIL-CLOSED: Source directory not found: {SRC_ROOT}")
        return False, messages

    messages.append("=" * 60)
    messages.append("Phase 3 No Network Mutation Audit")
    messages.append("=" * 60)
    messages.append("")

    # Check for HTTP mutation patterns
    messages.append("Checking for HTTP mutation methods...")
    violations = scan_directory(SRC_ROOT, HTTP_MUTATION_PATTERNS, "http_mutation")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} HTTP mutation violations")

    # Check for WebSocket patterns
    messages.append("Checking for WebSocket connections...")
    violations = scan_directory(SRC_ROOT, WEBSOCKET_PATTERNS, "websocket")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} WebSocket violations")

    # Check for GitHub API patterns
    messages.append("Checking for GitHub API clients...")
    violations = scan_directory(SRC_ROOT, GITHUB_API_PATTERNS, "github_api")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} GitHub API violations")

    # Check for workflow dispatch patterns
    messages.append("Checking for workflow dispatch logic...")
    violations = scan_directory(SRC_ROOT, WORKFLOW_DISPATCH_PATTERNS, "workflow_dispatch")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} workflow dispatch violations")

    # Check for AI/Agent patterns
    messages.append("Checking for AI/Agent integrations...")
    violations = scan_directory(SRC_ROOT, AI_AGENT_PATTERNS, "ai_agent")
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} AI/Agent violations")

    # Check package.json
    messages.append("Checking package.json for forbidden dependencies...")
    violations = check_package_json(PHASE3_ROOT)
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} forbidden dependency violations")

    # Check env files
    messages.append("Checking for write credentials in environment files...")
    violations = check_env_files(PHASE3_ROOT)
    all_violations.extend(violations)
    messages.append(f"  Found {len(violations)} credential violations")

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
        messages.append("No network mutation violations detected")
        messages.append("GET-only network access confirmed")
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
