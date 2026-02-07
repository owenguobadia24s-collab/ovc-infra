# OVC Operating Base

> **Version:** 0.1
> **Last Updated:** 2026-01-20
> **Status:** ACTIVE
> **Purpose:** Enable a new AI agent to become productive in the OVC codebase immediately.

---

## 0. TL;DR (60 seconds)

**What this repo is:**
OVC (Option Validation Chain) is a TradingView-driven market observation pipeline that captures 2-hour OHLC block data from forex markets (currently GBPUSD) and stores it in Neon Postgres for deterministic analysis and replay.

**What problems it solves:**
1. Reliable ingestion of TradingView alert payloads via Cloudflare Worker
2. Historical backfill from OANDA API for complete coverage
3. Deterministic computation of derived features (C1/C2/C3 layers)
4. Forward-looking outcome measurement (Option C) with hit rate tracking
5. Immutable, versioned truth layers that prevent self-deception in trading research

**What "success" looks like:**
- All 12 daily 2H blocks (A-L) for GBPUSD are captured without gaps
- Validation passes: facts match tape, derived features are consistent
- Option C outcomes compute correctly for historical analysis
- Run artifacts document every pipeline execution with evidence

---

## 1. System Overview (Big Picture)

### Component Diagram

```
┌─────────────────────────────┐
│     TradingView Pine        │
│   (pine/OVC_v0_1.pine)      │
│   Emits MIN export string   │
└─────────────┬───────────────┘
              │ POST /tv or /tv_secure
              ▼
┌─────────────────────────────┐       ┌──────────────────────────────┐
│   Cloudflare Worker         │       │   Cloudflare R2              │
│   (infra/ovc-webhook)       ├──────►│   ovc-raw-events bucket      │
│   - Validates MIN contract  │       │   (raw payload archive)      │
│   - Upserts to Neon         │       └──────────────────────────────┘
└─────────────┬───────────────┘
              │ INSERT/UPSERT
              ▼
┌─────────────────────────────┐
│   Neon Postgres             │
│   ovc.ovc_blocks_v01_1_min  │ ◄──── Primary canonical table
│   (B-Layer: LOCKED)         │       (PK: block_id)
└─────────────┬───────────────┘
              │
      ┌───────┴───────┐
      ▼               ▼
┌───────────┐   ┌───────────────────────┐
│  Option B │   │  Option C             │
│  C1/C2/C3 │   │  derived.ovc_outcomes │
│  Features │   │  Forward returns, MFE │
└───────────┘   │  MAE, hit rates       │
                └───────────────────────┘

Parallel ingest path:
┌─────────────────────────────┐
│   OANDA API                 │
│   (GBP_USD H1 candles)      │
└─────────────┬───────────────┘
              │ Backfill script
              ▼
┌─────────────────────────────┐
│   src/backfill_oanda_2h_    │
│   checkpointed.py           │
│   - Fetches H1 → 2H resample│
│   - Upserts to same table   │
└─────────────────────────────┘
```

### Service Boundaries

| Boundary | What It Contains | Ownership |
|----------|------------------|-----------|
| **P1: Webhook Ingest** | Cloudflare Worker, /tv and /tv_secure endpoints | Live TradingView alerts |
| **P2: Backfill** | `src/backfill_oanda_2h_checkpointed.py` | Historical OANDA data |
| **Option B** | C1 (single-bar), C2 (multi-bar), C3 (semantic tags) | Derived features |
| **Option C** | `derived.ovc_outcomes_v0_1` view | Forward outcomes |
| **D: Validation** | `src/validate_day.py`, `src/validate_range.py` | Facts-vs-tape checks |

### Data Flow

1. **Ingest** → TradingView emits pipe-delimited export string at 2H bar close
2. **Canonical Storage** → Worker validates against MIN contract, upserts to `ovc.ovc_blocks_v01_1_min`
3. **Derived Layers** → C1/C2/C3 features computed from canonical facts
4. **Validation** → SQL pack compares OVC facts against TradingView/OANDA tape
5. **Reports** → Run artifacts written to `reports/runs/<run_id>/`

