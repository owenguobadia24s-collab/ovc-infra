# Study Verdict

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Critical Disclaimer

> **Association does not imply predictability or exploitability.**

This study describes statistical relationships only. Any observed pattern:
- May be spurious
- May be unstable over time
- May disappear out-of-sample
- May be economically insignificant after costs
- Does NOT constitute a trading signal

---

## Primary Question Outcome

| Question | Answer | Confidence |
|----------|--------|------------|
| Do outcomes vary systematically across score buckets? | [Pending execution] | Low–Medium |

---

## Key Findings

### Finding 1: Correlation Magnitudes

_[Pending execution: Document whether correlations are negligible, weak, or moderate]_

**Evidence:** Correlation table in [results.md](results.md)

**Observation:** [To be documented]

### Finding 2: Bucket Patterns

_[Pending execution: Document whether outcome means vary monotonically with score buckets]_

**Evidence:** Bucket summary tables in [results.md](results.md)

**Observation:** [To be documented]

### Finding 3: Tail Comparison

_[Pending execution: Document whether top/bottom deciles differ]_

**Evidence:** Tail comparison in [results.md](results.md)

**Observation:** [To be documented]

---

## Interpretation Framework

### Negligible Association (|r| < 0.1, flat buckets)

If observed:
- Score has no linear relationship with outcomes
- Bucket summaries show no systematic pattern
- Consistent with null hypothesis of no relationship

**Implication:** Score does not describe outcome variation in this sample.

### Weak Association (0.1 ≤ |r| < 0.3, slight bucket gradient)

If observed:
- Score shows slight linear relationship with outcomes
- Bucket means show weak gradient
- Large overlap in bucket distributions

**Implication:** Association exists but is not strong. Does NOT imply predictability.

### Moderate Association (|r| ≥ 0.3, clear bucket gradient)

If observed:
- Would be unexpected for this simple score
- Warrants additional scrutiny for data issues
- Does NOT automatically imply exploitability

**Implication:** Investigate for artifacts before drawing conclusions.

---

## Repeated Disclaimer

> **Association does not imply predictability or exploitability.**

Even if correlations are non-zero:
- Correlation ≠ causation
- In-sample ≠ out-of-sample
- Statistical relationship ≠ economic profit
- Description ≠ strategy

This study produces no trading recommendations.

---

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Single instrument (GBPUSD) | Results may not generalize | Future: expand instruments |
| Single time window (2025) | Regime-specific effects possible | Future: rolling windows |
| Linear correlation only | Non-linear relationships missed | Future: rank correlations |
| No out-of-sample test | Unknown stability | Future: hold-out validation |
| Simple score (z-scored range) | May not capture meaningful variation | Future: richer scores |

---

## What This Study Does NOT Conclude

- ❌ The score predicts outcomes
- ❌ High-score blocks should be traded differently than low-score blocks
- ❌ Bucket boundaries are meaningful thresholds
- ❌ The score has "edge" or "alpha"
- ❌ Any strategy should be built on these findings

---

## Confidence Assessment

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Data quality | [Pending] | Depends on join match rate |
| Statistical rigor | Medium | Standard methods, no complex modeling |
| Reproducibility | High | Deterministic queries, documented inputs |
| Generalizability | Low | Single instrument, single window |

**Overall confidence:** Low–Medium (appropriate for exploratory work)

---

## Next Steps

### Recommended Follow-Up

1. **Expand instruments:** Repeat for EURUSD, USDJPY to test generalization
2. **Expand time:** Test stability across different periods
3. **Rank correlations:** Compute Spearman if Pearson is weak
4. **Additional outcomes:** Include fwd_ret_6, mfe_6, mae_6
5. **Document carefully:** Any non-negligible finding warrants skepticism

### NOT Recommended

- ❌ Building a strategy based on bucket patterns
- ❌ Using bucket boundaries as entry/exit thresholds
- ❌ Claiming the score is "predictive"
- ❌ Optimizing score parameters for outcome relationships

---

## Canonical Promotion Path

**Not applicable.** This study produces no artifacts intended for canonical promotion. The score remains non-canonical. Findings are descriptive only.

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Author | @ovc-research | 2026-01-20 |
| Reviewer | [pending] | — |
