# Option D Organization Map (Draft)
## Purpose
Map Path1/bridge workflows, report generation, and integration subsystems.

## Option Scope (brief)
Daily runners, report builders, packaging, user-facing outputs, and integrations.

## Category Index (list folders by category)
- Orchestration: scripts, scripts/path1, scripts/path1_replay, scripts/path1_seal, scripts/export, scripts/deploy, scripts/dev, scripts/local, scripts/reports, src/ovc_ops
- Artifacts & Evidence: artifacts, artifacts/derived_validation, reports, reports/path1, reports/path1/evidence, reports/path1/evidence/runs, reports/path1/scores, reports/path1/trajectory_families, reports/path1/trajectory_families/v0.1, reports/path1/trajectory_families/v0.1/fingerprints, reports/runs, reports/validation, reports/verification, reports/pipeline_audit
- Sub-systems: infra, infra/ovc-webhook, infra/ovc-webhook/src, infra/ovc-webhook/sql, infra/ovc-webhook/test, infra/ovc-webhook/node_modules, infra/ovc-webhook/.wrangler, infra/ovc-webhook/.vscode, infra/ovc-webhook/.pytest_cache
- Models: pine

## Folder-by-Folder Map
FOLDER: scripts
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Top-level scripts for running Path1 workflows and integrations.

