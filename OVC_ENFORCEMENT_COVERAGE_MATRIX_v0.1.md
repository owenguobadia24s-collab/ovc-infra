# OVC Enforcement Coverage Matrix v0.1

**Version**: 0.1
**Status**: PHASE 1.5 GOVERNANCE ARTIFACT
**Date**: 2026-02-04

---

## Enforcement Surface Definitions

| Label | Name | Description |
|-------|------|-------------|
| E1 | Contract / Schema | Formal contract document or JSON schema defining inputs, outputs, rules |
| E2 | Runtime Validation | Code-level checks at execution time (assertions, guards, sanity checks) |
| E3 | Tests | Automated test suite (pytest, vitest, etc.) |
| E4 | CI Gate | GitHub Actions workflow that blocks merge or flags failure |
| E5 | Audit Harness | Coverage audit, replay verification, post-run validation, migration ledger |
| E6 | Documentation Law | Governance rules, doctrine, contracts that constrain behavior by policy |
| E7 | Run Artifact Ledger | Run artifacts (run.json, manifests, hashes) that provide provenance trail |

## Coverage Level Definitions

| Level | Name | Criteria |
|-------|------|----------|
| C0 | None | No enforcement evidence exists |
| C1 | Documentary only | Only E6 (documentation/policy) exists |
| C2 | Runtime but not gated | E2 exists but no CI gate (E4) enforces it |
| C3 | CI / audit gated | E4 or E5 present and active |
| C4 | Gated + reproducible run-artifact evidence | E4/E5 + E7 present |
| C5 | Fully governed | C4 + E1 (schema/contract) + E3 (tests) |

---

## Coverage Matrix

