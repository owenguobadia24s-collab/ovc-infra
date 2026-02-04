# Archive Non-Canonical Operations v0.1

**Version**: 0.1
**Status**: PHASE 1.5 PRUNING ARTIFACT
**Date**: 2026-02-04

---

## Purpose

This document records the classification and disposition of all 29 OP-NC (NON_CANONICAL) entries from the Allowed Operations Catalog v0.1. Each entry is assigned exactly one status:

| Status | Meaning | Action |
|--------|---------|--------|
| ARCHIVED | Superseded, historical, or development-only. No canonical dependency. | Move to `_archive/` |
| QUARANTINED | Dormant, stub, unsafe, or future. No canonical dependency. | Move to `_quarantine/` |
| LIBRARY-ONLY | Import-only infrastructure used by canonical operations. No standalone entrypoint governance. | Fence in-place (no move). |

---

## Classification Table

| ID | Path(s) | Status | Rationale | Canonical Replacement |
|----|---------|--------|-----------|-----------------------|
| OP-NC01 | `src/backfill_oanda_2h.py` | ARCHIVED | Legacy backfill without checkpoint resumption. | OP-A02 (`src/backfill_oanda_2h_checkpointed.py`) |
| OP-NC02 | `src/backfill_day.py` | LIBRARY-ONLY | Utility library imported by canonical OP-QA01 (`validate_day.py`, `validate_range.py`). | None — shared infrastructure |
| OP-NC03 | `src/full_ingest_stub.py` | QUARANTINED | Placeholder stub; not fully implemented. | None |
| OP-NC04 | `src/ingest_history_day.py` | LIBRARY-ONLY | Historical ingest helper imported by canonical OP-QA01 (`validate_day.py`). | None — shared infrastructure |
| OP-NC05 | `src/test_insert.py` | ARCHIVED | Development test insert utility. No canonical import. | None |
| OP-NC06 | `src/ovc_artifacts.py` | LIBRARY-ONLY | Early-gen artifact helper; `make_run_dir`, `write_meta`, `write_latest` imported by OP-QA01 (`validate_range.py`) and OP-B08 (`validate_derived_range_v0_1.py`). | Partially by OP-NC08 (`RunWriter`), but direct imports remain. |
| OP-NC07 | `src/ovc_ops/run_artifact_cli.py` | LIBRARY-ONLY | CLI wrapper called by canonical OP-C02 (`run_option_c_with_artifact.sh`). | None — CLI scaffold |
| OP-NC08 | `src/ovc_ops/run_artifact.py` | LIBRARY-ONLY | Core `RunWriter` class imported by OP-A02, OP-A03, OP-B01, OP-B02, OP-B04, OP-B08, OP-C02, OP-D11, OP-QA01. | None — foundational infrastructure |
| OP-NC09 | `scripts/export/oanda_export_2h_day.py` | ARCHIVED | Development OANDA export utility. No canonical import. | None |
| OP-NC10 | `scripts/run/run_migration.py` | ARCHIVED | Manual SQL migration runner. No canonical import. | None |
| OP-NC11 | `scripts/deploy/deploy_worker.ps1` | ARCHIVED | Deployment scaffold for Cloudflare Worker. No canonical import. | None |
| OP-NC12 | `scripts/dev/check_dst_mapping.py` | ARCHIVED | Development DST boundary verification tool. No canonical import. | None |
| OP-NC13 | `scripts/validate/pipeline_status.py` | ARCHIVED | Pipeline status utility. Not imported by any canonical script. | None |
| OP-NC14 | `scripts/validate/validate_day.ps1` | ARCHIVED | Windows PowerShell wrapper for `validate_day.py`. No canonical import. | OP-QA01 (`validate_day.py`) directly |
| OP-NC15 | `tools/validate_contract.py`, `tools/validate_contract.ps1`, `tools/parse_export.py` | ARCHIVED | Development contract validation and export parsing tools. No canonical import. | None |
| OP-NC16 | `tools/maze/gen_repo_maze.py`, `tools/maze/gen_repo_maze_curated.py` | ARCHIVED | Repository structure visualization generators. No canonical import. | None |
| OP-NC17 | `src/utils/csv_locator.py`, `src/history_sources/tv_csv.py` | LIBRARY-ONLY | CSV locator and TradingView parser imported by canonical OP-QA01 (`validate_day.py`). | None — shared infrastructure |
| OP-NC18 | `.codex/CHECKS/apply_graph_nodeid_renames.py`, `.codex/CHECKS/plan_graph_nodeid_renames.py`, `.codex/CHECKS/run_graph_nodeid_rename_plan.ps1` | ARCHIVED | Governance canonicalization tools. One-time use completed. | None |
| OP-NC19 | `.codex/CHECKS/preflight_parse.ps1` | ARCHIVED | Codex preflight validation. No canonical import. | None |
| OP-NC20 | `scripts/local/verify_local.ps1`, `scripts/dev/pytest_win.ps1` | ARCHIVED | Local development verification and Windows pytest wrappers. | None |
| OP-NC21 | `sql/derived_v0_1.sql` | ARCHIVED | Deprecated combined derived features view. | OP-B05 (split C1/C2/C3 views) |
| OP-NC22 | `sql/option_c_v0_1.sql` | LIBRARY-ONLY | Loaded at runtime by canonical OP-C02 runners (`run_option_c.sh`, `run_option_c.ps1`). Creates deprecated `derived.ovc_outcomes_v0_1` view. | OP-C01 (`v_ovc_c_outcomes_v0_1.sql`) is authoritative, but this SQL is still executed. |
| OP-NC23 | `sql/schema_v01.sql` | ARCHIVED | Historical v0.1 schema definition. | OP-A04 (current schema DDL) |
| OP-NC24 | `sql/10_views_research_v0.1.sql` | QUARANTINED | Research/analytical views (pattern outcomes, transition stats, session heatmaps). Exploratory. | None |
| OP-NC25 | `infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql` | ARCHIVED | Non-MIN webhook detail table DDL. Not part of canonical MIN flow. | OP-A01 uses MIN schema only |
| OP-NC26 | `infra/ovc-webhook/test/index.spec.ts`, `infra/ovc-webhook/test/env.d.ts` | LIBRARY-ONLY | Test infrastructure for canonical OP-A01. Listed as evidence anchor. | None — test support |
| OP-NC27 | `src/derived/compute_c3_stub_v0_1.py` | QUARANTINED | Dormant experimental C3 alternative. Not integrated into any workflow or test. | OP-B04 (`compute_c3_regime_trend_v0_1.py`) |
| OP-NC28 | `.github/workflows/ovc_full_ingest.yml` | QUARANTINED | Dormant full ingest workflow stub. Manual dispatch only. | None |
| OP-NC29 | `src/config/__init__.py`, `src/derived/__init__.py`, `src/history_sources/__init__.py`, `src/ovc_ops/__init__.py`, `src/utils/__init__.py`, `src/validate/__init__.py` | LIBRARY-ONLY | Python package `__init__.py` files. Required for all imports from these packages by canonical operations. | None — structural |

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ARCHIVED | 15 | NC01, NC05, NC09, NC10, NC11, NC12, NC13, NC14, NC15, NC16, NC18, NC19, NC20, NC21, NC23, NC25 |
| QUARANTINED | 4 | NC03, NC24, NC27, NC28 |
| LIBRARY-ONLY | 10 | NC02, NC04, NC06, NC07, NC08, NC17, NC22, NC26, NC29 |
| **Total** | **29** | — |

**Note**: ARCHIVED count is 16 (NC15 has 3 files, NC16 has 2 files, NC18 has 3 files, NC20 has 2 files — but these are single OP-NC entries with multiple files).

---

## Constraint Verification

- No ARCHIVED or QUARANTINED file is imported by any canonical operation.
- All LIBRARY-ONLY files have verified import chains from canonical operations.
- Moving LIBRARY-ONLY files would break canonical behavior — they are fenced in-place only.
- Governance artifacts (AOC, ECM, GCS, Phase 1.5 Closure) are NOT modified.

---

*End of Archive Non-Canonical Operations v0.1*
