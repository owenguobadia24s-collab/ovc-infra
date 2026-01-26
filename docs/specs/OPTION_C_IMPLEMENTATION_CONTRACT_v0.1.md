# Option C Implementation Contract v0.1

**[STATUS: CANONICAL]** [CHANGE][CHANGED]

> **ENFORCEMENT**: All implementations MUST conform to this contract. Specification changes MUST precede code changes. No sentinel value substitutions permitted. See [C_v0_1_promotion.md](../../reports/validation/C_v0_1_promotion.md) for promotion evidence.

| Field          | Value                               |
|----------------|-------------------------------------|
| Version        | 0.1                                 |
| Created        | 2026-01-20                          |
| Promoted       | 2026-01-20                          |
| Author         | OVC Governance                      |
| Depends On     | OPTION_C_OUTCOMES_v0.1.md           |
| Governed By    | GOVERNANCE_RULES_v0.1.md            |
| Validation     | [C_v0_1_validation.md](../../docs/validation/C_v0_1_validation.md) |
| Promotion      | [C_v0_1_promotion.md](../../reports/validation/C_v0_1_promotion.md) |

---

## 1. Source of Truth

### 1.1 Specification Authority

**Outcome meanings are defined in OPTION_C_OUTCOMES_v0.1.md.**

This implementation contract governs **HOW** outcomes are computed. It does not redefine **WHAT** they mean.

### 1.2 Conformance Requirement

All implementation code (SQL, Python, or otherwise) **MUST** conform exactly to:

1. The outcome definitions in OPTION_C_OUTCOMES_v0.1.md
2. The computation rules in this contract

### 1.3 Conflict Resolution

**If code and specification disagree, the specification wins.**

| Situation                          | Resolution                                    |
|------------------------------------|-----------------------------------------------|
| Code produces different result     | Code is BUGGY; fix the code                   |
| Spec is ambiguous                  | Amend spec first; then fix code               |
| Edge case not covered in spec      | Add to spec; then implement                   |
| Performance requires deviation     | PROHIBITED without governance approval        |

No implementation optimization may alter outcome semantics.

---

## 2. Lookahead Semantics (Binding)

### 2.1 Forward Window Computation

Forward windows are computed using **bar indexing** relative to the anchor block.

| Symbol    | Definition                                      |
|-----------|-------------------------------------------------|
| T         | Anchor block index (the block being evaluated)  |
| T+1       | First block after anchor                        |
| T+N       | N-th block after anchor                         |
| close[T]  | Close price of block T                          |
| high[T+k] | High price of block T+k                         |
| low[T+k]  | Low price of block T+k                          |

### 2.2 Anchor Bar Inclusion/Exclusion

**The anchor bar (T) is EXCLUDED from forward measurements.**

| Measurement Type       | Range                    | Anchor Included? |
|------------------------|--------------------------|------------------|
| Forward return         | close[T] → close[T+N]    | Reference only   |
| MFE                    | high[T+1] ... high[T+N]  | NO               |
| MAE                    | low[T+1] ... low[T+N]    | NO               |
| Realized volatility    | ret[T+1] ... ret[T+N]    | NO               |

The anchor bar provides the **reference price** (close[T]) but is not part of the forward window.

### 2.3 Session Boundary Behavior

**Outcomes continue across session boundaries.**

| Scenario                              | Behavior                                      |
|---------------------------------------|-----------------------------------------------|
| Forward window spans session close    | Continue measurement into next session        |
| Gap between sessions                  | Use actual prices; do not interpolate         |
| Weekend/holiday gap                   | Treat as continuous sequence (no bar skip)    |

Bars are indexed sequentially as they appear in the canonical L1 table. Session boundaries do not interrupt the sequence.

### 2.4 Lookahead Prohibition Outside Option C

**BINDING RULE**: Lookahead is permitted ONLY in Option C.

| Layer    | Lookahead Allowed? | Enforcement                          |
|----------|--------------------|--------------------------------------|
| Option A | NO                 | Ingest validation                    |
| Option B | NO                 | Schema constraints, code review      |
| Option C | YES                | Within defined windows only          |

