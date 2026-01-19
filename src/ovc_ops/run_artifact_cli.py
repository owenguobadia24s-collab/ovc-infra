#!/usr/bin/env python3
"""
OVC Run Artifact CLI Wrapper v0.1

Minimal CLI wrapper for non-Python pipelines (e.g., bash scripts).
Wraps command execution and emits run artifacts.

Usage:
    python -m src.ovc_ops.run_artifact_cli \\
        --pipeline-id C-Eval \\
        --pipeline-version 0.1.0 \\
        --required-env DATABASE_URL \\
        -- bash scripts/run_option_c.sh --run-id my_run

The wrapper will:
1. Create a RunWriter
2. Tee stdout/stderr of the command into run.log
3. Finish with success/failed based on exit code
4. Add basic checks for required env presence
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add parent to path for local imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from ovc_ops.run_artifact import RunWriter, detect_trigger


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    """Parse CLI arguments, separating wrapper args from command args."""
    parser = argparse.ArgumentParser(
        description="Run artifact CLI wrapper for non-Python pipelines.",
        usage="python -m src.ovc_ops.run_artifact_cli [OPTIONS] -- COMMAND...",
    )
    parser.add_argument(
        "--pipeline-id",
        required=True,
        help="Pipeline identifier (e.g., C-Eval)",
    )
    parser.add_argument(
        "--pipeline-version",
        default="0.1.0",
        help="Pipeline version (default: 0.1.0)",
    )
    parser.add_argument(
        "--required-env",
        action="append",
        default=[],
        dest="required_env",
        help="Required environment variable (can be specified multiple times)",
    )
    parser.add_argument(
        "--reports-base",
        default=None,
        help="Base directory for reports (default: reports/runs)",
    )
    
    # Find the -- separator
    if "--" in sys.argv:
        sep_idx = sys.argv.index("--")
        wrapper_args = sys.argv[1:sep_idx]
        cmd_args = sys.argv[sep_idx + 1:]
    else:
        wrapper_args = sys.argv[1:]
        cmd_args = []
    
    args = parser.parse_args(wrapper_args)
    return args, cmd_args


def main() -> int:
    """Run the wrapper."""
    args, cmd_args = parse_args()
    
    if not cmd_args:
        print("ERROR: No command specified after --", file=sys.stderr)
        print("Usage: python -m src.ovc_ops.run_artifact_cli [OPTIONS] -- COMMAND...", file=sys.stderr)
        return 2
    
    # Detect trigger
    trigger_type, trigger_source, actor = detect_trigger()
    
    # Create writer
    writer = RunWriter(
        pipeline_id=args.pipeline_id,
        pipeline_version=args.pipeline_version,
        required_env_vars=args.required_env,
        reports_base=args.reports_base,
    )
    
    # Start run
    run_id = writer.start(
        trigger_type=trigger_type,
        trigger_source=trigger_source,
        actor=actor,
    )
    
    # Add input (the command itself)
    writer.add_input(type="command", ref=" ".join(cmd_args))
    
    # Check if any required env is missing
    missing_env = [v for v in args.required_env if not os.environ.get(v)]
    if missing_env:
        writer.log(f"ERROR: Missing required environment variables: {missing_env}")
        writer.finish("failed")
        return 1
    
    # Run the command
    writer.log(f"Executing: {' '.join(cmd_args)}")
    writer.log("-" * 60)
    
    exit_code = 0
    try:
        # Run command and tee output to log
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
        )
        
        line_num = 2  # Start after RUN_ID line
        for line in process.stdout:
            writer.log(line.rstrip("\n"))
            line_num += 1
        
        process.wait()
        exit_code = process.returncode
        
    except FileNotFoundError:
        writer.log(f"ERROR: Command not found: {cmd_args[0]}")
        exit_code = 127
    except Exception as e:
        writer.log(f"ERROR: {type(e).__name__}: {e}")
        exit_code = 1
    
    # Add exit code check
    if exit_code == 0:
        writer.check(
            "command_exit_code",
            "Command exited successfully",
            "pass",
            [f"run.log:line:{line_num}"]
        )
        status = "success"
    else:
        writer.check(
            "command_exit_code",
            f"Command exited with code {exit_code}",
            "fail",
            [f"run.log:line:{line_num}"]
        )
        status = "failed"
    
    writer.log("-" * 60)
    writer.log(f"Command exit code: {exit_code}")
    
    # Add output (run artifacts)
    writer.add_output(type="artifact", ref=str(writer.run_dir))
    
    # Finish
    writer.finish(status)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
