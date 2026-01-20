# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_sanity` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

**What is the distributional and structural behavior of the `block_range_intensity` score across time and instruments?**

This study characterizes the score itself — its distribution, stability, and basic statistical properties — to validate that it behaves as expected before any downstream analysis.

---

## Critical Disclaimer

> **This study does NOT evaluate predictive power.**

This is a sanity check. We examine whether the score:
- Has expected distributional properties for a z-score
- Is stable over time
- Has no obvious data quality issues

We do NOT examine whether the score relates to any outcome.

---

## Hypothesis

**The score should exhibit z-score-like properties:**

- Mean approximately 0
- Standard deviation approximately 1
- Roughly symmetric distribution
- Reasonable tail behavior

Deviations from these properties are not necessarily errors, but should be documented and understood.

---

## Scope

### Included

- **Instrument:** GBPUSD only
- **Time window:** 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (UTC)
- **Score:** `block_range_intensity` (v1.0)
- **Analysis:** Distribution, stability, data quality

### Excluded

- All other instruments
- Data outside the specified window
- **ALL Option C outcomes (fwd_ret, mfe, mae, rvol)**

---

## Success Criteria

| Criterion | Expected | Rationale |
|-----------|----------|-----------|
| Score mean | Near 0 | Z-score property |
| Score std | Near 1 | Z-score property |
| NULL rate | < 1% | Data quality |
| No extreme drift | Rolling mean within ±0.5 | Stability |
| Documented distribution | Complete | Primary deliverable |

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT an outcome analysis
- ❌ This does NOT evaluate predictive power
- ❌ This does NOT claim the score is useful
- ❌ This does NOT define trading rules
- ❌ This does NOT threshold the score
- ❌ This does NOT compare to any benchmark

---

## Dependencies

- **Canonical views:**
  - `derived.ovc_block_features_v0_1` (Option B) — input to score
- **Scores:**
  - `research/scores/score_block_range_intensity_v1_0.sql`
- **Outcomes:** NONE
- **External data:** NONE

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
