# OVC Current State Delta 2026-07-15 2b1811a

**R0 status:** HOLD  
**Repository:** `ovc-infra`  
**Observed branch:** `main`  
**Observed HEAD:** `2b1811a path1 evidence: p1_20260617_GBPUSD_20260616_len5d_8cf43821`  
**Observed origin/main during continuation:** `cf22372 path1 evidence: p1_20260712_GBPUSD_20260711_len5d_2e4b43bf`  
**Snapshot purpose:** contain unsafe scheduled automation while recording exactly which live-state evidence is verified and which remains unavailable.

This file is a read-only evidence delta over the frozen snapshot at `docs/pipeline/CURRENT_STATE_INVARIANTS.md`. It does not edit the frozen snapshot.

## 1. Repo, Commit, And Worktree Status

Local command evidence:

```text
git rev-parse --short HEAD
2b1811a

git log --oneline -1
2b1811a path1 evidence: p1_20260617_GBPUSD_20260616_len5d_8cf43821

git rev-parse origin/main
cf22372c14544a1207a74abbf6efec21ae22b2f4

git status --short --branch
## main...origin/main [behind 25]
```

Continuation note: local `main` began 25 commits behind `origin/main`. The remote workflow files at `origin/main` still contained the Option C and Notion cron schedules before R0 containment was rebased/pushed.

Pre-existing untracked files were present before R0 containment and were not touched by this R0 pass:

```text
OVC_INFRA_DEPENDENCY_MAP.md
OVC_INFRA_FILE_TRACE_MATRIX.md
PHASE_3_SQL_PYTHON_MAPPING.md
ovc-infra-handbook.html
ovc-infra-handbook.md
ovc-infra-sql-python-deps.dot
ovc-infra-sql-python-deps.pdf
ovc-infra-sql-python-deps.png
ovc-infra-sql-python-deps.svg
ovc-infra-system-overview.dot
ovc-infra-system-overview.pdf
ovc-infra-system-overview.png
ovc-infra-system-overview.svg
```

R0 intended change scope:

```text
.github/workflows/ovc_option_c_schedule.yml
.github/workflows/notion_sync.yml
docs/current-state/OVC_CURRENT_STATE_DELTA_2026-07-15_2b1811a.md
```

## 2. Schedule Containment Status

### Option C

Before R0, `.github/workflows/ovc_option_c_schedule.yml` had:

```text
schedule:
  - cron: "15 6 * * *"
workflow_dispatch:
```

R0 containment removes the `schedule` trigger and preserves `workflow_dispatch` so controlled manual diagnosis remains possible.

Remote verification after push:

```text
remote main commit containing R0 containment: 25a90bb
raw GitHub .github/workflows/ovc_option_c_schedule.yml: workflow_dispatch present; schedule/cron absent
```

### Notion Sync

Before R0, `.github/workflows/notion_sync.yml` had:

```text
workflow_dispatch:
schedule:
  - cron: "17 */2 * * *"
```

R0 containment removes the `schedule` trigger and preserves `workflow_dispatch` so controlled manual diagnosis remains possible.

Remote verification after push:

```text
remote main commit containing R0 containment: 25a90bb
raw GitHub .github/workflows/notion_sync.yml: workflow_dispatch present; schedule/cron absent
```

### Paths Not Automatically Paused

R0 did not disable A ingest/backfill or Path1 workflows. Per the R0 contract, those paths require live run/dependency inspection before any pause decision.

## 3. Neon Live Object Evidence

Status: **VERIFIED LIVE VIA NEON CONNECTOR**

Local CLI/env access remains unavailable, but the Neon connector provided read-only live access:

```text
psql: unavailable
neon: unavailable
DATABASE_URL: absent locally
NEON_DSN: absent locally
Neon connector project: icy-forest-24883364 (OVC)
```

Live object inventory confirms deployed OVC, derived, ops, QA, config, and public objects. Relevant deployed objects include:

