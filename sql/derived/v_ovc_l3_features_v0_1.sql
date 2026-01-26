-- =============================================================================
-- VIEW: derived.v_ovc_l3_features_v0_1
-- =============================================================================
-- This view implements OPTION_B_L3_FEATURES_v0.1.md
-- and is governed by OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md
--
-- Source of Truth:
--   - Feature Definitions: docs/ops/OPTION_B_L3_FEATURES_v0.1.md
--   - Implementation Contract: docs/ops/OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md
--   - Charter: docs/ops/OPTION_B_L3_CHARTER_v0.1.md
--   - Governance: docs/ops/GOVERNANCE_RULES_v0.1.md
--
-- L3 Feature Set (per OPTION_B_L3_FEATURES_v0.1.md §4):
--   L3-01: l3_trend_bias         - Directional bias state
--   L3-02: l3_volatility_regime  - Volatility context classification
--   L3-03: l3_structure_type     - Candle structure classification
--   L3-04: l3_momentum_state     - Momentum continuity state
--   L3-05: l3_session_position   - Session time classification
--   L3-06: l3_wick_dominance     - Wick rejection pattern
--   L3-07: l3_range_context      - Range relative to recent average
--
-- Compliance:
--   - Reads ONLY from CANONICAL L1 and L2 views (per Charter §2.1)
--   - NO direct access to ovc.ovc_blocks_v01_1_min (per Charter §2.2)
--   - Lookback-only computation (per Charter §2.3)
--   - Mutual exclusivity: exactly one label per feature (per Contract §3.1)
--   - Precedence rules applied per Contract §3.2
--   - NULL handling per Contract §2.2-2.4
--   - Deterministic, side-effect free (per Contract §5)
--   - All thresholds per Contract §6.1
--
-- Created: 2026-01-20
-- Status: [ACTIVE]
-- =============================================================================

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS derived;

-- Drop existing view if present (for idempotent deployment)
DROP VIEW IF EXISTS derived.v_ovc_l3_features_v0_1;

CREATE VIEW derived.v_ovc_l3_features_v0_1 AS
WITH
-- =============================================================================
-- CTE: base_joined
-- Join CANONICAL L1 and L2 views
-- Per Charter §2.1: ONLY L1 and L2 views are allowed inputs
-- =============================================================================
base_joined AS (
    SELECT
        -- Identity columns from L1
        c1.block_id,
        c1.sym,
        c1.o,
        c1.h,
        c1.l,
        c1.c,
        c1.rng,
        c1.body,
        c1.dir,
        
        -- L1 ratio features
        c1.body_ratio,
        c1.upper_wick_ratio,
        c1.lower_wick_ratio,
        
        -- L2 temporal features
        c2.dir_streak,
        c2.rng_avg_6,
        c2.session_block_idx,
        c2.bar_close_ms
        
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
),

-- =============================================================================
-- CTE: with_lookback
-- Add lookback columns required for L3 features
-- Per Contract §4.1: Allowed lookback per feature
-- =============================================================================
with_lookback AS (
    SELECT
        bj.*,
        
        -- Previous block direction (for dir_change detection)
        -- Contract §3.2 l3_trend_bias: needs dir_change
        LAG(bj.dir, 1) OVER (
            PARTITION BY bj.sym
            ORDER BY bj.bar_close_ms
        ) AS prev_dir,
        
        -- Previous block body (for momentum comparison)
        -- Contract §4.1 l3_momentum_state: needs prev_body
        LAG(bj.body, 1) OVER (
            PARTITION BY bj.sym
            ORDER BY bj.bar_close_ms
        ) AS prev_body,
        
        -- Previous block rng (for volatility streak detection)
        -- Contract §3.2 l3_volatility_regime: needs rng comparison
        LAG(bj.rng, 1) OVER (
            PARTITION BY bj.sym
            ORDER BY bj.bar_close_ms
        ) AS prev_rng,
        
        -- 2-back rng for streak detection
        LAG(bj.rng, 2) OVER (
            PARTITION BY bj.sym
            ORDER BY bj.bar_close_ms
        ) AS prev_rng_2
        
    FROM base_joined bj
),

