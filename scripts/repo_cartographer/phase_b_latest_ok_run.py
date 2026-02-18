#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


LEDGER_PATH_DEFAULT = "docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl"
ARTIFACTS_DIR_DEFAULT = "artifacts/repo_cartographer"
LATEST_OK_OUT_DEFAULT = "docs/catalogs/REPO_CARTOGRAPHER_LATEST_OK_RUN_v0.1.json"
POINTER_OUT_DEFAULT = "docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json"


class PhaseBError(RuntimeError):
    pass


def get_repo_root() -> Path:
    # Deterministic: use filesystem (no git required here)
    # Repo root assumed to be two levels up from this script: scripts/repo_cartographer/*
    return Path(__file__).resolve().parents[2]


def is_utc_iso_timestamp(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_sha256_sidecar(path: Path) -> str:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return ""
    return content.split()[0].lower()


@dataclass(frozen=True)
class LedgerRow:
    raw: dict[str, Any]

    @property
    def run_id(self) -> str:
        return str(self.raw.get("run_id", ""))

    @property
    def run_ts(self) -> str:
        return str(self.raw.get("run_ts", ""))

    @property
    def status(self) -> str:
        return str(self.raw.get("status", ""))

    @property
    def artifacts_path(self) -> str:
        return str(self.raw.get("artifacts_path", ""))

    @property
    def manifest_sha256(self) -> str:
        return str(self.raw.get("manifest_sha256", ""))

    @property
    def seal_sha256(self) -> str:
        return str(self.raw.get("seal_sha256", ""))


def iter_ledger_rows(ledger_path: Path) -> Iterable[LedgerRow]:
    if not ledger_path.exists():
        raise PhaseBError(f"ledger not found: {ledger_path}")
    for idx, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PhaseBError(f"invalid JSON in ledger at line {idx}: {exc}") from exc
        if not isinstance(obj, dict):
            raise PhaseBError(f"ledger line {idx} must be a JSON object")
        yield LedgerRow(obj)


def select_latest_ok_run(rows: Iterable[LedgerRow]) -> LedgerRow:
    eligible: list[LedgerRow] = []
    for r in rows:
        if r.status != "OK":
            continue
        if not r.run_id or not r.run_ts:
            continue
        if not is_utc_iso_timestamp(r.run_ts):
            continue
        eligible.append(r)

    if not eligible:
        raise PhaseBError(
            "no eligible OK runs found in ledger "
            "(need at least one row with status=='OK' and valid run_ts)"
        )

    # ISO Z timestamps are lexicographically sortable
    eligible.sort(key=lambda x: x.run_ts)
    return eligible[-1]


def verify_run_artifacts(repo_root: Path, row: LedgerRow) -> dict[str, Any]:
    """
    Deterministic verification gate:
      - resolves run_dir either via artifacts_path or artifacts/repo_cartographer/<run_id>
      - checks required files exist
      - checks MANIFEST/S EAL sidecar hashes match file bytes
      - (optional) checks ledger manifest_sha256 and seal_sha256 match computed (enforced here)
    """
    # Resolve run_dir deterministically
    run_dir: Path
    if row.artifacts_path:
        run_dir = (repo_root / row.artifacts_path).resolve()
    else:
        run_dir = (repo_root / ARTIFACTS_DIR_DEFAULT / row.run_id).resolve()

    manifest_path = run_dir / "MANIFEST.json"
    manifest_sha_path = run_dir / "MANIFEST.sha256"
    seal_path = run_dir / "SEAL.json"
    seal_sha_path = run_dir / "SEAL.sha256"

    required = [manifest_path, manifest_sha_path, seal_path, seal_sha_path]
    missing = [p.name for p in required if not p.exists()]

    result: dict[str, Any] = {
        "run_id": row.run_id,
        "run_ts": row.run_ts,
        "status": row.status,
        "artifacts_path": row.artifacts_path or str((Path(ARTIFACTS_DIR_DEFAULT) / row.run_id).as_posix()),
        "run_dir": run_dir.as_posix(),
        "ok": False,
        "missing": missing,
        "checks": {},
    }

    if missing:
        result["checks"]["files_present"] = False
        return result
    result["checks"]["files_present"] = True

    # Sidecar expected hashes
    expected_manifest = parse_sha256_sidecar(manifest_sha_path)
    expected_seal = parse_sha256_sidecar(seal_sha_path)
    result["checks"]["sidecars_parseable"] = bool(expected_manifest and expected_seal)
    if not expected_manifest or not expected_seal:
        return result

    actual_manifest = sha256_file(manifest_path)
    actual_seal = sha256_file(seal_path)

    result["checks"]["manifest_sidecar_match"] = (actual_manifest == expected_manifest)
    result["checks"]["seal_sidecar_match"] = (actual_seal == expected_seal)

    # Ledger ↔ actual checks (stronger guarantee)
    if row.manifest_sha256:
        result["checks"]["ledger_manifest_match"] = (row.manifest_sha256 == actual_manifest)
    else:
        result["checks"]["ledger_manifest_match"] = None

    if row.seal_sha256:
        result["checks"]["ledger_seal_match"] = (row.seal_sha256 == actual_seal)
    else:
        result["checks"]["ledger_seal_match"] = None

    # OK only if all boolean checks pass
    bool_checks = [
        result["checks"]["files_present"],
        result["checks"]["sidecars_parseable"],
        result["checks"]["manifest_sidecar_match"],
        result["checks"]["seal_sidecar_match"],
    ]
    # Ledger matches are optional only if absent; if present and False -> fail.
    if result["checks"]["ledger_manifest_match"] is False:
        bool_checks.append(False)
    if result["checks"]["ledger_seal_match"] is False:
        bool_checks.append(False)

    result["ok"] = all(x is True for x in bool_checks)
    return result


def build_pointer_payload(row: LedgerRow, verification: dict[str, Any]) -> dict[str, Any]:
    checks = verification.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    # Pointer consumers require these booleans to be strictly true. If ledger hash checks
    # are absent upstream, these values resolve to False and consumers fail closed.
    return {
        "LATEST_OK_RUN_ID": row.run_id,
        "LATEST_OK_RUN_TS": row.run_ts,
        "ok": verification.get("ok") is True,
        "ledger_manifest_match": checks.get("ledger_manifest_match") is True,
        "ledger_seal_match": checks.get("ledger_seal_match") is True,
        "manifest_sidecar_match": checks.get("manifest_sidecar_match") is True,
        "seal_sidecar_match": checks.get("seal_sidecar_match") is True,
    }


def write_json_atomic(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = out_path.with_name(out_path.name + ".tmp")
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    try:
        temp_path.write_text(content, encoding="utf-8")
        os.replace(temp_path, out_path)
    except OSError as exc:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass
        raise PhaseBError(f"failed writing JSON output: {out_path}") from exc


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Phase-B: select and verify latest OK cartographer run.")
    parser.add_argument("--ledger", default=LEDGER_PATH_DEFAULT, help="Path to JSONL run ledger.")
    parser.add_argument("--out", default=LATEST_OK_OUT_DEFAULT, help="Path to write latest OK run JSON.")
    parser.add_argument("--no-write", action="store_true", help="Do not write output file; print only.")
    parser.add_argument("--strict-verify", action="store_true", help="Exit nonzero if verification fails.")
    args = parser.parse_args(argv)

    repo_root = get_repo_root()
    ledger_path = (repo_root / args.ledger).resolve()
    out_path = (repo_root / args.out).resolve()
    pointer_path = (repo_root / POINTER_OUT_DEFAULT).resolve()

    if out_path == pointer_path and not args.no_write:
        print(
            f"ERROR: --out may not equal pointer path ({POINTER_OUT_DEFAULT}); "
            "legacy payload would violate pointer schema",
            file=sys.stderr,
        )
        return 2

    row = select_latest_ok_run(iter_ledger_rows(ledger_path))
    verification = verify_run_artifacts(repo_root, row)

    payload = {
        "schema_version": "REPO_CARTOGRAPHER_LATEST_OK_RUN_v0.1",
        "selected": row.raw,
        "verification": verification,
    }

    # Always print a minimal summary (deterministic)
    print(f"LATEST_OK_RUN_ID={row.run_id}")
    print(f"LATEST_OK_RUN_TS={row.run_ts}")
    print(f"VERIFY_OK={verification['ok']}")

    if not args.no_write:
        write_json_atomic(out_path, payload)
        print(f"WROTE={out_path.as_posix()}")
        # Preserve legacy --out payload while also emitting pointer artifact for downstream consumers.
        if out_path != pointer_path:
            pointer_payload = build_pointer_payload(row, verification)
            write_json_atomic(pointer_path, pointer_payload)
            print(f"WROTE_POINTER={pointer_path.as_posix()}")

    if args.strict_verify and not verification["ok"]:
        print("ERROR: verification failed for selected run", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
