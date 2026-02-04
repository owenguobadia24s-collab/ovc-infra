# OVC Governance Completeness Scorecard v0.1

**Version**: 0.1
**Status**: PHASE 1.5 GOVERNANCE ARTIFACT
**Date**: 2026-02-04

---

## Executable Inventory Basis

Total executable files in repository (excluding .venv, node_modules, __pycache__, .pytest_cache, .pytest-tmp2, .wrangler, Tetsu/.obsidian, testdir/testdir2):

| Extension | Count |
|-----------|-------|
| .py | 74 |
| .ps1 | 11 |
| .sh | 2 |
| .ts | 4 |
| .sql (infrastructure DDL/DML) | 30 |
| .sql (generated run artifacts — study_*.sql in sql/path1/evidence/runs/) | ~105 |
| .sql (path1 score/study/view templates) | 26 |
| .yml (CI workflows) | 13 |
| **Total (all)** | **265** |

### Classification Note

Generated SQL run artifacts (`sql/path1/evidence/runs/p1_*/study_*.sql`, ~105 files) are **outputs of OP-D02/OP-D03**, not independent operations. They are mapped to those operations as evidence anchors. Path1 score definitions, study templates, and evidence views (`sql/path1/scores/`, `sql/path1/studies/`, `sql/path1/evidence/v_*.sql`, ~26 files) are supporting SQL for the Path1 evidence system and are mapped under OP-D02.

**Governance-relevant executables** (excluding generated run outputs): **160**

| Category | Count | Mapped to Operations |
|----------|-------|---------------------|
| Python scripts & libraries (src/, scripts/, tools/, .codex/, trajectory_families/) | 74 | All 74 mapped |
| PowerShell scripts | 11 | All 11 mapped |
| Shell scripts | 2 | Both mapped |
| TypeScript files | 4 | All 4 mapped |
| SQL infrastructure (DDL/DML/views/QA) | 30 | All 30 mapped |
| SQL path1 support (scores/studies/views) | 26 | Mapped under OP-D02 |
| CI workflows (.yml) | 13 | All 13 mapped |
| **Subtotal mapped** | **160** | — |
| SQL generated run artifacts | ~105 | Outputs of OP-D02/OP-D03 |

---

## Metric 1: Executable Mapping Coverage