Any Option B code that references T+1 or later is **non-conformant** and must be rejected.

---

## 3. Outcome-Specific Rules

### 3.1 Forward Return (`fwd_ret_N`)

**Status**: ACTIVE

#### 3.1.1 Required Inputs

| Input       | Source | Field              |
|-------------|--------|--------------------|
| close[T]    | L1     | Anchor block close |
| close[T+N]  | L1     | Forward block close|

#### 3.1.2 Computation Definition

```
fwd_ret_N = (close[T+N] - close[T]) / close[T]
```

Where:
- `close[T]` is the close price of the anchor block
- `close[T+N]` is the close price of the block N periods forward
- Result is a signed fractional return (positive = price increased)

#### 3.1.3 Window Alignment

| Parameter | Value                                      |
|-----------|--------------------------------------------|
| Start     | close[T] (anchor close, reference only)    |
| End       | close[T+N] (forward close)                 |
| Bars used | 1 (only the endpoint)                      |

#### 3.1.4 Edge Cases

| Condition                     | Behavior                                      |
|-------------------------------|-----------------------------------------------|
| Block T+N does not exist      | `fwd_ret_N` = NULL                            |
| close[T] = 0                  | `fwd_ret_N` = NULL (division undefined)       |
| close[T] = NULL               | `fwd_ret_N` = NULL                            |
| close[T+N] = NULL             | `fwd_ret_N` = NULL                            |
| Gap between T and T+N         | Compute using actual closes; no adjustment    |

#### 3.1.5 Canonical Windows

| Outcome      | N  | Duration    |
|--------------|----|-------------|
| `fwd_ret_1`  | 1  | 2 hours     |
| `fwd_ret_3`  | 3  | 6 hours     |
| `fwd_ret_6`  | 6  | 12 hours    |

---

### 3.2 Maximum Favorable Excursion (`mfe_N`)

**Status**: ACTIVE

#### 3.2.1 Required Inputs

| Input         | Source | Field                        |
|---------------|--------|------------------------------|
| close[T]      | L1     | Anchor block close           |
| high[T+1..N]  | L1     | High prices of forward bars  |

#### 3.2.2 Computation Definition

```
mfe_N = (max(high[T+1], high[T+2], ..., high[T+N]) - close[T]) / close[T]
```

Where:
- The maximum is taken over all highs in the forward window
- Result is **unsigned** (always ≥ 0 when max high ≥ close[T])
- If max high < close[T], result is 0 (not negative)

**Formal definition with floor at zero**:
```
mfe_N = max(0, (max_high - close[T]) / close[T])
where max_high = max(high[T+k] for k in 1..N)
```

#### 3.2.3 Window Alignment

| Parameter | Value                                      |
|-----------|--------------------------------------------|
| Start     | high[T+1] (first bar after anchor)         |
| End       | high[T+N] (N-th bar after anchor)          |
| Bars used | N                                          |

#### 3.2.4 Edge Cases

| Condition                           | Behavior                                  |
|-------------------------------------|-------------------------------------------|
| Fewer than N bars after T           | `mfe_N` = NULL                            |
| close[T] = 0                        | `mfe_N` = NULL                            |
| close[T] = NULL                     | `mfe_N` = NULL                            |
| Any high[T+k] = NULL (k ≤ N)        | `mfe_N` = NULL                            |
| All highs ≤ close[T]                | `mfe_N` = 0                               |

#### 3.2.5 Canonical Windows

| Outcome   | N  | Duration    |
|-----------|----|-------------|
| `mfe_3`   | 3  | 6 hours     |
| `mfe_6`   | 6  | 12 hours    |

---

### 3.3 Maximum Adverse Excursion (`mae_N`)

**Status**: ACTIVE

#### 3.3.1 Required Inputs

| Input        | Source | Field                       |
|--------------|--------|-----------------------------|
| close[T]     | L1     | Anchor block close          |
| low[T+1..N]  | L1     | Low prices of forward bars  |

#### 3.3.2 Computation Definition

```
mae_N = (close[T] - min(low[T+1], low[T+2], ..., low[T+N])) / close[T]
```

