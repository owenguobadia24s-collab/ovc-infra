# REPO_TOPOLOGY v0.1

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Generated | 2026-02-16 UTC |
| Branch | `maintenance/sentinel` |
| HEAD | `56145dab6e0f6f148f515c83fd835d85420e6e0b` |
| Total tracked files | 1,284 (via `git ls-files \| wc -l`) |
| Top-level folders (tracked) | 28 directories + 14 root-level files |

---

## 1. Top-Level Folder Inventory

Alphabetical. All counts are **tracked files only** (`git ls-files`).

**Signal level definitions:**
- **High** — contains workflows, tests, or governance scripts
- **Medium** — contains docs or non-trivial scripts
- **Low** — otherwise

| Folder | Tracked Files | Subfolders (depth-2) | Signal | Last Commit | Purpose (best-effort) |
|--------|--------------|----------------------|--------|-------------|----------------------|
| `_archive/` | 23 | 7 | Low | 2026-02-04 | Deprecated code from Phase 1 pruning |
| `_quarantine/` | 5 | 4 | Low | 2026-02-05 | Isolated deprecated scripts pending review |
| `artifacts/` | 8 | 4 | Medium | 2026-02-07 | Generated pipeline outputs (classifier, validation, path1 replay) |
| `CLAIMS/` | 2 | 2 | Medium | 2026-01-22 | Anchor index + claim binding declarations |
| `.codex/` | 43 | 4 | Medium | 2026-02-10 | Claude Code agent run artifacts, prompts, checks |
| `configs/` | 3 | 1 | Medium | 2026-01-21 | Threshold pack JSON configs |
| `contracts/` | 8 | 8 | Medium | 2026-01-19 | JSON schema contracts (export, derived, run artifact, eval) |
| `docs/` | 192 | 27 | High | 2026-02-14 | Governance, doctrine, specs, catalogs, runbooks, maps |
| `.github/` | 17 | 4 | High | 2026-02-14 | Workflows (14), PR template, copilot instructions |
| `infra/` | 17 | 1 | Medium | 2026-02-04 | Cloudflare Worker (`ovc-webhook`) |
| `modules/` | 21 | 1 | Low | 2026-02-15 | Epoch-range forensic freeze outputs (Phase A batch) |
| `pine/` | 3 | 3 | Low | 2026-01-17 | TradingView Pine Scripts |
| `releases/` | 1 | 1 | Low | 2026-01-20 | Single release note (`ovc-v0.1-spine.md`) |
| `reports/` | 482 | 4 | High | 2026-02-14 | Path1 evidence packs, run reports, validation, audits |
| `research/` | 55 | 6 | Medium | 2026-01-20 | Block range intensity studies, notebooks, scores |
| `schema/` | 2 | 2 | Medium | 2026-01-23 | Migration ledger + required objects list |
| `scripts/` | 29 | 9 | High | 2026-02-14 | sentinel, governance, path1, ci, deploy, export, validate |
| `sql/` | 191 | 21 | High | 2026-02-14 | Schema definitions, QA packs, path1 evidence SQL, views |
| `src/` | 28 | 14 | High | 2026-02-05 | Core pipeline: ingest, derived (C1/C2/C3), validate, ops |
| `tests/` | 23 | 20 | High | 2026-02-14 | Cross-cutting pytest suite |
| `Tetsu/` | 49 | 2 | Low | 2026-02-02 | Obsidian vault (OVC_REPO_MAZE navigation docs) |
| `tools/` | 52 | 8 | High | 2026-02-14 | audit_interpreter, run_registry, phase3_control_panel |
| `trajectory_families/` | 9 | 9 | Medium | 2026-01-22 | Trajectory fingerprinting and clustering |
| `.vscode/` | 1 | 1 | Low | — | Editor settings |
| `Work Timeline/` | 1 | 1 | Low | 2026-02-02 | Personal notes (single file) |

**Note:** `data/` exists on disk but has zero tracked files in `git ls-files` on this branch. Not listed above.