### Design Rationale

The architecture enforces strict epistemic boundaries (`docs/OVC_DOCTRINE.md:L1-L96`):

- **Option B describes "what is happening"** — structure, motion, context
- **Option C describes "what happened after"** — outcomes, not predictions
- **No feedback loops** — performance results never flow backward to change how facts are recorded
- **Immutability** — canonical layers are frozen; changes require version bumps (`docs/IMMUTABILITY_NOTICE.md:L1-L93`)

---

## 2. Repo Map (What Lives Where)

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `.github/workflows/` | CI/CD automation | `backfill.yml`, `path1_evidence_queue.yml`, `ovc_option_c_schedule.yml` |
| `contracts/` | Data contracts (JSON schemas) | `export_contract_v0.1.1_min.json`, `eval_contract_v0.1.json`, `run_artifact_spec_v0.1.json` |
| `docs/` | Documentation hub | `OVC_DOCTRINE.md`, `WORKFLOW_STATUS.md`, `IMMUTABILITY_NOTICE.md` |
| `docs/ops/` | Canonical operational specs | `OVC_DATA_FLOW_CANON_v0.1.md`, `OPTION_B_*.md`, `OPTION_C_*.md` |
| `infra/ovc-webhook/` | Cloudflare Worker (TypeScript) | `src/index.ts`, `wrangler.jsonc` |
| `pine/` | TradingView Pine scripts | `OVC_v0_1.pine`, `export_module_v0.1.pine` |
| `reports/` | Pipeline output artifacts | `reports/runs/<run_id>/`, `reports/validation/` |
| `scripts/` | CLI entry points | `run_option_c.sh`, `pipeline_status.py`, `verify_local.ps1` |
| `sql/` | Database schema and migrations | `01_tables_min.sql`, `option_c_v0_1.sql`, `02_derived_c1_c2_tables_v0_1.sql` |
| `src/` | Python source code | `backfill_oanda_2h_checkpointed.py`, `validate_day.py`, `validate_range.py` |
| `src/derived/` | C1/C2/C3 compute scripts | `compute_c1_v0_1.py`, `compute_c2_v0_1.py` |
| `src/ovc_ops/` | Run artifact utilities | `run_artifact.py` |
| `tests/` | Test suite | `test_contract_equivalence.py`, `test_min_contract_validation.py` |
| `tools/` | Validation utilities | `validate_contract.py`, `validate_contract.ps1` |

### Special Folders

- **`reports/runs/`** — Deterministic run artifact directories per `run_artifact_spec_v0.1.json`
- **`reports/path1/evidence/`** — Evidence queue system for structured validation runs
- **`releases/`** — Release notes for frozen versions (e.g., `ovc-v0.1-spine.md`)

---

## 3. Core Concepts & Contracts

### Canonical vs Non-Canonical Zones

| Zone | Schema | Mutability | Example Objects |
|------|--------|------------|-----------------|
| **Canonical Facts** | `ovc` | LOCKED (Option A) | `ovc_blocks_v01_1_min` |
| **Derived Features** | `derived` | Versioned, replayable | `ovc_c1_features_v0_1`, `ovc_outcomes_v0_1` |
| **QA/Governance** | `ovc_qa`, `ovc_cfg` | Operational | `validation_run`, `threshold_pack` |
| **Research** | `public` (legacy) | Orphaned | `ovc_blocks_v01` (superseded) |

(`docs/ops/OVC_DATA_FLOW_CANON_v0.1.md:L54-L127`)

### Data Contracts

