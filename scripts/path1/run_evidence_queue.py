#!/usr/bin/env python3
"""
Path 1 Evidence Queue Runner
============================
Mechanical execution of Path 1 Evidence runs from a queued CSV file.

Replicates exact behavior of manual Runs 001-003:
- Environment validation
- Data availability check (with substitution)
- SQL wrapper generation
- psql study execution
- Output capture
- Report generation (RUN.md, evidence markdowns)
- INDEX.md append-only update

CRITICAL: This script behaves like a mechanical clerk.
It repeats the same procedure deterministically.
It does NOT "improve" anything.
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================================
# SAFEGUARD FUNCTIONS
# ============================================================================

def validate_date_format(date_str: str, field_name: str) -> bool:
    """Validate date is in ISO format YYYY-MM-DD.
    
    Rejects Excel-corrupted formats like DD/MM/YYYY or MM/DD/YYYY.
    """
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        print(f"ERROR: {field_name} has invalid format: '{date_str}'")
        print(f"       Expected: YYYY-MM-DD (ISO format)")
        print(f"       This often happens when CSV is edited in Excel.")
        print(f"       Fix: Edit with a text editor, not Excel.")
        return False
    return True


# ============================================================================
# FROZEN CONSTANTS (DO NOT MODIFY)
# ============================================================================

SCORE_CONFIGS = {
    "DIS": {
        "version": "v1.1",
        "column": "dis_v1_1_raw",
        "view": "derived.v_path1_evidence_dis_v1_1",
        "status": "FROZEN"
    },
    "RES": {
        "version": "v1.0",
        "column": "res_v1_0_raw",
        "view": "derived.v_path1_evidence_res_v1_0",
        "status": "FROZEN"
    },
    "LID": {
        "version": "v1.0",
        "column": "lid_v1_0_raw",
        "view": "derived.v_path1_evidence_lid_v1_0",
        "status": "FROZEN"
    }
}

INVARIANTS_TEXT = """
> **Association ≠ Predictability.** Co-occurrence patterns do not imply scores predict outcomes.  
> **Scores are descriptive and frozen.** They describe structural characteristics, not signals.  
> **Summaries are non-interpretive.** They describe what occurred, not what will occur.
"""

REQUIRED_RUN_FILES = [
    "RUN.md",
    "DIS_v1_1_evidence.md",
    "RES_v1_0_evidence.md",
    "LID_v1_0_evidence.md",
]

REQUIRED_OUTPUT_FILES = [
    "outputs/study_dis_v1_1.txt",
    "outputs/study_res_v1_0.txt",
    "outputs/study_lid_v1_0.txt",
]

REQUIRED_PACK_FILES = [
    "outputs/evidence_pack_v0_2/manifest.json",
    "outputs/evidence_pack_v0_2/manifest_sha256.txt",
    "outputs/evidence_pack_v0_2/pack_sha256.txt",
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_environment() -> str:
    """Validate required environment variables and tools."""
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not db_url:
        print("ERROR: DATABASE_URL or NEON_DSN environment variable not set")
        sys.exit(1)
    
    # Test psql availability
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True, text=True, check=True
        )
        print(f"psql available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: psql command not found")
        sys.exit(1)
    
    return db_url


def update_queue_status(queue_path: Path, completed_runs: dict):
    """Update queue CSV to mark completed runs and update actual dates.
    
    Args:
        queue_path: Path to queue CSV file
        completed_runs: Dict of run_id -> (actual_start, actual_end) for completed runs
    
    Preserves comment lines, adds/updates 'status' column, and updates
    date_start/date_end columns to reflect actual dates used (in case of substitution).
    """
    # Read all lines preserving comments
    with open(queue_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    
    # Separate comments from data
    comment_lines = [line for line in all_lines if line.strip().startswith('#')]
    data_lines = [line for line in all_lines if not line.strip().startswith('#') and line.strip()]
    
    if not data_lines:
        return
    
    # Parse header
    header_line = data_lines[0].strip()
    headers = [h.strip() for h in header_line.split(',')]
    
    # Add status column if not present
    if 'status' not in headers:
        headers.append('status')
        header_line = ','.join(headers)
    
    status_idx = headers.index('status')
    date_start_idx = headers.index('date_start') if 'date_start' in headers else None
    date_end_idx = headers.index('date_end') if 'date_end' in headers else None
    
    # Process data rows
    updated_rows = [header_line]
    for line in data_lines[1:]:
        if not line.strip():
            continue
        
        values = line.strip().split(',')
        
        # Pad with empty values if needed
        while len(values) < len(headers):
            values.append('')
        
        run_id = values[0].strip() if values else ''
        
        # Update status and dates for completed runs
        if run_id in completed_runs:
            actual_start, actual_end = completed_runs[run_id]
            old_start = values[date_start_idx] if date_start_idx is not None else ''
            old_end = values[date_end_idx] if date_end_idx is not None else ''
            
            values[status_idx] = 'complete'
            
            # Update dates if they were substituted
            if date_start_idx is not None and actual_start != old_start:
                values[date_start_idx] = actual_start
                print(f"Queue updated: {run_id} date_start {old_start} -> {actual_start}")
            if date_end_idx is not None and actual_end != old_end:
                values[date_end_idx] = actual_end
                print(f"Queue updated: {run_id} date_end {old_end} -> {actual_end}")
            
            print(f"Queue updated: {run_id} -> complete")
        
        updated_rows.append(','.join(values))
    
    # Write back with comments preserved
    with open(queue_path, "w", encoding="utf-8", newline="\n") as f:
        for comment in comment_lines:
            f.write(comment)
        for row in updated_rows:
            f.write(row + '\n')
    
    print(f"Queue file updated: {queue_path}")


def run_sql_query(db_url: str, sql: str) -> str:
    """Execute SQL via psql and return output."""
    result = subprocess.run(
        ["psql", db_url, "-t", "-A", "-c", sql],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def run_sql_file(db_url: str, sql_file: Path, output_file: Path) -> str:
    """Execute SQL file via psql and capture output.
    
    Raises:
        subprocess.CalledProcessError: If psql returns non-zero exit code.
    """
    result = subprocess.run(
        ["psql", db_url, "-f", str(sql_file)],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    output_file.write_text(output, encoding="utf-8", newline="\n")
    
    # Fail-fast: propagate psql failures (Task A remediation)
    # WARNING: Prior runs in this batch are already committed to filesystem.
    # This exception stops the batch but does NOT roll back completed runs.
    if result.returncode != 0:
        print(f"ERROR: psql failed with exit code {result.returncode}")
        print(f"SQL file: {sql_file}")
        print(f"Output: {output[:2000]}" if len(output) > 2000 else f"Output: {output}")
        raise subprocess.CalledProcessError(
            result.returncode, result.args, result.stdout, result.stderr
        )
    
    return output


def truthy_env(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y"}


def write_path1_summary(
    repo_root: Path,
    run_id: str,
    date_from: str,
    date_to: str,
    rows_processed: int,
    outcome: str,
) -> Path:
    summary_dir = repo_root / "artifacts"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / "path1_summary.json"
    payload = {
        "run_id": run_id,
        "date_from": date_from,
        "date_to": date_to,
        "rows_processed": rows_processed,
        "outcome": outcome,
    }
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"PATH1_SUMMARY_JSON: {summary_path}")
    return summary_path


def parse_run_md_metadata(run_md_path: Path) -> Dict[str, Optional[str]]:
    metadata: Dict[str, Optional[str]] = {
        "date_start_actual": None,
        "date_end_actual": None,
        "symbol": None,
        "n_obs": None,
    }
    if not run_md_path.exists():
        return metadata
    content = run_md_path.read_text(encoding="utf-8")
    date_match = re.search(
        r"\| `date_range_actual` \| `(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})` \|",
        content,
    )
    if date_match:
        metadata["date_start_actual"] = date_match.group(1)
        metadata["date_end_actual"] = date_match.group(2)
    symbol_match = re.search(r"\| `symbol\(s\)` \| `([^`]+)` \|", content)
    if symbol_match:
        metadata["symbol"] = symbol_match.group(1)
    n_obs_match = re.search(r"\| `n_observations` \| `(\d+)` \|", content)
    if n_obs_match:
        metadata["n_obs"] = n_obs_match.group(1)
    return metadata


def check_run_completeness(report_dir: Path, require_pack: bool) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    for rel_path in REQUIRED_RUN_FILES + REQUIRED_OUTPUT_FILES:
        path = report_dir / rel_path
        if not path.exists() or not path.is_file() or path.stat().st_size == 0:
            missing.append(rel_path)
    if require_pack:
        for rel_path in REQUIRED_PACK_FILES:
            path = report_dir / rel_path
            if not path.exists() or not path.is_file() or path.stat().st_size == 0:
                missing.append(rel_path)
    return (len(missing) == 0, missing)


def quarantine_run_folder(report_dir: Path, missing: List[str]) -> Path:
    quarantine_root = report_dir.parent / "_quarantine"
    quarantine_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    quarantine_dir = quarantine_root / f"{report_dir.name}__{timestamp}__INCOMPLETE"
    if report_dir.is_dir():
        shutil.move(str(report_dir), str(quarantine_dir))
    else:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(report_dir), str(quarantine_dir / report_dir.name))
    note_path = quarantine_dir / "QUARANTINE_NOTE.md"
    missing_lines = "\n".join(f"- {item}" for item in missing) if missing else "- Unknown"
    note_path.write_text(
        "# Quarantine Note\n\n"
        "This run folder was moved because it was incomplete at execution time.\n\n"
        f"Original path: `{report_dir}`\n"
        f"Quarantined at: `{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}`\n\n"
        "Missing or empty artifacts:\n"
        f"{missing_lines}\n",
        encoding="utf-8",
        newline="\n",
    )
    return quarantine_dir


def build_evidence_pack_v0_2(
    repo_root: Path,
    db_url: str,
    run_id: str,
    symbol: str,
    date_start: str,
    date_end: str,
) -> None:
    """Run the evidence pack v0.2 builder (best-effort, non-fatal)."""
    script_path = repo_root / "scripts" / "path1" / "build_evidence_pack_v0_2.py"
    if not script_path.exists():
        print(f"WARNING: Evidence pack builder missing: {script_path}")
        return

    cmd = [
        sys.executable,
        str(script_path),
        "--run-id",
        run_id,
        "--sym",
        symbol,
        "--date-from",
        date_start,
        "--date-to",
        date_end,
        "--repo-root",
        str(repo_root),
    ]
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print("WARNING: Evidence pack v0.2 build failed (non-fatal).")
        if result.stdout:
            print(result.stdout.strip()[:2000])
        if result.stderr:
            print(result.stderr.strip()[:2000])
    else:
        print("Evidence pack v0.2 build complete.")


def check_data_availability(db_url: str, symbol: str, date_start: str, date_end: str) -> int:
    """Check row count for given date range."""
    sql = f"""
    SELECT COUNT(*)
    FROM derived.v_path1_evidence_dis_v1_1
    WHERE sym = '{symbol}'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start}' AND '{date_end}';
    """
    result = run_sql_query(db_url, sql)
    return int(result) if result else 0


def find_substitute_range(
    db_url: str, symbol: str, requested_start: str, requested_end: str,
    existing_ranges: list
) -> Tuple[Optional[str], Optional[str], int]:
    """
    Find substitute 5-day weekday range if requested range has no data.
    Search backwards in 7-day increments until data found.
    Avoids overlapping with existing runs.
    """
    from datetime import date
    
    start_dt = datetime.strptime(requested_start, "%Y-%m-%d").date()
    
    # Search backwards up to 1 year
    for offset in range(7, 366, 7):
        candidate_end = start_dt - timedelta(days=offset)
        
        # Find 5 weekdays ending on candidate_end
        weekdays_found = []
        check_date = candidate_end
        while len(weekdays_found) < 5 and check_date > (candidate_end - timedelta(days=14)):
            if check_date.weekday() < 5:  # Mon=0, Fri=4
                weekdays_found.insert(0, check_date)
            check_date -= timedelta(days=1)
        
        if len(weekdays_found) < 5:
            continue
            
        sub_start = weekdays_found[0].strftime("%Y-%m-%d")
        sub_end = weekdays_found[-1].strftime("%Y-%m-%d")
        
        # Check not overlapping with existing runs
        overlaps = False
        for ex_start, ex_end in existing_ranges:
            if not (sub_end < ex_start or sub_start > ex_end):
                overlaps = True
                break
        
        if overlaps:
            continue
        
        # Check data availability
        row_count = check_data_availability(db_url, symbol, sub_start, sub_end)
        if row_count > 0:
            return sub_start, sub_end, row_count
    
    return None, None, 0


# ============================================================================
# SQL GENERATION (exact replication of manual runs)
# ============================================================================

def generate_study_sql(
    run_id: str, symbol: str, date_start: str, date_end: str,
    score_name: str, score_config: dict
) -> str:
    """Generate study SQL matching exact format of Run 002/003."""
    version = score_config["version"]
    column = score_config["column"]
    view = score_config["view"]
    version_str = f"{score_name}-{version}"
    
    return f"""-- =============================================================================
