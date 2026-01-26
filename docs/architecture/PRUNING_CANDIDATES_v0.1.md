# OVC Pruning Candidates v0.1

> **[STATUS: ACTIVE]**  
> **Created:** 2026-01-20  
> **Purpose:** Inventory of deprecated/orphaned artifacts eligible for future removal  
> **Governance:** NO DELETIONS without explicit approval; document preconditions first

---

## 1. Lifecycle Classification Summary

### Status Definitions

| Status | Definition | Action |
|--------|------------|--------|
| **CANONICAL** | Authoritative, relied upon, referenced by other systems | Freeze; protect from unreviewed changes |
| **ACTIVE** | Used operationally but not authoritative | Maintain; update as needed |
| **DEPRECATED** | Superseded but kept intentionally | Keep for reference; do not extend |
| **ORPHANED** | Exists but has no current consumers | Candidate for removal after verification |

---

## 2. Lifecycle Classification Tables

### 2.1 Neon Tables

| Table | Schema | Status | Notes |
|-------|--------|--------|-------|
| `ovc_blocks_v01_1_min` | `ovc` | **CANONICAL** | Option A locked; P1/P2 write target |
| `ovc_run_reports_v01` | `ovc` | **ACTIVE** | Run metadata for ingest/backfill |
| `ovc_outcomes_v01` | `ovc` | **ORPHANED** | FK syntax error; superseded by `derived.ovc_outcomes_v0_1` |
| `ovc_blocks_v01` | `public` | **ORPHANED** | Legacy MIN table; different PK structure |
| `ovc_blocks_detail_v01` | `public` | **ORPHANED** | FULL JSONB table; never integrated |
| `derived_runs` | `derived` | **DEPRECATED** | Coexists with `derived_runs_v0_1`; confirm authoritative before removal |
| `derived_runs_v0_1` | `derived` | **ACTIVE** | Extended run metadata with run_type, window_spec |
| `ovc_l1_features_v0_1` | `derived` | **ACTIVE** | Materialized L1 features |
| `ovc_l2_features_v0_1` | `derived` | **ACTIVE** | Materialized L2 features |
| `ovc_l3_regime_trend_v0_1` | `derived` | **ACTIVE** | L3 semantic tags |
| `eval_runs` | `derived` | **ACTIVE** | Option C evaluation runs |
| `validation_run` | `ovc_qa` | **ACTIVE** | Tape validation metadata |
| `expected_blocks` | `ovc_qa` | **ACTIVE** | Validation scaffold |
| `tv_ohlc_2h` | `ovc_qa` | **ACTIVE** | TradingView reference data |
| `ohlc_mismatch` | `ovc_qa` | **ACTIVE** | Mismatch artifacts |
| `derived_validation_run` | `ovc_qa` | **ACTIVE** | Derived validation QA |
| `threshold_pack` | `ovc_cfg` | **ACTIVE** | Immutable threshold versions |
| `threshold_pack_active` | `ovc_cfg` | **ACTIVE** | Activation pointers |
| `notion_sync_state` | `ops` | **ACTIVE** | Notion sync watermarks |

### 2.2 Python Scripts (`src/`)

| Script | Status | Notes |
|--------|--------|-------|
| `backfill_oanda_2h_checkpointed.py` | **CANONICAL** | P2 authoritative backfill |
| `backfill_oanda_2h.py` | **DEPRECATED** | Legacy; header says "use checkpointed" |
| `backfill_day.py` | **DEPRECATED** | Single-day variant; use checkpointed with date range |
| `validate_day.py` | **ACTIVE** | P4 single-day validation |
| `validate_range.py` | **ACTIVE** | P4 range validation |
| `full_ingest_stub.py` | **DEPRECATED** | FULL ingest stub; never productionized |
| `ingest_history_day.py` | **ORPHANED** | History ingest; no workflow references it |
| `test_insert.py` | **DEPRECATED** | Test utility; not part of any pipeline |
| `ovc_artifacts.py` | **ACTIVE** | Artifact utilities |
| `derived/compute_l1_v0_1.py` | **ACTIVE** | B1 L1 features |
| `derived/compute_l2_v0_1.py` | **ACTIVE** | B1 L2 features |
| `derived/compute_l3_regime_trend_v0_1.py` | **ACTIVE** | B1 L3 regime tags |
| `derived/compute_l3_stub_v0_1.py` | **DEPRECATED** | Test stub for L3 |
| `validate/validate_derived_range_v0_1.py` | **ACTIVE** | B2 derived validation |
| `ovc_ops/run_artifact.py` | **CANONICAL** | RunWriter class |
| `ovc_ops/run_artifact_cli.py` | **ACTIVE** | CLI wrapper |

### 2.3 GitHub Actions Workflows

