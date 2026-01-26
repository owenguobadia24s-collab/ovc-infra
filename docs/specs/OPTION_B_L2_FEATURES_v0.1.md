# Option B – L2 Feature Definitions v0.1

[CHANGE][CHANGED] **[STATUS: CANONICAL]**

> **Canonical Lock (2026-01-20):**  
> Feature meanings are frozen. Any change requires MAJOR version bump + governance approval.  
> Validation evidence: [reports/validation/C2_v0_1_validation.md](../../../reports/validation/C2_v0_1_validation.md)

| Field              | Value                              |
|--------------------|------------------------------------|
| Version            | 0.1                                |
| Effective Date     | 2026-01-20                         |
| Governing Charter  | OPTION_B_L2_CHARTER_v0.1.md        |
| Upstream Dependency| L1 Features (CANONICAL)            |
| Governance         | GOVERNANCE_RULES_v0.1.md           |

---

## 1. Purpose of L2 Features

### 1.1 What L2 Represents

L2 features are **multi-bar / sequence-derived facts** that provide temporal context around individual blocks. They answer questions that require awareness of prior bars:

- *"How does this bar's range compare to recent bars?"*
- *"Where are we within the current session?"*
- *"How many consecutive bars have moved in this direction?"*

### 1.2 How L2 Extends L1

L2 **extends** L1 by computing derived context; it does not **reinterpret** L1.

| Principle                  | Meaning                                              |
|----------------------------|------------------------------------------------------|
| Additive only              | L2 adds columns; never modifies L1 values            |
| Semantic preservation      | L1 field meanings are unchanged                      |
| Compositional              | L2 features are functions of L1 outputs              |

Example of valid extension:
- L1 provides `rng` (single-bar range)
- L2 computes `rng_avg_3` (rolling average of `rng` over last 3 bars)

Example of invalid reinterpretation:
- L2 redefines `rng` as "normalized range" with different semantics

### 1.3 Why L2 Features Remain Non-Decisional

L2 features are **descriptive facts**, not **prescriptive signals**.

| L2 Provides                | L2 Does NOT Provide                    |
|----------------------------|----------------------------------------|
| Rolling average of range   | "Volatility is high" (threshold)       |
| Consecutive up-bar count   | "Trend confirmed" (interpretation)     |
| Session block index        | "Trade entry window" (decision)        |

Decision logic belongs to L3 (thresholds) or Option C (outcomes).

---

## 2. Input Contract

### 2.1 Explicit Sources

L2 features **MAY** consume:

| Source                        | Priority  | Usage                                    |
|-------------------------------|-----------|------------------------------------------|
| L1 feature outputs            | PRIMARY   | Preferred for all computations           |
| `ovc.ovc_blocks_v01_1_min`    | SECONDARY | Only when L1 does not expose needed field|

When canonical blocks are used directly, the feature definition must include explicit justification.

### 2.2 Lookback-Only Rule

**All L2 computations are strictly lookback.**

For any bar at time `t`, L2 features may use:
- The bar at `t` (current)
- Bars at `t-1, t-2, ..., t-N` (prior confirmed bars)

L2 features **MAY NOT** use:
- Bars at `t+1, t+2, ...` (future bars)
- Unconfirmed or provisional data

### 2.3 Maximum Window

| Constraint       | Value         | Rationale                              |
|------------------|---------------|----------------------------------------|
| Maximum lookback | 12 bars       | One full session (12 × 2H = 24H)       |
| Minimum lookback | 2 bars        | Single-bar scope belongs to L1         |

Windows exceeding 12 bars require charter amendment.

### 2.4 Lookahead Prohibition

**LOOKAHEAD IS PROHIBITED.**

Any computation that uses information not available at bar confirmation time violates this contract and must be rejected.

---

## 3. Window Semantics

### 3.1 Allowed Window Types

| Window Type            | Definition                                           |
|------------------------|------------------------------------------------------|
| Fixed N-bar            | Last N confirmed bars, including current             |
| Session-to-date (STD)  | All bars from session start through current bar      |

