# Path 1 Evidence Runs — Operational How-To

**STATUS: HISTORICAL (REFERENCE ONLY)**  
This document reflects the operational guide at the time it was written.  
Current execution ergonomics are defined in `PATH1_EXECUTION_MODEL.md`.  
Canonical facts remain in `reports/path1/evidence/INDEX.md`.

**Version:** 1.1  
**Created:** 2026-01-20  
**Updated:** 2026-01-20  
**Scope:** End-to-end execution of Path 1 evidence studies

---

## Path1 Run Observability (Non-Canonical)

Each Path1 execution emits a **non-canonical run summary** for human inspection.

- Summary file: `artifacts/path1_summary.json`
- CI rendering: GitHub Actions → `$GITHUB_STEP_SUMMARY`

The summary includes:
- Run ID
- Date range
- Rows processed
- Outcome (`EXECUTED` or `SKIPPED`)
- Commit SHA (`N/A` if no commit occurred)

Important invariants:
- **No-op is success**: a run that produces no new evidence exits `0`, commits nothing, and still emits a summary.
- The **canonical ledger** remains:
  - `reports/path1/evidence/INDEX.md`
  - `reports/path1/evidence/runs/<run_id>/`
- `$GITHUB_STEP_SUMMARY` and `path1_summary.json` are **observational only** and must not be treated as sources of truth.

For authoritative state, always inspect the ledger, not the summary.

## 0. Deployment Order & Prerequisites

### 0.1 Full Deployment Chain (One-Time or After Schema Reset)

Deploy views in strict dependency order. Stop on first failure.

```powershell
# Step A: Apply DB patches (if needed for schema drift)
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql

# Step B: Deploy canonical L1/L2/L3 feature views
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_l1_features_v0_1.sql
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_l2_features_v0_1.sql
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f sql/derived/v_ovc_l3_features_v0_1.sql

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
- `v_ovc_l1_features_v0_1`, `v_ovc_l2_features_v0_1`, `v_ovc_l3_features_v0_1`
- `v_ovc_c_outcomes_v0_1`
- `v_ovc_b_scores_dis_v1_1`, `v_ovc_b_scores_res_v1_0`, `v_ovc_b_scores_lid_v1_0`
- `v_path1_evidence_dis_v1_1`, `v_path1_evidence_res_v1_0`, `v_path1_evidence_lid_v1_0`

### 0.3 DB Patches Applied

| Patch | Purpose | Status |
|-------|---------|--------|
| `patch_align_c1_tf_column_20260120.sql` | Add `tf` column alias (L1 drift fix) | Applied 2026-01-20 |
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
| Run Conventions | [docs/history/path1/RUN_CONVENTIONS.md](RUN_CONVENTIONS.md) |
| Evidence Framework README | [reports/path1/evidence/README.md](../../reports/path1/evidence/README.md) |
| Path 1 Status | [docs/history/path1/OPTION_B_PATH1_STATUS.md](OPTION_B_PATH1_STATUS.md) |
| Run Template | [reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md](../../reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md) |

---

## 10. Governance Reminders

- **Do NOT modify** score SQL (DIS-v1.1, RES-v1.0, LID-v1.0)
- **Do NOT introduce** thresholds, signals, or decision logic
- **Do NOT interpret** results beyond observational description
- **All runs** produce observational outputs only

---

## 11. Automated Evidence Runs (GitHub Action)

### 11.1 Overview

The `.github/workflows/path1_evidence_queue.yml` workflow enables on-demand execution of Path 1 Evidence runs from a queued CSV file. It replicates the exact behavior of manual Runs 001-003.

**Key Features:**
- On-demand execution via `workflow_dispatch`
- Queue-based batch processing
- Automatic date range substitution (when requested range has no data)
- Artifact upload and optional branch commit
- Never auto-merges (human review required)

### 11.2 Queue File Format

Queue file: `reports/path1/evidence/RUN_QUEUE.csv`

```csv
run_id,symbol,date_start,date_end
p1_20260121_001,GBPUSD,2023-11-27,2023-12-01
p1_20260121_002,GBPUSD,2023-11-20,2023-11-24
p1_20260121_003,GBPUSD,2023-11-13,2023-11-17
```

| Column | Description |
|--------|-------------|
| `run_id` | Unique identifier (`p1_YYYYMMDD_SEQ`) |
| `symbol` | Trading pair (e.g., `GBPUSD`) |
| `date_start` | Requested start date (`YYYY-MM-DD`) |
| `date_end` | Requested end date (`YYYY-MM-DD`) |

**Note:** Lines starting with `#` are comments and ignored.

