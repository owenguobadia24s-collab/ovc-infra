# Option A Organization Map (Draft)
## Purpose
Map canonical ingest and raw data foundations for Option A.

## Option Scope (brief)
Raw ingest, canonical facts, resampling/time normalization, and C0/C1 foundations.

## Category Index (list folders by category)
- Data Stores & Interfaces: data, data/raw, data/raw/tradingview
- Sub-systems: src, src/history_sources, src/utils

## Folder-by-Folder Map
FOLDER: data
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: A
AUTHORITY: CANONICAL
ROLE (1 line): Repository data root for raw inputs and verification snapshots.

INPUTS (contracts/interfaces): docs/contracts/ingest_boundary.md (conceptual boundary; not enforced)
OUTPUTS (artifacts/data): data/raw/*, data/verification_private/*

CONTAINS (high-signal items):
- raw/ -> Data Stores & Interfaces -> raw ingest drops (TradingView CSV)
- verification_private/ -> QA & Governance -> verification snapshots and command logs

CROSS-REFERENCES:
- QA map for data/verification_private

FOLDER: data/raw
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: A
AUTHORITY: CANONICAL
ROLE (1 line): Canonical raw ingest drop zone.

INPUTS (contracts/interfaces): docs/contracts/ingest_boundary.md
OUTPUTS (artifacts/data): raw CSVs under data/raw/*

CONTAINS (high-signal items):
- tradingview/ -> Data Stores & Interfaces -> TradingView alert exports

CROSS-REFERENCES:
- None.

FOLDER: data/raw/tradingview
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: A
AUTHORITY: CANONICAL
ROLE (1 line): TradingView alert CSV snapshots for ingest.

INPUTS (contracts/interfaces): External TradingView export format
OUTPUTS (artifacts/data): *.csv raw alert logs

CONTAINS (high-signal items):
- TradingView_Alerts_Log_2026-01-14_6bab8.csv -> Data Stores & Interfaces -> sample raw input file

CROSS-REFERENCES:
- None.

FOLDER: src
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: A
AUTHORITY: CANONICAL
ROLE (1 line): Core Python codebase for ingest, derived computation, validation, and ops tooling.

INPUTS (contracts/interfaces): contracts/*.json (runtime validation), sql/*.sql (schema expectations)
OUTPUTS (artifacts/data): database rows, run artifacts, validation reports (via scripts)

CONTAINS (high-signal items):
- backfill_day.py -> Pipelines/A/CANONICAL -> day backfill driver
- backfill_oanda_2h.py -> Pipelines/A/CANONICAL -> 2h backfill driver
- backfill_oanda_2h_checkpointed.py -> Pipelines/A/CANONICAL -> checkpointed 2h backfill
- backfill_oanda_m15_checkpointed.py -> Pipelines/A/CANONICAL -> checkpointed m15 backfill
- ingest_history_day.py -> Pipelines/A/CANONICAL -> daily history ingest
- full_ingest_stub.py -> Pipelines/A/EXPERIMENTAL -> stub for full ingest
- validate_day.py -> QA/QA/SUPPORTING -> day-level validation entrypoint
- validate_range.py -> QA/QA/SUPPORTING -> range validation entrypoint
- ovc_artifacts.py -> Artifacts/D/SUPPORTING -> artifact utilities
- history_sources/ -> Data Stores & Interfaces/A/CANONICAL -> raw source adapters
- derived/ -> Pipelines/B/CANONICAL -> derived feature computation
- config/ -> Registries/B/SUPPORTING -> threshold registry code
- ovc_ops/ -> Orchestration/D/SUPPORTING -> ops helpers
- validate/ -> QA & Governance/QA/SUPPORTING -> validation routines
- utils/ -> Sub-systems/Cross/SUPPORTING -> shared helpers

CROSS-REFERENCES:
- Option B map for src/derived and src/config
- Option D map for src/ovc_ops and ovc_artifacts.py usage
- QA map for src/validate and validation entrypoints

FOLDER: src/history_sources
PRIMARY CATEGORY: Data Stores & Interfaces
OPTION OWNER: A
AUTHORITY: CANONICAL
ROLE (1 line): Source adapters for raw history ingest.

INPUTS (contracts/interfaces): data/raw/* (source CSVs)
OUTPUTS (artifacts/data): normalized ingest rows (via pipelines)

CONTAINS (high-signal items):
- tv_csv.py -> Data Stores & Interfaces/A/CANONICAL -> TradingView CSV reader

CROSS-REFERENCES:
- None.

FOLDER: src/utils
PRIMARY CATEGORY: Sub-systems
OPTION OWNER: Cross
AUTHORITY: SUPPORTING
ROLE (1 line): Shared utility helpers used across pipelines.

INPUTS (contracts/interfaces): None observed
OUTPUTS (artifacts/data): helper functions used by pipelines

CONTAINS (high-signal items):
- csv_locator.py -> Sub-systems/Cross/SUPPORTING -> CSV discovery helper
- __init__.py -> Sub-systems/Cross/SUPPORTING -> package init

CROSS-REFERENCES:
- Option B/C/D maps for shared usage

## Cross-Cutting References
- .github/workflows contains scheduled/CI workflows that invoke Option A backfill and ingest jobs.
- sql/00_schema.sql and sql/schema_v01.sql define canonical tables consumed by ingest pipelines.

## Unresolved / Needs Decision
- Clarify whether data/verification_private should be treated as QA-only (current classification) or shared evidence for all options.
