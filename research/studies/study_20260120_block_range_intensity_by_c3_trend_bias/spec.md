# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_by_c3_trend_bias` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

_How do score–outcome associations vary across canonical trend bias states (l3_trend_bias)?_

> Specifically: Does the association between `block_range_intensity` and forward outcomes
> (`fwd_ret_3`, `mfe_3`, `mae_3`) differ when conditioning on the canonical `l3_trend_bias`
> field from the L3 feature layer?

---

## Hypothesis

_Uncertain — structural state may modulate dispersion._

> Market trend/bias states may produce different score–outcome association patterns. This
> hypothesis is exploratory; the study is designed to describe differences across canonical
> L3 states, not to confirm a directional expectation or identify "better" states.

---

## Scope

### Included

- Instruments: GBPUSD
- Time window: 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (exclusive)
- Bar types: 2H blocks
- Outcomes: `fwd_ret_3`, `mfe_3`, `mae_3`
- Score: `block_range_intensity` v1.0
- Conditioning variable: `l3_trend_bias` (canonical L3 field)

### Excluded

- Instruments other than GBPUSD
- Blocks outside the time window
- Outcomes beyond 3-bar horizon (e.g., fwd_ret_6, mfe_6, mae_6)
- Weekend/holiday blocks (if excluded by canonical pipeline)
- Blocks with NULL `l3_trend_bias` (documented separately)

---

## Conditioning Variable: l3_trend_bias

**Source:** `derived.ovc_block_features_v0_1.l3_trend_bias`

**Important:**
- This study uses `l3_trend_bias` **as-is** from the canonical L3 layer.
- This study does NOT define, compute, or modify the trend bias logic.
- The underlying derivation (from `dir_streak`, `dir_change`, etc.) is documented in L3 specifications, not here.
- Observed categories will be documented at execution time; no assumptions about category values.
- Categories are **descriptive partitions** for reporting — NOT trade filters or signals.
- No category is ranked as "better" or "worse" than others.

---

## Success Criteria

_This study is descriptive; success is defined by completeness and reproducibility, not by statistical significance thresholds._

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Sample size per category | N ≥ 50 | Sufficient for stable statistics |
| Results populated | All tables complete | Reproducibility requirement |
| NULL rate documented | Reported | Transparency requirement |

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a strategy or trading system
- ❌ This does NOT define entry/exit rules
- ❌ This does NOT optimize for PnL, Sharpe, or any performance metric
- ❌ This does NOT modify canonical definitions
- ❌ This does NOT claim predictive power or tradability
- ❌ This does NOT define or compute l3_trend_bias (uses canonical field only)
- ❌ This does NOT rank trend bias states as better or worse
- ❌ This does NOT recommend trading in specific states
- ❌ This does NOT reference "edge", "alpha", or "signal" in a trading context

---

## Dependencies

- Canonical views:
  - `derived.ovc_block_features_v0_1` (block_id, ts, instrument, rng, l3_trend_bias)
  - `derived.ovc_outcomes_v0_1` (block_id, fwd_ret_3, mfe_3, mae_3)
- Scores:
  - `research/scores/score_block_range_intensity_v1_0.sql` (read-only definition)
- External data: None

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
