# L1 v0.1 Validation Report

**Validation Date:** 2026-01-20  
**Status:** ✅ ALL FIXTURES PASSED  
**Outcome:** L1 eligible for CANONICAL promotion

---

## 1. Implementation Under Test

| Property | Value |
|----------|-------|
| View | `derived.v_ovc_l1_features_v0_1` |
| SQL File | `sql/derived/v_ovc_l1_features_v0_1.sql` |
| Feature Spec | `docs/ops/OPTION_B_L1_FEATURES_v0.1.md` |
| Implementation Contract | `docs/ops/OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md` |

---

## 2. Mandatory Fixtures Executed

Per `OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md §5.2`, the following mandatory fixtures were executed:

| Fixture ID | Description | Condition |
|------------|-------------|-----------|
| `ZERO_RANGE_001` | Zero-range bar | h = l = o = c |
| `FLAT_BAR_001` | Flat bar (body = 0, range > 0) | o = c, h > l |
| `PURE_BULL_001` | Pure bullish bar | o = l, c = h |
| `PURE_BEAR_001` | Pure bearish bar | o = h, c = l |
| `DOJI_001` | Doji bar (body_ratio ≤ 0.1) | body_ratio = 0.05 |
| `FULL_BODY_001` | Full body bar (body_ratio ≥ 0.8) | body_ratio = 0.95 |
| `HAMMER_001` | Hammer shape | lower_wick ≥ 0.6, upper_wick ≤ 0.1, body ≤ 0.3 |
| `INV_HAMMER_001` | Inverted hammer shape | upper_wick ≥ 0.6, lower_wick ≤ 0.1, body ≤ 0.3 |

---

## 3. Validation Results

### 3.1 Pass/Fail Summary

| Fixture ID | Result | Notes |
|------------|--------|-------|
| `ZERO_RANGE_001` | ✅ PASS | All ratios → NULL; all booleans → FALSE |
| `FLAT_BAR_001` | ✅ PASS | body_ratio = 0; is_doji = TRUE |
| `PURE_BULL_001` | ✅ PASS | body_ratio = 1; directional_efficiency = +1 |
| `PURE_BEAR_001` | ✅ PASS | body_ratio = 1; directional_efficiency = -1 |
| `DOJI_001` | ✅ PASS | is_doji = TRUE |
| `FULL_BODY_001` | ✅ PASS | is_full_body = TRUE |
| `HAMMER_001` | ✅ PASS | is_hammer_shape = TRUE |
| `INV_HAMMER_001` | ✅ PASS | is_inverted_hammer_shape = TRUE |

**Overall: 8/8 PASS**

### 3.2 Feature Coverage

| Feature | Tested | Conforms to Spec |
|---------|--------|------------------|
| `body_ratio` | ✅ | ✅ |
| `upper_wick_ratio` | ✅ | ✅ |
| `lower_wick_ratio` | ✅ | ✅ |
| `wick_symmetry` | ✅ | ✅ |
| `body_position` | ✅ | ✅ |
| `close_position` | ✅ | ✅ |
| `open_position` | ✅ | ✅ |
| `is_doji` | ✅ | ✅ |
| `is_full_body` | ✅ | ✅ |
| `is_hammer_shape` | ✅ | ✅ |
| `is_inverted_hammer_shape` | ✅ | ✅ |
| `directional_efficiency` | ✅ | ✅ |

**Overall: 12/12 features conform**

---

## 4. Edge Case Compliance

| Edge Case | Contract Section | Behavior | Verified |
|-----------|------------------|----------|----------|
| Zero-range (h = l) | §2.2 | Ratios → NULL; Booleans → FALSE | ✅ |
| Flat bar (o = c) | §2.3 | body_ratio = 0; is_doji = TRUE | ✅ |
| NULL input propagation | §2.4 | Output → NULL | ✅ |
| Division by zero protection | §2.2 | Prevented via CASE | ✅ |

---

## 5. Type Compliance

| Requirement | Contract Section | Implementation | Verified |
|-------------|------------------|----------------|----------|
| 64-bit float | §3.1 | DOUBLE PRECISION | ✅ |
| Explicit casts | §3.4 | CAST() used | ✅ |
| Boolean strictness | §3.2 | TRUE/FALSE/NULL only | ✅ |
| No implicit casts | §3.4 | All casts explicit | ✅ |

---

## 6. Determinism Compliance

| Requirement | Contract Section | Implementation | Verified |
|-------------|------------------|----------------|----------|
| Same input → same output | §4.1 | No external state | ✅ |
| No random() | §4.2 | Not used | ✅ |
| No now() / timestamps | §4.2 | Not used | ✅ |
| No window functions | Features §2.3 | Not used | ✅ |
| No joins | Features §2.3 | Single table source | ✅ |

---

## 7. Conformance Statement

> **All L1 features conform exactly to OPTION_B_L1_FEATURES_v0.1.md.**  
> **No deviations detected.**

The implementation in `sql/derived/v_ovc_l1_features_v0_1.sql`:
- Implements all 12 L1 features as defined in the feature specification
- Handles all edge cases as required by the implementation contract
- Uses correct types and explicit casts
- Is deterministic and side-effect free
- References only the canonical source table (`ovc.ovc_blocks_v01_1_min`)

---

## 8. Promotion Recommendation

**RECOMMENDATION: PROMOTE L1 TO CANONICAL**

| Promotion Criterion | Status |
|---------------------|--------|
| All 12 features implemented | ✅ |
| All features match spec exactly | ✅ |
| All mandatory fixtures pass | ✅ |
| Zero-range edge cases handled | ✅ |
| Flat-bar edge cases handled | ✅ |
| NULL propagation correct | ✅ |
| No implicit casts | ✅ |
| Determinism verified | ✅ |

All prerequisites from `OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md §6.2` are satisfied.

---

*Validation completed: 2026-01-20*  
*Validated by: Governance process*  
*Next step: Update L1 specs to [STATUS: CANONICAL]*
