# MOD-76 — scripts

## Purpose
This module consistently exists to build, harden, and run path-resolved generation of `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl` plus seal artifacts from ledger commits by invoking `scripts/governance/classify_change.py` from `scripts/governance/build_change_classification_overlay_v0_1.py`, while validating deterministic output behavior in `tests/test_change_overlay_builder.py` (evidence: commit range `8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015`; files changed counts; commits `3ee57f5`, `35eb846`, `6919b4e`).

## Owned Paths
### OWNS
- `scripts/governance/` (evidence: touched 4 times in selected range; directories changed count shows `scripts/governance/` = 4; example commits: `3ee57f5`, `35eb846`, `6919b4e`)
- `scripts/governance/build_change_classification_overlay_v0_1.py` (evidence: touched 3 times in selected range; files changed count shows this file = 3; example commits: `3ee57f5`, `35eb846`, `6919b4e`)
- `scripts/governance/classify_change.py` (evidence: touched in selected range and invoked by builder `--classifier`; files changed list contains this path; code reference in builder main path resolution and invocation)

### DOES NOT OWN
- `reports/path1/evidence/` (evidence: changed by `7d92461` path1 evidence commit; no selected-range script commit modifies report generation logic)
- `sql/path1/evidence/` (evidence: changed by `7d92461` path1 evidence commit; no selected-range script commit modifies SQL run authoring logic)

### AMBIGUOUS
- `tests/test_change_overlay_builder.py` (evidence: touched once in selected range (`3ee57f5`) and appears in dominant directories for epoch 19 candidate context; ownership is unclear from this range alone)
- `docs/catalogs/` output artifact paths (evidence: artifact files created in `3ee57f5`; subsequent selected-range commits harden generator logic but do not re-edit all artifact files)

## Produced / Enforced Artifacts
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl` — overlay rows per commit including `commit`, `classes`, `unknown`, `ambiguous`, `files`, `base` (evidence: file changed in selected range; builder writes overlay JSONL; commit `3ee57f5`)
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json` — seal payload with artifact hashes/bytes and range metadata (evidence: file changed in selected range; builder `build_seal_payload` and `write_seal_files`; commit `3ee57f5`)
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256` — SHA256 line over UTF-8 bytes of seal JSON (evidence: file changed in selected range; builder `sha_policy` and `write_seal_files`; commit `3ee57f5`)
- `.gitignore` entries (`testdir/`, `testdir2/`, `.pytest-tmp-overlay/`, `tools/dev/codex_tests.ps1`) — local test artifact ignore policy (evidence: changed in selected range; commit `6919b4e`)

## Invariants (Observed)
- INV-01: `scripts/governance/build_change_classification_overlay_v0_1.py` is the only file touched at least twice in the selected range. (evidence: 6 commits; files: `scripts/governance/build_change_classification_overlay_v0_1.py`; example commits: `3ee57f5`, `35eb846`, `6919b4e`)
- INV-02: Overlay builder resolves relative IO paths from repo root before writing outputs and seals. (evidence: 3 commits touching builder in range; files: `scripts/governance/build_change_classification_overlay_v0_1.py`; example commits: `35eb846`, `6919b4e`)
- INV-03: Overlay builder checks that each ledger commit has a parent before per-commit diff/classification. (evidence: builder enforcement function `ensure_parent_exists`; files: `scripts/governance/build_change_classification_overlay_v0_1.py`; example commits: `3ee57f5`)
- INV-04: Classifier `--range` parsing rejects triple-dot syntax and malformed range forms, enforcing two-dot `A..B`. (evidence: parser checks in selected-range file change; files: `scripts/governance/classify_change.py`; example commits: `3ee57f5`, anchor context `8950c6c`)
- INV-05: Seal integrity is enforced as SHA256 over written seal JSON bytes and validated by tests. (evidence: builder `sha_policy` + `write_seal_files`, test `expected_seal_hash`; files: `scripts/governance/build_change_classification_overlay_v0_1.py`, `tests/test_change_overlay_builder.py`; example commits: `3ee57f5`)
- INV-06: Deterministic rerun equality for overlay/seal artifacts is asserted in tests. (evidence: deterministic rerun assertions on bytes; files: `tests/test_change_overlay_builder.py`; example commits: `3ee57f5`)

## Interfaces
### Upstream
- `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl` — commit list input consumed by builder (`read_ledger_commits`)
- `git` commit graph and per-commit diff (`<commit>^..commit`) — consumed via `ensure_parent_exists` and `collect_commit_files`
- `scripts/governance/classify_change.py` — classifier called by builder via `--classifier`

### Downstream
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl` — produced overlay artifact
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json` — produced seal metadata artifact
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256` — produced seal hash artifact
- `UNKNOWN (no evidence)` — explicit downstream consumer module/process in selected range

