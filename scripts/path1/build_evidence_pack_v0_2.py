#!/usr/bin/env python3
"""
Path 1 Evidence Pack v0.2 Builder (M15 overlay)

Includes DST audit functionality for validating M15 strip integrity across
Daylight Saving Time transitions at the NY session boundary (17:00 America/New_York).
"""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bisect

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

BLOCKS_VIEW = "derived.v_path1_evidence_dis_v1_1"
SPINE_TABLE = "ovc.ovc_blocks_v01_1_min"
M15_TABLE = "ovc.ovc_candles_m15_raw"

M15_STEP_MS = 15 * 60 * 1000
TWO_H_MS = 2 * 60 * 60 * 1000
FOUR_H_MS = 4 * 60 * 60 * 1000

DEFAULT_TOLERANCE = float(os.environ.get("EVIDENCE_PACK_OHLC_TOL", "1e-6"))

# DST stress test date ranges (NY dates)
DST_RANGES = {
    "spring": ["2023-03-10", "2023-03-11", "2023-03-12", "2023-03-13", "2023-03-14"],
    "fall": ["2023-11-03", "2023-11-04", "2023-11-05", "2023-11-06", "2023-11-07"],
}

NY_TZ = ZoneInfo("America/New_York")
UTC_TZ = timezone.utc

# Files excluded from manifests (the manifests/hash files themselves)
MANIFEST_EXCLUDE = {
    "manifest.json",
    "manifest_sha256.txt",
    "pack_sha256.txt",
    # New data/build hash files
    "data_manifest.json",
    "data_manifest_sha256.txt",
    "data_sha256.txt",
    "build_manifest.json",
    "build_manifest_sha256.txt",
    "build_sha256.txt",
}

# Data files included in data_manifest (deterministic candle data only)
DATA_FILE_PATTERNS = {
    "backbone_2h.csv",
    "strips/2h/",
    "context/4h/",
}


def validate_date(value: str, field_name: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"{field_name} must be YYYY-MM-DD, got: {value}") from exc
    return value


def resolve_dsn() -> str:
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not dsn:
        raise SystemExit("Missing DATABASE_URL or NEON_DSN environment variable")
    return dsn


def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_data_file(rel_path: str) -> bool:
    """Check if a relative path is a deterministic data file."""
    if rel_path == "backbone_2h.csv":
        return True
    if rel_path.startswith("strips/2h/") and rel_path.endswith(".csv"):
        return True
    if rel_path.startswith("context/4h/") and rel_path.endswith(".csv"):
        return True
    return False


def build_manifest(pack_root: Path, data_only: bool = False) -> dict:
    """
    Build manifest of files in pack_root.

    Args:
        pack_root: Root directory of the evidence pack
        data_only: If True, only include deterministic data files (backbone, strips, context)
                   If False, include all files (for build manifest)
    """
    entries = []
    for path in pack_root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(pack_root).as_posix()
        if rel_path in MANIFEST_EXCLUDE:
            continue
        if data_only and not is_data_file(rel_path):
            continue
        entries.append(
            {
                "bytes": path.stat().st_size,
                "relative_path": rel_path,
                "sha256": compute_file_sha256(path),
            }
        )
    entries.sort(key=lambda item: item["relative_path"])
    return {"files": entries}


def compute_pack_sha256(manifest: dict) -> str:
    lines = []
    for entry in manifest.get("files", []):
        lines.append(f"{entry['sha256']}  {entry['relative_path']}\n")
    data = "".join(lines).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def write_manifest_files(pack_root: Path) -> dict:
    """
    Write both data manifest (stable) and build manifest (includes timestamps).

    Returns dict with all hash values for ledger recording.
    """
    # Build data manifest (deterministic candle data only)
    data_manifest = build_manifest(pack_root, data_only=True)
    data_manifest_path = pack_root / "data_manifest.json"
    data_manifest_text = json.dumps(data_manifest, sort_keys=True, separators=(",", ":")) + "\n"
    data_manifest_path.write_text(data_manifest_text, encoding="utf-8")

    data_sha256 = compute_pack_sha256(data_manifest)
    (pack_root / "data_sha256.txt").write_text(data_sha256 + "\n", encoding="utf-8")

    data_manifest_sha256 = compute_file_sha256(data_manifest_path)
    (pack_root / "data_manifest_sha256.txt").write_text(data_manifest_sha256 + "\n", encoding="utf-8")

    # Build full manifest (all files including meta.json, qc_report.json)
    build_manifest_dict = build_manifest(pack_root, data_only=False)
    build_manifest_path = pack_root / "build_manifest.json"
    build_manifest_text = json.dumps(build_manifest_dict, sort_keys=True, separators=(",", ":")) + "\n"
    build_manifest_path.write_text(build_manifest_text, encoding="utf-8")

    build_sha256 = compute_pack_sha256(build_manifest_dict)
    (pack_root / "build_sha256.txt").write_text(build_sha256 + "\n", encoding="utf-8")

    build_manifest_sha256 = compute_file_sha256(build_manifest_path)
    (pack_root / "build_manifest_sha256.txt").write_text(build_manifest_sha256 + "\n", encoding="utf-8")

    # Legacy compatibility: also write old manifest files
    # (manifest.json = build_manifest, pack_sha256 = build_sha256)
    manifest = build_manifest_dict
    manifest_path = pack_root / "manifest.json"
    manifest_text = json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    manifest_path.write_text(manifest_text, encoding="utf-8")

    pack_sha256 = build_sha256
    (pack_root / "pack_sha256.txt").write_text(pack_sha256 + "\n", encoding="utf-8")

    manifest_sha256 = compute_file_sha256(manifest_path)
    (pack_root / "manifest_sha256.txt").write_text(manifest_sha256 + "\n", encoding="utf-8")

    return {
        # New data/build separation
        "data_manifest_sha256": data_manifest_sha256,
        "data_sha256": data_sha256,
        "build_manifest_sha256": build_manifest_sha256,
        "build_sha256": build_sha256,
        # Legacy fields
        "manifest": manifest,
        "manifest_sha256": manifest_sha256,
        "pack_sha256": pack_sha256,
    }


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n")


