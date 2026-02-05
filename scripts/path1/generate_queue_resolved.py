#!/usr/bin/env python3
"""
Generate RUN_QUEUE_RESOLVED.csv by reconciling queue intent with INDEX.md ledger.

This script produces a derived view that:
- Takes RUN_QUEUE.csv (intent-only, not authoritative)
- Compares against INDEX.md (canonical execution ledger)
- Parses RUN.md files for actual executed date ranges (in case of substitution)
- Outputs RUN_QUEUE_RESOLVED.csv with complete reconciliation

The output file is GENERATED, not manually maintained.
INDEX.md remains the canonical source of truth.

Usage:
    python scripts/path1/generate_queue_resolved.py
    python scripts/path1/generate_queue_resolved.py --repo-root /path/to/repo
"""

import argparse
import csv
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ovc_ops.run_envelope_v0_1 import (  # noqa: E402
    ensure_run_dir,
    get_git_state,
    make_run_id,
    seal_dir,
    write_run_json,
)


def parse_index_md(index_path: Path) -> dict:
    """
    Parse INDEX.md to extract completed runs.
    
    Returns dict: run_id -> {date_range, symbol, n, status, line_number}
    """
    runs = {}
    
    if not index_path.exists():
        return runs
    
    content = index_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Pattern: | run_id | date_range | symbol | n | status | link |
    table_pattern = re.compile(
        r'^\|\s*(p1_\d{8}_\d{3})\s*\|\s*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s*\|'
        r'\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|'
    )
    
    for line_num, line in enumerate(lines, start=1):
        match = table_pattern.match(line)
        if match:
            run_id = match.group(1)
            date_start = match.group(2)
            date_end = match.group(3)
            symbol = match.group(4)
            n_obs = int(match.group(5))
            status = match.group(6)
            
            runs[run_id] = {
                'date_range': f"{date_start} to {date_end}",
                'date_start': date_start,
                'date_end': date_end,
                'symbol': symbol,
                'n_observations': n_obs,
                'status': status,
                'index_line': line_num,
            }
    
    return runs


def parse_run_md(run_md_path: Path) -> dict:
    """
    Parse RUN.md to extract actual executed date range (handles substitution).
    
    Returns dict with date_range_requested, date_range_actual, symbol, n_observations.
    """
    result = {
        'date_range_requested_start': None,
        'date_range_requested_end': None,
        'date_range_actual_start': None,
        'date_range_actual_end': None,
        'symbol': None,
        'n_observations': None,
    }
    
    if not run_md_path.exists():
        return result
    
    content = run_md_path.read_text(encoding='utf-8')
    
    # Parse metadata table
    # | `date_range_requested` | `2023-10-02` to `2023-10-06` |
    requested_match = re.search(
        r'\|\s*`date_range_requested`\s*\|\s*`(\d{4}-\d{2}-\d{2})`\s+to\s+`(\d{4}-\d{2}-\d{2})`',
        content
    )
    if requested_match:
        result['date_range_requested_start'] = requested_match.group(1)
        result['date_range_requested_end'] = requested_match.group(2)
    
    # | `date_range_actual` | `2023-10-02` to `2023-10-06` |
    actual_match = re.search(
        r'\|\s*`date_range_actual`\s*\|\s*`(\d{4}-\d{2}-\d{2})`\s+to\s+`(\d{4}-\d{2}-\d{2})`',
        content
    )
    if actual_match:
        result['date_range_actual_start'] = actual_match.group(1)
        result['date_range_actual_end'] = actual_match.group(2)
    
    # | `symbol(s)` | `GBPUSD` |
    symbol_match = re.search(r'\|\s*`symbol\(s\)`\s*\|\s*`([^`]+)`', content)
    if symbol_match:
        result['symbol'] = symbol_match.group(1)
    
    # | `n_observations` | `59` |
    n_obs_match = re.search(r'\|\s*`n_observations`\s*\|\s*`?(\d+)`?', content)
    if n_obs_match:
        result['n_observations'] = int(n_obs_match.group(1))
    
    return result


