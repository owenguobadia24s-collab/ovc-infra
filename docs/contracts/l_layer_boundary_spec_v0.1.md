# OVC C-Layer Boundary Spec v0.1

> **Status**: DRAFT — requires approval before implementation
> **Purpose**: LOCK tier definitions to enable validation, prevent tier drift
> **Scope**: L1, L2, L3 boundaries; B-layer inputs; Decision outputs
> **Authority**: This spec is normative for all derived metric implementations

---

## Section A — Tier Purpose

### B-Layer (Canonical Facts)

**Purpose**: Store source-agnostic raw facts that form the immutable foundation for all derived computation.

**Semantic Boundary**:
- OHLC price data at 2H block granularity
- Schedule/identity metadata (block_id, sym, date_ny, block2h)
- Ingest metadata (source, build_id, bar_close_ms)

**NOT B-Layer**: Any computed, derived, or synthesized value.

---

### L1 — Single-Bar Primitives

**Purpose**: Compute deterministic, stateless transformations of a single block's OHLC values.

**Semantic Boundary**:
- Formulas that operate on {o, h, l, c} of ONE block only
- No lookback, no history, no rolling windows
- Output is fully determined by the four OHLC values of the current block

**Guarantees**:
- Deterministic: Same OHLC → same output, always
- Source-agnostic: Formula does not depend on data provenance
- Replayable: No external state required

---

### L2 — Multi-Bar Structure & Context

**Purpose**: Compute features that require cross-bar relationships, rolling windows, or session context.

**Semantic Boundary**:
- Features requiring lookback to prior blocks (e.g., `gap = o - prev_c`)
- Rolling aggregations (e.g., `roll_avg_range_12`)
- Session-scoped accumulators (e.g., `sess_high`)
- Structural detections (e.g., `hh_12`, `took_prev_high`)
- Numeric outputs from multi-bar logic (e.g., `rd_hi`, `rd_lo`, `rm`, `sd`)

**Guarantees**:
- Deterministic given ordered block sequence
- Window specification must be explicit and versioned
- Rolling features require minimum sample count enforcement

---

### L3 — Categorical Tags & Regime Interpretation

**Purpose**: Synthesize categorical interpretations from L2 numeric evidence.

**Semantic Boundary**:
- Categorical/enum outputs derived from L2 numeric features + thresholds
- Regime state machines (e.g., `rd_state`: RANGE/SOFT_RANGE/NO_RANGE)
- Directional bias tags (e.g., `rd_brkdir`: UP/DN/0)
- Composite condition tags (e.g., `state_tag`, `value_tag`, `tt`)
- Diagnostic strings combining multiple signals (e.g., `rd_why`)

**Guarantees**:
- Deterministic given L2 inputs + versioned threshold parameters
- Thresholds must be documented and frozen per version
- Categorical outputs must have defined enum domains

---

### Decision Layer (L3)

**Purpose**: Produce actionable trading signals by synthesizing L2/L3 evidence into bias/play/prediction objects.

**Semantic Boundary**:
- Bias objects (e.g., `L3_BIAS`, `L3_BIAS_WHY`)
- Play objects (e.g., `L3_PLAY`, `L3_PLAY_WHY`)
- Permission gates (e.g., `L3_PERMIT`, `L3_PERMIT_WHY`)
- Prediction objects (e.g., `L3_PRED`, `L3_PRED_WHY`, `L3_PRED_CONF`)

**NOT Decision Layer**: Raw numeric features or intermediate categorical tags.

---

## Section B — Allowed Inputs

| Tier | Allowed Inputs | Notes |
|------|----------------|-------|
| **B** | Raw external data (TradingView export, OANDA API, manual entry) | Must be parseable to OHLC + identity |
| **L1** | B-layer OHLC of current block only: `o`, `h`, `l`, `c` | No prior blocks, no external state |
| **L2** | B-layer OHLC sequence + L1 outputs | Explicit window spec required |
| **L3** | L2 numeric outputs + versioned threshold parameters | No direct OHLC access |
| **Decision** | L2/L3 outputs + versioned decision rules | Synthesis only, no raw OHLC |

