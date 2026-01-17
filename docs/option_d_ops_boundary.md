# Option D Ops Boundary (Automation + Operations)

## Scope (Orchestration Only)
- Schedule Option C runs, register run_id, and generate run artifacts.
- Produce run reports + spotcheck outputs for auditing.
- Enforce CI guardrails against accidental Option C semantic drift.

## Sealed Surface (Option C)
- Option C computation semantics are sealed and must not change without a version bump.
- Any semantic change requires:
  1) Bump the eval_version everywhere it appears.
  2) Update the formula_hash deterministically.
  3) Update VERSION_OPTION_C.
  4) Document the change here.

## Required Run Artifacts
- `reports/run_report_<run_id>.json`
- `reports/spotchecks_<run_id>.txt`
- Optional: `reports/run_report_<run_id>.md`

## Failure Policy
- Exit code 0 = PASS
- Exit code 1 = WARN (fails CI only in strict mode)
- Exit code 2 = FAIL (always fails CI)
