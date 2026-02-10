# OVC Development Timeline (Derived from Ledger + Overlay)

## Coverage

- **ROOT:** `e144cf064769f1a5e332090d02a272f6cadc0e6c`
- **HEAD:** `cfd91a7d80267d717ab519102b1ce7956361503c`
- **Total commits:** 264
- **Working tree state:** clean
- **Micro epochs:** 63
- **Macro epochs:** 20

## Macro Epochs (Primary View)

### Macro Epoch 0 -- /+.github/ | ci_workflows+contracts | backfill contract workflow

- **Date range:** 2026-01-14T01:00:01 -> 2026-01-14T08:31:23
- **Commits:** 16
- **Micro epochs included:** [0]
- **Dominant dirs:** `/` (6), `.github/` (4), `contracts/` (3), `docs/` (1), `sql/` (1)
- **Dominant tags:** `ci_workflows` (4), `contracts` (3), `evidence_runs` (1), `source_code` (1), `pine` (1)
- **Dominant classes:** `UNKNOWN` (10), `E` (6), `C` (6)
- **Representative commits:**
  - `dc6e7f5913a5...` 2026-01-14T01:20:35Z|Add OVC backfill v0.1 (OANDA checkpointed) + repo structure
  - `e144cf064769...` 2026-01-14T01:00:01Z|Initial commit
  - `a78f7c9d92ba...` 2026-01-14T01:02:43Z|Update .gitignore for OVC and data/logs
  - `d6c8b7c90a87...` 2026-01-14T01:30:37Z|Add GitHub Actions daily backfill workflow
  - `456723685af2...` 2026-01-14T01:37:05Z|Add requirements.txt for GitHub Actions

### Macro Epoch 1 -- tests/+tools/ | tests+tools_general | export tools contract

- **Date range:** 2026-01-14T08:31:49 -> 2026-01-14T09:37:00
- **Commits:** 5
- **Micro epochs included:** [1, 2]
- **Dominant dirs:** `tests/` (4), `tools/` (3)
- **Dominant tags:** `tests` (4), `tools_general` (3)
- **Dominant classes:** `C` (5)
- **Representative commits:**
  - `be09dd8b5876...` 2026-01-14T08:36:08Z|Add v0.1 export contracts, validation tools, and tests
  - `aad498312338...` 2026-01-14T08:36:18Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `b694a744daa3...` 2026-01-14T08:31:49Z|Delete tools\validate_contract.py
  - `c5574da31212...` 2026-01-14T09:29:49Z|Add export string for MIN contract in min_001.txt
  - `e8c253791cb6...` 2026-01-14T09:37:00Z|Update export string in full_001.txt

### Macro Epoch 2 -- contracts/+tools/ | contracts+tools_general | export type refactor

- **Date range:** 2026-01-14T10:29:13 -> 2026-01-14T14:15:46
- **Commits:** 11
- **Micro epochs included:** [3]
- **Dominant dirs:** `contracts/` (4), `tools/` (3), `/` (2), `ovc-webhook/` (2), `infra/` (2)
- **Dominant tags:** `contracts` (4), `tools_general` (3), `infra` (2), `tests` (1), `pine` (1)
- **Dominant classes:** `UNKNOWN` (9), `C` (3), `E` (1)
- **Representative commits:**
  - `8b566f3aa4da...` 2026-01-14T14:07:05Z|Add ovc-webhook worker project
  - `4547615fb0df...` 2026-01-14T10:29:13Z|Update export strings in full_001.txt and min_001.txt; add validation script for export strings
  - `09d951775170...` 2026-01-14T10:42:13Z|Refactor export contract schema: remove formatting and update types for clarity and consistency
  - `42bf13666843...` 2026-01-14T12:44:49Z|Update tradeable and ready fields to use bool_01 type for consistency in export format
  - `1859414a24a6...` 2026-01-14T10:57:45Z|Enhance validation logic: normalize input values and improve type checks for contract fields

### Macro Epoch 3 -- infra/ | infra | refactor ovc webhook

- **Date range:** 2026-01-14T15:57:49 -> 2026-01-14T15:57:49
- **Commits:** 1
- **Micro epochs included:** [4]
- **Dominant dirs:** `infra/` (1)
- **Dominant tags:** `infra` (1)
- **Dominant classes:** `UNKNOWN` (1)
- **Representative commits:**
  - `7c3982068064...` 2026-01-14T15:57:49Z|Refactor OVC webhook for improved clarity and structure

### Macro Epoch 4 -- docs/+infra/ | infra+ci_workflows | ovc merge owenguobadia24s

