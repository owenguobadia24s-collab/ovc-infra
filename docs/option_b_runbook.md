# Option B Runbook (Derived Truth Layer)

## Recompute (view-based)
- Ensure ingest tables are current (no derived writes back into ingest).
- Query the view; recomputation is on read:

```sql
select *
from derived.ovc_block_features_v0_1
order by bar_close_ms desc
limit 5;
```

## Optional materialization (immutable snapshot)
- Insert a run record and materialize to a new table without mutating history:

```sql
-- Replace :run_id with a UUID from your client.
insert into derived.derived_runs (run_id, version, formula_hash)
values (:run_id, 'v0.1', md5('derived.ovc_block_features_v0_1:v0.1:block_physics'));

create table derived.ovc_block_features_v0_1_run as
select *, :run_id::uuid as run_id
from derived.ovc_block_features_v0_1;
```

## Validate
- Row parity: compare counts per symbol and date_ny.
- Null guards: verify windowed fields are null when history is missing (N=12 or session start).
- Versioning: check derived_version, formula_hash, and window_spec are stable.
- Spot checks: compute a handful of rows and compare against raw OHLC geometry.

Example checks:

```sql
select sym, count(*)
from derived.ovc_block_features_v0_1
group by sym;

select derived_version, formula_hash, window_spec, count(*)
from derived.ovc_block_features_v0_1
group by derived_version, formula_hash, window_spec;
```

## Compare versions without mutating history
- Keep each version as its own view or snapshot table.
- Use run_id to compare two materialized runs.
- Never update or overwrite prior derived results.

```sql
select a.block_id, a.range_z_12 as range_z_v0_1, b.range_z_12 as range_z_v0_2
from derived.ovc_block_features_v0_1 a
join derived.ovc_block_features_v0_2 b using (block_id);
```
