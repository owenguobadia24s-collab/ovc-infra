# Option B – L3 Features v0.1

**[STATUS: CANONICAL]**

> **[CHANGE][CHANGED] Canonical Lock (2026-01-20)**
> Semantic meanings for all L3 features are now FROZEN.
> Any changes to label definitions or vocabularies require a MAJOR version bump.
> Validation evidence: [C3_v0_1_validation.md](../../reports/validation/C3_v0_1_validation.md)

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Created | 2026-01-20 |
| Promoted | 2026-01-20 |
| Author | OVC Infrastructure Team |
| Governs | L3 Semantic Feature Definitions |
| Parent Charter | OPTION_B_L3_CHARTER_v0.1.md |
| Governance | GOVERNANCE_RULES_v0.1.md |

---

## 1. Purpose of L3 Features

### 1.1 What Semantic States Represent

L3 features encode **semantic states** – higher-order descriptions that capture the structural meaning of market behavior. Unlike L1 (atomic facts) and L2 (temporal context), L3 features answer: **"What does this configuration mean?"**

Semantic states are:
- Derived from canonical L1 and L2 outputs only
- Descriptive labels, not predictive signals
- Stable interpretations of structural patterns

### 1.2 How L3 Differs from L2

| Layer | Focus | Example Output |
|-------|-------|----------------|
| L1 | Atomic facts | `dir = 1` (close > open) |
| L2 | Temporal context | `dir_streak = 3` (three consecutive bullish blocks) |
| L3 | Semantic meaning | `trend_bias = 'sustained'` (streak indicates directional persistence) |

L2 measures **motion** (what changed, how much, how long).
L3 assigns **meaning** (what the motion pattern represents structurally).

### 1.3 Why L3 Features Remain Descriptive

L3 features MUST NOT:
- Imply actions (buy, sell, hold)
- Encode outcomes (profit, loss)
- Suggest entries or exits
- Predict future behavior

L3 features describe **what is**, not **what to do about it**.

---

## 2. Input Contract

### 2.1 Explicitly Allowed Inputs

L3 features MAY read from:

| Source | Schema | Examples |
|--------|--------|----------|
| L1 Atomic Facts | `derived.ovc_l1_*` | `dir`, `rng`, `body`, `wick_top`, `wick_bot` |
| L2 Temporal Context | `derived.ovc_l2_*` | `dir_streak`, `rng_streak`, `prev_dir`, `dir_change` |

### 2.2 Explicit Prohibitions

L3 computations MUST NOT:
- Access `ovc.ovc_blocks_v01_1_min` (raw block table)
- Access Option C outputs (no circular dependency)
- Access external data sources
- Access non-CANONICAL artifacts

### 2.3 Lookback-Only Rule

All L3 features MUST be computed using only:
- The current row's L1/L2 values
- Historical rows (time < current)

Prohibited:
- `LEAD()` or forward window functions
- Joins on future timestamps
- Any lookahead bias

---

## 3. Semantic Axes

L3 features are organized along the following semantic axes. These axes define **what dimensions of meaning** L3 captures.

### 3.1 Directional Bias Axis

Describes the structural directional tendency based on recent behavior.

- NOT a prediction of future direction
- NOT an action recommendation
- IS a description of observed directional persistence or reversal

### 3.2 Volatility Regime Axis

Describes the current volatility context relative to recent history.

- Captures whether current ranges are compressed or expanded
- Enables downstream layers to interpret moves in context
- NOT a threshold trigger for action

### 3.3 Structural State Axis

Describes the relationship between body and range (candle structure).

- Captures whether price action is decisive or indecisive
- Distinguishes trending bars from doji-like formations
- NOT an entry/exit signal

### 3.4 Momentum Continuity Axis

Describes whether recent motion shows continuation or exhaustion patterns.

- Based on streak behavior and directional changes
- Captures structural momentum state
- NOT a prediction of continuation or reversal

---

## 4. Feature Definitions

### 4.1 `l3_trend_bias`