```text
derived.derived_runs_v0_1                         BASE TABLE
derived.eval_runs                                 BASE TABLE
derived.ovc_c1_features_v0_1                      BASE TABLE
derived.ovc_c2_features_v0_1                      BASE TABLE
derived.ovc_outcomes_v0_1                         VIEW
derived.ovc_scores_v0_1                           VIEW
derived.v_ovc_b_scores_dis_v1_1                   VIEW
derived.v_ovc_b_scores_lid_v1_0                   VIEW
derived.v_ovc_b_scores_res_v1_0                   VIEW
derived.v_ovc_c1_features_v0_1                    VIEW
derived.v_ovc_c2_features_v0_1                    VIEW
derived.v_ovc_c3_features_v0_1                    VIEW
derived.v_ovc_c_outcomes_v0_1                     VIEW
derived.v_ovc_state_plane_v0_2                    VIEW
derived.v_path1_evidence_dis_v1_1                 VIEW
derived.v_path1_evidence_lid_v1_0                 VIEW
derived.v_path1_evidence_res_v1_0                 VIEW
ops.notion_sync_state                             BASE TABLE
ovc.ovc_blocks_v01_1_min                          BASE TABLE
ovc.ovc_candles_m15_raw                           BASE TABLE
ovc.ovc_run_reports_v01                           BASE TABLE
ovc.v_data_quality_ohlc_basic                     VIEW
ovc.v_ovc_min_events_norm                         VIEW
ovc.v_ovc_min_events_seq                          VIEW
ovc_cfg.threshold_pack                            BASE TABLE
ovc_cfg.threshold_pack_active                     BASE TABLE
ovc_qa.derived_validation_run                     BASE TABLE
ovc_qa.validation_run                             BASE TABLE
```

Live view definition fingerprints from `pg_get_viewdef`:

```text
derived.v_ovc_b_scores_dis_v1_1       md5:c58df8f09536998f70b80e139d0c5719 chars:726
derived.v_ovc_b_scores_lid_v1_0       md5:d5b093d2a97aab28051f1fc3a8756b5f chars:1042
derived.v_ovc_b_scores_res_v1_0       md5:ade22f74b4b72f1da46d2a72a49d1ebb chars:1160
derived.v_ovc_c1_features_v0_1        md5:4ff85d2489450db9c1f1492952363287 chars:3427
derived.v_ovc_c2_features_v0_1        md5:65c490412dd231d1e6177b5a809f892b chars:9080
derived.v_ovc_c3_features_v0_1        md5:7f856b8b09d68b161b59ea4bf16e1994 chars:6662
derived.v_ovc_c_outcomes_v0_1         md5:7067dea0e6805d090bea5134d514ba4f chars:8164
derived.v_ovc_state_plane_v0_2        md5:952a69167f7795de898c46d58926053a chars:8560
derived.v_path1_evidence_dis_v1_1     md5:169f7c42dacd1452ad6c132134a3d145 chars:784
derived.v_path1_evidence_lid_v1_0     md5:de34d34ebb9b547b2d010db7eedff291 chars:784
derived.v_path1_evidence_res_v1_0     md5:8cbe4851d4337304285bbd52b40c4bff chars:784
ovc.v_data_quality_ohlc_basic         md5:7e1d317cac1be54b0a8603f43195902a chars:404
ovc.v_ovc_min_events_norm             md5:ece0b167cd7b541fbff866eea01b6b1f chars:418
ovc.v_ovc_min_events_seq              md5:505b80d560901c16594b59db8ceacc5e chars:2451
```

Repository SHA-256 hashes and live `pg_get_viewdef` MD5 hashes are recorded as separate fingerprints. A direct hash equality comparison is not claimed because PostgreSQL normalizes view definitions when returning `pg_get_viewdef`.

## 4. A/B/C/Run Table Counts And Latest Timestamps

Status: **VERIFIED LIVE VIA NEON CONNECTOR**

```text
object_name                              row_count  latest_bar_close_or_finish        latest_ingest_or_start
derived.derived_runs_v0_1                2          2026-01-18 20:59:04.343906+00   2026-01-18 20:59:03.534487+00
derived.v_ovc_c1_features_v0_1           59875      null                             null
derived.v_ovc_c2_features_v0_1           59875      2026-02-19 10:00:00+00          null
derived.v_ovc_c3_features_v0_1           59875      2026-02-19 10:00:00+00          null
derived.v_ovc_c_outcomes_v0_1            59875      2026-02-19 10:00:00+00          null
derived.v_path1_evidence_dis_v1_1        59875      2026-02-19 10:00:00+00          null
derived.v_path1_evidence_lid_v1_0        59875      2026-02-19 10:00:00+00          null
derived.v_path1_evidence_res_v1_0        59875      2026-02-19 10:00:00+00          null
ops.notion_sync_state                    3          2026-01-21 19:43:21.698162+00   2026-01-21 19:44:20.799466+00
ovc.ovc_blocks_v01_1_min                 59875      2026-02-19 10:00:00+00          2026-03-20 07:14:36.277491+00
ovc.ovc_candles_m15_raw                  384        2022-12-15 22:00:00+00          2026-01-22 01:27:42.970387+00
ovc.ovc_run_reports_v01                  0          null                             null
```

