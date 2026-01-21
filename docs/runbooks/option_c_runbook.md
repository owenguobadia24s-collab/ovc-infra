# Option C Runbook (Evaluation + Feedback v0.1)

## Apply SQL to Neon
- Run the schema/view definitions from `sql/option_c_v0_1.sql` using your Neon client.

Example (psql):

```sql
psql "$NEON_DATABASE_URL" -f sql/option_c_v0_1.sql
```

## Spot checks
Sample outcomes:

```sql
select *
from derived.ovc_outcomes_v0_1
order by bar_close_ms desc
limit 100;
```

Null rates by horizon:

```sql
select
  sym,
  avg((fwd_ret_1 is null)::int) as p_null_fwd_ret_1,
  avg((fwd_ret_2 is null)::int) as p_null_fwd_ret_2,
  avg((fwd_ret_6 is null)::int) as p_null_fwd_ret_6,
  avg((fwd_ret_12 is null)::int) as p_null_fwd_ret_12
from derived.ovc_outcomes_v0_1
group by sym;
```

Distribution sanity:

```sql
select
  sym,
  avg(fwd_ret_1) as avg_fwd_ret_1,
  min(fwd_ret_1) as min_fwd_ret_1,
  max(fwd_ret_1) as max_fwd_ret_1,
  percentile_cont(0.5) within group (order by fwd_ret_1) as med_fwd_ret_1,
  percentile_cont(0.95) within group (order by fwd_ret_1) as p95_fwd_ret_1
from derived.ovc_outcomes_v0_1
group by sym;
```

## Optional run_id registration
Use this when you want an immutable run identifier for downstream comparisons:

```sql
insert into derived.eval_runs (run_id, eval_version, formula_hash, horizon_spec, notes)
values (
  'run_2026_01_17_001',
  'v0.1',
  md5('derived.ovc_outcomes_v0_1:v0.1:K=1,2,6,12:ref=c:dir=sign:exc=max(h)-c,min(l)-c'),
  'K=1,2,6,12',
  'optional note'
);
```

## Compare versions safely (no mutation)
- Keep each eval version in its own view or snapshot table.
- Compare by `eval_version` + `formula_hash` or by `run_id` when materialized.

```sql
select
  a.block_id,
  a.fwd_ret_1 as fwd_ret_1_v0_1,
  b.fwd_ret_1 as fwd_ret_1_v0_2
from derived.ovc_outcomes_v0_1 a
join derived.ovc_outcomes_v0_2 b using (block_id);
```
