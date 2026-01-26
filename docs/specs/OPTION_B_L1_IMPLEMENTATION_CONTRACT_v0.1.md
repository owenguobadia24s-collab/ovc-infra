# Option B – L1 Implementation Contract v0.1

[CHANGE][CHANGED] [STATUS: CANONICAL]

> **Binding Statement:** This document governs HOW L1 features must be implemented.
> All code (SQL, Python, or other) must comply with these rules.

> **Enforcement (2026-01-20):**  
> All current and future implementations MUST comply with this contract.  
> Any deviation requires spec change first — code must never diverge from spec.

---

## 1. Source of Truth

### 1.1 Authoritative Reference

| Property | Value |
|----------|-------|
| Feature Definitions | [OPTION_B_L1_FEATURES_v0.1.md](OPTION_B_L1_FEATURES_v0.1.md) |
| Implementation Rules | This document |
| Governance | [GOVERNANCE_RULES_v0.1.md](GOVERNANCE_RULES_v0.1.md) |

### 1.2 Precedence Rule

**If code and specification disagree, the specification wins.**

| Scenario | Required Action |
|----------|-----------------|
| Code produces different output than spec | Code is WRONG; fix code |
| Code handles edge case differently than spec | Code is WRONG; fix code |
| Spec is ambiguous | Clarify spec FIRST; then implement |
| Spec appears incorrect | Raise issue; do NOT silently "fix" in code |

### 1.3 Deviation Protocol

If an implementer believes the spec is wrong:

1. Document the concern in a GitHub issue
2. Reference specific feature and edge case
3. Propose spec amendment with rationale
4. **Do NOT ship code that deviates from spec**
5. Wait for spec update before implementing alternative

---

## 2. Null & Edge Case Rules

### 2.1 UNDEFINED Mapping

The spec uses "UNDEFINED" for mathematically invalid operations. Implementation mapping:

| Spec Term | SQL Representation | Python Representation |
|-----------|-------------------|----------------------|
| UNDEFINED | `NULL` | `None` |
| Valid value | Computed result | Computed result |

**Prohibition:** UNDEFINED must NEVER be represented as:
- ❌ `0` (zero)
- ❌ `NaN` (Not a Number)
- ❌ `-1` (sentinel value)
- ❌ Empty string
- ❌ Any magic number

### 2.2 Zero-Range Bar Rules

**Condition:** `high = low` (range = 0)

| Feature | Required Output | Rationale |
|---------|-----------------|-----------|
| `body_ratio` | NULL | Division by zero |
| `upper_wick_ratio` | NULL | Division by zero |
| `lower_wick_ratio` | NULL | Division by zero |
| `wick_symmetry` | NULL | Division by zero |
| `body_position` | NULL | Division by zero |
| `close_position` | NULL | Division by zero |
| `open_position` | NULL | Division by zero |
| `is_doji` | FALSE | No valid ratio to evaluate |
| `is_full_body` | FALSE | No valid ratio to evaluate |
| `is_hammer_shape` | FALSE | No valid ratios |
| `is_inverted_hammer_shape` | FALSE | No valid ratios |
| `directional_efficiency` | NULL | Division by zero |

**Detection Rule:**
```
IF (high - low) = 0 THEN zero_range = TRUE
```

Implementations MUST check for zero range BEFORE attempting division.

### 2.3 Flat Bar Rules

**Condition:** `close = open` AND `high ≠ low` (body = 0, range > 0)

| Feature | Required Output | Rationale |
|---------|-----------------|-----------|
| `body_ratio` | 0.0 | Body is zero; 0 / range = 0 |
| `upper_wick_ratio` | Computed | (high - max(o,c)) / range |
| `lower_wick_ratio` | Computed | (min(o,c) - low) / range |
| `wick_symmetry` | Computed | Difference of wicks / range |
| `body_position` | Computed | Midpoint at open=close level |
| `close_position` | Computed | (close - low) / range |
| `open_position` | Computed | (open - low) / range |
| `is_doji` | TRUE | body_ratio ≤ 0.1 satisfied |
| `is_full_body` | FALSE | body_ratio < 0.8 |
| `is_hammer_shape` | Evaluate | May be TRUE if wick conditions met |
| `is_inverted_hammer_shape` | Evaluate | May be TRUE if wick conditions met |
| `directional_efficiency` | 0.0 | (close - open) = 0 |

### 2.4 Null Propagation

If ANY required input field is NULL, the derived feature MUST be NULL.

| Input State | Output |
|-------------|--------|
| `rng` is NULL | All ratio features → NULL |
| `o` is NULL | All features using open → NULL |
| `c` is NULL | All features using close → NULL |
| `h` is NULL | All features → NULL |
| `l` is NULL | All features → NULL |

**Prohibition:** Implementations must NOT:
- ❌ Substitute default values for NULL inputs
- ❌ Skip rows with NULL inputs silently
- ❌ Coerce NULL to zero

---

## 3. Type Enforcement

