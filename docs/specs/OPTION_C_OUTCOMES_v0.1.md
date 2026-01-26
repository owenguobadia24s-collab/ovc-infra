# Option C Outcomes v0.1

**[STATUS: CANONICAL]** [CHANGE][CHANGED]

> **CANONICAL LOCK**: Outcome meanings are FROZEN. Any breaking change requires MAJOR version bump + governance approval. See [C_v0_1_promotion.md](../../reports/validation/C_v0_1_promotion.md) for promotion evidence.

| Field          | Value                          |
|----------------|--------------------------------|
| Version        | 0.1                            |
| Created        | 2026-01-20                     |
| Promoted       | 2026-01-20                     |
| Author         | OVC Governance                 |
| Depends On     | OPTION_C_CHARTER_v0.1.md       |
| Governed By    | GOVERNANCE_RULES_v0.1.md       |
| Validation     | [C_v0_1_validation.md](../../docs/validation/C_v0_1_validation.md) |
| Promotion      | [C_v0_1_promotion.md](../../reports/validation/C_v0_1_promotion.md) |

---

## 1. Purpose of Outcomes

### 1.1 What an Outcome Represents in OVC

An **outcome** is a **retrospective measurement** of what happened after a given block completed.

Outcomes describe **consequences**—they answer the question:

> *"Given the state described by Option B at block T, what subsequently occurred?"*

Outcomes are **facts about the future relative to a past moment**, computed only after that future has become history.

### 1.2 Difference Between Outcome, Signal, and Decision

| Concept      | Definition                                          | Layer           |
|--------------|-----------------------------------------------------|-----------------|
| **Signal**   | A descriptive condition or pattern at time T        | Option B (L2/L3)|
| **Outcome**  | What happened after time T                          | Option C        |
| **Decision** | An action taken based on signals and/or outcomes    | NOT IN SCOPE    |

**Signals** describe state. **Outcomes** describe consequence. **Decisions** prescribe action.

OVC Option C produces outcomes. It does not produce decisions.

### 1.3 Why Outcomes Are Descriptive of Consequence, Not Prescriptions

Outcomes are **descriptive**, not **prescriptive**:

- Outcomes say: *"After this block, price moved X%"*
- Outcomes do NOT say: *"You should have bought here"*

This distinction is critical because:

1. The same outcome may be favorable or unfavorable depending on context
2. Outcomes carry no implicit position or direction
3. Outcomes are independent of any trading strategy

Outcomes are **neutral measurements**. They become meaningful only when combined with strategy assumptions outside OVC scope.

---

## 2. Input Contract

### 2.1 Explicitly Allowed Inputs

Option C outcomes MAY be computed using:

| Source | Layer | Description                              |
|--------|-------|------------------------------------------|
| L1     | B     | Canonical block-level facts              |
| L2     | B     | Canonical derived features               |
| L3     | B     | Canonical semantic labels and regime     |

Outcomes reference **Option B outputs** to establish the "anchor point" from which forward measurement begins.

### 2.2 Explicit Prohibition on Feedback

Option C outcomes **SHALL NOT**:

- Modify any L1, L2, or L3 output
- Write to any Option B schema
- Influence Option B computation in any way
- Be consumed by Option B layers

The relationship is strictly **one-directional**:

```
Option B (L1 → L2 → L3) → Option C Outcomes
                              ↓
                         (terminal, no feedback)
```

---

## 3. Outcome Definitions

This section defines the **canonical outcome set** for Option C v0.1.

All definitions are **declarative**. Implementation is deferred and governed separately.

---

### 3.1 Forward Return (N-Bar)

| Property          | Value                                                      |
|-------------------|------------------------------------------------------------|
| **Name**          | `fwd_ret_N`                                                |
| **Type**          | `float`                                                    |
| **Reference Frame** | N bars forward from anchor block close                   |
| **Unit**          | Fractional return (e.g., 0.0015 = 0.15%)                   |

**What It Measures**:
The percentage price change from the anchor block's close to the close of the block N periods later.

```
fwd_ret_N = (close[T+N] - close[T]) / close[T]
```

**What It Does NOT Mean**:
- Does NOT imply a position was taken
- Does NOT account for spread, slippage, or costs
- Does NOT indicate whether the move was "good" or "bad"

**Edge Cases**:
| Condition                  | Behavior                                      |
|----------------------------|-----------------------------------------------|
| N extends beyond available data | Outcome is NULL                          |
| Gap between T and T+N      | Use actual close prices; do not interpolate   |
| Session boundary crossed   | Continue measurement across sessions          |

**Canonical Values of N**:
- `fwd_ret_1` (1 block = 2 hours)
- `fwd_ret_3` (3 blocks = 6 hours)
- `fwd_ret_6` (6 blocks = 12 hours)

---

