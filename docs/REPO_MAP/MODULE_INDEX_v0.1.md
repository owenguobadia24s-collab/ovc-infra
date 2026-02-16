# MODULE_INDEX v0.1

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Generated | 2026-02-16 UTC |
| Branch | `maintenance/sentinel` |
| HEAD | `56145dab6e0f6f148f515c83fd835d85420e6e0b` |

---

## Definition of "Module"

A **module** is a path-owned region with a primary intent, confirmed by **both**:

1. **Anchor evidence** — at least one of: README.md, `__init__.py`, pyproject.toml, package.json, or a clear entry-point script
2. **Commit evidence** — dedicated commits touching primarily that path (not just incidental bulk commits)

**Confidence levels:**
- **High** — both anchor and commit evidence present; clear single intent; active (commits within last 30 days)
- **Med** — both present but partially integrated, inactive, or narrow scope
- **Low** — only one type of evidence, or scope unclear

Paths that fail both checks or have mixed signals are directed to [BORDERLANDS_v0.1.md](BORDERLANDS_v0.1.md).

---

## Module Summary Table

| ID | Root Path(s) | Intent | Tracked Files | Confidence | Last Commit |
|----|-------------|--------|--------------|------------|-------------|
| M01 | `scripts/sentinel/` | Append-only commit ledger + overlay | 4 | High | 2026-02-14 |
| M02 | `scripts/governance/` | Change taxonomy + classification + module candidates | 5 | High | 2026-02-14 |
| M03 | `scripts/path1/`, `scripts/path1_replay/`, `scripts/path1_seal/` | Path1 evidence execution, replay, sealing | 10 | High | 2026-02-14 |
| M04 | `src/derived/` | C1/C2/C3 derived metric computation | 4 | High | 2026-02-05 |
| M05 | `src/config/` | Threshold registry | 3 | High | 2026-01-18 |
| M06 | `src/ovc_ops/` | Run artifact management + envelope | 4 | High | 2026-02-05 |
| M07 | `src/validate/` | Derived range validation | 2 | High | 2026-02-05 |
| M08 | `src/history_sources/` | Data source adapters (TradingView CSV) | 3 | Med | 2026-01-22 |
| M09 | `tools/audit_interpreter/` | Phase 4 audit interpreter (installable package) | 15 | Med | 2026-02-07 |
| M10 | `tools/run_registry/` | Run registry + system health rendering | 4 | Med | 2026-02-05 |
| M11 | `tools/phase3_control_panel/` | Phase 3 audit UI (TypeScript/Vite) | 22 | Med | 2026-02-05 |
| M12 | `infra/ovc-webhook/` | Cloudflare Worker (TradingView ingest) | 17 | Med | 2026-02-04 |
| M13 | `trajectory_families/` | Trajectory fingerprinting + clustering | 9 | Med | 2026-01-22 |
| M14 | `tests/` | Cross-cutting pytest suite | 23 | High | 2026-02-14 |
| M15 | `.github/workflows/` | CI/CD orchestration | 14 | High | 2026-02-14 |

**Cross-cutting modules:** M14 (`tests/`) and M15 (`.github/workflows/`) serve multiple modules and do not have exclusive path ownership.

---

## Module Detail Cards

### M01 — scripts/sentinel/ (Commit Ledger)

**Anchor evidence:** `scripts/sentinel/README.md`, entry point `append_sentinel.py`
**Commit evidence:** 10+ dedicated `chore(sentinel):` and `feat(sentinel):` commits

**Purpose:** Append-only commit ingestion into a deterministic sentinel ledger. Runs on every push to `maintenance/sentinel` and via pre-push hook. Produces `sentinel_state.json` and sealed ledger entries in `docs/catalogs/`.

**Key files:**
- `scripts/sentinel/append_sentinel.py` — core ingestion logic
- `scripts/sentinel/install_pre_push_hook.sh` — git hook installer
- `scripts/sentinel/sentinel_state.json` — operational state pointer
- `scripts/sentinel/README.md` — module docs

**Linked workflows:** `append_sentinel.yml`

**Last 10 commits (via `scripts/sentinel/`):**
```
87d79d1 2026-02-14 chore(sentinel): settle state to HEAD
dd1b72a 2026-02-14 chore(sentinel): settle state to HEAD
6fb425d 2026-02-14 chore(sentinel): settle state to HEAD
c5b4c64 2026-02-14 chore(sentinel): ingest maintenance hook trip commit
9ad8d6d 2026-02-14 chore(sentinel): settle state to HEAD
9fb44b1 2026-02-14 chore(sentinel): scope enforcement to maintenance branch
06b23a7 2026-02-14 chore(sentinel): settle state to HEAD
bafb63a 2026-02-14 chore(sentinel): ingest governance hardening commit
a37d992 2026-02-14 chore(sentinel): clarify state semantics + enforce LF for artifacts
e0717d8 2026-02-13 chore(sentinel): settle state to HEAD
```

