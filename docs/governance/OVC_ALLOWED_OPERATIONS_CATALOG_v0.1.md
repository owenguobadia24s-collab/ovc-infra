# OVC Allowed Operations Catalog v0.1

**Version**: 0.1
**Status**: PHASE 1.5 GOVERNANCE ARTIFACT
**Date**: 2026-02-04

---

## Option A — Canonical Ingest

---

### OP-A01: Webhook Bar Ingest (A1)

Operation ID: OP-A01
Option: A
Purpose: Receive TradingView webhook payloads, validate against MIN export contract, and upsert 2H OHLC blocks into canonical facts table.
Bound Executables:
- `infra/ovc-webhook/src/index.ts`
Inputs:
- TradingView webhook POST payload (pipe-delimited export string)
- `contracts/export_contract_v0.1.1_min.json` (MIN schema)
Outputs:
- `ovc.ovc_blocks_v01_1_min` (upsert rows)
- R2 bucket `ovc-raw-events` (raw payload archive)
Determinism Rules:
- Same `block_id` produces same row (idempotent upsert)
- OHLC sanity: h >= max(o,c), l <= min(o,c)
- Duplicate `block_id` rejected
Failure Modes:
- Invalid token → 401
- Schema mismatch → 400
- OHLC sanity violation → row rejected
- R2 write failure → logged
Enforcement Surfaces: E1, E3, E6
Evidence Anchors:
- `infra/ovc-webhook/src/index.ts`
- `infra/ovc-webhook/test/index.spec.ts` (2 tests PASS)
- `contracts/export_contract_v0.1.1_min.json`
- `docs/contracts/option_a1_bar_ingest_contract_v1.md`
- `docs/contracts/option_a_ingest_contract_v1.md`

---

### OP-A02: OANDA 2H Backfill (Checkpointed)

Operation ID: OP-A02
Option: A
Purpose: Backfill 2H OHLC blocks from OANDA REST API with checkpoint-based resumption into canonical facts table.
Bound Executables:
- `src/backfill_oanda_2h_checkpointed.py`
Inputs:
- OANDA REST API (H1 candles)
- Environment: NEON_DSN, OANDA_API_TOKEN, OANDA_ENV
Outputs:
- `ovc.ovc_blocks_v01_1_min` (upsert rows)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- Same date range + same OANDA data → identical rows
- Upsert semantics (idempotent)
Failure Modes:
- OANDA API unavailable → run fails
- Checkpoint corruption → resumes from last good state
- DSN invalid → connection error
Enforcement Surfaces: E1, E4, E6, E7
Evidence Anchors:
- `src/backfill_oanda_2h_checkpointed.py`
- `.github/workflows/backfill.yml` (schedule: `0 */6 * * *`)
- `contracts/run_artifact_spec_v0.1.json`
- `docs/contracts/option_a_ingest_contract_v1.md`

---

### OP-A03: OANDA M15 Backfill (Checkpointed)

Operation ID: OP-A03
Option: A
Purpose: Backfill M15 raw candles from OANDA REST API into canonical M15 table for evidence overlay use.
Bound Executables:
- `src/backfill_oanda_m15_checkpointed.py`
Inputs:
- OANDA REST API (M15 candles)
- Environment: NEON_DSN, OANDA_API_TOKEN, OANDA_ENV
Outputs:
- `ovc.ovc_candles_m15_raw` (upsert rows)
Determinism Rules:
- Same date range + same OANDA data → identical rows
- Upsert by composite PK `(sym, bar_start_ms)`
Failure Modes:
- OANDA API unavailable → run fails
- DSN invalid → connection error
Enforcement Surfaces: E1, E4, E6
Evidence Anchors:
- `src/backfill_oanda_m15_checkpointed.py`
- `.github/workflows/backfill_m15.yml` (manual dispatch)
- `docs/contracts/option_a2_event_ingest_contract_v1.md`
- `sql/path1/db_patches/patch_m15_raw_20260122.sql`

---

### OP-A04: Schema DDL (Canonical Tables)

Operation ID: OP-A04
Option: A
Purpose: Define and create canonical database schemas and tables (base schemas, blocks table, M15 table, run reports).
Bound Executables:
- `sql/00_schema.sql`
- `sql/01_tables_min.sql`
- `sql/02_tables_run_reports.sql`
- `sql/03_tables_outcomes.sql`
- `sql/path1/db_patches/patch_m15_raw_20260122.sql`
Inputs:
- Database connection (Neon)
Outputs:
- Schemas: `ovc`, `derived`, `ovc_cfg`, `ops`, `ovc_qa`
- Tables: `ovc.ovc_blocks_v01_1_min`, `ovc.ovc_candles_m15_raw`, `ovc.ovc_run_reports_v01`, `ovc.ovc_outcomes_v01`
Determinism Rules:
- DDL is idempotent (IF NOT EXISTS)
- Schema frozen under governance rules v0.1
Failure Modes:
- Schema already exists → no-op
- Permission denied → migration fails
Enforcement Surfaces: E1, E4, E5, E6
Evidence Anchors:
- `schema/applied_migrations.json`
- `docs/governance/GOVERNANCE_RULES_v0.1.md` (FROZEN status)
- `.github/workflows/ci_schema_check.yml`

---

## Option B — Derived Features

---

### OP-B01: Compute C1 Features (Single-Bar)

