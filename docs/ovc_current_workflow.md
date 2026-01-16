# OVC Current Workflow (as implemented in this repo)

## 1) What OVC is (2–5 sentences)
OVC is a TradingView-driven signal export + storage pipeline that captures 2-hour market-state snapshots and persists them to Neon Postgres for analysis and replay. It solves the problem of reliably ingesting TradingView alert payloads (MIN) and, optionally, richer debug payloads (FULL) into structured storage with idempotent keys. In this repo, **MIN** is the webhook-safe subset of fields emitted by the Pine script and intended for live ingestion, while **FULL** is the complete “copy/debug” export string that contains every computed field and is intended for cold-path storage only. The Pine script explicitly labels these two profiles and builds different export strings for each. 【F:pine/OVC_v0_1.pine†L50-L178】

## 2) System Diagram (ASCII)
```
+-----------------------+          +---------------------------+          +----------------------+
| TradingView Alert     |  POST    | Cloudflare Worker         |  INSERT  | Neon Postgres        |
| (Pine export string)  +--------->| infra/ovc-webhook/src/... |--------->| ovc_blocks_v01 (MIN) |
+-----------------------+          +-------------+-------------+          +----------+-----------+
                                                |                                   |
                                                | RAW body write                    | FULL JSONB
                                                v                                   v
                                       +---------------------+           +-------------------------+
                                       | Cloudflare R2        |           | ovc_blocks_detail_v01  |
                                       | bucket: ovc-raw-...  |           | (FULL, JSONB)           |
                                       +---------------------+           +-------------------------+

   +----------------------+                                     +-----------------------------+
   | GitHub Actions       |                                     | Local scripts               |
   | backfill.yml         |---- backfill_oanda_2h_checkpointed ->| src/backfill_oanda_2h*.py   |
   | ovc_full_ingest.yml  |---- full_ingest_stub.py ------------>| src/full_ingest_stub.py     |
   +----------------------+                                     +-----------------------------+
```
Citations: Worker ingress and raw-event writes are in `infra/ovc-webhook/src/index.ts`, R2 bucket binding is in `infra/ovc-webhook/wrangler.jsonc`, and the GitHub Actions workflows call the backfill and full-ingest scripts. 【F:infra/ovc-webhook/src/index.ts†L57-L240】【F:infra/ovc-webhook/wrangler.jsonc†L1-L20】【F:.github/workflows/backfill.yml†L1-L56】【F:.github/workflows/ovc_full_ingest.yml†L1-L60】

## 3) Components & Responsibilities

### TradingView/Pine export contract(s)
- **Contracts:** `contracts/export_contract_v0.1_min.json` and `contracts/export_contract_v0.1_full.json` define the MIN/FULL schema keys, ordering, and types used for validation. 【F:contracts/export_contract_v0.1_min.json†L1-L67】【F:contracts/export_contract_v0.1_full.json†L1-L6】
- **Pine export source:** `pine/OVC_v0_1.pine` builds the MIN and FULL export strings and emits them via `alert()` at 2H bar close. 【F:pine/OVC_v0_1.pine†L50-L178】【F:pine/OVC_v0_1.pine†L332-L348】

### Cloudflare Worker ingress handler
- **File:** `infra/ovc-webhook/src/index.ts`. 【F:infra/ovc-webhook/src/index.ts†L1-L242】
- **Validations:**
  - Only accepts `POST /tv` or `POST /tv_secure`. 【F:infra/ovc-webhook/src/index.ts†L88-L99】
  - `/tv_secure` requires JSON, `schema=OVC_MIN_V01`, and a valid `OVC_TOKEN`. 【F:infra/ovc-webhook/src/index.ts†L114-L174】
  - Requires `sym`, `bar_close_ms`, and `bid` in the export or envelope. 【F:infra/ovc-webhook/src/index.ts†L185-L196】
- **Storage behavior:**
  - Always writes the raw body to R2 (keyed under `tv/YYYY-MM-DD/...`) if the binding is present. 【F:infra/ovc-webhook/src/index.ts†L52-L85】
  - Upserts MIN data into `ovc_blocks_v01`, storing `export_min` and `payload_min` JSONB along with the idempotency key. 【F:infra/ovc-webhook/src/index.ts†L210-L240】

### Neon schema/tables (MIN vs FULL)
- **Core (MIN):** `public.ovc_blocks_v01` is defined in `sql/schema_v01.sql` with a primary key on `(symbol, block_start, block_type, schema_ver)` and OHLC columns. 【F:sql/schema_v01.sql†L1-L21】
  - The Worker expects this table to also contain `bid`, `export_min`, and `payload_min` columns because it inserts them directly. 【F:infra/ovc-webhook/src/index.ts†L210-L240】
