create schema if not exists ovc_qa;

create table if not exists ovc_qa.validation_run (
  run_id uuid primary key,
  created_at timestamptz default now(),
  symbol text,
  date_ny date,
  ovc_contract_version text,
  status text,
  notes text
);

create table if not exists ovc_qa.expected_blocks (
  run_id uuid,
  symbol text,
  date_ny date,
  block_letter text,
  block_start_ny timestamptz,
  block_end_ny timestamptz
);

create table if not exists ovc_qa.tv_ohlc_2h (
  run_id uuid,
  symbol text,
  date_ny date,
  block_letter text,
  tv_open numeric,
  tv_high numeric,
  tv_low numeric,
  tv_close numeric,
  tv_ts_start_ny timestamptz,
  source text
);

create table if not exists ovc_qa.ohlc_mismatch (
  run_id uuid,
  block_id text,
  block_letter text,
  ovc_open numeric,
  tv_open numeric,
  ovc_high numeric,
  tv_high numeric,
  ovc_low numeric,
  tv_low numeric,
  ovc_close numeric,
  tv_close numeric,
  diff_open numeric,
  diff_high numeric,
  diff_low numeric,
  diff_close numeric,
  tolerance numeric,
  is_match boolean
);