| Contract | Profile | Purpose | Location |
|----------|---------|---------|----------|
| `export_contract_v0.1.1_min.json` | MIN | Webhook payload schema (50 fields) | `contracts/` |
| `export_contract_v0.1_full.json` | FULL | Debug export (cold path, not active) | `contracts/` |
| `eval_contract_v0.1.json` | Option C | Outcome evaluation parameters | `contracts/` |
| `run_artifact_spec_v0.1.json` | Runs | Pipeline artifact structure | `contracts/` |

### ID Conventions

| ID Type | Format | Example |
|---------|--------|---------|
| `block_id` | `YYYYMMDD-{A-L}-{SYMBOL}` | `20260116-I-GBPUSD` |
| `run_id` | `<utc_compact>__<pipeline_id>__<sha7>` | `20260119T061512Z__P2-Backfill__a1b2c3d` |
| `block2h` | Single letter A-L (12 blocks/day) | `I` (8th block, 02:00-04:00 NY) |
| `block4h` | Letter pair (6 pairs/day) | `IJ` |

### Key Terms

| Term | Definition |
|------|------------|
| **MIN** | Minimal webhook-safe export profile (live ingestion) |
| **FULL** | Complete debug export (not currently in production) |
| **Option A** | Logging foundations — canonical facts layer (LOCKED) |
| **Option B** | Feature layers — C1 (single-bar), C2 (multi-bar), C3 (semantic) |
| **Option C** | Outcome evaluation — forward returns, MFE/MAE, hit rates |
| **state_key** | Pipe-joined tuple of semantic state fields |
| **bar_close_ms** | Unix epoch milliseconds at 2H bar close (UTC) |

### Invariants

1. **`block_id` is globally unique** — PK on `ovc_blocks_v01_1_min`
2. **OHLC sanity**: `h >= l`, `h >= max(o,c)`, `l <= min(o,c)`
3. **`rng = h - l`**, **`body = abs(c - o)`**, **`dir = sign(c - o)`**
4. **Idempotency**: All upserts use `ON CONFLICT DO UPDATE`
5. **Versioning**: Schema changes require new version, not in-place edits

(`infra/ovc-webhook/src/index.ts:L252-L286`, `docs/IMMUTABILITY_NOTICE.md`)

---

## 4. Developer Workflows (Golden Paths)

### Initial Setup

**Environment Variables** (see `docs/secrets_and_env.md`):

```bash
# Required for most operations
DATABASE_URL=postgresql://user:pass@host/db   # or NEON_DSN
OANDA_API_TOKEN=your_oanda_token
OANDA_ENV=practice                            # or "live"

# Required for Notion sync
NOTIOM_TOKEN=secret_...                       # Note: NOTIOM not NOTION (canonical typo)
NOTION_BLOCKS_DB_ID=...
NOTION_OUTCOMES_DB_ID=...

# Worker secrets (via wrangler)
OVC_TOKEN=your_webhook_token
```

**Tool Versions**:
- Python 3.12+
- Node.js 18+ (for Cloudflare Worker)
- PostgreSQL client (`psql`) for validation packs

### Install/Build

```powershell
# Python dependencies (from repo root)
pip install -r requirements.txt

# Worker dependencies (from infra/ovc-webhook)
cd infra/ovc-webhook
npm install
```

(`requirements.txt:L1-L8`, `infra/ovc-webhook/package.json:L1-L22`)

### Run Locally

**Worker (local dev server)**:
```powershell
cd infra/ovc-webhook
npm run dev
# Runs on http://localhost:8787
```

**Test ingestion**:
```powershell
curl.exe -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"
```

(`infra/ovc-webhook/package.json:L7`, `README.md:L7`)

### Run Tests

```powershell
# Python tests (CANONICAL: unittest discovery)
# Requires tests/__init__.py to make tests/ importable (Python 3.14+)
python -m unittest discover -s tests -t . -p "test_*.py" -v

# Alternative: with fault handler for debugging hangs
python -X faulthandler -m unittest discover -s tests -t . -p "test_*.py" -v

# Legacy: pytest (if installed)
python -m pytest tests/

# Worker tests (from infra/ovc-webhook)
npm test
```

