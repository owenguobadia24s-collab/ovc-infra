# DEV Change Classification Overlay v0.2 - Changelog

## Scope Change
- Prior tracked v0.2 build used `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl` (22 rows), so overlay scope was 22 rows.
- Current tracked v0.2 build uses `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl` (270 rows), derived from reconciled full-history scratch ledger coverage against current `HEAD`.
- Overlay v0.2 was regenerated from ledger v0.2 using:
  - `scripts/governance/build_change_classification_overlay_v0_2.py`
  - `scripts/governance/classify_change.py`

## Current Tracked v0.2 Overlay Metrics (Full Scope)
Source: `.codex/_scratch/v0_2_overlay_stats.full.json`

- Ledger rows: 270
- Overlay rows: 270
- Row count match: true
- Hash alignment mode: strict row-order commit hash
- Hash mismatches: 0
- UNKNOWN commits: 15 (5.556%)

## Invariants
- No edits to tracked v0.1 ledger or v0.1 overlay files.
- v0.2 artifacts are versioned outputs (`DEV_CHANGE_LEDGER_v0.2.*`, `DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.*`).
- Determinism/repro check recorded in `.codex/_scratch/v0_2_full_repro_check.txt`.

## Seal Files
- `DEV_CHANGE_LEDGER_v0.2.seal.json`
- `DEV_CHANGE_LEDGER_v0.2.seal.sha256`
- `DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.json`
- `DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.sha256`
