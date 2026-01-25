# Category Process Appendix (DRAFT)

**Status:** DRAFT — Evidence-based mapping only
**Generated:** 2026-01-25
**Authority:** This document describes CATEGORIES independent of Option ownership.

---

## 1) PIPELINES

### CATEGORY PURPOSE
Orchestrated sequences of code execution that transform data from one state to another. Pipelines connect external sources to internal stores, or chain internal transformations.

### PROCESSES INSIDE THIS CATEGORY
- **Ingest**: External data → canonical tables
- **Backfill**: Historical gap-fill from OANDA API → canonical tables
- **Compute**: Canonical facts → derived features (C1, C2, C3)
- **Outcomes**: Derived features → forward-looking outcomes
- **Sync**: Internal data → external systems (Notion)

### EXPECTED FILE TYPES
Based on repo evidence:
- `.yml` workflow files (GitHub Actions)
- `.py` runner scripts
- `.sh` / `.ps1` shell wrappers

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `.github/workflows/backfill.yml` | Scheduled OANDA 2H backfill pipeline |
| `.github/workflows/backfill_m15.yml` | Scheduled OANDA M15 backfill pipeline |
| `.github/workflows/backfill_then_validate.yml` | Backfill + derived compute + validation (manual trigger) |
| `.github/workflows/ovc_full_ingest.yml` | Full ingest stub (manual trigger) |
| `.github/workflows/ovc_option_c_schedule.yml` | Scheduled Option C outcomes runner |
| `.github/workflows/notion_sync.yml` | Scheduled Notion database sync |
| `.github/workflows/path1_evidence.yml` | Path1 single evidence run |
| `.github/workflows/path1_evidence_queue.yml` | Path1 queued evidence runs |
| `.github/workflows/path1_replay_verify.yml` | Path1 replay verification |
| `scripts/run/run_option_c.sh` | Option C runner shell script |
| `scripts/run/run_option_c_wrapper.py` | Option C Python wrapper |
| `scripts/path1/run_evidence_queue.py` | Path1 evidence queue executor |
| `scripts/path1/run_evidence_range.py` | Path1 evidence range executor |
| `scripts/path1/build_evidence_pack_v0_2.py` | Evidence pack builder |

### DIAGRAM (ASCII)

