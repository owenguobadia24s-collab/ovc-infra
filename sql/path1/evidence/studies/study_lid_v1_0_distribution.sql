-- =============================================================================
-- Study: LID-v1.0 Distributional Analysis
-- Purpose: Compute distributional summaries for LID-v1.0 score and outcomes
-- Governance: Aggregational only. No thresholds. No trading logic.
-- =============================================================================

-- FROZEN SCORE VERSION: LID-v1.0
-- SOURCE VIEW: derived.v_path1_evidence_lid_v1_0

-- -----------------------------------------------------------------------------
-- Study 1: Overall LID-v1.0 Score Distribution
-- -----------------------------------------------------------------------------
-- Computes basic distributional statistics for the LID score across all data.

SELECT
    'LID-v1.0' AS score_version,
    COUNT(*) AS n_observations,
    AVG(lid_v1_0_raw) AS mean_score,
    STDDEV(lid_v1_0_raw) AS stddev_score,
    MIN(lid_v1_0_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p75_score,
    MAX(lid_v1_0_raw) AS max_score
FROM derived.v_path1_evidence_lid_v1_0
WHERE lid_v1_0_raw IS NOT NULL;


-- -----------------------------------------------------------------------------
-- Study 2: LID-v1.0 Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
-- Shows how LID score values are distributed within each outcome category.
-- Observation only: describes co-occurrence, not causation.

SELECT
    outcome_category,
    COUNT(*) AS n_observations,
    AVG(lid_v1_0_raw) AS mean_score,
    STDDEV(lid_v1_0_raw) AS stddev_score,
    MIN(lid_v1_0_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY lid_v1_0_raw) AS p75_score,
    MAX(lid_v1_0_raw) AS max_score
FROM derived.v_path1_evidence_lid_v1_0
WHERE lid_v1_0_raw IS NOT NULL
  AND outcome_category IS NOT NULL
GROUP BY outcome_category
ORDER BY outcome_category;


-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on LID-v1.0 Score Quantiles
-- -----------------------------------------------------------------------------
-- Divides LID scores into quantiles and counts outcome categories within each.
-- Uses data-driven quantiles (no fixed thresholds).

WITH score_quantiles AS (
    SELECT
        block_id,
        sym,
        lid_v1_0_raw,
        outcome_category,
        NTILE(4) OVER (ORDER BY lid_v1_0_raw) AS score_quartile
    FROM derived.v_path1_evidence_lid_v1_0
    WHERE lid_v1_0_raw IS NOT NULL
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
-- Study 4: Outcome Value Statistics by LID-v1.0 Score Quantile
-- -----------------------------------------------------------------------------
-- Computes outcome_ret summary statistics within each score quantile.
-- Observation only: describes what occurred, not what will occur.

WITH score_quantiles AS (
    SELECT
        lid_v1_0_raw,
        outcome_ret,
        NTILE(4) OVER (ORDER BY lid_v1_0_raw) AS score_quartile
    FROM derived.v_path1_evidence_lid_v1_0
    WHERE lid_v1_0_raw IS NOT NULL
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
