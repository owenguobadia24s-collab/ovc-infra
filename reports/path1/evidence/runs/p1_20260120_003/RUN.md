# Path 1 Evidence Run: p1_20260120_003

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `p1_20260120_003` |
| `date_range_requested` | `2023-12-11` to `2023-12-15` |
| `date_range_actual` | `2023-12-11` to `2023-12-15` |
| `symbol(s)` | `GBPUSD` |
| `generated_at` | `2026-01-20T00:00:00Z` |
| `n_observations` | `60` |

---

## Date Range Verification

| Field | Value |
|-------|-------|
| Requested Range | `2023-12-11` to `2023-12-15` |
| Rows in Requested Range | `60` |
| Substitution Required | `No` |
| Non-Overlap Confirmation | ✅ Does not overlap Run 001 (2024-01-08 to 2024-01-12) |
| Non-Overlap Confirmation | ✅ Does not overlap Run 002 (2023-12-18 to 2023-12-22) |

---

## Score Versions Used (Frozen)

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
| Count | 60 |
| Mean | 0.4795 |
| Std Dev | 0.2687 |
| Min | 0.0189 |
| P25 | 0.2927 |
| P50 (Median) | 0.4906 |
| P75 | 0.6666 |
| Max | 0.9917 |

### 1.2 RES-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 60 |
| Mean | 1.1773 |
| Std Dev | 0.8727 |
| Min | 0.2604 |
| P25 | 0.6375 |
| P50 (Median) | 0.9939 |
| P75 | 1.4423 |
| Max | 5.4304 |

### 1.3 LID-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 60 |
| Mean | 0.5111 |
| Std Dev | 0.3069 |
| Min | 0.0000 |
| P25 | 0.2846 |
| P50 (Median) | 0.5030 |
| P75 | 0.7828 |
| Max | 1.0000 |

---

## Section 2: Score by Outcome Category

### 2.1 DIS-v1.1 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 12 | 0.3626 | 0.1392 |
| FLAT | 37 | 0.5273 | 0.2929 |
| UP | 11 | 0.4463 | 0.2644 |

### 2.2 RES-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 12 | 1.2109 | 0.5298 |
| FLAT | 37 | 1.0808 | 0.9348 |
| UP | 11 | 1.4656 | 0.9546 |

### 2.3 LID-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 12 | 0.4579 | 0.3042 |
| FLAT | 37 | 0.5259 | 0.2951 |
| UP | 11 | 0.5193 | 0.3688 |

---

## Section 3: Outcome Frequency by Score Quartile

### 3.1 DIS-v1.1 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 20.00% | 60.00% | 20.00% |
| Q2 | 46.67% | 40.00% | 13.33% |
| Q3 | 13.33% | 53.33% | 33.33% |
| Q4 (high) | 0.00% | 93.33% | 6.67% |

### 3.2 RES-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 13.33% | 73.33% | 13.33% |
| Q2 | 13.33% | 73.33% | 13.33% |
| Q3 | 26.67% | 46.67% | 26.67% |
| Q4 (high) | 26.67% | 53.33% | 20.00% |

### 3.3 LID-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 20.00% | 53.33% | 26.67% |
| Q2 | 26.67% | 73.33% | 0.00% |
| Q3 | 20.00% | 53.33% | 26.67% |
| Q4 (high) | 13.33% | 66.67% | 20.00% |

---

## Section 4: Outcome Return Statistics by Score Quartile

### 4.1 DIS-v1.1 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | -0.000049 | 0.002079 | -0.000112 |
| Q2 | 15 | -0.000272 | 0.001671 | -0.000775 |
| Q3 | 15 | 0.000952 | 0.002672 | 0.000382 |
| Q4 | 15 | -0.000005 | 0.000884 | -0.000040 |

### 4.2 RES-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | -0.000171 | 0.001078 | -0.000112 |
| Q2 | 15 | 0.000233 | 0.001191 | 0.000501 |
| Q3 | 15 | 0.000660 | 0.003358 | 0.000048 |
| Q4 | 15 | -0.000096 | 0.001289 | -0.000347 |

### 4.3 LID-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | 0.000352 | 0.001955 | -0.000040 |
| Q2 | 15 | -0.000689 | 0.001468 | -0.000541 |
| Q3 | 15 | 0.000719 | 0.002717 | 0.000048 |
| Q4 | 15 | 0.000244 | 0.001211 | 0.000494 |

---

## Commands Executed

```powershell
# Data availability check
psql $env:DATABASE_URL -c "SELECT COUNT(*) AS rows_in_range FROM derived.v_path1_evidence_dis_v1_1 WHERE sym = 'GBPUSD' AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-12-11' AND '2023-12-15';"
# Result: 60 rows (no substitution required)

# Execute DIS-v1.1 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_003/study_dis_v1_1.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_003/outputs/study_dis_v1_1.txt"

# Execute RES-v1.0 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_003/study_res_v1_0.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_003/outputs/study_res_v1_0.txt"

# Execute LID-v1.0 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_003/study_lid_v1_0.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_003/outputs/study_lid_v1_0.txt"
```

---

## Patches Applied

| Patch ID | Description | Status |
|----------|-------------|--------|
| N/A | No new patches required | Views already deployed from Run 001/002 |

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

---

## Verification Results

| Check | Status |
|-------|--------|
| No Option B modifications | ✅ PASS |
| No SCORE_LIBRARY_v1 changes | ✅ PASS |
| No new scores added | ✅ PASS |
| No interpretation layers | ✅ PASS |
| Outputs are observational only | ✅ PASS |
| Frozen score versions used | ✅ PASS |
| Evidence views read-only | ✅ PASS |

---

## Governance Confirmation

- ✅ No Option B views, tables, or contracts were modified
- ✅ SCORE_LIBRARY_v1 unchanged (DIS-v1.1, RES-v1.0, LID-v1.0 remain frozen)
- ✅ No new scores added
- ✅ No interpretation layers added
- ✅ No automation escalation
- ✅ All outputs are observational summaries only

---

## Execution Log

```
Run executed: 2026-01-20
SQL sources: sql/path1/evidence/runs/p1_20260120_003/
Output location: reports/path1/evidence/runs/p1_20260120_003/outputs/
```