- **Date range:** 2026-01-14T18:01:00 -> 2026-01-16T18:13:06
- **Commits:** 11
- **Micro epochs included:** [5, 6, 7]
- **Dominant dirs:** `docs/` (8), `infra/` (5), `.github/` (3), `src/` (3), `contracts/` (3)
- **Dominant tags:** `infra` (5), `ci_workflows` (3), `source_code` (3), `contracts` (3), `pine` (1)
- **Dominant classes:** `UNKNOWN` (11), `C` (3), `E` (3)
- **Representative commits:**
  - `fb35f4976787...` 2026-01-14T18:10:11Z|Merge pull request #2 from owenguobadia24s-collab/codex/fix-export_contract_v0.1_full.json
  - `aaecb0cab415...` 2026-01-14T18:01:00Z|Worker: upsert MIN into ovc_blocks_v01 (Option B)
  - `df6e2c64fc22...` 2026-01-14T18:02:46Z|Merge pull request #1 from owenguobadia24s-collab/codex/complete-step-8b-hardening-for-ovc
  - `7a2ea214f506...` 2026-01-14T18:36:25Z|Add AI Agent guidelines to project documentation
  - `1b17fb4f810f...` 2026-01-14T18:09:45Z|Allow empty tis and hints in full export contract

### Macro Epoch 5 -- sql/+/ | evidence_runs+contracts | sql table references

- **Date range:** 2026-01-16T21:16:53 -> 2026-01-16T22:36:02
- **Commits:** 4
- **Micro epochs included:** [8]
- **Dominant dirs:** `sql/` (4), `/` (1), `contracts/` (1), `docs/` (1), `specs/` (1)
- **Dominant tags:** `evidence_runs` (4), `contracts` (1), `specs` (1), `validation` (1)
- **Dominant classes:** `UNKNOWN` (4)
- **Representative commits:**
  - `15353b9226cd...` 2026-01-16T21:16:53Z|Gate1: lock MIN contract + specs + SQL v0.1
  - `043271a319cc...` 2026-01-16T22:19:10Z|Fix table name references in SQL scripts for consistency
  - `02abc800df9a...` 2026-01-16T22:32:36Z|Fix table reference in events view SQL script for accuracy
  - `8553d2640951...` 2026-01-16T22:36:02Z|Fix date column references in events views for consistency

### Macro Epoch 6 -- infra/+pine/ | infra+pine | min pine export

- **Date range:** 2026-01-16T22:50:47 -> 2026-01-17T04:46:32
- **Commits:** 11
- **Micro epochs included:** [9, 10]
- **Dominant dirs:** `infra/` (6), `pine/` (5), `tests/` (5), `docs/` (5), `tools/` (3)
- **Dominant tags:** `infra` (6), `pine` (5), `tests` (5), `validation` (4), `tools_general` (3)
- **Dominant classes:** `UNKNOWN` (10), `C` (5)
- **Representative commits:**
  - `9d05d844c4f0...` 2026-01-17T04:37:47Z|Merge branch 'main' into pr/pine-min-export-v0.1_min_r1
  - `f6d9928e6c2a...` 2026-01-17T04:32:21Z|Merge pull request #5 from owenguobadia24s-collab/wip/infra-contract-validation
  - `f7bbdde22c1a...` 2026-01-17T03:41:49Z|WIP: align infra validation to v0.1.1 MIN
  - `f205e42e1e93...` 2026-01-17T03:42:47Z|Pine: align MIN export to contract v0.1_min_r1 + readiness panel
  - `a71332b4f911...` 2026-01-17T03:59:32Z|Infra: enforce MIN contract v0.1.1

### Macro Epoch 7 -- docs/+scripts/ | scripts_general+evidence_runs | option ingest disable

- **Date range:** 2026-01-17T06:37:55 -> 2026-01-17T18:53:10
- **Commits:** 9
- **Micro epochs included:** [11, 12]
- **Dominant dirs:** `docs/` (5), `scripts/` (4), `sql/` (4), `/` (3), `contracts/` (3)
- **Dominant tags:** `scripts_general` (4), `evidence_runs` (4), `contracts` (3), `infra` (2), `tests` (2)
- **Dominant classes:** `UNKNOWN` (7), `C` (6), `E` (2)
- **Representative commits:**
  - `607a8c5c4e82...` 2026-01-17T17:12:47Z|Evaluation + Feedback Layer (v0.1)
  - `13a589b968ee...` 2026-01-17T18:02:40Z|Option D
  - `72ce4b0a7871...` 2026-01-17T15:28:56Z|chore: lock v0.1 ingest boundary + harden verifier (MIN default, FULL opt-in)
  - `bacc7ff998bc...` 2026-01-17T16:36:14Z|Define the Derived Metric Classes and the First Canonical Feature Set
  - `fab9e5ba3cac...` 2026-01-17T06:58:24Z|Docs: normalize workflow + verification scripts

### Macro Epoch 8 -- pine/+sql/ | evidence_runs+pine | option audit

- **Date range:** 2026-01-17T20:40:32 -> 2026-01-17T20:40:32
- **Commits:** 1
- **Micro epochs included:** [13]
- **Dominant dirs:** `pine/` (1), `sql/` (1)
- **Dominant tags:** `evidence_runs` (1), `pine` (1)
- **Dominant classes:** `UNKNOWN` (1)
- **Representative commits:**
  - `e3b80fc3cebd...` 2026-01-17T20:40:32Z|Option A -> D Audit

