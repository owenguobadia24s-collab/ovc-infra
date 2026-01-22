# Path 1 Evidence Protocol v1.0

**Status:** FROZEN (mechanics)  
**Scope:** End-to-end execution of Path 1 Evidence Runs (observational only)

## Purpose

Path 1 Evidence Runs exist to generate **repeatable observational artifacts** over frozen Option B scores and canonical Option C outcomes, without modifying any canonical objects.

This protocol freezes the *procedure*, not the conclusions.

## Canonical Boundaries

- **Option B (Canonical Spine):** descriptive facts and frozen score views
- **Path 1 (Non-Canonical):** evidence studies and run artifacts only
- **Option C (Canonical Outcomes):** realized outcomes view used for joins

## Governance (Non-Negotiable)

- DO NOT modify any Option B canonical views/tables/contracts
- DO NOT modify SCORE_LIBRARY_v1
- Frozen scores only:
  - DIS-v1.1
  - RES-v1.0
  - LID-v1.0
- DO NOT add new scores
- DO NOT add interpretation layers
- DO NOT introduce thresholds/signals/trading logic
- Outputs are **observational only**
- Runs are **append-only** (no retroactive edits)

## Path 1 Contract Freeze (v1.0)

Path 1 is **frozen at v1.0**. The contract is stable and must not change without an explicit
version bump and compatibility note.

Frozen components (v1.0):
- `scripts/path1/run_evidence_queue.py` (mechanics + output semantics)
- Run folder layout: `reports/path1/evidence/runs/<run_id>/`
- Canonical ledger semantics: `reports/path1/evidence/INDEX.md` is append-only and authoritative

Rule for changes:
- Any change to the frozen components requires an explicit version bump (v1.0 -> v1.1/v2.0)
  plus a compatibility note describing what changed and why.

## Observability (Non-Canonical)

- **No-op is success.** If no new evidence is generated, the run exits `0`, commits nothing,
  and still emits a summary.
- `$GITHUB_STEP_SUMMARY` is **non-canonical**. It is for human-readable context only.
- The **canonical ledger** remains `INDEX.md + run folders` only.

## Deployment Chain (Strict Order)

Follow `docs/path1/EVIDENCE_RUNS_HOWTO.md` exactly.

If (and only if) required due to schema drift / fresh environment:
1) Apply DB patches
2) Deploy canonical C1/C2/C3 feature views
3) Deploy Option C outcomes view
4) Deploy Path 1 score views (frozen)
5) Deploy evidence join views (read-only)

Verify required views exist before studies.

## Run Execution Procedure

1) Choose run_id using convention: `p1_{YYYYMMDD}_{SEQ}`
2) Choose requested date range (weekday 5-day block) and symbol(s)
3) If requested range returns 0 rows:
   - substitute a nearest non-overlapping weekday range with data
   - document substitution reason and actual range in RUN.md
4) Create run directory:
   `reports/path1/evidence/runs/<run_id>/`
   with:
   - RUN.md
   - DIS_v1_1_evidence.md
   - RES_v1_0_evidence.md
   - LID_v1_0_evidence.md
   - outputs/ (raw query outputs)
5) Create run-scoped SQL wrappers (run_id/symbol/date_range baked in)
6) Execute studies and capture outputs into outputs/
7) Populate RUN.md and evidence markdowns with pasted outputs
8) Update run registry: `reports/path1/evidence/INDEX.md`

## Required Artifacts

Each run MUST produce:

- `RUN.md` (metadata, exact commands, verification, governance confirmations)
- `DIS_v1_1_evidence.md`
- `RES_v1_0_evidence.md`
- `LID_v1_0_evidence.md`
- `outputs/` containing raw study output text files
- run-scoped SQL wrappers (if used by your workflow)

## Verification (Before Marking COMPLETE)

- Confirm no Option B modifications occurred
- Confirm no SCORE_LIBRARY_v1 changes occurred
- Confirm no new scores were added
- Confirm outputs contain no interpretation layer content
- Record verification results in RUN.md
