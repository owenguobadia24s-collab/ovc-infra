#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".cache",
}

BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf",
    ".zip", ".tar", ".gz", ".7z",
    ".mp3", ".mp4", ".mov",
    ".exe", ".dll", ".so", ".dylib",
}

@dataclass(frozen=True)
class FileRow:
    path: str
    ext: str
    top: str
    size: int

def iter_files(root: Path, excludes: set[str]) -> Iterable[Path]:
    # Walk with pruning for speed.
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs in-place
        dirnames[:] = [d for d in dirnames if d not in excludes]
        for name in filenames:
            yield Path(dirpath) / name

def top_dir(root: Path, p: Path) -> str:
    rel = p.relative_to(root)
    parts = rel.parts
    return parts[0] if len(parts) > 1 else "(root)"

def normalize_ext(p: Path) -> str:
    # Handle dotfiles like ".env" -> treat as "(dotfile)" unless it has a suffix beyond first dot
    name = p.name
    suf = p.suffix.lower()
    if suf:
        return suf
    if name.startswith(".") and name.count(".") == 1:
        return "(dotfile)"
    return "(none)"

def main() -> int:
    ap = argparse.ArgumentParser(description="Repo file census (read-only).")
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--exclude", action="append", default=[], help="Dir name to exclude (repeatable)")
    ap.add_argument("--out", default="repo_census.json", help="Output JSON path")
    ap.add_argument("--top-n", type=int, default=30, help="Top N lists")
    ap.add_argument("--include-binaries", action="store_true", help="Include binary extensions in size/top lists")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    excludes = set(DEFAULT_EXCLUDES) | set(args.exclude)

    ext_counts = Counter()
    top_counts = Counter()
    ext_sizes = Counter()
    top_sizes = Counter()

    rows: list[FileRow] = []
    unknown_ext_paths: list[str] = []
    largest_files: list[tuple[int, str]] = []

    total_files = 0
    total_bytes = 0

    for p in iter_files(root, excludes):
        try:
            st = p.stat()
        except OSError:
            continue

        rel = str(p.relative_to(root))
        ext = normalize_ext(p)
        top = top_dir(root, p)
        size = int(st.st_size)

        total_files += 1
        total_bytes += size

        ext_counts[ext] += 1
        top_counts[top] += 1
        ext_sizes[ext] += size
        top_sizes[top] += size

        rows.append(FileRow(path=rel, ext=ext, top=top, size=size))

        if ext in ("(none)", "(dotfile)"):
            unknown_ext_paths.append(rel)

        # Track largest files
        largest_files.append((size, rel))

    largest_files.sort(reverse=True)
    if not args.include_binaries:
        # filter out common binaries from the "largest" list
        def is_binary(path: str) -> bool:
            return Path(path).suffix.lower() in BINARY_EXTS
        largest_files = [(s, r) for (s, r) in largest_files if not is_binary(r)]
    largest_files = largest_files[: args.top_n]

    # Prepare top-N breakdowns
    top_ext = ext_counts.most_common(args.top_n)
    top_dirs = top_counts.most_common(args.top_n)

    report = {
        "root": str(root),
        "excludes": sorted(excludes),
        "totals": {
            "files": total_files,
            "bytes": total_bytes,
        },
        "by_extension": {
            "counts_top": top_ext,
            "bytes_top": ext_sizes.most_common(args.top_n),
        },
        "by_top_dir": {
            "counts_top": top_dirs,
            "bytes_top": top_sizes.most_common(args.top_n),
        },
        "largest_files": largest_files,
        "unknown_or_extensionless_sample": unknown_ext_paths[: args.top_n],
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Also print a quick human summary
    print(f"Root: {root}")
    print(f"Files: {total_files:,}")
    print(f"Size:  {total_bytes/1024/1024:.2f} MiB")
    print("\nTop extensions:")
    for ext, n in top_ext[:15]:
        print(f"  {ext:10} {n:>10,}")
    print("\nTop directories:")
    for d, n in top_dirs[:15]:
        print(f"  {d:20} {n:>10,}")
    print(f"\nWrote: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
