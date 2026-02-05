#!/usr/bin/env python3
"""
Run SQL QA validation pack with evidence envelope (OP-QA06).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ovc_ops.run_envelope_v0_1 import (  # noqa: E402
    ensure_run_dir,
    get_git_state,
    make_run_id,
    seal_dir,
    write_run_json,
)


def resolve_dsn() -> str:
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not dsn:
        raise SystemExit("Missing DATABASE_URL or NEON_DSN environment variable")
    return dsn


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QA SQL validation pack")
    parser.add_argument("--symbol", required=True, help="Symbol (e.g., GBPUSD)")
    parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--run-id", dest="run_id", help="Optional run_id override")
    parser.add_argument("--tolerance", default="0.00001", help="Tolerance (default: 0.00001)")
    parser.add_argument("--tolerance-seconds", dest="tolerance_seconds", default="10")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    sql_path = repo_root / "sql" / "qa_validation_pack.sql"
    if not sql_path.is_file():
        raise SystemExit(f"Missing SQL file: {sql_path}")

    if not shutil.which("psql"):
        raise SystemExit("psql not found in PATH")

    run_id = args.run_id or make_run_id("op_qa06")
    run_dir = ensure_run_dir(repo_root / "reports" / "runs", run_id)
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_commit, working_tree_state = get_git_state()

    dsn = resolve_dsn()

    psql_args = [
        "psql",
        "-d",
        dsn,
        "-v",
        f"run_id='{run_id}'",
        "-v",
        f"symbol='{args.symbol}'",
        "-v",
        f"date_ny='{args.date}'",
        "-v",
        f"tolerance_seconds={args.tolerance_seconds}",
        "-v",
        f"tolerance={args.tolerance}",
        "-f",
        str(sql_path),
    ]

    exit_code = 0
    try:
        result = subprocess.run(psql_args, check=False)
        exit_code = result.returncode
    finally:
        try:
            run_json_payload = {
                "run_id": run_dir.name,
                "created_utc": created_utc,
                "run_type": "op_run",
                "option": "QA",
                "operation_id": "OP-QA06",
                "git_commit": git_commit,
                "working_tree_state": working_tree_state,
                "inputs": {
                    "symbol": args.symbol,
                    "date_ny": args.date,
                },
                "outputs": [
                    "run.json",
                    "manifest.json",
                    "MANIFEST.sha256",
                ],
            }
            write_run_json(run_dir, run_json_payload)
            seal_dir(run_dir, ["run.json"])
        except Exception as exc:
            print(f"WARNING: run envelope write failed: {exc}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
