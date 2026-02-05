# Phase 4 Audit Interpreter (Reader-Only) v0.1

**NON-AUTHORITATIVE**: This tool is a derived interpreter. Truth resides in source artifacts.

## Purpose

The Audit Interpreter is a read-only agent that consumes Phase 3 run artifacts and emits a structured interpretation report in canonical JSON format. The agent performs classification, aggregation, and formatting of evidence from sealed run folders.

**This agent is not a source of truth.** All claims in the interpretation report are derived from and must reference the source artifacts. The source artifacts remain authoritative; the interpretation report is a convenience layer for human and downstream consumption.

## Contract

This tool is governed by:

- `AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1`
- `AUDIT_INTERPRETATION_REPORT_v0.1.json` (JSON Schema)

## Non-Authority Declaration

The Audit Interpreter agent CANNOT and MUST NOT:

- Write to any file in the repository (except the report file)
- Create, modify, or delete run artifacts
- Execute any subprocess, shell command, or external process
- Perform git operations
- Assert facts not present in source artifacts
- Interpret ambiguous evidence as definitive
- Generate synthetic evidence or placeholder data

## Installation

```bash
cd tools/audit_interpreter
pip install -e .
```

## Usage

### Basic Usage

```bash
# Interpret a run and write report to canonical path
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build
```

### Output to Stdout

```bash
# Print report to stdout instead of writing file
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --stdout
```

When `--stdout` is used, the interpreter emits **machine-only JSON** to stdout. Any human-readable messages (if present) are sent to stderr to preserve pipe safety.

Pipe-safe example:

```bash
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --stdout | python -c "import sys,json; r=json.load(sys.stdin); print(r['schema_version'])"
```

### Strict Mode

```bash
# Treat unknown artifacts as OUT_OF_SCOPE non-claims
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --strict
```

### Custom Paths

```bash
# Override runs root directory
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --runs-root /path/to/.codex/RUNS

# Override repository root
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --repo-root /path/to/ovc-infra
```

### Windows PATH Troubleshooting

On Windows, the console script may install to a user scripts directory (for example:
`C:\Users\<you>\AppData\Roaming\Python\Python314\Scripts`) that is not on `PATH`.
If `audit-interpreter` is not recognized, prefer the PATH-independent form:

```bash
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build
```

You may also add the scripts directory to `PATH` to use the `audit-interpreter` command directly.

## Canonical Output Path

Reports are written to:

```
.codex/RUNS/<run_id>/audit_interpretation_v0.1.json
```

## Recursive Artifact Scanning

Artifacts are discovered by walking the entire run folder recursively. Each `artifact_path` recorded in the report is the run-relative POSIX path (forward slashes), so nested files appear as `subdir/file.json`.

## Fail-Closed Philosophy

This interpreter operates on a **fail-closed** principle:

1. **Missing Evidence**: If evidence required for a claim is missing, the claim MUST NOT be made. Instead, the condition is recorded in `non_claims` with reason `EVIDENCE_MISSING`.

2. **Ambiguous Evidence**: If evidence is present but ambiguous or contradictory, the classification MUST be `UNKNOWN` and confidence MUST be `NONE`.

3. **Parse Failures**: If an artifact cannot be parsed, the failure is recorded with `failure_class: ARTIFACT_MALFORMED` and no further interpretation of that artifact is permitted.

4. **No Inference from Absence**: The interpreter NEVER infers failures from absence of "success" text. Only explicit failure evidence is classified.

## Pipeline

The interpreter executes these steps in order:

1. **Load Run Context** - Read run.json, extract metadata
2. **Detect Seal** - Check manifest.json + MANIFEST.sha256 validity
3. **Scan Artifacts** - Identify and classify all artifacts
4. **Parse Artifacts** - Type-specific parsing
5. **Classify Failures** - From explicit evidence only
6. **Build Report** - Construct canonical JSON
7. **Validate Report** - Against JSON schema
8. **Emit Report** - Write file or stdout

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - report emitted |
| 1 | Failure - interpretation failed |

## Overall Status Precedence

The `interpretation_summary.overall_status` field is determined by the following precedence rules:

1. **UNKNOWN** dominates if seal is invalid (`SEAL_INVALID` failure) OR any `EVIDENCE_INCOMPLETE` failure exists
2. Else **FAIL** if any `CRITICAL` or `ERROR` severity failures exist
3. Else **PASS** if no failures exist (warnings only do not cause FAIL)

## Report ID Determinism

The `report_id` follows the format `AIR-YYYYMMDDTHHMMSSZ-<8hex>` where:
- The timestamp is from `generated_utc`
- The 8-hex suffix is **deterministic**, derived from SHA256 of:
  - `run_id`
  - `schema_version`
  - `interpreter_version`
  - Sorted evidence_index entries (artifact_path + sha256 or read_status)

Running the interpreter twice on the same unchanged run will produce the same 8-hex suffix (timestamp may differ).

## Report Structure

The interpretation report contains:

- `schema_version`: "0.1"
- `report_id`: Deterministic identifier (AIR-YYYYMMDDTHHMMSSZ-8hex)
- `generated_utc`: ISO8601 timestamp
- `interpreter_version`: "0.1"
- `run_id`: Interpreted run identifier
- `run_type`: From run.json
- `run_created_utc`: From run.json
- `seal_status`: Seal validity information
- `interpretation_summary`: Overall status, counts, confidence
- `failures`: Array of classified failures with evidence refs
- `non_claims`: Claims withheld due to insufficient evidence
- `next_actions`: Recommended remediation actions
- `evidence_index`: All artifacts referenced
- `metadata`: Contract version, authority statement

## Failure Classes

| Class | Severity | Description |
|-------|----------|-------------|
| SEAL_INVALID | CRITICAL | Manifest hash mismatch |
| RUN_ENVELOPE_MALFORMED | CRITICAL | run.json structure invalid |
| AUDIT_FAILED | ERROR | Explicit audit failure |
| ARTIFACT_MISSING | ERROR/CRITICAL | Required artifact not found |
| ARTIFACT_MALFORMED | ERROR | Artifact unparseable |
| SCHEMA_VIOLATION | ERROR | Artifact violates schema |
| EVIDENCE_INCOMPLETE | WARNING | Partial evidence |
| UNKNOWN | varies | Unclassifiable failure |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Verification (Git Bash, PATH-independent)

```bash
# Install (venv active)
python -m pip install -e tools/audit_interpreter

# Import smoke test
python -c "import audit_interpreter.cli as c; print('import_ok')"

# Pipe-safe JSON stdout test (stderr separated)
python -m audit_interpreter.cli interpret --run-id 2026-02-05__031005__registry_delta_log_build --stdout 1>out.json 2>out.err
python -c "import json; json.load(open('out.json')); print('JSON_OK')"
cat out.err
```

If that run id is not present, list available runs and substitute one:

```bash
ls .codex/RUNS
```

---

*Contract: AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1*
