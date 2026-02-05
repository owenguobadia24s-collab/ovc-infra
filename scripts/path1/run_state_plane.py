#!/usr/bin/env python3
"""
Path 1 State Plane Evidence Runner
==================================
Generates per-day state plane trajectory artifacts from derived.v_ovc_state_plane_v0_2.
Observational only: no outcome joins, no scoring, no decision surfaces.
"""

import argparse
import csv
import json
import math
import os
import re
import struct
import sys
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATE_PLANE_VIEW = "derived.v_ovc_state_plane_v0_2"
OUTPUT_SUBDIR = "state_plane_v0_2"
SOURCE_VIEW_NAMES = [
    "derived.v_ovc_c1_features_v0_1",
    "derived.v_ovc_c2_features_v0_1",
    "derived.v_ovc_c3_features_v0_1",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ovc_ops.run_envelope_v0_1 import (  # noqa: E402
    get_git_state,
    seal_dir,
    write_run_json,
)


def validate_date(value: str, field_name: str) -> str:
    if not DATE_RE.match(value):
        raise ValueError(f"{field_name} must be YYYY-MM-DD, got: {value}")
    return value


def resolve_dsn() -> str:
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not dsn:
        raise SystemExit("Missing DATABASE_URL or NEON_DSN environment variable")
    return dsn


def get_connection():
    return psycopg2.connect(resolve_dsn())


def iter_dates(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def next_run_id(runs_root: Path) -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"p1_{today}_"
    existing = []
    if runs_root.exists():
        for entry in runs_root.iterdir():
            if entry.is_dir() and entry.name.startswith(prefix):
                parts = entry.name.split("_")
                if len(parts) >= 3 and parts[2].isdigit():
                    existing.append(int(parts[2]))
    seq = max(existing, default=0) + 1
    return f"{prefix}{seq:03d}"


def fetch_state_plane_blocks(conn, symbol: str, date_ny: str) -> List[Dict]:
    sql = f"""
        SELECT
            block_id,
            sym,
            date_ny,
            block2h,
            bar_close_ms,
            x_energy,
            y_shift,
            quadrant_id,
            quadrant_name,
            threshold_pack_id,
            threshold_pack_version,
            threshold_pack_hash
        FROM {STATE_PLANE_VIEW}
        WHERE sym = %s
          AND date_ny = %s
        ORDER BY bar_close_ms;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (symbol, date_ny))
        return list(cur.fetchall())


def fetch_thresholds(conn, pack_id: str, pack_version: int) -> Tuple[Optional[float], Optional[float]]:
    sql = """
        SELECT config_json
        FROM ovc_cfg.threshold_pack
        WHERE pack_id = %s AND pack_version = %s;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (pack_id, pack_version))
        row = cur.fetchone()
    if not row:
        return None, None
    cfg = row["config_json"]
    thresholds = cfg.get("thresholds") if isinstance(cfg, dict) else None
    if not isinstance(thresholds, dict):
        return None, None
    return thresholds.get("E_hi"), thresholds.get("S_hi")


def format_float(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def compute_metrics(points: List[Dict]) -> Dict:
    path_length = 0.0
    valid_point_count = 0
    first_point = None
    last_point = None
    prev_point = None

    for p in points:
        x_val = p["x_energy"]
        y_val = p["y_shift"]
        if x_val is None or y_val is None:
            prev_point = None
            continue
        valid_point_count += 1
        current = (x_val, y_val)
        if first_point is None:
            first_point = current
        last_point = current
        if prev_point is not None:
            path_length += math.sqrt(
                (current[0] - prev_point[0]) ** 2 + (current[1] - prev_point[1]) ** 2
            )
        prev_point = current

    net_displacement = None
    if valid_point_count >= 2 and first_point is not None and last_point is not None:
        net_displacement = math.sqrt(
            (last_point[0] - first_point[0]) ** 2 + (last_point[1] - first_point[1]) ** 2
        )

    efficiency = None
    if net_displacement is not None and path_length > 0:
        efficiency = net_displacement / path_length

    jump_count = sum(1 for p in points if p.get("quadrant_id") in ("Q3", "Q4"))
    quadrant_string = " ".join(p.get("quadrant_id") or "NA" for p in points)

    return {
        "block_count": len(points),
        "valid_point_count": valid_point_count,
        "path_length": path_length if valid_point_count else None,
        "net_displacement": net_displacement,
        "efficiency": efficiency,
        "jump_count": jump_count,
        "quadrant_string": quadrant_string,
    }


def write_trajectory_csv(points: List[Dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "block2h",
            "block_id",
            "x_energy",
            "y_shift",
            "quadrant_id",
            "quadrant_name",
        ])
        for p in points:
            writer.writerow([
                p.get("block2h"),
                p.get("block_id"),
                format_float(p.get("x_energy")),
                format_float(p.get("y_shift")),
                p.get("quadrant_id"),
                p.get("quadrant_name"),
            ])


def write_quadrant_string(text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")


def write_metrics_json(metrics: Dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")


def set_pixel(pixels: bytearray, width: int, height: int, x: int, y: int,
              color: Tuple[int, int, int]) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    idx = (y * width + x) * 3
    pixels[idx:idx + 3] = bytes(color)


def draw_line(pixels: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int,
              color: Tuple[int, int, int]) -> None:
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if 0 <= x < width and 0 <= y < height:
            set_pixel(pixels, width, height, x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def draw_point(pixels: bytearray, width: int, height: int, x: int, y: int,
               color: Tuple[int, int, int]) -> None:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            px = x + dx
            py = y + dy
            if 0 <= px < width and 0 <= py < height:
                set_pixel(pixels, width, height, px, py, color)


def write_png(path: Path, width: int, height: int, pixels: bytearray) -> None:
    # Minimal PNG writer to avoid external plotting dependencies.
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        row_start = y * stride
        raw.extend(pixels[row_start:row_start + stride])
    compressed = zlib.compress(raw, level=9)

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return length + chunk_type + data + struct.pack(">I", crc)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = (
        header +
        chunk(b"IHDR", ihdr) +
        chunk(b"IDAT", compressed) +
        chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def render_trajectory_png(points: List[Dict], output_path: Path,
                          e_hi: Optional[float], s_hi: Optional[float]) -> None:
    width, height = 640, 640
    margin = 50
    pixels = bytearray([255, 255, 255] * width * height)

    def to_pixel(x: float, y: float) -> Tuple[int, int]:
        px = int(round(margin + x * (width - 2 * margin)))
        norm_y = (y + 1.0) / 2.0
        py = int(round(margin + (1.0 - norm_y) * (height - 2 * margin)))
        return px, py

    border_color = (200, 200, 200)
    axis_color = (180, 180, 180)
    threshold_color = (220, 220, 220)
    path_color = (30, 110, 200)
    point_color = (10, 10, 10)

    draw_line(pixels, width, height, margin, margin, width - margin, margin, border_color)
    draw_line(pixels, width, height, margin, height - margin, width - margin, height - margin, border_color)
    draw_line(pixels, width, height, margin, margin, margin, height - margin, border_color)
    draw_line(pixels, width, height, width - margin, margin, width - margin, height - margin, border_color)

    y_zero = to_pixel(0.0, 0.0)[1]
    draw_line(pixels, width, height, margin, y_zero, width - margin, y_zero, axis_color)

    if e_hi is not None:
        x_e, _ = to_pixel(e_hi, 0.0)
        draw_line(pixels, width, height, x_e, margin, x_e, height - margin, threshold_color)
    if s_hi is not None:
        _, y_pos = to_pixel(0.0, s_hi)
        _, y_neg = to_pixel(0.0, -s_hi)
        draw_line(pixels, width, height, margin, y_pos, width - margin, y_pos, threshold_color)
        draw_line(pixels, width, height, margin, y_neg, width - margin, y_neg, threshold_color)

    prev_px = None
    for p in points:
        x_val = p.get("x_energy")
        y_val = p.get("y_shift")
        if x_val is None or y_val is None:
            prev_px = None
            continue
        px = to_pixel(x_val, y_val)
        if prev_px is not None:
            draw_line(pixels, width, height, prev_px[0], prev_px[1], px[0], px[1], path_color)
        draw_point(pixels, width, height, px[0], px[1], point_color)
        prev_px = px

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_png(output_path, width, height, pixels)


def write_run_md(
    output_dir: Path,
    run_id: str,
    symbol: str,
    date_ny: str,
    generated_at: str,
    metrics: Dict,
    pack_id: Optional[str],
    pack_version: Optional[int],
    pack_hash: Optional[str],
    command_text: str,
) -> None:
    run_md = f"""# Path 1 State Plane Run: {run_id}

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `{run_id}` |
| `date_ny` | `{date_ny}` |
| `symbol` | `{symbol}` |
| `generated_at` | `{generated_at}` |
| `block_count` | `{metrics.get('block_count')}` |
| `valid_point_count` | `{metrics.get('valid_point_count')}` |
| `threshold_pack_id` | `{pack_id}` |
| `threshold_pack_version` | `{pack_version}` |
| `threshold_pack_hash` | `{pack_hash}` |

---

## Invariants Reminder

1. Observational only (no outcomes or decision surfaces).
2. Canonical inputs only (C1/C2/C3 views).
3. Thresholds and weights are versioned in the registry.

---

## Source

- View: `{STATE_PLANE_VIEW}`
- Canonical views: {", ".join(SOURCE_VIEW_NAMES)}

---

## Commands Executed

```bash
{command_text}
```

---

## Artifacts Generated

| File | Description |
|------|-------------|
| `outputs/{OUTPUT_SUBDIR}/trajectory.csv` | Block-ordered coordinates (A-L) |
| `outputs/{OUTPUT_SUBDIR}/trajectory.png` | State plane trajectory plot |
| `outputs/{OUTPUT_SUBDIR}/quadrant_string.txt` | Quadrant sequence |
| `outputs/{OUTPUT_SUBDIR}/path_metrics.json` | Path metrics summary |

---

## Execution Log

```
Run executed: {generated_at}
Output location: {output_dir}
```
"""
    (output_dir / "RUN.md").write_text(run_md, encoding="utf-8")


def run_for_date(conn, repo_root: Path, symbol: str, date_ny: str, run_id: Optional[str]) -> None:
    points = fetch_state_plane_blocks(conn, symbol, date_ny)
    if not points:
        print(f"WARNING: No rows for {symbol} on {date_ny}")
        return

    if run_id is None:
        run_id = next_run_id(repo_root / "reports" / "path1" / "evidence" / "runs")

    run_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / run_id
    output_dir = run_dir / "outputs" / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = compute_metrics(points)
    quadrant_string = metrics["quadrant_string"]

    pack_id = points[0].get("threshold_pack_id")
    pack_version = points[0].get("threshold_pack_version")
    pack_hash = points[0].get("threshold_pack_hash")
    e_hi, s_hi = (None, None)
    if pack_id and pack_version is not None:
        e_hi, s_hi = fetch_thresholds(conn, pack_id, pack_version)

    write_trajectory_csv(points, output_dir / "trajectory.csv")
    write_quadrant_string(quadrant_string, output_dir / "quadrant_string.txt")
    write_metrics_json(metrics, output_dir / "path_metrics.json")
    render_trajectory_png(points, output_dir / "trajectory.png", e_hi, s_hi)

    generated_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    command_text = (
        f"python scripts/path1/run_state_plane.py --symbol {symbol} --date {date_ny}"
    )
    write_run_md(
        run_dir,
        run_id,
        symbol,
        date_ny,
        generated_at,
        metrics,
        pack_id,
        pack_version,
        pack_hash,
        command_text,
    )

    git_commit, working_tree_state = get_git_state()
    outputs = [
        "RUN.md",
        f"outputs/{OUTPUT_SUBDIR}/trajectory.csv",
        f"outputs/{OUTPUT_SUBDIR}/trajectory.png",
        f"outputs/{OUTPUT_SUBDIR}/quadrant_string.txt",
        f"outputs/{OUTPUT_SUBDIR}/path_metrics.json",
        "run.json",
        "manifest.json",
        "MANIFEST.sha256",
    ]
    run_json_payload = {
        "run_id": run_id,
        "created_utc": generated_at,
        "run_type": "op_run",
        "option": "D",
        "operation_id": "OP-D07",
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "inputs": {
            "symbol": symbol,
            "date_ny": date_ny,
        },
        "outputs": outputs,
    }
    write_run_json(run_dir, run_json_payload)
    seal_dir(
        run_dir,
        [
            "RUN.md",
            f"outputs/{OUTPUT_SUBDIR}/trajectory.csv",
            f"outputs/{OUTPUT_SUBDIR}/trajectory.png",
            f"outputs/{OUTPUT_SUBDIR}/quadrant_string.txt",
            f"outputs/{OUTPUT_SUBDIR}/path_metrics.json",
            "run.json",
        ],
    )

    print(f"Run complete: {run_id} ({symbol} {date_ny})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Path 1 state plane artifacts")
    parser.add_argument("--symbol", required=True, help="Symbol (e.g., GBPUSD)")
    parser.add_argument("--date", help="Single date (YYYY-MM-DD)")
    parser.add_argument("--start-date", dest="start_date", help="Range start (YYYY-MM-DD)")
    parser.add_argument("--end-date", dest="end_date", help="Range end (YYYY-MM-DD)")
    parser.add_argument("--run-id", dest="run_id", help="Optional run_id (single-date only)")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    args = parser.parse_args()

    if args.date:
        validate_date(args.date, "--date")
        if args.start_date or args.end_date:
            raise SystemExit("Use --date or --start-date/--end-date, not both")
        date_list = [args.date]
    else:
        if not args.start_date or not args.end_date:
            raise SystemExit("Provide --date or both --start-date and --end-date")
        validate_date(args.start_date, "--start-date")
        validate_date(args.end_date, "--end-date")
        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        if start > end:
            raise SystemExit("--start-date must be <= --end-date")
        date_list = [d.strftime("%Y-%m-%d") for d in iter_dates(start, end)]
        if args.run_id:
            raise SystemExit("--run-id is only supported for single-date runs")

    repo_root = Path(args.repo_root).resolve()
    with get_connection() as conn:
        for date_ny in date_list:
            run_for_date(conn, repo_root, args.symbol, date_ny, args.run_id)


if __name__ == "__main__":
    main()
