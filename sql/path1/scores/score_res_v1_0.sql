-- =============================================================================
-- SCORE: RES-v1.0 — Rotation Efficiency Score
-- =============================================================================
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Descriptive measure of range utilization relative to recent average
-- Formula: RES_raw = (rng / rng_avg_6) × body_ratio
--
-- Source Views (CANONICAL - READ ONLY):
--   - derived.v_ovc_l1_features_v0_1 (rng, body_ratio)
--   - derived.v_ovc_l2_features_v0_1 (rng_avg_6, bar_close_ms)
--
-- DISCLAIMER: This score is NOT predictive. Association with outcomes
--             does NOT imply predictability. NOT a strategy component.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: base_data
-- Join L1 and L2 to get required columns
-- -----------------------------------------------------------------------------
base_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c1.rng,
        c1.body_ratio,
        c2.rng_avg_6
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_raw_score
-- Compute RES raw score with explicit NULL handling
-- Formula: (rng / rng_avg_6) × body_ratio
-- Domain: [0, ∞) theoretically
-- -----------------------------------------------------------------------------
with_raw_score AS (
    SELECT
        block_id,
        sym,
        bar_close_ms,
        
        -- Raw score computation
        CASE
            -- NULL if any input is NULL
            WHEN rng IS NULL THEN NULL
            WHEN rng_avg_6 IS NULL THEN NULL
            WHEN body_ratio IS NULL THEN NULL
            -- NULL if divide by zero
            WHEN rng_avg_6 = 0 THEN NULL
            -- Normal computation
            ELSE (CAST(rng AS DOUBLE PRECISION) / CAST(rng_avg_6 AS DOUBLE PRECISION))
               * CAST(body_ratio AS DOUBLE PRECISION)
        END AS raw_score,
        
        -- Debug columns (prefixed with dbg_)
        rng AS dbg_rng,
        rng_avg_6 AS dbg_rng_avg_6,
        body_ratio AS dbg_body_ratio
        
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
    wrs.dbg_rng,
    wrs.dbg_rng_avg_6,
    wrs.dbg_body_ratio

FROM with_raw_score wrs
LEFT JOIN with_stats ws ON wrs.sym = ws.sym
ORDER BY wrs.sym, wrs.bar_close_ms;

-- =============================================================================
-- VALIDATION NOTES
-- =============================================================================
-- Expected behaviors:
--   1. raw_score >= 0 for all non-NULL values
--   2. raw_score = NULL when rng, rng_avg_6, or body_ratio is NULL
--   3. raw_score = NULL when rng_avg_6 = 0 (divide-by-zero)
--   4. z_score is per-symbol normalized
--   5. Typical bars: raw_score ≈ body_ratio (when rng ≈ rng_avg_6)
--   6. Wide bars with full body: raw_score > 1
--   7. Narrow bars or doji: raw_score < mean
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