### Root-Level Files (14 tracked, non-directory)

| File | Purpose |
|------|---------|
| `.gitattributes` | Git attribute rules |
| `.gitignore` | Git ignore rules |
| `ARCHIVE_NON_CANONICAL_v0.1.md` | Archive non-canonical declaration |
| `CHANGELOG_evidence_pack_provenance.md` | Evidence pack provenance changelog |
| `CHANGELOG_overlays_v0_3.md` | Overlays v0.3 changelog |
| `CHANGELOG_overlays_v0_3_hardening.md` | Overlays v0.3 hardening changelog |
| `out.err` | Output error log (artifact) |
| `out.json` | Output JSON (artifact) |
| `OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md` | Governance: allowed operations catalog |
| `OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md` | Governance: enforcement coverage matrix |
| `OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md` | Governance: completeness scorecard |
| `package-lock.json` | Node lock file (minimal) |
| `PATH1_EXECUTION_MODEL.md` | Path 1 execution model |
| `PHASE_1_5_CLOSURE_DECLARATION.md` | Phase 1.5 closure declaration |
| `PRUNE_PLAN_v0.1.md` | Canonical pruning plan |
| `pytest.ini` | Pytest configuration |
| `README.md` | Main project readme |
| `requirements.txt` | Python dependencies |
| `VERSION_OPTION_C` | Version tag file |

---

## 2. Anchor Files (Tracked)

### README.md files

| Path |
|------|
| `README.md` |
| `_archive/README.md` |
| `_quarantine/README.md` |
| `docs/contracts/README.md` |
| `docs/history/path1/README.md` |
| `reports/README.md` |
| `reports/path1/evidence/README.md` |
| `research/README.md` |
| `research/notebooks/README.md` |
| `research/scores/README.md` |
| `research/tooling/README.md` |
| `scripts/path1_replay/README.md` |
| `scripts/sentinel/README.md` |
| `tests/sample_exports/README.md` |
| `tools/audit_interpreter/README.md` |
| `tools/phase3_control_panel/README.md` |

### `__init__.py` files

| Path |
|------|
| `src/config/__init__.py` |
| `src/derived/__init__.py` |
| `src/history_sources/__init__.py` |
| `src/ovc_ops/__init__.py` |
| `src/utils/__init__.py` |
| `src/validate/__init__.py` |
| `tools/__init__.py` |
| `tools/audit_interpreter/src/audit_interpreter/__init__.py` |
| `tools/audit_interpreter/src/audit_interpreter/pipeline/__init__.py` |
| `trajectory_families/__init__.py` |

### Package manifests

| Path | Type |
|------|------|
| `requirements.txt` | Python deps (root) |
| `pytest.ini` | Pytest config (root) |
| `tools/audit_interpreter/pyproject.toml` | Python package (audit-interpreter) |
| `infra/ovc-webhook/package.json` | Node/Cloudflare Worker |
| `tools/phase3_control_panel/package.json` | Node/Vite React UI |

---

## 3. Workflow Inventory

14 workflow files tracked in `.github/workflows/`.

| Workflow File | Purpose (from filename/commit evidence) |
|---------------|----------------------------------------|
| `append_sentinel.yml` | Sentinel state verify on push to `maintenance/sentinel` |
| `backfill.yml` | OANDA 2H backfill pipeline (scheduled) |
| `backfill_m15.yml` | OANDA M15 backfill pipeline (dispatch) |
| `backfill_then_validate.yml` | Backfill + derived compute + validation (dispatch) |
| `change_classifier.yml` | Governance change classification on PR |
| `ci_pytest.yml` | Python test suite (pytest) on PR |
| `ci_schema_check.yml` | Schema object verification on PR |
| `ci_workflow_sanity.yml` | Workflow YAML sanity checks on PR |
| `main.yml` | Borderland candidate — name too generic to classify without reading |
| `notion_sync.yml` | Notion database sync (scheduled) |
| `ovc_option_c_schedule.yml` | Option C outcomes runner (scheduled) |
| `path1_evidence.yml` | Path1 single evidence run (dispatch) |
| `path1_evidence_queue.yml` | Path1 queued evidence runs (dispatch) |
| `path1_replay_verify.yml` | Path1 replay verification (dispatch) |

