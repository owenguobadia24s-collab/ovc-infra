# Option B – C2 Implementation Contract v0.1

[CHANGE][CHANGED] **[STATUS: CANONICAL]**

> **Enforcement (2026-01-20):**  
> All implementations must comply with this contract.  
> Spec changes must precede code changes; implementation must never lead spec.

| Field              | Value                                    |
|--------------------|------------------------------------------|
| Version            | 0.1                                      |
| Effective Date     | 2026-01-20                               |
| Feature Spec       | OPTION_B_C2_FEATURES_v0.1.md             |
| Governing Charter  | OPTION_B_C2_CHARTER_v0.1.md              |
| Governance         | GOVERNANCE_RULES_v0.1.md                 |

---

## 1. Source of Truth

### 1.1 Specification Authority

The **sole source of truth** for C2 feature meanings is:

```
docs/ops/OPTION_B_C2_FEATURES_v0.1.md
```

### 1.2 Conflict Resolution

| Scenario                              | Resolution                                |
|---------------------------------------|-------------------------------------------|
| Implementation disagrees with spec    | **Spec wins.** Implementation must change.|
| Spec is ambiguous                     | Clarify spec first; do not assume.        |
| Edge case not covered in spec         | Add to spec before implementing.          |
| Test reveals spec error               | Update spec via governance review.        |

### 1.3 Binding Hierarchy

```
OPTION_B_C2_FEATURES_v0.1.md     (WHAT)
         │
         ▼
This Document                    (HOW)
         │
         ▼
Implementation Code              (executes HOW per WHAT)
```

Implementation code must conform to both documents. If this contract contradicts the feature spec, the feature spec governs meaning; this contract governs mechanics.

---

## 2. Window Semantics (Binding)

### 2.1 Rolling Window Inclusion Rule

**The current bar is INCLUDED in all windows.**

| Window Type     | Definition                                          |
|-----------------|-----------------------------------------------------|
| Fixed N-bar     | `[t-(N-1), t-(N-2), ..., t-1, t]` — current bar is rightmost |
| Session STD     | `[session_start, ..., t]` — current bar is rightmost |

Example for `rng_avg_3` at bar `t`:
```
Window = [t-2, t-1, t]
Result = (rng[t-2] + rng[t-1] + rng[t]) / 3
```

### 2.2 Session Boundary Behavior

#### 2.2.1 Session Definition

A session consists of 12 consecutive 2H blocks labeled A through L:
- Block A = session start (index 1)
- Block L = session end (index 12)

Session boundaries are determined by the block letter in `block_id`.

#### 2.2.2 Fixed N-Bar Windows at Session Boundaries

Fixed N-bar windows **MAY cross session boundaries**.

| Scenario                          | Behavior                                  |
|-----------------------------------|-------------------------------------------|
| Window spans two sessions         | Include bars from both sessions           |
| Window spans session gap          | If bars exist, include; if gap, treat as missing |

Example: `rng_avg_3` at block A (session start) uses:
- Block A of current session
- Blocks K and L of prior session (if available)

#### 2.2.3 Session-to-Date Windows at Session Boundaries

Session-to-date (STD) windows **reset at session start**.

| Scenario                          | Behavior                                  |
|-----------------------------------|-------------------------------------------|
| Block A (session start)           | Window contains only block A              |
| Block B                           | Window contains blocks A and B            |
| Block L (session end)             | Window contains blocks A through L        |

### 2.3 Partial Window Handling (Insufficient History)

When a window cannot be fully populated:

| Window Type     | Required Minimum | If Insufficient       |
|-----------------|------------------|-----------------------|
| Fixed 3-bar     | 3 bars           | Return NULL           |
| Fixed 6-bar     | 6 bars           | Return NULL           |
| Session STD     | 1 bar            | Compute with available|

**Binding rule:** Fixed N-bar windows return NULL if fewer than N bars are available. Session STD windows compute with available bars (minimum 1).

---

## 3. NULL & Edge Case Rules

### 3.1 NULL Propagation Rules