**Why unittest discovery?**
Python 3.14+ requires `tests/` to be importable for `unittest discover` to work. The empty `tests/__init__.py` serves as a package marker. The canonical command above is the authoritative way to run all Python tests in this repo (~105 tests, ~3s runtime).

### Lint/Format

```powershell
# Worker TypeScript
cd infra/ovc-webhook
npx prettier --check src/
```

### Run Main Pipelines

**P2: Canonical Backfill (single date)**:
```powershell
$env:BACKFILL_DATE_NY="2024-01-10"
python src/backfill_oanda_2h_checkpointed.py
```

**P2: Canonical Backfill (date range)**:
```powershell
python src/backfill_oanda_2h_checkpointed.py --start_ny 2024-01-01 --end_ny 2024-01-31
```

**D: Validate a day**:
```powershell
python src/validate_day.py --symbol GBPUSD --date_ny 2024-01-10
```

**Option C: Run outcomes evaluation**:
```powershell
# Mac/Linux
./scripts/run_option_c.sh --run-id test_local

# Windows PowerShell
.\scripts\run_option_c.ps1 -RunId test_local
```

(`src/backfill_oanda_2h_checkpointed.py:L207-L224`, `scripts/run_option_c.sh`)

### Debugging Tips

**Log locations**:
- Run artifacts: `reports/runs/<run_id>/run.log`
- Worker logs: `wrangler dev` console or Cloudflare dashboard

**Common failure modes**:
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `contract not found` | Running from wrong directory | Run from repo root |
| `column does not exist` | Schema drift | Compare `index.ts` INSERT columns to Neon schema |
| `Invalid export: key order mismatch` | Pine export doesn't match contract | Validate with `tools/validate_contract.py` |
| `Missing required env vars` | Secrets not set | Check `DATABASE_URL`, `OANDA_API_TOKEN` |

(`docs/WORKFLOW_STATUS.md:L144-L149`)

---

## 5. CI/CD and Automation

### GitHub Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **OVC Backfill** | `backfill.yml` | Schedule: `17 */6 * * *` (every 6h) | P2 canonical backfill |
| **Backfill then Validate** | `backfill_then_validate.yml` | Manual dispatch | Backfill + full validation pipeline |
| **Option C Schedule** | `ovc_option_c_schedule.yml` | Schedule: `15 6 * * *` (daily 06:15 UTC) | Option C outcomes evaluation |
| **Notion Sync** | `notion_sync.yml` | Schedule: `17 */2 * * *` (every 2h) | Sync to Notion dashboards |
| **Path 1 Evidence Queue** | `path1_evidence_queue.yml` | Manual dispatch | Structured evidence runs with auto-PR |

(`.github/workflows/*.yml`)

### Artifacts

| Workflow | Artifact Name | Contents | Retention |
|----------|---------------|----------|-----------|
| Backfill | `backfill-run-artifacts` | `reports/runs/` | 30 days |
| Option C | `option-c-reports-*`, `option-c-run-artifacts-*` | Reports, run artifacts | 30 days |
| Evidence Queue | `evidence-run-artifacts-*` | SQL, reports, INDEX.md | 90 days |

### Run ID / Queue / Archival

- **Run IDs** follow spec: `<utc_compact>__<pipeline_id>__<sha7>`
- **Evidence queue**: `reports/path1/evidence/RUN_QUEUE.csv` defines intent
- **Execution ledger**: `reports/path1/evidence/INDEX.md` is the canonical record
- **RUN_QUEUE_RESOLVED.csv**: Generated reconciliation view (queue vs ledger)

(`contracts/run_artifact_spec_v0.1.json:L6-L14`, `.github/workflows/path1_evidence_queue.yml:L293-L306`)

---

