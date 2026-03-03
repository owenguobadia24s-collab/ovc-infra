# MOD-B — Derived System (v0.1)

## Definition
MOD-B classifies deterministic derived computation and threshold-registry surfaces for C1/C2/C3, grounded in `OVC ARCHITECTURAL WAVES v2.md` sections `W2 — Derived & Boundary Formalization` and `W3 — Structural Crystallization Event`, plus `docs/contracts/option_b_derived_contract_v1.md`.

Coverage: FULL
Derived contracts, SQL layers, runtime computation, and enforcement tests are present in tracked non-archive paths.

## Wave Span
- W2 — deterministic derived metrics and explicit layer boundaries are introduced (`OVC ARCHITECTURAL WAVES v2.md`, W2).
- W3 — contract-governed option structure and doctrine alignment are crystallized (`OVC ARCHITECTURAL WAVES v2.md`, W3).

## Core Invariants
- MUST compute C1/C2/C3 derived outputs deterministically from canonical facts and versioned thresholds.
- MUST preserve explicit B-layer boundaries and contract-defined feature semantics.
- MUST NOT mutate Option A canonical facts from derived pipelines.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `src/derived/**`
- `src/config/**`
- `configs/threshold_packs/**`
- `contracts/derived_feature_set_v0.1.json`
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `sql/03_qa_derived_validation_v0_1.sql`
- `sql/04_threshold_registry_v0_1.sql`
- `sql/05_c3_regime_trend_v0_1.sql`
- `sql/06_state_plane_threshold_pack_v0_2.sql`
- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `sql/derived/v_ovc_c3_features_v0_1.sql`
- `docs/specs/OPTION_B*.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `tests/test_derived_features.py`
- `tests/test_c3_regime_trend.py`
- `tests/test_threshold_registry.py`
- `tests/test_validate_derived.py`

### Excludes (Path Patterns)
- `_archive/**`
- `_quarantine/**`

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `src/derived/**`
- Attachment rule: attach when script computes B-layer deterministic features.
- Evidence reference: `docs/contracts/option_b_derived_contract_v1.md`.
- Pattern: `sql/derived/v_ovc_c*_features_v0_1.sql`
- Attachment rule: attach when view defines C-layer derivation semantics.
- Evidence reference: `docs/specs/OPTION_B_C1_FEATURES_v0.1.md`, `docs/specs/OPTION_B_C2_FEATURES_v0.1.md`, `docs/specs/OPTION_B_C3_FEATURES_v0.1.md`.
- Pattern: `configs/threshold_packs/**`
- Attachment rule: attach when file is versioned threshold-pack input for C3.
- Evidence reference: `tests/test_threshold_registry.py`.

## Primary Directories
- `src/derived` — runtime derived computation; matched by `src/derived/**`.
- `src/config` — threshold registry runtime interfaces; matched by `src/config/**`.
- `configs/threshold_packs` — versioned threshold inputs; matched by `configs/threshold_packs/**`.
- `sql/derived` — C1/C2/C3 derived views; matched by explicit `sql/derived/v_ovc_c*_features_v0_1.sql`.
- `docs/specs` — Option B specification set; matched by `docs/specs/OPTION_B*.md`.
- `tests` — derived deterministic enforcement tests; matched by explicit test paths.

## Canonical Artifacts
- contracts: `contracts/derived_feature_set_v0.1.json`, `docs/contracts/option_b_derived_contract_v1.md`, `docs/contracts/c3_semantic_contract_v0_1.md`.
- SQL migrations/views: `sql/02_derived_c1_c2_tables_v0_1.sql`, `sql/04_threshold_registry_v0_1.sql`, `sql/05_c3_regime_trend_v0_1.sql`, `sql/derived/v_ovc_c1_features_v0_1.sql`, `sql/derived/v_ovc_c2_features_v0_1.sql`, `sql/derived/v_ovc_c3_features_v0_1.sql`.
- Python entrypoints: `src/derived/compute_c1_v0_1.py`, `src/derived/compute_c2_v0_1.py`, `src/derived/compute_c3_regime_trend_v0_1.py`, `src/config/threshold_registry_cli.py`.
- governance docs: `docs/specs/OPTION_B_CHARTER_v0.1.md`, `docs/specs/OPTION_B_C3_IMPLEMENTATION_CONTRACT_v0.1.md`.

## Enforcement Hooks
- test files: `tests/test_derived_features.py`, `tests/test_c3_regime_trend.py`, `tests/test_threshold_registry.py`, `tests/test_validate_derived.py`.
- CI workflows: `.github/workflows/ci_pytest.yml`, `.github/workflows/ci_schema_check.yml`.
- validators: `src/validate/validate_derived_range_v0_1.py`, `scripts/validate/run_qa_validation_pack.py`.
- sha256 / seal checks: threshold pack provenance fields enforced in runtime and tests; no dedicated independent seal workflow for MOD-B-only surfaces.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: derived governance and enforcement span `docs/specs/OPTION_B*.md`, `tests/test_validate_derived.py`, and `.github/workflows/ci_pytest.yml`.
- `docs/governance/DRIFT_REPORT_v2.md` / `2. Quarantine Layer (LOW–MEDIUM)`: dormant alternative `_quarantine/src/derived/compute_c3_stub_v0_1.py` remains outside active carve.

## Change Policy
Allowed:
- additive B-layer docs and tests
- additive versioned threshold packs
- additive SQL views/tables with forward-only evolution
- additive validators and CI checks

Disallowed:
- breaking contract changes without evolution protocol
- writes from derived runtime to canonical Option A facts
- silent threshold semantics mutation

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md`

## Unassigned / Edge Cases
- `_quarantine/src/derived/compute_c3_stub_v0_1.py` — NEEDS_REVIEW, routed to `MOD-UNASSIGNED`.
- `sql/derived/v_ovc_state_plane_v0_2.sql` — assigned to evidence/state-plane module (`MOD-D`), not MOD-B.
