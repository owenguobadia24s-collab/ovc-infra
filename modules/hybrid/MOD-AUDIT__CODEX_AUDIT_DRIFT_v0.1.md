# MOD-AUDIT — Codex Audit Drift (v0.1)

## Definition
MOD-AUDIT classifies machine-audit and drift-classification surfaces that are read-only and fail-closed, grounded in `OVC ARCHITECTURAL WAVES v2.md` section `W6 — Machine Audit & Classification Consciousness` and `docs/governance/DRIFT_REPORT_v2.md`.

Coverage: FULL
Audit harness, prompts, cartographer pipeline, CI wiring, and associated test surfaces are present in tracked active paths.

## Wave Span
- W6 — repository must be machine-auditable and fail-closed (`OVC ARCHITECTURAL WAVES v2.md`, W6).

## Core Invariants
- MUST run audit checks read-only and fail-closed.
- MUST classify drift using explicit deterministic artifacts, not guesses.
- MUST NOT mutate canonical state as part of audit interpretation.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `.codex/CHECKS/**`
- `.codex/PROMPTS/**`
- `scripts/repo_cartographer/**`
- `.github/workflows/repo_cartographer.yml`
- `tests/test_repo_cartographer_*.py`
- `tools/audit_interpreter/**`
- `artifacts/repo_cartographer/**`
- `artifacts/repo_cartographer_proposals/**`
- `docs/catalogs/REPO_CARTOGRAPHER_*`
- `reports/pipeline_audit/**`
- .codex/**
- scripts/governance/build_module_candidates_v0_*.py
- tests/test_module_candidates_v0_1.py

### Excludes (Path Patterns)
- `.codex/_scratch/**`
- `_archive/**`

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `.codex/CHECKS/**` and `.codex/PROMPTS/**`
- Attachment rule: attach when file defines pass-based read-only audit harness behavior.
- Evidence reference: `.codex/CHECKS/coverage_audit.py`, `.codex/PROMPTS/PASS_3_DRIFT_CONTRADICTIONS.md`.
- Pattern: `scripts/repo_cartographer/**`
- Attachment rule: attach when script classifies ownership and drift surfaces deterministically.
- Evidence reference: `scripts/repo_cartographer/cartographer.py`.
- Pattern: `.github/workflows/repo_cartographer.yml`
- Attachment rule: attach when workflow executes fail-closed cartographer pipeline.
- Evidence reference: `.github/workflows/repo_cartographer.yml`.

## Primary Directories
- `.codex/CHECKS` — machine audit checks; matched by `.codex/CHECKS/**`.
- `.codex/PROMPTS` — pass prompts for deterministic audit phases; matched by `.codex/PROMPTS/**`.
- `scripts/repo_cartographer` — cartographer pipeline; matched by `scripts/repo_cartographer/**`.
- `tools/audit_interpreter` — audit interpretation toolchain; matched by `tools/audit_interpreter/**`.
- `artifacts/repo_cartographer` — sealed cartographer outputs; matched by `artifacts/repo_cartographer/**`.
- `tests` — cartographer enforcement tests; matched by `tests/test_repo_cartographer_*.py`.

## Canonical Artifacts
- contracts: `docs/contracts/AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1.md`.
- SQL migrations/views: none required for core MOD-AUDIT ownership.
- Python entrypoints: `.codex/CHECKS/coverage_audit.py`, `scripts/repo_cartographer/cartographer.py`, `tools/audit_interpreter/src/audit_interpreter/cli.py`.
- governance docs: `docs/governance/DRIFT_REPORT_v2.md`, input doc WAVE_ENFORCEMENT_COVERAGE_v1.md.

## Enforcement Hooks
- test files: `tests/test_repo_cartographer_phase_b_chain.py`, `tests/test_repo_cartographer_phase_b_latest_ok.py`, `tests/test_repo_cartographer_phase_b6_publish_latest_summary.py`, `tests/test_repo_cartographer_phase_b7_unknown_frontier.py`, `tests/test_repo_cartographer_phase_c_rule_proposal.py`.
- CI workflows: `.github/workflows/repo_cartographer.yml`.
- validators: fail-closed checks embedded in `scripts/repo_cartographer/phase_b_latest_ok_run.py`.
- sha256 / seal checks: `artifacts/repo_cartographer/20260218_142951Z/MANIFEST.sha256`, `artifacts/repo_cartographer/20260218_142951Z/SEAL.sha256`.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: audit coverage intentionally spans docs, scripts, tests, workflows, and artifacts.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: audit reports and ownership summaries remain in artifact trees (`artifacts/repo_cartographer/**`) and require explicit attachment discipline.

## Change Policy
Allowed:
- additive audit prompts and checks
- additive cartographer tests
- additive versioned audit contracts
- forward-only fail-closed pipeline evolution

Disallowed:
- bypassing read-only/fail-closed audit posture
- unsealed mutation of archived audit outputs
- silent drift-logic mutation without governance trace

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/DRIFT_REPORT_v2.md`
- `.codex/PROMPTS/PASS_0_OPERATING_RULES.md`

## Unassigned / Edge Cases
- `.codex/_scratch/**` — non-canonical scratch analysis, routed to `MOD-UNASSIGNED`.
- `artifacts/repo_census.json` — shared census output, routed to `MOD-UNASSIGNED`.
