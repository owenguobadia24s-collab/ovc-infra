# OVC Development Timeline - v0.2

## Source Artifacts
- Ledger: `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl`
- Overlay: `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.jsonl`

## Coverage
- Total commits: `22`
- Start commit (ledger first row): `e54a663953319ac936696413623538e5139e9849`
- End commit (ledger last row): `7021c84d722a6782d032dbeccfccc8aa81bd3353`
- Date span (UTC): `2026-02-05T00:53:52Z` to `2026-02-07T05:33:31Z`
- UNKNOWN commits: `2` / `22` (9.1%)
- Remaining UNKNOWN clusters by top prefix:
  - `/`: `2` commit(s)
  - `tools/`: `2` commit(s)
  - `docs/`: `1` commit(s)

## Frequency Tables

### Commits Per Month by Class
Month | A | B | C | D | E | UNKNOWN
---|---:|---:|---:|---:|---:|---:
2026-02 | 5 | 6 | 7 | 4 | 4 | 2

### Top-Level Directory Touch Counts
Prefix | Commit Touch Count
---|---:
`tools/` | 8
`docs/` | 7
`/` | 5
`reports/` | 4
`sql/` | 3
`.github/` | 2
`.codex/` | 1
`.vscode/` | 1
`_quarantine/` | 1
`scripts/` | 1
`src/` | 1
`tests/` | 1

## Derived Epochs / Time Windows
- Source: date-derived month windows (time windows, not ledger epochs)

### Macro Time Windows by Month
Month | Commits | Date Start (UTC) | Date End (UTC) | First Commit | Last Commit
---|---:|---|---|---|---
2026-02 | 22 | `2026-02-05T00:53:52Z` | `2026-02-07T05:33:31Z` | `e54a663953319ac936696413623538e5139e9849` | `7021c84d722a6782d032dbeccfccc8aa81bd3353`

## Overlap / Crossover

### Top 10 Co-Occurring Class Pairs
Pair | Commit Count
---|---:
`C+D` | 4
`B+C` | 1
`B+E` | 1
`C+E` | 1

### Top 5 Contiguous Windows for Highest-Overlap Pair
- Highest-overlap pair: `C+D` (4 commit(s))
- Window 1: indices 16-18, date `2026-02-05T07:09:55Z` to `2026-02-05T08:52:15Z`, commits: `71cfd9c1f982dc1fa96fd36f12406f0cfe6dddf4`, `1af13559e2f56707f29d12b62b34d46917f09c22`, `9fa7d15fbb1433fb1cdb88d6ff0f7f2012dd3fe1`
- Window 2: indices 13-13, date `2026-02-05T06:44:19Z` to `2026-02-05T06:44:19Z`, commits: `8f660b20cd1d0df1780e10e7b52efe7564868719`

## Appendix: Commit Index
Index | Commit | Date (UTC) | Classes
---:|---|---|---
1 | `e54a663953319ac936696413623538e5139e9849` | `2026-02-05T00:53:52Z` | `B`
2 | `456567ea4a3a64b3a374152955b1ba150628216a` | `2026-02-05T00:54:03Z` | `C`
3 | `41600c050adf38bc71e8ced7244d5b6917497154` | `2026-02-05T00:54:11Z` | `A`
4 | `a4f56d59989f53af9d204a2589f11abf523a6e7d` | `2026-02-05T00:55:14Z` | `C`
5 | `a818656ec69636a910e6bdc459bf6d122d85b802` | `2026-02-05T02:28:02Z` | `B`
6 | `519d031e804f247df4fb65b0a186b8c374e93fc9` | `2026-02-05T02:28:12Z` | `E`
7 | `fd374fa7bb76584c072d1abf7751adde9484a462` | `2026-02-05T02:59:06Z` | `E`
8 | `dd964ca3d0151285b5a3d5fc398f4b70feec7b30` | `2026-02-05T03:15:59Z` | `B`
9 | `287cf61e3e0ecba43f4606b1f0dc1ee37284b04b` | `2026-02-05T03:52:22Z` | `B`
10 | `34e45abaa3e1214689e2348e295c76090f279a6c` | `2026-02-05T04:18:21Z` | `B,C,E`
11 | `3b73583bcc60a6f93d2aa437188be998f6f50551` | `2026-02-05T05:55:19Z` | `UNKNOWN`
12 | `07022ac03513f1191f0bc192d8979d5318801c3f` | `2026-02-05T06:13:00Z` | `A`
13 | `8f660b20cd1d0df1780e10e7b52efe7564868719` | `2026-02-05T06:44:19Z` | `C,D`
14 | `8452511e7ae16af73801df8db9137a2fb429c466` | `2026-02-05T06:45:20Z` | `A`
15 | `8f5c33733a2ff75f51d3c8848ada4de0596d6506` | `2026-02-05T06:48:35Z` | `E`
16 | `71cfd9c1f982dc1fa96fd36f12406f0cfe6dddf4` | `2026-02-05T07:09:55Z` | `C,D`
17 | `1af13559e2f56707f29d12b62b34d46917f09c22` | `2026-02-05T07:24:02Z` | `C,D`
18 | `9fa7d15fbb1433fb1cdb88d6ff0f7f2012dd3fe1` | `2026-02-05T08:52:15Z` | `C,D`
19 | `22e99cd6be68a05c4c967758bacae7cbe4ff0ad6` | `2026-02-05T10:13:05Z` | `B`
20 | `9267725acf1cb687ad543188a75076013f29b0c0` | `2026-02-05T11:53:16Z` | `UNKNOWN`
21 | `a317006c3e075bb61e6d6a009c1b96537c1cc95f` | `2026-02-06T06:10:05Z` | `A`
22 | `7021c84d722a6782d032dbeccfccc8aa81bd3353` | `2026-02-07T05:33:31Z` | `A`
