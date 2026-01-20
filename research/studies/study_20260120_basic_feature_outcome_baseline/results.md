# Study Results

> ⚠️ **NON-CANONICAL** — This study is downstream research only.  
> **NO FEEDBACK INTO CANONICAL** — Findings do not alter Option B/C definitions.

## Summary Statistics

### Sample Overview

| Metric | Value |
|--------|-------|
| Total observations | [N] |
| Instrument | GBPUSD |
| Time span | 2025-01-01 to 2026-01-01 |
| Missing data (join failures) | [count or %] |
| Observations after join | [N_joined] |

### Feature Distributions

| Feature | N | Mean | Std | Min | P25 | P50 | P75 | Max |
|---------|---|------|-----|-----|-----|-----|-----|-----|
| `rng` | | | | | | | | |
| `body` | | | | | | | | |

### Direction Distribution

| `dir` | Count | Percentage |
|-------|-------|------------|
| -1 (down) | | |
| 0 (doji) | | |
| 1 (up) | | |

### Outcome Distributions

| Outcome | N | Mean | Std | Min | P25 | P50 | P75 | Max |
|---------|---|------|-----|-----|-----|-----|-----|-----|
| `fwd_ret_3` | | | | | | | | |
| `mfe_3` | | | | | | | | |
| `mae_3` | | | | | | | | |

---

## Primary Results

### Correlation Matrix (Features × Outcomes)

| Feature | `fwd_ret_3` | `mfe_3` | `mae_3` |
|---------|-------------|---------|---------|
| `rng` | | | |
| `body` | | | |

**Interpretation guide:**
- |r| < 0.1: Negligible
- 0.1 ≤ |r| < 0.3: Weak
- 0.3 ≤ |r| < 0.5: Moderate
- |r| ≥ 0.5: Strong

### Outcomes by Direction

| `dir` | N | Mean `fwd_ret_3` | Std `fwd_ret_3` | Mean `mfe_3` | Mean `mae_3` |
|-------|---|------------------|-----------------|--------------|--------------|
| -1 (down) | | | | | |
| 0 (doji) | | | | | |
| 1 (up) | | | | | |

---

## Secondary Results

### Distribution Shape Notes

| Variable | Skewness | Kurtosis | Notes |
|----------|----------|----------|-------|
| `rng` | | | [e.g., right-skewed, positive values only] |
| `body` | | | |
| `fwd_ret_3` | | | [e.g., approximately symmetric] |
| `mfe_3` | | | [e.g., positive values only] |
| `mae_3` | | | [e.g., negative values only] |

---

## Figures

### Figure 1: Feature Distributions

_[Placeholder: Histograms of `rng` and `body`]_

### Figure 2: Outcome Distributions

_[Placeholder: Histograms of `fwd_ret_3`, `mfe_3`, `mae_3`]_

### Figure 3: Feature vs Outcome Scatter

_[Placeholder: Scatter plots of `rng` vs `fwd_ret_3`, `body` vs `fwd_ret_3`]_

---

## Raw Output Location

| Output | Path | Status |
|--------|------|--------|
| Summary table | `research/outputs/study_20260120_basic_feature_outcome_baseline/summary.csv` | Not yet created |
| Correlation matrix | `research/outputs/study_20260120_basic_feature_outcome_baseline/correlations.csv` | Not yet created |
| Figures | `research/outputs/study_20260120_basic_feature_outcome_baseline/figures/` | Not yet created |

---

## Data Quality Notes

- [ ] No unexpected NULLs in results
- [ ] Results consistent across multiple runs
- [ ] Sample sizes adequate for correlation estimates (N > 500)
- [ ] Join match rate documented

---

## Execution Log

| Step | Timestamp | Notes |
|------|-----------|-------|
| Query executed | [pending] | |
| Summary computed | [pending] | |
| Correlations computed | [pending] | |
| Results documented | [pending] | |