Where:
- The minimum is taken over all lows in the forward window
- Result is **unsigned** (always ≥ 0 when min low ≤ close[T])
- If min low > close[T], result is 0 (not negative)

**Formal definition with floor at zero**:
```
mae_N = max(0, (close[T] - min_low) / close[T])
where min_low = min(low[T+k] for k in 1..N)
```

#### 3.3.3 Window Alignment

| Parameter | Value                                      |
|-----------|--------------------------------------------|
| Start     | low[T+1] (first bar after anchor)          |
| End       | low[T+N] (N-th bar after anchor)           |
| Bars used | N                                          |

#### 3.3.4 Edge Cases

| Condition                           | Behavior                                  |
|-------------------------------------|-------------------------------------------|
| Fewer than N bars after T           | `mae_N` = NULL                            |
| close[T] = 0                        | `mae_N` = NULL                            |
| close[T] = NULL                     | `mae_N` = NULL                            |
| Any low[T+k] = NULL (k ≤ N)         | `mae_N` = NULL                            |
| All lows ≥ close[T]                 | `mae_N` = 0                               |

#### 3.3.5 Canonical Windows

| Outcome   | N  | Duration    |
|-----------|----|-------------|
| `mae_3`   | 3  | 6 hours     |
| `mae_6`   | 6  | 12 hours    |

---

### 3.4 Realized Volatility (`rvol_N`)

**Status**: ACTIVE

#### 3.4.1 Required Inputs

| Input           | Source | Field                         |
|-----------------|--------|-------------------------------|
| close[T]        | L1     | Anchor block close            |
| close[T+1..N]   | L1     | Close prices of forward bars  |

#### 3.4.2 Computation Definition

**Step 1**: Compute bar-to-bar returns in forward window:
```
ret[T+k] = (close[T+k] - close[T+k-1]) / close[T+k-1]
for k in 1..N
```

Note: `ret[T+1]` uses `close[T]` as the prior close.

**Step 2**: Compute sample standard deviation:
```
rvol_N = sqrt( sum((ret[T+k] - mean_ret)^2 for k in 1..N) / (N - 1) )
where mean_ret = sum(ret[T+k] for k in 1..N) / N
```

