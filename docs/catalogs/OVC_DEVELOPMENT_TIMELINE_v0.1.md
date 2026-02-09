# OVC Development Timeline — v0.1

## Source Artifacts
- DEV Change Ledger: `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl`
- Classification Overlay: `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl`

## Coverage
- Start (GB0): `39696066e87f82b694bf4f20905f0f3ea3c9cce2`
- End (HEAD): `52d4a177ba43263c8817db27b6634b073b4e5015`

## Derivation Statement
"This document is a derived view. It introduces no new claims."
- Overlay/ledger joins are keyed by commit hash, not row alignment.
- Overlay rows out of GB0..HEAD range: `0`

# Epochs
Epoch partition rule: Epoch windows are contiguous ranges where dominant directory cluster remains stable and overlay class distribution remains stable.
Label rule: Label text is derived only from dominant directories and repeated tokens in commit subjects; otherwise label is `Mixed activity (insufficient signal)`.
Material shift definition: A boundary is material when either dominant directory (>=50%) changes identity or dominant class set (covering >=60%) changes identity.

## Epoch 1 — contracts envelope activity
2026-02-05T00:53:52Z to 2026-02-05T03:52:22Z
Observed focus:
Dominant directories in this window: `docs/`, `tools/`, `/`.
Repeated subject tokens in this window: `contracts`, `envelope`, `registry`, `run`.
Evidence:
- commits: `e54a663` (G1,L1,O1), `456567e` (G2,L2,O2), `41600c0` (G3,L3,O3), `a4f56d5` (G4,L4,O4), `a818656` (G5,L5,O5), `519d031` (G6,L6,O6), `fd374fa` (G7,L7,O7), `dd964ca` (G8,L8,O8), `287cf61` (G9,L9,O9)
- dominant classes: B(4), C(2), E(2), A(1)
- dominant directories: docs/(4), tools/(2), /(2), .codex/(1), scripts/(1), src/(1), tests/(1), reports/(1)
- ledger refs: `L1`, `L2`, `L3`, `L4`, `L5`, `L6`, `L7`, `L8`, `L9`
- overlay refs: `O1`, `O2`, `O3`, `O4`, `O5`, `O6`, `O7`, `O8`, `O9`

## Epoch 2 — tools activity
2026-02-05T04:18:21Z to 2026-02-05T08:52:15Z
Observed focus:
Dominant directories in this window: `tools/`, `/`, `.github/`.
Repeated subject tokens in this window: `UNKNOWN (no evidence in sources)`.
Evidence:
- commits: `34e45ab` (G10,L10,O10), `3b73583` (G11,L11,O11), `07022ac` (G12,L12,O12), `8f660b2` (G13,L13,O13), `8452511` (G14,L14,O14), `8f5c337` (G15,L15,O15), `71cfd9c` (G16,L16,O16), `1af1355` (G17,L17,O17), `9fa7d15` (G18,L18,O18)
- dominant classes: C(4), D(4), UNKNOWN(3), A(2)
- dominant directories: tools/(6), /(3), .github/(2), reports/(2), sql/(2), .vscode/(1), _quarantine/(1), docs/(1)
- ledger refs: `L10`, `L11`, `L12`, `L13`, `L14`, `L15`, `L16`, `L17`, `L18`
- overlay refs: `O10`, `O11`, `O12`, `O13`, `O14`, `O15`, `O16`, `O17`, `O18`

## Epoch 3 — root/docs activity
2026-02-05T10:13:05Z to 2026-02-05T11:53:16Z
Observed focus:
Dominant directories in this window: `docs/`, `/`, `tools/`.
Repeated subject tokens in this window: `UNKNOWN (no evidence in sources)`.
Evidence:
- commits: `22e99cd` (G19,L19,O19), `9267725` (G20,L20,O20)
- dominant classes: B(1), UNKNOWN(1)
- dominant directories: docs/(2), /(1), tools/(1)
- ledger refs: `L19`, `L20`
- overlay refs: `O19`, `O20`

## Epoch 4 — reports/sql evidence path1 activity
2026-02-06T06:10:05Z to 2026-02-07T05:33:31Z
Observed focus:
Dominant directories in this window: `reports/`, `sql/`.
Repeated subject tokens in this window: `evidence`, `path1`.
Evidence:
- commits: `a317006` (G21,L21,O21), `7021c84` (G22,L22,O22)
- dominant classes: A(2)
- dominant directories: reports/(2), sql/(2)
- ledger refs: `L21`, `L22`
- overlay refs: `O21`, `O22`

