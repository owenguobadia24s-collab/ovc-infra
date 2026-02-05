# Phase 2.2.1 Validation Report

validation_run_utc: 2026-02-05T02:05:53Z
validators:
- docs/phase_2_2/validators/validate_registry_seals_v0_1.py
- docs/phase_2_2/validators/validate_registry_schema_v0_1.py
- docs/phase_2_2/validators/validate_active_pointers_v0_1.py

seal_validation:
- run_registry: PASS (run_id=2026-02-05__000138__run_registry_build)
- op_status_table: PASS (run_id=2026-02-05__000144__op_status_table_build)
- drift_signals: PASS (run_id=2026-02-05__001255__drift_signals_build)
- migration_ledger: PASS (run_id=2026-02-05__015605__seal_migration_ledger)
- expected_versions: PASS (run_id=2026-02-05__015605__seal_expected_versions)
- threshold_packs_file: PASS (run_id=2026-02-05__015605__seal_threshold_packs)
- fingerprint_index: PASS (run_id=2026-02-05__015605__seal_fingerprint_index)
- derived_validation_reports: PASS (run_id=2026-02-05__015605__seal_derived_validation)

schema_validation:
- run_registry: PASS (RUN_REGISTRY_v0_1.jsonl)
- op_status_table: FAIL (OPERATION_STATUS_TABLE_v0_1.json top-level is array; schema expects object)
- drift_signals: PASS (DRIFT_SIGNALS_v0_1.json)
- migration_ledger: NOT_APPLICABLE (schema validator supports 3 registry types only)
- expected_versions: NOT_APPLICABLE (schema validator supports 3 registry types only)
- threshold_packs_file: NOT_APPLICABLE (schema validator supports 3 registry types only)
- fingerprint_index: NOT_APPLICABLE (schema validator supports 3 registry types only)
- derived_validation_reports: NOT_APPLICABLE (schema validator supports 3 registry types only)

pointer_validation:
- ACTIVE_REGISTRY_POINTERS_v0_1.json: PASS
- threshold_registry_db: UNKNOWN (pointer unresolved by design)
- validation_range_results: UNKNOWN (collection registry, no singleton active)
- evidence_pack_registry: UNKNOWN (collection registry, no singleton active)
- system_health_report: UNKNOWN (presentation-only, no singleton active)
