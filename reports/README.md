# Reports Directory Policy

This repo uses `reports/` for human-readable evidence and run artifacts.

## Tracked (committed)

- `reports/path1/**` — Path 1 observational evidence runs (append-only)
- `reports/validation/*.md` — canonical validation evidence (human-readable)
- `reports/verification/**` — canonical verification evidence (redacted; see below)

## Local-only (not committed)

- `reports/runs/**` — pipeline run artifacts written by scripts/workflows
- `reports/pipeline_audit/**` — ad-hoc local audits
- `reports/validation/*.json|*.csv|*.jsonl` — machine outputs (keep local; referenced via `.md` when needed)

## Redaction rule (verification)

If `reports/verification/**` is committed, it must not contain personal identifiers or secrets.
Raw/unredacted verification outputs belong in `data/verification_private/` (gitignored).

