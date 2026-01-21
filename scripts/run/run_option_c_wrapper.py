#!/usr/bin/env python
"""
Wrapper for run_option_c.sh/ps1 that creates run artifacts.

Usage:
    python scripts/run_option_c_wrapper.py [--run-id <id>] [--strict] [--spotchecks-only]
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add src to path for ovc_ops import
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ovc_ops.run_artifact import RunWriter, detect_trigger

PIPELINE_ID = "C-Eval"
PIPELINE_VERSION = "0.1.0"
REQUIRED_ENV_VARS = ["DATABASE_URL"]


def main():
    parser = argparse.ArgumentParser(description="Run Option C with artifact capture")
    parser.add_argument("--run-id", dest="run_id", help="Run ID for Option C")
    parser.add_argument("--strict", action="store_true", help="Treat WARN as FAIL")
    parser.add_argument("--spotchecks-only", action="store_true", help="Skip apply, run spotchecks only")
    args = parser.parse_args()

    trigger_type, trigger_source, actor = detect_trigger()
    writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
    writer.start(trigger_type=trigger_type, trigger_source=trigger_source, actor=actor)

    # Check required env
    if not os.environ.get("DATABASE_URL"):
        writer.log("DATABASE_URL not set")
        writer.check(name="env_check", status="fail", evidence="DATABASE_URL not set")
        writer.finish(status="failed")
        print("DATABASE_URL is not set.")
        sys.exit(1)

    writer.add_input(type="neon_view", ref="derived.ovc_block_features_v0_1")

    # Build command for underlying script
    repo_root = Path(__file__).resolve().parents[1]
    
    # Prefer PowerShell on Windows
    if sys.platform == "win32":
        script_path = repo_root / "scripts" / "run_option_c.ps1"
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
        if args.run_id:
            cmd.extend(["-RunId", args.run_id])
        if args.strict:
            cmd.append("-Strict")
        if args.spotchecks_only:
            cmd.append("-SpotchecksOnly")
    else:
        script_path = repo_root / "scripts" / "run_option_c.sh"
        cmd = ["bash", str(script_path)]
        if args.run_id:
            cmd.extend(["--run-id", args.run_id])
        if args.strict:
            cmd.append("--strict")
        if args.spotchecks_only:
            cmd.append("--spotchecks-only")

    writer.log(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=str(repo_root), capture_output=False)
        exit_code = result.returncode

        # Determine actual run_id used
        actual_run_id = args.run_id
        if not actual_run_id:
            # Script generates its own - we can't easily capture it
            # For artifact purposes, we'll note this
            actual_run_id = "auto-generated"

        # Record outputs
        reports_dir = repo_root / "reports"
        if actual_run_id != "auto-generated":
            spotcheck_file = reports_dir / f"spotchecks_{actual_run_id}.txt"
            report_json = reports_dir / f"run_report_{actual_run_id}.json"
            report_md = reports_dir / f"run_report_{actual_run_id}.md"
            
            if spotcheck_file.exists():
                writer.add_output(type="file", ref=str(spotcheck_file))
            if report_json.exists():
                writer.add_output(type="file", ref=str(report_json))
            if report_md.exists():
                writer.add_output(type="file", ref=str(report_md))

        writer.add_output(type="neon_table", ref="derived.ovc_outcomes_v0_1")
        writer.add_output(type="neon_table", ref="derived.eval_runs")

        # Interpret exit code
        if exit_code == 0:
            writer.check(name="spotchecks", status="pass", evidence="exit_code=0")
            writer.finish(status="success")
        elif exit_code == 1:
            writer.check(name="spotchecks", status="pass", evidence="exit_code=1 (WARN)")
            writer.finish(status="partial")
        else:
            writer.check(name="spotchecks", status="fail", evidence=f"exit_code={exit_code}")
            writer.finish(status="failed")

        sys.exit(exit_code)

    except Exception as e:
        writer.log(f"Exception: {e}")
        writer.check(name="execution", status="fail", evidence=str(e))
        writer.finish(status="failed")
        raise


if __name__ == "__main__":
    main()
