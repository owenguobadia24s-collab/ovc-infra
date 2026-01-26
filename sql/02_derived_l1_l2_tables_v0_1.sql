-- OVC Option B.1: Derived L1/L2 Feature Pack Tables (v0.1)
-- Generated: 2026-01-18
-- Purpose: Create tables for L1 (single-bar) and L2 (multi-bar) derived features
-- 
-- Tier Boundaries (per c_layer_boundary_spec_v0.1.md):
--   L1: Single-bar OHLC math. No history, no lookback, no rolling windows.
--   L2: Multi-bar structure/context. Requires explicit window_spec.
--
-- Schema: derived (not ovc - B-layer is LOCKED)
-- Idempotency: All tables use ON CONFLICT DO UPDATE for reruns

CREATE SCHEMA IF NOT EXISTS derived;

--------------------------------------------------------------------------------
-- DERIVED_RUNS_V0_1: Run metadata for provenance tracking
--------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS derived.derived_runs_v0_1 (
    run_id              UUID PRIMARY KEY,
    run_type            TEXT NOT NULL,              -- 'l1', 'l2', 'l3', etc.
    version             TEXT NOT NULL,              -- 'v0.1'
    formula_hash        TEXT NOT NULL,              -- MD5 hash of computation logic
    window_spec         TEXT,                       -- NULL for L1, required for L2+
    threshold_version   TEXT,                       -- NULL for L1/L2, required for L3
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    block_count         INTEGER,                    -- Number of blocks processed
    status              TEXT NOT NULL DEFAULT 'running', -- 'running', 'completed', 'failed'
    error_message       TEXT,
    config_snapshot     JSONB                       -- Runtime config for reproducibility
);

CREATE INDEX IF NOT EXISTS idx_derived_runs_v0_1_type_version 
    ON derived.derived_runs_v0_1(run_type, version);
CREATE INDEX IF NOT EXISTS idx_derived_runs_v0_1_started_at 
    ON derived.derived_runs_v0_1(started_at DESC);

--------------------------------------------------------------------------------
-- OVC_L1_FEATURES_V0_1: Single-bar OHLC primitives
--------------------------------------------------------------------------------
-- L1 KEEP set from metric_trial_log_noncanonical_v0.md Section E.1:
--   range, body, direction, ret, logret, body_ratio, close_pos, 
--   upper_wick, lower_wick, clv
--
-- All formulas depend ONLY on {o, h, l, c} of current block.
-- NO lookback, NO history, NO rolling windows.

CREATE TABLE IF NOT EXISTS derived.ovc_l1_features_v0_1 (
    -- Identity (FK to B-layer)
    block_id            TEXT PRIMARY KEY,
    
    -- Provenance
    run_id              UUID NOT NULL REFERENCES derived.derived_runs_v0_1(run_id),
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    formula_hash        TEXT NOT NULL,              -- MD5 of L1 formula set
    derived_version     TEXT NOT NULL DEFAULT 'v0.1',
    
    -- L1 Features: Single-bar OHLC primitives
    range               DOUBLE PRECISION NOT NULL,  -- h - l
    body                DOUBLE PRECISION NOT NULL,  -- abs(c - o)
    direction           INTEGER NOT NULL,           -- sign(c - o): 1, -1, 0
    ret                 DOUBLE PRECISION,           -- (c - o) / o (NULL if o=0)
    logret              DOUBLE PRECISION,           -- ln(c / o) (NULL if o<=0 or c<=0)
    body_ratio          DOUBLE PRECISION,           -- body / range (NULL if range=0)
    close_pos           DOUBLE PRECISION,           -- (c - l) / range (NULL if range=0)
    upper_wick          DOUBLE PRECISION NOT NULL,  -- h - max(o, c)
    lower_wick          DOUBLE PRECISION NOT NULL,  -- min(o, c) - l
    clv                 DOUBLE PRECISION,           -- ((c-l)-(h-c))/(h-l) (NULL if range=0)
    
    -- Diagnostics
    range_zero          BOOLEAN NOT NULL DEFAULT false,  -- Flag: range = 0
    inputs_valid        BOOLEAN NOT NULL DEFAULT true    -- Flag: all OHLC present and sane
);

CREATE INDEX IF NOT EXISTS idx_c1_features_v0_1_run_id 
    ON derived.ovc_l1_features_v0_1(run_id);

