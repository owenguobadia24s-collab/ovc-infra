# Study Specification

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Metadata

| Field | Value |
|-------|-------|
| Study ID | `study_20260120_block_range_intensity_temporal_stability` |
| Created | 2026-01-20 |
| Author | @ovc-research |
| Canonical Release | `ovc-v0.1-spine` |
| Status | Draft |

---

## Research Question

**Are score–outcome associations for block_range_intensity stable across time?**

This study partitions the analysis window into quarterly slices and examines whether the descriptive relationships observed in `study_20260120_block_range_intensity_vs_outcomes` persist, weaken, reverse, or vary across periods.

---

## Study Purpose

This is a **robustness check**, not a discovery exercise. We assess:

- Whether correlations are consistent across quarters
- Whether bucket patterns persist or drift
- Whether tail behavior is stable

We do NOT:

- Seek stronger effects in any period
- Optimize time windows
- Cherry-pick favorable periods
- Claim any period is "better" for trading

---

## Hypothesis

**Instability is an expected and acceptable outcome.**

For a simple z-scored range score, we have no strong reason to expect:
- Stable correlations across market regimes
- Persistent bucket patterns
- Time-invariant relationships

Findings of instability, drift, or regime sensitivity are valid conclusions, not failures.

---

## Scope

### Included

- **Instrument:** GBPUSD only
- **Time window:** 2025-01-01T00:00:00Z to 2026-01-01T00:00:00Z (UTC)
- **Score:** `block_range_intensity` v1.0
- **Outcomes:** `fwd_ret_3`, `mfe_3`, `mae_3`
- **Time slicing:** Quarterly (Q1, Q2, Q3, Q4 2025)

### Time Slice Definitions

| Slice | Start (inclusive) | End (exclusive) |
|-------|-------------------|-----------------|
| Q1 2025 | 2025-01-01 | 2025-04-01 |
| Q2 2025 | 2025-04-01 | 2025-07-01 |
| Q3 2025 | 2025-07-01 | 2025-10-01 |
| Q4 2025 | 2025-10-01 | 2026-01-01 |

### Excluded

- All other instruments
- Data outside the specified window
- Other outcomes

---

## Success Criteria

This study succeeds by documenting stability (or instability) clearly:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| All quarters have N ≥ 100 | Minimum for stable estimates | Per-slice validity |
| Correlations computed per quarter | 4 quarters × 3 outcomes | Primary deliverable |
| Bucket summaries per quarter | 4 quarters × 6 buckets × 3 outcomes | Full characterization |
| Stability assessment documented | Qualitative | Key conclusion |

**Note:** Finding instability is a valid success. The study does not require stable associations.

---

## Exclusions (What This Study Is NOT)

- ❌ This is NOT a search for the best time period
- ❌ This does NOT optimize windows for stronger effects
- ❌ This does NOT claim any period is tradable
- ❌ This does NOT modify bucket definitions per slice
- ❌ This does NOT constitute evidence of predictability

---

## Dependencies

- **Prior study:** `study_20260120_block_range_intensity_vs_outcomes` (full-sample baseline)
- **Canonical views:**
  - `derived.ovc_block_features_v0_1` (Option B)
  - `derived.ovc_outcomes_v0_1` (Option C)
- **Scores:**
  - `research/scores/score_block_range_intensity_v1_0.sql`

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-20 | Initial draft | @ovc-research |