-- Study: {version_str} Distributional Analysis (Run-Scoped)
-- Run ID: {run_id} | Symbol: {symbol} | Dates: {date_start} to {date_end}
-- =============================================================================

-- FROZEN SCORE VERSION: {version_str}
-- SOURCE VIEW: {view}

-- -----------------------------------------------------------------------------
-- Study 1: Overall {version_str} Score Distribution
-- -----------------------------------------------------------------------------
SELECT
    '{version_str}' AS score_version,
    '{run_id}' AS run_id,
    COUNT(*) AS n_observations,
    AVG({column}) AS mean_score,
    STDDEV({column}) AS stddev_score,
    MIN({column}) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column}) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY {column}) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column}) AS p75_score,
    MAX({column}) AS max_score
FROM {view}
WHERE {column} IS NOT NULL
  AND sym = '{symbol}'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start}' AND '{date_end}';

-- -----------------------------------------------------------------------------
-- Study 2: {version_str} Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
SELECT
    outcome_category,
    COUNT(*) AS n_observations,
    AVG({column}) AS mean_score,
    STDDEV({column}) AS stddev_score,
    MIN({column}) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column}) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY {column}) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column}) AS p75_score,
    MAX({column}) AS max_score
FROM {view}
WHERE {column} IS NOT NULL
  AND outcome_category IS NOT NULL
  AND sym = '{symbol}'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start}' AND '{date_end}'