Operation ID: OP-B01
Option: B
Purpose: Compute single-bar OHLC primitives (body_ratio, wick ratios, positions, flags) from canonical facts into materialized C1 table.
Bound Executables:
- `src/derived/compute_c1_v0_1.py`
Inputs:
- `ovc.ovc_blocks_v01_1_min` (authoritative fields only per A1 allowlist)
Outputs:
- `derived.ovc_c1_features_v0_1` (materialized table)
- `derived.derived_runs_v0_1` (run provenance row)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- `f(o,h,l,c) → identical output` for all time
- formula_hash tracked per run
- No lookback, no rolling windows
Failure Modes:
- Zero-range bar → ratios return NULL, booleans return FALSE
- Missing OHLC → `inputs_valid = false`
Enforcement Surfaces: E1, E2, E3, E4, E5, E7
Evidence Anchors:
- `src/derived/compute_c1_v0_1.py`
- `sql/02_derived_c1_c2_tables_v0_1.sql:47-72`
- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `tests/test_derived_features.py` (C1 determinism, correctness, formula hash)
- `tests/test_validate_derived.py` (compute_c1_inline)
- `.github/workflows/backfill_then_validate.yml` (Step 3)
- `docs/contracts/option_b_derived_contract_v1.md`

---

### OP-B02: Compute C2 Features (Multi-Bar Context)

Operation ID: OP-B02
Option: B
Purpose: Compute multi-bar context features (rolling averages, streaks, session stats, rank) with explicit window_spec from canonical facts.
Bound Executables:
- `src/derived/compute_c2_v0_1.py`
Inputs:
- `ovc.ovc_blocks_v01_1_min` (authoritative fields only per A1 allowlist)
Outputs:
- `derived.ovc_c2_features_v0_1` (materialized table)
- `derived.derived_runs_v0_1` (run provenance row)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- `f(ohlc_sequence, window_spec) → identical output` given same ordering
- formula_hash + window_spec tracked per run
- Explicit window: N=1, session=date_ny, N=12, parameterized=rd_len
Failure Modes:
- Partial window (fewer than N bars) → NULL
- Missing prev block → gap detection defaults
Enforcement Surfaces: E1, E2, E3, E4, E5, E7
Evidence Anchors:
- `src/derived/compute_c2_v0_1.py`
- `sql/02_derived_c1_c2_tables_v0_1.sql:88-130`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `tests/test_derived_features.py` (C2 determinism, correctness, formula hash)
- `.github/workflows/backfill_then_validate.yml` (Step 4)
- `docs/contracts/option_b_derived_contract_v1.md`

---

### OP-B03: Compute C3 Features (Semantic Tags — View)

Operation ID: OP-B03
Option: B
Purpose: Compute semantic classification tags (trend_bias, volatility_regime, structure_type, etc.) via SQL view reading only from C1/C2 views.
Bound Executables:
- `sql/derived/v_ovc_c3_features_v0_1.sql`
Inputs:
- `derived.v_ovc_c1_features_v0_1` (C1 view)
- `derived.v_ovc_c2_features_v0_1` (C2 view)
Outputs:
- `derived.v_ovc_c3_features_v0_1` (SQL view, stateless)
Determinism Rules:
- All thresholds hardcoded in SQL CASE expressions
- Exactly one label per feature per block (mutual exclusivity)
- No direct read from `ovc.ovc_blocks_v01_1_min`
Failure Modes:
- C1/C2 views unavailable → query error
- NULL C1/C2 inputs → NULL classification propagated
Enforcement Surfaces: E1, E4, E6
Evidence Anchors:
- `sql/derived/v_ovc_c3_features_v0_1.sql`
- `docs/contracts/option_b_derived_contract_v1.md` (section 3.2)
- `docs/contracts/c3_semantic_contract_v0_1.md`
- `.github/workflows/ci_schema_check.yml`

---

### OP-B04: Compute C3 Regime Trend (Materialized — Threshold Pack)

Operation ID: OP-B04
Option: B
Purpose: Compute materialized C3 regime trend classification (TREND/NON_TREND) from versioned threshold packs with full provenance.
Bound Executables:
- `src/derived/compute_c3_regime_trend_v0_1.py`
Inputs:
- `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1` (via C1/C2 tables)
- `ovc_cfg.threshold_pack` (versioned threshold configuration)
- `ovc_cfg.threshold_pack_active` (active version pointer)
Outputs:
- `derived.ovc_c3_regime_trend_v0_1` (materialized table)
- `derived.derived_runs_v0_1` (run provenance row)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- Same inputs + same threshold_pack (id, version, hash) = identical output
- `c3_regime_trend` constrained to CHECK IN ('TREND','NON_TREND')
- threshold_pack_hash is SHA256 of config_json
Failure Modes:
- Missing threshold pack → script error
- Workflow invocation missing `--threshold-pack` and `--scope` args → INCOMPLETE (known issue)
- No CI workflow integration → CLI only
Enforcement Surfaces: E1, E2, E3, E7
Evidence Anchors:
- `src/derived/compute_c3_regime_trend_v0_1.py`
- `sql/05_c3_regime_trend_v0_1.sql`
- `sql/04_threshold_registry_v0_1.sql`
- `tests/test_c3_regime_trend.py` (20 tests, 19 pass, 1 skip)
- `docs/contracts/option_b_derived_contract_v1.md` (section 5.1 known issue)

---

### OP-B05: C1/C2/C3 View DDL (Authoritative Interface)

Operation ID: OP-B05
Option: B
Purpose: Define authoritative SQL views for C1, C2, C3 derived features as the canonical read interface for downstream Options.
Bound Executables:
- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `sql/derived/v_ovc_c3_features_v0_1.sql`
Inputs:
- `ovc.ovc_blocks_v01_1_min` (C1, C2 views)
- `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1` (C3 view)
Outputs:
- `derived.v_ovc_c1_features_v0_1` (VIEW)
- `derived.v_ovc_c2_features_v0_1` (VIEW)
- `derived.v_ovc_c3_features_v0_1` (VIEW)
Determinism Rules:
- Views are stateless; output determined entirely by underlying data
- C3 view reads ONLY from C1/C2 views (not canonical table)
Failure Modes:
- Base table missing → view creation fails
- Column rename → cascading view failure
Enforcement Surfaces: E1, E4, E6
Evidence Anchors:
- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `sql/derived/v_ovc_c3_features_v0_1.sql`
- `schema/applied_migrations.json`
- `.github/workflows/ci_schema_check.yml`

