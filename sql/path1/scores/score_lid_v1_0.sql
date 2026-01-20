-- =============================================================================
-- SCORE: LID-v1.0 — Liquidity Interaction Density
-- =============================================================================
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Descriptive measure of wick activity relative to body
-- Formula: LID_raw = (upper_wick_ratio + lower_wick_ratio) / body_ratio
--
-- Source Views (CANONICAL - READ ONLY):
--   - derived.v_ovc_c1_features_v0_1 (upper_wick_ratio, lower_wick_ratio, body_ratio)
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
        c1.upper_wick_ratio,
        c1.lower_wick_ratio,
        c1.body_ratio
    FROM derived.v_ovc_c1_features_v0_1 c1
    INNER JOIN derived.v_ovc_c2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_raw_score
-- Compute LID raw score with explicit NULL handling
-- Formula: (upper_wick_ratio + lower_wick_ratio) / body_ratio
-- Domain: [0, ∞)
-- -----------------------------------------------------------------------------
with_raw_score AS (
    SELECT
        block_id,
        sym,
        bar_close_ms,
        
        -- Raw score computation
        CASE
            -- NULL if any input is NULL
            WHEN upper_wick_ratio IS NULL THEN NULL
            WHEN lower_wick_ratio IS NULL THEN NULL
            WHEN body_ratio IS NULL THEN NULL
            -- NULL if divide by zero (doji or zero-body bar)
            WHEN body_ratio = 0 THEN NULL
            -- Normal computation
            ELSE (CAST(upper_wick_ratio AS DOUBLE PRECISION) 
                + CAST(lower_wick_ratio AS DOUBLE PRECISION))
               / CAST(body_ratio AS DOUBLE PRECISION)
        END AS raw_score,
        
        -- Debug columns (prefixed with dbg_)
        upper_wick_ratio AS dbg_upper_wick,
        lower_wick_ratio AS dbg_lower_wick,
        body_ratio AS dbg_body_ratio,
        -- Total wick ratio for verification
        CASE
            WHEN upper_wick_ratio IS NULL OR lower_wick_ratio IS NULL THEN NULL
            ELSE upper_wick_ratio + lower_wick_ratio
        END AS dbg_total_wick
        
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
    wrs.dbg_upper_wick,
    wrs.dbg_lower_wick,
    wrs.dbg_body_ratio,
    wrs.dbg_total_wick

FROM with_raw_score wrs
LEFT JOIN with_stats ws ON wrs.sym = ws.sym
ORDER BY wrs.sym, wrs.bar_close_ms;

-- =============================================================================
-- VALIDATION NOTES
-- =============================================================================
-- Expected behaviors:
--   1. raw_score >= 0 for all non-NULL values
--   2. raw_score = NULL when any wick ratio or body_ratio is NULL
--   3. raw_score = NULL when body_ratio = 0 (divide-by-zero)
--   4. z_score is per-symbol normalized
--   5. Pure body bars (no wicks): raw_score = 0
--   6. Equal wick and body: raw_score = 1 (when total_wick = body_ratio)
--   7. Doji-like bars: raw_score → ∞ (but NULL due to body_ratio ≈ 0)
--
-- Mathematical identity check:
--   upper_wick_ratio + lower_wick_ratio + body_ratio = 1 (by C1 construction)
--   Therefore: LID = (1 - body_ratio) / body_ratio when body_ratio > 0
--
-- Sample validation query:
-- SELECT sym, 
--        MIN(raw_score), MAX(raw_score), AVG(raw_score),
--        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY raw_score) AS median,
--        COUNT(*) AS n_total, 
--        COUNT(raw_score) AS n_valid,
--        COUNT(*) - COUNT(raw_score) AS n_null
-- FROM (<this query>) t
-- GROUP BY sym;
-- =============================================================================
