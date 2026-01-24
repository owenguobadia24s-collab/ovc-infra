#!/usr/bin/env python3
"""
OVC Repo Maze Generator (CURATED) — Obsidian-friendly, low-node-count, semantic graph

Fixes the “1k empty notes” failure mode by generating ~10–30 *curated* notes total:
- 00_REPO_MAZE.md (index)
- OPT_A/B/C/D notes (Option spine)
- ROOM__WORKFLOWS / DOCS / SQL / REPORTS / ARTIFACTS (system rooms)
- Optional extra rooms only if they actually exist (TOOLS, SCRIPTS, SRC)

It DOES NOT:
- create a note per directory
- create a note per file

It DOES:
- scan the repo
- pick “anchors” (real existing repo paths) and place them under Options + Rooms
- generate a single Obsidian Canvas showing the spine + core rooms

Usage:
  python tools/maze/gen_repo_maze_curated.py --repo . --out "C:\\Users\\Owner\\projects\\ovc-infra\\Tetsu\\OVC_REPO_MAZE" --wipe

Recommended:
  --wipe  (deletes the previous junk output folder contents safely)

Constraints enforced:
- note count <= 40
- each note > 200 bytes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ----------------------------
# Scanning limits / filtering
# ----------------------------

IGNORE_DIRS = {
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

# we only want to show these as “rooms” by default (plus extras if present)
CORE_ROOM_DIRS = [
    ".github/workflows",
    "docs",
    "sql",
    "reports",
    "artifacts",
]

EXTRA_ROOM_DIRS = [
    "tools",
    "scripts",
    "src",
]

# anchor selection: prefer these extensions and key filenames
PREFERRED_EXTS = {".md", ".sql", ".py", ".ts", ".js", ".yml", ".yaml", ".json", ".toml"}
PREFERRED_NAME_HINTS = [
    "readme", "contract", "spec", "boundary", "registry", "metric", "map",
    "path1", "path2", "evidence", "validate", "validation", "determin", "fingerprint",
    "ingest", "canonical", "export", "c0", "c1", "c2", "c3",
    "outcome", "eval", "evaluation", "label",
    "main.yml", "workflow",
]

MAX_ANCHORS_PER_ROOM = 30
MAX_ANCHORS_PER_OPTION = 40

MIN_NOTE_BYTES = 200
MAX_NOTES = 40


# ----------------------------
# Option classification heuristics
# ----------------------------

@dataclass(frozen=True)
class OptionDef:
    key: str
    title: str
    definition: str
    keywords: Tuple[str, ...]
    # directories that strongly indicate membership
    dir_prefixes: Tuple[str, ...]


OPTION_DEFS = [
    OptionDef(
        key="A",
        title="OPT_A__CANONICAL_INGEST",
        definition="Canonical ingest: raw/source → canonical facts (C0/R) and early primitives (C1).",
        keywords=("ingest", "canonical", "canon", "export", "c0", "c1", "worker", "wrangler", "neon", "oanda", "tradingview"),
        dir_prefixes=("ingest", "canonical", "c0", "c1", "export", "workers"),
    ),
    OptionDef(
        key="D",
        title="OPT_D__PATHS_QA_BRIDGE",
        definition="Paths + QA bridge: Path1 evidence runner + Path2 determinism tightening. This is the A↔D corridor.",
        keywords=("path1", "path2", "qa", "validate", "validation", "evidence", "determin", "fingerprint", "harness", "drift"),
        dir_prefixes=("path1", "path2", "qa", "validation", "evidence", "tests"),
    ),
    OptionDef(
        key="B",
        title="OPT_B__DERIVED_LAYERS",
        definition="Derived layers: compute C2/C3 features, registries, thresholds, and semantic tags from canonical facts.",
        keywords=("derived", "features", "feature", "registry", "threshold", "c2", "c3", "compute_c2", "compute_c3", "tag", "metric"),
        dir_prefixes=("c2", "c3", "derived", "features", "registry", "registries"),
    ),
    OptionDef(
        key="C",
        title="OPT_C__OUTCOMES_EVAL",
        definition="Outcomes & evaluation: labeling what happened, evaluation reports, regression checks, and feedback artifacts.",
        keywords=("outcome", "outcomes", "eval", "evaluation", "label", "labels", "regression", "score", "grading"),
        dir_prefixes=("outcomes", "evaluation", "eval", "labels"),
    ),
]

OPTION_SPINE = ["A", "D", "B", "C"]


# ----------------------------
# Utility
# ----------------------------

def rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()

def is_ignored_dir(path_parts: Tuple[str, ...]) -> bool:
    return any(part in IGNORE_DIRS for part in path_parts)

def score_path(path_str: str) -> int:
    """Higher score = more likely to be a meaningful anchor."""
    s = path_str.lower()
    score = 0
    # extension preference
    ext = Path(path_str).suffix.lower()
    if ext in PREFERRED_EXTS:
        score += 3
    # name hints
    for h in PREFERRED_NAME_HINTS:
        if h in s:
            score += 5
    # shorter paths tend to be more “core” (not always, but good heuristic)
    score += max(0, 8 - s.count("/"))
    return score

def list_files_under(root: Path, subdir: str) -> List[str]:
    base = root / subdir
    if not base.exists():
        return []
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        rp = Path(dirpath).relative_to(root)
        if is_ignored_dir(rp.parts):
            dirnames[:] = []
            continue
        for fn in filenames:
            # keep only reasonable candidates
            p = (Path(dirpath) / fn)
            ext = p.suffix.lower()
            if ext and ext not in PREFERRED_EXTS:
                continue
            out.append(rel(p, root))
    return sorted(set(out))

def top_n_scored(paths: List[str], n: int) -> List[str]:
    scored = sorted(((score_path(p), p) for p in paths), key=lambda x: (-x[0], x[1]))
    return [p for _, p in scored[:n]]

def classify_option_for_path(path_str: str) -> Set[str]:
    s = path_str.lower()
    hits: Set[str] = set()
    # directory prefix rule
    for opt in OPTION_DEFS:
        for pref in opt.dir_prefixes:
            if s.startswith(pref + "/") or f"/{pref}/" in s:
                hits.add(opt.key)
        # keyword hits
        for kw in opt.keywords:
            if kw in s:
                hits.add(opt.key)
    return hits

def mk_canvas(nodes: List[dict], edges: List[dict]) -> dict:
    return {"nodes": nodes, "edges": edges}


# ----------------------------
# Content builders
# ----------------------------

def build_rooms(repo_root: Path) -> Dict[str, List[str]]:
    rooms: Dict[str, List[str]] = {}
    for d in CORE_ROOM_DIRS + EXTRA_ROOM_DIRS:
        paths = list_files_under(repo_root, d)
        if paths:
            rooms[d] = top_n_scored(paths, MAX_ANCHORS_PER_ROOM)
    return rooms

def build_options_from_rooms(rooms: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Assign anchors to options based on heuristics across discovered room files."""
    opt_anchors: Dict[str, Set[str]] = {o.key: set() for o in OPTION_DEFS}
    all_paths = []
    for _, ps in rooms.items():
        all_paths.extend(ps)
    all_paths = sorted(set(all_paths))

    for p in all_paths:
        hits = classify_option_for_path(p)
        for k in hits:
            opt_anchors[k].add(p)

    # cap + sort for stability
    out: Dict[str, List[str]] = {}
    for opt in OPTION_DEFS:
        lst = sorted(opt_anchors[opt.key])
        out[opt.key] = top_n_scored(lst, MAX_ANCHORS_PER_OPTION)
    return out

