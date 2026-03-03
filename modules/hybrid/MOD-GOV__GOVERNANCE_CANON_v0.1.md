# MOD-GOV — Governance Canon (v0.1)

## Definition
MOD-GOV classifies canonical governance, doctrine, contract, and runbook surfaces that define allowed operations and change controls, grounded in `OVC ARCHITECTURAL WAVES v2.md` section `W3 — Structural Crystallization Event` and `docs/governance/GOVERNANCE_RULES_v0.1.md`.

Coverage: FULL
Governance contract and rule surfaces are present in tracked canonical paths and remain attachable under deterministic ownership rules.

## Wave Span
- W3 — governance becomes explicit and contract-bound in `OVC ARCHITECTURAL WAVES v2.md` (`W3 — Structural Crystallization Event`).
- W5 — operational governance hardening is documented (`W5 — Operational Integrity Layer`).
- W6 — machine-auditable governance and drift classification extend canon (`W6 — Machine Audit & Classification Consciousness`).

## Core Invariants
- MUST keep governance and contract artifacts explicit, versioned, and inspectable in tracked paths.
- MUST enforce rule-of-change via governance docs and contract evolution protocol.
- MUST NOT permit silent invariant mutation outside ratified governance process.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `docs/governance/**`
- `docs/contracts/**`
- `docs/doctrine/**`
- `docs/architecture/**`
- `docs/workflows/**`
- `docs/runbooks/**`
- `docs/pipeline/**`
- `docs/REPO_MAP/**`
- `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md`
- `docs/governance/OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md`
- `docs/governance/OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md`
- `docs/governance/PHASE_1_5_CLOSURE_DECLARATION.md`
- `docs/governance/PRUNE_PLAN_v0.1.md`
- `docs/governance/ARCHIVE_NON_CANONICAL_v0.1.md`
- .github/copilot-instructions.md
- .github/copilot-instructions.txt
- .github/pull_request_template.md

### Excludes (Path Patterns)
- `_archive/**`
- docs/contracts/option_*.md
- docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json
- docs/governance/CHANGE_TAXONOMY_v0_*.md
- docs/governance/EXPECTED_VERSIONS_v0_*.json
- docs/governance/RUN_ENVELOPE_STANDARD_v0_*.md
- docs/governance/contracts/phase_2_3/**

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `docs/governance/**`
- Attachment rule: attach when file states invariant, policy, matrix, or drift governance.
- Evidence reference: `OVC ARCHITECTURAL WAVES v2.md`, input doc WAVE_ENFORCEMENT_COVERAGE_v1.md.
- Pattern: `docs/contracts/**`
- Attachment rule: attach when file constrains behavior through contract law.
- Evidence reference: `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md`.
- Pattern: governance-rooted docs under `docs/governance/` (`OVC_*`, `docs/governance/PRUNE_PLAN_v0.1.md`, `docs/governance/PHASE_1_5_CLOSURE_DECLARATION.md`)
- Attachment rule: attach when file is still tracked governance canon outside `docs/governance/`.
- Evidence reference: `docs/governance/DRIFT_REPORT_v2.md`.

## Primary Directories
- `docs/governance` — governance invariants and matrices; matched by `docs/governance/**`.
- `docs/contracts` — formal behavior constraints; matched by `docs/contracts/**`.
- `docs/doctrine` — doctrine constraints; matched by `docs/doctrine/**`.
- `docs/architecture` — architecture canon references; matched by `docs/architecture/**`.
- `docs/runbooks` — operational canon procedures; matched by `docs/runbooks/**`.

## Canonical Artifacts
- contracts: `docs/contracts/A_TO_D_CONTRACT_v1.md`, `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md`, `docs/contracts/qa_validation_contract_v1.md`.
- SQL migrations/views: `docs/contracts/schemas/AUDIT_INTERPRETATION_REPORT_v0.1.json` (schema contract artifact).
- Python entrypoints: none required for governance definition surface.
- governance docs: `docs/governance/GOVERNANCE_RULES_v0.1.md`, `docs/governance/BRANCH_POLICY.md`, input doc WAVE_ENFORCEMENT_COVERAGE_v1.md, `docs/governance/DRIFT_REPORT_v2.md`.

## Enforcement Hooks
- test files: governance-specific tests are indirect via rule-enforcing suites in `tests/`.
- CI workflows: `.github/workflows/ci_pytest.yml`, `.github/workflows/ci_schema_check.yml`, `.github/workflows/change_classifier.yml`.
- validators: `scripts/governance/classify_change.py`, `scripts/ci/verify_schema_objects.py`.
- sha256 / seal checks: governance-aligned seal artifacts in `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.sha256`.
If enforcement is incomplete, state explicitly: policy-level human ratification remains required for Class B changes.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: governance paths remain periodically checked against organization policy using `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md`, `docs/governance/OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md`, and `docs/governance/OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md`.
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: governance linkage spans `docs/`, `scripts/`, `tests/`, and `.github/`.

## Change Policy
Allowed:
- additive governance docs
- new tests for governance claims
- new versioned contracts and schemas
- forward-only evolution through contract protocol

Disallowed:
- breaking contract changes without evolution protocol
- bypassing ratification for governance/contract changes
- silent invariant mutation in canonical governance text

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md`

## Unassigned / Edge Cases
- `docs/path2/ROADMAP_v0_1.md` — outside frozen W1–W6 governance ownership, routed to `MOD-UNASSIGNED`.
- `docs/README_ORG_NOTES.md` — organizational note with uncertain canonical status, routed to `MOD-UNASSIGNED`.
