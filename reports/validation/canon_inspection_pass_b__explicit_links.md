# Canon Inspection — Pass B (Explicit Links & Authority Claims)

## 0) Inspection Set
- docs/doctrine/OVC_DOCTRINE.md
- docs/doctrine/IMMUTABILITY_NOTICE.md
- docs/doctrine/ovc_logging_doctrine_v0.1.md
- docs/doctrine/GATES.md
- docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md
- docs/architecture/legend_canonicalization_purpose.md
- docs/governance/GOVERNANCE_RULES_v0.1.md
- docs/governance/BRANCH_POLICY.md
- docs/governance/decisions.md
- docs/contracts/A_TO_D_CONTRACT_v1.md
- docs/contracts/qa_validation_contract_v1.md
- docs/contracts/option_a_ingest_contract_v1.md
- docs/contracts/option_b_derived_contract_v1.md
- docs/contracts/option_c_outcomes_contract_v1.md
- docs/contracts/option_d_evidence_contract_v1.md
- docs/contracts/option_d_ops_boundary.md
- docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md
- contracts/run_artifact_spec_v0.1.json
- PATH1_EXECUTION_MODEL.md
- docs/operations/OPERATING_BASE.md
- docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md
- docs/pipeline/CURRENT_STATE_INVARIANTS.md
- docs/pipeline/PIPELINE_REALITY_MAP_v0.1.md (NOT FOUND)
- CLAIMS/CLAIM_BINDING_v0_1.md
- CLAIMS/ANCHOR_INDEX_v0_1.csv
- reports/verification/EVIDENCE_ANCHOR_v0_1.md
- Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md
- Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md
- Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md

## 1) Authority Claims Index
| File | Declares Authority? (Y/N) | Declared Type (Canon/Gov/Contract/Spec/Other) | Governs What (explicit) |
|---|---|---|---|
| docs/doctrine/OVC_DOCTRINE.md | Y | Canon | design, development, and use of OVC |
| docs/doctrine/IMMUTABILITY_NOTICE.md | Y | Canon | all canonical OVC layers |
| docs/doctrine/ovc_logging_doctrine_v0.1.md | N | Other | current logging and validation pipeline |
| docs/doctrine/GATES.md | N | Other | Not stated |
| docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md | Y | Canon | data ownership, purpose, and downstream flows |
| docs/architecture/legend_canonicalization_purpose.md | Y | Other | NodeIDs used across OVC graphs, audits, and automation |
| docs/governance/GOVERNANCE_RULES_v0.1.md | Y | Gov | all OVC repository artifacts (code, schemas, docs, configs) |
| docs/governance/BRANCH_POLICY.md | Y | Gov | branch policy (naming, deletion, and usage rules) |
| docs/governance/decisions.md | N | Other | Not stated |
| docs/contracts/A_TO_D_CONTRACT_v1.md | Y | Contract | flow from Option A (Ingest) through Option D (Evidence) |
| docs/contracts/qa_validation_contract_v1.md | Y | Contract | QA validation across pipeline layers |
| docs/contracts/option_a_ingest_contract_v1.md | Y | Contract | Option A ingest into canonical fact tables |
| docs/contracts/option_b_derived_contract_v1.md | Y | Contract | Option B derived feature computation |
| docs/contracts/option_c_outcomes_contract_v1.md | Y | Contract | Option C outcomes computation |
| docs/contracts/option_d_evidence_contract_v1.md | Y | Contract | Option D evidence packs |
| docs/contracts/option_d_ops_boundary.md | Y | Other | Option D ops boundary (automation + operations) |
| docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md | Y | Spec | deterministic run artifact directory and files |
| contracts/run_artifact_spec_v0.1.json | Y | Spec | run artifact schema (run.json/checks.json/run.log) |
| PATH1_EXECUTION_MODEL.md | Y | Canon | Path 1 execution ergonomics |
| docs/operations/OPERATING_BASE.md | N | Other | Not stated |
| docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md | Y | Canon | OVC operating loop |
| docs/pipeline/CURRENT_STATE_INVARIANTS.md | Y | Other | current state invariants |
| docs/pipeline/PIPELINE_REALITY_MAP_v0.1.md | N | Other | Not Observable (file missing) |
| CLAIMS/CLAIM_BINDING_v0_1.md | Y | Other | strongest claims supported by current evidence anchors |
| CLAIMS/ANCHOR_INDEX_v0_1.csv | N | Other | Not stated |
| reports/verification/EVIDENCE_ANCHOR_v0_1.md | Y | Other | ANCHOR_GBPUSD_2026-01-16_optionc_v0.1 |
| Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md | Y | Other | master mapping of Node IDs used across graphs |
| Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md | N | Other | Not stated |
| Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md | N | Other | Not stated |

## 2) Explicit Link Graph (Text)
### docs/doctrine/OVC_DOCTRINE.md
- References: None
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "Performance results must never flow backward to change how facts are recorded."; "Only Option C is permitted to reference future data."; "Do not silently edit the past."; "Descriptive layers must not contain hidden judgments."

### docs/doctrine/IMMUTABILITY_NOTICE.md
- References: `docs/ops/GOVERNANCE_RULES_v0.1.md`; `GOVERNANCE_RULES_v0.1.md`; `OPTION_B_C1_*.md`; `OPTION_B_C2_*.md`; `OPTION_B_C3_*.md`; `OPTION_C_*.md`; `OPTION_B_C1_FEATURES_v0.2.md`; `derived.v_ovc_c1_features_v0_2`; `docs/WORKFLOW_STATUS.md`; `releases/ovc-v0.1-spine.md`
- Run fields mentioned: None
- Schemas referenced: `derived` (schema); `derived.v_ovc_c1_*`; `derived.v_ovc_c2_*`; `derived.v_ovc_c3_*`; `derived.v_ovc_c_outcomes_*`; `derived.v_ovc_c1_features_v0_2`; `research.*`; `experimental.*`
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "Canonical layers must not be modified in place."; "Experimental or exploratory work (Option E, research views, strategy prototypes) must:"; "Never mutate the `derived` schema canonical views"; "Governance approval is required for any canonical change."

