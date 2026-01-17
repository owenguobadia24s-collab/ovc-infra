with params as (
  select
    :'run_id'::text as run_id,
    :'started_at'::text as started_at,
    :'finished_at'::text as finished_at,
    nullif(:'spotcheck_status', '')::text as spotcheck_status,
    nullif(:'spotcheck_reason', '')::text as spotcheck_reason
),
run_info as (
  select
    er.eval_version,
    er.formula_hash
  from derived.eval_runs er
  join params p on p.run_id = er.run_id
),
counts as (
  select
    (select count(*) from ovc.ovc_blocks_v01_1_min) as blocks_seen,
    (select count(*) from derived.ovc_outcomes_v0_1 where run_id = (select run_id from params)) as outcomes_written,
    (select count(*) from derived.ovc_scores_v0_1 where run_id = (select run_id from params)) as scores_written
),
null_rates as (
  select
    avg((fwd_ret_1 is null)::int) as k1,
    avg((fwd_ret_2 is null)::int) as k2,
    avg((fwd_ret_6 is null)::int) as k6,
    avg((fwd_ret_12 is null)::int) as k12
  from derived.ovc_outcomes_v0_1
  where run_id = (select run_id from params)
),
hit_rates as (
  select
    avg(hit_1::double precision) as k1,
    avg(hit_2::double precision) as k2,
    avg(hit_6::double precision) as k6,
    avg(hit_12::double precision) as k12
  from derived.ovc_outcomes_v0_1
  where run_id = (select run_id from params)
)
select jsonb_build_object(
  'run_id', p.run_id,
  'started_at', p.started_at,
  'finished_at', p.finished_at,
  'eval_version', coalesce(r.eval_version, 'v0.1'),
  'formula_hash', coalesce(r.formula_hash, md5('derived.ovc_outcomes_v0_1:v0.1:K=1,2,6,12:ref=c:dir=sign:exc=max(h)-c,min(l)-c')),
  'counts', jsonb_build_object(
    'blocks_seen', c.blocks_seen,
    'outcomes_written', c.outcomes_written,
    'scores_written', c.scores_written
  ),
  'null_rates', jsonb_build_object(
    'k1', n.k1,
    'k2', n.k2,
    'k6', n.k6,
    'k12', n.k12
  ),
  'hit_rate', jsonb_build_object(
    'k1', h.k1,
    'k2', h.k2,
    'k6', h.k6,
    'k12', h.k12
  ),
  'spotchecks', jsonb_build_object(
    'status', coalesce(p.spotcheck_status, 'UNKNOWN'),
    'reasons', jsonb_build_array(coalesce(p.spotcheck_reason, ''))
  )
) as run_report_json
from params p
left join run_info r on true
left join counts c on true
left join null_rates n on true
left join hit_rates h on true;
