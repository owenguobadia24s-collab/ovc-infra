# Option B – L1 Feature Definitions v0.1

[CHANGE][CHANGED] [STATUS: CANONICAL]

> **Canonical Lock (2026-01-20):**  
> Feature meanings are frozen. Any change requires MAJOR version bump + governance approval.  
> Validation evidence: [reports/validation/C1_v0_1_validation.md](../../../reports/validation/C1_v0_1_validation.md)

---

## 1. Purpose of L1 Features

### 1.1 What L1 Represents

L1 features are **single-bar facts** derived exclusively from one 2H block record. Each L1 feature:

- Is computed from fields within a **single row** of `ovc.ovc_blocks_v01_1_min`
- Contains **no lookahead** — uses only information available at bar close
- Contains **no interpretation** — purely mechanical derivation from OHLC and raw fields
- Is **deterministic** — same input always produces same output
- Is **replayable** — can be recomputed from canonical facts at any time

### 1.2 What L1 Is NOT

L1 features explicitly **do not** include:

| Excluded Concept | Reason |
|------------------|--------|
| Multi-bar patterns | Requires sequence context (L2 domain) |
| Rolling statistics | Requires window > 1 bar (L2 domain) |
| Session aggregates | Requires grouping across bars (L2 domain) |
| Trend classification | Requires interpretation or context |
| Signal generation | Requires thresholds or decision logic (L3 domain) |
| Time-of-day bias | Requires external reference data |

---

## 2. Input Contract

### 2.1 Canonical Source

| Property | Value |
|----------|-------|
| Schema | `ovc` |
| Table | `ovc_blocks_v01_1_min` |
| Authority | Option A (LOCKED) |

### 2.2 Required Input Fields

The following fields from MIN v0.1.1 are required for L1 computation:

| Field | Type | Description |
|-------|------|-------------|
| `block_id` | string | Primary key (YYYYMMDD-{A-L}-{SYM}) |
| `sym` | string | Symbol identifier |
| `tf` | string | Timeframe (e.g., "120") |
| `o` | float | Open price |
| `h` | float | High price |
| `l` | float | Low price |
| `c` | float | Close price |
| `rng` | float | Range: high − low |
| `body` | float | Body: |close − open| |
| `dir` | int | Direction: 1 (bull), −1 (bear), 0 (flat) |

### 2.3 Constraints

**Explicit prohibition:**

- ❌ No joins to other tables
- ❌ No window functions spanning multiple rows
- ❌ No subqueries referencing other blocks
- ❌ No external data sources

**Explicit allowance:**

- ✅ Arithmetic on fields within single row
- ✅ Conditional logic on single-row values
- ✅ NULL handling for edge cases

---

## 3. Feature Definitions

### 3.1 Body Ratio

| Property | Value |
|----------|-------|
| **Name** | `body_ratio` |
| **Type** | float |
| **Definition** | Proportion of range occupied by body: \|close − open\| ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED (high = low → division by zero) |
| — Flat bar | 0 (close = open, but range > 0) |
| **Semantic** | Higher values indicate stronger directional conviction within the bar |

---

### 3.2 Upper Wick Ratio

| Property | Value |
|----------|-------|
| **Name** | `upper_wick_ratio` |
| **Type** | float |
| **Definition** | Proportion of range above the body: (high − max(open, close)) ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| — No upper wick | 0 (high = max(open, close)) |
| **Semantic** | Measures rejection from highs; larger values suggest selling pressure |

---

### 3.3 Lower Wick Ratio

| Property | Value |
|----------|-------|
| **Name** | `lower_wick_ratio` |
| **Type** | float |
| **Definition** | Proportion of range below the body: (min(open, close) − low) ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| — No lower wick | 0 (low = min(open, close)) |
| **Semantic** | Measures rejection from lows; larger values suggest buying pressure |

---

### 3.4 Wick Symmetry

