# OVC Logging Doctrine v0.1

This doctrine records the current logging and validation pipeline as implemented
in the repo. It is descriptive (what exists), not prescriptive (what should
change).

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

### P2 Historical Backfill -> Facts (Oanda -> Neon MIN)
- Backfill workflow: `.github/workflows/backfill.yml`
- Backfill script: `src/backfill_oanda_2h_checkpointed.py`
- Oanda export utility (CSV-only): `scripts/oanda_export_2h_day.py`
- Current target table used by backfill scripts: `ovc_blocks_v01` (no schema qualifier)
- Canonical MIN target table (spec): `ovc.ovc_blocks_v01_1_min`

### P3 Facts -> Derived (Derived/eval tables)
- Derived feature view: `sql/derived_v0_1.sql`
- Outcomes/eval views: `sql/option_c_v0_1.sql`
- Runner (applies eval views): `scripts/run_option_c.sh`
- Scheduled runner: `.github/workflows/ovc_option_c_schedule.yml`

### P4 Facts + Tape -> Validation (validate_day QA)
- Entrypoint: `src/validate_day.py`
- QA schema: `sql/qa_schema.sql`
- Validation pack: `sql/qa_validation_pack.sql`
- Harness doc: `docs/tape_validation_harness.md`

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
- P2 backfill scripts currently write to `ovc_blocks_v01`, not the canonical
  MIN table `ovc.ovc_blocks_v01_1_min`. This is a schema alignment gap and is
  reported as PARTIAL/FAIL by the status harness when detected.