---

### OP-B06: Derived Table DDL (C1/C2 Materialized + Runs)

Operation ID: OP-B06
Option: B
Purpose: Define materialized derived tables for C1/C2 features and run provenance tracking.
Bound Executables:
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `sql/05_c3_regime_trend_v0_1.sql`
Inputs:
- Database connection
Outputs:
- `derived.derived_runs_v0_1` (run provenance table)
- `derived.ovc_c1_features_v0_1` (materialized C1)
- `derived.ovc_c2_features_v0_1` (materialized C2)
- `derived.ovc_c3_regime_trend_v0_1` (materialized C3)
Determinism Rules:
- DDL is idempotent (IF NOT EXISTS)
Failure Modes:
- Schema `derived` missing → creation fails
Enforcement Surfaces: E1, E4, E6
Evidence Anchors:
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `sql/05_c3_regime_trend_v0_1.sql`
- `schema/applied_migrations.json`

---

### OP-B07: Threshold Registry Management

Operation ID: OP-B07
Option: B
Purpose: Manage immutable versioned threshold packs for C3 regime classification with append-only semantics.
Bound Executables:
- `sql/04_threshold_registry_v0_1.sql`
- `sql/06_state_plane_threshold_pack_v0_2.sql`
- `src/config/threshold_registry_v0_1.py`
- `src/config/threshold_registry_cli.py`
Inputs:
- Threshold configuration JSON
- Database connection
Outputs:
- `ovc_cfg.threshold_pack` (immutable pack rows)
- `ovc_cfg.threshold_pack_active` (active version pointer)
Determinism Rules:
- Packs are immutable once created (append-only)
- `config_hash` is SHA256 of `config_json`
- Status progression: DRAFT → ACTIVE → DEPRECATED (no reversal)
Failure Modes:
- Duplicate (pack_id, pack_version) → conflict error
- Hash mismatch → integrity violation
Enforcement Surfaces: E1, E2, E3, E6
Evidence Anchors:
- `sql/04_threshold_registry_v0_1.sql`
- `src/config/threshold_registry_v0_1.py`
- `tests/test_threshold_registry.py`
- `configs/threshold_packs/c3_regime_trend_v1.json`
- `configs/threshold_packs/state_plane_v0_2_default_v1.json`

---

### OP-B08: Derived Validation (B.2)

Operation ID: OP-B08
Option: B
Purpose: Validate C1/C2/C3 derived features for coverage parity, key uniqueness, null rates, determinism, and provenance.
Bound Executables:
- `src/validate/validate_derived_range_v0_1.py`
Inputs:
- `derived.ovc_c1_features_v0_1`, `derived.ovc_c2_features_v0_1` (materialized tables)
- `derived.ovc_c3_regime_trend_v0_1` (materialized table)
- `ovc.ovc_blocks_v01_1_min` (reference count)
Outputs:
- `derived_validation_report.json`, `derived_validation_report.md`
- `derived_validation_diffs.csv` (optional)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- Same database state → identical report
Failure Modes:
- Coverage parity mismatch → FAIL
- Duplicate block_id → FAIL
- NaN/Inf detected → FAIL
Enforcement Surfaces: E1, E2, E3, E4, E5, E7
Evidence Anchors:
- `src/validate/validate_derived_range_v0_1.py`
- `sql/03_qa_derived_validation_v0_1.sql`
- `tests/test_validate_derived.py` (50 tests)
- `.github/workflows/backfill_then_validate.yml` (Step 5)
- `docs/contracts/option_b_derived_contract_v1.md` (section 6)

---

## Option C — Outcomes & Evaluation

---

### OP-C01: Outcomes View (Authoritative)

Operation ID: OP-C01
Option: C
Purpose: Compute forward-looking outcomes (fwd_ret, MFE, MAE, rvol) via SQL view reading only from Option B derived views.
Bound Executables:
- `sql/derived/v_ovc_c_outcomes_v0_1.sql`
Inputs:
- `derived.v_ovc_c1_features_v0_1`
- `derived.v_ovc_c2_features_v0_1`
- `derived.v_ovc_c3_features_v0_1`
Outputs:
- `derived.v_ovc_c_outcomes_v0_1` (VIEW)
Determinism Rules:
- View is stateless; output determined by underlying data
- Reads ONLY from B views (not canonical table)
- NULL if anchor close is zero/NULL or insufficient forward bars
Failure Modes:
- B views unavailable → query error
- Insufficient forward data → NULL outcomes (not sentinel values)
Enforcement Surfaces: E1, E4, E6
Evidence Anchors:
- `sql/derived/v_ovc_c_outcomes_v0_1.sql`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `.github/workflows/ci_schema_check.yml`
- `schema/applied_migrations.json`

---

### OP-C02: Option C Runner (Scheduled Evaluation)

