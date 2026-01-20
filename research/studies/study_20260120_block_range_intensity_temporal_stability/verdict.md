# Study Verdict

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Critical Disclaimer

> **Temporal stability does not imply tradability.**

Even fully stable associations:
- May be spurious
- May be economically insignificant
- May not persist out-of-sample
- Do NOT constitute trading signals

Conversely, instability is a valid and informative finding.

---

## Primary Question Outcome

| Question | Answer | Confidence |
|----------|--------|------------|
| Are score–outcome associations stable across quarters? | [Pending execution] | Low–Medium |

---

## Stability Classification

Based on the observed variability, classify each outcome:

| Outcome | Classification | Evidence |
|---------|----------------|----------|
| `fwd_ret_3` | [Stable / Weakly Stable / Unstable / Regime-Fragile] | [brief] |
| `mfe_3` | [Stable / Weakly Stable / Unstable / Regime-Fragile] | [brief] |
| `mae_3` | [Stable / Weakly Stable / Unstable / Regime-Fragile] | [brief] |

### Classification Criteria

| Classification | Criteria |
|----------------|----------|
| **Stable** | Correlation range < 0.1, sign consistent, bucket pattern consistent |
| **Weakly Stable** | Correlation range 0.1–0.2, sign consistent, bucket pattern similar |
| **Unstable** | Correlation range > 0.2 OR sign inconsistent |
| **Regime-Fragile** | Clear pattern in some quarters, absent or reversed in others |

---

## Key Findings

### Finding 1: Correlation Variability

_[Pending execution: Document whether correlations vary meaningfully across quarters]_

**Evidence:** Quarterly correlations and stability metrics in [results.md](results.md)

**Observation:** [To be documented]

### Finding 2: Directional Consistency

_[Pending execution: Document whether correlation signs are consistent]_

**Evidence:** Sign consistency column in results

**Observation:** [To be documented]

### Finding 3: Bucket Pattern Persistence

_[Pending execution: Document whether bucket gradients persist]_

**Evidence:** Quarterly bucket summaries in [results.md](results.md)

**Observation:** [To be documented]

### Finding 4: Tail Behavior

_[Pending execution: Document whether top/bottom decile differences persist]_

**Evidence:** Tail comparison by quarter in [results.md](results.md)

**Observation:** [To be documented]

---

## Interpretation Framework

### If Stable

- Associations persist across all quarters with low variability
- Does NOT mean the score is useful
- Does NOT mean the score should be traded
- May still be spurious or economically insignificant

### If Weakly Stable

- Associations persist but with meaningful variability
- Suggests some regime sensitivity
- Caution warranted in any downstream use
- Expected outcome for simple scores

### If Unstable

- Associations vary substantially across quarters
- Sign flips or large magnitude changes observed
- Strong caution: full-sample results may be misleading
- Score–outcome relationship is time-dependent

### If Regime-Fragile

- Clear pattern in some periods, absent/reversed in others
- Suggests market regime dependency
- Full-sample statistics are unreliable summaries
- Any downstream use would require regime identification (NOT recommended)

---

## Warning if Structure is Time-Dependent

_[Pending execution: Add explicit warning if instability is found]_

> ⚠️ **WARNING:** If associations are unstable or regime-fragile, the full-sample results from `study_20260120_block_range_intensity_vs_outcomes` may not generalize. Downstream use of this score should account for temporal variability.

---

## Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Only 4 quarters | Limited statistical power for stability assessment | Future: longer history |
| Calendar quarters may not align with regimes | Real regime shifts may not match Q1/Q2/Q3/Q4 | Future: event-based slicing |
| Single instrument | Stability may differ for other pairs | Future: expand instruments |
| No regime labels | Cannot explain why instability occurs | Outside scope |

---

## What This Study Does NOT Conclude

- ❌ Stable associations are tradable
- ❌ Any quarter is "better" for the score
- ❌ Instability is a failure
- ❌ The score should be re-optimized per quarter
- ❌ Regime-dependent use is recommended

---

## Confidence Assessment

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Data quality | [Pending] | Per-quarter sample sizes |
| Methodology | Medium | Standard stability checks |
| Reproducibility | High | Fixed parameters, deterministic |
| Generalizability | Low | Single year, single instrument |

**Overall confidence:** Low–Medium

---

## Next Steps

### Recommended Follow-Up

1. **Expand time range:** Include 2024 or earlier if available
2. **Expand instruments:** Test stability for EURUSD, USDJPY
3. **Alternative slicing:** Monthly windows, rolling 3-month
4. **Document regime hypotheses:** If instability found, note potential drivers (non-predictive)

### NOT Recommended

- ❌ Selecting "stable" periods for trading
- ❌ Re-optimizing the score per quarter
- ❌ Treating stable quarters as evidence of edge
- ❌ Building regime-switching strategies

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Author | @ovc-research | 2026-01-20 |
| Reviewer | [pending] | — |
