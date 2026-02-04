-- OVC v0.1-min schema (historical + live-compatible)

CREATE TABLE IF NOT EXISTS ovc_blocks_v01 (
  schema_ver     TEXT        NOT NULL,        -- e.g. 'v0.1-min'
  source         TEXT        NOT NULL,        -- e.g. 'oanda' | 'dukascopy' | 'tv'
  symbol         TEXT        NOT NULL,        -- e.g. 'GBPUSD'
  block_type     TEXT        NOT NULL,        -- '2H' (Step 1 scope)
  block_start    TIMESTAMPTZ NOT NULL,        -- start of the 2H bar (UTC)
  bid            TEXT,                        -- TradingView block id (if present)
  export_min     TEXT,                        -- raw MIN export string
  payload_min    JSONB,                       -- parsed MIN payload

  open           NUMERIC(18,8) NOT NULL,
  high           NUMERIC(18,8) NOT NULL,
  low            NUMERIC(18,8) NOT NULL,
  close          NUMERIC(18,8) NOT NULL,
  volume         BIGINT,                     -- can be null if provider doesn't supply

  ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Idempotency key (this is the spine)
  CONSTRAINT ovc_blocks_v01_pk PRIMARY KEY (symbol, block_start, block_type, schema_ver)
);

-- Helpful index for time-range queries per instrument
CREATE INDEX IF NOT EXISTS ovc_blocks_v01_sym_time_idx
  ON ovc_blocks_v01 (symbol, block_start);

-- Optional: helps fast filtering by type/version
CREATE INDEX IF NOT EXISTS ovc_blocks_v01_type_ver_idx
  ON ovc_blocks_v01 (block_type, schema_ver);
