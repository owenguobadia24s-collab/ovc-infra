-- =============================================================================
-- STUDY: DIS vs Outcomes (Bucketed, Descriptive)
-- =============================================================================
-- Score: DIS-v1.1 — Directional Imbalance Score
-- Status: NON-CANONICAL (Path 1 Research)
-- Created: 2026-01-20
-- Updated: 2026-01-20 (v1.1 removes non-canonical dependency on directional_efficiency)
--
-- Purpose: Descriptive association between DIS z-score buckets and outcomes
--
-- DISCLAIMER: This is a descriptive study only. Association ≠ predictability.
--             NOT a strategy. NOT actionable.
-- =============================================================================

WITH
-- -----------------------------------------------------------------------------
-- CTE: score_data
-- Compute DIS score with z-score normalization
-- -----------------------------------------------------------------------------
score_data AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.bar_close_ms,
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
            WHEN z_score < -2.0 THEN 1   -- Extreme low
            WHEN z_score < -1.5 THEN 2
            WHEN z_score < -1.0 THEN 3
            WHEN z_score < -0.5 THEN 4
            WHEN z_score < 0.0 THEN 5
            WHEN z_score < 0.5 THEN 6
            WHEN z_score < 1.0 THEN 7
            WHEN z_score < 1.5 THEN 8
            WHEN z_score < 2.0 THEN 9
            ELSE 10                       -- Extreme high
        END AS z_bucket
    FROM with_zscore wz
),

-- -----------------------------------------------------------------------------
-- CTE: joined_outcomes
-- Join with canonical outcomes (ONLY view allowed for outcome data)
-- -----------------------------------------------------------------------------
joined_outcomes AS (
    SELECT
        wb.block_id,
        wb.sym,
        wb.bar_close_ms,
        wb.raw_score,
        wb.z_score,
        wb.z_bucket,
        
        -- Outcome columns from canonical view
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
    
    -- Sample size
    COUNT(*) AS n,
    
    -- Forward returns (mean and median)
    ROUND(CAST(AVG(fwd_ret_1) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_1_bps,
    ROUND(CAST(AVG(fwd_ret_3) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_3_bps,
    ROUND(CAST(AVG(fwd_ret_6) AS NUMERIC) * 10000, 4) AS mean_fwd_ret_6_bps,
    
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_1) AS NUMERIC) * 10000, 4) AS med_fwd_ret_1_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_3) AS NUMERIC) * 10000, 4) AS med_fwd_ret_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fwd_ret_6) AS NUMERIC) * 10000, 4) AS med_fwd_ret_6_bps,
    
    -- MFE (mean and median)
    ROUND(CAST(AVG(mfe_3) AS NUMERIC) * 10000, 4) AS mean_mfe_3_bps,
    ROUND(CAST(AVG(mfe_6) AS NUMERIC) * 10000, 4) AS mean_mfe_6_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mfe_3) AS NUMERIC) * 10000, 4) AS med_mfe_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mfe_6) AS NUMERIC) * 10000, 4) AS med_mfe_6_bps,
    
    -- MAE (mean and median)
    ROUND(CAST(AVG(mae_3) AS NUMERIC) * 10000, 4) AS mean_mae_3_bps,
    ROUND(CAST(AVG(mae_6) AS NUMERIC) * 10000, 4) AS mean_mae_6_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mae_3) AS NUMERIC) * 10000, 4) AS med_mae_3_bps,
    ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mae_6) AS NUMERIC) * 10000, 4) AS med_mae_6_bps,
    
    -- Realized volatility (mean)
    ROUND(CAST(AVG(rvol_6) AS NUMERIC) * 10000, 4) AS mean_rvol_6_bps

FROM joined_outcomes
WHERE z_bucket IS NOT NULL
GROUP BY sym, z_bucket
ORDER BY sym, z_bucket;

-- =============================================================================
-- NOTES
-- =============================================================================
-- Output columns (all returns/excursions in basis points):
--   sym            : Instrument symbol
--   z_bucket       : Z-score bucket (1-10, 1=low, 10=high)
--   n              : Sample size in bucket
--   mean_fwd_ret_* : Mean forward return at horizon 1/3/6 bars
--   med_fwd_ret_*  : Median forward return at horizon 1/3/6 bars
--   mean_mfe_*     : Mean maximum favorable excursion
--   med_mfe_*      : Median maximum favorable excursion
--   mean_mae_*     : Mean maximum adverse excursion
--   med_mae_*      : Median maximum adverse excursion
--   mean_rvol_6    : Mean realized volatility (6-bar)
--
-- DISCLAIMER: Any patterns observed are DESCRIPTIVE ONLY.
--             Association does NOT imply predictability.
--             This is NOT a trading strategy.
-- =============================================================================
