-- =============================================================================
-- VIEW: derived.v_ovc_c2_features_v0_1
-- =============================================================================
-- This view implements OPTION_B_C2_FEATURES_v0.1.md and is governed by
-- OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md
--
-- Source of Truth:
--   - Feature Definitions: docs/ops/OPTION_B_C2_FEATURES_v0.1.md
--   - Implementation Contract: docs/ops/OPTION_B_C2_IMPLEMENTATION_CONTRACT_v0.1.md
--   - Charter: docs/ops/OPTION_B_C2_CHARTER_v0.1.md
--   - Governance: docs/ops/GOVERNANCE_RULES_v0.1.md
--
-- C2 Feature Set (per OPTION_B_C2_FEATURES_v0.1.md §4.1):
--   C2-01: rng_avg_3         - Rolling mean of rng (3-bar)
--   C2-02: rng_avg_6         - Rolling mean of rng (6-bar)
--   C2-03: dir_streak        - Consecutive same-direction count (signed)
--   C2-04: session_block_idx - Session position (1-12 from block letter)
--   C2-05: session_rng_cum   - Cumulative session range
--   C2-06: session_dir_net   - Net directional count in session
--   C2-07: rng_rank_6        - Percentile rank of rng (6-bar)
--   C2-08: body_rng_pct_avg_3 - Rolling mean of body/rng % (3-bar)
--
-- Compliance:
--   - Reads from CANONICAL C1 view + canonical blocks (per Charter §2.1)
--   - Current bar INCLUDED in all windows (per Contract §2.1)
--   - Lookback-only computation (per Charter §2.3)
--   - Fixed N-bar windows may cross sessions (per Contract §2.2.2)
--   - Session-to-date windows reset at block A (per Contract §2.2.3)
--   - Partial windows → NULL for fixed windows (per Contract §2.3)
--   - NULL in window → NULL output (per Contract §3.1)
--   - Flat bar (dir=0) → streak=0 (per Contract §4.1.1)
--   - Zero-range included in averages (per Contract §3.3.2)
--   - 64-bit float precision (per Contract §5.1)
--   - Deterministic, side-effect free (per Contract §6)
--
-- Created: 2026-01-20
-- Validated: 2026-01-20 (reports/validation/C2_v0_1_validation.md)
-- Status: [CANONICAL] - All fixtures pass; C2 features frozen
-- =============================================================================

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS derived;

-- Drop existing view if present (for idempotent deployment)
DROP VIEW IF EXISTS derived.v_ovc_c2_features_v0_1;

CREATE VIEW derived.v_ovc_c2_features_v0_1 AS
WITH 
-- =============================================================================
-- CTE: base_data
-- Join canonical blocks with C1 features and extract session info
-- =============================================================================
base_data AS (
    SELECT
        b.block_id,
        b.sym,
        b.block2h,
        b.bar_close_ms,
        b.date_ny,
        b.o,
        b.h,
        b.l,
        b.c,
        -- C1 passthrough fields (prefer canonical block values per spec)
        b.rng,
        b.dir,
        -- Compute body_rng_pct from canonical fields
        -- Per OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-08): requires C1 body_rng_pct
        -- Derivation: body / rng * 100 (percentage)
        CASE 
            WHEN b.rng IS NULL OR b.rng = 0 THEN NULL
            WHEN b.body IS NULL THEN NULL
            ELSE CAST(b.body AS DOUBLE PRECISION) / CAST(b.rng AS DOUBLE PRECISION) * 100.0
        END AS body_rng_pct,
        
        -- =================================================================
        -- C2-04: session_block_idx
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-04)
        -- Contract Reference: §4 (justification for canonical block access)
        -- Definition: Map block letter (from block_id) to index 1-12
        --   block_id format: YYYYMMDD-{A-L}-{SYM}
        --   A→1, B→2, ..., L→12
        -- Domain: [1, 12]
        -- =================================================================
        CASE SUBSTRING(b.block_id FROM 10 FOR 1)
            WHEN 'A' THEN 1
            WHEN 'B' THEN 2
            WHEN 'C' THEN 3
            WHEN 'D' THEN 4
            WHEN 'E' THEN 5
            WHEN 'F' THEN 6
            WHEN 'G' THEN 7
            WHEN 'H' THEN 8
            WHEN 'I' THEN 9
            WHEN 'J' THEN 10
            WHEN 'K' THEN 11
            WHEN 'L' THEN 12
            ELSE NULL  -- Contract §3.2: Invalid block letter → NULL
        END AS session_block_idx,
        
        -- Extract session date for partitioning
        SUBSTRING(b.block_id FROM 1 FOR 8) AS session_date
        
    FROM ovc.ovc_blocks_v01_1_min b
    WHERE b.block_id IS NOT NULL
),

