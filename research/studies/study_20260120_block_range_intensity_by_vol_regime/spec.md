# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_by_vol_regime` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

_How do score–outcome associations vary across volatility regimes (LOW/MID/HIGH)?_

> Specifically: Does the association between `block_range_intensity` and forward outcomes
> (`fwd_ret_3`, `mfe_3`, `mae_3`) differ when conditioning on the volatility regime of the
> underlying block, where regime is defined by the canonical `rng` feature?

---

## Hypothesis

_Uncertain — volatility may modulate dispersion._

> Volatility regimes may produce different score–outcome association strengths. HIGH volatility
> blocks may exhibit greater outcome dispersion, while LOW volatility blocks may cluster near
> zero. This hypothesis is exploratory; the study is designed to describe differences, not to
> confirm a specific directional expectation.

---

## Scope

### Included

- Instruments: GBPUSD
- Time window: 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (exclusive)
- Bar types: 2H blocks
- Outcomes: `fwd_ret_3`, `mfe_3`, `mae_3`
- Score: `block_range_intensity` v1.0

### Excluded

- Instruments other than GBPUSD
- Blocks outside the time window
- Outcomes beyond 3-bar horizon (e.g., fwd_ret_6, mfe_6, mae_6)
- Weekend/holiday blocks (if excluded by canonical pipeline)

---

## Regime Definition

Volatility regimes are defined as **descriptive partitions** based on the canonical `rng` feature:

| Regime | Definition |
|--------|------------|
| LOW | `rng <= P33` (33rd percentile) |
| MID | `P33 < rng <= P66` (33rd–66th percentile) |
| HIGH | `rng > P66` (above 66th percentile) |

**Important:**
- Percentiles are computed over the **full sample** (GBPUSD, full window), not per-slice.
- Regime bins are **fixed cutoffs**, not optimized or tuned.
- Regimes are **reporting partitions only** — they are NOT trade filters or signals.

---

## Success Criteria

_This study is descriptive; success is defined by completeness and reproducibility, not by statistical significance thresholds._

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Sample size per regime | N ≥ 100 | Sufficient for stable statistics |
| Results populated | All tables complete | Reproducibility requirement |
| No data leakage | Regimes defined from features only | Prevent contamination |

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a strategy or trading system
- ❌ This does NOT define entry/exit rules
- ❌ This does NOT optimize for PnL, Sharpe, or any performance metric
- ❌ This does NOT modify canonical definitions
- ❌ This does NOT claim predictive power or tradability
- ❌ This does NOT optimize regime cutoffs
- ❌ This does NOT treat regimes as trade filters
- ❌ This does NOT reference "edge", "alpha", or "signal" in a trading context

---

## Dependencies

- Canonical views:
  - `derived.ovc_block_features_v0_1` (block_id, ts, instrument, rng)
  - `derived.ovc_outcomes_v0_1` (block_id, fwd_ret_3, mfe_3, mae_3)
- Scores:
  - `research/scores/score_block_range_intensity_v1_0.sql` (read-only definition)
- External data: None

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