def parse_queue_csv(queue_path: Path) -> list:
    """
    Parse RUN_QUEUE.csv intent file.
    
    Returns list of dicts with run_id, symbol, date_start, date_end.
    Ignores status column (intent-only, not authoritative).
    """
    rows = []
    
    if not queue_path.exists():
        return rows
    
    with open(queue_path, 'r', encoding='utf-8') as f:
        # Filter out comment lines
        lines = [line for line in f if not line.strip().startswith('#') and line.strip()]
    
    if not lines:
        return rows
    
    reader = csv.DictReader(lines)
    for row in reader:
        if row.get('run_id'):
            rows.append({
                'run_id': row['run_id'].strip(),
                'symbol': row.get('symbol', '').strip(),
                'date_start': row.get('date_start', '').strip(),
                'date_end': row.get('date_end', '').strip(),
                # Note: We read status but do NOT use it as authoritative
                'queue_status': row.get('status', '').strip(),
            })
    
    return rows


def generate_resolved_csv(repo_root: Path, output_path: Path) -> int:
    """
    Generate RUN_QUEUE_RESOLVED.csv by reconciling queue with INDEX.md.
    
    Returns number of rows written.
    """
    queue_path = repo_root / 'reports' / 'path1' / 'evidence' / 'RUN_QUEUE.csv'
    index_path = repo_root / 'reports' / 'path1' / 'evidence' / 'INDEX.md'
    runs_dir = repo_root / 'reports' / 'path1' / 'evidence' / 'runs'
    
    # Parse sources
    queue_rows = parse_queue_csv(queue_path)
    index_runs = parse_index_md(index_path)
    
    # Build resolved rows
    resolved_rows = []
    
    for queue_row in queue_rows:
        run_id = queue_row['run_id']
        
        resolved = {
            'intent_run_id': run_id,
            'symbol': queue_row['symbol'],
            'requested_date_start': queue_row['date_start'],
            'requested_date_end': queue_row['date_end'],
            'completed': 'false',
            'executed_run_id': '',
            'executed_date_start': '',
            'executed_date_end': '',
            'n_observations': '',
            'index_line': '',
            'was_substituted': 'false',
        }
        
        # Check if run exists in INDEX.md (canonical truth)
        if run_id in index_runs:
            index_entry = index_runs[run_id]
            resolved['completed'] = 'true'
            resolved['executed_run_id'] = run_id
            resolved['executed_date_start'] = index_entry['date_start']
            resolved['executed_date_end'] = index_entry['date_end']
            resolved['n_observations'] = str(index_entry['n_observations'])
            resolved['index_line'] = str(index_entry['index_line'])
            
            # Check RUN.md for substitution details
            run_md_path = runs_dir / run_id / 'RUN.md'
            if run_md_path.exists():
                run_details = parse_run_md(run_md_path)
                
                # Detect if date was substituted
                if (run_details['date_range_requested_start'] and 
                    run_details['date_range_actual_start']):
                    if (run_details['date_range_requested_start'] != run_details['date_range_actual_start'] or
                        run_details['date_range_requested_end'] != run_details['date_range_actual_end']):
                        resolved['was_substituted'] = 'true'
                        # Use actual executed dates from RUN.md
                        resolved['executed_date_start'] = run_details['date_range_actual_start']
                        resolved['executed_date_end'] = run_details['date_range_actual_end']
        
        resolved_rows.append(resolved)
    
    # Also add any runs in INDEX.md that are NOT in queue (manual runs, etc.)
    queue_run_ids = {row['run_id'] for row in queue_rows}
    for run_id, index_entry in index_runs.items():
        if run_id not in queue_run_ids:
            resolved_rows.append({
                'intent_run_id': '',  # No queue intent
                'symbol': index_entry['symbol'],
                'requested_date_start': '',
                'requested_date_end': '',
                'completed': 'true',
                'executed_run_id': run_id,
                'executed_date_start': index_entry['date_start'],
                'executed_date_end': index_entry['date_end'],
                'n_observations': str(index_entry['n_observations']),
                'index_line': str(index_entry['index_line']),
                'was_substituted': 'unknown',  # Can't determine without queue intent
            })
    
    # Sort by executed_run_id or intent_run_id
    resolved_rows.sort(key=lambda r: r['executed_run_id'] or r['intent_run_id'])
    
    # Write output CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'intent_run_id',
        'symbol',
        'requested_date_start',
        'requested_date_end',
        'completed',
        'executed_run_id',
        'executed_date_start',
        'executed_date_end',
        'n_observations',
        'index_line',
        'was_substituted',
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        # Write header comment
        f.write('# RUN_QUEUE_RESOLVED.csv - GENERATED FILE (DO NOT EDIT MANUALLY)\n')
        f.write(f'# Generated: {datetime.now(tz=None).strftime("%Y-%m-%dT%H:%M:%SZ")}\n')
        f.write('# Source of truth: reports/path1/evidence/INDEX.md\n')
        f.write('# This file reconciles queue intent with actual execution ledger.\n')
        f.write('#\n')
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resolved_rows)
    
    return len(resolved_rows)


