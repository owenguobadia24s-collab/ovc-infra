# Study Results

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

> ⚠️ **DISCLAIMER:** Results below are **descriptive only**. No predictive claims are made.
> Regime partitions are for **reporting purposes only** — not trade filters.

## Summary Statistics

### Sample Overview

| Metric | Value |
|--------|-------|
| Total observations | _[PENDING]_ |
| Instruments | GBPUSD |
| Time span | 2025-01-01 to 2026-01-01 |
| Missing data (excluded) | _[PENDING]_ |

### Regime Thresholds

| Percentile | rng Value |
|------------|-----------|
| P33 (LOW/MID boundary) | _[PENDING]_ |
| P66 (MID/HIGH boundary) | _[PENDING]_ |

**Note:** Thresholds computed over full sample (GBPUSD, 2025-01-01 to 2026-01-01).

---

## Sample Sizes per Regime

| Regime | N Blocks | % of Total |
|--------|----------|------------|
| LOW | _[PENDING]_ | ~33% |
| MID | _[PENDING]_ | ~33% |
| HIGH | _[PENDING]_ | ~33% |
| **Total** | _[PENDING]_ | 100% |

---

## Primary Results

### Correlations per Regime (Score vs Outcome)

| Regime | N | corr(score, fwd_ret_3) | corr(score, mfe_3) | corr(score, mae_3) |
|--------|---|------------------------|--------------------|--------------------|
| LOW | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| **Full Sample** | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

**Interpretation guidance:**
- Correlations describe linear association strength; they do NOT imply causality or tradability.
- Differences across regimes indicate regime-sensitivity of the score–outcome relationship.

---

## Bucket Summaries per Regime

### LOW Volatility Regime

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### MID Volatility Regime

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### HIGH Volatility Regime

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

**Note:** Score bucket edges are computed over the **full sample** and applied identically across all regimes.

---

## Tail Comparison per Regime

### Top Decile (Score Bucket 90-100) vs Bottom Decile (Score Bucket 0-10)

| Regime | Tail | N | mean(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------|------|---|-----------------|-------------|-------------|
| LOW | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| LOW | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

**Interpretation guidance:**
- Tail comparisons describe extreme score values' outcome distributions.
- Differences between tails within a regime do NOT imply exploitable patterns.

---

## Score Distribution by Regime

| Regime | N | mean(score) | std(score) | min | P25 | P50 | P75 | max |
|--------|---|-------------|------------|-----|-----|-----|-----|-----|
| LOW | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

---

## Outcome Distribution by Regime

### fwd_ret_3

| Regime | N | mean | std | min | P25 | P50 | P75 | max |
|--------|---|------|-----|-----|-----|-----|-----|-----|
| LOW | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### mfe_3

| Regime | N | mean | std | min | P25 | P50 | P75 | max |
|--------|---|------|-----|-----|-----|-----|-----|-----|
| LOW | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### mae_3

| Regime | N | mean | std | min | P25 | P50 | P75 | max |
|--------|---|------|-----|-----|-----|-----|-----|-----|
| LOW | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| MID | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| HIGH | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

---

## Explicit Disclaimers

1. **No Predictive Claim:** These results describe historical associations. They do NOT predict future outcomes.

2. **Partitions Are Reporting Only:** Volatility regimes (LOW/MID/HIGH) are descriptive categories for organizing results. They are NOT trade filters, entry conditions, or decision boundaries.

3. **No Tradability Implication:** Differences in correlations or bucket summaries across regimes do NOT imply that any regime is "better" or "worse" for trading.

4. **No Optimization:** Regime cutoffs (P33, P66) and score buckets are fixed. No fitting or optimization was performed to maximize any metric.

5. **Non-Canonical:** This study is a downstream research artifact. Results do NOT modify canonical Option B/C definitions.