### docs/doctrine/ovc_logging_doctrine_v0.1.md
- References: `infra/ovc-webhook/src/index.ts`; `infra/ovc-webhook/wrangler.jsonc`; `sql/01_tables_min.sql`; `sql/02_tables_run_reports.sql`; `sql/derived_v0_1.sql`; `sql/option_c_v0_1.sql`; `sql/qa_schema.sql`; `sql/qa_validation_pack.sql`; `.github/workflows/backfill.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `src/backfill_oanda_2h_checkpointed.py`; `scripts/oanda_export_2h_day.py`; `scripts/run_option_c.sh`; `src/validate_day.py`; `docs/tape_validation_harness.md`; `.\scripts\pipeline_status.py`; `.\src\backfill_oanda_2h_checkpointed.py`; `.\src\validate_day.py`
- Run fields mentioned: `run_id`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_run_reports_v01`; `ovc_qa.tv_ohlc_2h.source`; `ovc` (schema); `derived` (schema); `ovc_qa` (schema)
- Scripts/tools referenced: `.github/workflows/backfill.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `src/backfill_oanda_2h_checkpointed.py`; `scripts/oanda_export_2h_day.py`; `scripts/run_option_c.sh`; `src/validate_day.py`; `.\scripts\pipeline_status.py`
- Must/shall/invalidates phrases: "A validation run must use exactly one tape source per run."; "Mixing sources inside a single `run_id` invalidates the run."; "Requirement: all meaning layers must be replayable and fully derived from canonical inputs."; "Prohibited: mutating or reclassifying canonical facts."

### docs/doctrine/GATES.md
- References: None
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None
### docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md
- References: `docs/ops/GOVERNANCE_RULES_v0.1.md`; `docs/ops/WORKFLOW_AUDIT_*.md`; `GOVERNANCE_RULES_v0.1.md`; `sql/10_views_research_v0.1.sql`; `sql/derived_v0_1.sql`; `sql/02_derived_c1_c2_tables_v0_1.sql`; `sql/05_c3_regime_trend_v0_1.sql`; `sql/option_c_v0_1.sql`; `sql/qa_schema.sql`; `sql/03_qa_derived_validation_v0_1.sql`; `sql/04_threshold_registry_v0_1.sql`; `sql/04_ops_notion_sync.sql`; `sql/schema_v01.sql`; `infra/ovc-webhook/sql/`; `../../scripts/notion_sync.py`; `scripts/notion_sync.py`; `.github/workflows/backfill.yml`; `.github/workflows/notion_sync.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ovc_full_ingest.yml`; `contracts/run_artifact_spec_v0.1.json`; `docs/ops/RUN_ARTIFACT_SPEC_v0.1.md`; `src/ovc_ops/run_artifact.py`; `src/ovc_ops/run_artifact_cli.py`; `src/backfill_oanda_2h_checkpointed.py`; `src/derived/compute_c1_v0_1.py`; `src/derived/compute_c2_v0_1.py`; `src/derived/compute_c3_regime_trend_v0_1.py`; `src/validate/validate_derived_range_v0_1.py`; `src/validate_day.py`; `src/validate_range.py`; `sql/archive/`; `reports/runs/<pipeline_id>/<run_id>/run.json`
- Run fields mentioned: `run.json`; `run_id`; `pipeline_id`; `run_type`; `inputs`; `outputs`; `env`; `checks`; `Summary`
- Schemas referenced: `ovc` (schema); `derived` (schema); `ovc_qa` (schema); `ovc_cfg` (schema); `ops` (schema); `public` (schema); `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_run_reports_v01`; `ovc_outcomes_v01`; `v_ovc_min_events_norm`; `v_ovc_min_events_seq`; `v_pattern_outcomes_v01`; `v_transition_stats_v01`; `v_session_heatmap_v01`; `v_data_quality_ohlc_basic`; `derived_runs`; `derived_runs_v0_1`; `eval_runs`; `ovc_block_features_v0_1`; `ovc_c1_features_v0_1`; `ovc_c2_features_v0_1`; `ovc_c3_regime_trend_v0_1`; `ovc_outcomes_v0_1`; `ovc_scores_v0_1`; `validation_run`; `expected_blocks`; `tv_ohlc_2h`; `ohlc_mismatch`; `derived_validation_run`; `ovc_cfg.threshold_pack`; `ovc_cfg.threshold_pack_active`; `ops.notion_sync_state`; `public.ovc_blocks_v01`; `public.ovc_blocks_detail_v01`; `derived.v_ovc_c_outcomes_v0_1`; `derived.eval_runs`
- Scripts/tools referenced: `.github/workflows/backfill.yml`; `.github/workflows/notion_sync.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ovc_full_ingest.yml`; `scripts/notion_sync.py`; `src/ovc_ops/run_artifact.py`; `src/ovc_ops/run_artifact_cli.py`; `src/backfill_oanda_2h_checkpointed.py`; `src/derived/compute_c1_v0_1.py`; `src/derived/compute_c2_v0_1.py`; `src/derived/compute_c3_regime_trend_v0_1.py`; `src/validate/validate_derived_range_v0_1.py`; `src/validate_day.py`; `src/validate_range.py`
- Must/shall/invalidates phrases: "DO NOT MODIFY without review"; "This document is CANONICAL."; "Raw facts, derived features, and intermediate calculations must never flow to Notion."; "The following categories must never flow to Notion:"; "If a human cannot act differently after seeing this field, it must not go to Notion."; "This is intentional and must not be \"fixed\" to standard spelling."

### docs/architecture/legend_canonicalization_purpose.md
- References: None
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### docs/governance/GOVERNANCE_RULES_v0.1.md
- References: `contracts/export_contract_v0.1.1_min.json`; `sql/01_tables_min.sql`; `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md`; `docs/ops/GOVERNANCE_RULES_v0.1.md`; `docs/ops/PIPELINE_REALITY_MAP_v0.1.md`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ovc_full_ingest.yml`; `src/derived/compute_c1_v0_1.py`; `src/backfill_oanda_2h_checkpointed.py`; `src/backfill_oanda_2h.py`; `docs/ovc_current_workflow.md`; `docs/WORKER_PIPELINE.md`; `sql/schema_v01.sql`; `scripts/notion_sync.py`; `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md`; `WORKFLOW_AUDIT_2026-01-20.md`; `SCHEMA_AUDIT_2026-02-15.md`; `CONTRACT_AUDIT_2026-03-01.md`
- Run fields mentioned: None
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `public.ovc_blocks_v01`; `ovc.*`; `derived.*`
- Scripts/tools referenced: `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ovc_full_ingest.yml`; `src/backfill_oanda_2h_checkpointed.py`; `src/backfill_oanda_2h.py`; `src/derived/compute_c1_v0_1.py`; `scripts/notion_sync.py`
- Must/shall/invalidates phrases: "frozen contracts that must not change without explicit review"; "Modification PROHIBITED without explicit audit and version bump"; "Deletion PROHIBITED — mark DEPRECATED first, then ORPHANED"; "Derived layers must NOT: Write to `ovc.*` schema"; "All canonical NodeIDs must be declared as markdown pipe-table rows in `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md`."

