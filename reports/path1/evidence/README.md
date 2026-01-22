# Path 1 Evidence-Building Framework

**Canonical Path 1 entrypoint:** see repo root `README.md` → “Path 1 (FROZEN) — Descriptive Score Research”.

## Overview

This directory contains the scaffolding for repeatable evidence runs that compare
**frozen Path 1 scores** against **realized outcomes** from Option C. All outputs
are observational and non-interpretive.

## Frozen Scores

| Score | Version | Status |
|-------|---------|--------|
| RES | v1.0 | FROZEN |
| LID | v1.0 | FROZEN |
| DIS | v1.1 | FROZEN |

**Why frozen scores matter**: Comparability across runs requires that score
definitions remain constant. If scores were modified between runs, differences
in observed associations could be due to score changes rather than data changes.
Frozen scores ensure that any variation in results is attributable to the data
scope alone.

---

## Running Evidence Studies

### Prerequisites

1. Evidence views must be deployed to the database:
   ```sql
   -- Deploy views (run once or after schema changes)
   \i sql/path1/evidence/v_path1_evidence_dis_v1_1.sql
   \i sql/path1/evidence/v_path1_evidence_res_v1_0.sql
   \i sql/path1/evidence/v_path1_evidence_lid_v1_0.sql
   ```

2. Underlying score views and Option C outcomes must exist:
   - `derived.v_ovc_b_scores_dis_v1_1`
   - `derived.v_ovc_b_scores_res_v1_0`
   - `derived.v_ovc_b_scores_lid_v1_0`
   - `derived.v_ovc_c_outcomes_v0_1`

### Running a Study

Execute the study SQL files against your database:

```bash
# DIS-v1.1 distributional study
psql $DATABASE_URL -f sql/path1/evidence/studies/study_dis_v1_1_distribution.sql

# RES-v1.0 distributional study
psql $DATABASE_URL -f sql/path1/evidence/studies/study_res_v1_0_distribution.sql

# LID-v1.0 distributional study
psql $DATABASE_URL -f sql/path1/evidence/studies/study_lid_v1_0_distribution.sql
```

### Filtering by Date Range

Add WHERE clauses to study queries to scope to specific date ranges:

```sql
-- Example: Add to any study query
WHERE bar_close_ms >= EXTRACT(EPOCH FROM '2026-01-01'::date) * 1000
  AND bar_close_ms <  EXTRACT(EPOCH FROM '2026-01-15'::date) * 1000
```

### Filtering by Symbol

```sql
-- Example: Add to any study query
WHERE sym IN ('GBPUSD', 'EURUSD')
```

---

## Comparing Runs Across Time

### Procedure

1. **Create a new run**: Copy `EVIDENCE_RUN_TEMPLATE.md` to a dated file:
   ```
   cp EVIDENCE_RUN_TEMPLATE.md runs/RUN_20260120_001.md
   ```

2. **Fill metadata**: Update run_id, date_range, symbols in the new file.

3. **Execute studies**: Run SQL studies with appropriate date filters.

4. **Populate tables**: Copy study outputs into the report placeholders.

5. **Archive**: Keep completed runs in `reports/path1/evidence/runs/` for
   longitudinal comparison.

### What to Compare

When comparing runs:

- **Distribution shifts**: Did score distributions change across date ranges?
- **Association stability**: Are co-occurrence patterns consistent or variable?
- **Data quality**: Are there coverage gaps or missing outcomes in some periods?

### What NOT to Conclude

- Do not conclude that a score "predicts" outcomes.
- Do not derive thresholds or trading rules from observations.
- Do not claim causation from correlation.

---

## Directory Structure

```
reports/path1/evidence/
├── README.md                      # This file
├── EVIDENCE_RUN_TEMPLATE.md       # Template for new runs
└── runs/                          # Archived completed runs
    └── <run_id>/                  # e.g., p1_20260120_001
        ├── RUN.md
        ├── DIS_v1_1_evidence.md
        ├── RES_v1_0_evidence.md
        ├── LID_v1_0_evidence.md
        └── outputs/

sql/path1/evidence/
├── v_path1_evidence_dis_v1_1.sql  # DIS evidence view
├── v_path1_evidence_res_v1_0.sql  # RES evidence view
├── v_path1_evidence_lid_v1_0.sql  # LID evidence view
└── studies/
    ├── study_dis_v1_1_distribution.sql
    ├── study_res_v1_0_distribution.sql
    └── study_lid_v1_0_distribution.sql
```

---

## Operational Guide

For step-by-step execution instructions, see:  
**[docs/history/path1/EVIDENCE_RUNS_HOWTO.md](../../../docs/history/path1/EVIDENCE_RUNS_HOWTO.md)**

---

## Governance Reminders

1. **No score modifications**: Score SQL is frozen. Do not alter definitions.
2. **No threshold introduction**: Use quantiles for binning, not fixed values.
3. **No signal framing**: Scores describe structure, they do not predict.
4. **Associative language only**: "co-occurs with" not "predicts" or "causes".
5. **Read-only views**: Evidence views join data, they do not transform it.

---

## Out of Scope

The following are explicitly **out of scope** for this evidence-building phase:

- Interpretation of results
- Decision logic or trading rules
- Threshold optimization
- Signal generation
- Backtesting or simulation
- Recommendations or conclusions

This phase is strictly observational.