def get_git_info(repo_root: Path) -> dict:
    commit = None
    dirty = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            commit = result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = None

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            dirty = bool(result.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        dirty = None

    return {"commit": commit, "dirty": dirty}


def build_qc_summary(qc_report: dict) -> dict:
    summary = qc_report.get("summary") or {}
    return {
        "blocks_total": summary.get("blocks_total", 0),
        "strips_written": summary.get("strips_written", 0),
        "context_written": summary.get("context_written", 0),
        "candle_count_failures": len(qc_report.get("candle_count", [])),
        "continuity_issues": len(qc_report.get("continuity", [])),
        "ohlc_sanity_issues": len(qc_report.get("ohlc_sanity", [])),
        "aggregation_match_issues": len(qc_report.get("aggregation_match", [])),
    }


def build_m15_scope(qc_report: dict) -> dict:
    scope = qc_report.get("m15_scope") or {}
    return {
        "min_needed_ms": scope.get("min_needed_ms"),
        "max_needed_ms": scope.get("max_needed_ms"),
        "rows_loaded": scope.get("rows_loaded"),
    }


def build_error_payload(exc: BaseException) -> dict:
    message = f"{type(exc).__name__}: {exc}"
    trace = traceback.format_exc().strip().replace("\r\n", "\n")
    if len(trace) > 1000:
        trace = trace[:1000]
    return {"message": message, "trace": trace}


def append_pack_ledger(
    ledger_path: Path,
    *,
    run_id: str,
    symbol: str,
    date_from: str,
    date_to: str,
    run_dir_rel: str,
    pack_root_rel: str,
    git_info: dict,
    qc_report: dict,
    hashes: dict,
    status: str,
    error_payload: Optional[dict],
) -> None:
    event = {
        "event_type": "evidence_pack_build",
        "pack_version": "0.2",
        "run_id": run_id,
        "sym": symbol,
        "date_from": date_from,
        "date_to": date_to,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "git": git_info,
        "paths": {
            "run_dir": run_dir_rel,
            "pack_root": pack_root_rel,
        },
        "m15_scope": build_m15_scope(qc_report),
        "qc_summary": build_qc_summary(qc_report),
        "hashes": {
            # Data hashes (stable across rebuilds if candle data unchanged)
            "data_manifest_sha256": hashes.get("data_manifest_sha256"),
            "data_sha256": hashes.get("data_sha256"),
            # Build hashes (may change due to timestamps in meta.json, qc_report.json)
            "build_manifest_sha256": hashes.get("build_manifest_sha256"),
            "build_sha256": hashes.get("build_sha256"),
            # Legacy fields (kept for backward compatibility)
            "manifest_sha256": hashes.get("manifest_sha256"),
            "pack_sha256": hashes.get("pack_sha256"),
        },
        "error": error_payload,
    }
    try:
        append_jsonl(ledger_path, event)
    except Exception as exc:
        print(f"WARNING: Failed to append pack_build.jsonl: {exc}")


def format_time_utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ohlc_sane(o: float, h: float, l: float, c: float) -> bool:
    if h < l:
        return False
    if h < max(o, c) or l > min(o, c):
        return False
    return True


def sum_volume(rows: List[Dict]) -> Optional[int]:
    values = [r.get("volume") for r in rows if r.get("volume") is not None]
    if not values:
        return None
    return int(sum(values))


def aggregate_rows(rows: List[Dict], group_size: int, base_step_ms: int) -> Optional[List[Dict]]:
    if len(rows) % group_size != 0:
        return None
    aggregated = []
    expected_span = group_size * base_step_ms
    for idx in range(0, len(rows), group_size):
        chunk = rows[idx:idx + group_size]
        if not chunk:
            return None
        bar_start_ms = chunk[0]["bar_start_ms"]
        bar_close_ms = chunk[-1]["bar_close_ms"]
        if bar_close_ms - bar_start_ms != expected_span:
            return None
        o = chunk[0]["o"]
        c = chunk[-1]["c"]
        h = max(r["h"] for r in chunk)
        l = min(r["l"] for r in chunk)
        volume = sum_volume(chunk)
        if not ohlc_sane(o, h, l, c):
            return None
        aggregated.append(
            {
                "bar_start_ms": bar_start_ms,
                "bar_close_ms": bar_close_ms,
                "o": o,
                "h": h,
                "l": l,
                "c": c,
                "volume": volume,
            }
        )
    return aggregated


def check_continuity(
    rows: List[Dict],
    step_ms: int,
    expected_start_ms: Optional[int] = None,
    expected_end_ms: Optional[int] = None,
) -> List[Dict]:
    issues = []
    if not rows:
        return issues
    if expected_start_ms is not None and rows[0]["bar_start_ms"] != expected_start_ms:
        issues.append(
            {
                "issue": "start_mismatch",
                "expected_start_ms": expected_start_ms,
                "actual_start_ms": rows[0]["bar_start_ms"],
            }
        )
    for idx in range(1, len(rows)):
        prev = rows[idx - 1]
        cur = rows[idx]
        step_actual = cur["bar_start_ms"] - prev["bar_start_ms"]
        if step_actual != step_ms:
            issues.append(
                {
                    "issue": "step_mismatch",
                    "idx": idx,
                    "expected_step_ms": step_ms,
                    "actual_step_ms": step_actual,
                }
            )
    for idx, row in enumerate(rows):
        span = row["bar_close_ms"] - row["bar_start_ms"]
        if span != step_ms:
            issues.append(
                {
                    "issue": "span_mismatch",
                    "idx": idx,
                    "expected_span_ms": step_ms,
                    "actual_span_ms": span,
                }
            )
    if expected_end_ms is not None and rows[-1]["bar_close_ms"] != expected_end_ms:
        issues.append(
            {
                "issue": "end_mismatch",
                "expected_end_ms": expected_end_ms,
                "actual_end_ms": rows[-1]["bar_close_ms"],
            }
        )
    return issues


def fetch_blocks(conn, symbol: str, date_from: str, date_to: str) -> List[Dict]:
    sql = f"""
        SELECT
            e.block_id,
            e.sym,
            e.bar_close_ms,
            m.date_ny,
            m.block4h,
            m.o,
            m.h,
            m.l,
            m.c
        FROM {BLOCKS_VIEW} e
        INNER JOIN {SPINE_TABLE} m
            ON e.block_id = m.block_id
           AND e.sym = m.sym
        WHERE e.sym = %s
          AND to_timestamp(e.bar_close_ms / 1000)::date BETWEEN %s AND %s
        ORDER BY e.bar_close_ms;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (symbol, date_from, date_to))
        return list(cur.fetchall())


def fetch_m15_range(conn, symbol: str, min_needed_ms: int, max_needed_ms: int) -> List[Dict]:
    sql = f"""
        SELECT
            bar_start_ms,
            bar_close_ms,
            o,
            h,
            l,
            c,
            volume
        FROM {M15_TABLE}
        WHERE sym = %s
          AND bar_start_ms >= %s
          AND bar_start_ms < %s
        ORDER BY bar_start_ms;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (symbol, min_needed_ms, max_needed_ms))
        return list(cur.fetchall())


