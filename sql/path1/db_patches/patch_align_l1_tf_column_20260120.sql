-- =============================================================================
-- DB PATCH: Align L1 view with actual MIN table schema
-- =============================================================================
-- Issue: v_ovc_l1_features_v0_1.sql references column 'tf' which does not exist
--        in ovc.ovc_blocks_v01_1_min table. Table has 'tz' and 'tt' columns.
--
-- Root Cause: Schema drift between view definition and canonical table.
--             The view SQL expects 'tf' (timeframe?) but table has:
--               - tz (text): timezone string
--               - tt (integer): timeframe type indicator
--
-- Fix Strategy: Add computed column alias 'tf' to table via a wrapper view,
--               OR patch the database to add a generated column.
--
-- Decision: Add a generated column 'tf' as alias for 'tz' to maintain
--           backward compatibility with existing view SQL.
--
-- Created: 2026-01-20
-- Author: Evidence Run p1_20260120_001 deployment
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- OPTION A: Add computed column to MIN table (preferred - minimal change)
-- This adds 'tf' as GENERATED ALWAYS column aliasing 'tz'
-- -----------------------------------------------------------------------------

-- Check if column already exists before adding
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ovc' 
          AND table_name = 'ovc_blocks_v01_1_min' 
          AND column_name = 'tf'
    ) THEN
        -- Add tf as a stored generated column copying tz value
        -- Note: PostgreSQL 12+ supports GENERATED ALWAYS AS (expression) STORED
        ALTER TABLE ovc.ovc_blocks_v01_1_min 
        ADD COLUMN tf text GENERATED ALWAYS AS (tz) STORED;
        
        RAISE NOTICE 'Added generated column tf as alias for tz';
    ELSE
        RAISE NOTICE 'Column tf already exists, skipping';
    END IF;
END $$;

COMMIT;

-- =============================================================================
-- SMOKE TEST QUERIES (run after patch)
-- =============================================================================
-- 1. Verify column exists:
--    SELECT column_name, data_type, is_generated 
--    FROM information_schema.columns 
--    WHERE table_schema='ovc' AND table_name='ovc_blocks_v01_1_min' AND column_name='tf';
--
-- 2. Verify data matches:
--    SELECT block_id, tz, tf FROM ovc.ovc_blocks_v01_1_min LIMIT 5;
--    (tf should equal tz for all rows)
--
-- 3. Verify L1 view can now be created:
--    psql $DATABASE_URL -f sql/derived/v_ovc_l1_features_v0_1.sql
-- =============================================================================
