# OVC Derived Validation Report

**Run ID**: `1dfb7850-2cdd-5dd0-9cd5-dd7758d19439`
**Version**: v0.1
**Symbol**: GBPUSD
**Date Range**: 2026-01-13 to 2026-01-17
**Mode**: fail
**Status**: **PASS**

---

## 1. Coverage Parity

| Layer | Count |
|-------|-------|
| B-layer blocks | 1 |
| C1 rows | 1 |
| C2 rows | 1 |

**Parity**: ✅ PASS

## 2. Key Uniqueness

| Table | Duplicates |
|-------|------------|
| C1 | 0 |
| C2 | 0 |

## 3. Null Rates (C1)

| Column | Null Rate |
|--------|-----------|
| range | 0.00% |
| body | 0.00% |
| direction | 0.00% |
| ret | 0.00% |
| logret | 0.00% |
| body_ratio | 0.00% |
| close_pos | 0.00% |
| upper_wick | 0.00% |
| lower_wick | 0.00% |
| clv | 0.00% |

## 4. Null Rates (C2)

| Column | Null Rate |
|--------|-----------|
| gap | 0.00% |
| took_prev_high | 0.00% |
| took_prev_low | 0.00% |
| sess_high | 0.00% |
| sess_low | 0.00% |
| dist_sess_high | 0.00% |
| dist_sess_low | 0.00% |
| roll_avg_range_12 | 0.00% |
| roll_std_logret_12 | 0.00% |
| range_z_12 | 0.00% |

## 5. Window Spec Enforcement (C2)

**Valid**: ✅ PASS


## 6. Determinism Quickcheck

- Sample Size: 1
- Mismatches: 0
- **Result**: ✅ PASS


---

## Errors

None

## Warnings

None

---
*Generated: 2026-01-18T21:23:32.510167+00:00*