#!/usr/bin/env python3
"""
Path1 Replay Verification v0.1 (STRUCTURAL ONLY, read-only).
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
    compare_dates,
    is_iso_date,
    json_dumps_deterministic,
    list_run_ids,
    load_index_text,
    parse_run_md,
)

TOOL_VERSION = "path1_replay_v0_1"


def validate_run(
    repo_root: Path,
    run_id: str,
    index_text: str,
    strict: bool,
) -> Dict:
    failures: List[str] = []
    warnings: List[str] = []

    run_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / run_id
    run_md = run_dir / "RUN.md"

    if not run_dir.exists() or not run_dir.is_dir():
        failures.append("run_folder_missing")
        return {
            "run_id": run_id,
            "ok": False,
            "failures": failures,
            "warnings": warnings,
            "index_ref": False,
            "parsed": {
                "date_from": None,
                "date_to": None,
                "n_obs": None,
                "symbol": None,
            },
        }

    if not run_md.exists() or not run_md.is_file():
        failures.append("run_md_missing")
        return {
            "run_id": run_id,
            "ok": False,
            "failures": failures,
            "warnings": warnings,
            "index_ref": run_id in index_text,
            "parsed": {
                "date_from": None,
                "date_to": None,
                "n_obs": None,
                "symbol": None,
            },
        }

    content = run_md.read_text(encoding="utf-8")
    parsed, parse_warnings = parse_run_md(content)
    warnings.extend(parse_warnings)

    if parsed.date_from is None or parsed.date_to is None:
        failures.append("date_range_missing")
    else:
        if not is_iso_date(parsed.date_from):
            failures.append("date_from_invalid_format")
        if not is_iso_date(parsed.date_to):
            failures.append("date_to_invalid_format")
        if not compare_dates(parsed.date_from, parsed.date_to):
            failures.append("date_range_invalid_order")

    if parsed.n_obs is not None and parsed.n_obs < 0:
        failures.append("n_obs_negative")

    if parsed.symbol is None or parsed.symbol.strip() == "":
        failures.append("symbol_missing_or_empty")

    evidence_files = list(run_dir.glob("*_evidence.md"))
    if not evidence_files:
        warnings.append("evidence_files_missing")

    outputs_path = run_dir / "outputs"
    if outputs_path.exists() and not outputs_path.is_dir():
        failures.append("outputs_path_not_directory")

    index_ref = run_id in index_text if index_text else False
    if not index_ref:
        warnings.append("index_ref_missing")

    if strict and warnings:
        failures.append("warnings_in_strict_mode")

    failures_sorted = sorted(set(failures))
    warnings_sorted = sorted(set(warnings))
    ok = len(failures_sorted) == 0 and (len(warnings_sorted) == 0 or not strict)

    return {
        "run_id": run_id,
        "ok": ok,
        "failures": failures_sorted,
        "warnings": warnings_sorted,
        "index_ref": index_ref,
        "parsed": {
            "date_from": parsed.date_from,
            "date_to": parsed.date_to,
            "n_obs": parsed.n_obs,
            "symbol": parsed.symbol,
        },
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Path1 Replay Verification v0.1 (structural, read-only)"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: .)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-id", help="Run ID to verify")
    group.add_argument("--all", action="store_true", help="Verify all runs in ledger")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    parser.add_argument(
        "--report-json",
        help="Optional JSON report path (observational only)",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Limit number of runs when using --all",
    )
    return parser


def main() -> int:
    try:
        args = build_arg_parser().parse_args()
        repo_root = Path(args.repo_root).resolve()
        index_path = repo_root / "reports" / "path1" / "evidence" / "INDEX.md"
        runs_root = repo_root / "reports" / "path1" / "evidence" / "runs"

        if not index_path.exists() or not index_path.is_file():
            print("ERROR: INDEX.md missing")
            return 3
        if not runs_root.exists() or not runs_root.is_dir():
            print("ERROR: runs folder missing")
            return 3

        if args.all:
            run_ids = list_run_ids(runs_root)
            if args.max_runs is not None:
                run_ids = run_ids[: args.max_runs]
        else:
            run_ids = [args.run_id]

        if not run_ids:
            print("ERROR: no run_ids found to verify")
            return 3

        index_text = load_index_text(index_path)
        results = []
        warnings_total = 0
        passed = 0
        failed = 0

        for run_id in sorted(run_ids):
            result = validate_run(repo_root, run_id, index_text, args.strict)
            results.append(result)
            if result["ok"]:
                passed += 1
                status = "OK"
            else:
                failed += 1
                status = "FAIL"
            warnings_total += len(result["warnings"])
            if result["ok"]:
                reasons = result["warnings"]
            else:
                reasons = result["failures"] + (result["warnings"] if args.strict else [])
            reason_text = "; ".join(reasons) if reasons else "clean"
            print(f"{status} | {run_id} | {reason_text}")

        summary = {
            "checked": len(results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings_total,
        }
        print(
            f"SUMMARY | checked={summary['checked']} "
            f"passed={summary['passed']} failed={summary['failed']} "
            f"warnings={summary['warnings']}"
        )

        if args.report_json:
            report_path = Path(args.report_json)
            payload = {
                "tool_version": TOOL_VERSION,
                "mode": "structural",
                "repo_root": str(repo_root),
                "run_ids_checked": sorted(run_ids),
                "results": sorted(results, key=lambda r: r["run_id"]),
                "summary": summary,
            }
            report_path.write_text(
                json_dumps_deterministic(payload),
                encoding="utf-8",
                newline="\n",
            )

        if failed > 0 or (args.strict and warnings_total > 0):
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
