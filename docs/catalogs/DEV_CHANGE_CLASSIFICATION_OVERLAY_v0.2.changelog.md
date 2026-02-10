# DEV Change Classification Overlay v0.2 - Changelog

## Scope
- Base ledger input: `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl`
- Prior overlay: `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl`
- New overlay: `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl`
- Builder used: `scripts/governance/build_change_classification_overlay_v0_2.py`

## What Changed vs v0.1 (Tracked Dataset)
- v0.2 is additive: a new derived overlay artifact was produced instead of editing v0.1 overlay lines.
- Row count is unchanged: 22 commits in v0.1 and 22 commits in v0.2.
- UNKNOWN reduction (tracked overlays): 4 -> 2 commits (`-2`, 50.0% reduction; 18.2% -> 9.1% of tracked rows).
- Reclassified tracked commits (`.codex/_scratch/v0_2_overlay_stats.json`):
  - `34e45abaa3e1214689e2348e295c76090f279a6c`: `UNKNOWN` -> `B,C,E`
  - `8f5c33733a2ff75f51d3c8848ada4de0596d6506`: `UNKNOWN` -> `E`

## Additive Coverage Evidence (Full-History Scratch Simulation)
Source: `.codex/_scratch/CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json`

- Total commits analyzed: 264
- UNKNOWN before: 160
- UNKNOWN after: 10
- UNKNOWN reduction: 150 (93.8%)
- Commits reclassified: 150
- Invariant checks in source file:
  - `total_unchanged`: `true`
  - `no_lost_non_unknown`: `true`
  - `only_unknown_to_known`: `true`

## Explicit Invariants for This v0.2 Apply
- No edits to v0.1 files.
- v0.2 overlay is a new derived artifact.
- Determinism checks passed for overlay and timeline (`.codex/_scratch/v0_2_repro_check.txt`).

## Seal Files
- `DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.json`
- `DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.sha256`
