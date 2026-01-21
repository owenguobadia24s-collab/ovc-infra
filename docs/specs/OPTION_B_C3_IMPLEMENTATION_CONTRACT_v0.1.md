# Option B – C3 Implementation Contract v0.1

**[STATUS: CANONICAL]**

> **[CHANGE][CHANGED] Enforcement Note (2026-01-20)**
> This contract is now CANONICAL. The specification takes precedence over code.
> If implementation disagrees with this contract, the implementation is non-conformant.
> Validation evidence: [C3_v0_1_validation.md](../../reports/validation/C3_v0_1_validation.md)

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Created | 2026-01-20 |
| Promoted | 2026-01-20 |
| Author | OVC Infrastructure Team |
| Governs | C3 Implementation Behavior |
| Parent Documents | OPTION_B_C3_CHARTER_v0.1.md, OPTION_B_C3_FEATURES_v0.1.md |
| Governance | GOVERNANCE_RULES_v0.1.md |

---

## 1. Source of Truth

### 1.1 Semantic Authority

The **semantic meaning** of each C3 feature is defined in:

```
docs/ops/OPTION_B_C3_FEATURES_v0.1.md
```

This implementation contract defines **how** those meanings are computed, not **what** they mean.

### 1.2 Precedence Rule

If implementation code produces outputs that disagree with the feature specification:

1. The **specification wins**
2. The code is **non-conformant** and must be corrected
3. No exception: code cannot redefine semantic meanings

### 1.3 Contract Scope

| Document | Defines |
|----------|---------|
| FEATURES_v0.1.md | What each label means |
| This contract | How labels are derived (thresholds, precedence, edge cases) |
| SQL/Python code | Executable implementation (must conform to both) |

---

## 2. Input Semantics

### 2.1 Required Inputs by Feature

| Feature | Required C1 Inputs | Required C2 Inputs |
|---------|-------------------|-------------------|
| `c3_trend_bias` | — | `dir_streak`, `dir_change` |
| `c3_volatility_regime` | — | `rng_streak` |
| `c3_structure_type` | `body`, `rng` | — |
| `c3_momentum_state` | `body` | `dir_streak`, `dir_change` |
| `c3_session_position` | `block_id` | — |
| `c3_wick_dominance` | `wick_top`, `wick_bot`, `rng` | — |
| `c3_range_context` | `rng` | `rng_avg_5` |

### 2.2 NULL Handling Rules

When a required input is NULL:

| Condition | Behavior |
|-----------|----------|
| Any required C1 input is NULL | Output the feature's **fallback label** |
| Any required C2 input is NULL | Output the feature's **fallback label** |
| `block_id` is NULL | Output NULL (row is invalid) |
| `rng = 0` (not NULL) | Apply specific edge case rules per feature |

### 2.3 Fallback Labels by Feature

| Feature | Fallback Label | Rationale |
|---------|----------------|-----------|
| `c3_trend_bias` | `'neutral'` | No directional information available |
| `c3_volatility_regime` | `'normal'` | Assume baseline volatility |
| `c3_structure_type` | `'balanced'` | Assume typical structure |
| `c3_momentum_state` | `'steady'` | Assume no momentum change |
| `c3_session_position` | NULL | Cannot determine without block_id |
| `c3_wick_dominance` | `'balanced'` | Assume no dominant rejection |
| `c3_range_context` | `'typical'` | Assume average range |

### 2.4 "Unknown" vs NULL

This implementation does NOT use an `'unknown'` label.

- NULL output = row is invalid or unprocessable
- Fallback label = insufficient data but row is valid

All valid rows MUST produce a non-NULL label for each feature.

---

## 3. Label Resolution Rules

### 3.1 Mutual Exclusivity Guarantee

For every feature, **exactly one label** MUST be assigned per block.

- Labels within a feature are **mutually exclusive**
- Overlapping conditions are resolved by **precedence order**
- No block may have zero labels or multiple labels for a single feature

### 3.2 Precedence Rules by Feature

#### `c3_trend_bias`

Evaluation order (first match wins):

1. If `dir_change = true` → `'fading'`
2. If `dir_streak >= 3` → `'sustained'`
3. If `dir_streak IN (1, 2)` → `'nascent'`
4. Otherwise → `'neutral'`

#### `c3_volatility_regime`

Evaluation order:

1. If `rng_streak >= 2` AND streak direction is narrowing → `'compressed'`
2. If `rng_streak >= 2` AND streak direction is widening → `'expanded'`
3. Otherwise → `'normal'`

Note: "narrowing" and "widening" refer to consecutive ranges decreasing or increasing.

#### `c3_structure_type`

Evaluation order:

1. If `rng = 0` → `'indecisive'`
2. If `body / rng >= 0.7` → `'decisive'`
3. If `body / rng <= 0.3` → `'indecisive'`
4. Otherwise → `'balanced'`

#### `c3_momentum_state`

Evaluation order:

1. If `dir_change = true` → `'reversing'`
2. If streak continuing AND `body > prev_body * 1.2` → `'accelerating'`
3. If streak continuing AND `body < prev_body * 0.8` → `'decelerating'`
4. Otherwise → `'steady'`

#### `c3_session_position`

Deterministic mapping (no precedence needed):

| Block Letter | Label |
|--------------|-------|
| A, B, C, D | `'early'` |
| E, F, G, H | `'mid'` |
| I, J, K, L | `'late'` |
| Other/Invalid | NULL |

#### `c3_wick_dominance`

Evaluation order:

1. If `rng = 0` → `'no_wicks'`
2. If `(wick_top + wick_bot) / rng < 0.1` → `'no_wicks'`
3. If `wick_top / rng >= 0.3` AND `wick_bot / rng < 0.15` → `'top_heavy'`
4. If `wick_bot / rng >= 0.3` AND `wick_top / rng < 0.15` → `'bottom_heavy'`
5. Otherwise → `'balanced'`

#### `c3_range_context`

Evaluation order:

1. If `rng_avg_5` is NULL or 0 → `'typical'`
2. If `rng < rng_avg_5 * 0.6` → `'narrow'`
3. If `rng > rng_avg_5 * 1.4` → `'wide'`
4. Otherwise → `'typical'`

---

## 4. Lookback & Window Semantics

### 4.1 Allowed Lookback Ranges

| Feature | Maximum Lookback | Notes |
|---------|------------------|-------|
| `c3_trend_bias` | Current + C2 streak | Streak computed in C2 |
| `c3_volatility_regime` | Current + C2 streak | Streak computed in C2 |
| `c3_structure_type` | Current block only | No lookback required |
| `c3_momentum_state` | Current + 1 prior | Compares current vs previous body |
| `c3_session_position` | Current block only | Deterministic from block_id |
| `c3_wick_dominance` | Current block only | No lookback required |
| `c3_range_context` | Current + 5-block average | Uses C2's `rng_avg_5` |

### 4.2 Session Boundary Handling

Session boundaries (block A following block L) affect:

| Feature | Boundary Behavior |
|---------|-------------------|
| `c3_trend_bias` | Streaks reset at session start (handled in C2) |
| `c3_volatility_regime` | Streaks reset at session start (handled in C2) |
| `c3_momentum_state` | No prior block available → fallback to `'steady'` |
| `c3_range_context` | Lookback average may span sessions (allowed) |

C3 does NOT independently detect session boundaries; it relies on C2's streak calculations.

### 4.3 Short History Handling

When insufficient history exists:

| Condition | Behavior |
|-----------|----------|
| First block of dataset | Use fallback labels for lookback features |
| First block of session | Streaks = 0 or 1 (from C2), labels derived normally |
| Fewer than 5 blocks for average | Use available blocks; if none, fallback |

---

## 5. Determinism & Stability

### 5.1 Determinism Guarantee

Given identical C1 and C2 inputs, C3 MUST produce **identical outputs**.

- No randomness in any computation
- No dependence on row processing order
- No dependence on wall-clock time
- No dependence on external state or APIs

### 5.2 Prohibited Dependencies

C3 computations MUST NOT depend on:

| Prohibited Dependency | Reason |
|-----------------------|--------|
| Current timestamp | Would break replay |
| Row insertion order | Would break parallel execution |
| External API calls | Non-deterministic |
| Random number generators | Non-deterministic |
| Global mutable state | Non-reproducible |

### 5.3 Replay Guarantee

C3 outputs MUST be fully reproducible:

```
Historical backfill on day D₁ → Output set O
Historical backfill on day D₂ → Output set O (identical)
```

If replay produces different outputs, the implementation is **non-conformant**.

---

## 6. Threshold Governance

### 6.1 Threshold Registry

All numeric thresholds are defined in **this contract** (Section 3.2).

| Feature | Threshold | Value | Meaning |
|---------|-----------|-------|---------|
| `c3_trend_bias` | Sustained streak minimum | 3 | Streak ≥ 3 = sustained |
| `c3_structure_type` | Decisive ratio | 0.7 | body/rng ≥ 0.7 = decisive |
| `c3_structure_type` | Indecisive ratio | 0.3 | body/rng ≤ 0.3 = indecisive |
| `c3_momentum_state` | Acceleration ratio | 1.2 | body > prev * 1.2 = accelerating |
| `c3_momentum_state` | Deceleration ratio | 0.8 | body < prev * 0.8 = decelerating |
| `c3_wick_dominance` | Dominance threshold | 0.3 | wick/rng ≥ 0.3 = dominant |
| `c3_wick_dominance` | Non-dominant threshold | 0.15 | wick/rng < 0.15 = not dominant |
| `c3_wick_dominance` | No-wick threshold | 0.1 | total_wick/rng < 0.1 = no wicks |
| `c3_range_context` | Narrow multiplier | 0.6 | rng < avg * 0.6 = narrow |
| `c3_range_context` | Wide multiplier | 1.4 | rng > avg * 1.4 = wide |

