# v0.2 Classifier Apply Report

## Summary

Applying additive classifier rules from the v0.2 coverage proposal to
`scripts/governance/classify_change.py`. This report documents evidence
from the scratch analysis phase.

## Unknown Reduction

- **Before (v0.1)**: 160 / 264 commits classified UNKNOWN (60.6%)
- **After (v0.2)**: 10 / 264 commits classified UNKNOWN (3.8%)
- **Reduction**: 150 commits reclassified (93.8% of UNKNOWNs resolved)

Source: `.codex/_scratch/CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json`

## Invariants (all PASS)

| Invariant | Status |
|-----------|--------|
| Total commits unchanged (264) | PASS |
| No lost non-UNKNOWN classifications | PASS |
| Only UNKNOWN→known transitions | PASS |

Source: `.codex/_scratch/CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json` field `invariants`

## Path Families Newly Classified

### Class B (documentation/governance)
- `docs/` (all subdirs, extending existing B coverage of contracts/governance/phase_2_2)
- `contracts/` (top-level governance contract JSONs)
- `specs/` (specification .md files)
- `reports/ (non-path1)` (validation/verification reports; path1 remains A)
- `releases/` (release documentation)
- Root-level doc-extension files (e.g., README.md)

### Class C (code/scripts)
- `sql/ (non-path1)` (schema/query SQL; path1 remains A)
- `.codex/` (all; CHECKS/ already C under v0.1)
- `infra/` (TypeScript infrastructure code)
- `pine/` (PineScript files)
- `Tetsu/` (code directory)
- `trajectory_families/` (Python modules)
- `_archive/` (archived scripts/SQL/checks)
- `_quarantine/` (quarantined workflows/SQL/Python)
- `configs/` (threshold pack JSONs)
- `schema/` (database schema definitions)

### Class A (evidence runs)
- `artifacts/` (evidence/validation outputs)

### Class E (repo config/CI)
- `.github/ (non-workflows)` (copilot-instructions, PR template)
- `.vscode/` (editor config)
- `ovc-webhook/` (webhook config)

## Clusters Remaining UNKNOWN

- `research/` (9 commits, mixed content)
- `CLAIMS/` (2 commits, insufficient data)
- `Work Timeline/` (1 commit, insufficient data)

## Class Count Changes (v0.1 → v0.2 simulated)

| Class | Before | After | Delta |
|-------|--------|-------|-------|
| A | 64 | 69 | +5 |
| B | 21 | 118 | +97 |
| C | 123 | 162 | +39 |
| D | 6 | 6 | 0 |
| E | 58 | 65 | +7 |
| UNKNOWN | 160 | 10 | -150 |

## Note on Tracked Overlay Scope

The tracked ledger (`DEV_CHANGE_LEDGER_v0.1.jsonl`) contains 22 commits.
The scratch backfill analysis covered 264 commits (full repo history).
The tracked v0.2 overlay will cover the same 22 commits as the ledger.
The class count changes above are from the full backfill simulation;
the tracked overlay will show a subset of these changes.

## Evidence Files Referenced

- `.codex/_scratch/CLASSIFIER_COVERAGE_PROPOSAL_v0.2.md` (proposal)
- `.codex/_scratch/CLASSIFIER_COVERAGE_DIFF_PREVIEW.txt` (patch preview)
- `.codex/_scratch/CLASSIFIER_COVERAGE_STATS_BEFORE_AFTER.json` (stats)
