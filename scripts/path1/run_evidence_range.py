import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple


SCORE_CONFIGS = {
    "DIS": {
        "version": "v1.1",
        "column": "dis_v1_1_raw",
        "view": "derived.v_path1_evidence_dis_v1_1",
        "status": "FROZEN",
    },
    "RES": {
        "version": "v1.0",
        "column": "res_v1_0_raw",
        "view": "derived.v_path1_evidence_res_v1_0",
        "status": "FROZEN",
    },
    "LID": {
        "version": "v1.0",
        "column": "lid_v1_0_raw",
        "view": "derived.v_path1_evidence_lid_v1_0",
        "status": "FROZEN",
    },
}

INVARIANTS_TEXT = (
    "> **Association ≠ Predictability.** Co-occurrence patterns do not imply scores predict outcomes.  \n"
    "> **Scores are descriptive and frozen.** They describe structural characteristics, not signals.  \n"
    "> **Summaries are non-interpretive.** They describe what occurred, not what will occur.\n"
)

TEMPLATE_VERSION = "evidence_run_template_v2"


@dataclass
class DateRange:
    start: str
    end: str
    length_days: int


def validate_date_format(date_str: str, field_name: str) -> None:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValueError(
            f"{field_name} has invalid format: '{date_str}' (expected YYYY-MM-DD)"
        )


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def normalize_date_range(
    start_date: str | None, end_date: str | None, length_days: int | None
) -> DateRange:
    if start_date and end_date:
        validate_date_format(start_date, "start_date")
        validate_date_format(end_date, "end_date")
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
        if start_dt > end_dt:
            raise ValueError("start_date must be <= end_date")
        length = (end_dt.date() - start_dt.date()).days + 1
        return DateRange(start=start_date, end=end_date, length_days=length)

    if end_date and length_days:
        validate_date_format(end_date, "end_date")
        if length_days < 1:
            raise ValueError("length_days must be >= 1")
        end_dt = parse_date(end_date)
        start_dt = end_dt - timedelta(days=length_days - 1)
        return DateRange(
            start=start_dt.strftime("%Y-%m-%d"),
            end=end_date,
            length_days=length_days,
        )

    raise ValueError(
        "Provide either --start-date and --end-date, or --end-date and --length-days"
    )


