-- =============================================================================
-- STUDY: RES vs Outcomes (Bucketed, Descriptive)
-- =============================================================================
-- Score: RES-v1.0 — Rotation Efficiency Score
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
--
-- Purpose: Descriptive association between RES z-score buckets and outcomes
--
-- DISCLAIMER: This is a descriptive study only. Association ≠ predictability.
--             NOT a strategy. NOT actionable.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: score_data
-- Compute RES score with z-score normalization
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
        CASE
            WHEN c1.rng IS NULL THEN NULL
            WHEN c2.rng_avg_6 IS NULL THEN NULL
            WHEN c1.body_ratio IS NULL THEN NULL
            WHEN c2.rng_avg_6 = 0 THEN NULL
            ELSE (CAST(c1.rng AS DOUBLE PRECISION) / CAST(c2.rng_avg_6 AS DOUBLE PRECISION))
               * CAST(c1.body_ratio AS DOUBLE PRECISION)
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
),

-- -----------------------------------------------------------------------------
-- CTE: with_buckets
-- Assign fixed z-score decile buckets
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
),

-- -----------------------------------------------------------------------------
-- CTE: joined_outcomes
-- Join with canonical outcomes
-- -----------------------------------------------------------------------------
joined_outcomes AS (
    SELECT
        wb.block_id,
        wb.sym,
        wb.bar_close_ms,
        wb.raw_score,
        wb.z_score,
        wb.z_bucket,
        oc.fwd_ret_1,
        oc.fwd_ret_3,
        oc.fwd_ret_6,
        oc.mfe_3,
        oc.mfe_6,
        oc.mae_3,
        oc.mae_6,
        oc.rvol_6
    FROM with_buckets wb
    INNER JOIN derived.v_ovc_c_outcomes_v0_1 oc
        ON wb.block_id = oc.block_id
)

-- =============================================================================
-- FINAL: Outcome Association by Z-Score Bucket
-- =============================================================================
SELECT
    sym,
    z_bucket,
    COUNT(*) AS n,
    
    ROUND(CAST(AVG(fwd_ret_1) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_1_bps,
    ROUND(CAST(AVG(fwd_ret_3) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_3_bps,
    ROUND(CAST(AVG(fwd_ret_6) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_6_bps,
    
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_1) AS NUMERIC) * 10000, 4) AS med_fwd_ret_1_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_3) AS NUMERIC) * 10000, 4) AS med_fwd_ret_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_6) AS NUMERIC) * 10000, 4) AS med_fwd_ret_6_bps,
    
    ROUND(CAST(AVG(mfe_3) AS NUMERIC) * 10000, 4) AS mean_mfe_3_bps,
    ROUND(CAST(AVG(mfe_6) AS NUMERIC) * 10000, 4) AS mean_mfe_6_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mfe_3) AS NUMERIC) * 10000, 4) AS med_mfe_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mfe_6) AS NUMERIC) * 10000, 4) AS med_mfe_6_bps,
    
    ROUND(CAST(AVG(mae_3) AS NUMERIC) * 10000, 4) AS mean_mae_3_bps,
    ROUND(CAST(AVG(mae_6) AS NUMERIC) * 10000, 4) AS mean_mae_6_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mae_3) AS NUMERIC) * 10000, 4) AS med_mae_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mae_6) AS NUMERIC) * 10000, 4) AS med_mae_6_bps,
    
    ROUND(CAST(AVG(rvol_6) AS NUMERIC) * 10000, 4) AS mean_rvol_6_bps

FROM joined_outcomes
WHERE z_bucket IS NOT NULL
GROUP BY sym, z_bucket
ORDER BY sym, z_bucket;

-- =============================================================================
-- DISCLAIMER: Any patterns observed are DESCRIPTIVE ONLY.
--             Association does NOT imply predictability.
--             This is NOT a trading strategy.
-- =============================================================================