---

## 4. Artifact / Generated Zones

Tracked paths that appear to be generated outputs (not hand-authored).

| Zone | Pattern | File Count | Evidence |
|------|---------|-----------|----------|
| `docs/catalogs/*.seal.json` | Sealed governance ledgers | 4 | SHA256 integrity pairs present |
| `docs/catalogs/*.seal.sha256` | Seal integrity hashes | 4 | Paired with `.seal.json` |
| `docs/catalogs/*.jsonl` | Append-only ledger lines | 4 | DEV_CHANGE_LEDGER + OVERLAY v0.1/v0.2 |
| `.codex/_scratch/*.jsonl` | Scratch/backfill ledger data | 3 | Simulation + backfill artifacts |
| `reports/path1/evidence/runs/*/MANIFEST.sha256` | Evidence pack manifests | 2 | Run integrity records |
| `reports/path1/evidence/runs/*/pack_build.jsonl` | Pack build logs | 1 | Build trace |
| `modules/epoch_*/` | Epoch freeze outputs | 19 | Single batch commit `56145da` |
| `modules/_REPORTS/` | Batch freeze reports | 2 | EPOCH_GAPS_AND_TIES.md, EPOCH_OK_INDEX.md |

---

## 5. Commit Pulse

### Last 30 Commits (repo-wide)

```
56145da 2026-02-15 Option 1 Batch Run: Forensic Module Freezes for All OK Epochs (Phase A)
87d79d1 2026-02-14 chore(sentinel): settle state to HEAD
dd1b72a 2026-02-14 chore(sentinel): settle state to HEAD
a5df74b 2026-02-14 catalog: add epoch ranges and module candidates baseline v0.1
d33793d 2026-02-14 feat(governance): add deterministic module candidate generator v0.1
6fb425d 2026-02-14 chore(sentinel): settle state to HEAD
c5b4c64 2026-02-14 chore(sentinel): ingest maintenance hook trip commit
0c755d5 2026-02-14 test: maintenance hook trip commit
9ad8d6d 2026-02-14 chore(sentinel): settle state to HEAD
9fb44b1 2026-02-14 chore(sentinel): scope enforcement to maintenance branch
06b23a7 2026-02-14 chore(sentinel): settle state to HEAD
bafb63a 2026-02-14 chore(sentinel): ingest governance hardening commit
a37d992 2026-02-14 chore(sentinel): clarify state semantics + enforce LF for artifacts
01c6cf9 2026-02-14 path1 evidence: p1_20260214_GBPUSD_20260213_len5d_e5c7de9d
e0717d8 2026-02-13 chore(sentinel): settle state to HEAD
19fbda7 2026-02-13 chore(sentinel): ingest sentinel fix commit
6b69b69 2026-02-13 fix(sentinel): avoid state-only verify loop
27199d8 2026-02-13 chore(sentinel): settle state to HEAD
82f57ea 2026-02-13 chore(sentinel): ingest sentinel ingest commit
71cb9d4 2026-02-13 chore(sentinel): ingest sentinel install commit
93a79ec 2026-02-13 feat(sentinel): append-only commit ingestion + deterministic overlay (v0.1)
ad8588c 2026-02-13 path1 evidence: p1_20260213_GBPUSD_20260212_len5d_55cc6e5e
7ca08ab 2026-02-12 path1 evidence: p1_20260212_GBPUSD_20260211_len5d_35489ad0
bb54a29 2026-02-11 path1 evidence: p1_20260211_GBPUSD_20260210_len5d_2c08b0c8
c8a27bf 2026-02-10 CONT: DEV_CHANGE_LEDGER_v0.2 seal and corresponding SHA256 file
c3cf19d 2026-02-10 cont. Enhance timeline generation and reproducibility checks
50a130f 2026-02-10 CONT: Implement v0.2 additive classifier rules and build overlay files
e8a4c9c 2026-02-10 CONT: Add refined classifier coverage analysis pipeline v2
542a873 2026-02-10 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
f901cd3 2026-02-10 Git Timeline: macro merge trace and micro epoch labels JSON files
```

