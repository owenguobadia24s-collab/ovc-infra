# Phase 3 Architecture Validation Report v0.1

**Version**: 0.1  
**Status**: DRAFT — normative  
**Date**: 2026-02-05 (UTC)  
**Authority**: This report validates architecture. It introduces no execution authority.

---

## 1. Phase 3 Invariants (Copied as Law)

The following invariants are copied verbatim from the Phase 3 Definition of Done. They are LAW for all Phase 3 work.

### 1.1 Global Invariants (Must All Be True)

| ID | Invariant | Architectural Enforcement |
|----|-----------|---------------------------|
| P3-INV-01 | No Phase 3 component can write to registries | File system mounted read-only; no write credentials provisioned; static file viewer or read-only API only |
| P3-INV-02 | No Phase 3 component can mutate artifacts | No write paths in codebase; FS permissions enforce read-only; container/OS-level enforcement |
| P3-INV-03 | No Phase 3 component can update active pointers | Pointer files are read, never written; no pointer mutation functions exist in Phase 3 code |
| P3-INV-04 | No Phase 3 component can trigger executions | No subprocess.run, no HTTP POST to CI, no workflow dispatch; UI is purely navigational |
| P3-INV-05 | No Phase 3 component can reseal anything | Sealing logic (manifest generation, SHA256 computation for seals) is excluded from Phase 3 codebase |
| P3-INV-06 | All Phase 3 outputs are derived from sealed artifacts only | Every view traces to a manifest-sealed source referenced in ACTIVE_REGISTRY_POINTERS_v0_1.json |
| P3-INV-07 | All Phase 3 outputs are reproducible | Identical canon inputs produce identical view outputs; deterministic rendering |
| P3-INV-08 | All Phase 3 outputs are discardable without loss of truth | Phase 3 outputs are presentation artifacts; deleting them loses nothing canonical |
| P3-INV-09 | Phase 3 introduces zero new authority surfaces | No buttons, no approvals, no triggers, no fix flows, no automation hooks |

**Violation of any invariant = Phase 3 failure.**

---

## 2. Threat Model: How Phase 3 Could Accidentally Gain Power

The following table enumerates the top write/authority risks and the architectural mechanisms that prevent each.

| ID | Threat | Attack Vector | Prevention Mechanism (Architectural) |
|----|--------|---------------|--------------------------------------|
| TM-01 | Write to registry files | Phase 3 code opens registry file with write mode | **File system mount**: Registry directories mounted read-only at OS level. Static viewer reads from pre-built directory snapshot. No `open(path, 'w')` or equivalent in Phase 3 codebase (enforced by code review gate + grep audit). |
| TM-02 | Mutate active pointers | Phase 3 code modifies `ACTIVE_REGISTRY_POINTERS_v0_1.json` | **No pointer mutation functions**: Phase 3 codebase contains zero functions that write to pointer files. Pointer file is read once at startup. FS read-only mount prevents accidental writes. |
| TM-03 | Trigger CI workflow | Phase 3 backend makes HTTP POST to GitHub Actions API | **No GitHub token provisioned**: Phase 3 environment has no `GITHUB_TOKEN` or PAT with workflow dispatch scope. No HTTP client code for GitHub API exists in Phase 3 codebase. |
| TM-04 | Subprocess execution | Phase 3 code calls `subprocess.run()` or `os.system()` to invoke scripts | **Subprocess ban**: Phase 3 codebase excludes `subprocess`, `os.system`, `os.popen`, `Popen`. Enforced by static analysis gate (grep + AST check). |
| TM-05 | Database write | Phase 3 code executes INSERT/UPDATE/DELETE SQL | **No database credentials**: Phase 3 environment has no DSN with write privileges. If database access is required, it uses a read-only replica connection string with SELECT-only grants. |
| TM-06 | Git commit/push | Phase 3 code runs `git commit` or `git push` | **No git write commands**: Phase 3 codebase excludes `git commit`, `git push`, `git add`. Git binary not invoked. No `.git` write access from Phase 3 runtime environment. |
| TM-07 | Reseal artifacts | Phase 3 code generates new `manifest.json` or `MANIFEST.sha256` | **Sealing logic excluded**: All sealing functions (`seal_run_folder`, `compute_root_sha256`, manifest builders) are NOT imported or included in Phase 3 codebase. Static analysis confirms no sealing code. |
| TM-08 | Auto-refresh mutates state | UI polling or auto-refresh alters cache or state | **Stateless rendering**: Each page load re-reads canon files. No server-side state persisted. Refresh produces identical output for identical canon (determinism). No cache mutation. |
| TM-09 | Hidden action buttons | UI contains hidden or disabled buttons that could be enabled | **UI audit checklist**: All interactive elements are navigation, filter, sort, or explanation only. Build-time audit scans for `onClick` handlers that invoke non-navigation actions. Any action handler = build failure. |
| TM-10 | Agent introduction | Phase 3 introduces an AI agent or automated decision-maker | **Agent ban**: No LLM integration, no automated classifiers, no decision engines. Phase 3 is pure display. Any `import openai` or equivalent = build failure. |

