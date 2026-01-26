# OVC Workflow Audit Report

> **[CHANGE][ADDED] [STATUS: ACTIVE]**  
> **Audit Date:** 2026-01-20  
> **Primary Doc Audited:** `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md`  
> **Supporting Docs:** `docs/WORKFLOW_STATUS.md`, `docs/ovc_current_workflow.md`, `docs/ops/PIPELINE_REALITY_MAP_v0.1.md`

---

## A) Repo Reality Inventory

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `.github/workflows/` | CI/CD automation (5 workflows) |
| `infra/ovc-webhook/` | Cloudflare Worker (P1 ingest) |
| `src/` | Python scripts (backfill, validation, derived compute) |
| `src/derived/` | L1/L2/L3 feature compute scripts |
| `src/ovc_ops/` | Run artifact system (`run_artifact.py`) |
| `src/validate/` | Derived validation (`validate_derived_range_v0_1.py`) |
| `sql/` | Neon schema DDL (19 files) |
| `scripts/` | Operator scripts (11 files) |
| `contracts/` | JSON schemas (8 files) |
| `tests/` | pytest tests + sample exports |
| `tools/` | Validation utilities |
| `pine/` | TradingView Pine scripts |
| `configs/threshold_packs/` | L3 threshold configuration |
| `reports/` | Run artifacts output directory |
| `docs/` | Documentation (35+ files) |

### GitHub Actions Workflows (`.github/workflows/`)

| File | Name | Schedule | Status |
|------|------|----------|--------|
| `backfill.yml` | OVC Backfill (GBPUSD 2H) | `17 */6 * * *` (every 6h) | LIVE |
| `backfill_then_validate.yml` | OVC Backfill then Validate | workflow_dispatch only | DORMANT |
| `notion_sync.yml` | notion-sync | `17 */2 * * *` (every 2h) | LIVE |
| `ovc_option_c_schedule.yml` | OVC Option C Schedule | `15 6 * * *` (daily 06:15) | LIVE |
| `ovc_full_ingest.yml` | OVC FULL Ingest | workflow_dispatch only | DORMANT |

### Key Python Scripts (`src/`)

| File | Pipeline | Purpose |
|------|----------|---------|
| `backfill_oanda_2h_checkpointed.py` | P2 | Canonical OANDA backfill (active) |
| `backfill_oanda_2h.py` | P2 | Legacy backfill (DEPRECATED) |
| `validate_day.py` | P4 | Single-day validation |
| `validate_range.py` | P4 | Range validation |
| `full_ingest_stub.py` | - | FULL ingest stub (manual) |
| `derived/compute_l1_v0_1.py` | B1 | L1 single-bar features |
| `derived/compute_l2_v0_1.py` | B1 | L2 multi-bar features |
| `derived/compute_l3_regime_trend_v0_1.py` | B1 | L3 regime tags |
| `validate/validate_derived_range_v0_1.py` | B2 | Derived feature validation |
| `ovc_ops/run_artifact.py` | All | RunWriter class for artifacts |

### SQL Schema Files (`sql/`)

| File | Schema | Purpose |
|------|--------|---------|
| `00_schema.sql` | (base) | Schema creation |
| `01_tables_min.sql` | `ovc` | Canonical facts table (LOCKED) |
| `02_derived_c1_c2_tables_v0_1.sql` | `derived` | L1/L2 feature tables |
| `02_tables_run_reports.sql` | `ovc` | Run report metadata |
| `03_qa_derived_validation_v0_1.sql` | `ovc_qa` | Derived validation artifacts |
| `03_tables_outcomes.sql` | `ovc` | Legacy outcomes table |
| `04_ops_notion_sync.sql` | `ops` | Notion sync state |
| `04_threshold_registry_v0_1.sql` | `ovc_cfg` | Threshold packs |
| `05_c3_regime_trend_v0_1.sql` | `derived` | L3 regime tables |
| `10_views_research_v0.1.sql` | `ovc` | Research views |
| `derived_v0_1.sql` | `derived` | Feature views |
| `option_c_v0_1.sql` | `derived` | Outcome views |
| `qa_schema.sql` | `ovc_qa` | QA tables |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment template (9 vars) |
| `infra/ovc-webhook/wrangler.jsonc` | Worker config (R2 binding: `RAW_EVENTS`) |
| `contracts/export_contract_v0.1.1_min.json` | MIN export contract |
| `contracts/run_artifact_spec_v0.1.json` | Run artifact schema |
| `configs/threshold_packs/l3_regime_trend_v1.json` | L3 thresholds |

### Operator Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `verify_local.ps1` | Local validation harness |
| `deploy_worker.ps1` | Worker deployment |
| `pipeline_status.py` | Pipeline health check |
| `run_option_c.sh` | Option C runner |
| `run_option_c.ps1` | Option C runner (PowerShell) |
| `notion_sync.py` | Notion sync script |
| `validate_day.ps1` | Day validation wrapper |

---

## B) Workflow Claims Inventory (from docs)

### Claims from `OVC_DATA_FLOW_CANON_v0.1.md`