Operation ID: OP-C02
Option: C
Purpose: Execute daily scheduled Option C evaluation: apply outcomes SQL, run spotchecks, generate run reports.
Bound Executables:
- `scripts/run/run_option_c.sh`
- `scripts/run/run_option_c_with_artifact.sh`
- `scripts/run/run_option_c_wrapper.py`
- `scripts/run/run_option_c.ps1`
Inputs:
- Database connection (DATABASE_URL)
- `sql/option_c_v0_1.sql` (outcomes computation)
- `sql/option_c_spotchecks.sql` (QA checks)
- `sql/option_c_run_report.sql` (report generation)
Outputs:
- `derived.eval_runs` (run metadata row)
- `derived.ovc_outcomes_v0_1` (legacy view — DEPRECATED)
- `reports/runs/<run_id>/run.json`, `checks.json`
- Run report JSON
Determinism Rules:
- Same database state + same code → identical outcomes
- formula_hash tracked in eval_runs
Failure Modes:
- Spotcheck WARN in non-strict → continue (exit 0)
- Spotcheck FAIL → exit >1
- Missing DATABASE_URL → abort
Enforcement Surfaces: E1, E2, E4, E5, E7
Evidence Anchors:
- `scripts/run/run_option_c.sh`
- `.github/workflows/ovc_option_c_schedule.yml` (schedule: `15 6 * * *`)
- `sql/option_c_v0_1.sql`
- `sql/option_c_spotchecks.sql`
- `sql/option_c_run_report.sql`
- `contracts/eval_contract_v0.1.json`

---

## Option D — Paths / Orchestration

---

### OP-D01: Path1 Evidence Pack Build (v0.2)

Operation ID: OP-D01
Option: D
Purpose: Build deterministic evidence packs with M15 overlay, QC checks, data/build manifests, and SHA256 hashes for auditability.
Bound Executables:
- `scripts/path1/build_evidence_pack_v0_2.py`
Inputs:
- `derived.v_path1_evidence_dis_v1_1` (joined scores + outcomes)
- `ovc.ovc_blocks_v01_1_min` (spine)
- `ovc.ovc_candles_m15_raw` (M15 overlay)
Outputs:
- `reports/path1/evidence/runs/<run_id>/outputs/evidence_pack_v0_2/`
  - `backbone_2h.csv`, `strips/2h/*.csv`, `context/4h/*.csv`
  - `meta.json`, `qc_report.json`
  - `data_manifest.json`, `data_sha256.txt`
  - `build_manifest.json`, `build_sha256.txt`
Determinism Rules:
- Same DB state + run_id + sym + date range → identical `data_sha256`
- `build_sha256` may vary (timestamps in meta)
- M15 strips: exactly 8 candles per 2H block
Failure Modes:
- M15 strip count != 8 → QC warning/fail
- Aggregation mismatch (M15→2H) beyond tolerance → QC fail
- Missing M15 data → incomplete pack
Enforcement Surfaces: E1, E2, E3, E5, E7
Evidence Anchors:
- `scripts/path1/build_evidence_pack_v0_2.py`
- `docs/evidence_pack/EVIDENCE_PACK_v0_2.md`
- `docs/contracts/option_d_evidence_contract_v1.md`
- `reports/path1/evidence/runs/*/outputs/evidence_pack_v0_2/` (existing artifacts)

---

### OP-D02: Path1 Evidence Range Runner

Operation ID: OP-D02
Option: D
Purpose: Execute date-range evidence runs producing observation reports (DIS/RES/LID scores), SQL studies, and evidence pack artifacts.
Bound Executables:
- `scripts/path1/run_evidence_range.py`
Inputs:
- Database connection (NEON_DSN)
- Symbol, start_date, end_date (or length_days)
Outputs:
- `reports/path1/evidence/runs/<run_id>/RUN.md`
- `reports/path1/evidence/runs/<run_id>/*_evidence.md`
- `sql/path1/evidence/runs/<run_id>/study_*.sql`
- Evidence pack v0.2 artifacts
Determinism Rules:
- Same inputs + same DB state → same evidence observations
- Scores are FROZEN (DIS v1.1, RES v1.0, LID v1.0)
Failure Modes:
- Missing data for date range → partial evidence
- SQL study execution failure → logged error
Enforcement Surfaces: E1, E2, E4, E5, E7
Evidence Anchors:
- `scripts/path1/run_evidence_range.py`
- `.github/workflows/path1_evidence.yml` (schedule: `15 3 * * *`)
- `docs/contracts/option_d_evidence_contract_v1.md`
- `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md`

---

### OP-D03: Path1 Evidence Queue Runner

Operation ID: OP-D03
Option: D
Purpose: Mechanically execute queued evidence runs from RUN_QUEUE.csv with post-run validation, PR creation, and ledger updates.
Bound Executables:
- `scripts/path1/run_evidence_queue.py`
Inputs:
- `reports/path1/evidence/RUN_QUEUE.csv`
- Database connection (NEON_DSN)
Outputs:
- Evidence artifacts per queued run
- `reports/path1/evidence/INDEX.md` (append-only canonical ledger)
- Pull request (via OVC_PR_BOT_TOKEN)
Determinism Rules:
- Queue is processed in order; each run is deterministic
- Date format validation rejects Excel-corrupted dates
Failure Modes:
- Post-run validation failure → blocks PR
- Empty queue → NOOP
- Invalid date format → run skipped
Enforcement Surfaces: E1, E2, E4, E5, E7
Evidence Anchors:
- `scripts/path1/run_evidence_queue.py`
- `.github/workflows/path1_evidence_queue.yml`
- `.github/workflows/main.yml` (schedule: `0 */6 * * *`)
- `reports/path1/evidence/RUN_QUEUE.csv`

---

### OP-D04: Path1 Post-Run Validation

Operation ID: OP-D04
Option: D
Purpose: Validate structural integrity of completed Path1 evidence runs (file existence, size bounds, fatal markers, manifest presence).
Bound Executables:
- `scripts/path1/validate_post_run.py`
Inputs:
- `reports/path1/evidence/runs/<run_id>/` (run directory)
Outputs:
- Violation report (stdout or JSON)
- Exit code: 0=PASS, 1=FAIL
Determinism Rules:
- Same file system state → identical validation result
Failure Modes:
- Missing RUN.md → FAIL
- File < MIN_OUTPUT_BYTES (200) → FAIL
- Fatal markers in output → FAIL
Enforcement Surfaces: E2, E4, E5
Evidence Anchors:
- `scripts/path1/validate_post_run.py`
- `.github/workflows/path1_evidence_queue.yml` (post-run gate)