```
 EXTERNAL SOURCES              PIPELINES                    INTERNAL STORES
 ================           ===============              ==================

 TradingView ───────┐        ┌─────────────┐
    Alerts          │        │   INGEST    │
                    ├───────>│  Workflows  ├────────> ovc.ovc_blocks_v01_1_min
 OANDA API  ────────┤        │  (backfill) │                    │
                    │        └─────────────┘                    │
                                                                v
                             ┌─────────────┐           derived.c1_features
                             │   COMPUTE   │           derived.c2_features
                             │  Pipelines  │<──────────derived.c3_features
                             └──────┬──────┘                    │
                                    │                           v
                             ┌──────v──────┐           derived.v_ovc_c_outcomes
                             │  OUTCOMES   │
                             │  Pipeline   │
                             └──────┬──────┘
                                    │
                             ┌──────v──────┐           reports/path1/evidence/
                             │  EVIDENCE   │
                             │  Pipelines  │
                             └─────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `ovc_option_c_schedule.yml` references `scripts/run_option_c.sh` which exists at `scripts/run/run_option_c.sh` | CONTRADICTORY PATH (documented in CURRENT_STATE) |
| `ovc_full_ingest.yml` is workflow_dispatch only with no schedule | DORMANT PIPELINE |
| `backfill_then_validate.yml` has no schedule (manual only) | DORMANT PIPELINE |
| C3 compute (`compute_c3_regime_trend_v0_1.py`) exists but no workflow invokes it | IMPLIED BUT NOT IMPLEMENTED |
| No CI workflow runs pytest suite on push/PR | EXPECTED BUT MISSING |

---

## 2) SUB-SYSTEMS

### CATEGORY PURPOSE
Distinct functional units that encapsulate specific capabilities. Sub-systems may span multiple files but serve a single coherent purpose.

### PROCESSES INSIDE THIS CATEGORY
- **Cloudflare Worker**: HTTP webhook receiver + R2 archival
- **Threshold Registry**: Configuration management for derived computations
- **Run Artifact System**: Standardized execution metadata capture
- **Trajectory Families**: Clustering and fingerprinting module

### EXPECTED FILE TYPES
Based on repo evidence:
- `.ts` TypeScript source (Worker)
- `.py` Python modules
- `.json` configuration/schema files

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `infra/ovc-webhook/` | Cloudflare Worker sub-system (TypeScript) |
| `infra/ovc-webhook/src/index.ts` | Main worker entry point |
| `src/config/threshold_registry_v0_1.py` | Threshold pack management |
| `src/config/threshold_registry_cli.py` | CLI for threshold registry |
| `src/ovc_ops/run_artifact.py` | RunWriter class for execution metadata |
| `src/ovc_ops/run_artifact_cli.py` | CLI wrapper for run artifacts |
| `trajectory_families/` | Trajectory clustering sub-system |
| `trajectory_families/clustering.py` | Clustering algorithms |
| `trajectory_families/fingerprint.py` | Fingerprint generation |
| `trajectory_families/distance.py` | Distance metrics |

### DIAGRAM (ASCII)

```
 SUB-SYSTEMS INTERACTION
 =======================

 ┌─────────────────────────────────────────────────────────────┐
 │                    CLOUDFLARE WORKER                        │
 │  infra/ovc-webhook/                                         │
 │  ┌─────────┐     ┌─────────┐     ┌─────────┐               │
 │  │  /tv    │────>│ parse   │────>│  Neon   │               │
 │  │endpoint │     │ export  │     │  upsert │               │
 │  └─────────┘     └────┬────┘     └─────────┘               │
 │                       │                                     │
 │                       v                                     │
 │                  ┌─────────┐                                │
 │                  │   R2    │ (raw archive)                  │
 │                  └─────────┘                                │
 └─────────────────────────────────────────────────────────────┘

 ┌─────────────────────────────────────────────────────────────┐
 │                  THRESHOLD REGISTRY                         │
 │  src/config/threshold_registry_v0_1.py                      │
 │                                                             │
 │  configs/threshold_packs/*.json ──> ovc_cfg.threshold_packs │
 └─────────────────────────────────────────────────────────────┘

 ┌─────────────────────────────────────────────────────────────┐
 │                   RUN ARTIFACT SYSTEM                       │
 │  src/ovc_ops/run_artifact.py                                │
 │                                                             │
 │  [Pipeline Execution] ──> reports/runs/<run_id>/run.json    │
 │                      ──> contracts/run_artifact_spec_v0.1   │
 └─────────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| Worker deployment status is UNKNOWN (no wrangler deploy logs in repo) | UNKNOWN STATUS |
| Worker secrets (OVC_TOKEN, DATABASE_URL) unverifiable from repo | UNKNOWN STATUS |
| `trajectory_families/` has no workflow integration | EXPERIMENTAL / PARTIAL |

---

## 3) MODELS

### CATEGORY PURPOSE
Computational logic that produces classifications, scores, or predictions. Models are versioned formulas applied to data.

### PROCESSES INSIDE THIS CATEGORY
- **Score Computation**: DIS, LID, RES descriptive scores
- **Regime Trend**: C3 regime classification
- **State Plane**: Multi-dimensional path analysis

### EXPECTED FILE TYPES
Based on repo evidence:
- `.py` Python compute modules
- `.sql` view definitions
- `.json` parameter files

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `src/derived/compute_c1_v0_1.py` | C1 feature computation |
| `src/derived/compute_c2_v0_1.py` | C2 feature computation |
| `src/derived/compute_c3_regime_trend_v0_1.py` | C3 regime trend model |
| `src/derived/compute_c3_stub_v0_1.py` | C3 stub/placeholder |
| `sql/path1/scores/score_dis_v1_1.sql` | DIS score SQL |
| `sql/path1/scores/score_lid_v1_0.sql` | LID score SQL |
| `sql/path1/scores/score_res_v1_0.sql` | RES score SQL |
| `trajectory_families/params_v0_1.json` | Trajectory family parameters |

### DIAGRAM (ASCII)

```
 CANONICAL FACTS                 MODELS                    DERIVED OUTPUTS
 ===============           ==================            =================

 ovc.ovc_blocks_v01_1_min                               derived.ovc_c1_features
           │               ┌──────────────┐                      │
           ├──────────────>│  C1 Compute  │──────────────────────┤
           │               └──────────────┘                      │
           │                                             derived.ovc_c2_features
           │               ┌──────────────┐                      │
           ├──────────────>│  C2 Compute  │──────────────────────┤
           │               └──────────────┘                      │
           │                                             derived.ovc_c3_features
           │               ┌──────────────┐                      │
           └──────────────>│  C3 Regime   │──────────────────────┘
                           │  Trend Model │
                           └──────────────┘
                                  │
                                  v
                           ┌──────────────┐
                           │ Scores (DIS, │
                           │  LID, RES)   │
                           └──────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `compute_c3_regime_trend_v0_1.py` exists but is not invoked by any workflow | IMPLIED BUT NOT IMPLEMENTED |
| `compute_c3_stub_v0_1.py` purpose unclear vs full C3 compute | UNKNOWN RELATIONSHIP |
| Legacy `derived.ovc_block_features_v0_1` coexists with split C1/C2/C3 | CONTRADICTORY OWNERSHIP |

---

## 4) CONTRACTS

### CATEGORY PURPOSE
Formal specifications that define data shapes, boundaries, and rules. Contracts are the authoritative source for what data must look like.

### PROCESSES INSIDE THIS CATEGORY
- **Schema Definition**: Table/view column specifications
- **Boundary Enforcement**: Layer separation rules (A/B/C/D)
- **Export Specification**: External data format contracts

### EXPECTED FILE TYPES
Based on repo evidence:
- `.md` markdown contracts
- `.json` JSON schema contracts

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `docs/contracts/A_TO_D_CONTRACT_v1.md` | Master A→D pipeline contract |
| `docs/contracts/option_a_ingest_contract_v1.md` | Option A ingest contract |
| `docs/contracts/option_b_derived_contract_v1.md` | Option B derived contract |
| `docs/contracts/option_c_outcomes_contract_v1.md` | Option C outcomes contract |
| `docs/contracts/option_d_evidence_contract_v1.md` | Option D evidence contract |
| `docs/contracts/qa_validation_contract_v1.md` | QA validation contract |
| `docs/contracts/c_layer_boundary_spec_v0.1.md` | C-layer boundary specification |
| `docs/contracts/ingest_boundary.md` | Ingest boundary rules |
| `docs/contracts/derived_layer_boundary.md` | Derived layer boundary rules |
| `contracts/export_contract_v0.1.1_min.json` | MIN export contract (JSON) |
| `contracts/export_contract_v0.1_full.json` | FULL export contract (JSON) |
| `contracts/derived_feature_set_v0.1.json` | Derived feature set contract |
| `contracts/run_artifact_spec_v0.1.json` | Run artifact specification |
| `contracts/eval_contract_v0.1.json` | Evaluation contract |

### DIAGRAM (ASCII)

```
 CONTRACT HIERARCHY
 ==================

 ┌─────────────────────────────────────────────────────────────┐
 │              A_TO_D_CONTRACT_v1.md (MASTER)                 │
 │   Governs flow from Option A through Option D               │
 └──────────────────────────┬──────────────────────────────────┘
                            │
      ┌─────────────────────┼─────────────────────┐
      v                     v                     v
 ┌─────────┐          ┌─────────┐          ┌─────────┐
 │Option A │          │Option B │          │Option C │
 │Contract │          │Contract │          │Contract │
 └────┬────┘          └────┬────┘          └────┬────┘
      │                    │                    │
      v                    v                    v
 ┌─────────┐          ┌─────────┐          ┌─────────┐
 │ ingest_ │          │derived_ │          │outcomes_│
 │boundary │          │layer_   │          │boundary │
 └─────────┘          │boundary │          └─────────┘
                      └─────────┘

 JSON Contracts (export/feature validation):
 ┌─────────────────────────────────────────────────────────────┐
 │ contracts/export_contract_v0.1.1_min.json   (52 fields)     │
 │ contracts/derived_feature_set_v0.1.json                     │
 │ contracts/run_artifact_spec_v0.1.json                       │
 └─────────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `docs/contracts/` contains markdown contracts; `contracts/` contains JSON contracts | SPLIT LOCATION (not necessarily wrong) |
| PATH2_CONTRACT_v1_0.md exists but Path2 has no implementation | IMPLIED BUT NOT IMPLEMENTED |
| Some contracts reference paths that don't exist (per CANONICAL_REPO_MAP) | CONTRADICTIONS DOCUMENTED |

---

## 5) REGISTRIES

### CATEGORY PURPOSE
Central lookup tables for configuration, thresholds, and metadata. Registries provide single sources of truth for parameters.

### PROCESSES INSIDE THIS CATEGORY
- **Threshold Pack Management**: Store/retrieve threshold configurations
- **Migration Tracking**: Record applied SQL migrations

### EXPECTED FILE TYPES
Based on repo evidence:
- `.sql` table definitions
- `.json` registry data files
- `.py` registry access code

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `sql/04_threshold_registry_v0_1.sql` | Threshold registry table definition |
| `configs/threshold_packs/` | Threshold pack JSON files |
| `configs/threshold_packs/c3_regime_trend_v1.json` | C3 regime trend thresholds |
| `configs/threshold_packs/state_plane_v0_2_default_v1.json` | State plane defaults |
| `schema/applied_migrations.json` | Migration tracking ledger |
| `schema/required_objects.txt` | Required database objects list |

### DIAGRAM (ASCII)

```
 REGISTRIES
 ==========

 ┌───────────────────────────────────────────────────────────┐
 │                   THRESHOLD REGISTRY                      │
 │                                                           │
 │  configs/threshold_packs/*.json                           │
 │           │                                               │
 │           v                                               │
 │  src/config/threshold_registry_v0_1.py                    │
 │           │                                               │
 │           v                                               │
 │  ovc_cfg.threshold_packs (Neon table)                     │
 │  ovc_cfg.threshold_pack_active                            │
 └───────────────────────────────────────────────────────────┘

 ┌───────────────────────────────────────────────────────────┐
 │                  MIGRATION LEDGER                         │
 │                                                           │
 │  schema/applied_migrations.json                           │
 │           │                                               │
 │           └──> Tracks which sql/*.sql files applied       │
 │               (all currently marked UNVERIFIED)           │
 └───────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `applied_migrations.json` has all migrations marked "UNVERIFIED" | GAP: No verified migration state |
| No CI check verifies migration ledger matches database state | EXPECTED BUT MISSING |

---

## 6) DATA STORES & INTERFACES

### CATEGORY PURPOSE
Persistent storage locations and their access interfaces. Includes databases, file stores, and external system connectors.

### PROCESSES INSIDE THIS CATEGORY
- **Neon PostgreSQL**: Primary relational store
- **Cloudflare R2**: Raw event archive
- **Notion API**: External sync target

### EXPECTED FILE TYPES
Based on repo evidence:
- `.sql` schema/table definitions
- `.py` database access code
- `.ts` Worker database bindings

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `sql/00_schema.sql` | Base schema creation (ovc, derived, ovc_cfg) |
| `sql/01_tables_min.sql` | Canonical facts table `ovc.ovc_blocks_v01_1_min` |
| `sql/02_tables_run_reports.sql` | Run reports table |
| `sql/02_derived_c1_c2_tables_v0_1.sql` | Derived feature tables |
| `sql/03_tables_outcomes.sql` | Outcomes tables |
| `sql/04_ops_notion_sync.sql` | Notion sync tables |
| `scripts/export/notion_sync.py` | Notion API sync script |
| `infra/ovc-webhook/wrangler.jsonc` | R2 bucket binding config |
| `data/raw/tradingview/` | Local raw TradingView data |

### DIAGRAM (ASCII)

```
 DATA STORES & INTERFACES
 ========================

 ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
 │   CLOUDFLARE R2  │     │  NEON POSTGRESQL │     │     NOTION       │
 │  (raw archive)   │     │   (primary DB)   │     │   (external)     │
 └────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
          │                        │                        │
          │                        │                        │
    infra/ovc-webhook/       sql/*.sql                scripts/export/
    wrangler.jsonc           definitions              notion_sync.py
          │                        │                        │
          v                        v                        v
 ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
 │  tv/YYYY-MM-DD/  │     │ ovc.* (canonical)│     │ Notion Databases │
 │  raw event blobs │     │ derived.* (comp) │     │ (synced views)   │
 └──────────────────┘     │ ovc_cfg.* (reg)  │     └──────────────────┘
                          │ ovc_qa.* (valid) │
                          └──────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `data/raw/tradingview/` exists locally but relationship to R2 unclear | UNKNOWN RELATIONSHIP |
| Notion sync uses `NOTIOM_TOKEN` spelling (canonical per documentation) | DOCUMENTED QUIRK |
| Worker telemetry schema drift documented (`ended_at` vs `finished_at`) | CONTRACTUAL VIOLATION |

---

## 7) ARTIFACTS & EVIDENCE

### CATEGORY PURPOSE
Outputs produced by pipeline execution. Artifacts are versioned, timestamped records of what was computed.

### PROCESSES INSIDE THIS CATEGORY
- **Run Artifacts**: Execution metadata (run.json, run.log, checks.json)
- **Evidence Packs**: Path1 study outputs
- **Validation Reports**: QA execution results

### EXPECTED FILE TYPES
Based on repo evidence:
- `.json` metadata files
- `.md` human-readable reports
- `.csv` / `.jsonl` data outputs
- `.log` execution logs

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `reports/runs/` | Run artifact directories (timestamped) |
| `reports/path1/evidence/runs/` | Path1 evidence run outputs (31 runs) |
| `reports/path1/scores/` | Score computation results |
| `reports/path1/trajectory_families/` | Trajectory fingerprint outputs |
| `reports/validation/` | Validation range summaries |
| `reports/pipeline_audit/` | Pipeline audit results |
| `reports/verification/` | Verification outputs |
| `artifacts/derived_validation/` | Derived validation artifacts |
| `artifacts/option_c/` | Option C sanity outputs |
| `artifacts/path1_replay_report.json` | Path1 replay results |

### DIAGRAM (ASCII)

```
 ARTIFACTS & EVIDENCE FLOW
 =========================

 [Pipeline Execution]
         │
         v
 ┌──────────────────────────────────────────────────────────┐
 │                    reports/runs/                          │
 │  ┌─────────────────────────────────────────────────────┐ │
 │  │ 20260120T175509Z__P2-Backfill__ee6a769/             │ │
 │  │   ├── run.json                                       │ │
 │  │   ├── run.log                                        │ │
 │  │   └── checks.json                                    │ │
 │  └─────────────────────────────────────────────────────┘ │
 └──────────────────────────────────────────────────────────┘

 [Path1 Evidence Runs]
         │
         v
 ┌──────────────────────────────────────────────────────────┐
 │              reports/path1/evidence/runs/                 │
 │  ┌─────────────────────────────────────────────────────┐ │
 │  │ p1_20260120_001/                                     │ │
 │  │   ├── RUN.md                                         │ │
 │  │   ├── DIS_v1_1_evidence.md                           │ │
 │  │   ├── LID_v1_0_evidence.md                           │ │
 │  │   ├── RES_v1_0_evidence.md                           │ │
 │  │   └── outputs/                                       │ │
 │  └─────────────────────────────────────────────────────┘ │
 └──────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `reports/path1/evidence/INDEX.md` referenced in Maze but not found in glob | CLAIMED-BUT-MISSING OR DYNAMIC |
| Evidence pack structure varies across runs (some have outputs/, some don't) | INCONSISTENT STRUCTURE |

---

## 8) ORCHESTRATION

### CATEGORY PURPOSE
Coordination of execution across systems. Includes CI/CD, scheduling, and execution wrappers.

### PROCESSES INSIDE THIS CATEGORY
- **GitHub Actions**: Workflow scheduling and execution
- **Shell Wrappers**: Local execution coordination
- **CI Gates**: Automated verification

### EXPECTED FILE TYPES
Based on repo evidence:
- `.yml` GitHub Actions workflows
- `.sh` / `.ps1` shell scripts
- `.py` wrapper scripts

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `.github/workflows/` | All GitHub Actions workflows (13 files) |
| `.github/workflows/main.yml` | Main workflow (purpose unclear) |
| `.github/workflows/ci_pytest.yml` | Python test CI |
| `.github/workflows/ci_schema_check.yml` | Schema verification CI |
| `.github/workflows/ci_workflow_sanity.yml` | Workflow YAML validation |
| `scripts/run/` | Execution wrapper scripts |
| `scripts/deploy/deploy_worker.ps1` | Worker deployment |
| `scripts/local/verify_local.ps1` | Local verification |
| `scripts/ci/verify_schema_objects.py` | Schema object verification |

### DIAGRAM (ASCII)

```
 ORCHESTRATION FLOW
 ==================

 ┌───────────────────────────────────────────────────────────┐
 │                    GITHUB ACTIONS                         │
 │                                                           │
 │  Scheduled:                                               │
 │    backfill.yml          (cron: 17 */6 * * *)             │
 │    backfill_m15.yml      (cron: ...)                      │
 │    ovc_option_c_schedule (cron: 15 6 * * *)               │
 │    notion_sync.yml       (cron: 17 */2 * * *)             │
 │                                                           │
 │  CI (on push/PR):                                         │
 │    ci_pytest.yml                                          │
 │    ci_schema_check.yml                                    │
 │    ci_workflow_sanity.yml                                 │
 │                                                           │
 │  Manual (workflow_dispatch):                              │
 │    ovc_full_ingest.yml                                    │
 │    backfill_then_validate.yml                             │
 │    path1_evidence.yml                                     │
 │    path1_evidence_queue.yml                               │
 │    path1_replay_verify.yml                                │
 └───────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `main.yml` purpose is UNKNOWN | UNKNOWN |
