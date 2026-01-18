# Mapping Validation Report: Spec v0.1 vs Current Implementation

> **Generated**: 2025-02-19
> **Purpose**: Compare current tier assignments against C-Layer Boundary Spec v0.1
> **Scope**: All fields in `metric_map_pine_to_c_layers.md` and `derived_v0_1.sql`

---

## Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| Fields correctly classified | 48 | ✅ PASS |
| Fields with tier violations | 15 | ⚠️ MISMATCH |
| Fields with ambiguous tier | 7 | ⚠️ NEEDS DECISION |
| Fields missing window_spec | 12 | ⚠️ INCOMPLETE |

**Overall Status**: ⚠️ PARTIAL ALIGNMENT — 15 fields violate spec boundary rules

---

## 1. Tier Violation Report

### 1.1 — C1 Violations: Fields Requiring History Classified as C1

The following fields are implemented in `derived.ovc_block_features_v0_1` (documented as C1) but violate the C1 rule: *"No lookback, no history, no rolling windows"*.

| Field | Current Tier | Actual Inputs | Correct Tier | Violation |
|-------|--------------|---------------|--------------|-----------|
| `gap` | C1 (impl) | `o[0] - prev_c` | **C2** | Requires `c[-1]` |
| `sess_high` | C1 (impl) | `max(h) over session` | **C2** | Session window |
| `sess_low` | C1 (impl) | `min(l) over session` | **C2** | Session window |
| `dist_sess_high` | C1 (impl) | `sess_high - c` | **C2** | Depends on sess_high |
| `dist_sess_low` | C1 (impl) | `c - sess_low` | **C2** | Depends on sess_low |
| `roll_avg_range_12` | C1 (impl) | `avg(range) N=12` | **C2** | 12-bar window |
| `roll_std_logret_12` | C1 (impl) | `stddev(logret) N=12` | **C2** | 12-bar window |
| `range_z_12` | C1 (impl) | `(range - avg) / std` | **C2** | Depends on rolling |
| `hh_12` | C1 (impl) | `h > max(h[-12:-1])` | **C2** | 12-bar lookback |
| `ll_12` | C1 (impl) | `l < min(l[-12:-1])` | **C2** | 12-bar lookback |
| `took_prev_high` | C1 (impl) | `h > h[-1]` | **C2** | 1-bar lookback |
| `took_prev_low` | C1 (impl) | `l < l[-1]` | **C2** | 1-bar lookback |

**Impact**: 12 fields in current "C1" view are actually C2 by spec definition.

---

### 1.2 — C3 Violations: Numeric Outputs Classified as C3

The following fields are classified as C3 in `metric_map_pine_to_c_layers.md` but are numeric rolling-window outputs, which should be C2 per spec.

| Field | Current Tier | Actual Formula | Correct Tier | Violation |
|-------|--------------|----------------|--------------|-----------|
| `rd_hi` | C3 | `highest(h, rd_len)` | **C2** | Numeric rolling max |
| `rd_lo` | C3 | `lowest(l, rd_len)` | **C2** | Numeric rolling min |
| `rd_mid` | C3 | `(rd_hi + rd_lo) / 2` | **C2** | Arithmetic from rd_hi/rd_lo |

**Impact**: 3 RD fields should be C2, not C3. RD module spans tiers.

---

### 1.3 — B-Layer Violations: Non-Derivable Field

| Field | Current Tier | Issue | Correct Tier |
|-------|--------------|-------|--------------|
| `news_flag` | B | External input, not derivable from OHLC | **Metadata** or **External Table** |

**Impact**: `news_flag` violates B-layer source-agnosticism.

---

## 2. Window Specification Gaps

Per spec Section E.3, all C2+ fields must have documented `window_spec`. The following fields lack explicit specification:

| Field | Tier | Window Type | Missing Spec |
|-------|------|-------------|--------------|
| `rm` (RR mean) | C2 | Rolling | N=? not documented |
| `sd` (Stddev) | C2 | Rolling | N=? not documented |
| `or` (Open ratio) | C2 | Rolling | N=? not documented |
| `rer` (Ret ratio) | C2 | Rolling | N=? not documented |
| `mc3` | C2 | Rolling | N=3 implied but not explicit |
| `vf3` | C2 | Rolling | N=3 implied but not explicit |
| `rd_len` | C2/C3 | Parameterized | Input parameter, not versioned |
| `kls_lookback` | C2 | Parameterized | Input parameter, not versioned |
| `htf_*` | C2 | Multi-TF | Resolution not versioned |
| `space_*` | C2 | Rolling | Window not documented |
| `bs_depth` | C2 | BlockStack | Depth parameter not versioned |
| `bar_count_*` | C2 | Rolling | Window not documented |