## Non-Goals
- Does not author Path1 evidence report documents in `reports/path1/evidence/...` (evidence: those files are changed by `7d92461`, not by script-hardening commits)
- Does not author Path1 evidence SQL study files in `sql/path1/evidence/...` (evidence: those files are changed by `7d92461`, not by script-hardening commits)
- Does not define epoch partitioning or module-candidate generation rules in selected-range changes (evidence: no selected-range file change to `scripts/governance/build_module_candidates_v0_1.py`)

## Ambiguities / Pressure Points
- Candidate tie at support `6/9` between `MOD-76` and `MOD-77`; selected by ordering-based tie-break proxy rather than published match-index values. (evidence: `docs/baselines/MODULE_CANDIDATES_v0.1.md` epoch 19 section)
- Selected range includes both script-hardening commits and one Path1 evidence payload commit. (evidence: commit list includes `7d92461` plus script commits; directories changed include `reports/path1/`, `sql/path1/`, `scripts/governance/`)
- Exact-match repeated commit subjects are absent in mandatory command output, while module-candidate artifact lists repeated subject phrases derived by its own phrase extraction. (evidence: command 4 output all counts = 1; epoch 19 candidate block lists repeated phrases)

## Evidence Appendix
### Target Selection Excerpt (`docs/baselines/MODULE_CANDIDATES_v0.1.md`)
```text
  12: | Epoch ID | Commit Count | Top Directory | % | Top Tag | % | Status |
  13: | --- | ---: | --- | ---: | --- | ---: | --- |
  ...
  33: | 19 | 9 | scripts | 66.67% | governance_tooling | 66.67% | OK |
```

```text
3679: ### Epoch 19
3683: #### MOD-76 — DIR:scripts
3688: - 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015
3694: | scripts | 6 | 66.67% |
3705: | governance_tooling | 6 | 66.67% |
3712: Repeated subject phrases:
3713: - "deterministic hardening"
3714: - "overlay builder"
3715: - "path resolution"
3716: - "repo root"
3729: #### MOD-77 — TAG:governance_tooling
3734: - 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015
```

### Anchor Commits
```text
8950c6c 8950c6cb233d58406ddaf20247d0367948bab316 2026-02-08T14:41:10Z governance: harden --range parsing (reject triple-dot) + tests
52d4a17 52d4a177ba43263c8817db27b6634b073b4e5015 2026-02-08T16:51:35Z Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```

### Step 1 — Evidence Inventory (No Interpretation)
Directories touched >= 2 (selected range):
- `reports/path1/` (9)
- `scripts/governance/` (4)
- `docs/catalogs/` (3)
- `sql/path1/` (3)

Files touched >= 2 (selected range):
- `scripts/governance/build_change_classification_overlay_v0_1.py` (3)

Repeated commit subject phrases (exact match from mandatory command 4):
- NONE

Repeated subject phrases listed in selected candidate artifact:
- `"deterministic hardening"`
- `"overlay builder"`
- `"path resolution"`
- `"repo root"`

Repeated ledger tags (selected range):
- `governance_tooling` (5)
- `catalogs` (3)
- `tests` (3)
- `evidence_runs` (2)

### Step 2 — Responsibility Extraction (Evidence-Bound)
Repeated operations (verbs only):
- harden
- build
- resolve
- merge

