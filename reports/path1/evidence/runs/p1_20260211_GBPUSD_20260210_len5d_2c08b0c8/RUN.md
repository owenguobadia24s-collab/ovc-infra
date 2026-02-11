# Path 1 Evidence Run Template

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `p1_20260211_GBPUSD_20260210_len5d_2c08b0c8` |
| `date_range_start` | `2026-02-06` |
| `date_range_end` | `2026-02-10` |
| `symbol(s)` | `GBPUSD` |
| `generated_at` | `2026-02-11T05:12:51Z` |

### Score Versions Used (Frozen)

| Score | Version | Status |
|-------|---------|--------|
| RES | v1.0 | FROZEN |
| LID | v1.0 | FROZEN |
| DIS | v1.1 | FROZEN |

### Outcome Source

- View: `derived.v_ovc_c_outcomes_v0_1`
- Schema: Option C canonical outcomes

---

## Invariants Reminder

> **CRITICAL**: The following invariants apply to all observations in this run.

1. **Association ≠ Predictability**  
   Co-occurrence patterns observed between scores and outcomes do not imply
   that scores predict outcomes. Correlation is not causation.

2. **Scores Are Descriptive, Frozen**  
   Score definitions are locked at the versions specified above. They describe
   structural characteristics of price blocks. They are not signals.

3. **Observations Are Non-Interpretive**  
   All summaries in this report describe what occurred in the data. They do
   not prescribe actions, imply trading logic, or recommend thresholds.

---

## Section 1: Score Distributions

### 1.1 DIS-v1.1 Distribution

| Statistic | Value |
|-----------|-------|
| Count | |
| Mean | |
| Std Dev | |
| Min | |
| P25 | |
| P50 (Median) | |
| P75 | |
| Max | |

### 1.2 RES-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | |
| Mean | |
| Std Dev | |
| Min | |
| P25 | |
| P50 (Median) | |
| P75 | |
| Max | |

### 1.3 LID-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | |
| Mean | |
| Std Dev | |
| Min | |
| P25 | |
| P50 (Median) | |
| P75 | |
| Max | |

---

## Section 2: Outcome Distributions

### 2.1 Outcome Category Frequencies

| Outcome Category | Count | Percentage |
|------------------|-------|------------|
| | | |

### 2.2 Outcome Value Summary

| Statistic | Value |
|-----------|-------|
| Count | |
| Mean | |
| Std Dev | |
| Min | |
| P25 | |
| P50 (Median) | |
| P75 | |
| Max | |

---

## Section 3: Joint Observations

> **Note**: All observations below describe co-occurrence patterns only.
> They do not imply causation or predictability.

### 3.1 Score Distribution by Outcome Category

_Placeholder for tabular summary showing how score values distributed
across different outcome categories._

### 3.2 Outcome Frequency by Score Quantile

_Placeholder for tabular summary showing outcome category frequencies
within each score quantile (e.g., Q1, Q2, Q3, Q4)._

### 3.3 Summary Statistics by Score Quantile

_Placeholder for outcome value statistics (mean, median, std) within
each score quantile._

---

## Disclaimer

> These observations describe co-occurrence patterns only.
> They do not imply causation or predictability.
> No trading decisions, thresholds, or signals should be derived from this report.

---

## Appendix: Data Quality Notes

| Check | Status | Notes |
|-------|--------|-------|
| Missing scores | | |
| Missing outcomes | | |
| Join coverage | | |
| Date range completeness | | |

---

## Artifacts Generated

| File | Description |
|------|-------------|
| `outputs/study_dis_v1_1.txt` | Raw DIS-v1.1 study output |
| `outputs/study_res_v1_0.txt` | Raw RES-v1.0 study output |
| `outputs/study_lid_v1_0.txt` | Raw LID-v1.0 study output |
| `DIS_v1_1_evidence.md` | DIS-v1.1 evidence report |
| `RES_v1_0_evidence.md` | RES-v1.0 evidence report |
| `LID_v1_0_evidence.md` | LID-v1.0 evidence report |
