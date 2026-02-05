# PHASE_2_2_2_VALIDATION_REPORT

validation_run_utc: 2026-02-05T02:14:47Z

before:
- run_registry: PASS (schema validator)
- drift_signals: PASS (schema validator)
- op_status_table: FAIL (top-level array; schema expected object)

after:
- run_registry: PASS (schema validator)
- drift_signals: PASS (schema validator)
- op_status_table: PASS (array wrapper schema selected)

changes:
- added docs/phase_2_2/schemas/REGISTRY_op_status_table_v0_1.array.schema.json
- updated docs/phase_2_2/validators/validate_registry_schema_v0_1.py to select array schema when op_status_table root is a list

immutability_statement:
- Phase 2.1 build scripts: NOT MODIFIED
- Phase 2.1 run artifacts: NOT MODIFIED
- Phase 2.2 frozen artifacts (catalogs/schemas/seal contract/pointers): NOT MODIFIED
