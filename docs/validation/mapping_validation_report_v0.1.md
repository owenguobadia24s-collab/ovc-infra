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

### 1.1 — L1 Violations: Fields Requiring History Classified as L1

The following fields are implemented in `derived.ovc_block_features_v0_1` (documented as L1) but violate the L1 rule: *"No lookback, no history, no rolling windows"*.

| Field | Current Tier | Actual Inputs | Correct Tier | Violation |
|-------|--------------|---------------|--------------|-----------|
| `gap` | L1 (impl) | `o[0] - prev_c` | **L2** | Requires `c[-1]` |
| `sess_high` | L1 (impl) | `max(h) over session` | **L2** | Session window |
| `sess_low` | L1 (impl) | `min(l) over session` | **L2** | Session window |
| `dist_sess_high` | L1 (impl) | `sess_high - c` | **L2** | Depends on sess_high |
| `dist_sess_low` | L1 (impl) | `c - sess_low` | **L2** | Depends on sess_low |
| `roll_avg_range_12` | L1 (impl) | `avg(range) N=12` | **L2** | 12-bar window |
| `roll_std_logret_12` | L1 (impl) | `stddev(logret) N=12` | **L2** | 12-bar window |
| `range_z_12` | L1 (impl) | `(range - avg) / std` | **L2** | Depends on rolling |
| `hh_12` | L1 (impl) | `h > max(h[-12:-1])` | **L2** | 12-bar lookback |
| `ll_12` | L1 (impl) | `l < min(l[-12:-1])` | **L2** | 12-bar lookback |
| `took_prev_high` | L1 (impl) | `h > h[-1]` | **L2** | 1-bar lookback |
| `took_prev_low` | L1 (impl) | `l < l[-1]` | **L2** | 1-bar lookback |

**Impact**: 12 fields in current "L1" view are actually L2 by spec definition.

---

### 1.2 — L3 Violations: Numeric Outputs Classified as L3

The following fields are classified as L3 in `metric_map_pine_to_c_layers.md` but are numeric rolling-window outputs, which should be L2 per spec.

| Field | Current Tier | Actual Formula | Correct Tier | Violation |
|-------|--------------|----------------|--------------|-----------|
| `rd_hi` | L3 | `highest(h, rd_len)` | **L2** | Numeric rolling max |
| `rd_lo` | L3 | `lowest(l, rd_len)` | **L2** | Numeric rolling min |
| `rd_mid` | L3 | `(rd_hi + rd_lo) / 2` | **L2** | Arithmetic from rd_hi/rd_lo |

**Impact**: 3 RD fields should be L2, not L3. RD module spans tiers.

---

### 1.3 — B-Layer Violations: Non-Derivable Field

| Field | Current Tier | Issue | Correct Tier |
|-------|--------------|-------|--------------|
| `news_flag` | B | External input, not derivable from OHLC | **Metadata** or **External Table** |

**Impact**: `news_flag` violates B-layer source-agnosticism.

---

## 2. Window Specification Gaps

Per spec Section E.3, all L2+ fields must have documented `window_spec`. The following fields lack explicit specification:

| Field | Tier | Window Type | Missing Spec |
|-------|------|-------------|--------------|
| `rm` (RR mean) | L2 | Rolling | N=? not documented |
| `sd` (Stddev) | L2 | Rolling | N=? not documented |
| `or` (Open ratio) | L2 | Rolling | N=? not documented |
| `rer` (Ret ratio) | L2 | Rolling | N=? not documented |
| `mc3` | L2 | Rolling | N=3 implied but not explicit |
| `vf3` | L2 | Rolling | N=3 implied but not explicit |
| `rd_len` | L2/L3 | Parameterized | Input parameter, not versioned |
| `kls_lookback` | L2 | Parameterized | Input parameter, not versioned |
| `htf_*` | L2 | Multi-TF | Resolution not versioned |
| `space_*` | L2 | Rolling | Window not documented |
| `bs_depth` | L2 | BlockStack | Depth parameter not versioned |
| `bar_count_*` | L2 | Rolling | Window not documented |

**Remediation**: Add `window_spec` column to all L2+ field documentation.

---

## 3. Threshold Parameter Gaps

Per spec Section E.2, L3 requires versioned threshold parameters. The following are referenced but unversioned:

| Threshold | Used By | Current Status |
|-----------|---------|----------------|
| `th_move_OR` | `state_tag` | Pine input, not persisted |
| `th_move_RER` | `state_tag` | Pine input, not persisted |
| `th_accept_SD` | `value_tag` | Pine input, not persisted |
| `cp_hi` / `cp_lo` | `cp_tag` | Pine input, not persisted |
| `rd_width_th` | `rd_state` | Pine input, not persisted |
| `rd_drift_th` | `rd_state` | Pine input, not persisted |

**Remediation**: Implement `derived.threshold_registry_v0_1` before L3 implementation.

---

## 4. Correctly Classified Fields

### 4.1 — L1 Compliant (Single-Bar Only)

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

### 4.2 — L3 Compliant (Categorical from L2)

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
| L1 | 11 | 11 | 0 | 100% |
| L1 (impl view) | 23 | 11 | 12 (should be L2) | 48% |
| L2 | ~65 | ~62 | 3 (in L3) | 95% |
| L3 | ~30 | ~27 | 3 (should be L2) | 90% |
| Decision | 16 | 16 | 0 | 100% |

---

## 6. Recommended Actions

### Immediate (No Code Changes)

1. **Document window_spec** for all L2 fields in `metric_map_pine_to_c_layers.md`
2. **Add threshold inventory** to mapping document
3. **Mark violations** in mapping document with `[VIOLATES: L1 boundary]` annotations

### Pending Design Decisions

| ID | Decision | Blocking |
|----|----------|----------|
| D1 | Amend L1 definition or split view | Tier validation |
| D2 | Create L2.5 sub-tier | Classification consistency |
| D3 | Split RD module | L3 implementation |
| D4 | Threshold registry design | L3 replay guarantee |
| D5 | `news_flag` disposition | B-layer validation |

### After Decisions Approved

1. Restructure `derived.ovc_block_features_v0_1` if D1 = "split view"
2. Update `metric_map_pine_to_c_layers.md` tier assignments
3. Create threshold registry if D4 approved
4. Update B-layer validation rules if D5 resolved

---

*Report generated against: c_layer_boundary_spec_v0.1.md*