-- =============================================================================
-- CTE: with_derived
-- Compute intermediate derived values needed for L3 features
-- =============================================================================
with_derived AS (
    SELECT
        wl.*,
        
        -- dir_change: TRUE if direction changed from previous block
        -- Contract §3.2: First precedence check for l3_trend_bias
        CASE
            WHEN wl.dir IS NULL OR wl.prev_dir IS NULL THEN NULL
            WHEN wl.dir != wl.prev_dir AND wl.prev_dir != 0 THEN TRUE
            ELSE FALSE
        END AS dir_change,
        
        -- rng_direction: Whether range is expanding or contracting
        -- -1 = narrowing, +1 = widening, 0 = unchanged
        CASE
            WHEN wl.rng IS NULL OR wl.prev_rng IS NULL THEN 0
            WHEN wl.rng < wl.prev_rng THEN -1
            WHEN wl.rng > wl.prev_rng THEN 1
            ELSE 0
        END AS rng_direction,
        
        -- prev_rng_direction: For 2-bar streak detection
        CASE
            WHEN wl.prev_rng IS NULL OR wl.prev_rng_2 IS NULL THEN 0
            WHEN wl.prev_rng < wl.prev_rng_2 THEN -1
            WHEN wl.prev_rng > wl.prev_rng_2 THEN 1
            ELSE 0
        END AS prev_rng_direction
        
    FROM with_lookback wl
),

-- =============================================================================
-- CTE: with_volatility_streak
-- Compute volatility streak (consecutive narrowing/widening)
-- Contract §3.2 l3_volatility_regime: rng_streak >= 2
-- =============================================================================
with_volatility_streak AS (
    SELECT
        wd.*,
        
        -- rng_streak_2: TRUE if 2+ consecutive bars in same direction
        -- Narrowing: rng[t] < rng[t-1] AND rng[t-1] < rng[t-2]
        -- Widening: rng[t] > rng[t-1] AND rng[t-1] > rng[t-2]
        CASE
            WHEN wd.rng_direction = -1 AND wd.prev_rng_direction = -1 THEN 'narrowing'
            WHEN wd.rng_direction = 1 AND wd.prev_rng_direction = 1 THEN 'widening'
            ELSE 'none'
        END AS rng_streak_type
        
    FROM with_derived wd
)

