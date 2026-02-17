#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_NAME = "cartographer.py"
TOOL_VERSION = "0.1"
DEFAULT_RULES_PATH = "docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json"
DEFAULT_STATE_PATH = "scripts/repo_cartographer/cartographer_state.json"
DEFAULT_LEDGER_PATH = "docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl"
ARTIFACTS_DIR = "artifacts/repo_cartographer"

CONTENT_ARTIFACTS = [
    "REPO_FILE_INDEX_v0.1.jsonl",
    "REPO_FILE_CLASSIFICATION_v0.1.jsonl",
    "MODULE_OWNERSHIP_SUMMARY_v0.1.md",
    "BORDERLANDS_PRESSURE_REPORT_v0.1.md",
    "UNTRACKED_VISIBLE_REPORT_v0.1.md",
    "MOVE_PLAN_PROPOSED_v0.1.json",
]


class CartographerError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Utility functions (sentinel pattern)
# ---------------------------------------------------------------------------

def run_git(repo_root: Path, args: list[str], check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed"
        raise CartographerError(detail)
    return proc.stdout


def run_git_bytes(repo_root: Path, args: list[str], check: bool = True) -> bytes:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip() or f"git {' '.join(args)} failed"
        raise CartographerError(detail)
    return proc.stdout


def get_repo_root() -> Path:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "could not resolve repository root"
        raise CartographerError(detail)
    root = proc.stdout.strip()
    if not root:
        raise CartographerError("could not resolve repository root")
    return Path(root)


def normalize_path(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.lstrip("/")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def relpath_posix(path: Path, repo_root: Path) -> str:
    resolved_path = path.resolve()
    resolved_root = repo_root.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def resolve_repo_path(path_text: str, repo_root: Path) -> Path:
    candidate = Path(path_text)
    if candidate.is_absolute():
        return candidate.resolve()
    return (repo_root / candidate).resolve()


def serialize_json_pretty(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def serialize_jsonl_line(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialize_jsonl(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    lines = [serialize_jsonl_line(row) for row in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Git enumeration
# ---------------------------------------------------------------------------

def enumerate_tracked_files(repo_root: Path) -> list[str]:
    raw = run_git_bytes(repo_root, ["ls-files", "-z"])
    if not raw:
        return []
    parts = raw.split(b"\x00")
    paths = [normalize_path(p.decode("utf-8", errors="replace")) for p in parts if p]
    return sorted(set(paths))


def enumerate_untracked_visible(repo_root: Path) -> list[str]:
    raw = run_git_bytes(repo_root, ["ls-files", "-z", "--others", "--exclude-standard"])
    if not raw:
        return []
    parts = raw.split(b"\x00")
    paths = [normalize_path(p.decode("utf-8", errors="replace")) for p in parts if p]
    return sorted(set(paths))


def get_head_commit(repo_root: Path) -> str:
    return run_git(repo_root, ["rev-parse", "HEAD"]).strip()


def get_file_size_tracked(repo_root: Path, path: str) -> tuple[int | None, list[str]]:
    try:
        raw = run_git(repo_root, ["cat-file", "-s", f":{path}"])
        return int(raw.strip()), []
    except (CartographerError, ValueError):
        return None, ["SIZE_GIT_CATFILE_FAILED"]


def get_file_size_untracked(repo_root: Path, path: str) -> tuple[int | None, list[str]]:
    try:
        full_path = repo_root / path
        return full_path.stat().st_size, []
    except OSError:
        return None, ["SIZE_STAT_FAILED"]


# ---------------------------------------------------------------------------
# File list hashing
# ---------------------------------------------------------------------------

def hash_file_list(paths: list[str]) -> str:
    joined = "\0".join(paths).encode("utf-8")
    return sha256_bytes(joined)


def compute_run_fingerprint(
    head_commit: str,
    ruleset_sha256: str,
    tracked_list_sha256: str,
    untracked_visible_list_sha256: str,
) -> str:
    fingerprint_input = (
        head_commit + "\n" +
        ruleset_sha256 + "\n" +
        tracked_list_sha256 + "\n" +
        untracked_visible_list_sha256
    ).encode("utf-8")
    return sha256_bytes(fingerprint_input)


# ---------------------------------------------------------------------------
# Rules loading and matching
# ---------------------------------------------------------------------------

def load_rules(rules_path: Path) -> dict[str, Any]:
    if not rules_path.exists():
        raise CartographerError(f"rules file not found: {rules_path}")
    try:
        payload = json.loads(rules_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CartographerError(f"rules file JSON parse failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise CartographerError("rules file must contain a JSON object")
    if "rules" not in payload or not isinstance(payload["rules"], list):
        raise CartographerError("rules file must contain a 'rules' array")
    if "modules" not in payload or not isinstance(payload["modules"], dict):
        raise CartographerError("rules file must contain a 'modules' dict")
    return payload


def match_pattern(path: str, rule: dict[str, Any]) -> bool:
    pattern = rule["pattern"]
    rule_type = rule["type"]

    if rule_type == "prefix":
        return path.startswith(pattern)
    elif rule_type == "exact":
        return path == pattern
    elif rule_type == "glob":
        constraint = rule.get("constraint")
        if constraint == "root_only":
            if "/" in path:
                return False
        return fnmatch.fnmatch(path, pattern)
    else:
        raise CartographerError(f"unknown rule type: {rule_type}")


def classify_path(
    path: str,
    tracked_status: str,
    rules: list[dict[str, Any]],
    modules: dict[str, Any],
) -> dict[str, Any]:
    file_ext = os.path.splitext(path)[1] if "." in os.path.basename(path) else ""

    for idx, rule in enumerate(rules):
        if match_pattern(path, rule):
            owner_id = rule["owner_id"]
            if owner_id == "UNKNOWN":
                break
            mod_info = modules.get(owner_id, {})
            kind = mod_info.get("kind", "unknown")
            if kind == "module":
                module_id = owner_id
                zone_id = None
            elif kind == "borderland":
                module_id = "BORDERLAND"
                zone_id = owner_id
            else:
                module_id = "UNKNOWN"
                zone_id = None

            reason = "prefix_match" if rule["type"] == "prefix" else (
                "exact_match" if rule["type"] == "exact" else "glob_match"
            )
            confidence = 1.0 if rule["type"] in ("prefix", "exact") else 0.9

            return {
                "confidence": confidence,
                "file_ext": file_ext,
                "generated_hint": None,
                "module_id": module_id,
                "path": path,
                "reason_codes": [reason],
                "review_required": False,
                "size_bytes": None,
                "tracked_status": tracked_status,
                "zone_id": zone_id,
            }

    return {
        "confidence": 0.0,
        "file_ext": file_ext,
        "generated_hint": None,
        "module_id": "UNKNOWN",
        "path": path,
        "reason_codes": ["no_rule_match"],
        "review_required": True,
        "size_bytes": None,
        "tracked_status": tracked_status,
        "zone_id": None,
    }


def classify_all_files(
    tracked: list[str],
    untracked: list[str],
    rules_data: dict[str, Any],
    repo_root: Path,
) -> list[dict[str, Any]]:
    rules = rules_data["rules"]
    modules = rules_data["modules"]
    records: list[dict[str, Any]] = []

    for path in tracked:
        rec = classify_path(path, "tracked", rules, modules)
        size, size_reasons = get_file_size_tracked(repo_root, path)
        rec["size_bytes"] = size
        if size_reasons:
            rec["reason_codes"] = rec["reason_codes"] + size_reasons
        records.append(rec)

    for path in untracked:
        rec = classify_path(path, "untracked_visible", rules, modules)
        size, size_reasons = get_file_size_untracked(repo_root, path)
        rec["size_bytes"] = size
        if size_reasons:
            rec["reason_codes"] = rec["reason_codes"] + size_reasons
        records.append(rec)

    records.sort(key=lambda r: r["path"])
    return records


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_file_index(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "file_ext": r["file_ext"],
            "path": r["path"],
            "size_bytes": r["size_bytes"],
            "tracked_status": r["tracked_status"],
        }
        for r in records
    ]


def build_ownership_summary_md(
    records: list[dict[str, Any]],
    modules: dict[str, Any],
    head_commit: str,
    run_id: str,
    run_fingerprint: str,
) -> str:
    lines: list[str] = []
    lines.append("# MODULE_OWNERSHIP_SUMMARY v0.1\n")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Run ID | `{run_id}` |")
    lines.append(f"| Fingerprint | `{run_fingerprint}` |")
    lines.append(f"| HEAD | `{head_commit}` |")
    lines.append(f"| Total Files | {len(records)} |")
    lines.append("")

    tracked_count = sum(1 for r in records if r["tracked_status"] == "tracked")
    untracked_count = sum(1 for r in records if r["tracked_status"] == "untracked_visible")
    lines.append("## By Tracked Status\n")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| tracked | {tracked_count} |")
    lines.append(f"| untracked_visible | {untracked_count} |")
    lines.append("")

    # Module counts
    module_counts: dict[str, dict[str, int]] = {}
    for r in records:
        mid = r["module_id"]
        if mid not in ("BORDERLAND", "UNKNOWN"):
            if mid not in module_counts:
                module_counts[mid] = {"tracked": 0, "untracked_visible": 0}
            module_counts[mid][r["tracked_status"]] += 1

    lines.append("## Module Ownership\n")
    lines.append("| Module | Label | Tracked | Untracked | Total |")
    lines.append("|--------|-------|---------|-----------|-------|")
    for mid in sorted(module_counts.keys()):
        label = modules.get(mid, {}).get("label", "")
        t = module_counts[mid]["tracked"]
        u = module_counts[mid]["untracked_visible"]
        lines.append(f"| {mid} | {label} | {t} | {u} | {t + u} |")
    lines.append("")

    # Zone counts
    zone_counts: dict[str, dict[str, int]] = {}
    for r in records:
        zid = r["zone_id"]
        if zid is not None:
            if zid not in zone_counts:
                zone_counts[zid] = {"tracked": 0, "untracked_visible": 0}
            zone_counts[zid][r["tracked_status"]] += 1

    lines.append("## Borderland Zones\n")
    lines.append("| Zone | Label | Tracked | Untracked | Total |")
    lines.append("|------|-------|---------|-----------|-------|")
    for zid in sorted(zone_counts.keys()):
        label = modules.get(zid, {}).get("label", "")
        t = zone_counts[zid]["tracked"]
        u = zone_counts[zid]["untracked_visible"]
        lines.append(f"| {zid} | {label} | {t} | {u} | {t + u} |")
    lines.append("")

    # Unknown totals
    unknown_tracked = sum(1 for r in records if r["module_id"] == "UNKNOWN" and r["tracked_status"] == "tracked")
    unknown_untracked = sum(1 for r in records if r["module_id"] == "UNKNOWN" and r["tracked_status"] == "untracked_visible")
    lines.append("## Unknown Files\n")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| tracked | {unknown_tracked} |")
    lines.append(f"| untracked_visible | {unknown_untracked} |")
    lines.append(f"| **total** | **{unknown_tracked + unknown_untracked}** |")
    lines.append("")

    return "\n".join(lines) + "\n"


def build_borderlands_pressure_md(
    records: list[dict[str, Any]],
    modules: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# BORDERLANDS_PRESSURE_REPORT v0.1\n")

    zone_records: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        zid = r["zone_id"]
        if zid is not None:
            if zid not in zone_records:
                zone_records[zid] = []
            zone_records[zid].append(r)

    for zid in sorted(zone_records.keys()):
        recs = zone_records[zid]
        label = modules.get(zid, {}).get("label", "")
        tracked = sum(1 for r in recs if r["tracked_status"] == "tracked")
        untracked = sum(1 for r in recs if r["tracked_status"] == "untracked_visible")

        ext_dist: dict[str, int] = {}
        for r in recs:
            ext = r["file_ext"] if r["file_ext"] else "(none)"
            ext_dist[ext] = ext_dist.get(ext, 0) + 1

        lines.append(f"## {zid}: {label}\n")
        lines.append(f"- **Total files:** {len(recs)}")
        lines.append(f"- **Tracked:** {tracked}")
        lines.append(f"- **Untracked-visible:** {untracked}")
        lines.append(f"- **Extension distribution:**")
        for ext in sorted(ext_dist.keys()):
            lines.append(f"  - `{ext}`: {ext_dist[ext]}")
        lines.append("")

    return "\n".join(lines) + "\n"


def build_untracked_visible_md(records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# UNTRACKED_VISIBLE_REPORT v0.1\n")

    untracked = [r for r in records if r["tracked_status"] == "untracked_visible"]
    lines.append(f"**Total untracked-visible files:** {len(untracked)}\n")

    unknown = sorted([r["path"] for r in untracked if r["module_id"] == "UNKNOWN"])
    borderland = sorted([r["path"] for r in untracked if r["module_id"] == "BORDERLAND"])
    module_matched = sorted([r["path"] for r in untracked if r["module_id"] not in ("UNKNOWN", "BORDERLAND")])

    lines.append("## UNKNOWN (unclassified)\n")
    if unknown:
        for p in unknown:
            lines.append(f"- `{p}`")
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("## Borderland-matched\n")
    if borderland:
        for p in borderland:
            lines.append(f"- `{p}`")
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("## Module-matched\n")
    if module_matched:
        for p in module_matched:
            lines.append(f"- `{p}`")
    else:
        lines.append("(none)")
    lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Manifest, Seal
# ---------------------------------------------------------------------------

def build_manifest(
    run_dir: Path,
    artifact_names: list[str],
    run_id: str,
) -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    for name in sorted(artifact_names):
        fpath = run_dir / name
        artifacts[name] = {
            "bytes": fpath.stat().st_size,
            "sha256": sha256_file(fpath),
        }
    return {
        "artifacts": artifacts,
        "run_id": run_id,
        "schema_version": "REPO_CARTOGRAPHER_MANIFEST_v0.1",
    }


def build_seal(
    manifest_path: Path,
    run_id: str,
    run_fingerprint: str,
    repo_root: Path,
    script_path: Path,
    rules_path: Path,
) -> dict[str, Any]:
    return {
        "inputs": {
            relpath_posix(rules_path, repo_root): {
                "bytes": rules_path.stat().st_size,
                "sha256": sha256_file(rules_path),
            },
            relpath_posix(script_path, repo_root): {
                "bytes": script_path.stat().st_size,
                "sha256": sha256_file(script_path),
            },
        },
        "kind": "REPO_CARTOGRAPHER_RUN_SEAL",
        "run_fingerprint": run_fingerprint,
        "run_id": run_id,
        "target": {
            "bytes": manifest_path.stat().st_size,
            "path": manifest_path.name,
            "sha256": sha256_file(manifest_path),
        },
        "version": "0.1",
    }


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {
            "last_classification_sha256": None,
            "last_index_sha256": None,
            "last_processed_commit": None,
            "last_run_fingerprint": None,
            "last_run_id": None,
            "last_tracked_list_sha256": None,
            "last_untracked_visible_list_sha256": None,
            "ruleset_id": "MODULE_OWNERSHIP_RULES_v0.1",
        }
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CartographerError(f"state file JSON parse failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise CartographerError("state file must contain a JSON object")
    return payload


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    content = serialize_json_pretty(state)
    state_path.write_bytes(content)


# ---------------------------------------------------------------------------
# Run ledger
# ---------------------------------------------------------------------------

def build_ledger_line(
    run_id: str,
    run_fingerprint: str,
    generated_utc: str,
    head_commit: str,
    ruleset_id: str,
    tracked_list_sha256: str,
    untracked_visible_list_sha256: str,
    ruleset_sha256: str,
    manifest_sha256: str,
    seal_sha256: str,
    summary_counts: dict[str, int],
    artifacts_path: str,
) -> dict[str, Any]:
    return {
        "artifacts_path": artifacts_path,
        "generated_utc": generated_utc,
        "head_commit": head_commit,
        "manifest_sha256": manifest_sha256,
        "ruleset_id": ruleset_id,
        "ruleset_sha256": ruleset_sha256,
        "run_fingerprint": run_fingerprint,
        "run_id": run_id,
        "seal_sha256": seal_sha256,
        "summary_counts": summary_counts,
        "tracked_list_sha256": tracked_list_sha256,
        "untracked_visible_list_sha256": untracked_visible_list_sha256,
    }


def append_ledger(ledger_path: Path, line: dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    line_bytes = (serialize_jsonl_line(line) + "\n").encode("utf-8")
    with ledger_path.open("ab") as f:
        f.write(line_bytes)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_index(repo_root: Path, args: argparse.Namespace) -> int:
    tracked = enumerate_tracked_files(repo_root)
    untracked = enumerate_untracked_visible(repo_root)

    print(f"TRACKED={len(tracked)}")
    print(f"UNTRACKED_VISIBLE={len(untracked)}")
    print(f"TOTAL={len(tracked) + len(untracked)}")
    print(f"TRACKED_LIST_SHA256={hash_file_list(tracked)}")
    print(f"UNTRACKED_VISIBLE_LIST_SHA256={hash_file_list(untracked)}")
    return 0


def cmd_classify(repo_root: Path, args: argparse.Namespace) -> int:
    rules_path = resolve_repo_path(args.rules, repo_root)
    rules_data = load_rules(rules_path)

    tracked = enumerate_tracked_files(repo_root)
    untracked = enumerate_untracked_visible(repo_root)
    records = classify_all_files(tracked, untracked, rules_data, repo_root)

    module_count = sum(1 for r in records if r["module_id"] not in ("BORDERLAND", "UNKNOWN"))
    borderland_count = sum(1 for r in records if r["module_id"] == "BORDERLAND")
    unknown_count = sum(1 for r in records if r["module_id"] == "UNKNOWN")

    print(f"TOTAL={len(records)}")
    print(f"MODULE_CLASSIFIED={module_count}")
    print(f"BORDERLAND_CLASSIFIED={borderland_count}")
    print(f"UNKNOWN={unknown_count}")
    return 0


def cmd_report(repo_root: Path, args: argparse.Namespace) -> int:
    rules_path = resolve_repo_path(args.rules, repo_root)
    rules_data = load_rules(rules_path)

    tracked = enumerate_tracked_files(repo_root)
    untracked = enumerate_untracked_visible(repo_root)
    records = classify_all_files(tracked, untracked, rules_data, repo_root)

    print(build_ownership_summary_md(records, rules_data["modules"], get_head_commit(repo_root), "preview", "preview"))
    print(build_borderlands_pressure_md(records, rules_data["modules"]))
    print(build_untracked_visible_md(records))
    return 0


def cmd_run(repo_root: Path, args: argparse.Namespace) -> int:
    rules_path = resolve_repo_path(args.rules, repo_root)
    state_path = resolve_repo_path(args.state, repo_root)
    ledger_path = resolve_repo_path(DEFAULT_LEDGER_PATH, repo_root)
    script_path = Path(__file__).resolve()

    # 1. Load and hash rules
    rules_data = load_rules(rules_path)
    ruleset_id = rules_data.get("ruleset_id", "MODULE_OWNERSHIP_RULES_v0.1")
    ruleset_sha256 = sha256_file(rules_path)

    # 2-3. Enumerate files
    tracked = enumerate_tracked_files(repo_root)
    untracked = enumerate_untracked_visible(repo_root)
    tracked_list_sha256 = hash_file_list(tracked)
    untracked_visible_list_sha256 = hash_file_list(untracked)

    # 4. HEAD
    head_commit = get_head_commit(repo_root)

    # 5. Fingerprint
    run_fingerprint = compute_run_fingerprint(
        head_commit, ruleset_sha256, tracked_list_sha256, untracked_visible_list_sha256,
    )

    # 6. Run ID
    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.run_id:
        run_id = args.run_id
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    # 7-8. Classify
    records = classify_all_files(tracked, untracked, rules_data, repo_root)

    # 9. Determinism check
    records2 = classify_all_files(tracked, untracked, rules_data, repo_root)
    classification_bytes = serialize_jsonl(records)
    classification_bytes_2 = serialize_jsonl(records2)
    if classification_bytes != classification_bytes_2:
        raise CartographerError("determinism check failed: classification output differs between runs")

    # 10. Create run directory
    run_dir = repo_root / ARTIFACTS_DIR / run_id
    if run_dir.exists():
        raise CartographerError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    # 11. Write content artifacts
    # 11a. File index
    index_rows = build_file_index(records)
    index_bytes = serialize_jsonl(index_rows)
    (run_dir / "REPO_FILE_INDEX_v0.1.jsonl").write_bytes(index_bytes)

    # 11b. Classification
    (run_dir / "REPO_FILE_CLASSIFICATION_v0.1.jsonl").write_bytes(classification_bytes)

    # 11c. Ownership summary
    summary_md = build_ownership_summary_md(
        records, rules_data["modules"], head_commit, run_id, run_fingerprint,
    )
    (run_dir / "MODULE_OWNERSHIP_SUMMARY_v0.1.md").write_bytes(summary_md.encode("utf-8"))

    # 11d. Borderlands pressure
    pressure_md = build_borderlands_pressure_md(records, rules_data["modules"])
    (run_dir / "BORDERLANDS_PRESSURE_REPORT_v0.1.md").write_bytes(pressure_md.encode("utf-8"))

    # 11e. Untracked visible report
    untracked_md = build_untracked_visible_md(records)
    (run_dir / "UNTRACKED_VISIBLE_REPORT_v0.1.md").write_bytes(untracked_md.encode("utf-8"))

    # 11f. Move plan (empty for v0.1)
    move_plan = {"note": "No proposals in v0.1", "proposals": []}
    (run_dir / "MOVE_PLAN_PROPOSED_v0.1.json").write_bytes(serialize_json_pretty(move_plan))

    # 12. Manifest
    manifest_data = build_manifest(run_dir, CONTENT_ARTIFACTS, run_id)
    manifest_bytes = serialize_json_pretty(manifest_data)
    manifest_path = run_dir / "MANIFEST.json"
    manifest_path.write_bytes(manifest_bytes)
    manifest_sha_line = f"{sha256_bytes(manifest_bytes)}  MANIFEST.json\n"
    (run_dir / "MANIFEST.sha256").write_bytes(manifest_sha_line.encode("utf-8"))

    # 13. Seal
    seal_data = build_seal(
        manifest_path, run_id, run_fingerprint, repo_root, script_path, rules_path,
    )
    seal_bytes = serialize_json_pretty(seal_data)
    seal_path = run_dir / "SEAL.json"
    seal_path.write_bytes(seal_bytes)
    seal_sha_line = f"{sha256_bytes(seal_bytes)}  SEAL.json\n"
    (run_dir / "SEAL.sha256").write_bytes(seal_sha_line.encode("utf-8"))

    # 14. Post-write verification
    for name in CONTENT_ARTIFACTS:
        fpath = run_dir / name
        if not fpath.exists():
            raise CartographerError(f"post-write verification: missing artifact {name}")
    if manifest_path.read_bytes() != manifest_bytes:
        raise CartographerError("post-write verification: MANIFEST.json mismatch")
    if seal_path.read_bytes() != seal_bytes:
        raise CartographerError("post-write verification: SEAL.json mismatch")

    # 15. Append ledger
    index_sha256 = sha256_bytes(index_bytes)
    classification_sha256 = sha256_bytes(classification_bytes)
    manifest_sha256_val = sha256_bytes(manifest_bytes)
    seal_sha256_val = sha256_bytes(seal_bytes)

    unknown_count = sum(1 for r in records if r["module_id"] == "UNKNOWN")
    summary_counts = {
        "total": len(records),
        "tracked": len(tracked),
        "unknown": unknown_count,
        "untracked_visible": len(untracked),
    }

    ledger_line = build_ledger_line(
        run_id=run_id,
        run_fingerprint=run_fingerprint,
        generated_utc=generated_utc,
        head_commit=head_commit,
        ruleset_id=ruleset_id,
        tracked_list_sha256=tracked_list_sha256,
        untracked_visible_list_sha256=untracked_visible_list_sha256,
        ruleset_sha256=ruleset_sha256,
        manifest_sha256=manifest_sha256_val,
        seal_sha256=seal_sha256_val,
        summary_counts=summary_counts,
        artifacts_path=relpath_posix(run_dir, repo_root),
    )
    append_ledger(ledger_path, ledger_line)

    # 16. Update state
    state = {
        "last_classification_sha256": classification_sha256,
        "last_index_sha256": index_sha256,
        "last_processed_commit": head_commit,
        "last_run_fingerprint": run_fingerprint,
        "last_run_id": run_id,
        "last_tracked_list_sha256": tracked_list_sha256,
        "last_untracked_visible_list_sha256": untracked_visible_list_sha256,
        "ruleset_id": ruleset_id,
    }
    save_state(state_path, state)

    # Print summary
    print(f"RUN_ID={run_id}")
    print(f"RUN_FINGERPRINT={run_fingerprint}")
    print(f"HEAD={head_commit}")
    print(f"ARTIFACTS={relpath_posix(run_dir, repo_root)}")
    print(f"TRACKED={len(tracked)}")
    print(f"UNTRACKED_VISIBLE={len(untracked)}")
    print(f"TOTAL={len(records)}")
    print(f"UNKNOWN={unknown_count}")
    print(f"MANIFEST_SHA256={manifest_sha256_val}")
    print(f"SEAL_SHA256={seal_sha256_val}")

    return 0


def cmd_verify(repo_root: Path, args: argparse.Namespace) -> int:
    state_path = resolve_repo_path(args.state, repo_root)
    rules_path = resolve_repo_path(args.rules, repo_root)
    state = load_state(state_path)

    run_id = args.run_id if args.run_id else state.get("last_run_id")
    if not run_id:
        raise CartographerError("no run_id to verify (no previous run or --run-id not provided)")

    run_dir = repo_root / ARTIFACTS_DIR / run_id
    if not run_dir.exists():
        raise CartographerError(f"run directory not found: {run_dir}")

    # Check SEAL integrity
    seal_path = run_dir / "SEAL.json"
    seal_sha_path = run_dir / "SEAL.sha256"
    if not seal_path.exists() or not seal_sha_path.exists():
        raise CartographerError("SEAL.json or SEAL.sha256 missing")

    seal_bytes = seal_path.read_bytes()
    seal_sha_content = seal_sha_path.read_text(encoding="utf-8").strip()
    expected_seal_sha = seal_sha_content.split()[0] if seal_sha_content else ""
    actual_seal_sha = sha256_bytes(seal_bytes)
    if expected_seal_sha != actual_seal_sha:
        raise CartographerError("SEAL.sha256 integrity check failed")

    # Check MANIFEST integrity
    manifest_path = run_dir / "MANIFEST.json"
    manifest_sha_path = run_dir / "MANIFEST.sha256"
    if not manifest_path.exists() or not manifest_sha_path.exists():
        raise CartographerError("MANIFEST.json or MANIFEST.sha256 missing")

    manifest_bytes = manifest_path.read_bytes()
    manifest_sha_content = manifest_sha_path.read_text(encoding="utf-8").strip()
    expected_manifest_sha = manifest_sha_content.split()[0] if manifest_sha_content else ""
    actual_manifest_sha = sha256_bytes(manifest_bytes)
    if expected_manifest_sha != actual_manifest_sha:
        raise CartographerError("MANIFEST.sha256 integrity check failed")

    seal_data = json.loads(seal_bytes.decode("utf-8"))
    seal_target_sha = seal_data.get("target", {}).get("sha256", "")
    if seal_target_sha != actual_manifest_sha:
        raise CartographerError("SEAL target sha256 does not match MANIFEST.json")

    # Check manifest artifact integrity
    manifest_data = json.loads(manifest_bytes.decode("utf-8"))
    for name, info in manifest_data.get("artifacts", {}).items():
        fpath = run_dir / name
        if not fpath.exists():
            raise CartographerError(f"artifact missing: {name}")
        actual_sha = sha256_file(fpath)
        if actual_sha != info["sha256"]:
            raise CartographerError(f"artifact integrity failed: {name}")

    # Re-classify and compare identity fields
    rules_data = load_rules(rules_path)
    tracked = enumerate_tracked_files(repo_root)
    untracked = enumerate_untracked_visible(repo_root)
    current_records = classify_all_files(tracked, untracked, rules_data, repo_root)

    stored_classification_path = run_dir / "REPO_FILE_CLASSIFICATION_v0.1.jsonl"
    stored_text = stored_classification_path.read_text(encoding="utf-8")
    stored_records: list[dict[str, Any]] = []
    for line in stored_text.splitlines():
        if line.strip():
            stored_records.append(json.loads(line))

    # Build identity maps
    stored_identity = {
        r["path"]: (r["tracked_status"], r["module_id"], r["zone_id"])
        for r in stored_records
    }
    current_identity = {
        r["path"]: (r["tracked_status"], r["module_id"], r["zone_id"])
        for r in current_records
    }

    diffs: list[str] = []
    new_unknowns: list[str] = []

    # The run's own artifacts directory is expected to appear as new untracked files
    run_artifacts_prefix = relpath_posix(run_dir, repo_root) + "/"

    # Check for new files
    for path in sorted(current_identity.keys()):
        if path not in stored_identity:
            if path.startswith(run_artifacts_prefix):
                continue
            mid = current_identity[path][1]
            if mid == "UNKNOWN":
                new_unknowns.append(path)
            diffs.append(f"NEW: {path} ({mid})")

    # Check for removed files
    for path in sorted(stored_identity.keys()):
        if path not in current_identity:
            diffs.append(f"REMOVED: {path}")

    # Check for classification changes
    for path in sorted(current_identity.keys()):
        if path in stored_identity and current_identity[path] != stored_identity[path]:
            old = stored_identity[path]
            new = current_identity[path]
            diffs.append(f"CHANGED: {path} ({old} -> {new})")

    if diffs:
        print(f"VERIFY: {len(diffs)} drift(s) detected:")
        for d in diffs:
            print(f"  {d}")

    if new_unknowns and not args.allow_unknown:
        print(f"VERIFY FAILED: {len(new_unknowns)} new UNKNOWN file(s):", file=sys.stderr)
        for p in new_unknowns:
            print(f"  {p}", file=sys.stderr)
        return 1

    print("VERIFY OK")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repo Cartographer: deterministic file ownership classification.",
    )
    parser.add_argument(
        "--state",
        default=DEFAULT_STATE_PATH,
        help="Path to state JSON file.",
    )
    parser.add_argument(
        "--rules",
        default=DEFAULT_RULES_PATH,
        help="Path to ownership rules JSON file.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="Enumerate tracked and untracked-visible files.")
    sub.add_parser("classify", help="Classify files against ownership rules.")
    sub.add_parser("report", help="Generate classification reports to stdout.")

    run_parser = sub.add_parser("run", help="Full run with artifact generation and sealing.")
    run_parser.add_argument("--run-id", help="Override the run ID (default: UTC timestamp).")

    verify_parser = sub.add_parser("verify", help="Verify last run against current state.")
    verify_parser.add_argument("--run-id", help="Verify a specific run ID instead of latest.")
    verify_parser.add_argument("--allow-unknown", action="store_true", help="Allow UNKNOWN files.")

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        repo_root = get_repo_root()
        dispatch = {
            "index": cmd_index,
            "classify": cmd_classify,
            "report": cmd_report,
            "run": cmd_run,
            "verify": cmd_verify,
        }
        return dispatch[args.command](repo_root, args)
    except CartographerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