### Macro Epoch 9 -- docs/+src/ | source_code+validation | validation documentation workflow

- **Date range:** 2026-01-17T21:17:23 -> 2026-01-20T03:05:49
- **Commits:** 37
- **Micro epochs included:** [14, 15, 16, 17, 18, 19]
- **Dominant dirs:** `docs/` (34), `src/` (18), `sql/` (11), `scripts/` (9), `.github/` (7)
- **Dominant tags:** `source_code` (18), `validation` (17), `evidence_runs` (11), `ci_workflows` (9), `scripts_general` (9)
- **Dominant classes:** `UNKNOWN` (36), `C` (23), `E` (6)
- **Representative commits:**
  - `ee46496d2627...` 2026-01-19T23:07:30Z|RUN_ARTIFACT_IMPLEMENTATION
  - `ab9daed39984...` 2026-01-18T21:43:28Z|Option B.2 Implemented
  - `201fd6c8465a...` 2026-01-18T06:43:57Z|Update documentation and SQL validation packs for enhanced pipeline status and derived data validation
  - `961738bf86f3...` 2026-01-18T22:19:09Z|OVC Option C.3 Stub and unit tests for Threshold Registry
  - `c0a56dca5669...` 2026-01-20T01:30:52Z|feat(docs): Update Pipeline Reality Map and OVC Current Workflow

### Macro Epoch 10 -- docs/+releases/ | releases | ovc doctrine immutability

- **Date range:** 2026-01-20T03:11:01 -> 2026-01-20T03:11:01
- **Commits:** 1
- **Micro epochs included:** [20]
- **Dominant dirs:** `docs/` (1), `releases/` (1)
- **Dominant tags:** `releases` (1)
- **Dominant classes:** `UNKNOWN` (1)
- **Representative commits:**
  - `88eff122fe89...` 2026-01-20T03:11:01Z| OVC Doctrine and Immutability Notice

### Macro Epoch 11 -- research/ | research | study block range

- **Date range:** 2026-01-20T04:58:31 -> 2026-01-20T05:31:50
- **Commits:** 8
- **Micro epochs included:** [21, 22, 23, 24, 25, 26]
- **Dominant dirs:** `research/` (8)
- **Dominant tags:** `research` (8)
- **Dominant classes:** `UNKNOWN` (8)
- **Representative commits:**
  - `f2f8bd0bbdf3...` 2026-01-20T04:58:31Z|Add research artifacts and documentation for exploratory studies
  - `913bd4d3430b...` 2026-01-20T05:01:54Z|Add initial study files for basic feature-outcome analysis of GBPUSD
  - `db312bd11cfd...` 2026-01-20T05:10:12Z|Add initial files for block range intensity score sanity study
  - `5553e731fc66...` 2026-01-20T05:13:47Z|Add study files for block range intensity score analysis
  - `4607f31a4ed9...` 2026-01-20T05:18:09Z|Add initial files for block range intensity score temporal stability study

### Macro Epoch 12 -- sql/+docs/ | evidence_runs+research | dis studies lid

- **Date range:** 2026-01-20T05:43:18 -> 2026-01-20T10:06:54
- **Commits:** 7
- **Micro epochs included:** [27]
- **Dominant dirs:** `sql/` (6), `docs/` (4), `research/` (1)
- **Dominant tags:** `evidence_runs` (6), `research` (1)
- **Dominant classes:** `A` (6), `UNKNOWN` (5)
- **Representative commits:**
  - `04d95ab73c8d...` 2026-01-20T06:41:53Z|Add new studies for DIS, LID, and RES scores focusing on stability and outcome associations
  - `0f853613954d...` 2026-01-20T08:29:35Z|Update DIS score to v1.1, removing directional_efficiency dependency; add documentation and status files for Path 1 freeze
  - `b07313878bb6...` 2026-01-20T09:24:25Z|feat: Add operational guide and SQL patches for Path 1 evidence runs
  - `38fcad2b1963...` 2026-01-20T05:43:18Z|Add study documentation for block range intensity by C3 trend bias
  - `a04f8b2d318e...` 2026-01-20T08:39:31Z|Add distributional analysis studies for DIS-v1.1, LID-v1.0, and RES-v1.0 scores with corresponding views

### Macro Epoch 13 -- reports/+scripts/ | evidence_runs+scripts_general | evidence path1 automated

