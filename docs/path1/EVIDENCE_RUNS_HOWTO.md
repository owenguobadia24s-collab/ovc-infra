# Path 1 Evidence Runs — Operational How-To

**Version:** 1.1  
**Created:** 2026-01-20  
**Updated:** 2026-01-20  
**Scope:** End-to-end execution of Path 1 evidence studies

---

## 0. Deployment Order & Prerequisites

### 0.1 Full Deployment Chain (One-Time or After Schema Reset)

Deploy views in strict dependency order. Stop on first failure.

```powershell
# Step A: Apply DB patches (if needed for schema drift)
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql

# Step B: Deploy canonical C1/C2/C3 feature views
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_c1_features_v0_1.sql
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_c2_features_v0_1.sql
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_c3_features_v0_1.sql

# Step C: Deploy Option C outcomes view
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_c_outcomes_v0_1.sql

# Step D: Deploy Path 1 score views
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/path1/db_patches/patch_create_score_views_20260120.sql

# Step E: Deploy evidence join views
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/path1/db_patches/patch_create_evidence_views_20260120.sql
```

### 0.2 Verify Deployment

```powershell
psql $env:DATABASE_URL -c "SELECT table_name FROM information_schema.views WHERE table_schema='derived' ORDER BY 1;"
```

Expected views:
- `v_ovc_c1_features_v0_1`, `v_ovc_c2_features_v0_1`, `v_ovc_c3_features_v0_1`
- `v_ovc_c_outcomes_v0_1`
- `v_ovc_b_scores_dis_v1_1`, `v_ovc_b_scores_res_v1_0`, `v_ovc_b_scores_lid_v1_0`
- `v_path1_evidence_dis_v1_1`, `v_path1_evidence_res_v1_0`, `v_path1_evidence_lid_v1_0`

### 0.3 DB Patches Applied

| Patch | Purpose | Status |
|-------|---------|--------|
| `patch_align_c1_tf_column_20260120.sql` | Add `tf` column alias (C1 drift fix) | Applied 2026-01-20 |
| `patch_create_score_views_20260120.sql` | Create persistent score views | Applied 2026-01-20 |
| `patch_create_evidence_views_20260120.sql` | Create evidence join views | Applied 2026-01-20 |

---

## 1. Prerequisites

### 1.1 Environment Variables

Set `DATABASE_URL` (or `NEON_DSN`) to your Neon connection string:

```powershell
# PowerShell (Windows)
$env:DATABASE_URL = "postgresql://user:password@host/neondb?sslmode=require"
```

```bash
# Bash (Linux/macOS)
export DATABASE_URL="postgresql://user:password@host/neondb?sslmode=require"
```

### 1.2 Required Database Objects

The following views must exist before running studies:

| View | Purpose |
|------|---------|
| `derived.v_ovc_b_scores_dis_v1_1` | Frozen DIS-v1.1 score |
| `derived.v_ovc_b_scores_res_v1_0` | Frozen RES-v1.0 score |
| `derived.v_ovc_b_scores_lid_v1_0` | Frozen LID-v1.0 score |
| `derived.v_ovc_c_outcomes_v0_1` | Option C canonical outcomes |
| `derived.v_path1_evidence_dis_v1_1` | DIS evidence join view |
| `derived.v_path1_evidence_res_v1_0` | RES evidence join view |
| `derived.v_path1_evidence_lid_v1_0` | LID evidence join view |

---

## 2. Deploy Evidence Views (One-Time Setup)

> **Note:** If following Section 0 deployment chain, evidence views are already deployed via patches.

For standalone evidence view deployment (when score views already exist):

```powershell
psql $env:DATABASE_URL -f sql/path1/db_patches/patch_create_evidence_views_20260120.sql
```

These views are **read-only** and do not modify any score definitions.

---

## 3. Execute Evidence Studies

### 3.1 DIS-v1.1 Studies

```powershell
# Distribution study (4 queries)
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_dis_v1_1_distribution.sql
```

### 3.2 RES-v1.0 Studies

```powershell
# Distribution study
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_res_v1_0_distribution.sql
```

### 3.3 LID-v1.0 Studies

```powershell
# Distribution study
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_lid_v1_0_distribution.sql
```

### 3.4 Capture Output to File

Redirect query output to a file for archival:

```powershell
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_dis_v1_1_distribution.sql > outputs/dis_study1.txt
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_res_v1_0_distribution.sql > outputs/res_study1.txt
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_lid_v1_0_distribution.sql > outputs/lid_study1.txt
```

---

## 4. Create a Run Artifact

### 4.1 Prepare Run Directory

