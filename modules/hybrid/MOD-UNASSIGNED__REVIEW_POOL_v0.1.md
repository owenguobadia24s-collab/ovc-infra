# MOD-UNASSIGNED — Review Pool (v0.1)

## Definition
MOD-UNASSIGNED classifies uncertain, quarantine, archive, and residual surfaces that cannot be deterministically attached to another module without additional ratified evidence, grounded in `GENESIS_LEDGER.tsv` PASS-2 residual handling and `docs/governance/DRIFT_REPORT_v2.md`.

Coverage: DRIFT
This pool intentionally contains drift-signaled and uncertain artifacts; assignment is fail-closed and non-speculative.

## Wave Span
- W1 — includes early-wave quarantine and legacy ingest artifacts pending explicit status.
- W2 — includes legacy/experimental boundary artifacts pending deterministic ownership.
- W3 — includes historical module docs and cross-era references.
- W4 — includes overlay/changelog sidecar artifacts with unresolved canonical placement.
- W5 — includes drift-signaled root outputs and operational residuals.
- W6 — includes scratch and residual audit-adjacent artifacts not in active canonical audit harness.

## Core Invariants
- MUST isolate uncertain ownership instead of force-fitting paths.
- MUST keep quarantine/archive surfaces explicit and review-gated.
- MUST NOT claim enforcement completeness for artifacts parked in review pool.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `modules/**`
- `.codex/_scratch/**`
- `.codex/config.toml`
- `artifacts/derived_validation/**`
- `artifacts/option_c/**`
- `artifacts/repo_census.json`
- `docs/path2/**`
- `docs/README_ORG_NOTES.md`
- `src/_LIBRARY_ONLY.md`
- `tools/_maintenance_sentinel_hook_trip.md`

### Excludes (Path Patterns)
- none
- Tetsu/**
- _archive/**
- _quarantine/**
- pine/**
- CLAIMS/**
- releases/**
- Work Timeline/**
- research/**
- reports/**
- docs/state_plane/**
- .codex/config.toml

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `_quarantine/**` and `_archive/**`
- Attachment rule: attach when artifact is explicitly dormant, deprecated, or non-canonical.
- Evidence reference: `docs/governance/DRIFT_REPORT_v2.md` (`2. Quarantine Layer (LOW–MEDIUM)`).
- Pattern: residual roots from `GENESIS_LEDGER.tsv`
- Attachment rule: attach when no other module include rule matches under precedence.
- Evidence reference: `GENESIS_LEDGER.tsv`.

## Primary Directories
- `_archive` — archived non-canonical state; matched by `_archive/**`.
- `_quarantine` — dormant/deprecated state; matched by `_quarantine/**`.
- `research` — research pool outside canonical W1–W6 module ownership.
- `Tetsu` — external notes/maze hierarchy outside canonical carve.
- `modules` — legacy module set, superseded by hybrid carve context.
- `pine` — pine artifacts with unresolved active module attachment.
- `Work Timeline` — historical timeline files with non-canonical structure.
- `CLAIMS` — claim-binding sidecar artifacts requiring explicit governance mapping.

## Canonical Artifacts
- contracts: none (NEEDS_REVIEW).
- SQL migrations/views: `_quarantine/sql/10_views_research_v0.1.sql`.
- Python entrypoints: `_quarantine/src/full_ingest_stub.py`, `_quarantine/src/derived/compute_c3_stub_v0_1.py`.
- governance docs: `_quarantine/README.md`, `docs/path2/ROADMAP_v0_1.md`.

## Enforcement Hooks
- test files: none module-specific; artifacts in this pool are not considered strongly enforced.
- CI workflows: `_quarantine/.github/workflows/ovc_full_ingest.yml` exists but is quarantined.
- validators: no deterministic active validator set owned by this module.
- sha256 / seal checks: seal artifacts may exist in subtrees, but no module-level active seal contract applies.
If enforcement is incomplete, state explicitly: enforcement is intentionally incomplete until paths are ratified into canonical modules.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: organizational drift handling remains attached to tracked governance surfaces and unresolved residual pools in this module.
- `docs/governance/DRIFT_REPORT_v2.md` / `2. Quarantine Layer (LOW–MEDIUM)`: `_quarantine/**` is explicitly flagged for deprecated-status clarity.
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: mixed residual artifacts from cross-wave surfaces are parked here as fail-closed residuals.

## Change Policy
Allowed:
- additive review notes and classification evidence
- additive tests that reduce ambiguity
- additive versioned contracts to promote paths out of unassigned
- forward-only reclassification after governance ratification

Disallowed:
- force-fit reclassification without deterministic evidence
- bypassing quarantine/archival status controls
- silent reassignment of uncertain artifacts

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/governance/DRIFT_REPORT_v2.md`

## Unassigned / Edge Cases
- Top-level roots (PASS-2 first): `_archive`, `_quarantine`, `research`, `Tetsu`, `modules`, `pine`, `releases`, `Work Timeline`, `CLAIMS`.
- Additional residual paths: `.codex/_scratch/**`, `.codex/config.toml`, `artifacts/derived_validation/**`, `artifacts/option_c/**`, `artifacts/repo_census.json`, `docs/path2/**`, `src/_LIBRARY_ONLY.md`, `tools/_maintenance_sentinel_hook_trip.md`.
- Status for all listed entries: `NEEDS_REVIEW`.