#### 3.1.1 Default Propagation

**If any required input within a window is NULL, the output is NULL.**

This applies to all C2 features unless explicitly overridden in the feature spec.

#### 3.1.2 Propagation Table

| Feature               | NULL in Window → Output |
|-----------------------|-------------------------|
| `rng_avg_3`           | NULL                    |
| `rng_avg_6`           | NULL                    |
| `dir_streak`          | NULL (streak breaks)    |
| `session_block_idx`   | NULL                    |
| `session_rng_cum`     | NULL                    |
| `session_dir_net`     | NULL                    |
| `rng_rank_6`          | NULL                    |
| `body_rng_pct_avg_3`  | NULL                    |

### 3.2 C1 Input NULL Handling

When a C1 input field is NULL:

| C1 Field          | C2 Features Affected           | Behavior              |
|-------------------|--------------------------------|-----------------------|
| `rng` is NULL     | `rng_avg_*`, `rng_rank_6`, `session_rng_cum` | Output NULL |
| `dir` is NULL     | `dir_streak`, `session_dir_net`| Output NULL           |
| `body_rng_pct` NULL| `body_rng_pct_avg_3`          | Output NULL           |
| `block_id` NULL   | `session_block_idx`, all STD   | Output NULL           |

### 3.3 Special Case Rules

#### 3.3.1 Flat Bars (dir = 0)

A flat bar has `dir = 0` (open equals close).

| Feature           | Flat Bar Handling                          |
|-------------------|--------------------------------------------|
| `dir_streak`      | Streak = 0; breaks any prior streak        |
| `session_dir_net` | Contributes 0 to sum                       |

#### 3.3.2 Zero-Range Bars (rng = 0)

A zero-range bar has `rng = 0` (high equals low).

| Feature           | Zero-Range Handling                        |
|-------------------|--------------------------------------------|
| `rng_avg_*`       | Include 0 in average (do not skip)         |
| `rng_rank_6`      | Rank normally; 0 is valid minimum          |
| `session_rng_cum` | Contributes 0 to sum                       |

#### 3.3.3 Session Start Bars (block A)

At block A (session_block_idx = 1):

| Feature               | Session Start Behavior                   |
|-----------------------|------------------------------------------|
| `session_rng_cum`     | Equals `rng[t]` (single bar)             |
| `session_dir_net`     | Equals `dir[t]` (single bar)             |
| `rng_avg_3`           | Uses prior session blocks if available   |
| `dir_streak`          | May continue from prior session          |

---

## 4. Feature-Specific Constraints

### 4.1 `dir_streak` Constraints

#### 4.1.1 Signed Direction Definition

| `dir[t]` Value | Meaning    | Streak Sign |
|----------------|------------|-------------|
| +1             | Bullish    | Positive    |
| -1             | Bearish    | Negative    |
| 0              | Flat/Doji  | Zero        |

#### 4.1.2 Streak Counting Algorithm

```
streak[t] =
  if dir[t] == 0:
    0
  else if dir[t] == dir[t-1] and streak[t-1] != 0:
    streak[t-1] + sign(dir[t])
  else:
    dir[t]
```

**In words:**
1. If current bar is flat → streak is 0
2. If current bar continues prior direction → increment streak magnitude
3. If direction changes or prior was flat → start new streak at ±1

#### 4.1.3 Reset Conditions

Streak resets to ±1 when:
- Direction changes (bullish → bearish or vice versa)
- Prior bar was flat (streak was 0)
- Prior bar was NULL

Streak becomes 0 when:
- Current bar is flat (dir = 0)

#### 4.1.4 Maximum Streak

Streak is capped at ±12 (one full session). If a streak would exceed 12, clamp to 12.

### 4.2 `rng_rank_6` Constraints

#### 4.2.1 Percentile Calculation Definition

**Strict less-than ranking:**

```
rng_rank_6[t] = count(rng[t-5:t-1] where rng[k] < rng[t]) / 5
```

The current bar's range is compared against the 5 prior bars. The rank is the proportion of prior bars with strictly smaller range.

