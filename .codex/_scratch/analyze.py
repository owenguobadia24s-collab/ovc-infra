#!/usr/bin/env python3
"""
OVC Repo History Analysis — Steps 2-5
Reads git history and produces metrics JSON + human report.
"""

import subprocess
import json
import re
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import combinations

REPO = r"c:\Users\Owner\projects\ovc-infra"
SCRATCH = os.path.join(REPO, ".codex", "_scratch")
SPINE = os.path.join(SCRATCH, "history_spine.txt")

ROOT = "e144cf064769f1a5e332090d02a272f6cadc0e6c"
HEAD = "cfd91a7d80267d717ab519102b1ce7956361503c"

# ── Tag mappings ──
def derive_tags(paths):
    tags = set()
    for p in paths:
        pl = p.replace("\\", "/")
        parts = pl.split("/")

        # docs subtrees
        if pl.startswith("docs/governance/") or pl.startswith("docs/contracts/"):
            tags.add("governance_contracts")
        elif pl.startswith("docs/operations/") or "OPERATING" in os.path.basename(pl).upper():
            tags.add("operations")
        elif pl.startswith("docs/REPO_MAP/"):
            tags.add("repo_map")
        elif pl.startswith("docs/catalogs/"):
            tags.add("catalogs")
        elif pl.startswith("docs/validation/") or "audit" in pl.lower() or "validation" in pl.lower():
            tags.add("validation")

        # scripts
        if pl.startswith("scripts/governance/"):
            tags.add("governance_tooling")
        elif pl.startswith("scripts/") and not pl.startswith("scripts/governance/"):
            tags.add("scripts_general")

        # tools
        if pl.startswith("tools/phase3_control_panel/"):
            tags.add("control_panel")
        elif pl.startswith("tools/audit_interpreter/"):
            tags.add("audit_interpreter")
        elif pl.startswith("tools/") and not pl.startswith("tools/phase3_control_panel/") and not pl.startswith("tools/audit_interpreter/"):
            tags.add("tools_general")

        # reports / sql
        if pl.startswith("reports/"):
            tags.add("evidence_runs")
        if parts[0] == "sql":
            tags.add("evidence_runs")

        # ci/workflows
        if pl.startswith(".github/") or pl.startswith("configs/"):
            tags.add("ci_workflows")

        # top-level named dirs
        mapping_simple = {
            "contracts": "contracts",
            "CLAIMS": "claims",
            "data": "data",
            "infra": "infra",
            "research": "research",
            "specs": "specs",
            "schema": "schema",
            "src": "source_code",
            "tests": "tests",
            "testdir": "tests",
            "testdir2": "tests",
            "Tetsu": "repo_maze",
            "artifacts": "artifacts",
            "releases": "releases",
            "trajectory_families": "trajectory",
            "pine": "pine",
            "chmod_test": "chmod_test",
        }
        if parts[0] in mapping_simple:
            tags.add(mapping_simple[parts[0]])

        if pl.startswith(".codex/"):
            tags.add("codex_runtime")

        # Also catch "OPERATING" in basename anywhere
        if "OPERATING" in os.path.basename(pl).upper():
            tags.add("operations")

    return sorted(tags)


def top_level_dir(path):
    p = path.replace("\\", "/")
    if "/" in p:
        return p.split("/")[0] + "/"
    return "/"


