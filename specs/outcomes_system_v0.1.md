1) Design choice (frozen)
MIN stays MIN.

Outcomes are stored in a separate table keyed by block_id (and sym as safety), plus timestamps for audit.

Why: outcomes often require future candles to compute and you’ll want to recompute them when logic improves.

2) Outcome table spec
Table: ovc_outcomes_v01

Primary key: (block_id)
Foreign key: block_id → ovc_min_events(block_id) (conceptual)

Core columns (v0.1)

Identity

block_id (string, PK)

sym (string)

bar_close_ms (bigint) — copied from MIN for easy joins and range filtering

Outcome window definition

outcome_ver (string) — version of the outcome computation logic (evolves)

window_type (string enum) — e.g. NEXT_2H, NEXT_4H, NEXT_N_BARS

window_n (int) — if applicable

window_end_ms (bigint) — timestamp of last candle used in computation

Core realized metrics

mfe_up (float) — max favorable excursion upward from entry reference

mfe_down (float) — max favorable excursion downward (or MAE depending on convention; pick one)

mae_up (float) — max adverse excursion upward

mae_down (float) — max adverse excursion downward

close_pos (float) — normalized close position within the window range (0–1)

next_ext (float) — “next extension” magnitude (your definition)

next_sd (float) — “next standard deviation move” or whatever your nxtsd means (your definition)

Label outcomes (optional but powerful)

outcome_dir (enum UP/DOWN/NEUTRAL) — realized direction over window

outcome_hit_invalidation (bool_01) — did price touch invalidation level (if provided)

outcome_hit_target (bool_01) — did price touch pred_target (if provided)

Audit

computed_at_ms (bigint)

source (string) — e.g. python_job, gh_actions

note (string_or_empty)

3) Reference points (must be explicit)

Outcomes depend on what you consider the “entry reference price”:

v0.1 default (frozen)

ref_price = c (the MIN close price for that block)

And:

pred_target and invalidation are strings in MIN; outcome job must parse numeric when possible.

4) Window definition (v0.1)

Pick one primary window to start. This is the simplest and most consistent:

v0.1 window

window_type = NEXT_4H

uses the next two 2H candles after the current block close (i.e., next 4 hours)

You can later add additional windows (NEXT_2H, NEXT_SESSION, etc.) via window_type without changing MIN.

5) Computation definitions (v0.1)

Assume we have the future candles within the outcome window with:

highs H_i, lows L_i, closes C_i

Given ref_price = c_now:

mfe_up = max(H_i) - ref_price

mfe_down = ref_price - min(L_i)

Adverse versions:

mae_up = max(H_i) - ref_price (if your position is short; so this needs orientation)

mae_down = ref_price - min(L_i) (if your position is long)

To avoid confusion, v0.1 should store direction-agnostic excursions:

exc_up = max(H_i) - ref_price

exc_down = ref_price - min(L_i)

Then later, your strategy logic decides which is MFE/MAE based on play direction.

So in v0.1 I recommend renaming:

mfe_up → exc_up

mfe_down → exc_down

But since you asked for mfe_up/mfe_down, we can keep your names and define them as excursions, not trade-specific.

Close position (0–1):

close_pos = (C_end - min(L_i)) / NULLIF(max(H_i) - min(L_i), 0)

Outcome direction:

outcome_dir = UP if C_end > ref_price; DOWN if C_end < ref_price; else NEUTRAL

Hit invalidation/target:

If invalidation parses to a float:

hit if window range crosses it (using highs/lows)

Same for pred_target

6) Join patterns (how analysis uses it)
Join key

ovc_min_events.block_id = ovc_outcomes_v01.block_id

Upgrade pattern outcomes

Extend v_pattern_outcomes_v01 into a v0.2 view that includes:

avg_exc_up, avg_exc_down

p_hit_target, p_hit_invalidation

expectancy conditioned on plays

7) DoD — Outcome Join Spec v0.1 complete when:

 Outcomes stored separately (MIN unchanged)

 Outcome table columns defined

 Reference price frozen (ref_price = c)

 Window definition frozen (NEXT_4H default)

 Excursion formulas defined

 Target/invalidation hit rules defined

Checklist (spec-only)

Confirm naming: keep mfe_up/mfe_down as excursions, or rename to exc_up/exc_down.

Confirm primary window: NEXT_4H is the default starting point.

Confirm ref_price (close) is acceptable.

Approve ovc_outcomes_v01 table spec as canonical v0.1.