Repeated constraints enforced by code or workflow:
- enforce two-dot range syntax (`A..B`) and reject triple-dot
- enforce repo-root path resolution for builder IO paths
- enforce parent-commit existence before per-commit diff
- enforce seal hash over written seal JSON bytes
- enforce deterministic rerun byte equality in tests
- enforce local test artifact ignore paths in `.gitignore`

### Mandatory Command Output 1
Command:
```bash
git log --oneline 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015
```
Output:
```text
52d4a17 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
6919b4e governance: tighten overlay builder path resolution + ignore local test artifacts
d50080c merge: overlay v0.1 deterministic hardening
35eb846 governance: make overlay builder cwd-independent (repo-root path resolution)
3ee57f5 governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
7d92461 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
```

### Mandatory Command Output 2
Command:
```bash
git log --name-only --pretty=format: 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | sort | uniq -c | sort -nr
```
Output:
```text
   3 scripts/governance/build_change_classification_overlay_v0_1.py
   1 .gitignore
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_dis_v1_1.sql
   1 scripts/governance/classify_change.py
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/RUN.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_res_v1_0.txt
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/meta.json
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_dis_v1_1.txt
   1 tests/test_change_overlay_builder.py
```

### Mandatory Command Output 3
Command:
```bash
git log --name-only --pretty=format: 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
```
Output:
```text
   9 reports/path1/
   4 scripts/governance/
   3 docs/catalogs/
   3 sql/path1/
   1 ./
   1 tests/test_change_overlay_builder.py/
```

### Mandatory Command Output 4
Command:
```bash
git log --pretty=format:%s 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | sort | uniq -c | sort -nr
```
Output:
```text
   1 governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
   1 governance: make overlay builder cwd-independent (repo-root path resolution)
   1 governance: tighten overlay builder path resolution + ignore local test artifacts
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
   1 merge: overlay v0.1 deterministic hardening
   1 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
```

### Ledger Filter Output (Selected Range)
```text
7d92461d83ba71f8df87d28a130a7279c86d0e62 | path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b | tags=evidence_runs
3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2 | governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys) | tags=catalogs,governance_tooling,tests
35eb846e5c7111384b1570ab3a142d3fee8f3002 | governance: make overlay builder cwd-independent (repo-root path resolution) | tags=governance_tooling
d50080c7197abd03ed944af08d21f64cbccbd65e | merge: overlay v0.1 deterministic hardening | tags=catalogs,governance_tooling,tests
6919b4e26e428bedfa3187e8ecd049c4da2aa14a | governance: tighten overlay builder path resolution + ignore local test artifacts | tags=governance_tooling
52d4a177ba43263c8817db27b6634b073b4e5015 | Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra | tags=catalogs,evidence_runs,governance_tooling,tests
--- TAG COUNTS ---
   5 governance_tooling
   3 catalogs
   3 tests
   2 evidence_runs
```

### Enforcement Evidence (Code/Workflow Excerpts)
```text
scripts/governance/build_change_classification_overlay_v0_1.py:54:def resolve_repo_path(path: Path, repo_root: Path) -> Path:
scripts/governance/build_change_classification_overlay_v0_1.py:103:def ensure_parent_exists(commit_hash: str) -> None:
scripts/governance/build_change_classification_overlay_v0_1.py:203:        "sha_policy": "sha256 in .seal.sha256 is computed over UTF-8 bytes of this seal JSON as written",
scripts/governance/classify_change.py:234:def parse_range_spec(range_spec: str) -> tuple[str, str]:
scripts/governance/classify_change.py:236:        raise ValueError("--range must use two-dot syntax A..B; triple-dot is not allowed")
tests/test_change_overlay_builder.py:80:def test_builder_deterministic_rerun():
tests/test_change_overlay_builder.py:90:    assert overlay_path.read_bytes() == overlay_first
tests/test_change_overlay_builder.py:115:    expected_seal_hash = hashlib.sha256(seal_json_path.read_bytes()).hexdigest()
.gitignore:288:testdir/
.gitignore:289:testdir2/
.gitignore:290:.pytest-tmp-overlay/
.gitignore:293:tools/dev/codex_tests.ps1
```
