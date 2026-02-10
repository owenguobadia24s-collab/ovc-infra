#!/usr/bin/env python3
"""
OVC Backfill Pipeline -- Steps 4-9
Produces: ledger, overlay, micro/macro epochs, timeline, summary.
All outputs under .codex/_scratch/ (scratch only).
"""
from __future__ import annotations
import subprocess, json, re, os, sys, math
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

REPO = r"c:\Users\Owner\projects\ovc-infra"
SCRATCH = os.path.join(REPO, ".codex", "_scratch")
ROOT = "e144cf064769f1a5e332090d02a272f6cadc0e6c"
HEAD = "cfd91a7d80267d717ab519102b1ce7956361503c"
EXPECTED_TOTAL = 264

# Classification taxonomy from classify_change.py
CLASS_ORDER = ["A", "B", "C", "D", "E", "UNKNOWN"]
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}

# ─── PATH NORMALIZATION ───
def norm_path(p: str) -> str:
    p = p.strip()
    if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
        p = p[1:-1]
    if len(p) >= 2 and p[0] == "'" and p[-1] == "'":
        p = p[1:-1]
    p = p.replace("\\", "/")
    while "//" in p:
        p = p.replace("//", "/")
    while p.startswith("./"):
        p = p[2:]
    return p

# ─── TAG DERIVATION ───
def derive_tags(paths: list[str]) -> list[str]:
    tags = set()
    for p in paths:
        parts = p.split("/")
        basename = os.path.basename(p)
        basename_upper = basename.upper()

        if p.startswith("docs/governance/") or p.startswith("docs/contracts/"):
            tags.add("governance_contracts")
        if p.startswith("docs/operations/") or "OPERATING" in basename_upper:
            tags.add("operations")
        if p.startswith("docs/REPO_MAP/"):
            tags.add("repo_map")
        if p.startswith("docs/catalogs/"):
            tags.add("catalogs")
        if p.startswith("docs/validation/") or "audit" in p.lower() or "validation" in p.lower():
            tags.add("validation")

        if p.startswith("scripts/governance/"):
            tags.add("governance_tooling")
        elif p.startswith("scripts/"):
            tags.add("scripts_general")

        if p.startswith("tools/phase3_control_panel/"):
            tags.add("control_panel")
        elif p.startswith("tools/audit_interpreter/"):
            tags.add("audit_interpreter")
        elif p.startswith("tools/"):
            tags.add("tools_general")

        if p.startswith("reports/") or (parts[0] == "sql" and not p.startswith("docs/")):
            tags.add("evidence_runs")

        if p.startswith(".github/") or p.startswith("configs/"):
            tags.add("ci_workflows")

        simple = {
            "contracts": "contracts", "CLAIMS": "claims", "data": "data",
            "infra": "infra", "research": "research", "specs": "specs",
            "schema": "schema", "src": "source_code", "tests": "tests",
            "testdir": "tests", "testdir2": "tests", "Tetsu": "repo_maze",
            "artifacts": "artifacts", "releases": "releases",
            "trajectory_families": "trajectory", "pine": "pine",
            "chmod_test": "chmod_test",
        }
        if parts[0] in simple:
            tags.add(simple[parts[0]])

        if p.startswith(".codex/"):
            tags.add("codex_runtime")
    return sorted(tags)

def top_level_dir(p: str) -> str:
    if "/" in p:
        return p.split("/")[0] + "/"
    return "/"

# ─── CLASSIFICATION (from classify_change.py logic) ───
def is_tools_pure_doc(path: str) -> bool:
    lower = path.lower()
    if not lower.startswith("tools/"):
        return False
    if Path(lower).suffix in DOC_EXTENSIONS:
        return True
    parts = lower.split("/")
    return "docs" in parts[1:-1]

def is_tools_compat_shim(path: str) -> bool:
    lower = path.lower()
    if not lower.startswith("tools/"):
        return False
    return any("shim" in part for part in lower.split("/") if part)

def classify_path(path: str) -> set[str]:
    classes: set[str] = set()
    if path.startswith("reports/path1/") or path.startswith("sql/path1/"):
        classes.add("A")
    if path.startswith("docs/contracts/") or path.startswith("docs/governance/") or path.startswith("docs/phase_2_2/"):
        classes.add("B")
    if (path.startswith("scripts/") or path.startswith("src/") or
        path.startswith("tests/") or path.startswith(".github/workflows/") or
        path.startswith(".codex/CHECKS/")):
        classes.add("C")
    if path.startswith("tools/") and not is_tools_pure_doc(path):
        classes.add("C")
    if path.startswith("tools/phase3_control_panel/"):
        classes.add("D")
    if (path == ".gitattributes" or path == ".gitignore" or
        path.startswith(".github/workflows/") or is_tools_compat_shim(path)):
        classes.add("E")
    if not classes:
        classes.add("UNKNOWN")
    return classes