- **Date range:** 2026-01-20T10:19:30 -> 2026-02-02T06:44:44
- **Commits:** 94
- **Micro epochs included:** [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]
- **Dominant dirs:** `reports/` (48), `scripts/` (30), `docs/` (28), `sql/` (27), `.github/` (25)
- **Dominant tags:** `evidence_runs` (48), `scripts_general` (30), `ci_workflows` (25), `governance_contracts` (11), `repo_maze` (9)
- **Dominant classes:** `A` (46), `C` (44), `UNKNOWN` (34), `E` (29), `B` (11)
- **Representative commits:**
  - `27354e74047c...` 2026-01-21T21:48:05Z|Repo-restructuring
  - `3c9fbb1079f7...` 2026-01-22T06:49:07Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `bf516503e1c7...` 2026-01-22T03:57:26Z|Path1: add Evidence Pack v0.2 + run p1_20260120_031 outputs; add backfill_m15 workflow; ignore pytest temp dirs
  - `d5a9c3694ea1...` 2026-01-20T12:33:06Z|Path 1 Evidence Run(s) - Automated
  - `fcbe9465b876...` 2026-01-20T12:54:24Z|Merge pull request #8 from owenguobadia24s-collab/evidence-run-20260120-123211

### Macro Epoch 14 -- .codex/+Tetsu/ | codex_runtime+validation | main audit merge

- **Date range:** 2026-02-02T14:36:41 -> 2026-02-02T21:06:37
- **Commits:** 9
- **Micro epochs included:** [45, 46, 47, 48]
- **Dominant dirs:** `.codex/` (8), `Tetsu/` (6), `/` (3), `reports/` (1), `sql/` (1)
- **Dominant tags:** `codex_runtime` (8), `validation` (6), `repo_maze` (6), `operations` (3), `evidence_runs` (1)
- **Dominant classes:** `C` (8), `UNKNOWN` (8), `E` (3), `A` (1)
- **Representative commits:**
  - `44403d3f4725...` 2026-02-02T15:24:36Z|Merge branches 'main' and 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `85cb367082e9...` 2026-02-02T17:03:44Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `4c245c6e90ee...` 2026-02-02T14:36:41Z|Add codex audit harness (prompts + checks); ignore runtime and runs
  - `731fe267ee27...` 2026-02-02T18:28:08Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `d844f2eb3abf...` 2026-02-02T18:26:45Z|Audit Harness_V1

### Macro Epoch 15 -- reports/+sql/ | evidence_runs+governance_contracts | path1 evidence 20260203

- **Date range:** 2026-02-02T23:00:17 -> 2026-02-04T06:05:33
- **Commits:** 3
- **Micro epochs included:** [49]
- **Dominant dirs:** `reports/` (2), `sql/` (2), `Tetsu/` (1), `Work Timeline/` (1), `docs/` (1)
- **Dominant tags:** `evidence_runs` (2), `governance_contracts` (1), `repo_maze` (1)
- **Dominant classes:** `A` (2), `B` (1), `UNKNOWN` (1)
- **Representative commits:**
  - `11bba2ccaf60...` 2026-02-03T06:08:18Z|path1 evidence: p1_20260203_GBPUSD_20260202_len5d_8c35df6c
  - `956982dbb26f...` 2026-02-04T06:05:33Z|path1 evidence: p1_20260204_GBPUSD_20260203_len5d_c00576a2
  - `b3e733edcd5f...` 2026-02-02T23:00:17Z|freeze(legend): canonicalize NodeID authority and lock governance

### Macro Epoch 16 -- tools/+docs/ | validation+evidence_runs | phase governance registry

- **Date range:** 2026-02-04T20:14:03 -> 2026-02-07T05:33:31
- **Commits:** 25
- **Micro epochs included:** [50, 51, 52, 53, 54, 55, 56]
- **Dominant dirs:** `tools/` (11), `docs/` (9), `/` (8), `sql/` (7), `reports/` (7)
- **Dominant tags:** `validation` (9), `evidence_runs` (8), `governance_contracts` (7), `control_panel` (6), `ci_workflows` (4)
- **Dominant classes:** `C` (13), `UNKNOWN` (8), `B` (8), `A` (6), `D` (6)
- **Representative commits:**
  - `39696066e87f...` 2026-02-04T20:14:36Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `02fc2accfe43...` 2026-02-04T20:14:03Z|Phase 1 - Goveranance Reference & Inspection Phase 1.5 - Governance Cohesion & Closure Phase 1.6 — Canonical Pruning & Freeze
  - `a818656ec696...` 2026-02-05T02:28:02Z|Phase 2.2: add registry schema wrapper + validation reports
  - `8452511e7ae1...` 2026-02-05T06:45:20Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `9267725acf1c...` 2026-02-05T11:53:16Z|Phase 4:  audit interpretation/ agent

### Macro Epoch 17 -- .github/+.vscode/ | artifacts+catalogs | change classification taxonomy

