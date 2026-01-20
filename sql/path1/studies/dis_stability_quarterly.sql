-- =============================================================================
-- STUDY: DIS Temporal Stability (Quarterly)
-- =============================================================================
-- Score: DIS-v1.1 — Directional Imbalance Score
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
-- Updated: 2026-01-20 (v1.1 removes non-canonical dependency on directional_efficiency)
--
-- Purpose: Assess score distribution stability across fixed quarterly periods
--
-- DISCLAIMER: This is a descriptive study only. NOT predictive.
--             No refitting or re-bucketing applied.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: score_data
-- Compute DIS score with z-score and quarter assignment
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c2.date_ny,
        -- Extract quarter from date_ny (format: YYYYMMDD)
        SUBSTRING(c2.date_ny::TEXT FROM 1 FOR 4) || '-Q' ||
            CASE 
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 3 THEN '1'
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 6 THEN '2'
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 9 THEN '3'
                ELSE '4'
            END AS quarter,
        CASE
            WHEN c1.body_ratio IS NULL THEN NULL
            ELSE CAST(c1.body_ratio AS DOUBLE PRECISION)
        END AS raw_score
    FROM derived.v_ovc_c1_features_v0_1 c1
    INNER JOIN derived.v_ovc_c2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_zscore
-- Add per-symbol z-score (computed over ALL data, not per-quarter)
-- This ensures buckets are stable across time
-- -----------------------------------------------------------------------------
with_zscore AS (
    SELECT
        sd.*,
        (raw_score - AVG(raw_score) OVER (PARTITION BY sym)) 
            / NULLIF(STDDEV_POP(raw_score) OVER (PARTITION BY sym), 0) AS z_score
    FROM score_data sd
),

-- -----------------------------------------------------------------------------
-- CTE: with_buckets
-- Assign fixed z-score buckets (same buckets used across all quarters)
-- -----------------------------------------------------------------------------
with_buckets AS (
    SELECT
        wz.*,
        CASE
            WHEN z_score IS NULL THEN NULL
            WHEN z_score < -2.0 THEN 1
            WHEN z_score < -1.5 THEN 2
            WHEN z_score < -1.0 THEN 3
            WHEN z_score < -0.5 THEN 4
            WHEN z_score < 0.0 THEN 5
            WHEN z_score < 0.5 THEN 6
            WHEN z_score < 1.0 THEN 7
            WHEN z_score < 1.5 THEN 8
            WHEN z_score < 2.0 THEN 9
            ELSE 10
        END AS z_bucket
    FROM with_zscore wz
)

-- =============================================================================
-- FINAL: Bucket Distribution by Quarter
-- =============================================================================
SELECT
    sym,
    quarter,
    z_bucket,
    
    -- Count and percentage
    COUNT(*) AS n,
    ROUND(CAST(COUNT(*) AS NUMERIC) / SUM(COUNT(*)) OVER (PARTITION BY sym, quarter) * 100, 2) AS pct_of_quarter,
    
    -- Raw score statistics within bucket
    ROUND(CAST(AVG(raw_score) AS NUMERIC), 6) AS mean_raw,
    ROUND(CAST(STDDEV_POP(raw_score) AS NUMERIC), 6) AS stddev_raw,
    
    -- Z-score statistics (should be stable if normalization is consistent)
    ROUND(CAST(AVG(z_score) AS NUMERIC), 4) AS mean_z,
    ROUND(CAST(STDDEV_POP(z_score) AS NUMERIC), 4) AS stddev_z

FROM with_buckets
WHERE z_bucket IS NOT NULL
GROUP BY sym, quarter, z_bucket
ORDER BY sym, quarter, z_bucket;

-- =============================================================================
-- ALTERNATIVE: Summary Statistics per Quarter (uncomment to use)
-- =============================================================================
-- SELECT
--     sym,
--     quarter,
--     COUNT(*) AS n_total,
--     COUNT(raw_score) AS n_valid,
--     ROUND(CAST(AVG(raw_score) AS NUMERIC), 6) AS mean_raw,
--     ROUND(CAST(STDDEV_POP(raw_score) AS NUMERIC), 6) AS stddev_raw,
--     ROUND(CAST(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS p25,
--     ROUND(CAST(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS p50,
--     ROUND(CAST(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY raw_score) AS NUMERIC), 6) AS p75
-- FROM score_data
-- GROUP BY sym, quarter
-- ORDER BY sym, quarter;

-- =============================================================================
-- NOTES
-- =============================================================================
-- Stability indicators:
--   1. pct_of_quarter should be similar across quarters for same bucket
--   2. mean_z should be consistent within bucket across quarters
--   3. Large changes in distribution may indicate regime shifts (descriptive only)
--
-- IMPORTANT: Z-score normalization uses FULL history, not per-quarter.
--            This ensures bucket definitions are fixed and comparable.
--            No refitting is performed.
--
-- DISCLAIMER: Any temporal patterns are DESCRIPTIVE ONLY.
--             This is NOT a trading strategy.
-- =============================================================================