| Property | Value |
|----------|-------|
| **Name** | `l3_trend_bias` |
| **Type** | `enum` |
| **Required Inputs** | L2: `dir_streak`, `dir_change` |
| **Allowed Values** | `'sustained'`, `'nascent'`, `'neutral'`, `'fading'` |

**Semantic Meaning:**
- `'sustained'`: Directional streak ≥ 3, no recent reversal – persistent trend structure
- `'nascent'`: Directional streak = 1–2 after a reversal – new direction emerging
- `'neutral'`: No directional streak (alternating direction) – no bias present
- `'fading'`: Streak broken this block (`dir_change = true`) – prior bias ending

**Edge Cases:**
- If `dir_streak` is NULL, output `'neutral'`
- First block of session: output `'neutral'`

---

### 4.2 `l3_volatility_regime`

| Property | Value |
|----------|-------|
| **Name** | `l3_volatility_regime` |
| **Type** | `enum` |
| **Required Inputs** | L2: `rng_streak`, `rng_vs_prev` (or equivalent) |
| **Allowed Values** | `'compressed'`, `'normal'`, `'expanded'` |

**Semantic Meaning:**
- `'compressed'`: Consecutive narrowing ranges – volatility contracting
- `'normal'`: No sustained range pattern – baseline volatility
- `'expanded'`: Consecutive widening ranges – volatility expanding

**Edge Cases:**
- If `rng_streak` is NULL or 0, output `'normal'`
- Requires at least 2 blocks of history to assess

---

### 4.3 `l3_structure_type`

| Property | Value |
|----------|-------|
| **Name** | `l3_structure_type` |
| **Type** | `enum` |
| **Required Inputs** | L1: `body`, `rng` |
| **Allowed Values** | `'decisive'`, `'balanced'`, `'indecisive'` |

**Semantic Meaning:**
- `'decisive'`: Body is large relative to range – strong directional conviction
- `'balanced'`: Body is moderate relative to range – typical structure
- `'indecisive'`: Body is small relative to range – doji-like, no conviction

**Edge Cases:**
- If `rng = 0`, output `'indecisive'` (no price movement)
- Thresholds to be defined at implementation (ratios, not absolute values)

---

### 4.4 `l3_momentum_state`

| Property | Value |
|----------|-------|
| **Name** | `l3_momentum_state` |
| **Type** | `enum` |
| **Required Inputs** | L2: `dir_streak`, `dir_change`; L1: `body` (current vs prior) |
| **Allowed Values** | `'accelerating'`, `'steady'`, `'decelerating'`, `'reversing'` |

**Semantic Meaning:**
- `'accelerating'`: Streak continuing with increasing body size – momentum building
- `'steady'`: Streak continuing with stable body size – momentum maintained
- `'decelerating'`: Streak continuing with decreasing body size – momentum waning
- `'reversing'`: Direction changed this block – momentum reversed

**Edge Cases:**
- If `dir_change = true`, output `'reversing'` regardless of body
- If no prior block available, output `'steady'`

---

### 4.5 `l3_session_position`

| Property | Value |
|----------|-------|
| **Name** | `l3_session_position` |
| **Type** | `enum` |
| **Required Inputs** | Block letter (A–L from `block_id`) |
| **Allowed Values** | `'early'`, `'mid'`, `'late'` |

**Semantic Meaning:**
- `'early'`: Blocks A–D (NY 00:00–08:00) – Asian/early European session
- `'mid'`: Blocks E–H (NY 08:00–16:00) – London/NY overlap
- `'late'`: Blocks I–L (NY 16:00–24:00) – NY afternoon/Asian open

**Edge Cases:**
- Invalid block letter: output NULL
- This is a deterministic mapping, no ambiguity

---

### 4.6 `l3_wick_dominance`

| Property | Value |
|----------|-------|
| **Name** | `l3_wick_dominance` |
| **Type** | `enum` |
| **Required Inputs** | L1: `wick_top`, `wick_bot`, `rng` |
| **Allowed Values** | `'top_heavy'`, `'balanced'`, `'bottom_heavy'`, `'no_wicks'` |