- **Date range:** 2026-02-07T18:26:34 -> 2026-02-07T18:26:34
- **Commits:** 1
- **Micro epochs included:** [57]
- **Dominant dirs:** `.github/` (1), `.vscode/` (1), `/` (1), `artifacts/` (1), `docs/` (1)
- **Dominant tags:** `artifacts` (1), `catalogs` (1), `ci_workflows` (1), `governance_contracts` (1), `governance_tooling` (1)
- **Dominant classes:** `B` (1), `C` (1), `E` (1), `UNKNOWN` (1)
- **Representative commits:**
  - `ff1564dd8e4c...` 2026-02-07T18:26:34Z|Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation

### Macro Epoch 18 -- .github/ | ci_workflows | docs change classification

- **Date range:** 2026-02-07T18:29:46 -> 2026-02-07T18:29:46
- **Commits:** 1
- **Micro epochs included:** [58]
- **Dominant dirs:** `.github/` (1)
- **Dominant tags:** `ci_workflows` (1)
- **Dominant classes:** `UNKNOWN` (1)
- **Representative commits:**
  - `2a68adf9762f...` 2026-02-07T18:29:46Z|docs(pr): add change classification section to PR template

### Macro Epoch 19 -- scripts/+tests/ | governance_tooling+tests | governance overlay path1

- **Date range:** 2026-02-08T05:12:11 -> 2026-02-09T05:12:52
- **Commits:** 9
- **Micro epochs included:** [59, 60, 61, 62]
- **Dominant dirs:** `scripts/` (6), `tests/` (4), `docs/` (4), `reports/` (3), `sql/` (3)
- **Dominant tags:** `governance_tooling` (6), `tests` (4), `catalogs` (4), `evidence_runs` (3)
- **Dominant classes:** `C` (6), `UNKNOWN` (4), `A` (3), `E` (2)
- **Representative commits:**
  - `52d4a177ba43...` 2026-02-08T16:51:35Z|Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
  - `7d92461d83ba...` 2026-02-08T05:12:11Z|path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
  - `cfd91a7d8026...` 2026-02-09T05:12:52Z|path1 evidence: p1_20260209_GBPUSD_20260208_len5d_b4cdab60
  - `d50080c7197a...` 2026-02-08T16:27:49Z|merge: overlay v0.1 deterministic hardening
  - `3ee57f59d634...` 2026-02-08T14:59:28Z|governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)

## Micro Epochs (Compact View)

