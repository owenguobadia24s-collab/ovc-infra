#!/usr/bin/env python3
"""Build DEV Change Classification Overlay v0.2.

Reuses the v0.1 builder infrastructure with the updated classifier (v0.2 rules).
Produces overlay JSONL + seal files with version "0.2".
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

# Import all shared functions from the v0.1 builder
from build_change_classification_overlay_v0_1 import (
    collect_commit_files,
    get_repo_root,
    normalize_seal_path,
    read_ledger_commits,
    resolve_repo_path,
    run_git,
    sha256_bytes,
    write_overlay_jsonl,
    write_text,
    artifact_info,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build DEV Change Classification Overlay v0.2.")
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
        "version": "0.2",
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


def commit_has_parent(commit_hash: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{commit_hash}^"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0


def collect_root_commit_files(commit_hash: str) -> list[str]:
    output = run_git(["show", "--no-color", "--pretty=format:", "--name-only", commit_hash])
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_classifier_module(classifier_path: Path):
    spec = importlib.util.spec_from_file_location("overlay_v02_classifier_module", str(classifier_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load classifier module from {classifier_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    classify_paths = getattr(module, "classify_paths", None)
    if classify_paths is None:
        raise RuntimeError("classifier module missing classify_paths function")
    return module


def classify_files(module, files: list[str], commit_hash: str) -> tuple[list[str], bool, bool]:
    payload = module.classify_paths(files)
    classes = payload.get("classes")
    if not isinstance(classes, list) or not all(isinstance(c, str) and c for c in classes):
        raise RuntimeError(f"classifier returned invalid classes for commit {commit_hash}")
    if not classes:
        classes = ["UNKNOWN"]
    unknown = classes == ["UNKNOWN"]
    ambiguous = len(classes) > 1
    return classes, unknown, ambiguous


def build_overlay_records_v0_2(classifier_path: Path, commits: list[str]) -> list[dict]:
    records: list[dict] = []
    classifier_module = load_classifier_module(classifier_path)
    for commit_hash in commits:
        if commit_has_parent(commit_hash):
            file_list = collect_commit_files(commit_hash)
        else:
            file_list = collect_root_commit_files(commit_hash)
        classes, unknown, ambiguous = classify_files(classifier_module, file_list, commit_hash)
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
        overlay_records = build_overlay_records_v0_2(classifier_path=classifier_path, commits=commits)
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
