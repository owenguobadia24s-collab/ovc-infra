# Option B – L3 Charter v0.1

**[STATUS: ACTIVE]**

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Created | 2026-01-20 |
| Author | OVC Infrastructure Team |
| Governs | Option B – Semantic Aggregation Layer (L3) |
| Parent Charter | OPTION_B_CHARTER_v0.1.md |
| Governance | GOVERNANCE_RULES_v0.1.md |

---

## 1. Purpose of L3

### 1.1 What L3 Represents

L3 is the **Semantic Aggregation Layer** within Option B. It synthesizes outputs from L1 (Atomic Facts) and L2 (Temporal Context) into higher-order structural descriptions that capture **meaning** rather than motion.

L3 answers questions like:
- What structural pattern does this sequence represent?
- What regime or context classification applies?
- What semantic state label describes this configuration?

### 1.2 How L3 Differs from L2

| Aspect | L2 (Temporal Context) | L3 (Semantic Aggregation) |
|--------|----------------------|---------------------------|
| Focus | Motion and change | Meaning and classification |
| Inputs | L1 atomic facts | L1 + L2 outputs |
| Outputs | Directional context, momentum, sequences | Pattern labels, regime states, structural summaries |
| Granularity | Per-block temporal relationships | Multi-block semantic synthesis |
| Question answered | "What changed?" | "What does it mean?" |

### 1.3 Why L3 Does NOT Produce Decisions or Outcomes

L3 exists to **describe** semantic structure, not to **prescribe** action.

- L3 outputs are **labels**, not **signals**
- L3 provides **context**, not **conclusions**
- L3 enables downstream interpretation but does not perform it

The boundary between description and decision belongs to Option C (Evaluation/Outcomes). L3 must remain on the descriptive side of that boundary.

---

## 2. Allowed Inputs

### 2.1 Explicitly Allowed Sources

L3 computations MAY read from:

| Source | Schema | Status |
|--------|--------|--------|
| L1 Atomic Facts | `derived.ovc_l1_*` | CANONICAL |
| L2 Temporal Context | `derived.ovc_l2_*` | CANONICAL |

### 2.2 Explicit Prohibitions on Inputs

L3 computations MUST NOT:

- Access `ovc.ovc_blocks_v01_1_min` directly (raw block table)
- Access any table outside the `derived` schema
- Access Option C outputs (no circular dependencies)
- Access external APIs or real-time feeds
- Access any non-CANONICAL intermediate artifacts

### 2.3 Lookback-Only Rule

All L3 computations MUST be **lookback-only**:

- A row at time T may reference only data from times ≤ T
- No forward-looking window functions
- No future joins or lookahead bias
- Violation of this rule invalidates the entire L3 output

---

## 3. Allowed Computations

L3 MAY perform the following computation types:

### 3.1 Pattern Aggregation

- Sequence-based pattern recognition over L2 outputs
- Multi-block structural summarization
- Compositional pattern building from atomic elements

### 3.2 Regime / Context Classification

- Market regime labeling (e.g., trending, ranging, volatile)
- Session context classification
- Structural state identification

### 3.3 Structural State Labeling (Non-Decisional)

- Labeling configurations with semantic names
- Categorizing structural arrangements
- Assigning descriptive classifications

**Constraint**: All labels must be **descriptive**, not **prescriptive**.

### 3.4 Multi-Feature Synthesis

- Combining multiple L1/L2 features into composite descriptors
- Cross-feature relationship encoding
- Dimensional reduction for semantic summarization

---

## 4. Explicit Prohibitions

L3 MUST NOT:

### 4.1 Outcomes or PnL

- No profit/loss calculations
- No outcome measurements
- No performance metrics
- No success/failure labels

### 4.2 Thresholds That Imply Actions

- No "overbought/oversold" labels
- No "entry zone" or "exit zone" designations
- No threshold-crossing signals that suggest action

### 4.3 Buy/Sell/Hold Semantics

- No directional recommendations
- No position sizing suggestions
- No trade signals of any kind
- No labels that encode action intent

### 4.4 Forward-Looking Logic

- No predictions
- No forecasts
- No probability estimates of future states
- No lookahead in any computation

