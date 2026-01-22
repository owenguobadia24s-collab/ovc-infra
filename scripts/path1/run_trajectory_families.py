#!/usr/bin/env python3
"""
Trajectory Families v0.1 CLI
============================
Path 1 (Observation & Cataloging Only)

Commands:
  emit-fingerprint    Generate fingerprint for a single day
  batch-fingerprints  Generate fingerprints for a date range

No clustering, naming, or galleries in this PR.
"""

import argparse
import csv
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# Add parent to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from trajectory_families import (
    compute_fingerprint,
    get_dominant_quadrant,
    is_valid_fingerprint,
    load_params,
    load_trajectory_csv,
    write_fingerprint_json,
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "path1" / "trajectory_families"
DEFAULT_EVIDENCE_DIR = REPO_ROOT / "reports" / "path1" / "evidence" / "runs"


def validate_date(value: str, field_name: str) -> str:
    """Validate date format YYYY-MM-DD."""
    if not DATE_RE.match(value):
        raise ValueError(f"{field_name} must be YYYY-MM-DD, got: {value}")
    return value


def iter_dates(start: date, end: date) -> Iterable[date]:
    """Iterate over dates in range [start, end]."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def find_trajectory_csv(
    evidence_dir: Path,
    symbol: str,
    date_ny: str,
) -> Optional[Path]:
    """
    Find trajectory.csv for a given symbol and date.

    Searches through evidence runs for matching state_plane_v0_2 output.
    """
    date_compact = date_ny.replace("-", "")

    # Search all run directories
    if not evidence_dir.exists():
        return None

    for run_dir in sorted(evidence_dir.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue

        # Check state_plane_v0_2 subdirectory
        trajectory_path = run_dir / "outputs" / "state_plane_v0_2" / "trajectory.csv"
        if not trajectory_path.exists():
            continue

        # Verify this trajectory matches our date/symbol
        try:
            with open(trajectory_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    block_id = row.get("block_id", "")
                    if block_id:
                        # Format: YYYYMMDD-X-SYMBOL
                        parts = block_id.split("-")
                        if len(parts) >= 3:
                            if parts[0] == date_compact and parts[2] == symbol:
                                return trajectory_path
                    break  # Only check first row
        except Exception:
            continue

    return None


def compute_relative_path(path: Path, base: Path) -> str:
    """Compute relative path with forward slashes (POSIX style)."""
    try:
        rel = path.relative_to(base)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def get_index_csv_path(output_dir: Path) -> Path:
    """Get path to index.csv."""
    return output_dir / "v0.1" / "fingerprints" / "index.csv"


def load_index_csv(index_path: Path) -> Dict[str, Dict]:
    """Load existing index.csv into dict keyed by fingerprint_id."""
    if not index_path.exists():
        return {}

    index = {}
    with open(index_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fp_id = row.get("fingerprint_id", "")
            if fp_id:
                index[fp_id] = row
    return index


def write_index_csv(index_path: Path, index: Dict[str, Dict]) -> None:
    """Write index.csv sorted by date_ny, symbol."""
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort by date_ny, then symbol
    sorted_entries = sorted(
        index.values(),
        key=lambda x: (x.get("date_ny", ""), x.get("symbol", "")),
    )

    fieldnames = [
        "fingerprint_id",
        "date_ny",
        "symbol",
        "trajectory_csv_path",
        "fingerprint_json_path",
        "path_length",
        "efficiency",
        "dominant_quadrant",
        "family_id",
        "content_hash",
    ]

    with open(index_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in sorted_entries:
            # Ensure all fields present
            row = {k: entry.get(k, "") for k in fieldnames}
            writer.writerow(row)


def emit_fingerprint(
    symbol: str,
    date_ny: str,
    trajectory_csv: Optional[Path],
    evidence_dir: Path,
    output_dir: Path,
    params: Dict,
) -> Tuple[bool, str, Optional[Dict]]:
    """
    Emit fingerprint for a single day.

    Returns (success, message, fingerprint_or_none).
    """
    # Find trajectory CSV if not provided
    if trajectory_csv is None:
        trajectory_csv = find_trajectory_csv(evidence_dir, symbol, date_ny)
        if trajectory_csv is None:
            return False, f"No trajectory.csv found for {symbol} {date_ny}", None

    if not trajectory_csv.exists():
        return False, f"Trajectory CSV not found: {trajectory_csv}", None

    # Load trajectory data
    try:
        points, csv_symbol, csv_date = load_trajectory_csv(trajectory_csv)
    except Exception as e:
        return False, f"Failed to load trajectory CSV: {e}", None

    # Validate block count
    if len(points) != 12:
        return False, f"Expected 12 blocks, got {len(points)} for {symbol} {date_ny}", None

    # Check for excessive null coordinates
    null_count = sum(1 for p in points if p.get("x") is None or p.get("y") is None)
    if null_count > 2:
        return False, f"Too many null coordinates ({null_count}) for {symbol} {date_ny}", None

    # Build source artifacts paths (relative to repo root)
    trajectory_png = trajectory_csv.parent / "trajectory.png"
    path_metrics_json = trajectory_csv.parent / "path_metrics.json"

    source_artifacts = {
        "trajectory_csv": compute_relative_path(trajectory_csv, REPO_ROOT),
        "trajectory_png": compute_relative_path(trajectory_png, REPO_ROOT) if trajectory_png.exists() else "",
    }
    if path_metrics_json.exists():
        source_artifacts["path_metrics_json"] = compute_relative_path(path_metrics_json, REPO_ROOT)

    # Compute fingerprint
    try:
        fingerprint = compute_fingerprint(
            points=points,
            params=params,
            source_artifacts=source_artifacts,
            date_ny=date_ny,
            symbol=symbol,
        )
    except ValueError as e:
        return False, f"Fingerprint computation failed: {e}", None

    # Validate fingerprint
    is_valid, errors = is_valid_fingerprint(fingerprint)
    if not is_valid:
        return False, f"Fingerprint validation failed: {errors}", None

    # Determine output path
    year = date_ny[:4]
    fp_id = fingerprint["fingerprint_id"]
    fp_path = output_dir / "v0.1" / "fingerprints" / symbol / year / f"{fp_id}.json"

    # Write fingerprint JSON
    write_fingerprint_json(fingerprint, fp_path)

    # Update index.csv
    index_path = get_index_csv_path(output_dir)
    index = load_index_csv(index_path)

    index[fp_id] = {
        "fingerprint_id": fp_id,
        "date_ny": date_ny,
        "symbol": symbol,
        "trajectory_csv_path": source_artifacts["trajectory_csv"],
        "fingerprint_json_path": compute_relative_path(fp_path, output_dir / "v0.1"),
        "path_length": f"{fingerprint['path_geometry']['path_length']:.6f}",
        "efficiency": f"{fingerprint['path_geometry']['efficiency']:.6f}",
        "dominant_quadrant": get_dominant_quadrant(fingerprint["quadrants"]) or "",
        "family_id": "",  # Not assigned until clustering
        "content_hash": fingerprint["content_hash"],
    }

    write_index_csv(index_path, index)

    return True, f"Fingerprint emitted: {fp_id}", fingerprint


def emit_fingerprint_worker(args: Tuple) -> Tuple[str, str, bool, str]:
    """Worker function for parallel fingerprint emission."""
    symbol, date_ny, evidence_dir, output_dir, params = args
    success, message, _ = emit_fingerprint(
        symbol=symbol,
        date_ny=date_ny,
        trajectory_csv=None,
        evidence_dir=evidence_dir,
        output_dir=output_dir,
        params=params,
    )
    return symbol, date_ny, success, message


def batch_fingerprints(
    symbol: str,
    date_from: str,
    date_to: str,
    evidence_dir: Path,
    output_dir: Path,
    params: Dict,
    parallel: int = 1,
) -> Tuple[int, int, List[str]]:
    """
    Generate fingerprints for a date range.

    Returns (success_count, skip_count, error_messages).
    """
    start = datetime.strptime(date_from, "%Y-%m-%d").date()
    end = datetime.strptime(date_to, "%Y-%m-%d").date()

    if start > end:
        raise ValueError("date_from must be <= date_to")

    dates = [d.strftime("%Y-%m-%d") for d in iter_dates(start, end)]
    success_count = 0
    skip_count = 0
    errors = []

    if parallel > 1:
        # Parallel execution
        work_items = [
            (symbol, date_ny, evidence_dir, output_dir, params)
            for date_ny in dates
        ]

        with ProcessPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(emit_fingerprint_worker, item): item for item in work_items}

            for future in as_completed(futures):
                sym, date_ny, success, message = future.result()
                if success:
                    success_count += 1
                    print(f"  {message}")
                else:
                    skip_count += 1
                    errors.append(f"{date_ny}: {message}")

        # Re-sort index.csv after parallel writes (ensure determinism)
        index_path = get_index_csv_path(output_dir)
        index = load_index_csv(index_path)
        write_index_csv(index_path, index)

    else:
        # Sequential execution
        for date_ny in dates:
            success, message, _ = emit_fingerprint(
                symbol=symbol,
                date_ny=date_ny,
                trajectory_csv=None,
                evidence_dir=evidence_dir,
                output_dir=output_dir,
                params=params,
            )

            if success:
                success_count += 1
                print(f"  {message}")
            else:
                skip_count += 1
                errors.append(f"{date_ny}: {message}")

    return success_count, skip_count, errors


def cmd_emit_fingerprint(args: argparse.Namespace) -> int:
    """Handle emit-fingerprint command."""
    symbol = args.symbol.upper()
    date_ny = validate_date(args.date, "--date")

    trajectory_csv = Path(args.trajectory_csv) if args.trajectory_csv else None
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else DEFAULT_EVIDENCE_DIR
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR

    # Load params
    params_path = Path(args.params_file) if args.params_file else None
    params = load_params(params_path)

    print(f"Emitting fingerprint for {symbol} {date_ny}...")

    success, message, _ = emit_fingerprint(
        symbol=symbol,
        date_ny=date_ny,
        trajectory_csv=trajectory_csv,
        evidence_dir=evidence_dir,
        output_dir=output_dir,
        params=params,
    )

    print(message)
    return 0 if success else 1


def cmd_batch_fingerprints(args: argparse.Namespace) -> int:
    """Handle batch-fingerprints command."""
    symbol = args.symbol.upper()
    date_from = validate_date(args.date_from, "--date-from")
    date_to = validate_date(args.date_to, "--date-to")

    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else DEFAULT_EVIDENCE_DIR
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    parallel = args.parallel

    # Load params
    params_path = Path(args.params_file) if args.params_file else None
    params = load_params(params_path)

    print(f"Batch fingerprinting {symbol} from {date_from} to {date_to}...")
    print(f"  Evidence dir: {evidence_dir}")
    print(f"  Output dir: {output_dir}")
    print(f"  Parallel workers: {parallel}")
    print()

    success_count, skip_count, errors = batch_fingerprints(
        symbol=symbol,
        date_from=date_from,
        date_to=date_to,
        evidence_dir=evidence_dir,
        output_dir=output_dir,
        params=params,
        parallel=parallel,
    )

    print()
    print(f"Summary: {success_count} emitted, {skip_count} skipped")

    if errors:
        print()
        print("Skipped dates:")
        for err in errors:
            print(f"  {err}")

    return 0 if success_count > 0 else 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Trajectory Families v0.1 - DayFingerprint Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # emit-fingerprint command
    emit_parser = subparsers.add_parser(
        "emit-fingerprint",
        help="Generate fingerprint for a single day",
    )
    emit_parser.add_argument(
        "--symbol", required=True, help="Symbol (e.g., GBPUSD)"
    )
    emit_parser.add_argument(
        "--date", required=True, help="Date (YYYY-MM-DD)"
    )
    emit_parser.add_argument(
        "--trajectory-csv", help="Path to trajectory.csv (optional, auto-discovered)"
    )
    emit_parser.add_argument(
        "--evidence-dir", help="Evidence runs directory"
    )
    emit_parser.add_argument(
        "--output-dir", help="Output directory for fingerprints"
    )
    emit_parser.add_argument(
        "--params-file", help="Path to params JSON file"
    )

    # batch-fingerprints command
    batch_parser = subparsers.add_parser(
        "batch-fingerprints",
        help="Generate fingerprints for a date range",
    )
    batch_parser.add_argument(
        "--symbol", required=True, help="Symbol (e.g., GBPUSD)"
    )
    batch_parser.add_argument(
        "--date-from", required=True, help="Start date (YYYY-MM-DD)"
    )
    batch_parser.add_argument(
        "--date-to", required=True, help="End date (YYYY-MM-DD)"
    )
    batch_parser.add_argument(
        "--evidence-dir", help="Evidence runs directory"
    )
    batch_parser.add_argument(
        "--output-dir", help="Output directory for fingerprints"
    )
    batch_parser.add_argument(
        "--params-file", help="Path to params JSON file"
    )
    batch_parser.add_argument(
        "--parallel", type=int, default=1, help="Number of parallel workers (default: 1)"
    )

    args = parser.parse_args()

    if args.command == "emit-fingerprint":
        return cmd_emit_fingerprint(args)
    elif args.command == "batch-fingerprints":
        return cmd_batch_fingerprints(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
