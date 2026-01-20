# Study Verdict

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Hypothesis Outcome

| Hypothesis | Supported? | Confidence |
|------------|------------|------------|
| Volatility regimes may modulate score–outcome association strength | _[PENDING RESULTS]_ | Low–Medium |

---

## Interpretation Framework

This study examines whether the association between `block_range_intensity` and forward outcomes
differs across volatility regimes. The following framework guides interpretation:

### If Correlations Differ Materially by Regime

**Observation:** The correlation between score and outcomes is substantially different in LOW vs MID vs HIGH regimes.

**Interpretation:**
- The score–outcome relationship is **regime-sensitive**.
- The strength of the linear association varies with the underlying volatility level.
- This suggests that a single pooled correlation may obscure regime-specific patterns.

**What this does NOT mean:**
- It does NOT mean any regime is "better" for trading.
- It does NOT imply the score is more "useful" in certain regimes.
- It does NOT recommend filtering trades by regime.

### If Bucket Gradients Differ by Regime

**Observation:** The progression of mean outcomes across score buckets differs by regime.

**Interpretation:**
- The distributional relationship between score and outcomes varies by volatility level.
- In some regimes, extreme scores may correspond to different outcome distributions than in others.

**What this does NOT mean:**
- It does NOT validate any threshold for decision-making.
- It does NOT imply monotonicity should be expected or exploited.

### If Tail Behavior Differs by Regime

**Observation:** The top decile vs bottom decile outcome differences vary by regime.

**Interpretation:**
- Extreme score values have different outcome characteristics depending on regime.
- This could reflect different market dynamics in low vs high volatility periods.

**What this does NOT mean:**
- It does NOT recommend focusing on tails in any regime.
- It does NOT imply tail-based rules would be profitable.

---

## Key Findings

### Finding 1: Regime Distribution

_[PENDING: Summary of sample sizes per regime]_

**Evidence:** See Results > Sample Sizes per Regime

**Implication:** Confirms regimes are populated and analysis is feasible.

### Finding 2: Cross-Regime Correlation Comparison

_[PENDING: Summary of correlation differences]_

**Evidence:** See Results > Correlations per Regime

**Implication:** Describes degree of regime-sensitivity in score–outcome relationship.

### Finding 3: Bucket Gradient Patterns

_[PENDING: Summary of bucket-level outcome progressions]_

**Evidence:** See Results > Bucket Summaries per Regime

**Implication:** Describes shape of score–outcome relationship within each regime.

---

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Single instrument (GBPUSD) | Results may not generalize to other pairs | Future study with multi-instrument scope |
| One-year window | Regime characteristics may vary across years | Extend window or replicate on other periods |
| Fixed regime cutoffs (P33/P66) | Alternative cutoffs may show different patterns | Accept as design choice; no optimization by intent |
| No out-of-sample validation | Cannot assess stability of patterns | Future walk-forward study |
| Descriptive only | No inferential statistics or confidence intervals | Accept as design scope |

---

## What This Study Does NOT Conclude

- ❌ This study does NOT recommend any trading strategy
- ❌ This study does NOT validate entry/exit rules
- ❌ This study does NOT claim predictive power for live trading
- ❌ This study does NOT modify canonical metric definitions
- ❌ This study does NOT claim any regime is "better" or "worse"
- ❌ This study does NOT recommend filtering by volatility regime
- ❌ This study does NOT imply exploitable patterns exist
- ❌ This study does NOT reference PnL, Sharpe, "edge", or "alpha"

---

## Confidence Assessment

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Data quality | Medium | Depends on canonical pipeline completeness |
| Statistical rigor | Low | Descriptive only; no significance tests |
| Reproducibility | High | Deterministic SQL, fixed parameters |
| Generalizability | Low | Single instrument, single year |

**Overall confidence:** Low–Medium (by design)

This study intentionally operates at low–medium confidence because:
1. It is exploratory/descriptive, not confirmatory.
2. Regime cutoffs are arbitrary (P33/P66), not validated.
3. Single-instrument, single-year scope limits generalizability.

---

## Next Steps

### Recommended Follow-Up

1. **Populate results:** Execute analysis SQL and fill in results tables.
2. **Multi-instrument replication:** Repeat for EURUSD, USDJPY to assess generalizability.
3. **Temporal stability check:** Split window (e.g., H1 2025 vs H2 2025) and compare regime behavior.
4. **Alternative regime definitions:** (If warranted) Study with quintiles or other fixed partitions.

### NOT Recommended

- ❌ Proceeding to strategy development based solely on this study
- ❌ Modifying canonical definitions based on these findings
- ❌ Using regime as a trade filter without extensive validation
- ❌ Optimizing regime cutoffs for outcome metrics

---

## Canonical Promotion Path

**Not applicable.** This study is purely descriptive and does not propose any new canonical metrics, features, or definitions. Regime definitions used here are for reporting only and should NOT be promoted to canonical status without separate rigorous validation.

---

## Statement of Non-Tradability

**Explicit statement:** This study describes statistical patterns for research understanding only. No trading decisions, position sizing, entry rules, exit rules, or risk management conclusions should be drawn from these results. Regime sensitivity, if observed, is a descriptive property that does NOT imply actionable opportunity.
