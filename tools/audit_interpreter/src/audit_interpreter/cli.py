"""
Phase 4 Audit Interpreter - CLI Interface

Command: audit-interpreter interpret --run-id <run_id>

Optional flags:
  --stdout        Print report instead of writing file
  --strict        Treat unknown artifacts as OUT_OF_SCOPE non-claims

NON-AUTHORITATIVE: This interpreter is read-only and derived.
Truth resides in source artifacts.
"""

import argparse
import sys
from pathlib import Path

from . import __version__, __contract__
from .interpret import interpret_run


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="audit-interpreter",
        description=(
            "Phase 4 Audit Interpreter (Reader-Only) v{version}\n\n"
            "NON-AUTHORITATIVE: This interpreter is read-only and derived.\n"
            "Truth resides in source artifacts.\n\n"
            "Contract: {contract}"
        ).format(version=__version__, contract=__contract__),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # interpret command
    interpret_parser = subparsers.add_parser(
        "interpret",
        help="Interpret a Phase 3 run folder",
        description="Interpret a sealed run folder and emit a canonical interpretation report."
    )

    interpret_parser.add_argument(
        "--run-id",
        required=True,
        help="The run identifier (folder name under .codex/RUNS/)"
    )

    interpret_parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print report to stdout instead of writing to file"
    )

    interpret_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat unknown artifacts as OUT_OF_SCOPE non-claims"
    )

    interpret_parser.add_argument(
        "--runs-root",
        type=Path,
        help="Override runs root directory (default: .codex/RUNS)"
    )

    interpret_parser.add_argument(
        "--repo-root",
        type=Path,
        help="Override repository root directory (default: current directory)"
    )

    interpret_parser.add_argument(
        "--base-ref",
        help="Optional base ref for change classification context (default: classifier auto-resolve)"
    )

    # version command
    parser.add_argument(
        "--version",
        action="version",
        version=f"audit-interpreter {__version__} ({__contract__})"
    )

    return parser


def cmd_interpret(args: argparse.Namespace) -> int:
    """Execute the interpret command."""
    result = interpret_run(
        run_id=args.run_id,
        runs_root=args.runs_root,
        stdout=args.stdout,
        strict=args.strict,
        repo_root=args.repo_root,
        base_ref=args.base_ref
    )

    if result.success:
        if not args.stdout:
            print(f"Report written to: {result.output_path}")

        # Print summary (stderr only when --stdout is used)
        if result.report:
            summary = result.report.get("interpretation_summary", {})
            summary_out = sys.stderr if args.stdout else sys.stdout
            print(f"\nInterpretation Summary:", file=summary_out)
            print(f"  Overall Status: {summary.get('overall_status', 'UNKNOWN')}", file=summary_out)
            print(f"  Failure Count:  {summary.get('failure_count', 0)}", file=summary_out)
            print(f"  Warning Count:  {summary.get('warning_count', 0)}", file=summary_out)
            print(f"  Confidence:     {summary.get('confidence', 'NONE')}", file=summary_out)

            notes = result.report.get("metadata", {}).get("notes")
            if isinstance(notes, str) and notes.strip():
                print(f"\n{notes}", file=summary_out)

        return 0
    else:
        print("Interpretation FAILED:", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "interpret":
        return cmd_interpret(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
