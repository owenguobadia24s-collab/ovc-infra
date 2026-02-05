#!/usr/bin/env python3
"""
Phase 2.1 — System Health Renderer v0.1

Presentation-only renderer for OPERATION_STATUS_TABLE_v0_1.json.
Produces a one-glance report + summary and writes an evidence envelope.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path


RUNS_DIR = Path(".codex/RUNS")
STATUS_FILENAME = "OPERATION_STATUS_TABLE_v0_1.json"
REGISTRY_FILENAME = "RUN_REGISTRY_v0_1.jsonl"
DRIFT_FILENAME = "DRIFT_SIGNALS_v0_1.json"
OPTION_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "QA": 4}


def utcnow_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def make_run_id(tag: str) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d__%H%M%S")
    return f"{ts}__{tag}"


def build_manifest(output_dir: Path, file_names: list[str]) -> None:
    manifest_entries = []
    sha_lines = []

    for name in sorted(file_names):
        fpath = output_dir / name
        if not fpath.is_file():
            continue
        h = sha256_file(fpath)
        size = fpath.stat().st_size
        manifest_entries.append({
            "relpath": name,
            "bytes": size,
            "sha256": h,
        })
        sha_lines.append(f"{h}  {name}")

    manifest_json_path = output_dir / "manifest.json"
    manifest_json_bytes = json.dumps(manifest_entries, indent=2, sort_keys=False).encode("utf-8") + b"\n"
    manifest_json_path.write_bytes(manifest_json_bytes)

    mj_hash = sha256_bytes(manifest_json_bytes)
    sha_lines.append(f"{mj_hash}  manifest.json")

    all_lines = "\n".join(sorted(sha_lines)) + "\n"
    root_hash = sha256_bytes(all_lines.encode("utf-8"))
    sha_lines.append(f"ROOT_SHA256  {root_hash}")

    manifest_sha_path = output_dir / "MANIFEST.sha256"
    manifest_sha_path.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")


def find_latest_status_table(runs_dir: Path) -> Path | None:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "op_status_table_build" in child.name:
            status_path = child / STATUS_FILENAME
            if status_path.is_file():
                candidates.append(status_path)
    return candidates[-1] if candidates else None


def find_latest_registry(runs_dir: Path) -> Path | None:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "run_registry_build" in child.name:
            jsonl = child / REGISTRY_FILENAME
            if jsonl.is_file():
                candidates.append(jsonl)
    return candidates[-1] if candidates else None


def find_latest_drift_signals(runs_dir: Path) -> Path | None:
    candidates = []
    for child in sorted(runs_dir.iterdir()):
        if child.is_dir() and "drift_signals_build" in child.name:
            drift_path = child / DRIFT_FILENAME
            if drift_path.is_file():
                candidates.append(drift_path)
    return candidates[-1] if candidates else None


def load_status_records(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry_records(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def build_registry_index(records: list[dict]) -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for rec in records:
        if not rec.get("has_run_json"):
            continue
        op_id = rec.get("operation_id")
        run_id = rec.get("run_id")
        if not op_id or not run_id:
            continue
        key = (op_id, run_id)
        current = index.get(key)
        if current is None:
            index[key] = rec
            continue
        current_key = (current.get("created_utc") or "", current.get("run_key") or "")
        new_key = (rec.get("created_utc") or "", rec.get("run_key") or "")
        if new_key > current_key:
            index[key] = rec
    return index


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "- (none)"
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def limit_list(items: list, max_list: int) -> tuple[list, bool]:
    if len(items) > max_list:
        return items[:max_list], True
    return items, False


def observed_sort_key(rec: dict) -> tuple:
    option = rec.get("option")
    opt_rank = OPTION_ORDER.get(option, 99)
    staleness = rec.get("staleness_days")
    staleness_none = 1 if staleness is None else 0
    staleness_val = -staleness if staleness is not None else 0
    return (opt_rank, staleness_none, staleness_val, rec.get("operation_id") or "")


def stale_sort_key(rec: dict) -> tuple:
    staleness = rec.get("staleness_days") or 0
    return (-staleness, rec.get("operation_id") or "")


def format_reasons(reasons: list | None) -> str:
    if not reasons:
        return ""
    return ", ".join([str(r) for r in reasons if r])


def format_json_value(value: object) -> str:
    return json.dumps(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Phase 2.1 system health overview")
    parser.add_argument("--stale-days", type=int, default=2, help="Stale threshold in days (default: 2)")
    parser.add_argument("--max-list", type=int, default=20, help="Max rows per list (default: 20)")
    parser.add_argument("--show-legacy", action="store_true", help="Show legacy-only list")
    parser.add_argument("--show-unobserved", action="store_true", help="Show unobserved list")
    args = parser.parse_args()

    if not RUNS_DIR.is_dir():
        print(f"ERROR: {RUNS_DIR} not found.", file=sys.stderr)
        return 1

    status_path = find_latest_status_table(RUNS_DIR)
    if status_path is None:
        print("ERROR: No OPERATION_STATUS_TABLE_v0_1.json found.", file=sys.stderr)
        return 1

    status_records = load_status_records(status_path)

    registry_path = find_latest_registry(RUNS_DIR)
    registry_records = []
    if registry_path is not None:
        registry_records = load_registry_records(registry_path)
    registry_index = build_registry_index(registry_records)

    drift_path = find_latest_drift_signals(RUNS_DIR)
    drift_summary = None
    drift_signals_missing = False
    if drift_path is not None:
        try:
            drift_payload = json.loads(drift_path.read_text(encoding="utf-8"))
            drift_summary = drift_payload.get("system_drift")
        except Exception:
            drift_path = None
    if drift_path is None or drift_summary is None:
        drift_signals_missing = True

    enriched_records = []
    for rec in status_records:
        enriched = dict(rec)
        op_id = rec.get("operation_id")
        last_run_id = rec.get("last_run_id")
        last_run_root = None
        if op_id and last_run_id:
            match = registry_index.get((op_id, last_run_id))
            if match:
                last_run_root = match.get("run_root")
        enriched["last_run_root"] = last_run_root
        enriched_records.append(enriched)

    observed = [r for r in enriched_records if r.get("run_evidence_state") == "OBSERVED"]
    legacy_only = [r for r in enriched_records if r.get("run_evidence_state") == "LEGACY_ONLY"]
    unobserved = [r for r in enriched_records if r.get("run_evidence_state") == "UNOBSERVED"]
    stale = [
        r for r in observed
        if r.get("staleness_days") is not None and r.get("staleness_days") >= args.stale_days
    ]
    drifting = [r for r in enriched_records if r.get("op_drift") is True]
    below_c3 = [
        r for r in enriched_records
        if "coverage level < C3" in (r.get("warnings") or [])
        or r.get("coverage_level") in {"C0", "C1", "C2"}
    ]

    observed_sorted = sorted(observed, key=observed_sort_key)
    stale_sorted = sorted(stale, key=stale_sort_key)
    legacy_sorted = sorted(legacy_only, key=lambda r: r.get("operation_id") or "")
    unobserved_sorted = sorted(unobserved, key=lambda r: r.get("operation_id") or "")
    below_c3_sorted = sorted(below_c3, key=lambda r: r.get("operation_id") or "")
    drifting_sorted = sorted(
        drifting,
        key=lambda r: (OPTION_ORDER.get(r.get("option"), 99), r.get("operation_id") or ""),
    )

    observed_list, observed_truncated = limit_list(observed_sorted, args.max_list)
    stale_list, stale_truncated = limit_list(stale_sorted, args.max_list)
    legacy_list, legacy_truncated = limit_list(legacy_sorted, args.max_list)
    unobserved_list, unobserved_truncated = limit_list(unobserved_sorted, args.max_list)
    below_c3_list, below_c3_truncated = limit_list(below_c3_sorted, args.max_list)
    drifting_list, drifting_truncated = limit_list(drifting_sorted, args.max_list)

    report_lines = []
    report_lines.append("# System Health Report v0.1")
    report_lines.append("")
    report_lines.append(f"- generated_utc: `{utcnow_iso()}`")
    report_lines.append(f"- stale_threshold_days: `{args.stale_days}`")
    report_lines.append(f"- status_table: `{status_path}`")
    if registry_path is not None:
        report_lines.append(f"- registry: `{registry_path}`")
    if drift_path is not None:
        report_lines.append(f"- drift_signals: `{drift_path}`")
    report_lines.append("")
    report_lines.append("## System Drift Summary")
    report_lines.append("")
    if drift_signals_missing:
        report_lines.append("- drift_signals_missing")
    else:
        report_lines.append(f"- canon_dirty: `{format_json_value(drift_summary.get('canon_dirty'))}`")
        report_lines.append(f"- schema_drift: `{format_json_value(drift_summary.get('schema_drift'))}`")
        report_lines.append(f"- threshold_drift: `{format_json_value(drift_summary.get('threshold_drift'))}`")
    report_lines.append("")
    report_lines.append("## Counts")
    report_lines.append("")
    report_lines.append(f"- total_ops: **{len(enriched_records)}**")
    report_lines.append(f"- observed: **{len(observed)}**")
    report_lines.append(f"- stale: **{len(stale)}**")
    report_lines.append(f"- drifting: **{len(drifting)}**")
    report_lines.append(f"- legacy_only: **{len(legacy_only)}**")
    report_lines.append(f"- unobserved: **{len(unobserved)}**")
    report_lines.append(f"- coverage_below_c3: **{len(below_c3)}**")
    report_lines.append("")

    report_lines.append("## Observed")
    report_lines.append("")
    observed_rows = []
    for r in observed_list:
        observed_rows.append([
            r.get("operation_id") or "",
            r.get("option") or "",
            r.get("last_run_id") or "",
            r.get("last_run_root") or "",
            str(r.get("staleness_days")) if r.get("staleness_days") is not None else "",
            r.get("manifest_state") or "",
        ])
    report_lines.append(render_table(
        ["operation_id", "option", "last_run_id", "run_root", "staleness_days", "manifest_state"],
        observed_rows,
    ))
    if observed_truncated:
        report_lines.append("")
        report_lines.append(f"- truncated: showing first {args.max_list} of {len(observed)}")
    report_lines.append("")

    report_lines.append("## Stale")
    report_lines.append("")
    stale_rows = []
    for r in stale_list:
        stale_rows.append([
            r.get("operation_id") or "",
            r.get("option") or "",
            r.get("last_run_id") or "",
            r.get("last_run_root") or "",
            str(r.get("staleness_days")) if r.get("staleness_days") is not None else "",
            r.get("manifest_state") or "",
        ])
    report_lines.append(render_table(
        ["operation_id", "option", "last_run_id", "run_root", "staleness_days", "manifest_state"],
        stale_rows,
    ))
    if stale_truncated:
        report_lines.append("")
        report_lines.append(f"- truncated: showing first {args.max_list} of {len(stale)}")
    report_lines.append("")

    report_lines.append("## Drifting")
    report_lines.append("")
    drifting_rows = []
    for r in drifting_list:
        drifting_rows.append([
            r.get("operation_id") or "",
            r.get("option") or "",
            format_reasons(r.get("op_drift_reasons")),
            r.get("last_run_id") or "",
            str(r.get("staleness_days")) if r.get("staleness_days") is not None else "",
        ])
    report_lines.append(render_table(
        ["operation_id", "option", "op_drift_reasons", "last_run_id", "staleness_days"],
        drifting_rows,
    ))
    if drifting_truncated:
        report_lines.append("")
        report_lines.append(f"- truncated: showing first {args.max_list} of {len(drifting)}")
    report_lines.append("")

    report_lines.append("## Legacy Only")
    report_lines.append("")
    report_lines.append(f"- count: **{len(legacy_only)}**")
    if args.show_legacy:
        legacy_rows = []
        for r in legacy_list:
            legacy_rows.append([
                r.get("operation_id") or "",
                r.get("option") or "",
                r.get("coverage_level") or "",
            ])
        report_lines.append("")
        report_lines.append(render_table(
            ["operation_id", "option", "coverage_level"],
            legacy_rows,
        ))
        if legacy_truncated:
            report_lines.append("")
            report_lines.append(f"- truncated: showing first {args.max_list} of {len(legacy_only)}")
    report_lines.append("")

    report_lines.append("## Unobserved")
    report_lines.append("")
    report_lines.append(f"- count: **{len(unobserved)}**")
    if args.show_unobserved:
        unobserved_rows = []
        for r in unobserved_list:
            unobserved_rows.append([
                r.get("operation_id") or "",
                r.get("option") or "",
                r.get("coverage_level") or "",
            ])
        report_lines.append("")
        report_lines.append(render_table(
            ["operation_id", "option", "coverage_level"],
            unobserved_rows,
        ))
        if unobserved_truncated:
            report_lines.append("")
            report_lines.append(f"- truncated: showing first {args.max_list} of {len(unobserved)}")
    report_lines.append("")

    report_lines.append("## Coverage Below C3")
    report_lines.append("")
    report_lines.append(f"- count: **{len(below_c3)}**")
    below_rows = []
    for r in below_c3_list:
        below_rows.append([
            r.get("operation_id") or "",
            r.get("option") or "",
            r.get("coverage_level") or "",
        ])
    report_lines.append("")
    report_lines.append(render_table(
        ["operation_id", "option", "coverage_level"],
        below_rows,
    ))
    if below_c3_truncated:
        report_lines.append("")
        report_lines.append(f"- truncated: showing first {args.max_list} of {len(below_c3)}")
    report_lines.append("")

    report_text = "\n".join(report_lines)

    run_id = make_run_id("system_health_render")
    output_dir = RUNS_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    report_path = output_dir / "SYSTEM_HEALTH_REPORT_v0_1.md"
    report_path.write_text(report_text + "\n", encoding="utf-8")

    summary = {
        "generated_utc": utcnow_iso(),
        "stale_threshold_days": args.stale_days,
        "max_list": args.max_list,
        "counts": {
            "total_ops": len(enriched_records),
            "observed": len(observed),
            "stale": len(stale),
            "drifting": len(drifting),
            "legacy_only": len(legacy_only),
            "unobserved": len(unobserved),
            "coverage_below_c3": len(below_c3),
        },
        "observed": observed_list,
        "stale": stale_list,
        "legacy_only": legacy_list if args.show_legacy else [],
        "unobserved": unobserved_list if args.show_unobserved else [],
        "coverage_below_c3": below_c3_list,
        "drifting": drifting_list,
        "drifting_ops": drifting_list,
        "truncated": {
            "observed": observed_truncated,
            "stale": stale_truncated,
            "drifting": drifting_truncated,
            "legacy_only": legacy_truncated if args.show_legacy else False,
            "unobserved": unobserved_truncated if args.show_unobserved else False,
            "coverage_below_c3": below_c3_truncated,
        },
        "system_drift": drift_summary if not drift_signals_missing else {"drift_signals_missing": True},
        "input_sources": {
            "status_table": str(status_path),
            "registry": str(registry_path) if registry_path is not None else None,
            "drift_signals": str(drift_path) if drift_path is not None else None,
        },
    }

    summary_path = output_dir / "SYSTEM_HEALTH_SUMMARY_v0_1.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    git_commit = None
    working_tree_state = None
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        status_out = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        working_tree_state = "clean" if status_out == "" else "dirty"
    except Exception:
        pass

    run_json_payload = {
        "run_id": run_id,
        "created_utc": utcnow_iso(),
        "run_type": "system_health_render",
        "option": "QA",
        "operation_id": None,
        "git_commit": git_commit,
        "working_tree_state": working_tree_state,
        "input_sources": {
            "status_table": str(status_path),
            "registry": str(registry_path) if registry_path is not None else None,
            "drift_signals": str(drift_path) if drift_path is not None else None,
        },
        "outputs": [
            "SYSTEM_HEALTH_REPORT_v0_1.md",
            "SYSTEM_HEALTH_SUMMARY_v0_1.json",
            "run.json",
            "manifest.json",
            "MANIFEST.sha256",
        ],
    }
    run_json_path = output_dir / "run.json"
    run_json_path.write_text(json.dumps(run_json_payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    build_manifest(output_dir, [
        "SYSTEM_HEALTH_REPORT_v0_1.md",
        "SYSTEM_HEALTH_SUMMARY_v0_1.json",
        "run.json",
    ])

    print(report_text)
    print("")
    print(f"RUN_FOLDER: {output_dir}")
    print(
        "COUNTS | observed={observed} stale={stale} legacy_only={legacy_only} "
        "unobserved={unobserved} below_c3={coverage_below_c3} drifting={drifting}".format(**summary["counts"])
    )
    if drift_signals_missing:
        print("SYSTEM_DRIFT | drift_signals_missing")
    else:
        print(
            "SYSTEM_DRIFT | canon_dirty={canon_dirty} schema_drift={schema_drift} "
            "threshold_drift={threshold_drift}".format(
                canon_dirty=format_json_value(drift_summary.get("canon_dirty")),
                schema_drift=format_json_value(drift_summary.get("schema_drift")),
                threshold_drift=format_json_value(drift_summary.get("threshold_drift")),
            )
        )
    preview_count = min(5, len(observed_sorted))
    print(f"OBSERVED (first {preview_count}):")
    for row in observed_sorted[:preview_count]:
        print(
            f"- {row.get('operation_id')} {row.get('last_run_id')} "
            f"{row.get('last_run_root') or ''} staleness={row.get('staleness_days')} "
            f"manifest={row.get('manifest_state')}"
        )
    drift_preview = min(5, len(drifting_sorted))
    print(f"DRIFTING (first {drift_preview}):")
    for row in drifting_sorted[:drift_preview]:
        print(
            f"- {row.get('operation_id')} {format_reasons(row.get('op_drift_reasons'))} "
            f"last_run={row.get('last_run_id')} staleness={row.get('staleness_days')}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