### 3.2 Maximum Favorable Excursion (MFE)

| Property          | Value                                                      |
|-------------------|------------------------------------------------------------|
| **Name**          | `mfe_N`                                                    |
| **Type**          | `float`                                                    |
| **Reference Frame** | Maximum over N bars forward from anchor block close      |
| **Unit**          | Fractional return (e.g., 0.0025 = 0.25%)                   |

**What It Measures**:
The maximum favorable price movement observed within N bars after the anchor block, measured from anchor close.

For a **bullish** reference (default, unsigned):
```
mfe_N = max(high[T+1], high[T+2], ..., high[T+N]) - close[T]) / close[T]
```

**What It Does NOT Mean**:
- Does NOT imply the favorable move was captured
- Does NOT account for entry timing or execution
- Does NOT indicate directional bias of a hypothetical trade

**Edge Cases**:
| Condition                  | Behavior                                      |
|----------------------------|-----------------------------------------------|
| N extends beyond available data | Outcome is NULL                          |
| All bars within N have lower highs than close[T] | MFE = 0              |

**Note**: MFE is computed as **unsigned magnitude** (always ≥ 0). Directional interpretation requires external context.

**Canonical Values of N**:
- `mfe_3`
- `mfe_6`

---

### 3.3 Maximum Adverse Excursion (MAE)

| Property          | Value                                                      |
|-------------------|------------------------------------------------------------|
| **Name**          | `mae_N`                                                    |
| **Type**          | `float`                                                    |
| **Reference Frame** | Maximum over N bars forward from anchor block close      |
| **Unit**          | Fractional return (e.g., 0.0018 = 0.18%)                   |

**What It Measures**:
The maximum adverse price movement observed within N bars after the anchor block, measured from anchor close.

For a **bullish** reference (default, unsigned):
```
mae_N = (close[T] - min(low[T+1], low[T+2], ..., low[T+N])) / close[T]
```

**What It Does NOT Mean**:
- Does NOT imply a stop-loss was hit
- Does NOT account for position sizing or risk management
- Does NOT indicate whether the adverse move was terminal

**Edge Cases**:
| Condition                  | Behavior                                      |
|----------------------------|-----------------------------------------------|
| N extends beyond available data | Outcome is NULL                          |
| All bars within N have higher lows than close[T] | MAE = 0              |

**Note**: MAE is computed as **unsigned magnitude** (always ≥ 0). Directional interpretation requires external context.

**Canonical Values of N**:
- `mae_3`
- `mae_6`

---

### 3.4 Time to Threshold (TTT)

| Property          | Value                                                      |
|-------------------|------------------------------------------------------------|
| **Name**          | `ttt_threshold_dir`                                        |
| **Type**          | `int` (bar count) or `NULL`                                |
| **Reference Frame** | Bars until threshold reached, within maximum window      |
| **Unit**          | Number of bars                                             |

**What It Measures**:
The number of bars after the anchor block until price first reaches a specified threshold level, searching within a maximum window.

**What It Does NOT Mean**:
- Does NOT imply a target was "hit" in a trading sense
- Does NOT account for whether price stayed beyond threshold
- Does NOT indicate trade success or failure

**Edge Cases**:
| Condition                          | Behavior                                  |
|------------------------------------|-------------------------------------------|
| Threshold never reached in window  | Outcome is NULL                           |
| Threshold reached on first bar     | TTT = 1                                   |
| Gap jumps past threshold           | TTT = bar where gap occurred              |

**Canonical Configurations**:
- Threshold definitions are **deferred** to implementation specification
- This outcome requires parameterization (threshold level, direction, window)

**Note**: TTT is included as a **placeholder** for future parameterized outcome definitions. Specific threshold values require separate governance approval.

---

### 3.5 Realized Volatility (Forward Window)

| Property          | Value                                                      |
|-------------------|------------------------------------------------------------|
| **Name**          | `rvol_N`                                                   |
| **Type**          | `float`                                                    |
| **Reference Frame** | N bars forward from anchor block close                   |
| **Unit**          | Standard deviation of returns (annualization deferred)     |

**What It Measures**:
The realized volatility of close-to-close returns over the N bars following the anchor block.

```
rvol_N = stddev(ret[T+1], ret[T+2], ..., ret[T+N])
where ret[i] = (close[i] - close[i-1]) / close[i-1]
```