-- =============================================================================
-- CTE: windowed_data
-- Add window functions for rolling and session computations
-- Per Contract §2.1: Current bar is INCLUDED in all windows
-- =============================================================================
windowed_data AS (
    SELECT
        bd.*,
        
        -- =================================================================
        -- Window context for fixed N-bar rolling windows
        -- Contract §2.2.1: Fixed N-bar windows MAY cross session boundaries
        -- =================================================================
        
        -- Count of available bars in 3-bar window (current + 2 prior)
        COUNT(*) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS window_3_count,
        
        -- Count of available bars in 6-bar window (current + 5 prior)
        COUNT(*) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS window_6_count,
        
        -- =================================================================
        -- C2-01: rng_avg_3 (intermediate: sum of rng in 3-bar window)
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-01)
        -- Contract Reference: §2.1 (current bar included), §2.3 (partial → NULL)
        -- Window: Fixed 3-bar (current + 2 prior)
        -- =================================================================
        SUM(CAST(rng AS DOUBLE PRECISION)) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rng_sum_3,
        
        -- Count of non-NULL rng in 3-bar window (for NULL propagation check)
        COUNT(rng) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rng_count_3,
        
        -- =================================================================
        -- C2-02: rng_avg_6 (intermediate: sum of rng in 6-bar window)
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-02)
        -- Contract Reference: §2.1 (current bar included), §2.3 (partial → NULL)
        -- Window: Fixed 6-bar (current + 5 prior)
        -- =================================================================
        SUM(CAST(rng AS DOUBLE PRECISION)) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS rng_sum_6,
        
        -- Count of non-NULL rng in 6-bar window
        COUNT(rng) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS rng_count_6,
        
        -- =================================================================
        -- C2-08: body_rng_pct_avg_3 (intermediate: sum of body_rng_pct)
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-08)
        -- Contract Reference: §2.1 (current bar included), §3.1 (NULL propagation)
        -- Window: Fixed 3-bar (current + 2 prior)
        -- =================================================================
        SUM(body_rng_pct) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS body_rng_pct_sum_3,
        
        -- Count of non-NULL body_rng_pct in 3-bar window
        COUNT(body_rng_pct) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS body_rng_pct_count_3,
        
        -- =================================================================
        -- C2-07: rng_rank_6 (intermediate: count of prior bars with rng < current)
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-07)
        -- Contract Reference: §4.2.1 (strict less-than), §4.2.3 (ties excluded)
        -- Definition: count(rng[t-5:t-1] where rng[k] < rng[t]) / 5
        -- Window: Fixed 6-bar, rank against 5 prior bars
        -- NOTE: PostgreSQL window frames don't directly support conditional rank,
        --       so we use PERCENT_RANK as approximation for rank within window
        -- =================================================================
        -- For rank calculation, we need the individual prior values
        -- Using LAG to get the 5 prior rng values
        LAG(rng, 1) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS rng_lag_1,
        LAG(rng, 2) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS rng_lag_2,
        LAG(rng, 3) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS rng_lag_3,
        LAG(rng, 4) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS rng_lag_4,
        LAG(rng, 5) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS rng_lag_5,
        
        -- =================================================================
        -- C2-03: dir_streak (intermediate: prior direction and streak)
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-03)
        -- Contract Reference: §4.1 (signed direction, reset conditions)
        -- =================================================================
        LAG(dir, 1) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_dir,
        
        -- =================================================================
        -- Session-to-date features (partition by session)
        -- Contract §2.2.3: STD windows reset at session start (block A)
        -- =================================================================
        
        -- C2-05: session_rng_cum
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-05)
        -- Definition: sum(rng[session_start:t])
        SUM(CAST(rng AS DOUBLE PRECISION)) OVER (
            PARTITION BY sym, session_date
            ORDER BY bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_rng_cum_raw,
        
        -- Count of non-NULL rng in session (for NULL check)
        COUNT(rng) OVER (
            PARTITION BY sym, session_date
            ORDER BY bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_rng_count,
        
        -- C2-06: session_dir_net
        -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-06)
        -- Definition: sum(dir[session_start:t])
        SUM(dir) OVER (
            PARTITION BY sym, session_date
            ORDER BY bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_dir_net_raw,
        
        -- Count of non-NULL dir in session (for NULL check)
        COUNT(dir) OVER (
            PARTITION BY sym, session_date
            ORDER BY bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_dir_count,
        
        -- Row number within session (for NULL check against session_block_idx)
        ROW_NUMBER() OVER (
            PARTITION BY sym, session_date
            ORDER BY bar_close_ms
        ) AS session_row_num
        
    FROM base_data bd
),

-- =============================================================================
-- CTE: streak_calc
-- Recursive-style streak calculation using window functions
-- Contract §4.1.2: Streak counting algorithm
-- =============================================================================
streak_calc AS (
    SELECT
        wd.*,
        
        -- =================================================================
        -- C2-03: dir_streak calculation
        -- Contract §4.1.2 Algorithm:
        --   if dir[t] == 0: streak = 0
        --   else if dir[t] == dir[t-1] and streak[t-1] != 0: increment
        --   else: start new streak at ±1
        --
        -- Since recursive CTEs are expensive, we use a grouping approach:
        -- Group consecutive same-direction bars and count within group
        -- =================================================================
        
        -- Create streak group ID: changes when direction changes or is 0
        SUM(
            CASE 
                WHEN dir = 0 THEN 1  -- Flat bar always starts new group
                WHEN prev_dir IS NULL THEN 1  -- First bar starts new group
                WHEN dir != prev_dir THEN 1  -- Direction change starts new group
                ELSE 0
            END
        ) OVER (
            PARTITION BY sym
            ORDER BY bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS streak_group
        
    FROM windowed_data wd
),

streak_final AS (
    SELECT
        sc.*,
        
        -- =================================================================
        -- C2-03: dir_streak final calculation
        -- Contract §4.1.1: Sign matches dir[t]
        -- Contract §4.1.3: Reset to ±1 when direction changes
        -- Contract §4.1.4: Capped at ±12
        -- =================================================================
        CASE
            -- Contract §3.2: NULL dir → NULL streak
            WHEN dir IS NULL THEN NULL
            -- Contract §4.1.1: Flat bar (dir=0) → streak = 0
            WHEN dir = 0 THEN 0
            -- Normal case: count within streak group, signed by direction
            -- Capped at ±12 per Contract §4.1.4
            ELSE LEAST(12, GREATEST(-12,
                dir * CAST(ROW_NUMBER() OVER (
                    PARTITION BY sym, streak_group
                    ORDER BY bar_close_ms
                ) AS INTEGER)
            ))
        END AS dir_streak
        
    FROM streak_calc sc
)

-- =============================================================================
-- FINAL SELECT: Compute all C2 features
-- =============================================================================
SELECT
    -- Identity columns
    sf.block_id,
    sf.sym,
    sf.block2h,
    sf.bar_close_ms,
    sf.date_ny,
    
    -- Passthrough from canonical (for downstream convenience)
    sf.o,
    sf.h,
    sf.l,
    sf.c,
    sf.rng,
    sf.dir,
    
    -- =========================================================================
    -- C2-01: rng_avg_3
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-01)
    -- Contract Reference: §2.3 (partial window → NULL), §3.1 (NULL propagation)
    -- Definition: Rolling arithmetic mean of rng over last 3 bars
    -- Formula: (rng[t] + rng[t-1] + rng[t-2]) / 3
    -- Domain: [0, +∞), Units: pips
    -- =========================================================================
    CASE
        -- Contract §2.3: Fewer than 3 bars → NULL
        WHEN window_3_count < 3 THEN NULL
        -- Contract §3.1: Any NULL in window → NULL
        WHEN rng_count_3 < 3 THEN NULL
        -- Normal computation
        ELSE CAST(rng_sum_3 AS DOUBLE PRECISION) / 3.0
    END AS rng_avg_3,
    
    -- =========================================================================
    -- C2-02: rng_avg_6
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-02)
    -- Contract Reference: §2.3 (partial window → NULL), §3.1 (NULL propagation)
    -- Definition: Rolling arithmetic mean of rng over last 6 bars
    -- Formula: sum(rng[t-5:t]) / 6
    -- Domain: [0, +∞), Units: pips
    -- =========================================================================
    CASE
        -- Contract §2.3: Fewer than 6 bars → NULL
        WHEN window_6_count < 6 THEN NULL
        -- Contract §3.1: Any NULL in window → NULL
        WHEN rng_count_6 < 6 THEN NULL
        -- Normal computation
        ELSE CAST(rng_sum_6 AS DOUBLE PRECISION) / 6.0
    END AS rng_avg_6,
    
    -- =========================================================================
    -- C2-03: dir_streak
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-03)
    -- Contract Reference: §4.1 (full algorithm specification)
    -- Definition: Count of consecutive bars with same direction, signed
    -- Domain: [-12, +12], Units: bars (signed)
    -- =========================================================================
    sf.dir_streak,
    
    -- =========================================================================
    -- C2-04: session_block_idx
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-04)
    -- Contract Reference: §3.2 (NULL handling for invalid block_id)
    -- Definition: Position of current bar within session (1-indexed)
    -- Formula: Map block letter to index: A→1, B→2, ..., L→12
    -- Domain: [1, 12], Units: ordinal position
    -- =========================================================================
    sf.session_block_idx,
    
    -- =========================================================================
    -- C2-05: session_rng_cum
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-05)
    -- Contract Reference: §2.2.3 (STD window reset at block A), §3.3.3 (session start)
    -- Definition: Cumulative sum of bar ranges within current session
    -- Formula: sum(rng[session_start:t])
    -- Domain: [0, +∞), Units: pips
    -- Edge case: At block 1, equals rng[t]
    -- =========================================================================
    CASE
        -- Contract §3.2: NULL block_id → NULL
        WHEN sf.session_block_idx IS NULL THEN NULL
        -- Contract §3.1: Any NULL in session → NULL
        -- Check if all bars in session have non-NULL rng
        WHEN sf.session_rng_count < sf.session_block_idx THEN NULL
        -- Normal computation
        ELSE sf.session_rng_cum_raw
    END AS session_rng_cum,
    
    -- =========================================================================
    -- C2-06: session_dir_net
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-06)
    -- Contract Reference: §2.2.3 (STD window reset), §3.3.3 (session start)
    -- Definition: Net directional count within current session
    -- Formula: sum(dir[session_start:t])
    -- Domain: [-12, +12], Units: net bars
    -- Edge case: At block 1, equals dir[t]
    -- =========================================================================
    CASE
        -- Contract §3.2: NULL block_id → NULL
        WHEN sf.session_block_idx IS NULL THEN NULL
        -- Contract §3.1: Any NULL in session → NULL
        WHEN sf.session_dir_count < sf.session_block_idx THEN NULL
        -- Normal computation
        ELSE CAST(sf.session_dir_net_raw AS INTEGER)
    END AS session_dir_net,
    
    -- =========================================================================
    -- C2-07: rng_rank_6
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-07)
    -- Contract Reference: §4.2.1 (strict less-than), §4.2.3 (ties excluded)
    -- Definition: Percentile rank of current bar's range within last 6 bars
    -- Formula: count(rng[t-5:t-1] where rng[k] < rng[t]) / 5
    -- Domain: [0.0, 1.0], Units: ratio (dimensionless)
    -- =========================================================================
    CASE
        -- Contract §4.2.4: Fewer than 6 bars → NULL
        WHEN sf.window_6_count < 6 THEN NULL
        -- Contract §3.1: Current rng NULL → NULL
        WHEN sf.rng IS NULL THEN NULL
        -- Contract §3.1: Any prior rng NULL → NULL
        WHEN sf.rng_lag_1 IS NULL OR sf.rng_lag_2 IS NULL OR sf.rng_lag_3 IS NULL 
             OR sf.rng_lag_4 IS NULL OR sf.rng_lag_5 IS NULL THEN NULL
        -- Contract §4.2.1: Strict less-than count / 5
        -- Contract §4.2.3: Ties do not contribute (use < not <=)
        ELSE CAST(
            (CASE WHEN sf.rng_lag_1 < sf.rng THEN 1 ELSE 0 END) +
            (CASE WHEN sf.rng_lag_2 < sf.rng THEN 1 ELSE 0 END) +
            (CASE WHEN sf.rng_lag_3 < sf.rng THEN 1 ELSE 0 END) +
            (CASE WHEN sf.rng_lag_4 < sf.rng THEN 1 ELSE 0 END) +
            (CASE WHEN sf.rng_lag_5 < sf.rng THEN 1 ELSE 0 END)
        AS DOUBLE PRECISION) / 5.0
    END AS rng_rank_6,
    
    -- =========================================================================
    -- C2-08: body_rng_pct_avg_3
    -- Spec Reference: OPTION_B_C2_FEATURES_v0.1.md §4.2 (C2-08)
    -- Contract Reference: §2.3 (partial window → NULL), §3.1 (NULL propagation)
    -- Definition: Rolling mean of body-to-range percentage over last 3 bars
    -- Formula: sum(body_rng_pct[t-2:t]) / 3
    -- Domain: [0.0, 100.0], Units: percentage
    -- =========================================================================
    CASE
        -- Contract §2.3: Fewer than 3 bars → NULL
        WHEN sf.window_3_count < 3 THEN NULL
        -- Contract §3.1: Any NULL in window → NULL
        WHEN sf.body_rng_pct_count_3 < 3 THEN NULL
        -- Normal computation
        ELSE CAST(sf.body_rng_pct_sum_3 AS DOUBLE PRECISION) / 3.0
    END AS body_rng_pct_avg_3,
    
    -- =========================================================================
    -- DIAGNOSTIC COLUMNS (for validation and debugging)
    -- =========================================================================
    sf.window_3_count,
    sf.window_6_count,
    sf.session_row_num,
    sf.streak_group

