# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_basic_feature_outcome_baseline` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

**How do selected Option B block-level features relate to Option C forward returns and excursions, descriptively?**

This study characterizes the statistical relationship between a small subset of canonical features and outcomes. It does not claim predictive utility or tradability.

---

## Hypothesis

**Neutral / weak relationships expected.**

The goal is characterization, not discovery of edge. We expect:

- Correlations will likely be weak (|r| < 0.3)
- Distributions may be non-normal
- Relationships may be noisy or non-linear

This study establishes a baseline for future research sanity checks.

---

## Scope

### Included

- **Instrument:** GBPUSD only
- **Time window:** 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (UTC)
- **Bar type:** 2H blocks from canonical Option B/C views
- **Features:** Small subset (2-3 numeric features)
- **Outcomes:** `fwd_ret_3`, `mfe_3`, `mae_3`

### Excluded

- All other instruments (EURUSD, etc.)
- Data outside the specified window
- Weekends/holidays (if no data exists)

---

## Success Criteria

This is a descriptive study. Success is defined as:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Sample size | N ≥ 500 | Minimum for stable correlation estimates |
| Data completeness | < 5% missing | Confidence in join integrity |
| Documented distributions | All features/outcomes | Baseline characterization complete |
| Correlation matrix computed | All pairs | Primary deliverable achieved |

**Note:** There is no "significant result" criterion. The study succeeds by producing a complete, documented characterization.

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a strategy or trading system
- ❌ This does NOT define entry/exit rules
- ❌ This does NOT optimize for PnL or any performance metric
- ❌ This does NOT modify canonical definitions
- ❌ This does NOT include regime classification
- ❌ This does NOT apply thresholds for decision-making
- ❌ This does NOT interpret results as signals

---

## Dependencies

- **Canonical views:**
  - `derived.ovc_block_features_v0_1` (Option B)
  - `derived.ovc_outcomes_v0_1` (Option C)
- **Scores:** None (this study does not consume or produce scores)
- **External data:** None

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