---

## 3. Read-Only Enforcement Model

### 3.1 Chosen Architecture

**Static Viewer (renders from files)**

Phase 3 shall be implemented as a **static file viewer** that:

1. Reads from a read-only mounted directory containing all sealed registry artifacts
2. Renders HTML/Markdown views at build time or on-demand via a read-only local server
3. Has no backend capable of write operations

### 3.2 Justification

| Alternative | Rejected Because |
|-------------|------------------|
| Local service with read-only FS permissions | Requires runtime enforcement discipline; misconfiguration possible |
| Web UI backed by read-only API | Requires API credential management; attack surface larger |
| **Static viewer (renders from files)** | **SELECTED**: Smallest attack surface; no credentials; no network; deterministic |

### 3.3 Read-Only Enforcement Statement

**"No write credentials exist."**

The Phase 3 control panel operates with:

- **No `GITHUB_TOKEN`** with push/dispatch scope
- **No database DSN** with INSERT/UPDATE/DELETE grants
- **No filesystem paths** opened in write mode
- **No API credentials** for any system that can mutate state

### 3.4 Proof-of-Enforcement Approach

| Layer | Enforcement Mechanism |
|-------|----------------------|
| **OS / Container** | Mount `artifacts/`, `.codex/RUNS/`, `docs/phase_2_2/` as read-only volumes. Container user has no write permissions to these paths. |
| **Code** | Static analysis gate (grep + AST) confirms: no `open(..., 'w')`, no `subprocess`, no `os.system`, no `git push`, no HTTP POST to GitHub, no sealing imports. |
| **Build** | CI workflow runs `phase3_read_only_audit.py` that fails if any write-capable code is detected. |
| **Runtime** | No environment variables containing write-capable credentials. No secrets mounted. |
| **IAM (if cloud-hosted)** | Read-only IAM role attached; no S3 PutObject, no RDS write, no Secrets Manager write. |

---

## 4. Canonical Data Sources Map

Every required Phase 3 view maps to exact canonical source(s). No view invents meaning.

