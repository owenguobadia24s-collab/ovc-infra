-- Normalized events view
create or replace view ovc.v_ovc_min_events_norm as
select
  block_id, sym, date_utc, block2h, block4h,
  o,h,l,c, rng, body, ret,
  with_htf, tradeable, ready,
  bias_dir, pred_dir,
  trend_tag, struct_state, space_tag, bias_mode, perm_state, play, timebox,
  state_key,
  ingest_ts, src, contract_ver
from ovc.ovc_blocks_v01_1_min;

-- Sequenced view (adds previous state + next returns)
create or replace view ovc.v_ovc_min_events_seq as
with x as (
  select
    *,
    lag(state_key) over (partition by sym order by date_utc, block2h, block_id) as prev_state_key,
    lag(play)      over (partition by sym order by date_utc, block2h, block_id) as prev_play,
    lead(ret)      over (partition by sym order by date_utc, block2h, block_id) as next_ret
  from ovc.v_ovc_min_events_norm
)
select * from x;

-- Pattern outcomes (v0.1): group by play/state_key and compute expectancy
create or replace view ovc.v_pattern_outcomes_v01 as
select
  sym,
  play,
  state_key,
  count(*) as n,
  avg(ret) as avg_ret,
  percentile_cont(0.5) within group (order by ret) as med_ret,
  avg(case when ret > 0 then 1 else 0 end)::double precision as win_rate
from ovc.v_ovc_min_events_norm
group by sym, play, state_key;

-- Transition stats: what tends to follow what (state_key -> next state_key)
create or replace view ovc.v_transition_stats_v01 as
with t as (
  select
    sym,
    prev_state_key as from_state_key,
    state_key as to_state_key
  from ovc.v_ovc_min_events_seq
  where prev_state_key is not null
)
select
  sym,
  from_state_key,
  to_state_key,
  count(*) as n,
  (count(*)::double precision / sum(count(*)) over (partition by sym, from_state_key)) as p
from t
group by sym, from_state_key, to_state_key;

-- Session heatmap: time-of-day edge by block2h / play
create or replace view ovc.v_session_heatmap_v01 as
select
  sym,
  block2h,
  play,
  count(*) as n,
  avg(ret) as avg_ret,
  avg(case when ret > 0 then 1 else 0 end)::double precision as win_rate
from ovc.v_ovc_min_events_norm
group by sym, block2h, play;

-- Data quality views (starter stubs; you can enrich once worker emits dq flags)
create or replace view ovc.v_data_quality_ohlc_basic as
select
  sym,
  count(*) as n,
  sum(case when h < greatest(o,c) then 1 else 0 end) as bad_h_count,
  sum(case when l > least(o,c)    then 1 else 0 end) as bad_l_count,
  sum(case when h < l             then 1 else 0 end) as bad_hl_count
from ovc.v_ovc_min_events_norm
group by sym;