FROM streak_final sf
ORDER BY sf.sym, sf.bar_close_ms;

-- =============================================================================
-- VIEW COMMENTS
-- =============================================================================
COMMENT ON VIEW derived.v_ovc_c2_features_v0_1 IS 
'C2 multi-bar features per OPTION_B_C2_FEATURES_v0.1.md. Status: ACTIVE (not CANONICAL).';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.rng_avg_3 IS 
'C2-01: Rolling mean of rng over 3 bars. Contract §2.3: partial→NULL.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.rng_avg_6 IS 
'C2-02: Rolling mean of rng over 6 bars. Contract §2.3: partial→NULL.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.dir_streak IS 
'C2-03: Consecutive same-direction bars, signed. Contract §4.1: flat→0, cap ±12.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.session_block_idx IS 
'C2-04: Position in session 1-12 (A→1, L→12). Contract §3.2: invalid→NULL.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.session_rng_cum IS 
'C2-05: Cumulative session range. Contract §2.2.3: resets at block A.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.session_dir_net IS 
'C2-06: Net directional count in session. Contract §2.2.3: resets at block A.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.rng_rank_6 IS 
'C2-07: Percentile rank of rng in 6-bar window. Contract §4.2: strict <, ties excluded.';

COMMENT ON COLUMN derived.v_ovc_c2_features_v0_1.body_rng_pct_avg_3 IS 
'C2-08: Rolling mean of body/rng % over 3 bars. Contract §3.1: NULL propagation.';


