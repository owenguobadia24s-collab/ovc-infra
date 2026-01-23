# AUDIT: Rulebook Violations (Current Repo State)

**Mode:** AUDIT-ONLY  
**Agent:** OVC_Validator  
**Rulebook:** `docs/GOVERNANCE/OVC_RULEBOOK.md`  
**Audit Target:** Recurring patterns that violate the Rulebook, as evidenced in the repository.  

---

## A) Audit Scope & Method

### A.1 Scanned Folders (per instruction)
- `.github/workflows/**`
- `scripts/**`
- `sql/**`
- `reports/**`
- `artifacts/**`
- `docs/**`
- Pipeline runner entrypoints at repo root (e.g., workflow scripts, CI scripts, contracts, schema ledger)

### A.2 Heuristics / Detection Patterns Used
- **Broken/missing artifacts**: workflow references to non-existent scripts (`python …/*.py`, `bash …/*.sh`) and `Test-Path` verification.
- **Option boundary violations**: searches for prohibited read/write edges defined in Contracts (e.g., Option C reading `ovc.ovc_blocks_v01_1_min`).
- **Canonical vs derived breaches**: canonical schema contains fields explicitly prohibited by Contracts; derived behavior forcing canonical schema changes.
- **Version / naming drift**: inconsistent paths for the same intended artifact (e.g., `scripts/oanda_export_2h_day.py` vs `scripts/export/oanda_export_2h_day.py`), and docs claiming outdated status.
- **CI / determinism weaknesses**: workflows with degraded gates, missing hashing, non-scope-tied run IDs, and repo-mutating workflows (`git push`).
- **Freeze/CURRENT_STATE integrity**: `docs/pipeline/CURRENT_STATE_*` statements contradicted by committed workflows/files.

---

## B) Violations Index (Table)

> **Categories (required):**
> 1) Option Boundary Breach
> 2) Canonical vs Derived Breach
> 3) Version / Naming Drift
> 4) Change Control / Unauthorized Behavior
> 5) CI / Determinism Weakness
> 6) AI Conduct Clause Violation
> 7) Freeze / CURRENT_STATE Leak