---

### M02 — scripts/governance/ (Change Classification)

**Anchor evidence:** Entry points `classify_change.py`, `build_module_candidates_v0_1.py`; no README (Borderland signal: undocumented module)
**Commit evidence:** Dedicated `feat(governance):` and `governance:` commits

**Purpose:** Deterministic change taxonomy and overlay system. Classifies commits into A/B/C/D/E/UNKNOWN taxonomy, builds versioned JSONL ledgers and overlays, seals with SHA256, generates module candidate lists.

**Key files:**
- `scripts/governance/classify_change.py` — per-commit classifier
- `scripts/governance/build_change_classification_overlay_v0_1.py` — overlay v0.1 builder
- `scripts/governance/build_change_classification_overlay_v0_2.py` — overlay v0.2 builder
- `scripts/governance/build_module_candidates_v0_1.py` — module candidate generator
- `scripts/governance/install_precommit_change_classifier.sh` — pre-commit hook

**Linked workflows:** `change_classifier.yml`

**Last 10 commits (via `scripts/governance/`):**
```
d33793d 2026-02-14 feat(governance): add deterministic module candidate generator v0.1
c8a27bf 2026-02-10 CONT: DEV_CHANGE_LEDGER_v0.2 seal and corresponding SHA256 file
50a130f 2026-02-10 CONT: Implement v0.2 additive classifier rules and build overlay files
3ee57f5 2026-02-08 governance: deterministic hardening for overlay v0.1
8950c6c 2026-02-08 governance: harden --range parsing (reject triple-dot) + tests
ff1564d 2026-02-07 Change Taxonomy & Governance Classification (Post-Phase 4)
```

---

### M03 — scripts/path1*, scripts/path1_replay/, scripts/path1_seal/ (Evidence Pipeline)

**Anchor evidence:** `scripts/path1_replay/README.md`, entry points in each subfolder
**Commit evidence:** Dedicated path1-related commits across all three subfolders

**Purpose:** Three coordinated subfolders executing Path1 evidence runs. `path1/` runs evidence queue and pack builder; `path1_replay/` handles deterministic replay verification; `path1_seal/` handles run sealing.

**Key files:**
- `scripts/path1/run_evidence_queue.py` — queued executor
- `scripts/path1/run_evidence_range.py` — range executor
- `scripts/path1/build_evidence_pack_v0_2.py` — evidence pack builder
- `scripts/path1/overlays_v0_3.py` — overlay logic
- `scripts/path1_replay/run_replay_verification.py` — replay verifier
- `scripts/path1_replay/README.md`
- `scripts/path1_seal/run_seal_manifests.py` — sealing

**Linked workflows:** `path1_evidence.yml`, `path1_evidence_queue.yml`, `path1_replay_verify.yml`, `main.yml` (likely — Borderland candidate for confirmation)

**Last 10 commits (via `scripts/path1*/`):**
```
01c6cf9 2026-02-14 path1 evidence: p1_20260214_GBPUSD_20260213_len5d_e5c7de9d
456567e 2026-02-05 feat(qa): add run envelope v0.1 + validation pack + registry tooling
ee6e3e3 2026-01-22 feat: Introduce Path1 Sealing Protocol and Replay Verification
0cf7aac 2026-01-23 Add new workflows for CI sanity checks and Path 1 evidence generation
bf51650 2026-01-22 Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs
```

---

### M04 — src/derived/ (Derived Metrics)

**Anchor evidence:** `src/derived/__init__.py`
**Commit evidence:** Dedicated C1/C2/C3 implementation commits

**Purpose:** Three-layer derived feature computation. C1 = base features, C2 = composite features, C3 = regime trend classification.

**Key files:**
- `src/derived/compute_c1_v0_1.py` — C1 feature computation
- `src/derived/compute_c2_v0_1.py` — C2 feature computation
- `src/derived/compute_c3_regime_trend_v0_1.py` — C3 regime trend model
- `src/derived/__init__.py`

**Linked workflows:** `backfill_then_validate.yml` (indirectly, via src/ pipeline)

**Last 10 commits:** See `src/` in REPO_TOPOLOGY commit pulse.

---

### M05 — src/config/ (Threshold Registry)

**Anchor evidence:** `src/config/__init__.py`
**Commit evidence:** Dedicated threshold registry commits (`961738b`, `e43ee24`)

**Purpose:** Manages threshold packs for derived computations. Loads JSON threshold packs from `configs/threshold_packs/`.