### 6.2 Threshold Change Rules

| Change Type | Version Impact | Requirements |
|-------------|----------------|--------------|
| Threshold value change (same label set) | MINOR bump | Validation evidence, rationale documented |
| New threshold added | MINOR bump | Must not change existing label assignments |
| Threshold removed | MAJOR bump | Migration plan required |
| Label vocabulary change | MAJOR bump | Requires new feature version |

### 6.3 Threshold Intent Statement

All thresholds in this contract are **descriptive, not decisional**.

- Thresholds define label boundaries, not action triggers
- Changing a threshold changes classification, not strategy
- Downstream layers (Option C) must NOT interpret threshold crossings as signals

---

## 7. Testing Obligations

### 7.1 Minimum Test Cases per Feature

Each C3 feature MUST have at least **5 test cases**:

1. **Happy path**: Standard input → expected label
2. **Boundary condition**: Input at exact threshold → verify correct label
3. **NULL input**: Required input NULL → verify fallback
4. **Edge case**: Zero values, extreme values
5. **Precedence verification**: Multiple conditions true → verify first-match wins

### 7.2 Mandatory Semantic Fixtures

The test suite MUST include fixtures for:

| Fixture Name | Description | Expected Behaviors |
|--------------|-------------|-------------------|
| `fixture_clean_trend` | 5+ consecutive same-direction blocks | `trend_bias='sustained'`, `momentum_state='steady'` or better |
| `fixture_choppy` | Alternating direction blocks | `trend_bias='neutral'`, `momentum_state='reversing'` |
| `fixture_vol_expansion` | 3+ consecutive widening ranges | `volatility_regime='expanded'` |
| `fixture_vol_compression` | 3+ consecutive narrowing ranges | `volatility_regime='compressed'` |
| `fixture_session_transition` | Block L followed by block A | Correct `session_position` labels, streak resets |
| `fixture_doji_sequence` | Small body / large range blocks | `structure_type='indecisive'` |
| `fixture_decisive_move` | Large body / small wick blocks | `structure_type='decisive'`, `wick_dominance='no_wicks'` |

### 7.3 Failure Protocol

If implementation output disagrees with expected fixture output:

1. **STOP** – Do not merge implementation
2. **DIAGNOSE** – Identify whether spec or code is wrong
3. **RESOLVE** – If spec is wrong, update spec first (with review)
4. **RETEST** – Verify all fixtures pass after fix

No exception: implementation may not override specification.

---

## 8. Promotion Rules

### 8.1 Preconditions for CANONICAL Promotion

C3 may be promoted to CANONICAL only when:

| Precondition | Evidence Required |
|--------------|-------------------|
| All fixtures pass | Test report showing 100% pass |
| Determinism verified | 3+ replay runs with identical output |
| Lookback compliance | Audit confirming no future data access |
| NULL handling verified | Test cases for all NULL scenarios |
| Threshold documentation | All thresholds listed in this contract |
| Downstream compatibility | Option C can consume C3 outputs |

### 8.2 Required Validation Artifacts

Before promotion, the following artifacts MUST exist:

| Artifact | Location | Contents |
|----------|----------|----------|
| Test report | `artifacts/c3_validation/test_report.json` | Fixture results |
| Replay log | `artifacts/c3_validation/replay_log.txt` | 3+ run comparison |
| Coverage report | `artifacts/c3_validation/coverage.json` | Feature × fixture matrix |
| Threshold audit | `artifacts/c3_validation/threshold_audit.md` | All thresholds documented |

### 8.3 Required Reviewers

Promotion to CANONICAL requires approval from:

| Role | Responsibility |
|------|----------------|
| C3 Feature Owner | Semantic correctness |
| C2 Maintainer | Input compatibility |
| Option C Consumer | Downstream compatibility |
| Governance Lead | Charter compliance |

Minimum: 2 reviewers, including at least one from outside C3 implementation team.

---

## 9. Amendment History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-20 | 0.1 | Initial contract | OVC Infrastructure Team |

---

## 10. Authorization

### 10.1 Contract Status

This implementation contract is **CANONICAL** and governs all C3 implementations.

> **[CHANGE][CHANGED]** Contract promoted to CANONICAL (2026-01-20).

### 10.2 Implementation Status

Implementation is complete and validated:

- SQL View: `derived.v_ovc_c3_features_v0_1`
- Implementation CONFORMS to this contract
- Validation evidence: [C3_v0_1_validation.md](../../reports/validation/C3_v0_1_validation.md)

### 10.3 What This Contract Does NOT Authorize

- Changing semantic meanings (requires FEATURES_v0.1.md update)
- Writing Option C evaluation logic
- Introducing action thresholds or signals
- Bypassing validation requirements

### 10.4 Downstream Authorization

With C3 CANONICAL:

- Option C is authorized to consume C3 features
- C3 outputs are stable and may be depended upon
- Label vocabularies and thresholds are frozen

---

**[END OF IMPLEMENTATION CONTRACT]**