-- =============================================================================
-- FINAL SELECT: Compute all L3 semantic features
-- =============================================================================
SELECT
    -- =========================================================================
    -- IDENTITY COLUMNS (passthrough)
    -- =========================================================================
    vs.block_id,
    vs.sym,
    vs.bar_close_ms,
    
    -- =========================================================================
    -- L3-01: l3_trend_bias
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.1
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Directional bias based on streak behavior
    -- Values: 'sustained', 'nascent', 'neutral', 'fading'
    -- Thresholds: sustained >= 3 (Contract §6.1)
    -- =========================================================================
    CAST(
        CASE
            -- Contract §2.3: NULL dir_streak → fallback 'neutral'
            WHEN vs.dir_streak IS NULL THEN 'neutral'
            
            -- Contract §3.2 Precedence 1: dir_change = true → 'fading'
            WHEN vs.dir_change = TRUE THEN 'fading'
            
            -- Contract §3.2 Precedence 2: |dir_streak| >= 3 → 'sustained'
            -- Threshold from Contract §6.1: Sustained streak minimum = 3
            WHEN ABS(vs.dir_streak) >= 3 THEN 'sustained'
            
            -- Contract §3.2 Precedence 3: |dir_streak| IN (1, 2) → 'nascent'
            WHEN ABS(vs.dir_streak) IN (1, 2) THEN 'nascent'
            
            -- Contract §3.2 Precedence 4: Otherwise → 'neutral'
            ELSE 'neutral'
        END
    AS TEXT) AS l3_trend_bias,
    
    -- =========================================================================
    -- L3-02: l3_volatility_regime
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.2
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Volatility context based on range streak
    -- Values: 'compressed', 'normal', 'expanded'
    -- Thresholds: rng_streak >= 2 (Contract §3.2)
    -- =========================================================================
    CAST(
        CASE
            -- Contract §2.3: Insufficient data → fallback 'normal'
            WHEN vs.rng IS NULL OR vs.prev_rng IS NULL THEN 'normal'
            
            -- Contract §3.2 Precedence 1: 2+ consecutive narrowing → 'compressed'
            WHEN vs.rng_streak_type = 'narrowing' THEN 'compressed'
            
            -- Contract §3.2 Precedence 2: 2+ consecutive widening → 'expanded'
            WHEN vs.rng_streak_type = 'widening' THEN 'expanded'
            
            -- Contract §3.2 Precedence 3: Otherwise → 'normal'
            ELSE 'normal'
        END
    AS TEXT) AS l3_volatility_regime,
    
    -- =========================================================================
    -- L3-03: l3_structure_type
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.3
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Candle structure based on body/range ratio
    -- Values: 'decisive', 'balanced', 'indecisive'
    -- Thresholds: decisive >= 0.7, indecisive <= 0.3 (Contract §6.1)
    -- =========================================================================
    CAST(
        CASE
            -- Contract §3.2 Precedence 1: rng = 0 → 'indecisive'
            WHEN vs.rng IS NULL OR vs.rng = 0 THEN 'indecisive'
            
            -- Contract §2.3: NULL body → fallback 'balanced'
            WHEN vs.body IS NULL THEN 'balanced'
            
            -- Contract §3.2 Precedence 2: body/rng >= 0.7 → 'decisive'
            -- Threshold from Contract §6.1: Decisive ratio = 0.7
            WHEN CAST(vs.body AS DOUBLE PRECISION) / CAST(vs.rng AS DOUBLE PRECISION) >= 0.7 THEN 'decisive'
            
            -- Contract §3.2 Precedence 3: body/rng <= 0.3 → 'indecisive'
            -- Threshold from Contract §6.1: Indecisive ratio = 0.3
            WHEN CAST(vs.body AS DOUBLE PRECISION) / CAST(vs.rng AS DOUBLE PRECISION) <= 0.3 THEN 'indecisive'
            
            -- Contract §3.2 Precedence 4: Otherwise → 'balanced'
            ELSE 'balanced'
        END
    AS TEXT) AS l3_structure_type,
    
    -- =========================================================================
    -- L3-04: l3_momentum_state
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.4
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Momentum continuity based on body change
    -- Values: 'accelerating', 'steady', 'decelerating', 'reversing'
    -- Thresholds: accel > 1.2, decel < 0.8 (Contract §6.1)
    -- =========================================================================
    CAST(
        CASE
            -- Contract §3.2 Precedence 1: dir_change = true → 'reversing'
            WHEN vs.dir_change = TRUE THEN 'reversing'
            
            -- Contract §2.3: NULL prev_body → fallback 'steady'
            WHEN vs.prev_body IS NULL OR vs.prev_body = 0 THEN 'steady'
            
            -- Contract §2.3: NULL body → fallback 'steady'
            WHEN vs.body IS NULL THEN 'steady'
            
            -- Contract §3.2 Precedence 2: body > prev_body * 1.2 → 'accelerating'
            -- Threshold from Contract §6.1: Acceleration ratio = 1.2
            WHEN CAST(vs.body AS DOUBLE PRECISION) > CAST(vs.prev_body AS DOUBLE PRECISION) * 1.2 THEN 'accelerating'
            
            -- Contract §3.2 Precedence 3: body < prev_body * 0.8 → 'decelerating'
            -- Threshold from Contract §6.1: Deceleration ratio = 0.8
            WHEN CAST(vs.body AS DOUBLE PRECISION) < CAST(vs.prev_body AS DOUBLE PRECISION) * 0.8 THEN 'decelerating'
            
            -- Contract §3.2 Precedence 4: Otherwise → 'steady'
            ELSE 'steady'
        END
    AS TEXT) AS l3_momentum_state,
    
    -- =========================================================================
    -- L3-05: l3_session_position
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.5
    -- Contract Reference: §3.2 (deterministic mapping)
    -- Definition: Session time classification from block letter
    -- Values: 'early', 'mid', 'late'
    -- Mapping: A-D → early, E-H → mid, I-L → late
    -- =========================================================================
    CAST(
        CASE
            -- Contract §2.3: NULL session_block_idx → NULL (row invalid)
            WHEN vs.session_block_idx IS NULL THEN NULL
            
            -- Contract §3.2: Blocks A-D (indices 1-4) → 'early'
            WHEN vs.session_block_idx BETWEEN 1 AND 4 THEN 'early'
            
            -- Contract §3.2: Blocks E-H (indices 5-8) → 'mid'
            WHEN vs.session_block_idx BETWEEN 5 AND 8 THEN 'mid'
            
            -- Contract §3.2: Blocks I-L (indices 9-12) → 'late'
            WHEN vs.session_block_idx BETWEEN 9 AND 12 THEN 'late'
            
            -- Invalid index (should not occur) → NULL
            ELSE NULL
        END
    AS TEXT) AS l3_session_position,
    
    -- =========================================================================
    -- L3-06: l3_wick_dominance
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.6
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Wick rejection pattern classification
    -- Values: 'top_heavy', 'balanced', 'bottom_heavy', 'no_wicks'
    -- Thresholds: dominant >= 0.3, non-dominant < 0.15, no_wick < 0.1 (Contract §6.1)
    -- =========================================================================
    CAST(
        CASE
            -- Contract §3.2 Precedence 1: rng = 0 → 'no_wicks'
            WHEN vs.rng IS NULL OR vs.rng = 0 THEN 'no_wicks'
            
            -- Contract §2.3: NULL wick ratios → fallback 'balanced'
            WHEN vs.upper_wick_ratio IS NULL OR vs.lower_wick_ratio IS NULL THEN 'balanced'
            
            -- Contract §3.2 Precedence 2: (wick_top + wick_bot) / rng < 0.1 → 'no_wicks'
            -- Threshold from Contract §6.1: No-wick threshold = 0.1
            WHEN (vs.upper_wick_ratio + vs.lower_wick_ratio) < 0.1 THEN 'no_wicks'
            
            -- Contract §3.2 Precedence 3: upper >= 0.3 AND lower < 0.15 → 'top_heavy'
            -- Thresholds from Contract §6.1: Dominance = 0.3, Non-dominant = 0.15
            WHEN vs.upper_wick_ratio >= 0.3 AND vs.lower_wick_ratio < 0.15 THEN 'top_heavy'
            
            -- Contract §3.2 Precedence 4: lower >= 0.3 AND upper < 0.15 → 'bottom_heavy'
            WHEN vs.lower_wick_ratio >= 0.3 AND vs.upper_wick_ratio < 0.15 THEN 'bottom_heavy'
            
            -- Contract §3.2 Precedence 5: Otherwise → 'balanced'
            ELSE 'balanced'
        END
    AS TEXT) AS l3_wick_dominance,
    
    -- =========================================================================
    -- L3-07: l3_range_context
    -- Spec Reference: OPTION_B_L3_FEATURES_v0.1.md §4.7
    -- Contract Reference: §3.2 (precedence), §2.3 (fallback)
    -- Definition: Range relative to recent average
    -- Values: 'narrow', 'typical', 'wide'
    -- Thresholds: narrow < 0.6, wide > 1.4 (Contract §6.1)
    -- Note: Using rng_avg_6 (available in L2) instead of rng_avg_5
    -- =========================================================================
    CAST(
        CASE
            -- Contract §3.2 Precedence 1: rng_avg NULL or 0 → 'typical'
            WHEN vs.rng_avg_6 IS NULL OR vs.rng_avg_6 = 0 THEN 'typical'
            
            -- Contract §2.3: NULL rng → fallback 'typical'
            WHEN vs.rng IS NULL THEN 'typical'
            
            -- Contract §3.2 Precedence 2: rng < avg * 0.6 → 'narrow'
            -- Threshold from Contract §6.1: Narrow multiplier = 0.6
            WHEN CAST(vs.rng AS DOUBLE PRECISION) < vs.rng_avg_6 * 0.6 THEN 'narrow'
            
            -- Contract §3.2 Precedence 3: rng > avg * 1.4 → 'wide'
            -- Threshold from Contract §6.1: Wide multiplier = 1.4
            WHEN CAST(vs.rng AS DOUBLE PRECISION) > vs.rng_avg_6 * 1.4 THEN 'wide'
            
            -- Contract §3.2 Precedence 4: Otherwise → 'typical'
            ELSE 'typical'
        END
    AS TEXT) AS l3_range_context