**Key files:**
- `src/config/threshold_registry_v0_1.py` — registry core
- `src/config/threshold_registry_cli.py` — CLI interface
- `src/config/__init__.py`

**Linked workflows:** None directly (invoked by derived compute scripts)

---

### M06 — src/ovc_ops/ (Run Artifact Management)

**Anchor evidence:** `src/ovc_ops/__init__.py`
**Commit evidence:** Dedicated `RUN_ARTIFACT_IMPLEMENTATION` commit + `feat(qa): add run envelope v0.1`

**Purpose:** Standardized run artifact capture system. Records execution metadata into JSON files under `reports/runs/`.

**Key files:**
- `src/ovc_ops/run_artifact.py` — `RunWriter` class
- `src/ovc_ops/run_artifact_cli.py` — CLI wrapper
- `src/ovc_ops/run_envelope_v0_1.py` — envelope standard
- `src/ovc_ops/__init__.py`

**Linked workflows:** Used by all evidence and backfill workflows (via scripts)

---

### M07 — src/validate/ (Derived Validation)

**Anchor evidence:** `src/validate/__init__.py`
**Commit evidence:** Dedicated validation refactor commit (`597ca8e`)

**Purpose:** Validates derived feature computation correctness across date ranges.

**Key files:**
- `src/validate/validate_derived_range_v0_1.py` — core validation logic
- `src/validate/__init__.py`

**Linked workflows:** `backfill_then_validate.yml`

---

### M08 — src/history_sources/ (Data Adapters)

**Anchor evidence:** `src/history_sources/__init__.py`
**Commit evidence:** Touched by broader ingest commits; no dedicated history_sources-only commits observed

**Purpose:** Adapters for reading raw source data formats into normalized rows for pipeline ingest.

**Key files:**
- `src/history_sources/tv_csv.py` — TradingView CSV reader
- `src/history_sources/__init__.py`
- `src/history_sources/_LIBRARY_ONLY.md`

**Linked workflows:** `backfill.yml`, `backfill_m15.yml` (via src/ ingest scripts)

**Note:** Confidence is Med because no dedicated commits were observed — changes arrive bundled with broader ingest work.

---

### M09 — tools/audit_interpreter/ (Phase 4 Audit)

**Anchor evidence:** `tools/audit_interpreter/pyproject.toml`, `README.md`, `src/audit_interpreter/__init__.py`
**Commit evidence:** Dedicated Phase 4 audit commits (`9267725`, `ff1564d`)

**Purpose:** Installable Python package that interprets audit run outputs. Has its own `pyproject.toml` (package name: `audit-interpreter`, v0.1.0).

**Key files:**
- `tools/audit_interpreter/pyproject.toml` — package definition
- `tools/audit_interpreter/README.md`
- `tools/audit_interpreter/src/audit_interpreter/cli.py` — CLI entry point
- `tools/audit_interpreter/src/audit_interpreter/interpret.py` — main interpreter
- `tools/audit_interpreter/src/audit_interpreter/pipeline/` — analysis pipeline

**Linked workflows:** Borderland candidate — no direct workflow observed

---

### M10 — tools/run_registry/ (System Health)

**Anchor evidence:** No README or `__init__.py` (anchor deficit — documented)
**Commit evidence:** Touched by `feat(qa): add run envelope v0.1 + validation pack + registry tooling` (`456567e`)

**Purpose:** Builds and renders a run registry from `reports/runs/` and derives system health metrics.

**Key files:**
- `tools/run_registry/build_run_registry_v0_1.py`
- `tools/run_registry/build_op_status_table_v0_1.py`
- `tools/run_registry/build_drift_signals_v0_1.py`
- `tools/run_registry/render_system_health_v0_1.py`

**Linked workflows:** None currently wired

**Note:** No README or `__init__.py`. Classified as Med confidence: clear intent from filenames but missing formal anchor.

---

### M11 — tools/phase3_control_panel/ (Audit UI)

**Anchor evidence:** `tools/phase3_control_panel/package.json`, `README.md`
**Commit evidence:** Cluster of 5+ dedicated Phase 3 commits on 2026-02-05

**Purpose:** TypeScript/Vite read-only UI for viewing Phase 3 audit results.

**Key files:**
- `tools/phase3_control_panel/package.json` — npm package definition
- `tools/phase3_control_panel/README.md`
- `tools/phase3_control_panel/src/main.tsx` — UI entry
- `tools/phase3_control_panel/vite.config.ts`

**Linked workflows:** None (local dev tool)

---

### M12 — infra/ovc-webhook/ (Cloudflare Worker)

**Anchor evidence:** `infra/ovc-webhook/package.json`
**Commit evidence:** Dedicated infra implementation commits (`e32bbad`, `a71332b`, `f7bbdde`)