## 6. External Dependencies & Integration Points

| Dependency | Purpose | Where Configured | Secrets Required | Failure Symptoms |
|------------|---------|------------------|------------------|------------------|
| **Neon Postgres** | Primary data store | `DATABASE_URL` / `NEON_DSN` env | Connection string | `psycopg2.OperationalError`, 500s from Worker |
| **Cloudflare Workers** | Webhook ingestion | `infra/ovc-webhook/wrangler.jsonc` | `OVC_TOKEN`, `DATABASE_URL` (via `wrangler secret`) | 500 errors, "Missing DATABASE_URL" |
| **Cloudflare R2** | Raw event archive | `wrangler.jsonc` `r2_buckets` | R2 binding | Raw events not written (non-blocking) |
| **OANDA API** | Historical OHLC data | `OANDA_API_TOKEN`, `OANDA_ENV` env | API token | `oandapyV20` exceptions, empty dataframes |
| **TradingView** | Live alert source | Pine script `alert()` calls | None (alerts push to Worker) | No data ingested |
| **Notion** | Human dashboard | `NOTIOM_TOKEN`, `NOTION_*_DB_ID` env | Notion integration token | Sync fails silently |
| **GitHub Actions** | CI/CD | `.github/workflows/` | `DATABASE_URL`, `OANDA_API_TOKEN`, `OVC_PR_BOT_TOKEN` | Workflow failures |

### Neon Schema Management

- **Schema files**: `sql/*.sql` (numbered for ordering)
- **Migrations**: Manual SQL execution; no automated migration runner
- **Connection**: Via `psycopg2` (Python) or `@neondatabase/serverless` (Worker)

### Cloudflare Deployment

```powershell
# From infra/ovc-webhook
wrangler deploy

# Set secrets
wrangler secret put OVC_TOKEN
wrangler secret put DATABASE_URL
```

(`infra/ovc-webhook/wrangler.jsonc:L9-L12`)

---

## 7. Conventions & Patterns

### Naming Conventions

| Entity | Convention | Example |
|--------|------------|---------|
| Tables | `{schema}.{entity}_v{major}_{minor}` | `ovc.ovc_blocks_v01_1_min` |
| Views | `{schema}.v_{entity}_v{version}` | `derived.v_ovc_c_outcomes_v0_1` |
| SQL files | `{order}_{purpose}.sql` | `01_tables_min.sql` |
| Contracts | `{name}_v{version}.json` | `export_contract_v0.1.1_min.json` |
| Run IDs | `{utc_compact}__{pipeline}__{sha7}` | `20260119T061512Z__P2-Backfill__a1b2c3d` |
| Branches | `{type}/{description}` | `pr/infra-min-v0.1.1`, `codex/fix-*` |

### Code Patterns

**RunWriter for pipeline telemetry** (`src/ovc_ops/run_artifact.py`):
```python
from ovc_ops.run_artifact import RunWriter, detect_trigger

trigger_type, trigger_source, actor = detect_trigger()
writer = RunWriter("P2-Backfill", "0.1.0", ["NEON_DSN", "OANDA_API_TOKEN"])
writer.start(trigger_type, trigger_source, actor)
writer.add_input(type="oanda", ref="GBP_USD")
writer.log("Processing...")
writer.add_output(type="neon_table", ref="ovc.ovc_blocks_v01_1_min", rows_written=60)
writer.check("step_name", "Description", "pass", ["run.log:line:42"])
writer.finish("success")
```

**Idempotent upserts** (all INSERT statements):
```sql
INSERT INTO ... VALUES (...)
ON CONFLICT (block_id)
DO UPDATE SET ...;
```

**Contract validation** (`tools/validate_contract.py`):
```powershell
python -m tools.validate_contract contracts/export_contract_v0.1.1_min.json tests/sample_exports/min_001.txt
```

### Footguns (Do Not Do This)