| CI runs but pytest not integrated into scheduled pipelines | GAP |

---

## 9) QA & GOVERNANCE

### CATEGORY PURPOSE
Validation, verification, and policy enforcement. Ensures correctness, determinism, and contract compliance.

### PROCESSES INSIDE THIS CATEGORY
- **Validation Harness**: Day/range validation against OANDA
- **Derived Validation**: Coverage and correctness checks
- **Determinism Testing**: Replay and equivalence tests
- **Contract Enforcement**: Boundary and schema checks

### EXPECTED FILE TYPES
Based on repo evidence:
- `.py` validation scripts
- `.sql` QA queries and tables
- `.md` governance documentation
- `test_*.py` pytest files

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `src/validate_day.py` | Single-day validation harness |
| `src/validate_range.py` | Range validation harness |
| `src/validate/validate_derived_range_v0_1.py` | Derived feature validation |
| `sql/qa_schema.sql` | QA schema tables |
| `sql/qa_validation_pack.sql` | QA validation queries |
| `sql/qa_validation_pack_core.sql` | Core validation pack |
| `sql/qa_validation_pack_derived.sql` | Derived validation pack |
| `sql/03_qa_derived_validation_v0_1.sql` | Derived validation tables |
| `sql/90_verify_gate2.sql` | Gate 2 verification queries |
| `tests/` | Pytest test suite (13+ test files) |
| `docs/doctrine/OVC_DOCTRINE.md` | Epistemic governance rules |
| `docs/doctrine/GATES.md` | Gate definitions |
| `docs/governance/GOVERNANCE_RULES_v0.1.md` | Governance rules |