### 3.2 Window Boundary Determination

**Fixed N-bar windows:**
- Window includes the current bar and the preceding (N-1) bars
- Window size is constant regardless of session boundaries
- Windows may span session boundaries (cross-session context)

**Session-to-date windows:**
- Window starts at the first bar of the current session (block index 1)
- Window grows as session progresses (size = current block index)
- Window resets at session boundary

### 3.3 Missing Bar Handling

When a window contains fewer than N bars (e.g., start of data, gaps):

| Scenario                    | Handling                                      |
|-----------------------------|-----------------------------------------------|
| Insufficient history        | Output NULL (do not impute)                   |
| Gap in sequence             | Skip gap; use available bars with NULL flag   |
| Session start (STD window)  | Compute with available bars; minimum = 1      |

**Null propagation rule:** If any required input within the window is NULL, the L2 output is NULL unless the feature definition explicitly handles NULLs.

---

## 4. Feature Definitions

### 4.1 Feature Registry

| ID    | Feature Name              | Type   | Window        | Status |
|-------|---------------------------|--------|---------------|--------|
| L2-01 | `rng_avg_3`               | float  | Fixed 3-bar   | ACTIVE |
| L2-02 | `rng_avg_6`               | float  | Fixed 6-bar   | ACTIVE |
| L2-03 | `dir_streak`              | int    | Dynamic       | ACTIVE |
| L2-04 | `session_block_idx`       | int    | Session       | ACTIVE |
| L2-05 | `session_rng_cum`         | float  | Session STD   | ACTIVE |
| L2-06 | `session_dir_net`         | int    | Session STD   | ACTIVE |
| L2-07 | `rng_rank_6`              | float  | Fixed 6-bar   | ACTIVE |
| L2-08 | `body_rng_pct_avg_3`      | float  | Fixed 3-bar   | ACTIVE |

---

### 4.2 Feature Specifications

#### L2-01: `rng_avg_3`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `rng_avg_3`                                            |
| **Type**         | float                                                  |
| **Description**  | Rolling arithmetic mean of bar range over last 3 bars  |
| **Required Inputs** | L1: `rng` (float, pips)                             |
| **Window**       | Fixed 3-bar (current + 2 prior)                        |
| **Formula**      | `rng_avg_3 = (rng[t] + rng[t-1] + rng[t-2]) / 3`       |
| **Domain**       | [0, +∞)                                                |
| **Units**        | pips                                                   |
| **Edge Cases**   | If fewer than 3 bars available → NULL                  |
| **NULL Handling**| If any `rng` in window is NULL → NULL                  |

---

#### L2-02: `rng_avg_6`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `rng_avg_6`                                            |
| **Type**         | float                                                  |
| **Description**  | Rolling arithmetic mean of bar range over last 6 bars  |
| **Required Inputs** | L1: `rng` (float, pips)                             |
| **Window**       | Fixed 6-bar (current + 5 prior)                        |
| **Formula**      | `rng_avg_6 = sum(rng[t-5:t]) / 6`                      |
| **Domain**       | [0, +∞)                                                |
| **Units**        | pips                                                   |
| **Edge Cases**   | If fewer than 6 bars available → NULL                  |
| **NULL Handling**| If any `rng` in window is NULL → NULL                  |

---

#### L2-03: `dir_streak`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `dir_streak`                                           |
| **Type**         | int (signed)                                           |
| **Description**  | Count of consecutive bars with same direction, signed  |
| **Required Inputs** | L1: `dir` (int: -1, 0, +1)                          |
| **Window**       | Dynamic (lookback until direction changes, max 12)     |
| **Formula**      | Count consecutive bars where `dir[t-k] == dir[t]`, for k=0,1,2,... until `dir` changes or k=11. Sign matches `dir[t]`. |
| **Domain**       | [-12, +12]                                             |
| **Units**        | bars (signed)                                          |
| **Edge Cases**   | If `dir[t] == 0` (doji), streak = 0                    |
| **NULL Handling**| If `dir[t]` is NULL → NULL; streak breaks at NULL      |

