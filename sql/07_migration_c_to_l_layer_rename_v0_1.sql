-- =============================================================================
-- MIGRATION: C-layer to L-layer Rename (Phase 1: Compatibility Shims)
-- =============================================================================
-- Purpose: Transition from C-notation (C1/C2/C3) to L-notation (L1/L2/L3)
--          for derived feature views while maintaining backward compatibility.
--
-- Strategy:
--   Phase 1 (this file): Create L* views as canonical, with C* as compatibility wrappers
--   - If C* views exist and L* do not: Create L* as wrappers over C*
--   - If L* views exist: Create C* as wrappers over L* for backward compatibility
--   - If both exist: Do nothing (manual intervention required)
--
-- Background:
--   The repository has completed a rename from C-layer to L-layer notation:
--   - C0 → L0 (passthrough canonical fields)
--   - C1 → L1 (single-bar OHLC primitives)
--   - C2 → L2 (multi-bar context/structure)
--   - C3 → L3 (categorical/regime classification)
--
-- Semantic Change: NONE. L* views are semantically identical to C* views.
--                  This is purely a naming convention change.
--
-- Created: 2026-01-26
-- Author: OVC_Implementer (C-to-L layer rename completion)
-- =============================================================================

BEGIN;

-- =============================================================================
-- PHASE 1A: Create L1 view if only C1 exists
-- =============================================================================

DO $$
DECLARE
    c1_exists boolean;
    l1_exists boolean;
BEGIN
    -- Check if C1 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_c1_features_v0_1'
    ) INTO c1_exists;
    
    -- Check if L1 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_l1_features_v0_1'
    ) INTO l1_exists;
    
    IF c1_exists AND NOT l1_exists THEN
        -- Create L1 as wrapper over C1 (transitional shim)
        RAISE NOTICE 'Creating L1 view as wrapper over existing C1 view';
        CREATE VIEW derived.v_ovc_l1_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_c1_features_v0_1;
        
        RAISE NOTICE 'L1 view created successfully';
    ELSIF l1_exists AND NOT c1_exists THEN
        -- Create C1 as backward compatibility wrapper over L1
        RAISE NOTICE 'Creating C1 compatibility wrapper over L1 view';
        CREATE VIEW derived.v_ovc_c1_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_l1_features_v0_1;
        
        RAISE NOTICE 'C1 compatibility wrapper created';
    ELSIF c1_exists AND l1_exists THEN
        RAISE NOTICE 'Both C1 and L1 views exist - skipping (manual intervention may be needed)';
    ELSE
        RAISE NOTICE 'Neither C1 nor L1 view exists - will be created by canonical view definitions';
    END IF;
END $$;

-- =============================================================================
-- PHASE 1B: Create L2 view if only C2 exists
-- =============================================================================

DO $$
DECLARE
    c2_exists boolean;
    l2_exists boolean;
BEGIN
    -- Check if C2 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_c2_features_v0_1'
    ) INTO c2_exists;
    
    -- Check if L2 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_l2_features_v0_1'
    ) INTO l2_exists;
    
    IF c2_exists AND NOT l2_exists THEN
        -- Create L2 as wrapper over C2 (transitional shim)
        RAISE NOTICE 'Creating L2 view as wrapper over existing C2 view';
        CREATE VIEW derived.v_ovc_l2_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_c2_features_v0_1;
        
        RAISE NOTICE 'L2 view created successfully';
    ELSIF l2_exists AND NOT c2_exists THEN
        -- Create C2 as backward compatibility wrapper over L2
        RAISE NOTICE 'Creating C2 compatibility wrapper over L2 view';
        CREATE VIEW derived.v_ovc_c2_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_l2_features_v0_1;
        
        RAISE NOTICE 'C2 compatibility wrapper created';
    ELSIF c2_exists AND l2_exists THEN
        RAISE NOTICE 'Both C2 and L2 views exist - skipping (manual intervention may be needed)';
    ELSE
        RAISE NOTICE 'Neither C2 nor L2 view exists - will be created by canonical view definitions';
    END IF;
END $$;

-- =============================================================================
-- PHASE 1C: Create L3 view if only C3 exists
-- =============================================================================

DO $$
DECLARE
    c3_exists boolean;
    l3_exists boolean;
BEGIN
    -- Check if C3 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_c3_features_v0_1'
    ) INTO c3_exists;
    
    -- Check if L3 view exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'derived' AND table_name = 'v_ovc_l3_features_v0_1'
    ) INTO l3_exists;
    
    IF c3_exists AND NOT l3_exists THEN
        -- Create L3 as wrapper over C3 (transitional shim)
        RAISE NOTICE 'Creating L3 view as wrapper over existing C3 view';
        CREATE VIEW derived.v_ovc_l3_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_c3_features_v0_1;
        
        RAISE NOTICE 'L3 view created successfully';
    ELSIF l3_exists AND NOT c3_exists THEN
        -- Create C3 as backward compatibility wrapper over L3
        RAISE NOTICE 'Creating C3 compatibility wrapper over L3 view';
        CREATE VIEW derived.v_ovc_c3_features_v0_1 AS 
        SELECT * FROM derived.v_ovc_l3_features_v0_1;
        
        RAISE NOTICE 'C3 compatibility wrapper created';
    ELSIF c3_exists AND l3_exists THEN
        RAISE NOTICE 'Both C3 and L3 views exist - skipping (manual intervention may be needed)';
    ELSE
        RAISE NOTICE 'Neither C3 nor L3 view exists - will be created by canonical view definitions';
    END IF;
END $$;

COMMIT;

-- =============================================================================
-- VERIFICATION QUERIES (run after migration)
-- =============================================================================
-- Check which views now exist:
--   SELECT table_name 
--   FROM information_schema.views 
--   WHERE table_schema = 'derived' 
--     AND table_name ~ '(c|l)[123]_features'
--   ORDER BY table_name;
--
-- Verify L1 view works:
--   SELECT block_id, sym, range, body, direction 
--   FROM derived.v_ovc_l1_features_v0_1 
--   LIMIT 5;
--
-- Verify C1 compatibility wrapper (if exists):
--   SELECT block_id, sym, range, body, direction 
--   FROM derived.v_ovc_c1_features_v0_1 
--   LIMIT 5;
-- =============================================================================
