# MOD-UI — Phase 3 Control Panel (v0.1)

## Definition
MOD-UI classifies the read-only Phase 3 control panel surfaces and its audit contracts, grounded in `tools/phase3_control_panel/README.md` and `OVC ARCHITECTURAL WAVES v2.md` (`W6 — Machine Audit & Classification Consciousness`).

Coverage: FULL
Phase 3 UI/runtime/audit assets are present in tracked paths under `tools/phase3_control_panel/**` and `docs/phase_3/**`.

## Wave Span
- W5 — operational health visibility and registry surfaces are consumed by UI views.
- W6 — machine-auditable, read-only, fail-closed constraints are explicitly enforced.

## Core Invariants
- MUST provide read-only visibility with no write authority.
- MUST enforce no network mutation and no action-trigger affordances.
- MUST trace displayed data to canonical sealed artifacts and governance sources.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `tools/phase3_control_panel/**`
- `docs/phase_3/**`
- docs/specs/system/dashboards_v0.1.md

### Excludes (Path Patterns)
- `_archive/**`

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `tools/phase3_control_panel/src/**`
- Attachment rule: attach when file implements read-only phase3 UI/server behavior.
- Evidence reference: `tools/phase3_control_panel/README.md`.
- Pattern: `tools/phase3_control_panel/audits/**`
- Attachment rule: attach when file enforces read-only/no-network-mutation/no-action invariants.
- Evidence reference: `tools/phase3_control_panel/audits/phase3_read_only_audit.py`, `tools/phase3_control_panel/audits/phase3_no_network_mutation_audit.py`, `tools/phase3_control_panel/audits/phase3_ui_action_audit.py`.
- Pattern: `tools/phase3_control_panel/docs/contracts/**`
- Attachment rule: attach when file defines schema contract for consumed canonical artifacts.
- Evidence reference: `tools/phase3_control_panel/docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.md`.

## Primary Directories
- `tools/phase3_control_panel/src` — UI/runtime source code; matched by `tools/phase3_control_panel/**`.
- `tools/phase3_control_panel/audits` — audit enforcement scripts; matched by `tools/phase3_control_panel/**`.
- `tools/phase3_control_panel/docs/contracts` — phase3 schema contracts; matched by `tools/phase3_control_panel/**`.
- `docs/phase_3` — phase3 architecture validation reports; matched by `docs/phase_3/**`.

## Canonical Artifacts
- contracts: `tools/phase3_control_panel/docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.md`, `tools/phase3_control_panel/docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.json`.
- SQL migrations/views: none required for MOD-UI ownership.
- Python entrypoints: `tools/phase3_control_panel/audits/phase3_read_only_audit.py`, `tools/phase3_control_panel/audits/phase3_no_network_mutation_audit.py`, `tools/phase3_control_panel/audits/phase3_ui_action_audit.py`.
- governance docs: `docs/phase_3/PHASE_3_ARCHITECTURE_VALIDATION_REPORT_v0_1.md`, `tools/phase3_control_panel/README.md`.

## Enforcement Hooks
- test files: enforcement is audit-script based within phase3 package.
- CI workflows: no dedicated root-level `phase3` workflow file is present in current tracked set.
- validators: `tools/phase3_control_panel/audits/phase3_read_only_audit.py`, `tools/phase3_control_panel/audits/phase3_no_network_mutation_audit.py`, `tools/phase3_control_panel/audits/phase3_ui_action_audit.py`.
- sha256 / seal checks: phase3 consumes sealed artifacts from registry layer; it does not generate phase3-specific seals.
If enforcement is incomplete, state explicitly: no dedicated root workflow is currently scoped only to phase3 audit execution.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: phase3 ownership intentionally spans `tools/` and `docs/`.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: phase3 governance dependencies include root-level governance references that remain outside `docs/governance/`.

## Change Policy
Allowed:
- additive read-only UI docs
- additive phase3 audit tests and scripts
- additive versioned schema contract revisions
- forward-only read-model evolution

Disallowed:
- introducing mutation endpoints or write credentials
- bypassing phase3 audit checks
- silent mutation of phase3 read-only invariants

Grounding:
- `tools/phase3_control_panel/README.md`
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/BRANCH_POLICY.md`

## Unassigned / Edge Cases
- `tools/phase3_control_panel` missing-case fallback is not active in this snapshot because tracked paths exist.
- Any future UI path outside `tools/phase3_control_panel/**` is `NEEDS_REVIEW` and routed to `MOD-UNASSIGNED`.