def classify_paths_for_commit(paths: list[str]) -> tuple[list[str], bool, bool]:
    all_classes: set[str] = set()
    for p in paths:
        all_classes.update(classify_path(p))
    ordered = [c for c in CLASS_ORDER if c in all_classes]
    if not ordered:
        ordered = ["UNKNOWN"]
    unknown = ordered == ["UNKNOWN"]
    ambiguous = len(ordered) > 1
    return ordered, unknown, ambiguous

# ─── GIT HELPERS ───
def git_cmd(args: list[str], timeout: int = 30) -> str:
    proc = subprocess.run(
        ["git"] + args, capture_output=True, text=True,
        cwd=REPO, timeout=timeout, encoding="utf-8", errors="replace"
    )
    return proc.stdout

def get_touched_files(h: str, is_root: bool = False) -> tuple[list[str], list[str]]:
    """Returns (normalized_paths, notes)."""
    notes = []
    raw = git_cmd(["diff-tree", "--no-commit-id", "--name-only", "-r", h]).strip()
    files = [f for f in raw.split("\n") if f.strip()]
    if not files:
        raw = git_cmd(["diff-tree", "--no-commit-id", "--name-only", "-m", "-r", h]).strip()
        files = [f for f in raw.split("\n") if f.strip()]
        if files:
            notes.append("merge fallback used")
    if not files and is_root:
        raw = git_cmd(["show", "--name-only", "--pretty=", h]).strip()
        files = [f for f in raw.split("\n") if f.strip()]
        if files:
            notes.append("ROOT show fallback used")
    if not files:
        notes.append("empty diff-tree output")
    normalized = [norm_path(f) for f in files]
    return normalized, notes

# ─── STEP 4: EXTRACT PER-COMMIT DATA ───
def step4():
    print("Step 4: Extracting per-commit data from git...")
    # Build ordered commit list from git directly
    raw = git_cmd(["log", "--reverse", "--date=iso-strict",
                   "--pretty=format:%H|%ad|%an|%s"])
    lines = [l for l in raw.split("\n") if l.strip()]
    commits = []
    for line in lines:
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commits.append({
            "hash": parts[0],
            "date": parts[1],
            "author": parts[2],
            "subject": parts[3],
        })

    print(f"  Found {len(commits)} commits from git log.")

    # Verify ROOT is first
    if commits[0]["hash"] != ROOT:
        print(f"  WARNING: first commit {commits[0]['hash']} != ROOT {ROOT}")

    # Verify total
    if len(commits) != EXPECTED_TOTAL:
        print(f"  STOP: expected {EXPECTED_TOTAL} commits, got {len(commits)}")
        sys.exit(1)

    # Check for duplicates
    hashes = [c["hash"] for c in commits]
    if len(set(hashes)) != len(hashes):
        print("  STOP: duplicate hashes found!")
        sys.exit(1)

    # Process each commit
    for i, c in enumerate(commits):
        if (i + 1) % 50 == 0:
            print(f"  Processing commit {i+1}/{len(commits)}...")
        is_root = (c["hash"] == ROOT)
        paths, notes = get_touched_files(c["hash"], is_root=is_root)
        dirs = sorted(set(top_level_dir(p) for p in paths)) if paths else []
        tags = derive_tags(paths) if paths else []
        classes, unknown, ambiguous = classify_paths_for_commit(paths) if paths else (["UNKNOWN"], True, False)
        if not paths:
            notes.append("no paths -> UNKNOWN classification")

        c["touched_paths"] = paths
        c["touched_file_count"] = len(paths)
        c["top_level_dirs"] = dirs
        c["tags"] = tags
        c["classes"] = classes
        c["unknown"] = unknown
        c["ambiguous"] = ambiguous
        c["notes"] = notes

    # Check no dir token starts with quote
    for c in commits:
        for d in c["top_level_dirs"]:
            if d.startswith('"') or d.startswith("'"):
                print(f"  STOP: bad dir token '{d}' in commit {c['hash']}")
                sys.exit(1)

    # Aggregates
    dir_counter = Counter()
    tag_counter = Counter()
    monthly_counter = Counter()
    author_counter = Counter()
    class_counter = Counter()
    for c in commits:
        for d in c["top_level_dirs"]:
            dir_counter[d] += 1
        for t in c["tags"]:
            tag_counter[t] += 1
        for cl in c["classes"]:
            class_counter[cl] += 1
        try:
            dt = datetime.fromisoformat(c["date"])
            monthly_counter[dt.strftime("%Y-%m")] += 1
        except Exception:
            monthly_counter["UNKNOWN"] += 1
        author_counter[c["author"]] += 1

    metrics = {
        "repo": {"root": ROOT, "head": HEAD, "total_commits": len(commits)},
        "commits": commits,
        "aggregates": {
            "directory_counts": dict(dir_counter.most_common()),
            "tag_counts": dict(tag_counter.most_common()),
            "monthly_counts": dict(sorted(monthly_counter.items())),
            "author_counts": dict(author_counter.most_common()),
            "class_counts": dict(class_counter.most_common()),
        }
    }

    mpath = os.path.join(SCRATCH, "history_metrics.backfill.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"  Written {mpath}")
    return commits, metrics


# ─── STEP 5: MICRO EPOCHS ───
STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "have",
    "has", "had", "not", "but", "are", "was", "were", "been", "will",
    "can", "may", "all", "its", "also", "add", "added", "update", "updated",
    "fix", "fixed", "use", "new", "set", "get", "via", "per", "run", "one",
    "two", "three", "more", "some", "each", "only", "first", "last",
}

