# OVC Decisions Log

## 2026-01-14
- Implemented OANDA → resample 2H → Neon insert (idempotent).
- Primary key: (symbol, block_start, block_type, schema_ver).
- Chunked OANDA fetch via OANDA_SLICE_DAYS to avoid candle limits.
