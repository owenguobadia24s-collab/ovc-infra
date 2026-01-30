# Option A1 -- Bar Ingest Contract v1_0

**OPTION_A1_CONTRACT_VERSION**: v1.0
**MIN_EXPORT_SCHEMA_VERSION**: 0.1.1
**MIN_EXPORT_SCHEMA_ID**: export_contract_v0.1_min_r1
**Status**: ACTIVE
**Date**: 2026-01-29

---

## 1. Purpose & Non-Goals

### Purpose

Option A1 governs the ingest of time-bucketed OHLC bar data into the
canonical table `ovc.ovc_blocks_v01_1_min`.

This contract defines:

- The complete field-level schema of the canonical bar table.
- Mechanical normalization performed at ingest time.
- Validation rules that reject records.
- Idempotency guarantees and overwrite-by-reingest semantics.
- What downstream consumers (Option B) may assume about ingested data.

### Non-Goals

This contract MUST NOT govern:

- Event-level or sub-block data (see Option A2).
- Feature derivation, classification, or inference (Option B).
- Market structure, session logic, or regime tagging (Option B/C).
- Heuristic cleaning or backfilled reinterpretation.
- Outcome computation (Option C).
- Evidence generation (Option D).

---

## 2. Version Domains

This contract tracks three independent version identifiers.
They MUST NOT be conflated.

| Domain | Identifier | Current Value | Citation |
|--------|------------|---------------|----------|
| A1 Contract version | `OPTION_A1_CONTRACT_VERSION` | `v1.0` | This document |
| MIN export schema version | `MIN_EXPORT_SCHEMA_VERSION` | `0.1.1` | `contracts/export_contract_v0.1.1_min.json` meta.status=IMMUTABLE |
| MIN export schema ID | `MIN_EXPORT_SCHEMA_ID` | `export_contract_v0.1_min_r1` | `contracts/export_contract_v0.1.1_min.json:2`, `infra/ovc-webhook/src/index.ts:54` |

- The A1 contract version governs the policy and field classification in
  this document.
- The MIN export schema version and ID govern the wire format accepted by
  the webhook and used to build `export_str`.  They are IMMUTABLE per
  `contracts/export_contract_v0.1.1_min.json:4`.
- Bumping the A1 contract version does NOT require bumping the MIN schema
  version, and vice versa.

---

## 3. Canonical Ingest Unit Definition

| Property | Value | Citation |
|----------|-------|----------|
| Grain | 2-hour (2H) block | `sql/01_tables_min.sql` -- `block2h` column |
| Table | `ovc.ovc_blocks_v01_1_min` | `sql/01_tables_min.sql:1` |
| Primary Key | `block_id` (TEXT) | `sql/01_tables_min.sql:3` |
| Block ID Format | `YYYYMMDD-X-SYMBOL` (e.g. `20260116-I-GBPUSD`) | `src/backfill_oanda_2h_checkpointed.py:402` |
| Session Reference | NY session (17:00 ET to 17:00 ET next day) | `src/backfill_oanda_2h_checkpointed.py:361-362` |
| Blocks per Session | 12 (A through L) | `src/backfill_oanda_2h_checkpointed.py:68` |
| 4H Groupings | AB, CD, EF, GH, IJ, KL | `src/backfill_oanda_2h_checkpointed.py:69` |

### Accepted Input Modes

A1 accepts 2H bars via either:

1. **Direct 2H source bars** -- bars already at 2H granularity from the
   external source (e.g. TradingView webhook, TradingView CSV history).
   - Citation: `infra/ovc-webhook/src/index.ts` (webhook path),
     `src/ingest_history_day.py` (CSV history path).

2. **Deterministic aggregation of two complete H1 bars** -- the OANDA
   backfill pipeline fetches H1 candles and aggregates consecutive pairs
   into 2H blocks.  Aggregation rule: `open` = first H1 open,
   `high` = max of H1 highs, `low` = min of H1 lows,
   `close` = last H1 close.  Only blocks with exactly 2 H1 candles are
   emitted; incomplete blocks are dropped.
   - Citation: `src/backfill_oanda_2h_checkpointed.py:371-381`.

Both modes produce identical row shapes and are subject to the same
validation and upsert semantics.

---

## 4. Schema (field-by-field)