| Micro | Label | Dates | Commits | Top Dir | Top Tag |
|-------|-------|-------|---------|---------|---------|
| 0 | /+.github/ | ci_workflows+contracts | backfill contract work | 2026-01-14 -> 2026-01-14 | 16 | `/` | `ci_workflows` |
| 1 | tools/+tests/ | tools_general+tests | tools contract export | 2026-01-14 -> 2026-01-14 | 4 | `tools/` | `tools_general` |
| 2 | tests/ | tests | export string full | 2026-01-14 -> 2026-01-14 | 1 | `tests/` | `tests` |
| 3 | contracts/+tools/ | contracts+tools_general | export type re | 2026-01-14 -> 2026-01-14 | 11 | `contracts/` | `contracts` |
| 4 | infra/ | infra | refactor ovc webhook | 2026-01-14 -> 2026-01-14 | 1 | `infra/` | `infra` |
| 5 | .github/+docs/ | ci_workflows+infra | worker upsert min | 2026-01-14 -> 2026-01-14 | 1 | `.github/` | `ci_workflows` |
| 6 | docs/+infra/ | infra+contracts | merge pull request | 2026-01-14 -> 2026-01-15 | 8 | `docs/` | `infra` |
| 7 | docs/ | ovc current workflow | 2026-01-16 -> 2026-01-16 | 2 | `docs/` | `-` |
| 8 | sql/+/ | evidence_runs+contracts | sql table references | 2026-01-16 -> 2026-01-16 | 4 | `sql/` | `evidence_runs` |
| 9 | sql/+infra/ | evidence_runs+infra | column references events | 2026-01-16 -> 2026-01-17 | 2 | `sql/` | `evidence_runs` |
| 10 | infra/+tests/ | infra+tests | min infra pine | 2026-01-17 -> 2026-01-17 | 9 | `infra/` | `infra` |
| 11 | infra/+docs/ | infra+scripts_general | disable ret semantic | 2026-01-17 -> 2026-01-17 | 2 | `infra/` | `infra` |
| 12 | docs/+sql/ | evidence_runs+contracts | option sample script | 2026-01-17 -> 2026-01-17 | 7 | `docs/` | `evidence_runs` |
| 13 | pine/+sql/ | evidence_runs+pine | option audit | 2026-01-17 -> 2026-01-17 | 1 | `pine/` | `evidence_runs` |
| 14 | docs/+scripts/ | validation+scripts_general | validation ing | 2026-01-17 -> 2026-01-18 | 9 | `docs/` | `validation` |
| 15 | docs/+src/ | source_code+validation | refactor backfill scri | 2026-01-18 -> 2026-01-18 | 1 | `docs/` | `source_code` |
| 16 | docs/+src/ | source_code+validation | validation option docu | 2026-01-18 -> 2026-01-18 | 12 | `docs/` | `source_code` |
| 17 | docs/+src/ | source_code+ci_workflows | regime trend impleme | 2026-01-18 -> 2026-01-19 | 7 | `docs/` | `source_code` |
| 18 | docs/+sql/ | evidence_runs+validation | pipeline reality map | 2026-01-19 -> 2026-01-20 | 6 | `docs/` | `evidence_runs` |
| 19 | docs/+sql/ | evidence_runs+validation | implementation contr | 2026-01-20 -> 2026-01-20 | 2 | `docs/` | `evidence_runs` |
| 20 | docs/+releases/ | releases | ovc doctrine immutability | 2026-01-20 -> 2026-01-20 | 1 | `docs/` | `releases` |
| 21 | research/ | research | research artifacts documentation | 2026-01-20 -> 2026-01-20 | 1 | `research/` | `research` |
| 22 | research/ | research | initial study files | 2026-01-20 -> 2026-01-20 | 1 | `research/` | `research` |
| 23 | research/ | research | block range intensity | 2026-01-20 -> 2026-01-20 | 1 | `research/` | `research` |
| 24 | research/ | research | initial files block | 2026-01-20 -> 2026-01-20 | 1 | `research/` | `research` |
| 25 | research/ | research | study files block | 2026-01-20 -> 2026-01-20 | 3 | `research/` | `research` |
| 26 | research/ | research | study 20260120 block | 2026-01-20 -> 2026-01-20 | 1 | `research/` | `research` |
| 27 | sql/+docs/ | evidence_runs+research | dis studies lid | 2026-01-20 -> 2026-01-20 | 7 | `sql/` | `evidence_runs` |
| 28 | reports/+.github/ | evidence_runs+ci_workflows | path1 queue | 2026-01-20 -> 2026-01-20 | 3 | `reports/` | `evidence_runs` |
| 29 | scripts/+reports/ | scripts_general+evidence_runs | validati | 2026-01-20 -> 2026-01-20 | 7 | `scripts/` | `scripts_general` |
| 30 | reports/+sql/ | evidence_runs+ci_workflows | evidence enhanc | 2026-01-20 -> 2026-01-20 | 5 | `reports/` | `evidence_runs` |
| 31 | reports/+scripts/ | evidence_runs+scripts_general | evidence | 2026-01-20 -> 2026-01-20 | 3 | `reports/` | `evidence_runs` |
| 32 | .github/+scripts/ | ci_workflows+scripts_general | enhance e | 2026-01-20 -> 2026-01-20 | 1 | `.github/` | `ci_workflows` |
| 33 | reports/+.github/ | evidence_runs+ci_workflows | evidence en | 2026-01-20 -> 2026-01-22 | 15 | `reports/` | `evidence_runs` |
| 34 | /+reports/ | evidence_runs | chore vscode path1 | 2026-01-22 -> 2026-01-22 | 4 | `/` | `evidence_runs` |
| 35 | .github/+reports/ | ci_workflows+evidence_runs | evidence wo | 2026-01-22 -> 2026-01-22 | 3 | `.github/` | `ci_workflows` |
| 36 | reports/+sql/ | evidence_runs+ci_workflows | evidence path1  | 2026-01-22 -> 2026-01-22 | 7 | `reports/` | `evidence_runs` |
| 37 | reports/+scripts/ | evidence_runs+scripts_general | evidence | 2026-01-22 -> 2026-01-22 | 17 | `reports/` | `evidence_runs` |
| 38 | reports/+scripts/ | evidence_runs+scripts_general | feat sta | 2026-01-22 -> 2026-01-22 | 6 | `reports/` | `evidence_runs` |
| 39 | docs/+.github/ | ci_workflows+scripts_general | documentatio | 2026-01-22 -> 2026-01-23 | 7 | `docs/` | `ci_workflows` |
| 40 | /+docs/ | governance_contracts+ci_workflows | governance fea | 2026-01-23 -> 2026-01-23 | 2 | `/` | `governance_contracts` |
| 41 | Tetsu/+docs/ | repo_maze+governance_contracts | repo map ovc | 2026-01-24 -> 2026-01-26 | 6 | `Tetsu/` | `repo_maze` |
| 42 | Tetsu/+reports/ | repo_maze+evidence_runs | path1 evidence g | 2026-01-29 -> 2026-02-01 | 6 | `Tetsu/` | `repo_maze` |
| 43 | Tetsu/+docs/ | evidence_runs+governance_contracts | merge br | 2026-02-01 -> 2026-02-01 | 1 | `Tetsu/` | `evidence_runs` |
| 44 | reports/+sql/ | evidence_runs | path1 evidence 20260202 | 2026-02-02 -> 2026-02-02 | 1 | `reports/` | `evidence_runs` |
| 45 | .codex/+/ | codex_runtime+operations | codex audit harness | 2026-02-02 -> 2026-02-02 | 1 | `.codex/` | `codex_runtime` |
| 46 | .codex/+/ | codex_runtime+evidence_runs | main merge branche | 2026-02-02 -> 2026-02-02 | 2 | `.codex/` | `codex_runtime` |
| 47 | .codex/+Tetsu/ | codex_runtime+repo_maze | merge branch main | 2026-02-02 -> 2026-02-02 | 4 | `.codex/` | `codex_runtime` |
| 48 | .codex/+Tetsu/ | codex_runtime+validation | timestamp genera | 2026-02-02 -> 2026-02-02 | 2 | `.codex/` | `codex_runtime` |
| 49 | reports/+sql/ | evidence_runs+governance_contracts | path1 e | 2026-02-02 -> 2026-02-04 | 3 | `reports/` | `evidence_runs` |
| 50 | src/+.codex/ | evidence_runs+source_code | phase governance  | 2026-02-04 -> 2026-02-05 | 6 | `src/` | `evidence_runs` |
| 51 | /+tools/ | tools_general+governance_contracts | phase regist | 2026-02-05 -> 2026-02-05 | 4 | `/` | `tools_general` |
| 52 | docs/ | validation+governance_contracts | phase contracts re | 2026-02-05 -> 2026-02-05 | 2 | `docs/` | `validation` |
| 53 | /+.github/ | validation+ci_workflows | refactor workflows st | 2026-02-05 -> 2026-02-05 | 3 | `/` | `validation` |
| 54 | tools/ | control_panel | typescript configuration package | 2026-02-05 -> 2026-02-05 | 1 | `tools/` | `control_panel` |
| 55 | /+reports/ | control_panel+evidence_runs | merge branch main | 2026-02-05 -> 2026-02-05 | 1 | `/` | `control_panel` |
| 56 | tools/+docs/ | control_panel+governance_contracts | agent go | 2026-02-05 -> 2026-02-07 | 8 | `tools/` | `control_panel` |
| 57 | .github/+.vscode/ | artifacts+catalogs | change classificati | 2026-02-07 -> 2026-02-07 | 1 | `.github/` | `artifacts` |
| 58 | .github/ | ci_workflows | docs change classification | 2026-02-07 -> 2026-02-07 | 1 | `.github/` | `ci_workflows` |
| 59 | scripts/+tests/ | governance_tooling+tests | governance rang | 2026-02-08 -> 2026-02-08 | 3 | `scripts/` | `governance_tooling` |
| 60 | scripts/ | governance_tooling | governance make overlay | 2026-02-08 -> 2026-02-08 | 1 | `scripts/` | `governance_tooling` |
| 61 | scripts/+docs/ | governance_tooling+catalogs | merge overlay | 2026-02-08 -> 2026-02-08 | 3 | `scripts/` | `governance_tooling` |
| 62 | docs/+reports/ | catalogs+evidence_runs | post phase consoli | 2026-02-09 -> 2026-02-09 | 2 | `docs/` | `catalogs` |