- **Detail (FULL):** `public.ovc_blocks_detail_v01` stores FULL payloads as JSONB with the same PK. 【F:infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql†L1-L12】

### R2 raw event storage
- **Bucket binding/name:** `RAW_EVENTS` → `ovc-raw-events` in `infra/ovc-webhook/wrangler.jsonc`. 【F:infra/ovc-webhook/wrangler.jsonc†L12-L18】
- **Object key structure:** `tv/YYYY-MM-DD/<bid>_<uuid>.txt` or `tv/YYYY-MM-DD/<iso>_<uuid>.txt` (if bid missing). 【F:infra/ovc-webhook/src/index.ts†L52-L85】

### FULL ingest pipeline stub / scripts
- **Stub script:** `src/full_ingest_stub.py` inserts JSONB payloads into `ovc_blocks_detail_v01` with schema `OVC_FULL_V01`. 【F:src/full_ingest_stub.py†L8-L76】
- **GitHub Action:** `ovc_full_ingest.yml` runs the stub manually with `symbol`, `start_date`, and `end_date`. 【F:.github/workflows/ovc_full_ingest.yml†L1-L60】

## 4) Current “Definition of Done” Status
| Item | Status | Evidence |
| --- | --- | --- |
| MIN ingestion only via TradingView | **Implemented** | Worker enforces MIN schema (`OVC_MIN_V01`) and `/tv_secure` JSON-only ingestion. 【F:infra/ovc-webhook/src/index.ts†L114-L174】 |
| FULL stored as JSONB only (opt-in) | **Implemented** | `ovc_blocks_detail_v01.full_payload` is JSONB and the FULL ingest stub writes JSONB. 【F:infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql†L1-L12】【F:src/full_ingest_stub.py†L8-L58】 |
| Core/detail tables with PKs enforced | **Implemented** | PKs in `ovc_blocks_v01` and `ovc_blocks_detail_v01`. 【F:sql/schema_v01.sql†L1-L21】【F:infra/ovc-webhook/sql/20250215_create_ovc_blocks_detail_v01.sql†L1-L12】 |
| Backfill reruns produce zero duplicates | **Implemented** | Backfill uses `ON CONFLICT ... DO UPDATE` on the PK. 【F:src/backfill_oanda_2h.py†L95-L113】【F:src/backfill_oanda_2h_checkpointed.py†L89-L117】 |
| Run report artifact generated per run | **Not Implemented** | No artifact-generation step exists in the workflows. 【F:.github/workflows/backfill.yml†L1-L56】【F:.github/workflows/ovc_full_ingest.yml†L1-L60】 |
| Tests present (what exists, where) | **Implemented** | Contract validation tests in `tests/`, Worker unit tests in `infra/ovc-webhook/test/`. 【F:tests/test_contract_equivalence.py†L1-L75】【F:infra/ovc-webhook/test/index.spec.ts†L1-L20】 |

## 5) How to Use It (Operator Steps)

### Run the Worker locally
From `infra/ovc-webhook`:
```bash
npm install
npm run dev
```
The `dev` script is `wrangler dev`. 【F:infra/ovc-webhook/package.json†L1-L11】

### Deploy the Worker
From `infra/ovc-webhook`:
```bash
wrangler deploy
```
Required secrets (per `wrangler.jsonc` comments):
```bash
wrangler secret put OVC_TOKEN
wrangler secret put DATABASE_URL
```
Citations: worker scripts and secrets listing in `wrangler.jsonc` and `package.json`. 【F:infra/ovc-webhook/wrangler.jsonc†L1-L20】【F:infra/ovc-webhook/package.json†L1-L11】

### Verify ingestion (Neon + R2)
**Neon SQL examples (from readiness doc):**
```sql
SELECT *
FROM ovc_blocks_v01
WHERE source IN ('tv_plain', 'tv_secure')
ORDER BY ingested_at DESC
LIMIT 50;
```
```sql
SELECT *
FROM ovc_blocks_detail_v01
ORDER BY ingested_at DESC
LIMIT 50;
```
These queries are documented in `docs/step8_readiness.md`. 【F:docs/step8_readiness.md†L41-L79】

**R2 raw events:** the worker writes all raw request bodies into the `ovc-raw-events` bucket under `tv/YYYY-MM-DD/...`. 【F:infra/ovc-webhook/wrangler.jsonc†L12-L18】【F:infra/ovc-webhook/src/index.ts†L52-L85】

