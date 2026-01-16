1) Purpose (frozen)

A Run Report answers four questions, unambiguously:

What ran?

What data was processed?

What succeeded vs failed (and why)?

Is the dataset still trustworthy after this run?

2) Report scope (v0.1)

A run report is generated for:

each live ingest window (e.g. every 2H TradingView webhook batch), or

each offline job (historical backfill, outcome computation, FULL enrichment).

One report per run. Immutable once written.

3) Report identity fields

These uniquely identify the run.

run_id (string, UUID or deterministic hash)

run_type (enum: LIVE_INGEST, HIST_BACKFILL, OUTCOME_COMPUTE, FULL_ENRICH)

run_ver (string) — version of the runner code (Worker build / Python job version)

profile (string) — MIN, OUTCOME, FULL

scheme (string) — e.g. export_contract_v0.1_min_r1, outcome_v0.1

env (string) — prod, staging, local

started_at_ms (bigint)

finished_at_ms (bigint)

duration_ms (bigint)

4) Input summary

What the run attempted to process.

input_source (string) — e.g. tv_webhook, dukascopy_csv, oanda_api

input_range (string) — free text, e.g. 2026-01-15..2026-01-16 or block_id=20260116-I-GBPUSD

expected_events (int_or_null) — null if unknown

received_events (int)

unique_events (int) — after dedupe by block_id or equivalent

duplicate_events (int)

5) Parsing & validation results

What survived the parser.

parse_ok (int) — count of payloads that parsed + validated

parse_fail (int)

fail_by_code (json) — map: { "E_DUPLICATE_KEY": 2, "E_SEMANTIC_DIR": 1 }

Invariant:

received_events = parse_ok + parse_fail

6) Insert / upsert results

What hit the database.

insert_attempted (int)

insert_success (int)

insert_skipped (int) — idempotent skip (already exists)

insert_failed (int)

Invariant:

insert_attempted = parse_ok
insert_attempted = insert_success + insert_skipped + insert_failed

7) Data quality checks (post-run)

Computed after inserts.

blocks_missing (int) — based on expected cadence (if computable)

ready0_count (int)

tradeable0_count (int)

null_rate_summary (json) — e.g. { "state_tag": 0.03, "play": 0.00 }

sanity_error_count (int) — from sanity checks (should be 0)

8) Outcome-specific fields (only when applicable)

For run_type = OUTCOME_COMPUTE.

outcomes_attempted (int)

outcomes_inserted (int)

outcomes_skipped (int)

outcomes_failed (int)

window_type (string) — e.g. NEXT_4H

outcome_ver (string)

9) Integrity & traceability

raw_events_written (int) — count written to RAW store

raw_store_path (string_or_null) — e.g. R2 prefix

schema_versions_seen (json) — e.g. { "export_contract_v0.1_min_r1": 24 }

build_ids_seen (json) — e.g. { "ovc_pine_0.1.0": 24 }

10) Final run verdict

run_status (enum: PASS, WARN, FAIL)

warnings (array of strings)

notes (string_or_empty)

Verdict rules (v0.1)

PASS: insert_failed = 0 AND sanity_error_count = 0

WARN: non-zero parse_fail OR ready0_count spike OR blocks_missing > 0

FAIL: any invariant broken OR insert_failed > 0

11) Storage & retention

Store run reports in a dedicated table: ovc_run_reports_v01

Retain indefinitely (they are tiny and priceless)

12) Minimal table DDL (spec-level)
CREATE TABLE IF NOT EXISTS ovc_run_reports_v01 (
  run_id text PRIMARY KEY,
  run_type text,
  run_ver text,
  profile text,
  scheme text,
  env text,

  started_at_ms bigint,
  finished_at_ms bigint,
  duration_ms bigint,

  input_source text,
  input_range text,
  expected_events integer,
  received_events integer,
  unique_events integer,
  duplicate_events integer,

  parse_ok integer,
  parse_fail integer,
  fail_by_code jsonb,

  insert_attempted integer,
  insert_success integer,
  insert_skipped integer,
  insert_failed integer,

  blocks_missing integer,
  ready0_count integer,
  tradeable0_count integer,
  null_rate_summary jsonb,
  sanity_error_count integer,

  outcomes_attempted integer,
  outcomes_inserted integer,
  outcomes_skipped integer,
  outcomes_failed integer,
  window_type text,
  outcome_ver text,

  raw_events_written integer,
  raw_store_path text,
  schema_versions_seen jsonb,
  build_ids_seen jsonb,

  run_status text,
  warnings jsonb,
  notes text
);

DoD — Run Report Spec v0.1 complete when:

 Report answers what ran / what data / what failed / trust status

 Invariants are explicitly defined

 PASS/WARN/FAIL rules are frozen

 Storage schema exists