#!/usr/bin/env python3
"""
Curated OVC Repo Maze Generator (Obsidian) — small, semantic map

Creates a small set of curated notes (no per-dir/per-file nodes) plus an optional canvas.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


# ----------------------------
# Config
# ----------------------------

DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".cache",
}

ROOMS = {
    "WORKFLOWS": ".github/workflows",
    "DOCS": "docs",
    "SQL": "sql",
    "REPORTS": "reports",
    "ARTIFACTS": "artifacts",
}

OPTION_SPINE = [
    "OPT_A__CANONICAL_INGEST",
    "OPT_D__PATHS_BRIDGE",
    "OPT_B__DERIVED_LAYERS",
    "OPT_C__OUTCOMES_EVAL",
]

OPTION_DEFS = {
    "OPT_A__CANONICAL_INGEST": (
        "Canonical ingest: raw -> canonical facts (L0/R + L1).",
        [
            r"ingest",
            r"canonical",
            r"canon",
            r"l0",
            r"l1",
            r"export",
            r"raw",
            r"contract",
            r"schema",
        ],
        [r"ingest", r"canon", r"export", r"l0", r"l1"],
    ),
    "OPT_D__PATHS_BRIDGE": (
        "Path1 evidence runner + Path2 determinism mechanics + evidence pack orchestration.",
        [
            r"path1",
            r"path2",
            r"evidence",
            r"evidence_pack",
            r"orchestr",
            r"runner",
            r"pack",
        ],
        [r"path1", r"path2", r"evidence", r"runner", r"pack"],
    ),
    "OPT_B__DERIVED_LAYERS": (
        "Derived layers: L2/L3 features, registries, semantics, metrics.",
        [
            r"l2",
            r"l3",
            r"derived",
            r"feature",
            r"registry",
            r"metric",
            r"threshold",
            r"boundary",
            r"semantic",
        ],
        [r"l2", r"l3", r"derived", r"feature", r"registry"],
    ),
    "OPT_C__OUTCOMES_EVAL": (
        "Outcomes & evaluation: labels, eval reports, regressions.",
        [
            r"outcome",
            r"label",
            r"evaluation",
            r"eval",
            r"regression",
            r"report",
        ],
        [r"outcome", r"label", r"eval", r"evaluation", r"regression"],
    ),
}

INPUT_KEYWORDS = ["raw", "ingest", "l0", "l1", "source", "contract", "schema", "spec"]
OUTPUT_KEYWORDS = ["export", "derived", "l2", "l3", "report", "artifact", "outcome", "eval", "label"]

QA_KEYWORDS = [
    "determin",
    "invariant",
    "contract",
    "drift",
    "fingerprint",
    "hash",
    "norm",
    "pass",
    "fail",
    "policy",
    "boundary",
    "audit",
    "validate",
    "validation",
]

IMPORTANT_EXT_WEIGHT = {
    ".md": 5,
    ".sql": 4,
    ".yaml": 3,
    ".yml": 3,
    ".json": 2,
    ".py": 2,
    ".txt": 1,
    ".csv": 1,
}

IMPORTANT_KEYWORDS = [
    ("readme", 8),
    ("overview", 6),
    ("index", 5),
    ("spec", 6),
    ("schema", 6),
    ("contract", 6),
    ("path1", 6),
    ("path2", 6),
    ("validation", 6),
    ("determin", 5),
    ("evidence", 5),
    ("ingest", 5),
    ("canonical", 5),
    ("derived", 5),
    ("registry", 5),
    ("metric", 4),
    ("threshold", 4),
    ("outcome", 5),
    ("evaluation", 5),
    ("label", 4),
    ("regression", 4),
]


# ----------------------------
# Helpers
# ----------------------------

def norm_rel(path: Path) -> str:
    return path.as_posix().lstrip("./")


def iter_files(repo_root: Path) -> List[str]:
    files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel_dir = norm_rel(Path(dirpath).relative_to(repo_root))
        if rel_dir == ".":
            rel_dir = ""
        if rel_dir:
            parts = rel_dir.split("/")
            if parts and parts[0] in DEFAULT_IGNORE_DIRS:
                dirnames[:] = []
                continue
        # prune ignored dirs
        pruned = []
        for d in dirnames:
            if d in DEFAULT_IGNORE_DIRS:
                continue
            pruned.append(d)
        dirnames[:] = pruned

        for fn in filenames:
            rel = f"{rel_dir}/{fn}".strip("/")
            files.append(rel)
    return sorted(set(files))


def score_path(rel: str) -> int:
    score = 0
    low = rel.lower()
    ext = Path(rel).suffix.lower()
    score += IMPORTANT_EXT_WEIGHT.get(ext, 0)
    for kw, w in IMPORTANT_KEYWORDS:
        if kw in low:
            score += w
    # prefer shallower paths slightly
    depth = low.count("/")
    score -= min(depth, 6)
    return score


def pick_top(paths: Sequence[str], min_n: int = 10, max_n: int = 30) -> List[str]:
    if not paths:
        return []
    ranked = sorted(paths, key=lambda p: (-score_path(p), p))
    top = ranked[: max_n]
    if len(top) < min_n:
        top = ranked[: min(len(ranked), max_n)]
    return top


def sort_by_score(paths: Sequence[str]) -> List[str]:
    return sorted(paths, key=lambda p: (-score_path(p), p))


def match_any(patterns: Sequence[str], text: str) -> bool:
    low = text.lower()
    return any(pat in low for pat in patterns)


def is_qa_anchor(path: str) -> bool:
    return match_any(QA_KEYWORDS, path)


def filter_by_regex(paths: Sequence[str], rx_list: Sequence[str]) -> List[str]:
    out: List[str] = []
    for rel in paths:
        for rx in rx_list:
            if re.search(rx, rel, re.IGNORECASE):
                out.append(rel)
                break
    return sorted(set(out))


def list_area_files(all_files: Sequence[str], area_prefix: str) -> List[str]:
    prefix = area_prefix.rstrip("/") + "/"
    return [p for p in all_files if p.startswith(prefix)]


def to_md_list(items: Sequence[str], bullet: str = "-") -> str:
    if not items:
        return f"{bullet} none found"
    return "\n".join(f"{bullet} `{i}`" for i in items)


def ensure_dir_clean(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def safe_room_link(room_name: str) -> str:
    return f"ROOM__{room_name}"


# ----------------------------
# Build curated content
# ----------------------------

def build_rooms(all_files: Sequence[str]) -> Dict[str, Dict[str, object]]:
    rooms: Dict[str, Dict[str, object]] = {}
    for room_key, prefix in ROOMS.items():
        area_files = list_area_files(all_files, prefix)
        top_files = pick_top(area_files, min_n=10, max_n=30)
        rooms[room_key] = {
            "prefix": prefix,
            "files": area_files,
            "top": top_files,
        }
    return rooms


def build_qa_anchors(all_files: Sequence[str]) -> List[str]:
    qa_anchors = [p for p in all_files if is_qa_anchor(p)]
    return sort_by_score(qa_anchors)


def build_options(all_files: Sequence[str], workflows: Sequence[str]) -> Dict[str, Dict[str, object]]:
    options: Dict[str, Dict[str, object]] = {}
    for opt_name, (definition, anchor_kw, wf_kw) in OPTION_DEFS.items():
        anchors_all = [p for p in all_files if match_any(anchor_kw, p)]
        anchors_all = sort_by_score(anchors_all)
        if opt_name == "OPT_D__PATHS_BRIDGE":
            anchors_non_qa = [p for p in anchors_all if not is_qa_anchor(p)]
        else:
            anchors_non_qa = list(anchors_all)
        anchors = anchors_non_qa[:18] if anchors_non_qa else []
        key_wf = [w for w in workflows if match_any(wf_kw, w)]
        key_wf = sort_by_score(key_wf)[:12] if key_wf else []

        # inputs/outputs derived from anchors
        inputs = [p for p in anchors_non_qa if match_any(INPUT_KEYWORDS, p)]
        outputs = [p for p in anchors_non_qa if match_any(OUTPUT_KEYWORDS, p)]
        inputs = inputs[:5]
        outputs = outputs[:5]

        options[opt_name] = {
            "definition": definition,
            "anchors": anchors,
            "anchors_all": anchors_all,
            "anchors_non_qa": anchors_non_qa,
            "workflows": key_wf,
            "inputs": inputs,
            "outputs": outputs,
        }
    return options


def option_room_links(option_anchors: Sequence[str]) -> List[str]:
    links: List[str] = []
    for room_key, prefix in ROOMS.items():
        pref = prefix.rstrip("/") + "/"
        if any(a.startswith(pref) for a in option_anchors):
            links.append(safe_room_link(room_key))
    # workflows are special room
    if any(a.startswith(".github/workflows/") for a in option_anchors):
        if safe_room_link("WORKFLOWS") not in links:
            links.append(safe_room_link("WORKFLOWS"))
    return sorted(set(links))


def rooms_used_by_option(options: Dict[str, Dict[str, object]]) -> Dict[str, List[str]]:
    room_to_opts: Dict[str, List[str]] = {k: [] for k in ROOMS.keys()}
    for opt_name, data in options.items():
        anchors = data.get("anchors_non_qa", []) or data.get("anchors_all", []) or data.get("anchors", [])
        for room_key, prefix in ROOMS.items():
            pref = prefix.rstrip("/") + "/"
            if any(a.startswith(pref) for a in anchors):
                room_to_opts[room_key].append(opt_name)
    # workflows: use key workflows
    for opt_name, data in options.items():
        if data.get("workflows"):
            if opt_name not in room_to_opts["WORKFLOWS"]:
                room_to_opts["WORKFLOWS"].append(opt_name)
    return room_to_opts


# ----------------------------
# Writers
# ----------------------------

def write_note(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_index(out_dir: Path, rooms: Dict[str, Dict[str, object]], options: Dict[str, Dict[str, object]], top_dirs: List[str]) -> None:
    lines: List[str] = []
    lines.append("---")
    lines.append("type: repo-maze-index")
    lines.append("tags: [ovc, repo, maze, curated]")
    lines.append("---")
    lines.append("")
    lines.append("# OVC Repo Maze (Curated)")
    lines.append("")
    lines.append("This map is intentionally small and semantic. Use it as a navigation spine, not a mirror of the filesystem.")
    lines.append("")
    lines.append("## How to navigate")
    lines.append("- Start with an Option (A/D/B/C) to follow the pipeline lens.")
    lines.append("- Jump to a Room to browse concrete artifacts (workflows/docs/sql/reports/artifacts).")
    lines.append("- Each Option lists anchors and workflows, with inputs/outputs derived from actual files.")
    lines.append("")
    lines.append("## Option spine")
    for opt in OPTION_SPINE:
        lines.append(f"- [[{opt}]]")
    lines.append("")
    lines.append("## System canopy")
    lines.append("- [[QA_GOVERNANCE]]")
    lines.append("")
    lines.append("## Rooms")
    for room_key in ROOMS.keys():
        lines.append(f"- [[{safe_room_link(room_key)}]]")
    lines.append("")
    lines.append("## Repo shape (top-level)")
    if top_dirs:
        for d in top_dirs:
            lines.append(f"- `{d}/`")
    else:
        lines.append("- (no top-level folders detected)")
    lines.append("")
    lines.append("## Notes")
    lines.append("- No per-dir or per-file notes are generated.")
    lines.append("- This vault folder is fully regeneratable.")

    write_note(out_dir / "00_REPO_MAZE.md", "\n".join(lines))


def write_option_notes(out_dir: Path, options: Dict[str, Dict[str, object]]) -> None:
    for opt_name, data in options.items():
        definition = data["definition"]
        anchors = data["anchors"]
        workflows = data["workflows"]
        inputs = data["inputs"]
        outputs = data["outputs"]
        room_links = option_room_links(anchors)

        lines: List[str] = []
        lines.append("---")
        lines.append("type: repo-maze-option")
        lines.append("tags: [ovc, repo, maze, option]")
        lines.append("---")
        lines.append("")
        lines.append(f"# {opt_name}")
        lines.append("")
        lines.append("## Definition")
        lines.append(definition)
        lines.append("")
        lines.append("## Anchors (real repo paths)")
        lines.append(to_md_list(anchors))
        lines.append("")
        lines.append("## Key workflows")
        lines.append(to_md_list(workflows))
        lines.append("")
        lines.append("## Inputs")
        lines.append(to_md_list(inputs))
        lines.append("")
        lines.append("## Outputs")
        lines.append(to_md_list(outputs))
        lines.append("")
        lines.append("## Rooms")
        if room_links:
            for rl in room_links:
                lines.append(f"- [[{rl}]]")
        else:
            lines.append("- none")
        lines.append("")
        lines.append("## Spine")
        lines.append("- " + " -> ".join(f"[[{o}]]" for o in OPTION_SPINE))

        write_note(out_dir / f"{opt_name}.md", "\n".join(lines))


def write_room_notes(out_dir: Path, rooms: Dict[str, Dict[str, object]], room_to_opts: Dict[str, List[str]]) -> None:
    for room_key, room_data in rooms.items():
        prefix = room_data["prefix"]
        area_files = room_data["files"]
        top_files = room_data["top"]
        opts = room_to_opts.get(room_key, [])

        lines: List[str] = []
        lines.append("---")
        lines.append("type: repo-maze-room")
        lines.append("tags: [ovc, repo, maze, room]")
        lines.append("---")
        lines.append("")
        lines.append(f"# ROOM__{room_key}")
        lines.append("")
        lines.append("## What this area contains")
        lines.append(f"- Root: `{prefix}/`")
        lines.append(f"- File count: {len(area_files)}")
        lines.append("")
        lines.append("## Most important files")
        lines.append(to_md_list(top_files))
        lines.append("")
        lines.append("## Options that use this room")
        if opts:
            for opt in sorted(set(opts)):
                lines.append(f"- [[{opt}]]")
        else:
            lines.append("- none")

        write_note(out_dir / f"ROOM__{room_key}.md", "\n".join(lines))


def write_qa_governance(out_dir: Path, qa_anchors: Sequence[str], room_exists: Dict[str, bool]) -> None:
    lines: List[str] = []
    lines.append("---")
    lines.append("type: repo-maze-layer")
    lines.append("tags: [ovc, repo, maze, governance, qa]")
    lines.append("---")
    lines.append("")
    lines.append("# QA_GOVERNANCE")
    lines.append("")
    lines.append("## Definition")
    lines.append("System-wide QA/Governance layer (referee for A/B/C/D).")
    lines.append("")
    lines.append("## System Invariants")
    lines.append("- PASS/FAIL gates")
    lines.append("- Allowed drift thresholds")
    lines.append("- Determinism hashes")
    lines.append("- Boundary contracts")
    lines.append("")
    lines.append("## QA Anchors (real repo paths)")
    for room_key, prefix in ROOMS.items():
        if not room_exists.get(room_key, False):
            continue
        room_prefix = prefix.rstrip("/") + "/"
        room_anchors = [a for a in qa_anchors if a.startswith(room_prefix)]
        room_anchors = sort_by_score(room_anchors)[:25]
        lines.append(f"### {room_key}")
        lines.append(to_md_list(room_anchors))
        lines.append("")
    lines.append("## Applies to")
    lines.append(f"- [[{OPTION_SPINE[0]}]]")
    lines.append(f"- [[{OPTION_SPINE[1]}]]")
    lines.append(f"- [[{OPTION_SPINE[2]}]]")
    lines.append(f"- [[{OPTION_SPINE[3]}]]")
    lines.append("")
    lines.append("## Key corridors")
    lines.append("- A<->D: resample alignment, workflow ordering, hash normalization")

    write_note(out_dir / "QA_GOVERNANCE.md", "\n".join(lines))


def write_anchor_catalog(
    out_dir: Path,
    options: Dict[str, Dict[str, object]],
    room_exists: Dict[str, bool],
    workflows: Sequence[str],
    qa_anchors: Sequence[str],
) -> None:
    lines: List[str] = []
    lines.append("---")
    lines.append("type: repo-maze-catalog")
    lines.append("tags: [ovc, repo, maze, catalog]")
    lines.append("---")
    lines.append("")
    lines.append("# ANCHOR_CATALOG")
    lines.append("")
    lines.append("A deterministic catalog of anchors by Option and Room. Same repo state => same ordering.")
    lines.append("")

    for opt_name in OPTION_SPINE:
        data = options.get(opt_name, {})
        anchors_all = data.get("anchors_all", []) or data.get("anchors", [])
        if opt_name == "OPT_D__PATHS_BRIDGE":
            anchors_all = [a for a in anchors_all if not is_qa_anchor(a)]

        lines.append(f"## {opt_name}")
        for room_key, prefix in ROOMS.items():
            if not room_exists.get(room_key, False):
                continue
            room_prefix = prefix.rstrip("/") + "/"
            room_anchors = [a for a in anchors_all if a.startswith(room_prefix)]
            room_anchors = sort_by_score(room_anchors)[:25]
            lines.append(f"### {room_key}")
            lines.append(to_md_list(room_anchors))
            lines.append("")

    lines.append("## QA / Governance")
    for room_key, prefix in ROOMS.items():
        if not room_exists.get(room_key, False):
            continue
        room_prefix = prefix.rstrip("/") + "/"
        room_anchors = [a for a in qa_anchors if a.startswith(room_prefix)]
        room_anchors = sort_by_score(room_anchors)[:25]
        lines.append(f"### {room_key}")
        lines.append(to_md_list(room_anchors))
        lines.append("")

    # Cross-Option Corridors
    lines.append("## Cross-Option Corridors")
    lines.append(
        "Candidates only — these are not asserted boundaries, just high-signal paths to inspect."
    )
    lines.append("")

    corridor_kw = [
        "resample",
        "15m",
        "2h",
        "block",
        "timezone",
        "dst",
        "align",
        "normalize",
        "fingerprint",
        "determin",
    ]

    a_anchors = options.get("OPT_A__CANONICAL_INGEST", {}).get("anchors_all", [])
    d_anchors = options.get("OPT_D__PATHS_BRIDGE", {}).get("anchors_all", [])
    corridor_candidates = [p for p in (a_anchors + d_anchors) if match_any(corridor_kw, p)]
    corridor_candidates = sort_by_score(corridor_candidates)[:20]

    lines.append("### A<->D corridor anchors")
    lines.append(to_md_list(corridor_candidates))
    lines.append("")

    wf_kw = ["ingest", "path1", "path2", "validate", "evidence", "determin"]
    wf_candidates = []
    for wf in workflows:
        if match_any(wf_kw, Path(wf).name):
            wf_candidates.append(wf)
    wf_candidates = sort_by_score(wf_candidates)[:10]

    lines.append("### A<->D corridor workflows (filename match)")
    lines.append(to_md_list(wf_candidates))

    write_note(out_dir / "ANCHOR_CATALOG.md", "\n".join(lines))


def write_canvas(out_dir: Path) -> None:
    nodes = []
    edges = []

    def add_node(node_id: str, text: str, x: int, y: int, w: int = 260, h: int = 150) -> None:
        nodes.append({"id": node_id, "type": "text", "text": text, "x": x, "y": y, "width": w, "height": h})

    x0, y0 = -600, -220
    dx, dy = 280, 200

    add_node("n0", "# 00_REPO_MAZE\n[[00_REPO_MAZE]]", x0, y0, 280, 160)

    spine = [
        ("n1", "OPT_A__CANONICAL_INGEST"),
        ("n2", "OPT_D__PATHS_BRIDGE"),
        ("n3", "OPT_B__DERIVED_LAYERS"),
        ("n4", "OPT_C__OUTCOMES_EVAL"),
    ]
    for i, (nid, name) in enumerate(spine, start=1):
        add_node(nid, f"## {name}\n[[{name}]]", x0 + dx * i, y0, 300, 160)

    rooms = [
        ("n5", "ROOM__WORKFLOWS"),
        ("n6", "ROOM__DOCS"),
        ("n7", "ROOM__SQL"),
        ("n8", "ROOM__REPORTS"),
        ("n9", "ROOM__ARTIFACTS"),
    ]
    for j, (nid, name) in enumerate(rooms):
        add_node(nid, f"## {name}\n[[{name}]]", x0 + dx * (j + 1), y0 + dy, 260, 140)

    edge_i = 0
    def link(a: str, b: str) -> None:
        nonlocal edge_i
        edges.append({
            "id": f"e{edge_i}",
            "fromNode": a,
            "fromSide": "right",
            "toNode": b,
            "toSide": "left",
        })
        edge_i += 1

    # index to first option
    link("n0", "n1")
    # QA canopy
    add_node("n10", "## QA_GOVERNANCE\n[[QA_GOVERNANCE]]", x0 + dx * 2, y0 - dy, 280, 150)
    link("n10", "n1")
    link("n10", "n2")
    link("n10", "n3")
    link("n10", "n4")
    # spine
    link("n1", "n2")
    link("n2", "n3")
    link("n3", "n4")

    canvas = {"nodes": nodes, "edges": edges}
    (out_dir / "OVC_REPO_MAZE.canvas").write_text(json.dumps(canvas, indent=2), encoding="utf-8")


def verify_outputs(out_dir: Path, max_notes: int = 15, min_bytes: int = 200) -> None:
    notes = sorted(out_dir.glob("*.md"))
    if len(notes) > max_notes:
        raise SystemExit(f"Too many notes: {len(notes)} (max {max_notes})")
    small = [n for n in notes if n.stat().st_size <= min_bytes]
    if small:
        names = ", ".join(n.name for n in small)
        raise SystemExit(f"Notes below size threshold ({min_bytes} bytes): {names}")


# ----------------------------
# Main
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a curated Obsidian repo maze (small graph).")
    ap.add_argument("--repo", required=True, help="Repo root")
    ap.add_argument("--out", required=True, help="Output folder inside Obsidian vault")
    ap.add_argument("--wipe", action="store_true", help="Delete and recreate output folder")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()

    if not repo_root.exists() or not repo_root.is_dir():
        raise SystemExit(f"--repo is not a directory: {repo_root}")
    if out_dir.name != "OVC_REPO_MAZE":
        raise SystemExit(f"Refusing to write outside OVC_REPO_MAZE: {out_dir}")

    # scan repo
    all_files = iter_files(repo_root)
    workflows = list_area_files(all_files, ".github/workflows")

    # top-level folders (exclude ignored + hidden)
    top_dirs = []
    for p in repo_root.iterdir():
        if not p.is_dir():
            continue
        if p.name in DEFAULT_IGNORE_DIRS:
            continue
        if p.name.startswith(".") and p.name != ".github":
            continue
        top_dirs.append(p.name)
    top_dirs = sorted(top_dirs)

    rooms = build_rooms(all_files)
    qa_anchors = build_qa_anchors(all_files)
    options = build_options(all_files, workflows)
    room_to_opts = rooms_used_by_option(options)
    room_exists = {}
    for room_key, prefix in ROOMS.items():
        room_path = repo_root / prefix
        room_exists[room_key] = room_path.exists() and room_path.is_dir()

    # write outputs
    if args.wipe:
        ensure_dir_clean(out_dir)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
    write_index(out_dir, rooms, options, top_dirs)
    write_option_notes(out_dir, options)
    write_room_notes(out_dir, rooms, room_to_opts)
    write_qa_governance(out_dir, qa_anchors, room_exists)
    write_anchor_catalog(out_dir, options, room_exists, workflows, qa_anchors)
    write_canvas(out_dir)
    verify_outputs(out_dir)

    print("Curated Repo Maze generated")
    print(f"Output folder: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
