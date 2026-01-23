# QA: Validation Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

---

## 1. Purpose

QA validates correctness, coverage, and determinism across all pipeline layers. QA is read-only and produces no data products consumed by other layers.

---

## 2. Inputs (All Layers - Read Only)

| Source | Purpose |
|--------|---------|
| `ovc.ovc_blocks_v01_1_min` | Canonical facts validation |
| `ovc.ovc_candles_m15_raw` | M15 coverage validation |
| `derived.v_ovc_c1_features_v0_1` | Derived C1 validation |
| `derived.v_ovc_c2_features_v0_1` | Derived C2 validation |
| `derived.v_ovc_c3_features_v0_1` | Derived C3 validation |
| `derived.v_ovc_c_outcomes_v0_1` | Outcomes validation |
| Evidence packs | Path1 integrity validation |

---

## 3. Outputs (Validation Reports Only)

| Output | Location | Purpose |
|--------|----------|---------|
| Validation reports | `reports/validation/` | Human-readable results |
| Test results | CI logs / pytest output | Automated gate results |
| QC reports | `reports/path1/evidence/runs/*/qc_report.json` | Evidence pack QC |

---

## 4. Validation Gates

### 4.1 Gate Categories

| Category | Gate Name | Failure Mode |
|----------|-----------|--------------|
| **Schema** | Required objects exist | HARD FAIL |
| **Coverage** | Row count parity | HARD FAIL |
| **Integrity** | OHLC sanity | HARD FAIL |
| **Determinism** | Replay equivalence | HARD FAIL |
| **Continuity** | M15 strip integrity | WARN or FAIL |
| **Aggregation** | M15 → 2H match | WARN or FAIL |

### 4.2 PASS/FAIL Definitions

| Result | Meaning | Action |
|--------|---------|--------|
| **PASS** | All checks succeeded | Continue pipeline |
| **WARN** | Non-critical issues found | Log and continue (unless strict mode) |
| **FAIL** | Critical issues found | Block pipeline progression |

---

## 5. Required Validation Scripts

### 5.1 Canonical Facts Validation

| Script | Purpose |
|--------|---------|
| `src/validate_day.py` | Single day facts vs tape |
| `src/validate_range.py` | Date range facts vs tape |
| `sql/qa_validation_pack_core.sql` | SQL-based validation queries |

### 5.2 Derived Features Validation

| Script | Purpose |
|--------|---------|
| `src/validate/validate_derived_range_v0_1.py` | C1/C2 coverage parity |
| `sql/03_qa_derived_validation_v0_1.sql` | SQL coverage checks |

### 5.3 Evidence Validation

| Script | Purpose |
|--------|---------|
| `scripts/path1/run_replay_verification.py` | Replay determinism |
| `scripts/path1/run_seal_manifests.py` | Manifest sealing |
| `scripts/path1/validate_post_run.py` | Post-run integrity |

---

## 6. CI Integration Requirements

### 6.1 Required CI Checks

| Check | Workflow | Gate Type |
|-------|----------|-----------|
| YAML syntax | `ci_workflow_sanity.yml` | HARD FAIL |
| Script paths exist | `ci_workflow_sanity.yml` | HARD FAIL |
| Pytest suite | `ci_pytest.yml` (NEW) | HARD FAIL |
| Schema objects exist | `ci_schema_check.yml` (NEW) | HARD FAIL |

### 6.2 Required Pytest Tests

The following tests MUST pass in CI:

| Test File | Purpose |
|-----------|---------|
| `test_min_contract_validation.py` | Contract compliance |
| `test_contract_equivalence.py` | View equivalence |
| `test_validate_derived.py` | Derived validation |
| `test_threshold_registry.py` | Threshold config |
| `test_path1_replay_structural.py` | Replay structure |
| `test_fingerprint.py` | Hash stability |
| `test_fingerprint_determinism.py` | Determinism |

---

## 7. Schema Validation

### 7.1 Required Objects Check

CI MUST verify these objects exist in the database:

```sql
-- Canonical tables
SELECT 1 FROM ovc.ovc_blocks_v01_1_min LIMIT 0;
SELECT 1 FROM ovc.ovc_candles_m15_raw LIMIT 0;

-- Configuration tables
SELECT 1 FROM ovc_cfg.threshold_pack LIMIT 0;
SELECT 1 FROM ovc_cfg.threshold_pack_active LIMIT 0;

-- Derived views
SELECT 1 FROM derived.v_ovc_c1_features_v0_1 LIMIT 0;
SELECT 1 FROM derived.v_ovc_c2_features_v0_1 LIMIT 0;
SELECT 1 FROM derived.v_ovc_c3_features_v0_1 LIMIT 0;
SELECT 1 FROM derived.v_ovc_c_outcomes_v0_1 LIMIT 0;

-- Evidence views
SELECT 1 FROM derived.v_path1_evidence_dis_v1_1 LIMIT 0;
```

### 7.2 Migration Ledger Check

CI MUST verify `schema/applied_migrations.json` exists and contains expected entries.

---

## 8. Determinism Validation

### 8.1 Evidence Pack Determinism

For the same:
- `run_id`
- `sym`
- `date_from`, `date_to`
- Code version

The `data_sha256.txt` MUST be identical across rebuilds.

### 8.2 Allowed Variance

| Component | Allowed Variance |
|-----------|------------------|
| `data_sha256` | NONE (must match exactly) |
| `build_sha256` | May differ (timestamps in meta.json) |
| Float OHLC | Tolerance `1e-6` |

---

## 9. Compliance Checklist

| # | Requirement | Verified By |
|---|-------------|-------------|
| 1 | CI runs pytest suite | Workflow presence |
| 2 | CI verifies schema objects | Gate query execution |
| 3 | Validation scripts produce reports | Report file existence |
| 4 | PASS/WARN/FAIL semantics defined | This contract |
| 5 | Determinism tests included | Test file presence |
| 6 | Migration ledger checked | CI step |
