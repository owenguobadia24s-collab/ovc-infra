# Applying the C-to-L Layer Rename Migration

## Quick Start

To apply the migration to your database:

```bash
psql $DATABASE_URL -f sql/07_migration_c_to_l_layer_rename_v0_1.sql
```

Or if using NEON_DSN:

```bash
psql $NEON_DSN -f sql/07_migration_c_to_l_layer_rename_v0_1.sql
```

## What This Migration Does

This migration creates compatibility between C-layer (old) and L-layer (new) view names:

1. **If you have C-named views** (v_ovc_c1_features_v0_1, etc.):
   - Creates L-named views as wrappers over your existing C views
   - Allows new code (using L names) to work with your existing database

2. **If you have L-named views** (v_ovc_l1_features_v0_1, etc.):
   - Creates C-named compatibility wrappers
   - Allows legacy code/queries to continue working

3. **Safe to run multiple times** - The migration checks if views exist before creating them

## Expected Output

You should see messages like:

```
NOTICE:  Creating L1 view as wrapper over existing C1 view
NOTICE:  L1 view created successfully
NOTICE:  Creating L2 view as wrapper over existing C2 view
NOTICE:  L2 view created successfully
NOTICE:  Creating L3 view as wrapper over existing C3 view
NOTICE:  L3 view created successfully
COMMIT
```

Or:

```
NOTICE:  Creating C1 compatibility wrapper over L1 view
NOTICE:  C1 compatibility wrapper created
NOTICE:  Creating C2 compatibility wrapper over L2 view
NOTICE:  C2 compatibility wrapper created
NOTICE:  Creating C3 compatibility wrapper over L3 view
NOTICE:  C3 compatibility wrapper created
COMMIT
```

## Verification

After applying the migration, verify the views exist:

```sql
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'derived' 
  AND table_name ~ '(c|l)[123]_features'
ORDER BY table_name;
```

Expected results (all 6 views should exist):
- v_ovc_c1_features_v0_1
- v_ovc_c2_features_v0_1
- v_ovc_c3_features_v0_1
- v_ovc_l1_features_v0_1
- v_ovc_l2_features_v0_1
- v_ovc_l3_features_v0_1

Test the views work:

```sql
-- Test L1 view
SELECT block_id, sym, range, body, direction 
FROM derived.v_ovc_l1_features_v0_1 
LIMIT 5;

-- Test C1 compatibility wrapper
SELECT block_id, sym, range, body, direction 
FROM derived.v_ovc_c1_features_v0_1 
LIMIT 5;
```

Both queries should return the same data.

## CI Integration

After running this migration, the CI schema check should pass:

```bash
# Install dependencies if needed
pip install psycopg2-binary

# Run the verification
python3 scripts/ci/verify_schema_objects.py
```

This verifies that the required L-named views exist.

## Rollback (Emergency Only)

If you need to rollback the migration:

```sql
-- Drop the wrapper views created by the migration
DROP VIEW IF EXISTS derived.v_ovc_c1_features_v0_1;
DROP VIEW IF EXISTS derived.v_ovc_c2_features_v0_1;
DROP VIEW IF EXISTS derived.v_ovc_c3_features_v0_1;
DROP VIEW IF EXISTS derived.v_ovc_l1_features_v0_1;
DROP VIEW IF EXISTS derived.v_ovc_l2_features_v0_1;
DROP VIEW IF EXISTS derived.v_ovc_l3_features_v0_1;
```

Then recreate your original views from their definition files.

## Next Steps

After applying this migration:

1. ✅ CI schema checks will pass (L* views are now required)
2. ✅ New code using L-notation will work
3. ✅ Legacy code using C-notation will continue to work via compatibility wrappers
4. 📝 Consider updating any remaining C-notation in your local scripts/queries to use L-notation
5. 📅 Plan for eventual removal of C-compatibility wrappers (Q4 2026)

## Support

For questions or issues:
- See: `docs/C_TO_L_RENAME_COMPLETION.md`
- Check: `docs/contracts/l_layer_boundary_spec_v0.1.md`