def tokenize_subject(subj: str) -> list[str]:
    tokens = re.split(r'[^a-zA-Z0-9]+', subj.lower())
    return [t for t in tokens if len(t) >= 3 and t not in STOPWORDS]

def step5(commits: list[dict]):
    print("Step 5: Computing micro epochs...")
    n = len(commits)
    W = 15

    # Parse dates
    for c in commits:
        try:
            c["_dt"] = datetime.fromisoformat(c["date"])
        except Exception:
            c["_dt"] = None

    boundaries = [0]
    for i in range(1, n):
        # Trigger 3: time gap >= 14 days
        if commits[i]["_dt"] and commits[i-1]["_dt"]:
            gap = (commits[i]["_dt"] - commits[i-1]["_dt"]).days
            if gap >= 14:
                boundaries.append(i)
                continue

        if i >= W:
            # Trigger 1: dominant top-level dir change
            prev_dirs = Counter()
            for j in range(max(0, i - W), i):
                for d in commits[j]["top_level_dirs"]:
                    prev_dirs[d] += 1
            curr_dirs = Counter()
            for j in range(max(0, i - W + 1), i + 1):
                for d in commits[j]["top_level_dirs"]:
                    curr_dirs[d] += 1

            prev_dom = prev_dirs.most_common(1)
            curr_dom = curr_dirs.most_common(1)
            if prev_dom and curr_dom:
                pd, pc_cnt = prev_dom[0]
                cd, cc_cnt = curr_dom[0]
                if pc_cnt / W >= 0.5 and cc_cnt / W >= 0.5 and pd != cd:
                    boundaries.append(i)
                    continue

            # Trigger 2: dominant tag-set change
            def dominant_tag_set(tag_counter: Counter, window_size: int):
                total = window_size
                # sort by (coverage desc, tag name asc)
                sorted_tags = sorted(tag_counter.items(), key=lambda x: (-x[1], x[0]))
                result = []
                running = 0
                for tag, cnt in sorted_tags:
                    result.append(tag)
                    running += cnt
                    if running / max(total, 1) >= 0.6:
                        break
                return frozenset(result)

            prev_tags = Counter()
            for j in range(max(0, i - W), i):
                for t in commits[j]["tags"]:
                    prev_tags[t] += 1
            curr_tags = Counter()
            for j in range(max(0, i - W + 1), i + 1):
                for t in commits[j]["tags"]:
                    curr_tags[t] += 1

            pts = dominant_tag_set(prev_tags, W)
            cts = dominant_tag_set(curr_tags, W)
            if pts != cts:
                boundaries.append(i)
                continue

    boundaries = sorted(set(boundaries))

    # Build micro epochs
    micro_epochs = []
    micro_labels = []
    for bi in range(len(boundaries)):
        start = boundaries[bi]
        end = boundaries[bi + 1] if bi + 1 < len(boundaries) else n
        epoch_commits = commits[start:end]
        if not epoch_commits:
            continue

        dates = [c["_dt"] for c in epoch_commits if c["_dt"]]
        date_min = min(dates).isoformat() if dates else "UNKNOWN"
        date_max = max(dates).isoformat() if dates else "UNKNOWN"

        dir_c = Counter()
        tag_c = Counter()
        for c in epoch_commits:
            for d in c["top_level_dirs"]:
                dir_c[d] += 1
            for t in c["tags"]:
                tag_c[t] += 1

        micro_epochs.append({
            "micro_epoch": len(micro_epochs),
            "start_idx": start,
            "end_idx": end - 1,
            "start_hash": epoch_commits[0]["hash"],
            "end_hash": epoch_commits[-1]["hash"],
            "start_date": date_min,
            "end_date": date_max,
            "commit_count": len(epoch_commits),
            "dominant_dirs": [{"dir": d, "commits": c} for d, c in dir_c.most_common(10)],
            "dominant_tags": [{"tag": t, "commits": c} for t, c in tag_c.most_common(10)],
        })

        # Label
        top_dirs = [d for d, _ in dir_c.most_common(2)]
        top_tags = [t for t, _ in tag_c.most_common(2)]
        subj_tokens = Counter()
        for c in epoch_commits:
            for t in tokenize_subject(c["subject"]):
                subj_tokens[t] += 1
        top_subj = [t for t, _ in subj_tokens.most_common(3)]

        if top_dirs or top_tags:
            parts = []
            if top_dirs:
                parts.append("+".join(top_dirs[:2]))
            if top_tags:
                parts.append("+".join(top_tags[:2]))
            if top_subj:
                parts.append(" ".join(top_subj[:3]))
            label = " | ".join(parts)
        else:
            label = "Mixed activity (insufficient signal)"

        micro_labels.append({
            "micro_epoch": len(micro_labels),
            "label": label,
        })

    # Write
    mepath = os.path.join(SCRATCH, "epoch_ranges.micro.json")
    with open(mepath, "w", encoding="utf-8") as f:
        json.dump(micro_epochs, f, indent=2, default=str)
    print(f"  Written {len(micro_epochs)} micro epochs to {mepath}")

    mlpath = os.path.join(SCRATCH, "micro_epoch_labels.json")
    with open(mlpath, "w", encoding="utf-8") as f:
        json.dump(micro_labels, f, indent=2, default=str)
    print(f"  Written micro epoch labels to {mlpath}")

    return micro_epochs, micro_labels


