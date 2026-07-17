# OVC R1 Governance Artifact Inventory

**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

Classification values are the R1 values: `AUTHORITATIVE`, `SUPPORTING`,
`SUPERSEDED`, `CONFLICTING`, `UNRESOLVED`, and
`UNVERIFIED_DEPLOYMENT`.

`SUPERSEDED` is reserved for a completed, evidenced authority transition.
Historical retention and denial of new execution are recorded separately and
do not by themselves make a supersession effective.

## Authority Spine

| Path | R1 class | Basis |
|---|---|---|
| `docs/doctrine/OVC_DOCTRINE.md` | AUTHORITATIVE | Declares system epistemic boundaries. |
| `docs/doctrine/IMMUTABILITY_NOTICE.md` | AUTHORITATIVE | Canonical immutability rule. |
| `docs/doctrine/GATES.md` | SUPPORTING | Gate narrative; not a complete current enforcement map. |
| `docs/doctrine/ovc_logging_doctrine_v0.1.md` | AUTHORITATIVE | Run/logging validity rules. |
| `docs/governance/GOVERNANCE_RULES_v0.1.md` | AUTHORITATIVE | `[STATUS: CANONICAL]`; lifecycle and change rules. |
| `docs/governance/BRANCH_POLICY.md` | AUTHORITATIVE | Branch governance. |
| `docs/governance/OVC_GOVERNANCE_REFERENCE_v0.1.md` | CONFLICTING | Declares an authority spine but contains stale paths and elevates DRAFT contracts. |
| `docs/governance/decisions.md` | SUPPORTING | Existing decision log; only one dated decision. |
| `docs/governance/contracts/phase_2_3/UPGRADE_CONTRACTS_v0_1.md` | AUTHORITATIVE | Frozen normative maintenance law. |
| `docs/governance/contracts/phase_2_3/DEPRECATION_CONTRACTS_v0_1.md` | AUTHORITATIVE | Frozen normative maintenance law. |
| `docs/governance/contracts/phase_2_3/RECOVERY_CONTRACTS_v0_1.md` | AUTHORITATIVE | Frozen normative maintenance law. |
| `docs/governance/contracts/phase_2_3/HEALTH_CONTRACTS_v0_1.md` | AUTHORITATIVE | Frozen normative maintenance law. |
| `docs/governance/contracts/phase_2_3/PHASE_2_3_CLOSING_DECLARATION.md` | AUTHORITATIVE | Records Phase 2.3 closure and retains v0.1 operational governance. |

## Operational Governance

| Path | R1 class | Basis |
|---|---|---|
| `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md` | AUTHORITATIVE | Base authority retained for its existing operation entries. |
| `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md` | AUTHORITATIVE | Ratified additive extension containing only OP-QA07, OP-QA09, and OP-QA11 with recorded limitations. |
| `docs/governance/OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md` | AUTHORITATIVE | Frozen enforcement map, but some observations are stale. |
| `docs/governance/OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md` | SUPPORTING | Historical metrics bound to the Phase 1.5 inventory. |
| `docs/governance/PHASE_1_5_CLOSURE_DECLARATION.md` | AUTHORITATIVE | Declares the governed Phase 1.5 boundary and bounded gaps. |
| `docs/phase_2_2/OVC_ALLOWED_OPERATIONS_CATALOG_v0.2.md` | SUPPORTING | Historical DRAFT proposal; not the ratified catalog and not independent authority for QA08 or QA10. |
| `docs/phase_2_2/OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.2.md` | UNRESOLVED | DRAFT extension for OP-QA07 through OP-QA11. |
| `docs/phase_2_2/OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.2.md` | SUPPORTING | DRAFT metrics for the proposed v0.2 boundary. |
| `docs/governance/CHANGE_TAXONOMY_v0_1.md` | SUPPORTING | Historical base taxonomy retained; PS-11 is not effective without v0.2 ratification evidence. |
| `docs/governance/CHANGE_TAXONOMY_v0_2.md` | UNRESOLVED | Implemented by `scripts/governance/classify_change.py`, but no formal ratification record was found. |
| `docs/governance/RUN_ENVELOPE_STANDARD_v0_1.md` | AUTHORITATIVE | ACTIVE run-envelope standard. |
| `docs/governance/ARCHIVE_NON_CANONICAL_v0.1.md` | SUPPORTING | Records non-canonical/library-only treatment. |
| `docs/governance/PRUNE_PLAN_v0.1.md` | SUPPORTING | Historical plan, not execution authority. |
| `docs/governance/PHASE_2_1_CLOSURE_DECLARATION.md` | AUTHORITATIVE | Closes registry/drift/system-health evidence phase. |
| `docs/governance/EXPECTED_VERSIONS_v0_1.json` | AUTHORITATIVE | Expected-version registry input. |
| `docs/governance/DIRECTORY_WAVE_MAP_v2.md` | SUPPORTING | Architectural wave map. |
| `docs/governance/DRIFT_REPORT_v2.md` | SUPPORTING | Historical drift evidence. |
| `docs/governance/OVC ARCHITECTURAL WAVES v2.md` | SUPPORTING | Conceptual wave model. |
| `docs/governance/WAVE_COVERAGE_MATRIX_v2.md` | SUPPORTING | Coverage derivation. |
| `docs/governance/WAVE_ENFORCEMENT_COVERAGE_v1.md` | SUPPORTING | Enforcement derivation. |

