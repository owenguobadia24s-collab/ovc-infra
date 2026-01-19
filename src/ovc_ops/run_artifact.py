"""
OVC Run Artifact Module v0.1

Provides utilities for creating deterministic run artifact directories
per RUN_ARTIFACT_SPEC_v0.1.md.

Usage:
    from ovc_ops.run_artifact import RunWriter

    writer = RunWriter(
        pipeline_id="P2-Backfill",
        pipeline_version="0.1.0",
        required_env_vars=["NEON_DSN", "OANDA_API_TOKEN", "OANDA_ENV"]
    )
    writer.start(
        trigger_type="local_cli",
        trigger_source="cli:backfill_oanda_2h_checkpointed.py",
        actor="developer"
    )
    writer.add_input(type="oanda", ref="GBP_USD", range="2026-01-13 to 2026-01-17")
    writer.add_output(type="neon_table", ref="ovc.ovc_blocks_v01_1_min", rows_written=60)
    writer.check("oanda_fetch_success", "OANDA API fetch succeeded", "pass", ["run.log:line:42"])
    writer.finish("success")
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------- Utility Functions ----------

def get_git_sha() -> str:
    """
    Get current git commit SHA.
    
    Priority:
    1. GITHUB_SHA environment variable (for GitHub Actions)
    2. `git rev-parse HEAD` command output
    3. Fallback to "0000000000000000000000000000000000000000"
    """
    # Try GITHUB_SHA first (GitHub Actions)
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    
    # Try git command
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    
    # Fallback
    return "0000000000000000000000000000000000000000"


def get_git_ref() -> str:
    """
    Get current git ref.
    
    Priority:
    1. GITHUB_REF environment variable
    2. `git symbolic-ref HEAD` command output
    3. Fallback to "refs/heads/unknown"
    """
    ref = os.environ.get("GITHUB_REF")
    if ref:
        return ref
    
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    
    return "refs/heads/unknown"


def now_utc() -> str:
    """Return current UTC time as ISO8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_utc_compact() -> str:
    """Return current UTC time in compact format: YYYYMMDDTHHMMSSZ."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def make_run_id(pipeline_id: str, git_sha7: str, started_utc_compact: str) -> str:
    """
    Create deterministic run ID.
    
    Format: <utc_yyyymmddThhmmssZ>__<pipeline_id>__<git_sha7>
    """
    return f"{started_utc_compact}__{pipeline_id}__{git_sha7}"


def _stable_json_dumps(obj: Any) -> str:
    """Dump JSON with stable formatting (indent=2, sort_keys=True)."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


# ---------- Enums (for validation) ----------

TRIGGER_TYPES = frozenset([
    "github_schedule",
    "github_dispatch",
    "local_cli",
    "worker_http",
    "worker_cron",
])

STATUS_VALUES = frozenset(["success", "failed", "partial"])

CHECK_STATUS_VALUES = frozenset(["pass", "fail", "skip"])


# ---------- RunWriter Class ----------

