-- =============================================================================
-- STUDY: LID Sanity / Distribution (NO OUTCOMES)
-- =============================================================================
-- Score: LID-v1.0 — Liquidity Interaction Density
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Validate score distribution and coverage without outcome data
--
-- DISCLAIMER: This is a descriptive study only. NOT predictive.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: score_data
-- Compute LID score (inline from score_lid_v1_0.sql)
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c2.date_ny,
        CASE
            WHEN c1.upper_wick_ratio IS NULL THEN NULL
            WHEN c1.lower_wick_ratio IS NULL THEN NULL
            WHEN c1.body_ratio IS NULL THEN NULL
            WHEN c1.body_ratio = 0 THEN NULL
            ELSE (CAST(c1.upper_wick_ratio AS DOUBLE PRECISION) 
                + CAST(c1.lower_wick_ratio AS DOUBLE PRECISION))
               / CAST(c1.body_ratio AS DOUBLE PRECISION)
        END AS raw_score
    FROM derived.v_ovc_c1_features_v0_1 c1
    INNER JOIN derived.v_ovc_c2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_zscore
-- Add per-symbol z-score
-- -----------------------------------------------------------------------------
with_zscore AS (
    SELECT
        sd.*,
        (raw_score - AVG(raw_score) OVER (PARTITION BY sym)) 
            / NULLIF(STDDEV_POP(raw_score) OVER (PARTITION BY sym), 0) AS z_score
    FROM score_data sd
)

-- =============================================================================
-- SECTION 1: Overall Statistics by Symbol
-- =============================================================================
SELECT
    '1_OVERALL_STATS' AS section,
    sym,
    COUNT(*) AS n_total,
    COUNT(raw_score) AS n_valid,
    COUNT(*) - COUNT(raw_score) AS n_null,
    ROUND(CAST(COUNT(raw_score) AS NUMERIC) / COUNT(*) * 100, 2) AS pct_valid,
    
    -- Raw score statistics (note: LID can be unbounded, so check max)
    ROUND(CAST(MIN(raw_score) AS NUMERIC), 6) AS raw_min,
    ROUND(CAST(MAX(raw_score) AS NUMERIC), 6) AS raw_max,
    ROUND(CAST(AVG(raw_score) AS NUMERIC), 6) AS raw_mean,
    ROUND(CAST(STDDEV_POP(raw_score) AS NUMERIC), 6) AS raw_stddev,
    
    -- Percentiles (note asymmetric distribution expected)
    ROUND(CAST(PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p10,
    ROUND(CAST(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p25,
    ROUND(CAST(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p50,
    ROUND(CAST(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p75,
    ROUND(CAST(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p90,
    ROUND(CAST(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p95,
    ROUND(CAST(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p99

FROM with_zscore
GROUP BY sym
ORDER BY sym;

-- =============================================================================
-- SECTION 2: Z-Score Distribution (uncomment to run)
-- =============================================================================
-- SELECT
--     '2_ZSCORE_DISTRIBUTION' AS section,
--     sym,
--     CASE
--         WHEN z_score IS NULL THEN 'NULL'
--         WHEN z_score < -2.0 THEN 'z<-2'
--         WHEN z_score < -1.5 THEN '-2≤z<-1.5'
--         WHEN z_score < -1.0 THEN '-1.5≤z<-1'
--         WHEN z_score < -0.5 THEN '-1≤z<-0.5'
--         WHEN z_score < 0.0 THEN '-0.5≤z<0'
--         WHEN z_score < 0.5 THEN '0≤z<0.5'
--         WHEN z_score < 1.0 THEN '0.5≤z<1'
--         WHEN z_score < 1.5 THEN '1≤z<1.5'
--         WHEN z_score < 2.0 THEN '1.5≤z<2'
--         ELSE 'z≥2'
--     END AS z_bucket,
--     COUNT(*) AS n,
--     ROUND(CAST(COUNT(*) AS NUMERIC) / SUM(COUNT(*)) OVER (PARTITION BY sym) * 100, 2) AS pct
-- FROM with_zscore
-- GROUP BY sym, z_bucket
-- ORDER BY sym, z_bucket;

-- =============================================================================
-- NOTE: LID has an asymmetric distribution with right tail
--       (approaches infinity as body_ratio → 0)
--       Expect higher null rate due to body_ratio = 0 exclusion
-- =============================================================================
