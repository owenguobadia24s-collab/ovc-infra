# Step 8B Readiness (Ingestion + Storage Hardening)

## Canonical tables

- **Core (MIN)**: `public.ovc_blocks_v01`
- **Detail (FULL, cold path)**: `public.ovc_blocks_detail_v01`

## TradingView webhook: switch to `/tv_secure`

1. **Update webhook URL** in TradingView to point to `/tv_secure` (instead of `/tv`).
2. **Send JSON envelope** (MIN-only) with the secret token:

```json
{
  "schema": "OVC_MIN_V01",
  "contract_version": "1.0.0",
  "token": "${OVC_TOKEN}",
  "export": "ver=1|sym=GBPUSD|bar_close_ms=1700000000000|bid=...|..."
}
```

Notes:
- `/tv_secure` rejects non-JSON bodies, schemas other than `OVC_MIN_V01`, and invalid tokens.
- `/tv` remains available for plain export testing (no token required).

## Readiness SQL queries

### a) Latest TradingView rows
```sql
SELECT *
FROM ovc_blocks_v01
WHERE source IN ('tv_plain', 'tv_secure')
ORDER BY ingested_at DESC
LIMIT 50;
```

### b) Rows per source per day
```sql
SELECT
  date_trunc('day', ingested_at) AS day,
  source,
  COUNT(*) AS rows
FROM ovc_blocks_v01
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

### c) Count where OHLC is null (waiting for backfill)
```sql
SELECT COUNT(*) AS missing_ohlc
FROM ovc_blocks_v01
WHERE open IS NULL
   OR high IS NULL
   OR low IS NULL
   OR close IS NULL
   OR volume IS NULL;
```

### d) Latest FULL detail rows
```sql
SELECT *
FROM ovc_blocks_detail_v01
ORDER BY ingested_at DESC
LIMIT 50;
```

## Replay raw events from R2 (conceptual)

1. **List** raw event objects for a date prefix (e.g., `tv/2025-02-15/`).
2. **Download** the raw body files from the bucket.
3. **Repost** the raw bodies back to `/tv` or `/tv_secure` for re-ingestion.
4. If only backfill is needed, parse raw exports and upsert into `ovc_blocks_v01`.

This ensures zero data loss and allows deterministic replays for audits or recovery.
