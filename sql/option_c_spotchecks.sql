\pset pager off
\pset footer off

\echo 'Option C spotchecks v0.1'

\echo '1) Row count parity'
with ingest as (
  select count(*) as n_ingest
  from ovc.ovc_blocks_v01_1_min
),
outcomes as (
  select count(*) as n_outcomes
  from derived.ovc_outcomes_v0_1
)
select
  'row_count_parity' as check_name,
  n_ingest,
  n_outcomes,
  case when n_ingest = n_outcomes then 'PASS' else 'WARN' end as status
from ingest, outcomes;

\echo '2) Null-rate monotonicity (fwd_ret)'
with rates as (
  select
    sym,
    avg((fwd_ret_1 is null)::int) as p_null_1,
    avg((fwd_ret_2 is null)::int) as p_null_2,
    avg((fwd_ret_6 is null)::int) as p_null_6,
    avg((fwd_ret_12 is null)::int) as p_null_12
  from derived.ovc_outcomes_v0_1
  group by sym
  union all
  select
    '__all__' as sym,
    avg((fwd_ret_1 is null)::int) as p_null_1,
    avg((fwd_ret_2 is null)::int) as p_null_2,
    avg((fwd_ret_6 is null)::int) as p_null_6,
    avg((fwd_ret_12 is null)::int) as p_null_12
  from derived.ovc_outcomes_v0_1
)
select
  'null_rate_monotonicity' as check_name,
  sym,
  p_null_1,
  p_null_2,
  p_null_6,
  p_null_12,
  case
    when p_null_1 <= p_null_2
     and p_null_2 <= p_null_6
     and p_null_6 <= p_null_12
    then 'PASS'
    else 'WARN'
  end as status
from rates
order by case when sym = '__all__' then 0 else 1 end, sym;

\echo '3) Hit rate bounds'
with stats as (
  select
    'hit_1' as metric,
    min(hit_1) as min_hit,
    max(hit_1) as max_hit,
    count(*) filter (where hit_1 is not null and hit_1 not in (0, 1)) as n_out_of_bounds
  from derived.ovc_outcomes_v0_1
  union all
  select
    'hit_2' as metric,
    min(hit_2) as min_hit,
    max(hit_2) as max_hit,
    count(*) filter (where hit_2 is not null and hit_2 not in (0, 1)) as n_out_of_bounds
  from derived.ovc_outcomes_v0_1
  union all
  select
    'hit_6' as metric,
    min(hit_6) as min_hit,
    max(hit_6) as max_hit,
    count(*) filter (where hit_6 is not null and hit_6 not in (0, 1)) as n_out_of_bounds
  from derived.ovc_outcomes_v0_1
  union all
  select
    'hit_12' as metric,
    min(hit_12) as min_hit,
    max(hit_12) as max_hit,
    count(*) filter (where hit_12 is not null and hit_12 not in (0, 1)) as n_out_of_bounds
  from derived.ovc_outcomes_v0_1
)
select
  'hit_rate_bounds' as check_name,
  metric,
  min_hit,
  max_hit,
  n_out_of_bounds,
  case when n_out_of_bounds = 0 then 'PASS' else 'WARN' end as status
from stats;

\echo '4) MFE/MAE sign sanity'
with stats as (
  select
    'k=1' as horizon,
    count(*) filter (where mfe_1 is not null and mae_1 is not null and mfe_1 < mae_1) as n_order_violation,
    count(*) filter (where mfe_1 is not null and mfe_1 < 0) as n_mfe_negative,
    count(*) filter (where mae_1 is not null and mae_1 > 0) as n_mae_positive
  from derived.ovc_outcomes_v0_1
  union all
  select
    'k=2' as horizon,
    count(*) filter (where mfe_2 is not null and mae_2 is not null and mfe_2 < mae_2) as n_order_violation,
    count(*) filter (where mfe_2 is not null and mfe_2 < 0) as n_mfe_negative,
    count(*) filter (where mae_2 is not null and mae_2 > 0) as n_mae_positive
  from derived.ovc_outcomes_v0_1
  union all
  select
    'k=6' as horizon,
    count(*) filter (where mfe_6 is not null and mae_6 is not null and mfe_6 < mae_6) as n_order_violation,
    count(*) filter (where mfe_6 is not null and mfe_6 < 0) as n_mfe_negative,
    count(*) filter (where mae_6 is not null and mae_6 > 0) as n_mae_positive
  from derived.ovc_outcomes_v0_1
  union all
  select
    'k=12' as horizon,
    count(*) filter (where mfe_12 is not null and mae_12 is not null and mfe_12 < mae_12) as n_order_violation,
    count(*) filter (where mfe_12 is not null and mfe_12 < 0) as n_mfe_negative,
    count(*) filter (where mae_12 is not null and mae_12 > 0) as n_mae_positive
  from derived.ovc_outcomes_v0_1
)
select
  'mfe_mae_sign_sanity' as check_name,
  horizon,
  n_order_violation,
  n_mfe_negative,
  n_mae_positive,
  case when n_order_violation = 0 then 'PASS' else 'WARN' end as status
from stats;

\echo '5) Recent sample (last 20 blocks)'
select
  o.block_id,
  o.sym,
  o.bar_close_ms,
  m.c,
  m.pred_dir,
  o.fwd_ret_1,
  o.fwd_dir_1,
  o.mfe_1,
  o.mae_1,
  o.hit_1
from derived.ovc_outcomes_v0_1 o
join ovc.ovc_blocks_v01_1_min m on m.block_id = o.block_id
order by o.bar_close_ms desc
limit 20;