| Operation ID | Option | Enforcement Surfaces | Coverage Level | Justification |
|---|---|---|---|---|
| OP-A01 | A | E1, E3, E6 | C3 | Contract (`export_contract_v0.1.1_min.json`), worker tests (2 PASS), governance rules. CI pytest runs but no dedicated CI gate verifies worker deployment. Tests exist. |
| OP-A02 | A | E1, E4, E6, E7 | C4 | Contract docs, `backfill.yml` CI workflow (scheduled), governance FROZEN status, RunWriter emits run.json. No dedicated unit tests for backfill script. |
| OP-A03 | A | E1, E4, E6 | C3 | A2 contract doc, `backfill_m15.yml` workflow (manual dispatch), governance docs. No RunWriter evidence, no unit tests. |
| OP-A04 | A | E1, E4, E5, E6 | C4 | Schema DDL with applied_migrations.json ledger, `ci_schema_check.yml` verifies objects, governance FROZEN. No unit tests of DDL itself but CI gate validates existence. |
| OP-B01 | B | E1, E2, E3, E4, E5, E7 | C5 | Option B contract, runtime formula_hash, `test_derived_features.py` (C1 determinism+correctness), `backfill_then_validate.yml` CI, derived validation harness, RunWriter artifacts. |
| OP-B02 | B | E1, E2, E3, E4, E5, E7 | C5 | Option B contract, runtime window_spec+formula_hash, `test_derived_features.py` (C2 tests), `backfill_then_validate.yml` CI, derived validation, RunWriter artifacts. |
| OP-B03 | B | E1, E4, E6 | C3 | Option B contract, `ci_schema_check.yml` verifies view existence, c3_semantic_contract. No dedicated C3 view unit tests. Stateless view (deterministic by construction). |
| OP-B04 | B | E1, E2, E3, E7 | C4 | Contract, runtime threshold_pack provenance, `test_c3_regime_trend.py` (20 tests), RunWriter. NOT in CI workflow (CLI only — known gap). Tests run via ci_pytest. |
| OP-B05 | B | E1, E4, E6 | C3 | Schema contract, `ci_schema_check.yml` verifies existence, migration ledger. Views are stateless. |
| OP-B06 | B | E1, E4, E6 | C3 | Schema DDL, `ci_schema_check.yml`, migration ledger. Materialized tables DDL verified via schema check. |
| OP-B07 | B | E1, E2, E3, E6 | C3 | Threshold registry DDL, immutable pack semantics (runtime), `test_threshold_registry.py`, documentation. CI pytest gates these tests. |
| OP-B08 | B | E1, E2, E3, E4, E5, E7 | C5 | Contract, runtime validation checks (coverage parity, NaN detection), `test_validate_derived.py` (50 tests), `backfill_then_validate.yml` CI, QA tables, RunWriter. |
| OP-C01 | C | E1, E4, E6 | C3 | Outcomes contract, `ci_schema_check.yml` verifies view, migration ledger. Stateless view. No dedicated unit tests for outcomes SQL. |
| OP-C02 | C | E1, E2, E4, E5, E7 | C4 | Eval contract JSON, runtime spotchecks, `ovc_option_c_schedule.yml` CI (daily schedule), spotcheck SQL, RunWriter + run report JSON. No unit tests for runner script. |
| OP-D01 | D | E1, E2, E3, E5, E7 | C4 | Evidence pack contract, runtime QC checks (M15 strip count, aggregation), `test_evidence_pack_manifest.py` + `test_pack_rebuild_equivalence.py`, manifest hashes (data_sha256). No dedicated CI workflow for pack build alone. |
| OP-D02 | D | E1, E2, E4, E5, E7 | C4 | Evidence contract, runtime evidence generation, `path1_evidence.yml` CI (scheduled), post-run validation, RunWriter and INDEX.md ledger. |
| OP-D03 | D | E1, E2, E4, E5, E7 | C5 | Evidence contract, date validation guards, `path1_evidence_queue.yml` + `main.yml` CI, post-run validation gate, PR creation with artifact verification, INDEX.md ledger. |
| OP-D04 | D | E2, E4, E5 | C3 | Runtime structural checks (file existence, size, fatal markers), used as gate in `path1_evidence_queue.yml`. Audit function. |
| OP-D05 | D | E2, E4, E5 | C3 | Runtime replay checks, `path1_replay_verify.yml` CI (daily schedule), structural verification. |
| OP-D06 | D | E2, E5, E7 | C2 | Runtime SHA256 computation, idempotent sealing, MANIFEST.sha256 artifacts. No CI gate invokes sealing automatically. |
| OP-D07 | D | E1, E2 | C2 | State plane contract (threshold pack), runtime computation. No CI gate, no tests, no run artifacts. |
| OP-D08 | D | E1, E2, E3 | C3 | Schema validation, runtime fingerprint generation, `test_fingerprint.py` + `test_fingerprint_determinism.py` (CI pytest gates). No run artifacts. |
| OP-D09 | D | E1, E2, E3 | C3 | Overlay spec, runtime quantization/hash, `test_overlays_v0_3_determinism.py` (CI pytest). No run artifacts, no dedicated CI gate. |
| OP-D10 | D | E2, E5 | C2 | Runtime reconciliation, INDEX.md cross-reference. No CI gate, no tests, no run artifacts. |
| OP-D11 | D | E2, E4, E7 | C4 | Runtime env validation (check_required_env), `notion_sync.yml` CI (scheduled), RunWriter artifacts. No unit tests. |
| OP-QA01 | QA | E1, E2, E3, E5, E7 | C4 | QA contract, runtime OHLC sanity checks, `test_dst_audit.py` (indirectly), QA tables + validation reports, RunWriter. No dedicated CI gate for validation (runs inside `backfill_then_validate.yml`). |
| OP-QA02 | QA | E3, E4 | C3 | Tests are the enforcement. `ci_pytest.yml` CI gate. |
| OP-QA03 | QA | E4, E5 | C3 | `ci_schema_check.yml` CI gate, `applied_migrations.json` ledger, `verify_schema_objects.py`. |
| OP-QA04 | QA | E4 | C3 | `ci_workflow_sanity.yml` CI gate (self-contained). |
| OP-QA05 | QA | E5 | C2 | Audit harness only. No CI gate runs codex checks automatically. Manual invocation. |
| OP-QA06 | QA | E2, E5 | C2 | Runtime SQL checks, QA tables. No CI gate invokes these SQL packs directly (invoked within scripts). |

---

## NON_CANONICAL Operations (Coverage Not Evaluated for Governance)

| Operation ID | Option | Note |
|---|---|---|
| OP-NC01 through OP-NC29 | NON_CANONICAL | Legacy, scaffold, utility, or exploratory. Not subject to governance coverage requirements. Listed in AOC for completeness. Coverage level: C0 (by definition — not governed). |

---

## Summary Statistics

| Coverage Level | Count (Canonical Only) | Operations |
|---|---|---|
| C5 (Fully governed) | 4 | OP-B01, OP-B02, OP-B08, OP-D03 |
| C4 (Gated + artifacts) | 8 | OP-A02, OP-A04, OP-B04, OP-C02, OP-D01, OP-D02, OP-D11, OP-QA01 |
| C3 (CI/audit gated) | 12 | OP-A01, OP-A03, OP-B03, OP-B05, OP-B06, OP-B07, OP-C01, OP-D04, OP-D05, OP-D08, OP-D09, OP-QA02, OP-QA03, OP-QA04 |
| C2 (Runtime, not gated) | 4 | OP-D06, OP-D07, OP-D10, OP-QA05, OP-QA06 |
| C1 (Documentary only) | 0 | — |
| C0 (None) | 0 | — |

**Note**: C3 count is 14 (OP-QA02, OP-QA03, OP-QA04 included). C2 count is 5 (OP-QA05, OP-QA06 included). Total canonical operations: 31.

---

*End of Enforcement Coverage Matrix v0.1*
