#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

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

echo "Applying Option C SQL..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f sql/option_c_v0_1.sql

echo "Running Option C spotchecks..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f sql/option_c_spotchecks.sql

echo ""
echo "Summary: If every spotcheck row shows status=PASS, treat this run as PASS."
echo "Summary: If any row shows status=WARN, investigate before proceeding."