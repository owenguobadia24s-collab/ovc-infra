#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


POINTER_PATH = Path("docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json")
RUNS_ROOT = Path("artifacts/repo_cartographer")
SOURCE_NAME = "MODULE_OWNERSHIP_SUMMARY_v0.1.md"
DEST_PATH = Path("docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.md")
RECEIPT_PATH = Path("docs/REPO_MAP/LATEST_OWNERSHIP_SUMMARY.receipt.json")

BOOL_GATE_FIELDS = [
    "ok",
    "ledger_manifest_match",
    "ledger_seal_match",
    "manifest_sidecar_match",
    "seal_sidecar_match",
]

SUCCESS_ACTIONS = {"COPIED", "NOOP_IDENTICAL"}


class PublishError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class Summary:
    selected_run_id: str = ""
    pointer_path: str = POINTER_PATH.as_posix()
    source_path_exists: bool = False
    dest_path: str = DEST_PATH.as_posix()
    sha256_source: str = ""
    sha256_dest: str = ""
    byte_len_source: int = 0
    byte_len_dest: int = 0
    action: str = ""


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def digest_and_size(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return sha256_bytes(data), len(data)


def rel_posix(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def read_pointer(pointer_abs: Path) -> dict[str, Any]:
    if not pointer_abs.exists():
        raise PublishError("FAIL_POINTER_MISSING")
    try:
        data = json.loads(pointer_abs.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise PublishError("FAIL_POINTER_PARSE") from None
    if not isinstance(data, dict):
        raise PublishError("FAIL_POINTER_PARSE")
    return data


def validate_pointer(pointer: dict[str, Any]) -> tuple[str, str]:
    run_id = pointer.get("LATEST_OK_RUN_ID")
    run_ts = pointer.get("LATEST_OK_RUN_TS")
    if not isinstance(run_id, str) or not run_id:
        raise PublishError("FAIL_POINTER_PARSE")
    if not isinstance(run_ts, str) or not run_ts:
        raise PublishError("FAIL_POINTER_PARSE")

    for field in BOOL_GATE_FIELDS:
        if pointer.get(field) is not True:
            raise PublishError(f"FAIL_POINTER_GATE_FALSE:{field}")
    return run_id, run_ts


def write_receipt(receipt_abs: Path, receipt: dict[str, Any]) -> None:
    receipt_abs.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    receipt_abs.write_text(payload, encoding="utf-8")


def atomic_copy_bytes(source_bytes: bytes, dest_abs: Path) -> None:
    dest_abs.parent.mkdir(parents=True, exist_ok=True)
    temp_abs = dest_abs.with_name(dest_abs.name + ".tmp")
    try:
        temp_abs.write_bytes(source_bytes)
        os.replace(temp_abs, dest_abs)
    except OSError:
        try:
            if temp_abs.exists():
                temp_abs.unlink()
        except OSError:
            pass
        raise PublishError("FAIL_ATOMIC_WRITE") from None


def execute(repo_root: Path) -> Summary:
    summary = Summary()
    pointer_abs = repo_root / POINTER_PATH
    dest_abs = repo_root / DEST_PATH
    receipt_abs = repo_root / RECEIPT_PATH
    source_abs: Path | None = None
    selected_run_ts = ""

    try:
        pointer = read_pointer(pointer_abs)
        selected_run_id, selected_run_ts = validate_pointer(pointer)
        summary.selected_run_id = selected_run_id

        run_dir = repo_root / RUNS_ROOT / selected_run_id
        if not run_dir.is_dir():
            raise PublishError("FAIL_RUN_DIR_MISSING")

        source_abs = run_dir / SOURCE_NAME
        summary.source_path_exists = source_abs.exists()
        if not source_abs.exists():
            raise PublishError("FAIL_SOURCE_MISSING")

        source_sha, source_len = digest_and_size(source_abs)
        summary.sha256_source = source_sha
        summary.byte_len_source = source_len

        if dest_abs.exists():
            dest_sha, dest_len = digest_and_size(dest_abs)
            summary.sha256_dest = dest_sha
            summary.byte_len_dest = dest_len
        else:
            dest_sha, dest_len = "", 0

        if dest_abs.exists() and dest_sha == source_sha and dest_len == source_len:
            summary.action = "NOOP_IDENTICAL"
            summary.sha256_dest = source_sha
            summary.byte_len_dest = source_len
        else:
            source_bytes = source_abs.read_bytes()
            atomic_copy_bytes(source_bytes, dest_abs)
            copied_sha, copied_len = digest_and_size(dest_abs)
            summary.sha256_dest = copied_sha
            summary.byte_len_dest = copied_len
            if copied_sha != source_sha or copied_len != source_len:
                raise PublishError("FAIL_COPY_HASH_MISMATCH")
            summary.action = "COPIED"

        receipt = {
            "selected_run_id": selected_run_id,
            "selected_run_ts": selected_run_ts,
            "source_path": rel_posix(source_abs, repo_root),
            "dest_path": rel_posix(dest_abs, repo_root),
            "sha256_source": summary.sha256_source,
            "sha256_dest": summary.sha256_dest,
            "byte_len_source": summary.byte_len_source,
            "byte_len_dest": summary.byte_len_dest,
            "copy_mode": "verbatim",
            "lf_normalization": "preserve",
        }
        write_receipt(receipt_abs, receipt)
    except PublishError as exc:
        summary.action = exc.code
        # Fail-pointer states and all other failures must not emit a success-style receipt.
        if receipt_abs.exists() and summary.action not in SUCCESS_ACTIONS:
            receipt_abs.unlink()

    return summary


def print_summary(summary: Summary) -> None:
    print(f"selected_run_id={summary.selected_run_id}")
    print(f"pointer_path={summary.pointer_path}")
    print(f"source_path exists: {'true' if summary.source_path_exists else 'false'}")
    print(f"dest_path={summary.dest_path}")
    print(f"sha256_source={summary.sha256_source}")
    print(f"sha256_dest={summary.sha256_dest}")
    print(f"byte_len_source={summary.byte_len_source}")
    print(f"byte_len_dest={summary.byte_len_dest}")
    print(f"action: {summary.action}")


def main(argv: list[str]) -> int:
    if argv:
        print("ERROR: this consumer does not accept arguments", file=sys.stderr)
        return 2
    summary = execute(get_repo_root())
    print_summary(summary)
    if summary.action in SUCCESS_ACTIONS:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
