# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_by_session` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

_How do score–outcome associations vary across time-of-day sessions?_

> Specifically: Does the association between `block_range_intensity` and forward outcomes
> (`fwd_ret_3`, `mfe_3`, `mae_3`) differ when conditioning on fixed UTC time-of-day sessions
> (SESSION_A through SESSION_D)?

---

## Hypothesis

_Uncertain — intraday structure may affect dispersion._

> Market microstructure varies throughout the trading day (e.g., London open, NY overlap).
> This may produce different score–outcome association patterns across sessions. This hypothesis
> is exploratory; the study is designed to describe differences, not to confirm a directional
> expectation or identify "better" sessions.

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

## Session Definition

Sessions are defined as **fixed UTC hour bins** — descriptive partitions for reporting:

| Session | UTC Hours | Description |
|---------|-----------|-------------|
| SESSION_A | 00:00–06:00 | Asian session |
| SESSION_B | 06:00–12:00 | London morning |
| SESSION_C | 12:00–18:00 | NY / London overlap + NY afternoon |
| SESSION_D | 18:00–24:00 | NY evening / Asian transition |

**Important:**
- Sessions are **fixed bins**, not optimized or tuned.
- Sessions are **reporting partitions only** — they are NOT trade filters or signals.
- Session boundaries are defined in UTC; local market interpretations are approximate.
- No session is ranked as "better" or "worse" than others.

---

## Success Criteria

_This study is descriptive; success is defined by completeness and reproducibility, not by statistical significance thresholds._

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Sample size per session | N ≥ 100 | Sufficient for stable statistics |
| Results populated | All tables complete | Reproducibility requirement |
| Session coverage | All 4 sessions have data | Confirms partition validity |

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a strategy or trading system
- ❌ This does NOT define entry/exit rules
- ❌ This does NOT optimize for PnL, Sharpe, or any performance metric
- ❌ This does NOT modify canonical definitions
- ❌ This does NOT claim predictive power or tradability
- ❌ This does NOT rank sessions as better or worse
- ❌ This does NOT recommend trading during specific sessions
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