## Epoch 5 — .github/.vscode change classification activity
2026-02-07T18:26:34Z to 2026-02-07T18:29:46Z
Observed focus:
Dominant directories in this window: `.github/`, `.vscode/`, `/`.
Repeated subject tokens in this window: `change`, `classification`.
Evidence:
- commits: `ff1564d` (G23,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `2a68adf` (G24,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources))
- dominant classes: UNKNOWN (no evidence in sources)(2)
- dominant directories: .github/(2), .vscode/(1), /(1), artifacts/(1), docs/(1), scripts/(1), tests/(1), tools/(1)
- ledger refs: `UNKNOWN (no evidence in sources)`
- overlay refs: `UNKNOWN (no evidence in sources)`

## Epoch 6 — reports/sql activity
2026-02-08T05:12:11Z to 2026-02-08T05:12:11Z
Observed focus:
Dominant directories in this window: `reports/`, `sql/`.
Repeated subject tokens in this window: `UNKNOWN (no evidence in sources)`.
Evidence:
- commits: `7d92461` (G25,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources))
- dominant classes: UNKNOWN (no evidence in sources)(1)
- dominant directories: reports/(1), sql/(1)
- ledger refs: `UNKNOWN (no evidence in sources)`
- overlay refs: `UNKNOWN (no evidence in sources)`

