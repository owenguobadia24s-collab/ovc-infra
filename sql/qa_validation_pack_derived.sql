-- QA validation pack (derived-only, single-day tape validation)
-- Required psql vars: :symbol :date_ny

-- 5) Join blocks + derived + outcomes
with params as (
  select :symbol::text as symbol, :date_ny::date as date_ny
)
select
  m.block_id,
  m.sym,
  m.date_ny,
  m.block2h,
  m.block4h,
  m.o,
  m.h,
  m.l,
  m.c,
  f.range as derived_range,
  f.body_ratio as derived_body_ratio,
  o.fwd_ret_1,
  o.fwd_dir_1,
  o.hit_1
from ovc.ovc_blocks_v01_1_min m
left join derived.ovc_block_features_v0_1 f on f.block_id = m.block_id
left join derived.ovc_outcomes_v0_1 o on o.block_id = m.block_id
where m.sym = (select symbol from params)
  and m.date_ny = (select date_ny from params)
order by m.bar_close_ms;
