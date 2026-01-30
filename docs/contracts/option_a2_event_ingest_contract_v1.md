# Option A2 -- Tick / Event Ingest Contract v1_0

**OPTION_A2_CONTRACT_VERSION**: v1.0
**Status**: ACTIVE
**Date**: 2026-01-29

---

## 1. Purpose & Non-Goals

### Purpose

Option A2 governs the ingest of event-level (sub-block) OHLC candle data
into the canonical table `ovc.ovc_candles_m15_raw`.

This contract defines:

- The complete field-level schema of the canonical M15 candle table.
- Mechanical normalization performed at ingest time.
- Validation rules that reject records.
- Idempotency guarantees and overwrite-by-reingest semantics.
- What any downstream consumer may assume about ingested data.

### Non-Goals

This contract MUST NOT govern:

- Block-level (2H) OHLC data (see Option A1).
- Feature derivation, classification, or inference (Option B).
- Market structure, session logic, or regime tagging (Option B/C).
- Heuristic cleaning or backfilled reinterpretation.
- Outcome computation (Option C).
- Evidence generation logic (Option D) -- A2 provides raw overlay data only.

---

## 2. Canonical Ingest Unit Definition

| Property | Value | Citation |
|----------|-------|----------|
| Grain | 15-minute (M15) candle | `sql/path1/db_patches/patch_m15_raw_20260122.sql:10` |
| Table | `ovc.ovc_candles_m15_raw` | `sql/path1/db_patches/patch_m15_raw_20260122.sql:10` |
| Primary Key | `(sym, bar_start_ms)` (composite) | `sql/path1/db_patches/patch_m15_raw_20260122.sql:24` |
| Candles per 2H block | 8 (theoretical maximum: 120 min / 15 min) | Derived from grain definition |
| Candles per session | 96 (theoretical maximum: 24h x 4 per hour) | Derived from grain definition |
| Data source | OANDA REST API (`M15` granularity) | `src/backfill_oanda_m15_checkpointed.py:235` |
| Pipeline ID | `P2-Backfill-M15` | `src/backfill_oanda_m15_checkpointed.py:43` |
| Created | 2026-01-22 | `sql/path1/db_patches/patch_m15_raw_20260122.sql:5` |

---

## 3. Schema (field-by-field)

The A2 table stores raw OHLCV data only.  It contains NO mechanically
derived fields (`rng`, `body`, `dir`, `ret` do NOT exist in A2).

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `sym` | TEXT | -- | NOT NULL | Symbol string (e.g. `GBPUSD`), uppercase | IMPLEMENTED -- `patch_m15_raw_20260122.sql:11` |
| `tz` | TEXT | -- | NOT NULL, DEFAULT `'America/New_York'` | Timezone reference | IMPLEMENTED -- `patch_m15_raw_20260122.sql:12` |
| `bar_start_ms` | BIGINT | milliseconds | NOT NULL (composite PK) | UTC epoch milliseconds of candle open | IMPLEMENTED -- `patch_m15_raw_20260122.sql:13` |
| `bar_close_ms` | BIGINT | milliseconds | NOT NULL | UTC epoch milliseconds of candle close (`bar_start_ms + 900000`) | IMPLEMENTED -- `patch_m15_raw_20260122.sql:14` |
| `o` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw open price from external source | IMPLEMENTED -- `patch_m15_raw_20260122.sql:15` |
| `h` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw high price from external source | IMPLEMENTED -- `patch_m15_raw_20260122.sql:16` |
| `l` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw low price from external source | IMPLEMENTED -- `patch_m15_raw_20260122.sql:17` |
| `c` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw close price from external source | IMPLEMENTED -- `patch_m15_raw_20260122.sql:18` |
| `volume` | BIGINT | -- | NULL | Tick volume from OANDA (null if unavailable) | IMPLEMENTED -- `patch_m15_raw_20260122.sql:19` |
| `source` | TEXT | -- | NOT NULL | Ingest source identifier (e.g. `oanda`) | IMPLEMENTED -- `patch_m15_raw_20260122.sql:20` |
| `build_id` | TEXT | -- | NOT NULL | Build/pipeline identifier (e.g. `oanda_backfill_m15_v0.1`) | IMPLEMENTED -- `patch_m15_raw_20260122.sql:21` |
| `payload` | JSONB | -- | NOT NULL | Raw ingest metadata (instrument, granularity, timestamps, parsed values) | IMPLEMENTED -- `patch_m15_raw_20260122.sql:22` |
| `ingest_ts` | TIMESTAMPTZ | microseconds | NOT NULL, DEFAULT `now()` | Server-side timestamp at insert/upsert time | IMPLEMENTED -- `patch_m15_raw_20260122.sql:23` |

