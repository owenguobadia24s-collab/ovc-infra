create table if not exists ovc.ovc_blocks_v01_1_min (
  -- identity
  block_id        text primary key,
  sym             text not null,
  tz              text not null,
  date_ny         date not null,
  bar_close_ms    bigint not null,
  block2h         text not null,
  block4h         text not null,

  -- governance
  ver             text not null,
  profile         text not null,
  scheme_min      text not null,

  -- OHLC
  o               double precision not null,
  h               double precision not null,
  l               double precision not null,
  c               double precision not null,

  -- derived price
  rng             double precision not null,
  body            double precision not null,
  dir             integer not null,
  ret             double precision not null,

  -- state / structure
  state_tag       text not null,
  value_tag       text not null,
  event           text null,
  tt              integer not null,
  cp_tag          text not null,
  tis             integer null,

  rrc             double precision not null,
  vrc             double precision not null,

  trend_tag       text not null,
  struct_state    text not null,
  space_tag       text not null,

  htf_stack       text null,
  with_htf        boolean not null,

  rd_state        text null,
  regime_tag      text null,
  trans_risk      text null,

  bias_mode       text not null,
  bias_dir        text not null check (bias_dir in ('UP','DOWN','NEUTRAL')),
  perm_state      text not null,
  rail_loc        text null,

  tradeable       boolean not null,
  conf_l3         text not null,

  play            text not null,
  pred_dir        text not null check (pred_dir in ('UP','DOWN','NEUTRAL')),
  pred_target     text null,
  timebox         text not null,
  invalidation    text null,

  source          text not null,
  build_id        text not null,
  note            text null,
  ready           boolean not null,

  -- derived + ingest
  state_key       text not null,
  export_str      text not null,
  payload         jsonb not null,
  ingest_ts       timestamptz not null default now()
);

create index if not exists idx_ovc_min_sym_date
  on ovc.ovc_blocks_v01_1_min(sym, date_ny);

create index if not exists idx_ovc_min_state_key
  on ovc.ovc_blocks_v01_1_min(state_key);

create index if not exists idx_ovc_min_block2h
  on ovc.ovc_blocks_v01_1_min(block2h);
