-- =============================================================================
-- DB PATCH: Create Path 1 Score Views
-- =============================================================================
-- The score SQL files (score_dis_v1_1.sql, etc.) produce SELECT outputs but
-- do not create persistent views. The evidence views expect:
--   - derived.v_ovc_b_scores_dis_v1_1
--   - derived.v_ovc_b_scores_res_v1_0
--   - derived.v_ovc_b_scores_lid_v1_0
--
-- This patch creates these views with the correct definitions.
-- Created: 2026-01-20
-- =============================================================================

BEGIN;

-- Ensure derived schema exists
CREATE SCHEMA IF NOT EXISTS derived;

-- =============================================================================
-- DIS-v1.1 Score View
-- =============================================================================
DROP VIEW IF EXISTS derived.v_ovc_b_scores_dis_v1_1;

CREATE VIEW derived.v_ovc_b_scores_dis_v1_1 AS
WITH base_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c1.body_ratio
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),
with_raw_score AS (
    SELECT
        block_id,
        sym,
        bar_close_ms,
        CASE
            WHEN body_ratio IS NULL THEN NULL
            ELSE CAST(body_ratio AS DOUBLE PRECISION)
        END AS dis_score
    FROM base_data
)
SELECT
    block_id,
    sym,
    bar_close_ms,
    dis_score
FROM with_raw_score;

COMMENT ON VIEW derived.v_ovc_b_scores_dis_v1_1 IS 
'Path 1 Score: DIS-v1.1 (Displacement). Raw score = body_ratio. FROZEN.';

-- =============================================================================
-- RES-v1.0 Score View
-- =============================================================================
DROP VIEW IF EXISTS derived.v_ovc_b_scores_res_v1_0;

CREATE VIEW derived.v_ovc_b_scores_res_v1_0 AS
WITH base_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c1.body_ratio,
        c1.rng AS l1_rng
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),
with_stats AS (
    SELECT
        sym,
        AVG(l1_rng) AS mean_rng,
        STDDEV_POP(l1_rng) AS stddev_rng
    FROM base_data
    WHERE l1_rng IS NOT NULL
    GROUP BY sym
),
with_raw_score AS (
    SELECT
        bd.block_id,
        bd.sym,
        bd.bar_close_ms,
        CASE
            WHEN bd.l1_rng IS NULL THEN NULL
            WHEN ws.mean_rng IS NULL OR ws.mean_rng = 0 THEN NULL
            ELSE bd.l1_rng / ws.mean_rng
        END AS res_score
    FROM base_data bd
    LEFT JOIN with_stats ws ON bd.sym = ws.sym
)
SELECT
    block_id,
    sym,
    bar_close_ms,
    res_score
FROM with_raw_score;

COMMENT ON VIEW derived.v_ovc_b_scores_res_v1_0 IS 
'Path 1 Score: RES-v1.0 (Range Expansion). Raw score = range / mean_range per symbol. FROZEN.';

-- =============================================================================
-- LID-v1.0 Score View  
-- =============================================================================
DROP VIEW IF EXISTS derived.v_ovc_b_scores_lid_v1_0;

CREATE VIEW derived.v_ovc_b_scores_lid_v1_0 AS
WITH base_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c1.upper_wick_ratio,
        c1.lower_wick_ratio
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),
with_raw_score AS (
    SELECT
        block_id,
        sym,
        bar_close_ms,
        CASE
            WHEN upper_wick_ratio IS NULL OR lower_wick_ratio IS NULL THEN NULL
            WHEN (upper_wick_ratio + lower_wick_ratio) = 0 THEN NULL
            ELSE ABS(upper_wick_ratio - lower_wick_ratio) / (upper_wick_ratio + lower_wick_ratio)
        END AS lid_score
    FROM base_data
)
SELECT
    block_id,
    sym,
    bar_close_ms,
    lid_score
FROM with_raw_score;

COMMENT ON VIEW derived.v_ovc_b_scores_lid_v1_0 IS 
'Path 1 Score: LID-v1.0 (Wick Imbalance). Raw score = |upper_wick - lower_wick| / (upper + lower). FROZEN.';

COMMIT;

-- =============================================================================
-- SMOKE TEST QUERIES
-- =============================================================================
-- 1. Verify views exist:
--    SELECT table_name FROM information_schema.views 
--    WHERE table_schema='derived' AND table_name LIKE 'v_ovc_b_scores%';
--
-- 2. Verify data:
--    SELECT COUNT(*), AVG(dis_score) FROM derived.v_ovc_b_scores_dis_v1_1;
--    SELECT COUNT(*), AVG(res_score) FROM derived.v_ovc_b_scores_res_v1_0;
--    SELECT COUNT(*), AVG(lid_score) FROM derived.v_ovc_b_scores_lid_v1_0;
--
-- 3. Sample check:
--    SELECT * FROM derived.v_ovc_b_scores_dis_v1_1 LIMIT 5;
-- =============================================================================