## Epoch 7 — docs/scripts governance overlay activity
2026-02-08T14:32:41Z to 2026-02-08T16:51:35Z
Observed focus:
Dominant directories in this window: `scripts/`, `tests/`, `docs/`.
Repeated subject tokens in this window: `governance`, `overlay`, `repo-root`, `resolution`.
Evidence:
- commits: `8950c6c` (G26,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `3ee57f5` (G27,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `35eb846` (G28,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `d50080c` (G29,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `6919b4e` (G30,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources)), `52d4a17` (G31,UNKNOWN (no evidence in sources),UNKNOWN (no evidence in sources))
- dominant classes: UNKNOWN (no evidence in sources)(6)
- dominant directories: scripts/(6), tests/(4), docs/(3), /(2), reports/(1), sql/(1)
- ledger refs: `UNKNOWN (no evidence in sources)`
- overlay refs: `UNKNOWN (no evidence in sources)`

# Appendix — Commit Index (Derived)
Commit | Date | Classes | Directories | Subject
---|---|---|---|---
`e54a663953319ac936696413623538e5139e9849` | 2026-02-05T00:53:52Z | B | docs/ | docs(governance): add run envelope standard + expected versions v0.1
`456567ea4a3a64b3a374152955b1ba150628216a` | 2026-02-05T00:54:03Z | C | .codex/,scripts/,src/,tests/,tools/ | feat(qa): add run envelope v0.1 + validation pack + registry tooling
`41600c050adf38bc71e8ced7244d5b6917497154` | 2026-02-05T00:54:11Z | A | reports/ | evidence(path1): add p1_20260204_001 artifacts and update resolved queue
`a4f56d59989f53af9d204a2589f11abf523a6e7d` | 2026-02-05T00:55:14Z | C | tools/ | test(compat): restore tools.validate_contract + parse_export via archive shims
`a818656ec69636a910e6bdc459bf6d122d85b802` | 2026-02-05T02:28:02Z | B | docs/ | Phase 2.2: add registry schema wrapper + validation reports
`519d031e804f247df4fb65b0a186b8c374e93fc9` | 2026-02-05T02:28:12Z | E | / | Phase 2.2.1/2 Add new schemas and validators for registry management
`fd374fa7bb76584c072d1abf7751adde9484a462` | 2026-02-05T02:59:06Z | E | / | Option A: enforce LF normalization + ignore Windows nul
`dd964ca3d0151285b5a3d5fc398f4b70feec7b30` | 2026-02-05T03:15:59Z | B | docs/ | Phase 2.2.3 Registry Delta Log functionality
`287cf61e3e0ecba43f4606b1f0dc1ee37284b04b` | 2026-02-05T03:52:22Z | B | docs/ | Phase 2.3 Maintenance Contracts including Health, Recovery, and Upgrade Contracts
`34e45abaa3e1214689e2348e295c76090f279a6c` | 2026-02-05T04:18:21Z | UNKNOWN | .github/,.vscode/,/,_quarantine/,docs/ | Refactor CI workflows to streamline script path validation and enhance environment variable management
`3b73583bcc60a6f93d2aa437188be998f6f50551` | 2026-02-05T05:55:19Z | UNKNOWN | /,tools/ | Phase 3 with timeline display and summary stats
`07022ac03513f1191f0bc192d8979d5318801c3f` | 2026-02-05T06:13:00Z | A | reports/,sql/ | path1 evidence: p1_20260205_GBPUSD_20260204_len5d_34fb1bcb
`8f660b20cd1d0df1780e10e7b52efe7564868719` | 2026-02-05T06:44:19Z | C,D | tools/ | Add TypeScript configuration and package files for phase 3 control panel
`8452511e7ae16af73801df8db9137a2fb429c466` | 2026-02-05T06:45:20Z | A | /,reports/,sql/,tools/ | Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
`8f5c33733a2ff75f51d3c8848ada4de0596d6506` | 2026-02-05T06:48:35Z | UNKNOWN | .github/ | Update AI Agent Instructions with project overview, governance rules, and developer workflows
`71cfd9c1f982dc1fa96fd36f12406f0cfe6dddf4` | 2026-02-05T07:09:55Z | C,D | tools/ | Add ParseErrorPanel component to adapt ParseError for ErrorPanel display
`1af13559e2f56707f29d12b62b34d46917f09c22` | 2026-02-05T07:24:02Z | C,D | tools/ |  Implement Phase 3 Control Panel with read-only functionality
`9fa7d15fbb1433fb1cdb88d6ff0f7f2012dd3fe1` | 2026-02-05T08:52:15Z | C,D | tools/ | Refactor DeltaLogView and FailuresPage components for improved clarity and accuracy
`22e99cd6be68a05c4c967758bacae7cbe4ff0ad6` | 2026-02-05T10:13:05Z | B | docs/ | Add initial draft of CONTRACT_EVOLUTION_PROTOCOL for governance and versioning guidelines
`9267725acf1cb687ad543188a75076013f29b0c0` | 2026-02-05T11:53:16Z | UNKNOWN | /,docs/,tools/ | Phase 4:  audit interpretation/ agent
`a317006c3e075bb61e6d6a009c1b96537c1cc95f` | 2026-02-06T06:10:05Z | A | reports/,sql/ | path1 evidence: p1_20260206_GBPUSD_20260205_len5d_cc78af78
`7021c84d722a6782d032dbeccfccc8aa81bd3353` | 2026-02-07T05:33:31Z | A | reports/,sql/ | path1 evidence: p1_20260207_GBPUSD_20260206_len5d_efde5bd5
`ff1564dd8e4cd61b5bbc76db3aebbba48852abdb` | 2026-02-07T18:26:34Z | UNKNOWN (no evidence in sources) | .github/,.vscode/,/,artifacts/,docs/,scripts/,tests/,tools/ | Change Taxonomy & Governance Classification (Post-Phase 4): introduce change classification and ledger generation
`2a68adf9762ff6910ea1883a6d5cf1f999cf7dae` | 2026-02-07T18:29:46Z | UNKNOWN (no evidence in sources) | .github/ | docs(pr): add change classification section to PR template
`7d92461d83ba71f8df87d28a130a7279c86d0e62` | 2026-02-08T05:12:11Z | UNKNOWN (no evidence in sources) | reports/,sql/ | path1 evidence: p1_20260208_GBPUSD_20260207_len5d_3d531e1b
`8950c6cb233d58406ddaf20247d0367948bab316` | 2026-02-08T14:32:41Z | UNKNOWN (no evidence in sources) | scripts/,tests/ | governance: harden --range parsing (reject triple-dot) + tests
`3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2` | 2026-02-08T14:59:28Z | UNKNOWN (no evidence in sources) | docs/,scripts/,tests/ | governance: deterministic hardening for overlay v0.1 (range parser + repo-root seal keys)
`35eb846e5c7111384b1570ab3a142d3fee8f3002` | 2026-02-08T16:23:57Z | UNKNOWN (no evidence in sources) | scripts/ | governance: make overlay builder cwd-independent (repo-root path resolution)
`d50080c7197abd03ed944af08d21f64cbccbd65e` | 2026-02-08T16:27:49Z | UNKNOWN (no evidence in sources) | docs/,scripts/,tests/ | merge: overlay v0.1 deterministic hardening
`6919b4e26e428bedfa3187e8ecd049c4da2aa14a` | 2026-02-08T16:47:54Z | UNKNOWN (no evidence in sources) | /,scripts/ | governance: tighten overlay builder path resolution + ignore local test artifacts
`52d4a177ba43263c8817db27b6634b073b4e5015` | 2026-02-08T16:51:35Z | UNKNOWN (no evidence in sources) | /,docs/,reports/,scripts/,sql/,tests/ | Merge branch 'main' of https://github.com/owenguobadia24s-collab/ovc-infra
