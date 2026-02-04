# Prune Plan v0.1

**Version**: 0.1
**Status**: PHASE 1.5 PRUNING ARTIFACT
**Date**: 2026-02-04

---

## Statement

This plan describes **mechanical pruning only**. No canonical operations (OP-A/B/C/D/QA) are changed, renamed, edited, or moved. No logic, imports, formatting, or behavior is modified. Only NON_CANONICAL (OP-NC) files classified as ARCHIVED or QUARANTINED in `ARCHIVE_NON_CANONICAL_v0.1.md` are relocated. LIBRARY-ONLY files are fenced in-place with README markers.

Governance artifacts (`OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md`, `OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md`, `OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md`, `PHASE_1_5_CLOSURE_DECLARATION.md`) are **NOT modified**.

---

## Pruning Actions

### ARCHIVED Files → `_archive/`

Files are moved verbatim (no content changes) to `_archive/` preserving relative directory structure.

| File Path | OP-NC ID | Action | Destination |
|-----------|----------|--------|-------------|
| `src/backfill_oanda_2h.py` | NC01 | MOVE | `_archive/src/backfill_oanda_2h.py` |
| `src/test_insert.py` | NC05 | MOVE | `_archive/src/test_insert.py` |
| `scripts/export/oanda_export_2h_day.py` | NC09 | MOVE | `_archive/scripts/export/oanda_export_2h_day.py` |
| `scripts/run/run_migration.py` | NC10 | MOVE | `_archive/scripts/run/run_migration.py` |
| `scripts/deploy/deploy_worker.ps1` | NC11 | MOVE | `_archive/scripts/deploy/deploy_worker.ps1` |
| `scripts/dev/check_dst_mapping.py` | NC12 | MOVE | `_archive/scripts/dev/check_dst_mapping.py` |
| `scripts/validate/pipeline_status.py` | NC13 | MOVE | `_archive/scripts/validate/pipeline_status.py` |
| `scripts/validate/validate_day.ps1` | NC14 | MOVE | `_archive/scripts/validate/validate_day.ps1` |
| `tools/validate_contract.py` | NC15 | MOVE | `_archive/tools/validate_contract.py` |
| `tools/validate_contract.ps1` | NC15 | MOVE | `_archive/tools/validate_contract.ps1` |
| `tools/parse_export.py` | NC15 | MOVE | `_archive/tools/parse_export.py` |
| `tools/maze/gen_repo_maze.py` | NC16 | MOVE | `_archive/tools/maze/gen_repo_maze.py` |
| `tools/maze/gen_repo_maze_curated.py` | NC16 | MOVE | `_archive/tools/maze/gen_repo_maze_curated.py` |
| `.codex/CHECKS/apply_graph_nodeid_renames.py` | NC18 | MOVE | `_archive/.codex/CHECKS/apply_graph_nodeid_renames.py` |
| `.codex/CHECKS/plan_graph_nodeid_renames.py` | NC18 | MOVE | `_archive/.codex/CHECKS/plan_graph_nodeid_renames.py` |
| `.codex/CHECKS/run_graph_nodeid_rename_plan.ps1` | NC18 | MOVE | `_archive/.codex/CHECKS/run_graph_nodeid_rename_plan.ps1` |
| `.codex/CHECKS/preflight_parse.ps1` | NC19 | MOVE | `_archive/.codex/CHECKS/preflight_parse.ps1` |
| `scripts/local/verify_local.ps1` | NC20 | MOVE | `_archive/scripts/local/verify_local.ps1` |
| `scripts/dev/pytest_win.ps1` | NC20 | MOVE | `_archive/scripts/dev/pytest_win.ps1` |
| `sql/derived_v0_1.sql` | NC21 | MOVE | `_archive/sql/derived_v0_1.sql` |
| `sql/schema_v01.sql` | NC23 | MOVE | `_archive/sql/schema_v01.sql` |
| `infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql` | NC25 | MOVE | `_archive/infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql` |

**Total ARCHIVED files: 22**

---

### QUARANTINED Files → `_quarantine/`

Files are moved verbatim (no content changes) to `_quarantine/` preserving relative directory structure.

