-- =============================================================================
-- Study: LID-v1.0 Distributional Analysis (Run-Scoped)
-- Run ID: p1_20260201_GBPUSD_20260131_len5d_475dd734 | Symbol: GBPUSD | Dates: 2026-01-27 to 2026-01-31
-- =============================================================================

-- FROZEN SCORE VERSION: LID-v1.0
-- SOURCE VIEW: derived.v_path1_evidence_lid_v1_0

-- -----------------------------------------------------------------------------
-- Study 1: Overall LID-v1.0 Score Distribution
-- -----------------------------------------------------------------------------
SELECT
    'LID-v1.0' AS score_version,
    'p1_20260201_GBPUSD_20260131_len5d_475dd734' AS run_id,
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
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2026-01-27' AND '2026-01-31';

-- -----------------------------------------------------------------------------
-- Study 2: LID-v1.0 Score Distribution Conditioned on Outcome Category
-- -----------------------------------------------------------------------------
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
  AND sym = 'GBPUSD'
  AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2026-01-27' AND '2026-01-31'
GROUP BY outcome_category
ORDER BY outcome_category;

-- -----------------------------------------------------------------------------
-- Study 3: Outcome Frequency Conditioned on LID-v1.0 Score Quantiles
-- -----------------------------------------------------------------------------
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
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2026-01-27' AND '2026-01-31'
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
WITH score_quantiles AS (
    SELECT
        lid_v1_0_raw,
        outcome_ret,
        NTILE(4) OVER (ORDER BY lid_v1_0_raw) AS score_quartile
    FROM derived.v_path1_evidence_lid_v1_0
    WHERE lid_v1_0_raw IS NOT NULL
      AND outcome_ret IS NOT NULL
      AND sym = 'GBPUSD'
      AND to_timestamp(bar_close_ms/1000)::date BETWEEN '2026-01-27' AND '2026-01-31'
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
