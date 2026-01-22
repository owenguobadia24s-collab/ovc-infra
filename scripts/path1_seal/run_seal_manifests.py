#!/usr/bin/env python3
"""
Path1 Sealing v0.1: create MANIFEST.sha256 per run (append-only).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib import (  # noqa: E402
    build_manifest_lines,
    collect_included_files,
    json_dumps_deterministic,
)

TOOL_VERSION = "path1_seal_v0_1"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Path1 sealing v0.1 (append-only manifest generation)"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: .)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-id", help="Run ID to seal")
    group.add_argument("--all", action="store_true", help="Seal all runs")
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Limit number of runs when using --all",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing manifests",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any invariant or read error",
    )
    parser.add_argument(
        "--report-json",
        help="Optional JSON report path (observational only)",
    )
    return parser


def seal_one_run(repo_root: Path, run_id: str, dry_run: bool, strict: bool) -> Dict:
    run_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / run_id
    manifest_path = run_dir / "MANIFEST.sha256"

    if not run_dir.exists() or not run_dir.is_dir():
        return {
            "run_id": run_id,
            "status": "FAIL",
            "included_files_count": 0,
            "warnings": [],
            "failures": ["run_folder_missing"],
        }

    if manifest_path.exists():
        return {
            "run_id": run_id,
            "status": "SKIPPED_EXISTS",
            "included_files_count": 0,
            "warnings": [],
            "failures": [],
        }

    included, warnings, failures = collect_included_files(run_dir)
    warnings = list(warnings)
    failures = list(failures)

    if failures and not strict:
        demote: List[str] = []
        keep: List[str] = []
        for item in failures:
            if item.startswith("duplicate_path:") or item.startswith("stat_failed:"):
                demote.append(item)
            elif item == "outputs_path_not_directory":
                demote.append(item)
            else:
                keep.append(item)
        failures = keep
        warnings.extend(demote)

    if failures and strict:
        return {
            "run_id": run_id,
            "status": "FAIL",
            "included_files_count": len(included),
            "warnings": sorted(set(warnings)),
            "failures": sorted(set(failures)),
        }

    if failures and not strict:
        return {
            "run_id": run_id,
            "status": "FAIL",
            "included_files_count": len(included),
            "warnings": sorted(set(warnings)),
            "failures": sorted(set(failures)),
        }

    try:
        lines = build_manifest_lines(run_dir, included)
    except OSError as exc:
        return {
            "run_id": run_id,
            "status": "FAIL",
            "included_files_count": len(included),
            "warnings": sorted(set(warnings)),
            "failures": [f"read_failed:{exc}"],
        }

    if dry_run:
        return {
            "run_id": run_id,
            "status": "DRYRUN_WOULD_WRITE",
            "included_files_count": len(included),
            "warnings": sorted(set(warnings)),
            "failures": [],
        }

    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return {
        "run_id": run_id,
        "status": "WROTE",
        "included_files_count": len(included),
        "warnings": sorted(set(warnings)),
        "failures": [],
    }


def main() -> int:
    try:
        args = build_arg_parser().parse_args()
        repo_root = Path(args.repo_root).resolve()
        runs_root = repo_root / "reports" / "path1" / "evidence" / "runs"
        if not runs_root.exists() or not runs_root.is_dir():
            print("ERROR: runs folder missing")
            return 3

        if args.all:
            run_ids = sorted([p.name for p in runs_root.iterdir() if p.is_dir()])
            if args.max_runs is not None:
                run_ids = run_ids[: args.max_runs]
        else:
            run_ids = [args.run_id]

        if not run_ids:
            print("ERROR: no run_ids found to seal")
            return 3

        results: List[Dict] = []
        summary = {
            "checked": 0,
            "wrote": 0,
            "skipped_exists": 0,
            "dryrun_would_write": 0,
            "failed": 0,
            "warnings": 0,
        }

        for run_id in run_ids:
            result = seal_one_run(repo_root, run_id, args.dry_run, args.strict)
            results.append(result)
            summary["checked"] += 1
            summary["warnings"] += len(result["warnings"])
            status = result["status"]
            if status == "WROTE":
                summary["wrote"] += 1
            elif status == "SKIPPED_EXISTS":
                summary["skipped_exists"] += 1
            elif status == "DRYRUN_WOULD_WRITE":
                summary["dryrun_would_write"] += 1
            elif status == "FAIL":
                summary["failed"] += 1

            warn_count = len(result["warnings"])
            fail_count = len(result["failures"])
            print(
                f"RUN | {run_id} | {status} | included={result['included_files_count']} "
                f"| warnings={warn_count} | failures={fail_count}"
            )

        print(
            "SUMMARY | checked={checked} wrote={wrote} skipped_exists={skipped_exists} "
            "dryrun_would_write={dryrun_would_write} failed={failed} warnings={warnings}".format(
                **summary
            )
        )

        if args.report_json:
            report_path = Path(args.report_json)
            payload = {
                "tool_version": TOOL_VERSION,
                "repo_root": str(repo_root),
                "run_ids_checked": sorted(run_ids),
                "results": results,
                "summary": summary,
            }
            report_path.write_text(
                json_dumps_deterministic(payload),
                encoding="utf-8",
                newline="\n",
            )

        if summary["failed"] > 0:
            return 2
        return 0
    except SystemExit as exc:
        if exc.code and int(exc.code) != 0:
            return 3
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