### Indexes

| Index | Columns | Citation |
|-------|---------|----------|
| PRIMARY KEY | `(sym, bar_start_ms)` | `patch_m15_raw_20260122.sql:24` |
| `idx_ovc_candles_m15_raw_sym_start` | `(sym, bar_start_ms)` | `patch_m15_raw_20260122.sql:27-28` |
| `idx_ovc_candles_m15_raw_sym_close` | `(sym, bar_close_ms)` | `patch_m15_raw_20260122.sql:30-31` |

### Explicit: No Derived Fields

The A2 schema does NOT contain and MUST NOT be extended with mechanically
derived fields (`rng`, `body`, `dir`, `ret`).  Any consumer requiring
these computations MUST perform them from the raw `o`, `h`, `l`, `c`
values at read time.

---

## 4. Temporal Semantics

| Property | Rule | Citation |
|----------|------|----------|
| Candle duration | Exactly 15 minutes (900 seconds / 900000 ms) | `src/backfill_oanda_m15_checkpointed.py:284` |
| `bar_start_ms` | UTC epoch milliseconds of candle open time | `src/backfill_oanda_m15_checkpointed.py:286` |
| `bar_close_ms` | `bar_start_ms + 900000` (15 min in ms) | `src/backfill_oanda_m15_checkpointed.py:287` |
| Timezone reference | `tz` defaults to `America/New_York` | `patch_m15_raw_20260122.sql:12`, `src/backfill_oanda_m15_checkpointed.py:303` |
| OANDA granularity | `M15` candles fetched directly (no aggregation) | `src/backfill_oanda_m15_checkpointed.py:235` |
| Incomplete candle filter | Only `complete: true` candles from OANDA are ingested | `src/backfill_oanda_m15_checkpointed.py:244` |
| Deduplication at source | DataFrame `drop_duplicates(subset=["time"])` before processing | `src/backfill_oanda_m15_checkpointed.py:265` |
| Session boundary | No session boundary enforcement for M15 candles (continuous timeline) | No session logic in M15 backfill script |

---

## 5. Normalization Rules (mechanical only)

| Rule | Formula / Logic | Citation |
|------|-----------------|----------|
| Symbol normalization | Uppercase: `symbol.upper()` | `src/backfill_oanda_m15_checkpointed.py:278` |
| OANDA instrument mapping | Configurable via `--instrument` CLI arg, default `GBP_USD` | `src/backfill_oanda_m15_checkpointed.py:61` |
| OANDA mid-price extraction | Uses `mid` price object (`mid.o`, `mid.h`, `mid.l`, `mid.c`) | `src/backfill_oanda_m15_checkpointed.py:247-254` |
| Timestamp to ms conversion | `int(ts_start_utc.timestamp() * 1000)` | `src/backfill_oanda_m15_checkpointed.py:286` |
| Volume handling | `int(volume)` if present, `None` if missing or NaN | `src/backfill_oanda_m15_checkpointed.py:295-299` |
| UTC timezone enforcement | `ts_start_utc.replace(tzinfo=timezone.utc)` if naive | `src/backfill_oanda_m15_checkpointed.py:282-283` |