| Violation ID | Rulebook Clause(s) violated | Category | Evidence (file + line or snippet) | Why it’s illegal (mechanical) | Severity | Suggested governance remediation (docs/tests/CI gates only) |
|---|---|---:|---|---|---|---|
| V-001 | 3.4, 5.3, 7.3 | 3 | `.github/workflows/notion_sync.yml:30` runs `python scripts/notion_sync.py`; `Test-Path scripts/notion_sync.py` → `False` | Workflow references an artifact that does not exist in repo; under Rulebook 3.4 an undefined/missing artifact “does not exist” for pipeline purposes, and CI must fail on missing artifacts. | BLOCKER | CI gate: require `ci_workflow_sanity.yml` (or equivalent) to run on `push` to `main` for all workflows, not only PRs; add explicit “missing-script” failure list to governance docs. |
| V-002 | 3.4, 5.3, 7.3 | 3 | `.github/workflows/ovc_full_ingest.yml:90` runs `python scripts/oanda_export_2h_day.py`; `Test-Path scripts/oanda_export_2h_day.py` → `False`, `Test-Path scripts/export/oanda_export_2h_day.py` → `True` | Workflow references a non-existent path for a required pipeline helper; this is naming drift that breaks the contract artifact surface and should be CI-failing. | BLOCKER | CI gate: enforce a repo-wide allowlist of “workflow-invoked script paths” and fail if any reference is missing; maintain allowlist in docs under governance. |
| V-003 | 8.2, 7.3 | 5 | Worker inserts `ended_at, meta` into `ovc.ovc_run_reports_v01`: `infra/ovc-webhook/src/index.ts:446-447`; table definition uses `finished_at` and has no `meta`: `sql/02_tables_run_reports.sql:6` | Code and schema definition disagree about the contract of `ovc.ovc_run_reports_v01`; under Rulebook 8.2 code may not exceed contract, and CI must fail when contracts are violated. | BLOCKER | CI gate: schema check must validate required columns (not just object existence) for contract-bound tables; add “telemetry schema contract” doc listing required columns and enforce via CI. |
| V-004 | 3.1, 3.3, 8.2 | 1 | Option C runner reads canonical table directly: `sql/option_c_v0_1.sql:37` (`from ovc.ovc_blocks_v01_1_min`) while Option C contract forbids it: `docs/contracts/option_c_outcomes_contract_v1.md:51-58` | Option C is contractually required to read from Option B views; reading canonical directly crosses Option boundaries and violates “contracts before code.” | BLOCKER | CI gate: fail if Option C SQL (or workflow) references `ovc.ovc_blocks_v01_1_min` (string/AST lint); add a “forbidden read edges” contract-check test in `tests/`. |
| V-005 | 4.1, 4.2, 8.2 | 2 | Canonical schema includes prohibited derived fields (examples): `sql/01_tables_min.sql` includes `state_tag`, `trend_tag`, `pred_dir`, `bias_dir`, `struct_state`, `state_key`; explicitly prohibited in `docs/contracts/A_TO_D_CONTRACT_v1.md:33-36` and `docs/contracts/option_a_ingest_contract_v1.md:46-58` | Contracts define canonical as raw/minimum facts; prohibited derived fields in canonical violate canonical vs derived hierarchy and contract supremacy. | BLOCKER | CI gate: schema check must assert canonical table column allowlist; add a “canonical schema allowlist” contract test that fails on prohibited columns. |
| V-006 | 4.2, 8.2 | 2 | Derived view expects non-existent canonical column `tf` and patch alters canonical table to satisfy derived: `sql/derived/v_ovc_c1_features_v0_1.sql:39` references `tf`; patch adds `tf` to canonical: `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql:41` | Derived-layer requirements are driving canonical schema mutation; this is back-inference from derived to canonical and violates the canonical/derived hierarchy. | MAJOR | CI gate: forbid derived SQL from referencing undefined canonical columns; require a “canonical schema contract” check before allowing any db patch to canonical tables. |
| V-007 | 7.3, 8.4, 11.1 | 7 | CURRENT_STATE doc contains claims contradicted by repo: `docs/pipeline/CURRENT_STATE_A_TO_D.md:61` (“No pytest execution in CI workflows”) but `ci_pytest.yml` exists; `docs/pipeline/CURRENT_STATE_A_TO_D.md:77` claims “No ledger” while `schema/applied_migrations.json` exists | CURRENT_STATE documents must state what is true; contradicted claims make CURRENT_STATE unreliable and violate snapshot law + documentation law. | MAJOR | Governance gate: require a periodic CI job that asserts CURRENT_STATE docs match repo reality (presence/paths of workflows and ledgers); add a “CURRENT_STATE verification checklist” doc. |
| V-008 | 8.4, 5.3 | 7 | CURRENT_STATE doc references non-existent script locations: `docs/pipeline/CURRENT_STATE_A_TO_D.md:16-17` mentions `scripts/backfill/backfill_oanda_*_checkpointed.py` (paths not present; actual scripts are under `src/`) | CURRENT_STATE contains incorrect path claims; docs are asserting implementation truth that is not evidenced. | MAJOR | CI/doc gate: lint CURRENT_STATE docs for referenced paths and verify they exist; require CURRENT_STATE regeneration when paths change. |
| V-009 | 7.3 | 5 | CI schema workflow contains an explicit “degraded gate” that does not fail when required artifact is missing: `.github/workflows/ci_schema_check.yml:58-60` prints “DEGRADED GATE…” then `exit 0` | Rulebook requires CI to fail when contracts are violated or artifacts missing; “pass on missing ledger” is explicitly non-compliant. | MAJOR | Governance-only remediation: document that degraded gates are illegal under Rulebook; CI gate policy must require hard-fail on missing required artifacts. |
| V-010 | 7.4, 5.3 | 5 | Run IDs are not tied to canonical input scope: `src/ovc_ops/run_artifact.py` defines `run_id = <timestamp>__<pipeline_id>__<git_sha7>`; runner uses timestamp-only local IDs: `scripts/run/run_option_c.sh:102` (`run_id="local_$(date -u …)"`) | Rulebook 7.4 requires run identifiers tied to version + canonical input scope; timestamp-only IDs and non-scoped IDs violate reproducibility and stable identity law. | MAJOR | CI gate: enforce a run_id format contract per pipeline (regex + required “input scope” fields); add tests that validate run.json/run reports include canonical scope hashes/identifiers. |
| V-011 | 3.4, 7.4 | 5 | Option C runner produces file outputs under `reports/` without a declared content hash: `scripts/run/run_option_c.sh:102` sets `reports_dir="reports"` and writes `run_report_*.json` (`scripts/run/run_option_c.sh:162`) | Output-generating runs must emit content hashes; these reports are artifacts not defined as hashed outputs by contract and are not integrity-bound in CI. | MINOR | CI gate: require a `sha256` sidecar for any committed or uploaded report file; document “report artifact hashing law” under governance. |
| V-012 | 4.3, 7.4 | 5 | Backfill/validate workflow writes artifacts without content hashing: `.github/workflows/backfill_then_validate.yml` writes `artifacts/runs/<run_id>/run_meta.json` with `triggered_at="$(date -u …)"` and uploads folder; no content hash emitted | Rulebook 7.4 requires output payload hash; emitting timestamped metadata without a content hash prevents determinism certification. | MINOR | CI gate: require artifact bundles to include a deterministic manifest hash (e.g., sha256 over file list + contents); document the required manifest schema in governance docs. |
| V-013 | 6.1, 6.2 | 4 | Repo-mutating workflows push commits/branches: `path1_evidence.yml` does `git push origin HEAD:main` (`.github/workflows/path1_evidence.yml:172`); `main.yml` does `git push` (`.github/workflows/main.yml:102`); `path1_evidence_queue.yml` does `git push origin \"$BRANCH\"` (`.github/workflows/path1_evidence_queue.yml:368`) | Automated commits are Changes; Rulebook requires explicit Change Control authorization + Change Record + evidence. No Change Control record is evidenced in repo for these automated writes. | MAJOR | Governance-only remediation: require a “workflow write authorization registry” doc listing which workflows may write to which paths; CI gate must fail if workflow writes outside registry allowlist. |
| V-014 | 3.2, 3.4 | 1 | Option D workflow commits `artifacts/path1_summary.json` but Option D contract does not define `artifacts/` as an output root: `.github/workflows/path1_evidence_queue.yml:182` reads it; `.github/workflows/main.yml:73` stages it | Outputs outside declared Option directory roots violate boundary law unless explicitly contracted; this artifact is outside Option D’s declared `reports/path1/evidence/...` outputs. | MAJOR | Governance-only remediation: update Option D contract to explicitly include or forbid `artifacts/` outputs; CI gate should enforce option root allowlists for committed paths. |