### DIAGRAM (ASCII)

```
 QA & GOVERNANCE
 ===============

 ┌───────────────────────────────────────────────────────────┐
 │                    VALIDATION LAYER                       │
 │                                                           │
 │  src/validate_day.py ──────────┐                          │
 │  src/validate_range.py ────────┼───> ovc_qa.* tables      │
 │  src/validate/validate_derived_range_v0_1.py ──┘          │
 │                                                           │
 └───────────────────────────────────────────────────────────┘

 ┌───────────────────────────────────────────────────────────┐
 │                    TEST SUITE                             │
 │                                                           │
 │  tests/test_derived_features.py    (24 tests)             │
 │  tests/test_c3_regime_trend.py     (20 tests)             │
 │  tests/test_validate_derived.py    (50 tests)             │
 │  tests/test_fingerprint.py                                │
 │  tests/test_contract_equivalence.py                       │
 │  tests/test_overlays_v0_3_determinism.py                  │
 │  ... (134 tests total)                                    │
 └───────────────────────────────────────────────────────────┘

 ┌───────────────────────────────────────────────────────────┐
 │                    GOVERNANCE DOCS                        │
 │                                                           │
 │  docs/doctrine/OVC_DOCTRINE.md     (epistemic rules)      │
 │  docs/doctrine/GATES.md            (gate definitions)     │
 │  docs/governance/GOVERNANCE_RULES_v0.1.md                 │
 │  docs/governance/BRANCH_POLICY.md                         │
 └───────────────────────────────────────────────────────────┘
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| pytest runs locally (134 tests) but no CI workflow executes them on schedule | EXPECTED BUT MISSING |
| `90_verify_gate2.sql` exists but gate execution not automated | PARTIAL IMPLEMENTATION |

---

## 10) DOCUMENTATION & MAPS

### CATEGORY PURPOSE
Human-readable documentation, navigation aids, and system maps. Provides understanding of the system.

### PROCESSES INSIDE THIS CATEGORY
- **Architecture Docs**: System design documentation
- **Runbooks**: Operational procedures
- **Maps**: Repository navigation (Maze, CURRENT_STATE)
- **Changelogs**: Version history

### EXPECTED FILE TYPES
Based on repo evidence:
- `.md` markdown documentation
- `.canvas` Obsidian canvas files

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `docs/` | Main documentation folder (111+ markdown files) |
| `docs/architecture/` | Architecture documentation |
| `docs/operations/` | Operational documentation |
| `docs/runbooks/` | Operational runbooks |
| `docs/pipeline/` | Pipeline state documentation |
| `docs/governance/` | Governance documentation |
| `docs/validation/` | Validation reports |
| `docs/REPO_MAP/` | Repository organization maps |
| `Tetsu/OVC_REPO_MAZE/` | Obsidian maze navigation |
| `README.md` | Root README |
| `CHANGELOG_*.md` | Changelog files |

### DIAGRAM (ASCII)

```
 DOCUMENTATION STRUCTURE
 =======================

 docs/
 ├── architecture/          (system design)
 ├── contracts/             (boundary specs - markdown)
 ├── doctrine/              (governance principles)
 ├── evidence_pack/         (evidence pack docs)
 ├── governance/            (policies)
 ├── history/               (historical records)
 ├── operations/            (operational guides)
 ├── option_d/              (Option D specific)
 ├── path1/                 (Path1 docs)
 ├── path2/                 (Path2 docs)
 ├── pipeline/              (pipeline state - CURRENT_STATE_*)
 ├── REPO_MAP/              (organization maps)
 ├── runbooks/              (operational procedures)
 ├── specs/                 (detailed specifications)
 ├── state_plane/           (state plane docs)
 ├── validation/            (validation reports)
 └── workflows/             (workflow docs)

 Tetsu/OVC_REPO_MAZE/       (Obsidian navigation vault)
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `docs/REPO_MAP/` files are empty/draft stubs | EXPECTED BUT MISSING (this task fills them) |
| Maze claims file counts that contradict repo reality | CONTRADICTIONS DOCUMENTED |
| `docs/history/path1/OPTION_B_PATH1_STATUS.md` referenced but may not exist | CLAIMED-BUT-MISSING |

