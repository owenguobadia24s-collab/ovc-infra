-- =============================================================================
-- VIEW: derived.v_ovc_l1_features_v0_1
-- =============================================================================
-- This view implements OPTION_B_L1_FEATURES_v0.1.md and is governed by
-- OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md
--
-- Source of Truth:
--   - Feature Definitions: docs/ops/OPTION_B_L1_FEATURES_v0.1.md
--   - Implementation Contract: docs/ops/OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md
--   - Governance: docs/ops/GOVERNANCE_RULES_v0.1.md
--
-- Compliance:
--   - Reads ONLY from ovc.ovc_blocks_v01_1_min (per Charter §3.1)
--   - No joins, no window functions, no external state (per Features §2.3)
--   - UNDEFINED → NULL mapping (per Contract §2.1)
--   - Zero-range → NULL for ratios, FALSE for booleans (per Contract §2.2)
--   - Flat-bar handling (per Contract §2.3)
--   - NULL propagation (per Contract §2.4)
--   - 64-bit float precision (per Contract §3.1)
--   - Deterministic, side-effect free (per Contract §4)
--
-- Created: 2026-01-20
-- Status: [ACTIVE]
-- =============================================================================

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS derived;

-- Drop existing view if present (for idempotent deployment)
DROP VIEW IF EXISTS derived.v_ovc_l1_features_v0_1;

