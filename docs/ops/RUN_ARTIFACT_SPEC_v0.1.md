# Run Artifact Specification v0.1

## Purpose

Every OVC pipeline run must produce a deterministic run artifact directory to enable:
- Auditability: Know exactly what ran, when, and what it produced
- Reproducibility: Re-run with same inputs to verify outcomes
- Debugging: Trace failures back to specific inputs/checks
- CI Integration: Upload artifacts for post-mortem analysis

## Directory Structure

```
reports/runs/<run_id>/
├── run.json       # Manifest with inputs, outputs, metadata
├── checks.json    # Validation checks with pass/fail/skip + evidence
└── run.log        # Captured stdout/stderr from pipeline execution
```

## Run ID Format

Deterministic format:
```
<utc_yyyymmddThhmmssZ>__<pipeline_id>__<git_sha7>
```

Examples:
```
20260119T061512Z__P2-Backfill__a1b2c3d
20260119T143022Z__B1-DerivedC1__f4e5d6c
20260119T000000Z__D-NotionSync__0000000
```

Components:
- `utc_yyyymmddThhmmssZ`: UTC timestamp in ISO8601 compact format with Z suffix
- `pipeline_id`: Unique pipeline identifier (see Pipeline IDs section)
- `git_sha7`: First 7 characters of git commit SHA (or `0000000` if unavailable)

## Pipeline IDs

| Pipeline | ID | Description |
|----------|-----|-------------|
| OANDA Backfill | `P2-Backfill` | Historical 2H block backfill from OANDA |
| C1 Features | `B1-DerivedC1` | Single-bar OHLC primitive computation |
| C2 Features | `B1-DerivedC2` | Multi-bar structure feature computation |
| C3 Regime | `B1-DerivedC3` | Regime/trend classification |
| Derived Validation | `B2-DerivedValidation` | Validate derived feature packs |
| Day Validation | `D-ValidationHarness` | Single-day validation harness |
| Range Validation | `D-ValidationRange` | Multi-day range validation |
| Notion Sync | `D-NotionSync` | Sync to Notion databases |
| Option C | `C-Eval` | Option C evaluation runner |

## File Specifications

### run.json

Machine-readable manifest with all run metadata.

```json
{
  "run_id": "20260119T061512Z__P2-Backfill__a1b2c3d",
  "pipeline_id": "P2-Backfill",
  "pipeline_version": "0.1.0",
  "started_utc": "2026-01-19T06:15:12Z",
  "finished_utc": "2026-01-19T06:17:45Z",
  "duration_ms": 153000,
  "status": "success",
  "trigger": {
    "type": "github_schedule",
    "source": "workflow:backfill.yml",
    "actor": "github-actions[bot]"
  },
  "git": {
    "sha": "a1b2c3d4e5f6g7h8i9j0",
    "sha7": "a1b2c3d",
    "ref": "refs/heads/main"
  },
  "env": {
    "present": ["NEON_DSN", "OANDA_API_TOKEN", "OANDA_ENV"],
    "missing": []
  },
  "inputs": [
    {"type": "oanda", "ref": "GBP_USD", "range": "2026-01-13 to 2026-01-17"}
  ],
  "outputs": [
    {"type": "neon_table", "ref": "ovc.ovc_blocks_v01_1_min", "rows_written": 60}
  ]
}
```

Required keys:
- `run_id`: Deterministic run identifier
- `pipeline_id`: Pipeline identifier from table above
- `pipeline_version`: Semantic version of pipeline code
- `started_utc`: ISO8601 timestamp with Z suffix
- `finished_utc`: ISO8601 timestamp with Z suffix
- `duration_ms`: Execution time in milliseconds
- `status`: One of `success`, `failed`, `partial`
- `trigger`: Object with `type`, `source`, `actor`
- `git`: Object with `sha`, `sha7`, `ref`
- `env`: Object with `present` (list) and `missing` (list) - names only, no values!
- `inputs`: Array of input references
- `outputs`: Array of output references

### checks.json

Validation checks with evidence pointers.

```json
{
  "run_id": "20260119T061512Z__P2-Backfill__a1b2c3d",
  "checks": [
    {
      "id": "required_env_present",
      "name": "Required environment variables present",
      "status": "pass",
      "evidence": []
    },
    {
      "id": "oanda_fetch_success",
      "name": "OANDA API fetch succeeded",
      "status": "pass",
      "evidence": ["run.log:line:42"]
    },
    {
      "id": "rows_inserted",
      "name": "Rows inserted to Neon",
      "status": "pass",
      "evidence": ["run.json:$.outputs[0].rows_written"]
    }
  ],
  "summary": {
    "pass": 3,
    "fail": 0,
    "skip": 0
  }
}
```

Required keys:
- `run_id`: Must match run.json
- `checks`: Array of check objects
- `summary`: Object with `pass`, `fail`, `skip` counts

Check object keys:
- `id`: Machine identifier (snake_case)
- `name`: Human-readable description
- `status`: One of `pass`, `fail`, `skip`
- `evidence`: Array of evidence strings (see Evidence Format)

### run.log

Plain text log file capturing stdout/stderr from pipeline execution.

First line MUST be:
```
RUN_ID=<run_id>
```

This enables CI/CD systems to extract the run_id for artifact naming.

## Evidence Format

Evidence strings must use one of these formats:

| Format | Example | Description |
|--------|---------|-------------|
| `run.json:<jsonpath>` | `run.json:$.outputs[0].rows_written` | Reference to run.json value |
| `run.log:line:<n>` | `run.log:line:42` | Reference to specific log line |
| `artifacts/<path>` | `artifacts/validation_report.json` | Reference to additional artifact |

## Enums

### trigger.type
- `github_schedule`: Triggered by GitHub Actions cron schedule
- `github_dispatch`: Triggered by manual workflow_dispatch
- `local_cli`: Run locally via command line
- `worker_http`: Triggered by Cloudflare Worker HTTP request
- `worker_cron`: Triggered by Cloudflare Worker cron trigger

### status
- `success`: Pipeline completed successfully
- `failed`: Pipeline failed with errors
- `partial`: Pipeline completed with warnings or partial results

### check.status
- `pass`: Check passed validation
- `fail`: Check failed validation
- `skip`: Check was skipped (precondition not met)

## Formatting Rules

1. JSON files must use:
   - `indent=2` for pretty printing
   - `sort_keys=True` for deterministic key ordering
   - UTF-8 encoding

2. Timestamps must be UTC ISO8601 with Z suffix:
   - Correct: `2026-01-19T06:15:12Z`
   - Wrong: `2026-01-19T06:15:12+00:00`
   - Wrong: `2026-01-19 06:15:12`

3. No secret values in any artifact file:
   - Environment variable names only (present/missing lists)
   - No API tokens, passwords, or connection strings

## CI Integration

GitHub Actions workflows should:

1. Run the pipeline command (which creates artifacts)
2. Upload artifacts using `actions/upload-artifact`:
   ```yaml
   - uses: actions/upload-artifact@v4
     with:
       name: ovc-run-${{ env.PIPELINE_ID }}-${{ env.RUN_ID }}
       path: reports/runs/**
   ```

To make run_id available to workflows:
- Scripts print `RUN_ID=<run_id>` to stdout at start
- This line is also the first line of run.log
- Workflows can parse this from log output

## Error Handling

If required environment variables are missing:
1. Still create run artifact directory
2. Set `status=failed` in run.json
3. Add check `required_env_present` with `status=fail`
4. List missing variable names in evidence
5. Do not attempt to run business logic

This ensures every run attempt produces audit artifacts, even failures.
