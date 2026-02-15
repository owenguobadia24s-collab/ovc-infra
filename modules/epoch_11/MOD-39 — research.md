# MOD-39 — research

## Purpose
This module consistently exists to capture commit activity for `MOD-39` across 1 selected sub-range(s), centered on `DIR:research` basis tokens and co-changed paths `research/studies/`, `research/scores/`.

## Owned Paths
### OWNS
- `research/` (evidence: 8 touches; example commits: `336d0eb`, `9a2f52a`)
### DOES NOT OWN
- UNKNOWN (no evidence)
### AMBIGUOUS
- UNKNOWN (no evidence)

## Produced / Enforced Artifacts
- `research/studies/study_20260120_block_range_intensity_vs_outcomes/verdict.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `336d0eb`, `9a2f52a`)
- `research/studies/study_20260120_block_range_intensity_vs_outcomes/spec.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `336d0eb`, `9a2f52a`)
- `research/studies/study_20260120_block_range_intensity_vs_outcomes/results.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `336d0eb`, `9a2f52a`)
- `research/studies/study_20260120_block_range_intensity_vs_outcomes/method.md` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `336d0eb`, `9a2f52a`)
- `research/studies/study_20260120_block_range_intensity_vs_outcomes/manifest.json` — changed in selected sub-range evidence. (evidence: 1 touches; example commits: `336d0eb`, `9a2f52a`)

## Invariants (Observed)
- INV-01: `MOD-39` is selected at support `8/8` under epoch `11` rules. (evidence: 7 commits; files: `research/studies/study_20260120_block_range_intensity_vs_outcomes/verdict.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/spec.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/results.md`; example commits: `336d0eb`, `9a2f52a`)
- INV-02: Evidence scope is fixed to 1 sub-range(s) from `f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3` to `336d0eb6edc063b295ac0f30c030e591fd0b0d8e`. (evidence: 7 commits; files: `research/studies/study_20260120_block_range_intensity_vs_outcomes/verdict.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/spec.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/results.md`; example commits: `336d0eb`, `9a2f52a`)
- INV-03: Basis token(s) `research` are explicitly encoded in selected candidate label `DIR:research`. (evidence: 7 commits; files: `research/studies/study_20260120_block_range_intensity_vs_outcomes/verdict.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/spec.md`, `research/studies/study_20260120_block_range_intensity_vs_outcomes/results.md`; example commits: `336d0eb`, `9a2f52a`)

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
- Support tie resolved by `document_order` among `MOD-39`, `MOD-40`.
- Candidate block lists repeated subject phrases while exact-match command output has no repeated subjects. (evidence: candidate section vs mandatory command 4)

## Evidence Appendix
- Target selection excerpt
```text
25: | 11 | 8 | research | 100.00% | research | 100.00% | OK |
1820: #### MOD-39 — DIR:research
1825: - f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e
1857: - INV-01: Candidate matches 8/8 commits. (support: 8/8)
```
- Anchor commits
```text
f2f8bd0 f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3 2026-01-20T04:58:31Z Add research artifacts and documentation for exploratory studies
336d0eb 336d0eb6edc063b295ac0f30c030e591fd0b0d8e 2026-01-20T05:31:50Z Add study 20260120: Block Range Intensity by Session
```
- Inventory summaries (>=2 threshold)
  - Directories
- `research/studies/` (36)
  - Files
- NONE
  - Repeated commit subjects (exact)
- NONE
  - Repeated ledger tags
- `research` (7)
- Mandatory command outputs for EACH sub-range
  - Sub-range 1: `f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e` (execution range: `f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e`)
```text
git log --oneline f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e
336d0eb Add study 20260120: Block Range Intensity by Session
9a2f52a Add initial study files for block range intensity by volatility regime analysis
4607f31 Add initial files for block range intensity score temporal stability study
5553e73 Add study files for block range intensity score analysis
db312bd Add initial files for block range intensity score sanity study
007f21e Add block_range_intensity score implementation as a research artifact
913bd4d Add initial study files for basic feature-outcome analysis of GBPUSD

git log --name-only --pretty=format: f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e | sort | uniq -c | sort -nr
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/verdict.md
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/spec.md
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/results.md
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/method.md
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/manifest.json
   1 research/studies/study_20260120_block_range_intensity_vs_outcomes/inputs.md
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/verdict.md
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/spec.md
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/results.md
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/method.md
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/manifest.json
   1 research/studies/study_20260120_block_range_intensity_temporal_stability/inputs.md
   1 research/studies/study_20260120_block_range_intensity_sanity/verdict.md
   1 research/studies/study_20260120_block_range_intensity_sanity/spec.md
   1 research/studies/study_20260120_block_range_intensity_sanity/results.md
   1 research/studies/study_20260120_block_range_intensity_sanity/method.md
   1 research/studies/study_20260120_block_range_intensity_sanity/manifest.json
   1 research/studies/study_20260120_block_range_intensity_sanity/inputs.md
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/verdict.md
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/spec.md
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/results.md
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/method.md
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/manifest.json
   1 research/studies/study_20260120_block_range_intensity_by_vol_regime/inputs.md
   1 research/studies/study_20260120_block_range_intensity_by_session/verdict.md
   1 research/studies/study_20260120_block_range_intensity_by_session/spec.md
   1 research/studies/study_20260120_block_range_intensity_by_session/results.md
   1 research/studies/study_20260120_block_range_intensity_by_session/method.md
   1 research/studies/study_20260120_block_range_intensity_by_session/manifest.json
   1 research/studies/study_20260120_block_range_intensity_by_session/inputs.md
   1 research/studies/study_20260120_basic_feature_outcome_baseline/verdict.md
   1 research/studies/study_20260120_basic_feature_outcome_baseline/spec.md
   1 research/studies/study_20260120_basic_feature_outcome_baseline/results.md
   1 research/studies/study_20260120_basic_feature_outcome_baseline/method.md
   1 research/studies/study_20260120_basic_feature_outcome_baseline/manifest.json
   1 research/studies/study_20260120_basic_feature_outcome_baseline/inputs.md
   1 research/scores/score_block_range_intensity_v1_0.sql

git log --name-only --pretty=format: f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e | awk -F/ 'NF>1{print $1"/"$2"/"} NF==1{print "./"}' | sort | uniq -c | sort -nr
  36 research/studies/
   1 research/scores/

git log --pretty=format:%s f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e | sort | uniq -c | sort -nr
   1 Add study files for block range intensity score analysis
   1 Add study 20260120: Block Range Intensity by Session
   1 Add initial study files for block range intensity by volatility regime analysis
   1 Add initial study files for basic feature-outcome analysis of GBPUSD
   1 Add initial files for block range intensity score temporal stability study
   1 Add initial files for block range intensity score sanity study
   1 Add block_range_intensity score implementation as a research artifact
```
- Ledger evidence
```text
   7 research
```