## 5. Cloudflare Deployed Worker Evidence

Status: **LOCAL CONFIG VERIFIED; DEPLOYED STATE NOT VERIFIED - HOLD**

Local live access is unavailable in this execution environment:

```text
wrangler: unavailable
CLOUDFLARE_API_TOKEN: not present
CLOUDFLARE_ACCOUNT_ID: not present
```

No deployed Worker version, routes, secrets, or live Worker metadata were verified.

Local repository evidence from `infra/ovc-webhook/wrangler.jsonc`:

```text
worker_name: ovc-webhook
main: src/index.ts
compatibility_date: 2026-01-12
compatibility_flags: ["nodejs_compat"]
r2_binding: RAW_EVENTS
r2_bucket: ovc-raw-events
declared_secret_names: OVC_TOKEN, DATABASE_URL
routes/custom_domains: not declared in wrangler.jsonc
```

Local Worker-to-table shape from `infra/ovc-webhook/src/index.ts`:

```text
health_path: GET /
ingest_paths: POST /tv, POST /tv_secure
secure_ingest_requires: JSON envelope, schema export_contract_v0.1_min_r1, OVC_TOKEN
database_binding: DATABASE_URL via @neondatabase/serverless
raw_archive: RAW_EVENTS.put("tv/YYYY-MM-DD/<block_id-or-iso>_<uuid>.txt", raw)
primary_upsert_table: ovc.ovc_blocks_v01_1_min
run_report_table: ovc.ovc_run_reports_v01
```

This is repository-derived evidence only. It does not prove the deployed Cloudflare Worker matches the local source or has the required secrets/bindings.

Required follow-up evidence before R0 can pass:

- deployed Worker identity/version
- route bindings
- configured secret names only, not values
- deployed code/config relationship to `infra/ovc-webhook/`
- confirmation of Worker output table/column shape

## 6. GitHub Workflow Conclusions And Artifacts

Status: **PARTIALLY VERIFIED LIVE VIA PUBLIC GITHUB API - HOLD**

Local live access is unavailable in this execution environment:

```text
gh: unavailable
GITHUB_TOKEN: absent locally
GH_TOKEN: absent locally
```

GitHub connector check against commit `2b1811a1f1e76dd2db65437998e9ce241a23b56c` returned no PR-triggered workflow runs:

```text
workflow_runs: []
```

Escalated read-only public GitHub REST access then verified recent workflow runs:

```text
run_id       workflow                         path                                      event     conclusion  created_at
29422548349  notion-sync                      .github/workflows/notion_sync.yml         schedule  failure     2026-07-15T14:12:47Z
29422349482  OVC Backfill (GBPUSD 2H)         .github/workflows/backfill.yml            schedule  success     2026-07-15T14:10:04Z
29417788227  Path1 Evidence Runner            .github/workflows/main.yml                schedule  success     2026-07-15T13:05:41Z
29401317259  OVC Option C Schedule            .github/workflows/ovc_option_c_schedule.yml schedule failure     2026-07-15T08:35:09Z
29392098759  Path 1 Evidence Range Runner     .github/workflows/path1_evidence.yml      schedule  success     2026-07-15T05:41:24Z
```

Relevant artifact references:

```text
run_id       artifact_id  artifact_name                                      expired  expires_at
29422349482  8345754246   backfill-run-artifacts                            false    2026-08-14T14:10:36Z
29401317259  8337151486   option-c-reports-c_29401317259_1_153d47b_181      false    2026-10-13T08:35:10Z
```

The public API does not expose repository secret names. The latest run evidence also shows the remote repository still had scheduled automation active at the queried HEAD before local R0 containment is committed and pushed.

Required follow-up evidence before R0 can pass:

- latest runs for `ovc_option_c_schedule.yml`
- latest runs for `notion_sync.yml`
- latest runs for `backfill.yml`
- latest runs for Path1 workflows
- artifact names/IDs/URLs where available
- run event type, conclusion, timestamp, and commit SHA