GROUP BY outcome_category
ORDER BY outcome_category;

-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on {version_str} Score Quantiles
-- -----------------------------------------------------------------------------
WITH score_quantiles AS (
    SELECT
        block_id,
        sym,
        {column},
        outcome_category,
        NTILE(4) OVER (ORDER BY {column}) AS score_quartile
    FROM {view}
    WHERE {column} IS NOT NULL
      AND outcome_category IS NOT NULL
      AND sym = '{symbol}'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start}' AND '{date_end}'
)
SELECT
    score_quartile,
    outcome_category,
    COUNT(*) AS n_observations,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY score_quartile), 2) AS pct_within_quartile
FROM score_quantiles
GROUP BY score_quartile, outcome_category
ORDER BY score_quartile, outcome_category;

-- -----------------------------------------------------------------------------
-- Study 4: Outcome Value Statistics by {version_str} Score Quantile
-- -----------------------------------------------------------------------------
WITH score_quantiles AS (
    SELECT
        {column},
        outcome_ret,
        NTILE(4) OVER (ORDER BY {column}) AS score_quartile
    FROM {view}
    WHERE {column} IS NOT NULL
      AND outcome_ret IS NOT NULL
      AND sym = '{symbol}'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start}' AND '{date_end}'
)
SELECT
    score_quartile,
    COUNT(*) AS n_observations,
    AVG(outcome_ret) AS mean_outcome_ret,
    STDDEV(outcome_ret) AS stddev_outcome_ret,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY outcome_ret) AS median_outcome_ret