#### 4.2.2 Rank Domain

| Value | Interpretation                              |
|-------|---------------------------------------------|
| 0.0   | Current bar has smallest range in window    |
| 0.2   | 1 of 5 prior bars has smaller range         |
| 0.4   | 2 of 5 prior bars have smaller range        |
| 0.6   | 3 of 5 prior bars have smaller range        |
| 0.8   | 4 of 5 prior bars have smaller range        |
| 1.0   | Current bar has largest range in window     |

#### 4.2.3 Tie Handling

**Ties do not contribute to rank.**

If `rng[t-k] == rng[t]`, that bar does NOT count as "less than."

Example:
- Window ranges: [10, 15, 10, 12, 10, **10**] (current = 10)
- Bars with range < 10: 0
- `rng_rank_6 = 0 / 5 = 0.0`

#### 4.2.4 Minimum History Behavior

If fewer than 6 bars are available, `rng_rank_6` is NULL.

---

## 5. Type & Precision Enforcement

### 5.1 Float Precision

| Requirement          | Specification                             |
|----------------------|-------------------------------------------|
| Minimum precision    | 64-bit IEEE 754 (double)                  |
| Rounding             | No intermediate rounding; round only at output |
| Output precision     | 6 decimal places for display; full precision in storage |

### 5.2 Integer Rules

| Requirement          | Specification                             |
|----------------------|-------------------------------------------|
| `dir_streak`         | Signed 32-bit integer                     |
| `session_block_idx`  | Unsigned 8-bit or larger (values 1-12)    |
| `session_dir_net`    | Signed 32-bit integer                     |

### 5.3 Boolean Strictness

C2 does not define boolean features. If future versions add booleans:

| Requirement          | Specification                             |
|----------------------|-------------------------------------------|
| True values          | Exactly `true` or `1`                     |
| False values         | Exactly `false` or `0`                    |
| No implicit casts    | NULL is not false; 0.0 is not false       |

### 5.4 NULL Representation

| Context              | NULL Representation                       |
|----------------------|-------------------------------------------|
| SQL                  | Native NULL                               |
| Python               | `None` (not `float('nan')`)               |
| JSON                 | `null`                                    |

**NaN is not NULL.** If a computation produces NaN, treat as error, not NULL.

---

## 6. Determinism & Replayability

### 6.1 Determinism Guarantee

**Same input sequence → Same output sequence.**

| Prohibited                          | Rationale                              |
|-------------------------------------|----------------------------------------|
| Random number generation            | Non-deterministic                      |
| Wall-clock time dependence          | Changes between runs                   |
| Execution order dependence          | Parallelization variance               |
| External API calls                  | State may change                       |
| Caching with eviction               | May produce different results          |

### 6.2 Replayability Guarantee

C2 outputs must be **fully reproducible** from:
1. C1 outputs (or canonical blocks where specified)
2. This implementation contract
3. The feature specification

No external state, configuration, or runtime context may influence results.

### 6.3 Idempotency

Running C2 computation multiple times on the same input must produce identical output. Implementations must not accumulate state across runs.

### 6.4 Historical Backfill Consistency

When backfilling historical data:
- C2 outputs for historical bars must match what would have been computed in real-time
- No "future" information may leak into historical computations
- Lookback windows must use only bars that existed at computation time

---

## 7. Testing Obligations

### 7.1 Minimum Test Cases Per Feature

Each C2 feature requires **at minimum** the following test cases:

| Test Category                 | Required Count |
|-------------------------------|----------------|
| Happy path (normal window)    | ≥ 2            |
| Edge case (per §7.2)          | ≥ 4            |
| NULL propagation              | ≥ 1            |
| Type verification             | ≥ 1            |

**Minimum total: 8 test cases per feature.**

### 7.2 Mandatory Sequence Fixtures

Every C2 feature must be tested against these scenarios:

#### 7.2.1 Short History (< Window)

Test behavior when insufficient bars exist:
- First bar of dataset
- Second bar of dataset
- N-1 bars available for N-bar window

Expected: NULL output (for fixed windows)

