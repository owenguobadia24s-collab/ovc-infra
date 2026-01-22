# Option C Research Views v0.1

**STATUS: HISTORICAL (REFERENCE ONLY)**  
This document reflects research-view concepts at the time it was written.  
Execution ergonomics are defined in `PATH1_EXECUTION_MODEL.md`.  
Canonical facts remain in `reports/path1/evidence/INDEX.md`.

These views live in schema `derived` and join MIN tags with Option C outcomes.

## derived.v_pattern_outcomes_v01
Purpose: Evaluate pattern buckets using forward outcomes.

Group by:
- eval_version, formula_hash, run_id
- sym, block4h
- state_key, state_tag, value_tag, event
- bias_dir, pred_dir

Metrics:
- n
- avg_fwd_ret_1, med_fwd_ret_1
- avg_mfe_1, avg_mae_1
- hit_rate_1

## derived.v_session_heatmap_v01
Purpose: Time-of-day performance using forward outcomes.

Group by:
- eval_version, formula_hash, run_id
- sym, block4h, block2h

Metrics:
- n
- avg_fwd_ret_1
- hit_rate_1

## derived.v_transition_stats_v01
Purpose: Transition probabilities for structural states with outcome context.

Group by:
- eval_version, formula_hash, run_id
- sym, block4h
- prev_struct_state -> struct_state

Metrics:
- n
- p_next
- avg_fwd_ret_1
- hit_rate_1

Notes:
- These views are additive and do not replace existing research views in `ovc`.
- Outcomes are pulled from `derived.ovc_outcomes_v0_1` to keep evaluation separate.