1. **Never edit canonical SQL views in place** — Create new versioned views instead
2. **Never use `/tv_secure` without JSON envelope** — Will return 400
3. **Never use BACKFILL_DATE_NY format other than YYYY-MM-DD** — Will crash
4. **Never assume `psql` is available** — Validation scripts fall back gracefully
5. **Never commit `.env` files** — They contain secrets
6. **Never push to main without version bump** for canonical layer changes
7. **Never use `git commit --amend` on shared branches**

---

## 8. "First 3 Tasks" for a New Agent

### Task 1: Validate a Historical Date

**Goal**: Run validation for a specific date to verify facts match tape.

**Commands**:
```powershell
# Ensure you're at repo root
python src/validate_day.py --symbol GBPUSD --date_ny 2024-06-15 --missing_facts skip
```

**Expected output files**:
- Console output with `status: PASS|SKIP|FAIL`
- Run artifacts in `reports/runs/<run_id>/`

**If it fails**:
- Check `DATABASE_URL` or `NEON_DSN` is set
- Verify the date has backfilled data:
  ```sql
  SELECT COUNT(*) FROM ovc.ovc_blocks_v01_1_min WHERE date_ny = '2024-06-15';
  ```

### Task 2: Run a Single-Day Backfill

**Goal**: Backfill one day of OANDA data to Neon.

**Commands**:
```powershell
$env:BACKFILL_DATE_NY="2024-06-14"
python src/backfill_oanda_2h_checkpointed.py
```

**Expected output**:
- Console shows `RUN_ID=...`, H1 candles fetched, 2H blocks computed
- `inserted_est` should be 12 (or 0 if already backfilled)
- Artifacts in `reports/runs/<run_id>/run.json`, `checks.json`, `run.log`

**If it fails**:
- Check `OANDA_API_TOKEN` and `OANDA_ENV` are set
- Verify date is not before `BACKFILL_START_UTC` (2005-01-01)

### Task 3: Validate a Contract Against Sample Export

**Goal**: Verify the MIN export contract matches a sample payload.

**Commands**:
```powershell
python -m tools.validate_contract contracts/export_contract_v0.1.1_min.json tests/sample_exports/min_001.txt
```

**Expected output**:
- `PASS` with field-by-field validation results
- No type coercion errors

**If it fails**:
- Check that `min_001.txt` has valid pipe-delimited format
- Compare key order against contract's `fields[].order` values

---

## 9. Evidence Appendix (Citations)

### Critical Files

| File | Why It Matters |
|------|----------------|
| `docs/OVC_DOCTRINE.md` | Epistemic principles governing the entire system |
| `docs/IMMUTABILITY_NOTICE.md` | Rules for canonical layer changes |
| `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` | Authoritative schema and data flow reference |
| `infra/ovc-webhook/src/index.ts` | Worker implementation (ingest truth) |
| `contracts/export_contract_v0.1.1_min.json` | MIN export schema (50 fields) |
| `sql/01_tables_min.sql` | Canonical table definition |
| `sql/option_c_v0_1.sql` | Option C views (outcomes) |
| `src/backfill_oanda_2h_checkpointed.py` | P2 backfill implementation |
| `src/validate_day.py` | Validation harness entry point |
| `src/ovc_ops/run_artifact.py` | RunWriter utility |
| `.github/workflows/backfill.yml` | P2 scheduled backfill |
| `.github/workflows/path1_evidence_queue.yml` | Evidence queue runner |

### Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/WORKFLOW_STATUS.md` | Quick-reference status snapshot |
| `docs/c_layer_boundary_spec_v0.1.md` | C1/C2/C3 tier definitions |
| `docs/ops/GOVERNANCE_RULES_v0.1.md` | Change control process |
| `docs/secrets_and_env.md` | Environment variable guide |
| `contracts/run_artifact_spec_v0.1.json` | Run artifact schema |

---

**End of Operating Base**

