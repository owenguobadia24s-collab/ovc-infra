---
type: repo-maze-law
tags: [ovc, repo, maze, boundary, canonical]
---

# A↔D Boundary (Canonical Law)
This document defines the single authoritative boundary between Option A and Option D.

## Boundary Definition
### LAST 2H TRUTH SOURCE
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/backbone_2h.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-A-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-B-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-C-GBPUSD.csv`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/strips/2h/20221211-D-GBPUSD.csv`

### FIRST 15m TRUTH SOURCE
- `sql/path1/db_patches/patch_m15_raw_20260122.sql`
- `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`
- `docs/contracts/A_TO_D_CONTRACT_v1.md`

## Resample Contract (Authoritative)
### Inputs
- `sql/00_schema.sql`
- `sql/schema_v01.sql`
- `sql/02_derived_c1_c2_tables_v0_1.sql`
- `docs/contracts/ingest_boundary.md`
- `docs/contracts/option_a_ingest_contract_v1.md`

### Outputs
- `docs/evidence_pack/EVIDENCE_PACK_v0_2.md`
- `docs/evidence_pack_provenance.md`
- `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/backbone_2h.csv`

### Invariants
- The 2H backbone is derived only from the 15m-aligned inputs defined in `sql/path1/db_patches/patch_m15_raw_20260122.sql`.
- Contract boundaries in `docs/contracts/A_TO_D_CONTRACT_v1.md` and `docs/contracts/min_contract_alignment.md` are mandatory.
- Evidence pack provenance in `docs/evidence_pack_provenance.md` must be preserved for every run.

### Forbidden states
- 2H outputs exist without a corresponding 15m alignment patch applied (`sql/path1/db_patches/patch_m15_raw_20260122.sql`).
- Evidence pack outputs exist without contract alignment (`docs/contracts/min_contract_alignment.md`).
- A 2H backbone exists without evidence pack documentation (`docs/evidence_pack/EVIDENCE_PACK_v0_2.md`).

## Workflow Ordering Law
- Required predecessors before Path1 evidence runs:
  - `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md`
  - `docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md`
  - `docs/contracts/A_TO_D_CONTRACT_v1.md`
- Ordering rule: Path1 MUST NOT run unless the A→D contract is satisfied and the evidence protocol is in force for the run.

## Determinism & Hashing Law
### Required hashes
- Content fingerprints recorded in:
  - `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`
  - `reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2026/fp_GBPUSD_20260117_03c0d079.json`

### Fields included in hash
- As specified by contract alignment in `docs/contracts/min_contract_alignment.md`.

### Fields explicitly excluded/zeroed
- As specified by contract alignment in `docs/contracts/min_contract_alignment.md`.

### Where hashes are stored and verified
- Stored in fingerprint reports:
  - `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`
  - `reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2026/fp_GBPUSD_20260117_03c0d079.json`
- Verified by validation harness outputs:
  - `reports/runs/20260120T175601Z__D-ValidationHarness__ee6a769/checks.json`
  - `reports/runs/20260120T175633Z__D-ValidationHarness__ee6a769/checks.json`

## Failure Signatures (Operational)
- Missing 2H backbone output file: `reports/path1/evidence/runs/p1_20260120_031/outputs/evidence_pack_v0_2/backbone_2h.csv`
- Evidence pack outputs exist but contract alignment docs are absent: `docs/contracts/A_TO_D_CONTRACT_v1.md`
- Determinism fingerprints missing or mismatched: `reports/path1/trajectory_families/v0.1/fingerprints/index.csv`
- Validation harness reports a failed check: `reports/runs/20260120T175601Z__D-ValidationHarness__ee6a769/checks.json`
- Alignment patch not present for 15m inputs: `sql/path1/db_patches/patch_m15_raw_20260122.sql`

## References
- [[01_OPTION_A__INGEST]]
- [[04_OPTION_D_PATHS_BRIDGE]]
- [[05_QA_GOVERNANCE]]
- [[ANCHOR_CATALOG]]