**Interpretation:**
- `+3` means 3 consecutive bullish bars (including current)
- `-2` means 2 consecutive bearish bars (including current)
- `0` means current bar is neutral (doji)

---

#### L2-04: `session_block_idx`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `session_block_idx`                                    |
| **Type**         | int                                                    |
| **Description**  | Position of current bar within the session (1-indexed) |
| **Required Inputs** | Canonical: `block_id` (contains session letter A-L) |
| **Window**       | N/A (derived from block_id)                            |
| **Formula**      | Map block letter to index: A→1, B→2, ..., L→12         |
| **Domain**       | [1, 12]                                                |
| **Units**        | ordinal position                                       |
| **Edge Cases**   | Invalid block letter → NULL                            |
| **NULL Handling**| If `block_id` is NULL or malformed → NULL              |

**Justification for canonical block access:** Block letter is embedded in `block_id` and not exposed as a L1 feature. Direct extraction is required.

---

#### L2-05: `session_rng_cum`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `session_rng_cum`                                      |
| **Type**         | float                                                  |
| **Description**  | Cumulative sum of bar ranges within current session    |
| **Required Inputs** | L1: `rng` (float, pips); L2: `session_block_idx`    |
| **Window**       | Session-to-date (block 1 through current)              |
| **Formula**      | `session_rng_cum = sum(rng[session_start:t])`          |
| **Domain**       | [0, +∞)                                                |
| **Units**        | pips                                                   |
| **Edge Cases**   | At block 1: `session_rng_cum = rng[t]`                 |
| **NULL Handling**| If any `rng` in session is NULL → NULL                 |

---

#### L2-06: `session_dir_net`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `session_dir_net`                                      |
| **Type**         | int (signed)                                           |
| **Description**  | Net directional count within current session           |
| **Required Inputs** | L1: `dir` (int: -1, 0, +1); L2: `session_block_idx` |
| **Window**       | Session-to-date (block 1 through current)              |
| **Formula**      | `session_dir_net = sum(dir[session_start:t])`          |
| **Domain**       | [-12, +12]                                             |
| **Units**        | net bars                                               |
| **Edge Cases**   | At block 1: `session_dir_net = dir[t]`                 |
| **NULL Handling**| If any `dir` in session is NULL → NULL                 |

**Interpretation:**
- `+5` means 5 more bullish bars than bearish in session so far
- `-3` means 3 more bearish bars than bullish in session so far

---

#### L2-07: `rng_rank_6`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `rng_rank_6`                                           |
| **Type**         | float                                                  |
| **Description**  | Percentile rank of current bar's range within last 6 bars |
| **Required Inputs** | L1: `rng` (float, pips)                             |
| **Window**       | Fixed 6-bar (current + 5 prior)                        |
| **Formula**      | `rng_rank_6 = (count of bars where rng < rng[t]) / 5`  |
| **Domain**       | [0.0, 1.0]                                             |
| **Units**        | ratio (dimensionless)                                  |
| **Edge Cases**   | If fewer than 6 bars available → NULL; ties use strict < |
| **NULL Handling**| If any `rng` in window is NULL → NULL                  |

**Interpretation:**
- `1.0` means current bar has largest range in window
- `0.0` means current bar has smallest range in window
- `0.6` means current bar's range exceeds 60% of prior 5 bars

---

#### L2-08: `body_rng_pct_avg_3`

| Property         | Value                                                  |
|------------------|--------------------------------------------------------|
| **Name**         | `body_rng_pct_avg_3`                                   |
| **Type**         | float                                                  |
| **Description**  | Rolling mean of body-to-range percentage over last 3 bars |
| **Required Inputs** | L1: `body_rng_pct` (float, percentage)              |
| **Window**       | Fixed 3-bar (current + 2 prior)                        |
| **Formula**      | `body_rng_pct_avg_3 = sum(body_rng_pct[t-2:t]) / 3`    |
| **Domain**       | [0.0, 100.0]                                           |
| **Units**        | percentage                                             |
| **Edge Cases**   | If fewer than 3 bars available → NULL                  |
| **NULL Handling**| If any `body_rng_pct` in window is NULL → NULL         |