**Remediation**: Add `window_spec` column to all C2+ field documentation.

---

## 3. Threshold Parameter Gaps

Per spec Section E.2, C3 requires versioned threshold parameters. The following are referenced but unversioned:

| Threshold | Used By | Current Status |
|-----------|---------|----------------|
| `th_move_OR` | `state_tag` | Pine input, not persisted |
| `th_move_RER` | `state_tag` | Pine input, not persisted |
| `th_accept_SD` | `value_tag` | Pine input, not persisted |
| `cp_hi` / `cp_lo` | `cp_tag` | Pine input, not persisted |
| `rd_width_th` | `rd_state` | Pine input, not persisted |
| `rd_drift_th` | `rd_state` | Pine input, not persisted |

**Remediation**: Implement `derived.threshold_registry_v0_1` before C3 implementation.

---

## 4. Correctly Classified Fields

### 4.1 — C1 Compliant (Single-Bar Only)

| Field | Formula | Status |
|-------|---------|--------|
| `range` | `h - l` | ✅ |
| `body` | `abs(c - o)` | ✅ |
| `direction` | `sign(c - o)` | ✅ |
| `ret` | `(c - o) / o` | ✅ |
| `logret` | `ln(c / o)` | ✅ |
| `body_ratio` | `body / range` | ✅ |
| `close_pos` | `(c - l) / range` | ✅ |
| `upper_wick` | `h - max(o, c)` | ✅ |
| `lower_wick` | `min(o, c) - l` | ✅ |
| `clv` | `((c-l)-(h-c))/(h-l)` | ✅ |
| `brb` | Bar-relative-body | ✅ |

### 4.2 — C3 Compliant (Categorical from C2)

| Field | Inputs | Status |
|-------|--------|--------|
| `state_tag` | OR, RER, CLV + thresholds | ✅ |
| `value_tag` | SD + threshold | ✅ |
| `event_tag` | took_hi, took_lo, OA | ✅ |
| `rd_state` | rd_w_rrc, drift | ✅ |
| `rd_brkdir` | close vs rails | ✅ |
| `tt` | composite | ✅ |

### 4.3 — Decision Layer Compliant

| Field | Status |
|-------|--------|
| `L3_BIAS` | ✅ |
| `L3_PLAY` | ✅ |
| `L3_PERMIT` | ✅ |
| `L3_PRED` | ✅ |
| All `*_WHY` fields | ✅ |

---

## 5. Alignment Summary by Tier

| Tier | Total Fields | Compliant | Violations | Compliance Rate |
|------|--------------|-----------|------------|-----------------|
| B | 22 | 21 | 1 (`news_flag`) | 95% |
| C1 | 11 | 11 | 0 | 100% |
| C1 (impl view) | 23 | 11 | 12 (should be C2) | 48% |
| C2 | ~65 | ~62 | 3 (in C3) | 95% |
| C3 | ~30 | ~27 | 3 (should be C2) | 90% |
| Decision | 16 | 16 | 0 | 100% |

---

## 6. Recommended Actions

### Immediate (No Code Changes)

1. **Document window_spec** for all C2 fields in `metric_map_pine_to_c_layers.md`
2. **Add threshold inventory** to mapping document
3. **Mark violations** in mapping document with `[VIOLATES: C1 boundary]` annotations

### Pending Design Decisions

| ID | Decision | Blocking |
|----|----------|----------|
| D1 | Amend C1 definition or split view | Tier validation |
| D2 | Create C2.5 sub-tier | Classification consistency |
| D3 | Split RD module | C3 implementation |
| D4 | Threshold registry design | C3 replay guarantee |
| D5 | `news_flag` disposition | B-layer validation |

### After Decisions Approved

1. Restructure `derived.ovc_block_features_v0_1` if D1 = "split view"
2. Update `metric_map_pine_to_c_layers.md` tier assignments
3. Create threshold registry if D4 approved
4. Update B-layer validation rules if D5 resolved

---

*Report generated against: c_layer_boundary_spec_v0.1.md*
