-- =============================================================================
-- Study: DIS-v1.1 Distributional Analysis (Run-Scoped)
-- Run ID: p1_20260120_023 | Symbol: GBPUSD | Dates: 2023-07-24 to 2023-07-28
-- =============================================================================

-- FROZEN SCORE VERSION: DIS-v1.1
-- SOURCE VIEW: derived.v_path1_evidence_dis_v1_1

-- -----------------------------------------------------------------------------
-- Study 1: Overall DIS-v1.1 Score Distribution
-- -----------------------------------------------------------------------------
SELECT
    'DIS-v1.1' AS score_version,
    'p1_20260120_023' AS run_id,
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
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-24' AND '2023-07-28';

-- -----------------------------------------------------------------------------
-- Study 2: DIS-v1.1 Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
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
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-24' AND '2023-07-28'
GROUP BY outcome_category
ORDER BY outcome_category;

-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on DIS-v1.1 Score Quantiles
-- -----------------------------------------------------------------------------
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
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-24' AND '2023-07-28'
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
WITH score_quantiles AS (
    SELECT
        dis_v1_1_raw,
        outcome_ret,
        NTILE(4) OVER (ORDER BY dis_v1_1_raw) AS score_quartile
    FROM derived.v_path1_evidence_dis_v1_1
    WHERE dis_v1_1_raw IS NOT NULL
      AND outcome_ret IS NOT NULL
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2023-07-24' AND '2023-07-28'
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
