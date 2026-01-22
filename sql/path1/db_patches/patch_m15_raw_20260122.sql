-- =============================================================================
-- DB PATCH: Create OVC M15 Raw Candle Cache (Fork A)
-- =============================================================================
-- Purpose: Cache OANDA M15 candles in Neon for Evidence Pack v0.2 builder.
-- Created: 2026-01-22
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS ovc.ovc_candles_m15_raw (
    sym TEXT NOT NULL,
    tz TEXT NOT NULL DEFAULT 'America/New_York',
    bar_start_ms BIGINT NOT NULL,
    bar_close_ms BIGINT NOT NULL,
    o DOUBLE PRECISION NOT NULL,
    h DOUBLE PRECISION NOT NULL,
    l DOUBLE PRECISION NOT NULL,
    c DOUBLE PRECISION NOT NULL,
    volume BIGINT NULL,
    source TEXT NOT NULL,
    build_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    ingest_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (sym, bar_start_ms)
);

CREATE INDEX IF NOT EXISTS idx_ovc_candles_m15_raw_sym_start
    ON ovc.ovc_candles_m15_raw (sym, bar_start_ms);

CREATE INDEX IF NOT EXISTS idx_ovc_candles_m15_raw_sym_close
    ON ovc.ovc_candles_m15_raw (sym, bar_close_ms);

COMMIT;