def write_candles_csv(rows: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "idx",
            "time_utc",
            "bar_start_ms",
            "bar_close_ms",
            "o",
            "h",
            "l",
            "c",
            "volume",
        ])
        for idx, row in enumerate(rows, start=1):
            volume = row.get("volume")
            writer.writerow(
                [
                    idx,
                    format_time_utc(row["bar_start_ms"]),
                    row["bar_start_ms"],
                    row["bar_close_ms"],
                    row["o"],
                    row["h"],
                    row["l"],
                    row["c"],
                    "" if volume is None else volume,
                ]
            )


def unique_values(items: List[Dict], key: str) -> int:
    return len({item.get(key) for item in items if item.get(key) is not None})


# =============================================================================
# DST Audit Functions
# =============================================================================


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


def extract_block_letter(block_id: str) -> Optional[str]:
    """
    Extract block letter (A-L) from block_id.

    Expected format: YYYYMMDD-X-SYM where X is the block letter.

    Args:
        block_id: Block identifier (e.g., "20230312-A-GBPUSD")

    Returns:
        Block letter (A-L) or None if invalid format
    """
    parts = block_id.split("-")
    if len(parts) >= 2 and len(parts[1]) == 1 and parts[1].upper() in "ABCDEFGHIJKL":
        return parts[1].upper()
    return None