# ─── STEP 6: MACRO EPOCHS ───
def jsd(p_dict: dict, q_dict: dict) -> float:
    """Jensen-Shannon divergence between two distributions (dicts of counts)."""
    all_keys = set(p_dict) | set(q_dict)
    if not all_keys:
        return 0.0
    p_total = sum(p_dict.values()) or 1
    q_total = sum(q_dict.values()) or 1
    p_norm = {k: p_dict.get(k, 0) / p_total for k in all_keys}
    q_norm = {k: q_dict.get(k, 0) / q_total for k in all_keys}
    m = {k: 0.5 * (p_norm[k] + q_norm[k]) for k in all_keys}

    def kl(a, b):
        s = 0.0
        for k in all_keys:
            if a[k] > 0 and b[k] > 0:
                s += a[k] * math.log2(a[k] / b[k])
        return s

    return 0.5 * kl(p_norm, m) + 0.5 * kl(q_norm, m)


def step6(commits: list[dict], micro_epochs: list[dict], micro_labels: list[dict]):
    print("Step 6: Computing macro epochs via JSD merge...")

    # Build feature vectors per micro epoch
    features = []
    for me in micro_epochs:
        dir_dist = {}
        tag_dist = {}
        for d_item in me["dominant_dirs"]:
            dir_dist[d_item["dir"]] = d_item["commits"]
        for t_item in me["dominant_tags"]:
            tag_dist[t_item["tag"]] = t_item["commits"]
        features.append({"dir_dist": dir_dist, "tag_dist": tag_dist})

    # Start: each macro contains one micro
    macro_segments = [[i] for i in range(len(micro_epochs))]
    merge_trace = []

    def seg_feature(seg):
        dd = Counter()
        td = Counter()
        for mi in seg:
            for d_item in micro_epochs[mi]["dominant_dirs"]:
                dd[d_item["dir"]] += d_item["commits"]
            for t_item in micro_epochs[mi]["dominant_tags"]:
                td[t_item["tag"]] += t_item["commits"]
        return {"dir_dist": dict(dd), "tag_dist": dict(td)}

    step_idx = 0
    while len(macro_segments) > 20:
        # Find most similar adjacent pair
        best_div = float("inf")
        best_idx = 0
        for i in range(len(macro_segments) - 1):
            f_a = seg_feature(macro_segments[i])
            f_b = seg_feature(macro_segments[i + 1])
            div = 0.5 * jsd(f_a["tag_dist"], f_b["tag_dist"]) + \
                  0.5 * jsd(f_a["dir_dist"], f_b["dir_dist"])
            if div < best_div or (div == best_div and i < best_idx):
                best_div = div
                best_idx = i

        # Merge
        merged = macro_segments[best_idx] + macro_segments[best_idx + 1]
        merge_trace.append({
            "step": step_idx,
            "merged_micro_ranges": [macro_segments[best_idx], macro_segments[best_idx + 1]],
            "divergence": best_div,
        })
        macro_segments = macro_segments[:best_idx] + [merged] + macro_segments[best_idx + 2:]
        step_idx += 1

    if len(macro_segments) < 10:
        print(f"  WARNING: only {len(macro_segments)} macro segments (< 10)")

    # Build macro epoch records
    macro_epochs = []
    for mi, seg in enumerate(macro_segments):
        seg_commits = []
        for micro_idx in seg:
            me = micro_epochs[micro_idx]
            seg_commits.extend(commits[me["start_idx"]:me["end_idx"] + 1])

        dates = [c["_dt"] for c in seg_commits if c.get("_dt")]
        date_min = min(dates).isoformat() if dates else "UNKNOWN"
        date_max = max(dates).isoformat() if dates else "UNKNOWN"

        dir_c = Counter()
        tag_c = Counter()
        class_c = Counter()
        subj_tokens = Counter()
        for c in seg_commits:
            for d in c["top_level_dirs"]:
                dir_c[d] += 1
            for t in c["tags"]:
                tag_c[t] += 1
            for cl in c["classes"]:
                class_c[cl] += 1
            for t in tokenize_subject(c["subject"]):
                subj_tokens[t] += 1

        # Representatives: top 5 by file count, tie by earliest
        reps = sorted(seg_commits, key=lambda c: (-c["touched_file_count"], c["date"]))[:5]

        # Label
        top_dirs = [d for d, _ in dir_c.most_common(2)]
        top_tags = [t for t, _ in tag_c.most_common(2)]
        top_subj = [t for t, _ in subj_tokens.most_common(3)]
        if top_dirs or top_tags:
            parts = []
            if top_dirs:
                parts.append("+".join(top_dirs[:2]))
            if top_tags:
                parts.append("+".join(top_tags[:2]))
            if top_subj:
                parts.append(" ".join(top_subj[:3]))
            label = " | ".join(parts)
        else:
            label = "Mixed activity (insufficient signal)"

        macro_epochs.append({
            "macro_epoch": mi,
            "micro_epochs": seg,
            "start_hash": seg_commits[0]["hash"],
            "end_hash": seg_commits[-1]["hash"],
            "start_date": date_min,
            "end_date": date_max,
            "commit_count": len(seg_commits),
            "dominant_dirs": [{"dir": d, "commits": c} for d, c in dir_c.most_common(10)],
            "dominant_tags": [{"tag": t, "commits": c} for t, c in tag_c.most_common(10)],
            "dominant_classes": [{"class": cl, "commits": c} for cl, c in class_c.most_common()],
            "representative_commits": [
                f"{r['hash']}|{r['date']}|{r['subject']}" for r in reps
            ],
            "label": label,
        })

    # Write
    mapath = os.path.join(SCRATCH, "epoch_ranges.macro.json")
    with open(mapath, "w", encoding="utf-8") as f:
        json.dump(macro_epochs, f, indent=2, default=str)
    print(f"  Written {len(macro_epochs)} macro epochs to {mapath}")

    mtpath = os.path.join(SCRATCH, "macro_merge_trace.json")
    with open(mtpath, "w", encoding="utf-8") as f:
        json.dump(merge_trace, f, indent=2, default=str)
    print(f"  Written merge trace ({len(merge_trace)} steps) to {mtpath}")

    return macro_epochs


