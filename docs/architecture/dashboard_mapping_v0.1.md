# Dashboard Mapping v0.1 (Option C)

## Control Room
Primary views:
- `ovc.v_data_quality_missing_blocks_v01`
- `ovc.v_data_quality_empty_rates_v01`
- `ovc.v_data_quality_sanity_v01`
- `derived.ovc_scores_v0_1` (recent hit rates + avg_fwd_ret_1 by sym/block4h)

## Pattern Lab
Primary view:
- `derived.v_pattern_outcomes_v01`

## Session Map
Primary view:
- `derived.v_session_heatmap_v01`

Notes:
- Option C keeps evaluation separate; dashboards can join to MIN views for filters.
- When filtering by time, use `date_ny` from MIN and outcomes.
