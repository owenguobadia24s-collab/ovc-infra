"""
Change classification integration (context-only).

Runs the repository change classifier and records its JSON artifact when available.
This module is descriptive only and does not enforce gating behavior.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


MAX_STDERR_CHARS = 400


def _truncate_stderr(value: str, max_chars: int = MAX_STDERR_CHARS) -> str:
    text = (value or "").strip().replace("\n", " ").replace("\r", " ")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def _extract_json(stdout: str) -> Optional[Dict[str, Any]]:
    payload = (stdout or "").strip()
    if not payload:
        return None

    try:
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    for line in reversed(payload.splitlines()):
        candidate = line.strip()
        if not candidate or candidate[0] not in "{[":
            continue
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    return None


def _quote_cmd_arg(value: str) -> str:
    if value == "":
        return '""'
    needs_quotes = any(ch.isspace() or ch in "\"'" for ch in value)
    if not needs_quotes:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_invoked_cmd(value: Any) -> Optional[str]:
    if not isinstance(value, list) or not value:
        return None
    if not all(isinstance(item, str) for item in value):
        return None
    return " ".join(_quote_cmd_arg(item) for item in value)


def run_change_classifier(
    base_ref: Optional[str],
    *,
    repo_root: Path,
    output_dir: Path,
    fallback_output_dir: Path,
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Run scripts/governance/classify_change.py and capture JSON payload when available.

    Returns:
      (parsed_json_or_none, meta)

    meta contains:
      - exit_code
      - stderr (truncated)
      - raw_path (target artifact path for change_classification.json)
      - invoked_cmd
    """
    primary_artifact_path = output_dir / "change_classification.json"
    fallback_artifact_path = fallback_output_dir / "change_classification.json"
    cmd = [sys.executable or "python", "scripts/governance/classify_change.py", "--json"]
    if base_ref:
        cmd.extend(["--base", base_ref])

    meta: Dict[str, Any] = {
        "exit_code": 1,
        "stderr": "",
        "raw_path": "",
        "invoked_cmd": cmd,
        "fallback_used": False,
    }

    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        meta["stderr"] = _truncate_stderr(str(exc))
        return None, meta

    meta["exit_code"] = proc.returncode
    meta["stderr"] = _truncate_stderr(proc.stderr)

    parsed_json = _extract_json(proc.stdout)
    if isinstance(parsed_json, dict):
        try:
            primary_artifact_path.write_text(
                json.dumps(parsed_json, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            meta["raw_path"] = str(primary_artifact_path)
        except OSError as exc:
            meta["primary_write_error"] = _truncate_stderr(str(exc))
            try:
                fallback_output_dir.mkdir(parents=True, exist_ok=True)
                fallback_artifact_path.write_text(
                    json.dumps(parsed_json, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                meta["raw_path"] = str(fallback_artifact_path)
                meta["fallback_used"] = True
            except OSError as fallback_exc:
                meta["fallback_write_error"] = _truncate_stderr(str(fallback_exc))
        return parsed_json, meta

    return None, meta


def render_change_classification_section(
    parsed_json: Optional[Dict[str, Any]],
    meta: Dict[str, Any],
) -> str:
    """Render a plain-text report section for change classification context."""
    lines = ["Change Classification"]

    classes = []
    files_count = None
    required_map: Dict[str, Any] = {}

    if isinstance(parsed_json, dict):
        classes_raw = parsed_json.get("classes")
        if isinstance(classes_raw, list):
            classes = [str(c) for c in classes_raw]
            lines.append(f"CLASS={','.join(classes)}")

        files_raw = parsed_json.get("files")
        if isinstance(files_raw, int):
            files_count = files_raw
            lines.append(f"FILES={files_count}")

        required_raw = parsed_json.get("required")
        if isinstance(required_raw, dict):
            required_map = required_raw
            ordered_keys = [k for k in classes if k in required_map]
            for key in sorted(required_map.keys()):
                if key not in ordered_keys:
                    ordered_keys.append(key)
            for class_name in ordered_keys:
                lines.append(f"REQUIRED({class_name})={required_map[class_name]}")
    else:
        lines.append("CLASS=UNAVAILABLE")

    lines.append(f"Artifact path: {meta.get('raw_path', '')}")
    invoked_cmd = _format_invoked_cmd(meta.get("invoked_cmd"))
    if invoked_cmd:
        lines.append(f"invoked_cmd={invoked_cmd}")
    if meta.get("fallback_used"):
        lines.append("fallback_used=true")
    if meta.get("primary_write_error"):
        lines.append(f"primary_write_error={meta['primary_write_error']}")
    if meta.get("fallback_write_error"):
        lines.append(f"fallback_write_error={meta['fallback_write_error']}")

    exit_code = meta.get("exit_code", 1)
    if exit_code != 0:
        stderr = meta.get("stderr", "") or "no stderr"
        lines.append(f"WARNING: classifier exit_code={exit_code}; stderr={stderr}")

    return "\n".join(lines)