| Property | Value |
|----------|-------|
| **Name** | `wick_symmetry` |
| **Type** | float |
| **Definition** | Signed ratio comparing upper vs lower wick: (upper_wick − lower_wick) ÷ (high − low) |
| **Domain** | [−1, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| — Equal wicks | 0 |
| **Semantic** | Positive = longer upper wick (rejection high); Negative = longer lower wick (rejection low) |

---

### 3.5 Body Position

| Property | Value |
|----------|-------|
| **Name** | `body_position` |
| **Type** | float |
| **Definition** | Normalized position of body midpoint within range: ((open + close) / 2 − low) ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| **Semantic** | 0.5 = centered; <0.5 = body in lower half; >0.5 = body in upper half |

---

### 3.6 Close Position

| Property | Value |
|----------|-------|
| **Name** | `close_position` |
| **Type** | float |
| **Definition** | Normalized position of close within range: (close − low) ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| **Semantic** | 0 = closed at low; 1 = closed at high; measures settlement strength |

---

### 3.7 Open Position

| Property | Value |
|----------|-------|
| **Name** | `open_position` |
| **Type** | float |
| **Definition** | Normalized position of open within range: (open − low) ÷ (high − low) |
| **Domain** | [0, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| **Semantic** | Where bar opened relative to its eventual range |

---

### 3.8 Is Doji

| Property | Value |
|----------|-------|
| **Name** | `is_doji` |
| **Type** | bool |
| **Definition** | True if body_ratio ≤ 0.1 (body is ≤10% of range) |
| **Domain** | {true, false} |
| **Units** | Boolean flag |
| **Edge Cases** | |
| — Zero range | FALSE (no valid ratio) |
| **Semantic** | Indecision bar; open ≈ close relative to range |
| **Threshold** | 0.1 (configurable in future versions) |

---

### 3.9 Is Full Body

| Property | Value |
|----------|-------|
| **Name** | `is_full_body` |
| **Type** | bool |
| **Definition** | True if body_ratio ≥ 0.8 (body is ≥80% of range) |
| **Domain** | {true, false} |
| **Units** | Boolean flag |
| **Edge Cases** | |
| — Zero range | FALSE |
| **Semantic** | Strong conviction bar; minimal wicks |
| **Threshold** | 0.8 (configurable in future versions) |

---

### 3.10 Is Hammer Shape

| Property | Value |
|----------|-------|
| **Name** | `is_hammer_shape` |
| **Type** | bool |
| **Definition** | True if: lower_wick_ratio ≥ 0.6 AND upper_wick_ratio ≤ 0.1 AND body_ratio ≤ 0.3 |
| **Domain** | {true, false} |
| **Units** | Boolean flag |
| **Edge Cases** | |
| — Zero range | FALSE |
| **Semantic** | Long lower wick, small body at top — shape only, not signal |
| **Note** | Shape classification only; trend context required for signal meaning (L3) |

---

### 3.11 Is Inverted Hammer Shape

| Property | Value |
|----------|-------|
| **Name** | `is_inverted_hammer_shape` |
| **Type** | bool |
| **Definition** | True if: upper_wick_ratio ≥ 0.6 AND lower_wick_ratio ≤ 0.1 AND body_ratio ≤ 0.3 |
| **Domain** | {true, false} |
| **Units** | Boolean flag |
| **Edge Cases** | |
| — Zero range | FALSE |
| **Semantic** | Long upper wick, small body at bottom — shape only, not signal |
| **Note** | Shape classification only; trend context required for signal meaning (L3) |

---

### 3.12 Directional Efficiency

| Property | Value |
|----------|-------|
| **Name** | `directional_efficiency` |
| **Type** | float |
| **Definition** | Signed body ratio preserving direction: (close − open) ÷ (high − low) |
| **Domain** | [−1, 1] |
| **Units** | Dimensionless ratio |
| **Edge Cases** | |
| — Zero range | UNDEFINED |
| — Flat bar | 0 |
| **Semantic** | +1 = pure bull (open=low, close=high); −1 = pure bear; 0 = no net move |

---

## 4. Explicit Exclusions

The following concepts are **explicitly excluded** from L1 and belong to later layers:

| Excluded | Belongs To | Reason |
|----------|------------|--------|
| Session statistics (daily high/low) | L2 | Requires aggregation across multiple bars |
| Rolling z-scores | L2 | Requires window of N previous bars |
| ATR-normalized values | L2 | Requires rolling average |
| Trend context (uptrend/downtrend) | L2/L3 | Requires sequence analysis |
| Support/resistance levels | L2/L3 | Requires historical reference |
| Signal labels (buy/sell/hold) | L3 | Requires interpretation + thresholds |
| Entry/exit timing | L3 | Requires decision logic |
| Win/loss outcomes | Option C | Requires forward-looking data |
| External indicators (news, vol) | Out of scope | Requires non-canonical sources |

---

## 5. Versioning & Promotion Rules

### 5.1 Version Scheme

Format: `OPTION_B_L1_FEATURES_v{MAJOR}.{MINOR}.md`

| Change Type | Version Impact | Example |
|-------------|----------------|---------|
| New feature added | MINOR bump | v0.1 → v0.2 |
| Feature renamed | MINOR bump | v0.2 → v0.3 |
| Threshold adjusted | MINOR bump | v0.3 → v0.4 |
| Feature removed | MAJOR bump | v0.4 → v1.0 |
| Domain changed | MAJOR bump | v1.0 → v2.0 |
| Formula changed | MAJOR bump | v1.1 → v2.0 |

### 5.2 Breaking Changes

A change is **breaking** if:

1. Existing feature produces different output for same input
2. Feature is removed
3. Feature type changes (float → bool)
4. Domain constraints change ([0,1] → [−1,1])

Breaking changes require:
- MAJOR version bump
- Migration notes in document
- Downstream impact assessment

### 5.3 Promotion Path

```
[DRAFT] → [ACTIVE] → [CANONICAL]
           ↓
       [DEPRECATED]
```

| Status | Meaning |
|--------|---------|
| DRAFT | Under development; may change freely |
| ACTIVE | Stable definitions; implementation may proceed |
| CANONICAL | Frozen; changes require governance approval |
| DEPRECATED | Superseded; implementation should migrate |

---

## 6. Implementation Handoff

When this document reaches `[STATUS: CANONICAL]`, implementers should:

1. Create `derived.ovc_l1_features_v0_1` view
2. Implement each feature exactly as defined
3. Handle edge cases as specified (UNDEFINED → NULL)
4. Add validation tests against known fixtures
5. Document any implementation deviations (must get approval)

**Current Status:** ACTIVE — Implementation may proceed; definitions may still evolve.

---

## Appendix A: Feature Summary Table

| Feature | Type | Domain | Depends On |
|---------|------|--------|------------|
| `body_ratio` | float | [0, 1] | body, rng |
| `upper_wick_ratio` | float | [0, 1] | h, o, c, rng |
| `lower_wick_ratio` | float | [0, 1] | l, o, c, rng |
| `wick_symmetry` | float | [−1, 1] | upper_wick, lower_wick, rng |
| `body_position` | float | [0, 1] | o, c, l, rng |
| `close_position` | float | [0, 1] | c, l, rng |
| `open_position` | float | [0, 1] | o, l, rng |
| `is_doji` | bool | {T, F} | body_ratio |
| `is_full_body` | bool | {T, F} | body_ratio |
| `is_hammer_shape` | bool | {T, F} | lower_wick_ratio, upper_wick_ratio, body_ratio |
| `is_inverted_hammer_shape` | bool | {T, F} | upper_wick_ratio, lower_wick_ratio, body_ratio |
| `directional_efficiency` | float | [−1, 1] | c, o, rng |

---

## Appendix B: Edge Case Matrix

| Condition | body_ratio | upper_wick_ratio | lower_wick_ratio | is_doji | directional_efficiency |
|-----------|------------|------------------|------------------|---------|------------------------|
| Zero range (h = l) | NULL | NULL | NULL | FALSE | NULL |
| Flat bar (o = c, rng > 0) | 0 | varies | varies | TRUE | 0 |
| Pure bull (o = l, c = h) | 1 | 0 | 0 | FALSE | +1 |
| Pure bear (o = h, c = l) | 1 | 0 | 0 | FALSE | −1 |
| Perfect doji (midpoint) | 0 | 0.5 | 0.5 | TRUE | 0 |

---

*Document created: 2026-01-20*
*Charter reference: [OPTION_B_CHARTER_v0.1.md](OPTION_B_CHARTER_v0.1.md)*
*Governance: [GOVERNANCE_RULES_v0.1.md](GOVERNANCE_RULES_v0.1.md)*