### Per-Folder Commit History (10 most recent per folder)

#### `_archive/`
```
12ef20f 2026-02-04 .continued
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
```

#### `_quarantine/`
```
34e45ab 2026-02-05 Refactor CI workflows to streamline script path validation and enhance environment variable management
12ef20f 2026-02-04 .continued
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
```

#### `artifacts/`
```
ff1564d 2026-02-07 Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation
0cf7aac 2026-01-23 Add new workflows for CI sanity checks and Path 1 evidence generation
27354e7 2026-01-21 Repo-restructuring
ab9daed 2026-01-18 Option B.2 Implemented
```

#### `CLAIMS/`
```
04c3405 2026-01-22 gov: index claim anchors v0.1
359079c 2026-01-22 Add evidence and outputs for state plane run p1_20260122_004
```

#### `.codex/`
```
c8a27bf 2026-02-10 CONT: DEV_CHANGE_LEDGER_v0.2 seal and corresponding SHA256 file
c3cf19d 2026-02-10 cont. Enhance timeline generation and reproducibility checks
50a130f 2026-02-10 CONT: Implement v0.2 additive classifier rules and build overlay files
e8a4c9c 2026-02-10 CONT: Add refined classifier coverage analysis pipeline v2
f901cd3 2026-02-10 Git Timeline: macro merge trace and micro epoch labels JSON files
456567e 2026-02-05 feat(qa): add run envelope v0.1 + validation pack + registry tooling
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
3dc06d8 2026-02-02 codex: non-spec graph NodeID rename planner + applied safe renames
f758bd1 2026-02-02 Update timestamp generation in coverage_audit.py and refactor rg_index.ps1
b19cf71 2026-02-02 Refactor rg_index.ps1 queries and update workspace.json
```

#### `configs/`
```
b092afc 2026-01-21 Quadrant state plane evidence runner and related SQL views
e43ee24 2026-01-18 (c3_regime_trend): Implement C3 regime trend classifier (v0.1)
961738b 2026-01-18 OVC Option C.3 Stub and unit tests for Threshold Registry
```

#### `contracts/`
```
ee46496 2026-01-19 RUN_ARTIFACT_IMPLEMENTATION
607a8c5 2026-01-17 Evaluation + Feedback Layer (v0.1)
bacc7ff 2026-01-17 Define the Derived Metric Classes and the First Canonical Feature Set
72ce4b0 2026-01-17 chore: lock v0.1 ingest boundary + harden verifier (MIN default, FULL opt-in)
15353b9 2026-01-16 Gate1: lock MIN contract + specs + SQL v0.1
d5d84d3 2026-01-14 Update MIN export contract field types (#3)
fb35f49 2026-01-14 Merge pull request #2 from owenguobadia24s-collab/codex/fix-export_contract_v0.1_full.json
1b17fb4 2026-01-14 Allow empty tis and hints in full export contract
42bf136 2026-01-14 Update tradeable and ready fields to use bool_01 type for consistency in export format
3df870d 2026-01-14 Update rail_loc field type to string_or_empty for improved flexibility
```

#### `docs/`
```
dd1b72a 2026-02-14 chore(sentinel): settle state to HEAD
a5df74b 2026-02-14 catalog: add epoch ranges and module candidates baseline v0.1
c5b4c64 2026-02-14 chore(sentinel): ingest maintenance hook trip commit
bafb63a 2026-02-14 chore(sentinel): ingest governance hardening commit
19fbda7 2026-02-13 chore(sentinel): ingest sentinel fix commit
6b69b69 2026-02-13 fix(sentinel): avoid state-only verify loop
71cb9d4 2026-02-13 chore(sentinel): ingest sentinel install commit
93a79ec 2026-02-13 feat(sentinel): append-only commit ingestion + deterministic overlay (v0.1)
c8a27bf 2026-02-10 CONT: DEV_CHANGE_LEDGER_v0.2 seal and corresponding SHA256 file
c3cf19d 2026-02-10 cont. Enhance timeline generation and reproducibility checks
```