---

## 6. Idempotency & Overwrite-by-Reingest Semantics

### 6.1 Identity-Level Immutability

The composite key `(sym, bar_start_ms)` for a given M15 candle is
deterministic and stable: it is derived from the symbol and the UTC epoch
millisecond of the candle open.  Once assigned, this identity MUST NOT
change.

### 6.2 Row Content Overwrite-by-Reingest

Row contents (all non-PK columns) MAY be overwritten by a subsequent ingest
of the same `(sym, bar_start_ms)`.

| Path | Upsert mechanism | Citation |
|------|------------------|----------|
| OANDA M15 backfill | `ON CONFLICT (sym, bar_start_ms) DO UPDATE SET bar_close_ms, o, h, l, c, volume, source, build_id, payload, ingest_ts = now()` | `src/backfill_oanda_m15_checkpointed.py:86-104` |

This means:

- Multiple runs with the same source data produce identical DB state.
- `ingest_ts` reflects the timestamp of the most recent write, not the
  original insert.
- Re-ingesting corrected source data for a given candle replaces the
  prior row contents without creating a new row.

### 6.3 Dry-Run Mode

The M15 backfill script supports `--dry-run`, which fetches and builds rows
but skips DB inserts.
Citation: `src/backfill_oanda_m15_checkpointed.py:174`,
`.github/workflows/backfill_m15.yml:71`.

---

## 7. Validation Rules (reject vs quarantine)

| Rule | Behavior | Citation |
|------|----------|----------|
| OHLC sanity: `h >= max(o,c)` AND `l <= min(o,c)` | ABORT (`SystemExit`) | `src/backfill_oanda_m15_checkpointed.py:178-182` |
| Incomplete candle | SKIP (not ingested) | `src/backfill_oanda_m15_checkpointed.py:244` |
| Duplicate timestamps in source | DROP via `drop_duplicates(subset=["time"])` | `src/backfill_oanda_m15_checkpointed.py:265` |
| Volume null/NaN | ACCEPT as NULL | `src/backfill_oanda_m15_checkpointed.py:296-297` |
| Window before BACKFILL_START_UTC | SKIP entire run | `src/backfill_oanda_m15_checkpointed.py:507-511` |

**Quarantine**: NOT IMPLEMENTED.  No quarantine mechanism exists.  Validation
failures either abort the run or skip the record.

**Webhook ingest for M15**: NOT IMPLEMENTED.  M15 data is ingested
exclusively via the Python backfill script.  There is no webhook endpoint
for M15 data.

---

## 8. Downstream Guarantees (what any consumer may assume)

Any downstream consumer (including but not limited to Option D Evidence Pack
builder) MAY assume the following about any row in
`ovc.ovc_candles_m15_raw`:

| Guarantee | Basis |
|-----------|-------|
| `(sym, bar_start_ms)` is unique | PRIMARY KEY constraint |
| `o`, `h`, `l`, `c` are non-null DOUBLE PRECISION | DDL `NOT NULL` constraint |
| `h >= max(o, c)` and `l <= min(o, c)` | OHLC sanity check at ingest |
| `bar_close_ms = bar_start_ms + 900000` | Computed at ingest time |
| `volume` MAY be NULL | DDL allows NULL |
| `source` and `build_id` are non-null | DDL `NOT NULL` constraint |
| `payload` contains JSONB metadata | DDL `NOT NULL` constraint |
| `ingest_ts` is populated | DEFAULT `now()` |
| Rows are idempotent per `(sym, bar_start_ms)` | `ON CONFLICT` upsert |
| No derived fields exist in A2 rows | Schema contains only raw OHLCV + provenance |

Option D is a common consumer of this table (for M15 overlay in evidence
packs).  Citation: `docs/contracts/A_TO_D_CONTRACT_v1.md:161`.

