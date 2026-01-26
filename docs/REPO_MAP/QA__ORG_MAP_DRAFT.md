# QA Organization Map (Draft)
## Purpose
Map QA, governance, documentation, and cross-cutting repo infrastructure.

## Option Scope (brief)
Tests, validation harnesses, determinism checks, golden fixtures, governance logs, and CI checks.

## Category Index (list folders by category)
- QA & Governance: .github, .github/workflows, tests, scripts/ci, scripts/validate, schema, contracts, docs/governance, docs/validation, reports/validation, reports/verification, reports/pipeline_audit, CLAIMS, src/validate
- Documentation & Maps: docs, docs/architecture, docs/contracts, docs/doctrine, docs/evidence_pack, docs/examples, docs/history, docs/history/path2, docs/operations, docs/option_d, docs/path1, docs/path2, docs/pipeline, docs/runbooks, docs/specs, docs/specs/system, docs/state_plane, docs/workflows, releases, Tetsu, Tetsu/OVC_REPO_MAZE
- Experiments & Sandbox: research, research/notebooks, research/scores, research/studies, research/tooling, specs, chmod_test, testdir, testdir2, .venv
- Artifacts & Evidence: __pycache__, src/__pycache__, scripts/__pycache__, tests/__pycache__, tools/__pycache__, trajectory_families/__pycache__, .pytest_cache, .pytest-tmp, .pytest-tmp2, data/verification_private, data/verification_private/2026-01-19, data/verification_private/2026-01-19/outputs
- Orchestration: .claude, .vscode, .git, Tetsu/.obsidian

## Folder-by-Folder Map
FOLDER: .github
PRIMARY CATEGORY: Orchestration
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): GitHub automation and workflow definitions.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): CI/CD runs and artifacts

CONTAINS (high-signal items):
- workflows/ -> Orchestration/QA/CANONICAL -> CI and scheduled workflows

CROSS-REFERENCES:
- Option A/B/C/D maps for workflow usage

FOLDER: .github/workflows
PRIMARY CATEGORY: Orchestration
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Workflow definitions for CI, backfill, evidence, and schedules.

