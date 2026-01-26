-- =============================================================================
-- VIEW: derived.v_ovc_c_outcomes_v0_1
-- =============================================================================
-- [STATUS: CANONICAL] - Promoted 2026-01-20
--
-- This view implements OPTION_C_OUTCOMES_v0.1.md and is governed by
-- OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md (both CANONICAL).
--
-- CANONICAL LOCK: Outcome meanings and computation behavior are FROZEN.
-- Any breaking change requires MAJOR version bump + governance approval.
--
-- Source of Truth:
--   - Outcome Definitions: docs/ops/OPTION_C_OUTCOMES_v0.1.md [CANONICAL]
--   - Implementation Contract: docs/ops/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md [CANONICAL]
--   - Charter: docs/ops/OPTION_C_CHARTER_v0.1.md
--   - Governance: docs/ops/GOVERNANCE_RULES_v0.1.md
--   - Validation: docs/validation/C_v0_1_validation.md
--   - Promotion: reports/validation/C_v0_1_promotion.md
--
-- Option C Outcome Set (per OPTION_C_OUTCOMES_v0.1.md §7):
--   CANONICAL:
--     fwd_ret_1, fwd_ret_3, fwd_ret_6  - Forward returns (N-bar)
--     mfe_3, mfe_6                      - Maximum favorable excursion
--     mae_3, mae_6                      - Maximum adverse excursion
--     rvol_6                            - Realized volatility (forward window)
--   DRAFT (not implemented):
--     ttt_*                             - Time to threshold (deferred)
--
-- Compliance:
--   - Reads ONLY from CANONICAL Option B views (per Charter §2.1):
--       - derived.v_ovc_l1_features_v0_1
--       - derived.v_ovc_l2_features_v0_1
--       - derived.v_ovc_l3_features_v0_1
--   - NO raw block access (per Charter §2.2)
--   - Anchor bar EXCLUDED from forward windows (per Contract §2.2)
--   - Lookahead ONLY in Option C (per Contract §2.4)
--   - NULL for missing/insufficient data (per Contract §4.1)
--   - No sentinel values (per Contract §4.3)
--   - Deterministic, side-effect free (per Contract §5)
--   - 64-bit float precision (per Contract §5.4)
--
-- Created: 2026-01-20
-- Promoted: 2026-01-20
-- Status: [CANONICAL]
-- =============================================================================

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS derived;

-- Drop existing view if present (for idempotent deployment)
DROP VIEW IF EXISTS derived.v_ovc_c_outcomes_v0_1;

CREATE VIEW derived.v_ovc_c_outcomes_v0_1 AS
WITH
-- =============================================================================
-- CTE: base_joined
-- Join CANONICAL L1, L2, L3 views to establish anchor blocks
-- Per Charter §2.1: ONLY Option B views are allowed inputs
-- =============================================================================
base_joined AS (
    SELECT
        -- Identity columns from L1
        c1.block_id,
        c1.sym,
        c1.c AS anchor_close,
        
        -- Ordering column from L2 (bar_close_ms for deterministic sequencing)
        c2.bar_close_ms,
        
        -- L3 passthrough for optional regime conditioning (future use)
        c3.l3_volatility_regime,
        c3.l3_trend_bias
        
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    INNER JOIN derived.v_ovc_l3_features_v0_1 c3
        ON c1.block_id = c3.block_id
    WHERE c1.block_id IS NOT NULL
      AND c1.c IS NOT NULL
),

