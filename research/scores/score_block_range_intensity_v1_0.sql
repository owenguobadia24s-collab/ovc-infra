-- ============================================================================
-- SCORE: block_range_intensity
-- Version: v1.0
-- ============================================================================
--
-- ⚠️  NON-CANONICAL — This score is a downstream research artifact only.
--     NO FEEDBACK INTO CANONICAL — Does not modify Option B/C definitions.
--
-- ============================================================================
-- METADATA
-- ============================================================================
-- canonical_release: ovc-v0.1-spine
-- score_name: block_range_intensity
-- version: v1.0
--
-- purpose:
--   Descriptive compression of block-level price range (high - low) into a
--   normalized scalar value. This score quantifies how "intense" a block's
--   range is relative to the global distribution of ranges for that instrument.
--
-- inputs:
--   - derived.ovc_block_features_v0_1
--     columns: block_id, ts, instrument, rng
--
-- normalization_method:
--   Z-score using per-instrument global mean and standard deviation.
--   Formula: score_value = (rng - mean(rng)) / stddev(rng)
--   Computed over all available data for each instrument.
--
-- rationale_for_z_score:
--   - Deterministic: same input data always produces same output
--   - Interpretable: units are standard deviations from mean
--   - No parameters to tune (mean/std derived from data)
--   - Handles cross-instrument comparison (normalized within each instrument)
--
-- output_schema:
--   - block_id: text (primary key)
--   - ts: timestamptz (block timestamp)
--   - instrument: text (trading pair)
--   - score_name: text (constant: 'block_range_intensity')
--   - score_value: numeric (z-score of range)
--   - score_version: text (constant: 'v1.0')
--
-- author: @ovc-research
-- created: 2026-01-20
--
-- ============================================================================
-- EXPLICIT EXCLUSIONS
-- ============================================================================
--
-- ❌ This score is NOT a trading signal
-- ❌ This score is NOT thresholded for decisions
-- ❌ This score does NOT imply tradability or predictive utility
-- ❌ This score does NOT reference Option C outcomes
-- ❌ This score does NOT define entry/exit rules
-- ❌ This score does NOT require or produce position sizing
--
-- This is DESCRIPTIVE COMPRESSION only. A high or low score value has no
-- inherent trading meaning. Do not interpret score extremes as opportunities.
--
-- ============================================================================
-- ASSUMPTIONS
-- ============================================================================
--
-- 1. The column `rng` exists in derived.ovc_block_features_v0_1 and represents
--    the block range (high - low). If the actual column name differs, update
--    the column reference below.
--
-- 2. `rng` is non-negative (range cannot be negative by definition).
--
-- 3. There are sufficient observations per instrument to compute meaningful
--    mean and standard deviation (recommend N > 100).
--
-- 4. Standard deviation is non-zero. Rows with zero stddev (constant range
--    across all blocks for an instrument) will produce NULL score values.
--
-- ============================================================================
-- CTE STRUCTURE
-- ============================================================================

WITH

-- ----------------------------------------------------------------------------
-- BASE: Extract raw data from canonical Option B features
-- ----------------------------------------------------------------------------
base AS (
    SELECT
        block_id,
        ts,
        instrument,
        rng  -- Assumed column name for range (high - low)
    FROM derived.ovc_block_features_v0_1
    WHERE rng IS NOT NULL  -- Exclude rows with missing range
),

-- ----------------------------------------------------------------------------
-- GLOBAL_STATS: Compute per-instrument mean and standard deviation
-- ----------------------------------------------------------------------------
-- Note: "Global" here means across all time for each instrument, not a
-- rolling window. This ensures determinism: the same dataset always produces
-- the same statistics.
-- ----------------------------------------------------------------------------
global_stats AS (
    SELECT
        instrument,
        AVG(rng) AS mean_rng,
        STDDEV(rng) AS std_rng,
        COUNT(*) AS n_obs
    FROM base
    GROUP BY instrument
),

-- ----------------------------------------------------------------------------
-- SCORE_CALC: Compute z-score for each block
-- ----------------------------------------------------------------------------
-- Formula: z = (x - mean) / std
-- If std = 0 (all ranges identical), score is NULL to avoid division by zero.
-- ----------------------------------------------------------------------------
score_calc AS (
    SELECT
        b.block_id,
        b.ts,
        b.instrument,
        b.rng,
        g.mean_rng,
        g.std_rng,
        CASE
            WHEN g.std_rng IS NULL OR g.std_rng = 0 THEN NULL
            ELSE (b.rng - g.mean_rng) / g.std_rng
        END AS z_score
    FROM base b
    JOIN global_stats g USING (instrument)
),

-- ----------------------------------------------------------------------------
-- FINAL: Format output to standard score schema
-- ----------------------------------------------------------------------------
final AS (
    SELECT
        block_id,
        ts,
        instrument,
        'block_range_intensity'::text AS score_name,
        z_score AS score_value,
        'v1.0'::text AS score_version
    FROM score_calc
)

-- ============================================================================
-- OUTPUT
-- ============================================================================
-- This query returns the score for all blocks. To limit to a specific window
-- or instrument, add a WHERE clause to the final SELECT (not within CTEs).
-- ============================================================================

SELECT
    block_id,
    ts,
    instrument,
    score_name,
    score_value,
    score_version
FROM final
ORDER BY instrument, ts;

-- ============================================================================
-- USAGE NOTES
-- ============================================================================
--
-- To filter by time window, wrap or modify the final SELECT:
--
--   SELECT * FROM final
--   WHERE ts >= '2025-01-01' AND ts < '2026-01-01';
--
-- To filter by instrument:
--
--   SELECT * FROM final
--   WHERE instrument = 'GBPUSD';
--
-- Do NOT filter by score_value for trading decisions. That would constitute
-- thresholding, which is forbidden in this layer.
--
-- ============================================================================
-- END OF SCORE
-- ============================================================================
