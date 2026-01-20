-- ============================================================================
-- SCORE: [score_name]
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
-- 
-- purpose: 
--   [Brief description of what this score measures/compresses]
--
-- inputs:
--   - {{CANONICAL_FEATURE_VIEW}}  (replace with actual canonical object)
--     columns: block_id, ts, instrument, [list feature columns used]
--   - {{CANONICAL_OUTCOME_VIEW}}  (replace with actual canonical object)
--     columns: block_id, [list outcome columns used]
--
-- parameters:
--   - param_1: [value] — [description]
--   - param_2: [value] — [description]
--
-- output_schema:
--   - ts: timestamptz
--   - block_id: text
--   - instrument: text
--   - score_name: text (constant: '[score_name]')
--   - score_value: numeric
--   - metadata_json: jsonb (optional)
--
-- author: @handle
-- created: YYYY-MM-DD
-- ============================================================================

-- ============================================================================
-- CTE STRUCTURE
-- ============================================================================

WITH

-- ----------------------------------------------------------------------------
-- BASE: Extract raw data from canonical sources
-- ----------------------------------------------------------------------------
base AS (
    SELECT
        f.block_id,
        f.ts,
        f.instrument
        -- Add feature columns here
        -- Example: f.close, f.volume, f.rng
    FROM {{CANONICAL_FEATURE_VIEW}} f
    WHERE f.ts >= '{{WINDOW_START}}'::timestamptz
      AND f.ts <  '{{WINDOW_END}}'::timestamptz
      -- Add instrument filter if needed
      -- AND f.instrument IN ('GBPUSD', 'EURUSD')
),

-- ----------------------------------------------------------------------------
-- FEATURES: Compute intermediate features or transformations
-- ----------------------------------------------------------------------------
features AS (
    SELECT
        block_id,
        ts,
        instrument
        -- Add derived features here
        -- Example: (close - open) / NULLIF(rng, 0) AS body_ratio
    FROM base
),

-- ----------------------------------------------------------------------------
-- JOINS_OUTCOMES: Join with canonical outcomes if needed
-- ----------------------------------------------------------------------------
joins_outcomes AS (
    SELECT
        f.*
        -- Add outcome columns here
        -- Example: o.fwd_ret_3, o.mfe_3, o.mae_3
    FROM features f
    -- LEFT JOIN {{CANONICAL_OUTCOME_VIEW}} o USING (block_id)
),

-- ----------------------------------------------------------------------------
-- SCORE_CALC: Compute the score value
-- ----------------------------------------------------------------------------
score_calc AS (
    SELECT
        block_id,
        ts,
        instrument,
        -- ================================================================
        -- SCORE FORMULA: Define your score computation here
        -- ================================================================
        -- Example: (feature_1 * weight_1 + feature_2 * weight_2) AS raw_score
        0.0 AS raw_score
        -- ================================================================
    FROM joins_outcomes
),

-- ----------------------------------------------------------------------------
-- FINAL: Format output to standard schema
-- ----------------------------------------------------------------------------
final AS (
    SELECT
        ts,
        block_id,
        instrument,
        '[score_name]'::text AS score_name,
        raw_score AS score_value,
        jsonb_build_object(
            'canonical_release', 'ovc-v0.1-spine',
            'computed_at', NOW()
        ) AS metadata_json
    FROM score_calc
)

-- ============================================================================
-- OUTPUT
-- ============================================================================
SELECT
    ts,
    block_id,
    instrument,
    score_name,
    score_value,
    metadata_json
FROM final
ORDER BY ts, instrument;

-- ============================================================================
-- END OF SCORE
-- ============================================================================
