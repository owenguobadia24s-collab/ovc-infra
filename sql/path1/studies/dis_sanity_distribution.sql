-- =============================================================================
-- STUDY: DIS Sanity / Distribution (NO OUTCOMES)
-- =============================================================================
-- Score: DIS-v1.0 — Directional Imbalance Score
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
-- Compute DIS score (inline from score_dis_v1_0.sql)
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c2.date_ny,
        CASE
            WHEN c1.body_ratio IS NULL THEN NULL
            WHEN c1.directional_efficiency IS NULL THEN NULL
            ELSE CAST(c1.body_ratio AS DOUBLE PRECISION) 
               * ABS(CAST(c1.directional_efficiency AS DOUBLE PRECISION))
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
    
    -- Raw score statistics
    ROUND(CAST(MIN(raw_score) AS NUMERIC), 6) AS raw_min,
    ROUND(CAST(MAX(raw_score) AS NUMERIC), 6) AS raw_max,
    ROUND(CAST(AVG(raw_score) AS NUMERIC), 6) AS raw_mean,
    ROUND(CAST(STDDEV_POP(raw_score) AS NUMERIC), 6) AS raw_stddev,
    
    -- Percentiles
    ROUND(CAST(PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p10,
    ROUND(CAST(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p25,
    ROUND(CAST(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p50,
    ROUND(CAST(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p75,
    ROUND(CAST(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS raw_p90

FROM with_zscore
GROUP BY sym
ORDER BY sym;

-- =============================================================================
-- SECTION 2: Z-Score Distribution (Decile Buckets)
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
-- SECTION 3: Raw Score Histogram (Fixed Bins)
-- =============================================================================
-- SELECT
--     '3_RAW_HISTOGRAM' AS section,
--     sym,
--     CASE
--         WHEN raw_score IS NULL THEN 'NULL'
--         WHEN raw_score < 0.1 THEN '[0.0, 0.1)'
--         WHEN raw_score < 0.2 THEN '[0.1, 0.2)'
--         WHEN raw_score < 0.3 THEN '[0.2, 0.3)'
--         WHEN raw_score < 0.4 THEN '[0.3, 0.4)'
--         WHEN raw_score < 0.5 THEN '[0.4, 0.5)'
--         WHEN raw_score < 0.6 THEN '[0.5, 0.6)'
--         WHEN raw_score < 0.7 THEN '[0.6, 0.7)'
--         WHEN raw_score < 0.8 THEN '[0.7, 0.8)'
--         WHEN raw_score < 0.9 THEN '[0.8, 0.9)'
--         ELSE '[0.9, 1.0]'
--     END AS raw_bucket,
--     COUNT(*) AS n,
--     ROUND(CAST(COUNT(*) AS NUMERIC) / SUM(COUNT(*)) OVER (PARTITION BY sym) * 100, 2) AS pct
-- FROM with_zscore
-- GROUP BY sym, raw_bucket
-- ORDER BY sym, raw_bucket;

-- =============================================================================
-- SECTION 4: Extreme Values Sample (for manual inspection)
-- =============================================================================
-- SELECT
--     '4_EXTREMES' AS section,
--     block_id,
--     sym,
--     date_ny,
--     raw_score,
--     z_score,
--     'LOW' AS extreme_type
-- FROM with_zscore
-- WHERE z_score IS NOT NULL
-- ORDER BY z_score ASC
-- LIMIT 10
-- 
-- UNION ALL
-- 
-- SELECT
--     '4_EXTREMES' AS section,
--     block_id,
--     sym,
--     date_ny,
--     raw_score,
--     z_score,
--     'HIGH' AS extreme_type
-- FROM with_zscore
-- WHERE z_score IS NOT NULL
-- ORDER BY z_score DESC
-- LIMIT 10;
