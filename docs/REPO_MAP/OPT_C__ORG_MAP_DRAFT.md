# Option C Organization Map (Draft)
## Purpose
Map outcomes definitions, Option C runners, and Option C artifacts.

## Option Scope (brief)
Labels, outcome definitions, evaluation metrics, backtests/sims, and ground-truth attribution.

## Category Index (list folders by category)
- Orchestration: scripts/run
- Artifacts & Evidence: artifacts/option_c

## Folder-by-Folder Map
FOLDER: scripts/run
PRIMARY CATEGORY: Orchestration
OPTION OWNER: C
AUTHORITY: SUPPORTING
ROLE (1 line): Option C execution wrappers and migration utilities.

INPUTS (contracts/interfaces): docs/specs/OPTION_C_IMPLEMENTATION_CONTRACT_v0.1.md; sql/option_c_*.sql
OUTPUTS (artifacts/data): run reports and validation artifacts (via reports/)

CONTAINS (high-signal items):
- run_option_c.sh -> Orchestration/C/CANONICAL -> Option C runner (shell)
- run_option_c.ps1 -> Orchestration/C/SUPPORTING -> Option C runner (PowerShell)
- run_option_c_wrapper.py -> Orchestration/C/SUPPORTING -> wrapper entrypoint
- run_option_c_with_artifact.sh -> Orchestration/C/SUPPORTING -> artifact-enabled runner
- run_migration.py -> Orchestration/C/SUPPORTING -> schema migration helper

CROSS-REFERENCES:
- Option D map for scripts/ (parent) and report outputs
- Option B map for sql/option_c_*.sql

FOLDER: artifacts/option_c
PRIMARY CATEGORY: Artifacts & Evidence
OPTION OWNER: C
AUTHORITY: SUPPORTING
ROLE (1 line): Stored Option C run outputs and spotchecks.

INPUTS (contracts/interfaces): docs/specs/OPTION_C_OUTCOMES_v0.1.md
OUTPUTS (artifacts/data): run_report_sanity_local.json, spotchecks_sanity_local.txt

CONTAINS (high-signal items):
- sanity_local/ -> Artifacts & Evidence/C/SUPPORTING -> local sanity outputs

CROSS-REFERENCES:
- Option D map for artifacts/ (parent) and reports/run_report_* files

## Cross-Cutting References
- reports/run_report_* files contain Option C outputs but are stored under reports/ (Option D map).
- sql/option_c_*.sql defines Option C query outputs (Option B map).

## Unresolved / Needs Decision
- Determine authoritative location for Option C result artifacts: artifacts/option_c vs reports/ root files.