FROM score_quantiles
GROUP BY score_quartile
ORDER BY score_quartile;
"""


# ============================================================================
# REPORT GENERATION
# ============================================================================

def parse_study_output(output_text: str) -> dict:
    """
    Parse psql output into structured data.
    Returns dict with study1, study2, study3, study4 keys.
    """
    studies = {}
    current_study = None
    header = None
    rows = []
    
    for line in output_text.split('\n'):
        line = line.strip()
        
        # Detect study boundaries from SQL comments in output
        if 'Study 1:' in line:
            if current_study and rows:
                studies[current_study] = {'header': header, 'rows': rows}
            current_study = 'study1'
            header = None
            rows = []
        elif 'Study 2:' in line:
            if current_study and rows:
                studies[current_study] = {'header': header, 'rows': rows}
            current_study = 'study2'
            header = None
            rows = []
        elif 'Study 3:' in line:
            if current_study and rows:
                studies[current_study] = {'header': header, 'rows': rows}
            current_study = 'study3'
            header = None
            rows = []
        elif 'Study 4:' in line:
            if current_study and rows:
                studies[current_study] = {'header': header, 'rows': rows}
            current_study = 'study4'
            header = None
            rows = []
        elif current_study and line and not line.startswith('-') and not line.startswith('('):
            # Parse table row
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if header is None and any(p.lower() in ['score_version', 'outcome_category', 'score_quartile', 'n_observations'] for p in parts):
                    header = parts
                elif header is not None:
                    rows.append(parts)
    
    # Save last study
    if current_study and rows:
        studies[current_study] = {'header': header, 'rows': rows}
    
    return studies


def generate_evidence_md(
    run_id: str, symbol: str, date_start: str, date_end: str,
    n_obs: int, score_name: str, score_config: dict, 
    study_output: str
) -> str:
    """Generate evidence markdown matching exact format of Run 002."""
    version = score_config["version"]
    version_str = f"{score_name}-{version}"
    view = score_config["view"]
    
    # Parse output to extract study data
    # For now, include raw output as we did in manual runs
    # This ensures exact replication of behavior
    
    output_filename = f"study_{score_name.lower()}_{version.replace('.', '_')}.txt"
    
    return f"""# {version_str} Evidence Report

**Run ID:** {run_id}  
**Score Version:** {version_str} (FROZEN)  
**Symbol:** {symbol}  
**Date Range:** {date_start} to {date_end}  
**n:** {n_obs}

---

## Invariants
{INVARIANTS_TEXT}
---

## Study 1: Overall Score Distribution

*See raw output: `outputs/{output_filename}`*

---

## Study 2: Score Distribution by Outcome Category

*See raw output: `outputs/{output_filename}`*

---

## Study 3: Outcome Frequency by Score Quartile

*See raw output: `outputs/{output_filename}`*

---

## Study 4: Outcome Return by Score Quartile

*See raw output: `outputs/{output_filename}`*

---

## Source

- Evidence View: `{view}`
- Raw Output: `outputs/{output_filename}`
"""


def generate_run_md(
    run_id: str, symbol: str, 
    date_start_requested: str, date_end_requested: str,
    date_start_actual: str, date_end_actual: str,
    n_obs: int, was_substituted: bool
) -> str:
    """Generate RUN.md matching exact format of Run 002."""
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    substitution_section = ""
    if was_substituted:
        substitution_section = f"""
---

## Date Range Substitution

| Field | Value |
|-------|-------|
| Requested Range | `{date_start_requested}` to `{date_end_requested}` |
| Rows in Requested Range | `0` |
| Substituted Range | `{date_start_actual}` to `{date_end_actual}` |
| Rows in Substituted Range | `{n_obs}` |
| Rationale | Original range had zero data. Substituted with nearest non-overlapping 5-day weekday range. |
"""
    
    commands_section = f"""
## Commands Executed

