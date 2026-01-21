# Option D Model Registry Spec (Draft)

## Purpose

Define an append-only registry for downstream modeling artifacts that depend on the
frozen Option B/C spine. This registry records dataset specs, model specs, and runs
without changing any canonical views or scores.

## Spine Reference

- `spine_id` points to the canonical Option B/C views used for features and outcomes.
- Spine inputs are immutable and must not be modified by Option D.

Example spine pointers:

- Features: `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1`, `derived.v_ovc_c3_features_v0_1`
- Outcomes: `derived.v_ovc_c_outcomes_v0_1`

## Dataset Spec

Describes how a dataset is constructed from the spine:

- `dataset_spec_id` (unique, immutable)
- `spine_id` (pointer to canonical views)
- `feature_set_id` (explicit feature list + handling rules)
- `target_spec_id` (label and transformation)
- `filters` (symbol(s), date ranges, block filters)
- `split_policy` (train/val/test rules)
- `query_hash` (canonical hash of the dataset recipe)
- `created_at`, `created_by`, `note`

## Feature Set

Defines explicit columns and handling rules:

- `feature_set_id`
- `columns` (ordered list)
- `null_handling` (drop, impute, carry-forward)
- `scaling` (none, zscore, minmax)
- `encoding` (categorical handling rules)

## Target Spec

Defines the label and its transformation:

- `target_spec_id`
- `label` (source column)
- `transform` (none, log, bucket, quantile)
- `loss_family` (regression, classification)
- `horizon` (if applicable)

## Model Spec

Defines algorithm and constraints:

- `model_spec_id`
- `algorithm` (e.g., linear, xgboost, rf)
- `hyperparameters` (JSON)
- `constraints` (monotonicity, sparsity)
- `notes`

## Model Run

Execution record with artifacts and metrics:

- `model_run_id`
- `dataset_spec_id`
- `model_spec_id`
- `time_range` (training window)
- `metrics` (JSON)
- `artifact_uris` (paths to model files, plots, logs)
- `status` (draft, complete, failed)
- `created_at`, `created_by`

## Promotion Record

Tracks lifecycle stages:

- `promotion_id`
- `model_run_id`
- `status` (research -> candidate -> validated -> deployed)
- `checks` (leakage audit, stability audit, bias audit, drift plan)
- `approved_by`, `approved_at`
- `notes`

## Storage Guidance

- Use a dedicated schema (e.g., `ovc_model`) to avoid clutter.
- All tables are append-only; never update or delete past runs.
- Registry rows must carry `spine_id` and hashes for replay certification.
