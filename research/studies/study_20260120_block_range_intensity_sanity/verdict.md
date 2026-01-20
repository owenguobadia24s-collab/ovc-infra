# Study Verdict

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## ⚠️ NO OUTCOMES USED

**This verdict contains NO claims about predictive power or tradability.**

This study examined only the distributional properties of the score. No outcome data was used.

---

## Primary Question Outcome

| Question | Answer | Confidence |
|----------|--------|------------|
| Does `block_range_intensity` behave as expected for a z-score? | [Pending execution] | [Pending] |

---

## Key Findings

### Finding 1: Central Tendency

_[Pending execution: Document whether mean ≈ 0 and std ≈ 1]_

**Evidence:** Distribution table in [results.md](results.md)

**Implication:** [To be documented]

### Finding 2: Tail Behavior

_[Pending execution: Document whether tails are normal, fat, or thin]_

**Evidence:** Tail analysis in [results.md](results.md)

**Implication:** [To be documented]

### Finding 3: Temporal Stability

_[Pending execution: Document whether score is stable over time]_

**Evidence:** Quarterly table in [results.md](results.md)

**Implication:** [To be documented]

### Finding 4: Data Quality

_[Pending execution: Document NULL rate and any issues]_

**Evidence:** Quality metrics in [results.md](results.md)

**Implication:** [To be documented]

---

## Expected Observations

For a well-behaved z-score, we expect:

| Property | Expected | Concern If |
|----------|----------|------------|
| Mean | ≈ 0 | > ±0.1 |
| Std | ≈ 1 | < 0.8 or > 1.2 |
| Skewness | ≈ 0 | > ±0.5 |
| Kurtosis | ≈ 3 (normal) | > 5 (fat tails) |
| P1/P99 | ≈ ±2.3 | > ±3.5 |
| NULL rate | < 1% | > 5% |

---

## Critical Disclaimer

> **Score sanity does not imply usefulness.**

A score that passes all sanity checks:
- May still have zero predictive value
- May still be useless for any downstream purpose
- May still produce spurious patterns when combined with outcomes

This study validates only that the score is computed correctly and behaves as designed. It makes NO claims about the score's utility.

---

## Anomaly Documentation

### Observed Anomalies

| Anomaly | Severity | Description | Recommendation |
|---------|----------|-------------|----------------|
| [none yet] | — | — | — |

### Expected Non-Issues

The following observations are NOT anomalies:

- Quarterly means deviating from 0: Expected because z-score is global, not rolling
- Fat tails (kurtosis > 3): Common for financial data; document but do not "fix"
- Right skew: `rng` is non-negative, may cause asymmetry

---

## Confidence Assessment for Downstream Use

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Score computation | [Pending] | Does SQL execute correctly? |
| Distribution shape | [Pending] | Is it approximately z-score-like? |
| Data quality | [Pending] | NULL rate and coverage |
| Temporal stability | [Pending] | No severe drift? |

**Overall sanity confidence:** [Pending]

---

## Recommendation for Outcome Studies

| Sanity Status | Recommendation |
|---------------|----------------|
| All checks pass | Score may be used in outcome studies (with appropriate caveats) |
| Minor anomalies | Document anomalies; proceed with caution |
| Major anomalies | Investigate before using in downstream analysis |
| Critical failures | Do not use score until issues resolved |

**Current recommendation:** [Pending execution]

---

## What This Verdict Does NOT Conclude

- ❌ The score is useful or predictive
- ❌ The score should be used for trading
- ❌ High/low score values are meaningful
- ❌ The score has any relationship to outcomes
- ❌ The score passes any "edge" or "alpha" test

---

## Next Steps

### Recommended Follow-Up

1. **If sanity passes:** Proceed to outcome correlation study with appropriate caveats
2. **Document all anomalies:** Even minor ones, for future reference
3. **Expand instruments:** Repeat sanity check for EURUSD, etc.

### NOT Recommended

- ❌ Assuming sanity implies usefulness
- ❌ Proceeding to strategy development
- ❌ Using score values as trading signals

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Author | @ovc-research | 2026-01-20 |
| Reviewer | [pending] | — |
