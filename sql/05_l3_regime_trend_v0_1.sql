-- OVC L3 Regime Trend Classifier (v0.1)
-- Migration: 05_c3_regime_trend_v0_1.sql
-- Purpose: Store L3 regime trend classifications derived from L1/L2 features
--
-- L3 Tier Boundary:
--   L3 = Semantic tags derived from L1/L2 features + threshold packs.
--   All semantic decisions come from versioned threshold packs in ovc_cfg.
--   Every row stores threshold provenance for replay certification.
--
-- Usage:
--   psql $NEON_DSN -f sql/05_c3_regime_trend_v0_1.sql

-- ============================================================================
-- TABLE: L3 Regime Trend Classifications
-- ============================================================================

CREATE TABLE IF NOT EXISTS derived.ovc_l3_regime_trend_v0_1 (
    -- Identity (joint FK to B-layer via block_id)
    block_id                TEXT        NOT NULL,
    symbol                  TEXT        NOT NULL,
    ts                      TIMESTAMPTZ NOT NULL,
    
    -- L3 Classification output
    l3_regime_trend         TEXT        NOT NULL,
    
    -- Threshold pack provenance (MANDATORY for replay certification)
    threshold_pack_id       TEXT        NOT NULL,
    threshold_pack_version  INT         NOT NULL,
    threshold_pack_hash     TEXT        NOT NULL,
    
    -- Compute run metadata
    run_id                  UUID        NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Constraints
    PRIMARY KEY (symbol, ts),
    
    -- L3 value validation
    CONSTRAINT chk_c3_regime_trend_valid CHECK (
        l3_regime_trend IN ('TREND', 'NON_TREND')
    ),
    
    -- Hash format validation (SHA256 = 64 hex chars)
    CONSTRAINT chk_threshold_pack_hash_format CHECK (
        threshold_pack_hash ~ '^[a-f0-9]{64}$'
    )
);

-- Alternate unique constraint on block_id (for joins)
CREATE UNIQUE INDEX IF NOT EXISTS idx_c3_regime_trend_block_id
ON derived.ovc_l3_regime_trend_v0_1 (block_id);

-- Index for threshold pack queries (audit, replay certification)
CREATE INDEX IF NOT EXISTS idx_c3_regime_trend_threshold_pack
ON derived.ovc_l3_regime_trend_v0_1 (threshold_pack_id, threshold_pack_version);

-- Index for run_id queries (compute run tracking)
CREATE INDEX IF NOT EXISTS idx_c3_regime_trend_run_id
ON derived.ovc_l3_regime_trend_v0_1 (run_id);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_c3_regime_trend_symbol_ts
ON derived.ovc_l3_regime_trend_v0_1 (symbol, ts DESC);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE derived.ovc_l3_regime_trend_v0_1 IS 
'L3 regime trend classifications (TREND/NON_TREND) derived from L1/L2 features using versioned threshold packs.';

COMMENT ON COLUMN derived.ovc_l3_regime_trend_v0_1.l3_regime_trend IS 
'Classification result: TREND (directional momentum) or NON_TREND (ranging/consolidating)';

COMMENT ON COLUMN derived.ovc_l3_regime_trend_v0_1.threshold_pack_id IS 
'ID of the threshold pack used for classification (from ovc_cfg.threshold_pack)';

COMMENT ON COLUMN derived.ovc_l3_regime_trend_v0_1.threshold_pack_version IS 
'Version of the threshold pack used (immutable once created)';

COMMENT ON COLUMN derived.ovc_l3_regime_trend_v0_1.threshold_pack_hash IS 
'SHA256 hash of the threshold config for replay certification';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'derived' 
        AND table_name = 'ovc_l3_regime_trend_v0_1'
    ) THEN
        RAISE EXCEPTION 'ovc_l3_regime_trend_v0_1 table not created';
    END IF;
    RAISE NOTICE 'L3 regime trend table (derived.ovc_l3_regime_trend_v0_1) created successfully';
END
$$;