### 4.1 Identity Fields

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `block_id` | TEXT | -- | NOT NULL (PK) | Computed: `YYYYMMDD-X-SYMBOL` | IMPLEMENTED -- `sql/01_tables_min.sql:3` |
| `sym` | TEXT | -- | NOT NULL | External source symbol (e.g. `GBPUSD`) | IMPLEMENTED -- `sql/01_tables_min.sql:4` |
| `tz` | TEXT | -- | NOT NULL | Always `America/New_York` | IMPLEMENTED -- `sql/01_tables_min.sql:5` |
| `date_ny` | DATE | -- | NOT NULL | NY session date | IMPLEMENTED -- `sql/01_tables_min.sql:6` |
| `bar_close_ms` | BIGINT | milliseconds | NOT NULL | UTC epoch ms of block close | IMPLEMENTED -- `sql/01_tables_min.sql:7` |
| `block2h` | TEXT | -- | NOT NULL | Block letter A-L | IMPLEMENTED -- `sql/01_tables_min.sql:8` |
| `block4h` | TEXT | -- | NOT NULL | 4H grouping (AB, CD, EF, GH, IJ, KL) | IMPLEMENTED -- `sql/01_tables_min.sql:9` |

### 4.2 Governance Fields

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `ver` | TEXT | -- | NOT NULL | Contract version string (e.g. `ovc_v0.1.0`) | IMPLEMENTED -- `sql/01_tables_min.sql:12` |
| `profile` | TEXT | -- | NOT NULL | Profile name (e.g. `MIN`) | IMPLEMENTED -- `sql/01_tables_min.sql:13` |
| `scheme_min` | TEXT | -- | NOT NULL | Schema identifier (e.g. `export_contract_v0.1_min_r1`) | IMPLEMENTED -- `sql/01_tables_min.sql:14` |

### 4.3 OHLC Fields (Canonical Fact)

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `o` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw open price from external source | IMPLEMENTED -- `sql/01_tables_min.sql:17` |
| `h` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw high price from external source | IMPLEMENTED -- `sql/01_tables_min.sql:18` |
| `l` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw low price from external source | IMPLEMENTED -- `sql/01_tables_min.sql:19` |
| `c` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | Raw close price from external source | IMPLEMENTED -- `sql/01_tables_min.sql:20` |

### 4.4 Mechanically Derived Price Fields

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `rng` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | `h - l` | IMPLEMENTED -- `sql/01_tables_min.sql:23`, `src/backfill_oanda_2h_checkpointed.py:411` |
| `body` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | `abs(c - o)` | IMPLEMENTED -- `sql/01_tables_min.sql:24`, `src/backfill_oanda_2h_checkpointed.py:412` |
| `dir` | INTEGER | -- | NOT NULL | `1` if `c > o`, `-1` if `c < o`, `0` if `c == o` | IMPLEMENTED -- `sql/01_tables_min.sql:25`, `src/backfill_oanda_2h_checkpointed.py:413` |
| `ret` | DOUBLE PRECISION | ~15 significant digits | NOT NULL | `(c - o) / o` (0.0 if `o == 0`) | IMPLEMENTED -- `sql/01_tables_min.sql:26`, `src/backfill_oanda_2h_checkpointed.py:414` |

### 4.5 Non-Authoritative Fields (Legacy Physical Presence)

The following fields exist physically in the DDL and are populated by all
current ingest paths.  They are classified as **non-authoritative canonical
fact**: they occupy columns in the canonical table, but downstream consumers
MUST NOT treat their values as meaningful input.

- The **webhook** path writes source-provided values for these fields.
- The **OANDA backfill** and **CSV history** paths write placeholder values
  (`"UNKNOWN"`, `0`, `0.0`, `False`, `"NEUTRAL"`).
  Citation: `src/backfill_oanda_2h_checkpointed.py:435-466`,
  `src/ingest_history_day.py:321-352`.
- Per `docs/contracts/option_a_ingest_contract_v1.md:55-65` and
  `docs/contracts/A_TO_D_CONTRACT_v1.md:49`, these fields are PROHIBITED
  from being used as canonical fact.  Future migration will relocate them
  to derived tables.

