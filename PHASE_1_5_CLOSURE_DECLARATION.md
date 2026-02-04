# Phase 1.5 Closure Declaration

**Version**: 1.0
**Date**: 2026-02-04
**Status**: **PASS WITH GAPS**

---

## What OVC IS at the End of Phase 1.5

OVC is a finite, auditable data pipeline system comprising:

- **31 canonical operations** organized under Options A (Canonical Ingest), B (Derived Features), C (Outcomes & Evaluation), D (Paths / Orchestration), and QA (Audit / Coverage / Validation).
- **29 non-canonical entries** covering legacy, scaffold, utility, and exploratory executables that exist in the repository but are not governed.
- **160 governance-relevant executables** (Python, PowerShell, Shell, TypeScript, SQL DDL/DML, CI workflows) — all mapped to exactly one operation.
- **~105 generated SQL run artifacts** (Path1 evidence study files) — classified as outputs of their generating operations (OP-D02/OP-D03).
- **0 orphan executables**.

The governance boundary is defined by three interlocking artifacts:
1. **Allowed Operations Catalog v0.1** — finite enumeration of every permitted operation.
2. **Enforcement Coverage Matrix v0.1** — measurable mapping of operations to enforcement surfaces and coverage levels.
3. **Governance Completeness Scorecard v0.1** — quantitative metrics derived from the above.

---

## Scope Statement

### In Scope (Governed)

| Option | Operations | Description |
|--------|-----------|-------------|
| A | OP-A01 through OP-A04 | Webhook bar ingest, OANDA 2H/M15 backfill, canonical schema DDL |
| B | OP-B01 through OP-B08 | C1/C2/C3 derived feature computation (materialized + views), threshold registry, derived validation |
| C | OP-C01, OP-C02 | Outcomes view (authoritative), Option C scheduled evaluation runner |
| D | OP-D01 through OP-D11 | Evidence pack build, Path1 range/queue runners, post-run validation, replay verification, seal manifests, state plane, trajectory families, overlays v0.3, queue resolution, Notion sync |
| QA | OP-QA01 through OP-QA06 | Canonical facts validation, CI pytest, CI schema check, CI workflow sanity, coverage audit, SQL QA packs |

### Explicitly Out of Scope

- **Path2**: Not implemented in v1. `docs/contracts/PATH2_CONTRACT_v1_0.md` exists as specification only. No Path2 executables or workflows exist.
- **ML/Heuristic Inference**: OVC is deterministic and descriptive per doctrine. No ML models, no optimization, no signal generation.
- **Strategy / Decision Logic**: Per `docs/doctrine/OVC_DOCTRINE.md`, OVC records truth — it does not prescribe action.
- **Cloudflare Worker Deployment Verification**: Deployment status is UNKNOWN from repo evidence. Code compiles and tests pass, but no deploy logs exist in the repository.
- **External System State**: Neon database actual state, Notion database sync state, OANDA API availability, and GitHub Secrets configuration are not verifiable from repository evidence alone.
- **Obsidian Vault** (`Tetsu/`): Documentation and navigation tool, not an operational component.
- **Research Artifacts** (`research/`): Exploratory studies and score templates. Not governed.

---

## What Exists but is NOT CANONICAL