def validate_strip_integrity(
    m15_rows: List[Dict],
    block_id: str,
    expected_close_ms: int,
) -> Tuple[bool, List[Dict]]:
    """
    Validate Invariant A: Strip integrity per 2H block.

    Checks:
    - Strip contains exactly 8 candles
    - bar_start_ms increments exactly 900000ms across the strip
    - Last candle's bar_close_ms equals block.bar_close_ms

    Args:
        m15_rows: List of M15 candle dictionaries
        block_id: Block identifier for error reporting
        expected_close_ms: Expected bar_close_ms for the block

    Returns:
        Tuple of (passed: bool, issues: list of anomaly dicts)
    """
    issues = []

    # Check count
    if len(m15_rows) != 8:
        issues.append({
            "date_ny": None,  # Will be filled by caller
            "block_id": block_id,
            "type": "strip_count",
            "details": {
                "expected": 8,
                "actual": len(m15_rows),
            },
        })
        return (False, issues)

    # Check 900000ms step (continuity)
    for idx in range(1, len(m15_rows)):
        prev_start = m15_rows[idx - 1]["bar_start_ms"]
        cur_start = m15_rows[idx]["bar_start_ms"]
        step = cur_start - prev_start
        if step != M15_STEP_MS:
            issues.append({
                "date_ny": None,
                "block_id": block_id,
                "type": "continuity",
                "details": {
                    "idx": idx,
                    "expected_step_ms": M15_STEP_MS,
                    "actual_step_ms": step,
                    "prev_bar_start_ms": prev_start,
                    "cur_bar_start_ms": cur_start,
                },
            })

    # Check alignment on close
    last_close = m15_rows[-1]["bar_close_ms"]
    if last_close != expected_close_ms:
        issues.append({
            "date_ny": None,
            "block_id": block_id,
            "type": "continuity",
            "details": {
                "issue": "end_mismatch",
                "expected_close_ms": expected_close_ms,
                "actual_close_ms": last_close,
            },
        })

    return (len(issues) == 0, issues)


def validate_aggregation_match(
    m15_rows: List[Dict],
    spine_ohlc: Dict[str, float],
    block_id: str,
    tolerance: float,
) -> Tuple[bool, Optional[Dict], Optional[Dict]]:
    """
    Validate Invariant B: Aggregated strip OHLC matches canonical 2H block OHLC.

    Args:
        m15_rows: List of 8 M15 candle dictionaries
        spine_ohlc: Dict with keys 'o', 'h', 'l', 'c' from spine
        block_id: Block identifier for error reporting
        tolerance: OHLC comparison tolerance

    Returns:
        Tuple of (passed: bool, worst_deviation: dict or None, anomaly: dict or None)
    """
    if len(m15_rows) != 8:
        return (False, None, {
            "date_ny": None,
            "block_id": block_id,
            "type": "aggregation",
            "details": {"error": "insufficient_candles", "count": len(m15_rows)},
        })

    # Aggregate M15 to 2H
    agg_o = m15_rows[0]["o"]
    agg_c = m15_rows[-1]["c"]
    agg_h = max(r["h"] for r in m15_rows)
    agg_l = min(r["l"] for r in m15_rows)

    deviations = {
        "o": abs(agg_o - spine_ohlc["o"]),
        "h": abs(agg_h - spine_ohlc["h"]),
        "l": abs(agg_l - spine_ohlc["l"]),
        "c": abs(agg_c - spine_ohlc["c"]),
    }

    mismatches = [k for k, v in deviations.items() if v > tolerance]
    worst_metric = max(deviations.keys(), key=lambda k: deviations[k])
    worst_deviation = {
        "block_id": block_id,
        "metric": worst_metric,
        "value": deviations[worst_metric],
    }

    if mismatches:
        return (False, worst_deviation, {
            "date_ny": None,
            "block_id": block_id,
            "type": "aggregation",
            "details": {
                "mismatches": mismatches,
                "tolerance": tolerance,
                "agg": {"o": agg_o, "h": agg_h, "l": agg_l, "c": agg_c},
                "spine": spine_ohlc,
                "deviations": deviations,
            },
        })

    return (True, worst_deviation, None)


def validate_session_boundary(
    blocks_by_date: Dict[str, List[Dict]],
) -> Tuple[int, List[Dict]]:
    """
    Validate Invariant C: Session boundary coherence.

    For each NY date:
    - 2H blocks count to 12 (A-L)
    - A-block's computed UTC start corresponds to 17:00 NY

    Args:
        blocks_by_date: Dict mapping date_ny to list of block dicts

    Returns:
        Tuple of (failure_count: int, anomalies: list)
    """
    anomalies = []
    failure_count = 0

    for date_ny, blocks in sorted(blocks_by_date.items()):
        # Check block count (should be 12 for complete day)
        block_letters = sorted(
            {letter for letter in (extract_block_letter(b["block_id"]) for b in blocks) if letter}
        )
        if len(block_letters) != 12:
            failure_count += 1
            expected_letters = set("ABCDEFGHIJKL")
            actual_letters = set(block_letters)
            anomalies.append({
                "date_ny": date_ny,
                "block_id": None,
                "type": "session_boundary",
                "details": {
                    "issue": "block_count",
                    "expected_count": 12,
                    "actual_count": len(block_letters),
                    "missing_letters": sorted(expected_letters - actual_letters),
                    "extra_letters": sorted(actual_letters - expected_letters),
                },
            })

        # Find A-block
        a_blocks = [b for b in blocks if extract_block_letter(b["block_id"]) == "A"]
        if not a_blocks:
            # No A-block in this date - skip session boundary check
            continue

        a_block = a_blocks[0]
        actual_bar_close_ms = int(a_block["bar_close_ms"])
        # A-block spans 17:00-19:00 NY, so bar_open_ms = bar_close_ms - 2H
        actual_start_ms = actual_bar_close_ms - TWO_H_MS

        # Compute expected start from NY 17:00
        expected_start_ms = ny_17_to_epoch_ms(date_ny)

        if actual_start_ms != expected_start_ms:
            failure_count += 1
            anomalies.append({
                "date_ny": date_ny,
                "block_id": a_block["block_id"],
                "type": "session_boundary",
                "details": {
                    "expected_start_ms": expected_start_ms,
                    "actual_start_ms": actual_start_ms,
                    "delta_ms": actual_start_ms - expected_start_ms,
                    "expected_utc": format_time_utc(expected_start_ms),
                    "actual_utc": format_time_utc(actual_start_ms),
                },
            })

    return (failure_count, anomalies)