FROM with_volatility_streak vs
ORDER BY vs.sym, vs.bar_close_ms;

-- =============================================================================
-- VIEW COMMENTS
-- =============================================================================
COMMENT ON VIEW derived.v_ovc_l3_features_v0_1 IS 
'L3 semantic features per OPTION_B_L3_FEATURES_v0.1.md. Status: ACTIVE (not CANONICAL). Reads only from L1 and L2 canonical views.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_trend_bias IS 
'L3-01: Directional bias state. Values: sustained, nascent, neutral, fading. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_volatility_regime IS 
'L3-02: Volatility context. Values: compressed, normal, expanded. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_structure_type IS 
'L3-03: Candle structure. Values: decisive, balanced, indecisive. Thresholds: 0.7/0.3. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_momentum_state IS 
'L3-04: Momentum continuity. Values: accelerating, steady, decelerating, reversing. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_session_position IS 
'L3-05: Session time classification. Values: early, mid, late. A-D/E-H/I-L mapping. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_wick_dominance IS 
'L3-06: Wick rejection pattern. Values: top_heavy, balanced, bottom_heavy, no_wicks. Contract §3.2.';

COMMENT ON COLUMN derived.v_ovc_l3_features_v0_1.l3_range_context IS 
'L3-07: Range vs average. Values: narrow, typical, wide. Thresholds: 0.6/1.4. Contract §3.2.';


