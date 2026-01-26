# Workflow Operating Loop v0.1

> **Single canonical operating loop for OVC infrastructure.**

## The Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     OVC OPERATING LOOP                          │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │  INGEST  │ -> │ VALIDATE │ -> │ EVIDENCE │ -> │  LEDGER  │
  │ backfill │    │  range   │    │  studies │    │  commit  │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
       │               │               │               │
       v               v               v               v
   [Database]      [Database]    [Repo Files]    [Git Main]
   writes only    reads only     generated       append-only
```

## Stages

### 1. INGEST (Backfill)

**Workflow**: `backfill_then_validate.yml` or `backfill_m15.yml`

- Fetches data from OANDA API
- Writes to Neon PostgreSQL database
- Checkpointed: resumes from last successful bar
- **Output**: Database rows (no repo changes)
- **Persistence**: Database writes are idempotent (upsert)

### 2. VALIDATE

**Workflow**: `backfill_then_validate.yml` (Step 2-5)

- Compares database facts against tape (OANDA CSV)
- Computes derived features (L1, L2)
- Validates derived features against expectations
- **Output**: Validation reports (artifacts only)
- **Persistence**: Artifacts-only (ephemeral diagnostics)

### 3. EVIDENCE

**Workflow**: `path1_evidence.yml`

- Runs SQL studies against frozen score views
- Generates markdown evidence reports
- Creates per-run folder structure
- **Output**:
  - `reports/path1/evidence/runs/{run_id}/RUN.md`
  - `reports/path1/evidence/runs/{run_id}/*.md`
  - `reports/path1/evidence/runs/{run_id}/outputs/*.txt`
  - `sql/path1/evidence/runs/{run_id}/*.sql`
- **Persistence**: Files staged for ledger commit

### 4. LEDGER

**Workflow**: `path1_evidence.yml` (final steps)

- Updates `reports/path1/evidence/INDEX.md`
- Commits all generated files
- Pushes directly to `main` branch
- **Output**: Git commit with evidence run
- **Persistence**: Append-only ledger (never delete runs)

---

## Key Principles

### Append-Only Ledger

The evidence ledger is **append-only**:

```
reports/path1/evidence/
├── INDEX.md              # Table of all runs (append new rows)
├── README.md             # Static documentation
├── EVIDENCE_RUN_TEMPLATE.md
└── runs/
    ├── p1_20250120_GBPUSD_20250115_len5d_abc123/
    │   ├── RUN.md
    │   ├── DIS_v1_1_evidence.md
    │   ├── RES_v1_0_evidence.md
    │   ├── LID_v1_0_evidence.md
    │   ├── meta.json
    │   └── outputs/
    │       ├── study_dis_v1_1.txt
    │       ├── study_res_v1_0.txt
    │       └── study_lid_v1_0.txt
    └── p1_20250121_GBPUSD_20250120_len5d_def456/
        └── ...
```

**Rules**:
- New runs create new folders — never overwrite
- INDEX.md gains rows — never removes them
- Run IDs are deterministic (symbol + dates + git SHA + template version)
- Duplicate run attempts fail fast (folder already exists)

### No Queue Mutation

**Banned pattern**:
```yaml
# WRONG: Queue as mutable state
- read queue.json
- pop item from queue
- process item
- write queue.json back
```

**Correct pattern**:
```yaml
# RIGHT: Date range as input, run_id as output
- accept date range inputs
- generate deterministic run_id
- create run folder (fail if exists)
- write outputs
- commit (append-only)
```

### Expected Outputs Enforcement

Every ledger-writing workflow MUST verify outputs before commit:

```yaml
- name: Stage and commit results
  run: |
    git add "reports/path1/evidence/INDEX.md"
    git add "reports/path1/evidence/runs/${RUN_ID}"

    if git diff --cached --quiet; then
      echo "ERROR: No staged changes; failing to avoid false green"
      exit 1
    fi

    git commit -m "path1 evidence: ${RUN_ID}"
```

### Persistence Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **PR+merge** | Create branch, open PR, merge | Complex changes requiring review |
| **Direct-push** | Commit directly to main | Automated ledger appends |
| **Artifacts-only** | Upload to GitHub Artifacts | Ephemeral diagnostics, logs |
| **Database-only** | Write to Neon PostgreSQL | Backfill/ingest operations |

Current workflows use:
- `path1_evidence.yml`: Direct-push (append-only ledger)
- `backfill_then_validate.yml`: Artifacts-only + Database
- `backfill_m15.yml`: Artifacts-only + Database
- `ovc_option_c_schedule.yml`: Artifacts-only
- `path1_replay_verify.yml`: Artifacts-only

---

## Output Landing Zones

| Path | Purpose | Written By |
|------|---------|------------|
| `reports/path1/evidence/` | Evidence ledger | `path1_evidence.yml` |
| `sql/path1/evidence/` | SQL artifacts | `path1_evidence.yml` |
| `reports/runs/` | Ephemeral run logs | Multiple (artifacts) |
| `artifacts/` | Temp artifacts | Multiple (artifacts) |

---

## Workflow Execution Order

For a complete data refresh cycle:

1. **`backfill_then_validate.yml`** — Ingest + validate date range
2. **`path1_evidence.yml`** — Generate evidence studies for range
3. **`path1_replay_verify.yml`** — Verify structural integrity (optional)
4. **`ovc_option_c_schedule.yml`** — Run Option C spotchecks (daily)

These can run independently — each is idempotent given the same inputs.
