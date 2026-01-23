#!/usr/bin/env python3
"""
OVC Repo Maze Generator (Obsidian) — v2 (adds Option A/B/C/D special nodes)

What it does:
- Walks a repo folder
- Generates an Obsidian “maze” folder with:
  - one Markdown node per directory
  - optional nodes for selected files (workflows/sql/docs/scripts)
  - backlinks between nodes:
      * parent <-> child directory links
      * directory <-> file links
      * inferred references from file contents (lightweight)
- Generates:
  - 00_REPO_MAZE.md (index)
  - OVC_REPO_MAZE.canvas (Obsidian Canvas)
  - OPTION nodes:
      - OPT_A__CANONICAL_INGEST.md
      - OPT_B__DERIVED_LAYERS.md
      - OPT_C__OUTCOMES_EVAL.md
      - OPT_D__PATHS_QA_BRIDGE.md

The option nodes auto-link to directories/files by heuristic rules (no hallucinations):
- If relevant directories exist, they get linked.
- If relevant workflow files exist, they get linked.
- If nothing matches, the option node stays sparse (truth > vibes).

Usage:
  python tools/maze/gen_repo_maze.py --repo . --out ../Testudo/OVC_REPO_MAZE --include-files
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ----------------------------
# Config / heuristics
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

# We want workflows even if we ignore other .github contents
FORCE_INCLUDE_DIRS = {
    ".github/workflows",
}

FILE_NODE_PATTERNS = [
    re.compile(r"\.github/workflows/.*\.ya?ml$", re.I),
    re.compile(r"^docs/.*\.md$", re.I),
    re.compile(r"^sql/.*\.(sql|md)$", re.I),
    re.compile(r"^reports/.*\.(md|json)$", re.I),
    re.compile(r"^artifacts/.*\.(json|md)$", re.I),
    re.compile(r"^tools/.*\.(py|ts|js|md|yml|yaml|sh)$", re.I),
    re.compile(r"^scripts/.*\.(py|ts|js|sh|md)$", re.I),
    re.compile(r"^src/.*\.(py|ts|js|md)$", re.I),
]

PATH_REF_REGEXES = [
    re.compile(r"(?P<path>(?:docs|sql|reports|artifacts|tools|scripts|src|\.github/workflows)/[A-Za-z0-9_\-./]+)"),
    re.compile(r"(?P<path>\.github/workflows/[A-Za-z0-9_\-./]+\.ya?ml)", re.I),
]

BAD_FILENAME_CHARS = re.compile(r"[<>:\"/\\|?*\x00-\x1F]")


# ----------------------------
# Data model
# ----------------------------

@dataclass
class Node:
    node_id: str
    kind: str  # "dir" | "file" | "index" | "option"
    repo_rel: str
    title: str
    links: Set[str]


# ----------------------------
# Helpers
# ----------------------------

def norm_relpath(p: Path) -> str:
    return p.as_posix().lstrip("./")

def safe_title_from_relpath(rel: str, kind: str) -> str:
    rel = rel.strip("/")
    if rel == "":
        rel = "REPO_ROOT"

    s = rel.replace("/", "__")
    s = s.replace(".", "_")
    s = BAD_FILENAME_CHARS.sub("_", s)

    prefix = "DIR_" if kind == "dir" else "FILE_" if kind == "file" else "NODE_"
    return f"{prefix}{s}"

def should_ignore_dir(rel_dir: str, ignore_dirs: Set[str]) -> bool:
    parts = rel_dir.split("/") if rel_dir else []
    if parts and parts[0] in ignore_dirs:
        # allow forced include subpaths
        for forced in FORCE_INCLUDE_DIRS:
            if rel_dir == forced or rel_dir.startswith(forced + "/"):
                return False
        return True
    if rel_dir in ignore_dirs:
        return True
    return False

def match_file_node(rel_file: str) -> bool:
    rel_file = rel_file.lstrip("./")
    for pat in FILE_NODE_PATTERNS:
        if pat.search(rel_file):
            return True
    return False

def read_text_limited(path: Path, max_bytes: int) -> Optional[str]:
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

def extract_referenced_paths(text: str) -> Set[str]:
    refs: Set[str] = set()
    for rx in PATH_REF_REGEXES:
        for m in rx.finditer(text):
            p = m.group("path").lstrip("./").rstrip(").,;:'\"")
            refs.add(p)
    return refs

def title_exists(nodes_by_title: Dict[str, Node], title: str) -> bool:
    return title in nodes_by_title

def find_dir_title(title_by_repo_rel: Dict[str, str], rel_dir: str) -> Optional[str]:
    return title_by_repo_rel.get(rel_dir)

def find_any_dir_startswith(nodes_by_title: Dict[str, Node], rel_prefix: str) -> List[str]:
    out = []
    for n in nodes_by_title.values():
        if n.kind == "dir" and n.repo_rel and (n.repo_rel == rel_prefix or n.repo_rel.startswith(rel_prefix + "/")):
            out.append(n.title)
    return sorted(set(out))

def find_file_titles_matching(nodes_by_title: Dict[str, Node], rx: re.Pattern) -> List[str]:
    out = []
    for n in nodes_by_title.values():
        if n.kind == "file" and rx.search(n.repo_rel):
            out.append(n.title)
    return sorted(set(out))


# ----------------------------
# Build nodes (dirs + files)
# ----------------------------

def build_nodes(
    repo_root: Path,
    include_files: bool,
    ignore_dirs: Set[str],
    max_file_bytes: int,
) -> Tuple[Dict[str, Node], Dict[str, str], List[str]]:
    nodes_by_title: Dict[str, Node] = {}
    title_by_repo_rel: Dict[str, str] = {}

    # Directory nodes
    all_dirs: Set[str] = set()
    all_dirs.add("")  # root

    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel_dir = norm_relpath(Path(dirpath).relative_to(repo_root))
        if rel_dir == ".":
            rel_dir = ""
        if rel_dir and should_ignore_dir(rel_dir, ignore_dirs):
            dirnames[:] = []
            continue

        all_dirs.add(rel_dir)

        pruned = []
        for d in dirnames:
            candidate = f"{rel_dir}/{d}".strip("/")
            if should_ignore_dir(candidate, ignore_dirs):
                keep = any(fi.startswith(candidate + "/") or fi == candidate for fi in FORCE_INCLUDE_DIRS)
                if keep:
                    pruned.append(d)
            else:
                pruned.append(d)
        dirnames[:] = pruned

    for rel_dir in sorted(all_dirs):
        title = safe_title_from_relpath(rel_dir if rel_dir else "REPO_ROOT", "dir")
        node = Node(
            node_id=f"dir:{rel_dir or '.'}",
            kind="dir",
            repo_rel=rel_dir,
            title=title,
            links=set(),
        )
        nodes_by_title[title] = node
        title_by_repo_rel[rel_dir] = title

    # File nodes
    file_relpaths: List[str] = []
    if include_files:
        for dirpath, dirnames, filenames in os.walk(repo_root):
            rel_dir = norm_relpath(Path(dirpath).relative_to(repo_root))
            if rel_dir == ".":
                rel_dir = ""
            if rel_dir and should_ignore_dir(rel_dir, ignore_dirs):
                dirnames[:] = []
                continue

            pruned = []
            for d in dirnames:
                candidate = f"{rel_dir}/{d}".strip("/")
                if should_ignore_dir(candidate, ignore_dirs):
                    keep = any(fi.startswith(candidate + "/") or fi == candidate for fi in FORCE_INCLUDE_DIRS)
                    if keep:
                        pruned.append(d)
                else:
                    pruned.append(d)
            dirnames[:] = pruned

            for fn in filenames:
                rel_file = f"{rel_dir}/{fn}".strip("/")
                if rel_file.startswith(".github/workflows/") and re.search(r"\.ya?ml$", rel_file, re.I):
                    file_relpaths.append(rel_file)
                    continue
                if match_file_node(rel_file):
                    file_relpaths.append(rel_file)

        file_relpaths = sorted(set(file_relpaths))

        for rel_file in file_relpaths:
            title = safe_title_from_relpath(rel_file, "file")
            node = Node(
                node_id=f"file:{rel_file}",
                kind="file",
                repo_rel=rel_file,
                title=title,
                links=set(),
            )
            nodes_by_title[title] = node
            title_by_repo_rel[rel_file] = title

    # Parent <-> child directory links
    for rel_dir in sorted(all_dirs):
        if not rel_dir:
            continue
        parent = str(Path(rel_dir).parent)
        if parent == ".":
            parent = ""
        child_title = title_by_repo_rel.get(rel_dir)
        parent_title = title_by_repo_rel.get(parent)
        if child_title and parent_title:
            nodes_by_title[parent_title].links.add(child_title)
            nodes_by_title[child_title].links.add(parent_title)

    # File <-> containing directory links
    if include_files:
        for rel_file in file_relpaths:
            dir_rel = str(Path(rel_file).parent)
            if dir_rel == ".":
                dir_rel = ""
            file_title = title_by_repo_rel.get(rel_file)
            dir_title = title_by_repo_rel.get(dir_rel)
            if file_title and dir_title:
                nodes_by_title[file_title].links.add(dir_title)
                nodes_by_title[dir_title].links.add(file_title)

    # Infer links from file contents (file -> dirs/files)
    if include_files:
        for rel_file in file_relpaths:
            abs_file = repo_root / rel_file
            text = read_text_limited(abs_file, max_file_bytes)
            if not text:
                continue
            refs = extract_referenced_paths(text)
            from_title = title_by_repo_rel.get(rel_file)
            if not from_title:
                continue

            for ref in refs:
                # exact node (file or dir)
                if ref in title_by_repo_rel:
                    nodes_by_title[from_title].links.add(title_by_repo_rel[ref])
                    continue

                # walk up for nearest directory node
                probe = ref
                while probe and probe not in title_by_repo_rel:
                    parent = str(Path(probe).parent)
                    if parent in (".", probe):
                        break
                    probe = parent
                if probe in title_by_repo_rel:
                    nodes_by_title[from_title].links.add(title_by_repo_rel[probe])

    return nodes_by_title, title_by_repo_rel, file_relpaths


# ----------------------------
# Option nodes (A/B/C/D)
# ----------------------------

@dataclass(frozen=True)
class OptionSpec:
    key: str
    title: str
    desc: str
    # heuristics: relevant directories and workflow/file patterns
    dir_prefixes: Tuple[str, ...]
    file_title_regexes: Tuple[re.Pattern, ...]


OPTION_SPECS: List[OptionSpec] = [
    OptionSpec(
        key="A",
        title="OPT_A__CANONICAL_INGEST",
        desc="Option A — Canonical Ingest (C0/R + C1). Raw → canonical facts you can re-run and audit.",
        dir_prefixes=("ingest", "c0", "c1", "data", "raw", "canon", "canonical", "export", "contracts", "sql", "docs"),
        file_title_regexes=(
            re.compile(r"\.github/workflows/.*(ingest|canon|export|c0|c1).*\.ya?ml$", re.I),
            re.compile(r"(^|/)compute_c1|c0|canonical|export", re.I),
        ),
    ),
    OptionSpec(
        key="B",
        title="OPT_B__DERIVED_LAYERS",
        desc="Option B — Derived Layers (C2/C3). Feature packs, evidence, registries, semantics.",
        dir_prefixes=("c2", "c3", "derived", "features", "registry", "registries", "sql", "docs"),
        file_title_regexes=(
            re.compile(r"\.github/workflows/.*(c2|c3|derived|features|registry).*\.ya?ml$", re.I),
            re.compile(r"(compute_c2|compute_c3|derived|registry|metric_map|boundary_spec)", re.I),
        ),
    ),
    OptionSpec(
        key="C",
        title="OPT_C__OUTCOMES_EVAL",
        desc="Option C — Outcomes/Evaluation. Labeling what happened + evaluation reports/regressions.",
        dir_prefixes=("outcomes", "eval", "evaluation", "labels", "label", "reports", "artifacts", "docs"),
        file_title_regexes=(
            re.compile(r"\.github/workflows/.*(outcome|eval|evaluation|label).*\.ya?ml$", re.I),
            re.compile(r"(outcome|evaluation|label|regression)", re.I),
        ),
    ),
    OptionSpec(
        key="D",
        title="OPT_D__PATHS_QA_BRIDGE",
        desc="Option D — Paths + QA Bridge (Path1/Path2). Evidence runner + determinism tightening. A↔D is the famous pain corridor.",
        dir_prefixes=("path1", "path2", "qa", "validation", "reports", "artifacts", "sql", ".github/workflows", "docs"),
        file_title_regexes=(
            re.compile(r"\.github/workflows/.*(path1|path2|qa|validate|validation|determin).*\.ya?ml$", re.I),
            re.compile(r"(path1|path2|validation|determin|fingerprint|evidence)", re.I),
        ),
    ),
]

def add_option_nodes(
    nodes_by_title: Dict[str, Node],
    title_by_repo_rel: Dict[str, str],
    file_relpaths: List[str],
    include_files: bool,
) -> List[str]:
    """
    Create A/B/C/D nodes and wire them to existing directory/file nodes by heuristics.
    Returns titles of created option nodes.
    """
    option_titles: List[str] = []

    # index / root titles
    root_title = title_by_repo_rel.get("", "DIR_REPO_ROOT")
    workflows_dir_title = title_by_repo_rel.get(".github/workflows")

    # precompute candidate directory titles by prefixes
    dir_titles_by_prefix: Dict[str, List[str]] = {}
    for spec in OPTION_SPECS:
        collected: Set[str] = set()
        for prefix in spec.dir_prefixes:
            # exact directory
            exact = find_dir_title(title_by_repo_rel, prefix)
            if exact:
                collected.add(exact)
            # any directories that start with that prefix
            for t in find_any_dir_startswith(nodes_by_title, prefix):
                collected.add(t)
        dir_titles_by_prefix[spec.key] = sorted(collected)

    # map file relpaths -> file node title
    file_titles: List[str] = []
    if include_files:
        for rel in file_relpaths:
            t = title_by_repo_rel.get(rel)
            if t:
                file_titles.append(t)

    # create option nodes
    for spec in OPTION_SPECS:
        t = spec.title
        if t in nodes_by_title:
            continue

        node = Node(
            node_id=f"opt:{spec.key}",
            kind="option",
            repo_rel=f"OPTION_{spec.key}",
            title=t,
            links=set(),
        )

        # Always link to root + index-ish anchors (root node exists, index is separate file)
        if root_title in nodes_by_title:
            node.links.add(root_title)

        # Always link to workflows dir if present (Option nodes often depend on orchestration)
        if workflows_dir_title and workflows_dir_title in nodes_by_title:
            node.links.add(workflows_dir_title)

        # Link to relevant dirs found
        for dt in dir_titles_by_prefix.get(spec.key, []):
            if dt in nodes_by_title:
                node.links.add(dt)

        # Link to relevant file nodes by regex (only if include_files)
        if include_files and file_titles:
            for rx in spec.file_title_regexes:
                # match against repo_rel (not title)
                for n in nodes_by_title.values():
                    if n.kind != "file":
                        continue
                    if rx.search(n.repo_rel):
                        node.links.add(n.title)

        nodes_by_title[t] = node
        option_titles.append(t)

    # Cross-link options in flow order A -> D -> B -> C (your canonical pipeline framing)
    def link(a: str, b: str):
        if a in nodes_by_title and b in nodes_by_title:
            nodes_by_title[a].links.add(b)
            nodes_by_title[b].links.add(a)

    link("OPT_A__CANONICAL_INGEST", "OPT_D__PATHS_QA_BRIDGE")
    link("OPT_D__PATHS_QA_BRIDGE", "OPT_B__DERIVED_LAYERS")
    link("OPT_B__DERIVED_LAYERS", "OPT_C__OUTCOMES_EVAL")

    return option_titles


# ----------------------------
# Writers
# ----------------------------

def write_index(out_dir: Path, nodes_by_title: Dict[str, Node], title_by_repo_rel: Dict[str, str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    root_title = title_by_repo_rel.get("", "DIR_REPO_ROOT")

    index_md = [
        "---",
        "type: maze-index",
        "tags: [ovc, repo, maze, moc]",
        "---",
        "",
        "# OVC Repo Maze (Index)",
        "",
        "A link-web that Obsidian Graph View turns into a topology. Click rooms. Follow corridors. Laugh at Minotaurs.",
        "",
        "## Start",
        f"- [[{root_title}]]",
        "",
        "## Option Spine",
        "- [[OPT_A__CANONICAL_INGEST]] → [[OPT_D__PATHS_QA_BRIDGE]] → [[OPT_B__DERIVED_LAYERS]] → [[OPT_C__OUTCOMES_EVAL]]",
        "",
        "## High-signal Chambers (if they exist)",
    ]

    for rel in ["docs", "sql", "reports", "artifacts", ".github/workflows", "tools", "scripts", "src"]:
        t = title_by_repo_rel.get(rel)
        if t and t in nodes_by_title:
            index_md.append(f"- [[{t}]]  (`/{rel}`)")
        else:
            # pick representative if any startwith
            rep = None
            for n in nodes_by_title.values():
                if n.kind == "dir" and n.repo_rel and (n.repo_rel == rel or n.repo_rel.startswith(rel + "/")):
                    rep = n.title
                    break
            if rep:
                index_md.append(f"- [[{rep}]]  (`/{rel}`*)")

    index_md += [
        "",
        "## Notes",
        "- Dir nodes are prefixed `DIR_...`",
        "- File nodes are prefixed `FILE_...` (only if `--include-files`)",
        "- Option nodes are prefixed `OPT_...`",
        "",
    ]

    (out_dir / "00_REPO_MAZE.md").write_text("\n".join(index_md), encoding="utf-8")

def write_markdown_nodes(out_dir: Path, nodes_by_title: Dict[str, Node]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    for title, node in nodes_by_title.items():
        # we will write the index separately as 00_REPO_MAZE.md
        if title == "00_REPO_MAZE":
            continue

        filename = f"{title}.md"
        if len(filename) > 180:
            filename = filename[:180] + ".md"

        p = out_dir / filename

        tags = "tags: [ovc, maze, repo, graph]"
        if node.kind == "option":
            tags = "tags: [ovc, maze, repo, option]"

        fm = [
            "---",
            "type: maze-node",
            f"kind: {node.kind}",
            f"repo_rel: {node.repo_rel}",
            tags,
            "---",
            "",
        ]

        header = f"# {title}\n\n"

        body: List[str] = []
        if node.kind == "dir":
            rel_display = "/" + node.repo_rel if node.repo_rel else "/"
            body.append(f"**Directory:** `{rel_display}`\n")
            body.append("## Purpose\n")
            body.append("_What lives here? What invariants matter? What breaks when this breaks?_\n")
        elif node.kind == "file":
            body.append(f"**File:** `{node.repo_rel}`\n")
            body.append("## Role\n")
            body.append("_What does this file do in the system? Why does it exist?_\n")
        elif node.kind == "option":
            # option description hint (stored in title naming)
            body.append("## Summary\n")
            if title == "OPT_A__CANONICAL_INGEST":
                body.append("Canonical ingest: raw → canonical facts (C0/R + C1).")
            elif title == "OPT_B__DERIVED_LAYERS":
                body.append("Derived layers: compute C2/C3 features/registries/semantics.")
            elif title == "OPT_C__OUTCOMES_EVAL":
                body.append("Outcomes & evaluation: labels, eval reports, regressions.")
            elif title == "OPT_D__PATHS_QA_BRIDGE":
                body.append("Paths + QA bridge: Path1 evidence runner + Path2 determinism tightening (A↔D corridor).")
            body.append("")
            body.append("## What to lock here\n")
            body.append("- Contracts and boundaries (what belongs in this option)\n- Determinism rules (if applicable)\n- PASS/FAIL criteria\n")
        else:
            body.append("## Node\n")

        body.append("## Doors (Links)\n")
        if node.links:
            for t in sorted(node.links):
                body.append(f"- [[{t}]]")
        else:
            body.append("- _(none)_")

        p.write_text("\n".join(fm) + header + "\n".join(body) + "\n", encoding="utf-8")

def write_canvas(out_dir: Path, nodes_by_title: Dict[str, Node], title_by_repo_rel: Dict[str, str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    root_title = title_by_repo_rel.get("", "DIR_REPO_ROOT")

    featured = [
        root_title,
        "OPT_A__CANONICAL_INGEST",
        "OPT_D__PATHS_QA_BRIDGE",
        "OPT_B__DERIVED_LAYERS",
        "OPT_C__OUTCOMES_EVAL",
    ]
    featured = [t for t in featured if t in nodes_by_title]

    # add common chambers if present
    for rel in ["docs", "sql", "reports", "artifacts", ".github/workflows"]:
        t = title_by_repo_rel.get(rel)
        if t and t in nodes_by_title:
            featured.append(t)

    # add a handful of neighbors for context
    extras: Set[str] = set()
    for t in featured:
        for l in list(nodes_by_title[t].links)[:8]:
            extras.add(l)
    for t in sorted(extras):
        if t in nodes_by_title and t not in featured:
            featured.append(t)

    id_by_title = {t: f"n{i}" for i, t in enumerate(featured)}

    nodes = []
    edges = []

    def add_node(nid: str, text: str, x: int, y: int, w: int = 280, h: int = 160):
        nodes.append({"id": nid, "type": "text", "text": text, "x": x, "y": y, "width": w, "height": h})

    x0, y0 = -760, -220
    dx, dy = 320, 210

    # root
    if root_title in id_by_title:
        add_node(id_by_title[root_title], f"# Repo Root\n[[00_REPO_MAZE]]\n[[{root_title}]]", x0, y0, 300, 170)

    # option spine in a row
    spine = ["OPT_A__CANONICAL_INGEST", "OPT_D__PATHS_QA_BRIDGE", "OPT_B__DERIVED_LAYERS", "OPT_C__OUTCOMES_EVAL"]
    spine = [t for t in spine if t in id_by_title]
    for i, t in enumerate(spine):
        add_node(
            id_by_title[t],
            f"## {t}\n[[{t}]]",
            x0 + dx * (i + 1),
            y0,
            300 if "OPT_D" in t else 280,
            170,
        )

    # chambers beneath spine
    chamber_rels = ["docs", "sql", "reports", "artifacts", ".github/workflows"]
    chamber_titles = []
    for rel in chamber_rels:
        t = title_by_repo_rel.get(rel)
        if t and t in id_by_title:
            chamber_titles.append(t)

    for j, t in enumerate(chamber_titles):
        rel = nodes_by_title[t].repo_rel
        add_node(id_by_title[t], f"## /{rel}\n[[{t}]]", x0 + dx * (j + 1), y0 + dy, 280, 150)

    # edges among featured nodes
    edge_i = 0
    featured_set = set(featured)
    for t in featured:
        n = nodes_by_title[t]
        for l in n.links:
            if l not in featured_set:
                continue
            if t < l:  # de-dupe
                edges.append({
                    "id": f"e{edge_i}",
                    "fromNode": id_by_title[t],
                    "fromSide": "right",
                    "toNode": id_by_title[l],
                    "toSide": "left",
                })
                edge_i += 1

    canvas = {"nodes": nodes, "edges": edges}
    (out_dir / "OVC_REPO_MAZE.canvas").write_text(json.dumps(canvas, indent=2), encoding="utf-8")


# ----------------------------
# Main
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an Obsidian repo maze (Markdown + Canvas) from a repo tree.")
    ap.add_argument("--repo", type=str, required=True, help="Path to repo root (e.g. .)")
    ap.add_argument("--out", type=str, required=True, help="Output folder inside your Obsidian vault (will be created).")
    ap.add_argument("--include-files", action="store_true", help="Create nodes for selected files (workflows/sql/docs/etc).")
    ap.add_argument("--max-file-bytes", type=int, default=250_000, help="Max bytes to read per file for reference linking.")
    ap.add_argument("--ignore", type=str, default="", help="Comma-separated extra ignore dir names, e.g. 'data,tmp'")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    out_dir = Path(args.out).resolve()

    if not repo_root.exists() or not repo_root.is_dir():
        raise SystemExit(f"--repo is not a directory: {repo_root}")

    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    if args.ignore.strip():
        ignore_dirs |= {x.strip() for x in args.ignore.split(",") if x.strip()}

    nodes_by_title, title_by_repo_rel, file_relpaths = build_nodes(
        repo_root=repo_root,
        include_files=args.include_files,
        ignore_dirs=ignore_dirs,
        max_file_bytes=args.max_file_bytes,
    )

    # Add the special Option A/B/C/D nodes + wire them
    add_option_nodes(
        nodes_by_title=nodes_by_title,
        title_by_repo_rel=title_by_repo_rel,
        file_relpaths=file_relpaths,
        include_files=args.include_files,
    )

    # Write outputs
    write_index(out_dir, nodes_by_title, title_by_repo_rel)
    write_markdown_nodes(out_dir, nodes_by_title)
    write_canvas(out_dir, nodes_by_title, title_by_repo_rel)

    print("✅ Repo Maze generated (with Option A/B/C/D nodes)")
    print(f"   Output folder: {out_dir}")
    print(f"   Start here:    {out_dir / '00_REPO_MAZE.md'}")
    print(f"   Canvas:        {out_dir / 'OVC_REPO_MAZE.canvas'}")
    print()
    print("Obsidian:")
    print("- Open 00_REPO_MAZE.md")
    print("- Graph View will show the maze via backlinks")
    print("- Open OVC_REPO_MAZE.canvas for a draggable map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