Any consumer MUST NOT assume:

- All M15 candles exist for every time range (gaps exist for weekends,
  holidays, or market closures).
- Volume is always present (it MAY be NULL).
- `rng`, `body`, `dir`, `ret` exist (these fields are NOT in the A2
  schema; consumers MUST compute them if needed).
- Session boundary alignment (M15 table has no session concept).

---

## 9. Explicit Exclusions

| Exclusion | Rationale | Citation |
|-----------|-----------|----------|
| Mechanically derived fields (`rng`, `body`, `dir`, `ret`) | Not present in A2 schema; A2 stores raw OHLCV only | `sql/path1/db_patches/patch_m15_raw_20260122.sql` -- no derived columns |
| Session boundary enforcement | M15 candles represent a continuous timeline; session logic belongs downstream | No session logic in `backfill_oanda_m15_checkpointed.py` |
| Block mapping | M15 candles are not mapped to 2H blocks; that mapping is a derived operation | Not present in A2 pipeline |
| Webhook ingest path | M15 data has no webhook endpoint | NOT IMPLEMENTED |
| TradingView CSV ingest for M15 | No CSV adapter exists for M15 granularity | NOT IMPLEMENTED |
| Feature derivation | All classifiers, state tags, and structure tags are Option B/C scope | `A_TO_D_CONTRACT_v1.md:49` |
| Cross-table reads | Option A MUST NOT read from derived or config tables | `A_TO_D_CONTRACT_v1.md:157-158` |
| Export string / MIN contract | A2 does not use the MIN export contract; it has no `export_str` or `scheme_min` field | `sql/path1/db_patches/patch_m15_raw_20260122.sql` |

---

## Alignment Confirmation

### Fully Aligned with Repo Reality

| Item | Evidence |
|------|----------|
| Schema matches `ovc.ovc_candles_m15_raw` DDL | `sql/path1/db_patches/patch_m15_raw_20260122.sql` -- all 13 columns verified |
| Upsert semantics match backfill script | `src/backfill_oanda_m15_checkpointed.py:86-104` |
| OHLC validation enforced | `_ensure_ohlc_sane()` in `src/backfill_oanda_m15_checkpointed.py:178-182` |
| Workflow matches script invocation | `.github/workflows/backfill_m15.yml:74` |
| No derived fields in DDL | Verified against `patch_m15_raw_20260122.sql` |
| Option D reads from this table | `A_TO_D_CONTRACT_v1.md:161` |

### Explicitly Deferred

| Item | Status | Rationale |
|------|--------|-----------|
| Webhook ingest for M15 data | NOT IMPLEMENTED | Only Python backfill exists |
| TradingView CSV ingest for M15 data | NOT IMPLEMENTED | No CSV adapter for M15 |
| Quarantine table for failed records | NOT IMPLEMENTED | No quarantine table in DDL or scripts |
| Scheduled cron for M15 backfill | NOT IMPLEMENTED | `.github/workflows/backfill_m15.yml` is manual dispatch only |
| SQL-level CHECK constraint for OHLC relationships | DEFERRED | Enforced only in application code |

### What Would BREAK This Contract If Changed

| Change | Impact |
|--------|--------|
| Changing composite PK from `(sym, bar_start_ms)` to another key | Breaks deduplication guarantee |
| Adding derived fields (`rng`, `body`, `dir`, `ret`) to DDL | Violates A2 "no derived fields" rule; consumers may begin depending on them |
| Removing `ON CONFLICT` upsert | Breaks idempotency; duplicate runs would fail |
| Changing `bar_close_ms` computation from `bar_start_ms + 900000` | Breaks temporal join assumptions |
| Removing OHLC sanity checks | Breaks downstream guarantee that `h >= max(o,c)` and `l <= min(o,c)` |
| Adding session-boundary enforcement to M15 ingest | Would reject valid candles spanning session boundaries; changes A2 contract |
