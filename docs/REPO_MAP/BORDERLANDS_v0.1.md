# BORDERLANDS v0.1

| Field | Value |
|-------|-------|
| Version | 0.1 |
| Generated | 2026-02-16 UTC |
| Branch | `maintenance/sentinel` |
| HEAD | `56145dab6e0f6f148f515c83fd835d85420e6e0b` |

---

## Preamble

"Borderlands" are tracked paths whose ownership, classification, or retention status is uncertain or contested. This document does NOT recommend deletion or refactoring. It records open questions so governance decisions can be made explicitly.

### Criteria for Borderland Classification

A path becomes a borderland when any of the following apply:

1. **Mixed intent** — same folder contains files serving unrelated concerns
2. **Unclear ownership** — no clear anchor files (README, `__init__.py`, manifest)
3. **Split-location duplication** — same concern split across two paths
4. **Generated + hand-edited coexistence** — automated outputs mixed with authored content
5. **Personal/workspace content** — machine-specific or user-specific files in shared repo
6. **Unclear retention** — no documented policy for growth, archival, or pruning

---

## Top 10 Borderlands by Risk

Risk = impact on repo coherence if left unresolved. Rank 1 = highest.

| Rank | Path | Tracked Files | Last Commit | Risk Reason |
|------|------|--------------|-------------|-------------|
| 1 | Root-level `.md` sprawl | 10 | 2026-02-14 | Dual-truth with `docs/governance/` |
| 2 | `contracts/` vs `docs/contracts/` | 8 + ~10 | 2026-01-19 | Split-location; undocumented split rule |
| 3 | `sql/` | 191 | 2026-02-14 | Mixed: path1 evidence snapshots + schema definitions + QA packs |
| 4 | `reports/` | 482 | 2026-02-14 | Predominantly generated; no clear boundary with artifact zones |
| 5 | `Tetsu/` | 49 | 2026-02-02 | Personal Obsidian vault in shared repo |
| 6 | `_archive/` vs `_quarantine/` | 23 + 5 | 2026-02-05 | Undocumented boundary between the two |
| 7 | `modules/` | 21 | 2026-02-15 | Single commit; unclear retention policy |
| 8 | `.codex/` | 43 | 2026-02-10 | Agent artifact zone; unclear canonical status |
| 9 | `research/` | 55 | 2026-01-20 | Single-day burst; inactive 27 days; unclear if frozen or abandoned |
| 10 | `Work Timeline/`, `pine/`, scratch dirs | 4 total | 2026-02-02 | Isolated/personal content |

---

## Borderland Detail Cards

### B01 — Root-Level Markdown Sprawl

**Paths:**
```
ARCHIVE_NON_CANONICAL_v0.1.md
CHANGELOG_evidence_pack_provenance.md
CHANGELOG_overlays_v0_3.md
CHANGELOG_overlays_v0_3_hardening.md
OVC_ALLOWED_OPERATIONS_CATALOG_v0.1.md
OVC_ENFORCEMENT_COVERAGE_MATRIX_v0.1.md
OVC_GOVERNANCE_COMPLETENESS_SCORECARD_v0.1.md
PATH1_EXECUTION_MODEL.md
PHASE_1_5_CLOSURE_DECLARATION.md
PRUNE_PLAN_v0.1.md
```

**Why ambiguous:** 10 governance and changelog documents live at the repo root. `docs/governance/` and `docs/doctrine/` cover overlapping scope (governance rules, change taxonomy, closure declarations). A reader looking for authoritative governance content has two locations to check.

**Evidence:**
- `git ls-files | grep '\.md$' | grep -v /` returns 10 root-level markdown files (excluding README.md)
- `docs/governance/` contains `GOVERNANCE_RULES_v0.1.md`, `GOVERNANCE_INDEX_v0_1.md`, `PHASE_2_1_CLOSURE_DECLARATION.md`
- Root has `PHASE_1_5_CLOSURE_DECLARATION.md` — same pattern, different location