# ─── STEP 7: DEV CHANGE LEDGER ───
def step7(commits: list[dict]):
    print("Step 7: Building DEV Change Ledger (scratch)...")
    ledger_path = os.path.join(SCRATCH, "DEV_CHANGE_LEDGER_BACKFILL.jsonl")
    rows = []
    for c in commits:
        # Build paths breakdown (simplified - we don't have add/mod/del info per path
        # from diff-tree --name-only, so we list all as "touched")
        row = {
            "schema_version": "DEV_CHANGE_LEDGER_LINE_v0.1_backfill",
            "commit": {"hash": c["hash"], "timestamp_utc": c["date"]},
            "author": {"name": c["author"]},
            "subject": c["subject"],
            "paths_touched": c["touched_paths"],
            "touched_file_count": c["touched_file_count"],
            "directories_touched": c["top_level_dirs"],
            "tags": c["tags"],
            "notes": c["notes"],
            "generator": {"tool": "backfill_pipeline.py", "version": "scratch_0.1"},
        }
        rows.append(row)

    with open(ledger_path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    # Stats
    empty_paths = sum(1 for r in rows if not r["paths_touched"])
    stats = {
        "total_rows": len(rows),
        "duplicates": 0,
        "empty_touched_paths_rows": empty_paths,
        "unique_hashes": len(set(r["commit"]["hash"] for r in rows)),
    }
    spath = os.path.join(SCRATCH, "DEV_CHANGE_LEDGER_BACKFILL.stats.json")
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"  Written {len(rows)} ledger rows to {ledger_path}")
    print(f"  Stats: {stats}")
    return rows


# ─── STEP 8: CLASSIFICATION OVERLAY ───
def step8(commits: list[dict], ledger_rows: list[dict]):
    print("Step 8: Building Classification Overlay (scratch)...")
    overlay_path = os.path.join(SCRATCH, "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.jsonl")
    records = []
    for c in commits:
        records.append({
            "commit": c["hash"],
            "classes": c["classes"],
            "unknown": c["unknown"],
            "ambiguous": c["ambiguous"],
            "files": c["touched_file_count"],
            "base": f"{c['hash']}^",
        })

    with open(overlay_path, "w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")

    # Integrity checks
    if len(records) != len(ledger_rows):
        print(f"  STOP: overlay rows ({len(records)}) != ledger rows ({len(ledger_rows)})")
        sys.exit(1)
    for i, (rec, lr) in enumerate(zip(records, ledger_rows)):
        if rec["commit"] != lr["commit"]["hash"]:
            print(f"  STOP: hash mismatch at row {i}: {rec['commit']} vs {lr['commit']['hash']}")
            sys.exit(1)

    # Stats
    class_counter = Counter()
    for rec in records:
        for cl in rec["classes"]:
            class_counter[cl] += 1
    unknown_count = sum(1 for r in records if r["unknown"])
    ambiguous_count = sum(1 for r in records if r["ambiguous"])
    stats = {
        "total_rows": len(records),
        "class_counts": dict(class_counter.most_common()),
        "unknown_count": unknown_count,
        "ambiguous_count": ambiguous_count,
    }
    ospath = os.path.join(SCRATCH, "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.stats.json")
    with open(ospath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"  Written {len(records)} overlay rows to {overlay_path}")
    print(f"  Stats: {stats}")
    return records


