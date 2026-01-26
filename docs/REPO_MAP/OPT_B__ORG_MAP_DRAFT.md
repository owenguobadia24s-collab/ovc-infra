# Option B Organization Map (Draft)
## Purpose
Map derived-feature computation, registries, and supporting SQL for Option B.

## Option Scope (brief)
L1/L2/L3 computations, tagging, feature engineering, and feature/threshold registries.

## Category Index (list folders by category)
- Registries: configs, configs/threshold_packs, src/config
- Pipelines: src/derived
- Models: trajectory_families
- Data Stores & Interfaces: sql, sql/derived, sql/path1, sql/path1/evidence, sql/path1/scores, sql/path1/studies, sql/path1/db_patches, sql/path1/evidence/runs, sql/path1/evidence/studies

## Folder-by-Folder Map
FOLDER: configs
PRIMARY CATEGORY: Registries
OPTION OWNER: B
AUTHORITY: SUPPORTING
ROLE (1 line): Configuration root for derived feature/threshold packs.

INPUTS (contracts/interfaces): docs/specs/OPTION_B_C*_FEATURES_v0.1.md (feature definitions)
OUTPUTS (artifacts/data): JSON configuration packs used by pipelines

CONTAINS (high-signal items):
- threshold_packs/ -> Registries/B/SUPPORTING -> threshold pack JSONs

CROSS-REFERENCES:
- None.

FOLDER: configs/threshold_packs
PRIMARY CATEGORY: Registries
OPTION OWNER: B
AUTHORITY: SUPPORTING
ROLE (1 line): Versioned threshold packs for L3/state plane logic.

INPUTS (contracts/interfaces): docs/specs/system/Quadrant State Plane v0.2.md
OUTPUTS (artifacts/data): threshold pack JSONs consumed by compute pipelines

CONTAINS (high-signal items):
- l3_example_pack_v1.json -> Registries/B/SUPPORTING -> example pack
- l3_regime_trend_v1.json -> Registries/B/SUPPORTING -> regime trend thresholds
- state_plane_v0_2_default_v1.json -> Registries/B/SUPPORTING -> state plane defaults

CROSS-REFERENCES:
- None.

FOLDER: src/config
PRIMARY CATEGORY: Registries
OPTION OWNER: B
AUTHORITY: SUPPORTING
ROLE (1 line): Threshold registry helpers and CLI tooling.