-- =============================================================================
-- SEMANTIC VALIDATION QUERIES
-- =============================================================================
-- Uncomment and run these queries to validate L3 features against
-- mandatory semantic fixtures per OPTION_B_L3_IMPLEMENTATION_CONTRACT_v0.1.md §7.2
--
-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_clean_trend
-- Expected: l3_trend_bias = 'sustained', l3_momentum_state IN ('steady', 'accelerating')
-- Scenario: 5+ consecutive same-direction blocks
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_trend_bias,           -- Expected: 'sustained' (streak >= 3)
    l3_momentum_state,       -- Expected: 'steady' or 'accelerating'
    l3_volatility_regime
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_trend_bias = 'sustained'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_choppy
-- Expected: l3_trend_bias = 'neutral' or 'fading', l3_momentum_state = 'reversing'
-- Scenario: Alternating direction blocks
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_trend_bias,           -- Expected: 'neutral' or 'fading'
    l3_momentum_state,       -- Expected: 'reversing'
    l3_structure_type
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_momentum_state = 'reversing'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_vol_expansion
-- Expected: l3_volatility_regime = 'expanded'
-- Scenario: 3+ consecutive widening ranges
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_volatility_regime,    -- Expected: 'expanded'
    l3_range_context         -- May be 'wide' if above average
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_volatility_regime = 'expanded'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_vol_compression
-- Expected: l3_volatility_regime = 'compressed'
-- Scenario: 3+ consecutive narrowing ranges
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_volatility_regime,    -- Expected: 'compressed'
    l3_range_context         -- May be 'narrow' if below average
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_volatility_regime = 'compressed'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_session_transition
-- Expected: Correct l3_session_position labels across session boundary
-- Scenario: Block L → Block A transition
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_session_position,     -- Expected: 'late' for I-L, 'early' for A-D
    l3_trend_bias,
    l3_momentum_state
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
ORDER BY bar_close_ms DESC
LIMIT 24;  -- Show 2 full sessions
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_doji_sequence
-- Expected: l3_structure_type = 'indecisive'
-- Scenario: Small body / large range blocks
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_structure_type,       -- Expected: 'indecisive'
    l3_wick_dominance
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_structure_type = 'indecisive'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- FIXTURE: fixture_decisive_move
-- Expected: l3_structure_type = 'decisive', l3_wick_dominance = 'no_wicks'
-- Scenario: Large body / small wick blocks
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    l3_structure_type,       -- Expected: 'decisive'
    l3_wick_dominance        -- Expected: 'no_wicks' or 'balanced'