| Workflow | Status | Notes |
|----------|--------|-------|
| `backfill.yml` | **CANONICAL** | P2 scheduled backfill; cron `17 */6 * * *` |
| `notion_sync.yml` | **CANONICAL** | D-NotionSync; cron `17 */2 * * *` |
| `ovc_option_c_schedule.yml` | **CANONICAL** | C-Eval; cron `15 6 * * *` |
| `backfill_then_validate.yml` | **ACTIVE** | Manual-only; workflow_dispatch |
| `ovc_full_ingest.yml` | **DEPRECATED** | FULL ingest stub; never scheduled |

### 2.4 Operator Scripts (`scripts/`)

| Script | Status | Notes |
|--------|--------|-------|
| `verify_local.ps1` | **CANONICAL** | Local validation harness |
| `deploy_worker.ps1` | **CANONICAL** | Worker deployment |
| `pipeline_status.py` | **ACTIVE** | Pipeline health check |
| `run_option_c.sh` | **CANONICAL** | Option C runner (bash) |
| `run_option_c.ps1` | **ACTIVE** | Option C runner (PowerShell) |
| `run_option_c_with_artifact.sh` | **ACTIVE** | Variant with explicit artifact |
| `run_option_c_wrapper.py` | **ACTIVE** | Python wrapper |
| `notion_sync.py` | **CANONICAL** | D-NotionSync entrypoint |
| `validate_day.ps1` | **ACTIVE** | Day validation wrapper |
| `run_migration.py` | **ACTIVE** | Schema migration tool |
| `oanda_export_2h_day.py` | **ACTIVE** | OANDA CSV export utility |

### 2.5 SQL Schema Files (`sql/`)

| File | Status | Notes |
|------|--------|-------|
| `00_schema.sql` | **CANONICAL** | Base schema creation |
| `01_tables_min.sql` | **CANONICAL** | Option A LOCKED |
| `02_derived_c1_c2_tables_v0_1.sql` | **ACTIVE** | B1 feature tables |
| `02_tables_run_reports.sql` | **ACTIVE** | Run report metadata |
| `03_qa_derived_validation_v0_1.sql` | **ACTIVE** | B2 QA tables |
| `03_tables_outcomes.sql` | **ORPHANED** | Legacy outcomes; FK error |
| `04_ops_notion_sync.sql` | **ACTIVE** | D-Ops sync state |
| `04_threshold_registry_v0_1.sql` | **ACTIVE** | L3 thresholds |
| `05_c3_regime_trend_v0_1.sql` | **ACTIVE** | L3 regime tables |
| `10_views_research_v0.1.sql` | **ACTIVE** | Research views |
| `derived_v0_1.sql` | **ACTIVE** | Feature views |
| `option_c_v0_1.sql` | **ACTIVE** | Outcome views |
| `qa_schema.sql` | **ACTIVE** | QA tables |
| `schema_v01.sql` | **ORPHANED** | Legacy schema; superseded by 01_tables_min |

### 2.6 Documentation (`docs/`)

| Document | Status | Notes |
|----------|--------|-------|
| `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` | **CANONICAL** | Authoritative data flow reference |
| `docs/ops/PIPELINE_REALITY_MAP_v0.1.md` | **ACTIVE** | Pipeline wiring audit |
| `docs/ops/WORKFLOW_AUDIT_2026-01-20.md` | **ACTIVE** | Workflow audit findings |
| `docs/WORKFLOW_STATUS.md` | **ACTIVE** | Operator quick-reference |
| `docs/ovc_current_workflow.md` | **DEPRECATED** | Outdated; kept for history |
| `docs/WORKER_PIPELINE.md` | **ORPHANED** | Empty file |
| `docs/step8_readiness.md` | **DEPRECATED** | Initial readiness checklist; completed |

---

## 3. Pruning Candidates

### 3.1 High-Confidence Pruning (ORPHANED)

These items have no current consumers and can be removed after verification:

| Path | Type | Current Status | Safe to Remove? | Preconditions |
|------|------|----------------|-----------------|---------------|
| `public.ovc_blocks_v01` | Table | ORPHANED | **YES** | Verify no queries reference it; archive DDL first |
| `public.ovc_blocks_detail_v01` | Table | ORPHANED | **YES** | Verify no FULL ingest scripts use it; archive DDL |
| `ovc.ovc_outcomes_v01` | Table | ORPHANED | **YES** | Verify no views reference it; FK syntax error makes it non-functional |
| `sql/schema_v01.sql` | File | ORPHANED | **YES** | Verify no migrations reference it; archive to `sql/archive/` |
| `sql/03_tables_outcomes.sql` | File | ORPHANED | **YES** | Creates orphaned table; archive to `sql/archive/` |
| `src/ingest_history_day.py` | File | ORPHANED | **YES** | Grep for imports; no workflow references |
| `docs/WORKER_PIPELINE.md` | File | ORPHANED | **YES** | Empty file; safe to delete |

### 3.2 Medium-Confidence Pruning (DEPRECATED)

These items are superseded but may have historical value:

| Path | Type | Current Status | Safe to Remove? | Preconditions |
|------|------|----------------|-----------------|---------------|
| `src/backfill_oanda_2h.py` | File | DEPRECATED | **MAYBE** | Has header marking as legacy; confirm no scripts import it |
| `src/backfill_day.py` | File | DEPRECATED | **MAYBE** | Single-day variant; verify no manual use |
| `src/full_ingest_stub.py` | File | DEPRECATED | **NO** | Keep as reference for future FULL implementation |
| `src/test_insert.py` | File | DEPRECATED | **MAYBE** | Test utility; verify not in test suite |
| `src/derived/compute_l3_stub_v0_1.py` | File | DEPRECATED | **NO** | Keep for L3 development/testing reference |
| `.github/workflows/ovc_full_ingest.yml` | Workflow | DEPRECATED | **NO** | Keep for future FULL ingest |
| `derived.derived_runs` | Table | DEPRECATED | **MAYBE** | Confirm `derived_runs_v0_1` is authoritative |
| `docs/ovc_current_workflow.md` | File | DEPRECATED | **NO** | Keep for historical reference |
| `docs/step8_readiness.md` | File | DEPRECATED | **MAYBE** | Initial checklist; may have archive value |

### 3.3 Do Not Prune

These items must be kept:

| Path | Reason |
|------|--------|
| All `CANONICAL` items | Authoritative; production-critical |
| All `ACTIVE` items | Currently in use |
| `backfill_then_validate.yml` | Manual but functional; used for range validation |
| Config/threshold files | Required for L3 compute |

---

## 4. Verification Queries

Before removing any database objects, run these verification queries:

### Check table references
```sql
-- Check if a table is referenced by any view or function
SELECT 
    n.nspname AS schema_name,
    c.relname AS object_name,
    c.relkind AS object_type
FROM pg_depend d
JOIN pg_class c ON c.oid = d.objid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE d.refobjid = 'public.ovc_blocks_v01'::regclass;
```

### Check row counts (tables)
```sql
SELECT 'public.ovc_blocks_v01' AS tbl, count(*) FROM public.ovc_blocks_v01
UNION ALL
SELECT 'public.ovc_blocks_detail_v01', count(*) FROM public.ovc_blocks_detail_v01
UNION ALL
SELECT 'ovc.ovc_outcomes_v01', count(*) FROM ovc.ovc_outcomes_v01;
```

### Grep for script imports (PowerShell)
```powershell
# Check if deprecated script is imported anywhere
Get-ChildItem -Recurse -Include *.py | Select-String -Pattern "backfill_oanda_2h[^_]"
Get-ChildItem -Recurse -Include *.py | Select-String -Pattern "ingest_history_day"
```

---

## 5. Archive Procedure (When Ready)

When pruning is approved:

1. **Database objects:**
   ```sql
   -- Archive DDL
   \d+ public.ovc_blocks_v01 > sql/archive/ovc_blocks_v01.ddl.txt
   
   -- Drop (after backup)
   DROP TABLE IF EXISTS public.ovc_blocks_v01;
   ```

2. **Files:**
   ```powershell
   # Move to archive
   mkdir -p sql/archive
   Move-Item sql/schema_v01.sql sql/archive/
   
   # Or delete empty files
   Remove-Item docs/WORKER_PIPELINE.md
   ```

3. **Update docs:**
   - Remove references from PIPELINE_REALITY_MAP
   - Update DATA_FLOW_CANON orphan section

---

## 6. Summary

### Canonically Frozen (Protected)

| Category | Items |
|----------|-------|
| Tables | `ovc.ovc_blocks_v01_1_min` |
| Scripts | `backfill_oanda_2h_checkpointed.py`, `run_artifact.py` |
| Workflows | `backfill.yml`, `notion_sync.yml`, `ovc_option_c_schedule.yml` |
| Operator | `verify_local.ps1`, `deploy_worker.ps1`, `run_option_c.sh`, `notion_sync.py` |
| Docs | `OVC_DATA_FLOW_CANON_v0.1.md` |
| SQL | `00_schema.sql`, `01_tables_min.sql` |

### Intentionally Legacy (Keep for Reference)

| Category | Items |
|----------|-------|
| Tables | `derived.derived_runs` (pending confirmation) |
| Scripts | `backfill_oanda_2h.py`, `full_ingest_stub.py`, `compute_l3_stub_v0_1.py` |
| Workflows | `ovc_full_ingest.yml` |
| Docs | `ovc_current_workflow.md`, `step8_readiness.md` |

### Safely Removable (After Verification)

| Category | Items |
|----------|-------|
| Tables | `public.ovc_blocks_v01`, `public.ovc_blocks_detail_v01`, `ovc.ovc_outcomes_v01` |
| Scripts | `ingest_history_day.py` |
| SQL | `schema_v01.sql`, `03_tables_outcomes.sql` |
| Docs | `WORKER_PIPELINE.md` (empty) |

---

*End of Pruning Candidates v0.1*
