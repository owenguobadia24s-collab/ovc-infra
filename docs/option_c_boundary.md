# Option C Boundary (Evaluation + Feedback Layer v0.1)

## Purpose
- Compute replayable outcomes that describe what happened after each 2H block.
- Evaluate existing predictions/tags without creating new meaning labels.
- Keep outcomes and scoring additive, versioned, and recomputable.

## Boundary
- Reads: `ovc.ovc_blocks_v01_1_min` (authoritative MIN ingest).
- Optional reads: `derived.ovc_block_features_v0_1` if present for richer buckets.
- Writes: derived-only tables/views in schema `derived`.

## Outputs
- `derived.eval_runs` (optional immutable run tracking).
- `derived.ovc_outcomes_v0_1` (row-level outcomes + hit checks).
- `derived.ovc_scores_v0_1` (aggregated scoring metrics).
- Research views in `derived` that join MIN tags to outcomes.

## Non-responsibilities
- No changes to ingest/webhook code, MIN contract, or `ovc.ovc_blocks_v01_1_min` schema.
- No back-writing into ingest.
- No new interpretive labels; only outcomes and scoring.
- No mutation of Option A or Option B boundaries.

## Versioning
- Every output carries `eval_version` and `formula_hash`.
- `run_id` is optional and only populated for immutable runs.