--------------------------------------------------------------------------------
-- OVC_L2_FEATURES_V0_1: Multi-bar structure & context
--------------------------------------------------------------------------------
-- L2 KEEP set from mapping_validation_report_v0.1.md Section 1.1 and 1.2:
--   gap (N=1), sess_high/low (session=date_ny), dist_sess_high/low,
--   roll_avg_range_12 (N=12), roll_std_logret_12 (N=12), range_z_12 (N=12),
--   hh_12 (N=12), ll_12 (N=12), took_prev_high/low (N=1),
--   rd_hi/rd_lo/rd_mid (parameterized=rd_len)
--
-- All features require explicit window_spec per c_layer_boundary_spec_v0.1.md.

CREATE TABLE IF NOT EXISTS derived.ovc_l2_features_v0_1 (
    -- Identity (FK to B-layer)
    block_id            TEXT PRIMARY KEY,
    
    -- Provenance
    run_id              UUID NOT NULL REFERENCES derived.derived_runs_v0_1(run_id),
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    formula_hash        TEXT NOT NULL,              -- MD5 of L2 formula set
    derived_version     TEXT NOT NULL DEFAULT 'v0.1',
    window_spec         TEXT NOT NULL,              -- Aggregated window specs for this row
    
    -- L2 Features: 1-bar lookback (window_spec: N=1)
    gap                 DOUBLE PRECISION,           -- o - prev_c
    took_prev_high      BOOLEAN,                    -- h > prev_h
    took_prev_low       BOOLEAN,                    -- l < prev_l
    
    -- L2 Features: Session context (window_spec: session=date_ny)
    sess_high           DOUBLE PRECISION,           -- Running max(h) within date_ny
    sess_low            DOUBLE PRECISION,           -- Running min(l) within date_ny
    dist_sess_high      DOUBLE PRECISION,           -- sess_high - c
    dist_sess_low       DOUBLE PRECISION,           -- c - sess_low
    
    -- L2 Features: Rolling 12-bar stats (window_spec: N=12)
    roll_avg_range_12   DOUBLE PRECISION,           -- avg(range) over 12 blocks
    roll_std_logret_12  DOUBLE PRECISION,           -- stddev(logret) over 12 blocks
    range_z_12          DOUBLE PRECISION,           -- (range - avg) / std
    
    -- L2 Features: 12-bar structure breaks (window_spec: N=12)
    hh_12               BOOLEAN,                    -- h > max(h[-12:-1])
    ll_12               BOOLEAN,                    -- l < min(l[-12:-1])
    
    -- L2 Features: Range detector numeric (window_spec: parameterized=rd_len)
    rd_len_used         INTEGER,                    -- rd_len parameter value used
    rd_hi               DOUBLE PRECISION,           -- highest(h, rd_len)
    rd_lo               DOUBLE PRECISION,           -- lowest(l, rd_len)
    rd_mid              DOUBLE PRECISION,           -- (rd_hi + rd_lo) / 2
    
    -- Diagnostics / Context metadata
    prev_block_exists   BOOLEAN NOT NULL DEFAULT false,  -- Has N=1 lookback data
    sess_block_count    INTEGER,                    -- Blocks in session so far
    roll_12_count       INTEGER,                    -- Blocks in N=12 window
    rd_count            INTEGER                     -- Blocks in rd_len window
);

CREATE INDEX IF NOT EXISTS idx_c2_features_v0_1_run_id 
    ON derived.ovc_l2_features_v0_1(run_id);

--------------------------------------------------------------------------------
-- COMMENTS: Document window_spec per feature family
--------------------------------------------------------------------------------
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.gap IS 'window_spec: N=1 (prev_c)';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.took_prev_high IS 'window_spec: N=1';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.took_prev_low IS 'window_spec: N=1';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.sess_high IS 'window_spec: session=date_ny';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.sess_low IS 'window_spec: session=date_ny';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.dist_sess_high IS 'window_spec: session=date_ny (inherits)';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.dist_sess_low IS 'window_spec: session=date_ny (inherits)';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.roll_avg_range_12 IS 'window_spec: N=12';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.roll_std_logret_12 IS 'window_spec: N=12';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.range_z_12 IS 'window_spec: N=12 (inherits)';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.hh_12 IS 'window_spec: N=12';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.ll_12 IS 'window_spec: N=12';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.rd_hi IS 'window_spec: parameterized=rd_len';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.rd_lo IS 'window_spec: parameterized=rd_len';
COMMENT ON COLUMN derived.ovc_l2_features_v0_1.rd_mid IS 'window_spec: parameterized=rd_len (derived)';
