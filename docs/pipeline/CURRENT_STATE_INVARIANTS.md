# CURRENT STATE: Invariants

**Status: CURRENT_STATE (frozen on 2026-01-23)**

Facts that are true TODAY (even if wrong). Each references a specific file/table/view/script from the audit.

---

## Invariant List (minimum 12)

### Option A Invariants

1. **INV-A1**: The Cloudflare Worker (`infra/ovc-webhook/src/index.ts`) writes rows to `ovc.ovc_blocks_v01_1_min` including derived fields (`state_tag`, `trend_tag`, `pred_dir`).

2. **INV-A2**: The M15 backfill script (`scripts/backfill/backfill_oanda_m15_checkpointed.py`) writes to `ovc.ovc_candles_m15_raw`, which is separate from the canonical 2H facts table.

3. **INV-A3**: The table `ovc.ovc_blocks_v01_1_min` is defined in `sql/01_tables_min.sql` and contains both raw OHLC fields AND derived feature columns.

### Option B Invariants

4. **INV-B1**: Two derived feature implementations coexist: legacy view `derived.ovc_block_features_v0_1` (in `sql/derived_v0_1.sql`) AND split L1/L2/L3 tables/views (in `sql/derived/`).

5. **INV-B2**: The workflow `backfill_then_validate.yml` invokes only `compute_l1_v0_1.py` and `compute_l2_v0_1.py`; it does NOT invoke `compute_l3_regime_trend_v0_1.py`.

6. **INV-B3**: The threshold registry tables (`ovc_cfg.threshold_pack`, `ovc_cfg.threshold_pack_active`) are defined in `sql/04_threshold_registry_v0_1.sql` and consumed by `v_ovc_l3_features_v0_1.sql`.

### Option C Invariants

7. **INV-L1**: The Option C runner (`sql/option_c_v0_1.sql`) creates view `derived.ovc_outcomes_v0_1` by reading directly from `ovc.ovc_blocks_v01_1_min`.

8. **INV-L2**: A separate view `derived.v_ovc_c_outcomes_v0_1` (in `sql/derived/v_ovc_c_outcomes_v0_1.sql`) computes outcomes from L1/L2/L3 feature views, NOT from the canonical table.

9. **INV-L3**: The scheduled workflow `ovc_option_c_schedule.yml` references `scripts/run_option_c.sh` at line 82, but the actual script exists at `scripts/run/run_option_c.sh`.

### Option D Invariants

10. **INV-D1**: Path1 evidence views (`sql/path1/evidence/v_path1_evidence_dis_v1_1.sql`) join to `derived.v_ovc_c_outcomes_v0_1` (NOT `derived.ovc_outcomes_v0_1`).

11. **INV-D2**: The evidence pack builder (`scripts/path1/build_evidence_pack_v0_2.py`) reads from `derived.v_path1_evidence_dis_v1_1` (line 31) and `ovc.ovc_candles_m15_raw` (line 33).

12. **INV-D3**: Path2 evidence has only documentation (`docs/path2/PATH2_CONTRACT_v1_0.md`, `docs/path2/ROADMAP_v0_1.md`); no code or workflows exist.

### QA Invariants

13. **INV-QA1**: The CI workflow `ci_workflow_sanity.yml` validates YAML syntax and checks script path existence, but does NOT execute pytest.

14. **INV-QA2**: Test files exist in `tests/` directory (13 files including `test_min_contract_validation.py`, `test_path1_replay_structural.py`, etc.) but no workflow runs them.

15. **INV-QA3**: There is no migration ledger or applied-patches tracking mechanism. The only way to verify DB schema is manual inspection.

### Schema/Telemetry Invariants

16. **INV-SCHEMA1**: The Worker writes columns `ended_at` and `meta` to `ovc.ovc_run_reports_v01`, but table definition in `sql/02_tables_run_reports.sql` defines `finished_at` and has no `meta` column.

---

## Cross-Reference: Invariant → Audit Fracture

| Invariant | Fracture Point(s) |
|-----------|-------------------|
| INV-A1 | F1 (Option boundary breach) |
| INV-A3 | F1 (Option boundary breach) |
| INV-B1 | F2 (Multiple sources of truth) |
| INV-B2 | F3 (Unused L3 compute path) |
| INV-L1 | F5 (Outcome view mismatch) |
| INV-L2 | F5 (Outcome view mismatch) |
| INV-L3 | F4 (Option C scheduling mismatch) |
| INV-D1 | F5 (Outcome view mismatch) |
| INV-QA1 | F8 (QA vs CI gap) |
| INV-QA2 | F8 (QA vs CI gap) |
| INV-QA3 | F9 (Ambiguous migration state) |
| INV-SCHEMA1 | F7 (Worker telemetry schema drift) |
