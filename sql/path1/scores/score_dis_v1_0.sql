-- =============================================================================
-- SCORE: DIS-v1.0 — Directional Imbalance Score
-- =============================================================================
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Descriptive measure of directional commitment within a bar
-- Formula: DIS_raw = body_ratio × |directional_efficiency|
--
-- Source Views (CANONICAL - READ ONLY):
--   - derived.v_ovc_c1_features_v0_1 (body_ratio, directional_efficiency)
--   - derived.v_ovc_c2_features_v0_1 (bar_close_ms for ordering)
--
-- DISCLAIMER: This score is NOT predictive. Association with outcomes
--             does NOT imply predictability. NOT a strategy component.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: base_data
-- Join C1 and C2 to get required columns
-- -----------------------------------------------------------------------------
base_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c1.body_ratio,
        c1.directional_efficiency
    FROM derived.v_ovc_c1_features_v0_1 c1
    INNER JOIN derived.v_ovc_c2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_raw_score
-- Compute DIS raw score with explicit NULL handling
-- Formula: body_ratio × |directional_efficiency|
-- Domain: [0, 1]
-- -----------------------------------------------------------------------------
with_raw_score AS (
    SELECT
        block_id,
        sym,
        bar_close_ms,
        
        -- Raw score computation
        CASE
            -- NULL if any input is NULL
            WHEN body_ratio IS NULL THEN NULL
            WHEN directional_efficiency IS NULL THEN NULL
            -- Normal computation
            ELSE CAST(body_ratio AS DOUBLE PRECISION) 
               * ABS(CAST(directional_efficiency AS DOUBLE PRECISION))
        END AS raw_score,
        
        -- Debug columns (prefixed with dbg_)
        body_ratio AS dbg_body_ratio,
        directional_efficiency AS dbg_dir_eff
        
    FROM base_data
),

-- -----------------------------------------------------------------------------
-- CTE: with_stats
-- Compute per-symbol statistics for z-score normalization
-- -----------------------------------------------------------------------------
with_stats AS (
    SELECT
        sym,
        AVG(raw_score) AS mean_score,
        STDDEV_POP(raw_score) AS stddev_score
    FROM with_raw_score
    WHERE raw_score IS NOT NULL
    GROUP BY sym
)

-- -----------------------------------------------------------------------------
-- FINAL SELECT: Output tidy result set with z-score
-- -----------------------------------------------------------------------------
SELECT
    wrs.block_id,
    wrs.sym,
    wrs.bar_close_ms,
    wrs.raw_score,
    
    -- Z-score: (raw - mean) / stddev, per symbol
    CASE
        WHEN wrs.raw_score IS NULL THEN NULL
        WHEN ws.stddev_score IS NULL THEN NULL
        WHEN ws.stddev_score = 0 THEN NULL
        ELSE (wrs.raw_score - ws.mean_score) / ws.stddev_score
    END AS z_score,
    
    -- Debug columns (optional, for validation)
    wrs.dbg_body_ratio,
    wrs.dbg_dir_eff

FROM with_raw_score wrs
LEFT JOIN with_stats ws ON wrs.sym = ws.sym
ORDER BY wrs.sym, wrs.bar_close_ms;

-- =============================================================================
-- VALIDATION NOTES
-- =============================================================================
-- Expected behaviors:
--   1. raw_score ∈ [0, 1] for all non-NULL values
--   2. raw_score = NULL when body_ratio or directional_efficiency is NULL
--   3. z_score is per-symbol normalized (mean ≈ 0, stddev ≈ 1 per sym)
--   4. Pure body bars (no wicks): raw_score = body_ratio² = 1
--   5. Doji bars (tiny body): raw_score ≈ 0
--
-- Sample validation query:
-- SELECT sym, 
--        MIN(raw_score), MAX(raw_score), AVG(raw_score),
--        COUNT(*) AS n_total, 
--        COUNT(raw_score) AS n_valid,
--        COUNT(*) - COUNT(raw_score) AS n_null
-- FROM (<this query>) t
-- GROUP BY sym;
-- =============================================================================
