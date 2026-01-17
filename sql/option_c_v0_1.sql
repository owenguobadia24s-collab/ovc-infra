create schema if not exists derived;

create table if not exists derived.eval_runs (
  run_id text primary key,
  eval_version text not null,
  formula_hash text not null,
  horizon_spec text not null,
  computed_at timestamptz not null default now(),
  notes text
);

create or replace view derived.ovc_outcomes_v0_1 as
with base as (
  select
    block_id,
    sym,
    date_ny,
    block2h,
    block4h,
    bar_close_ms,
    c,
    h,
    l,
    pred_dir,
    lead(c, 1) over w as c_fwd_1,
    lead(c, 2) over w as c_fwd_2,
    lead(c, 6) over w as c_fwd_6,
    lead(c, 12) over w as c_fwd_12,
    max(h) over (w rows between 1 following and 1 following) as max_h_1,
    min(l) over (w rows between 1 following and 1 following) as min_l_1,
    max(h) over (w rows between 1 following and 2 following) as max_h_2,
    min(l) over (w rows between 1 following and 2 following) as min_l_2,
    max(h) over (w rows between 1 following and 6 following) as max_h_6,
    min(l) over (w rows between 1 following and 6 following) as min_l_6,
    max(h) over (w rows between 1 following and 12 following) as max_h_12,
    min(l) over (w rows between 1 following and 12 following) as min_l_12
  from ovc.ovc_blocks_v01_1_min
  window w as (partition by sym order by bar_close_ms)
),
calc as (
  select
    block_id,
    sym,
    date_ny,
    block2h,
    block4h,
    bar_close_ms,
    case when c_fwd_1 is null or c = 0 then null else (c_fwd_1 / c) - 1 end as fwd_ret_1,
    case when c_fwd_2 is null or c = 0 then null else (c_fwd_2 / c) - 1 end as fwd_ret_2,
    case when c_fwd_6 is null or c = 0 then null else (c_fwd_6 / c) - 1 end as fwd_ret_6,
    case when c_fwd_12 is null or c = 0 then null else (c_fwd_12 / c) - 1 end as fwd_ret_12,
    case
      when c_fwd_1 is null then null
      when c_fwd_1 > c then 'UP'
      when c_fwd_1 < c then 'DOWN'
      else 'FLAT'
    end as fwd_dir_1,
    case
      when c_fwd_2 is null then null
      when c_fwd_2 > c then 'UP'
      when c_fwd_2 < c then 'DOWN'
      else 'FLAT'
    end as fwd_dir_2,
    case
      when c_fwd_6 is null then null
      when c_fwd_6 > c then 'UP'
      when c_fwd_6 < c then 'DOWN'
      else 'FLAT'
    end as fwd_dir_6,
    case
      when c_fwd_12 is null then null
      when c_fwd_12 > c then 'UP'
      when c_fwd_12 < c then 'DOWN'
      else 'FLAT'
    end as fwd_dir_12,
    case when c_fwd_1 is null then null else max_h_1 - c end as mfe_1,
    case when c_fwd_1 is null then null else min_l_1 - c end as mae_1,
    case when c_fwd_2 is null then null else max_h_2 - c end as mfe_2,
    case when c_fwd_2 is null then null else min_l_2 - c end as mae_2,
    case when c_fwd_6 is null then null else max_h_6 - c end as mfe_6,
    case when c_fwd_6 is null then null else min_l_6 - c end as mae_6,
    case when c_fwd_12 is null then null else max_h_12 - c end as mfe_12,
    case when c_fwd_12 is null then null else min_l_12 - c end as mae_12,
    pred_dir
  from base
),
latest_run as (
  select run_id, formula_hash, computed_at
  from derived.eval_runs
  where eval_version = 'v0.1'
    and formula_hash = md5('derived.ovc_outcomes_v0_1:v0.1:K=1,2,6,12:ref=c:dir=sign:exc=max(h)-c,min(l)-c')
  order by computed_at desc
  limit 1
)
select
  'v0.1'::text as eval_version,
  md5('derived.ovc_outcomes_v0_1:v0.1:K=1,2,6,12:ref=c:dir=sign:exc=max(h)-c,min(l)-c') as formula_hash,
  latest_run.run_id,
  calc.block_id,
  calc.sym,
  calc.date_ny,
  calc.block2h,
  calc.block4h,
  calc.bar_close_ms,
  calc.fwd_ret_1,
  calc.fwd_dir_1,
  calc.fwd_ret_2,
  calc.fwd_dir_2,
  calc.fwd_ret_6,
  calc.fwd_dir_6,
  calc.fwd_ret_12,
  calc.fwd_dir_12,
  calc.mfe_1,
  calc.mae_1,
  calc.mfe_2,
  calc.mae_2,
  calc.mfe_6,
  calc.mae_6,
  calc.mfe_12,
  calc.mae_12,
  case
    when calc.pred_dir is null or calc.fwd_dir_1 is null then null
    when calc.pred_dir = 'NEUTRAL' and calc.fwd_dir_1 = 'FLAT' then 1
    when calc.pred_dir = calc.fwd_dir_1 then 1
    else 0
  end as hit_1,
  case
    when calc.pred_dir is null or calc.fwd_dir_2 is null then null
    when calc.pred_dir = 'NEUTRAL' and calc.fwd_dir_2 = 'FLAT' then 1
    when calc.pred_dir = calc.fwd_dir_2 then 1
    else 0
  end as hit_2,
  case
    when calc.pred_dir is null or calc.fwd_dir_6 is null then null
    when calc.pred_dir = 'NEUTRAL' and calc.fwd_dir_6 = 'FLAT' then 1
    when calc.pred_dir = calc.fwd_dir_6 then 1
    else 0
  end as hit_6,
  case
    when calc.pred_dir is null or calc.fwd_dir_12 is null then null
    when calc.pred_dir = 'NEUTRAL' and calc.fwd_dir_12 = 'FLAT' then 1
    when calc.pred_dir = calc.fwd_dir_12 then 1
    else 0
  end as hit_12