-- =============================================================================
-- CTE: with_forward_prices
-- Add forward-looking price data using LEAD window functions
-- Per Contract §2.2: Anchor bar excluded; forward window begins at T+1
-- Per Contract §2.3: Session boundaries do not interrupt sequence
-- =============================================================================
with_forward_prices AS (
    SELECT
        bj.*,
        
        -- =================================================================
        -- Forward close prices for fwd_ret_N (Contract §3.1)
        -- =================================================================
        LEAD(c1.c, 1) OVER w_sym_time AS close_t1,
        LEAD(c1.c, 2) OVER w_sym_time AS close_t2,
        LEAD(c1.c, 3) OVER w_sym_time AS close_t3,
        LEAD(c1.c, 4) OVER w_sym_time AS close_t4,
        LEAD(c1.c, 5) OVER w_sym_time AS close_t5,
        LEAD(c1.c, 6) OVER w_sym_time AS close_t6,
        
        -- =================================================================
        -- Forward high prices for mfe_N (Contract §3.2)
        -- =================================================================
        LEAD(c1.h, 1) OVER w_sym_time AS high_t1,
        LEAD(c1.h, 2) OVER w_sym_time AS high_t2,
        LEAD(c1.h, 3) OVER w_sym_time AS high_t3,
        LEAD(c1.h, 4) OVER w_sym_time AS high_t4,
        LEAD(c1.h, 5) OVER w_sym_time AS high_t5,
        LEAD(c1.h, 6) OVER w_sym_time AS high_t6,
        
        -- =================================================================
        -- Forward low prices for mae_N (Contract §3.3)
        -- =================================================================
        LEAD(c1.l, 1) OVER w_sym_time AS low_t1,
        LEAD(c1.l, 2) OVER w_sym_time AS low_t2,
        LEAD(c1.l, 3) OVER w_sym_time AS low_t3,
        LEAD(c1.l, 4) OVER w_sym_time AS low_t4,
        LEAD(c1.l, 5) OVER w_sym_time AS low_t5,
        LEAD(c1.l, 6) OVER w_sym_time AS low_t6
        
    FROM base_joined bj
    -- Re-join L1 to get forward OHLC (we need h, l, c from forward bars)
    INNER JOIN derived.v_ovc_l1_features_v0_1 c1
        ON bj.block_id = c1.block_id
    WINDOW w_sym_time AS (
        PARTITION BY bj.sym
        ORDER BY bj.bar_close_ms
    )
),

