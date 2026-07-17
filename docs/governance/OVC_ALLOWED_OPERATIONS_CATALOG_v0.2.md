# OVC Allowed Operations Catalog v0.2

**Version:** 0.2  
**Status:** RATIFIED_ADDITIVE_EXTENSION  
**Ratification date:** 2026-07-16  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`  
**Base catalog:** `docs/governance/OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md`  
**Ratification record:** `docs/current-state/r1/OVC_R1_CLOSURE_DECISION_2026-07-16_59db182dfbdd.md`

## Authority Model

This catalog is a formal additive extension to v0.1. It ratifies only
OP-QA07, OP-QA09, and OP-QA11.

The v0.1 catalog remains authoritative for its existing entries and is not
artifact-level superseded. The Phase 2.2 draft remains historical proposal
evidence and does not independently authorize OP-QA08 or OP-QA10.

## OP-QA07: Run Registry Build

| Field | Ratified value |
|---|---|
| Operation ID | OP-QA07 |
| Option | QA |
| Purpose | Scan governed run roots and produce the versioned run registry |
| Bound executable | `tools/run_registry/build_run_registry_v0_1.py` |
| Inputs | `.codex/RUNS/`, `reports/runs/`, `reports/path1/evidence/runs/` |
| Outputs | `RUN_REGISTRY_v0_1.jsonl`, schema, run envelope, manifest, and seal |
| Evidence | Historical sealed outputs and Phase 2.2.1 schema/seal validation |
| Lifecycle | `ACTIVE_WITH_RECORDED_LIMITATIONS` |

Recorded limitations:

- no dedicated unit test;
- no CI enforcement gate; and
- timestamped run-envelope fields prevent whole-folder byte identity even
  when registry content is deterministic.

## OP-QA09: Drift Signals Build

| Field | Ratified value |
|---|---|
| Operation ID | OP-QA09 |
| Option | QA |
| Purpose | Build versioned schema, threshold-pack, and operation drift signals |
| Bound executable | `tools/run_registry/build_drift_signals_v0_1.py` |
| Inputs | Active run registry, operation-status input, expected versions, and threshold packs |
| Outputs | `DRIFT_SIGNALS_v0_1.json`, schema, run envelope, manifest, and seal |
| Evidence | Historical sealed output, active pointer, and Phase 2.2.1 schema/seal validation |
| Lifecycle | `ACTIVE_WITH_RECORDED_LIMITATIONS` |

Recorded limitations:

- no dedicated unit test;
- no CI enforcement gate;
- expected threshold-version authority remains partly unresolved; and
- the current build chain consumes OP-QA08 output. OP-QA08 is not ratified
  by this catalog, so production chaining through OP-QA08 remains conditional
  until its path contract is corrected and separately approved.

The OP-QA09 operation is authoritative. This does not promote OP-QA08 or
convert its output into an independently authoritative operation.

## OP-QA11: Registry Delta Log Build

| Field | Ratified value |
|---|---|
| Operation ID | OP-QA11 |
| Option | QA |
| Purpose | Build an append-only registry transition log from sealed manifests |
| Bound executable | `docs/phase_2_2/builders/build_registry_delta_log_v0_1.py` |
| Inputs | Sealed run folders, active pointers, registry catalog, and catalog addendum |
| Outputs | `REGISTRY_DELTA_LOG_v0_1.jsonl`, run envelope, manifest, and seal |
| Evidence | Phase 2.2.3 schema, seal, ordering, and deterministic-input validation |
| Lifecycle | `ACTIVE_WITH_RECORDED_LIMITATIONS` |

Recorded limitations:

- no dedicated unit test;
- no CI enforcement gate; and
- execution remains manual.

## Operations Not Ratified

| Operation | Status | Required next decision |
|---|---|---|
| OP-QA08 | `CONDITIONAL / IMPLEMENTED_UNRATIFIED` | Correct and verify its governance path contract, then seek separate ratification |
| OP-QA10 | `DEFERRED / IMPLEMENTED_UNRATIFIED` | Correct the contract/output-name mismatch, then seek separate ratification |

## Change Log

| Version | Change |
|---|---|
| v0.1 | Existing authoritative operation inventory |
| v0.2 | Add OP-QA07, OP-QA09, and OP-QA11 with recorded limitations |

## Non-Authorization

This catalog does not authorize R2, Option C v1 ratification, workflow
changes, schema changes, deployment, database mutation, or schedule changes.