from calc
left join latest_run on true;

create or replace view derived.ovc_scores_v0_1 as
with base as (
  select
    o.*, 
    m.rng,
    m.ret,
    m.c
  from derived.ovc_outcomes_v0_1 o
  join ovc.ovc_blocks_v01_1_min m on m.block_id = o.block_id
),
bucketed as (
  select
    *,
    case when c = 0 then null else rng / c end as range_pct,
    abs(ret) as abs_ret
  from base
),
labeled as (
  select
    *,
    case
      when range_pct is null then 'UNK'
      when range_pct <= 0 then 'R0'
      when range_pct <= 0.001 then 'R1'
      when range_pct <= 0.0025 then 'R2'
      when range_pct <= 0.005 then 'R3'
      when range_pct <= 0.01 then 'R4'
      else 'R5'
    end as range_bucket,
    case
      when abs_ret is null then 'UNK'
      when abs_ret <= 0.001 then 'V1'
      when abs_ret <= 0.0025 then 'V2'
      when abs_ret <= 0.005 then 'V3'
      when abs_ret <= 0.01 then 'V4'
      else 'V5'
    end as abs_ret_bucket
  from bucketed
)
select
  eval_version,
  formula_hash,
  run_id,
  sym,
  date_ny,
  block4h,
  range_bucket,
  abs_ret_bucket,
  count(*) as n,
  avg(hit_1::double precision) as hit_rate_1,
  avg(hit_2::double precision) as hit_rate_2,
  avg(hit_6::double precision) as hit_rate_6,
  avg(hit_12::double precision) as hit_rate_12,
  avg(fwd_ret_1) as avg_fwd_ret_1,
  avg(fwd_ret_2) as avg_fwd_ret_2,
  avg(fwd_ret_6) as avg_fwd_ret_6,
  avg(fwd_ret_12) as avg_fwd_ret_12,
  percentile_cont(0.5) within group (order by fwd_ret_1) as med_fwd_ret_1,
  percentile_cont(0.5) within group (order by fwd_ret_2) as med_fwd_ret_2,
  percentile_cont(0.5) within group (order by fwd_ret_6) as med_fwd_ret_6,
  percentile_cont(0.5) within group (order by fwd_ret_12) as med_fwd_ret_12,
  avg(mfe_1) as avg_mfe_1,
  avg(mae_1) as avg_mae_1,
  avg(mfe_2) as avg_mfe_2,
  avg(mae_2) as avg_mae_2,
  avg(mfe_6) as avg_mfe_6,
  avg(mae_6) as avg_mae_6,
  avg(mfe_12) as avg_mfe_12,
  avg(mae_12) as avg_mae_12