This is the **sample standard deviation** (Bessel's correction with N-1 denominator).

#### 3.4.3 Window Alignment

| Parameter | Value                                       |
|-----------|---------------------------------------------|
| Start     | ret[T+1] (return from T to T+1)             |
| End       | ret[T+N] (return from T+N-1 to T+N)         |
| Returns   | N returns computed                          |

#### 3.4.4 Edge Cases

| Condition                           | Behavior                                  |
|-------------------------------------|-------------------------------------------|
| Fewer than N bars after T           | `rvol_N` = NULL                           |
| N < 2                               | `rvol_N` = NULL (stddev undefined)        |
| Any close[T+k] = NULL (k ≤ N)       | `rvol_N` = NULL                           |
| Any close[T+k-1] = 0 (k ≤ N)        | `rvol_N` = NULL (division undefined)      |
| All returns identical               | `rvol_N` = 0                              |

#### 3.4.5 Canonical Windows

| Outcome   | N  | Duration    |
|-----------|----|-------------|
| `rvol_6`  | 6  | 12 hours    |

---

### 3.5 Time to Threshold (`ttt_*`)

**Status**: DRAFT

#### 3.5.1 Implementation Deferred

Time-to-threshold outcomes are **not authorized for implementation** because:

1. **Threshold parameterization undefined**: No canonical threshold levels have been approved
2. **Direction semantics unresolved**: Bullish vs bearish reference frames require specification
3. **Window bounds unspecified**: Maximum search window not defined

#### 3.5.2 Activation Requirements

To activate `ttt_*` outcomes, the following approvals are required:

| Requirement                          | Approval Authority              |
|--------------------------------------|---------------------------------|
| Define canonical threshold levels    | Governance review               |
| Specify direction semantics          | OPTION_C_OUTCOMES amendment     |
| Define maximum search window         | OPTION_C_OUTCOMES amendment     |
| Add test fixtures                    | Implementation review           |

Until these requirements are met, any `ttt_*` implementation is **non-conformant**.

---

## 4. NULL & Missing Data Handling

### 4.1 When Outcomes Must Be NULL

An outcome **MUST** be NULL when:

| Condition                                    | Rationale                          |
|----------------------------------------------|------------------------------------|
| Required input is NULL                       | Garbage in → NULL out              |
| Forward window extends beyond available data | Cannot compute without future bars |
| Division by zero would occur                 | Mathematically undefined           |
| Insufficient data for statistical measure    | e.g., stddev requires N ≥ 2        |

### 4.2 Partial Computation Prohibition

**Partial computation is NOT allowed.**

| Scenario                              | Correct Behavior                          |
|---------------------------------------|-------------------------------------------|
| 5 of 6 bars available for `mfe_6`     | `mfe_6` = NULL (not partial MFE)          |
| Gap in middle of window               | Compute if all bars exist; else NULL      |
| Some highs NULL, some valid           | NULL (no partial max)                     |

An outcome is either **fully computable** or **NULL**. There is no middle ground.

### 4.3 Sentinel Value Prohibition

**Sentinel values are PROHIBITED.**

| Prohibited Pattern           | Correct Alternative          |
|------------------------------|------------------------------|
| Return -1 for missing        | Return NULL                  |
| Return NaN for undefined     | Return NULL                  |
| Return 0 for missing         | Return NULL                  |
| Return -999 for error        | Return NULL                  |

All outcome columns must be **nullable**. Missing data is represented by NULL, never by a magic number.

---

## 5. Determinism & Replayability

### 5.1 Determinism Requirement

**Same inputs MUST produce same outputs.**

```
Given: inputs I at time T
Then:  outcome(I) at time T₁ = outcome(I) at time T₂
For all T₁, T₂
```

No randomness, no sampling, no approximate algorithms.

### 5.2 No External State Dependency

Outcome computation **SHALL NOT** depend on:

| Prohibited Dependency          | Rationale                              |
|--------------------------------|----------------------------------------|
| Current wall-clock time        | Breaks replayability                   |
| Execution order of rows        | Non-deterministic                      |
| Database connection state      | External state                         |
| Environment variables          | Non-reproducible                       |
| Random number generators       | Non-deterministic                      |

### 5.3 Historical Replay Guarantee

**Full historical replay MUST reproduce identical results.**

If Option C is recomputed from scratch using the same:
- L1 data
- L2 data
- L3 data
- Implementation version

Then all outcome values **MUST** be bit-for-bit identical to the original computation.

### 5.4 Floating Point Handling

For floating point outcomes:

| Requirement                          | Specification                          |
|--------------------------------------|----------------------------------------|
| Precision                            | IEEE 754 double precision (64-bit)     |
| Rounding                             | Round-to-nearest, ties-to-even         |
| Comparison tolerance for tests       | 1e-12 relative tolerance               |

Implementations must not introduce platform-dependent floating point variance.

---

## 6. Testing Obligations

### 6.1 Minimum Test Cases Per Outcome

Each ACTIVE outcome requires the following **mandatory test fixtures**:

| Fixture Category         | Description                                    | Required |
|--------------------------|------------------------------------------------|----------|
| Positive move            | Price increases over window                    | YES      |
| Negative move            | Price decreases over window                    | YES      |
| Flat move                | Price unchanged (or nearly unchanged)          | YES      |
| High volatility          | Large swings within window                     | YES      |
| Session boundary         | Window spans session close                     | YES      |
| Short history            | Insufficient bars for window                   | YES      |
| NULL input               | At least one required input is NULL            | YES      |

**Minimum**: 7 test cases per outcome × 8 ACTIVE outcomes = **56 test cases minimum**.

### 6.2 Fixture Specifications

#### 6.2.1 Positive Move Fixture

```
Anchor close[T] = 1.00000
Forward closes increase monotonically
Expected: fwd_ret_N > 0, mfe_N > 0, mae_N ≥ 0
```

#### 6.2.2 Negative Move Fixture

```
Anchor close[T] = 1.00000
Forward closes decrease monotonically
Expected: fwd_ret_N < 0, mfe_N ≥ 0, mae_N > 0
```

#### 6.2.3 Flat Move Fixture

```
Anchor close[T] = 1.00000
All forward closes = 1.00000
All forward highs = 1.00000
All forward lows = 1.00000
Expected: fwd_ret_N = 0, mfe_N = 0, mae_N = 0, rvol_N = 0
```

#### 6.2.4 High Volatility Fixture

```
Anchor close[T] = 1.00000
Forward window has large swings (e.g., ±2%)
Expected: rvol_N > baseline, mfe_N > 0, mae_N > 0
```

#### 6.2.5 Session Boundary Fixture

```
Anchor block T is last block of session
Forward window spans into next session
Gap may exist between sessions
Expected: Outcomes computed normally using actual prices
```

#### 6.2.6 Short History Fixture

```
Anchor block T exists
Fewer than N blocks exist after T
Expected: All outcomes requiring N bars = NULL
```

#### 6.2.7 NULL Input Fixture

```
Anchor block T has close[T] = NULL
OR forward block has required field = NULL
Expected: Affected outcomes = NULL
```

### 6.3 Failure Protocol

If implementation diverges from contract:

| Divergence Type                     | Action Required                            |
|-------------------------------------|--------------------------------------------|
| Test fails against fixture          | Block merge; fix implementation            |
| Edge case produces wrong NULL       | Block merge; fix implementation            |
| Floating point beyond tolerance     | Block merge; investigate precision         |
| New edge case discovered            | Add to contract; add test; then fix        |

**No implementation may be merged if any test fails.**

---

## 7. Promotion Rules

### 7.1 Preconditions for CANONICAL Status

An Option C outcome implementation may be promoted to CANONICAL when:

| Precondition                         | Evidence Required                          |
|--------------------------------------|--------------------------------------------|
| All mandatory tests pass             | CI/CD test report                          |
| Edge cases documented                | Implementation notes                       |
| Determinism verified                 | Replay test with identical results         |
| No sentinel values used              | Code review attestation                    |
| NULL handling correct                | Test coverage report                       |
| Floating point stable                | Cross-platform test results                |

### 7.2 Required Validation Artifacts

Before CANONICAL promotion:

| Artifact                             | Location                                   |
|--------------------------------------|--------------------------------------------|
| Test fixture file                    | `tests/option_c/fixtures/`                 |
| Test result log                      | CI/CD artifacts                            |
| Code review sign-off                 | PR approval record                         |
| Replay validation report             | `artifacts/option_c_validation/`           |

### 7.3 Required Reviewers

CANONICAL promotion requires approval from:

| Role                    | Responsibility                              |
|-------------------------|---------------------------------------------|
| Implementation author   | Correctness attestation                     |
| Governance reviewer     | Contract conformance                        |
| Independent verifier    | Replay validation                           |

Minimum **2 approvals** required, including at least one non-author.

### 7.4 Activating DRAFT Outcomes

To move an outcome from DRAFT to ACTIVE:

1. **Amend OPTION_C_OUTCOMES_v0.1.md** with complete specification
2. **Amend this contract** with computation rules and edge cases
3. **Obtain governance approval** for the amendment
4. **Create test fixtures** before implementation begins
5. **Update status** in both documents

DRAFT outcomes **SHALL NOT** be implemented until activated.

---

## 8. Summary of Implementation Constraints

| Constraint                          | Binding? | Enforcement                      |
|-------------------------------------|----------|----------------------------------|
| Spec wins over code                 | YES      | Code review, governance          |
| Anchor bar excluded from window     | YES      | Test fixtures                    |
| No lookahead outside Option C       | YES      | Schema constraints, review       |
| NULL for missing/invalid            | YES      | Test fixtures                    |
| No sentinel values                  | YES      | Code review                      |
| Deterministic computation           | YES      | Replay tests                     |
| 7 fixtures per outcome minimum      | YES      | CI/CD gate                       |
| 2 approvals for CANONICAL           | YES      | PR policy                        |

---

## Appendix A: Document Control

| Version | Date       | Change Description                    |
|---------|------------|---------------------------------------|
| 0.1     | 2026-01-20 | Initial implementation contract       |

---

**END OF CONTRACT**