#### `.github/`
```
9fb44b1 2026-02-14 chore(sentinel): scope enforcement to maintenance branch
93a79ec 2026-02-13 feat(sentinel): append-only commit ingestion + deterministic overlay (v0.1)
2a68adf 2026-02-07 docs(pr): add change classification section to PR template
ff1564d 2026-02-07 Change Taxonomy & Governance Classification (Post-Phase 4)
8f5c337 2026-02-05 Update AI Agent Instructions with project overview, governance rules
34e45ab 2026-02-05 Refactor CI workflows to streamline script path validation
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
51f48c2 2026-01-23 feat: add comprehensive governance documentation and preflight instructions
064339b 2026-01-23 Add comprehensive documentation and schema verification for OVC pipeline
2f375f2 2026-01-23 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```

#### `infra/`
```
12ef20f 2026-02-04 .continued
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
851fbad 2026-01-22 feat: add initial implementation of trajectory families module
bf51650 2026-01-22 Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs
e32bbad 2026-01-19 Implement parseExport and msToTimestamptzStart2H functions
23fcb19 2026-01-19 Pipeline Reality Map
0dde777 2026-01-17 validation harness, spotchek and guardrail
a47e289 2026-01-17 Disable ret semantic check for v0.1 ingest stability
a71332b 2026-01-17 Infra: enforce MIN contract v0.1.1
f7bbdde 2026-01-17 WIP: align infra validation to v0.1.1 MIN
```

#### `modules/`
```
56145da 2026-02-15 Option 1 Batch Run: Forensic Module Freezes for All OK Epochs (Phase A)
```

#### `pine/`
```
e3b80fc 2026-01-17 Option A -> D Audit
f205e42 2026-01-17 Pine: align MIN export to contract v0.1_min_r1 + readiness panel
6e3ee4a 2026-01-17 Pine script for Tradining View panels
a4943eb 2026-01-17 feat: Implement export string generation for MIN and FULL profiles in Pine script
42bf136 2026-01-14 Update tradeable and ready fields to use bool_01 type for consistency in export format
e069d4d 2026-01-14 Add initial OVC_v0_1.pine script with export functions
```

#### `releases/`
```
88eff12 2026-01-20 OVC Doctrine and Immutability Notice
```

#### `reports/`
```
01c6cf9 2026-02-14 path1 evidence: p1_20260214_GBPUSD_20260213_len5d_e5c7de9d
ad8588c 2026-02-13 path1 evidence: p1_20260213_GBPUSD_20260212_len5d_55cc6e5e
7ca08ab 2026-02-12 path1 evidence: p1_20260212_GBPUSD_20260211_len5d_35489ad0
bb54a29 2026-02-11 path1 evidence: p1_20260211_GBPUSD_20260210_len5d_2c08b0c8
ca34b1a 2026-02-10 path1 evidence: p1_20260210_GBPUSD_20260209_len5d_c56a01f7
cfd91a7 2026-02-09 path1 evidence: p1_20260209_GBPUSD_20260208_len5d_b4cdab60
7d92461 2026-02-08 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
7021c84 2026-02-07 path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
a317006 2026-02-06 path1 evidence: p1_20260206_GBPUSD_20260205_len5d_cc78af78
07022ac 2026-02-05 path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb
```

