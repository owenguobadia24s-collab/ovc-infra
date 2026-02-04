create schema if not exists derived;

create table if not exists derived.derived_runs (
  run_id uuid primary key,
  version text not null,
  formula_hash text not null,
  computed_at timestamptz not null default now()
);

create or replace view derived.ovc_block_features_v0_1 as
with base as (
  select
    block_id,
    sym,
    date_ny,
    block2h,
    block4h,
    bar_close_ms,
    o,
    h,
    l,
    c,
    lag(c, 1) over (partition by sym order by bar_close_ms) as prev_c,
    lag(h, 1) over (partition by sym order by bar_close_ms) as prev_h,
    lag(l, 1) over (partition by sym order by bar_close_ms) as prev_l,
    max(h) over (
      partition by sym, date_ny
      order by bar_close_ms
      rows between unbounded preceding and current row
    ) as sess_high,
    min(l) over (
      partition by sym, date_ny
      order by bar_close_ms
      rows between unbounded preceding and current row
    ) as sess_low,
    avg(h - l) over (
      partition by sym
      order by bar_close_ms
      rows between 11 preceding and current row
    ) as roll_avg_range_12,
    stddev_samp(h - l) over (
      partition by sym
      order by bar_close_ms
      rows between 11 preceding and current row
    ) as roll_std_range_12,
    stddev_samp(case when o > 0 and c > 0 then ln(c / o) end) over (
      partition by sym
      order by bar_close_ms
      rows between 11 preceding and current row
    ) as roll_std_logret_12,
    count(h - l) over (
      partition by sym
      order by bar_close_ms
      rows between 11 preceding and current row
    ) as cnt_range_12,
    count(case when o > 0 and c > 0 then 1 end) over (
      partition by sym
      order by bar_close_ms
      rows between 11 preceding and current row
    ) as cnt_logret_12,
    max(h) over (
      partition by sym
      order by bar_close_ms
      rows between 12 preceding and 1 preceding
    ) as prev_high_12,
    min(l) over (
      partition by sym
      order by bar_close_ms
      rows between 12 preceding and 1 preceding
    ) as prev_low_12
  from ovc.ovc_blocks_v01_1_min
),
calc as (
  select
    block_id,
    sym,
    date_ny,
    block2h,
    block4h,
    bar_close_ms,
    to_timestamp(bar_close_ms / 1000.0) as ts_end,
    to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as ts_start,
    o,
    h,
    l,
    c,
    (h - l) as range,
    abs(c - o) as body,
    (h - greatest(o, c)) as upper_wick,
    (least(o, c) - l) as lower_wick,
    case when (h - l) = 0 then null else abs(c - o) / (h - l) end as body_ratio,
    case when (h - l) = 0 then null else (h - greatest(o, c)) / (h - l) end as upper_wick_ratio,
    case when (h - l) = 0 then null else (least(o, c) - l) / (h - l) end as lower_wick_ratio,
    case when (h - l) = 0 then null else (c - l) / (h - l) end as close_pos,
    case when c > o then 1 when c < o then -1 else 0 end as direction,
    case when o = 0 then null else (c / o) - 1 end as ret,
    case when o > 0 and c > 0 then ln(c / o) end as logret,
    case when prev_c is null then null else o - prev_c end as gap,
    sess_high,
    sess_low,
    case when sess_high is null then null else sess_high - c end as dist_sess_high,
    case when sess_low is null then null else c - sess_low end as dist_sess_low,
    case when cnt_range_12 >= 12 then roll_avg_range_12 end as roll_avg_range_12,
    case when cnt_logret_12 >= 12 then roll_std_logret_12 end as roll_std_logret_12,
    case
      when cnt_range_12 >= 12 and roll_std_range_12 is not null and roll_std_range_12 <> 0
      then (h - l - roll_avg_range_12) / roll_std_range_12
    end as range_z_12,
    case when prev_high_12 is null then null else h > prev_high_12 end as hh_12,
    case when prev_low_12 is null then null else l < prev_low_12 end as ll_12,
    case when prev_h is null then null else h > prev_h end as took_prev_high,
    case when prev_l is null then null else l < prev_l end as took_prev_low,
    case when (h - l) = 0 then true else false end as range_zero,
    (o is null or h is null or l is null or c is null) as any_missing_inputs,
    case when o = 0 then null else abs((c / o) - 1) >= 0.05 end as ret_extreme_flag,
    case
      when cnt_range_12 >= 12 and roll_std_range_12 is not null and roll_std_range_12 <> 0
      then abs((h - l - roll_avg_range_12) / roll_std_range_12) >= 3.0
    end as range_extreme_flag
  from base
),
latest_run as (
  select run_id, formula_hash, computed_at
  from derived.derived_runs
  where version = 'v0.1'
    and formula_hash = md5('derived.ovc_block_features_v0_1:v0.1:block_physics')
  order by computed_at desc
  limit 1
)
select
  'v0.1'::text as derived_version,
  md5('derived.ovc_block_features_v0_1:v0.1:block_physics') as formula_hash,
  'N=12;session=date_ny'::text as window_spec,
  latest_run.run_id,
  latest_run.computed_at,
  c.block_id,
  c.sym,
  c.date_ny,
  c.block2h,
  c.block4h,
  c.bar_close_ms,
  c.ts_end,
  c.ts_start,
  c.o,
  c.h,
  c.l,
  c.c,
  c.range,
  c.body,
  c.upper_wick,
  c.lower_wick,
  c.body_ratio,
  c.upper_wick_ratio,
  c.lower_wick_ratio,
  c.close_pos,
  c.direction,
  c.ret,
  c.logret,
  c.gap,
  c.sess_high,
  c.sess_low,
  c.dist_sess_high,
  c.dist_sess_low,
  c.roll_avg_range_12,
  c.roll_std_logret_12,
  c.range_z_12,
  c.hh_12,
  c.ll_12,
  c.took_prev_high,
  c.took_prev_low,
  c.range_zero,
  c.any_missing_inputs,
  c.ret_extreme_flag,
  c.range_extreme_flag
from calc c
left join latest_run on true;