## Crossover Map

### Top Tag-Tag Overlaps

| Tags | Commits |
|------|---------|
| `ci_workflows + scripts_general` | 21 |
| `evidence_runs + scripts_general` | 17 |
| `source_code + validation` | 17 |
| `ci_workflows + evidence_runs` | 14 |
| `ci_workflows + source_code` | 13 |
| `evidence_runs + source_code` | 12 |
| `evidence_runs + validation` | 11 |
| `scripts_general + validation` | 10 |
| `ci_workflows + validation` | 9 |
| `codex_runtime + validation` | 8 |
| `evidence_runs + tests` | 8 |
| `governance_contracts + validation` | 8 |
| `scripts_general + source_code` | 8 |
| `tests + tools_general` | 8 |
| `ci_workflows + tests` | 7 |
| `infra + source_code` | 7 |
| `infra + validation` | 7 |
| `scripts_general + tests` | 7 |
| `source_code + tests` | 7 |
| `tests + validation` | 7 |

### Top Class-Tag Overlaps

| Class + Tag | Commits |
|-------------|---------|
| `class:A + tag:evidence_runs` | 64 |
| `class:C + tag:scripts_general` | 46 |
| `class:C + tag:ci_workflows` | 45 |
| `class:UNKNOWN + tag:evidence_runs` | 43 |
| `class:E + tag:ci_workflows` | 42 |
| `class:UNKNOWN + tag:validation` | 40 |
| `class:C + tag:validation` | 37 |
| `class:C + tag:evidence_runs` | 30 |
| `class:UNKNOWN + tag:ci_workflows` | 30 |
| `class:C + tag:source_code` | 29 |
| `class:UNKNOWN + tag:scripts_general` | 29 |
| `class:C + tag:tests` | 27 |
| `class:UNKNOWN + tag:source_code` | 27 |
| `class:UNKNOWN + tag:infra` | 23 |
| `class:E + tag:scripts_general` | 22 |

### Top 5 Tag-Tag Overlap Windows

