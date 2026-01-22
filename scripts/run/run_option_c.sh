#!/usr/bin/env bash
set -euo pipefail

trap 'echo "Run failed." >&2; exit 2' ERR

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# Anchor SQL paths to repo root so psql never depends on the caller's CWD.
if [[ "$(basename "$script_dir")" == "run" ]]; then
  repo_root="$(cd "$script_dir/../.." && pwd -P)"
elif [[ "$(basename "$script_dir")" == "scripts" ]]; then
  repo_root="$(cd "$script_dir/.." && pwd -P)"
else
  repo_root="$script_dir"
fi
sql_file="$repo_root/sql/option_c_v0_1.sql"
cd "$repo_root"

usage() {
  cat <<'EOF'
Usage: scripts/run_option_c.sh [--run-id <id>] [--strict] [--spotchecks-only]

  --run-id <id>     Optional locally; required in CI. Defaults to UTC timestamp.
  --strict          Treat WARN as FAIL.
  --spotchecks-only Skip apply; run spotchecks + report only.
EOF
}

run_id=""
strict=false
spotchecks_only=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      if [[ -z "${2:-}" ]]; then
        echo "--run-id requires a value" >&2
        exit 2
      fi
      run_id="$2"
      shift 2
      ;;
    --strict)
      strict=true
      shift
      ;;
    --spotchecks-only)
      spotchecks_only=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$run_id" ]]; then
  if [[ "${GITHUB_ACTIONS:-}" == "true" || "${CI:-}" == "true" ]]; then
    echo "--run-id is required in CI." >&2
    exit 1
  fi
  run_id="local_$(date -u +%Y%m%dT%H%M%SZ)"
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set."
  echo "Set it in this shell, for example:"
  echo "  export DATABASE_URL='postgresql://user:pass@host/db'"
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found in PATH" >&2
  exit 127
fi

if [[ ! -f "$sql_file" ]]; then
  echo "Missing SQL file: $sql_file" >&2
  exit 2
fi

spotcheck_contains() {
  local pattern="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -q "$pattern" "$file"
  else
    grep -q "$pattern" "$file"
  fi
}

eval_version="v0.1"
formula_hash="6b328b4962b19a53e3a1c1f03f41d705"
horizon_spec="K=1,2,6,12"
notes="option_d_run"

reports_dir="reports"
mkdir -p "$reports_dir"

started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ "$spotchecks_only" != "true" ]]; then
  if ! psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
    -v run_id="$run_id" \
    -c "select :'run_id' as _run_id_check;"; then
    echo "psql variable substitution failed - aborting Option C run" >&2
    exit 2
  fi
  echo "Applying Option C SQL..."
  pwd
  echo "SQL_FILE=$sql_file"
  ls -la "$sql_file" || true
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
    -v run_id="$run_id" \
    -v eval_version="$eval_version" \
    -v formula_hash="$formula_hash" \
    -v horizon_spec="$horizon_spec" \
    -f "$sql_file"
fi

echo "Registering eval run..."
psql -d "$DATABASE_URL" \
  --set=ON_ERROR_STOP=1 \
  --set=run_id="$run_id" \
  --set=eval_version="$eval_version" \
  --set=formula_hash="$formula_hash" \
  --set=horizon_spec="$horizon_spec" \
  --set=notes="$notes" \
  -f - <<'SQL'
insert into derived.eval_runs (run_id, eval_version, formula_hash, horizon_spec, computed_at, notes)
values (:'run_id', :'eval_version', :'formula_hash', :'horizon_spec', now(), :'notes')
on conflict (run_id) do update
set eval_version = excluded.eval_version,
    formula_hash = excluded.formula_hash,
    horizon_spec = excluded.horizon_spec,
    computed_at = excluded.computed_at,
    notes = excluded.notes;
SQL

echo "Running Option C spotchecks..."
spotchecks_file="$reports_dir/spotchecks_${run_id}.txt"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f sql/option_c_spotchecks.sql | tee "$spotchecks_file"

spotcheck_status="PASS"
spotcheck_reason="All spotchecks PASS."
if spotcheck_contains "FAIL" "$spotchecks_file"; then
  spotcheck_status="FAIL"
  spotcheck_reason="Spotcheck output contains FAIL."
elif spotcheck_contains "WARN" "$spotchecks_file"; then
  spotcheck_status="WARN"
  spotcheck_reason="Spotcheck output contains WARN."
fi

finished_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "Generating run report..."
report_json="$reports_dir/run_report_${run_id}.json"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -v run_id="$run_id" \
  -v started_at="$started_at" \
  -v finished_at="$finished_at" \
  -v spotcheck_status="$spotcheck_status" \
  -v spotcheck_reason="$spotcheck_reason" \
  -v strict="$strict" \
  -t -A -f sql/option_c_run_report.sql > "$report_json"

report_md="$reports_dir/run_report_${run_id}.md"
cat > "$report_md" <<EOF
# Option C Run Report

- run_id: $run_id
- status: $spotcheck_status
- started_at: $started_at
- finished_at: $finished_at
- eval_version: $eval_version
- formula_hash: $formula_hash
- spotchecks: $spotcheck_reason
EOF

if [[ "$spotcheck_status" == "FAIL" ]]; then
  exit 2
fi
if [[ "$spotcheck_status" == "WARN" ]]; then
  if [[ "$strict" == "true" ]]; then
    exit 2
  fi
  exit 1
fi
exit 0