CREATE VIEW derived.v_ovc_l1_features_v0_1 AS
SELECT
    -- =========================================================================
    -- PASSTHROUGH COLUMNS (identity from canonical source)
    -- =========================================================================
    block_id,
    sym,
    tf,
    o,
    h,
    l,
    c,
    rng,
    body,
    dir,

    -- =========================================================================
    -- L1 FEATURE: body_ratio
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.1
    -- Contract Reference: §2.2 (zero-range → NULL), §2.3 (flat-bar → 0)
    -- Definition: |close - open| / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL (division by zero)
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation
        ELSE CAST(ABS(c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS body_ratio,

    -- =========================================================================
    -- L1 FEATURE: upper_wick_ratio
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.2
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: (high - max(open, close)) / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation
        ELSE CAST((h - GREATEST(o, c)) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS upper_wick_ratio,

    -- =========================================================================
    -- L1 FEATURE: lower_wick_ratio
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.3
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: (min(open, close) - low) / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation
        ELSE CAST((LEAST(o, c) - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS lower_wick_ratio,

    -- =========================================================================
    -- L1 FEATURE: wick_symmetry
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.4
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: (upper_wick - lower_wick) / (high - low)
    --           = ((h - max(o,c)) - (min(o,c) - l)) / (h - l)
    -- Domain: [-1, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation: (upper_wick - lower_wick) / range
        ELSE CAST(((h - GREATEST(o, c)) - (LEAST(o, c) - l)) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS wick_symmetry,

    -- =========================================================================
    -- L1 FEATURE: body_position
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.5
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: ((open + close) / 2 - low) / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation
        ELSE CAST(((o + c) / 2.0 - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS body_position,

    -- =========================================================================
    -- L1 FEATURE: close_position
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.6
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: (close - low) / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR c IS NULL THEN NULL
        -- Normal computation
        ELSE CAST((c - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS close_position,

    -- =========================================================================
    -- L1 FEATURE: open_position
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.7
    -- Contract Reference: §2.2 (zero-range → NULL)
    -- Definition: (open - low) / (high - low)
    -- Domain: [0, 1]
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL THEN NULL
        -- Normal computation
        ELSE CAST((o - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS open_position,

    -- =========================================================================
    -- L1 FEATURE: is_doji
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.8
    -- Contract Reference: §2.2 (zero-range → FALSE), §2.3 (flat-bar → TRUE)
    -- Definition: body_ratio <= 0.1
    -- Domain: {TRUE, FALSE}
    -- Threshold: 0.1 (per spec)
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return FALSE (no valid ratio)
        WHEN (h - l) = 0 THEN FALSE
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Spec §3.8: body_ratio <= 0.1
        ELSE (CAST(ABS(c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) <= 0.1
    END AS is_doji,

    -- =========================================================================
    -- L1 FEATURE: is_full_body
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.9
    -- Contract Reference: §2.2 (zero-range → FALSE)
    -- Definition: body_ratio >= 0.8
    -- Domain: {TRUE, FALSE}
    -- Threshold: 0.8 (per spec)
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return FALSE
        WHEN (h - l) = 0 THEN FALSE
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Spec §3.9: body_ratio >= 0.8
        ELSE (CAST(ABS(c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) >= 0.8
    END AS is_full_body,

    -- =========================================================================
    -- L1 FEATURE: is_hammer_shape
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.10
    -- Contract Reference: §2.2 (zero-range → FALSE)
    -- Definition: lower_wick_ratio >= 0.6 AND upper_wick_ratio <= 0.1 AND body_ratio <= 0.3
    -- Domain: {TRUE, FALSE}
    -- Note: Shape classification only; not a signal
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return FALSE
        WHEN (h - l) = 0 THEN FALSE
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Spec §3.10: All three conditions must be met
        ELSE (
            -- lower_wick_ratio >= 0.6
            (CAST((LEAST(o, c) - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) >= 0.6
            AND
            -- upper_wick_ratio <= 0.1
            (CAST((h - GREATEST(o, c)) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) <= 0.1
            AND
            -- body_ratio <= 0.3
            (CAST(ABS(c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) <= 0.3
        )
    END AS is_hammer_shape,

    -- =========================================================================
    -- L1 FEATURE: is_inverted_hammer_shape
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.11
    -- Contract Reference: §2.2 (zero-range → FALSE)
    -- Definition: upper_wick_ratio >= 0.6 AND lower_wick_ratio <= 0.1 AND body_ratio <= 0.3
    -- Domain: {TRUE, FALSE}
    -- Note: Shape classification only; not a signal
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return FALSE
        WHEN (h - l) = 0 THEN FALSE
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Spec §3.11: All three conditions must be met
        ELSE (
            -- upper_wick_ratio >= 0.6
            (CAST((h - GREATEST(o, c)) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) >= 0.6
            AND
            -- lower_wick_ratio <= 0.1
            (CAST((LEAST(o, c) - l) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) <= 0.1
            AND
            -- body_ratio <= 0.3
            (CAST(ABS(c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)) <= 0.3
        )
    END AS is_inverted_hammer_shape,

    -- =========================================================================
    -- L1 FEATURE: directional_efficiency
    -- Spec Reference: OPTION_B_L1_FEATURES_v0.1.md §3.12
    -- Contract Reference: §2.2 (zero-range → NULL), §2.3 (flat-bar → 0)
    -- Definition: (close - open) / (high - low)
    -- Domain: [-1, 1]
    -- Note: Preserves direction (signed)
    -- =========================================================================
    CASE
        -- Contract §2.2: Zero-range bars return NULL
        WHEN (h - l) = 0 THEN NULL
        -- Contract §2.4: NULL propagation
        WHEN h IS NULL OR l IS NULL OR o IS NULL OR c IS NULL THEN NULL
        -- Normal computation (signed, not absolute)
        ELSE CAST((c - o) AS DOUBLE PRECISION) / CAST((h - l) AS DOUBLE PRECISION)
    END AS directional_efficiency

FROM ovc.ovc_blocks_v01_1_min;

-- =============================================================================
-- VALIDATION QUERIES (for fixture testing)
-- =============================================================================
-- Uncomment and run these queries to validate against mandatory fixtures
-- per OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md §5.2
--
-- -----------------------------------------------------------------------------
-- FIXTURE: ZERO_RANGE_001 - Synthetic test (h = l = o = c)
-- Expected: All ratios NULL, all booleans FALSE
-- -----------------------------------------------------------------------------
-- SELECT
--     'ZERO_RANGE_001' AS fixture_id,
--     body_ratio IS NULL AS body_ratio_ok,           -- Expected: TRUE (NULL)
--     upper_wick_ratio IS NULL AS upper_wick_ok,     -- Expected: TRUE (NULL)
--     lower_wick_ratio IS NULL AS lower_wick_ok,     -- Expected: TRUE (NULL)
--     wick_symmetry IS NULL AS wick_symmetry_ok,     -- Expected: TRUE (NULL)
--     body_position IS NULL AS body_position_ok,     -- Expected: TRUE (NULL)
--     close_position IS NULL AS close_position_ok,   -- Expected: TRUE (NULL)
--     open_position IS NULL AS open_position_ok,     -- Expected: TRUE (NULL)
--     is_doji = FALSE AS is_doji_ok,                 -- Expected: TRUE (FALSE)
--     is_full_body = FALSE AS is_full_body_ok,       -- Expected: TRUE (FALSE)
--     is_hammer_shape = FALSE AS is_hammer_ok,       -- Expected: TRUE (FALSE)
--     is_inverted_hammer_shape = FALSE AS inv_hammer_ok, -- Expected: TRUE (FALSE)
--     directional_efficiency IS NULL AS dir_eff_ok   -- Expected: TRUE (NULL)
-- FROM (
--     SELECT 1.0 AS o, 1.0 AS h, 1.0 AS l, 1.0 AS c
-- ) AS synthetic
-- CROSS JOIN LATERAL (
--     SELECT
--         CASE WHEN (h - l) = 0 THEN NULL ELSE ABS(c - o) / (h - l) END AS body_ratio,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE (h - GREATEST(o, c)) / (h - l) END AS upper_wick_ratio,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE (LEAST(o, c) - l) / (h - l) END AS lower_wick_ratio,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE ((h - GREATEST(o, c)) - (LEAST(o, c) - l)) / (h - l) END AS wick_symmetry,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE ((o + c) / 2.0 - l) / (h - l) END AS body_position,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE (c - l) / (h - l) END AS close_position,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE (o - l) / (h - l) END AS open_position,
--         CASE WHEN (h - l) = 0 THEN FALSE ELSE ABS(c - o) / (h - l) <= 0.1 END AS is_doji,
--         CASE WHEN (h - l) = 0 THEN FALSE ELSE ABS(c - o) / (h - l) >= 0.8 END AS is_full_body,
--         CASE WHEN (h - l) = 0 THEN FALSE ELSE FALSE END AS is_hammer_shape,
--         CASE WHEN (h - l) = 0 THEN FALSE ELSE FALSE END AS is_inverted_hammer_shape,
--         CASE WHEN (h - l) = 0 THEN NULL ELSE (c - o) / (h - l) END AS directional_efficiency
-- ) AS features;
--
-- -----------------------------------------------------------------------------
-- FIXTURE: PURE_BULL_001 - Synthetic test (o = l, c = h)
-- Expected: body_ratio = 1, directional_efficiency = +1, is_full_body = TRUE
-- -----------------------------------------------------------------------------
-- SELECT
--     'PURE_BULL_001' AS fixture_id,
--     body_ratio,                    -- Expected: 1.0
--     directional_efficiency,        -- Expected: +1.0
--     is_full_body,                  -- Expected: TRUE
--     is_doji,                       -- Expected: FALSE
--     upper_wick_ratio,              -- Expected: 0.0
--     lower_wick_ratio               -- Expected: 0.0
-- FROM derived.v_ovc_l1_features_v0_1
-- WHERE block_id = '<INSERT_PURE_BULL_BLOCK_ID>';
--
-- -----------------------------------------------------------------------------
-- FIXTURE: PURE_BEAR_001 - Synthetic test (o = h, c = l)
-- Expected: body_ratio = 1, directional_efficiency = -1, is_full_body = TRUE
-- -----------------------------------------------------------------------------
-- SELECT
--     'PURE_BEAR_001' AS fixture_id,
--     body_ratio,                    -- Expected: 1.0
--     directional_efficiency,        -- Expected: -1.0
--     is_full_body,                  -- Expected: TRUE
--     is_doji,                       -- Expected: FALSE
--     upper_wick_ratio,              -- Expected: 0.0
--     lower_wick_ratio               -- Expected: 0.0
-- FROM derived.v_ovc_l1_features_v0_1
-- WHERE block_id = '<INSERT_PURE_BEAR_BLOCK_ID>';
--
-- -----------------------------------------------------------------------------
-- SAMPLE: View first 10 rows with all L1 features
-- -----------------------------------------------------------------------------
-- SELECT * FROM derived.v_ovc_l1_features_v0_1 LIMIT 10;
--
-- -----------------------------------------------------------------------------
-- SAMPLE: Count of doji bars
-- -----------------------------------------------------------------------------
-- SELECT COUNT(*) AS doji_count
-- FROM derived.v_ovc_l1_features_v0_1
-- WHERE is_doji = TRUE;
--
-- =============================================================================
