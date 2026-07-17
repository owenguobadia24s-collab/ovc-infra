# OVC Data Flow Canon v0.2

**Version:** 0.2  
**Status:** RATIFIED_CURRENT_CLAIMS_AUTHORITY  
**Date:** 2026-07-16  
**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`  
**Prior version:** `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md`  
**Supersession scope:** Current operational data-flow claims only. The prior
file remains preserved as historical governance evidence.

## 1. Authority and Scope

This document governs the intended A to B to C to D data-flow boundary during
operational recovery. It records authority and implementation nonconformance;
it does not repair code, alter schemas, migrate data, change workflows, or
verify deployments.

Current deployed-state evidence remains:

- `docs/current-state/OVC_CURRENT_STATE_DELTA_2026-07-15_ae88bca49e94.md`
- `docs/current-state/r1/OVC_R1_DRIFT_MATRIX_2026-07-16_59db182dfbdd.md`

Where repository implementation differs from this canon, the implementation
is nonconforming. The difference does not silently redefine this canon.

## 2. Canonical Layer Flow

```text
Option A canonical facts
  -> Option B derived feature interfaces
  -> Option C B-backed outcomes
  -> Option D evidence and approved projections
  -> human-facing projection surfaces
```

Direct A to C outcome computation is historical legacy and is not authorized
for new operations. Direct A semantic-field consumption by B, C, or D is
forbidden.

## 3. Option A: Canonical Facts

### 3.1 Authoritative Objects

| Object | Role | Current runtime evidence |
|---|---|---|
| `ovc.ovc_blocks_v01_1_min` | Canonical 2H fact spine | Verified by R0 |
| `ovc.ovc_candles_m15_raw` | Canonical M15 fact surface for evidence overlays | Verified by R0 |

### 3.2 Temporarily Tolerated Physical Legacy

Semantic columns physically present in `ovc.ovc_blocks_v01_1_min`, including
`state_tag`, `trend_tag`, `bias_mode`, `play`, and `pred_dir`, are:

- tolerated temporarily as physical legacy;
- non-authoritative;
- denied as inputs to B, C, and D; and
- not evidence that Option A owns semantic meaning.

Physical removal is not authorized by this document. Removal requires a later
versioned migration with equivalence, rollback, and deployment evidence.

## 4. Option B: Derived Features

The authoritative read interfaces for downstream layers are:

| Interface | Role |
|---|---|
| `derived.v_ovc_c1_features_v0_1` | Single-bar derived features |
| `derived.v_ovc_c2_features_v0_1` | Multi-bar context |
| `derived.v_ovc_c3_features_v0_1` | Semantic feature interface |

Option B may read authoritative Option A facts only through the allowlists in
the active Option A and Option B contracts. It must not consume Option A
semantic legacy columns.

Materialized B tables may coexist with these views, but deployment claims not
verified by R0 remain `UNVERIFIED_DEPLOYMENT`.

## 5. Option C: Outcomes

### 5.1 Required New-Operation Target

`derived.v_ovc_c_outcomes_v0_1` is the required target for:

- all new Option C outcome operations;
- new downstream evidence consumers; and
- new Notion outcome projection.

This preserves the B to C boundary because the view is defined by
`sql/derived/v_ovc_c_outcomes_v0_1.sql` over B interfaces.

The governing contract,
`docs/contracts/option_c_outcomes_contract_v1.md`, remains DRAFT. Therefore
the resolved-authority index must record this surface as
`RATIFICATION_PENDING` or `CONFLICTING`, not fully `AUTHORITATIVE`, until a
formal ratification record exists.

### 5.2 Historical Legacy Surface

`derived.ovc_outcomes_v0_1` and `sql/option_c_v0_1.sql` are retained for:

- historical replay;
- migration verification; and
- audit of prior Option C outputs.

They are not authorized for new operations or new consumers. No new workflow,
script, QA pack, dashboard, or Notion projection may adopt them.

Existing consumers remain nonconforming until changed under a later
authorized repair bundle.

## 6. Option D and Path1

### 6.1 Canonical Operating Path

The range-based Path1 operating loop is canonical:

- implementation: `scripts/path1/run_evidence_range.py`;
- workflow: `.github/workflows/path1_evidence.yml`;
- canonical ledger: `reports/path1/evidence/INDEX.md`.

### 6.2 Queue Path

Queue-based Path1 operation is rejected as canonical.

The following may be retained temporarily for historical analysis or a future
controlled manual recovery contract:

- `scripts/path1/run_evidence_queue.py`;
- `.github/workflows/path1_evidence_queue.yml`;
- `.github/workflows/main.yml`;
- `reports/path1/evidence/RUN_QUEUE.csv`; and
- `reports/path1/evidence/RUN_QUEUE_RESOLVED.csv`.

They are not authorized to:

- operate as scheduled production paths;
- mutate canonical queue state;
- replace the range runner; or
- establish a second canonical ledger.

The scheduled queue trigger currently present in `.github/workflows/main.yml`
is repository nonconformance. This document does not modify it.

## 7. Notion Projection Boundary

The implementation path is `scripts/export/notion_sync.py`. The workflow path
is `.github/workflows/notion_sync.yml`.

For new outcome projection:

- the source must be `derived.v_ovc_c_outcomes_v0_1`;
- the Option C v1 contract must be ratified;
- the workflow must invoke the real implementation path; and
- projection fields must exclude Option A semantic legacy and raw OHLC.

Block identifiers and run provenance may be projected only as identifiers and
audit metadata. `export_str`, raw OHLC, B feature vectors, C3 feature labels,
QA internals, threshold packs, and sync cursors are not authorized projection
payloads.

The current script and workflow are nonconforming because the workflow calls
a missing path and the script reads the legacy outcomes view. External Notion
deployment and schema remain unverified.

## 8. Workflow Authority

Current workflow inventory and execution disposition are defined in
`docs/workflows/WORKFLOW_CATALOG_v0_2.md`.

Key decisions:

- range-based Path1 remains canonical;
- scheduled queue execution is not authorized;
- Option C and Notion remain manual-only in the contained repository state
  and are not authorized for new production execution until their authority
  conflicts are repaired;
- repository workflow presence does not prove deployed trigger state.

## 9. Historical Retention Versus New Execution

| Surface | Retained historically | Authorized for new execution |
|---|---:|---:|
| `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` | Yes | No; current claims are governed by v0.2 |
| Option A semantic legacy columns | Yes, physically tolerated | No downstream semantic consumption |
| `sql/option_c_v0_1.sql` | Yes | No |
| `derived.ovc_outcomes_v0_1` | Yes | No new consumers |
| Queue Path1 files and workflows | Yes | Manual recovery only after a controlled recovery contract; never scheduled production |
| `derived.v_ovc_c_outcomes_v0_1` | Yes | Required target, but production authority remains pending contract ratification |

## 10. Non-Authorization

This canon does not authorize:

- R2;
- schema or migration changes;
- workflow edits;
- schedule changes;
- database writes;
- deployment;
- Notion mutation; or
- physical deletion of legacy state.