| ID | Artifact | Reason |
|----|----------|--------|
| OP-NC01 | `src/backfill_oanda_2h.py` | Legacy (superseded by checkpointed version OP-A02) |
| OP-NC02 | `src/backfill_day.py` | Utility library (not standalone operation) |
| OP-NC03 | `src/full_ingest_stub.py` | Placeholder/stub (not fully implemented) |
| OP-NC04 | `src/ingest_history_day.py` | Exploratory |
| OP-NC05 | `src/test_insert.py` | Development utility |
| OP-NC06 | `src/ovc_artifacts.py` | Superseded by `src/ovc_ops/run_artifact.py` |
| OP-NC07 | `src/ovc_ops/run_artifact_cli.py` | CLI scaffold (supports canonical ops but is not an operation) |
| OP-NC08 | `src/ovc_ops/run_artifact.py` | Shared infrastructure library (RunWriter class) |
| OP-NC09 | `scripts/export/oanda_export_2h_day.py` | Development reference export |
| OP-NC10 | `scripts/run/run_migration.py` | Manual migration utility |
| OP-NC11 | `scripts/deploy/deploy_worker.ps1` | Deployment scaffold |
| OP-NC12 | `scripts/dev/check_dst_mapping.py` | Development DST verification tool |
| OP-NC13 | `scripts/validate/pipeline_status.py` | Utility library (not standalone) |
| OP-NC14 | `scripts/validate/validate_day.ps1` | Windows wrapper (convenience) |
| OP-NC15 | `tools/validate_contract.py`, `tools/validate_contract.ps1`, `tools/parse_export.py` | Development tools |
| OP-NC16 | `tools/maze/gen_repo_maze.py`, `tools/maze/gen_repo_maze_curated.py` | Documentation generators |
| OP-NC17 | `src/utils/csv_locator.py`, `src/history_sources/tv_csv.py` | Shared utility libraries |
| OP-NC18 | `.codex/CHECKS/apply_graph_nodeid_renames.py`, `plan_graph_nodeid_renames.py`, `run_graph_nodeid_rename_plan.ps1` | Governance canonicalization tools |
| OP-NC19 | `.codex/CHECKS/preflight_parse.ps1` | Codex preflight |
| OP-NC20 | `scripts/local/verify_local.ps1`, `scripts/dev/pytest_win.ps1` | Local development wrappers |
| OP-NC21 | `sql/derived_v0_1.sql` | DEPRECATED combined view (superseded by C1/C2/C3 split) |
| OP-NC22 | `sql/option_c_v0_1.sql` (deprecated view) | DEPRECATED outcomes view (reads canonical table directly) |
| OP-NC23 | `sql/schema_v01.sql` | Historical schema (superseded) |
| OP-NC24 | `sql/10_views_research_v0.1.sql` | Research/analytical views (exploratory) |
| OP-NC25 | `infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql` | Non-MIN webhook DDL |
| OP-NC26 | `infra/ovc-webhook/test/index.spec.ts`, `env.d.ts` | Test infrastructure (supports OP-A01) |
| OP-NC27 | `src/derived/compute_c3_stub_v0_1.py` | Dormant experimental C3 alternative |
| OP-NC28 | `.github/workflows/ovc_full_ingest.yml` | Dormant workflow (stub) |
| OP-NC29 | `__init__.py` files (7 total) | Python package structure |

---

## Governance Metrics Summary

| Metric | Value |
|--------|-------|
| Executable Mapping Coverage | 100.0% (160/160) |
| Operation Evidence Coverage | 100.0% (31/31) |
| Enforcement Coverage (C3+) | 83.9% (26/31) |
| Orphan Rate | 0 |
| Weak Governance Operations (C2) | 5 (16.1%) |
| Fully Governed (C5) | 4 (12.9%) |

---

## Phase 1.5 Status: PASS WITH GAPS

### Determination Rationale

**NOT FAIL because:**
- All executables are mapped (0 orphans)
- Option A operations have evidence (OP-A01 through OP-A04 all at C3+)
- Option D operations have evidence (OP-D01 through OP-D11 mapped with evidence anchors; OP-D01/D02/D03 at C4+)
- Governance boundary is finite and auditable

**NOT PASS because:**
- 5 operations remain at C2 (runtime-only, no CI gate): OP-D06, OP-D07, OP-D10, OP-QA05, OP-QA06
- OP-B04 (C3 materialized) has incomplete CI workflow integration (missing CLI args in `backfill_then_validate.yml`)
- `schema/applied_migrations.json` entries are all UNVERIFIED
- Worker deployment status UNKNOWN from repo evidence
- Enforcement coverage is 83.9%, below the 100% ideal but above minimum viable threshold

### Bounded Gaps

| Gap | Impact | Bounded? |
|-----|--------|----------|
| 5 ops at C2 | No CI gate; manual invocation only | YES — all have runtime validation; none are in critical data path (A→B→C) |
| C3 workflow args | C3 materialized compute cannot run via CI | YES — CLI invocation works; documented in Option B contract |
| Migration ledger UNVERIFIED | Cannot prove when migrations were applied | YES — CI schema check verifies object existence regardless |
| Worker deployment UNKNOWN | Cannot prove live ingest operates | YES — code compiles, tests pass; deployment is external infrastructure |
| C3 view has no unit tests | C3 view semantic correctness untested | YES — view is stateless SQL with hardcoded thresholds; schema existence verified by CI |

All gaps are documented, bounded in scope, and do not compromise the integrity of the canonical data path (A→B→C→D).

---

## Closure Artifacts Produced

| Artifact | File | Purpose |
|----------|------|---------|
| Allowed Operations Catalog v0.1 | `OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md` | Finite operation enumeration |
| Enforcement Coverage Matrix v0.1 | `OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md` | Measurable enforcement mapping |
| Governance Completeness Scorecard v0.1 | `OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md` | Quantitative governance metrics |
| Phase 1.5 Closure Declaration | `PHASE_1_5_CLOSURE_DECLARATION.md` | This document |

---

*End of Phase 1.5 Closure Declaration*