| View | Canonical Source(s) | Source File(s) / Registry ID(s) | Seal Expectation | Derivation Rule |
|------|---------------------|----------------------------------|------------------|-----------------|
| **Runs View** | Run Registry | `.codex/RUNS/<run_id>/RUN_REGISTRY_v0_1.jsonl` via `run_registry` pointer in `ACTIVE_REGISTRY_POINTERS_v0_1.json` | SEALED: `manifest_sha256 = 1c0fc2ca...` | Read JSONL lines; render timeline; status from `run.json` in each run folder |
| **Failures View** | Operation Status Table, Run Registry | `OPERATION_STATUS_TABLE_v0_1.json` via `op_status_table` pointer | SEALED: `manifest_sha256 = 152d3edb...` | Aggregate `status = FAIL` records; failure causes from `reasons` field in run.json outputs |
| **Artifact Drill-Down** | Individual sealed run folders | `.codex/RUNS/<run_id>/manifest.json`, `MANIFEST.sha256` | SEALED per run | Navigate via `run_id`; display manifest entries and hashes directly |
| **Diff View** | Registry Delta Log (for registry diffs); manifest.json (for artifact diffs) | `.codex/RUNS/<run_id>/REGISTRY_DELTA_LOG_v0_1.jsonl` | SEALED: Phase 2.2.3 builder | Diff = structural comparison of `before_root_sha256` vs `after_root_sha256`; manifest field comparison |
| **System Health View** | Drift Signals, Op Status Table, Health Contracts v0.1 | `DRIFT_SIGNALS_v0_1.json` via `drift_signals` pointer; Health Contracts v0.1 (governance doc) | SEALED: `manifest_sha256 = df8aa730...` | Apply Health State Determination Rules (Section 9 of Health Contracts v0.1); display state code H0-H9 |
| **Governance Visibility View** | Expected Versions, Enforcement Matrix, Governance Scorecard, Active Pointers | `EXPECTED_VERSIONS_v0_1.json` via `expected_versions` pointer; `OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md`; `OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.2.md` | SEALED (versions); DOC (matrix/scorecard) | Read expected versions; display enforcement levels C0-C5; list known gaps from scorecard |

### 4.1 Source Seal Summary

| Registry/Source | Sealed? | Justification if Not Sealed |
|-----------------|---------|----------------------------|
| run_registry | YES | Phase 2.1 builder |
| op_status_table | YES | Phase 2.1 builder |
| drift_signals | YES | Phase 2.1 builder |
| migration_ledger | YES | Phase 2.2.1 seal promotion |
| expected_versions | YES | Phase 2.2.1 seal promotion |
| threshold_packs_file | YES | Phase 2.2.1 seal promotion |
| fingerprint_index | YES | Phase 2.2.1 seal promotion |
| derived_validation_reports | YES | Phase 2.2.1 seal promotion |
| registry_delta_log | YES | Phase 2.2.3 builder |
| threshold_registry_db | NO | NON-CLOSABLE: External database; cannot seal from repo |
| validation_range_results | NO | NON-CLOSABLE: Collection registry; individual runs |
| evidence_pack_registry | NO | NON-CLOSABLE: Collection registry; individually sealed per run |
| system_health_report | NO | NON-CLOSABLE: Presentation-only artifact |
| Health Contracts v0.1 | DOC | Governance document; not a data artifact |
| Enforcement Matrix | DOC | Governance document; frozen |
| Governance Scorecard | DOC | Governance document; frozen |

---

## 5. Health State Determination Compliance

### 5.1 Health Computation Method

The Phase 3 control panel shall compute/display health using **exactly** the rules defined in Health Contracts v0.1 (Section 9: Health State Determination Rules).

| Step | Rule | Phase 3 Implementation |
|------|------|------------------------|
| 1 | Check for H9 (UNKNOWN) conditions first | Read governance artifacts; if any read fails, display H9 |
| 2 | Check for H3 (RECOVERY_REQUIRED) conditions | Evaluate H3-01 through H3-07 from Health Contracts v0.1 |
| 3 | Check for H2 (DEGRADED_BLOCKING) conditions | Evaluate H2-01 through H2-07 from Health Contracts v0.1 |
| 4 | Check for H1 (DEGRADED_NON_BLOCKING) conditions | Evaluate H1-01 through H1-07 from Health Contracts v0.1 |
| 5 | If no degradation conditions found, state is H0 (HEALTHY) | Display H0 with all invariants confirmed |

### 5.2 Compliance Statement

**"No custom heuristics."**

The Phase 3 control panel:

- Does NOT invent health states beyond H0, H1, H2, H3, H9
- Does NOT create custom scoring or weighting
- Does NOT use color-only signaling without text explanation
- Does NOT display "Looks fine" or equivalent summaries
- DOES display the exact condition IDs (H0-01, H1-01, etc.) that triggered the current state
- DOES explicitly note when state is UNKNOWN (H9)

### 5.3 Health Display Requirements

| Requirement | Implementation |
|-------------|----------------|
| Current health state (H0–H9) | Large, prominent display of state code and name |
| Conditions triggering that state | Table of condition IDs with boolean status |
| Whether degradation is acceptable/blocking/recovery-required | Explicit label per Health Contracts v0.1 definitions |
| Explicit note when state is UNKNOWN | H9 displayed with "Health cannot be determined from available evidence" |

---

## 6. Diff Semantics

### 6.1 Artifact Diffs (Manifest Diffs)

| Aspect | Definition |
|--------|------------|
| **What is diffed** | `manifest.json` files between two sealed run folders |
| **Diff algorithm** | Structural comparison of `{relpath, bytes, sha256}` entries |
| **Output** | Added files, removed files, changed files (hash mismatch) |
| **Source** | Two sealed run folders referenced by `run_id` |

### 6.2 Registry Diffs (Delta Log Use)

| Aspect | Definition |
|--------|------------|
| **What is diffed** | Registry state transitions as recorded in `REGISTRY_DELTA_LOG_v0_1.jsonl` |
| **Delta log role** | **Explanatory only** — the delta log explains what changed between snapshots |
| **Delta log does NOT** | Drive control, trigger actions, or update pointers |
| **Output** | `transition_type` (BOOTSTRAP / UPDATE), `before_root_sha256`, `after_root_sha256`, `diff_summary` |

### 6.3 Delta Log Compliance Statement

**"Delta log is explanatory only; it does not drive control."**

The Phase 3 control panel:

- Reads delta log records as historical memory
- Displays transitions for audit purposes
- Does NOT use delta log to trigger updates, repairs, or pointer changes
- Does NOT interpret delta log records as commands

---

## 7. Non-Authority UX Rules

### 7.1 Allowed Interactions

| Interaction Type | Allowed? | Examples |
|------------------|----------|----------|
| Navigation | YES | Click to view run details; click to view artifact |
| Filtering | YES | Filter runs by date, status, option (A/B/C/D/QA) |
| Sorting | YES | Sort runs by timestamp, sort failures by count |
| Explanation | YES | Expand to see condition details; show hash values |
| Search | YES | Search for run_id, registry_id, operation_id |
| Copy to clipboard | YES | Copy hash values, copy run_id |
| Export view as text | YES | Download current view as static file (no new seals) |

### 7.2 Forbidden Interactions

| Interaction Type | Forbidden? | Why |
|------------------|------------|-----|
| Trigger | FORBIDDEN | No button to start a run, workflow, or build |
| Fix | FORBIDDEN | No "Fix this issue" button |
| Approve | FORBIDDEN | No approval flows |
| Reject | FORBIDDEN | No rejection flows |
| Reseal | FORBIDDEN | No "Reseal artifact" action |
| Update pointer | FORBIDDEN | No "Set as active" action |
| Edit | FORBIDDEN | No inline editing of any value |
| Auto-refresh with side effects | FORBIDDEN | Refresh only re-reads canon; no state mutation |
| Recommend | FORBIDDEN | No "Suggested action" displays |
| Prioritize | FORBIDDEN | No "High priority" classifications |

### 7.3 UI Audit Checklist (Build Gate)

The following checks MUST pass for Phase 3 build to succeed:

| Check ID | Check | Failure Condition |
|----------|-------|-------------------|
| UI-01 | No `onClick` handlers that invoke write functions | Any handler calling write/trigger function |
| UI-02 | No forms with `action` attributes posting to mutation endpoints | Any form POST to non-read endpoint |
| UI-03 | No hidden `<button>` or `<input type="submit">` elements | Any hidden action controls |
| UI-04 | No `fetch()` or `axios` calls with methods other than GET | Any POST/PUT/DELETE/PATCH |
| UI-05 | No WebSocket connections to mutation services | Any bidirectional channel to write service |
| UI-06 | All links are internal navigation or external read-only references | Any link to mutation endpoint |
| UI-07 | No `<button>` with action-implying labels (Fix, Approve, Run, Trigger, Update) | Forbidden button labels |
| UI-08 | No agent/AI integration imports | `import openai`, `import anthropic`, etc. |

---

## 8. Reproducibility Plan

### 8.1 Determinism Guarantee

Given identical canon:
- Identical views render
- Identical diffs appear
- Identical health states display

### 8.2 Reproducibility Rules

| Rule | Implementation |
|------|----------------|
| Same input files → same output views | Rendering logic is pure function of file contents |
| No randomness | No random IDs, no shuffled ordering |
| No external API calls affecting output | All data from local sealed files only |
| Deterministic ordering | All lists sorted by deterministic key (lexicographic, timestamp) |

### 8.3 Allowable Non-Canonical Display Fields

The following fields may appear in Phase 3 views but are **explicitly labeled as non-canonical**:

| Field | Label | Source |
|-------|-------|--------|
| Current render timestamp | `[Rendered at: <timestamp> — non-canonical]` | Local system clock |
| User's local timezone display | `[Displayed in: <timezone> — non-canonical]` | Browser/OS timezone |
| Relative time ("5 minutes ago") | `[Relative display — non-canonical]` | Derived from canonical timestamp |

### 8.4 Refresh Invariant

Refreshing the UI CANNOT change:
- Registry state
- Active pointers
- System health (as derived from canon)
- Any sealed artifact

Refreshing MAY change:
- Render timestamp (labeled non-canonical)
- Relative time displays (labeled non-canonical)

---

## 9. DoD Coverage Matrix

Every Definition of Done clause maps to an architectural enforcement mechanism with evidence.

| DoD Clause | DoD Requirement | Architectural Enforcement | Evidence |
|------------|-----------------|---------------------------|----------|
| **0. Global Invariants** | No write/mutate/trigger/reseal | Read-only mount; code audit; no credentials | Section 2 (Threat Model), Section 3 (Enforcement Model) |
| **1. Read-Only Contract** | All sources sealed; no write credentials; architecture-enforced | Static viewer on read-only mount; no DSN/tokens | Section 3.3, 3.4 |
| **2.1 Runs View** | Timeline of runs; status; linkage to run.json | Reads `run_registry` → sealed JSONL | Section 4 (Runs View row) |
| **2.2 Failures View** | Aggregated failures; causes from events/registries | Reads `op_status_table` → sealed JSON | Section 4 (Failures View row) |
| **2.3 Artifact Drill-Down** | Navigate to sealed artifact; manifest visible | Direct file read from `.codex/RUNS/<run_id>/` | Section 4 (Artifact Drill-Down row) |
| **2.4 Diff View** | Side-by-side; structural; traceable | Manifest diff + delta log | Section 4 (Diff View row), Section 6 |
| **3. Registry Fidelity** | Every value traceable to registry/artifact/run_id | All views cite source registry_id and run_id | Section 4 (all rows) |
| **4. Determinism** | Identical canon → identical views | Pure rendering functions; no randomness | Section 8 |
| **5. Health Representation** | H0–H9 per Health Contracts v0.1; no custom heuristics | Health Contracts v0.1 logic only | Section 5 |
| **6. Governance Visibility** | Active versions; enforcement levels; known gaps | Reads Expected Versions, ECM, Scorecard | Section 4 (Governance Visibility View row) |
| **7. No Decision Surfaces** | No action buttons; navigation/filter/sort only | Forbidden interactions list; UI audit gate | Section 7 |
| **8. Audit Survivability** | UI deletable; canon reconstructable | UI derives from sealed files; no unique state | Section 1 (P3-INV-08), Section 8 |
| **9. Closure Criteria** | "Humans can see everything OVC knows, exactly as OVC knows it, without changing anything OVC is" | Full coverage via sealed sources; zero write paths | Entire report |