---

## C) Pattern Catalogue (Most Important Section)

### Pattern 1 — “Workflow References a Non-Existent Script Path”

- Pattern Definition: A workflow invokes `python …` or `bash …` with a repo-relative path that does not exist.
- How to detect:
  - `rg -n "python\\s+[^\\s]+\\.py|bash\\s+[^\\s]+\\.sh" .github/workflows`
  - For each referenced path, verify existence (e.g., `Test-Path <path>`).
- Instances list:
  - `.github/workflows/notion_sync.yml` (invokes `scripts/notion_sync.py`, missing)
  - `.github/workflows/ovc_full_ingest.yml` (invokes `scripts/oanda_export_2h_day.py`, missing)
- Violated clause(s):
  - Rulebook: 3.4, 5.3, 7.3
- Proposed guardrail (docs/CI only):
  - CI: run `ci_workflow_sanity.yml` (or equivalent) on `push` to `main`, not only on PR paths.
  - Docs: maintain a canonical “workflow entrypoint registry” mapping each workflow to allowed script paths.

---

### Pattern 2 — “CURRENT_STATE Documents Contradict Repo Reality”

- Pattern Definition: `docs/pipeline/CURRENT_STATE_*` asserts facts that are contradicted by committed code/workflows/files (wrong paths, missing/existing CI gates).
- How to detect:
  - Extract path-like tokens from CURRENT_STATE docs and verify with `Test-Path`.
  - Compare CURRENT_STATE claims about CI/workflows to `.github/workflows/` inventory.