| Claim | Section | Line(s) |
|-------|---------|---------|
| `ovc.ovc_blocks_v01_1_min` is canonical facts table | §2 Schema ovc | 32 |
| `ovc.ovc_run_reports_v01` exists for run metadata | §2 Schema ovc | 33 |
| `ovc.ovc_outcomes_v01` is orphaned/dormant | §2 Schema ovc | 34 |
| Research views created by `sql/10_views_research_v0.1.sql` | §2 Schema ovc | 36-41 |
| Notion sync mappings in `scripts/notion_sync.py` | §4 | 140 |
| Notion uses `NOTIOM_TOKEN` (intentional spelling) | Implied | - |
| `export_str` synced to Notion (questionable) | §4 sync_blocks | 148 |
| `derived_runs` may be redundant with `derived_runs_v0_1` | §5 Orphans | 199 |

### Claims from `ovc_current_workflow.md`

| Claim | Status (per audit) |
|-------|-------------------|
| Pine script: `pine/OVC_v0_1.pine` | **EXISTS** |
| Worker: `infra/ovc-webhook/src/index.ts` | **EXISTS** |
| Table: `public.ovc_blocks_v01` (core MIN) | **OUTDATED** - now `ovc.ovc_blocks_v01_1_min` |
| Table: `public.ovc_blocks_detail_v01` (FULL) | **EXISTS** (orphaned) |
| Backfill: `src/backfill_oanda_2h.py` | **DEPRECATED** - use `backfill_oanda_2h_checkpointed.py` |
| R2 bucket: `ovc-raw-events` | **CORRECT** |
| Workflow: `.github/workflows/backfill.yml` | **EXISTS** |
| Workflow: `.github/workflows/ovc_full_ingest.yml` | **EXISTS** (dormant) |
| Schema: `sql/schema_v01.sql` | **EXISTS** (legacy) |

### Claims from `WORKFLOW_STATUS.md`

| Claim | Status |
|-------|--------|
| Worker: `infra/ovc-webhook/src/index.ts` | **CORRECT** |
| Contract: `contracts/export_contract_v0.1.1_min.json` | **CORRECT** |
| Validator: `tools/validate_contract.py` | **CORRECT** |
| Fixtures: `tests/sample_exports/min_001.txt` | **CORRECT** |
| Pipeline status: `scripts/pipeline_status.py` | **CORRECT** |
| P1 status: PARTIAL | **CORRECT** |
| P2 status: PASS | **CORRECT** |
| Option A: LOCKED | **CORRECT** |

---

## C) Diff Summary

### ADDED (in repo, not in docs)

| Item | Path | Impact | Fix |
|------|------|--------|-----|
| `run_option_c_with_artifact.sh` | `scripts/` | Undocumented script | Add to operator docs |
| `run_option_c_wrapper.py` | `scripts/` | Undocumented script | Add to operator docs |
| `run_migration.py` | `scripts/` | Schema migration tool | Add to docs |
| `oanda_export_2h_day.py` | `scripts/` | OANDA CSV export | Add to docs |
| `compute_l3_stub_v0_1.py` | `src/derived/` | L3 stub (testing) | Note as test stub |
| L3 threshold packs | `configs/threshold_packs/` | Config files | Document in workflow |
| `backfill_day.py` | `src/` | Single-day backfill | Document or mark deprecated |
| `ingest_history_day.py` | `src/` | History ingest | Document or mark deprecated |
| `ovc_artifacts.py` | `src/` | Artifact utilities | Document |

### REMOVED (in docs, not in repo)

| Item | Doc Location | Impact | Fix |
|------|--------------|--------|-----|
| (none found) | - | - | - |

### CHANGED (exists but differs)

| Item | Doc Claim | Reality | Impact | Fix |
|------|-----------|---------|--------|-----|
| Canonical table | `public.ovc_blocks_v01` | `ovc.ovc_blocks_v01_1_min` | Misleading operators | Update ovc_current_workflow.md |
| Backfill script | `backfill_oanda_2h.py` (active) | `backfill_oanda_2h_checkpointed.py` (active) | Wrong script reference | Update to checkpointed version |
| Notion token env var | (not documented) | `NOTIOM_TOKEN` (canonical spelling) | May confuse operators | Document explicitly |
| backfill.yml schedule | Not explicit | `cron: "17 */6 * * *"` | Undocumented schedule | Add schedule to docs |
| notion_sync.yml schedule | Not explicit | `cron: "17 */2 * * *"` | Undocumented schedule | Add schedule to docs |
| option_c schedule | Not explicit | `cron: "15 6 * * *"` | Undocumented schedule | Add schedule to docs |

---

## D) Recommended Updates

### Primary Doc: `OVC_DATA_FLOW_CANON_v0.1.md`

1. **Add GitHub Actions schedule summary** in new section after §5 ✓ DONE
2. **Add run artifact system reference** (already mentioned in PIPELINE_REALITY_MAP) ✓ DONE
3. **Document NOTIOM_TOKEN spelling** explicitly in §4 ✓ DONE

### Secondary Doc: `ovc_current_workflow.md`

This document is **significantly outdated** and should be:
- ✓ DONE: Marked as `[STATUS: DEPRECATED]`

### Secondary Doc: `WORKFLOW_STATUS.md`

- ✓ DONE: Minor updates + `[STATUS: ACTIVE]` marker added

---

## E) [CHANGE][ADDED] Lifecycle Classification Complete

All documents now have explicit status markers. See [PRUNING_CANDIDATES_v0.1.md](PRUNING_CANDIDATES_v0.1.md) for:
- Full lifecycle classification tables
- Pruning candidate list with preconditions
- Verification queries before removal

---

*End of Audit Report*