---

## 10. Phase 3 Build Gate

### 10.1 Go/No-Go Conditions

Phase 3 implementation scaffolding may begin ONLY if ALL of the following are true:

| Condition ID | Condition | Verification Method |
|--------------|-----------|---------------------|
| GATE-01 | **Any write path = STOP** | Static analysis finds zero write functions in Phase 3 codebase |
| GATE-02 | All 9 sealed registries accessible | Pointer validation passes for all 9 active_ref_known=true registries |
| GATE-03 | Health Contracts v0.1 frozen | Document hash matches expected |
| GATE-04 | Enforcement Matrix v0.1/v0.2 frozen | Document present and unmodified |
| GATE-05 | Governance Scorecard v0.1/v0.2 frozen | Document present and unmodified |
| GATE-06 | Run Envelope Standard v0.1 frozen | Document present and unmodified |
| GATE-07 | Registry Seal Contract v0.1 frozen | Document present and unmodified |
| GATE-08 | UI audit checklist passes | All 8 UI checks pass |
| GATE-09 | Read-only mount configured | Filesystem verification confirms read-only access |
| GATE-10 | No write credentials in environment | Environment variable audit confirms zero write-capable secrets |

### 10.2 Build Failure Conditions

The Phase 3 build MUST fail if ANY of the following are detected:

| Failure ID | Condition |
|------------|-----------|
| FAIL-01 | Any file opened in write mode |
| FAIL-02 | Any subprocess/os.system invocation |
| FAIL-03 | Any git write command |
| FAIL-04 | Any HTTP POST/PUT/DELETE/PATCH |
| FAIL-05 | Any sealing function imported |
| FAIL-06 | Any action button in UI |
| FAIL-07 | Any agent/AI integration |
| FAIL-08 | Any write-capable credential in environment |

### 10.3 Continuous Enforcement

The following checks run on every commit to Phase 3 code:

1. Static analysis for forbidden patterns
2. UI audit checklist
3. Environment credential audit
4. Pointer validation against sealed registries

---

## 11. Final Sanity Test

**Question**: If a hostile or careless user had full access to the Phase 3 control panel, could they damage OVC?

**Answer**: **NO**.

| Attack Vector | Prevention |
|---------------|------------|
| Delete artifacts | Read-only mount; user has no write permission |
| Modify registries | Read-only mount; no write functions in code |
| Trigger workflows | No GitHub token; no trigger endpoints |
| Change pointers | No pointer write functions; read-only FS |
| Reseal artifacts | No sealing code; no write paths |
| Inject malicious data | Static viewer; no user input persisted |
| Corrupt display | Deterministic rendering; refresh re-reads canon |

**Conclusion**: Phase 3 architecture is read-only by design, by implementation, and by enforcement.

---

## 12. Cross-References

| Document | Version | Role in Phase 3 |
|----------|---------|-----------------|
| Health Contracts v0.1 | 0.1 | Defines health state determination rules |
| Governance Completeness Scorecard v0.2 | 0.2 | Source of known governance gaps |
| Enforcement Coverage Matrix v0.1 | 0.1 | Source of enforcement levels C0-C5 |
| Registry Seal Contract v0.1 | 0.1 | Defines seal validation rules |
| Active Registry Pointers v0.1 | 0.1 | Pointer file read for active artifact selection |
| Registry Catalog v0.1 | 0.1 | Catalog of all registries |
| Run Envelope Standard v0.1 | 0.1 | Defines run.json structure |
| Registry Delta Log (Phase 2.2.3) | 0.1 | Explanatory diff source |
| Expected Versions v0.1 | 0.1 | Source of expected schema/threshold versions |

---

*End of Phase 3 Architecture Validation Report v0.1*