INPUTS (contracts/interfaces): configs/threshold_packs/*.json
OUTPUTS (artifacts/data): registry outputs and validation logs (runtime)

CONTAINS (high-signal items):
- threshold_registry_v0_1.py -> Registries/B/SUPPORTING -> registry implementation
- threshold_registry_cli.py -> Orchestration/B/SUPPORTING -> CLI wrapper

CROSS-REFERENCES:
- QA map for tests/test_threshold_registry.py

FOLDER: src/derived
PRIMARY CATEGORY: Pipelines
OPTION OWNER: B
AUTHORITY: CANONICAL
ROLE (1 line): Derived feature computation pipelines (L1/L2/L3).

INPUTS (contracts/interfaces): contracts/derived_feature_set_v0.1.json; sql/02_derived_c1_c2_tables_v0_1.sql
OUTPUTS (artifacts/data): derived feature tables/views

CONTAINS (high-signal items):
- compute_l1_v0_1.py -> Pipelines/B/CANONICAL -> L1 feature computation
- compute_l2_v0_1.py -> Pipelines/B/CANONICAL -> L2 feature computation
- compute_l3_regime_trend_v0_1.py -> Pipelines/B/CANONICAL -> L3 regime trend
- compute_l3_stub_v0_1.py -> Pipelines/B/EXPERIMENTAL -> L3 stub

CROSS-REFERENCES:
- QA map for tests/test_derived_features.py and validation harnesses

FOLDER: trajectory_families
PRIMARY CATEGORY: Models
OPTION OWNER: B
AUTHORITY: CANONICAL
ROLE (1 line): Trajectory family fingerprints and clustering utilities.

INPUTS (contracts/interfaces): docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md
OUTPUTS (artifacts/data): fingerprints and gallery outputs (via scripts)

CONTAINS (high-signal items):
- fingerprint.py -> Models/B/CANONICAL -> fingerprint computation
- clustering.py -> Models/B/SUPPORTING -> clustering utilities
- features.py -> Models/B/SUPPORTING -> feature extraction
- params_v0_1.json -> Models/B/CANONICAL -> parameter set

CROSS-REFERENCES:
- Option D map for reports/path1/trajectory_families outputs

FOLDER: sql
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: B
AUTHORITY: CANONICAL
ROLE (1 line): Core schema and derived-feature SQL definitions.

INPUTS (contracts/interfaces): docs/specs/system/*; docs/specs/OPTION_B_*; docs/contracts/derived_layer_boundary.md
OUTPUTS (artifacts/data): database schema, derived tables, QA validation packs

CONTAINS (high-signal items):
- 02_derived_c1_c2_tables_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> L1/L2 tables
- 04_threshold_registry_v0_1.sql -> Registries/B/CANONICAL -> threshold registry tables
- 05_c3_regime_trend_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> L3 trend logic
- 06_state_plane_threshold_pack_v0_2.sql -> Data Stores & Interfaces/B/CANONICAL -> state plane pack
- derived_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> derived schema rollup
- qa_validation_pack*.sql -> QA/QA/SUPPORTING -> QA validation SQL
- option_c_*.sql -> Outcomes/C/SUPPORTING -> Option C-specific outputs
- path1/ -> Pipelines/D/SUPPORTING -> Path1 evidence SQL

CROSS-REFERENCES:
- Option C map for option_c_*.sql usage
- Option D map for sql/path1 subtree
- QA map for qa_validation_pack*.sql

FOLDER: sql/derived
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: B
AUTHORITY: CANONICAL
ROLE (1 line): Derived feature views and state plane views.

INPUTS (contracts/interfaces): sql/02_derived_c1_c2_tables_v0_1.sql
OUTPUTS (artifacts/data): derived view definitions

CONTAINS (high-signal items):
- v_ovc_l1_features_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> L1 view
- v_ovc_l2_features_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> L2 view
- v_ovc_l3_features_v0_1.sql -> Data Stores & Interfaces/B/CANONICAL -> L3 view
- v_ovc_state_plane_v0_2.sql -> Data Stores & Interfaces/B/CANONICAL -> state plane view

CROSS-REFERENCES:
- None.

FOLDER: sql/path1
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Path1 evidence SQL assets (scores, studies, patches).

INPUTS (contracts/interfaces): docs/history/path1/*; docs/evidence_pack/EVIDENCE_PACK_v0_2.md
OUTPUTS (artifacts/data): Path1 evidence views and study outputs

CONTAINS (high-signal items):
- evidence/ -> Data Stores & Interfaces/D/SUPPORTING -> evidence view SQL
- scores/ -> Data Stores & Interfaces/D/SUPPORTING -> score SQL
- studies/ -> Experiments & Sandbox/D/SUPPORTING -> study SQL
- db_patches/ -> Orchestration/D/SUPPORTING -> patch SQL

CROSS-REFERENCES:
- Option D map for sql/path1 subfolders

FOLDER: sql/path1/evidence
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Evidence view SQL definitions for Path1.

INPUTS (contracts/interfaces): docs/history/path1/README.md; docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md
OUTPUTS (artifacts/data): v_path1_evidence_* views

CONTAINS (high-signal items):
- v_path1_evidence_dis_v1_1.sql -> Data Stores & Interfaces/D/SUPPORTING -> DIS evidence view
- v_path1_evidence_lid_v1_0.sql -> Data Stores & Interfaces/D/SUPPORTING -> LID evidence view
- v_path1_evidence_res_v1_0.sql -> Data Stores & Interfaces/D/SUPPORTING -> RES evidence view
- runs/ -> Artifacts & Evidence/D/SUPPORTING -> run-specific SQL snapshots
- studies/ -> Experiments & Sandbox/D/SUPPORTING -> evidence study SQL

CROSS-REFERENCES:
- Option D map for reports/path1/evidence outputs

FOLDER: sql/path1/scores
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Score SQL definitions for Path1 evidence.

INPUTS (contracts/interfaces): docs/history/path1/SCORE_INVENTORY_v1.md
OUTPUTS (artifacts/data): score SQL definitions

CONTAINS (high-signal items):
- score_dis_v1_1.sql -> Data Stores & Interfaces/D/SUPPORTING -> DIS score
- score_lid_v1_0.sql -> Data Stores & Interfaces/D/SUPPORTING -> LID score
- score_res_v1_0.sql -> Data Stores & Interfaces/D/SUPPORTING -> RES score

CROSS-REFERENCES:
- Option D map for reports/path1/scores

FOLDER: sql/path1/studies
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Study SQL for Path1 score stability and outcome comparisons.

INPUTS (contracts/interfaces): docs/history/path1/research_views_option_c_v0.1.md
OUTPUTS (artifacts/data): study SQL outputs (research queries)

CONTAINS (high-signal items):
- dis_vs_outcomes_bucketed.sql -> Experiments & Sandbox/D/SUPPORTING -> DIS vs outcomes
- lid_vs_outcomes_bucketed.sql -> Experiments & Sandbox/D/SUPPORTING -> LID vs outcomes
- res_vs_outcomes_bucketed.sql -> Experiments & Sandbox/D/SUPPORTING -> RES vs outcomes

CROSS-REFERENCES:
- Option C map for outcome interpretation

FOLDER: sql/path1/db_patches
PRIMARY CATEGORY: Orchestration
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Patch SQL applied to align or extend Path1 schema.

INPUTS (contracts/interfaces): schema/required_objects.txt
OUTPUTS (artifacts/data): patched database objects

CONTAINS (high-signal items):
- patch_align_c1_tf_column_20260120.sql -> Orchestration/D/SUPPORTING -> alignment patch
- patch_create_evidence_views_20260120.sql -> Orchestration/D/SUPPORTING -> evidence views
- patch_create_score_views_20260120.sql -> Orchestration/D/SUPPORTING -> score views
- patch_m15_raw_20260122.sql -> Orchestration/D/SUPPORTING -> m15 raw patch

CROSS-REFERENCES:
- Option D map for Path1 evidence runs

FOLDER: sql/path1/evidence/runs
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Run-specific evidence SQL snapshots.

INPUTS (contracts/interfaces): Path1 run ids and evidence protocol
OUTPUTS (artifacts/data): per-run SQL state

CONTAINS (high-signal items):
- p1_20260120_* -> Artifacts & Evidence/D/SUPPORTING -> run snapshots
- p1_20260121_* -> Artifacts & Evidence/D/SUPPORTING -> run snapshots
- p1_20260122_* -> Artifacts & Evidence/D/SUPPORTING -> run snapshots

CROSS-REFERENCES:
- Option D map for reports/path1/evidence/runs

FOLDER: sql/path1/evidence/studies
PRIMARY CATEGORY: Experiments & Sandbox
OPTION OWNER: D
AUTHORITY: SUPPORTING
ROLE (1 line): Evidence study SQL for distribution analysis.

INPUTS (contracts/interfaces): docs/history/path1/research_views_option_c_v0.1.md
OUTPUTS (artifacts/data): study queries for evidence distributions

CONTAINS (high-signal items):
- study_dis_v1_1_distribution.sql -> Experiments & Sandbox/D/SUPPORTING -> DIS distribution
- study_lid_v1_0_distribution.sql -> Experiments & Sandbox/D/SUPPORTING -> LID distribution
- study_res_v1_0_distribution.sql -> Experiments & Sandbox/D/SUPPORTING -> RES distribution

CROSS-REFERENCES:
- Option D map for evidence reporting

## Cross-Cutting References
- contracts/derived_feature_set_v0.1.json is the canonical contract for derived features (folder owned by QA map).
- docs/specs/OPTION_B_* provide option-level intent; stored under docs (QA map).

## Unresolved / Needs Decision
- Confirm whether sql/path1 should remain under Option B map (currently cross-referenced to Option D) or be moved to Option D-only mapping.
