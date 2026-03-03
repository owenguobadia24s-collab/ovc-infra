# MOD-UTIL — Cross-cutting Utilities (v0.1)

## Definition
MOD-UTIL classifies shared utility and validation surfaces reused across waves without owning a unique wave invariant, grounded in `docs/governance/DIRECTORY_WAVE_MAP_v2.md` (cross-wave directory evidence) and `docs/governance/DRIFT_REPORT_v2.md` (`3. Cross-Wave Directories (LOW)`).

Coverage: FULL
Shared validators, schema checks, fixtures, and CI utility surfaces are present in tracked active paths.

## Wave Span
- W1 — utility support appears in base ingest and schema validation flow.
- W2 — derived validation support expands in shared validators.
- W3 — governance crystallization adds reusable validation and contract tooling.
- W4 — evidence hardening adds deterministic support checks.
- W5 — operational integrity adds registry/health support validators.
- W6 — machine-audit layer consumes shared utility scaffolding.

## Core Invariants
- MUST keep shared validators deterministic and reusable across module boundaries.
- MUST preserve CI-level utility checks for schema and test execution.
- MUST NOT claim module-specific invariant authority beyond shared support role.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `src/utils/**`
- `src/validate*`
- `src/validate/**`
- `src/ovc_artifacts.py`
- `schema/**`
- `sql/qa_*.sql`
- `sql/90_verify_gate2.sql`
- `sql/02_tables_run_reports.sql`
- `sql/04_ops_notion_sync.sql`
- `scripts/ci/verify_schema_objects.py`
- `scripts/validate/run_qa_validation_pack.py`
- `scripts/export/notion_sync.py`
- `scripts/repo_census.py`
- `tools/validate_contract.py`
- `tools/parse_export.py`
- `.github/workflows/ci_*.yml`
- `.github/workflows/notion_sync.yml`
- `tests/fixtures/**`
- `tests/sample_exports/**`
- `reports/verification/**`
- `reports/validation/**`
- `docs/validation/**`
- `docs/operations/**`
- `docs/baselines/**`
- `pytest.ini`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.gitattributes`
- `.vscode/settings.json`
- `package-lock.json`
- sql/_LIBRARY_ONLY.md
- tools/__init__.py

### Excludes (Path Patterns)
- `_archive/**`
- `_quarantine/**`
- research/**
- reports/**
- docs/state_plane/**
- tests/test_fingerprint*.py
- tests/test_dst_audit.py
- .github/**

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `scripts/ci/verify_schema_objects.py` and `schema/**`
- Attachment rule: attach when artifact verifies schema object presence and migration metadata.
- Evidence reference: `.github/workflows/ci_schema_check.yml`.
- Pattern: `src/validate*` and `sql/qa_*.sql`
- Attachment rule: attach when artifact runs QA validation packs across shared surfaces.
- Evidence reference: `docs/contracts/qa_validation_contract_v1.md`.
- Pattern: `.github/workflows/ci_*.yml`
- Attachment rule: attach when workflow provides shared enforcement baseline for multiple modules.
- Evidence reference: `.github/workflows/ci_pytest.yml`, `.github/workflows/ci_schema_check.yml`.

## Primary Directories
- `src/utils` — reusable helper functions; matched by `src/utils/**`.
- `src/validate` — shared validation runtime; matched by `src/validate/**` and `src/validate*`.
- `schema` — schema guard metadata; matched by `schema/**`.
- `scripts/ci` — schema object verification utility; matched by `scripts/ci/verify_schema_objects.py`.
- `tests/fixtures` and `tests/sample_exports` — reusable fixtures and expected outputs.
- `docs/validation` and `docs/operations` — shared validation and operating references.

## Canonical Artifacts
- contracts: `docs/contracts/qa_validation_contract_v1.md`.
- SQL migrations/views: `sql/qa_schema.sql`, `sql/qa_validation_pack.sql`, `sql/qa_validation_pack_core.sql`, `sql/qa_validation_pack_derived.sql`, `sql/90_verify_gate2.sql`.
- Python entrypoints: `src/validate_day.py`, `src/validate_range.py`, `src/validate/validate_derived_range_v0_1.py`, `scripts/ci/verify_schema_objects.py`, `scripts/validate/run_qa_validation_pack.py`.
- governance docs: `docs/validation/VERIFICATION_REPORT_v0.1.md`, `docs/operations/OPERATING_BASE.md`.

## Enforcement Hooks
- test files: fixture-driven suites under `tests/fixtures/**` and `tests/sample_exports/**`.
- CI workflows: `.github/workflows/ci_pytest.yml`, `.github/workflows/ci_schema_check.yml`, `.github/workflows/ci_workflow_sanity.yml`.
- validators: `scripts/ci/verify_schema_objects.py`, `src/validate_day.py`, `src/validate_range.py`, `src/validate/validate_derived_range_v0_1.py`.
- sha256 / seal checks: utility layer consumes seal/hash outputs; no standalone utility-only seal emitter.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: utility ownership intentionally spans `docs`, `scripts`, `tests`, and `.github`.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: organizational drift tracking remains attached to `docs/governance/DRIFT_REPORT_v2.md` and adjacent utility docs under `docs/operations/**`.

## Change Policy
Allowed:
- additive utility docs
- additive shared tests and fixtures
- additive versioned contracts and validators
- forward-only CI utility hardening

Disallowed:
- breaking contract changes without evolution protocol
- bypassing schema/validation gates
- silent mutation of shared validation semantics

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/contracts/qa_validation_contract_v1.md`
- `docs/governance/BRANCH_POLICY.md`

## Unassigned / Edge Cases
- `src/_LIBRARY_ONLY.md` — uncertain governance role marker, routed to `MOD-UNASSIGNED`.
- `tools/_maintenance_sentinel_hook_trip.md` — mixed utility/change ownership, routed to `MOD-UNASSIGNED` pending ratification.