**Semantic Meaning:**
- `'top_heavy'`: Upper wick dominates – rejection from highs
- `'bottom_heavy'`: Lower wick dominates – rejection from lows
- `'balanced'`: Wicks roughly equal – no dominant rejection
- `'no_wicks'`: Minimal wicks – body fills most of range

**Edge Cases:**
- If `rng = 0`, output `'no_wicks'`
- Thresholds for "dominates" to be defined at implementation

---

### 4.7 `l3_range_context`

| Property | Value |
|----------|-------|
| **Name** | `l3_range_context` |
| **Type** | `enum` |
| **Required Inputs** | L1: `rng`; L2: `rng_avg_5` (or lookback average) |
| **Allowed Values** | `'narrow'`, `'typical'`, `'wide'` |

**Semantic Meaning:**
- `'narrow'`: Current range significantly below recent average – quiet block
- `'typical'`: Current range near recent average – normal activity
- `'wide'`: Current range significantly above recent average – active block

**Edge Cases:**
- If no lookback data available, output `'typical'`
- Thresholds (e.g., ±1 std dev) to be defined at implementation

---

## 5. Explicit Exclusions

### 5.1 What L3 Will NOT Express

| Excluded Concept | Reason |
|------------------|--------|
| Entry/exit signals | Decisional – belongs to Option C |
| Overbought/oversold labels | Implies action thresholds |
| Probability of continuation | Forward-looking prediction |
| PnL or outcome metrics | Evaluation – belongs to Option C |
| Position sizing hints | Decisional – outside scope |
| Confidence scores | Implies predictive reliability |

### 5.2 Boundary with Option C

L3 outputs **describe** the current semantic state.
Option C **evaluates** what those states meant for outcomes.

L3: "The trend bias is 'sustained' and volatility is 'expanded'."
Option C: "When trend_bias='sustained' AND volatility='expanded', historical win rate was X%."

L3 does not know or care about win rates.

---

## 6. Output Schema (Declarative)

The L3 feature view will expose:

| Column | Type | Source |
|--------|------|--------|
| `block_id` | `text` | Passthrough from L1 |
| `ts` | `timestamptz` | Passthrough from L1 |
| `l3_trend_bias` | `text` | Computed |
| `l3_volatility_regime` | `text` | Computed |
| `l3_structure_type` | `text` | Computed |
| `l3_momentum_state` | `text` | Computed |
| `l3_session_position` | `text` | Computed |
| `l3_wick_dominance` | `text` | Computed |
| `l3_range_context` | `text` | Computed |

Target object: `derived.ovc_l3_semantic_states_v0_1`

---

## 7. Validation Requirements

Before promotion to CANONICAL:

| Check | Requirement |
|-------|-------------|
| Input compliance | All inputs from L1/L2 only |
| Lookback compliance | No future data access |
| Determinism | Same inputs → same outputs |
| Completeness | No NULL outputs for valid inputs |
| Semantic coherence | Label meanings are consistent |

---

## 8. Promotion Path

```
DRAFT → ACTIVE → CANONICAL
```

| Transition | Requirements |
|------------|--------------|
| DRAFT → ACTIVE | Charter compliance verified, design review complete |
| ACTIVE → CANONICAL | Validation evidence, 7-day stability, downstream compatibility |

---

## 9. Authorization

### 9.1 Design Status

This document defines L3 features **declaratively**.

- Feature semantics: CANONICAL (frozen)
- Threshold values: Defined in Implementation Contract §6.1
- SQL implementation: `derived.v_ovc_l3_features_v0_1`

### 9.2 Canonical Status

> **[CHANGE][CHANGED]** This specification is now CANONICAL.

- All semantic meanings are frozen
- Label vocabularies may not change without MAJOR bump
- Implementation validated: [C3_v0_1_validation.md](../../reports/validation/C3_v0_1_validation.md)
- Option C is now authorized to consume L3 features

---

**[END OF FEATURE SPECIFICATION]**