---

## Section C — Forbidden Inputs

| Tier | Forbidden | Rationale |
|------|-----------|-----------|
| **B** | Any derived value; any computed metric | B = raw facts only |
| **L1** | Prior block data; session context; rolling stats | L1 = single-bar, no history |
| **L2** | L3 categorical tags; Decision outputs | No reverse dependencies |
| **L3** | Decision outputs; L3 tags from other regime domains | Categorical synthesis is terminal for that domain |
| **Decision** | B-layer OHLC directly; L1 outputs directly | Must flow through L2/L3 evidence |

**Critical Rule**: No tier may depend on outputs from a higher tier. Dependencies flow strictly upward: B → L1 → L2 → L3 → Decision.

---

## Section D — Time Horizon Rules

| Tier | Time Horizon | Window Spec |
|------|--------------|-------------|
| **B** | Single block (2H) | N/A — raw capture timestamp |
| **L1** | Single block (2H) | N/A — stateless |
| **L2** | 1–N blocks | Must specify: `N=<count>` or `session=<scope>` |
| **L3** | Inherits from L2 inputs | Must document L2 window dependencies |
| **Decision** | Current block + historical context | May reference L2/L3 from prior blocks |

**Window Specification Format**:
```
window_spec = "<feature>:<type>:<value>"
Examples:
  "roll_avg_range:N:12"
  "sess_high:session:date_ny"
  "rm:N:3"
  "rd_hi:N:rd_len"  (parameterized)
```

---

## Section E — Determinism & Replay Requirements

### E.1 — Determinism Guarantees

| Tier | Determinism Constraint |
|------|------------------------|
| **B** | N/A (raw input) |
| **L1** | `f(o, h, l, c) → output` — no external state |
| **L2** | `f(ohlc_sequence, window_spec) → output` — ordered input |
| **L3** | `f(l2_outputs, threshold_params) → output` — versioned params |
| **Decision** | `f(l2_c3_evidence, decision_rules) → output` — versioned rules |

### E.2 — Replay Requirements

For any block to be **replay-certified**, the following must be true:

1. **B-layer facts exist**: The block has OHLC + identity in `ovc.ovc_blocks_v01_1_min`
2. **Prior context exists**: All blocks in the lookback window exist (for L2+)
3. **Parameters are versioned**: All thresholds/configs have documented values
4. **Formula hash matches**: The computation formula matches the versioned specification

### E.3 — Version Metadata Required Per Computed Block

```sql
derived_version     TEXT     -- e.g., 'v0.1'
formula_hash        TEXT     -- MD5 of formula definition string
window_spec         TEXT     -- e.g., 'N=12;session=date_ny'
threshold_version   TEXT     -- e.g., 'th_v0.1' (for L3)
computed_at         TIMESTAMPTZ
```

---

## Section F — Examples (10 Metrics Per Tier)

### F.1 — B-Layer Examples (Identity + OHLC + Metadata)

| # | Field | Description | Source |
|---|-------|-------------|--------|
| 1 | `block_id` | Unique identifier: `YYYYMMDD-{A-L}-{SYM}` | Derived from timestamp |
| 2 | `sym` | Symbol: `EURUSD`, `GBPUSD`, etc. | Export payload |
| 3 | `date_ny` | NY session date | Export payload |
| 4 | `block2h` | 2H block label: A-L | Export payload |
| 5 | `o` | Open price | OHLC |
| 6 | `h` | High price | OHLC |
| 7 | `l` | Low price | OHLC |
| 8 | `c` | Close price | OHLC |
| 9 | `bar_close_ms` | Close timestamp (epoch ms) | Export payload |
| 10 | `source` | Data source: `tv`, `oanda`, `manual` | Ingest metadata |

### F.2 — L1 Examples (Single-Bar Primitives)

