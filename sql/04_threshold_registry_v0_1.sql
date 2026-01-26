-- OVC Threshold Registry Schema (v0.1)
-- Migration: 04_threshold_registry_v0_1.sql
-- Purpose: Configuration registry for deterministic, versioned threshold packs
--
-- Design rationale:
--   - Threshold packs are IMMUTABLE once created (append-only versioning)
--   - Activation is a separate pointer that can be updated
--   - config_hash ensures deterministic replay certification
--   - scope (GLOBAL/SYMBOL/SYMBOL_TF) supports hierarchical overrides
--
-- Usage:
--   psql $NEON_DSN -f sql/04_threshold_registry_v0_1.sql

-- ============================================================================
-- SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ovc_cfg;

COMMENT ON SCHEMA ovc_cfg IS 'OVC configuration registry: threshold packs and versioned config';

-- ============================================================================
-- ENUM-LIKE CHECK CONSTRAINTS
-- ============================================================================

-- Valid scope values
-- GLOBAL: applies to all symbols/timeframes (symbol and timeframe must be NULL)
-- SYMBOL: applies to a specific symbol (symbol NOT NULL, timeframe NULL)
-- SYMBOL_TF: applies to a specific symbol+timeframe combination (both NOT NULL)

-- Valid status values
-- DRAFT: newly created, not yet activated
-- ACTIVE: currently active for at least one selector
-- DEPRECATED: previously active, now superseded