### 4.5 Writes Outside `derived.*`

- All L3 outputs MUST write to `derived.ovc_l3_*` tables/views only
- No writes to `ovc.*` schema (LOCKED)
- No writes to `ovc_qa.*` schema (Option D only)
- No external writes (files, APIs, etc.)

---

## 5. Guarantees to Downstream Layers

L3 provides the following guarantees to Option C and other consumers:

### 5.1 Semantic Stability Guarantees

- Column names will not change without MAJOR version bump
- Label vocabularies will not change without MAJOR version bump
- Semantic meanings will not drift within a version

### 5.2 Versioned Meaning

| Change Type | Version Impact | Requirement |
|-------------|----------------|-------------|
| New column added | MINOR bump | Backward compatible |
| Column removed | MAJOR bump | Migration path required |
| Label vocabulary changed | MAJOR bump | Mapping documentation required |
| Computation logic changed | MINOR bump (if output stable) | Validation evidence required |

### 5.3 Deterministic Replay Guarantees

- Given identical L1 + L2 inputs, L3 MUST produce identical outputs
- No randomness in computations
- No external state dependencies
- Full reproducibility from canonical inputs

---

## 6. Relationship to L1 and L2

### 6.1 L1 and L2 Are Immutable Inputs

- L3 receives L1 and L2 as read-only inputs
- L3 MUST NOT modify L1 or L2 tables
- L3 MUST NOT request changes to L1 or L2 definitions

### 6.2 L3 May Not Reinterpret L1/L2 Meanings

- If L1 defines `dir` as close vs open direction, L3 must use that meaning
- L3 may not create alternate interpretations of upstream fields
- Semantic disagreements must be resolved at the source layer

### 6.3 L3 Failures Must Not Invalidate L1 or L2

- L3 computation failures are isolated to L3
- L1 and L2 remain valid regardless of L3 state
- Downstream layers may fall back to L2 if L3 is unavailable

---

## 7. Governance & Promotion Path

### 7.1 Status Progression

```
DRAFT → ACTIVE → CANONICAL
```

| Status | Meaning | Requirements |
|--------|---------|--------------|
| DRAFT | Under design, not for use | None |
| ACTIVE | Authorized for implementation | Charter approval |
| CANONICAL | Frozen, immutable | Validation evidence, stability period |

### 7.2 Audit Triggers

L3 outputs require re-validation when:

- L1 or L2 definitions change (MAJOR bump upstream)
- L3 computation logic is modified
- Downstream consumers report semantic inconsistencies
- Periodic audit schedule (quarterly minimum)

### 7.3 Validation Evidence Requirements

Before CANONICAL promotion, L3 must demonstrate:

| Evidence | Description |
|----------|-------------|
| Replay determinism | Same inputs → same outputs across 3+ runs |
| Lookback compliance | No future data leakage verified |
| Schema compliance | All outputs in `derived.ovc_l3_*` |
| Prohibition compliance | No outcomes, signals, or actions encoded |
| Downstream compatibility | Option C can consume without errors |

---

## 8. Authorization

### 8.1 Design Authorization

This charter **authorizes** the design phase of L3:

- Defining semantic features (in separate design documents)
- Specifying column schemas and label vocabularies
- Documenting computation logic in prose

### 8.2 Implementation Requires Separate Approval

This charter does **NOT** authorize:

- Writing SQL or Python code
- Creating database objects
- Executing computations against production data

Implementation approval requires:

1. Completed feature design documents
2. Validation plan
3. Explicit implementation approval on each feature

---

## 9. Summary

L3 is the Semantic Aggregation Layer that transforms L1 (atomic facts) and L2 (temporal context) into higher-order structural descriptions. It provides **meaning without action**, enabling downstream layers to interpret market structure without L3 itself making decisions.

### L3 Boundaries at a Glance

| Allowed | Prohibited |
|---------|------------|
| Read L1, L2 | Read raw blocks |
| Pattern aggregation | Outcome calculation |
| Regime classification | Action thresholds |
| Structural labeling | Buy/sell/hold signals |
| Write to `derived.ovc_l3_*` | Write elsewhere |
| Lookback computations | Forward-looking logic |

---

**[END OF CHARTER]**