### docs/governance/BRANCH_POLICY.md
- References: `pr/pine-min-export-v0.1_min_r1`; `origin/pr/pine-min-export-v0.1_min_r1`; `origin/wip/infra-contract-validation`; `origin/codex/complete-step-8b-hardening-for-ovc`; `origin/codex/create-ovc-current-workflow-documentation`; `origin/codex/fix-export_contract_v0.1_full.json`; `origin/codex/fix-min-contract-schema-in-exportmin`; `pr/infra-min-v0.1.1`; `pr/<area>-<topic>-vX.Y`; `wip/<area>-<topic>`
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "Never develop directly on main; always work on PR branches."; "Never mix pine + infra in the same PR unless explicitly requested."

### docs/governance/decisions.md
- References: None
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### docs/contracts/A_TO_D_CONTRACT_v1.md
- References: `schema/applied_migrations.json`; `sql/00_schema.sql`; `sql/01_tables_min.sql`; `90_verify_gate2.sql`; `ci_workflow_sanity.yml`; `option_a_ingest_contract_v1.md`; `option_b_derived_contract_v1.md`; `option_c_outcomes_contract_v1.md`; `option_d_evidence_contract_v1.md`; `qa_validation_contract_v1.md`
- Run fields mentioned: `run_id`; git commit hash; timestamp (UTC); input hash/checksum
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `derived.v_ovc_c1_features_v0_1`; `derived.v_ovc_c2_features_v0_1`; `derived.v_ovc_c3_features_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `ovc_cfg.threshold_*`
- Scripts/tools referenced: `90_verify_gate2.sql`; `ci_workflow_sanity.yml`
- Must/shall/invalidates phrases: "Option A → MUST NOT write derived fields to canonical tables."; "Option B → MUST read ONLY from canonical tables."; "Option C → MUST read ONLY from Option B outputs."; "Option D → MUST read ONLY from Option C outputs."; "Every automated run MUST produce:"; "The output MUST be bit-for-bit identical."; "CI MUST verify that expected tables/views exist."; "A file `schema/applied_migrations.json` MUST track:"

### docs/contracts/qa_validation_contract_v1.md
- References: `reports/validation/`; `reports/path1/evidence/runs/*/qc_report.json`; `src/validate_day.py`; `src/validate_range.py`; `sql/qa_validation_pack_core.sql`; `src/validate/validate_derived_range_v0_1.py`; `sql/03_qa_derived_validation_v0_1.sql`; `scripts/path1/run_replay_verification.py`; `scripts/path1/run_seal_manifests.py`; `scripts/path1/validate_post_run.py`; `ci_workflow_sanity.yml`; `ci_pytest.yml`; `ci_schema_check.yml`; `test_min_contract_validation.py`; `test_contract_equivalence.py`; `test_validate_derived.py`; `test_threshold_registry.py`; `test_path1_replay_structural.py`; `test_fingerprint.py`; `test_fingerprint_determinism.py`; `schema/applied_migrations.json`
- Run fields mentioned: `run_id`; `sym`; `date_from`; `date_to`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `derived.v_ovc_c1_features_v0_1`; `derived.v_ovc_c2_features_v0_1`; `derived.v_ovc_c3_features_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `derived.v_path1_evidence_dis_v1_1`; `ovc_cfg.threshold_pack`; `ovc_cfg.threshold_pack_active`
- Scripts/tools referenced: `src/validate_day.py`; `src/validate_range.py`; `src/validate/validate_derived_range_v0_1.py`; `scripts/path1/run_replay_verification.py`; `scripts/path1/run_seal_manifests.py`; `scripts/path1/validate_post_run.py`; `ci_workflow_sanity.yml`; `ci_pytest.yml`; `ci_schema_check.yml`
- Must/shall/invalidates phrases: "CI MUST verify these objects exist in the database."; "CI MUST verify `schema/applied_migrations.json` exists"; "The following tests MUST pass in CI:"; "The `data_sha256.txt` MUST be identical."

### docs/contracts/option_a_ingest_contract_v1.md
- References: `tv/YYYY-MM-DD/HH-MM-SS_uuid.json`; `reports/runs/<run_id>/`
- Run fields mentioned: `run_id`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "They are **DEPRECATED** and MUST NOT be written by new ingest code."; "Worker MUST reject duplicate `block_id` inserts"; "Backfill MUST use upsert with idempotent semantics"; "OHLC sanity checks MUST be enforced"

### docs/contracts/option_b_derived_contract_v1.md
- References: `A_TO_D_CONTRACT_v1.md`; `docs/contracts/option_a1_bar_ingest_contract_v1.md`; `docs/contracts/c_layer_boundary_spec_v0.1.md`; `docs/contracts/c3_semantic_contract_v0_1.md`; `sql/01_tables_min.sql`; `sql/02_derived_c1_c2_tables_v0_1.sql`; `sql/04_threshold_registry_v0_1.sql`; `sql/05_c3_regime_trend_v0_1.sql`; `sql/90_verify_gate2.sql`; `sql/derived/v_ovc_c1_features_v0_1.sql`; `sql/derived/v_ovc_c2_features_v0_1.sql`; `sql/derived/v_ovc_c3_features_v0_1.sql`; `sql/derived_v0_1.sql`; `src/derived/compute_c1_v0_1.py`; `src/derived/compute_c2_v0_1.py`; `src/derived/compute_c3_regime_trend_v0_1.py`; `src/derived/compute_c3_stub_v0_1.py`; `src/validate/validate_derived_range_v0_1.py`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `.github/workflows/ci_workflow_sanity.yml`; `tests/test_derived_features.py`; `tests/test_validate_derived.py`
- Run fields mentioned: `run_id`; `run_type`; `version`; `formula_hash`; `window_spec`; `threshold_version`; `started_at`; `completed_at`; `block_count`; `status`; `error_message`; `config_snapshot`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `derived.v_ovc_c1_features_v0_1`; `derived.v_ovc_c2_features_v0_1`; `derived.v_ovc_c3_features_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `derived.ovc_c1_features_v0_1`; `derived.ovc_c2_features_v0_1`; `derived.ovc_c3_regime_trend_v0_1`; `derived.derived_runs_v0_1`; `derived.ovc_block_features_v0_1`; `derived.derived_runs`; `ovc_cfg.threshold_pack`; `ovc_cfg.threshold_pack_active`
- Scripts/tools referenced: `src/derived/compute_c1_v0_1.py`; `src/derived/compute_c2_v0_1.py`; `src/derived/compute_c3_regime_trend_v0_1.py`; `src/derived/compute_c3_stub_v0_1.py`; `src/validate/validate_derived_range_v0_1.py`; `tests/test_derived_features.py`; `tests/test_validate_derived.py`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `.github/workflows/ci_workflow_sanity.yml`
- Must/shall/invalidates phrases: "Option B MUST treat A1 legacy/non-authoritative fields as tainted inputs."; "This contract MUST NOT govern:"; "Option B MUST NOT read the following non-authoritative fields"; "The legacy combined view is deprecated and MUST NOT be used"; "C1 MUST NOT have rolling windows or lookback."; "C2 MUST NOT access C3 outputs."; "C3 MUST NOT access `ovc.ovc_blocks_v01_1_min` directly."; "Option B MUST NOT write to `ovc.*` or `ovc_cfg.*` tables."

### docs/contracts/option_c_outcomes_contract_v1.md
- References: `sql/derived/v_ovc_c_outcomes_v0_1.sql`; `scripts/run/run_option_c.sh`; `ovc_option_c_schedule.yml`
- Run fields mentioned: `run_id`; `eval_version`; `formula_hash`; `horizon_spec`; `computed_at`
- Schemas referenced: `derived.v_ovc_c1_features_v0_1`; `derived.v_ovc_c2_features_v0_1`; `derived.v_ovc_c3_features_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `derived.ovc_outcomes_v0_1`; `derived.ovc_scores_v0_1`; `derived.eval_runs`; `ovc.ovc_blocks_v01_1_min`
- Scripts/tools referenced: `scripts/run/run_option_c.sh`; `ovc_option_c_schedule.yml`
- Must/shall/invalidates phrases: "Option C MUST"; "Option C MUST NOT"; "Option C MUST NOT read from `ovc.ovc_blocks_v01_1_min` directly"; "`ovc_option_c_schedule.yml` MUST:"

### docs/contracts/option_d_evidence_contract_v1.md
- References: `reports/path1/evidence/runs/<run_id>/`; `reports/path1/evidence/runs/<run_id>/outputs/evidence_pack_v0_2/`; `reports/path1/evidence/runs/<run_id>/pack_build.jsonl`; `path1_evidence.yml`; `path1_evidence_queue.yml`; `path1_replay_verify.yml`; `build_evidence_pack_v0_2.py`
- Run fields mentioned: `run_id`; `sym`; `date_from`; `date_to`; `generated_at_utc`; `git.commit`; `git.dirty`; `data_sha256`; `build_sha256`
- Schemas referenced: `derived.v_ovc_c_outcomes_v0_1`; `derived.v_path1_evidence_dis_v1_1`; `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `derived.ovc_outcomes_v0_1`
- Scripts/tools referenced: `path1_evidence.yml`; `path1_evidence_queue.yml`; `path1_replay_verify.yml`; `build_evidence_pack_v0_2.py`
- Must/shall/invalidates phrases: "Option D MUST"; "Option D MUST NOT"; "The `data_sha256.txt` MUST be identical."; "Produce deterministic data hashes for same inputs"

### docs/contracts/option_d_ops_boundary.md
- References: `VERSION_OPTION_C`; `reports/run_report_<run_id>.json`; `reports/spotchecks_<run_id>.txt`; `reports/run_report_<run_id>.md`
- Run fields mentioned: `run_id`
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "Option C computation semantics are sealed and must not change without a version bump."

### docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md
- References: `reports/runs/<run_id>/`; `artifacts/validation_report.json`
- Run fields mentioned: `run_id`; `pipeline_id`; `pipeline_version`; `started_utc`; `finished_utc`; `duration_ms`; `status`; `trigger.type`; `trigger.source`; `trigger.actor`; `git.sha`; `git.sha7`; `git.ref`; `env.present`; `env.missing`; `inputs`; `outputs`; `checks.json`; `summary.pass`; `summary.fail`; `summary.skip`; `run.log`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: "Every OVC pipeline run must produce a deterministic run artifact directory"; "`run_id`: Must match run.json"; "First line MUST be:"; "Evidence strings must use one of these formats"; "JSON files must use:"; "Timestamps must be UTC ISO8601 with Z suffix"

### contracts/run_artifact_spec_v0.1.json
- References: `run.json`; `checks.json`; `run.log`; `artifacts/`
- Run fields mentioned: `run_id`; `pipeline_id`; `pipeline_version`; `started_utc`; `finished_utc`; `duration_ms`; `status`; `trigger`; `git`; `env`; `inputs`; `outputs`; `checks`; `summary`
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### PATH1_EXECUTION_MODEL.md
- References: `reports/path1/evidence/RUN_QUEUE.csv`; `.github/workflows/path1_evidence_queue.yml`; `scripts/path1/run_evidence_queue.py`; `reports/path1/evidence/INDEX.md`; `reports/path1/evidence/runs/<run_id>/`
- Run fields mentioned: `run_id`
- Schemas referenced: None
- Scripts/tools referenced: `.github/workflows/path1_evidence_queue.yml`; `scripts/path1/run_evidence_queue.py`
- Must/shall/invalidates phrases: None

### docs/operations/OPERATING_BASE.md
- References: `pine/OVC_v0_1.pine`; `infra/ovc-webhook/`; `infra/ovc-webhook/src/index.ts`; `infra/ovc-webhook/wrangler.jsonc`; `src/backfill_oanda_2h_checkpointed.py`; `sql/01_tables_min.sql`; `sql/option_c_v0_1.sql`; `reports/runs/<run_id>/`; `docs/OVC_DOCTRINE.md`; `docs/IMMUTABILITY_NOTICE.md`; `docs/WORKFLOW_STATUS.md`; `docs/c_layer_boundary_spec_v0.1.md`; `docs/ops/GOVERNANCE_RULES_v0.1.md`; `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md`; `.github/workflows/backfill.yml`; `.github/workflows/path1_evidence_queue.yml`; `scripts/run_option_c.sh`; `scripts/run_option_c.ps1`; `tests/sample_exports/min_001.txt`; `tools/validate_contract.py`; `contracts/export_contract_v0.1.1_min.json`; `contracts/run_artifact_spec_v0.1.json`; `infra/ovc-webhook/package.json`; `infra/ovc-webhook/wrangler.json`; `reports/path1/evidence/INDEX.md`; `reports/path1/evidence/RUN_QUEUE.csv`; `src/ovc_ops/run_artifact.py`; `src/validate_day.py`; `src/validate_range.py`
- Run fields mentioned: `RUN_ID`; `run_id`; `run.json`; `run.log`; `checks.json`; `pipeline_id`; `env`; `git`; `Trigger`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `derived.ovc_outcomes_v0_1`; `derived.v_ovc_c_outcomes_v0_1`
- Scripts/tools referenced: `.github/workflows/backfill.yml`; `.github/workflows/path1_evidence_queue.yml`; `scripts/run_option_c.sh`; `scripts/run_option_c.ps1`; `src/backfill_oanda_2h_checkpointed.py`; `src/ovc_ops/run_artifact.py`; `src/validate_day.py`; `src/validate_range.py`; `tools/validate_contract.py`
- Must/shall/invalidates phrases: None

### docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md
- References: `backfill_then_validate.yml`; `backfill_m15.yml`; `path1_evidence.yml`; `path1_replay_verify.yml`; `ovc_option_c_schedule.yml`; `reports/path1/evidence/runs/{run_id}/RUN.md`; `reports/path1/evidence/runs/{run_id}/*.md`; `reports/path1/evidence/runs/{run_id}/outputs/*.txt`; `sql/path1/evidence/runs/{run_id}/*.sql`; `reports/path1/evidence/INDEX.md`; `reports/path1/evidence/README.md`; `reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md`; `reports/runs/`; `artifacts/`; `sql/path1/evidence/`
- Run fields mentioned: `run_id`; `RUN_ID`
- Schemas referenced: None
- Scripts/tools referenced: `backfill_then_validate.yml`; `backfill_m15.yml`; `path1_evidence.yml`; `path1_replay_verify.yml`; `ovc_option_c_schedule.yml`
- Must/shall/invalidates phrases: "Every ledger-writing workflow MUST verify outputs before commit."

### docs/pipeline/CURRENT_STATE_INVARIANTS.md
- References: `infra/ovc-webhook/src/index.ts`; `scripts/backfill/backfill_oanda_m15_checkpointed.py`; `sql/01_tables_min.sql`; `sql/derived_v0_1.sql`; `sql/derived/`; `backfill_then_validate.yml`; `compute_c1_v0_1.py`; `compute_c2_v0_1.py`; `compute_c3_regime_trend_v0_1.py`; `ovc_option_c_schedule.yml`; `scripts/run_option_c.sh`; `sql/derived/v_ovc_c_outcomes_v0_1.sql`; `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql`; `scripts/path1/build_evidence_pack_v0_2.py`; `docs/path2/PATH2_CONTRACT_v1_0.md`; `docs/path2/ROADMAP_v0_1.md`; `tests/`; `test_min_contract_validation.py`; `test_path1_replay_structural.py`
- Run fields mentioned: None
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `ovc.ovc_run_reports_v01`; `derived.ovc_block_features_v0_1`; `derived.ovc_outcomes_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `derived.v_path1_evidence_dis_v1_1`; `ovc_cfg.threshold_pack`; `ovc_cfg.threshold_pack_active`
- Scripts/tools referenced: `backfill_then_validate.yml`; `ovc_option_c_schedule.yml`; `scripts/run_option_c.sh`; `scripts/path1/build_evidence_pack_v0_2.py`
- Must/shall/invalidates phrases: None

### docs/pipeline/PIPELINE_REALITY_MAP_v0.1.md
- References: Not Observable (file missing)
- Run fields mentioned: Not Observable (file missing)
- Schemas referenced: Not Observable (file missing)
- Scripts/tools referenced: Not Observable (file missing)
- Must/shall/invalidates phrases: Not Observable (file missing)

### CLAIMS/CLAIM_BINDING_v0_1.md
- References: `reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_20260122.md`; `reports/path1/evidence/runs/p1_20260121_001/RUN.md`; `reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2022-09-26_path1_state_plane_v0_2.md`
- Run fields mentioned: `run_id`
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### CLAIMS/ANCHOR_INDEX_v0_1.csv
- References: `reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_20260122.md`; `reports/path1/evidence/runs/p1_20260121_001/RUN.md`; `reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2022-09-26_path1_state_plane_v0_2.md`
- Run fields mentioned: `run_ids`
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### reports/verification/EVIDENCE_ANCHOR_v0_1.md
- References: `contracts/export_contract_v0.1.1_min.json`; `contracts/eval_contract_v0.1.json`; `contracts/run_artifact_spec_v0.1.json`; `configs/threshold_packs/c3_example_pack_v1.json`; `configs/threshold_packs/c3_regime_trend_v1.json`; `configs/threshold_packs/state_plane_v0_2_default_v1.json`; `scripts/run/run_option_c.ps1`; `src/validate_day.py`; `reports/run_report_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.json`; `reports/run_report_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.md`; `reports/spotchecks_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.txt`
- Run fields mentioned: `started_at`; `finished_at`
- Schemas referenced: None
- Scripts/tools referenced: `scripts/run/run_option_c.ps1`; `src/validate_day.py`
- Must/shall/invalidates phrases: "must be identical after normalizing allowed timestamp fields"; "must be byte-equal"; "All other fields must match exactly"
### Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md
- References: `.github/workflows/backfill.yml`; `.github/workflows/backfill_m15.yml`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `.github/workflows/ci_workflow_sanity.yml`; `.github/workflows/notion_sync.yml`; `.github/workflows/ovc_full_ingest.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `.github/workflows/path1_evidence.yml`; `.github/workflows/path1_evidence_queue.yml`; `.github/workflows/path1_replay_verify.yml`; `artifacts/derived_validation/LATEST.txt`; `artifacts/derived_validation/run_id/meta.json`; `artifacts/option_c/run_report_sanity_local.json`; `artifacts/option_c/spotchecks_sanity_local.txt`; `artifacts/path1_replay_report.json`; `contracts/derived_feature_set_v0.1.json`; `contracts/eval_contract_v0.1.json`; `contracts/export_contract_v0.1.1_min.json`; `contracts/export_contract_v0.1_full.json`; `contracts/run_artifact_spec_v0.1.json`; `data/verification_private/2026-01-19/commands_run.txt`; `docs/contracts/A_TO_D_CONTRACT_v1.md`; `docs/contracts/PATH2_CONTRACT_v1_0.md`; `docs/contracts/c_layer_boundary_spec_v0.1.md`; `docs/contracts/derived_layer_boundary.md`; `docs/contracts/ingest_boundary.md`; `docs/contracts/option_a_ingest_contract_v1.md`; `docs/contracts/option_b_derived_contract_v1.md`; `docs/contracts/option_c_outcomes_contract_v1.md`; `docs/contracts/option_d_evidence_contract_v1.md`; `docs/contracts/qa_validation_contract_v1.md`; `docs/doctrine/GATES.md`; `docs/doctrine/IMMUTABILITY_NOTICE.md`; `docs/doctrine/OVC_DOCTRINE.md`; `docs/governance/BRANCH_POLICY.md`; `docs/governance/GOVERNANCE_RULES_v0.1.md`; `infra/ovc-webhook/wrangler.json`; `reports/path1/evidence/RUN_QUEUE.csv`; `reports/path1/scores/DIS_v1_1.md`; `reports/path1/scores/LID_v1_0.md`; `reports/path1/scores/RES_v1_0.md`; `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`; `reports/runs/run_id/checks.json`; `reports/runs/run_id/run.json`; `reports/validation/C1_v0_1_validation.md`; `reports/validation/C2_v0_1_validation.md`; `reports/validation/C3_v0_1_validation.md`; `reports/verification/EVIDENCE_ANCHOR_v0_1.md`; `schema/applied_migrations.json`; `schema/required_objects.txt`; `scripts/ci/verify_schema_objects.py`; `scripts/export/notion_sync.py`; `scripts/export/oanda_export_2h_day.py`; `scripts/path1/build_evidence_pack_v0_2.py`; `scripts/path1/generate_queue_resolved.py`; `scripts/path1/overlays_v0_3.py`; `scripts/path1/run_evidence_queue.py`; `scripts/path1/run_evidence_range.py`; `scripts/path1/run_state_plane.py`; `scripts/path1/run_trajectory_families.py`; `scripts/path1/validate_post_run.py`; `scripts/path1_replay/lib.py`; `scripts/path1_replay/run_replay_verification.py`; `scripts/path1_seal/lib.py`; `scripts/path1_seal/run_seal_manifests.py`; `scripts/run/run_migration.py`; `scripts/run/run_option_c.ps1`; `scripts/run/run_option_c.sh`; `scripts/run/run_option_c_with_artifact.sh`; `scripts/run/run_option_c_wrapper.py`; `scripts/validate/pipeline_status.py`; `scripts/validate/validate_day.ps1`; `sql/00_schema.sql`; `sql/01_tables_min.sql`; `sql/02_derived_c1_c2_tables_v0_1.sql`; `sql/03_qa_derived_validation_v0_1.sql`; `sql/04_threshold_registry_v0_1.sql`; `sql/05_c3_regime_trend_v0_1.sql`; `sql/06_state_plane_threshold_pack_v0_2.sql`; `sql/90_verify_gate2.sql`; `sql/derived/v_ovc_c1_features_v0_1.sql`; `sql/derived/v_ovc_c2_features_v0_1.sql`; `sql/derived/v_ovc_c3_features_v0_1.sql`; `sql/derived/v_ovc_c_outcomes_v0_1.sql`; `sql/derived/v_ovc_state_plane_v0_2.sql`; `sql/option_c_run_report.sql`; `sql/option_c_v0_1.sql`; `sql/path1/db_patches/patch_create_evidence_views_20260120.sql`; `sql/path1/db_patches/patch_create_score_views_20260120.sql`; `sql/path1/db_patches/patch_m15_raw_20260122.sql`; `sql/qa_schema.sql`; `sql/qa_validation_pack.sql`; `sql/qa_validation_pack_core.sql`; `sql/qa_validation_pack_derived.sql`; `src/backfill_oanda_2h_checkpointed.py`; `src/backfill_oanda_m15_checkpointed.py`; `src/config/threshold_registry_v0_1.py`; `src/derived/compute_c1_v0_1.py`; `src/derived/compute_c2_v0_1.py`; `src/derived/compute_c3_regime_trend_v0_1.py`; `src/derived/compute_c3_stub_v0_1.py`; `src/history_sources/tv_csv.py`; `src/ingest_history_day.py`; `src/ovc_ops/run_artifact.py`; `src/ovc_ops/run_artifact_cli.py`; `src/validate/validate_derived_range_v0_1.py`; `src/validate_day.py`; `src/validate_range.py`; `tests/test_c3_regime_trend.py`; `tests/test_contract_equivalence.py`; `tests/test_derived_features.py`; `tests/test_fingerprint.py`; `tests/test_min_contract_validation.py`; `tests/test_path1_replay_structural.py`; `tests/test_threshold_registry.py`; `tools/parse_export.py`; `tools/validate_contract.py`; `trajectory_families/clustering.py`; `trajectory_families/fingerprint.py`; `trajectory_families/params_v0_1.json`
- Run fields mentioned: `run_id`; `run.json`; `run.log`; `checks.json`
- Schemas referenced: `ovc.ovc_blocks_v01_1_min`; `ovc.ovc_candles_m15_raw`; `ovc_cfg.threshold_pack`; `ovc_cfg.threshold_pack_active`; `ovc_cfg.threshold_packs`; `ovc_qa.validation_run`; `ovc_qa.expected_blocks`; `ovc_qa.tv_ohlc_2h`; `ovc_qa.ohlc_mismatch`; `ovc_qa.derived_validation_run`; `derived.ovc_c1_features_v0_1`; `derived.ovc_c2_features_v0_1`; `derived.ovc_c3_regime_trend_v0_1`; `derived.ovc_block_features_v0_1`; `derived.v_ovc_c1_features_v0_1`; `derived.v_ovc_c2_features_v0_1`; `derived.v_ovc_c3_features_v0_1`; `derived.v_ovc_c_outcomes_v0_1`; `derived.v_ovc_state_plane_v0_2`; `derived.v_path1_evidence_dis_v1_1`; `derived.v_path1_evidence_lid_v1_0`; `derived.v_path1_evidence_res_v1_0`; `derived.v_ovc_b_scores_dis_v1_1`; `derived.v_ovc_b_scores_lid_v1_0`; `derived.v_ovc_b_scores_res_v1_0`
- Scripts/tools referenced: `.github/workflows/backfill.yml`; `.github/workflows/backfill_m15.yml`; `.github/workflows/backfill_then_validate.yml`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `.github/workflows/ci_workflow_sanity.yml`; `.github/workflows/notion_sync.yml`; `.github/workflows/ovc_full_ingest.yml`; `.github/workflows/ovc_option_c_schedule.yml`; `.github/workflows/path1_evidence.yml`; `.github/workflows/path1_evidence_queue.yml`; `.github/workflows/path1_replay_verify.yml`; `scripts/ci/verify_schema_objects.py`; `scripts/export/notion_sync.py`; `scripts/export/oanda_export_2h_day.py`; `scripts/path1/build_evidence_pack_v0_2.py`; `scripts/path1/generate_queue_resolved.py`; `scripts/path1/overlays_v0_3.py`; `scripts/path1/run_evidence_queue.py`; `scripts/path1/run_evidence_range.py`; `scripts/path1/run_state_plane.py`; `scripts/path1/run_trajectory_families.py`; `scripts/path1/validate_post_run.py`; `scripts/path1_replay/lib.py`; `scripts/path1_replay/run_replay_verification.py`; `scripts/path1_seal/lib.py`; `scripts/path1_seal/run_seal_manifests.py`; `scripts/run/run_migration.py`; `scripts/run/run_option_c.ps1`; `scripts/run/run_option_c.sh`; `scripts/run/run_option_c_with_artifact.sh`; `scripts/run/run_option_c_wrapper.py`; `scripts/validate/pipeline_status.py`; `scripts/validate/validate_day.ps1`; `tools/parse_export.py`; `tools/validate_contract.py`
- Must/shall/invalidates phrases: None
### Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md
- References: `docs/contracts/A_TO_D_CONTRACT_v1.md`; `docs/contracts/option_a_ingest_contract_v1.md`; `docs/contracts/option_b_derived_contract_v1.md`; `docs/contracts/option_c_outcomes_contract_v1.md`; `docs/contracts/option_d_evidence_contract_v1.md`; `docs/contracts/qa_validation_contract_v1.md`; `docs/contracts/ingest_boundary.md`; `docs/contracts/derived_layer_boundary.md`; `docs/contracts/c_layer_boundary_spec_v0.1.md`; `docs/contracts/PATH2_CONTRACT_v1_0.md`; `contracts/export_contract_v0.1.1_min.json`; `contracts/export_contract_v0.1_full.json`; `contracts/derived_feature_set_v0.1.json`; `contracts/run_artifact_spec_v0.1.json`; `contracts/eval_contract_v0.1.json`; `docs/doctrine/OVC_DOCTRINE.md`; `docs/doctrine/GATES.md`; `docs/doctrine/IMMUTABILITY_NOTICE.md`; `docs/governance/GOVERNANCE_RULES_v0.1.md`; `docs/governance/BRANCH_POLICY.md`
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: None
- Must/shall/invalidates phrases: None

### Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md
- References: `contracts/export_contract_v0.1.1_min.json`; `contracts/derived_feature_set_v0.1.json`; `contracts/run_artifact_spec_v0.1.json`; `infra/ovc-webhook/src/index.ts`; `tests/test_contract_equivalence.py`; `tests/test_derived_features.py`; `tests/test_min_contract_validation.py`; `tests/test_path1_replay_structural.py`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `sql/90_verify_gate2.sql`; `sql/qa_validation_pack*.sql`; `tools/validate_contract.py`; `schema/required_objects.txt`
- Run fields mentioned: None
- Schemas referenced: None
- Scripts/tools referenced: `infra/ovc-webhook/src/index.ts`; `tests/test_contract_equivalence.py`; `tests/test_derived_features.py`; `tests/test_min_contract_validation.py`; `tests/test_path1_replay_structural.py`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `sql/90_verify_gate2.sql`; `sql/qa_validation_pack*.sql`; `tools/validate_contract.py`
- Must/shall/invalidates phrases: None

## 3) Enforcement Surface Index
| Rule Source File | Enforcement Mechanism Mentioned (script/test/gate/check) | Where (path) | Severity (invalid/warn/unspecified) |
|---|---|---|---|
| docs/doctrine/ovc_logging_doctrine_v0.1.md | Invalidates run | Not stated | invalid |
| docs/doctrine/IMMUTABILITY_NOTICE.md | CI checks validate schema consistency | Not stated | unspecified |
| docs/governance/GOVERNANCE_RULES_v0.1.md | Mandatory human review (critical paths) | `sql/01_tables_min.sql`; `contracts/export_contract_v0.1.1_min.json`; `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md`; `docs/ops/GOVERNANCE_RULES_v0.1.md`; `infra/ovc-webhook/src/index.ts` | invalid |
| docs/contracts/qa_validation_contract_v1.md | CI gates (HARD FAIL) | `ci_workflow_sanity.yml`; `ci_pytest.yml`; `ci_schema_check.yml` | invalid |
| docs/contracts/qa_validation_contract_v1.md | Validation scripts | `src/validate_day.py`; `src/validate_range.py`; `src/validate/validate_derived_range_v0_1.py`; `sql/qa_validation_pack_core.sql`; `sql/03_qa_derived_validation_v0_1.sql` | unspecified |
| docs/contracts/option_b_derived_contract_v1.md | Validation script | `src/validate/validate_derived_range_v0_1.py` | unspecified |
| docs/contracts/option_b_derived_contract_v1.md | SQL gate | `sql/90_verify_gate2.sql` | unspecified |
| docs/contracts/option_c_outcomes_contract_v1.md | Workflow requirement | `ovc_option_c_schedule.yml` | unspecified |
| docs/contracts/option_d_ops_boundary.md | Exit code policy | Not stated | warn/invalid |
| Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md | Test/CI/Tool enforcement points | `tests/test_contract_equivalence.py`; `tests/test_derived_features.py`; `tests/test_min_contract_validation.py`; `tests/test_path1_replay_structural.py`; `.github/workflows/ci_pytest.yml`; `.github/workflows/ci_schema_check.yml`; `tools/validate_contract.py`; `sql/90_verify_gate2.sql` | unspecified |

## 4) Coupling Reality Check (Descriptive)
Docs that claim to govern runs but do NOT reference any artifact mechanism:
- docs/contracts/A_TO_D_CONTRACT_v1.md (mentions run provenance rules but no `run.json`/`checks.json`/`run.log`/`reports/runs/` references in this file)
- docs/contracts/option_b_derived_contract_v1.md (mentions `run_id` and run provenance table but no `run.json`/`checks.json`/`run.log`/`reports/runs/` references in this file)
- docs/contracts/option_c_outcomes_contract_v1.md (mentions `run_id`/`eval_runs` but no `run.json`/`checks.json`/`run.log`/`reports/runs/` references in this file)

Artifacts that exist but are NOT referenced by any canon/governance doc (from inspected set only):
- .codex/ (not referenced in docs/doctrine/*, docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md, docs/architecture/legend_canonicalization_purpose.md, docs/governance/*)
- artifacts/derived_validation/ (not referenced in docs/doctrine/*, docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md, docs/architecture/legend_canonicalization_purpose.md, docs/governance/*)
- reports/path1/evidence/runs/ (not referenced in docs/doctrine/*, docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md, docs/architecture/legend_canonicalization_purpose.md, docs/governance/*)
- reports/verification/ (not referenced in docs/doctrine/*, docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md, docs/architecture/legend_canonicalization_purpose.md, docs/governance/*)