**What It Does NOT Mean**:
- Does NOT predict future volatility
- Does NOT indicate regime (that is L3's domain)
- Does NOT account for intrabar volatility (only close-to-close)

**Edge Cases**:
| Condition                  | Behavior                                      |
|----------------------------|-----------------------------------------------|
| N extends beyond available data | Outcome is NULL                          |
| Fewer than 2 bars available     | Outcome is NULL (stddev undefined)       |

**Canonical Values of N**:
- `rvol_6`

---

## 4. Lookahead Semantics

### 4.1 Allowed Forward Windows

Option C outcomes are permitted to look forward from the anchor block. The following windows are authorized:

| Window | Bars | Duration (2H blocks) |
|--------|------|----------------------|
| 1      | 1    | 2 hours              |
| 3      | 3    | 6 hours              |
| 6      | 6    | 12 hours             |

Additional windows require governance approval and documentation.

### 4.2 Alignment with Bar Timestamps

Outcomes align to **bar close timestamps**:

- Anchor block T has close time `close_ts[T]`
- Forward block T+N has close time `close_ts[T+N]`
- Outcome computation uses **confirmed closes only**

No intra-bar lookahead is permitted. All forward references are to completed bars.

### 4.3 Lookahead is Allowed ONLY in Option C

**CRITICAL**: Lookahead (using future data relative to anchor) is **prohibited in Option B** and **permitted only in Option C**.

| Layer    | Lookahead Allowed? |
|----------|--------------------|
| Option A | NO                 |
| Option B | NO                 |
| Option C | YES (within defined windows) |

This is the fundamental distinction that makes Option C the evaluation layer.

---

## 5. Explicit Exclusions

### 5.1 What Option C Outcomes Will NOT Encode

The following are **explicitly out of scope** for Option C outcomes:

| Exclusion                      | Rationale                                         |
|--------------------------------|---------------------------------------------------|
| Trade entry/exit logic         | Outcomes describe consequence, not action         |
| Position direction assumption  | Outcomes are unsigned unless explicitly noted     |
| Transaction costs              | Outcomes are gross measurements                   |
| Slippage estimates             | Execution is out of scope                         |
| Win/loss classification        | Requires strategy context not present in OVC      |
| Sharpe ratio or risk metrics   | These are portfolio-level, not block-level        |
| Optimization targets           | Outcomes are not objective functions              |

### 5.2 No Trade Execution Assumptions

Outcomes assume **no trade was taken**. They measure what price did, not what a trader would have captured.

### 5.3 No Strategy Logic

Outcomes do not encode:

- Entry conditions
- Exit conditions
- Stop-loss or take-profit levels
- Position sizing
- Risk limits

### 5.4 No Optimization Criteria

Outcomes are **not objective functions**. They are measurements.

Using outcomes for optimization requires:

- External strategy definition
- Governance approval
- Separate documentation outside Option C

---

## 6. Versioning & Promotion Rules

### 6.1 Change Classification

| Change Type | Description                                    | Version Impact |
|-------------|------------------------------------------------|----------------|
| **MINOR**   | Clarification of edge case behavior            | Patch (0.1.x)  |
| **MINOR**   | Addition of new canonical N value              | Minor (0.x.0)  |
| **MAJOR**   | Change to outcome formula or semantics         | Major (x.0.0)  |
| **MAJOR**   | Removal of existing outcome                    | Major (x.0.0)  |
| **MAJOR**   | Change to reference frame definition           | Major (x.0.0)  |

### 6.2 Promotion Path

```
DRAFT → ACTIVE → CANONICAL
```

| Stage     | Meaning                                        | Requirements                          |
|-----------|------------------------------------------------|---------------------------------------|
| DRAFT     | Outcome under design review                    | Documentation only                    |
| ACTIVE    | Outcome approved for implementation            | Governance sign-off                   |
| CANONICAL | Outcome frozen and authoritative               | Validation evidence, audit complete   |

### 6.3 Current Outcome Status

| Outcome      | Status  | Notes                                      |
|--------------|---------|--------------------------------------------|
| `fwd_ret_N`  | ACTIVE  | Ready for implementation                   |
| `mfe_N`      | ACTIVE  | Ready for implementation                   |
| `mae_N`      | ACTIVE  | Ready for implementation                   |
| `ttt_*`      | DRAFT   | Requires threshold parameterization        |
| `rvol_N`     | ACTIVE  | Ready for implementation                   |

---

## 7. Summary of Canonical Outcome Set v0.1

| Outcome       | Type    | Windows   | Status  |
|---------------|---------|-----------|---------|
| `fwd_ret_N`   | float   | 1, 3, 6   | ACTIVE  |
| `mfe_N`       | float   | 3, 6      | ACTIVE  |
| `mae_N`       | float   | 3, 6      | ACTIVE  |
| `ttt_*`       | int     | TBD       | DRAFT   |
| `rvol_N`      | float   | 6         | ACTIVE  |

**Total ACTIVE outcomes**: 8 (3 fwd_ret + 2 mfe + 2 mae + 1 rvol)

---

## Appendix A: Document Control

| Version | Date       | Change Description              |
|---------|------------|---------------------------------|
| 0.1     | 2026-01-20 | Initial outcome definitions     |

---

**END OF DOCUMENT**
