# Path 1 Evidence Run: p1_20260120_001

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `p1_20260120_001` |
| `date_range_start` | `2024-01-08` |
| `date_range_end` | `2024-01-12` |
| `symbol(s)` | `GBPUSD` |
| `generated_at` | `2026-01-20T00:00:00Z` |
| `n_observations` | `48` |

### Note on Date Range

Original request was `2026-01-06` to `2026-01-10`, but that range contained 0 rows of data.
Substituted with closest equivalent 5-day weekday range with available data.

### Score Versions Used (Frozen)

| Score | Version | Status |
|-------|---------|--------|
| DIS | v1.1 | FROZEN |
| RES | v1.0 | FROZEN |
| LID | v1.0 | FROZEN |

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
| Count | 48 |
| Mean | 0.4654 |
| Std Dev | 0.3079 |
| Min | 0.0080 |
| P25 | 0.2128 |
| P50 (Median) | 0.4146 |
| P75 | 0.7554 |
| Max | 0.9455 |

### 1.2 RES-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 48 |
| Mean | 0.9366 |
| Std Dev | 0.5724 |
| Min | 0.2852 |
| P25 | 0.5703 |
| P50 (Median) | 0.8183 |
| P75 | 1.1003 |
| Max | 3.2442 |

### 1.3 LID-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 48 |
| Mean | 0.5110 |
| Std Dev | 0.2717 |
| Min | 0.0526 |
| P25 | 0.3137 |
| P50 (Median) | 0.4416 |
| P75 | 0.6903 |
| Max | 1.0000 |

---

## Section 2: Score by Outcome Category

### 2.1 DIS-v1.1 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 8 | 0.3181 | 0.2529 |
| FLAT | 33 | 0.4838 | 0.3094 |
| UP | 7 | 0.5472 | 0.3445 |

### 2.2 RES-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 8 | 0.9097 | 0.2676 |
| FLAT | 33 | 0.9614 | 0.6707 |
| UP | 7 | 0.8502 | 0.2657 |

### 2.3 LID-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 8 | 0.5428 | 0.2219 |
| FLAT | 33 | 0.4758 | 0.2850 |
| UP | 7 | 0.6402 | 0.2453 |

---

## Section 3: Outcome Frequency by Score Quartile

### 3.1 DIS-v1.1 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 25.00% | 66.67% | 8.33% |
| Q2 | 16.67% | 66.67% | 16.67% |
| Q3 | 25.00% | 66.67% | 8.33% |
| Q4 (high) | 0.00% | 75.00% | 25.00% |

### 3.2 RES-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 0.00% | 83.33% | 16.67% |
| Q2 | 33.33% | 58.33% | 8.33% |
| Q3 | 25.00% | 50.00% | 25.00% |
| Q4 (high) | 8.33% | 83.33% | 8.33% |

### 3.3 LID-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 8.33% | 91.67% | 0.00% |
| Q2 | 25.00% | 66.67% | 8.33% |
| Q3 | 25.00% | 50.00% | 25.00% |
| Q4 (high) | 8.33% | 66.67% | 25.00% |

---

## Section 4: Outcome Return Statistics by Score Quartile

### 4.1 DIS-v1.1 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 12 | -0.000458 | 0.001549 | 0.000055 |
| Q2 | 12 | 0.000214 | 0.001393 | 0.000181 |
| Q3 | 12 | -0.000257 | 0.001752 | -0.000004 |
| Q4 | 12 | 0.000432 | 0.000771 | 0.000169 |

### 4.2 RES-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 12 | 0.000049 | 0.000755 | 0.000055 |
| Q2 | 12 | -0.000114 | 0.001140 | 0.000091 |
| Q3 | 12 | 0.000027 | 0.002095 | 0.000216 |
| Q4 | 12 | -0.000032 | 0.001509 | 0.000252 |

### 4.3 LID-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 12 | -0.000424 | 0.001335 | -0.000169 |
| Q2 | 12 | -0.000123 | 0.001012 | 0.000287 |
| Q3 | 12 | 0.000184 | 0.002003 | 0.000298 |
| Q4 | 12 | 0.000294 | 0.001180 | 0.000173 |

---

## Artifacts

| File | Description |
|------|-------------|
| `outputs/study_dis_v1_1.txt` | Raw DIS-v1.1 study output |
| `outputs/study_res_v1_0.txt` | Raw RES-v1.0 study output |
| `outputs/study_lid_v1_0.txt` | Raw LID-v1.0 study output |

---

## Execution Log

```
Run executed: 2026-01-20
SQL sources: sql/path1/evidence/runs/p1_20260120_001/
Output location: reports/path1/evidence/runs/p1_20260120_001/outputs/
```
