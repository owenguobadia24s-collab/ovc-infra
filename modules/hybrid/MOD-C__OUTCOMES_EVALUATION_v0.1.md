# MOD-C — Outcomes & Evaluation (v0.1)

## Definition
MOD-C classifies Option C outcomes and evaluation surfaces where outcomes are computed from contract-defined SQL and run wrappers, grounded in `OVC ARCHITECTURAL WAVES v2.md` sections `W2 — Derived & Boundary Formalization` and `W3 — Structural Crystallization Event`, plus `docs/contracts/option_c_outcomes_contract_v1.md`.

Coverage: FULL
Outcome contracts, SQL, run wrappers, and scheduled workflow hooks are present in tracked non-archive paths.

## Wave Span
- W2 — evaluation must be contract-defined (`OVC ARCHITECTURAL WAVES v2.md`, W2 invariant text).
- W3 — option contracts become explicit and governance-bound (`OVC ARCHITECTURAL WAVES v2.md`, W3).
- W5 — operational version control is attached via `VERSION_OPTION_C` and schedule gating.

## Core Invariants
- MUST compute outcomes through contract-defined Option C SQL and run wrapper surfaces.
- MUST enforce version visibility for Option C sensitive surface changes.
- MUST NOT mutate historical run reports silently without explicit versioned evolution.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `contracts/eval_contract_v0.1.json`
- `VERSION_OPTION_C`
- `sql/03_tables_outcomes.sql`
- `sql/derived/v_ovc_c_outcomes_v0_1.sql`
- `sql/option_c*.sql`
- `scripts/run/run_option_c*`
- `docs/specs/OPTION_C*.md`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `.github/workflows/ovc_option_c_schedule.yml`
- `reports/run_report_*`
- `reports/spotchecks_*`
- docs/contracts/option_c_boundary.md

### Excludes (Path Patterns)
- `_archive/**`
- `_quarantine/**`

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `sql/option_c*.sql`
- Attachment rule: attach when SQL defines Option C outcomes or run report extraction.
- Evidence reference: `docs/contracts/option_c_outcomes_contract_v1.md`.
- Pattern: `scripts/run/run_option_c*`
- Attachment rule: attach when script is canonical Option C execution wrapper.
- Evidence reference: `.github/workflows/ovc_option_c_schedule.yml`.
- Pattern: `VERSION_OPTION_C`
- Attachment rule: attach when file seals Option C version boundary for sensitive updates.
- Evidence reference: `.github/workflows/ovc_option_c_schedule.yml`.

## Primary Directories
- `sql` — outcomes tables/views and option-c reports; matched by explicit `sql/03_tables_outcomes.sql`, `sql/option_c*.sql`.
- `scripts/run` — Option C runtime wrappers; matched by `scripts/run/run_option_c*`.
- `docs/specs` — Option C specs; matched by `docs/specs/OPTION_C*.md`.
- `docs/contracts` — Option C contract; matched by `docs/contracts/option_c_outcomes_contract_v1.md`.
- `.github/workflows` — Option C schedule gate; matched by `.github/workflows/ovc_option_c_schedule.yml`.
- `reports` — run report and spotcheck outputs; matched by `reports/run_report_*` and `reports/spotchecks_*`.

## Canonical Artifacts
- contracts: `contracts/eval_contract_v0.1.json`, `docs/contracts/option_c_outcomes_contract_v1.md`, `docs/contracts/option_c_boundary.md`.
- SQL migrations/views: `sql/03_tables_outcomes.sql`, `sql/derived/v_ovc_c_outcomes_v0_1.sql`, `sql/option_c_v0_1.sql`, `sql/option_c_run_report.sql`, `sql/option_c_spotchecks.sql`.
- Python entrypoints: `scripts/run/run_option_c_wrapper.py`.
- governance docs: `docs/specs/OPTION_C_CHARTER_v0.1.md`, `docs/specs/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md`, `docs/specs/OPTION_C_OUTCOMES_v0.1.md`.

## Enforcement Hooks
- test files: Option C-specific test file is not explicitly isolated under `tests/` in current active surface.
- CI workflows: `.github/workflows/ovc_option_c_schedule.yml`.
- validators: wrapper-driven spotcheck outputs via `sql/option_c_spotchecks.sql`.
- sha256 / seal checks: enforcement is version-gated (`VERSION_OPTION_C`) rather than dedicated Option-C manifest seal.
If enforcement is incomplete, state explicitly: dedicated Option C unit-test target is not isolated as a standalone `tests/test_option_c*.py` file in active paths.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: Option C spans `sql/`, `scripts/`, `.github/workflows/`, and `reports/` by design.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: root-level report artifacts (`reports/run_report_*`, `reports/spotchecks_*`) remain outside subfolders and require explicit attachment rules.

## Change Policy
Allowed:
- additive Option C documentation
- additive tests and spotchecks
- additive versioned contracts and SQL
- forward-only wrapper evolution

Disallowed:
- breaking contract changes without evolution protocol
- bypassing version gate on sensitive Option C changes
- silent invariant mutation in Option C computation semantics

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md`

## Unassigned / Edge Cases
- `artifacts/option_c/sanity_local/**` — NEEDS_REVIEW, routed to `MOD-UNASSIGNED`.
- `docs/path2/ROADMAP_v0_1.md` — outside W1–W6 carve ownership, routed to `MOD-UNASSIGNED`.