**Suggested module candidates:** `docs/governance/` (relocate) or declare root as canonical for top-level declarations
**Review action:** Define which root MDs are "top-level declarations" vs "should be in docs/"

---

### B02 — contracts/ vs docs/contracts/ (Split Location)

**Paths:** `contracts/` (8 JSON files), `docs/contracts/` (10+ MD files)

**Why ambiguous:** Two separate contracts locations split by format (JSON vs Markdown) but with no documented policy explaining the split. `contracts/` holds runtime JSON schema contracts. `docs/contracts/` holds human-readable boundary contracts.

**Evidence:**
- `git ls-files contracts/` — 8 JSON files (export, derived, run artifact, eval contracts)
- `git ls-files docs/contracts/` — Markdown boundary contracts (A_TO_D, option-specific, QA, path2)
- No README or policy file in `contracts/` documenting the split
- `docs/contracts/README.md` exists but does not reference `contracts/`

**Suggested module candidates:** Consolidate under one root, or document the format-based split in governance rules
**Review action:** Write explicit split policy in `docs/governance/GOVERNANCE_RULES_v0.1.md`

---

### B03 — sql/ (Mixed Intent)

**Paths:** `sql/` — 191 tracked files, 21 subfolders

**Why ambiguous:** `sql/` contains three distinct types of content sharing the same root:
1. **Schema definitions** — `00_schema.sql`, `01_tables_min.sql`, `02_*.sql` (hand-authored, stable)
2. **QA validation packs** — `qa_*.sql` (hand-authored, test-adjacent)
3. **Path1 evidence SQL** — `sql/path1/` and `sql/derived/` (generated per evidence run, bulk of file count)

The last 10 commits touching `sql/` are ALL `path1 evidence:` commits — the schema/QA files are stable but the folder appears "active" due to evidence SQL output.

**Evidence:**
- `git log --format="%h %as %s" -10 -- sql` — 10/10 are path1 evidence commits
- `git ls-files sql/ | wc -l` — 191 files
- No README in `sql/`

**Suggested module candidates:** Split schema SQL (hand-authored) from path1 evidence SQL (generated)
**Review action:** Determine if `sql/path1/` and `sql/derived/` are generated outputs; if so, label as artifact zone

---

### B04 — reports/ (Predominantly Generated)

**Paths:** `reports/` — 482 tracked files, 4 top-level subfolders

**Why ambiguous:** 482 files make this the largest tracked folder. The vast majority are path1 evidence pack outputs (generated daily by workflow). But it also contains hand-authored files (`README.md`, `run_report_sanity_local.md`) and the `pipeline_audit/` subfolder.

**Evidence:**
- `git log --format="%h %as %s" -10 -- reports` — 10/10 are `path1 evidence:` commits
- `reports/README.md` exists (anchor), but content growth is automated
- `reports/path1/evidence/runs/` contains MANIFEST.sha256 integrity files

**Suggested module candidates:** Classify as an artifact zone (like `docs/catalogs/`) rather than a module
**Review action:** Determine if `reports/` should be declared a generated artifact zone with a README policy

---

### B05 — Tetsu/ (Personal Obsidian Vault)

**Paths:** `Tetsu/` — 49 tracked files

**Why ambiguous:** A personal Obsidian workspace is committed to the shared repository. Contains `.obsidian/` (machine-specific editor state: `workspace.json`, `app.json`, `appearance.json`) mixed with `OVC_REPO_MAZE/` (legitimate documentation: maze navigation markdown files).

**Evidence:**
- `git ls-files Tetsu/ | wc -l` — 49 files
- `git ls-files Tetsu/.obsidian/` — machine-specific config files tracked
- `Tetsu/OVC_REPO_MAZE/` contains 7+ useful navigation docs (`00_REPO_MAZE.md` through `05_QA_GOVERNANCE.md`)
- No README in `Tetsu/`

