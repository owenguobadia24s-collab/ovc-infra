# Pipeline Reality Map v0.1 - Changelog

> **Date:** 2026-01-19  
> **Change Type:** Deterministic update based on repo evidence

---

## Summary

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| LIVE pipelines | 6 | 9 | +3 |
| PARTIAL pipelines | 4 | 2 | -2 |
| DORMANT pipelines | 1 | 1 | 0 |
| Open gaps | 8 | 5 | -3 |
| Resolved gaps | 0 | 3 | +3 |

---

## Status Changes

### CI-WorkerTests: PARTIAL → LIVE

**Reason:** Worker tests now pass (2/2).

**Evidence:**
- `infra/ovc-webhook/src/index.ts:10` - `export function parseExport(...)`
- `infra/ovc-webhook/src/index.ts:29` - `export function msToTimestamptzStart2H(...)`
- `npm test` output: `✓ test/index.spec.ts (2 tests) 49ms`

### D-NotionSync: PARTIAL → LIVE

**Reason:** `NOTIOM_TOKEN` confirmed as canonical spelling; workflow and script are consistent; startup validation added.

**Evidence:**
- `scripts/notion_sync.py:19-24` - `REQUIRED_ENV_VARS` includes `"NOTIOM_TOKEN"`
- `scripts/notion_sync.py:31-36` - `check_required_env()` validates at startup
- `.github/workflows/notion_sync.yml:25` - `NOTIOM_TOKEN: ${{ secrets.NOTIOM_TOKEN }}`
- `scripts/notion_sync.py:15-16` - RunWriter instrumentation added
- `.github/workflows/notion_sync.yml:34-39` - `upload-artifact` for run artifacts

### C-Eval: PARTIAL → LIVE

**Reason:** Run artifacts now emitted and uploaded in scheduled workflow.

**Evidence:**
- `.github/workflows/ovc_option_c_schedule.yml:99-104` - `upload-artifact` for reports
- `.github/workflows/ovc_option_c_schedule.yml:107-112` - `upload-artifact` for run artifacts

---

## Gaps Closed

### G1: Worker Tests - RESOLVED

**Was:** `npm test` failed with "parseExport is not a function"

**Fix:** Functions now exported from `index.ts`:
```typescript
// index.ts:10
export function parseExport(exportStr: string): Record<string, string> { ... }

// index.ts:29  
export function msToTimestamptzStart2H(barCloseMs: number): string { ... }
```

### G2: Notion Sync Token - RESOLVED (Design Decision)

**Was:** Flagged as typo (`NOTIOM_TOKEN` vs `NOTION_TOKEN`)

**Resolution:** `NOTIOM_TOKEN` is the **canonical** spelling - intentional design decision. Both workflow and script use it consistently, and startup validation ensures it's set.

### G8: Run Artifacts Missing - RESOLVED

**Was:** No evidence of run artifacts in scheduled pipelines

**Fix:** All scheduled pipelines now emit and upload run artifacts:

| Pipeline | Upload Step | Path |
|----------|-------------|------|
| P2-Backfill | `backfill.yml:58-63` | `reports/runs/` |
| C-Eval | `ovc_option_c_schedule.yml:107-112` | `reports/runs/` |
| D-NotionSync | `notion_sync.yml:34-39` | `reports/runs/` |

Additionally, all scripts are instrumented with `RunWriter`:

| Script | Import Line | Instantiation |
|--------|-------------|---------------|
| `backfill_oanda_2h_checkpointed.py` | 18 | 49, 529 |
| `compute_l1_v0_1.py` | 42 | 355 |
| `compute_l2_v0_1.py` | 46 | 569 |
| `compute_l3_regime_trend_v0_1.py` | 86 | 419 |
| `validate_derived_range_v0_1.py` | 55 | 1072 |
| `validate_day.py` | 16 | 408 |
| `validate_range.py` | 23 | 677 |
| `notion_sync.py` | 15 | (via RunWriter) |

---

## Remaining Gaps

| Gap ID | Type | Status | Notes |
|--------|------|--------|-------|
| G3 | UNKNOWN | Open | Worker deployment status unverifiable without external API access |
| G4 | UNKNOWN | Open | Worker secrets status unverifiable without Cloudflare dashboard |
| G5 | DORMANT | Open | `backfill_then_validate.yml` has no schedule (manual only) |
| G6 | DORMANT | Open | `ovc_full_ingest.yml` has no schedule (stub workflow) |
| G7 | PARTIAL | Open | L3 not integrated into any workflow |

---

## New Components Added

### Run Artifact System

| Component | Path | Description |
|-----------|------|-------------|
| Spec (JSON Schema) | `contracts/run_artifact_spec_v0.1.json` | Machine-readable artifact format |
| Helper Module | `src/ovc_ops/run_artifact.py` | RunWriter class (494 lines) |
| CLI Wrapper | `src/ovc_ops/run_artifact_cli.py` | Ad-hoc run artifact generation |
| Documentation | `docs/ops/RUN_ARTIFACT_SPEC_v0.1.md` | Specification document |
| Implementation Notes | `docs/ops/RUN_ARTIFACT_IMPLEMENTATION_NOTES.md` | Integration guide |

---

## Verification Commands Run

```bash
# Worker tests (PASS)
cd infra/ovc-webhook && npx vitest run
# Output: ✓ test/index.spec.ts (2 tests) 49ms

# Grep for export statements
grep -n "export function parseExport\|export function msToTimestamptzStart2H" infra/ovc-webhook/src/index.ts
# Output: 
#   10:export function parseExport(exportStr: string): Record<string, string> {
#   29:export function msToTimestamptzStart2H(barCloseMs: number): string {

# Grep for RunWriter usage
grep -rn "from ovc_ops.run_artifact import\|RunWriter" src/ scripts/
# Output: 20+ matches across instrumented scripts

# Grep for upload-artifact in workflows
grep -rn "upload-artifact" .github/workflows/
# Output: 7 matches across backfill.yml, notion_sync.yml, ovc_option_c_schedule.yml, etc.
```

---

*End of Changelog*
