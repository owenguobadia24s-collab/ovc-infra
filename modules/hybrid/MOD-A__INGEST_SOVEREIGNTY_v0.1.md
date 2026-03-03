# MOD-A — Ingest Sovereignty (v0.1)

## Definition
MOD-A classifies ingest authority surfaces that establish canonical fact entry via Option A contracts and ingest pipelines, grounded in `OVC ARCHITECTURAL WAVES v2.md` section `W1 — Ingest Sovereignty` and `docs/contracts/option_a_ingest_contract_v1.md`.

Coverage: FULL
Primary ingest, contract, schema, workflow, and boundary tests are present in tracked non-archive paths.

## Wave Span
- W1 — Ingest sovereignty invariant is explicitly introduced in `OVC ARCHITECTURAL WAVES v2.md` (`W1 — Ingest Sovereignty`).
- W2 — Boundary formalization extends ingest-to-derived contract edges (`W2 — Derived & Boundary Formalization`).

## Core Invariants
- MUST ingest canonical facts through Option A contract surfaces and canonical schema DDL.
- MUST NOT bypass Option A by writing downstream derived/outcome layers as source-of-truth ingest.
- MUST preserve export contract compatibility for canonical fact emission.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `infra/ovc-webhook/**`
- `src/backfill*_checkpointed.py`
- `src/backfill_day.py`
- `src/ingest_history_day.py`
- `src/history_sources/**`
- `contracts/export_contract_v0.1*.json`
- `sql/00_schema.sql`
- `sql/01_tables_min.sql`
- `docs/contracts/option_a*.md`
- `.github/workflows/backfill*.yml`
- `tests/test_min_contract_validation.py`
- `tests/test_contract_equivalence.py`
- contracts/export_contract_v0.1.1_min_sample.txt

### Excludes (Path Patterns)
- `_archive/**`
- `_quarantine/**`

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `infra/ovc-webhook/**`
- Attachment rule: attach when path is ingress worker logic for canonical facts.
- Evidence reference: `docs/contracts/option_a_ingest_contract_v1.md`.
- Pattern: `.github/workflows/backfill*.yml`
- Attachment rule: attach when workflow executes Option A backfill or validation chain.
- Evidence reference: `.github/workflows/backfill.yml`, `.github/workflows/backfill_m15.yml`.
- Pattern: `contracts/export_contract_v0.1*.json`
- Attachment rule: attach when file constrains canonical export structure.
- Evidence reference: `tests/test_min_contract_validation.py`.

## Primary Directories
- `infra/ovc-webhook` — canonical ingest worker boundary; matched by `infra/ovc-webhook/**`.
- `src/history_sources` — ingest history source adapters; matched by `src/history_sources/**`.
- `contracts` — export contract schemas; matched by `contracts/export_contract_v0.1*.json`.
- `sql` — canonical ingest schema surfaces; matched by `sql/00_schema.sql` and `sql/01_tables_min.sql`.
- `.github/workflows` — ingest workflows; matched by `.github/workflows/backfill*.yml`.
- `tests` — ingest/contract tests; matched by explicit test paths.

## Canonical Artifacts
- contracts: `contracts/export_contract_v0.1.1_min.json`, `contracts/export_contract_v0.1_min.json`.
- SQL migrations/views: `sql/00_schema.sql`, `sql/01_tables_min.sql`.
- Python entrypoints: `src/backfill_oanda_2h_checkpointed.py`, `src/backfill_oanda_m15_checkpointed.py`, `src/ingest_history_day.py`.
- governance docs: `docs/contracts/option_a_ingest_contract_v1.md`, `docs/contracts/option_a1_bar_ingest_contract_v1.md`, `docs/contracts/option_a2_event_ingest_contract_v1.md`.

## Enforcement Hooks
- test files: `tests/test_min_contract_validation.py`, `tests/test_contract_equivalence.py`.
- CI workflows: `.github/workflows/backfill.yml`, `.github/workflows/backfill_m15.yml`, `.github/workflows/backfill_then_validate.yml`.
- validators: `src/validate_range.py`, `src/validate_day.py`.
- sha256 / seal checks: none specific to Option A ingest surface in active non-archive scope.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: ingest enforcement spans `.github/workflows/backfill.yml` and `tests/test_min_contract_validation.py`.
- `docs/governance/DRIFT_REPORT_v2.md` / `2. Quarantine Layer (LOW–MEDIUM)`: related dormant ingest paths exist in `_quarantine/src/full_ingest_stub.py` and `_quarantine/.github/workflows/ovc_full_ingest.yml`.

## Change Policy
Allowed:
- additive docs for Option A behavior
- new ingest tests and validators
- forward-only versioned contract additions
- additive workflow hardening without bypassing Option A boundaries

Disallowed:
- breaking contract changes without evolution protocol
- bypassing canonical ingest boundary via downstream layers
- silent mutation of Option A invariant semantics

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/contracts/option_a_ingest_contract_v1.md`

## Unassigned / Edge Cases
- `_quarantine/src/full_ingest_stub.py` — NEEDS_REVIEW, routed to `MOD-UNASSIGNED`.
- `_quarantine/.github/workflows/ovc_full_ingest.yml` — NEEDS_REVIEW, routed to `MOD-UNASSIGNED`.
