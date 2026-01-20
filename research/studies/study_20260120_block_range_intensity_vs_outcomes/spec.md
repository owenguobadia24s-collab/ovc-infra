# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_vs_outcomes` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

**How do canonical outcomes (fwd_ret_3, mfe_3, mae_3) vary across buckets of the block_range_intensity score?**

This study describes the conditional distribution of outcomes given score buckets. It characterizes associations without claiming predictability.

---

## Hypothesis

**Neutral / uncertain.**

The goal is characterization, not discovery of edge. We have no strong prior about the direction or magnitude of any association. Possible observations:

- No meaningful association (most likely)
- Weak association (possible)
- Moderate or strong association (unexpected; would warrant scrutiny)

---

## Scope

### Included

- **Instrument:** GBPUSD only
- **Time window:** 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (UTC)
- **Score:** `block_range_intensity` v1.0
- **Outcomes:** `fwd_ret_3`, `mfe_3`, `mae_3`
- **Analysis:** Correlations + bucket summaries

### Excluded

- All other instruments
- Data outside the specified window
- Other outcomes (fwd_ret_1, fwd_ret_6, mfe_6, mae_6, rvol_6)

---

## Success Criteria

This is a descriptive study. Success is defined as:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Sample size | N ≥ 500 | Minimum for stable estimates |
| Join match rate | > 95% | Data quality confidence |
| All buckets populated | N ≥ 50 per bucket | Meaningful bucket statistics |
| Correlations computed | All 3 outcomes | Primary deliverable |
| Bucket summaries complete | 6 buckets × 3 outcomes | Full characterization |

**Note:** There is no "significant finding" criterion. The study succeeds by producing complete documentation.

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a strategy or trading system
- ❌ This does NOT define entry/exit rules
- ❌ This does NOT optimize for PnL or any metric
- ❌ This does NOT claim predictive power
- ❌ This does NOT recommend thresholds for decisions
- ❌ This does NOT label regimes
- ❌ This does NOT constitute evidence of exploitability

### On Bucket Usage

Buckets are used **for reporting purposes only**. They summarize outcome distributions at different score levels. They are NOT:

- Decision thresholds
- Entry/exit zones
- Regime boundaries
- Trading rules

---

## Dependencies

- **Canonical views:**
  - `derived.ovc_block_features_v0_1` (Option B)
  - `derived.ovc_outcomes_v0_1` (Option C)
- **Scores:**
  - `research/scores/score_block_range_intensity_v1_0.sql`
- **External data:** None

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