---

## 11) EXPERIMENTS & SANDBOX

### CATEGORY PURPOSE
Research, prototyping, and temporary files. Not part of production pipeline.

### PROCESSES INSIDE THIS CATEGORY
- **Research Studies**: Formal research investigations
- **Notebooks**: Jupyter exploration
- **Temporary Directories**: Test/debug artifacts

### EXPECTED FILE TYPES
Based on repo evidence:
- `.md` study documentation
- `.sql` research queries
- `.ipynb` notebooks (expected but missing)
- Temporary directories

### KNOWN FILES / FOLDERS

| Path | Description |
|------|-------------|
| `research/` | Research folder |
| `research/studies/` | Formal study folders (6 completed) |
| `research/notebooks/` | Jupyter notebooks (README only, no notebooks) |
| `research/scores/` | Score development |
| `research/RESEARCH_GUARDRAILS.md` | Research governance |
| `testdir/` | Test directory (temporary) |
| `testdir2/` | Test directory 2 (temporary) |
| `chmod_test/` | Chmod test directory (temporary) |
| `.pytest-tmp/` | Pytest temporary files |
| `.pytest-tmp2/` | Pytest temporary files 2 |

### DIAGRAM (ASCII)

```
 EXPERIMENTS & SANDBOX
 =====================

 research/
 ├── studies/
 │   ├── study_20260120_basic_feature_outcome_baseline/
 │   │   ├── spec.md
 │   │   ├── method.md
 │   │   ├── results.md
 │   │   └── verdict.md
 │   ├── study_20260120_block_range_intensity_vs_outcomes/
 │   └── ... (6 studies total)
 ├── notebooks/
 │   └── README.md (no actual notebooks)
 ├── scores/
 │   └── score_block_range_intensity_v1_0.sql
 └── RESEARCH_GUARDRAILS.md

 Temporary (should be gitignored):
   testdir/, testdir2/, chmod_test/
   .pytest-tmp/, .pytest-tmp2/
```

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `research/notebooks/` has README but no actual notebooks | EXPECTED BUT MISSING |
| `testdir/`, `testdir2/`, `chmod_test/` are tracked in git | SHOULD BE GITIGNORED |
| `.pytest-tmp/`, `.pytest-tmp2/` are tracked | SHOULD BE GITIGNORED |