class RunWriter:
    """
    Write run artifacts per RUN_ARTIFACT_SPEC_v0.1.
    
    Creates deterministic run artifact directory with:
    - run.json: Manifest with inputs, outputs, metadata
    - checks.json: Validation checks with evidence
    - run.log: Captured log output
    """
    
    def __init__(
        self,
        pipeline_id: str,
        pipeline_version: str,
        required_env_vars: Optional[list[str]] = None,
        reports_base: Optional[str] = None,
    ):
        """
        Initialize RunWriter.
        
        Args:
            pipeline_id: Pipeline identifier (e.g., "P2-Backfill")
            pipeline_version: Semantic version (e.g., "0.1.0")
            required_env_vars: List of required environment variable names
            reports_base: Base directory for reports (default: reports/runs)
        """
        self.pipeline_id = pipeline_id
        self.pipeline_version = pipeline_version
        self.required_env_vars = required_env_vars or []
        self.reports_base = Path(reports_base) if reports_base else Path("reports/runs")
        
        self._started = False
        self._finished = False
        self._run_id: Optional[str] = None
        self._run_dir: Optional[Path] = None
        self._log_file = None
        self._log_path: Optional[Path] = None
        
        self._started_utc: Optional[str] = None
        self._started_utc_compact: Optional[str] = None
        self._finished_utc: Optional[str] = None
        self._duration_ms: Optional[int] = None
        
        self._trigger: dict = {}
        self._git: dict = {}
        self._env_present: list[str] = []
        self._env_missing: list[str] = []
        
        self._inputs: list[dict] = []
        self._outputs: list[dict] = []
        self._checks: list[dict] = []
    
    @property
    def run_id(self) -> Optional[str]:
        """Get the run ID (available after start())."""
        return self._run_id
    
    @property
    def run_dir(self) -> Optional[Path]:
        """Get the run directory path (available after start())."""
        return self._run_dir
    
    def start(
        self,
        trigger_type: str,
        trigger_source: str,
        actor: str,
    ) -> str:
        """
        Start the run: create directory, open log, record metadata.
        
        Args:
            trigger_type: One of TRIGGER_TYPES
            trigger_source: Source identifier (e.g., "workflow:backfill.yml")
            actor: Actor identifier (e.g., "github-actions[bot]")
        
        Returns:
            The run_id
        
        Raises:
            ValueError: If already started or invalid trigger_type
        """
        if self._started:
            raise ValueError("RunWriter already started")
        
        if trigger_type not in TRIGGER_TYPES:
            raise ValueError(f"Invalid trigger_type: {trigger_type}. Must be one of {TRIGGER_TYPES}")
        
        self._started = True
        
        # Timestamps
        now = datetime.now(timezone.utc)
        self._started_utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._started_utc_compact = now.strftime("%Y%m%dT%H%M%SZ")
        
        # Git info
        git_sha = get_git_sha()
        git_sha7 = git_sha[:7]
        git_ref = get_git_ref()
        
        self._git = {
            "ref": git_ref,
            "sha": git_sha,
            "sha7": git_sha7,
        }
        
        # Trigger info
        self._trigger = {
            "actor": actor,
            "source": trigger_source,
            "type": trigger_type,
        }
        
        # Generate run ID
        self._run_id = make_run_id(self.pipeline_id, git_sha7, self._started_utc_compact)
        
        # Create run directory
        self._run_dir = self.reports_base / self._run_id
        self._run_dir.mkdir(parents=True, exist_ok=True)
        
        # Check required env vars
        for var_name in self.required_env_vars:
            if os.environ.get(var_name):
                self._env_present.append(var_name)
            else:
                self._env_missing.append(var_name)
        
        # Open log file
        self._log_path = self._run_dir / "run.log"
        self._log_file = open(self._log_path, "w", encoding="utf-8")
        
        # Write RUN_ID as first line (for CI extraction)
        self._log_file.write(f"RUN_ID={self._run_id}\n")
        self._log_file.flush()
        
        # Also echo to stdout for CI
        print(f"RUN_ID={self._run_id}")
        
        # Add required_env check if there are required vars
        if self.required_env_vars:
            if self._env_missing:
                self.check(
                    "required_env_present",
                    "Required environment variables present",
                    "fail",
                    [f"run.json:$.env.missing"]
                )
            else:
                self.check(
                    "required_env_present",
                    "Required environment variables present",
                    "pass",
                    []
                )
        
        return self._run_id
    
    def log(self, message: str) -> None:
        """Write a message to run.log and stdout."""
        if not self._started or self._finished:
            return
        
        if self._log_file:
            self._log_file.write(message)
            if not message.endswith("\n"):
                self._log_file.write("\n")
            self._log_file.flush()
        
        print(message, end="" if message.endswith("\n") else "\n")
    
    def add_input(
        self,
        type: str,
        ref: str,
        range: Optional[str] = None,
    ) -> None:
        """
        Record an input source.
        
        Args:
            type: Input type (e.g., "oanda", "neon_table", "csv")
            ref: Input reference (e.g., "GBP_USD", "ovc.ovc_blocks_v01_1_min")
            range: Optional range specification
        """
        input_obj = {"ref": ref, "type": type}
        if range is not None:
            input_obj["range"] = range
        self._inputs.append(input_obj)
    
    def add_output(
        self,
        type: str,
        ref: str,
        rows_written: Optional[int] = None,
        rows_updated: Optional[int] = None,
        extra: Optional[dict] = None,
    ) -> None:
        """
        Record an output target.
        
        Args:
            type: Output type (e.g., "neon_table", "notion_page", "file")
            ref: Output reference (e.g., "ovc.ovc_blocks_v01_1_min")
            rows_written: Number of rows written (if applicable)
            rows_updated: Number of rows updated (if applicable)
            extra: Additional metadata
        """
        output_obj = {"ref": ref, "type": type}
        if rows_written is not None:
            output_obj["rows_written"] = rows_written
        if rows_updated is not None:
            output_obj["rows_updated"] = rows_updated
        if extra is not None:
            output_obj["extra"] = extra
        self._outputs.append(output_obj)
    
    def check(
        self,
        id: str,
        name: str,
        status: str,
        evidence: list[str],
    ) -> None:
        """
        Record a validation check.
        
        Args:
            id: Check identifier (snake_case)
            name: Human-readable check name
            status: One of CHECK_STATUS_VALUES
            evidence: List of evidence strings
        
        Raises:
            ValueError: If invalid status
        """
        if status not in CHECK_STATUS_VALUES:
            raise ValueError(f"Invalid check status: {status}. Must be one of {CHECK_STATUS_VALUES}")
        
        self._checks.append({
            "evidence": evidence,
            "id": id,
            "name": name,
            "status": status,
        })
    
    def finish(self, status: str) -> None:
        """
        Finish the run: write run.json, checks.json, close log.
        
        Args:
            status: One of STATUS_VALUES
        
        Raises:
            ValueError: If not started, already finished, or invalid status
        """
        if not self._started:
            raise ValueError("RunWriter not started")
        if self._finished:
            raise ValueError("RunWriter already finished")
        if status not in STATUS_VALUES:
            raise ValueError(f"Invalid status: {status}. Must be one of {STATUS_VALUES}")
        
        self._finished = True
        
        # Calculate duration
        now = datetime.now(timezone.utc)
        self._finished_utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        started_dt = datetime.strptime(self._started_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self._duration_ms = int((now - started_dt).total_seconds() * 1000)
        
        # Override status if env missing
        if self._env_missing:
            status = "failed"
        
        # Write run.json
        run_data = {
            "duration_ms": self._duration_ms,
            "env": {
                "missing": sorted(self._env_missing),
                "present": sorted(self._env_present),
            },
            "finished_utc": self._finished_utc,
            "git": self._git,
            "inputs": self._inputs,
            "outputs": self._outputs,
            "pipeline_id": self.pipeline_id,
            "pipeline_version": self.pipeline_version,
            "run_id": self._run_id,
            "started_utc": self._started_utc,
            "status": status,
            "trigger": self._trigger,
        }
        
        run_json_path = self._run_dir / "run.json"
        run_json_path.write_text(_stable_json_dumps(run_data) + "\n", encoding="utf-8")
        
        # Compute check summary
        summary = {"fail": 0, "pass": 0, "skip": 0}
        for check in self._checks:
            summary[check["status"]] += 1
        
        # Write checks.json
        checks_data = {
            "checks": self._checks,
            "run_id": self._run_id,
            "summary": summary,
        }
        
        checks_json_path = self._run_dir / "checks.json"
        checks_json_path.write_text(_stable_json_dumps(checks_data) + "\n", encoding="utf-8")
        
        # Close log file
        if self._log_file:
            self._log_file.close()
            self._log_file = None
        
        # Final status message
        print(f"Run artifacts written to: {self._run_dir}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure finish is called."""
        if self._started and not self._finished:
            status = "failed" if exc_type else "success"
            self.finish(status)
        return False


def detect_trigger() -> tuple[str, str, str]:
    """
    Auto-detect trigger type, source, and actor from environment.
    
    Returns:
        Tuple of (trigger_type, trigger_source, actor)
    """
    # GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        event_name = os.environ.get("GITHUB_EVENT_NAME", "unknown")
        workflow = os.environ.get("GITHUB_WORKFLOW", "unknown")
        actor = os.environ.get("GITHUB_ACTOR", "github-actions[bot]")
        
        if event_name == "schedule":
            return ("github_schedule", f"workflow:{workflow}", actor)
        elif event_name == "workflow_dispatch":
            return ("github_dispatch", f"workflow:{workflow}", actor)
        else:
            return ("github_dispatch", f"workflow:{workflow}:{event_name}", actor)
    
    # Local CLI (default)
    user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    return ("local_cli", "cli", user)
