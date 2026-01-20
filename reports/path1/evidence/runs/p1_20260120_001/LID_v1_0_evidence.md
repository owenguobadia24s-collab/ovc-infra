# LID-v1.0 Evidence Report

## Score Identity

| Attribute | Value |
|-----------|-------|
| Score Name | LID (Lid/Cap) |
| Version | v1.0 |
| Status | FROZEN |
| Source View | `derived.v_ovc_b_scores_lid_v1_0` |

## Data Scope

| Parameter | Value |
|-----------|-------|
| Run ID | _{to be filled}_ |
| Date Range | _{start}_ to _{end}_ |
| Symbol(s) | _{symbols}_ |
| Evidence View | `derived.v_path1_evidence_lid_v1_0` |
| Outcome Source | `derived.v_ovc_c_outcomes_v0_1` |
| Generated At | _{timestamp}_ |

---

## Distribution Summary: LID-v1.0

_Placeholder: Populate from `study_lid_v1_0_distribution.sql` Study 1_

| Statistic | Value |
|-----------|-------|
| N | |
| Mean | |
| Std Dev | |
| Min | |
| P25 | |
| P50 | |
| P75 | |
| Max | |

---

## Score Distribution by Outcome Category

_Placeholder: Populate from `study_lid_v1_0_distribution.sql` Study 2_

| Outcome Category | N | Mean Score | Median Score | Std Dev |
|------------------|---|------------|--------------|---------|
| | | | | |

---

## Outcome Frequency by Score Quantile

_Placeholder: Populate from `study_lid_v1_0_distribution.sql` Study 3_

| Quartile | Outcome Category | N | % Within Quartile |
|----------|------------------|---|-------------------|
| Q1 | | | |
| Q2 | | | |
| Q3 | | | |
| Q4 | | | |

---

## Outcome Statistics by Score Quantile

_Placeholder: Populate from `study_lid_v1_0_distribution.sql` Study 4_

| Quartile | N | Mean Outcome Ret | Median Outcome Ret | Std Dev |
|----------|---|------------------|---------------------|---------|
| Q1 | | | | |
| Q2 | | | | |
| Q3 | | | | |
| Q4 | | | | |

---

## Disclaimer

> **These observations describe co-occurrence patterns only.**
> **They do not imply causation or predictability.**

- The LID-v1.0 score is a descriptive measure of price block structure.
- Associations observed between LID values and outcomes are historical observations.
- No trading signals, thresholds, or decision rules should be derived from this report.
- This report is part of an observational evidence-building phase.

---

## Appendix: Study Queries Used

| Study | Source File |
|-------|-------------|
| Distribution Summary | `sql/path1/evidence/studies/study_lid_v1_0_distribution.sql` |
| Evidence View | `sql/path1/evidence/v_path1_evidence_lid_v1_0.sql` |
