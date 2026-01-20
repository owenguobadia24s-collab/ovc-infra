-- =============================================================================
-- DB PATCH: Create Path 1 Evidence Compatible Outcomes Wrapper
-- =============================================================================
-- Issue: Evidence views expect columns (outcome_dir, outcome_rng, outcome_ret,
--        outcome_category, next_block_id, next_bar_close_ms) but the actual
--        v_ovc_c_outcomes_v0_1 has different column names (fwd_ret_1, etc.).
--
-- Fix: Create wrapper views that map existing columns to expected names,
--      then create evidence views that use these wrappers.
--
-- Created: 2026-01-20
-- =============================================================================

BEGIN;

-- =============================================================================
-- Create Path 1 Evidence Views with adapted column mappings
-- =============================================================================

-- DIS-v1.1 Evidence View
DROP VIEW IF EXISTS derived.v_path1_evidence_dis_v1_1;

CREATE VIEW derived.v_path1_evidence_dis_v1_1 AS
SELECT
    -- Identifiers
    s.block_id,
    s.sym,
    s.bar_close_ms,
    
    -- Score raw value (DIS-v1.1, frozen)
    s.dis_score AS dis_v1_1_raw,
    
    -- Outcome fields (mapped from actual Option C columns)
    -- Using fwd_ret_1 as the primary outcome return metric
    CASE 
        WHEN o.fwd_ret_1 > 0 THEN 1
        WHEN o.fwd_ret_1 < 0 THEN -1
        ELSE 0
    END AS outcome_dir,
    NULL::double precision AS outcome_rng,  -- Not available in current schema
    o.fwd_ret_1 AS outcome_ret,
    CASE 
        WHEN o.fwd_ret_1 > 0.001 THEN 'UP'
        WHEN o.fwd_ret_1 < -0.001 THEN 'DOWN'
        ELSE 'FLAT'
    END AS outcome_category,
    NULL::text AS next_block_id,  -- Not available in current schema
    NULL::bigint AS next_bar_close_ms  -- Not available in current schema

FROM derived.v_ovc_b_scores_dis_v1_1 s
LEFT JOIN derived.v_ovc_c_outcomes_v0_1 o
    ON s.block_id = o.block_id
    AND s.sym = o.sym;

COMMENT ON VIEW derived.v_path1_evidence_dis_v1_1 IS 
'Path 1 Evidence: DIS-v1.1 score joined with Option C outcomes. Read-only, no transformations.';

-- RES-v1.0 Evidence View
DROP VIEW IF EXISTS derived.v_path1_evidence_res_v1_0;

CREATE VIEW derived.v_path1_evidence_res_v1_0 AS
SELECT
    s.block_id,
    s.sym,
    s.bar_close_ms,
    s.res_score AS res_v1_0_raw,
    CASE 
        WHEN o.fwd_ret_1 > 0 THEN 1
        WHEN o.fwd_ret_1 < 0 THEN -1
        ELSE 0
    END AS outcome_dir,
    NULL::double precision AS outcome_rng,
    o.fwd_ret_1 AS outcome_ret,
    CASE 
        WHEN o.fwd_ret_1 > 0.001 THEN 'UP'
        WHEN o.fwd_ret_1 < -0.001 THEN 'DOWN'
        ELSE 'FLAT'
    END AS outcome_category,
    NULL::text AS next_block_id,
    NULL::bigint AS next_bar_close_ms
FROM derived.v_ovc_b_scores_res_v1_0 s
LEFT JOIN derived.v_ovc_c_outcomes_v0_1 o
    ON s.block_id = o.block_id
    AND s.sym = o.sym;

COMMENT ON VIEW derived.v_path1_evidence_res_v1_0 IS 
'Path 1 Evidence: RES-v1.0 score joined with Option C outcomes. Read-only, no transformations.';

-- LID-v1.0 Evidence View
DROP VIEW IF EXISTS derived.v_path1_evidence_lid_v1_0;

CREATE VIEW derived.v_path1_evidence_lid_v1_0 AS
SELECT
    s.block_id,
    s.sym,
    s.bar_close_ms,
    s.lid_score AS lid_v1_0_raw,
    CASE 
        WHEN o.fwd_ret_1 > 0 THEN 1
        WHEN o.fwd_ret_1 < 0 THEN -1
        ELSE 0
    END AS outcome_dir,
    NULL::double precision AS outcome_rng,
    o.fwd_ret_1 AS outcome_ret,
    CASE 
        WHEN o.fwd_ret_1 > 0.001 THEN 'UP'
        WHEN o.fwd_ret_1 < -0.001 THEN 'DOWN'
        ELSE 'FLAT'
    END AS outcome_category,
    NULL::text AS next_block_id,
    NULL::bigint AS next_bar_close_ms
FROM derived.v_ovc_b_scores_lid_v1_0 s
LEFT JOIN derived.v_ovc_c_outcomes_v0_1 o
    ON s.block_id = o.block_id
    AND s.sym = o.sym;

COMMENT ON VIEW derived.v_path1_evidence_lid_v1_0 IS 
'Path 1 Evidence: LID-v1.0 score joined with Option C outcomes. Read-only, no transformations.';

COMMIT;

-- =============================================================================
-- SMOKE TEST QUERIES
-- =============================================================================
-- 1. Verify views exist:
--    SELECT table_name FROM information_schema.views 
--    WHERE table_schema='derived' AND table_name LIKE 'v_path1_evidence%';
--
-- 2. Verify data:
--    SELECT COUNT(*) FROM derived.v_path1_evidence_dis_v1_1;
--    SELECT COUNT(*) FROM derived.v_path1_evidence_res_v1_0;
--    SELECT COUNT(*) FROM derived.v_path1_evidence_lid_v1_0;
--
-- 3. Sample check:
--    SELECT block_id, sym, dis_v1_1_raw, outcome_ret, outcome_category 
--    FROM derived.v_path1_evidence_dis_v1_1 LIMIT 5;
-- =============================================================================