INPUTS (contracts/interfaces): scripts/*; src/*
OUTPUTS (artifacts/data): CI runs, scheduled runs, artifacts

CONTAINS (high-signal items):
- backfill.yml -> Orchestration/A/SUPPORTING -> backfill pipeline
- backfill_m15.yml -> Orchestration/A/SUPPORTING -> backfill m15
- backfill_then_validate.yml -> Orchestration/B/SUPPORTING -> backfill + validation
- ovc_full_ingest.yml -> Orchestration/A/SUPPORTING -> full ingest
- ovc_option_c_schedule.yml -> Orchestration/C/SUPPORTING -> Option C schedule
- path1_evidence.yml -> Orchestration/D/SUPPORTING -> Path1 evidence run
- path1_evidence_queue.yml -> Orchestration/D/SUPPORTING -> queue runner
- path1_replay_verify.yml -> Orchestration/D/SUPPORTING -> replay verify
- ci_workflow_sanity.yml -> QA/QA/SUPPORTING -> workflow sanity checks
- ci_pytest.yml -> QA/QA/SUPPORTING -> pytest
- ci_schema_check.yml -> QA/QA/SUPPORTING -> schema checks
- main.yml -> Orchestration/Cross/UNKNOWN -> main workflow (unclassified)
- notion_sync.yml -> Orchestration/D/SUPPORTING -> Notion sync

CROSS-REFERENCES:
- Option C map for run_option_c runners

FOLDER: tests
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Automated test suite for derived features, contracts, and determinism.

INPUTS (contracts/interfaces): contracts/*.json; src/*; trajectory_families/*
OUTPUTS (artifacts/data): pytest outputs, test artifacts

CONTAINS (high-signal items):
- test_derived_features.py -> QA/QA/CANONICAL -> derived feature tests
- test_l3_regime_trend.py -> QA/QA/CANONICAL -> L3 regime tests
- test_contract_equivalence.py -> QA/QA/CANONICAL -> contract consistency
- test_min_contract_validation.py -> QA/QA/CANONICAL -> export contract tests
- test_threshold_registry.py -> QA/QA/CANONICAL -> registry tests
- fixtures/ -> Artifacts & Evidence/QA/SUPPORTING -> golden inputs
- sample_exports/ -> Artifacts & Evidence/QA/SUPPORTING -> contract samples

CROSS-REFERENCES:
- Option B map for derived feature scope

FOLDER: scripts/ci
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): CI helper scripts.

INPUTS (contracts/interfaces): schema/required_objects.txt
OUTPUTS (artifacts/data): schema verification output

CONTAINS (high-signal items):
- verify_schema_objects.py -> QA/QA/SUPPORTING -> schema checks

CROSS-REFERENCES:
- Option D map for CI usage

FOLDER: scripts/validate
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Validation entrypoints.

INPUTS (contracts/interfaces): docs/validation/*; sql/qa_validation_pack*.sql
OUTPUTS (artifacts/data): validation logs and summaries

CONTAINS (high-signal items):
- pipeline_status.py -> QA/QA/SUPPORTING -> pipeline status check
- validate_day.ps1 -> QA/QA/SUPPORTING -> validation runner

CROSS-REFERENCES:
- Option D map for report outputs

FOLDER: schema
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Schema ledger and required object list.

INPUTS (contracts/interfaces): sql/*.sql
OUTPUTS (artifacts/data): applied_migrations.json, required_objects.txt

CONTAINS (high-signal items):
- applied_migrations.json -> QA/QA/CANONICAL -> migration ledger
- required_objects.txt -> QA/QA/CANONICAL -> object inventory

CROSS-REFERENCES:
- Option B/D maps for sql and patch usage

FOLDER: contracts
PRIMARY CATEGORY: Contracts
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): JSON contracts for exports, derived features, and run artifacts.

INPUTS (contracts/interfaces): docs/contracts/*
OUTPUTS (artifacts/data): contract JSONs consumed by tools/tests

CONTAINS (high-signal items):
- derived_feature_set_v0.1.json -> Contracts/B/CANONICAL -> derived features
- export_contract_v0.1_min.json -> Contracts/D/CANONICAL -> export minimum
- export_contract_v0.1_full.json -> Contracts/D/CANONICAL -> export full
- eval_contract_v0.1.json -> Contracts/C/SUPPORTING -> evaluation contract
- run_artifact_spec_v0.1.json -> Contracts/D/CANONICAL -> run artifact spec

CROSS-REFERENCES:
- Option B/C/D maps for contract usage

FOLDER: docs
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Repository documentation root.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): design specs, governance docs, runbooks

CONTAINS (high-signal items):
- architecture/ -> Documentation & Maps/Cross/CANONICAL -> architecture maps
- contracts/ -> Contracts/Cross/CANONICAL -> contract documents
- doctrine/ -> QA & Governance/QA/CANONICAL -> doctrine and logging
- evidence_pack/ -> Documentation & Maps/D/SUPPORTING -> evidence pack spec
- governance/ -> QA & Governance/QA/CANONICAL -> governance rules
- history/ -> Documentation & Maps/D/SUPPORTING -> path history docs
- operations/ -> Documentation & Maps/D/SUPPORTING -> ops procedures
- pipeline/ -> Documentation & Maps/Cross/CANONICAL -> current state maps
- runbooks/ -> Documentation & Maps/Cross/SUPPORTING -> operator runbooks
- specs/ -> Documentation & Maps/Cross/CANONICAL -> option specs
- validation/ -> QA & Governance/QA/CANONICAL -> validation reports
- workflows/ -> Documentation & Maps/Cross/SUPPORTING -> workflow catalog

CROSS-REFERENCES:
- Option A/B/C/D maps for option-specific docs

FOLDER: docs/architecture
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): Architecture and pipeline reality maps.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): architecture docs

CONTAINS (high-signal items):
- OVC_DATA_FLOW_CANON_v0.1.md -> Documentation & Maps/Cross/CANONICAL -> data flow map
- PIPELINE_REALITY_MAP_v0.1.md -> Documentation & Maps/Cross/CANONICAL -> pipeline reality
- derived_metric_registry_v0.1.md -> Documentation & Maps/B/SUPPORTING -> registry map

CROSS-REFERENCES:
- Option B map for derived registry alignment

FOLDER: docs/contracts
PRIMARY CATEGORY: Contracts
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): Contract and boundary specifications.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): contract documentation

CONTAINS (high-signal items):
- option_a_ingest_contract_v1.md -> Contracts/A/CANONICAL -> ingest contract
- option_b_derived_contract_v1.md -> Contracts/B/CANONICAL -> derived contract
- option_c_outcomes_contract_v1.md -> Contracts/C/CANONICAL -> outcomes contract
- option_d_evidence_contract_v1.md -> Contracts/D/CANONICAL -> evidence contract
- qa_validation_contract_v1.md -> Contracts/QA/CANONICAL -> QA contract
- PATH2_CONTRACT_v1_0.md -> Contracts/Cross/CANONICAL -> path2 contract

CROSS-REFERENCES:
- Option A/B/C/D maps for boundary adherence

FOLDER: docs/doctrine
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Doctrine and immutability policies.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): governance doctrine

CONTAINS (high-signal items):
- OVC_DOCTRINE.md -> QA/QA/CANONICAL -> doctrine
- IMMUTABILITY_NOTICE.md -> QA/QA/CANONICAL -> immutability policy
- GATES.md -> QA/QA/CANONICAL -> gates definition

CROSS-REFERENCES:
- None.

FOLDER: docs/evidence_pack
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Evidence pack specification.

INPUTS (contracts/interfaces): contracts/run_artifact_spec_v0.1.json
OUTPUTS (artifacts/data): evidence pack spec

CONTAINS (high-signal items):
- EVIDENCE_PACK_v0_2.md -> Documentation & Maps/D/SUPPORTING -> evidence pack spec

CROSS-REFERENCES:
- Option D map for evidence pack generation

FOLDER: docs/examples
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Example outputs and overlays.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): example docs

CONTAINS (high-signal items):
- overlay_v0_3_sample_outputs.md -> Documentation & Maps/Cross/SUPPORTING -> overlay example

CROSS-REFERENCES:
- None.

FOLDER: docs/governance
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Governance rules and canonical repo maps.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): governance policy

CONTAINS (high-signal items):
- CANONICAL_REPO_MAP_v0.1.md -> QA/QA/CANONICAL -> canonical repo map
- GOVERNANCE_RULES_v0.1.md -> QA/QA/CANONICAL -> governance rules
- BRANCH_POLICY.md -> QA/QA/CANONICAL -> branch policy

CROSS-REFERENCES:
- None.

FOLDER: docs/history
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Historical and protocol documentation for paths.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): history docs

CONTAINS (high-signal items):
- path1/ -> Documentation & Maps/D/SUPPORTING -> Path1 history docs
- path2/ -> Documentation & Maps/Cross/SUPPORTING -> Path2 history docs

CROSS-REFERENCES:
- Option D map for Path1 execution

FOLDER: docs/history/path2
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Path2 history documentation (roadmap and status notes).

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): Path2 history docs

CONTAINS (high-signal items):
- (no files listed in tree output) -> UNKNOWN -> only folder observed

CROSS-REFERENCES:
- docs/path2 for roadmap documentation

FOLDER: docs/history/path1
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Path1 protocol and evidence documentation.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): Path1 protocol docs

CONTAINS (high-signal items):
- PATH1_EVIDENCE_PROTOCOL_v1_0.md -> Documentation & Maps/D/SUPPORTING -> evidence protocol
- PATH1_SEALING_PROTOCOL_v0_1.md -> Documentation & Maps/D/SUPPORTING -> sealing protocol
- SCORE_INVENTORY_v1.md -> Documentation & Maps/D/SUPPORTING -> score inventory
- scores/ -> Documentation & Maps/D/SUPPORTING -> score docs

CROSS-REFERENCES:
- Option D map for evidence workflows

FOLDER: docs/history/path1/scores
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Score documentation for Path1 evidence.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): score documentation

CONTAINS (high-signal items):
- DIS_v1_1.md -> Documentation & Maps/D/SUPPORTING -> DIS score doc
- LID_v1_0.md -> Documentation & Maps/D/SUPPORTING -> LID score doc
- RES_v1_0.md -> Documentation & Maps/D/SUPPORTING -> RES score doc

CROSS-REFERENCES:
- None.

FOLDER: docs/operations
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Operations procedures and environment notes.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): ops docs

CONTAINS (high-signal items):
- WORKER_PIPELINE.md -> Documentation & Maps/D/SUPPORTING -> worker pipeline
- ovc_current_workflow.md -> Documentation & Maps/D/SUPPORTING -> workflow notes
- secrets_and_env.md -> Documentation & Maps/D/SUPPORTING -> env guidance

CROSS-REFERENCES:
- Option D map for deployment scripts

FOLDER: docs/option_d
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Option D specific specs and registries.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): Option D spec docs

CONTAINS (high-signal items):
- MODEL_REGISTRY_SPEC.md -> Documentation & Maps/D/SUPPORTING -> model registry spec

CROSS-REFERENCES:
- Option D map for model outputs

FOLDER: docs/path1
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Path1 operational docs.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): Path1 reference docs

CONTAINS (high-signal items):
- UPSTREAM_TRAJECTORY_LOOKUP.md -> Documentation & Maps/D/SUPPORTING -> upstream lookup

CROSS-REFERENCES:
- Option D map for trajectory family runs

FOLDER: docs/path2
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Path2 roadmap and plans.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): roadmap docs

CONTAINS (high-signal items):
- ROADMAP_v0_1.md -> Documentation & Maps/Cross/SUPPORTING -> Path2 roadmap

CROSS-REFERENCES:
- None.

FOLDER: docs/pipeline
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): Current state maps and dependency graphs.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): pipeline maps

CONTAINS (high-signal items):
- CURRENT_STATE_A_TO_D.md -> Documentation & Maps/Cross/CANONICAL -> state map
- CURRENT_STATE_DEP_GRAPH.md -> Documentation & Maps/Cross/CANONICAL -> dependency graph
- CURRENT_STATE_INVARIANTS.md -> Documentation & Maps/Cross/CANONICAL -> invariants
- CURRENT_STATE_TRUST_MAP.md -> Documentation & Maps/Cross/CANONICAL -> trust map

CROSS-REFERENCES:
- All option maps for alignment

FOLDER: docs/runbooks
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Runbooks and operator checklists.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): runbooks

CONTAINS (high-signal items):
- option_b_runbook.md -> Documentation & Maps/B/SUPPORTING -> Option B runbook
- option_c_runbook.md -> Documentation & Maps/C/SUPPORTING -> Option C runbook
- path1_evidence_runner_test.md -> Documentation & Maps/D/SUPPORTING -> Path1 runner test

CROSS-REFERENCES:
- Option B/C/D maps for run guidance

FOLDER: docs/specs
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): Option and system specifications.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): spec docs

CONTAINS (high-signal items):
- OPTION_B_* -> Documentation & Maps/B/CANONICAL -> Option B specs
- OPTION_C_* -> Documentation & Maps/C/CANONICAL -> Option C specs
- TRAJECTORY_FAMILIES_v0_1_SPEC.md -> Documentation & Maps/B/CANONICAL -> TF spec
- system/ -> Documentation & Maps/Cross/CANONICAL -> system specs

CROSS-REFERENCES:
- Option B/C maps for spec usage

FOLDER: docs/specs/system
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): System-level specs for outcomes, dashboards, and validation rules.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): system specs

CONTAINS (high-signal items):
- outcomes_system_v0.1.md -> Documentation & Maps/C/CANONICAL -> outcomes system
- outcome_sql_spec_v0.1.md -> Documentation & Maps/C/CANONICAL -> outcome SQL spec
- parsing_validation_rules_v0.1.md -> QA/QA/CANONICAL -> validation rules

CROSS-REFERENCES:
- Option C map for outcome definitions

FOLDER: docs/state_plane
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: B
AUTHORITY: SUPPORTING
ROLE (1 line): State plane documentation.

INPUTS (contracts/interfaces): configs/threshold_packs/state_plane_v0_2_default_v1.json
OUTPUTS (artifacts/data): state plane docs

CONTAINS (high-signal items):
- STATE_PLANE_v0_2.md -> Documentation & Maps/B/SUPPORTING -> state plane spec
- RUN_STATE_PLANE.md -> Documentation & Maps/B/SUPPORTING -> state plane run doc

CROSS-REFERENCES:
- Option B map for derived state plane logic

FOLDER: docs/validation
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: CANONICAL
ROLE (1 line): Validation reports and harness docs.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): validation documentation

CONTAINS (high-signal items):
- C_v0_1_validation.md -> QA/QA/CANONICAL -> validation doc
- WORKFLOW_AUDIT_2026-01-20.md -> QA/QA/CANONICAL -> workflow audit
- VERIFICATION_REPORT_v0.1.md -> QA/QA/CANONICAL -> verification report

CROSS-REFERENCES:
- Option D map for validation outputs

FOLDER: docs/workflows
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Workflow catalog and operating loop docs.

INPUTS (contracts/interfaces): .github/workflows/*
OUTPUTS (artifacts/data): workflow documentation

CONTAINS (high-signal items):
- WORKFLOW_CATALOG_v0_1.md -> Documentation & Maps/Cross/SUPPORTING -> catalog
- WORKFLOW_OPERATING_LOOP_v0_1.md -> Documentation & Maps/Cross/SUPPORTING -> operating loop

CROSS-REFERENCES:
- .github/workflows entries

FOLDER: releases
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Release notes.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): release documentation

CONTAINS (high-signal items):
- ovc-v0.1-spine.md -> Documentation & Maps/Cross/SUPPORTING -> release note

CROSS-REFERENCES:
- None.

FOLDER: research
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Research notebooks and studies.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): study outputs and docs

CONTAINS (high-signal items):
- notebooks/ -> Experiments & Sandbox/Cross/SUPPORTING -> notebook area
- scores/ -> Experiments & Sandbox/Cross/SUPPORTING -> score SQL experiments
- studies/ -> Experiments & Sandbox/Cross/SUPPORTING -> study bundles
- tooling/ -> Experiments & Sandbox/Cross/SUPPORTING -> research tooling

CROSS-REFERENCES:
- Option B/C maps for research usage

FOLDER: research/studies
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Structured research study folders.

INPUTS (contracts/interfaces): research/RESEARCH_GUARDRAILS.md
OUTPUTS (artifacts/data): study manifests and results

CONTAINS (high-signal items):
- study_20260120_* -> Experiments & Sandbox/Cross/SUPPORTING -> dated studies
- TEMPLATE/ -> Experiments & Sandbox/Cross/SUPPORTING -> study template

CROSS-REFERENCES:
- None.

FOLDER: tools
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Validation and repo-map tooling.

INPUTS (contracts/interfaces): contracts/*.json; docs/governance/*
OUTPUTS (artifacts/data): validation outputs, maze generation

CONTAINS (high-signal items):
- validate_contract.py -> QA/QA/SUPPORTING -> contract validator
- validate_contract.ps1 -> QA/QA/SUPPORTING -> contract validator (PS)
- parse_export.py -> QA/QA/SUPPORTING -> export parser
- maze/ -> Documentation & Maps/QA/SUPPORTING -> repo maze generators

CROSS-REFERENCES:
- Option D map for export flows

FOLDER: tools/maze
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Repo maze generation scripts.

INPUTS (contracts/interfaces): Tetsu/OVC_REPO_MAZE/*
OUTPUTS (artifacts/data): maze maps (docs/governance)

CONTAINS (high-signal items):
- gen_repo_maze.py -> Documentation & Maps/QA/SUPPORTING -> maze generator
- gen_repo_maze_curated.py -> Documentation & Maps/QA/SUPPORTING -> curated maze generator

CROSS-REFERENCES:
- Tetsu/OVC_REPO_MAZE

FOLDER: CLAIMS
PRIMARY CATEGORY: Contracts
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Claim bindings and anchor indexes.

INPUTS (contracts/interfaces): docs/governance/decisions.md (policy context)
OUTPUTS (artifacts/data): claim CSVs and bindings

CONTAINS (high-signal items):
- ANCHOR_INDEX_v0_1.csv -> Contracts/QA/SUPPORTING -> anchor index
- CLAIM_BINDING_v0_1.md -> Contracts/QA/SUPPORTING -> claim binding spec

CROSS-REFERENCES:
- Option C map for outcome anchoring

FOLDER: data/verification_private
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Private verification snapshots and command logs.

INPUTS (contracts/interfaces): docs/validation/VERIFICATION_REPORT_v0.1.md
OUTPUTS (artifacts/data): verification outputs and logs

CONTAINS (high-signal items):
- 2026-01-19/ -> Artifacts & Evidence/QA/SUPPORTING -> verification snapshot

CROSS-REFERENCES:
- Option A map for data root

FOLDER: data/verification_private/2026-01-19
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Verification snapshot for 2026-01-19.

INPUTS (contracts/interfaces): docs/validation/VERIFICATION_REPORT_v0.1.md
OUTPUTS (artifacts/data): command logs and captured outputs

CONTAINS (high-signal items):
- commands_run.txt -> Artifacts & Evidence/QA/SUPPORTING -> command log
- outputs/ -> Artifacts & Evidence/QA/SUPPORTING -> captured outputs

CROSS-REFERENCES:
- reports/verification/2026-01-19

FOLDER: data/verification_private/2026-01-19/outputs
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Captured output logs for verification snapshot.

INPUTS (contracts/interfaces): verification commands
OUTPUTS (artifacts/data): *.txt output captures

CONTAINS (high-signal items):
- a0_wrangler_config.txt -> Artifacts & Evidence/QA/SUPPORTING -> wrangler config output
- b2_workflow_files.txt -> Artifacts & Evidence/QA/SUPPORTING -> workflow listing
- l1_neon_schema_verification.txt -> Artifacts & Evidence/QA/SUPPORTING -> schema verification

CROSS-REFERENCES:
- reports/verification/2026-01-19/outputs

FOLDER: reports/validation
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Validation report outputs.

INPUTS (contracts/interfaces): docs/validation/*
OUTPUTS (artifacts/data): validation reports

CONTAINS (high-signal items):
- C1_v0_1_validation.md -> QA/QA/SUPPORTING -> validation report
- C2_v0_1_validation.md -> QA/QA/SUPPORTING -> validation report
- C3_v0_1_validation.md -> QA/QA/SUPPORTING -> validation report

CROSS-REFERENCES:
- Option D map for report storage

FOLDER: reports/verification
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Verification report outputs.

INPUTS (contracts/interfaces): docs/validation/VERIFICATION_REPORT_v0.1.md
OUTPUTS (artifacts/data): verification reports

CONTAINS (high-signal items):
- REPRO_REPORT_* -> QA/QA/SUPPORTING -> repro reports
- 2026-01-19/ -> QA/QA/SUPPORTING -> verification snapshot

CROSS-REFERENCES:
- Option D map for report storage

FOLDER: reports/pipeline_audit
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Pipeline audit outputs.

INPUTS (contracts/interfaces): docs/validation/WORKFLOW_AUDIT_2026-01-20.md
OUTPUTS (artifacts/data): audit outputs

CONTAINS (high-signal items):
- 2026-01-19/ -> QA/QA/SUPPORTING -> audit run

CROSS-REFERENCES:
- Option D map for report storage

FOLDER: Tetsu
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Obsidian vault for repo maze and governance.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): maze docs

CONTAINS (high-signal items):
- OVC_REPO_MAZE/ -> Documentation & Maps/QA/SUPPORTING -> maze docs
- .obsidian/ -> Orchestration/QA/SUPPORTING -> vault config

CROSS-REFERENCES:
- tools/maze

FOLDER: Tetsu/.obsidian
PRIMARY CATEGORY: Orchestration
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Obsidian vault configuration files.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): local editor configuration

CONTAINS (high-signal items):
- app.json -> Orchestration/QA/SUPPORTING -> app settings
- appearance.json -> Orchestration/QA/SUPPORTING -> appearance settings
- core-plugins.json -> Orchestration/QA/SUPPORTING -> plugin list
- graph.json -> Orchestration/QA/SUPPORTING -> graph settings
- workspace.json -> Orchestration/QA/SUPPORTING -> workspace layout

CROSS-REFERENCES:
- None.

FOLDER: Tetsu/OVC_REPO_MAZE
PRIMARY CATEGORY: Documentation & Maps
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Repo maze documentation set.

INPUTS (contracts/interfaces): tools/maze/*
OUTPUTS (artifacts/data): maze maps

CONTAINS (high-signal items):
- 00_REPO_MAZE.md -> Documentation & Maps/QA/SUPPORTING -> maze root
- 01_OPTION_A__INGEST.md -> Documentation & Maps/A/SUPPORTING -> Option A maze
- 02_OPTION_B_DERIVED.md -> Documentation & Maps/B/SUPPORTING -> Option B maze
- 03_OPTION_C_OUTCOMES.md -> Documentation & Maps/C/SUPPORTING -> Option C maze
- 04_OPTION_D_PATHS_BRIDGE.md -> Documentation & Maps/D/SUPPORTING -> Option D maze
- 05_QA_GOVERNANCE.md -> Documentation & Maps/QA/SUPPORTING -> QA maze
- ROOM__WORKFLOWS.md -> Documentation & Maps/QA/SUPPORTING -> workflow room

CROSS-REFERENCES:
- .github/workflows

FOLDER: .git
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: Cross
AUTHORITY: CANONICAL
ROLE (1 line): Git metadata and version control history.

INPUTS (contracts/interfaces): git tooling
OUTPUTS (artifacts/data): git objects and refs

CONTAINS (high-signal items):
- (git metadata) -> QA & Governance/Cross/CANONICAL -> .git internals

CROSS-REFERENCES:
- None.

FOLDER: .vscode
PRIMARY CATEGORY: Orchestration
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Repository editor configuration.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): editor settings

CONTAINS (high-signal items):
- settings.json -> Orchestration/Cross/SUPPORTING -> editor settings

CROSS-REFERENCES:
- infra/ovc-webhook/.vscode

FOLDER: .claude
PRIMARY CATEGORY: Orchestration
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Local assistant configuration.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): settings.local.json

CONTAINS (high-signal items):
- settings.local.json -> Orchestration/Cross/SUPPORTING -> local config

CROSS-REFERENCES:
- None.

FOLDER: .venv
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Local Python virtual environment.

INPUTS (contracts/interfaces): requirements.txt
OUTPUTS (artifacts/data): site-packages and scripts

CONTAINS (high-signal items):
- Lib/ -> Experiments & Sandbox/Cross/EXPERIMENTAL -> packages
- Scripts/ -> Experiments & Sandbox/Cross/EXPERIMENTAL -> venv scripts

CROSS-REFERENCES:
- None.

FOLDER: __pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Top-level Python bytecode cache.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: src/__pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Bytecode cache for src modules.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: src/validate
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Validation routines for derived ranges.

INPUTS (contracts/interfaces): sql/qa_validation_pack*.sql
OUTPUTS (artifacts/data): validation results (via scripts)

CONTAINS (high-signal items):
- validate_derived_range_v0_1.py -> QA/QA/SUPPORTING -> derived validation
- __init__.py -> QA/QA/SUPPORTING -> package init

CROSS-REFERENCES:
- Option D map for validation reports

FOLDER: scripts/__pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Bytecode cache for scripts modules.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: tests/__pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Bytecode cache for tests.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: tools/__pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Bytecode cache for tools.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: trajectory_families/__pycache__
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Bytecode cache for trajectory families.

INPUTS (contracts/interfaces): Python runtime
OUTPUTS (artifacts/data): *.pyc

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> bytecode

CROSS-REFERENCES:
- None.

FOLDER: .pytest_cache
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Pytest cache (generated).

INPUTS (contracts/interfaces): tests/*
OUTPUTS (artifacts/data): pytest cache

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> cache data

CROSS-REFERENCES:
- None.

FOLDER: .pytest-tmp
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Temporary pytest artifacts.

INPUTS (contracts/interfaces): tests/*
OUTPUTS (artifacts/data): temp test files

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> temp files

CROSS-REFERENCES:
- None.

FOLDER: .pytest-tmp2
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Temporary pytest artifacts (second temp dir).

INPUTS (contracts/interfaces): tests/*
OUTPUTS (artifacts/data): temp test files

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> temp files

CROSS-REFERENCES:
- None.

FOLDER: chmod_test
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: UNKNOWN
ROLE (1 line): Empty or placeholder folder (purpose unclear).

INPUTS (contracts/interfaces): UNKNOWN
OUTPUTS (artifacts/data): UNKNOWN

CONTAINS (high-signal items):
- (empty) -> UNKNOWN -> no files observed

CROSS-REFERENCES:
- None.

FOLDER: testdir
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: UNKNOWN
ROLE (1 line): Empty or placeholder folder (purpose unclear).

INPUTS (contracts/interfaces): UNKNOWN
OUTPUTS (artifacts/data): UNKNOWN

CONTAINS (high-signal items):
- (empty) -> UNKNOWN -> no files observed

CROSS-REFERENCES:
- None.

FOLDER: testdir2
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: UNKNOWN
ROLE (1 line): Empty or placeholder folder (purpose unclear).

INPUTS (contracts/interfaces): UNKNOWN
OUTPUTS (artifacts/data): UNKNOWN

CONTAINS (high-signal items):
- (empty) -> UNKNOWN -> no files observed

CROSS-REFERENCES:
- None.

FOLDER: specs
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: UNKNOWN
ROLE (1 line): Empty or placeholder specs folder (no files observed).

INPUTS (contracts/interfaces): UNKNOWN
OUTPUTS (artifacts/data): UNKNOWN

CONTAINS (high-signal items):
- (empty) -> UNKNOWN -> no files observed

CROSS-REFERENCES:
- None.

## Cross-Cutting References
- Option maps A/B/C/D contain operational code and artifacts referenced by these governance and QA documents.

## Unresolved / Needs Decision
- Clarify intent for chmod_test, testdir, testdir2, and specs (empty folders).
- Decide whether .venv, __pycache__, and pytest temp dirs should be excluded from future canonical maps.
