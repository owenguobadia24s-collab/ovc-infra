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

## Canonical vs Generated (Reports Policy)

This repo distinguishes between:

- **Canonical evidence (human-authored):** narrative writeups intended to be read/cited (e.g., audits, verification narratives, summaries, indices).
- **Generated outputs (machine-produced):** files produced by runs/validators/scripts/workflows (e.g., JSON, logs, CSV/JSONL dumps, spotchecks).

### Where things must live

**Canonical evidence lives in `reports/`**
- Markdown writeups, audits, indices, and human explanations belong here.
- If a canonical markdown references generated attachments, the attachments should not be embedded as canonical content.

**Generated outputs live in `artifacts/`**
- Machine outputs that are replaceable/regenerable should be stored under `artifacts/` in an option-scoped subtree (e.g., `artifacts/option_c/...`).
- Example: local sanity machine outputs were moved from `reports/` to `artifacts/option_c/sanity_local/` while the narrative markdown remained in `reports/`.

### Compatibility exception (path-coupled writers)

Some workflows/scripts currently write to fixed locations under `reports/` (e.g., `reports/runs/`, parts of `reports/validation/`). These locations are treated as **compat-generated**:
- They may contain generated outputs due to hard coupling.
- Do not manually edit generated files in these locations.
- Any future relocation requires a planned change that updates writers/readers (no "moves-only" pass).

### Promotion / relocation rule

- If a generated file in `reports/` is **not path-coupled** (no writers/readers depend on its exact path), it should be relocated to `artifacts/` and left referenced by a canonical markdown if needed.
- If it *is* path-coupled, leave it in place and document it as compat-generated until Phase 2 changes are allowed.

### Safety rule for organization passes

During organization passes:
- **Moves only** (no deletions, no renames, no content edits) unless explicitly stated and reviewed.
- Any move must be preceded by a dependency search proving no execution coupling to the path being moved.

