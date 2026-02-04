#!/usr/bin/env python3
"""
DST Mapping Verification Script

Validates that NY 17:00 session boundary conversions are correct across DST transitions.
This is a development/verification tool to confirm the DST audit logic is sound.

DST Stress Ranges (NY dates):
- Spring forward: 2023-03-10 -> 2023-03-14 (DST transition on 2023-03-12 at 02:00 local)
- Fall back:      2023-11-03 -> 2023-11-07 (DST transition on 2023-11-05 at 02:00 local)

Expected behavior:
- EST (winter): 17:00 NY = 22:00 UTC (UTC offset -5:00)
- EDT (summer): 17:00 NY = 21:00 UTC (UTC offset -4:00)

Usage:
    python scripts/dev/check_dst_mapping.py
    python scripts/dev/check_dst_mapping.py --verbose
    python scripts/dev/check_dst_mapping.py --json
"""

import argparse
import json
from datetime import datetime, timezone
from typing import Dict, List

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

NY_TZ = ZoneInfo("America/New_York")
UTC_TZ = timezone.utc

# DST stress test date ranges (NY dates)
DST_RANGES = {
    "spring": ["2023-03-10", "2023-03-11", "2023-03-12", "2023-03-13", "2023-03-14"],
    "fall": ["2023-11-03", "2023-11-04", "2023-11-05", "2023-11-06", "2023-11-07"],
}

# Expected UTC offsets for each date
# Spring: EST until 2023-03-12 02:00 local, then EDT
# Fall: EDT until 2023-11-05 02:00 local, then EST
EXPECTED_OFFSETS = {
    # Spring forward (EST -> EDT on 2023-03-12)
    "2023-03-10": -5,  # EST
    "2023-03-11": -5,  # EST
    "2023-03-12": -4,  # EDT (DST starts 02:00, so 17:00 is in EDT)
    "2023-03-13": -4,  # EDT
    "2023-03-14": -4,  # EDT
    # Fall back (EDT -> EST on 2023-11-05)
    "2023-11-03": -4,  # EDT
    "2023-11-04": -4,  # EDT
    "2023-11-05": -5,  # EST (DST ends 02:00, so 17:00 is in EST)
    "2023-11-06": -5,  # EST
    "2023-11-07": -5,  # EST
}


def ny_17_to_epoch_ms(date_ny_str: str) -> int:
    """
    Convert a NY date string to epoch milliseconds for 17:00 America/New_York.

    This handles DST transitions correctly:
    - During EST (winter): 17:00 NY = 22:00 UTC
    - During EDT (summer): 17:00 NY = 21:00 UTC

    Args:
        date_ny_str: Date string in YYYY-MM-DD format

    Returns:
        Epoch milliseconds for 17:00 NY on that date
    """
    year, month, day = map(int, date_ny_str.split("-"))
    # Create timezone-aware datetime at 17:00 NY
    local_dt = datetime(year, month, day, 17, 0, 0, tzinfo=NY_TZ)
    # Convert to UTC
    utc_dt = local_dt.astimezone(UTC_TZ)
    # Return epoch ms
    return int(utc_dt.timestamp() * 1000)


def compute_mapping_table() -> List[Dict]:
    """
    Compute the DST mapping table for all dates in both ranges.

    Returns:
        List of dicts with mapping information
    """
    results = []

    for range_name, dates in DST_RANGES.items():
        for date_ny in dates:
            year, month, day = map(int, date_ny.split("-"))

            # Local datetime at 17:00 NY
            local_dt = datetime(year, month, day, 17, 0, 0, tzinfo=NY_TZ)

            # Convert to UTC
            utc_dt = local_dt.astimezone(UTC_TZ)

            # Epoch ms
            epoch_ms = int(utc_dt.timestamp() * 1000)

            # Get actual UTC offset in hours
            offset_seconds = local_dt.utcoffset().total_seconds()
            actual_offset_hours = int(offset_seconds / 3600)

            # Expected offset
            expected_offset = EXPECTED_OFFSETS.get(date_ny)

            # Check if offset matches expectation
            offset_ok = actual_offset_hours == expected_offset

            # Determine timezone abbreviation
            tz_abbr = "EDT" if actual_offset_hours == -4 else "EST"

            results.append({
                "range": range_name,
                "date_ny": date_ny,
                "local_17_00": local_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "utc_time": utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "epoch_ms": epoch_ms,
                "utc_offset_hours": actual_offset_hours,
                "expected_offset": expected_offset,
                "offset_ok": offset_ok,
                "tz_abbr": tz_abbr,
            })

    return results


def print_table(results: List[Dict], verbose: bool = False) -> None:
    """Print the mapping table in human-readable format."""
    print()
    print("=" * 90)
    print("DST Mapping Verification: NY 17:00 Session Boundary")
    print("=" * 90)
    print()

    current_range = None
    for row in results:
        if row["range"] != current_range:
            current_range = row["range"]
            if current_range == "spring":
                print("SPRING FORWARD (EST -> EDT on 2023-03-12 02:00 local)")
            else:
                print("\nFALL BACK (EDT -> EST on 2023-11-05 02:00 local)")
            print("-" * 90)
            print(f"{'Date NY':<12} {'Local 17:00':<26} {'UTC':<22} {'Offset':<8} {'TZ':<5} {'OK':<4}")
            print("-" * 90)

        ok_marker = "YES" if row["offset_ok"] else "NO!"
        print(
            f"{row['date_ny']:<12} "
            f"{row['local_17_00']:<26} "
            f"{row['utc_time']:<22} "
            f"{row['utc_offset_hours']:>+3}:00   "
            f"{row['tz_abbr']:<5} "
            f"{ok_marker:<4}"
        )

        if verbose:
            print(f"             epoch_ms: {row['epoch_ms']}")

    print("-" * 90)
    print()

    # Summary
    all_ok = all(row["offset_ok"] for row in results)
    if all_ok:
        print("RESULT: All DST mappings are correct.")
    else:
        print("RESULT: Some DST mappings are INCORRECT!")
        for row in results:
            if not row["offset_ok"]:
                print(f"  - {row['date_ny']}: expected offset {row['expected_offset']}, got {row['utc_offset_hours']}")

    print()


def print_json(results: List[Dict]) -> None:
    """Print the mapping table as JSON."""
    output = {
        "description": "DST mapping verification for NY 17:00 session boundary",
        "ranges": {
            "spring": {
                "dates": DST_RANGES["spring"],
                "transition": "2023-03-12 02:00 local (EST -> EDT)",
            },
            "fall": {
                "dates": DST_RANGES["fall"],
                "transition": "2023-11-05 02:00 local (EDT -> EST)",
            },
        },
        "mappings": results,
        "all_offsets_correct": all(row["offset_ok"] for row in results),
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify DST mapping for NY 17:00 session boundary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show epoch_ms values",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    results = compute_mapping_table()

    if args.json:
        print_json(results)
    else:
        print_table(results, verbose=args.verbose)

    # Exit with error if any offsets are wrong
    all_ok = all(row["offset_ok"] for row in results)
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
