#!/usr/bin/env python3
"""
Non-speculative graph NodeID rename planner:
- Uses evidence pack outputs (legend_nodes.json, graph_nodes.json)
- Proposes renames only when a deterministic canonicalization maps to an existing legend NodeID
- Detects collisions and ambiguous cases
Outputs:
- rename_plan.json
- rename_plan.md
"""

from __future__ import annotations
import argparse, json, re
from pathlib import Path
from collections import defaultdict

def canonicalize(node_id: str) -> str:
    s = node_id.strip()

    # Replace separators with underscores
    s = re.sub(r"[\s\-]+", "_", s)

    # Insert underscore between lower/digit followed by upper: fooBar -> foo_Bar
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)

    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)

    return s.upper()

def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True, help="Evidence pack directory under .codex/RUNS/<...>")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    legend_path = run_dir / "legend_nodes.json"
    graph_path = run_dir / "graph_nodes.json"

    if not legend_path.exists() or not graph_path.exists():
        raise SystemExit(f"Missing required evidence files in {run_dir} (need legend_nodes.json + graph_nodes.json)")

    legend = load_json(legend_path)
    graphs = load_json(graph_path)

    legend_ids = set(legend["entries"].keys())

    # Collect per-graph file node lists
    graph_files = graphs["graphs"].keys()

    # Proposals: per file, list of {from,to}
    per_file = defaultdict(list)

    # Track collisions: to_id -> [from_id...]
    to_collisions = defaultdict(set)

    # Track not-in-legend candidates
    not_in_legend = defaultdict(list)

    for gf, gd in graphs["graphs"].items():
        nodes = gd.get("nodes", [])
        for nid in nodes:
            cand = canonicalize(nid)
            if cand in legend_ids:
                if nid != cand:
                    per_file[gf].append({"from": nid, "to": cand, "canonical": cand})
                    to_collisions[cand].add(nid)
            else:
                # Record all nodes whose canonicalization is not in the legend,
                # even if the canonicalization is identical to the original.
                not_in_legend[gf].append({"from": nid, "candidate": cand})

    # Identify collision targets (same TO reached by multiple FROMs)
    collisions = {to: sorted(list(fr)) for to, fr in to_collisions.items() if len(fr) > 1}

    # Remove any proposals that map into collision targets (non-speculative safety)
    safe_per_file = defaultdict(list)
    removed_due_to_collision = defaultdict(list)

    for gf, pairs in per_file.items():
        for p in pairs:
            if p["to"] in collisions:
                removed_due_to_collision[gf].append(p)
            else:
                safe_per_file[gf].append(p)

    # Deterministic ordering of outputs
    safe_per_file_sorted = {}
    for gf in sorted(safe_per_file.keys()):
        safe_per_file_sorted[gf] = sorted(
            safe_per_file[gf], key=lambda p: (p["from"], p["to"])
        )

    not_in_legend_sorted = {}
    for gf in sorted(not_in_legend.keys()):
        not_in_legend_sorted[gf] = sorted(
            not_in_legend[gf], key=lambda p: (p["from"], p["candidate"])
        )

    out = {
        "run_dir": str(run_dir).replace("\\", "/"),
        "summary": {
            "legend_ids": len(legend_ids),
            "graph_files": len(graphs["graphs"]),
            "proposed_pairs_total": sum(len(v) for v in per_file.values()),
            "safe_pairs_total": sum(len(v) for v in safe_per_file_sorted.values()),
            "collision_targets": len(collisions),
            "files_with_candidates_not_in_legend": sum(1 for v in not_in_legend_sorted.values() if v),
        },
        "safe_renames_by_file": safe_per_file_sorted,
        "collisions": collisions,
        "removed_due_to_collision_by_file": dict(removed_due_to_collision),
        "candidates_not_in_legend_by_file": not_in_legend_sorted,
    }

    (run_dir / "rename_plan.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    # Markdown report
    md = []
    md.append("# Graph NodeID Rename Plan (Non-Speculative)")
    md.append("")
    md.append(f"- RUN_DIR: `{out['run_dir']}`")
    md.append(f"- Legend IDs: **{out['summary']['legend_ids']}**")
    md.append(f"- Graph files: **{out['summary']['graph_files']}**")
    md.append(f"- Proposed pairs (raw): **{out['summary']['proposed_pairs_total']}**")
    md.append(f"- Safe pairs (collision-free): **{out['summary']['safe_pairs_total']}**")
    md.append(f"- Collision targets: **{out['summary']['collision_targets']}**")
    md.append(f"- Files w/ candidates not in legend: **{out['summary']['files_with_candidates_not_in_legend']}**")
    md.append("")

    md.append("## Safe rename pairs by file")
    md.append("")
    if out["summary"]["safe_pairs_total"] == 0:
        md.append("- (none)")
    else:
        for gf in sorted(safe_per_file_sorted.keys()):
            pairs = safe_per_file_sorted[gf]
            if not pairs:
                continue
            md.append(f"### `{gf}`")
            md.append("")
            for p in pairs:
                md.append(f"- `{p['from']}` → `{p['to']}`")
            md.append("")

    md.append("## Collisions (blocked)")
    md.append("")
    if not collisions:
        md.append("- (none)")
    else:
        for to in sorted(collisions.keys()):
            md.append(f"- `{to}` <= {', '.join([f'`{x}`' for x in collisions[to]])}")

    md.append("")
    md.append("## Candidates not in legend (no auto-rename)")
    md.append("")
    any_missing = any(len(v) for v in not_in_legend_sorted.values())
    if not any_missing:
        md.append("- (none)")
    else:
        for gf in sorted(not_in_legend_sorted.keys()):
            items = not_in_legend_sorted[gf]
            if not items:
                continue
            md.append(f"### `{gf}`")
            md.append("")
            for it in items[:80]:
                md.append(f"- `{it['from']}` → candidate `{it['candidate']}` (NOT IN LEGEND)")
            if len(items) > 80:
                md.append(f"- … truncated (+{len(items)-80})")
            md.append("")

    (run_dir / "rename_plan.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("OK: wrote rename plan into evidence pack:")
    print(f" - {run_dir / 'rename_plan.json'}")
    print(f" - {run_dir / 'rename_plan.md'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