from labeled
group by
  eval_version,
  formula_hash,
  run_id,
  sym,
  date_ny,
  block4h,
  range_bucket,
  abs_ret_bucket;

create or replace view derived.v_pattern_outcomes_v01 as
select
  o.eval_version,
  o.formula_hash,
  o.run_id,
  m.sym,
  m.block4h,
  m.state_key,
  m.state_tag,
  m.value_tag,
  m.event,
  m.bias_dir,
  m.pred_dir,
  count(*) as n,
  avg(o.fwd_ret_1) as avg_fwd_ret_1,
  percentile_cont(0.5) within group (order by o.fwd_ret_1) as med_fwd_ret_1,
  avg(o.mfe_1) as avg_mfe_1,
  avg(o.mae_1) as avg_mae_1,
  avg(o.hit_1::double precision) as hit_rate_1
from ovc.ovc_blocks_v01_1_min m
left join derived.ovc_outcomes_v0_1 o on o.block_id = m.block_id
group by
  o.eval_version,
  o.formula_hash,
  o.run_id,
  m.sym,
  m.block4h,
  m.state_key,
  m.state_tag,
  m.value_tag,
  m.event,
  m.bias_dir,
  m.pred_dir;

create or replace view derived.v_session_heatmap_v01 as
select
  o.eval_version,
  o.formula_hash,
  o.run_id,
  m.sym,
  m.block4h,
  m.block2h,
  count(*) as n,
  avg(o.fwd_ret_1) as avg_fwd_ret_1,
  avg(o.hit_1::double precision) as hit_rate_1
from ovc.ovc_blocks_v01_1_min m
left join derived.ovc_outcomes_v0_1 o on o.block_id = m.block_id
group by
  o.eval_version,
  o.formula_hash,
  o.run_id,
  m.sym,
  m.block4h,
  m.block2h;

create or replace view derived.v_transition_stats_v01 as
with seq as (
  select
    block_id,
    sym,
    block4h,
    struct_state,
    lag(struct_state) over (partition by sym order by bar_close_ms) as prev_struct_state
  from ovc.ovc_blocks_v01_1_min
),
joined as (
  select
    o.eval_version,
    o.formula_hash,
    o.run_id,
    s.sym,
    s.block4h,
    s.prev_struct_state,
    s.struct_state,
    o.fwd_ret_1,
    o.hit_1
  from seq s
  left join derived.ovc_outcomes_v0_1 o on o.block_id = s.block_id
  where s.prev_struct_state is not null
)
select
  eval_version,
  formula_hash,
  run_id,
  sym,
  block4h,
  prev_struct_state,
  struct_state,
  count(*) as n,
  count(*)::double precision
    / nullif(sum(count(*)) over (partition by eval_version, formula_hash, run_id, sym, block4h, prev_struct_state), 0) as p_next,
  avg(fwd_ret_1) as avg_fwd_ret_1,
  avg(hit_1::double precision) as hit_rate_1
from joined
group by eval_version, formula_hash, run_id, sym, block4h, prev_struct_state, struct_state;
