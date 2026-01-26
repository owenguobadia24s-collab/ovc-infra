# Run Artifact Implementation Notes

This document describes the Run Artifact system implementation for OVC pipelines.

## Overview

The Run Artifact system provides deterministic, machine-readable outputs for all OVC pipelines. Each pipeline run produces:
- `reports/runs/<run_id>/run.json` - Core run metadata
- `reports/runs/<run_id>/checks.json` - Pass/fail checks
- `reports/runs/<run_id>/run.log` - Timestamped log

## run_id Format

```
<utc_yyyymmddThhmmssZ>__<pipeline_id>__<git_sha7>
```

Example: `20260117T143052Z__P2-Backfill__a1b2c3d`

## Instrumented Pipelines

| Pipeline ID | File | Status |
|------------|------|--------|
| P2-Backfill | [src/backfill_oanda_2h_checkpointed.py](../src/backfill_oanda_2h_checkpointed.py) | ✅ Instrumented |
| B1-DerivedC1 | [src/derived/compute_l1_v0_1.py](../src/derived/compute_l1_v0_1.py) | ✅ Instrumented |
| B1-DerivedC2 | [src/derived/compute_l2_v0_1.py](../src/derived/compute_l2_v0_1.py) | ✅ Instrumented |
| B1-DerivedC3 | [src/derived/compute_l3_regime_trend_v0_1.py](../src/derived/compute_l3_regime_trend_v0_1.py) | ✅ Instrumented |
| B2-DerivedValidation | [src/validate/validate_derived_range_v0_1.py](../src/validate/validate_derived_range_v0_1.py) | ✅ Instrumented |
| D-NotionSync | [scripts/notion_sync.py](../scripts/notion_sync.py) | ✅ Instrumented |
| D-ValidationHarness | [src/validate_day.py](../src/validate_day.py) | ✅ Instrumented |
| D-ValidationRange | [src/validate_range.py](../src/validate_range.py) | ✅ Instrumented |
| C-Eval | [scripts/run_option_c_wrapper.py](../scripts/run_option_c_wrapper.py) | ✅ Wrapper created |

## Core Files

### Python Helper Module

- **File**: [src/ovc_ops/run_artifact.py](../src/ovc_ops/run_artifact.py)
- **Class**: `RunWriter`
- **Methods**:
  - `start(trigger_type, trigger_source, actor)` - Initialize run
  - `add_input(type, ref, **kwargs)` - Record input dependency
  - `add_output(type, ref, **kwargs)` - Record output artifact
  - `check(name, status, evidence)` - Record pass/fail check
  - `log(message)` - Append timestamped log entry
  - `finish(status)` - Finalize and write artifacts

### CLI Wrapper

- **File**: [src/ovc_ops/run_artifact_cli.py](../src/ovc_ops/run_artifact_cli.py)
- **Usage**: Wrap non-Python pipelines (bash scripts)

```bash
python src/ovc_ops/run_artifact_cli.py \
  --pipeline-id "C-Eval" \
  --pipeline-version "0.1.0" \
  --required-env "DATABASE_URL" \
  -- \
  bash scripts/run_option_c.sh --run-id "$run_id"
```

## Specifications

- **Human spec**: [docs/ops/RUN_ARTIFACT_SPEC_v0.1.md](RUN_ARTIFACT_SPEC_v0.1.md)
- **Machine spec**: [contracts/run_artifact_spec_v0.1.json](../contracts/run_artifact_spec_v0.1.json)

## Enums

### trigger_type
- `github_schedule` - Scheduled GitHub Action
- `github_dispatch` - Manual workflow dispatch
- `local_cli` - Local command line execution
- `worker_http` - Cloudflare Worker HTTP trigger
- `worker_cron` - Cloudflare Worker cron trigger

### status (run)
- `success` - All checks passed
- `failed` - One or more checks failed
- `partial` - Some checks skipped or warnings

### status (check)
- `pass` - Check passed
- `fail` - Check failed
- `skip` - Check skipped (e.g., missing dependencies)

## Evidence Formats

- `run.json:<jsonpath>` - Reference to run.json field
- `run.log:line:<n>` - Reference to log line number
- `artifacts/<path>` - Reference to artifact file

## GitHub Workflow Integration

Workflows updated to upload run artifacts:

- `.github/workflows/backfill.yml` - Uploads `reports/runs/`
- `.github/workflows/notion_sync.yml` - Uploads `reports/runs/`
- `.github/workflows/ovc_option_c_schedule.yml` - Uploads `reports/runs/`
- `.github/workflows/backfill_then_validate.yml` - Uploads `reports/runs/`

### Artifact Upload Step

```yaml
- name: Upload run artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: run-artifacts-${{ github.run_id }}
    path: reports/runs/
    if-no-files-found: ignore
    retention-days: 30
```

## Locating Run Artifacts

### Local Runs

```
reports/runs/<run_id>/
├── run.json
├── checks.json
└── run.log
```

### GitHub Actions

Download from the Actions tab → Run → Artifacts section.

## Adding Instrumentation to New Pipelines

1. Import the helper:
   ```python
   from ovc_ops.run_artifact import RunWriter, detect_trigger
   ```

2. Define constants:
   ```python
   PIPELINE_ID = "YourPipelineId"
   PIPELINE_VERSION = "0.1.0"
   REQUIRED_ENV_VARS = ["VAR1", "VAR2"]
   ```

3. Wrap main execution:
   ```python
   if __name__ == "__main__":
       trigger_type, trigger_source, actor = detect_trigger()
       writer = RunWriter(PIPELINE_ID, PIPELINE_VERSION, REQUIRED_ENV_VARS)
       writer.start(trigger_type=trigger_type, trigger_source=trigger_source, actor=actor)
       
       try:
           result = main(writer)
           writer.finish(status="success")
       except Exception as e:
           writer.log(f"Exception: {e}")
           writer.finish(status="failed")
           raise
   ```

4. Add inputs/outputs/checks within main:
   ```python
   writer.add_input(type="neon_table", ref="ovc.ovc_blocks_v01_1_min")
   writer.add_output(type="file", ref=str(output_path))
   writer.check(name="row_count", status="pass", evidence=f"rows={count}")
   ```

## JSON Formatting

All JSON output uses:
- `indent=2`
- `sort_keys=True`
- ASCII-safe encoding

This ensures deterministic, diff-friendly output.