| Name | SQL Type | Nullability | Note |
|------|----------|-------------|------|
| `state_tag` | TEXT | NOT NULL | Non-authoritative |
| `value_tag` | TEXT | NOT NULL | Non-authoritative |
| `event` | TEXT | NULL | Non-authoritative |
| `tt` | INTEGER | NOT NULL | Non-authoritative |
| `cp_tag` | TEXT | NOT NULL | Non-authoritative |
| `tis` | INTEGER | NULL | Non-authoritative |
| `rrc` | DOUBLE PRECISION | NOT NULL | Non-authoritative |
| `vrc` | DOUBLE PRECISION | NOT NULL | Non-authoritative |
| `trend_tag` | TEXT | NOT NULL | Non-authoritative |
| `struct_state` | TEXT | NOT NULL | Non-authoritative |
| `space_tag` | TEXT | NOT NULL | Non-authoritative |
| `htf_stack` | TEXT | NULL | Non-authoritative |
| `with_htf` | BOOLEAN | NOT NULL | Non-authoritative |
| `rd_state` | TEXT | NULL | Non-authoritative |
| `regime_tag` | TEXT | NULL | Non-authoritative |
| `trans_risk` | TEXT | NULL | Non-authoritative |
| `bias_mode` | TEXT | NOT NULL | Non-authoritative |
| `bias_dir` | TEXT | NOT NULL, CHECK `IN ('UP','DOWN','NEUTRAL')` | Non-authoritative |
| `perm_state` | TEXT | NOT NULL | Non-authoritative |
| `rail_loc` | TEXT | NULL | Non-authoritative |
| `tradeable` | BOOLEAN | NOT NULL | Non-authoritative |
| `conf_l3` | TEXT | NOT NULL | Non-authoritative |
| `play` | TEXT | NOT NULL | Non-authoritative |
| `pred_dir` | TEXT | NOT NULL, CHECK `IN ('UP','DOWN','NEUTRAL')` | Non-authoritative |
| `pred_target` | TEXT | NULL | Non-authoritative |
| `timebox` | TEXT | NOT NULL | Non-authoritative |
| `invalidation` | TEXT | NULL | Non-authoritative |

**Downstream rule**: Option B, C, D, and QA layers MUST NOT read these
fields from `ovc.ovc_blocks_v01_1_min` as authoritative input.  If a
consumer requires the semantic content these fields once represented, it
MUST obtain that content from derived tables (Option B outputs).

### 4.6 Provenance Fields

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `source` | TEXT | -- | NOT NULL | Ingest source identifier (e.g. `oanda`, `tv_webhook`, `tv_csv_history`) | IMPLEMENTED -- `sql/01_tables_min.sql:64` |
| `build_id` | TEXT | -- | NOT NULL | Build/pipeline identifier (e.g. `oanda_backfill_v0.1`, `ovc_pine_0.1.0`) | IMPLEMENTED -- `sql/01_tables_min.sql:65` |
| `note` | TEXT | -- | NULL | Free-text annotation | IMPLEMENTED -- `sql/01_tables_min.sql:66` |
| `ready` | BOOLEAN | -- | NOT NULL | Source-provided readiness flag (see 4.7) | IMPLEMENTED -- `sql/01_tables_min.sql:67` |

### 4.7 `ready` Field Semantics

The `ready` field is a BOOLEAN, NOT NULL, set by the ingest source at write
time.

- The **webhook** path writes the value provided by the source payload
  (`0` or `1`, coerced to boolean).
  Citation: `infra/ovc-webhook/src/index.ts:131` (type `bool_01`),
  `infra/ovc-webhook/src/index.ts:623`.
- The **OANDA backfill** path writes `True` unconditionally.
  Citation: `src/backfill_oanda_2h_checkpointed.py:465`.
- The **CSV history** path writes `True` unconditionally.
  Citation: `src/ingest_history_day.py:351`.

`ready` indicates the source considered the record complete at export time.
It does NOT imply quarantine, gating, or conditional visibility.  There is
no mechanism in the current codebase that filters rows by `ready = false`
before downstream consumption.  A `ready = false` row is stored identically
to a `ready = true` row.

**Quarantine**: NOT IMPLEMENTED.  No quarantine table or quarantine-based
workflow exists.

### 4.8 Internal Fields

