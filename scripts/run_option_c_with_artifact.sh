#!/usr/bin/env bash
# Wrapper for run_option_c.sh that creates run artifacts via run_artifact_cli.py
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Determine run_id (matches logic in run_option_c.sh)
run_id="${1:-}"
if [[ -z "$run_id" ]]; then
  if [[ "${GITHUB_ACTIONS:-}" == "true" || "${CI:-}" == "true" ]]; then
    echo "--run-id is required in CI." >&2
    exit 1
  fi
  run_id="local_$(date -u +%Y%m%dT%H%M%SZ)"
fi

# Use CLI wrapper to start, run, and finish with artifact capture
python src/ovc_ops/run_artifact_cli.py \
  --pipeline-id "C-Eval" \
  --pipeline-version "0.1.0" \
  --required-env "DATABASE_URL" \
  --input "neon_view:derived.ovc_block_features_v0_1" \
  --output "neon_table:derived.ovc_outcomes_v0_1" \
  --output "file:reports/spotchecks_${run_id}.txt" \
  --output "file:reports/run_report_${run_id}.json" \
  -- \
  bash scripts/run_option_c.sh --run-id "$run_id" "${@:2}"