Genesis hybrid records are evidence, not authority:

- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_ASSIGNMENTS_v0.1.tsv`
- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_CONFLICTS_v0.1.tsv`
- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_CONSISTENCY_SUMMARY_v0.1.md`
- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_NOT_TRACKED_NOW_v0.1.tsv`
- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_PATTERN_PARSE_ERRORS_v0.1.md`
- `docs/governance/GENESIS_HYBRID/GENESIS_HYBRID_UNMATCHED_TOP_ROOTS_v0.1.md`

All six are classified `SUPPORTING`.

## ABCD and QA Contracts

| Path | R1 class | Basis |
|---|---|---|
| `docs/contracts/A_TO_D_CONTRACT_v1.md` | CONFLICTING | Used as master contract but retains DRAFT status and conflicts with live A semantics. |
| `docs/contracts/option_a_ingest_contract_v1.md` | CONFLICTING | DRAFT general contract; refined by ACTIVE A1/A2 contracts. |
| `docs/contracts/option_a1_bar_ingest_contract_v1.md` | AUTHORITATIVE | ACTIVE field-level A1 contract. |
| `docs/contracts/option_a2_event_ingest_contract_v1.md` | AUTHORITATIVE | ACTIVE field-level A2 contract. |
| `docs/contracts/ingest_boundary.md` | AUTHORITATIVE | Ingest responsibility boundary. |
| `docs/contracts/min_contract_alignment.md` | SUPPORTING | Operational alignment guide. |
| `docs/contracts/option_b_derived_contract_v1.md` | AUTHORITATIVE | ACTIVE v1.1 contract, superseding its v1.0 draft state. |
| `docs/contracts/c_feature_registry_freeze_v0_1.md` | AUTHORITATIVE | FROZEN C1/C2/C3 interface registry. |
| `docs/contracts/c3_semantic_contract_v0_1.md` | AUTHORITATIVE | FROZEN threshold-pack semantic contract. |
| `docs/contracts/c_layer_boundary_spec_v0.1.md` | CONFLICTING | Normative claim with DRAFT/approval-required status and unresolved tier decisions. |
| `docs/contracts/derived_layer_boundary.md` | SUPPORTING | Earlier broad boundary, less specific than the active Option B contract. |
| `docs/contracts/option_c_outcomes_contract_v1.md` | CONFLICTING | Explicitly resolves C authority but remains DRAFT. |
| `docs/contracts/option_c_boundary.md` | CONFLICTING | Earlier boundary authorizes direct A reads and the legacy outcomes view. |
| `docs/contracts/outcomes_definitions_v0.1.md` | SUPPORTING | Outcome formula definitions. |
| `docs/contracts/option_d_evidence_contract_v1.md` | CONFLICTING | Governing evidence contract remains DRAFT. |
| `docs/contracts/option_d_ops_boundary.md` | AUTHORITATIVE | Sealed Option C orchestration/failure policy. |
| `docs/contracts/qa_validation_contract_v1.md` | CONFLICTING | Required QA contract remains DRAFT and has stale script paths. |
| `docs/contracts/PATH2_CONTRACT_v1_0.md` | SUPPORTING | Specification-only; Path2 is not implemented. |
| `docs/contracts/tradingview_reference_contract_v0_1.md` | SUPPORTING | Reference/tolerance contract. |
| `docs/contracts/CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` | UNRESOLVED | Draft protocol skeleton with no ratification artifact. |
| `docs/contracts/AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1.md` | SUPPORTING | Explicitly non-authoritative formatter/classifier contract. |

Machine-readable contracts:

| Path | R1 class | Basis |
|---|---|---|
| `contracts/export_contract_v0.1.1_min.json` | AUTHORITATIVE | IMMUTABLE live MIN wire contract. |
| `contracts/export_contract_v0.1_min.json` | SUPPORTING | Historical MIN contract; PS-01 is not effective because no compliant deprecation record exists. |
| `contracts/export_contract_v0.1_full.json` | SUPPORTING | FULL profile remains optional/non-primary. |
| `contracts/eval_contract_v0.1.json` | CONFLICTING | Requires direct canonical-table input and legacy horizons. |
| `contracts/derived_feature_set_v0.1.json` | SUPPORTING | Historical combined-view machine contract; PS-02 is deferred until a versioned machine-readable replacement exists. |
| `contracts/run_artifact_spec_v0.1.json` | AUTHORITATIVE | Run artifact schema. |
| `docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json` | AUTHORITATIVE | Change-ledger schema. |
| `docs/contracts/schemas/AUDIT_INTERPRETATION_REPORT_v0.1.json` | SUPPORTING | Audit interpreter output schema. |
| `docs/contracts/templates/audit_interpretation_report_v0.1.example.json` | SUPPORTING | Non-authoritative example. |

## Registry and Ledger Artifacts

The following are `AUTHORITATIVE` registry-layer artifacts:

- `docs/phase_2_2/REGISTRY_CATALOG_v0_1.json`
- `docs/phase_2_2/REGISTRY_CATALOG_ADDENDUM_v0_1__phase_2_2_3.json`
- `docs/phase_2_2/REGISTRY_SEAL_CONTRACT_v0_1.md`
- `docs/phase_2_2/REGISTRY_LAYER_RUNBOOK_v0_1.md`
- `docs/phase_2_2/REGISTRY_ARTIFACT_TYPES_v0_1.md`
- `docs/phase_2_2/ACTIVE_REGISTRY_POINTERS_v0_1.json`
- `docs/phase_2_2/schemas/REGISTRY_derived_validation_reports_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_drift_signals_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_evidence_pack_v0_2.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_expected_versions_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_fingerprint_index_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_migration_ledger_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_op_status_table_v0_1.array.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_op_status_table_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_registry_delta_log_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_run_registry_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_system_health_report_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_threshold_packs_file_v0_1.schema.json`
- `docs/phase_2_2/schemas/REGISTRY_validation_range_results_v0_1.schema.json`

The following are `SUPPORTING` implementation or validation evidence:

- `docs/phase_2_2/builders/build_registry_delta_log_v0_1.py`
- `docs/phase_2_2/validators/seal_promote_v0_1.py`
- `docs/phase_2_2/validators/validate_active_pointers_v0_1.py`
- `docs/phase_2_2/validators/validate_registry_schema_v0_1.py`
- `docs/phase_2_2/validators/validate_registry_seals_v0_1.py`
- `docs/phase_2_2/GOVERNANCE_MAPPING_v0_1.md`
- `docs/phase_2_2/PHASE_2_2_DOD_CHECKLIST.md`
- `docs/phase_2_2/PHASE_2_2_1_COMPLETION_REPORT.md`
- `docs/phase_2_2/PHASE_2_2_1_VALIDATION_REPORT.md`
- `docs/phase_2_2/PHASE_2_2_2_VALIDATION_REPORT.md`
- `docs/phase_2_2/PHASE_2_2_3_COMPLETION_REPORT.md`
- `docs/phase_2_2/PHASE_2_2_3_VALIDATION_REPORT.md`
- `docs/phase_2_2/SEAL_PROMOTION_RESULTS.json`
- `docs/phase_2_2/THRESHOLD_REGISTRY_ASSESSMENT_v0_1.md`

Migration authority:

| Path | R1 class | Basis |
|---|---|---|
| `schema/applied_migrations.json` | UNVERIFIED_DEPLOYMENT | Every entry is UNVERIFIED; one referenced SQL file is missing. |
| `schema/required_objects.txt` | AUTHORITATIVE | Current CI required-object allowlist. |
| `artifacts/derived_validation/LATEST.txt` | SUPERSEDED | PS-12 condition is met: active-pointer governance explicitly selects the sealed replacement and records `LATEST.txt` as backward-compatible but non-authoritative. |

## Architecture and Conceptual Maps

| Path | R1 class | Basis |
|---|---|---|
| `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` | SUPPORTING | Historical governance evidence; its current operational claims are replaced by operator-approved v0.2. |
| `docs/architecture/OVC_DATA_FLOW_CANON_v0.2.md` | AUTHORITATIVE | Operator-approved current data-flow claims; records implementation nonconformance without changing runtime state. |
| `docs/architecture/PIPELINE_REALITY_MAP_v0.1.md` | SUPPORTING | Implementation-oriented map. |
| `docs/architecture/PIPELINE_REALITY_MAP_v0.1.changelog.md` | SUPPORTING | Change history. |
| `docs/architecture/derived_metric_registry_v0.1.md` | SUPPORTING | Derived metric narrative. |
| `docs/architecture/metric_map_pine_to_c_layers.md` | SUPPORTING | Cross-layer conceptual map. |
| `docs/architecture/ovc_metric_architecture.md` | SUPPORTING | Conceptual metric architecture. |
| `docs/architecture/dashboard_mapping_v0.1.md` | CONFLICTING | Projects legacy Option C views. |
| `docs/architecture/metric_trial_log_noncanonical_v0.md` | SUPPORTING | Historical non-canonical trial log; no effective replacement transition is asserted. |
| `docs/architecture/legend_canonicalization_purpose.md` | SUPPORTING | Legend governance rationale. |
| `docs/architecture/PRUNING_CANDIDATES_v0.1.md` | SUPPORTING | Candidate list, not authority. |
| `docs/pipeline/CURRENT_STATE_A_TO_D.md` | SUPPORTING | Preserved historical snapshot; PS-10 replaces only its current-state claims. |
| `docs/pipeline/CURRENT_STATE_DEP_GRAPH.md` | SUPPORTING | Frozen dependency snapshot with stale details. |
| `docs/pipeline/CURRENT_STATE_INVARIANTS.md` | SUPPORTING | Preserved historical snapshot; R0/R1 replace only its current-state claims. |
| `docs/pipeline/CURRENT_STATE_TRUST_MAP.md` | SUPPORTING | Historical trust snapshot. |
| `docs/governance/CANONICAL_REPO_MAP_v0.1.md` | SUPPORTING | DRAFT coordinate map; explicitly non-resolving. |
| `docs/REPO_MAP/REPO_TOPOLOGY_v0.1.md` | SUPPORTING | Commit-bound topology snapshot. |
| `docs/REPO_MAP/MODULE_INDEX_v0.1.md` | SUPPORTING | Module inventory. |
| `docs/REPO_MAP/BORDERLANDS_v0.1.md` | SUPPORTING | Ambiguity inventory. |
| `docs/REPO_MAP/CATEGORY_PROCESS_APPENDIX_DRAFT.md` | UNRESOLVED | Draft category model. |
| `docs/REPO_MAP/OPT_A__ORG_MAP_DRAFT.md` | UNRESOLVED | Draft organization map. |
| `docs/REPO_MAP/OPT_B__ORG_MAP_DRAFT.md` | UNRESOLVED | Draft organization map. |
| `docs/REPO_MAP/OPT_C__ORG_MAP_DRAFT.md` | UNRESOLVED | Draft organization map. |
| `docs/REPO_MAP/OPT_D__ORG_MAP_DRAFT.md` | UNRESOLVED | Draft organization map. |
| `docs/REPO_MAP/QA__ORG_MAP_DRAFT.md` | UNRESOLVED | Draft organization map. |

All files under `Tetsu/OVC_REPO_MAZE/` are classified `SUPPORTING`. The
repository itself and corroborated contracts outrank the Maze. Exact paths:

- `Tetsu/OVC_REPO_MAZE/00_REPO_MAZE.md`
- `Tetsu/OVC_REPO_MAZE/01_OPTION_A__INGEST.md`
- `Tetsu/OVC_REPO_MAZE/02_OPTION_B_DERIVED.md`
- `Tetsu/OVC_REPO_MAZE/03_OPTION_C_OUTCOMES.md`
- `Tetsu/OVC_REPO_MAZE/04_OPTION_D_PATHS_BRIDGE.md`
- `Tetsu/OVC_REPO_MAZE/05_QA_GOVERNANCE.md`
- `Tetsu/OVC_REPO_MAZE/ANCHOR_CATALOG.md`
- `Tetsu/OVC_REPO_MAZE/A_D_BOUNDARY.md`
- `Tetsu/OVC_REPO_MAZE/ROOM__ARTIFACTS.md`
- `Tetsu/OVC_REPO_MAZE/ROOM__DOCS.md`
- `Tetsu/OVC_REPO_MAZE/ROOM__REPORTS.md`
- `Tetsu/OVC_REPO_MAZE/ROOM__SQL.md`
- `Tetsu/OVC_REPO_MAZE/ROOM__WORKFLOWS.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/00_README__GRAPH_ATLAS.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/01_CANVAS_LAYOUT_SPEC.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/02_CANVAS__OVC_ATLAS.canvas`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/02_CANVAS__OVC_ATLAS_resolved.canvas`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.drawio`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_11__OVERVIEW__QA_GATES.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_12__OVERVIEW__ORCHESTRATION.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/OPTION FLOW GRAPH.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_20__OPT_A__PIPELINE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_21__OPT_B__PIPELINE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_22__OPT_C__PIPELINE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_23__OPT_D__PIPELINE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/GRAPH_24__QA__PIPELINE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/20_INTERNAL_PIPELINES/OPTION INTERNAL PIPELINE GRAPH.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/A&C FLOW GRAPH.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/40_ARTIFACTS_VALIDATION/A&C FLOW GRAPH.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/40_ARTIFACTS_VALIDATION/GRAPH_40__ARTIFACT_LIFECYCLE.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/40_ARTIFACTS_VALIDATION/GRAPH_41__VALIDATION_CHAIN.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/50_STORES_TOPOLOGY/GRAPH_50__NEON_SCHEMA_TOPOLOGY.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/50_STORES_TOPOLOGY/GRAPH_51__EXTERNAL_STORES.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_PER_GRAPH.md`
- `Tetsu/OVC_REPO_MAZE/OVC_REPO_MAZE.canvas`

