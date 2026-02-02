#!/usr/bin/env python3
"""
Applies SAFE graph NodeID renames from an evidence pack rename_plan.json
- Only renames collision-free pairs
- Token-safe replacement:
  replaces occurrences where the NodeID appears as an identifier token in Mermaid contexts.
Outputs:
- unified diffs printed to stdout
- (optional) write changes in-place with --apply
"""

from __future__ import annotations
import argparse, json, re, difflib, sys
from pathlib import Path

def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def token_pattern(node_id: str) -> re.Pattern:
    """
    Mermaid node IDs are identifier-like. We match whole tokens:
    - Not preceded/followed by [A-Za-z0-9_-]
    This avoids renaming inside longer IDs.
    """
    esc = re.escape(node_id)
    return re.compile(rf"(?<![A-Za-z0-9_\-]){esc}(?![A-Za-z0-9_\-])")

def apply_pairs(text: str, pairs: list[dict]) -> tuple[str, int]:
    n = 0
    out = text
    # Apply longer IDs first to reduce accidental partial overlaps (still token-safe, but good hygiene)
    pairs_sorted = sorted(pairs, key=lambda p: len(p["from"]), reverse=True)
    for p in pairs_sorted:
        pat = token_pattern(p["from"])
        out, c = pat.subn(p["to"], out)
        n += c
    return out, n

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true", help="Apply changes in-place. Otherwise dry-run diffs only.")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    repo_root = Path(args.repo_root).resolve()

    plan_path = run_dir / "rename_plan.json"
    if not plan_path.exists():
        raise SystemExit(f"Missing rename_plan.json in {run_dir}. Run plan_graph_nodeid_renames.py first.")

    plan = load_json(plan_path)
    by_file = plan.get("safe_renames_by_file", {})

    changed_files = 0
    total_replacements = 0

    for rel_path, pairs in sorted(by_file.items(), key=lambda kv: kv[0]):
        if not pairs:
            continue
        file_path = (repo_root / rel_path).resolve()
        if not file_path.exists():
            # Keep stdout clean for deterministic diff capture
            print(f"SKIP (missing): {rel_path}", file=sys.stderr)
            continue

        original = file_path.read_text(encoding="utf-8", errors="ignore")
        updated, count = apply_pairs(original, pairs)

        if updated == original:
            continue

        changed_files += 1
        total_replacements += count

        diff = difflib.unified_diff(
            original.splitlines(True),
            updated.splitlines(True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            lineterm="",
        )
        print("\n".join(diff))

        if args.apply:
            file_path.write_text(updated, encoding="utf-8")

    print("")
    print(f"SUMMARY: changed_files={changed_files} total_replacements={total_replacements} apply={args.apply}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