**Formula**: (# executables mapped to operations / total governance-relevant executables) × 100

- Executables mapped: **160**
- Total governance-relevant executables: **160**
- Generated run artifacts (mapped as outputs): **~105**

**Score: 160 / 160 = 100.0%**

All governance-relevant executables appear in exactly one operation in the AOC. Generated SQL run artifacts are classified as outputs of their generating operations.

---

## Metric 2: Operation Evidence Coverage

**Formula**: (# canonical ops with evidence anchors / total canonical ops) × 100

Canonical operations (Options A, B, C, D, QA): **31**

| Operation | Has Evidence Anchors? |
|-----------|----------------------|
| OP-A01 | YES — index.ts, tests, contracts |
| OP-A02 | YES — script, workflow, run artifacts |
| OP-A03 | YES — script, workflow, contract |
| OP-A04 | YES — SQL files, migrations, CI |
| OP-B01 | YES — script, SQL, tests, workflow |
| OP-B02 | YES — script, SQL, tests, workflow |
| OP-B03 | YES — SQL view, contract, CI |
| OP-B04 | YES — script, SQL, tests, run artifacts |
| OP-B05 | YES — SQL views, migrations, CI |
| OP-B06 | YES — SQL DDL, migrations |
| OP-B07 | YES — SQL, script, tests, configs |
| OP-B08 | YES — script, SQL, tests, workflow |
| OP-C01 | YES — SQL view, contract, CI |
| OP-C02 | YES — scripts, workflow, SQL, contract |
| OP-D01 | YES — script, contract, reports |
| OP-D02 | YES — script, workflow, contract |
| OP-D03 | YES — script, workflow, INDEX.md |
| OP-D04 | YES — script, workflow gate |
| OP-D05 | YES — script, workflow |
| OP-D06 | YES — script |
| OP-D07 | YES — script, SQL |
| OP-D08 | YES — script, library, tests, fixtures |
| OP-D09 | YES — script, tests, changelog |
| OP-D10 | YES — script |
| OP-D11 | YES — script, workflow, SQL |
| OP-QA01 | YES — scripts, SQL, tests |
| OP-QA02 | YES — test files, workflow |
| OP-QA03 | YES — script, SQL, workflow |
| OP-QA04 | YES — workflow (self-contained) |
| OP-QA05 | YES — scripts, codex runs |
| OP-QA06 | YES — SQL files |

- Canonical ops with evidence anchors: **31**
- Total canonical ops: **31**

**Score: 31 / 31 = 100.0%**

---

## Metric 3: Enforcement Coverage

**Formula**: (# ops at C3 or higher / total canonical ops) × 100

From the ECM v0.1:

| Coverage Level | Count | Operations |
|---|---|---|
| C5 | 4 | OP-B01, OP-B02, OP-B08, OP-D03 |
| C4 | 8 | OP-A02, OP-A04, OP-B04, OP-C02, OP-D01, OP-D02, OP-D11, OP-QA01 |
| C3 | 14 | OP-A01, OP-A03, OP-B03, OP-B05, OP-B06, OP-B07, OP-C01, OP-D04, OP-D05, OP-D08, OP-D09, OP-QA02, OP-QA03, OP-QA04 |
| C2 | 5 | OP-D06, OP-D07, OP-D10, OP-QA05, OP-QA06 |

- Ops at C3 or higher: **26**
- Total canonical ops: **31**

**Score: 26 / 31 = 83.9%**

---

## Metric 4: Orphan Rate

**Formula**: # executables not mapped to any operation

- Orphan executables: **0**

All 160 governance-relevant executables are mapped. All ~105 generated SQL run artifacts are accounted for as outputs of OP-D02/OP-D03.

**Score: 0 orphans**

---

## Metric 5: Weak Governance List

Operations at C0, C1, or C2 with reason:

| Operation | Level | Reason |
|-----------|-------|--------|
| OP-D06 (Seal Manifests) | C2 | Runtime SHA256 + idempotent sealing exist, but no CI gate invokes sealing automatically. Sealing is a manual/ad-hoc operation. |
| OP-D07 (State Plane Trajectory) | C2 | Runtime computation exists but no CI gate, no unit tests, and no run artifact ledger. CLI-only invocation. |
| OP-D10 (Queue Resolved Generation) | C2 | Runtime reconciliation script exists with INDEX.md cross-reference, but no CI gate and no tests. Output is generated/derived, not authoritative. |
| OP-QA05 (Coverage Audit — Codex) | C2 | Audit harness exists but no CI gate runs it automatically. Manual invocation only via PowerShell runner. |
| OP-QA06 (SQL QA Validation Packs) | C2 | Runtime SQL validation queries exist and are invoked within pipeline scripts, but no standalone CI gate runs them independently. |

**Total weak governance operations: 5 / 31 (16.1%)**

---

## Summary Dashboard

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Executable Mapping Coverage | 100.0% | 100% | PASS |
| Operation Evidence Coverage | 100.0% | 100% | PASS |
| Enforcement Coverage (C3+) | 83.9% | 80% | PASS |
| Orphan Rate | 0 | 0 | PASS |
| Weak Governance Operations | 5 (16.1%) | <25% | PASS |

---

## Known Gaps (Bounded)

These gaps are identified, documented, and bounded — they do not represent unmapped or ungoverned executables:

1. **OP-B04 (C3 Materialized)**: Workflow invocation missing `--threshold-pack` and `--scope` args. CLI works; CI integration incomplete. Documented in `option_b_derived_contract_v1.md` section 5.1.

2. **C3 View Unit Tests**: No dedicated unit test file for `v_ovc_c3_features_v0_1.sql`. C3 materialized has tests (`test_c3_regime_trend.py`), but the stateless view is tested only via schema existence check.

3. **Worker Deployment Status**: Cloudflare Worker deployment is UNKNOWN from repo evidence alone. Code compiles and tests pass, but no deployment log exists in repo.

4. **Dormant Workflows**: `ovc_full_ingest.yml` and `backfill_then_validate.yml` are manual-dispatch only with no schedule. Classified NON_CANONICAL (OP-NC28) and canonical (OP-A02 uses `backfill.yml` instead) respectively.

5. **Migration Ledger Verification**: `schema/applied_migrations.json` entries are all UNVERIFIED (null `applied_at`/`applied_by`). Existence is CI-checked but content verification is not automated.

---

*End of Governance Completeness Scorecard v0.1*
