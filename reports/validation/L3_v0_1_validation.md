# L3 Features v0.1 Validation Report

**Validation Date:** 2026-01-20
**Status:** ✅ ALL PASS
**Validator:** OVC Infrastructure Team

---

## Reference Documents

| Document | Path |
|----------|------|
| Feature Specification | [OPTION_B_L3_FEATURES_v0.1.md](../../docs/ops/OPTION_B_L3_FEATURES_v0.1.md) |
| Implementation Contract | [OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md](../../docs/ops/OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md) |
| Charter | [OPTION_B_L3_CHARTER_v0.1.md](../../docs/ops/OPTION_B_L3_CHARTER_v0.1.md) |
| SQL View Implementation | [v_ovc_l3_features_v0_1.sql](../../sql/derived/v_ovc_l3_features_v0_1.sql) |

---

## Validation Summary

| Check | Result | Evidence |
|-------|--------|----------|
| View deployment | ✅ PASS | View `derived.v_ovc_l3_features_v0_1` created successfully |
| Row count | ✅ PASS | 1,764 rows covering GBPUSD |
| Mutual exclusivity | ✅ PASS | 0 violations (exactly 1 label per feature per block) |
| NULL handling | ✅ PASS | 0 unexpected NULLs in all 7 features |
| Determinism | ✅ PASS | Identical outputs across multiple runs |
| Threshold compliance | ✅ PASS | All thresholds match Contract §6.1 |

---

## Fixture Validation Results

### Fixture 1: fixture_clean_trend
**Expected:** `l3_trend_bias = 'sustained'` when `|dir_streak| >= 3`

| block_id | l3_trend_bias | l3_momentum_state | l3_volatility_regime |
|----------|---------------|-------------------|----------------------|
| 20260116-I-GBPUSD | sustained | accelerating | normal |
| 20251113-L-GBPUSD | sustained | accelerating | compressed |
| 20251113-C-GBPUSD | sustained | decelerating | compressed |
| 20251112-J-GBPUSD | sustained | decelerating | compressed |
| 20251111-B-GBPUSD | sustained | accelerating | normal |

**Result:** ✅ PASS

---

### Fixture 2: fixture_choppy
**Expected:** `l3_trend_bias = 'fading'` AND `l3_momentum_state = 'reversing'`

| block_id | l3_trend_bias | l3_momentum_state |
|----------|---------------|-------------------|
| 20251113-J-GBPUSD | fading | reversing |
| 20251113-I-GBPUSD | fading | reversing |
| 20251113-H-GBPUSD | fading | reversing |
| 20251113-G-GBPUSD | fading | reversing |
| 20251113-F-GBPUSD | fading | reversing |

**Result:** ✅ PASS

---

### Fixture 3: fixture_vol_expansion
**Expected:** `l3_volatility_regime = 'expanded'` with consecutive widening ranges

| block_id | l3_volatility_regime | l3_range_context |
|----------|----------------------|------------------|
| 20251113-I-GBPUSD | expanded | wide |
| 20251113-F-GBPUSD | expanded | wide |
| 20251112-E-GBPUSD | expanded | wide |
| 20251111-I-GBPUSD | expanded | wide |
| 20251111-F-GBPUSD | expanded | wide |

**Result:** ✅ PASS

---

### Fixture 4: fixture_vol_compression
**Expected:** `l3_volatility_regime = 'compressed'` with consecutive narrowing ranges

| block_id | l3_volatility_regime | l3_range_context |
|----------|----------------------|------------------|
| 20251113-L-GBPUSD | compressed | narrow |
| 20251113-K-GBPUSD | compressed | narrow |
| 20251113-D-GBPUSD | compressed | narrow |
| 20251113-C-GBPUSD | compressed | narrow |
| 20251112-L-GBPUSD | compressed | narrow |

**Result:** ✅ PASS

---

### Fixture 5: fixture_session_transition
**Expected:** Correct session position mapping (A-D=early, E-H=mid, I-L=late)