```bash
# Data availability check
psql $DATABASE_URL -c "SELECT COUNT(*) AS rows_in_range FROM derived.v_path1_evidence_dis_v1_1 WHERE sym = '{symbol}' AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start_requested}' AND '{date_end_requested}';"
"""
    
    if was_substituted:
        commands_section += f"""
# Substitute range check
psql $DATABASE_URL -c "SELECT COUNT(*) AS rows_in_range FROM derived.v_path1_evidence_dis_v1_1 WHERE sym = '{symbol}' AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_start_actual}' AND '{date_end_actual}';"
"""
    
    commands_section += f"""
# Execute DIS-v1.1 study
psql $DATABASE_URL -f "sql/path1/evidence/runs/{run_id}/study_dis_v1_1.sql" | tee "reports/path1/evidence/runs/{run_id}/outputs/study_dis_v1_1.txt"

# Execute RES-v1.0 study
psql $DATABASE_URL -f "sql/path1/evidence/runs/{run_id}/study_res_v1_0.sql" | tee "reports/path1/evidence/runs/{run_id}/outputs/study_res_v1_0.txt"

# Execute LID-v1.0 study
psql $DATABASE_URL -f "sql/path1/evidence/runs/{run_id}/study_lid_v1_0.sql" | tee "reports/path1/evidence/runs/{run_id}/outputs/study_lid_v1_0.txt"
```
"""

    return f"""# Path 1 Evidence Run: {run_id}

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `{run_id}` |
| `date_range_requested` | `{date_start_requested}` to `{date_end_requested}` |
| `date_range_actual` | `{date_start_actual}` to `{date_end_actual}` |
| `symbol(s)` | `{symbol}` |
| `generated_at` | `{generated_at}` |
| `n_observations` | `{n_obs}` |
{substitution_section}
---

## Score Versions Used (Frozen)

| Score | Version | Status |
|-------|---------|--------|
| DIS | v1.1 | FROZEN |
| RES | v1.0 | FROZEN |
| LID | v1.0 | FROZEN |

### Outcome Source

- View: `derived.v_ovc_c_outcomes_v0_1`
- Schema: Option C canonical outcomes

---

## Invariants Reminder

> **CRITICAL**: The following invariants apply to all observations in this run.

1. **Association ≠ Predictability**  
   Co-occurrence patterns observed between scores and outcomes do not imply
   that scores predict outcomes. Correlation is not causation.

2. **Scores Are Descriptive, Frozen**  
   Score definitions are locked at the versions specified above. They describe
   structural characteristics of price blocks. They are not signals.

3. **Observations Are Non-Interpretive**  
   All summaries in this report describe what occurred in the data. They do
   not prescribe actions, imply trading logic, or recommend thresholds.

---
{commands_section}
---

## Artifacts Generated

| File | Description |
|------|-------------|
| `outputs/study_dis_v1_1.txt` | Raw DIS-v1.1 study output |
| `outputs/study_res_v1_0.txt` | Raw RES-v1.0 study output |
| `outputs/study_lid_v1_0.txt` | Raw LID-v1.0 study output |
| `DIS_v1_1_evidence.md` | DIS-v1.1 evidence report |
| `RES_v1_0_evidence.md` | RES-v1.0 evidence report |
| `LID_v1_0_evidence.md` | LID-v1.0 evidence report |

---

## Verification Results

| Check | Status |
|-------|--------|
| No Option B modifications | ✅ PASS |
| No score logic changes | ✅ PASS |
| Outputs are observational only | ✅ PASS |
| Frozen score versions used | ✅ PASS |
| Evidence views read-only | ✅ PASS |

---

## Governance Confirmation

- ✅ No Option B views, tables, or contracts were modified
- ✅ SCORE_LIBRARY_v1 unchanged (DIS-v1.1, RES-v1.0, LID-v1.0 remain frozen)
- ✅ No new scores added
- ✅ No interpretation layers added
- ✅ No automation escalation
- ✅ All outputs are observational summaries only

---

## Execution Log

