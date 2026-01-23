# Option A: Ingest Contract v1

**Version**: 1.0
**Status**: DRAFT
**Date**: 2026-01-23

---

## 1. Purpose

Option A ingests raw external data into canonical fact tables. It is the ONLY layer permitted to write to canonical tables.

---

## 2. Inputs (Authoritative Sources)

| Source | Type | Mechanism |
|--------|------|-----------|
| TradingView | Webhook payload | Cloudflare Worker |
| OANDA API | REST API | Python backfill scripts |
| Historical CSV | Local files | Python ingest scripts |

---

## 3. Outputs (Data Products)

| Table | Schema | Description |
|-------|--------|-------------|
| `ovc.ovc_blocks_v01_1_min` | Canonical | 2H block OHLC facts |
| `ovc.ovc_candles_m15_raw` | Canonical | M15 raw candles |
| R2 Bucket `tv/YYYY-MM-DD/` | Blob | Raw TradingView payloads |

---

## 4. Canonical vs Derived Rules

### 4.1 ALLOWED in Canonical Tables

```
block_id          -- Unique identifier (YYYYMMDD-X-SYM format)
sym               -- Symbol (e.g., GBPUSD)
date_ny           -- NY session date
block2h           -- Block letter (A-L)
block4h           -- 4H grouping
bar_close_ms      -- Bar close epoch milliseconds
o, h, l, c        -- Raw OHLC prices
rng               -- Range (h - l) [computed from raw]
ret               -- Return (c/o - 1) [computed from raw]
volume            -- Volume if available
```

### 4.2 PROHIBITED in Canonical Tables

```
state_tag         -- VIOLATION: C2/C3 derived
trend_tag         -- VIOLATION: C2/C3 derived
pred_dir          -- VIOLATION: C3 derived
bias_dir          -- VIOLATION: C3 derived
struct_state      -- VIOLATION: C2 derived
event             -- VIOLATION: C2 derived
value_tag         -- VIOLATION: C2 derived
state_key         -- VIOLATION: C2 derived
```

**v1 Resolution**: These fields currently exist in `ovc.ovc_blocks_v01_1_min`. They are **DEPRECATED** and MUST NOT be written by new ingest code. Future migration will move them to derived tables.

---

## 5. Versioning & Naming

- Canonical table names include version: `ovc_blocks_v01_1_min`
- R2 bucket paths use date: `tv/YYYY-MM-DD/HH-MM-SS_uuid.json`

---

## 6. Run Provenance

| Mechanism | Run ID Format | Output Location |
|-----------|---------------|-----------------|
| Worker | `tv_{timestamp}_{uuid}` | R2 bucket + DB |
| Backfill | `bf_{YYYYMMDD}_{seq}` | `reports/runs/<run_id>/` |

---

## 7. Allowed Dependencies

| Dependency | Allowed |
|------------|---------|
| External sources | ✅ |
| Other canonical tables | ❌ (except for dedup check) |
| Derived tables | ❌ |
| Configuration tables | ❌ |

---

## 8. Idempotency & Deduplication

- Worker MUST reject duplicate `block_id` inserts
- Backfill MUST use upsert with idempotent semantics
- OHLC sanity checks MUST be enforced (h >= max(o,c), l <= min(o,c))

---

## 9. Compliance Checklist

| # | Requirement | Verified By |
|---|-------------|-------------|
| 1 | No derived fields written to canonical | Code review |
| 2 | Duplicate rejection enforced | Test case |
| 3 | OHLC sanity enforced | Test case |
| 4 | Raw payload archived to R2 | Worker logs |
| 5 | Run ID included in reports | Manifest check |
