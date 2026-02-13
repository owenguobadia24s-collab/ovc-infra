#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


LEDGER_SCHEMA_VERSION = "DEV_CHANGE_LEDGER_LINE_v0.1_backfill"
LEDGER_KEY_ORDER = [
    "author",
    "commit",
    "directories_touched",
    "generator",
    "notes",
    "paths_touched",
    "schema_version",
    "subject",
    "tags",
    "touched_file_count",
]
OVERLAY_KEY_ORDER = ["ambiguous", "base", "classes", "commit", "files", "unknown"]
TIMESTAMP_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SentinelError(RuntimeError):
    pass


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
        raise SentinelError(detail)
    return proc.stdout


def git_ref_exists(repo_root: Path, ref: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0


def ensure_ancestor(repo_root: Path, older: str, newer: str) -> None:
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise SentinelError(f"state commit {older} is not an ancestor of {newer}")


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
        raise SentinelError(detail)
    root = proc.stdout.strip()
    if not root:
        raise SentinelError("could not resolve repository root")
    return Path(root)


def normalize_path(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.lstrip("/")


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OVC append-only sentinel commit ingestion.")
    parser.add_argument(
        "--state",
        default="scripts/sentinel/sentinel_state.json",
        help="Path to sentinel state JSON file.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Do not write files; fail if run would produce any diffs.",
    )
    parser.add_argument(
        "--allow-unknown",
        action="store_true",
        help="Allow UNKNOWN and ambiguous classifications for newly ingested commits.",
    )
    return parser.parse_args(argv)


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        raise SentinelError(f"state file not found: {state_path}")
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SentinelError(f"state file JSON parse failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise SentinelError("state file must contain a JSON object")

    for key in ("last_processed_commit", "ledger_path", "overlay_path"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SentinelError(f"state field {key} must be a non-empty string")
    return payload


def validate_sha256_value(name: str, value: Any) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise SentinelError(f"state field {name} must be a lowercase sha256 hex string")
    return value


def validate_ledger_row(row: dict[str, Any], line_no: int | None) -> None:
    where = f"line {line_no}" if line_no is not None else "generated row"
    if set(row.keys()) != set(LEDGER_KEY_ORDER):
        raise SentinelError(f"ledger schema mismatch at {where}: unexpected keys")

    if row.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise SentinelError(f"ledger schema mismatch at {where}: invalid schema_version")

    author = row.get("author")
    if not isinstance(author, dict) or set(author.keys()) != {"name"}:
        raise SentinelError(f"ledger schema mismatch at {where}: invalid author")
    if not isinstance(author.get("name"), str):
        raise SentinelError(f"ledger schema mismatch at {where}: invalid author.name")

    commit = row.get("commit")
    if not isinstance(commit, dict) or set(commit.keys()) != {"hash", "timestamp_utc"}:
        raise SentinelError(f"ledger schema mismatch at {where}: invalid commit")
    commit_hash = commit.get("hash")
    timestamp_utc = commit.get("timestamp_utc")
    if not isinstance(commit_hash, str) or not COMMIT_RE.fullmatch(commit_hash):
        raise SentinelError(f"ledger schema mismatch at {where}: invalid commit.hash")
    if not isinstance(timestamp_utc, str) or not TIMESTAMP_UTC_RE.fullmatch(timestamp_utc):
        raise SentinelError(f"ledger schema mismatch at {where}: invalid commit.timestamp_utc")

    for key in ("directories_touched", "notes", "paths_touched", "tags"):
        value = row.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise SentinelError(f"ledger schema mismatch at {where}: invalid {key}")

    touched_count = row.get("touched_file_count")
    if not isinstance(touched_count, int) or touched_count < 0:
        raise SentinelError(f"ledger schema mismatch at {where}: invalid touched_file_count")
    if touched_count != len(row["paths_touched"]):
        raise SentinelError(f"ledger schema mismatch at {where}: touched_file_count mismatch")

    if not isinstance(row.get("subject"), str):
        raise SentinelError(f"ledger schema mismatch at {where}: invalid subject")

    generator = row.get("generator")
    if not isinstance(generator, dict) or set(generator.keys()) != {"tool", "version"}:
        raise SentinelError(f"ledger schema mismatch at {where}: invalid generator")
    if not isinstance(generator.get("tool"), str) or not isinstance(generator.get("version"), str):
        raise SentinelError(f"ledger schema mismatch at {where}: invalid generator values")


def validate_overlay_row(row: dict[str, Any], line_no: int | None) -> None:
    where = f"line {line_no}" if line_no is not None else "generated row"
    if set(row.keys()) != set(OVERLAY_KEY_ORDER):
        raise SentinelError(f"overlay schema mismatch at {where}: unexpected keys")

    commit_hash = row.get("commit")
    if not isinstance(commit_hash, str) or not COMMIT_RE.fullmatch(commit_hash):
        raise SentinelError(f"overlay schema mismatch at {where}: invalid commit")

    classes = row.get("classes")
    if not isinstance(classes, list) or not classes or not all(isinstance(item, str) and item for item in classes):
        raise SentinelError(f"overlay schema mismatch at {where}: invalid classes")

    if not isinstance(row.get("unknown"), bool):
        raise SentinelError(f"overlay schema mismatch at {where}: invalid unknown")
    if not isinstance(row.get("ambiguous"), bool):
        raise SentinelError(f"overlay schema mismatch at {where}: invalid ambiguous")
    if row["ambiguous"] != (len(classes) > 1):
        raise SentinelError(f"overlay schema mismatch at {where}: ambiguous mismatch")
    if row["unknown"] and classes != ["UNKNOWN"]:
        raise SentinelError(f"overlay schema mismatch at {where}: unknown mismatch")

    base = row.get("base")
    if not isinstance(base, str) or base != f"{commit_hash}^":
        raise SentinelError(f"overlay schema mismatch at {where}: invalid base")

    files = row.get("files")
    if not isinstance(files, int) or files < 0:
        raise SentinelError(f"overlay schema mismatch at {where}: invalid files")


def parse_ledger_file(ledger_path: Path) -> tuple[list[dict[str, Any]], bytes]:
    if not ledger_path.exists():
        raise SentinelError(f"ledger file not found: {ledger_path}")
    ledger_bytes = ledger_path.read_bytes()
    if ledger_bytes and not ledger_bytes.endswith(b"\n"):
        raise SentinelError("ledger schema mismatch: ledger must be newline-terminated")

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    text = ledger_bytes.decode("utf-8")
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise SentinelError(f"ledger schema mismatch at line {line_no}: invalid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise SentinelError(f"ledger schema mismatch at line {line_no}: row must be object")
        validate_ledger_row(payload, line_no)
        commit_hash = payload["commit"]["hash"]
        if commit_hash in seen:
            raise SentinelError(f"duplicate commit sha in ledger: {commit_hash}")
        seen.add(commit_hash)
        rows.append(payload)
    return rows, ledger_bytes


def parse_overlay_file(overlay_path: Path) -> bytes:
    if not overlay_path.exists():
        return b""
    overlay_bytes = overlay_path.read_bytes()
    if overlay_bytes and not overlay_bytes.endswith(b"\n"):
        raise SentinelError("overlay schema mismatch: overlay must be newline-terminated")
    text = overlay_bytes.decode("utf-8")
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise SentinelError(f"overlay schema mismatch at line {line_no}: invalid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise SentinelError(f"overlay schema mismatch at line {line_no}: row must be object")
        validate_overlay_row(payload, line_no)
    return overlay_bytes


def extract_target_hash_from_seal(seal_payload: dict[str, Any], target_path: Path, repo_root: Path) -> str | None:
    target = seal_payload.get("target")
    if isinstance(target, dict):
        target_hash = target.get("sha256")
        if isinstance(target_hash, str) and SHA256_RE.fullmatch(target_hash):
            return target_hash

    artifacts = seal_payload.get("artifacts")
    if isinstance(artifacts, dict):
        rel_target = relpath_posix(target_path, repo_root)
        for key, value in artifacts.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            if key == rel_target or key == target_path.name or key.endswith(f"/{target_path.name}"):
                candidate = value.get("sha256")
                if isinstance(candidate, str) and SHA256_RE.fullmatch(candidate):
                    return candidate
    return None


def enforce_hash_from_existing_seal(target_path: Path, repo_root: Path, target_bytes: bytes) -> None:
    seal_json_path = target_path.with_suffix(".seal.json")
    if not seal_json_path.exists():
        return
    try:
        payload = json.loads(seal_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SentinelError(f"seal parse failed for {seal_json_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SentinelError(f"seal parse failed for {seal_json_path}: payload must be object")
    expected_hash = extract_target_hash_from_seal(payload, target_path, repo_root)
    if expected_hash is None:
        return
    actual_hash = sha256_bytes(target_bytes)
    if expected_hash != actual_hash:
        raise SentinelError(f"non-append mutation detected for {relpath_posix(target_path, repo_root)}")


def enforce_optional_state_hash(
    state: dict[str, Any],
    key_name: str,
    target_path: Path,
    target_bytes: bytes | None,
    repo_root: Path,
) -> None:
    if key_name not in state:
        return
    expected = validate_sha256_value(key_name, state[key_name])
    if target_bytes is None:
        raise SentinelError(f"state hash is set for missing file: {relpath_posix(target_path, repo_root)}")
    actual = sha256_bytes(target_bytes)
    if actual != expected:
        if key_name == "ledger_sha256":
            raise SentinelError("non-append mutation detected for ledger content")
        raise SentinelError(f"state hash mismatch for {relpath_posix(target_path, repo_root)}")


def load_classifier(classifier_path: Path) -> Callable[[list[str]], dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("sentinel_classifier", classifier_path)
    if spec is None or spec.loader is None:
        raise SentinelError(f"failed to load classifier from {classifier_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    classify_paths = getattr(module, "classify_paths", None)
    if not callable(classify_paths):
        raise SentinelError("classifier module missing classify_paths")
    return classify_paths


def classify_paths_payload(
    classify_paths: Callable[[list[str]], dict[str, Any]],
    paths: list[str],
) -> tuple[list[str], bool, bool, bool]:
    payload = classify_paths(paths)
    if not isinstance(payload, dict):
        raise SentinelError("classifier returned invalid payload (not object)")
    classes = payload.get("classes")
    if not isinstance(classes, list) or not all(isinstance(item, str) and item for item in classes):
        raise SentinelError("classifier returned invalid classes payload")
    if not classes:
        classes = ["UNKNOWN"]
    unknown_only = classes == ["UNKNOWN"]
    ambiguous = len(classes) > 1
    contains_unknown = "UNKNOWN" in classes
    return classes, unknown_only, ambiguous, contains_unknown


def collect_commit_paths(repo_root: Path, commit_hash: str) -> tuple[list[str], list[str]]:
    notes: list[str] = []
    raw = run_git(repo_root, ["diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash])
    paths = [normalize_path(line) for line in raw.splitlines() if line.strip()]
    if not paths:
        raw = run_git(repo_root, ["diff-tree", "--no-commit-id", "--name-only", "-m", "-r", commit_hash])
        paths = [normalize_path(line) for line in raw.splitlines() if line.strip()]
        if paths:
            notes.append("merge fallback used")
    if not paths:
        raw = run_git(repo_root, ["show", "--no-color", "--pretty=format:", "--name-only", commit_hash])
        paths = [normalize_path(line) for line in raw.splitlines() if line.strip()]
        if paths:
            notes.append("ROOT show fallback used")
    if not paths:
        notes.append("empty diff-tree output")

    unique_paths: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)
    return unique_paths, notes


def read_commit_metadata(repo_root: Path, commit_hash: str) -> tuple[str, str, str, str]:
    raw = run_git(
        repo_root,
        ["show", "--no-color", "--no-patch", "--pretty=format:%H%x00%ct%x00%an%x00%s", commit_hash],
    )
    fields = raw.split("\x00")
    if len(fields) != 4:
        raise SentinelError(f"unexpected commit metadata for {commit_hash}")
    output_hash, ts_raw, author_name, subject = fields
    try:
        ts = int(ts_raw.strip())
    except ValueError as exc:
        raise SentinelError(f"invalid commit timestamp for {commit_hash}") from exc
    timestamp_utc = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return output_hash.strip(), timestamp_utc, author_name.rstrip("\n"), subject.rstrip("\n")


def top_level_dir(path: str) -> str:
    if "/" in path:
        return path.split("/", 1)[0] + "/"
    return "/"


def derive_tags(paths: list[str]) -> list[str]:
    tags: set[str] = set()
    for path in paths:
        parts = path.split("/")
        basename_upper = Path(path).name.upper()

        if path.startswith("docs/governance/") or path.startswith("docs/contracts/"):
            tags.add("governance_contracts")
        if path.startswith("docs/operations/") or "OPERATING" in basename_upper:
            tags.add("operations")
        if path.startswith("docs/REPO_MAP/"):
            tags.add("repo_map")
        if path.startswith("docs/catalogs/"):
            tags.add("catalogs")
        if path.startswith("docs/validation/") or "audit" in path.lower() or "validation" in path.lower():
            tags.add("validation")

        if path.startswith("scripts/governance/"):
            tags.add("governance_tooling")
        elif path.startswith("scripts/"):
            tags.add("scripts_general")

        if path.startswith("tools/phase3_control_panel/"):
            tags.add("control_panel")
        elif path.startswith("tools/audit_interpreter/"):
            tags.add("audit_interpreter")
        elif path.startswith("tools/"):
            tags.add("tools_general")

        if path.startswith("reports/") or (parts and parts[0] == "sql" and not path.startswith("docs/")):
            tags.add("evidence_runs")

        if path.startswith(".github/") or path.startswith("configs/"):
            tags.add("ci_workflows")

        simple_map = {
            "contracts": "contracts",
            "CLAIMS": "claims",
            "data": "data",
            "infra": "infra",
            "research": "research",
            "specs": "specs",
            "schema": "schema",
            "src": "source_code",
            "tests": "tests",
            "testdir": "tests",
            "testdir2": "tests",
            "Tetsu": "repo_maze",
            "artifacts": "artifacts",
            "releases": "releases",
            "trajectory_families": "trajectory",
            "pine": "pine",
            "chmod_test": "chmod_test",
        }
        if parts and parts[0] in simple_map:
            tags.add(simple_map[parts[0]])

        if path.startswith(".codex/"):
            tags.add("codex_runtime")

    return sorted(tags)


def build_ledger_row(
    commit_hash: str,
    timestamp_utc: str,
    author_name: str,
    subject: str,
    paths_touched: list[str],
    notes: list[str],
) -> dict[str, Any]:
    directories = sorted({top_level_dir(path) for path in paths_touched})
    return {
        "author": {"name": author_name},
        "commit": {"hash": commit_hash, "timestamp_utc": timestamp_utc},
        "directories_touched": directories,
        "generator": {"tool": "append_sentinel.py", "version": "0.1"},
        "notes": notes,
        "paths_touched": paths_touched,
        "schema_version": LEDGER_SCHEMA_VERSION,
        "subject": subject,
        "tags": derive_tags(paths_touched),
        "touched_file_count": len(paths_touched),
    }


def serialize_jsonl(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    lines = [json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_overlay_rows(
    ledger_rows: list[dict[str, Any]],
    classify_paths: Callable[[list[str]], dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in ledger_rows:
        commit_hash = row["commit"]["hash"]
        paths = row["paths_touched"]
        classes, unknown_only, ambiguous, _ = classify_paths_payload(classify_paths, paths)
        record = {
            "ambiguous": ambiguous,
            "base": f"{commit_hash}^",
            "classes": classes,
            "commit": commit_hash,
            "files": len(paths),
            "unknown": unknown_only,
        }
        validate_overlay_row(record, None)
        records.append(record)
    return records


def artifact_info(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def seal_payload_bytes(
    name: str,
    target_path: Path,
    target_bytes: bytes,
    repo_root: Path,
    script_path: Path,
    classifier_path: Path,
    source_ledger_path: Path | None = None,
    source_ledger_bytes: bytes | None = None,
) -> bytes:
    payload: dict[str, Any] = {
        "kind": "APPEND_SENTINEL_FILE_SEAL",
        "name": name,
        "target": {
            "bytes": len(target_bytes),
            "path": relpath_posix(target_path, repo_root),
            "sha256": sha256_bytes(target_bytes),
        },
        "version": "0.1",
        "inputs": {
            relpath_posix(script_path, repo_root): artifact_info(script_path),
            relpath_posix(classifier_path, repo_root): artifact_info(classifier_path),
        },
    }
    if source_ledger_path is not None and source_ledger_bytes is not None:
        payload["source_ledger"] = {
            "bytes": len(source_ledger_bytes),
            "path": relpath_posix(source_ledger_path, repo_root),
            "sha256": sha256_bytes(source_ledger_bytes),
        }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def state_payload_bytes(
    current_state: dict[str, Any],
    repo_root: Path,
    ledger_path: Path,
    overlay_path: Path,
    last_processed_commit: str,
    ledger_hash: str,
    overlay_hash: str,
) -> bytes:
    next_state = dict(current_state)
    next_state["last_processed_commit"] = last_processed_commit
    next_state["ledger_path"] = relpath_posix(ledger_path, repo_root)
    next_state["overlay_path"] = relpath_posix(overlay_path, repo_root)
    next_state["ledger_sha256"] = ledger_hash
    next_state["overlay_sha256"] = overlay_hash
    if "state_version" not in next_state:
        next_state["state_version"] = "0.1"
    return (json.dumps(next_state, indent=2, sort_keys=True) + "\n").encode("utf-8")


def managed_match(path: str, managed_exact: set[str]) -> bool:
    normalized = normalize_path(path)
    if normalized in managed_exact:
        return True
    if normalized.startswith("scripts/sentinel/"):
        return True
    if normalized == ".github/workflows/append_sentinel.yml":
        return True
    return False


def is_state_only_commit(paths: list[str], state_relpath: str) -> bool:
    if not paths:
        return False
    return all(normalize_path(path) == state_relpath for path in paths)


def write_if_changed(path: Path, content: bytes) -> None:
    if path.exists() and path.read_bytes() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        repo_root = get_repo_root()
        state_path = resolve_repo_path(args.state, repo_root)
        state = load_state(state_path)

        ledger_path = resolve_repo_path(state["ledger_path"], repo_root)
        overlay_path = resolve_repo_path(state["overlay_path"], repo_root)
        classifier_path = repo_root / "scripts" / "governance" / "classify_change.py"
        script_path = Path(__file__).resolve()
        if not classifier_path.exists():
            raise SentinelError(f"classifier script not found: {classifier_path}")

        ledger_rows, ledger_bytes = parse_ledger_file(ledger_path)
        overlay_bytes = parse_overlay_file(overlay_path)

        enforce_optional_state_hash(state, "ledger_sha256", ledger_path, ledger_bytes, repo_root)
        enforce_optional_state_hash(
            state,
            "overlay_sha256",
            overlay_path,
            overlay_bytes if overlay_path.exists() else None,
            repo_root,
        )
        enforce_hash_from_existing_seal(ledger_path, repo_root, ledger_bytes)
        enforce_hash_from_existing_seal(overlay_path, repo_root, overlay_bytes)

        last_processed = state["last_processed_commit"]
        if not git_ref_exists(repo_root, last_processed):
            raise SentinelError(f"last_processed_commit not found: {last_processed}")
        head = run_git(repo_root, ["rev-parse", "HEAD"]).strip()
        if not head:
            raise SentinelError("could not resolve HEAD")
        ensure_ancestor(repo_root, last_processed, head)

        commits = [
            line.strip()
            for line in run_git(
                repo_root,
                ["rev-list", "--reverse", "--topo-order", f"{last_processed}..{head}"],
            ).splitlines()
            if line.strip()
        ]
        state_relpath = relpath_posix(state_path, repo_root)

        managed_exact = {
            relpath_posix(ledger_path, repo_root),
            relpath_posix(ledger_path.with_suffix(".seal.json"), repo_root),
            relpath_posix(ledger_path.with_suffix(".seal.sha256"), repo_root),
            relpath_posix(overlay_path, repo_root),
            relpath_posix(overlay_path.with_suffix(".seal.json"), repo_root),
            relpath_posix(overlay_path.with_suffix(".seal.sha256"), repo_root),
            state_relpath,
            ".github/workflows/append_sentinel.yml",
        }

        classify_paths = load_classifier(classifier_path)
        existing_hashes = {row["commit"]["hash"] for row in ledger_rows}
        new_rows: list[dict[str, Any]] = []
        expected_last_processed = last_processed

        for commit_hash in commits:
            paths, notes = collect_commit_paths(repo_root, commit_hash)
            if is_state_only_commit(paths, state_relpath):
                continue
            if paths and all(managed_match(path, managed_exact) for path in paths):
                expected_last_processed = commit_hash
                continue

            classes, _unknown_only, ambiguous, contains_unknown = classify_paths_payload(classify_paths, paths)
            if not args.allow_unknown and (ambiguous or contains_unknown):
                joined = ",".join(classes)
                raise SentinelError(
                    f"classification blocked for commit {commit_hash}: classes={joined} "
                    "(use --allow-unknown to override)"
                )

            out_hash, timestamp_utc, author_name, subject = read_commit_metadata(repo_root, commit_hash)
            if out_hash != commit_hash:
                raise SentinelError(f"commit metadata mismatch for {commit_hash}")

            row = build_ledger_row(
                commit_hash=commit_hash,
                timestamp_utc=timestamp_utc,
                author_name=author_name,
                subject=subject,
                paths_touched=paths,
                notes=notes,
            )
            validate_ledger_row(row, None)
            row_hash = row["commit"]["hash"]
            if row_hash in existing_hashes:
                raise SentinelError(f"duplicate commit sha in ledger: {row_hash}")
            existing_hashes.add(row_hash)
            new_rows.append(row)
            expected_last_processed = commit_hash

        append_bytes = serialize_jsonl(new_rows)
        candidate_ledger_bytes = ledger_bytes + append_bytes
        if not candidate_ledger_bytes.startswith(ledger_bytes):
            raise SentinelError("non-append mutation detected for ledger content")

        candidate_ledger_rows = ledger_rows + new_rows
        if len({row["commit"]["hash"] for row in candidate_ledger_rows}) != len(candidate_ledger_rows):
            raise SentinelError("duplicate commit sha in ledger")

        overlay_rows_a = build_overlay_rows(candidate_ledger_rows, classify_paths)
        overlay_rows_b = build_overlay_rows(candidate_ledger_rows, classify_paths)
        overlay_bytes_a = serialize_jsonl(overlay_rows_a)
        overlay_bytes_b = serialize_jsonl(overlay_rows_b)
        if overlay_bytes_a != overlay_bytes_b:
            raise SentinelError("overlay mismatch vs deterministic rebuild")

        ledger_seal_json_path = ledger_path.with_suffix(".seal.json")
        ledger_seal_sha_path = ledger_path.with_suffix(".seal.sha256")
        overlay_seal_json_path = overlay_path.with_suffix(".seal.json")
        overlay_seal_sha_path = overlay_path.with_suffix(".seal.sha256")

        expected_ledger_seal_json = seal_payload_bytes(
            name="ledger",
            target_path=ledger_path,
            target_bytes=candidate_ledger_bytes,
            repo_root=repo_root,
            script_path=script_path,
            classifier_path=classifier_path,
        )
        expected_ledger_seal_sha = (
            f"{sha256_bytes(expected_ledger_seal_json)}  {ledger_seal_json_path.name}\n".encode("utf-8")
        )

        expected_overlay_seal_json = seal_payload_bytes(
            name="overlay",
            target_path=overlay_path,
            target_bytes=overlay_bytes_a,
            repo_root=repo_root,
            script_path=script_path,
            classifier_path=classifier_path,
            source_ledger_path=ledger_path,
            source_ledger_bytes=candidate_ledger_bytes,
        )
        expected_overlay_seal_sha = (
            f"{sha256_bytes(expected_overlay_seal_json)}  {overlay_seal_json_path.name}\n".encode("utf-8")
        )

        expected_state_bytes = state_payload_bytes(
            current_state=state,
            repo_root=repo_root,
            ledger_path=ledger_path,
            overlay_path=overlay_path,
            last_processed_commit=expected_last_processed,
            ledger_hash=sha256_bytes(candidate_ledger_bytes),
            overlay_hash=sha256_bytes(overlay_bytes_a),
        )
        current_state_bytes = state_path.read_bytes()

        diffs: list[str] = []
        if candidate_ledger_bytes != ledger_bytes:
            diffs.append(relpath_posix(ledger_path, repo_root))
        if overlay_bytes_a != overlay_bytes:
            diffs.append(relpath_posix(overlay_path, repo_root))

        current_ledger_seal_json = ledger_seal_json_path.read_bytes() if ledger_seal_json_path.exists() else b""
        current_ledger_seal_sha = ledger_seal_sha_path.read_bytes() if ledger_seal_sha_path.exists() else b""
        current_overlay_seal_json = overlay_seal_json_path.read_bytes() if overlay_seal_json_path.exists() else b""
        current_overlay_seal_sha = overlay_seal_sha_path.read_bytes() if overlay_seal_sha_path.exists() else b""

        if expected_ledger_seal_json != current_ledger_seal_json:
            diffs.append(relpath_posix(ledger_seal_json_path, repo_root))
        if expected_ledger_seal_sha != current_ledger_seal_sha:
            diffs.append(relpath_posix(ledger_seal_sha_path, repo_root))
        if expected_overlay_seal_json != current_overlay_seal_json:
            diffs.append(relpath_posix(overlay_seal_json_path, repo_root))
        if expected_overlay_seal_sha != current_overlay_seal_sha:
            diffs.append(relpath_posix(overlay_seal_sha_path, repo_root))
        if expected_state_bytes != current_state_bytes:
            diffs.append(relpath_posix(state_path, repo_root))

        if args.verify:
            if diffs:
                raise SentinelError("verify detected diffs: " + ", ".join(sorted(set(diffs))))
            return 0

        if append_bytes:
            with ledger_path.open("ab") as handle:
                handle.write(append_bytes)
        final_ledger_bytes = ledger_path.read_bytes()
        if final_ledger_bytes != candidate_ledger_bytes:
            raise SentinelError("ledger write verification failed")

        write_if_changed(overlay_path, overlay_bytes_a)
        write_if_changed(ledger_seal_json_path, expected_ledger_seal_json)
        write_if_changed(ledger_seal_sha_path, expected_ledger_seal_sha)
        write_if_changed(overlay_seal_json_path, expected_overlay_seal_json)
        write_if_changed(overlay_seal_sha_path, expected_overlay_seal_sha)
        write_if_changed(state_path, expected_state_bytes)

        if overlay_path.read_bytes() != overlay_bytes_a:
            raise SentinelError("overlay write verification failed")
        if ledger_seal_json_path.read_bytes() != expected_ledger_seal_json:
            raise SentinelError("ledger seal JSON write verification failed")
        if ledger_seal_sha_path.read_bytes() != expected_ledger_seal_sha:
            raise SentinelError("ledger seal SHA write verification failed")
        if overlay_seal_json_path.read_bytes() != expected_overlay_seal_json:
            raise SentinelError("overlay seal JSON write verification failed")
        if overlay_seal_sha_path.read_bytes() != expected_overlay_seal_sha:
            raise SentinelError("overlay seal SHA write verification failed")
        if state_path.read_bytes() != expected_state_bytes:
            raise SentinelError("state write verification failed")

        return 0
    except SentinelError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
