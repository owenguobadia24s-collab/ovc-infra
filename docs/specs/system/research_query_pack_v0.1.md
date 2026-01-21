1) Core derived views/tables (conceptual)
A) ovc_min_events (base)

This is just your MIN rows, one per 2H block, keyed by:

block_id (PK)

sym

bar_close_ms

B) ovc_min_events_seq (adds "previous block" context)

Adds:

prev_block_id

prev_fx/fxv/tag later (if/when those exist)

prev_ret, prev_dir, etc.

Sequencing rule:

partition by sym

order by bar_close_ms

lag(...) to get previous values

C) pattern_outcomes_v01

Group stats for "what happens when the system says X".

Group by (v0.1):

sym

block4h, block2h

state_tag, value_tag, trend_tag, struct_state, space_tag

bias_mode, bias_dir, perm_state, play, pred_dir, timebox

tradeable (split stats)

Metrics:

n (count)

avg_ret, med_ret

winrate (ret > 0)

avg_rng

hit_invalidation_rate (requires outcome data later; placeholder now)

signal_alignment_rate (pred_dir == dir)

D) transition_stats_v01

"How often do states transition to other states?"

State definition for v0.1 (choose one, but freeze it):

state_key = trend_tag + "|" + struct_state + "|" + space_tag
(or include bias_mode/bias_dir if you want)

Compute:

prev_state_key -> state_key counts and probabilities

conditional on block4h and timebox

E) session_heatmap_v01

Performance by time segmentation.

Group by:

sym, block4h, block2h
Metrics:

n, avg_ret, winrate, avg_rng
Split by:

tradeable (and later by perm_state)

F) data_quality_v01

Non-negotiable.

Metrics:

duplicates (should be zero by PK)

missing blocks per day (expected 12 per sym/day unless weekend/market closed rules)

ready=0 rate

null/empty field rates for fields you expect populated

2) Important note (your current MIN doesn't include fx/fxv/tag)

Your revised MIN schema includes state/value/trend/struct/space, and L3 prediction fields, but not the full "TagString/fx/fxv" set as first-class fields in the sample object you approved.

That's fine. Lane C can start using:

play, bias_mode, bias_dir, trend_tag, struct_state, space_tag as the "pattern surface"
.and you can add tag/fx/fxv later as v0.1.1/v0.2 without breaking the research framework.

DoD - Research Query Pack v0.1 is complete when:

 We define the state_key formula (exact fields + delimiter)

 We define "win" precisely (ret > 0 vs dir aligned etc.)

 We list each view/table with exact group-by dimensions + metrics

 We define required indexes for fast queries (conceptually)

 We define the first 4 dashboards that consume these outputs

Checklist (spec-only)

Freeze state_key formula (what fields define a "pattern bucket").

Freeze win condition (ret-based, not subjective).

Decide whether to split stats by tradeable and/or perm_state (recommended yes).

Approve the v0.1 derived tables list (A-F).