| Name | SQL Type | Precision | Nullability | Source | Status |
|------|----------|-----------|-------------|--------|--------|
| `state_key` | TEXT | -- | NOT NULL | Pipe-delimited composite of 9 non-authoritative fields | IMPLEMENTED -- `sql/01_tables_min.sql:70` (non-authoritative; depends on legacy fields) |
| `export_str` | TEXT | -- | NOT NULL | Full pipe-delimited MIN export string | IMPLEMENTED -- `sql/01_tables_min.sql:71` |
| `payload` | JSONB | -- | NOT NULL | Raw ingest metadata (schema, contract version, source details, parsed values) | IMPLEMENTED -- `sql/01_tables_min.sql:72` |
| `ingest_ts` | TIMESTAMPTZ | microseconds | NOT NULL, DEFAULT `now()` | Server-side timestamp at insert/upsert time | IMPLEMENTED -- `sql/01_tables_min.sql:73` |

### 4.9 Indexes

| Index | Columns | Citation |
|-------|---------|----------|
| PRIMARY KEY | `block_id` | `sql/01_tables_min.sql:3` |
| `idx_ovc_min_sym_date` | `(sym, date_ny)` | `sql/01_tables_min.sql:76-77` |
| `idx_ovc_min_state_key` | `(state_key)` | `sql/01_tables_min.sql:79-80` |
| `idx_ovc_min_block2h` | `(block2h)` | `sql/01_tables_min.sql:82-83` |

---

## 5. Temporal Semantics

| Property | Rule | Citation |
|----------|------|----------|
| Session boundary | 17:00 ET to 17:00 ET next day | `src/backfill_oanda_2h_checkpointed.py:361-362`, `src/ingest_history_day.py:263-264` |
| Block duration | Exactly 2 hours (7200 seconds) | `src/backfill_oanda_2h_checkpointed.py:365` |
| Block indexing | 0-based (A=0, B=1, ... L=11) | `src/backfill_oanda_2h_checkpointed.py:68` |
| `bar_close_ms` | UTC epoch milliseconds of block close (block start + 2h) | `src/backfill_oanda_2h_checkpointed.py:403` |
| Timezone | All timestamps anchored to `America/New_York` | `src/backfill_oanda_2h_checkpointed.py:55` |
| DST handling | Handled by `ZoneInfo("America/New_York")` at conversion time | `src/backfill_oanda_2h_checkpointed.py:55`; test: `tests/test_dst_audit.py` |
| OANDA H1 fetch | H1 candles fetched, aggregated to 2H blocks (2 consecutive H1 per block) | `src/backfill_oanda_2h_checkpointed.py:372-381` |
| Incomplete candle filter | Only `complete: true` candles from OANDA are ingested | `src/backfill_oanda_2h_checkpointed.py:331` |
| Incomplete block filter | Blocks with fewer than 2 H1 candles are dropped | `src/backfill_oanda_2h_checkpointed.py:381` |

---

## 6. Normalization Rules (mechanical only)

| Rule | Formula / Logic | Citation |
|------|-----------------|----------|
| Range computation | `rng = h - l` | `src/backfill_oanda_2h_checkpointed.py:411`, `infra/ovc-webhook/src/index.ts:270` |
| Body computation | `body = abs(c - o)` | `src/backfill_oanda_2h_checkpointed.py:412`, `infra/ovc-webhook/src/index.ts:274` |
| Direction computation | `1` if `c > o`; `-1` if `c < o`; `0` if `c == o` | `src/backfill_oanda_2h_checkpointed.py:262-267`, `infra/ovc-webhook/src/index.ts:278` |
| Return computation | `(c - o) / o`; `0.0` if `o == 0` | `src/backfill_oanda_2h_checkpointed.py:414` |
| Block ID construction | `f"{date_ny:%Y%m%d}-{block_letter}-{symbol}"` | `src/backfill_oanda_2h_checkpointed.py:402` |
| Symbol normalization | Uppercase: `symbol.upper()` | `src/backfill_oanda_2h_checkpointed.py:389` |
| OANDA instrument mapping | `GBP_USD` -> `GBPUSD` (hardcoded) | `src/backfill_oanda_2h_checkpointed.py:57-58` |
| OANDA mid-price extraction | Uses `mid` price object (`mid.o`, `mid.h`, `mid.l`, `mid.c`) | `src/backfill_oanda_2h_checkpointed.py:337-340` |
| State key construction | Pipe-join of 9 non-authoritative fields | `src/backfill_oanda_2h_checkpointed.py:227-239` |
| Export string construction | Pipe-delimited key=value pairs per `EXPORT_FIELDS` order | `src/backfill_oanda_2h_checkpointed.py:250-252` |
| Webhook KV parse | Pipe `\|` delimiter, `=` separator, strict dedup check | `infra/ovc-webhook/src/index.ts:177-199` |
| Boolean normalization (webhook) | `1`/`true`/`y`/`yes` -> true; `0`/`false`/`n`/`no` -> false | `infra/ovc-webhook/src/index.ts:202-207` |