def run_dst_audit(
    blocks: List[Dict],
    m15_by_block: Dict[str, List[Dict]],
    tolerance: float,
    dst_range: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run DST audit on blocks, validating all three invariants.

    Args:
        blocks: List of block dicts from the pack build
        m15_by_block: Dict mapping block_id to list of M15 candles
        tolerance: OHLC comparison tolerance
        dst_range: Optional filter ("spring", "fall", or None for all)

    Returns:
        DST audit report dict matching dst_audit.json schema
    """
    # Filter blocks to DST dates if range specified
    if dst_range and dst_range in DST_RANGES:
        target_dates = set(DST_RANGES[dst_range])
        blocks = [b for b in blocks if str(b.get("date_ny")) in target_dates]

    # Deterministic ordering
    blocks = sorted(blocks, key=lambda b: (str(b["date_ny"]), int(b["bar_close_ms"]), b["block_id"]))

    # Get unique dates tested
    dates_tested = sorted({str(b["date_ny"]) for b in blocks})

    # Group blocks by date_ny
    blocks_by_date: Dict[str, List[Dict]] = defaultdict(list)
    for block in blocks:
        blocks_by_date[str(block["date_ny"])].append(block)

    # Sort blocks within each date by bar_open_ms
    for date_ny in blocks_by_date:
        blocks_by_date[date_ny].sort(key=lambda b: b["bar_close_ms"])

    # Initialize counters
    blocks_checked = 0
    strip_count_failures = 0
    continuity_failures = 0
    aggregation_failures = 0
    all_anomalies: List[Dict] = []
    worst_agg_deviation: Optional[Dict] = None

    # Validate each block
    for block in blocks:
        block_id = block["block_id"]
        date_ny = str(block["date_ny"])
        bar_close_ms = int(block["bar_close_ms"])
        blocks_checked += 1

        m15_rows = m15_by_block.get(block_id, [])

        # Invariant A: Strip integrity
        strip_ok, strip_issues = validate_strip_integrity(
            m15_rows, block_id, bar_close_ms
        )
        for issue in strip_issues:
            issue["date_ny"] = date_ny
            if issue["type"] == "strip_count":
                strip_count_failures += 1
            elif issue["type"] == "continuity":
                continuity_failures += 1
            all_anomalies.append(issue)

        # Invariant B: Aggregation match (only if we have 8 candles)
        if len(m15_rows) == 8:
            spine_ohlc = {
                "o": block["o"],
                "h": block["h"],
                "l": block["l"],
                "c": block["c"],
            }
            agg_ok, deviation, agg_anomaly = validate_aggregation_match(
                m15_rows, spine_ohlc, block_id, tolerance
            )
            if deviation:
                if (
                    worst_agg_deviation is None
                    or deviation["value"] > worst_agg_deviation["value"]
                ):
                    worst_agg_deviation = deviation
            if agg_anomaly:
                agg_anomaly["date_ny"] = date_ny
                aggregation_failures += 1
                all_anomalies.append(agg_anomaly)

    # Invariant C: Session boundary coherence
    session_failures, session_anomalies = validate_session_boundary(blocks_by_date)
    all_anomalies.extend(session_anomalies)

    # Check for missing DST dates if range was specified
    missing_dates: List[str] = []
    if dst_range and dst_range in DST_RANGES:
        requested_dates = set(DST_RANGES[dst_range])
        actual_dates = set(dates_tested)
        missing_dates = sorted(requested_dates - actual_dates)

    return {
        "dates_tested": dates_tested,
        "blocks_checked": blocks_checked,
        "strip_count_failures": strip_count_failures,
        "continuity_failures": continuity_failures,
        "aggregation_failures": aggregation_failures,
        "session_boundary_failures": session_failures,
        "worst_aggregation_deviation": worst_agg_deviation,
        "anomalies": all_anomalies,
        "dst_range_requested": dst_range,
        "missing_dates": missing_dates if missing_dates else None,
    }


def write_dst_audit(pack_dir: Path, audit_result: Dict[str, Any]) -> Path:
    """
    Write dst_audit.json to the evidence pack directory.

    Args:
        pack_dir: Evidence pack directory
        audit_result: DST audit result dict

    Returns:
        Path to written dst_audit.json
    """
    dst_audit_path = pack_dir / "dst_audit.json"
    dst_audit_path.write_text(
        json.dumps(audit_result, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return dst_audit_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Path 1 Evidence Pack v0.2 (M15 overlay)")
    parser.add_argument("--run-id", required=True, help="Evidence run ID (e.g., p1_20260120_001)")
    parser.add_argument("--sym", required=True, help="Symbol (e.g., GBPUSD)")
    parser.add_argument("--date-from", required=True, help="Start date YYYY-MM-DD (inclusive)")
    parser.add_argument("--date-to", required=True, help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE, help="OHLC match tolerance")
    parser.add_argument(
        "--dst-audit",
        action="store_true",
        help="Run DST audit on blocks included in pack (validates M15 strip integrity across DST transitions)",
    )
    parser.add_argument(
        "--dst-audit-range",
        choices=["spring", "fall"],
        default=None,
        help="Filter DST audit to specific range: spring (2023-03-10..14) or fall (2023-11-03..07)",
    )
    args = parser.parse_args()

    validate_date(args.date_from, "--date-from")
    validate_date(args.date_to, "--date-to")
    symbol = args.sym.upper()
    repo_root = Path(args.repo_root).resolve()

    run_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / args.run_id
    pack_dir = run_dir / "outputs" / "evidence_pack_v0_2"
    ledger_path = run_dir / "pack_build.jsonl"
    git_info = get_git_info(repo_root)
    run_dir_rel = (Path("reports") / "path1" / "evidence" / "runs" / args.run_id).as_posix()
    pack_root_rel = (Path(run_dir_rel) / "outputs" / "evidence_pack_v0_2").as_posix()
    strips_dir = pack_dir / "strips" / "2h"
    context_dir = pack_dir / "context" / "4h"

    pack_dir.mkdir(parents=True, exist_ok=True)
    strips_dir.mkdir(parents=True, exist_ok=True)
    context_dir.mkdir(parents=True, exist_ok=True)

    qc_report = {
        "run_id": args.run_id,
        "symbol": symbol,
        "date_from": args.date_from,
        "date_to": args.date_to,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "candle_count": [],
        "continuity": [],
        "ohlc_sanity": [],
        "aggregation_match": [],
        "context": [],
        "summary": {},
    }

    backbone_rows = []
    m15_by_block: Dict[str, List[Dict]] = {}
    m15_by_block_all: Dict[str, List[Dict]] = {}
    strips_written = 0
    hashes = {
        "data_manifest_sha256": None,
        "data_sha256": None,
        "build_manifest_sha256": None,
        "build_sha256": None,
        "manifest_sha256": None,
        "pack_sha256": None,
    }

    try:
        with psycopg2.connect(resolve_dsn()) as conn:
            blocks = fetch_blocks(conn, symbol, args.date_from, args.date_to)
            if not blocks:
                summary = {
                    "blocks_total": 0,
                    "strips_written": 0,
                    "blocks_missing_m15": 0,
                    "blocks_with_continuity_issues": 0,
                    "blocks_with_ohlc_issues": 0,
                    "blocks_with_agg_mismatch": 0,
                    "context_windows_total": 0,
                    "context_written": 0,
                    "context_m30": 0,
                    "context_h1": 0,
                }
                qc_report["summary"] = summary
                meta = {
                    "version": "evidence_pack_v0_2",
                    "run_id": args.run_id,
                    "symbol": symbol,
                    "date_from": args.date_from,
                    "date_to": args.date_to,
                    "generated_at": qc_report["generated_at"],
                    "counts": {
                        "blocks": 0,
                        "strips_written": 0,
                        "context_written": 0,
                    },
                    "sources": {
                        "blocks_view": BLOCKS_VIEW,
                        "spine_table": SPINE_TABLE,
                        "m15_table": M15_TABLE,
                    },
                    "tolerance": args.tolerance,
                    "m15_scope": qc_report.get("m15_scope", {}),
                }
                (pack_dir / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
                (pack_dir / "qc_report.json").write_text(
                    json.dumps(qc_report, indent=2, sort_keys=True), encoding="utf-8"
                )
                (pack_dir / "backbone_2h.csv").write_text(
                    "block_id,bar_close_ms,strip_path,m15_count\n", encoding="utf-8"
                )
                hashes = write_manifest_files(pack_dir)
                append_pack_ledger(
                    ledger_path,
                    run_id=args.run_id,
                    symbol=symbol,
                    date_from=args.date_from,
                    date_to=args.date_to,
                    run_dir_rel=run_dir_rel,
                    pack_root_rel=pack_root_rel,
                    git_info=git_info,
                    qc_report=qc_report,
                    hashes=hashes,
                    status="success",
                    error_payload=None,
                )
                print("No blocks found; wrote empty evidence pack.")
                print(f"Evidence pack v0.2 complete: {pack_dir}")
                return

            block_start_ms_values = [int(block["bar_close_ms"]) - TWO_H_MS for block in blocks]
            min_needed_ms = min(block_start_ms_values)
            max_needed_ms = max(int(block["bar_close_ms"]) for block in blocks)
            m15_rows_all = fetch_m15_range(conn, symbol, min_needed_ms, max_needed_ms)
            m15_close_ms = [int(row["bar_close_ms"]) for row in m15_rows_all]

            qc_report["m15_scope"] = {
                "min_needed_ms": min_needed_ms,
                "max_needed_ms": max_needed_ms,
                "rows_loaded": len(m15_rows_all),
            }

            for block in blocks:
                block_id = block["block_id"]
                bar_close_ms = int(block["bar_close_ms"])
                start_ms = bar_close_ms - TWO_H_MS
                start_idx = bisect.bisect_right(m15_close_ms, start_ms)
                end_idx = bisect.bisect_right(m15_close_ms, bar_close_ms)
                m15_rows = m15_rows_all[start_idx:end_idx]
                m15_count = len(m15_rows)
                m15_by_block_all[block_id] = m15_rows

                strip_rel = Path("strips/2h") / f"{block_id}.csv"
                strip_path = pack_dir / strip_rel
                backbone_rows.append(
                    {
                        "block_id": block_id,
                        "bar_close_ms": bar_close_ms,
                        "strip_path": strip_rel.as_posix() if m15_count == 8 else "",
                        "m15_count": m15_count,
                    }
                )

                if m15_count != 8:
                    qc_report["candle_count"].append(
                        {
                            "scope": "2h",
                            "block_id": block_id,
                            "expected": 8,
                            "actual": m15_count,
                        }
                    )
                    continue

                continuity_issues = check_continuity(
                    m15_rows, M15_STEP_MS, expected_start_ms=start_ms, expected_end_ms=bar_close_ms
                )
                for issue in continuity_issues:
                    qc_report["continuity"].append(
                        {
                            "scope": "2h",
                            "block_id": block_id,
                            **issue,
                        }
                    )

                for idx, row in enumerate(m15_rows):
                    if not ohlc_sane(row["o"], row["h"], row["l"], row["c"]):
                        qc_report["ohlc_sanity"].append(
                            {
                                "scope": "2h",
                                "block_id": block_id,
                                "idx": idx + 1,
                                "o": row["o"],
                                "h": row["h"],
                                "l": row["l"],
                                "c": row["c"],
                            }
                        )

                agg_o = m15_rows[0]["o"]
                agg_c = m15_rows[-1]["c"]
                agg_h = max(r["h"] for r in m15_rows)
                agg_l = min(r["l"] for r in m15_rows)

                spine_o = block["o"]
                spine_h = block["h"]
                spine_l = block["l"]
                spine_c = block["c"]

                if not ohlc_sane(agg_o, agg_h, agg_l, agg_c):
                    qc_report["ohlc_sanity"].append(
                        {
                            "scope": "2h_aggregate",
                            "block_id": block_id,
                            "o": agg_o,
                            "h": agg_h,
                            "l": agg_l,
                            "c": agg_c,
                        }
                    )

                mismatch = []
                if abs(agg_o - spine_o) > args.tolerance:
                    mismatch.append("o")
                if abs(agg_h - spine_h) > args.tolerance:
                    mismatch.append("h")
                if abs(agg_l - spine_l) > args.tolerance:
                    mismatch.append("l")
                if abs(agg_c - spine_c) > args.tolerance:
                    mismatch.append("c")
                if mismatch:
                    qc_report["aggregation_match"].append(
                        {
                            "block_id": block_id,
                            "mismatch": mismatch,
                            "tolerance": args.tolerance,
                            "agg": {"o": agg_o, "h": agg_h, "l": agg_l, "c": agg_c},
                            "spine": {"o": spine_o, "h": spine_h, "l": spine_l, "c": spine_c},
                        }
                    )

                write_candles_csv(m15_rows, strip_path)
                strips_written += 1
                m15_by_block[block_id] = m15_rows

            # Write backbone
            backbone_path = pack_dir / "backbone_2h.csv"
            with backbone_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["block_id", "bar_close_ms", "strip_path", "m15_count"])
                for row in backbone_rows:
                    writer.writerow(
                        [
                            row["block_id"],
                            row["bar_close_ms"],
                            row["strip_path"],
                            row["m15_count"],
                        ]
                    )

            # Build 4H context
            groups: Dict[tuple, List[Dict]] = defaultdict(list)
            for block in blocks:
                groups[(block["date_ny"], block["block4h"])].append(block)

            context_written = 0
            context_m30 = 0
            context_h1 = 0

            for (date_ny, block4h), block_group in groups.items():
                block_group.sort(key=lambda b: b["bar_close_ms"])
                window_end_ms = int(block_group[-1]["bar_close_ms"])
                window_start_ms = window_end_ms - FOUR_H_MS
                m15_rows = []
                missing_blocks = []
                for block in block_group:
                    block_id = block["block_id"]
                    if block_id not in m15_by_block:
                        missing_blocks.append(block_id)
                        continue
                    m15_rows.extend(m15_by_block[block_id])

                if missing_blocks:
                    qc_report["context"].append(
                        {
                            "date_ny": str(date_ny),
                            "block4h": block4h,
                            "issue": "missing_blocks",
                            "blocks": missing_blocks,
                        }
                    )
                    continue

                if len(m15_rows) != 16:
                    qc_report["context"].append(
                        {
                            "date_ny": str(date_ny),
                            "block4h": block4h,
                            "issue": "m15_count",
                            "expected": 16,
                            "actual": len(m15_rows),
                        }
                    )
                    continue

                m15_rows.sort(key=lambda r: r["bar_start_ms"])
                continuity_issues = check_continuity(
                    m15_rows, M15_STEP_MS, expected_start_ms=window_start_ms, expected_end_ms=window_end_ms
                )
                if continuity_issues:
                    qc_report["context"].append(
                        {
                            "date_ny": str(date_ny),
                            "block4h": block4h,
                            "issue": "continuity",
                            "details": continuity_issues,
                        }
                    )
                    continue

                m30_rows = aggregate_rows(m15_rows, 2, M15_STEP_MS)
                granularity = None
                context_rows = None

                if m30_rows and len(m30_rows) == 8:
                    granularity = "M30"
                    context_rows = m30_rows
                    context_m30 += 1
                else:
                    h1_rows = aggregate_rows(m15_rows, 4, M15_STEP_MS)
                    if h1_rows and len(h1_rows) == 4:
                        granularity = "H1"
                        context_rows = h1_rows
                        context_h1 += 1

                if not context_rows:
                    qc_report["context"].append(
                        {
                            "date_ny": str(date_ny),
                            "block4h": block4h,
                            "issue": "aggregate_failed",
                        }
                    )
                    continue

                context_path = context_dir / f"{block4h}_{date_ny}.csv"
                write_candles_csv(context_rows, context_path)
                context_written += 1

                qc_report["context"].append(
                    {
                        "date_ny": str(date_ny),
                        "block4h": block4h,
                        "issue": "ok",
                        "granularity": granularity,
                        "count": len(context_rows),
                    }
                )

            summary = {
                "blocks_total": len(blocks),
                "strips_written": strips_written,
                "blocks_missing_m15": unique_values(qc_report["candle_count"], "block_id"),
                "blocks_with_continuity_issues": unique_values(qc_report["continuity"], "block_id"),
                "blocks_with_ohlc_issues": unique_values(qc_report["ohlc_sanity"], "block_id"),
                "blocks_with_agg_mismatch": unique_values(qc_report["aggregation_match"], "block_id"),
                "context_windows_total": len(groups),
                "context_written": context_written,
                "context_m30": context_m30,
                "context_h1": context_h1,
            }
            qc_report["summary"] = summary

            meta = {
                "version": "evidence_pack_v0_2",
                "run_id": args.run_id,
                "symbol": symbol,
                "date_from": args.date_from,
                "date_to": args.date_to,
                "generated_at": qc_report["generated_at"],
                "counts": {
                    "blocks": len(blocks),
                    "strips_written": strips_written,
                    "context_written": context_written,
                },
                "sources": {
                    "blocks_view": BLOCKS_VIEW,
                    "spine_table": SPINE_TABLE,
                    "m15_table": M15_TABLE,
                },
                "tolerance": args.tolerance,
                "m15_scope": qc_report.get("m15_scope", {}),
                "strip_columns": [
                    "idx",
                    "time_utc",
                    "bar_start_ms",
                    "bar_close_ms",
                    "o",
                    "h",
                    "l",
                    "c",
                    "volume",
                ],
                "context_columns": [
                    "idx",
                    "time_utc",
                    "bar_start_ms",
                    "bar_close_ms",
                    "o",
                    "h",
                    "l",
                    "c",
                    "volume",
                ],
            }

            (pack_dir / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
            (pack_dir / "qc_report.json").write_text(
                json.dumps(qc_report, indent=2, sort_keys=True), encoding="utf-8"
            )

            # Run DST audit if requested
            if args.dst_audit:
                print("Running DST audit...")
                dst_audit_result = run_dst_audit(
                    blocks=blocks,
                    m15_by_block=m15_by_block_all,
                    tolerance=args.tolerance,
                    dst_range=args.dst_audit_range,
                )
                dst_audit_path = write_dst_audit(pack_dir, dst_audit_result)
                print(f"DST audit complete: {dst_audit_path}")

                # Report summary
                print(f"  Dates tested: {len(dst_audit_result['dates_tested'])}")
                print(f"  Blocks checked: {dst_audit_result['blocks_checked']}")
                print(f"  Strip count failures: {dst_audit_result['strip_count_failures']}")
                print(f"  Continuity failures: {dst_audit_result['continuity_failures']}")
                print(f"  Aggregation failures: {dst_audit_result['aggregation_failures']}")
                print(f"  Session boundary failures: {dst_audit_result['session_boundary_failures']}")
                if dst_audit_result.get("missing_dates"):
                    print(f"  Missing dates (from requested range): {dst_audit_result['missing_dates']}")

        hashes = write_manifest_files(pack_dir)
        append_pack_ledger(
            ledger_path,
            run_id=args.run_id,
            symbol=symbol,
            date_from=args.date_from,
            date_to=args.date_to,
            run_dir_rel=run_dir_rel,
            pack_root_rel=pack_root_rel,
            git_info=git_info,
            qc_report=qc_report,
            hashes=hashes,
            status="success",
            error_payload=None,
        )
        print(f"Evidence pack v0.2 complete: {pack_dir}")
    except Exception as exc:
        error_payload = build_error_payload(exc)
        append_pack_ledger(
            ledger_path,
            run_id=args.run_id,
            symbol=symbol,
            date_from=args.date_from,
            date_to=args.date_to,
            run_dir_rel=run_dir_rel,
            pack_root_rel=pack_root_rel,
            git_info=git_info,
            qc_report=qc_report,
            hashes=hashes,
            status="error",
            error_payload=error_payload,
        )
        raise


if __name__ == "__main__":
    main()