def build_workflow_list(rooms: Dict[str, List[str]]) -> List[str]:
    wf = rooms.get(".github/workflows", [])
    # only keep yaml
    wf = [p for p in wf if p.lower().endswith((".yml", ".yaml"))]
    return wf[:30]

def note_header(frontmatter: Dict[str, str | List[str]]) -> str:
    lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)

def ensure_min_size(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Expected note not written: {path}")
    if path.stat().st_size < MIN_NOTE_BYTES:
        raise RuntimeError(f"Note too small (<{MIN_NOTE_BYTES} bytes): {path.name}")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ----------------------------
# Note templates
# ----------------------------

def render_index(rooms: Dict[str, List[str]]) -> str:
    room_links = []
    for d in CORE_ROOM_DIRS:
        if d in rooms:
            room_links.append(f"- [[ROOM__{room_name(d)}]]  (`/{d}`)")
    for d in EXTRA_ROOM_DIRS:
        if d in rooms:
            room_links.append(f"- [[ROOM__{room_name(d)}]]  (`/{d}`)")

    return (
        note_header({"type": "maze-index", "tags": ["ovc", "repo", "maze", "moc"]})
        + "# OVC Repo Maze (Curated)\n\n"
        + "This is the *semantic* map (low-node-count). It sorts the repo into **Option A/B/C/D** and links the real anchors.\n\n"
        + "## Option Spine\n"
        + "- [[OPT_A__CANONICAL_INGEST]] → [[OPT_D__PATHS_QA_BRIDGE]] → [[OPT_B__DERIVED_LAYERS]] → [[OPT_C__OUTCOMES_EVAL]]\n\n"
        + "## System Rooms\n"
        + ("\n".join(room_links) if room_links else "- _(no rooms detected)_")
        + "\n\n"
        + "## How to use\n"
        + "- Open Graph View and filter: `path:\"OVC_REPO_MAZE\"`\n"
        + "- Start at Option D for the A↔D corridor (2H→15m resample + workflow ordering).\n"
    )

def room_name(dir_path: str) -> str:
    # ".github/workflows" -> "WORKFLOWS"
    if dir_path == ".github/workflows":
        return "WORKFLOWS"
    return dir_path.strip("/").replace("/", "__").upper()

def render_room(dir_path: str, anchors: List[str]) -> str:
    rn = room_name(dir_path)
    intro = {
        ".github/workflows": "GitHub Actions: ordering is fate. These workflows orchestrate A→D→B→C.",
        "docs": "Repo documentation: contracts, invariants, mental model. (This should be the source-of-truth for boundaries.)",
        "sql": "SQL surface: migrations, queries, evidence-run SQL, validation queries.",
        "reports": "Reports/evidence outputs: Path1 packs, validation summaries, run writeups.",
        "artifacts": "Artifacts: small machine-readable outputs passed between steps (hashes, indexes, summaries).",
    }.get(dir_path, "Repo area detected by scanner.")

    body = "\n".join([f"- `{p}`" for p in anchors]) if anchors else "- _(no anchors)_"
    return (
        note_header({"type": "maze-room", "tags": ["ovc", "maze", "room"]})
        + f"# ROOM__{rn}\n\n"
        + f"**Directory:** `/{dir_path}`\n\n"
        + f"## What this room is\n{intro}\n\n"
        + "## Top anchors (curated)\n"
        + body
        + "\n\n"
        + "## Used by\n"
        + "- [[OPT_A__CANONICAL_INGEST]]\n"
        + "- [[OPT_D__PATHS_QA_BRIDGE]]\n"
        + "- [[OPT_B__DERIVED_LAYERS]]\n"
        + "- [[OPT_C__OUTCOMES_EVAL]]\n"
    )

def render_option(opt: OptionDef, opt_anchors: List[str], workflows: List[str], rooms: Dict[str, List[str]]) -> str:
    key = opt.key
    spine_links = {
        "A": "→ [[OPT_D__PATHS_QA_BRIDGE]]",
        "D": "← [[OPT_A__CANONICAL_INGEST]]  → [[OPT_B__DERIVED_LAYERS]]",
        "B": "← [[OPT_D__PATHS_QA_BRIDGE]]  → [[OPT_C__OUTCOMES_EVAL]]",
        "C": "← [[OPT_B__DERIVED_LAYERS]]",
    }[key]

    # room links that exist
    room_links = []
    for d in CORE_ROOM_DIRS:
        if d in rooms:
            room_links.append(f"- [[ROOM__{room_name(d)}]]")
    for d in EXTRA_ROOM_DIRS:
        if d in rooms:
            room_links.append(f"- [[ROOM__{room_name(d)}]]")

    anchors_txt = "\n".join([f"- `{p}`" for p in opt_anchors]) if opt_anchors else "- _(no anchors matched heuristics; add keywords/dir rules)_"

    # workflows relevant to this option by keyword (light filter)
    kw = list(opt.keywords)
    wf_relevant = []
    for w in workflows:
        wl = w.lower()
        if any(k in wl for k in kw):
            wf_relevant.append(w)
    wf_relevant = wf_relevant[:20]
    wf_txt = "\n".join([f"- `{p}`" for p in wf_relevant]) if wf_relevant else "- _(no obvious workflow matches)_"

    # input/output “best effort” based on key
    io = {
        "A": ("Raw/source events → canonical facts (C0/R) (+ maybe C1 primitives).", "Canonical dataset + export contract outputs."),
        "D": ("Option A outputs + run config → evidence packs + determinism checks.", "PASS/FAIL evidence, hashes, run-ledger artifacts."),
        "B": ("Canonical facts + verified evidence → C2/C3 derived packs, registries, semantic tags.", "Derived tables/features, registry-driven tags."),
        "C": ("Verified structure + derived evidence → outcomes/eval/regression outputs.", "Outcome labels + evaluation reports."),
    }[key]

    special = ""
    if key == "D":
        special = (
            "\n## The A↔D pain corridor (explicit)\n"
            "- Resample boundary: where 2H intake becomes 15m (must be *single source of truth*).\n"
            "- Workflow ordering: ensure A completes and publishes artifacts *before* D consumes them.\n"
            "- Determinism: stable hashes + normalized hashes for reruns.\n"
        )

    return (
        note_header({"type": "maze-option", "tags": ["ovc", "maze", "option", f"opt-{key.lower()}"]})
        + f"# {opt.title}\n\n"
        + f"**Definition:** {opt.definition}\n\n"
        + f"**Spine:** {spine_links}\n\n"
        + "## Inputs → Outputs\n"
        + f"- **Inputs:** {io[0]}\n"
        + f"- **Outputs:** {io[1]}\n\n"
        + "## Key rooms\n"
        + ("\n".join(room_links) if room_links else "- _(no rooms detected)_")
        + "\n\n"
        + "## Key workflows (heuristic)\n"
        + wf_txt
        + "\n\n"
        + "## Anchors (real repo paths)\n"
        + anchors_txt
        + "\n"
        + special
    )


# ----------------------------
# Canvas generator (small)
# ----------------------------

def render_canvas(out_dir: Path, rooms: Dict[str, List[str]]) -> None:
    # nodes to include
    spine_titles = [
        "00_REPO_MAZE",
        "OPT_A__CANONICAL_INGEST",
        "OPT_D__PATHS_QA_BRIDGE",
        "OPT_B__DERIVED_LAYERS",
        "OPT_C__OUTCOMES_EVAL",
    ]

    room_titles = []
    for d in CORE_ROOM_DIRS:
        if d in rooms:
            room_titles.append(f"ROOM__{room_name(d)}")

    nodes = []
    edges = []

    def add_node(nid: str, text: str, x: int, y: int, w: int = 280, h: int = 160):
        nodes.append({"id": nid, "type": "text", "text": text, "x": x, "y": y, "width": w, "height": h})

    id_by = {t: f"n{i}" for i, t in enumerate(spine_titles + room_titles)}

    x0, y0 = -760, -220
    dx, dy = 330, 210

    # index
    add_node(id_by["00_REPO_MAZE"], "# Index\n[[00_REPO_MAZE]]", x0, y0, 260, 140)

    # spine row
    for i, t in enumerate(spine_titles[1:]):
        add_node(id_by[t], f"## {t}\n[[{t}]]", x0 + dx * (i + 1), y0, 320 if "OPT_D" in t else 280, 160)

    # rooms under
    for j, t in enumerate(room_titles):
        add_node(id_by[t], f"## {t}\n[[{t}]]", x0 + dx * (j + 1), y0 + dy, 280, 140)

    # edges: index -> options
    e = 0
    for t in spine_titles[1:]:
        edges.append({"id": f"e{e}", "fromNode": id_by["00_REPO_MAZE"], "fromSide": "right", "toNode": id_by[t], "toSide": "left"})
        e += 1

    # edges: spine order A->D->B->C
    spine = spine_titles[1:]
    for a, b in zip(spine, spine[1:]):
        edges.append({"id": f"e{e}", "fromNode": id_by[a], "fromSide": "right", "toNode": id_by[b], "toSide": "left"})
        e += 1

    # edges: rooms connect to D (bridge), and to A/B/C lightly
    for t in room_titles:
        edges.append({"id": f"e{e}", "fromNode": id_by[t], "fromSide": "top", "toNode": id_by["OPT_D__PATHS_QA_BRIDGE"], "toSide": "bottom"})
        e += 1

    canvas = mk_canvas(nodes, edges)
    (out_dir / "OVC_REPO_MAZE.canvas").write_text(json.dumps(canvas, indent=2), encoding="utf-8")


# ----------------------------
# Main
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a curated Obsidian repo maze (low node count).")
    ap.add_argument("--repo", required=True, help="Repo root path (e.g. .)")
    ap.add_argument("--out", required=True, help="Output folder inside Obsidian vault (e.g. .../Tetsu/OVC_REPO_MAZE)")
    ap.add_argument("--wipe", action="store_true", help="Delete output folder contents before writing")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()

    if not repo_root.exists() or not repo_root.is_dir():
        raise SystemExit(f"--repo is not a directory: {repo_root}")

    if args.wipe and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Scan
    rooms = build_rooms(repo_root)
    workflows = build_workflow_list(rooms)
    opt_anchors = build_options_from_rooms(rooms)

    # Write notes (curated set)
    written: List[Path] = []

    # Index
    write_text(out_dir / "00_REPO_MAZE.md", render_index(rooms))
    written.append(out_dir / "00_REPO_MAZE.md")

    # Rooms
    for d, anchors in rooms.items():
        # only create room notes for core + extras that exist
        if d not in CORE_ROOM_DIRS and d not in EXTRA_ROOM_DIRS:
            continue
        nm = f"ROOM__{room_name(d)}.md"
        write_text(out_dir / nm, render_room(d, anchors))
        written.append(out_dir / nm)

    # Options
    opt_by_key = {o.key: o for o in OPTION_DEFS}
    for k in OPTION_SPINE:
        o = opt_by_key[k]
        nm = f"{o.title}.md"
        write_text(out_dir / nm, render_option(o, opt_anchors.get(k, []), workflows, rooms))
        written.append(out_dir / nm)

    # Canvas
    render_canvas(out_dir, rooms)
    canvas_path = out_dir / "OVC_REPO_MAZE.canvas"

    # Verification
    created_notes = [p for p in written if p.suffix.lower() == ".md"]
    note_count = len(created_notes)

    if note_count > MAX_NOTES:
        raise RuntimeError(f"Too many notes generated: {note_count} > {MAX_NOTES}")

    for p in created_notes:
        ensure_min_size(p)

    if not canvas_path.exists():
        raise RuntimeError("Canvas missing")

    # Print summary
    print("✅ Curated Repo Maze generated")
    print(f"Output folder: {out_dir}")
    print(f"Notes created: {note_count}")
    for p in sorted(created_notes):
        print(f" - {p.name}")
    print(f"Canvas: {canvas_path.name} (exists=True)")
    print("\nObsidian tip: Graph filter →  path:\"OVC_REPO_MAZE\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
