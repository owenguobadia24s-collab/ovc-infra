# Repo Organization Notes (OVC Infra)

## Purpose + mental model

This repo implements and governs the OVC pipeline: ingest canonical market facts, compute derived features (Option B), compute outcomes/evaluation (Option C), and produce evidence/validation artifacts for operations.

Pipeline stages (high level):
- **Ingest (P1/P2):** TradingView/Pine export → webhook ingest (P1) and backfill (P2) into Neon Postgres canonical tables.
- **Transform/Compute (Option B):** deterministic derived features (L1/L2/L3) computed from canonical facts, with versioned threshold/config provenance.
- **Evaluation/Outcomes (Option C):** forward-return/outcome views and run reports derived from Option B outputs.
- **Validation/QA:** contract validation + derived validation packs + tape/consistency checks; produces evidence artifacts.
- **Ops/Orchestration:** GitHub Actions schedules and operator scripts to run/deploy/verify and to sync operational surfaces (Option D).

## Top-level folders (responsibilities)

- `docs/` — human-authored doctrine, governance, architecture maps, narrative contracts/specs, runbooks, operations guides, validation writeups, and history.
- `contracts/` — machine-readable contracts/specs (JSON) used by validators/tests (e.g., export contracts, derived feature set, run artifact spec).
- `src/` — Python implementation code (ingest/backfill, derived compute, validation harness, ops helpers).
- `scripts/` — operator entrypoints/wrappers grouped by lifecycle (`deploy/`, `run/`, `validate/`, `export/`, `local/`, plus path-specific like `path1/`).
- `sql/` — schema DDL, migrations, and query packs (canonical schemas, derived layer, QA packs, Option C SQL, Path1 SQL packs).
- `reports/` — human-readable evidence and run artifacts (policy in `reports/README.md`; includes committed validation/verification evidence and local-only run outputs); may contain both canonical evidence narratives and small, scoped generated attachments that are referenced by those narratives.
- `artifacts/` — machine-generated replacebale artifacts produced by validators/automation (e.g., derived validation bundles; pointers like `LATEST.txt`).
- `data/` — inputs and private/unredacted verification material; includes raw samples under `data/raw/` and private verification under `data/verification_private/`.
- `infra/` — infrastructure subprojects (e.g., Cloudflare Worker webhook under `infra/ovc-webhook/`).
- `pine/` — TradingView/Pine sources that emit export strings and related panels/modules.
- `research/` — research notebooks, studies, scoring templates, and research tooling (guardrailed by `research/RESEARCH_GUARDRAILS.md`).
- `tools/` — repo utilities (e.g., contract validators/parsers) intended to be run directly.
- `releases/` — release notes and versioned rollout artifacts.
- `.github/` — GitHub Actions workflows (schedules/orchestration for backfill, validation, Option C runs, Notion sync, Path1 evidence queue).

## `docs/` subfolders

- `docs/doctrine/` — epistemic boundaries and invariants (e.g., gates, immutability).
- `docs/governance/` — decision logs and repo/process rules (e.g., branch policy, governance rules).
- `docs/contracts/` — narrative contracts/boundaries (Option boundaries, semantic contracts) that complement `contracts/` JSON.
- `docs/specs/` — implementation specs/charters/contracts for Options and components.
  - `docs/specs/system/` — system-level specs that apply across options (e.g., run report spec, parsing/validation rules, research SQL spec).
- `docs/architecture/` — canonical dataflow maps and “reality maps” for what is implemented (e.g., `OVC_DATA_FLOW_CANON_v0.1.md`).
- `docs/runbooks/` — operator checklists and step-by-step procedures for Options (e.g., Option C runbook, threshold registry runbook).
- `docs/operations/` — operating base docs: environment/secrets, workflow status, readiness, deployment and workflow notes.
- `docs/validation/` — canonical validation narratives and audit writeups.
- `docs/history/` — historical lineage by path/option (e.g., Path1/Path2 history and protocols).

## Canonical vs generated policy

- **Canonical (human-authored, versioned, reviewed):**
  - `docs/**` (doctrine/governance/architecture/contracts/specs/runbooks/operations/validation/history)
  - `contracts/**` (machine contracts)
  - `sql/**`, `src/**`, `scripts/**`, `infra/**`, `pine/**`, `tools/**`, `releases/**` (implementation and release artifacts)
- **Generated (outputs of runs/validators; may be local-only or selectively committed as evidence):**
  - Run outputs and evidence: `reports/**` (follow `reports/README.md` for what is committed vs local-only)
  - Machine bundles/artifacts: `artifacts/**`
  - Private/unredacted verification: `data/verification_private/**` (gitignored)

Where generated outputs must go:
- Human-readable evidence meant to be reviewed: `reports/` (prefer `reports/validation/` and `reports/verification/` for committed evidence).
- Machine-generated bundles/pointers: `artifacts/`.
- Unredacted/private verification material: `data/verification_private/`.

## How to add new things (rules of thumb)

- New system specs (cross-cutting): put in `docs/specs/system/`.
- New option specs/runbooks: put in `docs/specs/` or `docs/runbooks/` (keep Option B/C naming consistent with existing files).
- New machine contracts/schemas: put in `contracts/` (JSON), versioned (e.g., `*_v0.1*.json`).
- New scripts: put in `scripts/<lifecycle>/`:
  - deploy → `scripts/deploy/`
  - run/orchestrate → `scripts/run/`
  - validate → `scripts/validate/`
  - export/sync → `scripts/export/`
  - local-only helpers → `scripts/local/`
  - path-specific automation → `scripts/path1/` (and analogous existing path folders only)
- New SQL:
  - canonical schema/migrations → `sql/` (match existing naming/versioning)
  - derived/Option C/path packs → the existing subtrees (`sql/derived/`, `sql/path1/`, or clearly named root SQL files if they are canonical entrypoints)
- New run outputs:
  - human evidence → `reports/` (follow `reports/README.md`)
  - machine bundles → `artifacts/`
  - private outputs → `data/verification_private/`

## Safety rule for organization passes

Organization passes are **moves-only unless explicitly stated otherwise**: no deletions, no renames, and no content edits.
Anchor C indexed in CLAIMS/ANCHOR_INDEX_v0_1.csv.
