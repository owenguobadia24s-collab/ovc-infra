# MOD-RUNOPS — Run Envelope Registry Health (v0.1)

## Definition
MOD-RUNOPS classifies run-envelope, registry, drift-signal, and health rendering surfaces, grounded in `OVC ARCHITECTURAL WAVES v2.md` section `W5 — Operational Integrity Layer` and `docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md`.

Coverage: FULL
Run envelope standards, registry schemas/validators/builders, and health contracts are present in tracked active paths.

## Wave Span
- W5 — expected versions, run registry, drift computation, and health measurability are introduced in `OVC ARCHITECTURAL WAVES v2.md`.
- W6 — machine-auditable enforcement extends operational integrity into deterministic audit surfaces.

## Core Invariants
- MUST emit run artifacts with required run envelope keys and deterministic file accounting.
- MUST treat active pointers as the only mutable selector for registry state.
- MUST compute drift and health from explicit expected/observed sources, not inferred guesses.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `src/ovc_ops/**`
- `contracts/run_artifact_spec_v0.1.json`
- `docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md`
- `docs/governance/EXPECTED_VERSIONS_v0_1.json`
- `docs/phase_2_2/**`
- `docs/governance/contracts/phase_2_3/**`
- `tools/run_registry/**`
- `tests/test_run_envelope_v0_1.py`
- .github/workflows/**

### Excludes (Path Patterns)
- `_archive/**`
- .github/workflows/repo_cartographer.yml
- .github/workflows/change_classifier.yml
- .github/workflows/append_sentinel.yml
- .github/workflows/backfill*.yml
- .github/workflows/ovc_option_c_schedule.yml
- .github/workflows/path1_*.yml
- .github/workflows/main.yml

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `src/ovc_ops/**`
- Attachment rule: attach when code emits or validates run envelope artifacts.
- Evidence reference: `contracts/run_artifact_spec_v0.1.json`.
- Pattern: `tools/run_registry/**`
- Attachment rule: attach when builder/renderer computes run registry, op status, drift signals, or system health.
- Evidence reference: `docs/phase_2_2/REGISTRY_LAYER_RUNBOOK_v0_1.md`.
- Pattern: `docs/phase_2_2/**` and `docs/governance/contracts/phase_2_3/**`
- Attachment rule: attach when document constrains registry seal, pointers, upgrade, deprecation, recovery, or health state.
- Evidence reference: `docs/phase_2_2/REGISTRY_SEAL_CONTRACT_v0_1.md`, `docs/governance/contracts/phase_2_3/HEALTH_CONTRACTS_v0_1.md`.

## Primary Directories
- `src/ovc_ops` — run artifact and envelope runtime; matched by `src/ovc_ops/**`.
- `tools/run_registry` — registry/drift/health builders; matched by `tools/run_registry/**`.
- `docs/phase_2_2` — registry schema and validation layer; matched by `docs/phase_2_2/**`.
- `docs/governance/contracts/phase_2_3` — health/upgrade/recovery/deprecation contracts; matched by `docs/governance/contracts/phase_2_3/**`.
- `tests` — run envelope test enforcement; matched by `tests/test_run_envelope_v0_1.py`.

## Canonical Artifacts
- contracts: `contracts/run_artifact_spec_v0.1.json`, `docs/phase_2_2/REGISTRY_SEAL_CONTRACT_v0_1.md`, `docs/governance/contracts/phase_2_3/HEALTH_CONTRACTS_v0_1.md`.
- SQL migrations/views: registry schema files `docs/phase_2_2/schemas/REGISTRY_run_registry_v0_1.schema.json`, `docs/phase_2_2/schemas/REGISTRY_drift_signals_v0_1.schema.json`.
- Python entrypoints: `src/ovc_ops/run_envelope_v0_1.py`, `tools/run_registry/build_run_registry_v0_1.py`, `tools/run_registry/build_drift_signals_v0_1.py`, `tools/run_registry/render_system_health_v0_1.py`.
- governance docs: `docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md`, `docs/governance/EXPECTED_VERSIONS_v0_1.json`, `docs/phase_2_2/REGISTRY_LAYER_RUNBOOK_v0_1.md`.

## Enforcement Hooks
- test files: `tests/test_run_envelope_v0_1.py`.
- CI workflows: `.github/workflows/repo_cartographer.yml`, `.github/workflows/ci_pytest.yml` (executes run envelope tests).
- validators: `docs/phase_2_2/validators/validate_registry_schema_v0_1.py`, `docs/phase_2_2/validators/validate_registry_seals_v0_1.py`, `docs/phase_2_2/validators/validate_active_pointers_v0_1.py`.
- sha256 / seal checks: seal contract and run manifests in `docs/phase_2_2/REGISTRY_SEAL_CONTRACT_v0_1.md` and sealed outputs under `artifacts/repo_cartographer/**`.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: organizational drift signal is tracked in governance source `docs/governance/DRIFT_REPORT_v2.md` and reviewed with active runops artifacts under `docs/phase_2_2/**`.
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: runops enforcement spans `docs/`, `tools/`, `tests/`, and `.github/`.

## Change Policy
Allowed:
- additive run envelope docs
- additive registry tests and validators
- additive versioned schemas/contracts
- forward-only builder and renderer evolution

Disallowed:
- breaking contract changes without evolution protocol
- bypassing active pointer mechanism
- silent mutation of envelope/health invariants

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md`
- `docs/phase_2_2/REGISTRY_LAYER_RUNBOOK_v0_1.md`

## Unassigned / Edge Cases
- `artifacts/path1_replay_report.json` — generated runtime artifact outside canonical registry docs; retained but not a module-defining source.
- `schema/applied_migrations.json` — shared validation utility surface; attached to `MOD-UTIL`.