FROM derived.v_ovc_l3_features_v0_1
WHERE sym = 'GBPUSD'
  AND l3_structure_type = 'decisive'
ORDER BY bar_close_ms DESC
LIMIT 10;
*/

-- -----------------------------------------------------------------------------
-- MUTUAL EXCLUSIVITY CHECK
-- Contract §3.1: Exactly one label per feature per block
-- Expected: All counts = 1
-- -----------------------------------------------------------------------------
/*
SELECT 
    block_id,
    COUNT(DISTINCT l3_trend_bias) AS trend_labels,
    COUNT(DISTINCT l3_volatility_regime) AS vol_labels,
    COUNT(DISTINCT l3_structure_type) AS struct_labels,
    COUNT(DISTINCT l3_momentum_state) AS momentum_labels,
    COUNT(DISTINCT l3_session_position) AS session_labels,
    COUNT(DISTINCT l3_wick_dominance) AS wick_labels,
    COUNT(DISTINCT l3_range_context) AS range_labels
FROM derived.v_ovc_l3_features_v0_1
GROUP BY block_id
HAVING 
    COUNT(DISTINCT l3_trend_bias) != 1 OR
    COUNT(DISTINCT l3_volatility_regime) != 1 OR
    COUNT(DISTINCT l3_structure_type) != 1 OR
    COUNT(DISTINCT l3_momentum_state) != 1 OR
    COUNT(DISTINCT l3_wick_dominance) != 1 OR
    COUNT(DISTINCT l3_range_context) != 1;
-- Should return 0 rows if mutual exclusivity holds
*/

-- -----------------------------------------------------------------------------
-- LABEL DISTRIBUTION SUMMARY
-- Verify reasonable distribution of labels
-- -----------------------------------------------------------------------------
/*
SELECT 
    'l3_trend_bias' AS feature,
    l3_trend_bias AS label,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_trend_bias

UNION ALL

SELECT 
    'l3_volatility_regime',
    l3_volatility_regime,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_volatility_regime

UNION ALL

SELECT 
    'l3_structure_type',
    l3_structure_type,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_structure_type

UNION ALL

SELECT 
    'l3_momentum_state',
    l3_momentum_state,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_momentum_state

UNION ALL

SELECT 
    'l3_session_position',
    l3_session_position,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_session_position

UNION ALL

SELECT 
    'l3_wick_dominance',
    l3_wick_dominance,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_wick_dominance

UNION ALL

SELECT 
    'l3_range_context',
    l3_range_context,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM derived.v_ovc_l3_features_v0_1
GROUP BY l3_range_context

ORDER BY feature, label;
*/

-- =============================================================================
-- END OF VIEW DEFINITION
-- =============================================================================