#### 7.2.2 Session Boundary Crossing

Test behavior at session transitions:
- Block L → Block A transition
- Window spanning two sessions
- STD window reset at block A

Expected: Correct boundary handling per §2.2

#### 7.2.3 Direction Flip

Test `dir_streak` and `session_dir_net` with:
- Bullish → Bearish transition
- Bearish → Bullish transition
- Multiple flips within window

Expected: Correct streak reset and net calculation

#### 7.2.4 Flat-Bar Interruption

Test features with flat bars (dir = 0):
- Flat bar in middle of window
- Consecutive flat bars
- Flat bar at session start

Expected: Correct handling per §3.3.1

### 7.3 Test Fixture Format

Test fixtures must include:

| Field              | Description                               |
|--------------------|-------------------------------------------|
| `fixture_id`       | Unique identifier                         |
| `description`      | What scenario is being tested             |
| `input_sequence`   | Ordered C1 values                         |
| `target_bar`       | Which bar's C2 output is under test       |
| `expected_output`  | Expected C2 value (or NULL)               |
| `rationale`        | Why this is the expected result           |

### 7.4 Failure Protocol

If a test reveals divergence between implementation and spec:

| Divergence Type               | Action                                    |
|-------------------------------|-------------------------------------------|
| Implementation bug            | Fix implementation; do not change spec    |
| Spec ambiguity                | Clarify spec; update tests; fix implementation |
| Spec error discovered         | File governance review; update spec if approved |
| Test fixture error            | Fix fixture; re-run tests                 |

**Implementations must not ship with known spec divergence.**

---

## 8. Promotion Rules

### 8.1 Preconditions for CANONICAL Status

C2 features may be promoted from ACTIVE to CANONICAL when:

| Precondition                         | Evidence Required                       |
|--------------------------------------|-----------------------------------------|
| Implementation matches spec          | All tests pass                          |
| 30-day stability period              | No spec changes in 30 days              |
| No open defects                      | Bug tracker shows zero C2 issues        |
| Downstream consumption               | At least one downstream layer uses C2   |
| Performance acceptable               | Query time < 5s for full history        |

### 8.2 Required Validation Artifacts

Before promotion, the following artifacts must exist:

| Artifact                             | Location                                |
|--------------------------------------|-----------------------------------------|
| Test suite (all passing)             | `tests/option_b/c2/`                    |
| Test coverage report                 | `artifacts/c2_coverage.json`            |
| Sample output validation             | `artifacts/c2_sample_outputs.csv`       |
| Spec compliance checklist            | `docs/ops/C2_COMPLIANCE_CHECKLIST.md`   |

### 8.3 Required Reviewers

Promotion to CANONICAL requires sign-off from:

| Role                    | Responsibility                            |
|-------------------------|-------------------------------------------|
| Spec Owner              | Confirms implementation matches intent    |
| QA Lead                 | Confirms test coverage is sufficient      |
| Downstream Consumer     | Confirms outputs are usable               |

### 8.4 Promotion Ceremony

1. All preconditions verified
2. Reviewers sign off in governance log
3. Version bumped to CANONICAL in feature spec
4. Implementation contract updated to reference CANONICAL spec
5. Announcement to downstream consumers

---

## 9. Implementation Authorization

### 9.1 What This Contract Authorizes

Upon approval of this contract, implementation may begin for:
- SQL views implementing C2 features
- Python computation modules
- Test fixtures and validation scripts

### 9.2 What This Contract Does NOT Authorize

- Changes to C1 outputs or schema
- Writes to `ovc.*` schema
- Threshold logic or decision rules
- Outcome computation

### 9.3 Implementation Must Reference

All implementation code must include a header comment referencing:
```
Spec: OPTION_B_C2_FEATURES_v0.1.md
Contract: OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md
```

---

## 10. Document Control

| Action         | Date       | Author     | Notes                              |
|----------------|------------|------------|------------------------------------|
| Created        | 2026-01-20 | —          | Initial implementation contract    |

---

**END OF CONTRACT**