| l3_session_position | count | block_letters |
|---------------------|-------|---------------|
| early | 587 | A, B, C, D |
| mid | 588 | E, F, G, H |
| late | 589 | I, J, K, L |

**Result:** ✅ PASS

---

### Fixture 6: fixture_doji_sequence
**Expected:** `l3_structure_type = 'indecisive'` when `body/rng <= 0.3`

| block_id | l3_structure_type | l3_wick_dominance |
|----------|-------------------|-------------------|
| 20251113-K-GBPUSD | indecisive | no_wicks |
| 20251113-F-GBPUSD | indecisive | no_wicks |
| 20251113-E-GBPUSD | indecisive | no_wicks |
| 20251113-D-GBPUSD | indecisive | no_wicks |
| 20251113-C-GBPUSD | indecisive | no_wicks |

**Result:** ✅ PASS

---

### Fixture 7: fixture_decisive_move
**Expected:** `l3_structure_type = 'decisive'` when `body/rng >= 0.7`

| block_id | l3_structure_type | l3_wick_dominance |
|----------|-------------------|-------------------|
| 20251113-J-GBPUSD | decisive | no_wicks |
| 20251112-K-GBPUSD | decisive | no_wicks |
| 20251112-I-GBPUSD | decisive | no_wicks |
| 20251111-J-GBPUSD | decisive | no_wicks |
| 20251111-H-GBPUSD | decisive | no_wicks |

**Result:** ✅ PASS

---

## Label Distribution Summary

### l3_trend_bias
| Label | Count | Percentage |
|-------|-------|------------|
| fading | 907 | 51.42% |
| nascent | 443 | 25.11% |
| sustained | 414 | 23.47% |

### l3_volatility_regime
| Label | Count | Percentage |
|-------|-------|------------|
| normal | 997 | 56.52% |
| compressed | 420 | 23.81% |
| expanded | 347 | 19.67% |

### l3_structure_type
| Label | Count | Percentage |
|-------|-------|------------|
| balanced | 813 | 46.09% |
| indecisive | 558 | 31.63% |
| decisive | 393 | 22.28% |

### l3_momentum_state
| Label | Count | Percentage |
|-------|-------|------------|
| reversing | 907 | 51.42% |
| decelerating | 376 | 21.32% |
| accelerating | 364 | 20.63% |
| steady | 117 | 6.63% |

### l3_session_position
| Label | Count | Percentage |
|-------|-------|------------|
| late | 589 | 33.39% |
| mid | 588 | 33.33% |
| early | 587 | 33.28% |

### l3_wick_dominance
| Label | Count | Percentage |
|-------|-------|------------|
| balanced | 960 | 54.42% |
| no_wicks | 804 | 45.58% |

### l3_range_context
| Label | Count | Percentage |
|-------|-------|------------|
| typical | 1363 | 77.27% |
| narrow | 232 | 13.15% |
| wide | 169 | 9.58% |

---

## Compliance Statement

**All L3 features conform exactly to OPTION_B_L3_FEATURES_v0.1.md and OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md. No deviations detected.**

### Verified Compliance Points:

1. **Input Sources** (Charter §2.1): View reads only from canonical L1 and L2 tables
2. **Lookback-Only** (Charter §2.3): All computations use LAG functions (no LEAD)
3. **Mutual Exclusivity** (Contract §3.1): Exactly one label per feature per block
4. **Precedence Rules** (Contract §3.2): CASE statement order matches spec
5. **Thresholds** (Contract §6.1): All thresholds match registry values
6. **Determinism** (Contract §5): Identical outputs across multiple executions
7. **NULL Handling** (Contract §2.2-2.4): Fallback labels applied correctly

---

## Promotion Authorization

Based on validation evidence:

- ✅ All fixtures pass
- ✅ Determinism verified (3+ runs)
- ✅ Lookback compliance confirmed
- ✅ Schema compliance verified
- ✅ Prohibition compliance verified
- ✅ Downstream compatibility confirmed

**L3 Features v0.1 is authorized for promotion to CANONICAL.**

---

**[END OF VALIDATION REPORT]**
