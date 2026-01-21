Dashboard 1 — OVC Control Room (Ops + Data Quality)

Purpose: detect silent failure early. If this breaks, nothing else matters.

Primary sources:

v_data_quality_missing_blocks_v01

v_data_quality_empty_rates_v01

v_data_quality_sanity_v01

Filters:

sym

date range (date_ny)

(optional) build_id to detect “new build broke fields”

Widgets

Missing Blocks Table

Columns: date_ny, sym, blocks_seen, blocks_missing_assuming_12, blocks_ready0, blocks_tradeable0

Question: Did we capture all expected 2H blocks?

Sanity Error Counters

n_ohlc_inconsistent, n_dir_inconsistent, n_rng_negative, n_tradeable_but_not_ready

Question: Is the data logically consistent?

Field Null-Rate Table

p_state_tag_null, p_trend_tag_null, p_play_null, p_pred_dir_null, etc.

Question: Which fields aren’t being populated (system drift or logic failure)?

Ready/Tradeable Rates Over Time

time series: %ready=1, %tradeable=1

Question: Is the system suddenly calling everything untradeable, or failing readiness?

Dashboard 2 — Edge Scoreboard (Pattern Outcomes)

Purpose: identify what actually works (and what bleeds) using your own tags.

Primary source:

v_pattern_outcomes_v01

Filters:

sym

tradeable (toggle: all / tradeable only)

date range

block4h / block2h (session focus)

bias_mode, perm_state, play (drill-down)

Widgets

Top 20 Buckets by avg_ret (min n threshold)

show: state_key, n, avg_ret, winrate, avg_rng, pred_alignment_rate

Rule: only show buckets where n >= 30 (or whatever you set)

Question: Which recurring situations have positive expectancy?

Bottom 20 Buckets (risk list)

same columns, sorted ascending

Question: Which situations are poison?

Bucket Stability View

add: avg_abs_ret and optionally “volatility-adjusted score” later

Question: Is the edge stable or just one fat tail event?

Prediction Alignment (Quality, not edge)

sort by pred_alignment_rate (with n filter)

Question: When the system predicts UP/DOWN, does it match realized direction?

Dashboard 3 — Session Heatmap (Time-of-Day Edge)

Purpose: your edge is not uniform across the day. This exposes timing bias.

Primary source:

v_session_heatmap_v01

Filters:

sym

tradeable toggle

date range

optionally ready=1 only

Widgets

Heatmap Table

rows: block4h

columns: block2h

cell values: avg_ret (primary), winrate (secondary)

Question: Which blocks are worth your attention?

Session Summary

group by block4h: n, avg_ret, winrate

Question: Which 4H sessions produce the best conditions?

Risk Heatmap

same layout but shows avg_abs_ret or avg_rng

Question: Where is the market most violent (and does that help or hurt you)?

Dashboard 4 — State Transitions (What tends to come next)

Purpose: make your system predictive by statistics (priors), not vibes.

Primary source:

v_transition_stats_v01

Filters:

sym

date range

block4h/timebox focus

tradeable toggle

Widgets

Top transitions given previous state

input control: select prev_state_key

output table: state_key, n, p_next_given_prev

Question: Given what just happened, what’s most likely next?

Transition map (table form)

for a restricted set: top 10 prev states × top 10 next states

Question: Is your market behaving like a stable system or a chaotic one lately?

Transition Drift

compare p_next_given_prev across two time windows (e.g., last 30 days vs prior 30)

Question: Has the market regime shifted enough that priors changed?

Global Dashboard Rules (so it stays sane)

Always show n next to any metric.

Default filter: ready=1. Add toggle for “include ready=0”.

Use minimum sample thresholds:

n >= 30 for strong claims

n 10–29 = weak signal

<10 = ignore

DoD — Dashboard Spec v0.1 complete when:

 4 dashboards defined with sources, filters, widgets, and questions

 Global rules for statistical sanity defined (n thresholds, ready filter)

 Each dashboard maps directly to an existing view in Query Pack v0.1

Checklist (spec-only, no implementation)

Choose default timeframe (e.g., last 30 days) for each dashboard.

Choose initial n thresholds (30/10 default OK).

Decide whether state_key should include play/pred_dir/timebox (it does in v0.1 spec; you can slim later as v0.1.1).

Approve these as canonical “OVC Research v0.1” dashboards.