#### `research/`
```
38fcad2 2026-01-20 Add study documentation for block range intensity by C3 trend bias
336d0eb 2026-01-20 Add study 20260120: Block Range Intensity by Session
9a2f52a 2026-01-20 Add initial study files for block range intensity by volatility regime analysis
4607f31 2026-01-20 Add initial files for block range intensity score temporal stability study
5553e73 2026-01-20 Add study files for block range intensity score analysis
db312bd 2026-01-20 Add initial files for block range intensity score sanity study
007f21e 2026-01-20 Add block_range_intensity score implementation as a research artifact
913bd4d 2026-01-20 Add initial study files for basic feature-outcome analysis of GBPUSD
f2f8bd0 2026-01-20 Add research artifacts and documentation for exploratory studies
```

#### `schema/`
```
064339b 2026-01-23 Add comprehensive documentation and schema verification for OVC pipeline
```

#### `scripts/`
```
87d79d1 2026-02-14 chore(sentinel): settle state to HEAD
dd1b72a 2026-02-14 chore(sentinel): settle state to HEAD
d33793d 2026-02-14 feat(governance): add deterministic module candidate generator v0.1
6fb425d 2026-02-14 chore(sentinel): settle state to HEAD
c5b4c64 2026-02-14 chore(sentinel): ingest maintenance hook trip commit
9ad8d6d 2026-02-14 chore(sentinel): settle state to HEAD
9fb44b1 2026-02-14 chore(sentinel): scope enforcement to maintenance branch
06b23a7 2026-02-14 chore(sentinel): settle state to HEAD
bafb63a 2026-02-14 chore(sentinel): ingest governance hardening commit
a37d992 2026-02-14 chore(sentinel): clarify state semantics + enforce LF for artifacts
```

#### `sql/`
```
01c6cf9 2026-02-14 path1 evidence: p1_20260214_GBPUSD_20260213_len5d_e5c7de9d
ad8588c 2026-02-13 path1 evidence: p1_20260213_GBPUSD_20260212_len5d_55cc6e5e
7ca08ab 2026-02-12 path1 evidence: p1_20260212_GBPUSD_20260211_len5d_35489ad0
bb54a29 2026-02-11 path1 evidence: p1_20260211_GBPUSD_20260210_len5d_2c08b0c8
ca34b1a 2026-02-10 path1 evidence: p1_20260210_GBPUSD_20260209_len5d_c56a01f7
cfd91a7 2026-02-09 path1 evidence: p1_20260209_GBPUSD_20260208_len5d_b4cdab60
7d92461 2026-02-08 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
7021c84 2026-02-07 path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
a317006 2026-02-06 path1 evidence: p1_20260206_GBPUSD_20260205_len5d_cc78af78
07022ac 2026-02-05 path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb
```

#### `src/`
```
456567e 2026-02-05 feat(qa): add run envelope v0.1 + validation pack + registry tooling
12ef20f 2026-02-04 .continued
02fc2ac 2026-02-04 Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
bf51650 2026-01-22 Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs
e25017b 2026-01-21 Add verification outputs and SQL specifications for OVC project
597ca8e 2026-01-19 Refactor validation logic in validate_derived_range_v0_1.py
ee46496 2026-01-19 RUN_ARTIFACT_IMPLEMENTATION
d348c04 2026-01-18 C3 lifecycle documentation and entry checklist
e43ee24 2026-01-18 (c3_regime_trend): Implement C3 regime trend classifier (v0.1)
961738b 2026-01-18 OVC Option C.3 Stub and unit tests for Threshold Registry
```

#### `tests/`
```
d33793d 2026-02-14 feat(governance): add deterministic module candidate generator v0.1
6b69b69 2026-02-13 fix(sentinel): avoid state-only verify loop
93a79ec 2026-02-13 feat(sentinel): append-only commit ingestion + deterministic overlay (v0.1)
3ee57f5 2026-02-08 governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
8950c6c 2026-02-08 governance: harden --range parsing (reject triple-dot) + tests
ff1564d 2026-02-07 Change Taxonomy & Governance Classification (Post-Phase 4)
456567e 2026-02-05 feat(qa): add run envelope v0.1 + validation pack + registry tooling
851fbad 2026-01-22 feat: add initial implementation of trajectory families module
101e3b4 2026-01-22 chore: remove reserved 'nul' file and rebuild index
ee6e3e3 2026-01-22 feat: Introduce Path1 Sealing Protocol and Replay Verification
```