---

### OP-D05: Path1 Replay Verification

Operation ID: OP-D05
Option: D
Purpose: Verify structural integrity of existing Path1 runs via read-only replay (run folder, RUN.md, date range, index cross-reference).
Bound Executables:
- `scripts/path1_replay/run_replay_verification.py`
- `scripts/path1_replay/lib.py`
Inputs:
- `reports/path1/evidence/runs/` (run directories)
- `reports/path1/evidence/INDEX.md` (canonical ledger)
Outputs:
- Replay report (stdout or `artifacts/path1_replay_report.json`)
- Exit code: 0=OK, 2=failure, 3=error
Determinism Rules:
- Read-only; does not modify any files
Failure Modes:
- run_folder_missing → structural violation
- date_range_missing → metadata violation
- Index reference missing → ledger gap
Enforcement Surfaces: E2, E4, E5
Evidence Anchors:
- `scripts/path1_replay/run_replay_verification.py`
- `.github/workflows/path1_replay_verify.yml` (schedule: `0 3 * * *`)

---

### OP-D06: Path1 Seal Manifests

Operation ID: OP-D06
Option: D
Purpose: Create append-only MANIFEST.sha256 per evidence run as immutability seal.
Bound Executables:
- `scripts/path1_seal/run_seal_manifests.py`
- `scripts/path1_seal/lib.py`
Inputs:
- `reports/path1/evidence/runs/<run_id>/` (run directory)
Outputs:
- `MANIFEST.sha256` per run directory
Determinism Rules:
- Idempotent (skips if manifest already exists)
- SHA256 of file contents
Failure Modes:
- Permission error on write → FAIL
Enforcement Surfaces: E2, E5, E7
Evidence Anchors:
- `scripts/path1_seal/run_seal_manifests.py`

---

### OP-D07: Path1 State Plane Trajectory

Operation ID: OP-D07
Option: D
Purpose: Generate per-day state plane trajectory artifacts from derived state plane view for observation and cataloging.
Bound Executables:
- `scripts/path1/run_state_plane.py`
Inputs:
- `derived.v_ovc_state_plane_v0_2` (state plane view)
- Symbol, start_date, end_date
Outputs:
- `outputs/state_plane_v0_2/trajectory.csv`
- `outputs/state_plane_v0_2/summary.json`
- `outputs/state_plane_v0_2/compressed.bin`
Determinism Rules:
- Same DB state → identical trajectory
- Observational only (no outcome joins, no scoring)
Failure Modes:
- Missing state plane view → query error
- No data in range → empty output
Enforcement Surfaces: E1, E2
Evidence Anchors:
- `scripts/path1/run_state_plane.py`
- `sql/06_state_plane_threshold_pack_v0_2.sql`

---

### OP-D08: Path1 Trajectory Families (Fingerprints)

Operation ID: OP-D08
Option: D
Purpose: Emit deterministic fingerprints for trajectory shape clustering (observation phase only — no clustering or naming in v0.1).
Bound Executables:
- `scripts/path1/run_trajectory_families.py`
- `trajectory_families/__init__.py`
- `trajectory_families/fingerprint.py`
- `trajectory_families/features.py`
- `trajectory_families/distance.py`
- `trajectory_families/clustering.py`
- `trajectory_families/naming.py`
- `trajectory_families/gallery.py`
- `trajectory_families/schema.py`
Inputs:
- State plane trajectory.csv files
- Symbol, date_ny
Outputs:
- Fingerprint JSON files (`fp_SYMBOL_DATE_HASH`)
- `reports/path1/trajectory_families/v0.1/fingerprints/`
Determinism Rules:
- Fingerprint ID = `fp_{SYMBOL}_{DATE}_{content_hash[:8]}`
- Content hash is SHA256 of trajectory data
- Schema version: `day_fingerprint_v0.1`
Failure Modes:
- Missing trajectory.csv → skip
- Schema validation error → ValidationError raised
Enforcement Surfaces: E1, E2, E3
Evidence Anchors:
- `scripts/path1/run_trajectory_families.py`
- `trajectory_families/schema.py`
- `tests/test_fingerprint.py`
- `tests/test_fingerprint_determinism.py`
- `trajectory_families/params_v0_1.json`
- `tests/fixtures/golden_fingerprint_v0_1.json`

---

### OP-D09: Evidence Pack Overlays v0.3

Operation ID: OP-D09
Option: D
Purpose: Derive observational overlays (wick/sweep microstructure, displacement/imbalance, liquidity gradient) from M15 strips without mutating canonical data.
Bound Executables:
- `scripts/path1/overlays_v0_3.py`
Inputs:
- Evidence pack v0.2 strips (`strips/2h/*.csv`)
- 2H spine (`backbone_2h.csv`)
Outputs:
- v0.3-A: Wick & sweep overlay (per-block)
- v0.3-B: Displacement/imbalance events (global JSONL)
- v0.3-C: Liquidity gradient map (per-block)
Determinism Rules:
- All numerics quantized to 1e-5 precision
- Event IDs derived from canonical SHA-1 hash
- Intrablock-only computation (no cross-block lookbacks)
Failure Modes:
- Missing v0.2 pack → cannot compute overlays
- Strip data incomplete → partial overlay
Enforcement Surfaces: E1, E2, E3
Evidence Anchors:
- `scripts/path1/overlays_v0_3.py`
- `tests/test_overlays_v0_3_determinism.py`
- `docs/OVERLAY_V0_3_HARDENING_SUMMARY.md`
- `CHANGELOG_overlays_v0_3.md`