-- =============================================================================
-- VALIDATION QUERIES (commented out - for test fixture verification)
-- =============================================================================

/*
-- ---------------------------------------------------------------------------
-- FIXTURE 1: Short History (< Window)
-- Contract §2.3: Fixed N-bar windows return NULL if fewer than N bars available
-- Expected: NULL for rng_avg_3, rng_avg_6, rng_rank_6 on first few bars
-- ---------------------------------------------------------------------------
SELECT 
    block_id, sym, session_block_idx,
    window_3_count, rng_avg_3,      -- Should be NULL when window_3_count < 3
    window_6_count, rng_avg_6,      -- Should be NULL when window_6_count < 6
    rng_rank_6                       -- Should be NULL when window_6_count < 6
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
ORDER BY bar_close_ms
LIMIT 10;

-- ---------------------------------------------------------------------------
-- FIXTURE 2: Session Boundary Crossing
-- Contract §2.2.2: Fixed N-bar windows MAY cross session boundaries
-- Contract §2.2.3: STD windows reset at block A (session_block_idx = 1)
-- Expected: session_rng_cum resets at block A; rng_avg_3 spans sessions
-- ---------------------------------------------------------------------------
SELECT 
    block_id, sym, session_block_idx,
    rng_avg_3,           -- Should span across session boundary
    session_rng_cum,     -- Should reset at session_block_idx = 1
    session_dir_net      -- Should reset at session_block_idx = 1
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
  AND session_block_idx IN (11, 12, 1, 2)  -- Around session boundary
ORDER BY bar_close_ms
LIMIT 20;

-- ---------------------------------------------------------------------------
-- FIXTURE 3: Direction Flip
-- Contract §4.1.2: Streak resets when direction changes
-- Expected: dir_streak resets to ±1 when dir changes sign
-- ---------------------------------------------------------------------------
SELECT 
    block_id, sym, dir, 
    dir_streak,
    LAG(dir) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_dir,
    LAG(dir_streak) OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_streak
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
ORDER BY bar_close_ms
LIMIT 50;

-- ---------------------------------------------------------------------------
-- FIXTURE 4: Flat-Bar Interruption
-- Contract §4.1.1: Flat bar (dir=0) → streak = 0
-- Contract §3.3.1: Flat bar breaks any prior streak
-- Expected: dir_streak = 0 when dir = 0; streak restarts after flat
-- ---------------------------------------------------------------------------
SELECT 
    block_id, sym, dir, dir_streak,
    session_dir_net      -- Flat bars contribute 0 to sum
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
  AND dir = 0            -- Find flat bars
ORDER BY bar_close_ms
LIMIT 10;

-- ---------------------------------------------------------------------------
-- FIXTURE 5: Zero-Range Bar Handling
-- Contract §3.3.2: Zero-range bars include 0 in calculations
-- Expected: rng = 0 is included in rng_avg_* calculations (not skipped)
-- ---------------------------------------------------------------------------
SELECT 
    block_id, sym, rng,
    rng_avg_3,           -- Should include 0 values, not skip them
    body_rng_pct_avg_3   -- body_rng_pct is NULL when rng=0, so avg may be NULL
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
  AND rng = 0
LIMIT 10;

-- ---------------------------------------------------------------------------
-- FIXTURE 6: Determinism Check
-- Contract §6.1: Same input → same output
-- Expected: Running twice produces identical results
-- ---------------------------------------------------------------------------
SELECT 
    block_id,
    rng_avg_3, rng_avg_6, dir_streak, session_block_idx,
    session_rng_cum, session_dir_net, rng_rank_6, body_rng_pct_avg_3
FROM derived.v_ovc_c2_features_v0_1
WHERE sym = 'GBPUSD'
ORDER BY bar_close_ms
LIMIT 100;
-- Run twice and diff results - should be identical
*/
