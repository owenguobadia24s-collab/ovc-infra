# Option B: Derived Features Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

---

## 1. Purpose

Option B computes derived features from canonical facts. All features are recomputable and versioned.

---

## 2. Inputs (Authoritative Sources)

| Source | Table/Config | Description |
|--------|--------------|-------------|
| Canonical facts | `ovc.ovc_blocks_v01_1_min` | 2H block OHLC |
| Threshold config | `ovc_cfg.threshold_pack` | C3 regime thresholds |
| Active threshold | `ovc_cfg.threshold_pack_active` | Current threshold version |

---

## 3. Outputs (Data Products)

### 3.1 v1 Authoritative Outputs (Split Implementation)

| Output | Type | Source Definition |
|--------|------|-------------------|
| `derived.v_ovc_c1_features_v0_1` | View | `sql/derived/v_ovc_c1_features_v0_1.sql` |
| `derived.v_ovc_c2_features_v0_1` | View | `sql/derived/v_ovc_c2_features_v0_1.sql` |
| `derived.v_ovc_c3_features_v0_1` | View | `sql/derived/v_ovc_c3_features_v0_1.sql` |
| `derived.ovc_c1_features_v0_1` | Table | `src/derived/compute_c1_v0_1.py` |
| `derived.ovc_c2_features_v0_1` | Table | `src/derived/compute_c2_v0_1.py` |

### 3.2 DEPRECATED (Legacy Implementation)

| Output | Type | Status |
|--------|------|--------|
| `derived.ovc_block_features_v0_1` | View | **DEPRECATED** — Do not use for new code |

**v1 Resolution**: The split C1/C2/C3 implementation is authoritative. The legacy combined view is deprecated and will be removed in v2.

---

## 4. Feature Layers

| Layer | Content | Example Features |
|-------|---------|------------------|
| C0 | Raw passthrough | `block_id`, `sym`, `bar_close_ms`, `o`, `h`, `l`, `c` |
| R | Immediate risk | `rng`, `ret`, `body_ratio`, `close_pos` |
| C1 | Block physics | `range`, `body`, `direction`, `gap`, rolling stats |
| C2 | Structural | `sess_high`, `sess_low`, `hh_12`, `ll_12`, structure state |
| C3 | Regime/trend | `c3_volatility_regime`, `c3_trend_bias` |

---

## 5. Canonical vs Derived Rules

### 5.1 Option B MUST

- Read ONLY from `ovc.ovc_blocks_v01_1_min` (canonical OHLC fields)
- Read configuration from `ovc_cfg.threshold_*`
- Write ONLY to `derived.*` schema

### 5.2 Option B MUST NOT

- Write to canonical tables
- Read derived fields from canonical table (even if they exist)
- Have side effects beyond derived table writes

---

## 6. Versioning & Naming

### 6.1 View Naming

```
derived.v_ovc_{layer}_features_v{major}_{minor}
```

### 6.2 Compute Script Naming

```
src/derived/compute_{layer}_v{major}_{minor}.py
```

### 6.3 Formula Hash

Each view/table MUST include a deterministic `formula_hash`:
```sql
md5('derived.v_ovc_c1_features_v0_1:v0.1:{computation_spec}')
```

---

## 7. Run Provenance

| Mechanism | Table | Fields |
|-----------|-------|--------|
| Compute scripts | `derived.derived_runs` | `run_id`, `version`, `formula_hash`, `computed_at` |

---

## 8. Allowed Dependencies

| Dependency | Allowed |
|------------|---------|
| `ovc.ovc_blocks_v01_1_min` (OHLC only) | ✅ |
| `ovc_cfg.threshold_pack` | ✅ |
| `ovc_cfg.threshold_pack_active` | ✅ |
| Other canonical tables | ❌ |
| Option C outputs | ❌ |
| Option D outputs | ❌ |

---

## 9. Workflow Requirements

### 9.1 v1 Required Workflow

`backfill_then_validate.yml` MUST invoke:
1. `compute_c1_v0_1.py` → materializes C1 table
2. `compute_c2_v0_1.py` → materializes C2 table
3. `compute_c3_regime_trend_v0_1.py` → materializes C3 table (**currently missing**)

### 9.2 Validation Gate

After compute, workflow MUST run `validate_derived_range_v0_1.py` to verify:
- Row count parity with canonical
- No NULL in required fields
- Formula hash matches expected

---

## 10. Compliance Checklist

| # | Requirement | Verified By |
|---|-------------|-------------|
| 1 | Reads only OHLC from canonical | SQL/code review |
| 2 | Writes only to derived schema | SQL/code review |
| 3 | Formula hash present | View definition |
| 4 | Run provenance logged | `derived.derived_runs` query |
| 5 | All C1/C2/C3 computes invoked | Workflow YAML |
| 6 | Validation gate passes | CI logs |
