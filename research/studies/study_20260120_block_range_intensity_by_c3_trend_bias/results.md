# Study Results

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

> ⚠️ **DISCLAIMER:** Results below are **descriptive only**. No predictive claims are made.
> C3 trend bias categories are for **reporting purposes only** — not trade filters or state recommendations.

## Summary Statistics

### Sample Overview

| Metric | Value |
|--------|-------|
| Total observations | _[PENDING]_ |
| Instruments | GBPUSD |
| Time span | 2025-01-01 to 2026-01-01 |
| Missing data (rng NULL, excluded) | _[PENDING]_ |

### Conditioning Variable

| Field | Source |
|-------|--------|
| `c3_trend_bias` | `derived.ovc_block_features_v0_1` (canonical C3) |

**Note:** This study uses `c3_trend_bias` as-is from the canonical C3 layer. No definition or computation of trend bias is performed here.

---

## Category Counts (c3_trend_bias)

| c3_trend_bias | N Blocks | % of Total |
|---------------|----------|------------|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ |
| _[... additional categories ...]_ | _[PENDING]_ | _[PENDING]_ |
| **NULL** | _[PENDING]_ | _[PENDING]_ |
| **Total** | _[PENDING]_ | 100% |

**Note:** Observed categories will be populated at execution time. NULL values are documented but excluded from per-category analysis.

---

## Primary Results

### Correlations per c3_trend_bias (Score vs Outcome)

| c3_trend_bias | N | corr(score, fwd_ret_3) | corr(score, mfe_3) | corr(score, mae_3) |
|---------------|---|------------------------|--------------------|--------------------|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[... additional categories ...]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| **Full Sample (excl NULL)** | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

**Interpretation guidance:**
- Correlations describe linear association strength; they do NOT imply causality or tradability.
- Differences across categories indicate trend-bias sensitivity of the score–outcome relationship.
- No category should be interpreted as "better" or "worse" based on correlations.

---

## Bucket Summaries per c3_trend_bias

### _[CATEGORY_1]_

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### _[CATEGORY_2]_

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### _[CATEGORY_3]_

| Score Bucket | N | mean(fwd_ret_3) | std(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|--------------|---|-----------------|----------------|-------------|-------------|
| 0-10 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 10-25 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 25-50 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 50-75 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 75-90 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| 90-100 | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

_[Additional category tables to be added at execution time based on observed categories]_

**Note:** Score bucket edges are computed over the **full sample** and applied identically across all c3_trend_bias categories.

---

## Tail Comparison per c3_trend_bias

### Top Decile (Score Bucket 90-100) vs Bottom Decile (Score Bucket 0-10)

| c3_trend_bias | Tail | N | mean(fwd_ret_3) | mean(mfe_3) | mean(mae_3) |
|---------------|------|---|-----------------|-------------|-------------|
| _[CATEGORY_1]_ | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_1]_ | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | Bottom (0-10) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | Top (90-100) | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[... additional categories ...]_ | _[...]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

**Interpretation guidance:**
- Tail comparisons describe extreme score values' outcome distributions within each category.
- Differences between tails within a category do NOT imply exploitable patterns.

---

## Score Distribution by c3_trend_bias

| c3_trend_bias | N | mean(score) | std(score) | min | P25 | P50 | P75 | max |
|---------------|---|-------------|------------|-----|-----|-----|-----|-----|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

---

## Outcome Distribution by c3_trend_bias

### fwd_ret_3

| c3_trend_bias | N | mean | std | min | P25 | P50 | P75 | max |
|---------------|---|------|-----|-----|-----|-----|-----|-----|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### mfe_3

| c3_trend_bias | N | mean | std | min | P25 | P50 | P75 | max |
|---------------|---|------|-----|-----|-----|-----|-----|-----|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

### mae_3

| c3_trend_bias | N | mean | std | min | P25 | P50 | P75 | max |
|---------------|---|------|-----|-----|-----|-----|-----|-----|
| _[CATEGORY_1]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_2]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |
| _[CATEGORY_3]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ | _[PENDING]_ |

---

## Explicit Disclaimers

1. **No Predictive Claim:** These results describe historical associations. They do NOT predict future outcomes.

2. **Categories Are Reporting Only:** C3 trend bias categories are descriptive partitions for organizing results. They are NOT trade filters, entry conditions, or state recommendations.

3. **No Category Ranking:** Results do NOT identify any c3_trend_bias state as "better" or "worse" for trading. Differences are descriptive, not prescriptive.

4. **Association ≠ Predictability:** Observing different correlations across categories does NOT imply the score predicts outcomes in any category.

5. **Conditioning ≠ Tradability:** Conditioning analysis describes statistical patterns; it does NOT imply actionable opportunity.

6. **No C3 Definition Work:** This study uses `c3_trend_bias` as-is from canonical C3. No definition, computation, or modification of trend bias logic is performed.

7. **Non-Canonical:** This study is a downstream research artifact. Results do NOT modify canonical Option B/C definitions.