- Instances list:
  - `docs/pipeline/CURRENT_STATE_A_TO_D.md` (claims “No pytest execution in CI workflows” and “No ledger”; references non-existent `scripts/backfill/...` paths)
  - `docs/pipeline/CURRENT_STATE_TRUST_MAP.md` (marks “Migration state — No ledger” while `schema/applied_migrations.json` exists)
  - `docs/pipeline/CURRENT_STATE_INVARIANTS.md` (contains multiple claims contradicted by `.github/workflows/ci_pytest.yml` and `.github/workflows/ci_schema_check.yml`)
- Violated clause(s):
  - Rulebook: 8.4, 11.1
- Proposed guardrail (docs/CI only):
  - CI: add a “CURRENT_STATE verifier” job that checks referenced workflow/script paths exist and that CI presence/absence claims match actual files.
  - Docs: require a “regen checklist” section inside CURRENT_STATE files listing the commands used to generate/verify them.

---

### Pattern 3 — “Contract/Schema Drift (Code Uses Columns Not in Declared Schema)”

- Pattern Definition: Runtime code writes/reads columns that do not match the repository’s schema definitions/migrations.
- How to detect:
  - `rg -n "INSERT INTO .*\\(" infra/** src/** sql/**` and compare column lists to SQL migrations.
  - CI: column existence checks (information_schema) for contract tables.
- Instances list:
  - `infra/ovc-webhook/src/index.ts` writes `ended_at` and `meta` into `ovc.ovc_run_reports_v01`
  - `sql/02_tables_run_reports.sql` defines `finished_at` and no `meta`
- Violated clause(s):
  - Rulebook: 8.2, 7.3
- Proposed guardrail (docs/CI only):
  - CI schema check must validate required columns and types for contract tables (not only existence of table/view).

---

### Pattern 4 — “Canonical Contains Prohibited Derived Columns”

- Pattern Definition: Canonical tables contain fields declared “PROHIBITED” by Contracts (semantic tags/predictions/state).
- How to detect:
  - Compare `sql/01_tables_min.sql` column set to allowlist in `docs/contracts/A_TO_D_CONTRACT_v1.md` and `docs/contracts/option_a_ingest_contract_v1.md`.
- Instances list:
  - `sql/01_tables_min.sql` (canonical table includes: `state_tag`, `trend_tag`, `pred_dir`, `bias_dir`, `struct_state`, `state_key`, etc.)
- Violated clause(s):
  - Rulebook: 4.1, 4.2, 8.2
- Proposed guardrail (docs/CI only):
  - Add a “canonical schema allowlist” test that fails if prohibited columns exist in canonical tables.

---

### Pattern 5 — “Derived Forces Canonical Mutation”

- Pattern Definition: A derived/view implementation forces changes to canonical schema to satisfy derived expectations (instead of updating derived logic/contracts).
- How to detect:
  - Look for patches altering canonical tables inside Option D/Path folders (e.g., `sql/path1/db_patches/**`).
  - Search for commentary like “view references column that does not exist”.
- Instances list:
  - `sql/derived/v_ovc_c1_features_v0_1.sql` (references `tf`)
  - `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql` (adds generated column `tf` to canonical)
- Violated clause(s):
  - Rulebook: 4.2, 8.2
- Proposed guardrail (docs/CI only):
  - CI: forbid canonical-table ALTERs outside Option A migration directory (allowlist).
  - Docs: “canonical schema changes require Change Control record” policy.

---

### Pattern 6 — “Degraded CI Gates (Non-Failing on Missing Required Artifacts)”

- Pattern Definition: CI steps explicitly choose to pass when required artifacts/ledgers are missing.
- How to detect:
  - Search for “DEGRADED”, “Skipping”, “exit 0” in CI workflows.
- Instances list:
  - `.github/workflows/ci_schema_check.yml` (`DEGRADED GATE … exit 0`)
- Violated clause(s):
  - Rulebook: 7.3
- Proposed guardrail (docs/CI only):
  - Governance policy: degraded gates are illegal under Rulebook; CI must hard-fail on required artifacts missing.

---

### Pattern 7 — “Run IDs Not Tied to Canonical Input Scope”