Create a new run folder using the run ID convention `{YYYYMMDD}-{SEQ}`:

```powershell
# Example: p1_20260120_001
mkdir reports/path1/evidence/runs/p1_20260120_001
mkdir reports/path1/evidence/runs/p1_20260120_001/outputs
```

### 4.2 Copy Templates

```powershell
cd reports/path1/evidence
copy EVIDENCE_RUN_TEMPLATE.md runs/p1_20260120_001/RUN.md
copy DIS_v1_1_evidence.md runs/p1_20260120_001/DIS_v1_1_evidence.md
copy RES_v1_0_evidence.md runs/p1_20260120_001/RES_v1_0_evidence.md
copy LID_v1_0_evidence.md runs/p1_20260120_001/LID_v1_0_evidence.md
```

### 4.3 Execute and Capture

From repo root:

```powershell
psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_dis_v1_1_distribution.sql > reports/path1/evidence/runs/p1_20260120_001/outputs/dis_distribution.txt

psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_res_v1_0_distribution.sql > reports/path1/evidence/runs/p1_20260120_001/outputs/res_distribution.txt

psql $env:DATABASE_URL -f sql/path1/evidence/studies/study_lid_v1_0_distribution.sql > reports/path1/evidence/runs/p1_20260120_001/outputs/lid_distribution.txt
```

### 4.4 Populate Report Documents

1. Open `runs/p1_20260120_001/RUN.md` and fill in metadata (run_id, date_range, symbols)
2. Open each score evidence file (DIS, RES, LID) and paste results from outputs into placeholders
3. Review and save

---

## 5. Run Directory Structure

Each completed run follows this structure:

```
reports/path1/evidence/runs/<run_id>/
├── RUN.md                    # Filled EVIDENCE_RUN_TEMPLATE
├── DIS_v1_1_evidence.md      # Populated DIS report
├── RES_v1_0_evidence.md      # Populated RES report
├── LID_v1_0_evidence.md      # Populated LID report
└── outputs/                  # Raw query outputs
    ├── dis_distribution.txt
    ├── res_distribution.txt
    └── lid_distribution.txt
```

---

## 6. Run ID Convention

Format: `p1_{YYYYMMDD}_{SEQ}`

| Component | Example | Description |
|-----------|---------|-------------|
| `p1` | `p1` | Path 1 prefix |
| `YYYYMMDD` | `20260120` | Run date (NY timezone) |
| `SEQ` | `001` | Sequential run number for the day |

Examples:
- `p1_20260120_001` — First run on 2026-01-20
- `p1_20260120_002` — Second run on 2026-01-20
- `p1_20260121_001` — First run on 2026-01-21

---

## 7. SQL File Reference

### Evidence Views (deploy once)

| File | Creates |
|------|---------|
| `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql` | `derived.v_path1_evidence_dis_v1_1` |
| `sql/path1/evidence/v_path1_evidence_res_v1_0.sql` | `derived.v_path1_evidence_res_v1_0` |
| `sql/path1/evidence/v_path1_evidence_lid_v1_0.sql` | `derived.v_path1_evidence_lid_v1_0` |

### Study SQL Files (run per study)

| File | Purpose |
|------|---------|
| `sql/path1/evidence/studies/study_dis_v1_1_distribution.sql` | DIS distributional analysis |
| `sql/path1/evidence/studies/study_res_v1_0_distribution.sql` | RES distributional analysis |
| `sql/path1/evidence/studies/study_lid_v1_0_distribution.sql` | LID distributional analysis |

---

## 8. Troubleshooting

| Issue | Fix |
|-------|-----|
| `psql: command not found` | Install PostgreSQL client or use full path |
| `relation does not exist` | Deploy prerequisite score/outcome views first |
| `permission denied` | Check DATABASE_URL credentials |
| `SSL required` | Add `?sslmode=require` to connection string |

---

## 9. Related Documents

| Document | Location |
|----------|----------|
| Run Conventions | [docs/path1/RUN_CONVENTIONS.md](RUN_CONVENTIONS.md) |
| Evidence Framework README | [reports/path1/evidence/README.md](../../reports/path1/evidence/README.md) |
| Path 1 Status | [docs/path1/OPTION_B_PATH1_STATUS.md](OPTION_B_PATH1_STATUS.md) |
| Run Template | [reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md](../../reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md) |

---

## 10. Governance Reminders

- **Do NOT modify** score SQL (DIS-v1.1, RES-v1.0, LID-v1.0)
- **Do NOT introduce** thresholds, signals, or decision logic
- **Do NOT interpret** results beyond observational description
- **All runs** produce observational outputs only