INPUTS (contracts/interfaces): docs/operations/WORKER_PIPELINE.md; docs/runbooks/*
OUTPUTS (artifacts/data): run reports, evidence packs, exports

CONTAINS (high-signal items):
- path1/ -> Orchestration/D/CANONICAL -> Path1 evidence workflows
- path1_replay/ -> QA/D/SUPPORTING -> replay verification tools
- path1_seal/ -> Orchestration/D/SUPPORTING -> sealing manifest tooling
- export/ -> Orchestration/D/SUPPORTING -> exports and Notion sync
- deploy/ -> Orchestration/D/SUPPORTING -> worker deployment
- dev/ -> Orchestration/Cross/EXPERIMENTAL -> dev utilities
- local/ -> Orchestration/Cross/SUPPORTING -> local verification scripts
- run/ -> Orchestration/C/SUPPORTING -> Option C runners
- ci/ -> QA/QA/SUPPORTING -> CI helpers
- validate/ -> QA/QA/SUPPORTING -> validation entrypoints

CROSS-REFERENCES:
- Option C map for scripts/run
- QA map for scripts/ci and scripts/validate

FOLDER: scripts/path1
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: CANONICAL
ROLE (1 line): Primary Path1 evidence run orchestration and pack building.

INPUTS (contracts/interfaces): docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md; contracts/run_artifact_spec_v0.1.json
OUTPUTS (artifacts/data): evidence packs, run queues, state plane outputs

CONTAINS (high-signal items):
- build_evidence_pack_v0_2.py -> Orchestration/D/CANONICAL -> evidence pack builder
- run_evidence_queue.py -> Orchestration/D/CANONICAL -> queue runner
- run_evidence_range.py -> Orchestration/D/CANONICAL -> range runner
- run_state_plane.py -> Orchestration/D/SUPPORTING -> state plane runner
- run_trajectory_families.py -> Orchestration/D/SUPPORTING -> TF runner
- overlays_v0_3.py -> Orchestration/D/SUPPORTING -> overlays logic
- generate_queue_resolved.py -> Orchestration/D/SUPPORTING -> queue resolver
- validate_post_run.py -> QA/D/SUPPORTING -> post-run validation

CROSS-REFERENCES:
- Option B map for trajectory_families (modeling)
- QA map for validation expectations

FOLDER: scripts/path1_replay
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Replay verification tooling for Path1 evidence runs.

INPUTS (contracts/interfaces): docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md
OUTPUTS (artifacts/data): replay verification reports

CONTAINS (high-signal items):
- run_replay_verification.py -> QA/D/SUPPORTING -> replay verification runner
- lib.py -> Sub-systems/D/SUPPORTING -> shared helpers
- README.md -> Documentation & Maps/D/SUPPORTING -> usage notes

CROSS-REFERENCES:
- QA map for tests/test_path1_replay_structural.py

FOLDER: scripts/path1_seal
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Seal manifest generation for Path1 runs.

INPUTS (contracts/interfaces): docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md
OUTPUTS (artifacts/data): seal manifests (via reports/)

CONTAINS (high-signal items):
- run_seal_manifests.py -> Orchestration/D/SUPPORTING -> seal manifest runner
- lib.py -> Sub-systems/D/SUPPORTING -> shared helpers

CROSS-REFERENCES:
- QA map for seal validation expectations

FOLDER: scripts/export
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Export and integration scripts.

INPUTS (contracts/interfaces): contracts/export_contract_v0.1*.json
OUTPUTS (artifacts/data): exported files, Notion sync updates

CONTAINS (high-signal items):
- notion_sync.py -> Orchestration/D/SUPPORTING -> Notion loader
- oanda_export_2h_day.py -> Orchestration/D/SUPPORTING -> Oanda export

CROSS-REFERENCES:
- QA map for tools/validate_contract.py

FOLDER: scripts/deploy
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Deployment tooling for worker environments.

INPUTS (contracts/interfaces): docs/operations/NEON_STAGING.md
OUTPUTS (artifacts/data): deployed worker instances

CONTAINS (high-signal items):
- deploy_worker.ps1 -> Orchestration/D/SUPPORTING -> deploy script

CROSS-REFERENCES:
- None.

FOLDER: scripts/dev
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: Cross
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Developer utilities and one-off checks.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): ad-hoc outputs

CONTAINS (high-signal items):
- check_dst_mapping.py -> Experiments & Sandbox/Cross/EXPERIMENTAL -> DST audit helper

CROSS-REFERENCES:
- QA map for tests/test_dst_audit.py

FOLDER: scripts/local
PRIMARY CATEGORY: Orchestration
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Local verification entrypoints.

INPUTS (contracts/interfaces): docs/runbooks/*
OUTPUTS (artifacts/data): local verification logs

CONTAINS (high-signal items):
- verify_local.ps1 -> Orchestration/Cross/SUPPORTING -> local verification

CROSS-REFERENCES:
- QA map for validation guidance

FOLDER: scripts/reports
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: UNKNOWN
ROLE (1 line): Placeholder for report scripts (empty in repo).

INPUTS (contracts/interfaces): UNKNOWN
OUTPUTS (artifacts/data): UNKNOWN

CONTAINS (high-signal items):
- (empty) -> UNKNOWN -> no files observed

CROSS-REFERENCES:
- None.

FOLDER: src/ovc_ops
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Run artifact helpers and CLI for ops flows.

INPUTS (contracts/interfaces): contracts/run_artifact_spec_v0.1.json
OUTPUTS (artifacts/data): run artifact entries (via scripts)

CONTAINS (high-signal items):
- run_artifact.py -> Orchestration/D/SUPPORTING -> run artifact builder
- run_artifact_cli.py -> Orchestration/D/SUPPORTING -> CLI wrapper

CROSS-REFERENCES:
- Option C map for runners that emit run artifacts

FOLDER: artifacts
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Generated artifacts from validation and Option C sanity runs.

INPUTS (contracts/interfaces): scripts/path1/*; scripts/run/*; tests/*
OUTPUTS (artifacts/data): JSON artifacts, spotchecks, validation summaries

CONTAINS (high-signal items):
- derived_validation/ -> QA & Governance/QA/SUPPORTING -> derived validation artifacts
- option_c/ -> Artifacts & Evidence/C/SUPPORTING -> Option C artifacts
- path1_replay_report.json -> QA/D/SUPPORTING -> replay report output

CROSS-REFERENCES:
- Option C map for artifacts/option_c
- QA map for artifacts/derived_validation

FOLDER: artifacts/derived_validation
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Derived validation run outputs and metadata.

INPUTS (contracts/interfaces): sql/qa_validation_pack*.sql
OUTPUTS (artifacts/data): derived_validation_*.jsonl, meta.json

CONTAINS (high-signal items):
- LATEST.txt -> QA/QA/SUPPORTING -> pointer to latest run
- <run_id>/ -> QA/QA/SUPPORTING -> per-run outputs

CROSS-REFERENCES:
- QA map for validation reporting

FOLDER: reports
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Report outputs and run logs across Path1 and Option C.

INPUTS (contracts/interfaces): contracts/run_artifact_spec_v0.1.json; docs/runbooks/*
OUTPUTS (artifacts/data): run reports, spotchecks, validation reports

CONTAINS (high-signal items):
- path1/ -> Artifacts & Evidence/D/SUPPORTING -> Path1 evidence reports
- runs/ -> Artifacts & Evidence/D/SUPPORTING -> run logs/checks
- validation/ -> QA & Governance/QA/SUPPORTING -> validation reports
- verification/ -> QA & Governance/QA/SUPPORTING -> verification reports
- pipeline_audit/ -> QA & Governance/QA/SUPPORTING -> audit snapshots
- run_report_* -> Artifacts & Evidence/C/SUPPORTING -> Option C run reports
- spotchecks_* -> Artifacts & Evidence/C/SUPPORTING -> Option C spotchecks

CROSS-REFERENCES:
- Option C map for report outputs
- QA map for validation/verification/pipeline_audit

FOLDER: reports/path1
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Path1 evidence reporting area.

INPUTS (contracts/interfaces): docs/history/path1/*
OUTPUTS (artifacts/data): evidence run reports and score summaries

CONTAINS (high-signal items):
- evidence/ -> Artifacts & Evidence/D/SUPPORTING -> evidence runs and queues
- scores/ -> Artifacts & Evidence/D/SUPPORTING -> score summaries
- trajectory_families/ -> Artifacts & Evidence/D/SUPPORTING -> TF outputs

CROSS-REFERENCES:
- Option B map for trajectory_families models

FOLDER: reports/path1/evidence
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Evidence run reports and queue files.

INPUTS (contracts/interfaces): docs/history/path1/EVIDENCE_RUNS_HOWTO.md
OUTPUTS (artifacts/data): run reports, queue CSVs

CONTAINS (high-signal items):
- runs/ -> Artifacts & Evidence/D/SUPPORTING -> per-run folders
- RUN_QUEUE.csv -> Artifacts & Evidence/D/SUPPORTING -> pending queue
- RUN_QUEUE_RESOLVED.csv -> Artifacts & Evidence/D/SUPPORTING -> resolved queue
- INDEX.md -> Documentation & Maps/D/SUPPORTING -> index of runs

CROSS-REFERENCES:
- Option B map for sql/path1/evidence/runs

FOLDER: reports/path1/evidence/runs
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Evidence run report folders.

INPUTS (contracts/interfaces): Path1 run queue
OUTPUTS (artifacts/data): per-run evidence packs and summaries

CONTAINS (high-signal items):
- p1_20260120_* -> Artifacts & Evidence/D/SUPPORTING -> run folders
- p1_20260121_* -> Artifacts & Evidence/D/SUPPORTING -> run folders
- p1_20260122_* -> Artifacts & Evidence/D/SUPPORTING -> run folders
- .gitkeep -> Artifacts & Evidence/D/SUPPORTING -> placeholder

CROSS-REFERENCES:
- Option B map for sql/path1/evidence/runs

FOLDER: reports/path1/scores
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Score report outputs for Path1.

INPUTS (contracts/interfaces): docs/history/path1/SCORE_INVENTORY_v1.md
OUTPUTS (artifacts/data): score summary markdown

CONTAINS (high-signal items):
- DIS_v1_1.md -> Artifacts & Evidence/D/SUPPORTING -> DIS score report
- LID_v1_0.md -> Artifacts & Evidence/D/SUPPORTING -> LID score report
- RES_v1_0.md -> Artifacts & Evidence/D/SUPPORTING -> RES score report

CROSS-REFERENCES:
- None.

FOLDER: reports/path1/trajectory_families
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Trajectory family report outputs.

INPUTS (contracts/interfaces): docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md
OUTPUTS (artifacts/data): fingerprint outputs and CSVs

CONTAINS (high-signal items):
- v0.1/ -> Artifacts & Evidence/D/SUPPORTING -> versioned outputs

CROSS-REFERENCES:
- Option B map for trajectory_families source code

FOLDER: reports/path1/trajectory_families/v0.1
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Versioned trajectory family outputs.

INPUTS (contracts/interfaces): trajectory_families/params_v0_1.json
OUTPUTS (artifacts/data): fingerprint CSVs

CONTAINS (high-signal items):
- fingerprints/ -> Artifacts & Evidence/D/SUPPORTING -> fingerprint outputs

CROSS-REFERENCES:
- None.

FOLDER: reports/path1/trajectory_families/v0.1/fingerprints
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Fingerprint CSV outputs per symbol.

INPUTS (contracts/interfaces): trajectory_families/fingerprint.py
OUTPUTS (artifacts/data): index.csv, per-symbol CSVs

CONTAINS (high-signal items):
- index.csv -> Artifacts & Evidence/D/SUPPORTING -> fingerprint index
- GBPUSD/ -> Artifacts & Evidence/D/SUPPORTING -> per-symbol folder

CROSS-REFERENCES:
- None.

FOLDER: reports/runs
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Run logs and checks for pipeline executions.

INPUTS (contracts/interfaces): docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md
OUTPUTS (artifacts/data): run.json, run.log, checks.json

CONTAINS (high-signal items):
- 20260120T*_P2-Backfill_* -> Artifacts & Evidence/D/SUPPORTING -> backfill runs
- 20260120T*_D-ValidationHarness_* -> Artifacts & Evidence/D/SUPPORTING -> validation harness runs
- 20260122T*_P2-Backfill-M15_* -> Artifacts & Evidence/D/SUPPORTING -> backfill m15 runs

CROSS-REFERENCES:
- QA map for validation summary expectations

FOLDER: reports/validation
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Validation reports for L1/L2/L3 and promotion decisions.

INPUTS (contracts/interfaces): docs/validation/C_v0_1_validation.md
OUTPUTS (artifacts/data): validation reports and summary CSV/JSON

CONTAINS (high-signal items):
- C1_v0_1_validation.md -> QA/QA/SUPPORTING -> L1 validation
- C2_v0_1_validation.md -> QA/QA/SUPPORTING -> L2 validation
- C3_v0_1_validation.md -> QA/QA/SUPPORTING -> L3 validation
- validate_range_* -> QA/QA/SUPPORTING -> range validation outputs

CROSS-REFERENCES:
- QA map for validation governance

FOLDER: reports/verification
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Verification report outputs and evidence anchors.

INPUTS (contracts/interfaces): docs/validation/VERIFICATION_REPORT_v0.1.md
OUTPUTS (artifacts/data): verification reports and command logs

CONTAINS (high-signal items):
- 2026-01-19/ -> QA/QA/SUPPORTING -> verification snapshot
- EVIDENCE_ANCHOR_v0_1.md -> QA/QA/SUPPORTING -> anchor report
- REPRO_REPORT_* -> QA/QA/SUPPORTING -> reproducibility reports

CROSS-REFERENCES:
- QA map for verification governance

FOLDER: reports/pipeline_audit
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Pipeline audit snapshots.

INPUTS (contracts/interfaces): docs/validation/WORKFLOW_AUDIT_2026-01-20.md
OUTPUTS (artifacts/data): audit results

CONTAINS (high-signal items):
- 2026-01-19/ -> QA/QA/SUPPORTING -> audit run

CROSS-REFERENCES:
- QA map for governance context

FOLDER: infra
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Infrastructure and integration subprojects.

INPUTS (contracts/interfaces): docs/operations/*
OUTPUTS (artifacts/data): deployed webhook/service artifacts

CONTAINS (high-signal items):
- ovc-webhook/ -> Sub-systems/D/SUPPORTING -> Cloudflare worker integration

CROSS-REFERENCES:
- None.

FOLDER: infra/ovc-webhook
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Cloudflare worker for webhook and ingestion integration.

INPUTS (contracts/interfaces): infra/ovc-webhook/wrangler.jsonc; sqlschema_v01.sql
OUTPUTS (artifacts/data): deployed worker bundles

CONTAINS (high-signal items):
- src/ -> Sub-systems/D/SUPPORTING -> worker source code
- sql/ -> Data Stores & Interfaces/D/SUPPORTING -> SQL schema
- test/ -> QA/D/SUPPORTING -> unit tests
- node_modules/ -> Sub-systems/D/EXPERIMENTAL -> third-party deps
- .wrangler/ -> Orchestration/D/EXPERIMENTAL -> local wrangler state
- .vscode/ -> Orchestration/Cross/SUPPORTING -> editor config
- .pytest_cache/ -> Artifacts & Evidence/QA/EXPERIMENTAL -> test cache

CROSS-REFERENCES:
- QA map for test expectations

FOLDER: infra/ovc-webhook/src
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Worker source implementation.

INPUTS (contracts/interfaces): worker-configuration.d.ts; wrangler.jsonc
OUTPUTS (artifacts/data): compiled worker bundle (via build)

CONTAINS (high-signal items):
- index.ts -> Sub-systems/D/SUPPORTING -> worker entrypoint

CROSS-REFERENCES:
- None.

FOLDER: infra/ovc-webhook/sql
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Worker-side SQL schema assets.

INPUTS (contracts/interfaces): sqlschema_v01.sql
OUTPUTS (artifacts/data): database schema scripts

CONTAINS (high-signal items):
- 20250215_create_ovc_blocks_detail_v01.sql -> Data Stores & Interfaces/D/SUPPORTING -> schema patch

CROSS-REFERENCES:
- None.

FOLDER: infra/ovc-webhook/test
PRIMARY CATEGORY: QA & Governance
OPTION OWNER: QA
AUTHORITY: SUPPORTING
ROLE (1 line): Worker unit tests and test config.

INPUTS (contracts/interfaces): vitest.config.mts
OUTPUTS (artifacts/data): test reports (local)

CONTAINS (high-signal items):
- index.spec.ts -> QA/QA/SUPPORTING -> worker tests
- env.d.ts -> QA/QA/SUPPORTING -> test types

CROSS-REFERENCES:
- QA map for overall test policy

FOLDER: infra/ovc-webhook/node_modules
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: D
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Vendored Node dependencies for the webhook project.

INPUTS (contracts/interfaces): package.json
OUTPUTS (artifacts/data): third-party libraries

CONTAINS (high-signal items):
- @cloudflare/* -> Sub-systems/D/EXPERIMENTAL -> worker runtime deps
- wrangler/* -> Sub-systems/D/EXPERIMENTAL -> deployment tooling

CROSS-REFERENCES:
- None.

FOLDER: infra/ovc-webhook/.wrangler
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Local Wrangler state and temporary build outputs.

INPUTS (contracts/interfaces): wrangler.jsonc
OUTPUTS (artifacts/data): cached build state

CONTAINS (high-signal items):
- state/ -> Orchestration/D/EXPERIMENTAL -> local state
- tmp/ -> Orchestration/D/EXPERIMENTAL -> temp bundles

CROSS-REFERENCES:
- None.

FOLDER: infra/ovc-webhook/.vscode
PRIMARY CATEGORY: Orchestration
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Editor configuration for webhook subproject.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): developer settings

CONTAINS (high-signal items):
- settings.json -> Orchestration/Cross/SUPPORTING -> editor settings

CROSS-REFERENCES:
- QA map for repo-level editor settings

FOLDER: infra/ovc-webhook/.pytest_cache
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: QA
AUTHORITY: EXPERIMENTAL
ROLE (1 line): Pytest cache (generated).

INPUTS (contracts/interfaces): tests
OUTPUTS (artifacts/data): pytest cache files

CONTAINS (high-signal items):
- (generated) -> Artifacts & Evidence/QA/EXPERIMENTAL -> cache data

CROSS-REFERENCES:
- QA map for generated artifacts

FOLDER: pine
PRIMARY CATEGORY: Models
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Pine scripts for charting and user-facing overlays.

INPUTS (contracts/interfaces): docs/architecture/ovc_metric_architecture.md
OUTPUTS (artifacts/data): Pine scripts for TradingView

CONTAINS (high-signal items):
- OVC_v0_1.pine -> Models/D/SUPPORTING -> primary Pine script
- export_module_v0.1.pine -> Models/D/SUPPORTING -> export module
- ovc_panelsv0.1 -> Models/D/SUPPORTING -> panel config

CROSS-REFERENCES:
- Option B map for derived feature definitions

## Cross-Cutting References
- .github/workflows includes Path1 and evidence workflows (QA map).
- contracts/* define run artifacts and export contracts (QA map).

## Unresolved / Needs Decision
- Confirm whether scripts/dev and scripts/local should be reclassified under QA-only tooling or remain under Option D.