-- =============================================================================
-- CTE: with_forward_aggregates
-- Compute forward-window aggregates for MFE, MAE
-- Per Contract §3.2, §3.3: Max/min over forward bars T+1 to T+N
-- =============================================================================
with_forward_aggregates AS (
    SELECT
        wfp.*,
        
        -- =================================================================
        -- MFE max high over N bars (Contract §3.2.2)
        -- =================================================================
        GREATEST(high_t1, high_t2, high_t3) AS max_high_3,
        GREATEST(high_t1, high_t2, high_t3, high_t4, high_t5, high_t6) AS max_high_6,
        
        -- =================================================================
        -- MAE min low over N bars (Contract §3.3.2)
        -- =================================================================
        LEAST(low_t1, low_t2, low_t3) AS min_low_3,
        LEAST(low_t1, low_t2, low_t3, low_t4, low_t5, low_t6) AS min_low_6,
        
        -- =================================================================
        -- Forward returns for rvol_6 (Contract §3.4.2)
        -- ret[T+k] = (close[T+k] - close[T+k-1]) / close[T+k-1]
        -- Note: ret_t1 uses anchor_close as prior
        -- =================================================================
        CASE 
            WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
            WHEN close_t1 IS NULL THEN NULL
            ELSE CAST((close_t1 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
        END AS ret_t1,
        CASE 
            WHEN close_t1 = 0 OR close_t1 IS NULL THEN NULL
            WHEN close_t2 IS NULL THEN NULL
            ELSE CAST((close_t2 - close_t1) AS DOUBLE PRECISION) / CAST(close_t1 AS DOUBLE PRECISION)
        END AS ret_t2,
        CASE 
            WHEN close_t2 = 0 OR close_t2 IS NULL THEN NULL
            WHEN close_t3 IS NULL THEN NULL
            ELSE CAST((close_t3 - close_t2) AS DOUBLE PRECISION) / CAST(close_t2 AS DOUBLE PRECISION)
        END AS ret_t3,
        CASE 
            WHEN close_t3 = 0 OR close_t3 IS NULL THEN NULL
            WHEN close_t4 IS NULL THEN NULL
            ELSE CAST((close_t4 - close_t3) AS DOUBLE PRECISION) / CAST(close_t3 AS DOUBLE PRECISION)
        END AS ret_t4,
        CASE 
            WHEN close_t4 = 0 OR close_t4 IS NULL THEN NULL
            WHEN close_t5 IS NULL THEN NULL
            ELSE CAST((close_t5 - close_t4) AS DOUBLE PRECISION) / CAST(close_t4 AS DOUBLE PRECISION)
        END AS ret_t5,
        CASE 
            WHEN close_t5 = 0 OR close_t5 IS NULL THEN NULL
            WHEN close_t6 IS NULL THEN NULL
            ELSE CAST((close_t6 - close_t5) AS DOUBLE PRECISION) / CAST(close_t5 AS DOUBLE PRECISION)
        END AS ret_t6
        
    FROM with_forward_prices wfp
)

-- =============================================================================
-- FINAL SELECT: Compute all ACTIVE outcomes
-- =============================================================================
SELECT
    -- =========================================================================
    -- Identity columns (passthrough from anchor block)
    -- =========================================================================
    block_id,
    sym,
    bar_close_ms,
    
    -- =========================================================================
    -- L3 regime context (passthrough for analysis convenience)
    -- =========================================================================
    l3_volatility_regime,
    l3_trend_bias,

    -- =========================================================================
    -- OUTCOME: fwd_ret_1
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.1
    -- Contract Reference: §3.1 (Forward Return)
    -- Definition: (close[T+1] - close[T]) / close[T]
    -- Domain: unbounded float (signed)
    -- =========================================================================
    CASE
        -- Contract §3.1.4: NULL if anchor close is zero or NULL
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        -- Contract §3.1.4: NULL if forward block does not exist
        WHEN close_t1 IS NULL THEN NULL
        -- Normal computation
        ELSE CAST((close_t1 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
    END AS fwd_ret_1,

    -- =========================================================================
    -- OUTCOME: fwd_ret_3
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.1
    -- Contract Reference: §3.1 (Forward Return)
    -- Definition: (close[T+3] - close[T]) / close[T]
    -- =========================================================================
    CASE
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        WHEN close_t3 IS NULL THEN NULL
        ELSE CAST((close_t3 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
    END AS fwd_ret_3,

    -- =========================================================================
    -- OUTCOME: fwd_ret_6
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.1
    -- Contract Reference: §3.1 (Forward Return)
    -- Definition: (close[T+6] - close[T]) / close[T]
    -- =========================================================================
    CASE
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        WHEN close_t6 IS NULL THEN NULL
        ELSE CAST((close_t6 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
    END AS fwd_ret_6,

    -- =========================================================================
    -- OUTCOME: mfe_3
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.2
    -- Contract Reference: §3.2 (Maximum Favorable Excursion)
    -- Definition: max(0, (max(high[T+1..T+3]) - close[T]) / close[T])
    -- Domain: [0, ∞) (unsigned)
    -- =========================================================================
    CASE
        -- Contract §3.2.4: NULL if anchor close is zero or NULL
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        -- Contract §3.2.4: NULL if any high in window is NULL (partial window)
        WHEN high_t1 IS NULL OR high_t2 IS NULL OR high_t3 IS NULL THEN NULL
        -- Contract §3.2.2: Floor at zero (never negative)
        ELSE GREATEST(
            0::DOUBLE PRECISION,
            CAST((max_high_3 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
        )
    END AS mfe_3,

    -- =========================================================================
    -- OUTCOME: mfe_6
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.2
    -- Contract Reference: §3.2 (Maximum Favorable Excursion)
    -- Definition: max(0, (max(high[T+1..T+6]) - close[T]) / close[T])
    -- =========================================================================
    CASE
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        WHEN high_t1 IS NULL OR high_t2 IS NULL OR high_t3 IS NULL 
          OR high_t4 IS NULL OR high_t5 IS NULL OR high_t6 IS NULL THEN NULL
        ELSE GREATEST(
            0::DOUBLE PRECISION,
            CAST((max_high_6 - anchor_close) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
        )
    END AS mfe_6,

    -- =========================================================================
    -- OUTCOME: mae_3
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.3
    -- Contract Reference: §3.3 (Maximum Adverse Excursion)
    -- Definition: max(0, (close[T] - min(low[T+1..T+3])) / close[T])
    -- Domain: [0, ∞) (unsigned)
    -- =========================================================================
    CASE
        -- Contract §3.3.4: NULL if anchor close is zero or NULL
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        -- Contract §3.3.4: NULL if any low in window is NULL (partial window)
        WHEN low_t1 IS NULL OR low_t2 IS NULL OR low_t3 IS NULL THEN NULL
        -- Contract §3.3.2: Floor at zero (never negative)
        ELSE GREATEST(
            0::DOUBLE PRECISION,
            CAST((anchor_close - min_low_3) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
        )
    END AS mae_3,

    -- =========================================================================
    -- OUTCOME: mae_6
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.3
    -- Contract Reference: §3.3 (Maximum Adverse Excursion)
    -- Definition: max(0, (close[T] - min(low[T+1..T+6])) / close[T])
    -- =========================================================================
    CASE
        WHEN anchor_close = 0 OR anchor_close IS NULL THEN NULL
        WHEN low_t1 IS NULL OR low_t2 IS NULL OR low_t3 IS NULL 
          OR low_t4 IS NULL OR low_t5 IS NULL OR low_t6 IS NULL THEN NULL
        ELSE GREATEST(
            0::DOUBLE PRECISION,
            CAST((anchor_close - min_low_6) AS DOUBLE PRECISION) / CAST(anchor_close AS DOUBLE PRECISION)
        )
    END AS mae_6,

    -- =========================================================================
    -- OUTCOME: rvol_6
    -- Spec Reference: OPTION_C_OUTCOMES_v0.1.md §3.5
    -- Contract Reference: §3.4 (Realized Volatility)
    -- Definition: sample stddev of returns ret[T+1..T+6]
    -- Formula: sqrt(sum((ret_i - mean_ret)^2) / (N-1)) where N=6
    -- Domain: [0, ∞)
    -- =========================================================================
    CASE
        -- Contract §3.4.4: NULL if any return is NULL
        WHEN ret_t1 IS NULL OR ret_t2 IS NULL OR ret_t3 IS NULL 
          OR ret_t4 IS NULL OR ret_t5 IS NULL OR ret_t6 IS NULL THEN NULL
        -- Normal computation: sample standard deviation
        -- Using explicit formula: sqrt(sum((x - mean)^2) / (n-1))
        ELSE (
            SELECT SQRT(
                (
                    POWER(ret_t1 - mean_ret, 2) +
                    POWER(ret_t2 - mean_ret, 2) +
                    POWER(ret_t3 - mean_ret, 2) +
                    POWER(ret_t4 - mean_ret, 2) +
                    POWER(ret_t5 - mean_ret, 2) +
                    POWER(ret_t6 - mean_ret, 2)
                ) / 5.0  -- N-1 = 6-1 = 5 (Bessel's correction)
            )
            FROM (
                SELECT CAST((ret_t1 + ret_t2 + ret_t3 + ret_t4 + ret_t5 + ret_t6) AS DOUBLE PRECISION) / 6.0 AS mean_ret
            ) AS mean_calc
        )
    END AS rvol_6

FROM with_forward_aggregates
ORDER BY sym, bar_close_ms;  -- Contract §5.1: Deterministic ordering

-- =============================================================================
-- VALIDATION QUERIES (inline, commented)
-- Reference: OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md §6.1
-- =============================================================================

-- -----------------------------------------------------------------------------
-- FIXTURE 1: Positive Move (Contract §6.2.1)
-- Verify: fwd_ret_N > 0, mfe_N > 0, mae_N >= 0 when price increases
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, fwd_ret_3, fwd_ret_6, mfe_3, mfe_6, mae_3, mae_6
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE fwd_ret_6 > 0.001  -- Price increased > 0.1%
-- LIMIT 5;

-- -----------------------------------------------------------------------------
-- FIXTURE 2: Negative Move (Contract §6.2.2)
-- Verify: fwd_ret_N < 0, mae_N > 0 when price decreases
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, fwd_ret_3, fwd_ret_6, mfe_3, mfe_6, mae_3, mae_6
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE fwd_ret_6 < -0.001  -- Price decreased > 0.1%
-- LIMIT 5;

-- -----------------------------------------------------------------------------
-- FIXTURE 3: Flat Move (Contract §6.2.3)
-- Verify: fwd_ret_N ≈ 0, mfe_N ≈ 0, mae_N ≈ 0 when price unchanged
-- Note: True flat is rare; look for small absolute return
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, fwd_ret_3, fwd_ret_6, mfe_3, mfe_6, mae_3, mae_6, rvol_6
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE ABS(fwd_ret_6) < 0.0001  -- Nearly flat
-- LIMIT 5;

-- -----------------------------------------------------------------------------
-- FIXTURE 4: High Volatility (Contract §6.2.4)
-- Verify: rvol_6 is significantly elevated
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_6, mfe_6, mae_6, rvol_6
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE rvol_6 > 0.005  -- High volatility threshold
-- ORDER BY rvol_6 DESC
-- LIMIT 10;

-- -----------------------------------------------------------------------------
-- FIXTURE 5: Session Boundary (Contract §6.2.5)
-- Verify: Outcomes computed correctly across session boundaries
-- Look for blocks near session end (K, L) that have valid forward outcomes
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, fwd_ret_3, fwd_ret_6, mfe_3, mae_3
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE block_id LIKE '________-K-%' OR block_id LIKE '________-L-%'
-- AND fwd_ret_6 IS NOT NULL
-- LIMIT 10;

-- -----------------------------------------------------------------------------
-- FIXTURE 6: Short History / NULL Outcomes (Contract §6.2.6)
-- Verify: Outcomes are NULL when insufficient forward data exists
-- Look for recent blocks where 6-bar forward window extends beyond data
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, fwd_ret_3, fwd_ret_6, mfe_6, mae_6, rvol_6
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE fwd_ret_1 IS NOT NULL AND fwd_ret_6 IS NULL
-- LIMIT 5;

-- -----------------------------------------------------------------------------
-- FIXTURE 7: NULL Input Handling (Contract §6.2.7)
-- Verify: NULL propagates correctly
-- This requires test data with NULL closes (rare in production)
-- -----------------------------------------------------------------------------
-- SELECT block_id, sym, fwd_ret_1, mfe_3, mae_3
-- FROM derived.v_ovc_c_outcomes_v0_1
-- WHERE block_id IN (SELECT block_id FROM derived.v_ovc_l1_features_v0_1 WHERE c IS NULL)
-- LIMIT 5;

-- -----------------------------------------------------------------------------
-- DETERMINISM CHECK (Contract §5.3)
-- Verify: Repeated queries return identical results
-- Run twice and compare row counts and checksums
-- -----------------------------------------------------------------------------
-- SELECT COUNT(*), SUM(COALESCE(fwd_ret_6::numeric, 0))::text AS checksum_fwd_ret_6
-- FROM derived.v_ovc_c_outcomes_v0_1;

-- -----------------------------------------------------------------------------
-- ROW COUNT VALIDATION
-- Verify: Total rows match L1/L2/L3 join (minus NULL anchor closes)
-- -----------------------------------------------------------------------------
-- SELECT 
--     (SELECT COUNT(*) FROM derived.v_ovc_c_outcomes_v0_1) AS outcome_rows,
--     (SELECT COUNT(*) FROM derived.v_ovc_l1_features_v0_1 c1
--      INNER JOIN derived.v_ovc_l2_features_v0_1 c2 ON c1.block_id = c2.block_id
--      INNER JOIN derived.v_ovc_l3_features_v0_1 c3 ON c1.block_id = c3.block_id
--      WHERE c1.c IS NOT NULL) AS expected_rows;

-- =============================================================================
-- END OF VIEW DEFINITION
-- =============================================================================