---

## 7. Idempotency & Overwrite-by-Reingest Semantics

### 7.1 Identity-Level Immutability

The `block_id` value for a given 2H block is deterministic and stable: it
is computed as `YYYYMMDD-X-SYMBOL` from the NY session date, block letter,
and symbol.  Once a `block_id` is assigned to a row, that identifier MUST
NOT change.  No mechanism exists to reassign a `block_id` to a different
block.

### 7.2 Row Content Overwrite-by-Reingest

Row contents (all non-PK columns) MAY be overwritten by a subsequent ingest
of the same `block_id`.  All ingest paths use an `ON CONFLICT (block_id)
DO UPDATE SET ...` upsert.  The latest ingest always wins.

| Path | Upsert mechanism | Citation |
|------|------------------|----------|
| Webhook | `ON CONFLICT (block_id) DO UPDATE SET ... ingest_ts = now()` | `infra/ovc-webhook/src/index.ts:626-680` |
| OANDA backfill | `ON CONFLICT (block_id) DO UPDATE SET ... ingest_ts = now()` | `src/backfill_oanda_2h_checkpointed.py:184-195` |
| CSV history | `ON CONFLICT (block_id) DO UPDATE SET ... ingest_ts = now()` | `src/ingest_history_day.py:135-146` |

This means:

- Multiple runs with the same source data produce identical DB state.
- `ingest_ts` reflects the timestamp of the most recent write, not the
  original insert.
- Re-ingesting corrected source data for a given `block_id` replaces the
  prior row contents without creating a new row.

### 7.3 Raw Payload Archival

The webhook path archives the raw payload to R2 before validation.

| Property | Value | Citation |
|----------|-------|----------|
| R2 key format | `tv/{YYYY-MM-DD}/{block_id}_{uuid}.txt` | `infra/ovc-webhook/src/index.ts:413-415` |
| Write timing | Before parse/validate | `infra/ovc-webhook/src/index.ts:559` |

The OANDA backfill and CSV history paths do NOT archive raw payloads to R2.

---

## 8. Validation Rules (reject vs quarantine)

### 8.1 Webhook Validation (`infra/ovc-webhook/src/index.ts`)

All webhook validation failures result in HTTP 400 (or 401) rejection.
There is no quarantine mechanism.

| Rule | Behavior | Code | Citation |
|------|----------|------|----------|
| Empty body | REJECT (400) | -- | `index.ts:478-483` |
| Invalid JSON (`/tv_secure`) | REJECT (400) | -- | `index.ts:498-505` |
| Missing export string | REJECT (400) | -- | `index.ts:522-528` |
| Schema mismatch (`/tv_secure`) | REJECT (400) | must be `export_contract_v0.1_min_r1` | `index.ts:531-537` |
| Bad token (`/tv_secure`) | REJECT (401) | -- | `index.ts:538-546` |
| Duplicate key in export | REJECT (400) | `E_DUPLICATE_KEY` | `index.ts:192-194` |
| Bad KV format | REJECT (400) | `E_BAD_KV` | `index.ts:183-185` |
| Missing required field | REJECT (400) | `E_REQUIRED_MISSING` | `index.ts:323-326` |
| Unknown key | REJECT (400) | `E_UNKNOWN_KEY` | `index.ts:328` |
| Key order violation | REJECT (400) | `E_KEY_ORDER` | `index.ts:330` |
| Type coercion failure | REJECT (400) | `E_TYPE_COERCION` | `index.ts:227-249` |
| Empty non-nullable field | REJECT (400) | `E_EMPTY_NOT_ALLOWED` | `index.ts:216-217` |
| Enum violation (`bias_dir`, `pred_dir`) | REJECT (400) | `E_ENUM` | `index.ts:355-360` |
| OHLC sanity: `h >= max(o,c)` AND `l <= min(o,c)` | REJECT (400) | `E_SEM_OHLC` | `index.ts:264-266` |
| Range sanity: `rng == h - l` (within 1e-9) | REJECT (400) | `E_SEM_RNG` | `index.ts:270` |
| Body sanity: `body == abs(c - o)` (within 1e-9) | REJECT (400) | `E_SEM_BODY` | `index.ts:274` |
| Direction sanity: `dir` matches OHLC relationship | REJECT (400) | `E_SEM_DIR` | `index.ts:278-279` |
| Return (`ret`) semantic check | **DISABLED** -- not validated at ingest | -- | `index.ts:281-282`, `docs/contracts/ingest_boundary.md:28` |

