-- =============================================================================
-- STUDY: LID Temporal Stability (Quarterly)
-- =============================================================================
-- Score: LID-v1.0 — Liquidity Interaction Density
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Assess score distribution stability across fixed quarterly periods
--
-- DISCLAIMER: This is a descriptive study only. NOT predictive.
--             No refitting or re-bucketing applied.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: score_data
-- Compute LID score with quarter assignment
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        c2.date_ny,
        SUBSTRING(c2.date_ny::TEXT FROM 1 FOR 4) || '-Q' ||
            CASE 
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 3 THEN '1'
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 6 THEN '2'
                WHEN SUBSTRING(c2.date_ny::TEXT FROM 5 FOR 2)::INT <= 9 THEN '3'
                ELSE '4'
            END AS quarter,
        CASE
            WHEN c1.upper_wick_ratio IS NULL THEN NULL
            WHEN c1.lower_wick_ratio IS NULL THEN NULL
            WHEN c1.body_ratio IS NULL THEN NULL
            WHEN c1.body_ratio = 0 THEN NULL
            ELSE (CAST(c1.upper_wick_ratio AS DOUBLE PRECISION) 
                + CAST(c1.lower_wick_ratio AS DOUBLE PRECISION))
               / CAST(c1.body_ratio AS DOUBLE PRECISION)
        END AS raw_score
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    WHERE c1.block_id IS NOT NULL
),

-- -----------------------------------------------------------------------------
-- CTE: with_zscore
-- Add per-symbol z-score (computed over ALL data, not per-quarter)
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
-- Assign fixed z-score buckets
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
    COUNT(*) AS n,
    ROUND(CAST(COUNT(*) AS NUMERIC) / SUM(COUNT(*)) OVER (PARTITION BY sym, quarter) * 100, 2) AS pct_of_quarter,
    ROUND(CAST(AVG(raw_score) AS NUMERIC), 6) AS mean_raw,
    ROUND(CAST(STDDEV_POP(raw_score) AS NUMERIC), 6) AS stddev_raw,
    ROUND(CAST(AVG(z_score) AS NUMERIC), 4) AS mean_z,
    ROUND(CAST(STDDEV_POP(z_score) AS NUMERIC), 4) AS stddev_z

FROM with_buckets
WHERE z_bucket IS NOT NULL
GROUP BY sym, quarter, z_bucket
ORDER BY sym, quarter, z_bucket;

-- =============================================================================
-- DISCLAIMER: Any temporal patterns are DESCRIPTIVE ONLY.
--             This is NOT a trading strategy.
-- =============================================================================