def get_touched_files(commit_hash):
    """Get files touched by a commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            capture_output=True, text=True, cwd=REPO, timeout=30
        )
        files = [f for f in result.stdout.strip().split("\n") if f]
        if not files:
            # merge fallback
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-m", "-r", commit_hash],
                capture_output=True, text=True, cwd=REPO, timeout=30
            )
            files = [f for f in result.stdout.strip().split("\n") if f]
        return files
    except Exception:
        return []


# ── STEP 2: Build per-commit data ──
def step2():
    print("Step 2: Reading spine and computing per-commit signals...")
    commits = []
    with open(SPINE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            h, date_str, author, subject = parts
            commits.append({
                "hash": h,
                "date": date_str,
                "author": author,
                "subject": subject,
            })

    print(f"  Found {len(commits)} commits in spine.")

    for i, c in enumerate(commits):
        if (i + 1) % 50 == 0:
            print(f"  Processing commit {i+1}/{len(commits)}...")
        files = get_touched_files(c["hash"])
        dirs = sorted(set(top_level_dir(f) for f in files))
        tags = derive_tags(files)
        c["touched_dirs"] = dirs
        c["touched_file_count"] = len(files)
        c["tags"] = tags

    # Aggregates
    dir_counter = Counter()
    tag_counter = Counter()
    monthly_counter = Counter()
    author_counter = Counter()

    for c in commits:
        for d in c["touched_dirs"]:
            dir_counter[d] += 1
        for t in c["tags"]:
            tag_counter[t] += 1
        # month key
        try:
            dt = datetime.fromisoformat(c["date"])
            month_key = dt.strftime("%Y-%m")
        except Exception:
            month_key = "UNKNOWN"
        monthly_counter[month_key] += 1
        author_counter[c["author"]] += 1

    metrics = {
        "repo": {
            "root": ROOT,
            "head": HEAD,
            "total_commits": len(commits),
        },
        "commits": commits,
        "aggregates": {
            "directory_counts": dict(dir_counter.most_common()),
            "tag_counts": dict(tag_counter.most_common()),
            "monthly_counts": dict(sorted(monthly_counter.items())),
            "author_counts": dict(author_counter.most_common()),
        }
    }
    return metrics


# ── STEP 3: Epoch detection ──
STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "have",
    "has", "had", "not", "but", "are", "was", "were", "been", "will",
    "can", "may", "all", "its", "also", "add", "added", "update", "updated",
    "fix", "fixed", "use", "new", "set", "get", "via", "per", "run", "one",
    "two", "three", "more", "some", "each", "only", "first", "last",
}

def tokenize_subject(subj):
    tokens = re.split(r'[^a-zA-Z0-9]+', subj.lower())
    return [t for t in tokens if len(t) >= 3 and t not in STOPWORDS]


def step3(metrics):
    print("Step 3: Computing epochs...")
    commits = metrics["commits"]
    n = len(commits)
    if n == 0:
        return []

    WINDOW = 15

    # Parse dates
    for c in commits:
        try:
            c["_dt"] = datetime.fromisoformat(c["date"])
        except Exception:
            c["_dt"] = None

    # Find boundary indices
    boundaries = [0]  # first commit is always a boundary

    for i in range(1, n):
        # Check time gap
        if commits[i]["_dt"] and commits[i-1]["_dt"]:
            gap = (commits[i]["_dt"] - commits[i-1]["_dt"]).days
            if gap >= 14:
                boundaries.append(i)
                continue

        # Rolling window dominant dir check
        if i >= WINDOW:
            # Previous window: [i-WINDOW, i)
            prev_dirs = Counter()
            for j in range(max(0, i - WINDOW), i):
                for d in commits[j]["touched_dirs"]:
                    prev_dirs[d] += 1
            prev_dom = prev_dirs.most_common(1)

            # Current window: [i-WINDOW+1, i+1)
            curr_dirs = Counter()
            for j in range(max(0, i - WINDOW + 1), min(n, i + 1)):
                for d in commits[j]["touched_dirs"]:
                    curr_dirs[d] += 1
            curr_dom = curr_dirs.most_common(1)

            if prev_dom and curr_dom:
                prev_dom_dir = prev_dom[0][0]
                prev_dom_pct = prev_dom[0][1] / WINDOW
                curr_dom_dir = curr_dom[0][0]
                curr_dom_pct = curr_dom[0][1] / WINDOW
                if prev_dom_pct >= 0.5 and curr_dom_pct >= 0.5 and prev_dom_dir != curr_dom_dir:
                    boundaries.append(i)
                    continue

            # Rolling window dominant tag check
            prev_tags = Counter()
            for j in range(max(0, i - WINDOW), i):
                for t in commits[j]["tags"]:
                    prev_tags[t] += 1
            curr_tags = Counter()
            for j in range(max(0, i - WINDOW + 1), min(n, i + 1)):
                for t in commits[j]["tags"]:
                    curr_tags[t] += 1

            # Dominant tag set: tags covering >=60% of commits
            def dominant_tag_set(tag_counter, window_size):
                total = window_size
                result = set()
                running = 0
                for tag, cnt in tag_counter.most_common():
                    result.add(tag)
                    running += cnt
                    if running / max(total, 1) >= 0.6:
                        break
                return frozenset(result)

            prev_tag_set = dominant_tag_set(prev_tags, WINDOW)
            curr_tag_set = dominant_tag_set(curr_tags, WINDOW)
            if prev_tag_set != curr_tag_set:
                boundaries.append(i)
                continue

    # Deduplicate and sort boundaries
    boundaries = sorted(set(boundaries))

    # Build epochs from boundary segments
    epochs = []
    for bi in range(len(boundaries)):
        start = boundaries[bi]
        end = boundaries[bi + 1] if bi + 1 < len(boundaries) else n
        epoch_commits = commits[start:end]
        if not epoch_commits:
            continue

        # Date range
        dates = [c["_dt"] for c in epoch_commits if c["_dt"]]
        date_min = min(dates).isoformat() if dates else "UNKNOWN"
        date_max = max(dates).isoformat() if dates else "UNKNOWN"

        # Dominant dirs
        dir_c = Counter()
        for c in epoch_commits:
            for d in c["touched_dirs"]:
                dir_c[d] += 1

        # Dominant tags
        tag_c = Counter()
        for c in epoch_commits:
            for t in c["tags"]:
                tag_c[t] += 1

        # Representative commits: top 3 by touched_file_count, ties broken by earliest
        sorted_by_files = sorted(epoch_commits, key=lambda c: (-c["touched_file_count"], c["date"]))
        reps = sorted_by_files[:3]

        # Label derivation
        top_dirs = [d for d, _ in dir_c.most_common(2)]
        subject_tokens = Counter()
        for c in epoch_commits:
            for t in tokenize_subject(c["subject"]):
                subject_tokens[t] += 1
        top_tokens = [t for t, _ in subject_tokens.most_common(5)]

        if top_dirs or top_tokens:
            dir_part = "+".join(top_dirs[:2]) if top_dirs else ""
            tok_part = " ".join(top_tokens[:3]) if top_tokens else ""
            label = f"{dir_part}: {tok_part}".strip(": ")
            if not label:
                label = "Mixed activity (insufficient signal)"
        else:
            label = "Mixed activity (insufficient signal)"

        epochs.append({
            "epoch_index": len(epochs),
            "date_range": [date_min, date_max],
            "commit_count": len(epoch_commits),
            "dominant_dirs": dict(dir_c.most_common(10)),
            "dominant_tags": dict(tag_c.most_common(10)),
            "representative_commits": [
                {"hash": r["hash"], "date": r["date"], "subject": r["subject"]}
                for r in reps
            ],
            "label": label,
        })

    print(f"  Derived {len(epochs)} epochs.")
    return epochs


# ── STEP 4: Crossover map ──
def step4(metrics):
    print("Step 4: Computing crossover map...")
    commits = metrics["commits"]

    # Build tag→commit_indices mapping
    tag_commits = defaultdict(set)
    for i, c in enumerate(commits):
        for t in c["tags"]:
            tag_commits[t].add(i)

    all_tags = sorted(tag_commits.keys())

    # Pairwise overlap counts
    overlaps = {}
    for a, b in combinations(all_tags, 2):
        common = tag_commits[a] & tag_commits[b]
        if common:
            overlaps[f"{a} + {b}"] = len(common)

    # Sort by overlap count desc
    sorted_overlaps = dict(sorted(overlaps.items(), key=lambda x: -x[1]))

    # Top 5 overlap windows (contiguous runs)
    def find_contiguous_windows(indices, commits_list, max_windows=5):
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

        # Sort by length desc
        windows.sort(key=lambda w: -(w[1] - w[0] + 1))
        result = []
        for s, e in windows[:max_windows]:
            result.append({
                "start_idx": s,
                "end_idx": e,
                "commit_count": e - s + 1,
                "date_range": [commits_list[s]["date"], commits_list[e]["date"]],
                "hashes": [commits_list[j]["hash"][:12] for j in range(s, e + 1)]
            })
        return result

    # Top 20 overlaps with windows
    top_overlap_keys = list(sorted_overlaps.keys())[:20]
    overlap_details = {}
    for key in top_overlap_keys:
        a, b = key.split(" + ")
        common_indices = sorted(tag_commits[a] & tag_commits[b])
        overlap_details[key] = {
            "count": sorted_overlaps[key],
            "windows": find_contiguous_windows(common_indices, commits)
        }

    # Per-tag monthly frequencies
    tag_monthly = {}
    for tag in all_tags:
        monthly = Counter()
        for idx in tag_commits[tag]:
            c = commits[idx]
            try:
                dt = datetime.fromisoformat(c["date"])
                monthly[dt.strftime("%Y-%m")] += 1
            except Exception:
                pass
        tag_monthly[tag] = dict(sorted(monthly.items()))

    crossover = {
        "pairwise_overlaps": sorted_overlaps,
        "top_overlap_details": overlap_details,
        "tag_monthly_frequencies": tag_monthly,
    }
    print(f"  Found {len(sorted_overlaps)} tag pairs with overlap.")
    return crossover


# ── STEP 5: Write report ──
def step5(metrics, epochs, crossover):
    print("Step 5: Writing HISTORY_REPORT.md...")
    total = metrics["repo"]["total_commits"]
    lines = []
    lines.append("# OVC Repo History Recon — Derived Metrics (scratch)\n")

    # Coverage
    lines.append("## Coverage\n")
    lines.append(f"- **ROOT:** `{ROOT}`")
    lines.append(f"- **HEAD:** `{HEAD}`")
    lines.append(f"- **Total commits:** {total}")
    lines.append(f"- **Working tree state:** clean\n")

    # Directory heatmap
    lines.append("## Global Directory Heatmap\n")
    lines.append("| Directory | Commits | Percent |")
    lines.append("|-----------|---------|---------|")
    for d, cnt in sorted(metrics["aggregates"]["directory_counts"].items(), key=lambda x: -x[1]):
        pct = f"{cnt/total*100:.1f}%"
        lines.append(f"| `{d}` | {cnt} | {pct} |")
    lines.append("")

    # Tag heatmap
    lines.append("## Global Tag Heatmap\n")
    lines.append("| Tag | Commits | Percent |")
    lines.append("|-----|---------|---------|")
    for t, cnt in sorted(metrics["aggregates"]["tag_counts"].items(), key=lambda x: -x[1]):
        pct = f"{cnt/total*100:.1f}%"
        lines.append(f"| `{t}` | {cnt} | {pct} |")

    # Check for absent known tags
    all_known = [
        "governance_contracts", "operations", "repo_map", "catalogs", "validation",
        "governance_tooling", "scripts_general", "control_panel", "audit_interpreter",
        "tools_general", "evidence_runs", "ci_workflows", "contracts", "claims",
        "data", "infra", "research", "specs", "schema", "source_code", "tests",
        "repo_maze", "artifacts", "releases", "trajectory", "pine", "chmod_test",
        "codex_runtime"
    ]
    observed = set(metrics["aggregates"]["tag_counts"].keys())
    absent = [t for t in all_known if t not in observed]
    if absent:
        lines.append(f"\n**Tags not observed in paths:** {', '.join(sorted(absent))}\n")
    lines.append("")

    # Epochs
    lines.append("## Epochs (Derived)\n")
    for ep in epochs:
        lines.append(f"### Epoch {ep['epoch_index']} — {ep['label']}\n")
        lines.append(f"- **Date range:** {ep['date_range'][0]} → {ep['date_range'][1]}")
        lines.append(f"- **Commits:** {ep['commit_count']}")
        lines.append(f"- **Dominant dirs:** {', '.join(f'`{d}` ({c})' for d, c in list(ep['dominant_dirs'].items())[:5])}")
        lines.append(f"- **Dominant tags:** {', '.join(f'`{t}` ({c})' for t, c in list(ep['dominant_tags'].items())[:5])}")
        lines.append(f"- **Representative commits:**")
        for rc in ep["representative_commits"]:
            lines.append(f"  - `{rc['hash'][:12]}` | {rc['date']} | {rc['subject']}")
        lines.append("")

    # Crossover map
    lines.append("## Crossover Map (Streams Overlap)\n")
    lines.append("### Top Pairwise Overlaps\n")
    lines.append("| Tag A + Tag B | Commits |")
    lines.append("|---------------|---------|")
    top_pairs = list(crossover["pairwise_overlaps"].items())[:20]
    for pair, cnt in top_pairs:
        lines.append(f"| `{pair}` | {cnt} |")
    lines.append("")

    # Top 5 overlap windows
    lines.append("### Top 5 Overlap Windows\n")
    top5_keys = list(crossover["top_overlap_details"].keys())[:5]
    for key in top5_keys:
        detail = crossover["top_overlap_details"][key]
        lines.append(f"#### `{key}` ({detail['count']} commits)\n")
        for wi, w in enumerate(detail["windows"][:5]):
            lines.append(f"- Window {wi+1}: {w['date_range'][0]} → {w['date_range'][1]} ({w['commit_count']} commits)")
            if len(w["hashes"]) <= 8:
                lines.append(f"  - Hashes: {', '.join(w['hashes'])}")
            else:
                lines.append(f"  - Hashes: {', '.join(w['hashes'][:5])} ... +{len(w['hashes'])-5} more")
        lines.append("")

    # Timeline signals
    lines.append("## Timeline Signals\n")

    # evidence_runs per month
    er_monthly = crossover["tag_monthly_frequencies"].get("evidence_runs", {})
    if er_monthly:
        lines.append("### `evidence_runs` per Month\n")
        lines.append("| Month | Commits |")
        lines.append("|-------|---------|")
        for m, c in sorted(er_monthly.items()):
            lines.append(f"| {m} | {c} |")
        lines.append("")

    # governance/maintenance per month
    gov_tags = ["governance_contracts", "governance_tooling"]
    gov_monthly = Counter()
    for gt in gov_tags:
        for m, c in crossover["tag_monthly_frequencies"].get(gt, {}).items():
            gov_monthly[m] += c
    if gov_monthly:
        lines.append("### Governance/Maintenance per Month\n")
        lines.append("| Month | Commits |")
        lines.append("|-------|---------|")
        for m, c in sorted(gov_monthly.items()):
            lines.append(f"| {m} | {c} |")
        lines.append("")

    # Additional notable tags
    notable = ["control_panel", "validation", "scripts_general", "ci_workflows", "source_code", "tests"]
    for tag in notable:
        tm = crossover["tag_monthly_frequencies"].get(tag, {})
        if tm:
            lines.append(f"### `{tag}` per Month\n")
            lines.append("| Month | Commits |")
            lines.append("|-------|---------|")
            for m, c in sorted(tm.items()):
                lines.append(f"| {m} | {c} |")
            lines.append("")

    lines.append("---\n")
    lines.append("*Report generated from git history only. No intent claims.*\n")

    report_path = os.path.join(SCRATCH, "HISTORY_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written to {report_path}")


# ── STEP 6: Print summary ──
def step6(metrics, epochs, crossover):
    total = metrics["repo"]["total_commits"]
    print("\n" + "="*60)
    print("OVC REPO HISTORY — SUMMARY")
    print("="*60)
    print(f"ROOT:           {ROOT}")
    print(f"HEAD:           {HEAD}")
    print(f"Total commits:  {total}")
    print()

    print("Top 5 directories by commit count:")
    for d, cnt in list(metrics["aggregates"]["directory_counts"].items())[:5]:
        print(f"  {d:30s} {cnt:4d} ({cnt/total*100:.1f}%)")
    print()

    print("Top 5 tags by commit count:")
    for t, cnt in list(metrics["aggregates"]["tag_counts"].items())[:5]:
        print(f"  {t:30s} {cnt:4d} ({cnt/total*100:.1f}%)")
    print()

    print(f"Derived epochs: {len(epochs)}")
    for ep in epochs:
        print(f"  Epoch {ep['epoch_index']}: {ep['label']} ({ep['commit_count']} commits, {ep['date_range'][0][:10]} -> {ep['date_range'][1][:10]})")
    print()

    print("Top 5 tag overlaps:")
    for pair, cnt in list(crossover["pairwise_overlaps"].items())[:5]:
        print(f"  {pair:50s} {cnt:4d}")
    print()


# ── Main ──
if __name__ == "__main__":
    metrics = step2()

    # Save metrics JSON
    json_path = os.path.join(SCRATCH, "history_metrics.json")
    # Remove non-serializable _dt fields
    for c in metrics["commits"]:
        if "_dt" in c:
            del c["_dt"]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"  Written metrics to {json_path}")

    # Re-parse _dt for epoch computation
    for c in metrics["commits"]:
        try:
            c["_dt"] = datetime.fromisoformat(c["date"])
        except Exception:
            c["_dt"] = None

    epochs = step3(metrics)
    crossover = step4(metrics)

    # Add epochs and crossover to metrics
    metrics_full = {
        **{k: v for k, v in metrics.items() if k != "commits"},
        "commits": [{k: v for k, v in c.items() if k != "_dt"} for c in metrics["commits"]],
        "epochs": epochs,
        "crossover_summary": {
            "top_overlaps": dict(list(crossover["pairwise_overlaps"].items())[:20]),
        }
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_full, f, indent=2, default=str)
    print(f"  Updated metrics JSON with epochs + crossover.")

    step5(metrics, epochs, crossover)
    step6(metrics, epochs, crossover)