### 8.2 Backfill/History Validation (Python)

| Rule | Behavior | Citation |
|------|----------|----------|
| OHLC sanity: `h >= max(o,c)` AND `l <= min(o,c)` | ABORT (`SystemExit`) | `src/backfill_oanda_2h_checkpointed.py:255-259` |
| Incomplete H1 candle | SKIP (not ingested) | `src/backfill_oanda_2h_checkpointed.py:331` |
| Incomplete 2H block (< 2 H1 candles) | DROP | `src/backfill_oanda_2h_checkpointed.py:381` |
| Block index out of range (< 0 or > 11) | SKIP | `src/backfill_oanda_2h_checkpointed.py:396-397` |
| History: duplicate block in CSV | ABORT (`SystemExit`) | `src/ingest_history_day.py:283-284` |
| History: row count != 12 | ABORT (`SystemExit`) | `src/ingest_history_day.py:373-374` |
| History: timestamp not on 2H boundary | ABORT (`SystemExit`) | `src/ingest_history_day.py:205-206` |

### 8.3 QA Enforcement

| Claim | Backing Evidence | Status |
|-------|------------------|--------|
| MIN contract structural validation | `tests/test_min_contract_validation.py` (unit tests for missing keys, type errors, unknown keys) | IMPLEMENTED |
| MIN contract equivalence across profiles | `tests/test_contract_equivalence.py` (sample exports validated against JSON spec) | IMPLEMENTED |
| Schema object existence gate | `sql/90_verify_gate2.sql` (checks `ovc.ovc_blocks_v01_1_min` exists, enum sanity) | IMPLEMENTED |
| OHLC sanity SQL-level gate | No SQL-level CHECK constraint on OHLC relationships | DEFERRED |
| `ret` semantic validation downstream | Referenced in `index.ts:281-282` and `ingest_boundary.md:28`; no test or SQL gate exists for downstream `ret` validation | DEFERRED |
| Non-authoritative field migration enforcement | No CI gate prevents reading non-authoritative fields in downstream code | DEFERRED |

---

## 9. Downstream Guarantees (what Option B may assume)

Option B (derived features) MAY assume the following about any row in
`ovc.ovc_blocks_v01_1_min`:

| Guarantee | Basis |
|-----------|-------|
| `block_id` is unique and non-null | PRIMARY KEY constraint |
| `o`, `h`, `l`, `c` are non-null DOUBLE PRECISION | DDL `NOT NULL` constraint |
| `h >= max(o, c)` and `l <= min(o, c)` | Enforced at all ingest paths |
| `rng = h - l` | Mechanical computation at ingest |
| `body = abs(c - o)` | Mechanical computation at ingest |
| `dir` is `1`, `-1`, or `0` consistent with `c` vs `o` | Mechanical computation at ingest |
| `ret` is `(c - o) / o` | Mechanical computation at ingest (semantic validation DISABLED at ingest; no downstream gate exists -- DEFERRED) |
| `date_ny` is a valid date in NY timezone | Computed from session boundary logic |
| `block2h` is one of A-L | Computed from block index |
| `block4h` is one of AB, CD, EF, GH, IJ, KL | Computed from block index |
| `bar_close_ms` is UTC epoch milliseconds | Computed from block end time |
| `ingest_ts` is populated | DEFAULT `now()` |
| Rows are idempotent per `block_id` | `ON CONFLICT` upsert |

Option B MUST NOT assume:

- Non-authoritative fields (section 4.5) contain meaningful values.
- `ret` has been semantically validated at ingest or downstream.
- All 12 blocks exist for every session date.
- Volume is present (the column does not exist in the A1 table).

---

## 10. Explicit Exclusions