**Purpose:** Cloudflare Worker HTTP receiver. Accepts TradingView alert POSTs, parses export payload, upserts to Neon DB.

**Key files:**
- `infra/ovc-webhook/src/index.ts` — Worker entry point
- `infra/ovc-webhook/wrangler.jsonc` — Wrangler config
- `infra/ovc-webhook/package.json`

**Linked workflows:** None in repo (deployed via wrangler externally)

**Note:** 17 tracked files total. Deployment status unknown from repo evidence alone.

---

### M13 — trajectory_families/ (Clustering)

**Anchor evidence:** `trajectory_families/__init__.py`
**Commit evidence:** 2 dedicated commits (`851fbad`, `24d1b4d`)

**Purpose:** Trajectory fingerprinting and clustering module. Generates fingerprints from Path1 score sequences, clusters them, produces gallery outputs.

**Key files:**
- `trajectory_families/__init__.py`
- `trajectory_families/clustering.py`
- `trajectory_families/fingerprint.py`
- `trajectory_families/distance.py`
- `trajectory_families/features.py`
- `trajectory_families/gallery.py`
- `trajectory_families/naming.py`
- `trajectory_families/schema.py`
- `trajectory_families/params_v0_1.json`

**Linked workflows:** None currently wired

**Note:** Confidence Med — only 2 commits, last touched 2026-01-22. No workflow integration.

---

### M14 — tests/ (Cross-Cutting QA)

**Anchor evidence:** `tests/sample_exports/README.md`, `tests/fixtures/` directory
**Commit evidence:** Frequent test-related commits spanning multiple modules

**Purpose:** Cross-cutting pytest suite covering derived features, contracts, sentinel, governance, determinism.

**Key files (representative):**
- `tests/test_append_sentinel.py`
- `tests/test_change_classifier.py`
- `tests/test_derived_features.py`
- `tests/test_c3_regime_trend.py`
- `tests/test_contract_equivalence.py`
- `tests/test_overlays_v0_3_determinism.py`
- `tests/test_run_envelope_v0_1.py`
- `tests/fixtures/` — golden inputs
- `tests/sample_exports/` — contract samples

**Linked workflows:** `ci_pytest.yml`

**Note:** Cross-cutting — tests span M01 through M13. No `conftest.py` at project level; pytest config via `pytest.ini`.

---

### M15 — .github/workflows/ (CI/CD)

**Anchor evidence:** 14 tracked YAML workflow files
**Commit evidence:** Dedicated workflow commits across multiple sprints

**Purpose:** CI/CD orchestration layer. 14 workflows covering scheduled pipelines, CI gates, manual dispatch operations, and governance automation.

**Linked to:** M01 (sentinel), M02 (governance), M03 (path1), M04-M07 (src pipeline), M14 (tests)

See REPO_TOPOLOGY_v0.1.md §3 for full workflow inventory.

---

## Unconfirmed Candidates (Directed to BORDERLANDS)

The following paths were evaluated as module candidates but did not meet both anchor + commit evidence thresholds:

| Path | Anchor? | Commit Evidence? | Reason for Deferral |
|------|---------|-----------------|---------------------|
| `docs/` | README exists | High commit activity | Cross-cutting; 27 subfolders with mixed intent — see BORDERLANDS |
| `sql/` | No README, no `__init__.py` | Daily path1 evidence commits | 21 subfolders; commits are overwhelmingly path1 evidence SQL snapshots, not SQL development — mixed signal |
| `reports/` | README exists | Daily path1 evidence commits | Predominantly generated output (482 files); unclear if module or artifact zone |
| `modules/` | No README | Single commit | Single batch commit; unclear retention — see BORDERLANDS |
| `research/` | README exists | 9 commits (all 2026-01-20) | Single-day burst; inactive since — see BORDERLANDS |
| `.codex/` | No README | Mixed commits | Agent artifact zone; unclear if module — see BORDERLANDS |
| `CLAIMS/` | No README | 2 commits | Too few commits; unclear integration |
| `contracts/` | No README, no `__init__.py` | 10 commits | Split with `docs/contracts/` — see BORDERLANDS |

---

## How Computed

Module candidates identified from:
```bash
# Anchor detection (tracked files only)
git ls-files | grep -i 'README\.md$' | grep -v node_modules
git ls-files | grep '__init__\.py$' | grep -v node_modules
git ls-files | grep 'pyproject\.toml$' | grep -v node_modules
git ls-files | grep 'package\.json$' | grep -v node_modules

# Per-candidate commit evidence
git log --format="%h %as %s" -10 -- <candidate_path>

# Tracked file counts
git ls-files <candidate_path> | wc -l
```

Confirmation rule: anchor evidence AND dedicated commit evidence required. Mixed-signal paths deferred to BORDERLANDS_v0.1.md.