---

### OP-D10: Queue Resolved Generation

Operation ID: OP-D10
Option: D
Purpose: Reconcile RUN_QUEUE.csv intent with INDEX.md canonical ledger to produce derived RUN_QUEUE_RESOLVED.csv.
Bound Executables:
- `scripts/path1/generate_queue_resolved.py`
Inputs:
- `reports/path1/evidence/RUN_QUEUE.csv` (intent)
- `reports/path1/evidence/INDEX.md` (canonical ledger)
- `reports/path1/evidence/runs/*/RUN.md` (actual execution metadata)
Outputs:
- `reports/path1/evidence/RUN_QUEUE_RESOLVED.csv` (generated, not authoritative)
Determinism Rules:
- INDEX.md remains canonical source of truth
- Output is derived/generated, never manually maintained
Failure Modes:
- Missing INDEX.md → empty reconciliation
- RUN.md parse failure → unresolved row
Enforcement Surfaces: E2, E5
Evidence Anchors:
- `scripts/path1/generate_queue_resolved.py`

---

### OP-D11: Notion Sync

Operation ID: OP-D11
Option: D
Purpose: Sync database records (blocks, outcomes, eval runs) to Notion databases for external visibility.
Bound Executables:
- `scripts/export/notion_sync.py`
Inputs:
- Database connection (DATABASE_URL)
- Notion API (NOTIOM_TOKEN — canonical spelling)
- NOTION_BLOCKS_DB_ID, NOTION_OUTCOMES_DB_ID, NOTION_RUNS_DB_ID
Outputs:
- Notion database rows (external)
- `reports/runs/<run_id>/run.json` (run artifact)
- `ops.notion_sync_state` (sync cursor)
Determinism Rules:
- Sync is incremental based on last_ts cursor
- Exponential backoff for rate limiting
Failure Modes:
- Missing NOTIOM_TOKEN → startup abort (check_required_env)
- Notion API 429 → retry with backoff
- DB connection failure → run fails
Enforcement Surfaces: E2, E4, E7
Evidence Anchors:
- `scripts/export/notion_sync.py`
- `.github/workflows/notion_sync.yml` (schedule: `0 */2 * * *`)
- `sql/04_ops_notion_sync.sql`

---

## Option QA — Audit / Coverage / Validation

---

### OP-QA01: Canonical Facts Validation (Day/Range)

Operation ID: OP-QA01
Option: QA
Purpose: Validate canonical OHLC facts against TradingView reference data for single-day or date-range coverage and integrity.
Bound Executables:
- `src/validate_day.py`
- `src/validate_range.py`
Inputs:
- `ovc.ovc_blocks_v01_1_min` (canonical facts)
- `ovc_qa.tv_ohlc_2h` (TradingView reference)
- TradingView CSV files (via `src/utils/csv_locator.py`, `src/history_sources/tv_csv.py`)
Outputs:
- `ovc_qa.validation_run` (per-day metadata)
- `ovc_qa.ohlc_mismatch` (violation records)
- `reports/validation/` (reports)
- `reports/runs/<run_id>/run.json` (run artifact)
Determinism Rules:
- Same data → same validation result
Failure Modes:
- Missing TV CSV → validation cannot proceed
- OHLC sanity violation → FAIL
- Block count != 12 → FAIL
Enforcement Surfaces: E1, E2, E3, E5, E7
Evidence Anchors:
- `src/validate_day.py`
- `src/validate_range.py`
- `sql/qa_schema.sql`
- `sql/qa_validation_pack_core.sql`
- `sql/qa_validation_pack_derived.sql`

---

### OP-QA02: CI Pytest Suite

Operation ID: OP-QA02
Option: QA
Purpose: Run automated test suite covering contracts, derived features, determinism, fingerprints, threshold registry, and replay structure.
Bound Executables:
- `tests/test_min_contract_validation.py`
- `tests/test_contract_equivalence.py`
- `tests/test_derived_features.py`
- `tests/test_validate_derived.py`
- `tests/test_threshold_registry.py`
- `tests/test_path1_replay_structural.py`
- `tests/test_fingerprint.py`
- `tests/test_fingerprint_determinism.py`
- `tests/test_c3_regime_trend.py`
- `tests/test_overlays_v0_3_determinism.py`
- `tests/test_evidence_pack_manifest.py`
- `tests/test_pack_rebuild_equivalence.py`
- `tests/test_dst_audit.py`
Inputs:
- Source code, contracts, fixtures
Outputs:
- Test results (pass/fail)
- CI gate status
Determinism Rules:
- Same code → same test results
- Tests that require DB are skipped without connection
Failure Modes:
- Any test failure → CI blocks merge
Enforcement Surfaces: E3, E4
Evidence Anchors:
- `tests/` (all test files)
- `.github/workflows/ci_pytest.yml`
- `pytest.ini`

---

### OP-QA03: CI Schema Verification

Operation ID: OP-QA03
Option: QA
Purpose: Verify required database objects (tables, views, schemas) exist in Neon and migration ledger is valid JSON.
Bound Executables:
- `scripts/ci/verify_schema_objects.py`
- `sql/90_verify_gate2.sql`
Inputs:
- Database connection (NEON_DSN)
- `schema/applied_migrations.json`
Outputs:
- Pass/fail status
- CI gate result
Determinism Rules:
- Same DB state → same result
Failure Modes:
- Missing table/view → FAIL
- Connection failure → exit code 2
- Invalid migrations JSON → FAIL
Enforcement Surfaces: E4, E5
Evidence Anchors:
- `scripts/ci/verify_schema_objects.py`
- `sql/90_verify_gate2.sql`
- `.github/workflows/ci_schema_check.yml`
- `schema/applied_migrations.json`