#### `Tetsu/`
```
b3e733e 2026-02-02 freeze(legend): canonicalize NodeID authority and lock governance
3dc06d8 2026-02-02 codex: non-spec graph NodeID rename planner + applied safe renames
b19cf71 2026-02-02 Refactor rg_index.ps1 queries and update workspace.json
731fe26 2026-02-02 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
d844f2e 2026-02-02 Audit Harness_V1
ef2dd2f 2026-02-02 Update workspace and documentation for Neon Schema Topology
f1688f9 2026-02-01 Update workspace configuration and add new contracts
739ed43 2026-01-30 Add Option A1 and A2 contracts for bar and event ingest
cd19465 2026-01-29 Update workspace configuration to switch active file type to canvas
5994d30 2026-01-26 Add comprehensive legend documentation for each graph in the repository
```

#### `tools/`
```
0c755d5 2026-02-14 test: maintenance hook trip commit
ff1564d 2026-02-07 Change Taxonomy & Governance Classification (Post-Phase 4)
9267725 2026-02-05 Phase 4: audit interpretation/ agent
9fa7d15 2026-02-05 Refactor DeltaLogView and FailuresPage components
1af1355 2026-02-05 Implement Phase 3 Control Panel with read-only functionality
71cfd9c 2026-02-05 Add ParseErrorPanel component to adapt ParseError for ErrorPanel display
8f660b2 2026-02-05 Add TypeScript configuration and package files for phase 3 control panel
3b73583 2026-02-05 Phase 3 with timeline display and summary stats
a4f56d5 2026-02-05 test(compat): restore tools.validate_contract + parse_export via archive shims
456567e 2026-02-05 feat(qa): add run envelope v0.1 + validation pack + registry tooling
```

#### `trajectory_families/`
```
24d1b4d 2026-01-22 feat: implement clustering and gallery generation commands in trajectory families module
851fbad 2026-01-22 feat: add initial implementation of trajectory families module
```

#### `Work Timeline/`
```
b3e733e 2026-02-02 freeze(legend): canonicalize NodeID authority and lock governance
```

---

## 6. Dominant Commit Patterns

| Pattern | Frequency | Meaning |
|---------|-----------|---------|
| `chore(sentinel): settle state to HEAD` | Very high (daily, multiple) | Automated sentinel ledger cycle |
| `path1 evidence: p1_YYYYMMDD_...` | Daily | Automated Path1 evidence pack generation |
| `feat(governance):` / `chore(sentinel): ingest` | Recent cluster | Sentinel + governance hardening sprint |
| `CONT:` prefix | Mid-history (2026-02-10) | Governance overlay v0.2 build sprint |

---

## How Computed

All data derived from tracked paths only (`git ls-files`). Exact commands:

```bash
# HEAD
git rev-parse HEAD

# Total tracked files
git ls-files | wc -l

# Top-level folders
git ls-files | sed 's|/.*||' | sort -u

# File counts per top-level folder
git ls-files | sed 's|/.*||' | sort | uniq -c | sort -rn

# Subfolder counts (depth-2)
git ls-files | awk -F/ 'NF>=2{print $1"/"$2}' | sort -u | awk -F/ '{print $1}' | uniq -c | sort -rn

# Anchor files
git ls-files | grep -i 'README\.md$' | grep -v node_modules
git ls-files | grep '__init__\.py$' | grep -v node_modules
git ls-files | grep 'pyproject\.toml$' | grep -v node_modules
git ls-files | grep 'package\.json$' | grep -v node_modules

# Workflows
git ls-files .github/workflows/

# Generated zones
git ls-files | grep '\.seal\.'
git ls-files | grep '\.sha256'
git ls-files | grep '\.jsonl$'

# Last 30 commits
git log --format="%h %as %s" -30

# Per-folder commits (10 each)
git log --format="%h %as %s" -10 -- <folder>
```