## Workflow Governance

| Path | R1 class | Current trigger truth |
|---|---|---|
| `.github/workflows/backfill.yml` | AUTHORITATIVE | Manual plus `17 */6 * * *`. |
| `.github/workflows/backfill_m15.yml` | AUTHORITATIVE | Manual only. |
| `.github/workflows/backfill_then_validate.yml` | CONFLICTING | Manual; C3 invocation lacks required args. |
| `.github/workflows/ovc_option_c_schedule.yml` | CONFLICTING | Manual locally; R0 observed remote scheduled failures. |
| `.github/workflows/path1_evidence.yml` | AUTHORITATIVE | Manual plus `15 3 * * *`; R0 observed success. |
| `.github/workflows/path1_evidence_queue.yml` | SUPPORTING | Historical/manual recovery candidate only; not canonical and not authorized to mutate canonical queue state. |
| `.github/workflows/main.yml` | CONFLICTING | Still schedules the rejected queue production path every six hours. |
| `.github/workflows/path1_replay_verify.yml` | AUTHORITATIVE | Manual plus `0 3 * * *`; latest R0 run failed. |
| `.github/workflows/notion_sync.yml` | CONFLICTING | Manual locally; calls missing path; R0 observed remote scheduled failure. |
| `.github/workflows/ci_pytest.yml` | AUTHORITATIVE | PR/push QA gate. |
| `.github/workflows/ci_schema_check.yml` | CONFLICTING | Verifies object existence, but migration ledger check is syntax-only. |
| `.github/workflows/ci_workflow_sanity.yml` | CONFLICTING | Current repo still contains a workflow with a missing script path. |
| `.github/workflows/change_classifier.yml` | UNRESOLVED | Implements unratified Change Taxonomy v0.2. |
| `.github/workflows/append_sentinel.yml` | UNRESOLVED | Active control workflow absent from authoritative operations catalog. |
| `.github/workflows/repo_cartographer.yml` | UNRESOLVED | Active control workflow absent from authoritative operations catalog. |
| `.github/workflows/design_record_engine_ci.yml` | UNRESOLVED | Zero-byte workflow scaffold; no active CI definition and no authoritative operation record. |