| File Path | OP-NC ID | Action | Destination |
|-----------|----------|--------|-------------|
| `src/full_ingest_stub.py` | NC03 | MOVE | `_quarantine/src/full_ingest_stub.py` |
| `sql/10_views_research_v0.1.sql` | NC24 | MOVE | `_quarantine/sql/10_views_research_v0.1.sql` |
| `src/derived/compute_c3_stub_v0_1.py` | NC27 | MOVE | `_quarantine/src/derived/compute_c3_stub_v0_1.py` |
| `.github/workflows/ovc_full_ingest.yml` | NC28 | MOVE | `_quarantine/.github/workflows/ovc_full_ingest.yml` |

**Total QUARANTINED files: 4**

---

### LIBRARY-ONLY Files → Fence In-Place

These files are NOT moved. They remain at their current paths because canonical operations import from them. A `_LIBRARY_ONLY.md` README is placed in each containing directory to mark them as non-canonical infrastructure.

| File Path | OP-NC ID | Action | Fence |
|-----------|----------|--------|-------|
| `src/backfill_day.py` | NC02 | FENCE | `src/_LIBRARY_ONLY.md` |
| `src/ingest_history_day.py` | NC04 | FENCE | `src/_LIBRARY_ONLY.md` |
| `src/ovc_artifacts.py` | NC06 | FENCE | `src/_LIBRARY_ONLY.md` |
| `src/ovc_ops/run_artifact_cli.py` | NC07 | FENCE | `src/ovc_ops/_LIBRARY_ONLY.md` |
| `src/ovc_ops/run_artifact.py` | NC08 | FENCE | `src/ovc_ops/_LIBRARY_ONLY.md` |
| `src/utils/csv_locator.py` | NC17 | FENCE | `src/utils/_LIBRARY_ONLY.md` |
| `src/history_sources/tv_csv.py` | NC17 | FENCE | `src/history_sources/_LIBRARY_ONLY.md` |
| `sql/option_c_v0_1.sql` | NC22 | FENCE | `sql/_LIBRARY_ONLY.md` |
| `infra/ovc-webhook/test/index.spec.ts` | NC26 | FENCE | `infra/ovc-webhook/test/_LIBRARY_ONLY.md` |
| `infra/ovc-webhook/test/env.d.ts` | NC26 | FENCE | `infra/ovc-webhook/test/_LIBRARY_ONLY.md` |
| `src/config/__init__.py` | NC29 | FENCE | (structural — no README needed) |
| `src/derived/__init__.py` | NC29 | FENCE | (structural — no README needed) |
| `src/history_sources/__init__.py` | NC29 | FENCE | (structural — no README needed) |
| `src/ovc_ops/__init__.py` | NC29 | FENCE | (structural — no README needed) |
| `src/utils/__init__.py` | NC29 | FENCE | (structural — no README needed) |
| `src/validate/__init__.py` | NC29 | FENCE | (structural — no README needed) |

**Total LIBRARY-ONLY files: 16 (6 fence READMEs created, `__init__.py` files exempt)**

---

### Directory READMEs

| Directory | README | Content |
|-----------|--------|---------|
| `_archive/` | `_archive/README.md` | Marks directory as non-canonical archive. Lists disposition reference. |
| `_quarantine/` | `_quarantine/README.md` | Marks directory as quarantined non-canonical code. |

---

## Pre-Pruning Verification Checklist

- [ ] All ARCHIVED/QUARANTINED files verified as NOT imported by canonical operations
- [ ] All LIBRARY-ONLY files verified as IMPORTED by canonical operations
- [ ] No governance artifact is modified
- [ ] No canonical executable is moved, renamed, or edited
- [ ] CI workflows reference no ARCHIVED/QUARANTINED file (except OP-NC28 which IS a workflow)

## Post-Pruning Verification Checklist

- [ ] All canonical operations remain at original paths
- [ ] All canonical CI workflows (`backfill.yml`, `backfill_m15.yml`, `ci_pytest.yml`, `ci_schema_check.yml`, `ci_workflow_sanity.yml`, `backfill_then_validate.yml`, `ovc_option_c_schedule.yml`, `path1_evidence.yml`, `path1_evidence_queue.yml`, `path1_replay_verify.yml`, `notion_sync.yml`, `main.yml`) are unchanged
- [ ] LIBRARY-ONLY files remain importable at original paths
- [ ] `_archive/` and `_quarantine/` contain only OP-NC files
- [ ] No OP-NC file outside LIBRARY-ONLY is executable-by-default

---

*End of Prune Plan v0.1*
