#!/usr/bin/env python3
"""
coverage_audit.py
READ-ONLY repo coverage accounting:
Repo (git ls-files) -> Legend -> Graphs, and diffs between them.

Outputs (in .codex/RUNS/<stamp__label>/):
- repo_files.txt
- legend_nodes.json
- graph_nodes.json
- coverage_report.md

Assumptions:
- Legends are markdown pipe tables containing a NodeID column as the first cell in each row.
- Graphs are markdown files containing Mermaid blocks; we extract node IDs from declarations and edges.

This script is deliberately conservative:
- If it cannot parse a legend row meaningfully, it skips the row.
- For "EXTERNAL" legend targets, it does not attempt file matching.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


# ---------------------------
# Models
# ---------------------------

@dataclass(frozen=True)
class LegendEntry:
    node_id: str
    target: str                # path / glob / sql object / external label
    owner: str = "UNKNOWN"
    category: str = "UNKNOWN"
    status: str = "UNKNOWN"
    raw_row: str = ""          # for debugging / traceability
    source_file: str = ""      # legend file path

    def is_external(self) -> bool:
        t = (self.target or "").strip().lower()
        s = (self.status or "").strip().lower()
        c = (self.category or "").strip().lower()
        # Heuristic: treat these as external/unverifiable-in-repo.
        external_markers = ["external", "notion", "r2", "cloudflare", "gmail", "google", "api", "unverifiable"]
        return any(m in t for m in external_markers) or any(m in s for m in external_markers) or any(m in c for m in external_markers)

    def is_glob(self) -> bool:
        t = self.target.strip()
        return any(ch in t for ch in ["*", "?", "["]) or "**" in t

    def looks_like_sql_object(self) -> bool:
        # Very light heuristic: schema.object or db.schema.object
        t = self.target.strip()
        return bool(re.match(r"^[A-Za-z_][\w]*\.[A-Za-z_][\w]*$", t)) or bool(re.match(r"^[A-Za-z_][\w]*\.[A-Za-z_][\w]*\.[A-Za-z_][\w]*$", t))


# ---------------------------
# Utilities
# ---------------------------

def run_cmd(cmd: List[str], cwd: Path) -> str:
    out = subprocess.check_output(cmd, cwd=str(cwd), stderr=subprocess.STDOUT, text=True)
    return out

def repo_root_from_git(start: Path) -> Path:
    try:
        out = run_cmd(["git", "rev-parse", "--show-toplevel"], cwd=start)
        return Path(out.strip())
    except Exception:
        # fallback: walk up for .git
        p = start.resolve()
        for _ in range(20):
            if (p / ".git").exists():
                return p
            if p.parent == p:
                break
            p = p.parent
        raise RuntimeError("Could not determine repo root (no git rev-parse and no .git folder found).")

def utc_stamp(label: str = "") -> str:
    base = dt.datetime.utcnow().strftime("%Y-%m-%d__%H%M%S")
    if label.strip():
        return f"{base}__{label.strip()}"
    return base

def norm_path(p: str) -> str:
    # Normalize to repo-style forward slashes for matching consistency.
    return p.replace("\\", "/").strip().lstrip("./")

def safe_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def safe_write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")

def list_repo_files(repo_root: Path) -> List[str]:
    out = run_cmd(["git", "ls-files"], cwd=repo_root)
    files = [norm_path(line) for line in out.splitlines() if line.strip()]
    files.sort()
    return files


# ---------------------------
# Legend parsing
# ---------------------------

PIPE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
PIPE_SEP_RE = re.compile(r"^\s*\|\s*[-: ]+\|\s*[-:| ]+\|\s*$")

def parse_markdown_pipe_tables(md_text: str) -> List[List[str]]:
    """
    Returns rows as lists of cells for all pipe-table rows.
    Skips separator lines.
    """
    rows: List[List[str]] = []
    for line in md_text.splitlines():
        if PIPE_SEP_RE.match(line):
            continue
        m = PIPE_ROW_RE.match(line)
        if not m:
            continue
        inner = m.group(1)
        # split by | but keep empty cells if present
        cells = [c.strip() for c in inner.split("|")]
        # ignore empty row
        if all(c == "" for c in cells):
            continue
        rows.append(cells)
    return rows

def legend_entries_from_file(path: Path) -> List[LegendEntry]:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    rows = parse_markdown_pipe_tables(txt)

    entries: List[LegendEntry] = []

    # Heuristic:
    # - A header row typically contains "ID" or "Node" or "NodeID" in first cell.
    # - Data rows: first cell looks like an ID token (A-Z0-9_- ...)
    id_token = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]*$")

    for cells in rows:
        if not cells:
            continue
        first = (cells[0] or "").strip()
        # skip header-like rows
        if first.lower() in {"id", "node", "nodeid", "node id", "key"}:
            continue
        if not id_token.match(first):
            continue

        # Try to map common legend column layouts:
        # NodeID | Legend path/name | Owner | Category | Status | ...
        target = cells[1].strip() if len(cells) >= 2 else ""
        owner = cells[2].strip() if len(cells) >= 3 else "UNKNOWN"
        category = cells[3].strip() if len(cells) >= 4 else "UNKNOWN"
        status = cells[4].strip() if len(cells) >= 5 else "UNKNOWN"

        entries.append(
            LegendEntry(
                node_id=first,
                target=target,
                owner=owner or "UNKNOWN",
                category=category or "UNKNOWN",
                status=status or "UNKNOWN",
                raw_row="| " + " | ".join(cells) + " |",
                source_file=norm_path(str(path))
            )
        )

    return entries

def load_legends(repo_root: Path, legend_paths: List[str]) -> Dict[str, LegendEntry]:
    """
    Returns dict NodeID -> LegendEntry.
    If NodeID appears multiple times:
      - keep first, record duplicates in report stage via separate scan.
    """
    entries_all: List[LegendEntry] = []
    for lp in legend_paths:
        p = (repo_root / lp).resolve()
        if not p.exists():
            continue
        entries_all.extend(legend_entries_from_file(p))

    legend_map: Dict[str, LegendEntry] = {}
    for e in entries_all:
        if e.node_id not in legend_map:
            legend_map[e.node_id] = e
    return legend_map

def find_legend_duplicates(repo_root: Path, legend_paths: List[str]) -> Dict[str, List[LegendEntry]]:
    """
    Return NodeID -> [entries...] for NodeIDs defined more than once.
    """
    all_entries: List[LegendEntry] = []
    for lp in legend_paths:
        p = (repo_root / lp).resolve()
        if not p.exists():
            continue
        all_entries.extend(legend_entries_from_file(p))

    by_id: Dict[str, List[LegendEntry]] = {}
    for e in all_entries:
        by_id.setdefault(e.node_id, []).append(e)

    dupes = {k: v for k, v in by_id.items() if len(v) > 1}
    return dupes


# ---------------------------
# Graph parsing
# ---------------------------

MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*(.*?)```", re.DOTALL | re.IGNORECASE)

# Node IDs in declarations like: A[...], A(...), A{{...}}, A["..."]
NODE_DECL_RE = re.compile(r"(?m)^\s*([A-Za-z0-9][A-Za-z0-9_\-]*)\s*(?:\[\s*|\(\s*|\{\{\s*|\{\s*|\"\s*)")

# Edge endpoints like: A --> B, A -.-> B, A --x B, etc.
EDGE_RE = re.compile(
    r"(?m)^\s*([A-Za-z0-9][A-Za-z0-9_\-]*)\s*([-.=]{1,4}.*?>)\s*([A-Za-z0-9][A-Za-z0-9_\-]*)"
)

def parse_mermaid_from_md(md_text: str) -> List[str]:
    blocks = []
    for m in MERMAID_BLOCK_RE.finditer(md_text):
        blocks.append(m.group(1))
    return blocks

def extract_nodes_edges_from_mermaid(mermaid_text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    """
    Returns (nodes_in_order, edges[(src, style, dst)]) from a Mermaid block.
    Node order tries to preserve first-seen order (decls first, then edge endpoints).
    """
    nodes_order: List[str] = []
    seen: Set[str] = set()

    # declarations
    for m in NODE_DECL_RE.finditer(mermaid_text):
        nid = m.group(1)
        if nid not in seen:
            seen.add(nid)
            nodes_order.append(nid)

    edges: List[Tuple[str, str, str]] = []
    for m in EDGE_RE.finditer(mermaid_text):
        a, style, b = m.group(1), m.group(2).strip(), m.group(3)
        edges.append((a, style, b))
        for nid in (a, b):
            if nid not in seen:
                seen.add(nid)
                nodes_order.append(nid)

    return nodes_order, edges

def resolve_repo_path(repo_root: Path, path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (repo_root / path_str).resolve()

def load_graphs(repo_root: Path, graphs_root: str) -> Dict[str, Dict]:
    """
    Returns:
    {
      "path/to/graph.md": {
         "nodes": [...],
         "edges": [(a, style, b), ...]
      }
    }
    """
    root = (repo_root / graphs_root).resolve()
    if not root.exists():
        return {}

    graph_data: Dict[str, Dict] = {}
    md_files = sorted(root.rglob("*.md"))

    for f in md_files:
        rel = norm_path(str(f.relative_to(repo_root)))
        txt = f.read_text(encoding="utf-8", errors="ignore")
        blocks = parse_mermaid_from_md(txt)
        all_nodes: List[str] = []
        all_edges: List[Tuple[str, str, str]] = []
        seen_nodes: Set[str] = set()

        for block in blocks:
            nodes, edges = extract_nodes_edges_from_mermaid(block)
            for n in nodes:
                if n not in seen_nodes:
                    seen_nodes.add(n)
                    all_nodes.append(n)
            all_edges.extend(edges)

        graph_data[rel] = {
            "nodes": all_nodes,
            "edges": all_edges,
            "mermaid_blocks": len(blocks)
        }

    return graph_data

def load_graph_file(repo_root: Path, graph_path: str) -> Dict[str, Dict]:
    """
    Returns graph data for a single graph file.
    """
    p = resolve_repo_path(repo_root, graph_path)
    if not p.exists():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")

    rel = norm_path(str(p.relative_to(repo_root)))
    txt = p.read_text(encoding="utf-8", errors="ignore")
    blocks = parse_mermaid_from_md(txt)
    all_nodes: List[str] = []
    all_edges: List[Tuple[str, str, str]] = []
    seen_nodes: Set[str] = set()

    for block in blocks:
        nodes, edges = extract_nodes_edges_from_mermaid(block)
        for n in nodes:
            if n not in seen_nodes:
                seen_nodes.add(n)
                all_nodes.append(n)
        all_edges.extend(edges)

    return {
        rel: {
            "nodes": all_nodes,
            "edges": all_edges,
            "mermaid_blocks": len(blocks)
        }
    }


# ---------------------------
# Coverage computation
# ---------------------------

def match_legend_to_files(repo_files: List[str], entry: LegendEntry) -> Set[str]:
    """
    Match a LegendEntry target to repo files.
    - If external: empty set
    - If glob: fnmatch on normalized paths
    - If looks like folder path: prefix match
    - Else: exact match or prefix match if target is a directory (best-effort).
    """
    if not entry.target.strip():
        return set()
    if entry.is_external():
        return set()

    tgt = norm_path(entry.target)

    # If the legend uses backticks or quotes in the cell, strip common wrappers.
    tgt = tgt.strip("`").strip('"').strip("'").strip()

    # If it looks like a URL or external label, skip
    if tgt.lower().startswith(("http://", "https://")):
        return set()

    # If glob-like
    if entry.is_glob():
        pat = tgt
        # Ensure patterns behave with forward slashes
        matched = {f for f in repo_files if fnmatch.fnmatch(f, pat)}
        return matched

    # Non-glob: treat as file or folder-ish
    # If it ends with "/", treat as directory prefix
    if tgt.endswith("/"):
        prefix = tgt
        return {f for f in repo_files if f.startswith(prefix)}

    # Exact file match
    if tgt in repo_files:
        return {tgt}

    # Directory prefix fallback (common if legend points to folder)
    prefix = tgt.rstrip("/") + "/"
    pref = {f for f in repo_files if f.startswith(prefix)}
    if pref:
        return pref

    # Nothing matched
    return set()


def compute_coverage(
    repo_files: List[str],
    legend_map: Dict[str, LegendEntry],
    graph_data: Dict[str, Dict]
) -> Dict:
    # Graph-wide node set
    graph_all_nodes: Set[str] = set()
    for gd in graph_data.values():
        graph_all_nodes.update(gd.get("nodes", []))

    legend_ids = set(legend_map.keys())

    # Repo -> Legend coverage mapping
    file_to_nodes: Dict[str, List[str]] = {}
    node_to_files: Dict[str, List[str]] = {}

    for nid in sorted(legend_ids):
        entry = legend_map[nid]
        matched = match_legend_to_files(repo_files, entry)
        if matched:
            node_to_files[nid] = sorted(matched)
            for f in matched:
                file_to_nodes.setdefault(f, []).append(nid)

    # Normalize file_to_nodes ordering
    for f in list(file_to_nodes.keys()):
        file_to_nodes[f] = sorted(file_to_nodes[f])

    # A) Repo -> Legend: Unaccounted files
    accounted_files = set(file_to_nodes.keys())
    unaccounted_files = [f for f in repo_files if f not in accounted_files]

    # B) Legend -> Graph: legend IDs with 0 graph occurrences
    legend_not_graphed = sorted([nid for nid in legend_ids if nid not in graph_all_nodes])

    # C) Graph -> Legend: graph node IDs missing from legend
    graph_node_missing_legend = sorted([nid for nid in graph_all_nodes if nid not in legend_ids])

    # D) Ambiguities
    glob_overlap_collisions = sorted([(f, file_to_nodes[f]) for f in file_to_nodes if len(file_to_nodes[f]) > 1], key=lambda x: x[0])

    # Multi-owner collisions: same file matched by multiple NodeIDs with different owner/category
    multi_owner_collisions: List[Tuple[str, List[Dict[str, str]]]] = []
    for f, nids in glob_overlap_collisions:
        owners = []
        for nid in nids:
            e = legend_map.get(nid)
            owners.append({
                "node_id": nid,
                "owner": (e.owner if e else "UNKNOWN"),
                "category": (e.category if e else "UNKNOWN"),
                "status": (e.status if e else "UNKNOWN"),
                "target": (e.target if e else "")
            })
        distinct = {(o["owner"], o["category"]) for o in owners}
        if len(distinct) > 1:
            multi_owner_collisions.append((f, owners))
    multi_owner_collisions.sort(key=lambda x: x[0])

    return {
        "repo_files_count": len(repo_files),
        "legend_nodes_count": len(legend_ids),
        "graphs_count": len(graph_data),
        "graph_nodes_count": len(graph_all_nodes),
        "unaccounted_files": unaccounted_files,
        "legend_not_graphed": legend_not_graphed,
        "graph_node_missing_legend": graph_node_missing_legend,
        "glob_overlap_collisions": glob_overlap_collisions,
        "multi_owner_collisions": multi_owner_collisions,
        "file_to_nodes": file_to_nodes,
        "node_to_files": node_to_files,
        "graph_all_nodes": sorted(graph_all_nodes),
    }


# ---------------------------
# Reporting
# ---------------------------

def render_report(
    repo_root: Path,
    repo_files: List[str],
    legend_map: Dict[str, LegendEntry],
    legend_dupes: Dict[str, List[LegendEntry]],
    graph_data: Dict[str, Dict],
    coverage: Dict,
    graphs_root: str,
    legend_paths: List[str],
    graph_file: str = "",
) -> str:
    stamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lines: List[str] = []
    lines.append(f"# COVERAGE AUDIT — Repo ↔ Legend ↔ Graphs")
    lines.append("")
    lines.append(f"- REPO_ROOT: `{norm_path(str(repo_root))}`")
    lines.append(f"- GENERATED_UTC: `{stamp}`")
    lines.append(f"- GRAPHS_ROOT: `{graphs_root}`")
    if graph_file:
        lines.append(f"- GRAPH_FILE: `{graph_file}`")
    lines.append(f"- LEGENDS: {', '.join([f'`{p}`' for p in legend_paths])}")
    lines.append("")
    lines.append("## Summary Counts")
    lines.append("")
    lines.append(f"- Repo files (git ls-files): **{coverage['repo_files_count']}**")
    lines.append(f"- Legend NodeIDs: **{coverage['legend_nodes_count']}**")
    lines.append(f"- Graph files scanned: **{coverage['graphs_count']}**")
    lines.append(f"- Unique graph NodeIDs: **{coverage['graph_nodes_count']}**")
    lines.append("")

    # Section A
    unacc = coverage["unaccounted_files"]
    lines.append("## Section A — Repo → Legend")
    lines.append("")
    lines.append(f"### UNACCOUNTED_FILES ({len(unacc)})")
    lines.append("")
    if unacc:
        for f in unacc:
            lines.append(f"- `{f}`")
    else:
        lines.append("- (none)")
    lines.append("")

    # Section B
    lng = coverage["legend_not_graphed"]
    lines.append("## Section B — Legend → Graph")
    lines.append("")
    lines.append(f"### LEGEND_NOT_GRAPHED ({len(lng)})")
    lines.append("")
    if lng:
        for nid in lng:
            e = legend_map.get(nid)
            if e:
                lines.append(f"- `{nid}` → `{e.target}` (owner={e.owner}, category={e.category}, status={e.status})")
            else:
                lines.append(f"- `{nid}` → (legend entry missing?)")
    else:
        lines.append("- (none)")
    lines.append("")

    # Section C
    gml = coverage["graph_node_missing_legend"]
    lines.append("## Section C — Graph → Legend")
    lines.append("")
    lines.append(f"### GRAPH_NODE_MISSING_LEGEND ({len(gml)})")
    lines.append("")
    if gml:
        for nid in gml:
            # show where it appears
            graphs = [g for g, gd in graph_data.items() if nid in gd.get("nodes", [])]
            graphs.sort()
            where = ", ".join([f"`{g}`" for g in graphs[:6]])
            if len(graphs) > 6:
                where += f", …(+{len(graphs)-6})"
            lines.append(f"- `{nid}` appears in: {where if where else '(unknown)'}")
    else:
        lines.append("- (none)")
    lines.append("")

    # Section D: Ambiguities
    lines.append("## Section D — Ambiguities")
    lines.append("")
    overlaps = coverage["glob_overlap_collisions"]
    lines.append(f"### GLOB_OVERLAP_COLLISIONS ({len(overlaps)})")
    lines.append("")
    if overlaps:
        for f, nids in overlaps[:200]:
            lines.append(f"- `{f}` matched by NodeIDs: {', '.join([f'`{nid}`' for nid in nids])}")
        if len(overlaps) > 200:
            lines.append(f"- … truncated (+{len(overlaps)-200})")
    else:
        lines.append("- (none)")
    lines.append("")

    mo = coverage["multi_owner_collisions"]
    lines.append(f"### MULTI_OWNER_COLLISIONS ({len(mo)})")
    lines.append("")
    if mo:
        for f, owners in mo[:120]:
            lines.append(f"- `{f}`")
            for o in owners:
                lines.append(f"  - `{o['node_id']}` owner=`{o['owner']}` category=`{o['category']}` status=`{o['status']}` target=`{o['target']}`")
        if len(mo) > 120:
            lines.append(f"- … truncated (+{len(mo)-120})")
    else:
        lines.append("- (none)")
    lines.append("")

    # Duplicate NodeIDs in legend files
    lines.append("## Legend Duplicate IDs")
    lines.append("")
    lines.append(f"### DUPLICATE_NODEID_DEFINITIONS ({len(legend_dupes)})")
    lines.append("")
    if legend_dupes:
        for nid in sorted(legend_dupes.keys()):
            lines.append(f"- `{nid}` defined {len(legend_dupes[nid])} times:")
            for e in legend_dupes[nid]:
                lines.append(f"  - source=`{e.source_file}` target=`{e.target}` owner=`{e.owner}` category=`{e.category}` status=`{e.status}`")
    else:
        lines.append("- (none)")
    lines.append("")

    return "\n".join(lines)


# ---------------------------
# Main
# ---------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="OVC Coverage Audit: Repo ↔ Legend ↔ Graphs")
    ap.add_argument("--repo-root", default=".", help="Repo root (default: current directory; git used to resolve).")
    ap.add_argument("--runs-dir", default=".codex/RUNS", help="Runs output directory relative to repo root.")
    ap.add_argument("--run-dir", default="", help="Write outputs into this folder (no new timestamp subfolder).")
    ap.add_argument("--label", default="coverage", help="Run label appended to timestamp.")
    ap.add_argument("--graphs-root", default="Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS", help="Graphs root to scan for *.md")
    ap.add_argument("--graph-file", default="", help="Single graph file to scan (optional).")
    ap.add_argument("--legend-master", default="Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md", help="Legend master path")
    ap.add_argument("--legend-per-graph", default="Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_PER_GRAPH.md", help="Legend per-graph path")
    args = ap.parse_args()

    start = Path(args.repo_root).resolve()
    repo_root = repo_root_from_git(start)

    if args.run_dir.strip():
        run_dir = resolve_repo_path(repo_root, args.run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_name = utc_stamp(args.label)
        run_dir = (repo_root / norm_path(args.runs_dir) / run_name).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)

    # 1) Repo files
    repo_files = list_repo_files(repo_root)
    safe_write_text(run_dir / "repo_files.txt", "\n".join(repo_files) + "\n")

    # 2) Legends
    legend_paths = [norm_path(args.legend_master), norm_path(args.legend_per_graph)]
    legend_map = load_legends(repo_root, legend_paths)
    legend_dupes = find_legend_duplicates(repo_root, legend_paths)

    legend_json = {
        "legend_paths": legend_paths,
        "entries": {nid: asdict(e) for nid, e in sorted(legend_map.items(), key=lambda kv: kv[0])}
    }
    safe_write_json(run_dir / "legend_nodes.json", legend_json)

    # 3) Graphs
    if args.graph_file.strip():
        graph_data = load_graph_file(repo_root, args.graph_file.strip())
    else:
        graph_data = load_graphs(repo_root, norm_path(args.graphs_root))
    graph_json = {
        "graphs_root": norm_path(args.graphs_root),
        "graph_file": norm_path(args.graph_file) if args.graph_file.strip() else "",
        "graphs": graph_data
    }
    safe_write_json(run_dir / "graph_nodes.json", graph_json)

    # 4) Coverage
    coverage = compute_coverage(repo_files, legend_map, graph_data)

    report = render_report(
        repo_root=repo_root,
        repo_files=repo_files,
        legend_map=legend_map,
        legend_dupes=legend_dupes,
        graph_data=graph_data,
        coverage=coverage,
        graphs_root=norm_path(args.graphs_root),
        legend_paths=legend_paths,
        graph_file=norm_path(args.graph_file) if args.graph_file.strip() else ""
    )
    safe_write_text(run_dir / "coverage_report.md", report + "\n")

    print(f"OK: Wrote coverage audit to: {norm_path(str(run_dir))}")
    print(" - repo_files.txt")
    print(" - legend_nodes.json")
    print(" - graph_nodes.json")
    print(" - coverage_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
