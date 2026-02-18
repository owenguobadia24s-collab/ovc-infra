#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POINTER_PATH = Path("docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json")
RUNS_ROOT = Path("artifacts/repo_cartographer")
SOURCE_NAME = "REPO_FILE_CLASSIFICATION_v0.1.jsonl"
OUT_JSON_PATH = Path("docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json")
OUT_TXT_PATH = Path("docs/catalogs/REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt")

BOOL_GATE_FIELDS = [
    "ok",
    "ledger_manifest_match",
    "ledger_seal_match",
    "manifest_sidecar_match",
    "seal_sidecar_match",
]


class FrontierError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class Summary:
    selected_run_id: str = ""
    pointer_path: str = POINTER_PATH.as_posix()
    source_path_exists: bool = False
    unknown_count: int = 0
    output_json_path: str = OUT_JSON_PATH.as_posix()
    output_txt_path: str = "(not written)"
    action: str = ""


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def rel_posix(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def read_pointer(pointer_abs: Path) -> dict[str, Any]:
    if not pointer_abs.exists():
        raise FrontierError("FAIL_POINTER_MISSING")
    try:
        payload = json.loads(pointer_abs.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise FrontierError("FAIL_POINTER_PARSE") from None
    if not isinstance(payload, dict):
        raise FrontierError("FAIL_POINTER_PARSE")
    return payload


def validate_pointer(pointer: dict[str, Any]) -> tuple[str, str]:
    run_id = pointer.get("LATEST_OK_RUN_ID")
    run_ts = pointer.get("LATEST_OK_RUN_TS")
    if not isinstance(run_id, str) or not run_id:
        raise FrontierError("FAIL_POINTER_PARSE")
    if not isinstance(run_ts, str) or not run_ts:
        raise FrontierError("FAIL_POINTER_PARSE")
    for field in BOOL_GATE_FIELDS:
        if pointer.get(field) is not True:
            raise FrontierError(f"FAIL_POINTER_GATE_FALSE:{field}")
    return run_id, run_ts


def normalize_repo_posix_path(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while value.startswith("./"):
        value = value[2:]
    if not value:
        raise FrontierError("FAIL_CLASSIFICATION_SCHEMA")
    if value.startswith("/"):
        raise FrontierError("FAIL_CLASSIFICATION_SCHEMA")
    if "\x00" in value:
        raise FrontierError("FAIL_CLASSIFICATION_SCHEMA")
    return value


def path_top_level(path: str) -> str:
    parts = path.split("/", 1)
    return parts[0] if parts and parts[0] else "."


def path_extension(path: str) -> str:
    suffix = Path(path).suffix
    return suffix[1:] if suffix.startswith(".") else ""


def is_unknown_row(row: dict[str, Any]) -> bool:
    keys = ("classification", "ownership", "module", "module_id")
    for key in keys:
        if row.get(key) == "UNKNOWN":
            return True
    return False


def parse_classification_jsonl(source_abs: Path) -> list[dict[str, str]]:
    unknown_files: list[dict[str, str]] = []
    try:
        lines = source_abs.read_text(encoding="utf-8").splitlines()
    except OSError:
        raise FrontierError("FAIL_SOURCE_MISSING") from None

    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            raise FrontierError("FAIL_CLASSIFICATION_PARSE") from None
        if not isinstance(row, dict):
            raise FrontierError("FAIL_CLASSIFICATION_PARSE")

        path_raw = row.get("path")
        if not isinstance(path_raw, str):
            raise FrontierError("FAIL_CLASSIFICATION_SCHEMA")
        normalized_path = normalize_repo_posix_path(path_raw)

        if is_unknown_row(row):
            unknown_files.append(
                {
                    "path": normalized_path,
                    "top_level_dir": path_top_level(normalized_path),
                    "extension": path_extension(normalized_path),
                }
            )
    unknown_files.sort(key=lambda item: item["path"])
    return unknown_files


def build_counts(unknown_files: list[dict[str, str]]) -> tuple[dict[str, int], dict[str, int]]:
    by_dir: dict[str, int] = {}
    by_ext: dict[str, int] = {}
    for item in unknown_files:
        top = item["top_level_dir"]
        ext = item["extension"]
        by_dir[top] = by_dir.get(top, 0) + 1
        by_ext[ext] = by_ext.get(ext, 0) + 1
    by_dir_sorted = {k: by_dir[k] for k in sorted(by_dir.keys())}
    by_ext_sorted = {k: by_ext[k] for k in sorted(by_ext.keys())}
    return by_dir_sorted, by_ext_sorted


def render_txt(
    selected_run_id: str,
    unknown_files: list[dict[str, str]],
    counts_by_top_level_dir: dict[str, int],
    counts_by_extension: dict[str, int],
) -> str:
    lines = [
        f"UNKNOWN FRONTIER — {selected_run_id}",
        f"TOTAL UNKNOWN FILES: {len(unknown_files)}",
        "",
        "## By path (sorted)",
    ]
    for item in unknown_files:
        lines.append(item["path"])
    lines.append("")
    lines.append("## Counts by top-level directory")
    for key in sorted(counts_by_top_level_dir.keys()):
        lines.append(f"{key}: {counts_by_top_level_dir[key]}")
    lines.append("")
    lines.append("## Counts by extension")
    for key in sorted(counts_by_extension.keys()):
        label = key if key else "(none)"
        lines.append(f"{label}: {counts_by_extension[key]}")
    lines.append("")
    return "\n".join(lines)


def atomic_write_bytes(dest_abs: Path, data: bytes) -> None:
    dest_abs.parent.mkdir(parents=True, exist_ok=True)
    temp_abs = dest_abs.with_name(dest_abs.name + ".tmp")
    try:
        temp_abs.write_bytes(data)
        os.replace(temp_abs, dest_abs)
    except OSError:
        try:
            if temp_abs.exists():
                temp_abs.unlink()
        except OSError:
            pass
        raise FrontierError("FAIL_ATOMIC_WRITE") from None


def execute(repo_root: Path) -> Summary:
    summary = Summary()
    pointer_abs = repo_root / POINTER_PATH
    out_json_abs = repo_root / OUT_JSON_PATH
    out_txt_abs = repo_root / OUT_TXT_PATH

    try:
        pointer = read_pointer(pointer_abs)
        selected_run_id, selected_run_ts = validate_pointer(pointer)
        summary.selected_run_id = selected_run_id

        run_dir = repo_root / RUNS_ROOT / selected_run_id
        if not run_dir.is_dir():
            raise FrontierError("FAIL_RUN_DIR_MISSING")

        source_abs = run_dir / SOURCE_NAME
        summary.source_path_exists = source_abs.exists()
        if not source_abs.exists():
            raise FrontierError("FAIL_SOURCE_MISSING")

        unknown_files = parse_classification_jsonl(source_abs)
        counts_by_top_level_dir, counts_by_extension = build_counts(unknown_files)
        summary.unknown_count = len(unknown_files)

        output_payload = {
            "selected_run_id": selected_run_id,
            "selected_run_ts": selected_run_ts,
            "unknown_count": summary.unknown_count,
            "unknown_files": unknown_files,
            "counts_by_top_level_dir": counts_by_top_level_dir,
            "counts_by_extension": counts_by_extension,
        }
        json_bytes = (json.dumps(output_payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        txt_text = render_txt(
            selected_run_id=selected_run_id,
            unknown_files=unknown_files,
            counts_by_top_level_dir=counts_by_top_level_dir,
            counts_by_extension=counts_by_extension,
        )
        txt_bytes = txt_text.encode("utf-8")

        atomic_write_bytes(out_json_abs, json_bytes)
        atomic_write_bytes(out_txt_abs, txt_bytes)
        summary.output_txt_path = rel_posix(out_txt_abs, repo_root)
        summary.action = "COPIED"
    except FrontierError as exc:
        summary.action = exc.code

    return summary


def print_summary(summary: Summary) -> None:
    print(f"selected_run_id={summary.selected_run_id}")
    print(f"pointer_path={summary.pointer_path}")
    print(f"source_path exists: {'true' if summary.source_path_exists else 'false'}")
    print(f"unknown_count={summary.unknown_count}")
    print(f"output_json_path={summary.output_json_path}")
    print(f"output_txt_path={summary.output_txt_path}")
    print(f"action: {summary.action}")


def main(argv: list[str]) -> int:
    if argv:
        print("ERROR: this consumer does not accept arguments", file=sys.stderr)
        return 2
    summary = execute(get_repo_root())
    print_summary(summary)
    if summary.action == "COPIED":
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
