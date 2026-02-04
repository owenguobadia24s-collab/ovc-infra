import argparse
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROWCOUNT_ENV = "PIPELINE_STATUS_ROWCOUNT"


def load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    try:
        content = env_path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def file_exists(path: Path) -> bool:
    return path.exists()


def contains_text(path: Path, needle: str) -> bool:
    return needle in read_text(path)


def find_sql_files_with_text(needle: str) -> list[str]:
    sql_root = REPO_ROOT / "sql"
    if not sql_root.exists():
        return []
    matches: list[str] = []
    for path in sql_root.rglob("*.sql"):
        if needle in read_text(path):
            matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(matches)


@dataclass
class DbState:
    available: bool
    error: str | None
    conn: object | None


def connect_db(dsn: str | None) -> DbState:
    if not dsn:
        return DbState(available=False, error="missing DSN", conn=None)
    try:
        import psycopg2  # type: ignore
    except ImportError as exc:
        return DbState(available=False, error=f"psycopg2 missing: {exc}", conn=None)
    try:
        conn = psycopg2.connect(dsn)
        return DbState(available=True, error=None, conn=conn)
    except Exception as exc:  # noqa: BLE001
        return DbState(available=False, error=str(exc), conn=None)


def table_exists(conn, qualified_name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("select to_regclass(%s);", (qualified_name,))
        (regclass_name,) = cur.fetchone()
        return regclass_name is not None


def table_count(conn, qualified_name: str) -> int | None:
    schema, table = qualified_name.split(".", 1)
    with conn.cursor() as cur:
        cur.execute(f"select count(*) from {schema}.{table};")
        (count,) = cur.fetchone()
        return int(count)


@dataclass
class CheckSection:
    name: str
    status: str
    reason: str


@dataclass
class PipelineReport:
    key: str
    status: str
    summary: str
    checks: list[CheckSection]
    paths: list[str]


def build_section(name: str, fatal: list[str], warn: list[str], ok_reason: str = "ok") -> CheckSection:
    if fatal:
        return CheckSection(name=name, status="FAIL", reason="; ".join(fatal))
    if warn:
        return CheckSection(name=name, status="PARTIAL", reason="; ".join(warn))
    return CheckSection(name=name, status="PASS", reason=ok_reason)


def env_check(env: dict, required_keys: list[str], allow_any: bool = False) -> CheckSection:
    if allow_any:
        if any(env.get(key) for key in required_keys):
            return CheckSection(name="env", status="PASS", reason="ok")
        return CheckSection(
            name="env",
            status="UNKNOWN",
            reason=f"missing env: one of {', '.join(required_keys)}",
        )
    missing = [key for key in required_keys if not env.get(key)]
    if missing:
        return CheckSection(name="env", status="UNKNOWN", reason=f"missing env: {', '.join(missing)}")
    return CheckSection(name="env", status="PASS", reason="ok")


def db_check(
    db: DbState,
    required_tables: list[str],
    optional_tables: list[str],
    rowcount_tables: list[str],
    rowcount_enabled: bool,
) -> CheckSection:
    if not db.available or not db.conn:
        reason = db.error or "db check skipped"
        return CheckSection(name="db", status="UNKNOWN", reason=f"db check skipped: {reason}")

    missing_required: list[str] = []
    missing_optional: list[str] = []
    present_tables: set[str] = set()

    for table in required_tables:
        if table_exists(db.conn, table):
            present_tables.add(table)
        else:
            missing_required.append(table)
    for table in optional_tables:
        if table_exists(db.conn, table):
            present_tables.add(table)
        else:
            missing_optional.append(table)

    status = "PASS"
    reasons: list[str] = []
    if missing_required:
        status = "FAIL"
        reasons.append(f"missing required: {', '.join(missing_required)}")
    elif missing_optional:
        status = "PARTIAL"
        reasons.append(f"missing optional: {', '.join(missing_optional)}")

    if rowcount_enabled:
        counts: list[str] = []
        for table in rowcount_tables:
            if table in present_tables:
                count = table_count(db.conn, table)
                counts.append(f"{table}={count}")
        if counts:
            reasons.append("row_count: " + ", ".join(counts))
    else:
        reasons.append(f"row_count: skipped (set {ROWCOUNT_ENV}=1)")

    reason = "; ".join(reasons) if reasons else "ok"
    return CheckSection(name="db", status=status, reason=reason)


def api_check(status: str, reason: str) -> CheckSection:
    return CheckSection(name="api", status=status, reason=reason)


def finalize_report(
    key: str,
    checks: list[CheckSection],
    paths: list[str],
    ignore_unknown: bool,
) -> PipelineReport:
    repo_status = next(check.status for check in checks if check.name == "repo")
    db_status = next(check.status for check in checks if check.name == "db")
    if repo_status == "FAIL" or db_status == "FAIL":
        overall = "FAIL"
    else:
        non_pass = {"PARTIAL"}
        if not ignore_unknown:
            non_pass.add("UNKNOWN")
        overall = "PARTIAL" if any(check.status in non_pass for check in checks) else "PASS"

    summary = " ".join(f"{check.name}={check.status}" for check in checks)
    return PipelineReport(
        key=key,
        status=overall,
        summary=summary,
        checks=checks,
        paths=sorted(dict.fromkeys(paths)),
    )


def check_p1(env: dict, db: DbState, rowcount_enabled: bool, ignore_unknown: bool) -> PipelineReport:
    worker_rel = "infra/ovc-webhook/src/index.ts"
    wrangler_rel = "infra/ovc-webhook/wrangler.jsonc"
    test_rel = "infra/ovc-webhook/test/index.spec.ts"

    worker_path = REPO_ROOT / worker_rel
    wrangler_path = REPO_ROOT / wrangler_rel
    test_path = REPO_ROOT / test_rel

    paths = [worker_rel, wrangler_rel, test_rel]

    repo_fail: list[str] = []
    repo_warn: list[str] = []

    if not file_exists(worker_path):
        repo_fail.append("worker missing")
    if not file_exists(wrangler_path):
        repo_fail.append("wrangler config missing")
    if file_exists(wrangler_path) and not contains_text(wrangler_path, "\"RAW_EVENTS\""):
        repo_fail.append("R2 binding RAW_EVENTS missing")

    worker_src = read_text(worker_path)
    if worker_src and "ovc.ovc_blocks_v01_1_min" not in worker_src:
        repo_fail.append("Neon upsert target ovc.ovc_blocks_v01_1_min not found")
    if worker_src and "ovc.ovc_run_reports_v01" not in worker_src:
        repo_warn.append("run reports insert not detected")
    if not file_exists(test_path):
        repo_warn.append("tests missing")

    run_report_sql = find_sql_files_with_text("ovc_run_reports_v01")
    if run_report_sql:
        paths.extend(run_report_sql)
    else:
        repo_warn.append("run report schema SQL not found")

    repo_section = build_section("repo", repo_fail, repo_warn)
    env_section = env_check(env, ["DATABASE_URL", "OVC_TOKEN"])
    db_section = db_check(
        db,
        required_tables=["ovc.ovc_blocks_v01_1_min"],
        optional_tables=["ovc.ovc_run_reports_v01"],
        rowcount_tables=["ovc.ovc_blocks_v01_1_min"],
        rowcount_enabled=rowcount_enabled,
    )
    api_section = api_check("N/A", "not applicable")

    return finalize_report(
        key="P1_live_capture_to_facts",
        checks=[repo_section, env_section, db_section, api_section],
        paths=paths,
        ignore_unknown=ignore_unknown,
    )


def check_p2(env: dict, db: DbState, rowcount_enabled: bool, ignore_unknown: bool) -> PipelineReport:
    backfill_rel = "src/backfill_oanda_2h_checkpointed.py"
    workflow_rel = ".github/workflows/backfill.yml"
    export_rel = "scripts/oanda_export_2h_day.py"

    backfill_path = REPO_ROOT / backfill_rel
    workflow_path = REPO_ROOT / workflow_rel
    export_path = REPO_ROOT / export_rel

    paths = [backfill_rel, workflow_rel, export_rel]

    repo_fail: list[str] = []
    repo_warn: list[str] = []

    if not file_exists(backfill_path):
        repo_fail.append("backfill script missing")
    if not file_exists(workflow_path):
        repo_warn.append("workflow missing")
    if not file_exists(export_path):
        repo_warn.append("oanda export helper missing")

    backfill_src = read_text(backfill_path)
    if backfill_src and "ovc.ovc_blocks_v01_1_min" not in backfill_src:
        repo_warn.append("backfill targets ovc_blocks_v01 (not ovc.ovc_blocks_v01_1_min)")

    repo_section = build_section("repo", repo_fail, repo_warn)
    env_section = env_check(env, ["NEON_DSN", "OANDA_API_TOKEN", "OANDA_ENV"])
    db_section = db_check(
        db,
        required_tables=["ovc.ovc_blocks_v01_1_min"],
        optional_tables=[],
        rowcount_tables=["ovc.ovc_blocks_v01_1_min"],
        rowcount_enabled=rowcount_enabled,
    )
    api_section = api_check("SKIPPED", "detect mode: external API not called")

    return finalize_report(
        key="P2_history_backfill_to_facts",
        checks=[repo_section, env_section, db_section, api_section],
        paths=paths,
        ignore_unknown=ignore_unknown,
    )


def check_p3(
    env: dict,
    db: DbState,
    rowcount_enabled: bool,
    strict: bool,
    ignore_unknown: bool,
) -> PipelineReport:
    derived_rel = "sql/derived_v0_1.sql"
    outcomes_rel = "sql/option_c_v0_1.sql"
    runner_rel = "scripts/run_option_c.sh"

    derived_path = REPO_ROOT / derived_rel
    outcomes_path = REPO_ROOT / outcomes_rel
    runner_path = REPO_ROOT / runner_rel

    paths = [derived_rel, outcomes_rel, runner_rel]

    repo_fail: list[str] = []
    repo_warn: list[str] = []

    if not file_exists(derived_path):
        repo_fail.append("derived SQL missing")
    if not file_exists(outcomes_path):
        repo_fail.append("outcomes SQL missing")
    if not file_exists(runner_path):
        repo_warn.append("runner script missing")

    repo_section = build_section("repo", repo_fail, repo_warn)
    env_section = env_check(env, ["DATABASE_URL"])
    required_tables = []
    optional_tables = ["derived.ovc_block_features_v0_1", "derived.ovc_outcomes_v0_1"]
    if strict:
        required_tables = optional_tables
        optional_tables = []

    db_section = db_check(
        db,
        required_tables=required_tables,
        optional_tables=optional_tables,
        rowcount_tables=[],
        rowcount_enabled=rowcount_enabled,
    )
    api_section = api_check("N/A", "not applicable")

    return finalize_report(
        key="P3_facts_to_derived",
        checks=[repo_section, env_section, db_section, api_section],
        paths=paths,
        ignore_unknown=ignore_unknown,
    )


def check_p4(env: dict, db: DbState, rowcount_enabled: bool, ignore_unknown: bool) -> PipelineReport:
    entry_rel = "src/validate_day.py"
    range_rel = "src/validate_range.py"
    schema_rel = "sql/qa_schema.sql"
    pack_rel = "sql/qa_validation_pack.sql"
    doc_rel = "docs/tape_validation_harness.md"

    entry_path = REPO_ROOT / entry_rel
    range_path = REPO_ROOT / range_rel
    schema_path = REPO_ROOT / schema_rel
    pack_path = REPO_ROOT / pack_rel
    doc_path = REPO_ROOT / doc_rel

    paths = [entry_rel, range_rel, schema_rel, pack_rel, doc_rel]

    repo_fail: list[str] = []
    repo_warn: list[str] = []

    if not file_exists(entry_path):
        repo_fail.append("validate_day.py missing")
    if not file_exists(range_path):
        repo_warn.append("validate_range.py missing")
    if not file_exists(schema_path):
        repo_fail.append("qa schema SQL missing")
    if not file_exists(pack_path):
        repo_fail.append("qa validation pack SQL missing")
    if not file_exists(doc_path):
        repo_warn.append("harness doc missing")

    repo_section = build_section("repo", repo_fail, repo_warn)
    env_section = env_check(env, ["NEON_DSN", "DATABASE_URL"], allow_any=True)
    db_section = db_check(
        db,
        required_tables=[
            "ovc_qa.validation_run",
            "ovc_qa.expected_blocks",
            "ovc_qa.tv_ohlc_2h",
            "ovc_qa.ohlc_mismatch",
        ],
        optional_tables=[],
        rowcount_tables=[],
        rowcount_enabled=rowcount_enabled,
    )
    api_section = api_check("N/A", "not applicable")

    return finalize_report(
        key="P4_facts_plus_tape_to_validation",
        checks=[repo_section, env_section, db_section, api_section],
        paths=paths,
        ignore_unknown=ignore_unknown,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="OVC pipeline status harness (v0.1).")
    parser.add_argument(
        "--mode",
        default="detect",
        choices=("detect", "test"),
        help="detect=read-only checks (default); test=read-only extended checks",
    )
    parser.add_argument("--symbol", default="GBPUSD")
    parser.add_argument(
        "--date-ny",
        dest="date_ny",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="NY date for optional row count context (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require derived views for P3 (otherwise treated as optional).",
    )
    parser.add_argument(
        "--ignore-unknown",
        action="store_true",
        help="Do not downgrade overall status for UNKNOWN env/db checks.",
    )
    args = parser.parse_args()

    load_env()
    env = dict(os.environ)
    rowcount_enabled = env.get(ROWCOUNT_ENV, "").strip() == "1"
    dsn = env.get("NEON_DSN") or env.get("DATABASE_URL")
    db = connect_db(dsn)

    reports = [
        check_p1(env, db, rowcount_enabled, args.ignore_unknown),
        check_p2(env, db, rowcount_enabled, args.ignore_unknown),
        check_p3(env, db, rowcount_enabled, args.strict, args.ignore_unknown),
        check_p4(env, db, rowcount_enabled, args.ignore_unknown),
    ]

    if db.conn:
        db.conn.close()

    print("PIPELINE_STATUS v0.1")
    for report in reports:
        path_str = ", ".join(report.paths)
        print(f"{report.key}: {report.status} - {report.summary} | {path_str}")
        for check in report.checks:
            print(f"  {check.name}: {check.status} - {check.reason}")

    statuses = {report.status for report in reports}
    if "FAIL" in statuses:
        return 2
    if "PARTIAL" in statuses:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