**Suggested module candidates:** Move `OVC_REPO_MAZE/` to `docs/`; gitignore `Tetsu/.obsidian/`
**Review action:** Decide if `Tetsu/` is an official docs location or personal workspace

---

### B06 — _archive/ vs _quarantine/ (Undocumented Boundary)

**Paths:** `_archive/` (23 files), `_quarantine/` (5 files)

**Why ambiguous:** Both hold deprecated code from the Phase 1 cleanup. Both mirror the canonical folder structure (sub-folders `infra/`, `scripts/`, `sql/`, `src/`). Both have READMEs. But no written policy distinguishes what goes in "archive" vs "quarantine."

**Evidence:**
- `_archive/README.md` and `_quarantine/README.md` both exist
- Both last touched 2026-02-04/05 during Phase 1 pruning
- Naming implies different meanings (archive = retired; quarantine = isolated pending decision) but this is not formally defined

**Suggested module candidates:** Write explicit boundary policy in each README
**Review action:** Define: (1) criteria for each, (2) retention schedule, (3) pruning policy

---

### B07 — modules/ (Single Commit, Unclear Retention)

**Paths:** `modules/` — 21 tracked files

**Why ambiguous:** Entire folder created in a single batch commit (`56145da` on 2026-02-15). Contains `epoch_1` through `epoch_19` (with gap: `epoch_2` absent) plus `_REPORTS/`. Files have em-dash characters in names (unusual for code repos). Classification is unclear: frozen governance artifact? Active tracking folder? One-off analysis output?

**Evidence:**
- `git log --format="%h %as %s" -10 -- modules` — single commit: `56145da Option 1 Batch Run: Forensic Module Freezes for All OK Epochs (Phase A)`
- `epoch_2` is absent — gap unexplained
- No README in `modules/`
- `_REPORTS/EPOCH_GAPS_AND_TIES.md` and `_REPORTS/EPOCH_OK_INDEX.md` exist

**Suggested module candidates:** Declare as frozen governance artifact zone (like `docs/catalogs/`)
**Review action:** Add `modules/README.md` stating purpose, who writes here, how epochs are created

---

### B08 — .codex/ (Agent Artifact Zone)

**Paths:** `.codex/` — 43 tracked files

**Why ambiguous:** Contains Claude Code agent run artifacts (timestamped run directories with MANIFEST.sha256), prompts, checks, and scratch data. Mix of operational tooling (`CHECKS/`, `PROMPTS/`) and generated outputs (`RUNS/`, `_scratch/`).

**Evidence:**
- `git ls-files .codex/ | wc -l` — 43 tracked files
- `.codex/RUNS/` — timestamped run dirs (generated)
- `.codex/CHECKS/` — audit scripts (hand-authored)
- `.codex/PROMPTS/` — multi-pass prompt definitions (hand-authored)
- `.codex/_scratch/` — backfill/simulation JSONL files (generated)
- No README

**Suggested module candidates:** Split into authored tooling (CHECKS, PROMPTS) vs generated outputs (RUNS, _scratch)
**Review action:** Add `.codex/README.md`; consider gitignoring `RUNS/` and `_scratch/`

---

### B09 — research/ (Single-Day Burst, Inactive)

**Paths:** `research/` — 55 tracked files

**Why ambiguous:** All 9 commits touching `research/` occurred on a single day (2026-01-20). No activity since — 27 days dormant. Has README and clear structure (`notebooks/`, `scores/`, `studies/`, `tooling/`), but `notebooks/` contains zero Jupyter notebooks (placeholder?). Has `RESEARCH_GUARDRAILS.md` suggesting governance intent, but no integration with any workflow.

**Evidence:**
- `git log --format="%h %as %s" -10 -- research` — 9 commits, all dated 2026-01-20
- `research/README.md` exists
- `research/RESEARCH_GUARDRAILS.md` exists
- `research/notebooks/README.md` exists but `git ls-files research/notebooks/` shows only the README (no .ipynb files)