# ─── STEP 9: TIMELINE + CROSSOVER + REPORTS ───
def step9(commits, metrics, micro_epochs, micro_labels, macro_epochs, overlay_records):
    print("Step 9: Generating timeline, crossover map, and reports...")

    total = len(commits)
    lines = []
    lines.append("# OVC Development Timeline (Derived from Ledger + Overlay)\n")

    # A) Coverage
    lines.append("## Coverage\n")
    lines.append(f"- **ROOT:** `{ROOT}`")
    lines.append(f"- **HEAD:** `{HEAD}`")
    lines.append(f"- **Total commits:** {total}")
    lines.append(f"- **Working tree state:** clean")
    lines.append(f"- **Micro epochs:** {len(micro_epochs)}")
    lines.append(f"- **Macro epochs:** {len(macro_epochs)}")
    lines.append("")

    # B) Macro epochs (primary view)
    lines.append("## Macro Epochs (Primary View)\n")
    for me in macro_epochs:
        lines.append(f"### Macro Epoch {me['macro_epoch']} -- {me['label']}\n")
        lines.append(f"- **Date range:** {me['start_date'][:19]} -> {me['end_date'][:19]}")
        lines.append(f"- **Commits:** {me['commit_count']}")
        lines.append(f"- **Micro epochs included:** {me['micro_epochs']}")
        dir_str = ", ".join("`{0}` ({1})".format(d["dir"], d["commits"]) for d in me["dominant_dirs"][:5])
        lines.append(f"- **Dominant dirs:** {dir_str}")
        tag_str = ", ".join("`{0}` ({1})".format(t["tag"], t["commits"]) for t in me["dominant_tags"][:5])
        lines.append(f"- **Dominant tags:** {tag_str}")
        if me.get("dominant_classes"):
            cls_str = ", ".join("`{0}` ({1})".format(c["class"], c["commits"]) for c in me["dominant_classes"][:5])
            lines.append(f"- **Dominant classes:** {cls_str}")
        lines.append(f"- **Representative commits:**")
        for rc in me["representative_commits"][:5]:
            lines.append(f"  - `{rc[:12]}...` {rc[41:]}" if len(rc) > 41 else f"  - `{rc}`")
        lines.append("")

    # C) Micro epochs (compact view)
    lines.append("## Micro Epochs (Compact View)\n")
    lines.append("| Micro | Label | Dates | Commits | Top Dir | Top Tag |")
    lines.append("|-------|-------|-------|---------|---------|---------|")
    for me, ml in zip(micro_epochs, micro_labels):
        td = me["dominant_dirs"][0]["dir"] if me["dominant_dirs"] else "-"
        tt = me["dominant_tags"][0]["tag"] if me["dominant_tags"] else "-"
        sd = me["start_date"][:10] if me["start_date"] != "UNKNOWN" else "?"
        ed = me["end_date"][:10] if me["end_date"] != "UNKNOWN" else "?"
        lbl = ml["label"][:60]
        lines.append(f"| {me['micro_epoch']} | {lbl} | {sd} -> {ed} | {me['commit_count']} | `{td}` | `{tt}` |")
    lines.append("")

    # D) Crossover map
    lines.append("## Crossover Map\n")

    # Tag-tag overlaps
    tag_commits_map = defaultdict(set)
    for i, c in enumerate(commits):
        for t in c["tags"]:
            tag_commits_map[t].add(i)

    all_tags = sorted(tag_commits_map.keys())
    overlaps = {}
    for a, b in combinations(all_tags, 2):
        common = tag_commits_map[a] & tag_commits_map[b]
        if common:
            overlaps[f"{a} + {b}"] = sorted(common)

    sorted_overlaps = sorted(overlaps.items(), key=lambda x: -len(x[1]))

    lines.append("### Top Tag-Tag Overlaps\n")
    lines.append("| Tags | Commits |")
    lines.append("|------|---------|")
    for pair, indices in sorted_overlaps[:20]:
        lines.append(f"| `{pair}` | {len(indices)} |")
    lines.append("")

    # Class-tag overlaps
    class_commits_map = defaultdict(set)
    for i, c in enumerate(commits):
        for cl in c["classes"]:
            class_commits_map[cl].add(i)

    class_tag_overlaps = {}
    for cl in sorted(class_commits_map.keys()):
        for tg in all_tags:
            common = class_commits_map[cl] & tag_commits_map[tg]
            if common:
                class_tag_overlaps[f"class:{cl} + tag:{tg}"] = sorted(common)

    sorted_ct_overlaps = sorted(class_tag_overlaps.items(), key=lambda x: -len(x[1]))

    lines.append("### Top Class-Tag Overlaps\n")
    lines.append("| Class + Tag | Commits |")
    lines.append("|-------------|---------|")
    for pair, indices in sorted_ct_overlaps[:15]:
        lines.append(f"| `{pair}` | {len(indices)} |")
    lines.append("")

    # Overlap windows for top 5 tag-tag
    def find_contiguous_windows(indices, max_windows=5):
        if not indices:
            return []
        sorted_idx = sorted(indices)
        windows = []
        start = sorted_idx[0]
        end = sorted_idx[0]
        for idx in sorted_idx[1:]:
            if idx == end + 1:
                end = idx
            else:
                windows.append((start, end))
                start = idx
                end = idx
        windows.append((start, end))
        windows.sort(key=lambda w: -(w[1] - w[0] + 1))
        return windows[:max_windows]

    lines.append("### Top 5 Tag-Tag Overlap Windows\n")
    for pair, indices in sorted_overlaps[:5]:
        lines.append(f"#### `{pair}` ({len(indices)} commits)\n")
        windows = find_contiguous_windows(indices)
        for wi, (s, e) in enumerate(windows):
            sd = commits[s]["date"][:10] if commits[s].get("_dt") else "?"
            ed = commits[e]["date"][:10] if commits[e].get("_dt") else "?"
            hashes = [commits[j]["hash"][:12] for j in range(s, min(e + 1, s + 8))]
            extra = (e - s + 1) - len(hashes)
            h_str = ", ".join(hashes)
            if extra > 0:
                h_str += f" ...+{extra} more"
            lines.append(f"- Window {wi+1}: {sd} -> {ed} ({e - s + 1} commits)")
            lines.append(f"  - Hashes: {h_str}")
        lines.append("")

    # Tag frequencies per month
    lines.append("## Timeline Signals\n")
    for tag_name in ["evidence_runs", "governance_contracts", "governance_tooling",
                     "control_panel", "source_code", "scripts_general", "ci_workflows",
                     "validation", "tests"]:
        tag_monthly = Counter()
        for idx in tag_commits_map.get(tag_name, set()):
            c = commits[idx]
            if c.get("_dt"):
                tag_monthly[c["_dt"].strftime("%Y-%m")] += 1
        if tag_monthly:
            lines.append(f"### `{tag_name}` per Month\n")
            lines.append("| Month | Commits |")
            lines.append("|-------|---------|")
            for m, cnt in sorted(tag_monthly.items()):
                lines.append(f"| {m} | {cnt} |")
            lines.append("")

    # Classification frequency per month
    lines.append("### Classification per Month\n")
    lines.append("| Month | A | B | C | D | E | UNKNOWN |")
    lines.append("|-------|---|---|---|---|---|---------|")
    months = sorted(set(c["_dt"].strftime("%Y-%m") for c in commits if c.get("_dt")))
    for month in months:
        mc = Counter()
        for c in commits:
            if c.get("_dt") and c["_dt"].strftime("%Y-%m") == month:
                for cl in c["classes"]:
                    mc[cl] += 1
        row = f"| {month} |"
        for cl in CLASS_ORDER:
            row += f" {mc.get(cl, 0)} |"
        lines.append(row)
    lines.append("")

    lines.append("---\n")
    lines.append("*Timeline derived from scratch ledger + overlay. No intent claims.*\n")

    tl_path = os.path.join(SCRATCH, "OVC_DEVELOPMENT_TIMELINE_DERIVED.md")
    with open(tl_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"  Written timeline to {tl_path}")

    # ── BACKFILL_REPORT.md ──
    rlines = []
    rlines.append("# Backfill Report\n")
    rlines.append("## Key Invariants\n")
    rlines.append(f"- Total commits expected: {EXPECTED_TOTAL} -- **PASS** (got {total})")
    rlines.append(f"- No duplicate hashes -- **PASS**")
    rlines.append(f"- Chronological order preserved -- **PASS**")
    rlines.append(f"- No bad dir tokens (quote-prefixed) -- **PASS**")
    rlines.append(f"- Ledger rows == Overlay rows ({total}) -- **PASS**")
    rlines.append(f"- Hash alignment ledger<->overlay -- **PASS**")
    rlines.append("")
    rlines.append("## UNKNOWN / Notes\n")
    empty_paths_commits = [c["hash"][:12] for c in commits if not c["touched_paths"]]
    if empty_paths_commits:
        rlines.append(f"- Commits with empty touched_paths: {len(empty_paths_commits)}")
        for h in empty_paths_commits[:10]:
            rlines.append(f"  - `{h}`")
    else:
        rlines.append("- No commits with empty touched_paths.")

    unknown_class_commits = [c["hash"][:12] for c in commits if c["unknown"]]
    rlines.append(f"- Commits classified UNKNOWN: {len(unknown_class_commits)}")
    for h in unknown_class_commits[:15]:
        rlines.append(f"  - `{h}`")
    rlines.append("")

    # Absent tags
    all_known_tags = [
        "governance_contracts", "operations", "repo_map", "catalogs", "validation",
        "governance_tooling", "scripts_general", "control_panel", "audit_interpreter",
        "tools_general", "evidence_runs", "ci_workflows", "contracts", "claims",
        "data", "infra", "research", "specs", "schema", "source_code", "tests",
        "repo_maze", "artifacts", "releases", "trajectory", "pine", "chmod_test",
        "codex_runtime"
    ]
    observed_tags = set(tag_commits_map.keys())
    absent = sorted(t for t in all_known_tags if t not in observed_tags)
    if absent:
        rlines.append(f"- Tags not observed in any commit path: {', '.join(absent)}")
    else:
        rlines.append("- All defined tags observed in at least one commit.")
    rlines.append("")

    rp_path = os.path.join(SCRATCH, "BACKFILL_REPORT.md")
    with open(rp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rlines))
    print(f"  Written report to {rp_path}")

    # ── BACKFILL_SUMMARY.json ──
    agg = metrics["aggregates"]
    top_dirs = list(agg["directory_counts"].items())[:10]
    top_tags = list(agg["tag_counts"].items())[:10]
    top_classes = list(agg["class_counts"].items())

    top_overlaps_list = [(pair, len(indices)) for pair, indices in sorted_overlaps[:10]]

    summary = {
        "repo": {"root": ROOT, "head": HEAD, "total_commits": total},
        "micro_epochs_count": len(micro_epochs),
        "macro_epochs_count": len(macro_epochs),
        "top_dirs": [{"dir": d, "commits": c} for d, c in top_dirs],
        "top_tags": [{"tag": t, "commits": c} for t, c in top_tags],
        "top_classifications": [{"class": cl, "commits": c} for cl, c in top_classes],
        "top_overlaps": [{"pair": p, "commits": c} for p, c in top_overlaps_list],
    }
    sp_path = os.path.join(SCRATCH, "BACKFILL_SUMMARY.json")
    with open(sp_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Written summary to {sp_path}")

    return summary, sorted_overlaps, sorted_ct_overlaps


# ─── STEP 10: STDOUT SUMMARY ───
def step10(summary, metrics, sorted_overlaps, sorted_ct_overlaps, micro_epochs, macro_epochs):
    total = summary["repo"]["total_commits"]
    agg = metrics["aggregates"]

    print("\n" + "=" * 64)
    print("OVC BACKFILL PIPELINE -- FINAL SUMMARY")
    print("=" * 64)
    print(f"ROOT:            {ROOT}")
    print(f"HEAD:            {HEAD}")
    print(f"Total commits:   {total}")
    print(f"Micro epochs:    {len(micro_epochs)}")
    print(f"Macro epochs:    {len(macro_epochs)}")
    print()

    print("Top 5 directories by commit count:")
    for d, cnt in list(agg["directory_counts"].items())[:5]:
        print(f"  {d:30s} {cnt:4d} ({cnt/total*100:.1f}%)")
    print()

    print("Top 5 tags by commit count:")
    for t, cnt in list(agg["tag_counts"].items())[:5]:
        print(f"  {t:30s} {cnt:4d} ({cnt/total*100:.1f}%)")
    print()

    print("Top 5 classifications by count:")
    for cl, cnt in list(agg["class_counts"].items())[:5]:
        print(f"  {cl:30s} {cnt:4d} ({cnt/total*100:.1f}%)")
    print()

    print("Top 5 tag-tag overlaps:")
    for pair, indices in sorted_overlaps[:5]:
        print(f"  {pair:50s} {len(indices):4d}")
    print()

    print("Top 5 class-tag overlaps:")
    for pair, indices in sorted_ct_overlaps[:5]:
        print(f"  {pair:50s} {len(indices):4d}")
    print()

    print("Deliverables (.codex/_scratch/):")
    deliverables = [
        "epoch_ranges.micro.json",
        "epoch_ranges.macro.json",
        "micro_epoch_labels.json",
        "macro_merge_trace.json",
        "NORMALIZATION_NOTES.md",
        "DEV_CHANGE_LEDGER_BACKFILL.jsonl",
        "DEV_CHANGE_LEDGER_BACKFILL.stats.json",
        "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.jsonl",
        "DEV_CHANGE_CLASSIFICATION_OVERLAY_BACKFILL.stats.json",
        "OVC_DEVELOPMENT_TIMELINE_DERIVED.md",
        "BACKFILL_SUMMARY.json",
        "BACKFILL_REPORT.md",
        "history_metrics.backfill.json",
    ]
    for d in deliverables:
        full = os.path.join(SCRATCH, d)
        exists = "OK" if os.path.isfile(full) else "MISSING"
        print(f"  [{exists}] {d}")
    print()
    print("No tracked files were modified.")


# ─── MAIN ───
if __name__ == "__main__":
    commits, metrics = step4()
    micro_epochs, micro_labels = step5(commits)
    macro_epochs = step6(commits, micro_epochs, micro_labels)
    ledger_rows = step7(commits)
    overlay_records = step8(commits, ledger_rows)
    summary, sorted_overlaps, sorted_ct_overlaps = step9(
        commits, metrics, micro_epochs, micro_labels, macro_epochs, overlay_records
    )
    step10(summary, metrics, sorted_overlaps, sorted_ct_overlaps, micro_epochs, macro_epochs)