def main():
    parser = argparse.ArgumentParser(
        description='Generate RUN_QUEUE_RESOLVED.csv from queue intent and INDEX.md ledger'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root path (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path (default: reports/path1/evidence/RUN_QUEUE_RESOLVED.csv)'
    )
    
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    run_id = make_run_id("op_d10")
    run_dir = ensure_run_dir(repo_root / "reports" / "runs", run_id)
    created_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    git_commit, working_tree_state = get_git_state()
    
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = repo_root / 'reports' / 'path1' / 'evidence' / 'RUN_QUEUE_RESOLVED.csv'
    
    print(f"Repo root: {repo_root}")
    print(f"Output: {output_path}")
    
    # Verify paths exist
    index_path = repo_root / 'reports' / 'path1' / 'evidence' / 'INDEX.md'
    if not index_path.exists():
        print(f"WARNING: INDEX.md not found at {index_path}")
    
    queue_path = repo_root / 'reports' / 'path1' / 'evidence' / 'RUN_QUEUE.csv'
    if not queue_path.exists():
        print(f"WARNING: RUN_QUEUE.csv not found at {queue_path}")
    
    # Generate resolved CSV
    row_count = generate_resolved_csv(repo_root, output_path)

    copy_target = run_dir / "RUN_QUEUE_RESOLVED.csv"
    shutil.copyfile(output_path, copy_target)
    
    print(f"Generated {output_path.name} with {row_count} rows")
    print("Done.")

    try:
        inputs_payload = {
            "queue_path": "reports/path1/evidence/RUN_QUEUE.csv",
            "index_path": "reports/path1/evidence/INDEX.md",
            "source_output_path": "reports/path1/evidence/RUN_QUEUE_RESOLVED.csv",
        }
        run_json_payload = {
            "run_id": run_dir.name,
            "created_utc": created_utc,
            "run_type": "op_run",
            "option": "D",
            "operation_id": "OP-D10",
            "git_commit": git_commit,
            "working_tree_state": working_tree_state,
            "inputs": inputs_payload,
            "outputs": [
                "RUN_QUEUE_RESOLVED.csv",
                "run.json",
                "manifest.json",
                "MANIFEST.sha256",
            ],
        }
        write_run_json(run_dir, run_json_payload)
        seal_dir(run_dir, ["RUN_QUEUE_RESOLVED.csv", "run.json"], strict=True)
    except Exception as exc:
        print(f"WARNING: run envelope write failed: {exc}")


if __name__ == '__main__':
    main()