**Suggested module candidates:** Could become a module if reactivated; currently frozen/dormant
**Review action:** Determine if research is frozen, abandoned, or pending reactivation

---

### B10 — Isolated / Personal Content

#### `Work Timeline/`
- 1 tracked file (`020226.txt`)
- Space in folder name (unusual for code repos; can cause shell issues)
- Last commit: `b3e733e 2026-02-02` (bundled with Tetsu legend freeze)
- **Review action:** Gitignore or move to `Tetsu/`

#### `pine/`
- 3 tracked files (TradingView Pine Scripts)
- Last commit: 2026-01-17
- External tool code, not part of infrastructure pipeline
- No tests, no workflow integration
- **Review action:** Move to `docs/external_tools/pine/` or declare as reference material

#### Scratch directories
- `out.err`, `out.json` (root) — output files from past command invocations; should be gitignored
- `VERSION_OPTION_C` (root) — 5-byte version tag; unclear if active
- **Review action:** Gitignore `out.*`; clarify `VERSION_OPTION_C` status

---

## Additional Observations (Lower Priority)

| Path | Observation | Evidence |
|------|-------------|---------|
| `CLAIMS/` | 2 files, 2 commits (2026-01-22); unclear integration with any pipeline | No README; not referenced by any workflow |
| `schema/` | 2 files, 1 commit (2026-01-23); migration ledger + required objects | No README; referenced by `ci_schema_check.yml` workflow |
| `releases/` | 1 file (`ovc-v0.1-spine.md`); 1 commit (2026-01-20) | Placeholder? No release process documented |
| `configs/` | 3 files, 3 commits; threshold pack JSONs | Consumed by `src/config/` (M05); could be owned by M05 |
| `data/` | Exists on disk but 0 tracked files on this branch | Not in `git ls-files`; may be gitignored or branch-specific |
| `.github/workflows/main.yml` | Name too generic to classify from filename alone | Borderland candidate for workflow audit |
| `tools/dev_catalog/` | Contains `git2dev_change_ledger.py` | Single file; unclear if active or superseded by `scripts/governance/` |

---

## Resolved Borderlands

Paths that were initially ambiguous but resolved through evidence during this analysis.

| Path | Former Concern | Resolution | Evidence |
|------|---------------|------------|---------|
| `docs/catalogs/` | Docs or generated artifacts? | Generated artifact zone | Contains `.seal.json`, `.seal.sha256`, `.jsonl` — all sealed outputs from M02 |
| `scripts/sentinel/` | Mixed with broader scripts? | Confirmed module (M01) | README + `__init__`-equivalent entry point + 10+ dedicated commits |
| `scripts/governance/` | Mixed with broader scripts? | Confirmed module (M02) | Dedicated `feat(governance):` commits + clear entry points |
| `trajectory_families/` | Orphaned top-level code? | Confirmed module (M13) | `__init__.py` + 2 dedicated commits + clear single intent |
| `tools/audit_interpreter/` | Part of tools/ or standalone? | Confirmed module (M09) | Own `pyproject.toml` — installable package |

---

## How Computed

```bash
# Tracked file counts per path
git ls-files <path> | wc -l

# Commit history per borderland path
git log --format="%h %as %s" -10 -- <path>

# Root-level markdown files (non-directory)
git ls-files | grep '\.md$' | grep -v /

# Anchor detection
git ls-files | grep -i 'README\.md$' | grep -v node_modules

# Split-location detection (contracts)
git ls-files contracts/
git ls-files docs/contracts/

# Generated zone markers
git ls-files | grep '\.seal\.'
git ls-files | grep '\.sha256'
git ls-files | grep '\.jsonl$'
```

All data derived from `git ls-files` (tracked paths only) and `git log` (commit history).
