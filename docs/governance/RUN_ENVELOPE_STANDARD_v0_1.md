# Run Envelope Standard v0.1

**Version**: 0.1  
**Status**: ACTIVE  
**Date**: 2026-02-04

## Required `run.json` keys

- `run_id` (string) — run folder name.
- `created_utc` (string) — ISO8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`).
- `run_type` (string) — e.g. `op_run`.
- `option` (string) — one of `A|B|C|D|QA`.
- `operation_id` (string) — `OP-...`.
- `git_commit` (string or null).
- `working_tree_state` (`clean|dirty|null`).
- `inputs` (object, optional) — minimal inputs already available at runtime.
- `outputs` (array) — files written into the run folder.

## Run Folder Roots

- Preferred: `reports/runs/<run_id>/`
- Allowed: `.codex/RUNS/<run_id>/`
- Legacy (existing Path1 evidence/state-plane runs): `reports/path1/evidence/runs/<run_id>/`

## Sealing Format

- `manifest.json` — array of entries: `{"relpath": "...", "bytes": <int>, "sha256": "..."}`.
- `MANIFEST.sha256` — one line per file: `SHA256  relpath`.
- `MANIFEST.sha256` MUST include a `manifest.json` line and a `ROOT_SHA256  <hash>` line.
- `ROOT_SHA256` = SHA256 of all sha lines (including `manifest.json`), sorted lexicographically and joined with `\n` plus trailing newline.