---

## 12) UNKNOWN

### CATEGORY PURPOSE
Folders or files that cannot be confidently classified based on available evidence.

### KNOWN FILES / FOLDERS

| Path | Description | Reason for UNKNOWN |
|------|-------------|-------------------|
| `releases/` | Contains `ovc-v0.1-spine.md` | Single file, unclear purpose |
| `CLAIMS/` | Contains `ANCHOR_INDEX_v0_1.csv`, `CLAIM_BINDING_v0_1.md` | Unique structure, unclear integration |
| `pine/` | TradingView Pine Script | External tool code, not part of pipeline |
| `.github/workflows/main.yml` | Main workflow | Name too generic, purpose unclear |
| `specs/` (top-level) | Top-level specs folder | Exists but may be empty or duplicate of `docs/specs/` |

### GAPS / CONTRADICTIONS

| Issue | Classification |
|-------|----------------|
| `CLAIMS/` folder purpose and integration unclear | UNKNOWN |
| `releases/` contains only one markdown file | UNKNOWN PURPOSE |
| `pine/` is external tooling, not infrastructure | OUT OF SCOPE |

---

## CROSS-CATEGORY SUMMARY

### Categories Present in Repo
All 12 categories have at least some representation in the repository.

### Categories with Strong Implementation
- Pipelines (13 workflows, extensive scripts)
- Contracts (15+ contract documents)
- Artifacts & Evidence (extensive reports structure)
- Documentation & Maps (111+ docs)
- QA & Governance (134 tests, validation harness)

### Categories with Partial Implementation
- Models (C1/C2 complete, C3 incomplete)
- Sub-systems (Worker functional, trajectory_families partial)
- Registries (threshold registry complete, migration ledger unverified)

### Categories with Gaps
- Data Stores (schema drift, unverified migrations)
- Orchestration (missing scheduled pytest)
- Experiments (no actual notebooks)

---

*End of Category Process Appendix (Draft)*
