# Study Results

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Critical Disclaimer

> **No tradability or predictive claim is made in this document.**

Observed associations are descriptive only. They do not imply:
- Predictive power
- Exploitable edge
- Strategy recommendations
- Threshold validity

---

## Summary Statistics

### Sample Overview

| Metric | Value |
|--------|-------|
| Total blocks (pre-join) | [N_score] |
| Blocks with outcomes | [N_joined] |
| Join match rate | [%] |
| Instrument | GBPUSD |
| Time span | 2025-01-01 to 2026-01-01 |

### Score Distribution (for context)

| Statistic | Value |
|-----------|-------|
| Mean | [value] |
| Std | [value] |
| Min | [value] |
| Max | [value] |

### Outcome Distributions (unconditional)

| Outcome | Mean | Std | Min | P50 | Max |
|---------|------|-----|-----|-----|-----|
| `fwd_ret_3` | | | | | |
| `mfe_3` | | | | | |
| `mae_3` | | | | | |

---

## Correlation Analysis

### Score vs Outcomes (Pearson)

| Outcome | Correlation (r) | Interpretation |
|---------|-----------------|----------------|
| `fwd_ret_3` | [value] | [Negligible/Weak/Moderate] |
| `mfe_3` | [value] | [Negligible/Weak/Moderate] |
| `mae_3` | [value] | [Negligible/Weak/Moderate] |

**Interpretation guide:**

| |r| | Label |
|-----|-------|
| < 0.1 | Negligible |
| 0.1 – 0.3 | Weak |
| 0.3 – 0.5 | Moderate |
| > 0.5 | Strong |

---

## Bucket Summaries

### fwd_ret_3 by Score Bucket

| Bucket | N | Mean | Std | P25 | P50 | P75 |
|--------|---|------|-----|-----|-----|-----|
| 0-10 (bottom) | | | | | | |
| 10-25 | | | | | | |
| 25-50 | | | | | | |
| 50-75 | | | | | | |
| 75-90 | | | | | | |
| 90-100 (top) | | | | | | |

### mfe_3 by Score Bucket

| Bucket | N | Mean | Std | P50 |
|--------|---|------|-----|-----|
| 0-10 (bottom) | | | | |
| 10-25 | | | | |
| 25-50 | | | | |
| 50-75 | | | | |
| 75-90 | | | | |
| 90-100 (top) | | | | |

### mae_3 by Score Bucket

| Bucket | N | Mean | Std | P50 |
|--------|---|------|-----|-----|
| 0-10 (bottom) | | | | |
| 10-25 | | | | |
| 25-50 | | | | |
| 50-75 | | | | |
| 75-90 | | | | |
| 90-100 (top) | | | | |

---

## Tail Comparison (Bottom Decile vs Top Decile)

| Metric | Bottom Decile (0-10) | Top Decile (90-100) | Difference |
|--------|----------------------|---------------------|------------|
| N | | | — |
| Mean `fwd_ret_3` | | | |
| Mean `mfe_3` | | | |
| Mean `mae_3` | | | |

**Note:** This comparison is descriptive. No statistical test is applied. Observed differences do not imply exploitability.

---

## Figures

### Figure 1: Score vs fwd_ret_3 Scatter

_[Placeholder: Scatter plot of score_value vs fwd_ret_3]_

### Figure 2: Outcome Means by Bucket

_[Placeholder: Bar chart of mean fwd_ret_3 by bucket]_

### Figure 3: Bucket Distributions

_[Placeholder: Box plots of fwd_ret_3 by bucket]_

---

## Raw Output Location

| Output | Path | Status |
|--------|------|--------|
| Correlations | `research/outputs/study_20260120_block_range_intensity_vs_outcomes/correlations.csv` | Not yet created |
| Bucket summaries | `research/outputs/study_20260120_block_range_intensity_vs_outcomes/bucket_summaries.csv` | Not yet created |
| Combined dataset | `research/outputs/study_20260120_block_range_intensity_vs_outcomes/combined.csv` | Not yet created |
| Figures | `research/outputs/study_20260120_block_range_intensity_vs_outcomes/figures/` | Not yet created |

---

## Data Quality Notes

- [ ] Join match rate > 95%
- [ ] All buckets have N ≥ 50
- [ ] No unexpected NULLs in outcomes
- [ ] Results reproducible on re-run

---

## Execution Log

| Step | Timestamp | Notes |
|------|-----------|-------|
| Score computed | [pending] | |
| Outcomes joined | [pending] | |
| Correlations computed | [pending] | |
| Bucket summaries computed | [pending] | |
| Results documented | [pending] | |