---

## 5. Explicit Exclusions

### 5.1 Intentionally NOT Part of L2

The following are explicitly excluded from L2 scope:

| Exclusion                          | Rationale                                  |
|------------------------------------|--------------------------------------------|
| Volatility regime labels           | Requires threshold; deferred to L3         |
| Trend classification               | Semantic interpretation; deferred to L3    |
| Range expansion/contraction flags  | Requires threshold; deferred to L3         |
| Session quality scores             | Evaluative; deferred to Option C           |
| Forward returns                    | Outcome; prohibited in Option B            |
| Entry/exit signals                 | Decision logic; prohibited in Option B     |
| Cross-symbol correlations          | Multi-symbol scope; future consideration   |

### 5.2 Deferred to L3

The following will be defined in L3, building on L2:

| L3 Responsibility                  | L2 Prerequisite                            |
|------------------------------------|--------------------------------------------|
| `rng_is_elevated` (bool)           | `rng_avg_6`, `rng_rank_6`                  |
| `session_is_directional` (bool)    | `session_dir_net`                          |
| `streak_is_extended` (bool)        | `dir_streak`                               |

### 5.3 Deferred to Option C

| Option C Responsibility            | Reason for Exclusion                       |
|------------------------------------|--------------------------------------------|
| Return after N bars                | Outcome computation                        |
| Win/loss labeling                  | Outcome computation                        |
| Signal effectiveness metrics       | Evaluative                                 |

---

## 6. Versioning & Promotion Rules

### 6.1 Version Change Classification

| Change Type                        | Version Impact | Example                            |
|------------------------------------|----------------|------------------------------------|
| Add new feature                    | MINOR          | Add `rng_avg_12`                   |
| Modify feature formula             | MAJOR          | Change `rng_rank_6` tie handling   |
| Change feature type                | MAJOR          | `dir_streak` int → float           |
| Remove feature                     | MAJOR          | Remove `body_rng_pct_avg_3`        |
| Fix documentation typo             | PATCH          | Clarify edge case wording          |
| Change NULL handling               | MAJOR          | Skip NULLs instead of propagate    |

### 6.2 Promotion Path

```
DRAFT → ACTIVE → CANONICAL
```

| Stage      | Criteria                                              |
|------------|-------------------------------------------------------|
| DRAFT      | Feature defined; not yet validated                    |
| ACTIVE     | Feature validated against test data; may be consumed  |
| CANONICAL  | Feature frozen; 30-day stability demonstrated         |

### 6.3 Current Feature Status

All features defined in this document are **ACTIVE**.

Promotion to CANONICAL requires:
1. Implementation matching this specification
2. Validation suite passing
3. 30-day production stability
4. Governance sign-off

---

## 7. Document Control

| Action         | Date       | Author     | Notes                              |
|----------------|------------|------------|------------------------------------|
| Created        | 2026-01-20 | —          | Initial 8 features defined         |

---

## Appendix A: Feature Dependency Graph

```
Canonical Blocks
      │
      ▼
┌─────────────┐
│     L1      │
│  (single-   │
│   bar)      │
├─────────────┤
│ rng         │───────┬──────────┬──────────┐
│ dir         │───┐   │          │          │
│ body_rng_pct│─┐ │   │          │          │
│ block_id    │ │ │   │          │          │
└─────────────┘ │ │   │          │          │
                │ │   │          │          │
                ▼ ▼   ▼          ▼          ▼
┌─────────────────────────────────────────────┐
│                    L2                        │
├──────────────────┬──────────────────────────┤
│ body_rng_pct_avg_3│ rng_avg_3  rng_avg_6    │
│                   │ rng_rank_6              │
├───────────────────┼─────────────────────────┤
│ dir_streak        │ session_dir_net         │
├───────────────────┼─────────────────────────┤
│ session_block_idx │ session_rng_cum         │
└───────────────────┴─────────────────────────┘
```

---

**END OF DOCUMENT**