---

### OP-QA04: CI Workflow Sanity

Operation ID: OP-QA04
Option: QA
Purpose: Meta-validate GitHub workflow YAML syntax, permissions presence, script reference existence, and duplicate workflow names.
Bound Executables:
- `.github/workflows/ci_workflow_sanity.yml` (self-contained)
Inputs:
- `.github/workflows/*.yml`
- `scripts/` (referenced paths)
Outputs:
- Pass/fail status
Determinism Rules:
- Same repo state → same result
Failure Modes:
- Invalid YAML → FAIL
- Missing script reference → FAIL
- Duplicate workflow name → FAIL
Enforcement Surfaces: E4
Evidence Anchors:
- `.github/workflows/ci_workflow_sanity.yml`

---

### OP-QA05: Coverage Audit (Codex)

Operation ID: OP-QA05
Option: QA
Purpose: Read-only repo coverage accounting mapping repository files to legend entries and governance graphs.
Bound Executables:
- `.codex/CHECKS/coverage_audit.py`
- `.codex/CHECKS/run_audit_pack.ps1`
- `.codex/CHECKS/rg_index.ps1`
- `.codex/CHECKS/snapshot_tree.ps1`
Inputs:
- `git ls-files` (repo file inventory)
- Markdown legends (NodeID tables)
- Mermaid governance graphs
Outputs:
- `.codex/RUNS/<stamp>/repo_files.txt`
- `.codex/RUNS/<stamp>/legend_nodes.json`
- `.codex/RUNS/<stamp>/graph_nodes.json`
- `.codex/RUNS/<stamp>/coverage_report.md`
Determinism Rules:
- Same repo state → same coverage metrics
- Read-only (no modifications)
Failure Modes:
- Legend parse failure → incomplete coverage
- Graph parse failure → missing nodes
Enforcement Surfaces: E5
Evidence Anchors:
- `.codex/CHECKS/coverage_audit.py`
- `.codex/RUNS/` (existing audit runs)

---

### OP-QA06: SQL QA Validation Packs

Operation ID: OP-QA06
Option: QA
Purpose: Execute SQL-based validation queries for single-day tape checks, derived feature joins, and Option C spotchecks.
Bound Executables:
- `sql/qa_validation_pack_core.sql`
- `sql/qa_validation_pack_derived.sql`
- `sql/qa_validation_pack.sql`
- `sql/option_c_spotchecks.sql`
- `sql/option_c_run_report.sql`
Inputs:
- Database connection
- Parameters: symbol, date_ny, run_id
Outputs:
- Validation verdicts (PASS/WARN/FAIL)
- Spotcheck results
- Run report JSON
Determinism Rules:
- Same DB state + same parameters → same results
Failure Modes:
- Connection failure → abort
- Missing data → empty result sets
Enforcement Surfaces: E2, E5
Evidence Anchors:
- `sql/qa_validation_pack_core.sql`
- `sql/option_c_spotchecks.sql`
- `docs/contracts/qa_validation_contract_v1.md`

---

## NON_CANONICAL — Exploratory, Legacy, Scaffold, Informal

---

### OP-NC01: Legacy Backfill (Non-Checkpointed)

Operation ID: OP-NC01
Option: NON_CANONICAL
Purpose: Legacy OANDA 2H backfill without checkpoint resumption — superseded by OP-A02.
Bound Executables:
- `src/backfill_oanda_2h.py`

---

### OP-NC02: Legacy Backfill Day Utility

Operation ID: OP-NC02
Option: NON_CANONICAL
Purpose: Utility library for single-day backfill operations — not directly invoked as standalone.
Bound Executables:
- `src/backfill_day.py`

---

### OP-NC03: Full Ingest Stub

Operation ID: OP-NC03
Option: NON_CANONICAL
Purpose: Placeholder/stub for comprehensive symbol ingest — not fully implemented.
Bound Executables:
- `src/full_ingest_stub.py`

---

### OP-NC04: History Day Ingest

Operation ID: OP-NC04
Option: NON_CANONICAL
Purpose: Historical day-level ingest utility — exploratory.
Bound Executables:
- `src/ingest_history_day.py`

---

### OP-NC05: Test Insert (Dev)

Operation ID: OP-NC05
Option: NON_CANONICAL
Purpose: Development test insert utility.
Bound Executables:
- `src/test_insert.py`

---

### OP-NC06: Legacy OVC Artifacts Helper

Operation ID: OP-NC06
Option: NON_CANONICAL
Purpose: Early-generation run artifact helper — superseded by `src/ovc_ops/run_artifact.py`.
Bound Executables:
- `src/ovc_artifacts.py`

---

### OP-NC07: Run Artifact CLI

Operation ID: OP-NC07
Option: NON_CANONICAL
Purpose: CLI wrapper for non-Python pipelines to emit run artifacts — supporting scaffold.
Bound Executables:
- `src/ovc_ops/run_artifact_cli.py`

---

### OP-NC08: Run Artifact Library

Operation ID: OP-NC08
Option: NON_CANONICAL
Purpose: Core RunWriter class used by all pipeline scripts — shared infrastructure, not an operation per se.
Bound Executables:
- `src/ovc_ops/run_artifact.py`

---

### OP-NC09: OANDA Export (2H Day)

Operation ID: OP-NC09
Option: NON_CANONICAL
Purpose: Export OANDA H1 candles and aggregate to 2H for validation reference — development utility.
Bound Executables:
- `scripts/export/oanda_export_2h_day.py`

---

### OP-NC10: SQL Migration Runner

Operation ID: OP-NC10
Option: NON_CANONICAL
Purpose: Apply SQL migration files to database — manual utility.
Bound Executables:
- `scripts/run/run_migration.py`