def validate_environment() -> str:
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DSN")
    if not db_url:
        raise RuntimeError("DATABASE_URL or NEON_DSN environment variable not set")
    try:
        subprocess.run(["psql", "--version"], capture_output=True, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("psql command not found") from exc
    return db_url


def git_sha(repo_root: Path) -> str:
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha.strip()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def compute_run_id(
    symbol: str, start_date: str, end_date: str, length_days: int, git_sha_value: str
) -> str:
    created = datetime.now(UTC).strftime("%Y%m%d")
    end_compact = end_date.replace("-", "")
    template_seed = f"{symbol}|{start_date}|{end_date}|{git_sha_value}|{TEMPLATE_VERSION}"
    short_hash = hashlib.sha256(template_seed.encode("utf-8")).hexdigest()[:8]
    return f"p1_{created}_{symbol}_{end_compact}_len{length_days}d_{short_hash}"


def run_sql_query(db_url: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", db_url, "-t", "-A", "-c", sql],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def run_sql_file(db_url: str, sql_file: Path, output_file: Path) -> None:
    result = subprocess.run(
        ["psql", db_url, "-f", str(sql_file)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    output_file.write_text(output, encoding="utf-8", newline="\n")
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, result.args, result.stdout, result.stderr
        )


def generate_study_sql(
    run_id: str, symbol: str, date_start: str, date_end: str, score_name: str, score_config: Dict
) -> str:
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


def generate_evidence_md(
    run_id: str,
    symbol: str,
    date_start: str,
    date_end: str,
    n_obs: int,
    score_name: str,
    score_config: Dict,
) -> str:
    version = score_config["version"]
    version_str = f"{score_name}-{version}"
    view = score_config["view"]
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


def render_run_md(
    template_text: str,
    run_id: str,
    date_start: str,
    date_end: str,
    symbol: str,
    generated_at: str,
    n_obs: int,
    git_sha_value: str,
) -> str:
    rendered = template_text
    rendered = rendered.replace("{YYYYMMDD}-{SEQ}", run_id)
    rendered = rendered.replace("{YYYY-MM-DD}", date_start, 1)
    rendered = rendered.replace("{YYYY-MM-DD}", date_end, 1)
    rendered = rendered.replace("{SYM1, SYM2, ...}", symbol)
    rendered = rendered.replace("{ISO8601 timestamp}", generated_at)

    if "| `n_observations` |" not in rendered:
        rendered = rendered.replace(
            "| `generated_at` |",
            "| `generated_at` |",
        )
    rendered = rendered.replace("{N_OBSERVATIONS}", str(n_obs))
    rendered = rendered.replace("{GIT_SHA}", git_sha_value)

    artifacts_section = f"""

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
"""

    return rendered.strip() + artifacts_section


def append_index_entry(
    index_path: Path, run_id: str, date_range: str, symbol: str, n_obs: int
) -> bool:
    content = index_path.read_text(encoding="utf-8")
    if f"| {run_id} |" in content:
        raise RuntimeError(f"INDEX.md already contains run_id {run_id}")

    lines = content.split("\n")
    insert_idx = None
    in_table = False

    for i, line in enumerate(lines):
        if "| Run ID |" in line:
            in_table = True
            continue
        if in_table:
            if line.startswith("|"):
                continue
            insert_idx = i
            break

    if insert_idx is None:
        raise RuntimeError("Could not locate Completed Runs table in INDEX.md")

    new_row = (
        f"| {run_id} | {date_range} | {symbol} | {n_obs} | COMPLETE | "
        f"[RUN.md](runs/{run_id}/RUN.md) |"
    )
    lines.insert(insert_idx, new_row)
    index_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Path 1 evidence studies over a date range")
    parser.add_argument("--symbol", default="GBPUSD", help="Symbol to analyze")
    parser.add_argument("--start-date", dest="start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", dest="end_date", help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--length-days", dest="length_days", type=int, help="Length in days (inclusive)"
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    evidence_root = repo_root / "reports" / "path1" / "evidence"
    if not evidence_root.exists():
        print(f"ERROR: Evidence root not found: {evidence_root}")
        return 1

    try:
        date_range = normalize_date_range(args.start_date, args.end_date, args.length_days)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    try:
        db_url = validate_environment()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    git_sha_value = git_sha(repo_root)
    run_id = compute_run_id(
        args.symbol, date_range.start, date_range.end, date_range.length_days, git_sha_value
    )

    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("=" * 60)
    print("PATH 1 EVIDENCE RANGE RUNNER")
    print("=" * 60)
    print(f"Symbol: {args.symbol}")
    print(f"Date range: {date_range.start} to {date_range.end}")
    print(f"Length days: {date_range.length_days}")
    print(f"Run ID: {run_id}")
    print(f"Git SHA: {git_sha_value}")
    print("=" * 60)

    sql_dir = repo_root / "sql" / "path1" / "evidence" / "runs" / run_id
    report_dir = repo_root / "reports" / "path1" / "evidence" / "runs" / run_id
    output_dir = report_dir / "outputs"

    if report_dir.exists():
        print(f"ERROR: Run folder already exists: {report_dir}")
        return 1

    sql_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir(parents=True, exist_ok=False)

    if not report_dir.exists():
        print("ERROR: Run folder was not created")
        return 1

    try:
        count_sql = (
            "SELECT COUNT(*) FROM derived.v_path1_evidence_dis_v1_1 "
            f"WHERE sym = '{args.symbol}' "
            f"AND to_timestamp(bar_close_ms/1000)::date BETWEEN '{date_range.start}' "
            f"AND '{date_range.end}';"
        )
        n_obs = int(run_sql_query(db_url, count_sql) or "0")
    except Exception as exc:
        print(f"ERROR: Failed to count rows in range: {exc}")
        return 1

    for score_name, score_config in SCORE_CONFIGS.items():
        version = score_config["version"].replace(".", "_")
        sql_filename = f"study_{score_name.lower()}_{version}.sql"
        output_filename = f"study_{score_name.lower()}_{version}.txt"

        sql_content = generate_study_sql(
            run_id, args.symbol, date_range.start, date_range.end, score_name, score_config
        )
        sql_path = sql_dir / sql_filename
        sql_path.write_text(sql_content, encoding="utf-8", newline="\n")

        output_path = output_dir / output_filename
        try:
            run_sql_file(db_url, sql_path, output_path)
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: psql failed for {sql_filename} (exit {exc.returncode})")
            return 1

        evidence_md = generate_evidence_md(
            run_id,
            args.symbol,
            date_range.start,
            date_range.end,
            n_obs,
            score_name,
            score_config,
        )
        evidence_path = report_dir / f"{score_name}_{version}_evidence.md"
        evidence_path.write_text(evidence_md, encoding="utf-8", newline="\n")

    template_path = evidence_root / "EVIDENCE_RUN_TEMPLATE.md"
    template_text = template_path.read_text(encoding="utf-8")
    run_md = render_run_md(
        template_text,
        run_id,
        date_range.start,
        date_range.end,
        args.symbol,
        generated_at,
        n_obs,
        git_sha_value,
    )
    run_md_path = report_dir / "RUN.md"
    run_md_path.write_text(run_md, encoding="utf-8", newline="\n")

    meta_path = report_dir / "meta.json"
    meta_payload = {
        "run_id": run_id,
        "symbol": args.symbol,
        "start_date": date_range.start,
        "end_date": date_range.end,
        "length_days": date_range.length_days,
        "git_sha": git_sha_value,
        "generated_at": generated_at,
    }
    meta_path.write_text(
        json.dumps(meta_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    index_path = evidence_root / "INDEX.md"
    try:
        appended = append_index_entry(
            index_path,
            run_id,
            f"{date_range.start} to {date_range.end}",
            args.symbol,
            n_obs,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if not appended:
        print("ERROR: INDEX.md was not appended")
        return 1

    print(f"RUN_ID={run_id}")
    print(f"RUN_DIR={report_dir}")
    print(f"SQL_DIR={sql_dir}")
    print(f"OUTPUT_DIR={output_dir}")
    print(f"META_JSON={meta_path}")
    print("Run complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())