### 3.1 Float Precision

| Requirement | Specification |
|-------------|---------------|
| Minimum precision | 64-bit float (IEEE 754 double) |
| Storage precision | Database native FLOAT/DOUBLE |
| Comparison tolerance | None required; exact storage |
| Rounding | Do NOT round intermediate results |
| Final output | Store full precision; display may round |

**Prohibition:**
- ❌ 32-bit float (insufficient precision)
- ❌ Fixed-point decimal (unless explicitly required)
- ❌ String representation of numbers

### 3.2 Boolean Strictness

| Requirement | Specification |
|-------------|---------------|
| Valid values | TRUE, FALSE, NULL |
| SQL type | BOOLEAN |
| Python type | `bool` or `None` |

**Prohibition:**
- ❌ Integer 0/1 as boolean substitute
- ❌ String "true"/"false"
- ❌ Tri-state enums (use NULL for unknown)
- ❌ Empty string as FALSE

**NULL Semantics for Booleans:**
- NULL means "cannot be determined" (e.g., zero-range bar)
- NULL is NOT equivalent to FALSE
- Boolean features return FALSE (not NULL) for zero-range bars per §2.2

### 3.3 Integer Strictness

| Requirement | Specification |
|-------------|---------------|
| SQL type | INTEGER or BIGINT |
| Python type | `int` or `None` |

**Note:** L1 v0.1 defines no integer output features; this section reserves rules for future additions.

### 3.4 Prohibited Implicit Casts

Implementations MUST NOT rely on implicit type conversion:

| Prohibited Pattern | Required Alternative |
|--------------------|---------------------|
| Boolean → Integer | Explicit CASE/IF |
| Float → Integer truncation | Explicit FLOOR/ROUND |
| NULL → 0 | Preserve NULL |
| String → Number | Explicit CAST with validation |

---

## 4. Determinism Guarantees

### 4.1 Core Determinism Rule

**Same input row MUST produce same output row.**

| Invariant | Requirement |
|-----------|-------------|
| Row isolation | Output depends ONLY on that row's fields |
| No execution order | Result independent of processing sequence |
| No timestamps | Result independent of when computed |
| No random state | No random(), uuid_generate(), etc. |
| No external state | No environment variables, config lookups |

### 4.2 Prohibited Patterns

| Pattern | Why Prohibited |
|---------|----------------|
| `random()` | Non-deterministic |
| `now()` / `current_timestamp` | Time-dependent |
| `row_number()` without ORDER BY on stable key | Order-dependent |
| Environment variable reads | External state |
| Database sequence reads | Global state |
| Lookups to non-canonical tables | External dependency |

### 4.3 Replayability Requirement

Implementations MUST satisfy:

```
DELETE FROM derived.ovc_l1_features_v0_1;
INSERT INTO derived.ovc_l1_features_v0_1 (SELECT ...);
-- Result MUST be identical to previous state
```

If recomputing from the same canonical source produces different results, the implementation is **non-compliant**.

### 4.4 Idempotency Requirement

Running the L1 computation multiple times MUST:
- Produce identical output each time
- Not accumulate side effects
- Not depend on prior computation state

---

## 5. Testing Obligations

### 5.1 Minimum Test Coverage

Each feature MUST have tests covering:

| Test Category | Minimum Count | Description |
|---------------|---------------|-------------|
| Happy path | 3 | Normal values, various magnitudes |
| Boundary | 2 | Domain edges (0, 1, -1 where applicable) |
| Edge case | 4 | Zero range, flat bar, pure bull, pure bear |
| Null input | 1 | At least one NULL input field |

**Total minimum per feature:** 10 test cases

### 5.2 Mandatory Edge Case Fixtures

The following fixtures MUST exist and MUST be tested:

| Fixture ID | Condition | Required Tests |
|------------|-----------|----------------|
| `ZERO_RANGE_001` | h = l = o = c | All features return expected NULL/FALSE |
| `FLAT_BAR_001` | o = c, h > l | body_ratio = 0, is_doji = TRUE |
| `PURE_BULL_001` | o = l, c = h | body_ratio = 1, directional_efficiency = +1 |
| `PURE_BEAR_001` | o = h, c = l | body_ratio = 1, directional_efficiency = -1 |
| `DOJI_001` | body_ratio = 0.05 | is_doji = TRUE |
| `FULL_BODY_001` | body_ratio = 0.95 | is_full_body = TRUE |
| `HAMMER_001` | Valid hammer shape | is_hammer_shape = TRUE |
| `INV_HAMMER_001` | Valid inverted hammer | is_inverted_hammer_shape = TRUE |

### 5.3 Fixture Format

Test fixtures MUST include:

| Field | Required |
|-------|----------|
| `fixture_id` | Unique identifier |
| `description` | Human-readable purpose |
| `input` | Complete row from canonical schema |
| `expected` | All 12 L1 feature outputs |
| `rationale` | Why this output is correct |

### 5.4 Test Failure Protocol