### Run the FULL ingest stub
From repo root:
```bash
python src/full_ingest_stub.py --symbol GBPUSD --start-date 2025-01-01 --end-date 2025-01-07
```
- Dates must be **YYYY-MM-DD** (the parser uses `%Y-%m-%d`). 【F:src/full_ingest_stub.py†L24-L56】
- Requires `NEON_DSN` in the environment. 【F:src/full_ingest_stub.py†L59-L72】

## 6) Where to See the Logs (“the good stuff”)
- **TradingView alert logs:** Alerts are emitted via `alert()` in the Pine script; view the alert log in the TradingView UI for those alerts. 【F:pine/OVC_v0_1.pine†L340-L348】
- **Cloudflare Worker logs:** Use `wrangler dev` locally (prints request logs), and use the Cloudflare Workers dashboard/logs for deployed runs. The repo only defines the worker and `wrangler` scripts; log viewing itself is platform-provided. 【F:infra/ovc-webhook/package.json†L1-L11】
- **Neon rows:** Use SQL queries (examples in `docs/step8_readiness.md`) to inspect inserts. 【F:docs/step8_readiness.md†L41-L79】
- **R2 objects:** Check the `ovc-raw-events` bucket in Cloudflare R2 (bucket name defined in `wrangler.jsonc`). 【F:infra/ovc-webhook/wrangler.jsonc†L12-L18】

## 7) Troubleshooting (Top 8 Failures + Fixes)
1) **Date parsing errors (FULL ingest stub).** `full_ingest_stub.py` parses dates using `%Y-%m-%d`; other formats will crash. Fix by supplying `YYYY-MM-DD` dates. 【F:src/full_ingest_stub.py†L24-L56】
2) **Auth token / secret missing (Worker).** `/tv_secure` requires `OVC_TOKEN` and the worker requires `DATABASE_URL`; missing secrets return 500s. Fix by setting both secrets via `wrangler secret put`. 【F:infra/ovc-webhook/src/index.ts†L96-L104】【F:infra/ovc-webhook/wrangler.jsonc†L8-L14】
3) **Payload rejected because it’s not a MIN envelope.** `/tv_secure` rejects non-JSON bodies and any schema not equal to `OVC_MIN_V01`. Fix by sending JSON with the correct schema. 【F:infra/ovc-webhook/src/index.ts†L114-L174】
4) **Duplicate key conflicts / reruns.** The PK is `(symbol, block_start, block_type, schema_ver)`; the worker and backfill use `ON CONFLICT ... DO UPDATE` to avoid duplicates. If you see conflicts, the PK might be missing in your DB. 【F:sql/schema_v01.sql†L1-L21】【F:infra/ovc-webhook/src/index.ts†L210-L240】
5) **Schema mismatch with export contract.** Use `tools/validate_contract.py` against the JSON contracts to check order/types; mismatches will be flagged. 【F:tools/validate_contract.py†L9-L132】【F:contracts/export_contract_v0.1_min.json†L1-L67】
6) **Missing env vars in backfill or FULL ingest.** Backfill scripts require `NEON_DSN` and `OANDA_API_TOKEN`; the FULL stub requires `NEON_DSN`. Fix by setting them (locally or via GitHub Actions secrets). 【F:src/backfill_oanda_2h.py†L14-L33】【F:src/full_ingest_stub.py†L59-L72】【F:.github/workflows/backfill.yml†L13-L34】
7) **Wrong timezone / segment derivation mismatch.** The Pine export embeds `tz`, `date_ny`, and segment IDs; if your TradingView script uses a different timezone, the `bid`/segment values won’t line up with the worker’s `block_start` (computed from `bar_close_ms`). Fix by aligning Pine `EXP_TZ` and ensuring `bar_close_ms` matches the 2H close time you expect. 【F:pine/OVC_v0_1.pine†L26-L112】【F:infra/ovc-webhook/src/index.ts†L185-L207】
8) **Rate/limit constraints (OANDA backfill).** There’s no explicit throttling in the backfill scripts; control request volume by reducing `OANDA_SLICE_DAYS` or `BACKFILL_DAYS_PER_RUN`. These env vars are consumed by the checkpointed backfill and configured in the workflow. 【F:src/backfill_oanda_2h_checkpointed.py†L31-L64】【F:.github/workflows/backfill.yml†L13-L30】

## Not Implemented Yet
- No automated “run report artifact” generation exists in the workflows; runs only print to stdout. 【F:.github/workflows/backfill.yml†L1-L56】【F:.github/workflows/ovc_full_ingest.yml†L1-L60】
