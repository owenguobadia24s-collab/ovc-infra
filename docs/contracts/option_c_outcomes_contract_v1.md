# Option C: Outcomes Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

---

## 1. Purpose

Option C computes forward-looking outcomes from Option B derived features. It is the ONLY layer permitted to use lookahead (future prices).

---

## 2. Inputs (Authoritative Sources)

| Source | View | Description |
|--------|------|-------------|
| L1 features | `derived.v_ovc_l1_features_v0_1` | Block physics |
| L2 features | `derived.v_ovc_l2_features_v0_1` | Structural features |
| L3 features | `derived.v_ovc_l3_features_v0_1` | Regime/trend |

---

## 3. Outputs (Data Products)

### 3.1 v1 Authoritative Output

| Output | Type | Source Definition |
|--------|------|-------------------|
| `derived.v_ovc_c_outcomes_v0_1` | View | `sql/derived/v_ovc_c_outcomes_v0_1.sql` |

### 3.2 DEPRECATED (Runner Implementation)

| Output | Type | Status |
|--------|------|--------|
| `derived.ovc_outcomes_v0_1` | View | **DEPRECATED** — Reads from canonical table directly |
| `derived.ovc_scores_v0_1` | View | **DEPRECATED** — Built on deprecated outcomes |

**v1 Resolution**: `derived.v_ovc_c_outcomes_v0_1` is the authoritative outcomes view. It reads from L1/L2/L3 views per contract. The legacy `derived.ovc_outcomes_v0_1` is deprecated because it reads directly from the canonical table.

---

## 4. Outcome Definitions

### 4.1 v1 Active Outcomes

| Outcome | Definition | Domain |
|---------|------------|--------|
| `fwd_ret_1` | `(close[T+1] - close[T]) / close[T]` | Signed float |
| `fwd_ret_3` | `(close[T+3] - close[T]) / close[T]` | Signed float |
| `fwd_ret_6` | `(close[T+6] - close[T]) / close[T]` | Signed float |
| `mfe_3` | `max(0, (max(high[T+1..T+3]) - close[T]) / close[T])` | [0, ∞) |
| `mfe_6` | `max(0, (max(high[T+1..T+6]) - close[T]) / close[T])` | [0, ∞) |
| `mae_3` | `max(0, (close[T] - min(low[T+1..T+3])) / close[T])` | [0, ∞) |
| `mae_6` | `max(0, (close[T] - min(low[T+1..T+6])) / close[T])` | [0, ∞) |
| `rvol_6` | Sample stddev of returns `ret[T+1..T+6]` | [0, ∞) |

### 4.2 NULL Handling

- NULL if anchor close is zero or NULL
- NULL if insufficient forward bars exist
- No sentinel values (-999, NaN literals, etc.)

---

## 5. Canonical vs Derived Rules

### 5.1 Option C MUST

- Read ONLY from Option B views (`v_ovc_l1_features_v0_1`, etc.)
- Use lookahead ONLY for outcome computation
- Produce deterministic results for same input

### 5.2 Option C MUST NOT

- Read from `ovc.ovc_blocks_v01_1_min` directly
- Write to canonical tables
- Modify input data

---

## 6. Versioning & Naming

### 6.1 View Naming

```
derived.v_ovc_c_outcomes_v{major}_{minor}
```

### 6.2 Column Naming

Outcome columns follow pattern: `{outcome}_{horizon}`
- `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_6`
- `mfe_3`, `mfe_6`
- `mae_3`, `mae_6`
- `rvol_6`

---

## 7. Run Provenance

| Mechanism | Table | Fields |
|-----------|-------|--------|
| View execution | `derived.eval_runs` | `run_id`, `eval_version`, `formula_hash`, `horizon_spec`, `computed_at` |

For scheduled runs:
```
run_id format: c_{GITHUB_RUN_ID}_{ATTEMPT}_{SHA_SHORT}_{RUN_NUMBER}
```

---

## 8. Allowed Dependencies

| Dependency | Allowed |
|------------|---------|
| `derived.v_ovc_l1_features_v0_1` | ✅ |
| `derived.v_ovc_l2_features_v0_1` | ✅ |
| `derived.v_ovc_l3_features_v0_1` | ✅ |
| `ovc.ovc_blocks_v01_1_min` | ❌ (PROHIBITED) |
| Threshold config | ❌ (use L3 view passthrough) |

---

## 9. Workflow Requirements

### 9.1 v1 Scheduled Workflow

`ovc_option_c_schedule.yml` MUST:
1. Reference the correct script path: `scripts/run/run_option_c.sh`
2. Produce run artifacts in `reports/runs/<run_id>/`
3. Log run metadata to `derived.eval_runs`

### 9.2 Validation Gate

Before evidence generation, verify:
- Outcomes view returns rows
- No unexpected NULLs in forward windows with sufficient data
- Determinism check (same input → same output)

---

## 10. Migration: Outcome View Alignment

### 10.1 Current State (Fracture F5)

| Consumer | Uses | Problem |
|----------|------|---------|
| Option C runner | `derived.ovc_outcomes_v0_1` | Reads from canonical table |
| Path1 evidence | `derived.v_ovc_c_outcomes_v0_1` | Reads from Option B views |

### 10.2 v1 Resolution

- **Authoritative**: `derived.v_ovc_c_outcomes_v0_1`
- **Action**: Update Option C runner workflow to NOT use deprecated view
- **Evidence**: Path1 already uses authoritative view (no change needed)

---

## 11. Compliance Checklist

| # | Requirement | Verified By |
|---|-------------|-------------|
| 1 | Reads only from Option B views | SQL review |
| 2 | Does not read canonical table | SQL review |
| 3 | Outcomes match spec definitions | Unit tests |
| 4 | NULL handling correct | Unit tests |
| 5 | Deterministic output | Replay test |
| 6 | Run provenance logged | `eval_runs` query |
| 7 | Workflow script path correct | CI sanity check |
