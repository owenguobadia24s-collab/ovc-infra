CREATE TABLE IF NOT EXISTS public.ovc_blocks_detail_v01 (
  symbol text NOT NULL,
  block_start timestamptz NOT NULL,
  block_type text NOT NULL,
  schema_ver text NOT NULL,
  full_schema text NOT NULL DEFAULT 'OVC_FULL_V01',
  contract_version text NOT NULL DEFAULT '1.0.0',
  full_payload jsonb NOT NULL,
  ingested_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ovc_blocks_detail_v01_pk PRIMARY KEY (symbol, block_start, block_type, schema_ver)
);

CREATE INDEX IF NOT EXISTS ovc_blocks_detail_v01_sym_time_idx
  ON public.ovc_blocks_detail_v01 (symbol, block_start);