| # | Metric | Formula | Inputs |
|---|--------|---------|--------|
| 1 | `range` | `h - l` | h, l |
| 2 | `body` | `abs(c - o)` | c, o |
| 3 | `direction` | `c > o ? 1 : c < o ? -1 : 0` | c, o |
| 4 | `ret` | `(c - o) / o` | c, o |
| 5 | `logret` | `ln(c / o)` | c, o |
| 6 | `body_ratio` | `body / range` | body, range |
| 7 | `close_pos` | `(c - l) / range` | c, l, range |
| 8 | `upper_wick` | `h - max(o, c)` | h, o, c |
| 9 | `lower_wick` | `min(o, c) - l` | o, c, l |
| 10 | `clv` | `((c - l) - (h - c)) / (h - l)` | c, h, l |

### F.3 — L2 Examples (Multi-Bar Structure)

| # | Metric | Window | Description |
|---|--------|--------|-------------|
| 1 | `gap` | N=1 | `o[0] - c[-1]` |
| 2 | `sess_high` | session | Running max(h) within date_ny |
| 3 | `sess_low` | session | Running min(l) within date_ny |
| 4 | `roll_avg_range_12` | N=12 | `avg(range)` over 12 blocks |
| 5 | `roll_std_logret_12` | N=12 | `stddev(logret)` over 12 blocks |
| 6 | `range_z_12` | N=12 | `(range - avg) / std` |
| 7 | `hh_12` | N=12 | `h > max(h[-12:-1])` |
| 8 | `ll_12` | N=12 | `l < min(l[-12:-1])` |
| 9 | `took_prev_high` | N=1 | `h > h[-1]` |
| 10 | `took_prev_low` | N=1 | `l < l[-1]` |

### F.4 — L3 Examples (Categorical Tags)

| # | Metric | Type | Derivation |
|---|--------|------|------------|
| 1 | `state_tag` | enum | OR + RER + CLV → {OB, OS, EQ, MID} |
| 2 | `value_tag` | enum | SD → {V+, V-, EQ} |
| 3 | `event_tag` | enum | took_hi + took_lo + OA → category |
| 4 | `cp_tag` | string | OR + MC3 + VF3 + wicks → profile |
| 5 | `tt` | enum | Composite trade trigger |
| 6 | `rd_state` | enum | Width + drift → {RANGE, SOFT_RANGE, NO_RANGE} |
| 7 | `rd_brkdir` | enum | Close vs rails → {UP, DN, 0} |
| 8 | `tis` | int | barssince(state_tag change) |
| 9 | `flip` | bool | State tag reversal detection |
| 10 | `sweep` | enum | Liquidity sweep classification |

### F.5 — Decision Layer Examples

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | `L3_BIAS` | enum | UP/DN/FLAT directional bias |
| 2 | `L3_BIAS_WHY` | string | Reasons supporting bias |
| 3 | `L3_PLAY` | enum | Trade type classification |
| 4 | `L3_PLAY_WHY` | string | Reasons for play selection |
| 5 | `L3_PERMIT` | bool | Trade permission gate |
| 6 | `L3_PERMIT_WHY` | string | Permission gate reasons |
| 7 | `L3_PRED` | enum | Predicted outcome direction |
| 8 | `L3_PRED_CONF` | float | Confidence score [0, 1] |
| 9 | `L3_PRED_WHY` | string | Prediction evidence |
| 10 | `L3_STATE` | string | Combined state summary |

---

## Section G — Ambiguous/Borderline Fields List

The following fields have unclear tier assignment based on current definitions:

| Field | Current Tier | Ambiguity | Proposed Resolution |
|-------|--------------|-----------|---------------------|
| `rd_hi` | L3 | Numeric rolling output (L2-like) | Split RD: numeric → L2, categorical → L3 |
| `rd_lo` | L3 | Numeric rolling output (L2-like) | Split RD: numeric → L2, categorical → L3 |
| `rd_mid` | L3 | Arithmetic from rd_hi/rd_lo | Move to L2 with rd_hi/rd_lo |
| `rd_w_rrc` | L3 | Numeric normalized width | Move to L2 |
| `state_tag` | L3 | Immediate threshold classification (no regime memory) | Consider L2.5 sub-tier |
| `value_tag` | L3 | Single-bar threshold → category | Consider L2.5 sub-tier |
| `event_tag` | L3 | Immediate classification, no persistence | Consider L2.5 sub-tier |
| `roll_avg_range_12` | L1 (impl) | Requires 12-block window | Reclassify to L2 |
| `roll_std_logret_12` | L1 (impl) | Requires 12-block window | Reclassify to L2 |
| `range_z_12` | L1 (impl) | Depends on rolling stats | Reclassify to L2 |
| `sess_high` | L1 (impl) | Session-scoped accumulator | Reclassify to L2 |
| `sess_low` | L1 (impl) | Session-scoped accumulator | Reclassify to L2 |
| `hh_12` | L1 (impl) | 12-block structural break | Reclassify to L2 |
| `ll_12` | L1 (impl) | 12-block structural break | Reclassify to L2 |
| `gap` | L1 (impl) | Requires prev_c | Reclassify to L2 |
| `news_flag` | B | External input, not derivable | Reclassify to metadata or external table |
| `brb` | L1 | Bar-relative-body, uses body_ratio | Confirm L1 (depends only on current bar) |

---

## Section H — Decisions Required Before Implementation

### H.1 — Tier Boundary Decisions

| ID | Question | Options | Impact |
|----|----------|---------|--------|
| D1 | Should L1 include trivial rolling features? | (a) Yes, amend L1 def; (b) No, split view | View structure |
| D2 | Should immediate categorical tags be L2.5 or L3? | (a) L3 (status quo); (b) New L2.5 tier | Tier model complexity |
| D3 | Should RD module be split by output type? | (a) Yes, L2/L3 split; (b) No, keep cohesive | Module organization |
| D4 | How to version threshold parameters? | (a) Code freeze; (b) Config table; (c) Export with block | Replay architecture |
| D5 | Where does `news_flag` belong? | (a) B-layer + provenance; (b) Metadata; (c) External table | Schema design |

### H.2 — Implementation Dependencies

| Decision | Blocks Implementation Of |
|----------|--------------------------|
| D1 | `derived.ovc_block_features_v0_1` restructuring |
| D2 | L3 Python implementation, tier validation |
| D3 | RD module implementation location |
| D4 | All L3 implementations (replay guarantee) |
| D5 | B-layer validation rules |

### H.3 — Recommended Resolution Path

1. **D1**: Amend L1 definition to "L1 = single-bar; L1+ = trivial session/rolling" OR split into `derived.ovc_l1_pure_v0_1` and `derived.ovc_l2_simple_v0_1`
2. **D2**: Adopt L2.5 sub-tier for "immediate categorical interpretations" to preserve L3 for regime patterns
3. **D3**: Split RD — architectural purity > module cohesion
4. **D4**: Implement `derived.threshold_registry_v0_1` table with threshold snapshots per version
5. **D5**: Move `news_flag` to ingest metadata or create `ovc.news_calendar` external table

---

## Appendix: Validation Rules

### Field-to-Tier Validation

For any field `F` assigned to tier `T`:

```
VALID(F, L1) ⟺ inputs(F) ⊆ {o, h, l, c} of current block
VALID(F, L2) ⟺ inputs(F) ⊆ {B-fields, L1-fields} ∧ window_spec defined
VALID(F, L3) ⟺ inputs(F) ⊆ {L2-fields} ∧ threshold_params versioned
VALID(F, Decision) ⟺ inputs(F) ⊆ {L2-fields, L3-fields} ∧ rules versioned
```

### Replay Certification

A block `B` with derived metrics is **replay-certified** iff:

1. `B.block_id` exists in `ovc.ovc_blocks_v01_1_min`
2. All blocks in lookback window exist (count ≥ window_spec.N - 1)
3. `derived_version` matches known version
4. `formula_hash` matches versioned formula
5. `threshold_version` (if L3) matches known threshold set

---

*Spec Version: v0.1 | Generated: 2025-02-19 | Status: DRAFT*
