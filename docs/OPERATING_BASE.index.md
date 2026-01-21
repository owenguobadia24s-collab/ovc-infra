# OVC Operating Base Index

> **Purpose:** Quick map of where key knowledge lives in the codebase.
> **Companion to:** `OPERATING_BASE.md`

---

## Quick Navigation

| If You Need To... | Look Here |
|-------------------|-----------|
| Understand the philosophy | `docs/OVC_DOCTRINE.md` |
| See current pipeline status | `docs/WORKFLOW_STATUS.md` |
| Understand data flow | `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` |
| Know what's frozen | `docs/IMMUTABILITY_NOTICE.md` |
| Configure secrets | `docs/secrets_and_env.md` |
| Run the worker locally | `infra/ovc-webhook/` |
| Run a backfill | `src/backfill_oanda_2h_checkpointed.py` |
| Validate facts | `src/validate_day.py`, `src/validate_range.py` |
| Check contracts | `contracts/export_contract_v0.1.1_min.json` |
| Understand CI/CD | `.github/workflows/*.yml` |

---

## File Index by Category

### Doctrine & Governance

| File | Purpose |
|------|---------|
| `docs/OVC_DOCTRINE.md` | Epistemic principles — what OVC is and is not |
| `docs/IMMUTABILITY_NOTICE.md` | Rules for modifying canonical layers |
| `docs/ops/GOVERNANCE_RULES_v0.1.md` | Change control process |
| `docs/c_layer_boundary_spec_v0.1.md` | C1/C2/C3 tier definitions |
| `releases/ovc-v0.1-spine.md` | Frozen scope definition |

### Contracts & Schemas

| File | Purpose |
|------|---------|
| `contracts/export_contract_v0.1.1_min.json` | MIN export schema (50 fields) |
| `contracts/export_contract_v0.1_full.json` | FULL export schema (cold path) |
| `contracts/eval_contract_v0.1.json` | Option C evaluation parameters |
| `contracts/run_artifact_spec_v0.1.json` | Run artifact directory structure |
| `contracts/derived_feature_set_v0.1.json` | C1/C2 feature definitions |

### SQL / Database

| File | Purpose |
|------|---------|
| `sql/00_schema.sql` | Schema creation |
| `sql/01_tables_min.sql` | `ovc.ovc_blocks_v01_1_min` table |
| `sql/02_derived_c1_c2_tables_v0_1.sql` | C1/C2 feature tables |
| `sql/02_tables_run_reports.sql` | Run reports table |
| `sql/03_qa_derived_validation_v0_1.sql` | QA validation tables |
| `sql/04_threshold_registry_v0_1.sql` | C3 threshold configuration |
| `sql/05_c3_regime_trend_v0_1.sql` | C3 regime tags |
| `sql/option_c_v0_1.sql` | Option C views (outcomes, scores) |
| `sql/qa_validation_pack_core.sql` | Core validation SQL pack |

### Source Code (Python)

| File | Purpose |
|------|---------|
| `src/backfill_oanda_2h_checkpointed.py` | P2: OANDA historical backfill |
| `src/validate_day.py` | D: Single-day validation harness |
| `src/validate_range.py` | D: Date range validation |
| `src/ovc_ops/run_artifact.py` | RunWriter utility for artifacts |
| `src/derived/compute_c1_v0_1.py` | C1 feature computation |
| `src/derived/compute_c2_v0_1.py` | C2 feature computation |
| `src/full_ingest_stub.py` | FULL ingest (dormant) |
| `scripts/run_option_c.sh` | Option C automation entry |
| `scripts/pipeline_status.py` | Pipeline status harness |
| `scripts/notion_sync.py` | Notion sync script |
| `tools/validate_contract.py` | Contract validation CLI |

### Infrastructure

| File | Purpose |
|------|---------|
| `infra/ovc-webhook/src/index.ts` | Cloudflare Worker (ingest) |
| `infra/ovc-webhook/wrangler.jsonc` | Worker configuration |
| `infra/ovc-webhook/package.json` | Worker dependencies |