- Pattern Definition: Run identifiers are derived from timestamps/UUIDs without binding to canonical input scope and version, preventing deterministic replay certification.
- How to detect:
  - Locate run_id generation logic and verify whether canonical scope (symbol/date range/table hash) is included.
- Instances list:
  - `src/ovc_ops/run_artifact.py` (`run_id = <timestamp>__<pipeline_id>__<git_sha7>`)
  - `scripts/run/run_option_c.sh` (`run_id="local_$(date -u …)"`)
  - `.github/workflows/backfill_then_validate.yml` (`RUN_ID="gh_${{ github.run_id }}_${{ github.run_attempt }}"`)
- Violated clause(s):
  - Rulebook: 7.4, 5.3
- Proposed guardrail (docs/CI only):
  - Define a run_id contract per pipeline and enforce via CI (regex + required scope fields).

---

### Pattern 8 — “Repo-Mutating Automation Without Evidenced Change Control”

- Pattern Definition: Workflows commit/push generated content (to `main` or branches/PRs) without an evidenced Change Control record and without required determinism evidence.
- How to detect:
  - `rg -n "git push|git commit" .github/workflows`
  - Inventory which paths are staged/committed.
- Instances list:
  - `.github/workflows/path1_evidence.yml`
  - `.github/workflows/path1_evidence_queue.yml`
  - `.github/workflows/main.yml`
- Violated clause(s):
  - Rulebook: 6.1, 6.2, 7.4
- Proposed guardrail (docs/CI only):
  - Create a governance “workflow write allowlist” and require CI to validate workflow writes stay within allowed paths.

---

## D) Option Boundary Mapping (as observed)

### D.1 Observed Boundaries (from committed Contracts + code)
- **Option A (Ingest)**:
  - Writes to canonical tables `ovc.ovc_blocks_v01_1_min` and `ovc.ovc_candles_m15_raw` and raw R2 capture. (`docs/contracts/option_a_ingest_contract_v1.md`, `infra/ovc-webhook/src/index.ts`, `src/backfill_oanda_*`)
- **Option B (Derived)**:
  - Produces `derived.v_ovc_c*_features_v0_1` views and materialized `derived.ovc_c1_features_v0_1`/`derived.ovc_c2_features_v0_1` tables. (`docs/contracts/option_b_derived_contract_v1.md`, `sql/derived/`, `src/derived/`)
- **Option C (Outcomes)**:
  - Contract-authoritative outcomes view is `derived.v_ovc_c_outcomes_v0_1`. (`docs/contracts/option_c_outcomes_contract_v1.md`, `sql/derived/v_ovc_c_outcomes_v0_1.sql`)
  - A deprecated outcomes path exists and is used by the runner SQL (`sql/option_c_v0_1.sql`). (`docs/contracts/option_c_outcomes_contract_v1.md`)
- **QA (Validation)**:
  - CI + scripts validate object existence and test suite; validation outputs live under `reports/validation/` and CI logs. (`docs/contracts/qa_validation_contract_v1.md`, `.github/workflows/ci_schema_check.yml`, `.github/workflows/ci_pytest.yml`)
- **Option D (Evidence)**:
  - Path1 evidence outputs under `reports/path1/evidence/...` and DB evidence views under `derived.*`. (`docs/contracts/option_d_evidence_contract_v1.md`, `scripts/path1/*`, `sql/path1/*`)
  - Path2 is “docs-only / not implemented”. (`docs/contracts/PATH2_CONTRACT_v1_0.md`)

### D.2 Observed Violations of Boundaries
- Canonical contains columns prohibited by Option A / A→D contracts (Rulebook 4.1/4.2/8.2). Evidence: `sql/01_tables_min.sql` vs `docs/contracts/A_TO_D_CONTRACT_v1.md`.
- Option C runner reads canonical table directly (Rulebook 3.1/3.3/8.2). Evidence: `sql/option_c_v0_1.sql:37`.
- Option D commits artifacts outside declared evidence root (`artifacts/path1_summary.json`) (Rulebook 3.2/3.4). Evidence: `.github/workflows/main.yml:73`, `.github/workflows/path1_evidence_queue.yml:182`.

If additional Option directory roots exist beyond the referenced Contracts, they are UNKNOWN (not evidenced in repository Contracts).

