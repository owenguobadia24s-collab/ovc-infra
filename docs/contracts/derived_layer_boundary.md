# Derived Layer Boundary (Option B)

## Purpose
- Provide deterministic, versioned derived features computed from ingest tables.
- Preserve ingest as the immutable source of record for raw and MIN exports.

## Boundary
- Base ingest tables: `ovc.ovc_blocks_v01_1_min` and `ovc_blocks_v01` (raw OHLC).
- Derived layer: schema `derived` with views/tables such as `derived.ovc_block_features_v0_1`.
- Derived reads from ingest only; no derived writes back into ingest.
- Derived artifacts are additive and versioned (registry, feature set, SQL).

## Non-responsibilities
- Do not modify webhook behavior or ingest schemas.
- Do not change MIN contract files.
- Do not enable mandatory FULL validation; FULL remains opt-in.