Workflow doctrine:

| Path | R1 class | Basis |
|---|---|---|
| `docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md` | AUTHORITATIVE | Declares the single canonical loop and bans queue mutation. |
| `docs/workflows/WORKFLOW_CATALOG_v0_1.md` | SUPPORTING | Historical workflow inventory retained by PS-08. |
| `docs/workflows/WORKFLOW_CATALOG_v0_2.md` | AUTHORITATIVE | Operator-approved current repository inventory and execution disposition. |

## Projection Surfaces

| Path or object | R1 class | Basis |
|---|---|---|
| `scripts/export/notion_sync.py` | CONFLICTING | Actual implementation path, but reads the deprecated outcomes view. |
| `sql/04_ops_notion_sync.sql` | AUTHORITATIVE | Defines the sync cursor table. |
| `infra/ovc-webhook/wrangler.jsonc` | UNVERIFIED_DEPLOYMENT | Declares Worker and R2 binding; live Cloudflare state unavailable. |
| `infra/ovc-webhook/src/index.ts` | CONFLICTING | A1 authority applies, but run-report writes do not match deployed table schema. |

The Notion workflow and canonical data-flow document are classified once in
the Workflow Governance and Architecture sections above; both also govern
projection behavior.

## Current-State Evidence

| Path | R1 class | Basis |
|---|---|---|
| `docs/current-state/OVC_CURRENT_STATE_DELTA_2026-07-15_ae88bca49e94.md` | AUTHORITATIVE | Commit-bound R0 live-state evidence and explicit unknowns. |
| `docs/current-state/r1/OVC_R1_OPERATOR_DECISION_LEDGER_2026-07-16_59db182dfbdd.md` | AUTHORITATIVE | Records the final operator rulings and R1 closure disposition. |
| `docs/current-state/r1/OVC_R1_QA07_QA11_RATIFICATION_REVIEW_2026-07-16_59db182dfbdd.md` | SUPPORTING | Records the individual review and final QA07-QA11 decisions. |
| `docs/current-state/r1/OVC_R1_CLOSURE_DECISION_2026-07-16_59db182dfbdd.md` | AUTHORITATIVE | Closes R1 as `PASS_WITH_CARRIED_UNRESOLVED_ITEMS` and keeps R2 as a separate decision. |

## Newer Governance Components

| Component paths | R1 class | Basis |
|---|---|---|
| `scripts/sentinel/append_sentinel.py`, `scripts/sentinel/sentinel_state.json`, `scripts/sentinel/README.md`, `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl`, `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl` | UNRESOLVED | Branch-specific authority is documented, but no authoritative operation record exists. |
| `scripts/governance/classify_change.py`, `scripts/governance/build_change_classification_overlay_v0_2.py`, `docs/governance/CHANGE_TAXONOMY_v0_2.md` | UNRESOLVED | Implementation agrees internally, but PS-11 ratification evidence is absent. |
| `scripts/repo_cartographer/`, `docs/baselines/`, `docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl` | UNRESOLVED | Strong local contracts exist, but stable required outputs are currently absent and no authoritative operation record exists. |
| `scripts/design_record_engine/`, `docs/design_record_engine/`, `tests/design_record_engine/` | UNRESOLVED | Scripts and tests exist, but the named CI workflow is zero bytes and the component is outside the authoritative operations catalog. |
| `tools/phase3_control_panel/` | SUPPORTING | Read-only governance UI with its own contract; not ABCD execution authority. |
