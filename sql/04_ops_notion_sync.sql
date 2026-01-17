create schema if not exists ops;

create table if not exists ops.notion_sync_state (
  name text primary key,
  last_ts timestamptz,
  updated_at timestamptz not null default now()
);

insert into ops.notion_sync_state (name, last_ts, updated_at)
values
  ('blocks_min', null, now()),
  ('outcomes', null, now()),
  ('eval_runs', null, now())
on conflict (name) do nothing;