#### `ci_workflows + scripts_general` (21 commits)

- Window 1: 2026-01-23 -> 2026-01-23 (3 commits)
  - Hashes: 0cf7aac0e70d, 2f375f236068, 064339bb46be
- Window 2: 2026-01-19 -> 2026-01-19 (2 commits)
  - Hashes: 2764b9c2e8ad, ee46496d2627
- Window 3: 2026-01-21 -> 2026-01-22 (2 commits)
  - Hashes: b092afc564f9, bf516503e1c7
- Window 4: 2026-01-17 -> 2026-01-17 (1 commits)
  - Hashes: 13a589b968ee
- Window 5: 2026-01-17 -> 2026-01-17 (1 commits)
  - Hashes: cd780720b768

#### `evidence_runs + scripts_general` (17 commits)

- Window 1: 2026-01-17 -> 2026-01-17 (2 commits)
  - Hashes: 0dde7775c0f1, 13a589b968ee
- Window 2: 2026-01-21 -> 2026-01-22 (2 commits)
  - Hashes: b092afc564f9, bf516503e1c7
- Window 3: 2026-01-22 -> 2026-01-22 (2 commits)
  - Hashes: 851fbad32467, b7b09557b7fe
- Window 4: 2026-01-17 -> 2026-01-17 (1 commits)
  - Hashes: cd780720b768
- Window 5: 2026-01-18 -> 2026-01-18 (1 commits)
  - Hashes: ab9daed39984

#### `source_code + validation` (17 commits)

- Window 1: 2026-01-17 -> 2026-01-18 (5 commits)
  - Hashes: 5ddb81c41c2e, e4fb8f4f4194, c9d506c18207, 99d030e51d59, 1759c448f2d1
- Window 2: 2026-01-18 -> 2026-01-18 (4 commits)
  - Hashes: f09687dd9b64, 46f691a4aca2, b1e87b4a7983, d9a89c033de3
- Window 3: 2026-01-18 -> 2026-01-18 (2 commits)
  - Hashes: 71072aa465e5, 201fd6c8465a
- Window 4: 2026-02-04 -> 2026-02-04 (2 commits)
  - Hashes: 12ef20f81b85, 39696066e87f
- Window 5: 2026-01-18 -> 2026-01-18 (1 commits)
  - Hashes: ab9daed39984

#### `ci_workflows + evidence_runs` (14 commits)

- Window 1: 2026-01-18 -> 2026-01-18 (3 commits)
  - Hashes: ab9daed39984, 961738bf86f3, e43ee24cad88
- Window 2: 2026-01-20 -> 2026-01-20 (2 commits)
  - Hashes: 32459654a775, 66ecada57104
- Window 3: 2026-01-21 -> 2026-01-22 (2 commits)
  - Hashes: b092afc564f9, bf516503e1c7
- Window 4: 2026-01-17 -> 2026-01-17 (1 commits)
  - Hashes: 13a589b968ee
- Window 5: 2026-01-17 -> 2026-01-17 (1 commits)
  - Hashes: cd780720b768

#### `ci_workflows + source_code` (13 commits)

- Window 1: 2026-01-18 -> 2026-01-18 (3 commits)
  - Hashes: ab9daed39984, 961738bf86f3, e43ee24cad88
- Window 2: 2026-01-14 -> 2026-01-14 (2 commits)
  - Hashes: aaecb0cab415, df6e2c64fc22
- Window 3: 2026-01-18 -> 2026-01-18 (2 commits)
  - Hashes: b1e87b4a7983, d9a89c033de3
- Window 4: 2026-01-14 -> 2026-01-14 (1 commits)
  - Hashes: fb35f4976787
- Window 5: 2026-01-19 -> 2026-01-19 (1 commits)
  - Hashes: ee46496d2627

## Timeline Signals

### `evidence_runs` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 73 |
| 2026-02 | 17 |

### `governance_contracts` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 9 |
| 2026-02 | 11 |

### `governance_tooling` per Month

| Month | Commits |
|-------|---------|
| 2026-02 | 7 |

### `control_panel` per Month

| Month | Commits |
|-------|---------|
| 2026-02 | 6 |

### `source_code` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 25 |
| 2026-02 | 4 |

### `scripts_general` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 43 |
| 2026-02 | 3 |

### `ci_workflows` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 42 |
| 2026-02 | 6 |

### `validation` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 30 |
| 2026-02 | 15 |

### `tests` per Month

| Month | Commits |
|-------|---------|
| 2026-01 | 21 |
| 2026-02 | 6 |

### Classification per Month

| Month | A | B | C | D | E | UNKNOWN |
|-------|---|---|---|---|---|---------|
| 2026-01 | 49 | 9 | 95 | 0 | 47 | 135 |
| 2026-02 | 15 | 12 | 28 | 6 | 11 | 25 |

---

*Timeline derived from scratch ledger + overlay. No intent claims.*
