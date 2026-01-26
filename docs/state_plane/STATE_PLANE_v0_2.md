# State Plane v0.2

## Purpose

Define a deterministic state plane for each 2H block (A-L) as a point (x_energy, y_shift).
The day becomes a trajectory. This is descriptive only and uses canonical L1/L2/L3 views.

## Canonical Inputs

- `derived.v_ovc_l1_features_v0_1`
- `derived.v_ovc_l2_features_v0_1`
- `derived.v_ovc_l3_features_v0_1` (labels only)

No Option C joins inside the view.

## Axis Definitions

### X-axis: x_energy (0 to 1)

Weighted blend of three normalized components:

- Range intensity: `rng_rank_6` (L2)
- Body participation: `body_ratio` (L1)
- Directional efficiency: `abs(directional_efficiency)` (L1)

All weights and thresholds come from the threshold pack
`state_plane_v0_2_default` in `ovc_cfg.threshold_pack`.
If any input is NULL, `x_energy` is NULL.

### Y-axis: y_shift (-1 to 1)

Weighted blend of L3 labels mapped to numeric values:

- `l3_trend_bias`: sustained -> -1.0, nascent -> -0.5, neutral -> 0.0, fading -> 0.5
- `l3_momentum_state`: accelerating -> -1.0, steady -> 0.0, decelerating -> 0.5, reversing -> 1.0

Weights and mappings come from the threshold pack.
If any input is NULL, `y_shift` is NULL.

## Quadrants

Thresholds from the pack:

- `E_hi`: energy threshold
- `S_hi`: shift magnitude threshold

Quadrant assignment:

- Q1 Expansion: `x_energy >= E_hi` and `abs(y_shift) <= S_hi`
- Q2 Consolidation: `x_energy < E_hi` and `abs(y_shift) <= S_hi`
- Q3 Reversal: `x_energy >= E_hi` and `abs(y_shift) > S_hi`
- Q4 Retracement: `x_energy < E_hi` and `abs(y_shift) > S_hi`

`quadrant_confidence` is the minimum distance to the two thresholds
(`abs(x_energy - E_hi)` and `abs(abs(y_shift) - S_hi)`).

## View Contract

View: `derived.v_ovc_state_plane_v0_2`

Minimum outputs:

- Identity: `block_id`, `sym`, `date_ny`, `block2h`, `bar_close_ms`
- Coordinates: `x_energy`, `y_shift`
- Quadrants: `quadrant_id`, `quadrant_name`, `quadrant_confidence`
- Threshold pack provenance: `threshold_pack_id`, `threshold_pack_version`, `threshold_pack_hash`
- Metadata: `state_plane_meta` JSON with `threshold_pack_id` and `source_view_names`

## Threshold Pack JSON Spec

Pack ID: `state_plane_v0_2_default` (GLOBAL scope, version 1)
Default config file: `configs/threshold_packs/state_plane_v0_2_default_v1.json`

Required keys in `config_json`:

- `thresholds`: `E_hi`, `S_hi`
- `weights.x_energy`: `rng_rank_6`, `body_ratio`, `directional_efficiency`
- `weights.y_shift`: `trend_bias`, `momentum_state`
- `y_map.trend_bias`: mapping for sustained/nascent/neutral/fading
- `y_map.momentum_state`: mapping for accelerating/steady/decelerating/reversing
- `columns`: explicit column names for replay
- `source_views`: list of canonical inputs

All thresholds and weights are versioned in `ovc_cfg.threshold_pack`.

## Interpretation Notes

Quadrants are descriptive, not predictive.
They are safe to join with Option C outcomes for studies, but outcomes are not
used inside the state plane view.

## Misidentification Risks

- News spikes can inflate `x_energy` and mimic "reversal".
- Short-lived volatility bursts can look like shift even when regime persists.
- Low-liquidity periods can understate energy and exaggerate retracement.
- L3 label noise can move `y_shift` across the `S_hi` boundary.
