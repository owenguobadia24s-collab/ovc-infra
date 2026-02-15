# MOD-76 — scripts

## Purpose
This module consistently exists to capture commit activity for `MOD-76` across 1 selected sub-range(s), centered on `DIR:scripts` basis tokens and co-changed paths `reports/path1/`, `scripts/governance/`, `sql/path1/`.

## Owned Paths
### OWNS
- `scripts/` (evidence: 6 touches; example commits: `52d4a17`, `6919b4e`)
### DOES NOT OWN
- `tests/` (evidence: 4 touches; example commits: `52d4a17`, `6919b4e`)
- `docs/` (evidence: 3 touches; example commits: `52d4a17`, `6919b4e`)
- `./` (evidence: 2 touches; example commits: `52d4a17`, `6919b4e`)
- `reports/` (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)
- `sql/` (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)
### AMBIGUOUS
- Boundary with co-changed paths `tests`, `docs`, `./`. (evidence: dominant directory table in selected candidate block)

## Produced / Enforced Artifacts
- `scripts/governance/build_change_classification_overlay_v0_1.py` — changed in selected sub-range evidence. (evidence: 3 touches; example commits: `52d4a17`, `6919b4e`)
- `tests/test_change_overlay_builder.py` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)
- `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)
- `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_lid_v1_0.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)
- `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_dis_v1_1.sql` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `52d4a17`, `6919b4e`)

## Invariants (Observed)
- INV-01: `MOD-76` is selected at support `6/9` under epoch `19` rules. (evidence: 6 commits; files: `scripts/governance/build_change_classification_overlay_v0_1.py`, `tests/test_change_overlay_builder.py`, `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql`; example commits: `52d4a17`, `6919b4e`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `8950c6cb233d58406ddaf20247d0367948bab316` to `52d4a177ba43263c8817db27b6634b073b4e5015`. (evidence: 6 commits; files: `scripts/governance/build_change_classification_overlay_v0_1.py`, `tests/test_change_overlay_builder.py`, `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql`; example commits: `52d4a17`, `6919b4e`)
- INV-03: Basis token(s) `scripts` are explicitly encoded in selected candidate label `DIR:scripts`. (evidence: 6 commits; files: `scripts/governance/build_change_classification_overlay_v0_1.py`, `tests/test_change_overlay_builder.py`, `sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql`; example commits: `52d4a17`, `6919b4e`)

## Interfaces
### Upstream
- `docs/baselines/MODULE_CANDIDATES_v0.1.md` — selected candidate and commit ranges.
- `git` commit history for selected sub-range(s) — mandatory evidence input.
- `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl` — tag evidence source.
### Downstream
- UNKNOWN (no evidence)

## Non-Goals
- UNKNOWN (no evidence)

## Ambiguities / Pressure Points
- Support tie resolved by `document_order` among `MOD-76`, `MOD-77`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
33: | 19 | 9 | scripts | 66.67% | governance_tooling | 66.67% | OK |
3683: #### MOD-76 — DIR:scripts
3688: - 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015
3726: - INV-01: Candidate matches 6/9 commits. (support: 6/9)
```
- Anchor commits
```text
8950c6c 8950c6cb233d58406ddaf20247d0367948bab316 2026-02-08T14:41:10Z governance: harden --range parsing (reject triple-dot) + tests
52d4a17 52d4a177ba43263c8817db27b6634b073b4e5015 2026-02-08T16:51:35Z Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```
- Inventory summaries (>=2 threshold)
  - Directories
- `reports/path1/` (9)
- `scripts/governance/` (4)
- `sql/path1/` (3)
- `docs/catalogs/` (3)
  - Files
- `scripts/governance/build_change_classification_overlay_v0_1.py` (3)
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `governance_tooling` (5)
- `tests` (3)
- `catalogs` (3)
- `evidence_runs` (2)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015` (execution range: `8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015`)
```text
git log --oneline 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015
52d4a17 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
6919b4e governance: tighten overlay builder path resolution + ignore local test artifacts
d50080c merge: overlay v0.1 deterministic hardening
35eb846 governance: make overlay builder cwd-independent (repo-root path resolution)
3ee57f5 governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
7d92461 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b

git log --name-only --pretty=format: 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | sort | uniq -c | sort -nr
   3 scripts/governance/build_change_classification_overlay_v0_1.py
   1 tests/test_change_overlay_builder.py
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_res_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_lid_v1_0.sql
   1 sql/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/study_dis_v1_1.sql
   1 scripts/governance/classify_change.py
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_res_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_lid_v1_0.txt
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/outputs/study_dis_v1_1.txt
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/meta.json
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/RUN.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/RES_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/LID_v1_0_evidence.md
   1 reports/path1/evidence/runs/p1_20260208_GBPUSD_20260207_len5d_3d531e1b/DIS_v1_1_evidence.md
   1 reports/path1/evidence/INDEX.md
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json
   1 docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl
   1 .gitignore

git log --name-only --pretty=format: 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
   9 reports/path1/
   4 scripts/governance/
   3 sql/path1/
   3 docs/catalogs/
   1 tests/test_change_overlay_builder.py/
   1 ./

git log --pretty=format:%s 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015 | sort | uniq -c | sort -nr
   1 path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
   1 merge: overlay v0.1 deterministic hardening
   1 governance: tighten overlay builder path resolution + ignore local test artifacts
   1 governance: make overlay builder cwd-independent (repo-root path resolution)
   1 governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
   1 Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
```
- Ledger evidence
```text
   5 governance_tooling
   3 tests
   3 catalogs
   2 evidence_runs
```
