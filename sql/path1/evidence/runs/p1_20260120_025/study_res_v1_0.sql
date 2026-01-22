-- =============================================================================
-- Study: RES-v1.0 Distributional Analysis (Run-Scoped)
-- Run ID: p1_20260120_025 | Symbol: GBPUSD | Dates: 2023-07-10 to 2023-07-14
-- =============================================================================

-- FROZEN SCORE VERSION: RES-v1.0
-- SOURCE VIEW: derived.v_path1_evidence_res_v1_0

-- -----------------------------------------------------------------------------
-- Study 1: Overall RES-v1.0 Score Distribution
-- -----------------------------------------------------------------------------
SELECT
    'RES-v1.0' AS score_version,
    'p1_20260120_025' AS run_id,
    COUNT(*) AS n_observations,
    AVG(res_v1_0_raw) AS mean_score,
    STDDEV(res_v1_0_raw) AS stddev_score,
    MIN(res_v1_0_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p75_score,
    MAX(res_v1_0_raw) AS max_score
FROM derived.v_path1_evidence_res_v1_0
WHERE res_v1_0_raw IS NOT NULL
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-10' AND '2023-07-14';

-- -----------------------------------------------------------------------------
-- Study 2: RES-v1.0 Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
SELECT
    outcome_category,
    COUNT(*) AS n_observations,
    AVG(res_v1_0_raw) AS mean_score,
    STDDEV(res_v1_0_raw) AS stddev_score,
    MIN(res_v1_0_raw) AS min_score,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p25_score,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p50_score,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY res_v1_0_raw) AS p75_score,
    MAX(res_v1_0_raw) AS max_score
FROM derived.v_path1_evidence_res_v1_0
WHERE res_v1_0_raw IS NOT NULL
  AND outcome_category IS NOT NULL
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-10' AND '2023-07-14'
GROUP BY outcome_category
ORDER BY outcome_category;

-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on RES-v1.0 Score Quantiles
-- -----------------------------------------------------------------------------
WITH score_quantiles AS (
    SELECT
        block_id,
        sym,
        res_v1_0_raw,
        outcome_category,
        NTILE(4) OVER (ORDER BY res_v1_0_raw) AS score_quartile
    FROM derived.v_path1_evidence_res_v1_0
    WHERE res_v1_0_raw IS NOT NULL
      AND outcome_category IS NOT NULL
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-10' AND '2023-07-14'
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
-- Study 4: Outcome Value Statistics by RES-v1.0 Score Quantile
-- -----------------------------------------------------------------------------
WITH score_quantiles AS (
    SELECT
        res_v1_0_raw,
        outcome_ret,
        NTILE(4) OVER (ORDER BY res_v1_0_raw) AS score_quartile
    FROM derived.v_path1_evidence_res_v1_0
    WHERE res_v1_0_raw IS NOT NULL
      AND outcome_ret IS NOT NULL
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-10' AND '2023-07-14'
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