### 11.3 Workflow Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `queue_path` | `reports/path1/evidence/RUN_QUEUE.csv` | Path to queue CSV |
| `max_runs` | `10` | Maximum runs to execute |
| `run_id` | *(empty)* | Filter to single run_id (optional) |
| `commit_results` | `true` | Commit results to new branch |
| `branch_name` | *(auto)* | Custom branch name (default: `evidence-run-{timestamp}`) |
| `dry_run` | `false` | Validate without executing |

### 11.4 Required Secrets

Configure these in GitHub repository settings → Secrets:

| Secret | Purpose |
|--------|---------|
| `DATABASE_URL` or `NEON_DSN` | Neon PostgreSQL connection string |

### 11.5 Running the Workflow

#### Via GitHub UI

1. Go to **Actions** → **Path 1 Evidence Queue Runner**
2. Click **Run workflow**
3. Configure inputs
4. Click **Run workflow**

#### Via GitHub CLI

```bash
# Execute all queued runs
gh workflow run path1_evidence_queue.yml

# Execute specific run_id only
gh workflow run path1_evidence_queue.yml -f run_id=p1_20260121_001

# Dry run (validate only)
gh workflow run path1_evidence_queue.yml -f dry_run=true

# Custom branch name
gh workflow run path1_evidence_queue.yml -f branch_name=evidence-batch-2026-01-21
```

### 11.6 Output Artifacts

The workflow generates:

| Artifact | Location |
|----------|----------|
| SQL wrappers | `sql/path1/evidence/runs/{run_id}/` |
| Raw outputs | `reports/path1/evidence/runs/{run_id}/outputs/` |
| Evidence reports | `reports/path1/evidence/runs/{run_id}/*.md` |
| Updated index | `reports/path1/evidence/INDEX.md` |

Artifacts are uploaded to GitHub Actions and optionally committed to a new branch.

### 11.7 Post-Workflow Steps

1. **Review** the generated branch or downloaded artifacts
2. **Create PR** to merge into main:
   ```bash
   gh pr create --base main --head evidence-run-{timestamp} --title "Path 1 Evidence Runs"
   ```
3. **Manual merge** after human review (never auto-merge)
4. **Clear queue** by removing executed entries from `RUN_QUEUE.csv`

### 11.8 Date Range Substitution

If a requested date range has zero rows, the runner automatically:
1. Searches backwards in 7-day increments
2. Finds nearest 5-weekday range with data
3. Avoids overlap with existing runs in INDEX.md
4. Documents substitution in RUN.md

### 11.9 Local Testing

Run the queue locally before using the GitHub Action:

```powershell
# Dry run (validate only)
python scripts/path1/run_evidence_queue.py --dry-run

# Execute single run
python scripts/path1/run_evidence_queue.py --run-id p1_20260121_001

# Execute all queued (max 3)
python scripts/path1/run_evidence_queue.py --max-runs 3
```

### 11.10 Troubleshooting

| Issue | Fix |
|-------|-----|
| Queue file not found | Check `queue_path` input matches actual path |
| Database connection failed | Verify `DATABASE_URL`/`NEON_DSN` secret is set |
| No substitute range found | Verify data exists in evidence views |
| Branch already exists | Use unique `branch_name` or delete existing branch |
