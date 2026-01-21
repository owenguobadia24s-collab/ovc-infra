# OVC Logging Doctrine v0.1

This doctrine records the current logging and validation pipeline as implemented
in the repo. It is descriptive (what exists), not prescriptive (what should
change).

## Option A status (Logging Foundations & Validation Normalization)
- Status: COMPLETE and LOCKED.
- Guarantees: canonical MIN facts land in `ovc.ovc_blocks_v01_1_min` via P1/P2; core validation always runs; derived validation is conditional and skipped when absent.
- Not covered: derived features, new pipelines, or any Option B meaning layers; no changes to ingestion logic or Neon schemas.

## Species (data layers)
- A) Capture Ledger (Raw Events) - R2 append-only.
- B) Canonical Facts - Neon (`ovc` schema).
- C) Derived Layers - Neon (`derived` schema via `sql/derived_v0_1.sql` and `sql/option_c_v0_1.sql`).
- D) Validation Artifacts - Neon (`ovc_qa` schema via `sql/qa_schema.sql`).

## Canonical facts invariant
Facts are canonical ONLY in `ovc.ovc_blocks_v01_1_min`; any other facts table is
legacy/non-canonical.

## Pipelines (canonical paths)

### P1 Live Capture -> Facts (TV webhook MIN -> R2 -> Neon MIN)
- Worker: `infra/ovc-webhook/src/index.ts`
- Wrangler config + R2 binding: `infra/ovc-webhook/wrangler.jsonc` (`RAW_EVENTS`)
- Canonical facts table: `sql/01_tables_min.sql` (`ovc.ovc_blocks_v01_1_min`)
- Run reports table: `sql/02_tables_run_reports.sql` (`ovc.ovc_run_reports_v01`)
- Tests: `infra/ovc-webhook/test/index.spec.ts`
- Status: PARTIAL (env-dependent, structurally sound).

### P2 Historical Backfill -> Facts (Oanda -> Neon MIN)
- Backfill workflow: `.github/workflows/backfill.yml`
- Canonical P2 backfill (Historical Backfill -> Facts): `src/backfill_oanda_2h_checkpointed.py`
- Oanda export utility (CSV-only): `scripts/oanda_export_2h_day.py`
- Canonical MIN target table: `ovc.ovc_blocks_v01_1_min` (PK: `block_id`)
- Status: PASS (canonical backfill writes to `ovc.ovc_blocks_v01_1_min`)

Proof / Evidence:
- Test date: 2024-01-10 (weekday)
- Observed: H1 candles fetched=24; 2H blocks computed=12
- Rerun: inserted_est=0 (idempotent)
- Target: `ovc.ovc_blocks_v01_1_min`
- Key: `block_id` upsert aligned with P1
- Note: Weekend/market-closure sessions may return 0 candles; use weekday dates for sanity tests.

### P3 Facts -> Derived (Derived/eval tables)
- Derived feature view: `sql/derived_v0_1.sql`
- Outcomes/eval views: `sql/option_c_v0_1.sql`
- Runner (applies eval views): `scripts/run_option_c.sh`
- Scheduled runner: `.github/workflows/ovc_option_c_schedule.yml`
- Status: OPTIONAL / PARTIAL (derived, non-blocking).

### P4 Facts + Tape -> Validation (validate_day QA)
- Entrypoint: `src/validate_day.py`
- QA schema: `sql/qa_schema.sql`
- Validation pack: `sql/qa_validation_pack.sql`
- Harness doc: `docs/tape_validation_harness.md`
- Status: PASS (core validation always runs; derived conditional).
- Core validation: unconditional.
- Derived validation: conditional and skipped when absent.

## Verb dictionary (logging vocabulary)
- `capture`: accept raw export payloads and persist to R2 (A).
- `ingest`: parse/validate contract and write canonical facts to Neon (B).
- `upsert`: idempotent write into canonical facts (B).
- `backfill`: fetch historical market data and insert canonical facts (B).
- `derive`: compute derived features and outcomes as SQL views (C).
- `evaluate`: compute outcomes/eval metrics from facts (C).
- `validate`: compare facts to tape and record QA artifacts (D).
- `archive`: store raw inputs unchanged for audit (A).

## Tape-source rule
- A validation run must use exactly one tape source per run.
- The source is recorded in `ovc_qa.tv_ohlc_2h.source` (defaulted to `csv` by
  `src/validate_day.py` when no column is present).
- Mixing sources inside a single `run_id` invalidates the run.

## Notes on gaps (current reality)
- P2 backfill now targets the canonical MIN table `ovc.ovc_blocks_v01_1_min`.

## Next Phase: Option B
- Allowed inputs: canonical facts in `ovc.ovc_blocks_v01_1_min`, raw capture ledger, and existing validation artifacts.
- Prohibited: mutating or reclassifying canonical facts.
- Requirement: all meaning layers must be replayable and fully derived from canonical inputs.

## Minimal test procedure (P2 backfill + validation)
Backfill one NY date (YYYY-MM-DD):
```
$env:BACKFILL_DATE_NY="2026-01-16"
python .\src\backfill_oanda_2h_checkpointed.py
```

Check pipeline status (optional strict mode):
```
python .\scripts\pipeline_status.py --mode detect --strict
```

Validate the same date:
```
python .\src\validate_day.py --symbol GBPUSD --date_ny 2026-01-16
```

Rerun the same date and confirm rowcount is unchanged:
```
psql -d $env:NEON_DSN -c "select count(*) from ovc.ovc_blocks_v01_1_min where sym='GBPUSD' and date_ny='2026-01-16';"
python .\src\backfill_oanda_2h_checkpointed.py
psql -d $env:NEON_DSN -c "select count(*) from ovc.ovc_blocks_v01_1_min where sym='GBPUSD' and date_ny='2026-01-16';"
```
