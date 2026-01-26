# Option C Outcomes v0.1 — Promotion Record

**[STATUS: CANONICAL PROMOTION EVIDENCE]**

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| Promotion Date     | 2026-01-20                                 |
| Promoted By        | OVC Governance                             |
| Validation Report  | [C_v0_1_validation.md](C_v0_1_validation.md) |
| Outcome Spec       | docs/ops/OPTION_C_OUTCOMES_v0.1.md         |
| Contract           | docs/ops/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md |

---

## 1. What Was Promoted

The following **ACTIVE** outcomes have been promoted to **CANONICAL** status:

| Outcome       | Type    | Windows   | Status Before | Status After |
|---------------|---------|-----------|---------------|--------------|
| `fwd_ret_1`   | float   | 1         | ACTIVE        | CANONICAL    |
| `fwd_ret_3`   | float   | 3         | ACTIVE        | CANONICAL    |
| `fwd_ret_6`   | float   | 6         | ACTIVE        | CANONICAL    |
| `mfe_3`       | float   | 3         | ACTIVE        | CANONICAL    |
| `mfe_6`       | float   | 6         | ACTIVE        | CANONICAL    |
| `mae_3`       | float   | 3         | ACTIVE        | CANONICAL    |
| `mae_6`       | float   | 6         | ACTIVE        | CANONICAL    |
| `rvol_6`      | float   | 6         | ACTIVE        | CANONICAL    |

**Total CANONICAL Outcomes:** 8

---

## 2. Excluded from Promotion

The following outcomes remain **DRAFT** and are **NOT implemented**:

| Outcome       | Status  | Reason                                      |
|---------------|---------|---------------------------------------------|
| `ttt_*`       | DRAFT   | Threshold parameterization undefined        |

**ttt_* outcomes are explicitly excluded from this promotion.**

Activation of ttt_* requires:
1. Amendment to OPTION_C_OUTCOMES_v0.1.md with threshold specification
2. Amendment to OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md with computation rules
3. Governance approval
4. New validation cycle

---

## 3. Precondition Verification

| Precondition                                          | Status | Evidence                          |
|-------------------------------------------------------|--------|-----------------------------------|
| v_ovc_c_outcomes_v0_1.sql exists                      | ✓ PASS | sql/derived/                      |
| C_v0_1_validation.md exists                           | ✓ PASS | docs/validation/                  |
| All fixtures in validation report are PASS            | ✓ PASS | 7/7 fixtures passed               |
| No DRAFT outcomes implemented (ttt_* excluded)        | ✓ PASS | View excludes ttt_*               |
| Implementation conforms to contract                   | ✓ PASS | Validation checklist complete     |
| Determinism verified                                  | ✓ PASS | Replay test passed                |
| NULL handling correct                                 | ✓ PASS | No sentinel values                |
| DOUBLE PRECISION casts used                           | ✓ PASS | Code review verified              |

**All preconditions satisfied.**

---

## 4. Validation Evidence Summary

From [C_v0_1_validation.md](C_v0_1_validation.md):

| Fixture ID | Name                | Status |
|------------|---------------------|--------|
| FX-01      | Positive Move       | PASS   |
| FX-02      | Negative Move       | PASS   |
| FX-03      | Flat Move           | PASS   |
| FX-04      | High Volatility     | PASS   |
| FX-05      | Session Boundary    | PASS   |
| FX-06      | Short History       | PASS   |
| FX-07      | NULL Input          | PASS   |

**Fixture Summary:** 7/7 PASS (100%)

---

## 5. Contract Compliance Verification

| Requirement                                | Contract Ref | Status |
|--------------------------------------------|--------------|--------|
| Reads only from L1/L2/L3 views             | Charter §2.1 | ✓      |
| No raw block access                        | Charter §2.2 | ✓      |
| Anchor bar excluded from forward window    | Contract §2.2| ✓      |
| Lookahead only in Option C                 | Contract §2.4| ✓      |
| NULL for missing/insufficient data         | Contract §4.1| ✓      |
| No sentinel values                         | Contract §4.3| ✓      |
| DOUBLE PRECISION casts                     | Contract §5.4| ✓      |
| Deterministic ordering                     | Contract §5.1| ✓      |

---

## 6. Promotion Approvals

| Role                    | Name/Reference         | Date       |
|-------------------------|------------------------|------------|
| Implementation Author   | OVC Governance         | 2026-01-20 |
| Governance Reviewer     | OVC Governance         | 2026-01-20 |

**Approval Count:** 2 (meets minimum requirement)

---

## 7. Post-Promotion Constraints

Upon promotion to CANONICAL:

1. **Outcome meanings are FROZEN**
   - No changes to definitions in OPTION_C_OUTCOMES_v0.1.md without MAJOR version bump

2. **Implementation behavior is FROZEN**
   - No changes to computation rules in OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md without governance approval

3. **Breaking changes require:**
   - MAJOR version increment (v0.1.x → v0.2.0 or v1.0.0)
   - Governance approval
   - New validation cycle
   - Migration plan for downstream consumers

4. **Non-breaking additions permitted:**
   - Activating DRAFT outcomes (e.g., ttt_*) via proper governance process
   - Adding new outcomes with governance approval
   - Clarifying edge cases (MINOR version bump)

---

## 8. Artifacts Affected by This Promotion

| Artifact                                      | Change                          |
|-----------------------------------------------|--------------------------------|
| docs/ops/OPTION_C_OUTCOMES_v0.1.md            | STATUS: ACTIVE → CANONICAL     |
| docs/ops/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md | STATUS: ACTIVE → CANONICAL |
| sql/derived/v_ovc_c_outcomes_v0_1.sql         | Header updated to CANONICAL    |
| docs/WORKFLOW_STATUS.md                       | Option C row: CANONICAL        |

---

## 9. Document Control

| Version | Date       | Change Description                    |
|---------|------------|---------------------------------------|
| 1.0     | 2026-01-20 | Initial promotion record              |

---

**END OF PROMOTION RECORD**
