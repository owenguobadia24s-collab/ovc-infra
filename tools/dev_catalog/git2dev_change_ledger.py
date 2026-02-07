#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
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
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        detail = stderr or stdout or f"git {' '.join(args)} failed with exit {proc.returncode}"
        raise RuntimeError(detail)
    return proc.stdout


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def dir_prefix(path: str, depth: int) -> str:
    norm = normalize_path(path).strip("/")
    parts = [p for p in norm.split("/") if p]
    if len(parts) <= 1:
        return "."
    dirs = parts[:-1]
    return "/".join(dirs[:depth]) if dirs else "."


def parse_header(commit: str) -> dict:
    raw = run_git(
        [
            "show",
            "--no-color",
            "--no-patch",
            "--pretty=format:%H%x00%P%x00%an%x00%ae%x00%cn%x00%ce%x00%ct%x00%s",
            commit,
        ]
    )
    fields = raw.split("\x00")
    if len(fields) != 8:
        raise RuntimeError(f"unexpected header field count for commit {commit}: {len(fields)}")

    commit_hash, parents_raw, an, ae, cn, ce, ts_raw, subject = fields
    try:
        ts = int(ts_raw.strip())
    except ValueError as exc:
        raise RuntimeError(f"invalid unix timestamp for commit {commit}: {ts_raw!r}") from exc
    timestamp_utc = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    parent_list = [p for p in parents_raw.strip().split(" ") if p]
    parent_list = sorted(set(parent_list))

    return {
        "hash": commit_hash.strip(),
        "parents": parent_list,
        "author_name": an,
        "author_email": ae,
        "committer_name": cn,
        "committer_email": ce,
        "timestamp_utc": timestamp_utc,
        "subject": subject.rstrip("\n"),
    }


def parse_numstat(commit: str) -> dict:
    raw = run_git(["show", "--no-color", "--pretty=format:", "--numstat", commit])
    insertions = 0
    deletions = 0
    files = 0

    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ins_raw, del_raw = parts[0], parts[1]
        ins = 0 if ins_raw == "-" else int(ins_raw)
        dele = 0 if del_raw == "-" else int(del_raw)
        insertions += ins
        deletions += dele
        files += 1

    return {"files": files, "insertions": insertions, "deletions": deletions}


def parse_name_status(commit: str) -> dict:
    raw = run_git(["show", "--no-color", "--pretty=format:", "--name-status", "-M", commit])
    added: set[str] = set()
    modified: set[str] = set()
    deleted: set[str] = set()
    renamed_set: set[tuple[str, str]] = set()

    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        if not status:
            continue

        code = status[0]

        if code == "A" and len(parts) >= 2:
            added.add(normalize_path(parts[1]))
        elif code == "M" and len(parts) >= 2:
            modified.add(normalize_path(parts[1]))
        elif code == "D" and len(parts) >= 2:
            deleted.add(normalize_path(parts[1]))
        elif code == "R" and len(parts) >= 3:
            old_path = normalize_path(parts[1])
            new_path = normalize_path(parts[2])
            renamed_set.add((old_path, new_path))
        else:
            dest = None
            if len(parts) >= 3:
                dest = parts[2]
            elif len(parts) >= 2:
                dest = parts[1]
            if dest is not None:
                modified.add(normalize_path(dest))

    renamed = [{"from": old, "to": new} for old, new in sorted(renamed_set, key=lambda x: (x[0], x[1]))]
    return {
        "added": sorted(added),
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "renamed": renamed,
    }


def build_record(commit_hash: str, dir_depth: int) -> dict:
    header = parse_header(commit_hash)
    stats = parse_numstat(commit_hash)
    paths = parse_name_status(commit_hash)

    touched: set[str] = set(paths["added"]) | set(paths["modified"]) | set(paths["deleted"])
    for entry in paths["renamed"]:
        touched.add(entry["from"])
        touched.add(entry["to"])

    directories_touched = sorted({dir_prefix(path, dir_depth) for path in touched})

    record = {
        "schema_version": "DEV_CHANGE_LEDGER_LINE_v0.1",
        "commit": {
            "hash": header["hash"],
            "timestamp_utc": header["timestamp_utc"],
        },
        "author": {
            "name": header["author_name"],
            "email": header["author_email"],
        },
        "committer": {
            "name": header["committer_name"],
            "email": header["committer_email"],
        },
        "subject": header["subject"],
        "parents": header["parents"],
        "stats": stats,
        "paths": paths,
        "phase_hint": None,
        "intent_hint": None,
        "directories_touched": directories_touched,
        "generator": {
            "tool": "git2dev_change_ledger.py",
            "version": "0.1",
        },
    }

    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate DEV Change Ledger v0.1 JSONL from git history.")
    parser.add_argument("--range", dest="range_spec", required=True, help="Commit range in FROM..TO form.")
    parser.add_argument("--out", default="-", help="Output path or '-' for stdout (default: '-').")
    parser.add_argument("--dir-depth", type=int, default=1, help="Directory prefix depth (default: 1).")
    args = parser.parse_args()
    if args.dir_depth < 1:
        parser.error("--dir-depth must be >= 1")
    return args


def main() -> int:
    args = parse_args()
    try:
        revs_raw = run_git(["rev-list", "--reverse", args.range_spec])
        commits = [line.strip() for line in revs_raw.splitlines() if line.strip()]
        lines = []
        for commit_hash in commits:
            record = build_record(commit_hash, args.dir_depth)
            lines.append(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

        if args.out == "-":
            if lines:
                sys.stdout.write("\n".join(lines) + "\n")
            return 0

        out_path = Path(args.out)
        payload = ("\n".join(lines) + "\n") if lines else ""
        out_path.write_text(payload, encoding="utf-8")
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