### Pine Scripts

| File | Purpose |
|------|---------|
| `pine/OVC_v0_1.pine` | Main OVC Pine indicator |
| `pine/export_module_v0.1.pine` | Export string builder |

### CI/CD Workflows

| File | Trigger | Purpose |
|------|---------|---------|
| `.github/workflows/backfill.yml` | Schedule (6h) | P2 backfill |
| `.github/workflows/backfill_then_validate.yml` | Manual | Backfill + validation |
| `.github/workflows/ovc_option_c_schedule.yml` | Schedule (daily) | Option C |
| `.github/workflows/notion_sync.yml` | Schedule (2h) | Notion sync |
| `.github/workflows/path1_evidence_queue.yml` | Manual | Evidence runs |

### Tests

| File | Purpose |
|------|---------|
| `tests/test_contract_equivalence.py` | Contract consistency tests |
| `tests/test_min_contract_validation.py` | MIN contract validation |
| `tests/sample_exports/min_001.txt` | Sample MIN export fixture |
| `infra/ovc-webhook/test/index.spec.ts` | Worker unit tests |

---

## Schema Hierarchy

```
ovc (CANONICAL - LOCKED)
├── ovc_blocks_v01_1_min        # Primary facts table
└── ovc_run_reports_v01         # Run metadata

derived (VERSIONED)
├── derived_runs_v0_1           # Run provenance
├── ovc_c1_features_v0_1        # C1 features
├── ovc_c2_features_v0_1        # C2 features
├── ovc_c3_regime_trend_v0_1    # C3 semantic tags
├── ovc_outcomes_v0_1           # Option C outcomes (view)
└── eval_runs                   # Eval run metadata

ovc_qa (GOVERNANCE)
├── validation_run
├── expected_blocks
├── tv_ohlc_2h
└── ohlc_mismatch

ovc_cfg (CONFIG)
├── threshold_pack
└── threshold_pack_active

ops (OPERATIONAL)
└── notion_sync_state
```

---

## Pipeline IDs

| ID | Script | Schedule |
|----|--------|----------|
| `P2-Backfill` | `backfill_oanda_2h_checkpointed.py` | Every 6h |
| `B1-DerivedC1` | `compute_c1_v0_1.py` | On demand |
| `B1-DerivedC2` | `compute_c2_v0_1.py` | On demand |
| `B1-DerivedC3` | (C3 compute) | On demand |
| `D-ValidationHarness` | `validate_day.py` | On demand |
| `D-ValidationRange` | `validate_range.py` | On demand |
| `D-NotionSync` | `notion_sync.py` | Every 2h |
| `C-Eval` | `run_option_c.sh` | Daily 06:15 UTC |

---

## Environment Variables

| Variable | Required By | Purpose |
|----------|-------------|---------|
| `DATABASE_URL` / `NEON_DSN` | All pipelines | Neon connection |
| `OANDA_API_TOKEN` | P2-Backfill | OANDA auth |
| `OANDA_ENV` | P2-Backfill | `practice` or `live` |
| `OVC_TOKEN` | Worker | Webhook auth |
| `NOTIOM_TOKEN` | Notion sync | Notion auth |
| `NOTION_BLOCKS_DB_ID` | Notion sync | Blocks database |
| `NOTION_OUTCOMES_DB_ID` | Notion sync | Outcomes database |
| `BACKFILL_DATE_NY` | P2-Backfill | Single-date mode |
| `BACKFILL_DAYS_PER_RUN` | P2-Backfill | Batch size (default: 30) |
| `BACKFILL_START_UTC` | P2-Backfill | Earliest date (default: 2005-01-01) |

---

## Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| MIN schema | `export_contract_v0.1_min_r1` | Worker, contracts |
| Contract version | `0.1.1` | Worker |
| Block letters | `A-L` (12 per day) | All |
| Session start | 17:00 NY | All |
| Tolerance (validation) | `0.00001` | validate_day.py |

---

**End of Index**
