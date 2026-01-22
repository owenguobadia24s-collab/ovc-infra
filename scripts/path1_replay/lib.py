#!/usr/bin/env python3
"""
Path1 Replay Verification (structural-only) helpers.
Pure functions only; no writes to Path1 ledger.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True)
class ParsedRun:
    date_from: Optional[str]
    date_to: Optional[str]
    n_obs: Optional[int]
    symbol: Optional[str]


def normalize_cell(value: str) -> str:
    return value.replace("`", "").strip()


def parse_markdown_rows(content: str) -> Dict[str, str]:
    rows: Dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if "|" not in line:
            continue
        parts = [normalize_cell(p) for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        key = parts[0].strip().lower()
        value = parts[1].strip()
        if key:
            rows[key] = value
    return rows


def extract_date_range_from_text(text: str) -> Optional[Tuple[str, str]]:
    dates = DATE_RE.findall(text)
    if len(dates) >= 2:
        return dates[0], dates[1]
    return None


def parse_run_md(content: str) -> Tuple[ParsedRun, List[str]]:
    warnings: List[str] = []
    rows = parse_markdown_rows(content)

    date_from: Optional[str] = None
    date_to: Optional[str] = None

    # 1) date_range_actual
    if "date_range_actual" in rows:
        extracted = extract_date_range_from_text(rows["date_range_actual"])
        if extracted:
            date_from, date_to = extracted
        else:
            warnings.append("date_range_actual_unparseable")

    # 2) date_start_actual + date_end_actual
    if date_from is None or date_to is None:
        start_actual = rows.get("date_start_actual")
        end_actual = rows.get("date_end_actual")
        if start_actual and end_actual:
            date_from = DATE_RE.findall(start_actual)[0] if DATE_RE.findall(start_actual) else None
            date_to = DATE_RE.findall(end_actual)[0] if DATE_RE.findall(end_actual) else None
            warnings.append("date_range_actual_from_start_end")

    # 2b) date_range_start + date_range_end
    if date_from is None or date_to is None:
        start_range = rows.get("date_range_start")
        end_range = rows.get("date_range_end")
        if start_range and end_range:
            date_from = DATE_RE.findall(start_range)[0] if DATE_RE.findall(start_range) else None
            date_to = DATE_RE.findall(end_range)[0] if DATE_RE.findall(end_range) else None
            warnings.append("date_range_actual_from_range_start_end")

    # 3) date_range_requested
    if date_from is None or date_to is None:
        if "date_range_requested" in rows:
            extracted = extract_date_range_from_text(rows["date_range_requested"])
            if extracted:
                date_from, date_to = extracted
                warnings.append("date_range_actual_missing_using_requested")
            else:
                warnings.append("date_range_requested_unparseable")

    # 4) date_start_requested + date_end_requested
    if date_from is None or date_to is None:
        start_req = rows.get("date_start_requested")
        end_req = rows.get("date_end_requested")
        if start_req and end_req:
            date_from = DATE_RE.findall(start_req)[0] if DATE_RE.findall(start_req) else None
            date_to = DATE_RE.findall(end_req)[0] if DATE_RE.findall(end_req) else None
            warnings.append("date_range_requested_from_start_end")

    # 4b) date_start + date_end (generic)
    if date_from is None or date_to is None:
        start_generic = rows.get("date_start")
        end_generic = rows.get("date_end")
        if start_generic and end_generic:
            date_from = DATE_RE.findall(start_generic)[0] if DATE_RE.findall(start_generic) else None
            date_to = DATE_RE.findall(end_generic)[0] if DATE_RE.findall(end_generic) else None
            warnings.append("date_range_generic_start_end")

    # 5) last resort: any line with 'actual' or 'requested' and two dates
    if date_from is None or date_to is None:
        for raw_line in content.splitlines():
            line = raw_line.lower()
            if "actual" in line or "requested" in line:
                extracted = extract_date_range_from_text(raw_line)
                if extracted:
                    date_from, date_to = extracted
                    warnings.append("date_range_fallback_line_scan")
                    break

    symbol = None
    for key in ("symbol(s)", "symbol"):
        if key in rows:
            value = rows[key].strip()
            if value:
                symbol = value
            break

    n_obs = None
    for key in ("n_observations", "n_obs", "observations"):
        if key in rows:
            match = re.search(r"\d+", rows[key])
            if match:
                n_obs = int(match.group(0))
            break

    if symbol is None or symbol == "":
        warnings.append("symbol_missing_or_empty")

    warnings_sorted = sorted(set(warnings))
    return ParsedRun(
        date_from=date_from,
        date_to=date_to,
        n_obs=n_obs,
        symbol=symbol if symbol else None,
    ), warnings_sorted


def is_iso_date(value: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def compare_dates(date_from: str, date_to: str) -> bool:
    try:
        d1 = date.fromisoformat(date_from)
        d2 = date.fromisoformat(date_to)
    except ValueError:
        return False
    return d1 <= d2


def list_run_ids(runs_root: Path) -> List[str]:
    if not runs_root.exists() or not runs_root.is_dir():
        return []
    run_ids = sorted([p.name for p in runs_root.iterdir() if p.is_dir()])
    return run_ids


def load_index_text(index_path: Path) -> str:
    try:
        return index_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def json_dumps_deterministic(payload: Dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