## 7. Configured Secret Names

Status: **NOT VERIFIED LIVE - HOLD**

No live GitHub or Cloudflare secret list could be queried. The following local environment variable names were checked and absent; this does not prove remote secrets are absent.

```text
DATABASE_URL: absent locally
NEON_DSN: absent locally
CLOUDFLARE_API_TOKEN: absent locally
CLOUDFLARE_ACCOUNT_ID: absent locally
GITHUB_TOKEN: absent locally
GH_TOKEN: absent locally
NOTION_TOKEN: absent locally
NOTION_BLOCKS_DB_ID: absent locally
NOTION_OUTCOMES_DB_ID: absent locally
NOTION_RUNS_DB_ID: absent locally
```

Secret values were not requested, printed, or stored.

## 8. Repository SQL Hashes

Repository SQL hashes were collected locally. Live deployed view fingerprints were collected separately via `pg_get_viewdef`; direct equality is not claimed because repository SQL and PostgreSQL-normalized view definitions are not byte-identical representations.

```text
sql/derived/v_ovc_c_outcomes_v0_1.sql            7BD34FE9AF3FFC166689CAFFEA794F7A13C089F4CC08E796A23D7DBA4B5E345B
sql/derived/v_ovc_c1_features_v0_1.sql           1A4424A83223F78C5198FF5360094243D5A55635093EE592F92D6B8FC73B789E
sql/derived/v_ovc_c2_features_v0_1.sql           E83153C35CDF72D1E7B041369F0CF51E0CAE1CDFC777BCFC461FB5A53E89003C
sql/derived/v_ovc_c3_features_v0_1.sql           4B2F7E41513DE8EBBFAAAB23C342C4735B5A4E3641349C6545163DAED8737213
sql/path1/evidence/v_path1_evidence_dis_v1_1.sql AB06103C2E418493FA9C66FBC59FA74508C2FE4C9D1C07759EA334A14F18D574
sql/option_c_v0_1.sql                            F11A28A401C85D4FA39B4CA5E1144D4A21C959517D5866FF4516171C21B647FC
```

## 9. Superseded Or Qualified Claims From Frozen Current State

This delta qualifies the following claims in `docs/pipeline/CURRENT_STATE_INVARIANTS.md` without editing that frozen document:

- `INV-C3`: The frozen document states the scheduled workflow references a mismatched script path. At HEAD `2b1811a`, `.github/workflows/ovc_option_c_schedule.yml` invokes `scripts/run/run_option_c.sh`, and that path exists. The older mismatch claim is superseded for the current checkout.
- `INV-QA1` and `INV-QA2`: The frozen document says workflow sanity does not execute pytest and no workflow runs tests. At HEAD `2b1811a`, `.github/workflows/ci_pytest.yml` exists. Live run status is not verified in this R0 pass.
- `INV-QA3`: The frozen document says there is no migration ledger or applied-patches tracking mechanism. Current repo contains `schema/applied_migrations.json` references in the tree, but live deployment verification is not available in this R0 pass.
- Schedule claims for Option C and Notion are superseded by this R0 containment commit once merged: both cron schedules are intentionally held, while manual dispatch remains.

The following claims remain unverified live in this R0 pass:

- live Cloudflare Worker deployment and secret names
- live repository and Cloudflare configured secret names
- direct migration/application state equality versus repository SQL hashes

## 10. R0 Gate Result

**Gate result: HOLD**

Rationale:

- Unsafe cron automation for Option C and Notion is contained in the repository working tree.
- Manual dispatch is preserved for controlled diagnosis.
- Live Neon object inventory, view fingerprints, counts, and latest timestamps were collected through the Neon connector.
- Live GitHub workflow evidence is partial: latest relevant runs and artifact references were collected through the public GitHub API, but repository secret names could not be listed.
- Live Cloudflare evidence could not be collected because `wrangler`, Cloudflare credentials, and a Cloudflare connector are unavailable locally.
- Remote GitHub schedule containment is verified: raw GitHub workflow files on `main` after push contain `workflow_dispatch` and no `schedule`/`cron` trigger for Option C or Notion Sync.
- R0 requires live deployed objects and active automation to be known before `PASS`.

R0 should not proceed to R1 until an operator provides live Cloudflare access and repository/Cloudflare secret-name evidence.
