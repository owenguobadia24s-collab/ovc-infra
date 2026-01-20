-- =============================================================================
-- Study: DIS-v1.1 Distributional Analysis
-- Purpose: Compute distributional summaries for DIS-v1.1 score and outcomes
-- Governance: Aggregational only. No thresholds. No trading logic.
-- =============================================================================

-- FROZEN SCORE VERSION: DIS-v1.1
-- SOURCE VIEW: derived.v_path1_evidence_dis_v1_1

-- -----------------------------------------------------------------------------
-- Study 1: Overall DIS-v1.1 Score Distribution
-- -----------------------------------------------------------------------------
-- Computes basic distributional statistics for the DIS score across all data.

SELECT
    'DIS-v1.1' AS score_version,
    COUNT(*) AS n_observations,
    AVG(dis_v1_1_raw) AS mean_score,
    STDDEV(dis_v1_1_raw) AS stddev_score,
    MIN(dis_v1_1_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p75_score,
    MAX(dis_v1_1_raw) AS max_score
FROM derived.v_path1_evidence_dis_v1_1
WHERE dis_v1_1_raw IS NOT NULL;


-- -----------------------------------------------------------------------------
-- Study 2: DIS-v1.1 Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
-- Shows how DIS score values are distributed within each outcome category.
-- Observation only: describes co-occurrence, not causation.

SELECT
    outcome_category,
    COUNT(*) AS n_observations,
    AVG(dis_v1_1_raw) AS mean_score,
    STDDEV(dis_v1_1_raw) AS stddev_score,
    MIN(dis_v1_1_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY dis_v1_1_raw) AS p75_score,
    MAX(dis_v1_1_raw) AS max_score
FROM derived.v_path1_evidence_dis_v1_1
WHERE dis_v1_1_raw IS NOT NULL
  AND outcome_category IS NOT NULL
GROUP BY outcome_category
ORDER BY outcome_category;


-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on DIS-v1.1 Score Quantiles
-- -----------------------------------------------------------------------------
-- Divides DIS scores into quantiles and counts outcome categories within each.
-- Uses data-driven quantiles (no fixed thresholds).

WITH score_quantiles AS (
    SELECT
        block_id,
        sym,
        dis_v1_1_raw,
        outcome_category,
        NTILE(4) OVER (ORDER BY dis_v1_1_raw) AS score_quartile
    FROM derived.v_path1_evidence_dis_v1_1
    WHERE dis_v1_1_raw IS NOT NULL
      AND outcome_category IS NOT NULL
)
SELECT
    score_quartile,
    outcome_category,
    COUNT(*) AS n_observations,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY score_quartile), 2) AS pct_within_quartile
FROM score_quantiles
GROUP BY score_quartile, outcome_category
ORDER BY score_quartile, outcome_category;


-- -----------------------------------------------------------------------------
-- Study 4: Outcome Value Statistics by DIS-v1.1 Score Quantile
-- -----------------------------------------------------------------------------
-- Computes outcome_ret summary statistics within each score quantile.
-- Observation only: describes what occurred, not what will occur.

WITH score_quantiles AS (
    SELECT
        dis_v1_1_raw,
        outcome_ret,
        NTILE(4) OVER (ORDER BY dis_v1_1_raw) AS score_quartile
    FROM derived.v_path1_evidence_dis_v1_1
    WHERE dis_v1_1_raw IS NOT NULL
      AND outcome_ret IS NOT NULL
)
SELECT
    score_quartile,
    COUNT(*) AS n_observations,
    AVG(outcome_ret) AS mean_outcome_ret,
    STDDEV(outcome_ret) AS stddev_outcome_ret,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY outcome_ret) AS median_outcome_ret
FROM score_quantiles
GROUP BY score_quartile
ORDER BY score_quartile;


-- =============================================================================
-- GOVERNANCE NOTES:
-- - All queries are purely aggregational (COUNT, AVG, PERCENTILE, STDDEV)
-- - No if/else trading logic
-- - No fixed thresholds (quantiles are data-driven)
-- - Results describe co-occurrence patterns only
-- =============================================================================