---

## E) Determinism & CI Risk Summary

### E.1 Workflow Steps with Nondeterminism / Unstable Identifiers
- Timestamp-based IDs and metadata:
  - `.github/workflows/path1_evidence_queue.yml:122` (`TIMESTAMP=$(date -u …)`)
  - `.github/workflows/path1_evidence.yml:92` (`date -u -d "yesterday" …`)
  - `.github/workflows/backfill_then_validate.yml:174` (`triggered_at="$(date -u …)"`)
  - `scripts/run/run_option_c.sh:67,105,159` (`date -u …`)
- Random UUID usage (non-deterministic object keying):
  - `infra/ovc-webhook/src/index.ts:401` uses `crypto.randomUUID()` to generate raw event key suffix.

### E.2 Workflow Steps that Commit Generated Outputs Without Stable Hashing
- `.github/workflows/path1_evidence.yml` commits and pushes `reports/path1/evidence/...` but does not require a deterministic manifest hash for the committed content.
- `.github/workflows/main.yml` stages and pushes `reports/path1/evidence/...` and `artifacts/path1_summary.json` without a required content-hash artifact.
- `.github/workflows/path1_evidence_queue.yml` creates branches/PRs with generated outputs; no required hashing gate is evidenced in the workflow.

### E.3 Workflow Steps that Write Outside Allowed Directories (per Contracts)
- `artifacts/path1_summary.json` is staged/committed by workflows but is not defined as an Option D output root in `docs/contracts/option_d_evidence_contract_v1.md`.
- `scripts/run/run_option_c.sh` writes reports into top-level `reports/` (not defined as an Option C contract output directory).
- `.github/workflows/backfill_then_validate.yml` writes run logs under `artifacts/runs/...` (not defined as an Option A/B/QA contract output directory).

### E.4 Minimum CI Gates Required to Stop Drift (docs-only list)
1) **Workflow entrypoint existence gate on `push: main`** (not only PR): fail if any workflow references missing scripts. (Rulebook 7.3)
2) **Canonical schema allowlist gate**: fail if canonical tables contain prohibited derived columns. (Rulebook 4.2, 8.2)
3) **Forbidden edge gate**: fail if Option C SQL/scripts reference `ovc.ovc_blocks_v01_1_min` directly. (Rulebook 3.1/3.3/8.2)
4) **Column-level schema contract gate** for `ovc.ovc_run_reports_v01` and other contract-bound tables/views. (Rulebook 8.2)
5) **Run ID + hash gate**: require run artifacts/reports to include canonical scope identifiers + content hashes. (Rulebook 7.4)
6) **CURRENT_STATE verifier gate**: fail if CURRENT_STATE docs contradict repo inventory (workflows, ledgers, script paths). (Rulebook 8.4, 11.1)
7) **Committed-output allowlist gate**: fail if workflows commit outside explicitly contracted output roots. (Rulebook 3.2/3.4, 6.1)

---

## Mandatory Detection Checklist (Explicit)

1) Outputs written outside declared Option directory roots: **FOUND** (e.g., `artifacts/path1_summary.json`, top-level `reports/` outputs from Option C runner).
2) Workflows producing artifacts not declared / committing without gating: **FOUND** (workflow-script path drift; repo-mutating workflows without hash gates).
3) Evidence of version jumps or inconsistent version naming: **FOUND** (run_id formats differ across pipelines; contracts specify different formats than code).
4) Renames/duplicate “almost same” paths: **FOUND** (`scripts/oanda_export_2h_day.py` vs `scripts/export/oanda_export_2h_day.py`; docs refer to `scripts/backfill/...` vs actual `src/...`).
5) Canonical data overwritten by derived steps: **FOUND** (derived view expectation leads to canonical schema patch: `tf` column addition).
6) Multiple sources-of-truth for same artifact: **FOUND** (Option C authoritative outcomes view vs deprecated runner view; legacy derived view vs split implementation).
7) Missing CURRENT_STATE freeze record or contradictions: **FOUND** (freeze docs exist but contain contradicted claims).
8) Agent role leakage indicators: **FOUND** (CURRENT_STATE docs make incorrect implementation claims; CI/contract docs disagree with present workflows/files).