| Exclusion | Rationale | Citation |
|-----------|-----------|----------|
| Volume field | Not present in `ovc_blocks_v01_1_min` DDL | `sql/01_tables_min.sql` -- no `volume` column |
| `ret` semantic validation at ingest | Intentionally disabled for stability; validated downstream | `index.ts:281-282`, `ingest_boundary.md:10` (downstream gate: DEFERRED) |
| Feature derivation | State tags, trend tags, regime tags, and all classifiers are Option B/C scope | `A_TO_D_CONTRACT_v1.md:49` |
| Session logic | No session-level aggregation or completeness enforcement at ingest | Ingest writes individual blocks |
| Heuristic cleaning | No outlier detection, spike removal, or gap-fill logic | `docs/contracts/option_a_ingest_contract_v1.md` |
| Quarantine mechanism | No quarantine table exists; validation failures are rejected outright | NOT IMPLEMENTED |
| Cross-table reads | Option A MUST NOT read from derived or config tables | `A_TO_D_CONTRACT_v1.md:157-158` |

---

## Alignment Confirmation

### Fully Aligned with Repo Reality

| Item | Evidence |
|------|----------|
| Schema matches `ovc.ovc_blocks_v01_1_min` DDL | `sql/01_tables_min.sql` -- all 53 columns verified field-by-field |
| Upsert semantics match all three ingest paths | `index.ts:595-681`, `backfill_oanda_2h_checkpointed.py:184-195`, `ingest_history_day.py:135-146` |
| OHLC validation enforced in all ingest paths | Webhook: `index.ts:252-286`; Python: `_ensure_ohlc_sane()` in all scripts |
| `ret` validation intentionally disabled | `index.ts:281-282`, `ingest_boundary.md:28` |
| Non-authoritative fields documented with placeholder behavior | `backfill_oanda_2h_checkpointed.py:435-466`, `ingest_history_day.py:321-352` |
| MIN export schema v0.1.1 is IMMUTABLE | `contracts/export_contract_v0.1.1_min.json:4` |
| R2 archival exists for webhook path | `index.ts:407-424` |
| Test coverage for MIN contract validation | `tests/test_min_contract_validation.py`, `tests/test_contract_equivalence.py` |
| Schema existence gate | `sql/90_verify_gate2.sql` |
| Both direct-2H and H1-aggregated ingest modes documented | `index.ts` (webhook), `backfill_oanda_2h_checkpointed.py:371-381` (aggregation) |

### Explicitly Deferred

| Item | Status | Rationale |
|------|--------|-----------|
| Migration of non-authoritative fields out of `ovc_blocks_v01_1_min` | FUTURE -- non-binding | Per `option_a_ingest_contract_v1.md:65` |
| Quarantine table for failed ingest records | NOT IMPLEMENTED | No quarantine table in DDL or scripts |
| `ret` semantic validation (at ingest or downstream) | DEFERRED | Disabled at ingest; no downstream gate exists |
| Volume column in A1 table | NOT IMPLEMENTED | DDL does not include `volume` |
| CI gate preventing downstream reads of non-authoritative fields | DEFERRED | No automated enforcement exists |
| SQL-level CHECK constraint for OHLC relationships | DEFERRED | Enforced only in application code |

### What Would BREAK This Contract If Changed

| Change | Impact |
|--------|--------|
| Altering `block_id` format (`YYYYMMDD-X-SYMBOL`) | Breaks PK identity semantics and all downstream lookups |
| Removing `ON CONFLICT` upsert from any ingest path | Breaks idempotency; duplicate runs would fail or produce duplicates |
| Promoting non-authoritative fields to authoritative status without migration | Violates canonical/derived boundary; breaks Option B contract |
| Changing `bar_close_ms` from UTC epoch ms to another format | Breaks temporal join logic between A1 and A2 |
| Modifying MIN export contract v0.1.1 in place | Violates IMMUTABLE status; MUST create new version file |
| Removing OHLC sanity checks from any ingest path | Breaks downstream guarantee that `h >= max(o,c)` and `l <= min(o,c)` |
| Enabling `ret` semantic validation in webhook without coordination | Would reject records that currently pass; breaking change for live ingest |
| Changing H1-to-2H aggregation logic (e.g. accepting 1 H1 candle) | Breaks deterministic aggregation guarantee |
