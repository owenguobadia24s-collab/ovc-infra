#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

LEDGER_PATH = Path("docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl")
OVERLAY_PATH = Path("docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl")
TIMELINE_OUT = Path("docs/catalogs/OVC_DEVELOPMENT_TIMELINE_v0.2.md")
STATS_OUT = Path(".codex/_scratch/v0_2_timeline_stats.json")

CLASS_ORDER = ["A", "B", "C", "D", "E", "UNKNOWN"]

LEDGER_COMMIT_CANDIDATES = [
    ("commit.hash", ("commit", "hash")),
    ("commit_hash", ("commit_hash",)),
    ("hash", ("hash",)),
    ("sha", ("sha",)),
    ("commit", ("commit",)),
]
LEDGER_DATE_CANDIDATES = [
    ("commit.timestamp_utc", ("commit", "timestamp_utc")),
    ("commit.timestamp", ("commit", "timestamp")),
    ("commit.date", ("commit", "date")),
    ("timestamp_utc", ("timestamp_utc",)),
    ("timestamp", ("timestamp",)),
    ("date", ("date",)),
]
OVERLAY_COMMIT_CANDIDATES = [
    ("commit", ("commit",)),
    ("commit.hash", ("commit", "hash")),
    ("commit_hash", ("commit_hash",)),
    ("hash", ("hash",)),
    ("sha", ("sha",)),
]
OVERLAY_CLASSES_CANDIDATES = [
    ("classes", ("classes",)),
    ("class", ("class",)),
    ("classification", ("classification",)),
]
OVERLAY_UNKNOWN_CANDIDATES = [
    ("unknown", ("unknown",)),
    ("is_unknown", ("is_unknown",)),
]
MACRO_EPOCH_CANDIDATES = [
    ("macro_epoch_id", ("macro_epoch_id",)),
    ("macro_epoch", ("macro_epoch",)),
    ("epoch.macro_id", ("epoch", "macro_id")),
    ("epochs.macro", ("epochs", "macro")),
]
MICRO_EPOCH_CANDIDATES = [
    ("micro_epoch_id", ("micro_epoch_id",)),
    ("micro_epoch", ("micro_epoch",)),
    ("epoch.micro_id", ("epoch", "micro_id")),
    ("epochs.micro", ("epochs", "micro")),
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise RuntimeError(f"{path}:{line_no}: expected JSON object row")
            rows.append(row)
    return rows


def extract_by_path(row: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = row
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def is_commit_hash(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    v = value.strip()
    if len(v) < 7:
        return False
    return all(ch in "0123456789abcdefABCDEF" for ch in v)


def parse_date(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def detect_field(
    rows: list[dict[str, Any]],
    candidates: list[tuple[str, tuple[str, ...]]],
    validator,
    required: bool = True,
) -> tuple[str | None, tuple[str, ...] | None]:
    for label, path in candidates:
        values = [extract_by_path(row, path) for row in rows]
        if all(validator(v) for v in values):
            return label, path
    if required:
        labels = ", ".join(label for label, _ in candidates)
        raise RuntimeError(f"could not detect field from candidates: {labels}")
    return None, None


def normalize_classes(value: Any) -> list[str]:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = []
    out: list[str] = []
    for item in items:
        if item is None:
            continue
        text = str(item).strip().upper()
        if text:
            out.append(text)
    # Keep order stable while removing duplicates.
    dedup = list(dict.fromkeys(out))
    return dedup


def normalize_path(path: str) -> str:
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p


def top_prefix_for_path(path: str) -> str:
    p = normalize_path(path)
    if not p:
        return "/"
    if "/" not in p:
        return "/"
    first = p.split("/", 1)[0]
    return f"{first}/"


def extract_path_strings(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    paths_obj = row.get("paths")
    if isinstance(paths_obj, dict):
        for value in paths_obj.values():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        out.append(item)
                    elif isinstance(item, dict):
                        for k in ("from", "to", "src", "dst", "old", "new"):
                            v = item.get(k)
                            if isinstance(v, str):
                                out.append(v)
    return out


def normalize_directory_token(token: str) -> str:
    t = normalize_path(token)
    if not t or t == ".":
        return "/"
    if t == "/":
        return "/"
    if t.endswith("/"):
        return t
    return f"{t}/"


def extract_prefixes(row: dict[str, Any]) -> set[str]:
    prefixes: set[str] = set()
    for p in extract_path_strings(row):
        prefixes.add(top_prefix_for_path(p))
    if not prefixes:
        dirs = row.get("directories_touched")
        if isinstance(dirs, list):
            for d in dirs:
                if isinstance(d, str):
                    prefixes.add(normalize_directory_token(d))
    return prefixes


def contiguous_windows(indices: list[int]) -> list[tuple[int, int]]:
    if not indices:
        return []
    points = sorted(indices)
    windows: list[tuple[int, int]] = []
    start = points[0]
    prev = points[0]
    for idx in points[1:]:
        if idx == prev + 1:
            prev = idx
            continue
        windows.append((start, prev))
        start = idx
        prev = idx
    windows.append((start, prev))
    return windows


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def load_joined_records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ledger_rows = read_jsonl(LEDGER_PATH)
    overlay_rows = read_jsonl(OVERLAY_PATH)

    if not ledger_rows:
        raise RuntimeError(f"ledger has no rows: {LEDGER_PATH}")
    if not overlay_rows:
        raise RuntimeError(f"overlay has no rows: {OVERLAY_PATH}")

    ledger_commit_label, ledger_commit_path = detect_field(
        ledger_rows, LEDGER_COMMIT_CANDIDATES, is_commit_hash, required=True
    )
    ledger_date_label, ledger_date_path = detect_field(
        ledger_rows, LEDGER_DATE_CANDIDATES, lambda v: parse_date(v) is not None, required=True
    )
    overlay_commit_label, overlay_commit_path = detect_field(
        overlay_rows, OVERLAY_COMMIT_CANDIDATES, is_commit_hash, required=True
    )
    overlay_classes_label, overlay_classes_path = detect_field(
        overlay_rows,
        OVERLAY_CLASSES_CANDIDATES,
        lambda v: isinstance(v, (str, list, tuple, set)),
        required=True,
    )
    overlay_unknown_label, overlay_unknown_path = detect_field(
        overlay_rows,
        OVERLAY_UNKNOWN_CANDIDATES,
        lambda v: isinstance(v, (bool, int, float, str)),
        required=False,
    )
    macro_label, macro_path = detect_field(
        ledger_rows,
        MACRO_EPOCH_CANDIDATES,
        lambda v: v is not None and str(v).strip() != "",
        required=False,
    )
    micro_label, micro_path = detect_field(
        ledger_rows,
        MICRO_EPOCH_CANDIDATES,
        lambda v: v is not None and str(v).strip() != "",
        required=False,
    )

    if len(ledger_rows) != len(overlay_rows):
        raise RuntimeError(
            f"row-count mismatch: ledger={len(ledger_rows)} overlay={len(overlay_rows)}; cannot 1:1 join"
        )

    joined: list[dict[str, Any]] = []
    join_mismatches: list[dict[str, Any]] = []

    for idx, (lrow, orow) in enumerate(zip(ledger_rows, overlay_rows), start=1):
        lhash_raw = extract_by_path(lrow, ledger_commit_path or ())
        ohash_raw = extract_by_path(orow, overlay_commit_path or ())
        if not is_commit_hash(lhash_raw) or not is_commit_hash(ohash_raw):
            raise RuntimeError(f"invalid commit hash at row {idx}")
        lhash = str(lhash_raw).strip()
        ohash = str(ohash_raw).strip()
        if lhash != ohash:
            join_mismatches.append({"row": idx, "ledger": lhash, "overlay": ohash})
            continue

        dt = parse_date(extract_by_path(lrow, ledger_date_path or ()))
        if dt is None:
            raise RuntimeError(f"invalid ledger date at row {idx}")

        classes = normalize_classes(extract_by_path(orow, overlay_classes_path or ()))
        unknown_value = False
        if overlay_unknown_path is not None:
            raw_unknown = extract_by_path(orow, overlay_unknown_path)
            if isinstance(raw_unknown, bool):
                unknown_value = raw_unknown
            elif isinstance(raw_unknown, (int, float)):
                unknown_value = bool(raw_unknown)
            elif isinstance(raw_unknown, str):
                unknown_value = raw_unknown.strip().lower() in {"1", "true", "yes", "y"}

        if "UNKNOWN" in classes:
            unknown_value = True
        if unknown_value and "UNKNOWN" not in classes:
            classes.append("UNKNOWN")
        classes = list(dict.fromkeys(classes))

        joined.append(
            {
                "index": idx,
                "commit": lhash,
                "date": dt,
                "month": month_key(dt),
                "classes": classes,
                "unknown": bool(unknown_value),
                "ledger": lrow,
                "overlay": orow,
                "macro_epoch": str(extract_by_path(lrow, macro_path)).strip() if macro_path else None,
                "micro_epoch": str(extract_by_path(lrow, micro_path)).strip() if micro_path else None,
            }
        )

    if join_mismatches:
        preview = ", ".join(
            f"row {m['row']} ledger={m['ledger']} overlay={m['overlay']}" for m in join_mismatches[:5]
        )
        raise RuntimeError(
            f"hash order mismatch across ledger/overlay; strict 1:1 join failed ({len(join_mismatches)} mismatches): {preview}"
        )

    stats: dict[str, Any] = {
        "inputs": {"ledger": str(LEDGER_PATH), "overlay": str(OVERLAY_PATH)},
        "detected_fields": {
            "ledger_commit": ledger_commit_label,
            "ledger_date": ledger_date_label,
            "overlay_commit": overlay_commit_label,
            "overlay_classes": overlay_classes_label,
            "overlay_unknown": overlay_unknown_label,
            "ledger_macro_epoch": macro_label,
            "ledger_micro_epoch": micro_label,
        },
        "join_checks": {
            "ledger_rows": len(ledger_rows),
            "overlay_rows": len(overlay_rows),
            "join_mode": "strict_row_order_by_commit_hash",
            "hash_order_match": True,
            "mismatch_count": 0,
        },
    }
    return joined, stats


def build_timeline(joined: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    total = len(joined)
    first = joined[0]
    last = joined[-1]
    min_dt = min(r["date"] for r in joined)
    max_dt = max(r["date"] for r in joined)

    unknown_commits = [r for r in joined if r["unknown"]]
    unknown_count = len(unknown_commits)
    unknown_pct = (unknown_count / total) * 100 if total else 0.0

    unknown_prefix_counts: Counter[str] = Counter()
    for rec in unknown_commits:
        prefixes = extract_prefixes(rec["ledger"])
        for pref in prefixes:
            unknown_prefix_counts[pref] += 1

    per_month_class: dict[str, Counter[str]] = defaultdict(Counter)
    for rec in joined:
        month = rec["month"]
        present = set(rec["classes"])
        if rec["unknown"]:
            present.add("UNKNOWN")
        for cls in CLASS_ORDER:
            if cls in present:
                per_month_class[month][cls] += 1

    dir_touch_counts: Counter[str] = Counter()
    for rec in joined:
        for pref in extract_prefixes(rec["ledger"]):
            dir_touch_counts[pref] += 1

    pair_counts: Counter[tuple[str, str]] = Counter()
    pair_indices: dict[tuple[str, str], list[int]] = defaultdict(list)
    for rec in joined:
        class_set = set(rec["classes"])
        if rec["unknown"]:
            class_set.add("UNKNOWN")
        class_set = {c for c in class_set if c}
        if len(class_set) < 2:
            continue
        for pair in combinations(sorted(class_set), 2):
            pair_counts[pair] += 1
            pair_indices[pair].append(rec["index"])

    top_pairs = sorted(pair_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    highest_pair = top_pairs[0][0] if top_pairs else None
    highest_pair_count = top_pairs[0][1] if top_pairs else 0

    highest_windows: list[dict[str, Any]] = []
    if highest_pair is not None:
        windows = contiguous_windows(pair_indices[highest_pair])
        window_payloads: list[dict[str, Any]] = []
        for start, end in windows:
            members = joined[start - 1 : end]
            hashes = [r["commit"] for r in members]
            window_payloads.append(
                {
                    "start_index": start,
                    "end_index": end,
                    "length": end - start + 1,
                    "date_start": iso_z(members[0]["date"]),
                    "date_end": iso_z(members[-1]["date"]),
                    "hashes": hashes,
                }
            )
        highest_windows = sorted(window_payloads, key=lambda w: (-w["length"], w["start_index"]))[:5]

    macro_windows: list[dict[str, Any]] = []
    if all(r.get("macro_epoch") for r in joined):
        start = 0
        while start < total:
            current = joined[start]["macro_epoch"]
            end = start
            while end + 1 < total and joined[end + 1]["macro_epoch"] == current:
                end += 1
            members = joined[start : end + 1]
            macro_windows.append(
                {
                    "id": current,
                    "count": len(members),
                    "date_start": iso_z(members[0]["date"]),
                    "date_end": iso_z(members[-1]["date"]),
                    "commit_start": members[0]["commit"],
                    "commit_end": members[-1]["commit"],
                }
            )
            start = end + 1

    micro_windows: list[dict[str, Any]] = []
    if all(r.get("micro_epoch") for r in joined):
        start = 0
        while start < total:
            current = joined[start]["micro_epoch"]
            end = start
            while end + 1 < total and joined[end + 1]["micro_epoch"] == current:
                end += 1
            members = joined[start : end + 1]
            micro_windows.append(
                {
                    "id": current,
                    "count": len(members),
                    "date_start": iso_z(members[0]["date"]),
                    "date_end": iso_z(members[-1]["date"]),
                    "commit_start": members[0]["commit"],
                    "commit_end": members[-1]["commit"],
                }
            )
            start = end + 1

    monthly_windows: list[dict[str, Any]] = []
    by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in joined:
        by_month[rec["month"]].append(rec)
    for month in sorted(by_month):
        rows = by_month[month]
        monthly_windows.append(
            {
                "month": month,
                "count": len(rows),
                "date_start": iso_z(rows[0]["date"]),
                "date_end": iso_z(rows[-1]["date"]),
                "commit_start": rows[0]["commit"],
                "commit_end": rows[-1]["commit"],
            }
        )

    stats["coverage"] = {
        "total_commits": total,
        "start_commit": first["commit"],
        "end_commit": last["commit"],
        "min_date_utc": iso_z(min_dt),
        "max_date_utc": iso_z(max_dt),
        "unknown_count": unknown_count,
        "unknown_pct": round(unknown_pct, 3),
        "unknown_clusters_by_prefix": [
            {"prefix": prefix, "commit_count": count}
            for prefix, count in sorted(unknown_prefix_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
    }
    stats["frequency"] = {
        "per_month_by_class": {
            month: {cls: per_month_class[month].get(cls, 0) for cls in CLASS_ORDER}
            for month in sorted(per_month_class)
        },
        "top_level_directory_touch_counts": [
            {"prefix": prefix, "touch_count": count}
            for prefix, count in sorted(dir_touch_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
    }
    stats["overlap"] = {
        "top_pairs": [
            {"pair": list(pair), "count": count}
            for pair, count in top_pairs
        ],
        "highest_pair": list(highest_pair) if highest_pair else None,
        "highest_pair_count": highest_pair_count,
        "highest_pair_top_windows": highest_windows,
    }
    stats["derived_windows"] = {
        "source": (
            "ledger_epoch_fields"
            if macro_windows or micro_windows
            else "date_derived_month_time_windows"
        ),
        "macro_windows_count": len(macro_windows),
        "micro_windows_count": len(micro_windows),
        "monthly_windows_count": len(monthly_windows),
    }

    lines: list[str] = []
    lines.append("# OVC Development Timeline - v0.2")
    lines.append("")
    lines.append("## Source Artifacts")
    lines.append(f"- Ledger: `{LEDGER_PATH.as_posix()}`")
    lines.append(f"- Overlay: `{OVERLAY_PATH.as_posix()}`")
    lines.append("")
    lines.append("## Coverage")
    lines.append(f"- Total commits: `{total}`")
    lines.append(f"- Start commit (ledger first row): `{first['commit']}`")
    lines.append(f"- End commit (ledger last row): `{last['commit']}`")
    lines.append(f"- Date span (UTC): `{iso_z(min_dt)}` to `{iso_z(max_dt)}`")
    lines.append(f"- UNKNOWN commits: `{unknown_count}` / `{total}` ({unknown_pct:.1f}%)")
    lines.append("- Remaining UNKNOWN clusters by top prefix:")
    if unknown_prefix_counts:
        for prefix, count in sorted(unknown_prefix_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"  - `{prefix}`: `{count}` commit(s)")
    else:
        lines.append("  - `None`")
    lines.append("")
    lines.append("## Frequency Tables")
    lines.append("")
    lines.append("### Commits Per Month by Class")
    lines.append("Month | A | B | C | D | E | UNKNOWN")
    lines.append("---|---:|---:|---:|---:|---:|---:")
    for month in sorted(per_month_class):
        row = per_month_class[month]
        lines.append(
            f"{month} | {row.get('A', 0)} | {row.get('B', 0)} | {row.get('C', 0)} | "
            f"{row.get('D', 0)} | {row.get('E', 0)} | {row.get('UNKNOWN', 0)}"
        )
    lines.append("")
    lines.append("### Top-Level Directory Touch Counts")
    lines.append("Prefix | Commit Touch Count")
    lines.append("---|---:")
    if dir_touch_counts:
        for prefix, count in sorted(dir_touch_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"`{prefix}` | {count}")
    else:
        lines.append("`UNKNOWN` | 0")
    lines.append("")
    lines.append("## Derived Epochs / Time Windows")
    if macro_windows or micro_windows:
        lines.append("- Source: ledger epoch identifiers")
        if macro_windows:
            lines.append("")
            lines.append("### Macro Epoch Windows (from ledger)")
            lines.append("Macro Epoch | Commits | Date Start (UTC) | Date End (UTC) | First Commit | Last Commit")
            lines.append("---|---:|---|---|---|---")
            for w in macro_windows:
                lines.append(
                    f"`{w['id']}` | {w['count']} | `{w['date_start']}` | `{w['date_end']}` | "
                    f"`{w['commit_start']}` | `{w['commit_end']}`"
                )
        if micro_windows:
            lines.append("")
            lines.append("### Micro Epoch Windows (from ledger)")
            lines.append("Micro Epoch | Commits | Date Start (UTC) | Date End (UTC) | First Commit | Last Commit")
            lines.append("---|---:|---|---|---|---")
            for w in micro_windows:
                lines.append(
                    f"`{w['id']}` | {w['count']} | `{w['date_start']}` | `{w['date_end']}` | "
                    f"`{w['commit_start']}` | `{w['commit_end']}`"
                )
    else:
        lines.append("- Source: date-derived month windows (time windows, not ledger epochs)")
        lines.append("")
        lines.append("### Macro Time Windows by Month")
        lines.append("Month | Commits | Date Start (UTC) | Date End (UTC) | First Commit | Last Commit")
        lines.append("---|---:|---|---|---|---")
        for w in monthly_windows:
            lines.append(
                f"{w['month']} | {w['count']} | `{w['date_start']}` | `{w['date_end']}` | "
                f"`{w['commit_start']}` | `{w['commit_end']}`"
            )
    lines.append("")
    lines.append("## Overlap / Crossover")
    lines.append("")
    lines.append("### Top 10 Co-Occurring Class Pairs")
    lines.append("Pair | Commit Count")
    lines.append("---|---:")
    if top_pairs:
        for pair, count in top_pairs:
            lines.append(f"`{pair[0]}+{pair[1]}` | {count}")
    else:
        lines.append("`UNKNOWN` | 0")
    lines.append("")
    lines.append("### Top 5 Contiguous Windows for Highest-Overlap Pair")
    if highest_pair is None:
        lines.append("- Highest-overlap pair: `UNKNOWN` (no multi-label co-occurrence present)")
        lines.append("- Windows: `UNKNOWN`")
    else:
        lines.append(
            f"- Highest-overlap pair: `{highest_pair[0]}+{highest_pair[1]}` ({highest_pair_count} commit(s))"
        )
        if highest_windows:
            for idx, window in enumerate(highest_windows, start=1):
                hashes = window["hashes"][:10]
                extra = len(window["hashes"]) - len(hashes)
                hash_text = ", ".join(f"`{h}`" for h in hashes)
                if extra > 0:
                    hash_text += f", ... (+{extra} more)"
                lines.append(
                    f"- Window {idx}: indices {window['start_index']}-{window['end_index']}, "
                    f"date `{window['date_start']}` to `{window['date_end']}`, commits: {hash_text}"
                )
        else:
            lines.append("- Windows: `UNKNOWN`")
    lines.append("")
    lines.append("## Appendix: Commit Index")
    lines.append("Index | Commit | Date (UTC) | Classes")
    lines.append("---:|---|---|---")
    for rec in joined:
        class_text = ",".join(rec["classes"]) if rec["classes"] else "UNKNOWN"
        lines.append(f"{rec['index']} | `{rec['commit']}` | `{iso_z(rec['date'])}` | `{class_text}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    joined, stats = load_joined_records()
    timeline_text = build_timeline(joined, stats)
    TIMELINE_OUT.write_text(timeline_text, encoding="utf-8", newline="\n")
    STATS_OUT.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
