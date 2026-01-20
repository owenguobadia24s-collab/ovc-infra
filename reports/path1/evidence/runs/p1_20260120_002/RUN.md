# Path 1 Evidence Run: p1_20260120_002

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `p1_20260120_002` |
| `date_range_requested` | `2024-01-15` to `2024-01-19` |
| `date_range_actual` | `2023-12-18` to `2023-12-22` |
| `symbol(s)` | `GBPUSD` |
| `generated_at` | `2026-01-20T00:00:00Z` |
| `n_observations` | `60` |

---

## Date Range Substitution

| Field | Value |
|-------|-------|
| Requested Range | `2024-01-15` to `2024-01-19` |
| Rows in Requested Range | `0` |
| Substituted Range | `2023-12-18` to `2023-12-22` |
| Rows in Substituted Range | `60` |
| Rationale | Original range had zero data. Substituted with nearest non-overlapping 5-day weekday range. Run 001 used `2024-01-08` to `2024-01-12`; this range is distinct. |

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
| Mean | 0.4344 |
| Std Dev | 0.2675 |
| Min | 0.0294 |
| P25 | 0.2104 |
| P50 (Median) | 0.3702 |
| P75 | 0.6567 |
| Max | 0.9255 |

### 1.2 RES-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 60 |
| Mean | 1.0217 |
| Std Dev | 0.5708 |
| Min | 0.2562 |
| P25 | 0.5868 |
| P50 (Median) | 0.8596 |
| P75 | 1.3421 |
| Max | 3.0830 |

### 1.3 LID-v1.0 Distribution

| Statistic | Value |
|-----------|-------|
| Count | 60 |
| Mean | 0.4758 |
| Std Dev | 0.3124 |
| Min | 0.0000 |
| P25 | 0.2185 |
| P50 (Median) | 0.4601 |
| P75 | 0.7300 |
| Max | 1.0000 |

---

## Section 2: Score by Outcome Category

### 2.1 DIS-v1.1 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 10 | 0.3283 | 0.2554 |
| FLAT | 41 | 0.4554 | 0.2739 |
| UP | 9 | 0.4568 | 0.2498 |

### 2.2 RES-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 10 | 1.1510 | 0.5506 |
| FLAT | 41 | 0.9238 | 0.4911 |
| UP | 9 | 1.3243 | 0.8263 |

### 2.3 LID-v1.0 by Outcome Category

| Outcome | n | Mean | Std Dev |
|---------|---|------|---------|
| DOWN | 10 | 0.5392 | 0.2296 |
| FLAT | 41 | 0.4693 | 0.3338 |
| UP | 9 | 0.4348 | 0.3101 |

---

## Section 3: Outcome Frequency by Score Quartile

### 3.1 DIS-v1.1 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 26.67% | 60.00% | 13.33% |
| Q2 | 20.00% | 60.00% | 20.00% |
| Q3 | 13.33% | 73.33% | 13.33% |
| Q4 (high) | 6.67% | 80.00% | 13.33% |

### 3.2 RES-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 6.67% | 80.00% | 13.33% |
| Q2 | 6.67% | 86.67% | 6.67% |
| Q3 | 40.00% | 33.33% | 26.67% |
| Q4 (high) | 13.33% | 73.33% | 13.33% |

### 3.3 LID-v1.0 Quartiles → Outcome Frequency

| Quartile | DOWN | FLAT | UP |
|----------|------|------|----|
| Q1 (low) | 6.67% | 80.00% | 13.33% |
| Q2 | 13.33% | 66.67% | 20.00% |
| Q3 | 33.33% | 53.33% | 13.33% |
| Q4 (high) | 13.33% | 73.33% | 13.33% |

---

## Section 4: Outcome Return Statistics by Score Quartile

### 4.1 DIS-v1.1 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | -0.000142 | 0.001494 | -0.000243 |
| Q2 | 15 | 0.000098 | 0.001907 | 0.000174 |
| Q3 | 15 | 0.000105 | 0.001015 | 0.000457 |
| Q4 | 15 | 0.000113 | 0.000664 | 0.000039 |

### 4.2 RES-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | -0.000047 | 0.001368 | 0.000158 |
| Q2 | 15 | 0.000052 | 0.001130 | -0.000071 |
| Q3 | 15 | 0.000110 | 0.001826 | -0.000243 |
| Q4 | 15 | 0.000059 | 0.000944 | 0.000236 |

### 4.3 LID-v1.0 Quartiles → Outcome Return

| Quartile | n | Mean Return | Std Dev | Median |
|----------|---|-------------|---------|--------|
| Q1 | 15 | 0.000183 | 0.000971 | 0.000457 |
| Q2 | 15 | 0.000334 | 0.001361 | 0.004032 |
| Q3 | 15 | -0.000279 | 0.001923 | -0.001498 |
| Q4 | 15 | -0.000065 | 0.000812 | 0.000000 |

---

## Commands Executed

```powershell
# Data availability check
psql $env:DATABASE_URL -c "SELECT COUNT(*) AS rows_in_range FROM derived.v_path1_evidence_dis_v1_1 WHERE sym = 'GBPUSD' AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2024-01-15' AND '2024-01-19';"
# Result: 0 rows

# Substitute range check
psql $env:DATABASE_URL -c "SELECT COUNT(*) AS rows_in_range FROM derived.v_path1_evidence_dis_v1_1 WHERE sym = 'GBPUSD' AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-12-18' AND '2023-12-22';"
# Result: 60 rows

# Execute DIS-v1.1 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_002/study_dis_v1_1.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_002/outputs/study_dis_v1_1.txt"

# Execute RES-v1.0 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_002/study_res_v1_0.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_002/outputs/study_res_v1_0.txt"

# Execute LID-v1.0 study
psql $env:DATABASE_URL -f "sql/path1/evidence/runs/p1_20260120_002/study_lid_v1_0.sql" | Tee-Object -FilePath "reports/path1/evidence/runs/p1_20260120_002/outputs/study_lid_v1_0.txt"
```

---

## Patches Applied

| Patch ID | Description | Status |
|----------|-------------|--------|
| N/A | No new patches required | Views already deployed from Run 001 |

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
| No score logic changes | ✅ PASS |
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
SQL sources: sql/path1/evidence/runs/p1_20260120_002/
Output location: reports/path1/evidence/runs/p1_20260120_002/outputs/
```
