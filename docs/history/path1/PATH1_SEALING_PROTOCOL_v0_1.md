# Path1 Sealing Protocol v0.1

**Status:** DRAFT (observational tooling)  
**Scope:** Per-run immutable hash manifests

## Purpose

Provide deterministic, append-only integrity seals for Path1 run folders.
Seals are observational and do not change Path1 semantics.

## Manifest Location

`reports/path1/evidence/runs/<run_id>/MANIFEST.sha256`

## Format (exact)

Each line:
`<sha256_hex><two spaces><relative_path_under_run_dir>`

Rules:
- relative paths use forward slashes `/`
- file list sorted lexicographically by relative path
- LF line endings
- trailing newline required

## Included Files

Required:
- `RUN.md`

Optional:
- `*_evidence.md`
- `outputs/**` (recursive), excluding:
  - `outputs/**/logs/**`
  - `outputs/**/.cache/**`
  - `outputs/**/*.log`
  - files larger than 50MB

## Always Excluded

- `MANIFEST.sha256`
- `.DS_Store`, `Thumbs.db`
- any directory named `cache`, `.cache`, or `logs`
- `*.tmp`

## Append-Only Rule

If `MANIFEST.sha256` already exists, do nothing and never rewrite it.
