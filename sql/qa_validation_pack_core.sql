-- QA validation pack (core, single-day tape validation)
-- Required psql vars: :symbol :date_ny :run_id
-- Optional vars: :tolerance_seconds (default 10) :tolerance (default 0.00001)

-- 1) List all OVC blocks for date_ny
with params as (
  select :symbol::text as symbol, :date_ny::date as date_ny
)
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
  c
from ovc.ovc_blocks_v01_1_min
where sym = (select symbol from params)
  and date_ny = (select date_ny from params)
order by bar_close_ms;

-- 2) Count blocks (must equal 12)
with params as (
  select :symbol::text as symbol, :date_ny::date as date_ny
)
select count(*) as n_blocks
from ovc.ovc_blocks_v01_1_min
where sym = (select symbol from params)
  and date_ny = (select date_ny from params);

-- 3) Detect missing block letters (A-L)
with params as (
  select :symbol::text as symbol, :date_ny::date as date_ny
),
letters as (
  select chr(65 + idx) as block_letter
  from generate_series(0, 11) as idx
)
select l.block_letter
from letters l
left join ovc.ovc_blocks_v01_1_min m
  on m.sym = (select symbol from params)
 and m.date_ny = (select date_ny from params)
 and m.block2h = l.block_letter
where m.block2h is null
order by l.block_letter;

-- 4a) Validate 2H duration + contiguity (tolerance in seconds)
with params as (
  select
    :symbol::text as symbol,
    :date_ny::date as date_ny,
    :tolerance_seconds::int as tolerance_seconds
),
blocks as (
  select
    block_id,
    block2h as block_letter,
    to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as ts_start,
    to_timestamp(bar_close_ms / 1000.0) as ts_end
  from ovc.ovc_blocks_v01_1_min
  where sym = (select symbol from params)
    and date_ny = (select date_ny from params)
),
ordered as (
  select
    *,
    lag(ts_end) over (order by ts_start) as prev_end
  from blocks
)
select
  block_id,
  block_letter,
  ts_start,
  ts_end,
  abs(extract(epoch from (ts_end - ts_start)) - 7200) as duration_delta_s,
  abs(extract(epoch from (ts_start - prev_end))) as gap_delta_s
from ordered
where abs(extract(epoch from (ts_end - ts_start)) - 7200) > (select tolerance_seconds from params)
   or (prev_end is not null and abs(extract(epoch from (ts_start - prev_end))) > (select tolerance_seconds from params))
order by ts_start;

-- 4b) Validate 2H boundaries against expected schedule
with params as (
  select
    :run_id::uuid as run_id,
    :symbol::text as symbol,
    :date_ny::date as date_ny,
    :tolerance_seconds::int as tolerance_seconds
),
expected as (
  select block_letter, block_start_ny, block_end_ny
  from ovc_qa.expected_blocks
  where run_id = (select run_id from params)
),
blocks as (
  select
    block_id,
    block2h as block_letter,
    to_timestamp(bar_close_ms / 1000.0) - interval '2 hours' as ts_start,
    to_timestamp(bar_close_ms / 1000.0) as ts_end
  from ovc.ovc_blocks_v01_1_min
  where sym = (select symbol from params)
    and date_ny = (select date_ny from params)
)
select
  e.block_letter,
  b.block_id,
  b.ts_start,
  e.block_start_ny,
  extract(epoch from (b.ts_start - e.block_start_ny)) as start_delta_s,
  b.ts_end,
  e.block_end_ny,
  extract(epoch from (b.ts_end - e.block_end_ny)) as end_delta_s
from expected e
left join blocks b
  on b.block_letter = e.block_letter
where b.block_id is null
   or abs(extract(epoch from (b.ts_start - e.block_start_ny))) > (select tolerance_seconds from params)
   or abs(extract(epoch from (b.ts_end - e.block_end_ny))) > (select tolerance_seconds from params)
order by e.block_letter;

-- 6) Compare OVC OHLC vs TradingView OHLC
with params as (
  select
    :run_id::uuid as run_id,
    :symbol::text as symbol,
    :date_ny::date as date_ny
)
select
  m.block_id,
  m.block2h as block_letter,
  m.o as ovc_open,
  tv.tv_open,
  m.h as ovc_high,
  tv.tv_high,
  m.l as ovc_low,
  tv.tv_low,
  m.c as ovc_close,
  tv.tv_close,
  abs(m.o - tv.tv_open) as diff_open,
  abs(m.h - tv.tv_high) as diff_high,
  abs(m.l - tv.tv_low) as diff_low,
  abs(m.c - tv.tv_close) as diff_close
from ovc.ovc_blocks_v01_1_min m
join ovc_qa.tv_ohlc_2h tv
  on tv.run_id = (select run_id from params)
 and tv.symbol = (select symbol from params)
 and tv.date_ny = (select date_ny from params)
 and tv.block_letter = m.block2h
where m.sym = (select symbol from params)
  and m.date_ny = (select date_ny from params)
order by m.bar_close_ms;

-- 7) Populate ovc_qa.ohlc_mismatch (idempotent for run_id)
with params as (
  select :run_id::uuid as run_id
)
delete from ovc_qa.ohlc_mismatch
where run_id = (select run_id from params);

with params as (
  select
    :run_id::uuid as run_id,
    :symbol::text as symbol,
    :date_ny::date as date_ny,
    :tolerance::numeric as tolerance
),
joined as (
  select
    (select run_id from params) as run_id,
    m.block_id,
    m.block2h as block_letter,
    m.o as ovc_open,
    tv.tv_open,
    m.h as ovc_high,
    tv.tv_high,
    m.l as ovc_low,
    tv.tv_low,
    m.c as ovc_close,
    tv.tv_close,
    abs(m.o - tv.tv_open) as diff_open,
    abs(m.h - tv.tv_high) as diff_high,
    abs(m.l - tv.tv_low) as diff_low,
    abs(m.c - tv.tv_close) as diff_close
  from ovc.ovc_blocks_v01_1_min m
  join ovc_qa.tv_ohlc_2h tv
    on tv.run_id = (select run_id from params)
   and tv.symbol = (select symbol from params)
   and tv.date_ny = (select date_ny from params)
   and tv.block_letter = m.block2h
  where m.sym = (select symbol from params)
    and m.date_ny = (select date_ny from params)
)
insert into ovc_qa.ohlc_mismatch (
  run_id,
  block_id,
  block_letter,
  ovc_open,
  tv_open,
  ovc_high,
  tv_high,
  ovc_low,
  tv_low,
  ovc_close,
  tv_close,
  diff_open,
  diff_high,
  diff_low,
  diff_close,
  tolerance,
  is_match
)
select
  run_id,
  block_id,
  block_letter,
  ovc_open,
  tv_open,
  ovc_high,
  tv_high,
  ovc_low,
  tv_low,
  ovc_close,
  tv_close,
  diff_open,
  diff_high,
  diff_low,
  diff_close,
  (select tolerance from params) as tolerance,
  diff_open <= (select tolerance from params)
    and diff_high <= (select tolerance from params)
    and diff_low <= (select tolerance from params)
    and diff_close <= (select tolerance from params) as is_match
from joined
order by block_letter;
