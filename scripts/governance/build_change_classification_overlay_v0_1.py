#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed"
        raise RuntimeError(detail)
    return proc.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_repo_root() -> Path:
    root = run_git(["rev-parse", "--show-toplevel"]).strip()
    if not root:
        raise RuntimeError("could not resolve git repo root")
    return Path(root)


def normalize_seal_path(path: Path, root: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def resolve_repo_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (repo_root.resolve() / path).resolve()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build DEV Change Classification Overlay v0.1.")
    parser.add_argument("--out", required=True, help="Overlay JSONL output path.")
    parser.add_argument(
        "--ledger",
        default="docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl",
        help="Ledger JSONL input path.",
    )
    parser.add_argument(
        "--classifier",
        default="scripts/governance/classify_change.py",
        help="Classifier script path.",
    )
    parser.add_argument("--seal-json", help="Seal JSON output path.")
    parser.add_argument("--seal-sha256", help="Seal SHA256 output path.")
    return parser.parse_args(argv)


def read_ledger_commits(ledger_path: Path) -> list[str]:
    commits: list[str] = []
    for line_no, raw_line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid ledger JSON at line {line_no}: {exc}") from exc
        commit_hash = payload.get("commit", {}).get("hash")
        if not isinstance(commit_hash, str) or not commit_hash:
            raise RuntimeError(f"missing commit hash in ledger line {line_no}")
        commits.append(commit_hash)
    if not commits:
        raise RuntimeError("ledger has no commit lines")
    return commits


def ensure_parent_exists(commit_hash: str) -> None:
    base_ref = f"{commit_hash}^"
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", base_ref],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"commit has no parent for per-commit diff: {commit_hash}")


def collect_commit_files(commit_hash: str) -> list[str]:
    base_ref = f"{commit_hash}^"
    output = run_git(["diff", "--name-only", base_ref, commit_hash])
    return [line.strip() for line in output.splitlines() if line.strip()]


def parse_classifier_json(stdout: str, commit_hash: str) -> dict:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"classifier produced no output for commit {commit_hash}")
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"classifier JSON parse failed for commit {commit_hash}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"classifier JSON is not an object for commit {commit_hash}")
    return payload


def classify_commit(classifier_path: Path, commit_hash: str) -> tuple[list[str], bool, bool]:
    base_ref = f"{commit_hash}^"
    proc = subprocess.run(
        [sys.executable, str(classifier_path), "--range", f"{base_ref}..{commit_hash}", "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload = parse_classifier_json(proc.stdout, commit_hash)
    if proc.returncode not in (0, 2):
        detail = proc.stderr.strip() or proc.stdout.strip() or "classifier failed"
        raise RuntimeError(f"classifier failed for commit {commit_hash}: {detail}")
    if proc.returncode == 2:
        classes = ["UNKNOWN"]
    else:
        classes = payload.get("classes")
        if not isinstance(classes, list) or not classes or not all(isinstance(name, str) and name for name in classes):
            raise RuntimeError(f"classifier returned invalid classes for commit {commit_hash}")
    unknown = classes == ["UNKNOWN"]
    ambiguous = len(classes) > 1
    return classes, unknown, ambiguous


def build_overlay_records(classifier_path: Path, commits: list[str]) -> list[dict]:
    records: list[dict] = []
    for commit_hash in commits:
        ensure_parent_exists(commit_hash)
        file_list = collect_commit_files(commit_hash)
        classes, unknown, ambiguous = classify_commit(classifier_path, commit_hash)
        records.append(
            {
                "commit": commit_hash,
                "classes": classes,
                "unknown": unknown,
                "ambiguous": ambiguous,
                "files": len(file_list),
                "base": f"{commit_hash}^",
            }
        )
    return records


def write_overlay_jsonl(records: list[dict], out_path: Path) -> None:
    lines = [json.dumps(record, sort_keys=True, separators=(",", ":")) for record in records]
    payload = ("\n".join(lines) + "\n") if lines else ""
    write_text(out_path, payload)


def artifact_info(path: Path) -> dict:
    return {
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def build_seal_payload(
    out_path: Path,
    ledger_path: Path,
    generator_path: Path,
    classifier_path: Path,
    commits: list[str],
    repo_root: Path,
) -> dict:
    return {
        "kind": "DEV_CHANGE_CLASSIFICATION_OVERLAY_SEAL",
        "version": "0.1",
        "range": {"from": commits[0], "to": commits[-1]},
        "sha_policy": "sha256 in .seal.sha256 is computed over UTF-8 bytes of this seal JSON as written",
        "artifacts": {
            normalize_seal_path(out_path, repo_root): artifact_info(out_path),
            normalize_seal_path(ledger_path, repo_root): artifact_info(ledger_path),
            normalize_seal_path(generator_path, repo_root): artifact_info(generator_path),
            normalize_seal_path(classifier_path, repo_root): artifact_info(classifier_path),
        },
    }


def write_seal_files(seal_payload: dict, seal_json_path: Path, seal_sha256_path: Path) -> None:
    seal_text = json.dumps(seal_payload, indent=2, sort_keys=True) + "\n"
    write_text(seal_json_path, seal_text)
    seal_hash = sha256_bytes(seal_text.encode("utf-8"))
    write_text(seal_sha256_path, f"{seal_hash}  {seal_json_path.name}\n")


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)

        repo_root = get_repo_root()
        out_path = resolve_repo_path(Path(args.out), repo_root)
        ledger_path = resolve_repo_path(Path(args.ledger), repo_root)
        classifier_path = resolve_repo_path(Path(args.classifier), repo_root)
        seal_json_path = (
            resolve_repo_path(Path(args.seal_json), repo_root)
            if args.seal_json
            else out_path.with_suffix(".seal.json")
        )
        seal_sha256_path = (
            resolve_repo_path(Path(args.seal_sha256), repo_root)
            if args.seal_sha256
            else out_path.with_suffix(".seal.sha256")
        )
        generator_path = Path(__file__)

        commits = read_ledger_commits(ledger_path)
        overlay_records = build_overlay_records(classifier_path=classifier_path, commits=commits)
        write_overlay_jsonl(overlay_records, out_path)

        seal_payload = build_seal_payload(
            out_path=out_path,
            ledger_path=ledger_path,
            generator_path=generator_path,
            classifier_path=classifier_path,
            commits=commits,
            repo_root=repo_root,
        )
        write_seal_files(seal_payload=seal_payload, seal_json_path=seal_json_path, seal_sha256_path=seal_sha256_path)
        return 0
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