---

### OP-NC11: Deploy Worker

Operation ID: OP-NC11
Option: NON_CANONICAL
Purpose: Deploy Cloudflare Worker via wrangler — deployment scaffold.
Bound Executables:
- `scripts/deploy/deploy_worker.ps1`

---

### OP-NC12: DST Mapping Check (Dev)

Operation ID: OP-NC12
Option: NON_CANONICAL
Purpose: Development tool for verifying DST boundary handling.
Bound Executables:
- `scripts/dev/check_dst_mapping.py`

---

### OP-NC13: Pipeline Status Utility

Operation ID: OP-NC13
Option: NON_CANONICAL
Purpose: Utility library for pipeline status checks — not a standalone operation.
Bound Executables:
- `scripts/validate/pipeline_status.py`

---

### OP-NC14: Validate Day PowerShell Wrapper

Operation ID: OP-NC14
Option: NON_CANONICAL
Purpose: PowerShell wrapper for validate_day — Windows convenience script.
Bound Executables:
- `scripts/validate/validate_day.ps1`

---

### OP-NC15: Contract Validation Tools

Operation ID: OP-NC15
Option: NON_CANONICAL
Purpose: Contract validation and export parsing utilities — development tools.
Bound Executables:
- `tools/validate_contract.py`
- `tools/validate_contract.ps1`
- `tools/parse_export.py`

---

### OP-NC16: Repo Maze Generators

Operation ID: OP-NC16
Option: NON_CANONICAL
Purpose: Repository structure visualization and documentation generators.
Bound Executables:
- `tools/maze/gen_repo_maze.py`
- `tools/maze/gen_repo_maze_curated.py`

---

### OP-NC17: CSV Locator / TV CSV Parser

Operation ID: OP-NC17
Option: NON_CANONICAL
Purpose: Utility libraries for locating and parsing TradingView CSV files — shared infrastructure.
Bound Executables:
- `src/utils/csv_locator.py`
- `src/history_sources/tv_csv.py`

---

### OP-NC18: Codex Graph NodeID Utilities

Operation ID: OP-NC18
Option: NON_CANONICAL
Purpose: Graph node renaming utilities for governance canonicalization.
Bound Executables:
- `.codex/CHECKS/apply_graph_nodeid_renames.py`
- `.codex/CHECKS/plan_graph_nodeid_renames.py`
- `.codex/CHECKS/run_graph_nodeid_rename_plan.ps1`

---

### OP-NC19: Codex Preflight Parse

Operation ID: OP-NC19
Option: NON_CANONICAL
Purpose: Preflight validation parsing for codex runs.
Bound Executables:
- `.codex/CHECKS/preflight_parse.ps1`

---

### OP-NC20: Local Verification Scripts

Operation ID: OP-NC20
Option: NON_CANONICAL
Purpose: Local development verification and Windows pytest wrappers.
Bound Executables:
- `scripts/local/verify_local.ps1`
- `scripts/dev/pytest_win.ps1`

---

### OP-NC21: Legacy Derived View

Operation ID: OP-NC21
Option: NON_CANONICAL
Purpose: Deprecated combined derived features view — superseded by split C1/C2/C3 views.
Bound Executables:
- `sql/derived_v0_1.sql`

---

### OP-NC22: Legacy Outcomes View

Operation ID: OP-NC22
Option: NON_CANONICAL
Purpose: Deprecated outcomes view reading directly from canonical table — superseded by v_ovc_c_outcomes_v0_1.
Bound Executables:
- `sql/option_c_v0_1.sql` (creates deprecated `derived.ovc_outcomes_v0_1`)

---

### OP-NC23: Legacy Schema DDL

Operation ID: OP-NC23
Option: NON_CANONICAL
Purpose: Historical v0.1 schema definition — superseded by current schema.
Bound Executables:
- `sql/schema_v01.sql`

---

### OP-NC24: Research Views

Operation ID: OP-NC24
Option: NON_CANONICAL
Purpose: Analytical/research views for pattern outcomes, transition stats, session heatmaps — exploratory.
Bound Executables:
- `sql/10_views_research_v0.1.sql`

---

### OP-NC25: Webhook Detail Table DDL

Operation ID: OP-NC25
Option: NON_CANONICAL
Purpose: Full payload detail table for webhook ingestion — not part of canonical MIN flow.
Bound Executables:
- `infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql`

---

### OP-NC26: Webhook Test Suite

Operation ID: OP-NC26
Option: NON_CANONICAL
Purpose: Unit tests for Cloudflare Worker — supports OP-A01 but is test infrastructure.
Bound Executables:
- `infra/ovc-webhook/test/index.spec.ts`
- `infra/ovc-webhook/test/env.d.ts`

---

### OP-NC27: C3 Stub (Dormant)

Operation ID: OP-NC27
Option: NON_CANONICAL
Purpose: Experimental C3 alternative stub — not integrated into any workflow or test.
Bound Executables:
- `src/derived/compute_c3_stub_v0_1.py`

---

### OP-NC28: Full Ingest Workflow (Dormant)

Operation ID: OP-NC28
Option: NON_CANONICAL
Purpose: On-demand full ingest workflow — stub/dormant.
Bound Executables:
- `.github/workflows/ovc_full_ingest.yml`

---

### OP-NC29: Python Package Init Files

Operation ID: OP-NC29
Option: NON_CANONICAL
Purpose: Python package initializers — structural, not operational.
Bound Executables:
- `src/__init__.py` (if exists)
- `src/config/__init__.py`
- `src/derived/__init__.py`
- `src/history_sources/__init__.py`
- `src/ovc_ops/__init__.py`
- `src/utils/__init__.py`
- `src/validate/__init__.py`

---

*End of Allowed Operations Catalog v0.1*