-- ============================================================================
-- TABLE: threshold_pack (immutable configuration versions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ovc_cfg.threshold_pack (
    -- Identity
    pack_id         TEXT        NOT NULL,
    pack_version    INT         NOT NULL,
    
    -- Scope definition
    scope           TEXT        NOT NULL,
    symbol          TEXT        NULL,
    timeframe       TEXT        NULL,
    
    -- Configuration (immutable once created)
    config_json     JSONB       NOT NULL,
    config_hash     TEXT        NOT NULL,  -- sha256 hex of canonical JSON
    
    -- Lifecycle
    status          TEXT        NOT NULL DEFAULT 'DRAFT',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      TEXT        NULL,
    note            TEXT        NULL,
    
    -- Constraints
    PRIMARY KEY (pack_id, pack_version),
    
    -- Scope validation
    CONSTRAINT chk_scope_valid CHECK (scope IN ('GLOBAL', 'SYMBOL', 'SYMBOL_TF')),
    
    -- Status validation
    CONSTRAINT chk_status_valid CHECK (status IN ('DRAFT', 'ACTIVE', 'DEPRECATED')),
    
    -- Scope implies required fields
    CONSTRAINT chk_scope_global CHECK (
        scope != 'GLOBAL' OR (symbol IS NULL AND timeframe IS NULL)
    ),
    CONSTRAINT chk_scope_symbol CHECK (
        scope != 'SYMBOL' OR (symbol IS NOT NULL AND timeframe IS NULL)
    ),
    CONSTRAINT chk_scope_symbol_tf CHECK (
        scope != 'SYMBOL_TF' OR (symbol IS NOT NULL AND timeframe IS NOT NULL)
    ),
    
    -- Hash must be 64-char hex (sha256)
    CONSTRAINT chk_config_hash_format CHECK (
        config_hash ~ '^[a-f0-9]{64}$'
    )
);

-- ============================================================================
-- TABLE: threshold_pack_active (mutable activation pointers)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ovc_cfg.threshold_pack_active (
    -- Selector (unique key for activation lookup)
    pack_id         TEXT        NOT NULL,
    scope           TEXT        NOT NULL,
    symbol          TEXT        NOT NULL DEFAULT '',  -- empty string for NULL (GLOBAL scope)
    timeframe       TEXT        NOT NULL DEFAULT '',  -- empty string for NULL
    
    -- Active version pointer
    active_version  INT         NOT NULL,
    active_hash     TEXT        NOT NULL,  -- denormalized for fast lookup
    
    -- Audit
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    -- Composite primary key
    PRIMARY KEY (pack_id, scope, symbol, timeframe),
    
    -- Scope validation (same rules as threshold_pack)
    CONSTRAINT chk_active_scope_valid CHECK (scope IN ('GLOBAL', 'SYMBOL', 'SYMBOL_TF')),
    
    CONSTRAINT chk_active_scope_global CHECK (
        scope != 'GLOBAL' OR (symbol = '' AND timeframe = '')
    ),
    CONSTRAINT chk_active_scope_symbol CHECK (
        scope != 'SYMBOL' OR (symbol != '' AND timeframe = '')
    ),
    CONSTRAINT chk_active_scope_symbol_tf CHECK (
        scope != 'SYMBOL_TF' OR (symbol != '' AND timeframe != '')
    ),
    
    -- Hash format validation
    CONSTRAINT chk_active_hash_format CHECK (
        active_hash ~ '^[a-f0-9]{64}$'
    )
);

-- Note: We enforce referential integrity at application level rather than FK
-- because the FK would need to match (pack_id, pack_version) but we store
-- active_version. The registry module validates this on activate_pack().

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Fast lookup by pack_id and status
CREATE INDEX IF NOT EXISTS idx_threshold_pack_id_status 
ON ovc_cfg.threshold_pack (pack_id, status);

-- Fast lookup by scope selector
CREATE INDEX IF NOT EXISTS idx_threshold_pack_scope 
ON ovc_cfg.threshold_pack (pack_id, scope, symbol, timeframe);

-- Hash lookup (for integrity checks)
CREATE INDEX IF NOT EXISTS idx_threshold_pack_hash 
ON ovc_cfg.threshold_pack (config_hash);

-- Active pointer lookup (already covered by PK, but explicit for clarity)
CREATE INDEX IF NOT EXISTS idx_threshold_pack_active_lookup 
ON ovc_cfg.threshold_pack_active (pack_id, scope, symbol, timeframe);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE ovc_cfg.threshold_pack IS 
'Immutable configuration packs with versioning. Each (pack_id, pack_version) is unique and immutable once created.';

COMMENT ON COLUMN ovc_cfg.threshold_pack.pack_id IS 
'Logical identifier for a threshold pack (e.g., l3_reversal_thresholds)';

COMMENT ON COLUMN ovc_cfg.threshold_pack.pack_version IS 
'Version number, monotonically increasing per pack_id';

COMMENT ON COLUMN ovc_cfg.threshold_pack.scope IS 
'GLOBAL = all symbols, SYMBOL = specific symbol, SYMBOL_TF = symbol+timeframe';

COMMENT ON COLUMN ovc_cfg.threshold_pack.config_json IS 
'Threshold configuration as JSONB. Keys should be threshold names, values integers (basis points preferred).';

COMMENT ON COLUMN ovc_cfg.threshold_pack.config_hash IS 
'SHA256 hex hash of canonical JSON. Ensures deterministic replay.';

COMMENT ON COLUMN ovc_cfg.threshold_pack.status IS 
'DRAFT = not yet activated, ACTIVE = currently in use, DEPRECATED = superseded';

COMMENT ON TABLE ovc_cfg.threshold_pack_active IS 
'Mutable pointers to currently active threshold pack versions. One active version per (pack_id, scope, symbol, timeframe) selector.';

COMMENT ON COLUMN ovc_cfg.threshold_pack_active.active_hash IS 
'Denormalized config_hash for fast integrity checks without joining';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ovc_cfg' AND table_name = 'threshold_pack') THEN
        RAISE EXCEPTION 'threshold_pack table not created';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ovc_cfg' AND table_name = 'threshold_pack_active') THEN
        RAISE EXCEPTION 'threshold_pack_active table not created';
    END IF;
    RAISE NOTICE 'Threshold registry schema (ovc_cfg) created successfully';
END
$$;