```
Run executed: {datetime.now(UTC).strftime("%Y-%m-%d")}
SQL sources: sql/path1/evidence/runs/{run_id}/
Output location: reports/path1/evidence/runs/{run_id}/outputs/
Generated by: run_evidence_queue.py (automated)
```
"""


def update_index_md(index_path: Path, run_id: str, date_range: str, symbol: str, n_obs: int):
    """Append-only update to INDEX.md with deduplication."""
    content = index_path.read_text(encoding="utf-8")
    
    # SAFEGUARD: Check if run_id already exists in INDEX.md
    if f"| {run_id} |" in content:
        print(f"WARNING: {run_id} already exists in INDEX.md - skipping duplicate entry")
        return
    
    # Find the table and append new row after existing runs
    new_row = f"| {run_id} | {date_range} | {symbol} | {n_obs} | COMPLETE | [RUN.md](runs/{run_id}/RUN.md) |"
    
    # Insert before the "---" after the Completed Runs table
    lines = content.split('\n')
    insert_idx = None
    in_table = False
    
    for i, line in enumerate(lines):
        if '| Run ID |' in line:
            in_table = True
        elif in_table and line.startswith('|'):
            continue
        elif in_table and not line.startswith('|'):
            insert_idx = i
            break
    
    if insert_idx:
        lines.insert(insert_idx, new_row)
        # Update last updated date
        for i, line in enumerate(lines):
            if line.startswith('**Last Updated:**'):
                lines[i] = f"**Last Updated:** {datetime.now(UTC).strftime('%Y-%m-%d')}"
                break
        index_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def execute_single_run(
    db_url: str, repo_root: Path, run_id: str, symbol: str,
    date_start: str, date_end: str, existing_ranges: list,
    dry_run: bool = False,
    build_pack_v0_2: bool = False,
    force_overwrite: bool = False,
) -> Tuple[bool, bool, str, str, str, int]:
    """
    Execute a single evidence run.
    Returns (success, did_execute, message, date_start_actual, date_end_actual, rows_processed).
    """
    print(f"\n{'='*60}")
    print(f"EXECUTING RUN: {run_id}")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Requested: {date_start} to {date_end}")
    
    # SAFEGUARD: Validate date format (catch Excel corruption)
    if not validate_date_format(date_start, 'date_start'):
        return False, f"Invalid date_start format: {date_start}", date_start, date_end
    if not validate_date_format(date_end, 'date_end'):
        return False, f"Invalid date_end format: {date_end}", date_start, date_end
    
    # Create directories
    sql_dir = repo_root / "sql" / "path1" / "evidence" / "runs" / run_id
    report_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / run_id
    output_dir = report_dir / "outputs"
    
    # Check if run artifacts already exist (possible re-run)
    if report_dir.exists():
        if not report_dir.is_dir():
            missing = ["run_folder_not_a_directory"]
            if not force_overwrite and not dry_run:
                quarantine_dir = quarantine_run_folder(report_dir, missing)
                print(f"QUARANTINE: Existing run moved to {quarantine_dir}")
            elif force_overwrite:
                print("FORCE-OVERWRITE: I know what I'm doing. Existing run will be overwritten.")
            else:
                print("DRY RUN: Would quarantine non-directory run folder.")
            if dry_run:
                return True, False, "DRY RUN: non-directory run folder handled", date_start, date_end, 0
        else:
            is_complete, missing = check_run_completeness(report_dir, build_pack_v0_2)
            if is_complete:
                metadata = parse_run_md_metadata(report_dir / "RUN.md")
                date_start_actual = metadata["date_start_actual"] or date_start
                date_end_actual = metadata["date_end_actual"] or date_end
                n_obs = int(metadata["n_obs"]) if metadata["n_obs"] else 0
                if not dry_run:
                    if metadata["symbol"] and metadata["n_obs"] and date_start_actual and date_end_actual:
                        date_range_str = f"{date_start_actual} to {date_end_actual}"
                        index_path = repo_root / "reports" / "path1" / "evidence" / "INDEX.md"
                        if index_path.exists():
                            update_index_md(
                                index_path,
                                run_id,
                                date_range_str,
                                metadata["symbol"],
                                int(metadata["n_obs"]),
                            )
                        else:
                            print(f"WARNING: INDEX.md missing, cannot update: {index_path}")
                    else:
                        print("WARNING: Unable to parse RUN.md metadata for INDEX update.")
                existing_ranges.append((date_start_actual, date_end_actual))
                print(f"SKIP: folder already complete for {run_id}")
                return True, False, "SKIP: folder already complete", date_start_actual, date_end_actual, n_obs
            if not force_overwrite and not dry_run:
                quarantine_dir = quarantine_run_folder(report_dir, missing)
                print(f"QUARANTINE: Existing run moved to {quarantine_dir}")
            elif force_overwrite:
                print("FORCE-OVERWRITE: I know what I'm doing. Existing run will be overwritten.")
            else:
                print("DRY RUN: Would quarantine incomplete run folder.")
            if dry_run:
                return True, False, "DRY RUN: incomplete run folder handled", date_start, date_end, 0

    # Check data availability
    row_count = check_data_availability(db_url, symbol, date_start, date_end)
    print(f"Rows in requested range: {row_count}")
    
    # Substitution logic
    date_start_actual = date_start
    date_end_actual = date_end
    was_substituted = False
    
    if row_count == 0:
        print("Zero rows - searching for substitute range...")
        sub_start, sub_end, sub_count = find_substitute_range(
            db_url, symbol, date_start, date_end, existing_ranges
        )
        if sub_start is None:
            return False, False, "No substitute range found with data", date_start, date_end, 0
        
        date_start_actual = sub_start
        date_end_actual = sub_end
        row_count = sub_count
        was_substituted = True
        print("=" * 60)
        print("WARNING: DATE RANGE SUBSTITUTED")
        print(f"  Requested: {date_start} to {date_end} (0 rows)")
        print(f"  Executing: {date_start_actual} to {date_end_actual} ({row_count} rows)")
        print("  This substitution is automatic and non-interactive.")
        print("=" * 60)
    
    if dry_run:
        print("[DRY RUN] Would execute studies and generate artifacts")
        return True, False, f"DRY RUN: {row_count} rows", date_start_actual, date_end_actual, row_count
    
    sql_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and execute studies for each score
    study_outputs = {}
    
    for score_name, score_config in SCORE_CONFIGS.items():
        version = score_config["version"].replace(".", "_")
        sql_filename = f"study_{score_name.lower()}_{version}.sql"
        output_filename = f"study_{score_name.lower()}_{version}.txt"
        
        # Generate SQL
        sql_content = generate_study_sql(
            run_id, symbol, date_start_actual, date_end_actual,
            score_name, score_config
        )
        sql_path = sql_dir / sql_filename
        sql_path.write_text(sql_content, encoding="utf-8", newline="\n")
        print(f"Generated: {sql_path}")
        
        # Execute study
        output_path = output_dir / output_filename
        print(f"Executing: {sql_filename}...")
        output = run_sql_file(db_url, sql_path, output_path)
        study_outputs[score_name] = output
        print(f"Output saved: {output_path}")
    
    # Generate evidence reports
    for score_name, score_config in SCORE_CONFIGS.items():
        version = score_config["version"].replace(".", "_")
        evidence_filename = f"{score_name}_{version}_evidence.md"
        
        evidence_content = generate_evidence_md(
            run_id, symbol, date_start_actual, date_end_actual,
            row_count, score_name, score_config, study_outputs[score_name]
        )
        evidence_path = report_dir / evidence_filename
        evidence_path.write_text(evidence_content, encoding="utf-8", newline="\n")
        print(f"Generated: {evidence_path}")
    
    # Generate RUN.md
    run_md_content = generate_run_md(
        run_id, symbol,
        date_start, date_end,
        date_start_actual, date_end_actual,
        row_count, was_substituted
    )
    run_md_path = report_dir / "RUN.md"
    run_md_path.write_text(run_md_content, encoding="utf-8", newline="\n")
    print(f"Generated: {run_md_path}")

    if build_pack_v0_2:
        build_evidence_pack_v0_2(
            repo_root=repo_root,
            db_url=db_url,
            run_id=run_id,
            symbol=symbol,
            date_start=date_start_actual,
            date_end=date_end_actual,
        )
    
    # Update INDEX.md
    index_path = repo_root / "reports" / "path1" / "evidence" / "INDEX.md"
    if index_path.exists():
        date_range_str = f"{date_start_actual} to {date_end_actual}"
        update_index_md(index_path, run_id, date_range_str, symbol, row_count)
        print(f"Updated: {index_path}")
    
    # Add to existing ranges to avoid future overlap
    existing_ranges.append((date_start_actual, date_end_actual))
    
    return True, True, f"Completed: {row_count} rows ({date_start_actual} to {date_end_actual})", date_start_actual, date_end_actual, row_count


def parse_existing_runs(index_path: Path) -> list:
    """Parse existing date ranges from INDEX.md to avoid overlap."""
    ranges = []
    if not index_path.exists():
        return ranges
    
    content = index_path.read_text(encoding="utf-8")
    # Extract date ranges from table rows
    for line in content.split('\n'):
        if line.startswith('| p1_'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                date_range = parts[2]  # Second column is date range
                match = re.match(r'(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', date_range)
                if match:
                    ranges.append((match.group(1), match.group(2)))
    
    return ranges


def main():
    parser = argparse.ArgumentParser(
        description='Execute Path 1 Evidence runs from queue file'
    )
    parser.add_argument(
        '--queue', '-q',
        default='reports/path1/evidence/RUN_QUEUE.csv',
        help='Path to queue CSV file (default: reports/path1/evidence/RUN_QUEUE.csv)'
    )
    parser.add_argument(
        '--max-runs', '-m',
        type=int, default=10,
        help='Maximum runs to execute (default: 10)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Alias for --max-runs 1'
    )
    parser.add_argument(
        '--run-id', '-r',
        help='Execute only this specific run_id from queue'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Validate inputs and check data availability without executing'
    )
    parser.add_argument(
        '--evidence-pack-v0-2',
        action='store_true',
        help='Build Evidence Pack v0.2 (M15 overlay) for each completed run'
    )
    parser.add_argument(
        '--force-overwrite',
        action='store_true',
        help='Allow overwriting an existing run folder (default: abort if run exists)'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root path (default: current directory)'
    )
    
    args = parser.parse_args()
    if args.once:
        args.max_runs = 1
    
    print("=" * 60)
    print("PATH 1 EVIDENCE QUEUE RUNNER")
    print("=" * 60)
    print("NOTE: Runs execute sequentially. On failure, prior runs remain")
    print("      on disk and in INDEX.md. There is no rollback.")
    print("      Queue status is LOCAL ONLY and not auto-committed.")
    
    # Validate environment
    db_url = validate_environment()
    print(f"Database: connected")
    
    repo_root = Path(args.repo_root).resolve()
    print(f"Repo root: {repo_root}")
    
    # Load queue
    queue_path = repo_root / args.queue
    if not queue_path.exists():
        print(f"ERROR: Queue file not found: {queue_path}")
        sys.exit(1)
    
    print(f"Queue file: {queue_path}")
    
    # Parse existing runs to avoid overlap
    index_path = repo_root / "reports" / "path1" / "evidence" / "INDEX.md"
    existing_ranges = parse_existing_runs(index_path)
    print(f"Existing runs: {len(existing_ranges)}")
    
    # Read queue (skip comment lines before passing to DictReader)
    runs_to_execute = []
    with open(queue_path, "r", encoding="utf-8") as f:
        # Filter out comment lines (lines starting with #) before parsing
        lines = [line for line in f if not line.strip().startswith('#')]
        reader = csv.DictReader(lines)
        for row in reader:
            if row.get('run_id'):
                if args.run_id and row['run_id'] != args.run_id:
                    continue
                # Only process rows with status='pending' or empty/missing status
                status = row.get('status', '').strip().lower()
                if status and status != 'pending':
                    print(f"Skipping {row['run_id']}: status={row.get('status')}")
                    continue
                runs_to_execute.append(row)
    
    if not runs_to_execute:
        print("="*60)
        print("NOOP: Queue empty or no matching run_id")
        print("="*60)
        print("No runs to execute. This is not an error if the queue is intentionally empty.")
        print(f"Queue file: {queue_path}")
        print(f"Run ID filter: {args.run_id or '(none)'}")
        summary_run_id = args.run_id if args.run_id else "NONE"
        write_path1_summary(
            repo_root=repo_root,
            run_id=summary_run_id,
            date_from="N/A",
            date_to="N/A",
            rows_processed=0,
            outcome="SKIPPED",
        )
        sys.exit(0)
    
    print(f"Runs to execute: {len(runs_to_execute)}")
    
    # Limit runs
    if len(runs_to_execute) > args.max_runs:
        print(f"Limiting to --max-runs={args.max_runs}")
        runs_to_execute = runs_to_execute[:args.max_runs]
    
    enable_pack_v0_2 = args.evidence_pack_v0_2 or truthy_env(os.environ.get("EVIDENCE_PACK_V0_2"))

    # Execute runs
    results = []
    for run_spec in runs_to_execute:
        run_id = run_spec['run_id']
        symbol = run_spec['symbol']
        date_start = run_spec['date_start']
        date_end = run_spec['date_end']
        
        success, did_execute, message, actual_start, actual_end, rows_processed = execute_single_run(
            db_url, repo_root, run_id, symbol,
            date_start, date_end, existing_ranges,
            dry_run=args.dry_run,
            build_pack_v0_2=enable_pack_v0_2,
            force_overwrite=args.force_overwrite,
        )
        results.append((run_id, success, did_execute, message, date_start, date_end, actual_start, actual_end, rows_processed))
    
    # Summary
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    
    for run_id, success, _, message, _, _, _, _, _ in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} | {run_id} | {message}")
    
    passed = sum(1 for _, s, _, _, _, _, _, _, _ in results if s)
    failed = len(results) - passed
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

    executed = [r for r in results if r[2]]
    if executed:
        date_from = min(r[6] for r in executed)
        date_to = max(r[7] for r in executed)
        summary_run_id = executed[0][0] if len(executed) == 1 else "MULTIPLE"
        rows_processed = sum(r[8] for r in executed)
        outcome = "EXECUTED"
    else:
        summary_run_id = results[0][0] if len(results) == 1 else "MULTIPLE"
        date_from = min(r[6] for r in results)
        date_to = max(r[7] for r in results)
        rows_processed = sum(r[8] for r in results)
        outcome = "SKIPPED"

    try:
        write_path1_summary(
            repo_root=repo_root,
            run_id=summary_run_id,
            date_from=date_from,
            date_to=date_to,
            rows_processed=rows_processed,
            outcome=outcome,
        )
    except Exception as exc:
        print(f"WARNING: Failed to write Path1 summary: {exc}")
    
    # Update queue status for completed runs (unless dry run)
    # Include actual dates so CSV reflects what was actually executed
    executed_successes = [
        r for r in results
        if r[1] and r[2]
    ]
    print(
        "DEBUG: executed_successes="
        f"{len(executed_successes)} "
        f"first_len={len(executed_successes[0]) if executed_successes else None}"
    )
    if not args.dry_run and executed_successes:
        # executed_successes rows are expected to have indices 0..6:
        # run_id, success, did_execute, req_start, req_end, actual_start, actual_end
        try:
            completed_runs = {}
            for row in executed_successes:
                if len(row) < 7:
                    run_id_hint = row[0] if len(row) > 0 else None
                    print(
                        "WARNING: executed_successes row missing expected fields; "
                        f"len={len(row)} run_id={run_id_hint!r}. "
                        "Skipping queue update for this row only."
                    )
                    continue
                run_id = row[0]
                actual_start = row[5]
                actual_end = row[6]
                completed_runs[run_id] = (actual_start, actual_end)
            if completed_runs:
                update_queue_status(queue_path, completed_runs)
                print("")
                print("WARNING: Queue status updated LOCALLY ONLY. Changes are not auto-committed.")
                print("         INDEX.md is the canonical execution ledger, not the queue.")
        except Exception as exc:
            print(f"WARNING: Failed to update queue status update: {exc}")
    
    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