| Scenario | Required Action |
|----------|-----------------|
| Test fails, code appears wrong | Fix code |
| Test fails, spec appears wrong | HALT; raise issue; do NOT change test |
| Test fails, fixture appears wrong | HALT; verify against spec; fix fixture only if spec-compliant |

**Prohibition:** Tests MUST NOT be modified to match incorrect code output.

### 5.5 Regression Prevention

- All fixtures MUST be version-controlled
- Fixture changes require review
- CI MUST run all L1 tests on every PR touching derived schema

---

## 6. Promotion Rules

### 6.1 Promotion Path

```
[DRAFT] → [ACTIVE] → [CANONICAL]
```

| Stage | Meaning | Who Can Modify |
|-------|---------|----------------|
| DRAFT | Under development | Any contributor |
| ACTIVE | Ready for use; may have minor changes | Requires PR review |
| CANONICAL | Frozen; breaking changes need governance | Requires governance approval |

### 6.2 Prerequisites for CANONICAL Status

Before L1 implementation can be marked CANONICAL, ALL of the following must be true:

| Requirement | Verification |
|-------------|--------------|
| ✅ All 12 features implemented | Code review |
| ✅ All features match spec exactly | Automated tests |
| ✅ All mandatory fixtures pass | CI green |
| ✅ Zero-range edge cases handled | Fixture tests |
| ✅ Flat-bar edge cases handled | Fixture tests |
| ✅ NULL propagation correct | Fixture tests |
| ✅ No implicit casts | Code review |
| ✅ Determinism verified | Replay test |
| ✅ Feature definitions doc is CANONICAL | Doc status check |
| ✅ Implementation contract doc is CANONICAL | Doc status check |

### 6.3 Sign-Off Requirements

| Promotion | Required Sign-Offs |
|-----------|-------------------|
| DRAFT → ACTIVE | 1 reviewer |
| ACTIVE → CANONICAL | 2 reviewers + all tests green |

### 6.4 Audit Trail

Promotion to CANONICAL requires:

1. GitHub PR with explicit "Promote to CANONICAL" in title
2. All CI checks passing
3. Explicit approval comments from required reviewers
4. No unresolved spec deviation issues
5. Merge commit message referencing this contract

### 6.5 Post-CANONICAL Modifications

Once CANONICAL:

| Change Type | Allowed? | Process |
|-------------|----------|---------|
| Bug fix (code matches spec better) | Yes | Normal PR |
| Performance optimization (same output) | Yes | Normal PR + replay test |
| New feature | No | Requires spec update first |
| Feature removal | No | Requires governance approval |
| Output change | No | Requires MAJOR version bump |

---

## 7. Compliance Checklist

Before submitting L1 implementation for review, verify:

### 7.1 Code Compliance

- [ ] All 12 features implemented
- [ ] No SQL/Python that deviates from spec
- [ ] UNDEFINED → NULL mapping correct
- [ ] Zero-range returns NULL for ratios, FALSE for booleans
- [ ] Flat-bar returns 0 for body_ratio, TRUE for is_doji
- [ ] No implicit type casts
- [ ] No non-deterministic functions
- [ ] No external state dependencies

### 7.2 Test Compliance

- [ ] All mandatory fixtures exist
- [ ] All fixtures pass
- [ ] Edge cases covered
- [ ] NULL propagation tested
- [ ] No test modifications to match buggy code

### 7.3 Documentation Compliance

- [ ] Code comments reference spec sections
- [ ] Any ambiguities raised as issues
- [ ] No undocumented deviations

---

## Appendix A: Quick Reference Card

### NULL Decision Tree

```
Is (high - low) = 0?
├─ YES → Ratio features = NULL; Boolean features = FALSE
└─ NO → Is required input field NULL?
         ├─ YES → Output = NULL
         └─ NO → Compute normally
```

### Type Quick Reference

| Category | SQL | Python | NULL Allowed |
|----------|-----|--------|--------------|
| Ratio features | DOUBLE PRECISION | float | Yes |
| Boolean features | BOOLEAN | bool | Yes (but FALSE for zero-range) |
| Integer features | INTEGER | int | Yes |

### Edge Case Quick Reference

| Condition | body_ratio | is_doji | directional_efficiency |
|-----------|------------|---------|------------------------|
| Zero range | NULL | FALSE | NULL |
| Flat bar | 0.0 | TRUE | 0.0 |
| Pure bull | 1.0 | FALSE | +1.0 |
| Pure bear | 1.0 | FALSE | -1.0 |

---

*Document created: 2026-01-20*
*Feature definitions: [OPTION_B_L1_FEATURES_v0.1.md](OPTION_B_L1_FEATURES_v0.1.md)*
*Charter: [OPTION_B_CHARTER_v0.1.md](OPTION_B_CHARTER_v0.1.md)*
*Governance: [GOVERNANCE_RULES_v0.1.md](GOVERNANCE_RULES_v0.1.md)*
