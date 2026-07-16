# OVC Current-State Delta 2026-07-15 ae88bca49e94

**Status:** HOLD  
**R0 scope:** containment and live-state evidence only  
**Repository commit inspected:** `ae88bca49e94ab55d5c104ed4c7f371f111f2f94`  
**Local branch:** `backup/local-sentinel-pre-canonicalization`  
**Remote default branch:** `main`  
**Supersedes:** specific claims in `docs/pipeline/CURRENT_STATE_INVARIANTS.md`; the frozen snapshot was not edited.

## Gate Finding

R0 cannot pass yet.

1. The cron triggers for `.github/workflows/ovc_option_c_schedule.yml` and `.github/workflows/notion_sync.yml` have been removed locally while keeping `workflow_dispatch`.
2. The live GitHub default branch is `main`; this checkout is on `backup/local-sentinel-pre-canonicalization`, so remote scheduled automation is not held until the containment commit lands on `main`.
3. Neon live state was captured read-only.
4. GitHub workflow state and secret names were captured read-only.
5. Cloudflare live Worker version and Worker secret names were not captured: Wrangler is installed but the local session is not logged in and `CLOUDFLARE_API_TOKEN` is not configured.

## R0 Containment

| Workflow | Prior cron | Local R0 state | Manual dispatch |
|---|---:|---|---|
| `.github/workflows/ovc_option_c_schedule.yml` | `15 6 * * *` | cron removed locally | retained |
| `.github/workflows/notion_sync.yml` | `17 */2 * * *` | cron removed locally | retained |

No A ingest/backfill or Path1 workflow was disabled in R0. Latest live runs show A/backfill and Path1 evidence have recent successes, while Option C and Notion have recent failures.

## Neon Live Objects

Captured read-only via `psql` using local `.env` connection settings. No secret values are recorded here.

| Object | Exists | Kind | Rows | Latest marker | Definition MD5 |
|---|---:|---:|---:|---|---|
| `ovc.ovc_blocks_v01_1_min` | yes | table | 59,875 | `max(date_ny)=2026-02-18`; `max(ingest_ts)=2026-03-20 07:14:36.277491+00` | `1e592d177a2c6aeea47d88190f1d458f` |
| `ovc.ovc_candles_m15_raw` | yes | table | 384 | `max(ingest_ts)=2026-01-22 01:27:42.970387+00`; `max(bar_close_ms)=1671141600000` | `7d0cc0da3f8462ce88ae2fd3e20c9ae7` |
| `derived.v_ovc_c1_features_v0_1` | yes | view | 59,875 | no timestamp column | `4ff85d2489450db9c1f1492952363287` |
| `derived.v_ovc_c2_features_v0_1` | yes | view | 59,875 | `max(date_ny)=2026-02-18` | `65c490412dd231d1e6177b5a809f892b` |
| `derived.v_ovc_c3_features_v0_1` | yes | view | 59,875 | `max(bar_close_ms)=1771495200000` | `7f856b8b09d68b161b59ea4bf16e1994` |
| `derived.v_ovc_c_outcomes_v0_1` | yes | view | 59,875 | `max(bar_close_ms)=1771495200000` | `7067dea0e6805d090bea5134d514ba4f` |
| `derived.ovc_outcomes_v0_1` | yes | view | 59,875 | `max(date_ny)=2026-02-18` | `dd47ef737e78678d5f981b5916f0e649` |
| `derived.v_path1_evidence_dis_v1_1` | yes | view | 59,875 | `max(bar_close_ms)=1771495200000` | `169f7c42dacd1452ad6c132134a3d145` |
| `ovc.ovc_run_reports_v01` | yes | table | 0 | none | `eba0df997975840645cf2a230d5cb4d1` |
| `ovc_cfg.threshold_pack` | yes | table | 2 | not captured | `aa4c803bddd367fea1e42c295800693d` |
| `ovc_cfg.threshold_pack_active` | yes | table | 2 | not captured | `f8edb21624d2a61ee451df548efba40f` |

Notable deployed schema facts:

- `ovc.ovc_blocks_v01_1_min` contains semantic columns including `state_tag`, `trend_tag`, `bias_mode`, `play`, and `pred_dir`; it also has live columns `payload:text` and `tf:text`.
- `ovc.ovc_run_reports_v01` has `started_at` and `finished_at`, but no rows.
- Both the authoritative C view `derived.v_ovc_c_outcomes_v0_1` and legacy C view `derived.ovc_outcomes_v0_1` exist live.

## GitHub Live Automation

Captured read-only with `gh` as account `owenguobadia24s-collab`.

| Workflow | Latest observed run | Event | Conclusion | Notes |
|---|---:|---|---|---|
| `notion-sync` | `29422548349` at `2026-07-15T14:12:47Z` | schedule | failure | failed at `Run Notion sync`; no artifacts listed |
| `OVC Option C Schedule` | `29401317259` at `2026-07-15T08:35:09Z` | schedule | failure | failed at `Guardrail - require Option C version bump`; artifact `option-c-reports-c_29401317259_1_153d47b_181` |
| `OVC Backfill (GBPUSD 2H)` | `29422349482` at `2026-07-15T14:10:04Z` | schedule | success | artifact `backfill-run-artifacts` |
| `Path1 Evidence Runner` | `29417788227` at `2026-07-15T13:05:41Z` | schedule | success | no artifacts listed |
| `Path1 Replay Verification (Structural)` | `29391859268` at `2026-07-15T05:35:47Z` | schedule | failure | latest observed replay gate failure |

GitHub reports these workflows as active: `OVC Backfill (GBPUSD 2H)`, `OVC Backfill (M15 Raw)`, `OVC Backfill then Validate (Range)`, `Path1 Evidence Runner`, `Path 1 Evidence Queue Runner`, `Path 1 Evidence Range Runner`, `Path1 Replay Verification (Structural)`, `notion-sync`, `OVC Option C Schedule`, and CI workflows.

## Secret Names

GitHub Actions secret names observed:

- `DATABASE_URL`
- `NEON_DSN`
- `NOTIOM_TOKEN`
- `NOTION_BLOCKS_DB_ID`
- `NOTION_OUTCOMES_DB_ID`
- `NOTION_RUNS_DB_ID`
- `OANDA_ACCOUNT_ID`
- `OANDA_API_TOKEN`
- `OANDA_ENV`
- `OVC_PR_BOT_TOKEN`

Local `.env` key names observed:

- `BACKFILL_DAYS_PER_RUN`
- `BACKFILL_START_UTC`
- `NEON_DSN`
- `OANDA_ACCOUNT_ID`
- `OANDA_API_TOKEN`
- `OANDA_ENV`
- `OANDA_SLICE_DAYS`

Cloudflare Worker secret names were not available from live Cloudflare. The checked-in Wrangler config comments name expected secrets `OVC_TOKEN` and `DATABASE_URL`.

## Cloudflare Worker Evidence

Checked-in config at `infra/ovc-webhook/wrangler.jsonc` declares:

- Worker name: `ovc-webhook`
- Entry point: `src/index.ts`
- Compatibility date: `2026-01-12`
- Compatibility flags: `nodejs_compat`
- R2 binding: `RAW_EVENTS` to bucket `ovc-raw-events`

Checked-in Worker code uses `DATABASE_URL` and `OVC_TOKEN`, writes to `ovc.ovc_blocks_v01_1_min`, and attempts to write run reports to `ovc.ovc_run_reports_v01`.

Live Cloudflare version, deployment timestamp, and Worker secret names remain unknown because `wrangler whoami`, `wrangler versions list --name ovc-webhook --json`, and `wrangler secret list --name ovc-webhook --format json` failed with not-logged-in / missing `CLOUDFLARE_API_TOKEN`.

## Migration Hash State

`schema/applied_migrations.json` exists, but every ledger entry is `UNVERIFIED` and the ledger does not contain applied-object signatures. Repository SHA-256 values captured during R0:

| Ledger file | Ledger status | Repository SHA-256 |
|---|---|---|
| `sql/00_schema.sql` | `UNVERIFIED` | `db7c88e5e3efc476a46bf0ebdac45ddc4f8fafe73b96b8ef2811cda1420f92c2` |
| `sql/01_tables_min.sql` | `UNVERIFIED` | `f42351b903b74d810639145abc0e0bafcc36a644ba8f9ed784113f03fe2cb4a6` |
| `sql/02_tables_run_reports.sql` | `UNVERIFIED` | `a695d6beedf4e81a7f16785dfabafe88804ca35ca65e94937c665b6641582fad` |
| `sql/02_derived_c1_c2_tables_v0_1.sql` | `UNVERIFIED` | `7ba8104a2ec070ba22eb06e8c431811072f6abc0e33671a76ea2e6cc122dc945` |
| `sql/03_tables_outcomes.sql` | `UNVERIFIED` | `c1ff2cc8d257303226f7289664aa03a4be57cfafe5e17fc125a44614d1c49267` |
| `sql/04_threshold_registry_v0_1.sql` | `UNVERIFIED` | `e0c237e9f4b33cf0a82198e5c8c19df99b2f430318d74494358d9a0036c3d66d` |
| `sql/derived_v0_1.sql` | `UNVERIFIED` | `MISSING` |
| `sql/derived/v_ovc_c1_features_v0_1.sql` | `UNVERIFIED` | `1a4424a83223f78c5198ff5360094243d5a55635093ee592f92d6b8fc73b789e` |
| `sql/derived/v_ovc_c2_features_v0_1.sql` | `UNVERIFIED` | `e83153c35cdf72d1e7b041369f0cf51e0cae1cdfc777bcfc461fb5a53e89003c` |
| `sql/derived/v_ovc_c3_features_v0_1.sql` | `UNVERIFIED` | `4b2f7e41513de8ebbfaaab23c342c4735b5a4e3641349c6545163daed8737213` |
| `sql/derived/v_ovc_c_outcomes_v0_1.sql` | `UNVERIFIED` | `7bd34fe9af3ffc166689caffea794f7a13c089f4cc08e796a23d7dba4b5e345b` |
| `sql/option_c_v0_1.sql` | `UNVERIFIED` | `f11a28a401c85d4fa39b4ca5e1144d4a21c959517d5866ff4516171c21b647fc` |
| `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql` | `UNVERIFIED` | `ab06103c2e418493fa9c66fbc59fa74508c2fe4c9d1c07759ea334a14f18d574` |
| `sql/path1/db_patches/patch_m15_raw_20260122.sql` | `UNVERIFIED` | `cd30724602745a6122d2cbaba8627062d0e0155d92a8d9436c906dac0e609643` |

## Superseded Snapshot Claims

- `INV-C3` is no longer accurate for the inspected file: `.github/workflows/ovc_option_c_schedule.yml` calls `scripts/run/run_option_c.sh`, not `scripts/run_option_c.sh`.
- `INV-QA3` is no longer literally accurate: a migration ledger exists at `schema/applied_migrations.json`, but it is unverified and incomplete as deployment evidence.
- `INV-SCHEMA1` remains materially true: checked-in Worker code references `ended_at` and `meta` in run-report insert paths, while the live table has `finished_at` and no `meta`; the live run-report table currently has zero rows.
- `INV-C1` remains materially true for the legacy view: `derived.ovc_outcomes_v0_1` exists live and the repository SQL `sql/option_c_v0_1.sql` reads `ovc.ovc_blocks_v01_1_min` directly.
- `INV-C2` remains materially true: `derived.v_ovc_c_outcomes_v0_1` exists live and is the B-to-C candidate authority.

## Operator Decision

R0 status is `HOLD`.

Required before R0 can move to `PASS`:

1. Land the two local workflow cron removals on remote `main`, or otherwise prove the live default branch has those crons removed while preserving manual dispatch.
2. Provide Cloudflare live access through a valid Wrangler login or `CLOUDFLARE_API_TOKEN`, then capture Worker version, deployment timestamp, and Worker secret names.
3. Re-check active workflow state after containment lands.
