# Module Candidates v0.1

## 1. Scope & Canonical Sources

- Change Ledger: `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.jsonl`
- Macro Epoch Ranges: `docs/catalogs/epoch_ranges.macro.v0.1.json`
- Micro Epoch Ranges: `docs/catalogs/epoch_ranges.micro.v0.1.json`
- Micro Epoch Labels: `docs/catalogs/micro_epoch_labels.v0.1.json` (not provided, optional)

## 2. Epoch Summary Table

| Epoch ID | Commit Count | Top Directory | % | Top Tag | % | Status |
| --- | ---: | --- | ---: | --- | ---: | --- |
| 0 | 16 | ./ | 37.50% | ci_workflows | 25.00% | OK |
| 1 | 5 | tests | 80.00% | tests | 80.00% | OK |
| 2 | 11 | contracts | 36.36% | contracts | 36.36% | OK |
| 3 | 1 | infra | 100.00% | infra | 100.00% | OK |
| 4 | 11 | docs | 72.73% | infra | 45.45% | OK |
| 5 | 4 | sql | 100.00% | evidence_runs | 100.00% | OK |
| 6 | 11 | infra | 54.55% | infra | 54.55% | OK |
| 7 | 9 | docs | 55.56% | evidence_runs | 44.44% | OK |
| 8 | 1 | pine | 100.00% | evidence_runs | 100.00% | OK |
| 9 | 37 | docs | 91.89% | source_code | 48.65% | OK |
| 10 | 1 | docs | 100.00% | releases | 100.00% | OK |
| 11 | 8 | research | 100.00% | research | 100.00% | OK |
| 12 | 7 | sql | 85.71% | evidence_runs | 85.71% | OK |
| 13 | 94 | reports | 51.06% | evidence_runs | 51.06% | OK |
| 14 | 9 | .codex | 88.89% | codex_runtime | 88.89% | OK |
| 15 | 3 | reports | 66.67% | evidence_runs | 66.67% | OK |
| 16 | 25 | tools | 44.00% | validation | 36.00% | OK |
| 17 | 1 | ./ | 100.00% | artifacts | 100.00% | OK |
| 18 | 1 | .github | 100.00% | ci_workflows | 100.00% | OK |
| 19 | 9 | scripts | 66.67% | governance_tooling | 66.67% | OK |

## 3. Module Candidates (Grouped by Epoch)

### Epoch 0

Epoch Boundary Source: coerced(start_hash/end_hash)

No stable module candidate detected for this epoch.

### Epoch 1

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-01 — DIR:tests
Epoch: 1

Commit Ranges

- be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tests | 4 | 80.00% |
| tools | 2 | 40.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tests | 4 | 80.00% |
| tools_general | 2 | 40.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "001 txt"
- "add export"
- "export string"
Representative paths:
- tests
- tools

Draft Invariants

- INV-01: Candidate matches 4/5 commits. (support: 4/5)
- INV-02: Directory pair tests + tools co-occurs in 2/4 matched commits. (support: 2/4)

#### MOD-02 — TAG:tests
Epoch: 1

Commit Ranges

- be09dd8b58769540fc16260529816f9baef514d6..e8c253791cb6b44febb0ba6ea70b5b4042c015f0

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tests | 4 | 80.00% |
| tools | 2 | 40.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tests | 4 | 80.00% |
| tools_general | 2 | 40.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "001 txt"
- "add export"
- "export string"
Representative paths:
- tests
- tools

Draft Invariants

- INV-01: Candidate matches 4/5 commits. (support: 4/5)
- INV-02: Directory pair tests + tools co-occurs in 2/4 matched commits. (support: 2/4)

#### MOD-03 — DIR:tools
Epoch: 1

Commit Ranges

- b694a744daa305e5b5ac522a159c23a023586d5f..aad49831233824189a9c95528dc4dcee0fd9b237

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tools | 3 | 60.00% |
| tests | 2 | 40.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tools_general | 3 | 60.00% |
| tests | 2 | 40.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "tools"
Representative paths:
- tools
- tests

Draft Invariants

- INV-01: Candidate matches 3/5 commits. (support: 3/5)
- INV-02: Directory pair tests + tools co-occurs in 2/3 matched commits. (support: 2/3)

#### MOD-04 — TAG:tools_general
Epoch: 1

Commit Ranges

- b694a744daa305e5b5ac522a159c23a023586d5f..aad49831233824189a9c95528dc4dcee0fd9b237

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tools | 3 | 60.00% |
| tests | 2 | 40.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tools_general | 3 | 60.00% |
| tests | 2 | 40.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "tools"
Representative paths:
- tools
- tests

Draft Invariants

- INV-01: Candidate matches 3/5 commits. (support: 3/5)
- INV-02: Directory pair tests + tools co-occurs in 2/3 matched commits. (support: 2/3)

### Epoch 2

Epoch Boundary Source: coerced(start_hash/end_hash)

No stable module candidate detected for this epoch.

### Epoch 3

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-05 — DIR:infra
Epoch: 3

Commit Ranges

- 7c3982068064cde8acec78811adde90eca014e59..7c3982068064cde8acec78811adde90eca014e59

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- infra

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory infra appears in 1/1 matched commits. (support: 1/1)

#### MOD-06 — TAG:infra
Epoch: 3

Commit Ranges

- 7c3982068064cde8acec78811adde90eca014e59..7c3982068064cde8acec78811adde90eca014e59

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- infra

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory infra appears in 1/1 matched commits. (support: 1/1)

### Epoch 4

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-07 — DIR:docs
Epoch: 4

Commit Ranges

- aaecb0cab415bdc94a67ffb92ad903d488150367..df6e2c64fc22312b89e5baf052ec725d8bea5a07
- fb35f49767878631a9f78967cdb4c8b7150f6027..fb35f49767878631a9f78967cdb4c8b7150f6027
- 7a2ea214f506ed7320836ea9aef4277d37d04eb7..7a2ea214f506ed7320836ea9aef4277d37d04eb7
- f01d1624156f25af2d913c6e9220f23c341cd2ae..e9a5ef31982bf1086ef0633801f4c88a6d1bc7a9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 8 | 72.73% |
| infra | 4 | 36.36% |
| .github | 3 | 27.27% |
| src | 3 | 27.27% |
| ./ | 1 | 9.09% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 4 | 36.36% |
| ci_workflows | 3 | 27.27% |
| source_code | 3 | 27.27% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "owenguobadia24s collab"
- "collab codex"
- "from owenguobadia24s"
- "merge pull"
- "pull request"
- "request from"
- "workflow documentation"
- "current workflow"
- "ovc current"
Representative paths:
- docs
- infra
- .github
- src
- ./

Draft Invariants

- INV-01: Candidate matches 8/11 commits. (support: 8/11)
- INV-02: Directory pair docs + infra co-occurs in 4/8 matched commits. (support: 4/8)

#### MOD-08 — DIR:infra
Epoch: 4

Commit Ranges

- aaecb0cab415bdc94a67ffb92ad903d488150367..df6e2c64fc22312b89e5baf052ec725d8bea5a07
- fb35f49767878631a9f78967cdb4c8b7150f6027..fb35f49767878631a9f78967cdb4c8b7150f6027
- 7a2ea214f506ed7320836ea9aef4277d37d04eb7..439df1e58bf3cfab68cb9fa42313a228e4ebba01

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 5 | 45.45% |
| docs | 4 | 36.36% |
| .github | 3 | 27.27% |
| src | 3 | 27.27% |
| ./ | 1 | 9.09% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 5 | 45.45% |
| ci_workflows | 3 | 27.27% |
| source_code | 3 | 27.27% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab codex"
- "from owenguobadia24s"
- "merge pull"
- "owenguobadia24s collab"
- "pull request"
- "request from"
Representative paths:
- infra
- docs
- .github
- src
- ./

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair docs + infra co-occurs in 4/5 matched commits. (support: 4/5)

#### MOD-09 — TAG:infra
Epoch: 4

Commit Ranges

- aaecb0cab415bdc94a67ffb92ad903d488150367..df6e2c64fc22312b89e5baf052ec725d8bea5a07
- fb35f49767878631a9f78967cdb4c8b7150f6027..fb35f49767878631a9f78967cdb4c8b7150f6027
- 7a2ea214f506ed7320836ea9aef4277d37d04eb7..439df1e58bf3cfab68cb9fa42313a228e4ebba01

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 5 | 45.45% |
| docs | 4 | 36.36% |
| .github | 3 | 27.27% |
| src | 3 | 27.27% |
| ./ | 1 | 9.09% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 5 | 45.45% |
| ci_workflows | 3 | 27.27% |
| source_code | 3 | 27.27% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab codex"
- "from owenguobadia24s"
- "merge pull"
- "owenguobadia24s collab"
- "pull request"
- "request from"
Representative paths:
- infra
- docs
- .github
- src
- ./

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair docs + infra co-occurs in 4/5 matched commits. (support: 4/5)

#### MOD-10 — CLUSTER:.github|docs|infra|src
Epoch: 4

Commit Ranges

- aaecb0cab415bdc94a67ffb92ad903d488150367..df6e2c64fc22312b89e5baf052ec725d8bea5a07
- fb35f49767878631a9f78967cdb4c8b7150f6027..fb35f49767878631a9f78967cdb4c8b7150f6027
- 7a2ea214f506ed7320836ea9aef4277d37d04eb7..7a2ea214f506ed7320836ea9aef4277d37d04eb7

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 36.36% |
| infra | 4 | 36.36% |
| .github | 3 | 27.27% |
| src | 3 | 27.27% |
| ./ | 1 | 9.09% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 4 | 36.36% |
| ci_workflows | 3 | 27.27% |
| source_code | 3 | 27.27% |
| contracts | 1 | 9.09% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab codex"
- "from owenguobadia24s"
- "merge pull"
- "owenguobadia24s collab"
- "pull request"
- "request from"
Representative paths:
- docs
- infra
- .github
- src
- ./

Draft Invariants

- INV-01: Candidate matches 4/11 commits. (support: 4/11)
- INV-02: Directory pair docs + infra co-occurs in 4/4 matched commits. (support: 4/4)

### Epoch 5

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-11 — DIR:sql
Epoch: 5

Commit Ranges

- 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 4 | 100.00% |
| ./ | 1 | 25.00% |
| contracts | 1 | 25.00% |
| docs | 1 | 25.00% |
| specs | 1 | 25.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 100.00% |
| contracts | 1 | 25.00% |
| specs | 1 | 25.00% |
| validation | 1 | 25.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "fix table"
- "for consistency"
Representative paths:
- sql
- ./
- contracts
- docs
- specs

Draft Invariants

- INV-01: Candidate matches 4/4 commits. (support: 4/4)
- INV-02: Directory pair ./ + contracts co-occurs in 1/4 matched commits. (support: 1/4)

#### MOD-12 — TAG:evidence_runs
Epoch: 5

Commit Ranges

- 15353b9226cdc441cca675eda7cdb0cb91ade68d..8553d26409513c1b2abbe55a56c2d9da620777ae

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 4 | 100.00% |
| ./ | 1 | 25.00% |
| contracts | 1 | 25.00% |
| docs | 1 | 25.00% |
| specs | 1 | 25.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 100.00% |
| contracts | 1 | 25.00% |
| specs | 1 | 25.00% |
| validation | 1 | 25.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "fix table"
- "for consistency"
Representative paths:
- sql
- ./
- contracts
- docs
- specs

Draft Invariants

- INV-01: Candidate matches 4/4 commits. (support: 4/4)
- INV-02: Directory pair ./ + contracts co-occurs in 1/4 matched commits. (support: 1/4)

### Epoch 6

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-13 — CLUSTER:docs|infra|pine|tests|tools
Epoch: 6

Commit Ranges

- f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013..f42b38c714fbc4441ce7dbe0898bb66e8dfabf77

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 5 | 45.45% |
| infra | 4 | 36.36% |
| tests | 4 | 36.36% |
| pine | 3 | 27.27% |
| tools | 3 | 27.27% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 4 | 36.36% |
| tests | 4 | 36.36% |
| validation | 4 | 36.36% |
| pine | 3 | 27.27% |
| tools_general | 3 | 27.27% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min export"
- "export min"
- "from owenguobadia24s"
- "merge pull"
- "owenguobadia24s collab"
- "pine min"
- "pull request"
- "request from"
Representative paths:
- docs
- infra
- tests
- pine
- tools

Draft Invariants

- INV-01: Candidate matches 6/11 commits. (support: 6/11)
- INV-02: Directory pair infra + tests co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-14 — DIR:infra
Epoch: 6

Commit Ranges

- a4943ebb9401ac7a694316c215a93b4309b9a320..9555b7f67fde1578f02df14866d1940e2dba3dbb
- f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013..f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013
- a71332b4f91148f7c3e720210d65a6b5160db93d..9d05d844c4f072ce513c3ed8803b1ed31b288a27

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 6 | 54.55% |
| tests | 4 | 36.36% |
| docs | 3 | 27.27% |
| tools | 3 | 27.27% |
| pine | 2 | 18.18% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 6 | 54.55% |
| tests | 4 | 36.36% |
| validation | 4 | 36.36% |
| tools_general | 3 | 27.27% |
| pine | 2 | 18.18% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min"
- "infra"
- "contract"
- "export"
- "feat"
- "for"
- "merge"
- "pine"
- "validation"
- "wip"
Representative paths:
- infra
- tests
- docs
- tools
- pine

Draft Invariants

- INV-01: Candidate matches 6/11 commits. (support: 6/11)
- INV-02: Directory pair infra + tests co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-15 — TAG:infra
Epoch: 6

Commit Ranges

- a4943ebb9401ac7a694316c215a93b4309b9a320..9555b7f67fde1578f02df14866d1940e2dba3dbb
- f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013..f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013
- a71332b4f91148f7c3e720210d65a6b5160db93d..9d05d844c4f072ce513c3ed8803b1ed31b288a27

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| infra | 6 | 54.55% |
| tests | 4 | 36.36% |
| docs | 3 | 27.27% |
| tools | 3 | 27.27% |
| pine | 2 | 18.18% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 6 | 54.55% |
| tests | 4 | 36.36% |
| validation | 4 | 36.36% |
| tools_general | 3 | 27.27% |
| pine | 2 | 18.18% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min"
- "infra"
- "contract"
- "export"
- "feat"
- "for"
- "merge"
- "pine"
- "validation"
- "wip"
Representative paths:
- infra
- tests
- docs
- tools
- pine

Draft Invariants

- INV-01: Candidate matches 6/11 commits. (support: 6/11)
- INV-02: Directory pair infra + tests co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-16 — DIR:docs
Epoch: 6

Commit Ranges

- f205e42e1e936f048290671d4134bb10ad814f6b..f42b38c714fbc4441ce7dbe0898bb66e8dfabf77

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 5 | 45.45% |
| infra | 3 | 27.27% |
| pine | 3 | 27.27% |
| tests | 3 | 27.27% |
| tools | 2 | 18.18% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| infra | 3 | 27.27% |
| pine | 3 | 27.27% |
| tests | 3 | 27.27% |
| validation | 3 | 27.27% |
| tools_general | 2 | 18.18% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min export"
- "export min"
- "from owenguobadia24s"
- "merge pull"
- "owenguobadia24s collab"
- "pine min"
- "pull request"
- "request from"
Representative paths:
- docs
- infra
- pine
- tests
- tools

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair docs + infra co-occurs in 3/5 matched commits. (support: 3/5)

#### MOD-17 — DIR:pine
Epoch: 6

Commit Ranges

- a4943ebb9401ac7a694316c215a93b4309b9a320..a4943ebb9401ac7a694316c215a93b4309b9a320
- 6e3ee4a167af58cea41236135c318b77bca7b0eb..6e3ee4a167af58cea41236135c318b77bca7b0eb
- f205e42e1e936f048290671d4134bb10ad814f6b..f205e42e1e936f048290671d4134bb10ad814f6b
- 9d05d844c4f072ce513c3ed8803b1ed31b288a27..f42b38c714fbc4441ce7dbe0898bb66e8dfabf77

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 5 | 45.45% |
| docs | 3 | 27.27% |
| infra | 2 | 18.18% |
| tests | 1 | 9.09% |
| tools | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| pine | 5 | 45.45% |
| infra | 2 | 18.18% |
| tests | 1 | 9.09% |
| tools_general | 1 | 9.09% |
| validation | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min export"
- "export min"
- "pine min"
- "pine script"
Representative paths:
- pine
- docs
- infra
- tests
- tools

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair docs + pine co-occurs in 3/5 matched commits. (support: 3/5)

#### MOD-18 — DIR:tests
Epoch: 6

Commit Ranges

- f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013..f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013
- a71332b4f91148f7c3e720210d65a6b5160db93d..9d05d844c4f072ce513c3ed8803b1ed31b288a27
- 903698622a46dbc7515b110cf605269406e72360..903698622a46dbc7515b110cf605269406e72360

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tests | 5 | 45.45% |
| infra | 4 | 36.36% |
| docs | 3 | 27.27% |
| tools | 3 | 27.27% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tests | 5 | 45.45% |
| infra | 4 | 36.36% |
| validation | 4 | 36.36% |
| tools_general | 3 | 27.27% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min"
- "infra"
- "contract"
- "merge"
- "validation"
- "wip"
Representative paths:
- tests
- infra
- docs
- tools
- pine

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair infra + tests co-occurs in 4/5 matched commits. (support: 4/5)

#### MOD-19 — TAG:pine
Epoch: 6

Commit Ranges

- a4943ebb9401ac7a694316c215a93b4309b9a320..a4943ebb9401ac7a694316c215a93b4309b9a320
- 6e3ee4a167af58cea41236135c318b77bca7b0eb..6e3ee4a167af58cea41236135c318b77bca7b0eb
- f205e42e1e936f048290671d4134bb10ad814f6b..f205e42e1e936f048290671d4134bb10ad814f6b
- 9d05d844c4f072ce513c3ed8803b1ed31b288a27..f42b38c714fbc4441ce7dbe0898bb66e8dfabf77

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 5 | 45.45% |
| docs | 3 | 27.27% |
| infra | 2 | 18.18% |
| tests | 1 | 9.09% |
| tools | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| pine | 5 | 45.45% |
| infra | 2 | 18.18% |
| tests | 1 | 9.09% |
| tools_general | 1 | 9.09% |
| validation | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min export"
- "export min"
- "pine min"
- "pine script"
Representative paths:
- pine
- docs
- infra
- tests
- tools

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair docs + pine co-occurs in 3/5 matched commits. (support: 3/5)

#### MOD-20 — TAG:tests
Epoch: 6

Commit Ranges

- f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013..f7bbdde22c1a27c22a164f5a0e5e3c83d6f5e013
- a71332b4f91148f7c3e720210d65a6b5160db93d..9d05d844c4f072ce513c3ed8803b1ed31b288a27
- 903698622a46dbc7515b110cf605269406e72360..903698622a46dbc7515b110cf605269406e72360

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tests | 5 | 45.45% |
| infra | 4 | 36.36% |
| docs | 3 | 27.27% |
| tools | 3 | 27.27% |
| pine | 1 | 9.09% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| tests | 5 | 45.45% |
| infra | 4 | 36.36% |
| validation | 4 | 36.36% |
| tools_general | 3 | 27.27% |
| pine | 1 | 9.09% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "min"
- "infra"
- "contract"
- "merge"
- "validation"
- "wip"
Representative paths:
- tests
- infra
- docs
- tools
- pine

Draft Invariants

- INV-01: Candidate matches 5/11 commits. (support: 5/11)
- INV-02: Directory pair infra + tests co-occurs in 4/5 matched commits. (support: 4/5)

### Epoch 7

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-21 — DIR:docs
Epoch: 7

Commit Ranges

- fab9e5ba3cac560c71c3f5d98f013fd223296559..fab9e5ba3cac560c71c3f5d98f013fd223296559
- 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6
- 13a589b968eedf3690c3d6103ef9de0f69094a8e..13a589b968eedf3690c3d6103ef9de0f69094a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 5 | 55.56% |
| contracts | 3 | 33.33% |
| sql | 3 | 33.33% |
| ./ | 2 | 22.22% |
| scripts | 2 | 22.22% |
| .github | 1 | 11.11% |
| src | 1 | 11.11% |
| tests | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| contracts | 3 | 33.33% |
| evidence_runs | 3 | 33.33% |
| scripts_general | 2 | 22.22% |
| ci_workflows | 1 | 11.11% |
| source_code | 1 | 11.11% |
| tests | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "the"
Representative paths:
- docs
- contracts
- sql
- ./
- scripts

Draft Invariants

- INV-01: Candidate matches 5/9 commits. (support: 5/9)
- INV-02: Directory pair contracts + docs co-occurs in 3/5 matched commits. (support: 3/5)

#### MOD-22 — CLUSTER:contracts|docs|sql
Epoch: 7

Commit Ranges

- 72ce4b0a78717ca79fbc0360447faf20a1e73f70..607a8c5c4e828295534f03ef18d9ea51fde7d3c6
- 13a589b968eedf3690c3d6103ef9de0f69094a8e..13a589b968eedf3690c3d6103ef9de0f69094a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 44.44% |
| contracts | 3 | 33.33% |
| sql | 3 | 33.33% |
| ./ | 2 | 22.22% |
| .github | 1 | 11.11% |
| scripts | 1 | 11.11% |
| src | 1 | 11.11% |
| tests | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| contracts | 3 | 33.33% |
| evidence_runs | 3 | 33.33% |
| ci_workflows | 1 | 11.11% |
| scripts_general | 1 | 11.11% |
| source_code | 1 | 11.11% |
| tests | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "the"
Representative paths:
- docs
- contracts
- sql
- ./
- .github

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair contracts + docs co-occurs in 3/4 matched commits. (support: 3/4)

#### MOD-23 — DIR:scripts
Epoch: 7

Commit Ranges

- fab9e5ba3cac560c71c3f5d98f013fd223296559..fab9e5ba3cac560c71c3f5d98f013fd223296559
- 0dde7775c0f1f8073776e06d843da5bf56711ccb..68306e813ecfae4b9d5a0015441d64bbb8545119

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 4 | 44.44% |
| ./ | 2 | 22.22% |
| docs | 2 | 22.22% |
| sql | 2 | 22.22% |
| .github | 1 | 11.11% |
| infra | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| scripts_general | 4 | 44.44% |
| evidence_runs | 2 | 22.22% |
| ci_workflows | 1 | 11.11% |
| infra | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "option"
- "and"
- "run"
Representative paths:
- scripts
- ./
- docs
- sql
- .github

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair ./ + scripts co-occurs in 2/4 matched commits. (support: 2/4)

#### MOD-24 — DIR:sql
Epoch: 7

Commit Ranges

- bacc7ff998bc4375e8e1ad3bbbb6393dc51fa60a..13a589b968eedf3690c3d6103ef9de0f69094a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 4 | 44.44% |
| docs | 3 | 33.33% |
| contracts | 2 | 22.22% |
| scripts | 2 | 22.22% |
| ./ | 1 | 11.11% |
| .github | 1 | 11.11% |
| infra | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 44.44% |
| contracts | 2 | 22.22% |
| scripts_general | 2 | 22.22% |
| ci_workflows | 1 | 11.11% |
| infra | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and"
- "the"
Representative paths:
- sql
- docs
- contracts
- scripts
- ./

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair docs + sql co-occurs in 3/4 matched commits. (support: 3/4)

#### MOD-25 — TAG:evidence_runs
Epoch: 7

Commit Ranges

- bacc7ff998bc4375e8e1ad3bbbb6393dc51fa60a..13a589b968eedf3690c3d6103ef9de0f69094a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 4 | 44.44% |
| docs | 3 | 33.33% |
| contracts | 2 | 22.22% |
| scripts | 2 | 22.22% |
| ./ | 1 | 11.11% |
| .github | 1 | 11.11% |
| infra | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 44.44% |
| contracts | 2 | 22.22% |
| scripts_general | 2 | 22.22% |
| ci_workflows | 1 | 11.11% |
| infra | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and"
- "the"
Representative paths:
- sql
- docs
- contracts
- scripts
- ./

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair docs + sql co-occurs in 3/4 matched commits. (support: 3/4)

#### MOD-26 — TAG:scripts_general
Epoch: 7

Commit Ranges

- fab9e5ba3cac560c71c3f5d98f013fd223296559..fab9e5ba3cac560c71c3f5d98f013fd223296559
- 0dde7775c0f1f8073776e06d843da5bf56711ccb..68306e813ecfae4b9d5a0015441d64bbb8545119

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 4 | 44.44% |
| ./ | 2 | 22.22% |
| docs | 2 | 22.22% |
| sql | 2 | 22.22% |
| .github | 1 | 11.11% |
| infra | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| scripts_general | 4 | 44.44% |
| evidence_runs | 2 | 22.22% |
| ci_workflows | 1 | 11.11% |
| infra | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "option"
- "and"
- "run"
Representative paths:
- scripts
- ./
- docs
- sql
- .github

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair ./ + scripts co-occurs in 2/4 matched commits. (support: 2/4)

### Epoch 8

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-27 — DIR:pine
Epoch: 8

Commit Ranges

- e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 1 | 100.00% |
| sql | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 1 | 100.00% |
| pine | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- pine
- sql

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair pine + sql co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-28 — DIR:sql
Epoch: 8

Commit Ranges

- e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 1 | 100.00% |
| sql | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 1 | 100.00% |
| pine | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- pine
- sql

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair pine + sql co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-29 — TAG:evidence_runs
Epoch: 8

Commit Ranges

- e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 1 | 100.00% |
| sql | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 1 | 100.00% |
| pine | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- pine
- sql

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair pine + sql co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-30 — TAG:pine
Epoch: 8

Commit Ranges

- e3b80fc3cebdf11218409ce368e85a5b9192f923..e3b80fc3cebdf11218409ce368e85a5b9192f923

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| pine | 1 | 100.00% |
| sql | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 1 | 100.00% |
| pine | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- pine
- sql

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair pine + sql co-occurs in 1/1 matched commits. (support: 1/1)

### Epoch 9

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-31 — DIR:docs
Epoch: 9

Commit Ranges

- cd780720b768933334a53f0231c60b4227311e13..cd780720b768933334a53f0231c60b4227311e13
- 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..23fcb1976810add88fc9309a8f2fa7fa8c275448
- 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e
- 800fbb9a6063f067a63b2f51b5e6bd801d7769e8..0197359d49adff54eedae2d3c60e160fe9ba183c

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 34 | 91.89% |
| src | 17 | 45.95% |
| sql | 11 | 29.73% |
| scripts | 8 | 21.62% |
| .github | 7 | 18.92% |
| tests | 4 | 10.81% |
| ./ | 2 | 5.41% |
| configs | 2 | 5.41% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| source_code | 17 | 45.95% |
| validation | 17 | 45.95% |
| evidence_runs | 11 | 29.73% |
| ci_workflows | 9 | 24.32% |
| scripts_general | 8 | 21.62% |
| tests | 4 | 10.81% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |
| infra | 1 | 2.70% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and sql"
- "and update"
- "contract and"
- "for features"
- "implementation contract"
- "pipeline reality"
- "pipeline status"
- "reality map"
- "sql view"
- "update documentation"
Representative paths:
- docs
- src
- sql
- scripts
- .github

Draft Invariants

- INV-01: Candidate matches 34/37 commits. (support: 34/37)
- INV-02: Directory pair docs + src co-occurs in 17/34 matched commits. (support: 17/34)

#### MOD-32 — CLUSTER:./|.github|docs|scripts|sql|src|tests
Epoch: 9

Commit Ranges

- cd780720b768933334a53f0231c60b4227311e13..201fd6c8465a645b52b08435a1665638b2cfa281
- f09687dd9b6481b0c7d5fc26984ac984db39a269..d9a89c033de344b71b648ff33af27f076c0895d2
- cbb8bfcee27dea9525e43be8b9017d64fbda5bf5..d348c04646de00626c534cdf39d5ee1cae7e8511
- 2764b9c2e8ad17e3ce809e9f2100c3e1ffbcf89f..ee46496d262759fcae78902ffc07b4d2ac71282e
- 44d409e5a7f9c3ca15cc14b82b96bce5640ed307..0197359d49adff54eedae2d3c60e160fe9ba183c

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 25 | 67.57% |
| src | 17 | 45.95% |
| sql | 11 | 29.73% |
| scripts | 9 | 24.32% |
| .github | 7 | 18.92% |
| tests | 4 | 10.81% |
| ./ | 3 | 8.11% |
| configs | 2 | 5.41% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| source_code | 17 | 45.95% |
| validation | 15 | 40.54% |
| evidence_runs | 11 | 29.73% |
| ci_workflows | 9 | 24.32% |
| scripts_general | 9 | 24.32% |
| tests | 4 | 10.81% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and sql"
- "and update"
- "contract and"
- "for features"
- "implementation contract"
- "pipeline status"
- "sql view"
- "update documentation"
- "view for"
- "add initial"
Representative paths:
- docs
- src
- sql
- scripts
- .github

Draft Invariants

- INV-01: Candidate matches 26/37 commits. (support: 26/37)
- INV-02: Directory pair docs + src co-occurs in 17/26 matched commits. (support: 17/26)

#### MOD-33 — DIR:src
Epoch: 9

Commit Ranges

- 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..1759c448f2d135d240ea747913d85a3868653b73
- 71072aa465e553a151b4f57ce6fb78e59b5f30e3..201fd6c8465a645b52b08435a1665638b2cfa281
- f09687dd9b6481b0c7d5fc26984ac984db39a269..d9a89c033de344b71b648ff33af27f076c0895d2
- cbb8bfcee27dea9525e43be8b9017d64fbda5bf5..d348c04646de00626c534cdf39d5ee1cae7e8511
- ee46496d262759fcae78902ffc07b4d2ac71282e..597ca8e2c8a774a490342e796ab6da5424fdb003

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| src | 18 | 48.65% |
| docs | 17 | 45.95% |
| sql | 6 | 16.22% |
| .github | 4 | 10.81% |
| scripts | 4 | 10.81% |
| tests | 4 | 10.81% |
| configs | 2 | 5.41% |
| ./ | 1 | 2.70% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| source_code | 18 | 48.65% |
| validation | 12 | 32.43% |
| ci_workflows | 6 | 16.22% |
| evidence_runs | 6 | 16.22% |
| scripts_general | 4 | 10.81% |
| tests | 4 | 10.81% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and update"
- "documentation and"
- "multi day"
- "pipeline status"
- "regime trend"
- "update documentation"
- "validation scripts"
Representative paths:
- src
- docs
- sql
- .github
- scripts

Draft Invariants

- INV-01: Candidate matches 18/37 commits. (support: 18/37)
- INV-02: Directory pair docs + src co-occurs in 17/18 matched commits. (support: 17/18)

#### MOD-34 — TAG:source_code
Epoch: 9

Commit Ranges

- 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..1759c448f2d135d240ea747913d85a3868653b73
- 71072aa465e553a151b4f57ce6fb78e59b5f30e3..201fd6c8465a645b52b08435a1665638b2cfa281
- f09687dd9b6481b0c7d5fc26984ac984db39a269..d9a89c033de344b71b648ff33af27f076c0895d2
- cbb8bfcee27dea9525e43be8b9017d64fbda5bf5..d348c04646de00626c534cdf39d5ee1cae7e8511
- ee46496d262759fcae78902ffc07b4d2ac71282e..597ca8e2c8a774a490342e796ab6da5424fdb003

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| src | 18 | 48.65% |
| docs | 17 | 45.95% |
| sql | 6 | 16.22% |
| .github | 4 | 10.81% |
| scripts | 4 | 10.81% |
| tests | 4 | 10.81% |
| configs | 2 | 5.41% |
| ./ | 1 | 2.70% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| source_code | 18 | 48.65% |
| validation | 12 | 32.43% |
| ci_workflows | 6 | 16.22% |
| evidence_runs | 6 | 16.22% |
| scripts_general | 4 | 10.81% |
| tests | 4 | 10.81% |
| artifacts | 1 | 2.70% |
| contracts | 1 | 2.70% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and update"
- "documentation and"
- "multi day"
- "pipeline status"
- "regime trend"
- "update documentation"
- "validation scripts"
Representative paths:
- src
- docs
- sql
- .github
- scripts

Draft Invariants

- INV-01: Candidate matches 18/37 commits. (support: 18/37)
- INV-02: Directory pair docs + src co-occurs in 17/18 matched commits. (support: 17/18)

#### MOD-35 — TAG:validation
Epoch: 9

Commit Ranges

- 5ddb81c41c2e38ecf1bd0ad1a761c2b0075f6b4a..201fd6c8465a645b52b08435a1665638b2cfa281
- f09687dd9b6481b0c7d5fc26984ac984db39a269..d9a89c033de344b71b648ff33af27f076c0895d2
- bc1782dc944e9eef2089332451a64b6b5f7a8408..bc1782dc944e9eef2089332451a64b6b5f7a8408
- ab9daed3998490f0e456ff188fa55ab1ca685429..ab9daed3998490f0e456ff188fa55ab1ca685429
- c0a56dca5669a44d533917f3fdf798fba5a531fa..c0a56dca5669a44d533917f3fdf798fba5a531fa
- 0197359d49adff54eedae2d3c60e160fe9ba183c..0197359d49adff54eedae2d3c60e160fe9ba183c

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 17 | 45.95% |
| src | 12 | 32.43% |
| scripts | 5 | 13.51% |
| .github | 4 | 10.81% |
| sql | 4 | 10.81% |
| ./ | 1 | 2.70% |
| artifacts | 1 | 2.70% |
| tests | 1 | 2.70% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| validation | 17 | 45.95% |
| source_code | 12 | 32.43% |
| scripts_general | 5 | 13.51% |
| ci_workflows | 4 | 10.81% |
| evidence_runs | 4 | 10.81% |
| artifacts | 1 | 2.70% |
| tests | 1 | 2.70% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "pipeline status"
- "and add"
- "and update"
- "multi day"
- "update documentation"
- "update pipeline"
- "validation scripts"
Representative paths:
- docs
- src
- scripts
- .github
- sql

Draft Invariants

- INV-01: Candidate matches 17/37 commits. (support: 17/37)
- INV-02: Directory pair docs + src co-occurs in 12/17 matched commits. (support: 12/17)

### Epoch 10

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-36 — DIR:docs
Epoch: 10

Commit Ranges

- 88eff122fe893c14902013cedf36c25793e75e8f..88eff122fe893c14902013cedf36c25793e75e8f

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 1 | 100.00% |
| releases | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| releases | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- docs
- releases

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair docs + releases co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-37 — DIR:releases
Epoch: 10

Commit Ranges

- 88eff122fe893c14902013cedf36c25793e75e8f..88eff122fe893c14902013cedf36c25793e75e8f

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 1 | 100.00% |
| releases | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| releases | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- docs
- releases

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair docs + releases co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-38 — TAG:releases
Epoch: 10

Commit Ranges

- 88eff122fe893c14902013cedf36c25793e75e8f..88eff122fe893c14902013cedf36c25793e75e8f

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 1 | 100.00% |
| releases | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| releases | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- docs
- releases

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair docs + releases co-occurs in 1/1 matched commits. (support: 1/1)

### Epoch 11

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-39 — DIR:research
Epoch: 11

Commit Ranges

- f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| research | 8 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| research | 8 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "block range"
- "range intensity"
- "files for"
- "add initial"
- "for block"
- "intensity score"
- "study files"
- "add study"
- "initial files"
- "initial study"
Representative paths:
- research

Draft Invariants

- INV-01: Candidate matches 8/8 commits. (support: 8/8)
- INV-02: Directory research appears in 8/8 matched commits. (support: 8/8)

#### MOD-40 — TAG:research
Epoch: 11

Commit Ranges

- f2f8bd0bbdf3ce7a25eee7a62955602ae24d06d3..336d0eb6edc063b295ac0f30c030e591fd0b0d8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| research | 8 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| research | 8 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "block range"
- "range intensity"
- "files for"
- "add initial"
- "for block"
- "intensity score"
- "study files"
- "add study"
- "initial files"
- "initial study"
Representative paths:
- research

Draft Invariants

- INV-01: Candidate matches 8/8 commits. (support: 8/8)
- INV-02: Directory research appears in 8/8 matched commits. (support: 8/8)

### Epoch 12

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-41 — DIR:sql
Epoch: 12

Commit Ranges

- 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 6 | 85.71% |
| docs | 4 | 57.14% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 6 | 85.71% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and res"
- "dis lid"
- "for dis"
- "lid and"
- "res scores"
- "studies for"
- "and sql"
- "feat add"
- "for path"
- "path evidence"
Representative paths:
- sql
- docs

Draft Invariants

- INV-01: Candidate matches 6/7 commits. (support: 6/7)
- INV-02: Directory pair docs + sql co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-42 — TAG:evidence_runs
Epoch: 12

Commit Ranges

- 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..fb2bbd3b4513e5b61840519dc3053785300a00c2

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 6 | 85.71% |
| docs | 4 | 57.14% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 6 | 85.71% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and res"
- "dis lid"
- "for dis"
- "lid and"
- "res scores"
- "studies for"
- "and sql"
- "feat add"
- "for path"
- "path evidence"
Representative paths:
- sql
- docs

Draft Invariants

- INV-01: Candidate matches 6/7 commits. (support: 6/7)
- INV-02: Directory pair docs + sql co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-43 — CLUSTER:docs|sql
Epoch: 12

Commit Ranges

- 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..0f853613954d252b57104386a6edcdf010c4b52b
- b07313878bb6d92a0425f56fd7c0919144638a2a..b07313878bb6d92a0425f56fd7c0919144638a2a
- fb2bbd3b4513e5b61840519dc3053785300a00c2..fb2bbd3b4513e5b61840519dc3053785300a00c2

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 57.14% |
| sql | 4 | 57.14% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 57.14% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and res"
- "and sql"
- "dis lid"
- "feat add"
- "for dis"
- "for path"
- "lid and"
- "path evidence"
- "res scores"
- "studies for"
Representative paths:
- docs
- sql

Draft Invariants

- INV-01: Candidate matches 4/7 commits. (support: 4/7)
- INV-02: Directory pair docs + sql co-occurs in 4/4 matched commits. (support: 4/4)

#### MOD-44 — DIR:docs
Epoch: 12

Commit Ranges

- 04d95ab73c8d2dbbe4c5e28616aff6d0843ddf2d..0f853613954d252b57104386a6edcdf010c4b52b
- b07313878bb6d92a0425f56fd7c0919144638a2a..b07313878bb6d92a0425f56fd7c0919144638a2a
- fb2bbd3b4513e5b61840519dc3053785300a00c2..fb2bbd3b4513e5b61840519dc3053785300a00c2

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 57.14% |
| sql | 4 | 57.14% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 4 | 57.14% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "and res"
- "and sql"
- "dis lid"
- "feat add"
- "for dis"
- "for path"
- "lid and"
- "path evidence"
- "res scores"
- "studies for"
Representative paths:
- docs
- sql

Draft Invariants

- INV-01: Candidate matches 4/7 commits. (support: 4/7)
- INV-02: Directory pair docs + sql co-occurs in 4/4 matched commits. (support: 4/4)

### Epoch 13

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-45 — CLUSTER:./|.github|.vscode|artifacts|docs|reports|scripts|sql|tests|tetsu
Epoch: 13

Commit Ranges

- 1774ef56bfd2165b8b8e7a83230cd39a1fb46fc8..a512105780ad4af36705294041b10ad3ebbeee78
- d2e816266340a2e57b9432a886c3d9fef230be28..d2e816266340a2e57b9432a886c3d9fef230be28
- 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..19ae34b9980d3914d3a4ea62f5330a80ca364edc
- a67ef074544d1c75e30eb74759418ea197dfb5f0..a67ef074544d1c75e30eb74759418ea197dfb5f0
- d5a9c3694ea11a09563170c9ca59d1670784dae2..83f3d21122c122a44fbd3a85f78d7d4008202c58
- ef3e50e405dfa96d7d63364400ee309746b772e4..66ecada57104a6362a4e936a0ac5fcb768dbdef2
- e25017bd86466fce6308b8dc74f80fbb4382beaa..bf516503e1c796f4baf35d80f1d615e8217e3ba9
- ee6eedeaae948218edeae3b98de8d640036a57ca..ee6eedeaae948218edeae3b98de8d640036a57ca
- 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a
- 35507a0cedbbdc774fd96572154bf2425d27ad2d..3c9fbb1079f710d3c36e69572c61f82e318c18ea
- 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..510823df51a7a5393809dc0b394f851894bda078
- fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..b7b09557b7fea4c0199066df93ff64e591922494
- a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be
- 0cf7aac0e70dc6d758dbca94b0acb4a954a2cc27..064339bb46becb8c9d774441796ae5b8695c2762
- 51f48c227ef69f6ba7a0eb293746265577034fa2..380e199d700cbce7c6304ac96d18ad1626490622
- 536742709ec0420bb521f32b28ef5c84b61ff154..d271e385528ec6bc30132515c4dacb887d5b6db9
- 739ed433c57e17e257745f4072b6c3fd6f0fa335..f5318b3c33952781932b148d44c6909f78972a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 42 | 44.68% |
| sql | 27 | 28.72% |
| docs | 23 | 24.47% |
| scripts | 23 | 24.47% |
| .github | 17 | 18.09% |
| ./ | 10 | 10.64% |
| Tetsu | 6 | 6.38% |
| tests | 5 | 5.32% |
| .vscode | 3 | 3.19% |
| artifacts | 3 | 3.19% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 42 | 44.68% |
| scripts_general | 23 | 24.47% |
| ci_workflows | 17 | 18.09% |
| governance_contracts | 8 | 8.51% |
| repo_maze | 6 | 6.38% |
| validation | 6 | 6.38% |
| tests | 5 | 5.32% |
| operations | 4 | 4.26% |
| artifacts | 3 | 3.19% |
| infra | 2 | 2.13% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "evidence run"
- "automated evidence"
- "path1 automated"
- "path1 evidence"
- "run 20260120"
- "enhance evidence"
- "owenguobadia24s collab"
- "path evidence"
- "and update"
- "run queue"
Representative paths:
- reports
- sql
- docs
- scripts
- .github

Draft Invariants

- INV-01: Candidate matches 60/94 commits. (support: 60/94)
- INV-02: Directory pair reports + sql co-occurs in 27/60 matched commits. (support: 27/60)

#### MOD-46 — DIR:reports
Epoch: 13

Commit Ranges

- a512105780ad4af36705294041b10ad3ebbeee78..d2e816266340a2e57b9432a886c3d9fef230be28
- 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9
- d5a9c3694ea11a09563170c9ca59d1670784dae2..ef3e50e405dfa96d7d63364400ee309746b772e4
- 7cb0896c3c1068a27ebddb89ad36f0397ff06e6d..66ecada57104a6362a4e936a0ac5fcb768dbdef2
- e25017bd86466fce6308b8dc74f80fbb4382beaa..e25017bd86466fce6308b8dc74f80fbb4382beaa
- b092afc564f9339724bb13c9f08315652b03a2fb..bf516503e1c796f4baf35d80f1d615e8217e3ba9
- a5edd1adea92d8c21da2e7eeda181ab15c699d3d..a5edd1adea92d8c21da2e7eeda181ab15c699d3d
- ee6eedeaae948218edeae3b98de8d640036a57ca..ee6eedeaae948218edeae3b98de8d640036a57ca
- 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a
- 35507a0cedbbdc774fd96572154bf2425d27ad2d..35507a0cedbbdc774fd96572154bf2425d27ad2d
- f5064286f8a5e3183328e19c036315b0f66bf2a2..5ca5a325b92f780cf570394a25dcf21ec9b84db9
- f10548b4d300da4fffa4f791131d6603766b5529..3c9fbb1079f710d3c36e69572c61f82e318c18ea
- 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..04e3ece74e421b58ebe09ffebc233c9ad21e7e6f
- fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..edfe1bc01fb97b3595007e079f5a674648dcfb94
- 851fbad324673e97d0f97be4bcc242013e334929..b7b09557b7fea4c0199066df93ff64e591922494
- 359079c5f18d07f71b31872e21ab4adf1a3e9440..359079c5f18d07f71b31872e21ab4adf1a3e9440
- a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be
- 615c7964b8c1a82f1807b3f055cff5e4f602a7a4..316384b2a3c7be3433732b511662390d0057947c
- 53a3c0b9a0ba5c9a506224a338ba3da5ba40e2aa..f5318b3c33952781932b148d44c6909f78972a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 48 | 51.06% |
| sql | 27 | 28.72% |
| scripts | 11 | 11.70% |
| docs | 8 | 8.51% |
| .github | 7 | 7.45% |
| ./ | 6 | 6.38% |
| tests | 3 | 3.19% |
| .vscode | 2 | 2.13% |
| infra | 2 | 2.13% |
| src | 2 | 2.13% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 48 | 51.06% |
| scripts_general | 11 | 11.70% |
| ci_workflows | 7 | 7.45% |
| tests | 3 | 3.19% |
| infra | 2 | 2.13% |
| source_code | 2 | 2.13% |
| validation | 2 | 2.13% |
| claims | 1 | 1.06% |
| governance_contracts | 1 | 1.06% |
| operations | 1 | 1.06% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "evidence run"
- "automated evidence"
- "path1 automated"
- "path1 evidence"
- "run 20260120"
- "run queue"
- "owenguobadia24s collab"
- "collab evidence"
- "enhance evidence"
- "from owenguobadia24s"
Representative paths:
- reports
- sql
- scripts
- docs
- .github

Draft Invariants

- INV-01: Candidate matches 48/94 commits. (support: 48/94)
- INV-02: Directory pair reports + sql co-occurs in 27/48 matched commits. (support: 27/48)

#### MOD-47 — TAG:evidence_runs
Epoch: 13

Commit Ranges

- a512105780ad4af36705294041b10ad3ebbeee78..d2e816266340a2e57b9432a886c3d9fef230be28
- 4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9..4e1826bf2c8b83ec07c5603ad177b0cc17ffa2d9
- d5a9c3694ea11a09563170c9ca59d1670784dae2..ef3e50e405dfa96d7d63364400ee309746b772e4
- 7cb0896c3c1068a27ebddb89ad36f0397ff06e6d..66ecada57104a6362a4e936a0ac5fcb768dbdef2
- e25017bd86466fce6308b8dc74f80fbb4382beaa..e25017bd86466fce6308b8dc74f80fbb4382beaa
- b092afc564f9339724bb13c9f08315652b03a2fb..bf516503e1c796f4baf35d80f1d615e8217e3ba9
- a5edd1adea92d8c21da2e7eeda181ab15c699d3d..a5edd1adea92d8c21da2e7eeda181ab15c699d3d
- ee6eedeaae948218edeae3b98de8d640036a57ca..ee6eedeaae948218edeae3b98de8d640036a57ca
- 4673c7a6e8c6b5b19d6f2986b8f40c9d0ec720fa..26903304ea71a196706c84d7bb1c4babcd3e537a
- 35507a0cedbbdc774fd96572154bf2425d27ad2d..35507a0cedbbdc774fd96572154bf2425d27ad2d
- f5064286f8a5e3183328e19c036315b0f66bf2a2..5ca5a325b92f780cf570394a25dcf21ec9b84db9
- f10548b4d300da4fffa4f791131d6603766b5529..3c9fbb1079f710d3c36e69572c61f82e318c18ea
- 04e3ece74e421b58ebe09ffebc233c9ad21e7e6f..04e3ece74e421b58ebe09ffebc233c9ad21e7e6f
- fe1bccbb1eb8f315f493c4b8e7a3ba3fd940e7f0..edfe1bc01fb97b3595007e079f5a674648dcfb94
- 851fbad324673e97d0f97be4bcc242013e334929..b7b09557b7fea4c0199066df93ff64e591922494
- 359079c5f18d07f71b31872e21ab4adf1a3e9440..359079c5f18d07f71b31872e21ab4adf1a3e9440
- a49f425da9cba5cf7c05f1538848c9f0ebafd0b9..d62806071d873b3a7090de073de3de451421a4be
- 615c7964b8c1a82f1807b3f055cff5e4f602a7a4..316384b2a3c7be3433732b511662390d0057947c
- 53a3c0b9a0ba5c9a506224a338ba3da5ba40e2aa..f5318b3c33952781932b148d44c6909f78972a8e

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 48 | 51.06% |
| sql | 27 | 28.72% |
| scripts | 11 | 11.70% |
| docs | 8 | 8.51% |
| .github | 7 | 7.45% |
| ./ | 6 | 6.38% |
| tests | 3 | 3.19% |
| .vscode | 2 | 2.13% |
| infra | 2 | 2.13% |
| src | 2 | 2.13% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 48 | 51.06% |
| scripts_general | 11 | 11.70% |
| ci_workflows | 7 | 7.45% |
| tests | 3 | 3.19% |
| infra | 2 | 2.13% |
| source_code | 2 | 2.13% |
| validation | 2 | 2.13% |
| claims | 1 | 1.06% |
| governance_contracts | 1 | 1.06% |
| operations | 1 | 1.06% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "evidence run"
- "automated evidence"
- "path1 automated"
- "path1 evidence"
- "run 20260120"
- "run queue"
- "owenguobadia24s collab"
- "collab evidence"
- "enhance evidence"
- "from owenguobadia24s"
Representative paths:
- reports
- sql
- scripts
- docs
- .github

Draft Invariants

- INV-01: Candidate matches 48/94 commits. (support: 48/94)
- INV-02: Directory pair reports + sql co-occurs in 27/48 matched commits. (support: 27/48)

### Epoch 14

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-48 — DIR:.codex
Epoch: 14

Commit Ranges

- 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
- 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .codex | 8 | 88.89% |
| Tetsu | 5 | 55.56% |
| ./ | 3 | 33.33% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| codex_runtime | 8 | 88.89% |
| validation | 6 | 66.67% |
| repo_maze | 5 | 55.56% |
| operations | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "ovc infra"
- "owenguobadia24s collab"
- "audit harness"
- "branch main"
- "index ps1"
Representative paths:
- .codex
- Tetsu
- ./
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 8/9 commits. (support: 8/9)
- INV-02: Directory pair .codex + Tetsu co-occurs in 5/8 matched commits. (support: 5/8)

#### MOD-49 — TAG:codex_runtime
Epoch: 14

Commit Ranges

- 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
- 85cb367082e98ac3a2339ca71c51c1141ed91308..3dc06d8df45105eb06284c476f32243021c2a8b9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .codex | 8 | 88.89% |
| Tetsu | 5 | 55.56% |
| ./ | 3 | 33.33% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| codex_runtime | 8 | 88.89% |
| validation | 6 | 66.67% |
| repo_maze | 5 | 55.56% |
| operations | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "ovc infra"
- "owenguobadia24s collab"
- "audit harness"
- "branch main"
- "index ps1"
Representative paths:
- .codex
- Tetsu
- ./
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 8/9 commits. (support: 8/9)
- INV-02: Directory pair .codex + Tetsu co-occurs in 5/8 matched commits. (support: 5/8)

#### MOD-50 — CLUSTER:./|.codex|tetsu
Epoch: 14

Commit Ranges

- 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
- 85cb367082e98ac3a2339ca71c51c1141ed91308..b19cf71b1d1c48b59e5ba5853e37c33a45688220
- 3dc06d8df45105eb06284c476f32243021c2a8b9..3dc06d8df45105eb06284c476f32243021c2a8b9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .codex | 7 | 77.78% |
| Tetsu | 5 | 55.56% |
| ./ | 3 | 33.33% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| codex_runtime | 7 | 77.78% |
| repo_maze | 5 | 55.56% |
| validation | 5 | 55.56% |
| operations | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "ovc infra"
- "owenguobadia24s collab"
- "audit harness"
- "branch main"
- "merge branch"
Representative paths:
- .codex
- Tetsu
- ./
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 7/9 commits. (support: 7/9)
- INV-02: Directory pair .codex + Tetsu co-occurs in 5/7 matched commits. (support: 5/7)

#### MOD-51 — DIR:tetsu
Epoch: 14

Commit Ranges

- ef2dd2f4067b60028788b439394172e92d9d98ef..b19cf71b1d1c48b59e5ba5853e37c33a45688220
- 3dc06d8df45105eb06284c476f32243021c2a8b9..3dc06d8df45105eb06284c476f32243021c2a8b9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| Tetsu | 6 | 66.67% |
| .codex | 5 | 55.56% |
| ./ | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| repo_maze | 6 | 66.67% |
| codex_runtime | 5 | 55.56% |
| validation | 3 | 33.33% |
| operations | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "branch main"
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "merge branch"
- "ovc infra"
- "owenguobadia24s collab"
- "update workspace"
Representative paths:
- Tetsu
- .codex
- ./

Draft Invariants

- INV-01: Candidate matches 6/9 commits. (support: 6/9)
- INV-02: Directory pair .codex + Tetsu co-occurs in 5/6 matched commits. (support: 5/6)

#### MOD-52 — TAG:repo_maze
Epoch: 14

Commit Ranges

- ef2dd2f4067b60028788b439394172e92d9d98ef..b19cf71b1d1c48b59e5ba5853e37c33a45688220
- 3dc06d8df45105eb06284c476f32243021c2a8b9..3dc06d8df45105eb06284c476f32243021c2a8b9

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| Tetsu | 6 | 66.67% |
| .codex | 5 | 55.56% |
| ./ | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| repo_maze | 6 | 66.67% |
| codex_runtime | 5 | 55.56% |
| validation | 3 | 33.33% |
| operations | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "branch main"
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "merge branch"
- "ovc infra"
- "owenguobadia24s collab"
- "update workspace"
Representative paths:
- Tetsu
- .codex
- ./

Draft Invariants

- INV-01: Candidate matches 6/9 commits. (support: 6/9)
- INV-02: Directory pair .codex + Tetsu co-occurs in 5/6 matched commits. (support: 5/6)

#### MOD-53 — TAG:validation
Epoch: 14

Commit Ranges

- 4c245c6e90eec04733739f8879d1868e977f0257..44403d3f47251c870c548e726a596384e30ca426
- 85cb367082e98ac3a2339ca71c51c1141ed91308..731fe267ee2796446931564fb779fc52545878bf
- f758bd189a8b8b7a0b13baed703a4014b29748d5..f758bd189a8b8b7a0b13baed703a4014b29748d5

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .codex | 6 | 66.67% |
| ./ | 3 | 33.33% |
| Tetsu | 3 | 33.33% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| codex_runtime | 6 | 66.67% |
| validation | 6 | 66.67% |
| operations | 3 | 33.33% |
| repo_maze | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "ovc infra"
- "owenguobadia24s collab"
- "audit harness"
- "branch main"
- "merge branch"
Representative paths:
- .codex
- ./
- Tetsu
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 6/9 commits. (support: 6/9)
- INV-02: Directory pair ./ + .codex co-occurs in 3/6 matched commits. (support: 3/6)

### Epoch 15

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-54 — DIR:reports
Epoch: 15

Commit Ranges

- 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 2 | 66.67% |
| sql | 2 | 66.67% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 2 | 66.67% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "path1 evidence"
Representative paths:
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 2/3 commits. (support: 2/3)
- INV-02: Directory pair reports + sql co-occurs in 2/2 matched commits. (support: 2/2)

#### MOD-55 — DIR:sql
Epoch: 15

Commit Ranges

- 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 2 | 66.67% |
| sql | 2 | 66.67% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 2 | 66.67% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "path1 evidence"
Representative paths:
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 2/3 commits. (support: 2/3)
- INV-02: Directory pair reports + sql co-occurs in 2/2 matched commits. (support: 2/2)

#### MOD-56 — TAG:evidence_runs
Epoch: 15

Commit Ranges

- 11bba2ccaf601e48416c0558bd01328fd8ab33b3..956982dbb26f1db70741c3b2a207d1e65277afd1

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 2 | 66.67% |
| sql | 2 | 66.67% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 2 | 66.67% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "path1 evidence"
Representative paths:
- reports
- sql

Draft Invariants

- INV-01: Candidate matches 2/3 commits. (support: 2/3)
- INV-02: Directory pair reports + sql co-occurs in 2/2 matched commits. (support: 2/2)

### Epoch 16

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-57 — CLUSTER:./|.codex|.github|_archive|_quarantine|docs|infra|reports|scripts|sql|src|tools
Epoch: 16

Commit Ranges

- 02fc2accfe43f534e2cc305a216679be5e2a0b52..39696066e87f82b694bf4f20905f0f3ea3c9cce2
- 456567ea4a3a64b3a374152955b1ba150628216a..456567ea4a3a64b3a374152955b1ba150628216a
- 34e45abaa3e1214689e2348e295c76090f279a6c..07022ac03513f1191f0bc192d8979d5318801c3f
- 8452511e7ae16af73801df8db9137a2fb429c466..8452511e7ae16af73801df8db9137a2fb429c466
- 9267725acf1cb687ad543188a75076013f29b0c0..7021c84d722a6782d032dbeccfccc8aa81bd3353

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| sql | 7 | 28.00% |
| ./ | 6 | 24.00% |
| reports | 6 | 24.00% |
| tools | 6 | 24.00% |
| _quarantine | 4 | 16.00% |
| docs | 4 | 16.00% |
| src | 4 | 16.00% |
| .codex | 3 | 12.00% |
| .github | 3 | 12.00% |
| _archive | 3 | 12.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 7 | 28.00% |
| validation | 7 | 28.00% |
| source_code | 4 | 16.00% |
| ci_workflows | 3 | 12.00% |
| codex_runtime | 3 | 12.00% |
| governance_contracts | 3 | 12.00% |
| infra | 3 | 12.00% |
| scripts_general | 3 | 12.00% |
| tools_general | 3 | 12.00% |
| control_panel | 2 | 8.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "path1 evidence"
- "branch main"
- "collab ovc"
- "com owenguobadia24s"
- "github com"
- "https github"
- "main https"
- "merge branch"
- "ovc infra"
- "owenguobadia24s collab"
Representative paths:
- sql
- ./
- reports
- tools
- _quarantine

Draft Invariants

- INV-01: Candidate matches 11/25 commits. (support: 11/25)
- INV-02: Directory pair reports + sql co-occurs in 6/11 matched commits. (support: 6/11)

#### MOD-58 — DIR:tools
Epoch: 16

Commit Ranges

- 02fc2accfe43f534e2cc305a216679be5e2a0b52..02fc2accfe43f534e2cc305a216679be5e2a0b52
- 39696066e87f82b694bf4f20905f0f3ea3c9cce2..39696066e87f82b694bf4f20905f0f3ea3c9cce2
- 456567ea4a3a64b3a374152955b1ba150628216a..456567ea4a3a64b3a374152955b1ba150628216a
- a4f56d59989f53af9d204a2589f11abf523a6e7d..a4f56d59989f53af9d204a2589f11abf523a6e7d
- 3b73583bcc60a6f93d2aa437188be998f6f50551..3b73583bcc60a6f93d2aa437188be998f6f50551
- 8f660b20cd1d0df1780e10e7b52efe7564868719..8452511e7ae16af73801df8db9137a2fb429c466
- 71cfd9c1f982dc1fa96fd36f12406f0cfe6dddf4..9fa7d15fbb1433fb1cdb88d6ff0f7f2012dd3fe1
- 9267725acf1cb687ad543188a75076013f29b0c0..9267725acf1cb687ad543188a75076013f29b0c0

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| tools | 11 | 44.00% |
| ./ | 4 | 16.00% |
| .codex | 3 | 12.00% |
| scripts | 3 | 12.00% |
| sql | 3 | 12.00% |
| src | 3 | 12.00% |
| .github | 2 | 8.00% |
| _archive | 2 | 8.00% |
| _quarantine | 2 | 8.00% |
| docs | 2 | 8.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| control_panel | 6 | 24.00% |
| validation | 5 | 20.00% |
| tools_general | 4 | 16.00% |
| codex_runtime | 3 | 12.00% |
| evidence_runs | 3 | 12.00% |
| scripts_general | 3 | 12.00% |
| source_code | 3 | 12.00% |
| ci_workflows | 2 | 8.00% |
| governance_contracts | 2 | 8.00% |
| infra | 2 | 8.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "branch main"
- "collab ovc"
- "com owenguobadia24s"
- "control panel"
- "github com"
- "https github"
- "main https"
- "merge branch"
- "ovc infra"
- "owenguobadia24s collab"
Representative paths:
- tools
- ./
- .codex
- scripts
- sql

Draft Invariants

- INV-01: Candidate matches 11/25 commits. (support: 11/25)
- INV-02: Directory pair ./ + tools co-occurs in 4/11 matched commits. (support: 4/11)

### Epoch 17

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-59 — DIR:./
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-60 — DIR:.github
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-61 — DIR:.vscode
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-62 — DIR:artifacts
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-63 — DIR:docs
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-64 — DIR:scripts
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-65 — DIR:tests
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-66 — DIR:tools
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-67 — TAG:artifacts
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-68 — TAG:catalogs
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-69 — TAG:ci_workflows
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-70 — TAG:governance_contracts
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-71 — TAG:governance_tooling
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-72 — TAG:tests
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

#### MOD-73 — TAG:tools_general
Epoch: 17

Commit Ranges

- ff1564dd8e4cd61b5bbc76db3aebbba48852abdb..ff1564dd8e4cd61b5bbc76db3aebbba48852abdb

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| ./ | 1 | 100.00% |
| .github | 1 | 100.00% |
| .vscode | 1 | 100.00% |
| artifacts | 1 | 100.00% |
| docs | 1 | 100.00% |
| scripts | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| artifacts | 1 | 100.00% |
| catalogs | 1 | 100.00% |
| ci_workflows | 1 | 100.00% |
| governance_contracts | 1 | 100.00% |
| governance_tooling | 1 | 100.00% |
| tests | 1 | 100.00% |
| tools_general | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "change"
- "classification"
Representative paths:
- ./
- .github
- .vscode
- artifacts
- docs

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory pair ./ + .github co-occurs in 1/1 matched commits. (support: 1/1)

### Epoch 18

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-74 — DIR:.github
Epoch: 18

Commit Ranges

- 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .github | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| ci_workflows | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- .github

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory .github appears in 1/1 matched commits. (support: 1/1)

#### MOD-75 — TAG:ci_workflows
Epoch: 18

Commit Ranges

- 2a68adf9762ff6910ea1883a6d5cf1f999cf7dae..2a68adf9762ff6910ea1883a6d5cf1f999cf7dae

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| .github | 1 | 100.00% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| ci_workflows | 1 | 100.00% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "none"
Representative paths:
- .github

Draft Invariants

- INV-01: Candidate matches 1/1 commits. (support: 1/1)
- INV-02: Directory .github appears in 1/1 matched commits. (support: 1/1)

### Epoch 19

Epoch Boundary Source: coerced(start_hash/end_hash)

#### MOD-76 — DIR:scripts
Epoch: 19

Commit Ranges

- 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 6 | 66.67% |
| tests | 4 | 44.44% |
| docs | 3 | 33.33% |
| ./ | 2 | 22.22% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| governance_tooling | 6 | 66.67% |
| tests | 4 | 44.44% |
| catalogs | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
- "overlay builder"
- "path resolution"
- "repo root"
Representative paths:
- scripts
- tests
- docs
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 6/9 commits. (support: 6/9)
- INV-02: Directory pair scripts + tests co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-77 — TAG:governance_tooling
Epoch: 19

Commit Ranges

- 8950c6cb233d58406ddaf20247d0367948bab316..52d4a177ba43263c8817db27b6634b073b4e5015

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 6 | 66.67% |
| tests | 4 | 44.44% |
| docs | 3 | 33.33% |
| ./ | 2 | 22.22% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| governance_tooling | 6 | 66.67% |
| tests | 4 | 44.44% |
| catalogs | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
- "overlay builder"
- "path resolution"
- "repo root"
Representative paths:
- scripts
- tests
- docs
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 6/9 commits. (support: 6/9)
- INV-02: Directory pair scripts + tests co-occurs in 4/6 matched commits. (support: 4/6)

#### MOD-78 — CLUSTER:docs|scripts|tests
Epoch: 19

Commit Ranges

- 8950c6cb233d58406ddaf20247d0367948bab316..3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2
- d50080c7197abd03ed944af08d21f64cbccbd65e..d50080c7197abd03ed944af08d21f64cbccbd65e
- 52d4a177ba43263c8817db27b6634b073b4e5015..52d4a177ba43263c8817db27b6634b073b4e5015

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 4 | 44.44% |
| tests | 4 | 44.44% |
| docs | 3 | 33.33% |
| ./ | 1 | 11.11% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| governance_tooling | 4 | 44.44% |
| tests | 4 | 44.44% |
| catalogs | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
Representative paths:
- scripts
- tests
- docs
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair scripts + tests co-occurs in 4/4 matched commits. (support: 4/4)

#### MOD-79 — DIR:docs
Epoch: 19

Commit Ranges

- 3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2..3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2
- d50080c7197abd03ed944af08d21f64cbccbd65e..d50080c7197abd03ed944af08d21f64cbccbd65e
- 52d4a177ba43263c8817db27b6634b073b4e5015..5053bbfdba14990f4017d22ea8cead36e0adb94f

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 44.44% |
| scripts | 3 | 33.33% |
| tests | 3 | 33.33% |
| ./ | 1 | 11.11% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| catalogs | 4 | 44.44% |
| governance_tooling | 3 | 33.33% |
| tests | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
Representative paths:
- docs
- scripts
- tests
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair docs + scripts co-occurs in 3/4 matched commits. (support: 3/4)

#### MOD-80 — DIR:tests
Epoch: 19

Commit Ranges

- 8950c6cb233d58406ddaf20247d0367948bab316..3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2
- d50080c7197abd03ed944af08d21f64cbccbd65e..d50080c7197abd03ed944af08d21f64cbccbd65e
- 52d4a177ba43263c8817db27b6634b073b4e5015..52d4a177ba43263c8817db27b6634b073b4e5015

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 4 | 44.44% |
| tests | 4 | 44.44% |
| docs | 3 | 33.33% |
| ./ | 1 | 11.11% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| governance_tooling | 4 | 44.44% |
| tests | 4 | 44.44% |
| catalogs | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
Representative paths:
- scripts
- tests
- docs
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair scripts + tests co-occurs in 4/4 matched commits. (support: 4/4)

#### MOD-81 — TAG:catalogs
Epoch: 19

Commit Ranges

- 3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2..3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2
- d50080c7197abd03ed944af08d21f64cbccbd65e..d50080c7197abd03ed944af08d21f64cbccbd65e
- 52d4a177ba43263c8817db27b6634b073b4e5015..5053bbfdba14990f4017d22ea8cead36e0adb94f

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| docs | 4 | 44.44% |
| scripts | 3 | 33.33% |
| tests | 3 | 33.33% |
| ./ | 1 | 11.11% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| catalogs | 4 | 44.44% |
| governance_tooling | 3 | 33.33% |
| tests | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
Representative paths:
- docs
- scripts
- tests
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair docs + scripts co-occurs in 3/4 matched commits. (support: 3/4)

#### MOD-82 — TAG:tests
Epoch: 19

Commit Ranges

- 8950c6cb233d58406ddaf20247d0367948bab316..3ee57f59d634db7bb5b1ebb8f642444ee1d7fca2
- d50080c7197abd03ed944af08d21f64cbccbd65e..d50080c7197abd03ed944af08d21f64cbccbd65e
- 52d4a177ba43263c8817db27b6634b073b4e5015..52d4a177ba43263c8817db27b6634b073b4e5015

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| scripts | 4 | 44.44% |
| tests | 4 | 44.44% |
| docs | 3 | 33.33% |
| ./ | 1 | 11.11% |
| reports | 1 | 11.11% |
| sql | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| governance_tooling | 4 | 44.44% |
| tests | 4 | 44.44% |
| catalogs | 3 | 33.33% |
| evidence_runs | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "deterministic hardening"
Representative paths:
- scripts
- tests
- docs
- ./
- reports

Draft Invariants

- INV-01: Candidate matches 4/9 commits. (support: 4/9)
- INV-02: Directory pair scripts + tests co-occurs in 4/4 matched commits. (support: 4/4)

#### MOD-83 — CLUSTER:reports|sql
Epoch: 19

Commit Ranges

- 7d92461d83ba71f8df87d28a130a7279c86d0e62..7d92461d83ba71f8df87d28a130a7279c86d0e62
- 52d4a177ba43263c8817db27b6634b073b4e5015..52d4a177ba43263c8817db27b6634b073b4e5015
- cfd91a7d80267d717ab519102b1ce7956361503c..cfd91a7d80267d717ab519102b1ce7956361503c

Dominant Directories

| Directory | Count | % |
| --- | ---: | ---: |
| reports | 3 | 33.33% |
| sql | 3 | 33.33% |
| ./ | 1 | 11.11% |
| docs | 1 | 11.11% |
| scripts | 1 | 11.11% |
| tests | 1 | 11.11% |

Dominant Tags

| Tag | Count | % |
| --- | ---: | ---: |
| evidence_runs | 3 | 33.33% |
| catalogs | 1 | 11.11% |
| governance_tooling | 1 | 11.11% |
| tests | 1 | 11.11% |

Purpose (Evidence-Only)

Repeated subject phrases:
- "path1 evidence"
Representative paths:
- reports
- sql
- ./
- docs
- scripts

Draft Invariants

- INV-01: Candidate matches 3/9 commits. (support: 3/9)
- INV-02: Directory pair reports + sql co-occurs in 3/3 matched commits. (support: 3/3)

## 4. Visual Summary (Digestible, Not Decorative)

| Module | Directories | Tags |
| --- | --- | --- |
| MOD-01 | tests, tools | tests, tools_general |
| MOD-02 | tests, tools | tests, tools_general |
| MOD-03 | tools, tests | tools_general, tests |
| MOD-04 | tools, tests | tools_general, tests |
| MOD-05 | infra | infra |
| MOD-06 | infra | infra |
| MOD-07 | docs, infra, .github | infra, ci_workflows, source_code |
| MOD-08 | infra, docs, .github | infra, ci_workflows, source_code |
| MOD-09 | infra, docs, .github | infra, ci_workflows, source_code |
| MOD-10 | docs, infra, .github | infra, ci_workflows, source_code |
| MOD-11 | sql, ./, contracts | evidence_runs, contracts, specs |
| MOD-12 | sql, ./, contracts | evidence_runs, contracts, specs |
| MOD-13 | docs, infra, tests | infra, tests, validation |
| MOD-14 | infra, tests, docs | infra, tests, validation |
| MOD-15 | infra, tests, docs | infra, tests, validation |
| MOD-16 | docs, infra, pine | infra, pine, tests |
| MOD-17 | pine, docs, infra | pine, infra, tests |
| MOD-18 | tests, infra, docs | tests, infra, validation |
| MOD-19 | pine, docs, infra | pine, infra, tests |
| MOD-20 | tests, infra, docs | tests, infra, validation |
| MOD-21 | docs, contracts, sql | contracts, evidence_runs, scripts_general |
| MOD-22 | docs, contracts, sql | contracts, evidence_runs, ci_workflows |
| MOD-23 | scripts, ./, docs | scripts_general, evidence_runs, ci_workflows |
| MOD-24 | sql, docs, contracts | evidence_runs, contracts, scripts_general |
| MOD-25 | sql, docs, contracts | evidence_runs, contracts, scripts_general |
| MOD-26 | scripts, ./, docs | scripts_general, evidence_runs, ci_workflows |
| MOD-27 | pine, sql | evidence_runs, pine |
| MOD-28 | pine, sql | evidence_runs, pine |
| MOD-29 | pine, sql | evidence_runs, pine |
| MOD-30 | pine, sql | evidence_runs, pine |
| MOD-31 | docs, src, sql | source_code, validation, evidence_runs |
| MOD-32 | docs, src, sql | source_code, validation, evidence_runs |
| MOD-33 | src, docs, sql | source_code, validation, ci_workflows |
| MOD-34 | src, docs, sql | source_code, validation, ci_workflows |
| MOD-35 | docs, src, scripts | validation, source_code, scripts_general |
| MOD-36 | docs, releases | releases |
| MOD-37 | docs, releases | releases |
| MOD-38 | docs, releases | releases |
| MOD-39 | research | research |
| MOD-40 | research | research |
| MOD-41 | sql, docs | evidence_runs |
| MOD-42 | sql, docs | evidence_runs |
| MOD-43 | docs, sql | evidence_runs |
| MOD-44 | docs, sql | evidence_runs |
| MOD-45 | reports, sql, docs | evidence_runs, scripts_general, ci_workflows |
| MOD-46 | reports, sql, scripts | evidence_runs, scripts_general, ci_workflows |
| MOD-47 | reports, sql, scripts | evidence_runs, scripts_general, ci_workflows |
| MOD-48 | .codex, Tetsu, ./ | codex_runtime, validation, repo_maze |
| MOD-49 | .codex, Tetsu, ./ | codex_runtime, validation, repo_maze |
| MOD-50 | .codex, Tetsu, ./ | codex_runtime, repo_maze, validation |
| MOD-51 | Tetsu, .codex, ./ | repo_maze, codex_runtime, validation |
| MOD-52 | Tetsu, .codex, ./ | repo_maze, codex_runtime, validation |
| MOD-53 | .codex, ./, Tetsu | codex_runtime, validation, operations |
| MOD-54 | reports, sql | evidence_runs |
| MOD-55 | reports, sql | evidence_runs |
| MOD-56 | reports, sql | evidence_runs |
| MOD-57 | sql, ./, reports | evidence_runs, validation, source_code |
| MOD-58 | tools, ./, .codex | control_panel, validation, tools_general |
| MOD-59 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-60 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-61 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-62 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-63 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-64 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-65 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-66 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-67 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-68 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-69 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-70 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-71 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-72 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-73 | ./, .github, .vscode | artifacts, catalogs, ci_workflows |
| MOD-74 | .github | ci_workflows |
| MOD-75 | .github | ci_workflows |
| MOD-76 | scripts, tests, docs | governance_tooling, tests, catalogs |
| MOD-77 | scripts, tests, docs | governance_tooling, tests, catalogs |
| MOD-78 | scripts, tests, docs | governance_tooling, tests, catalogs |
| MOD-79 | docs, scripts, tests | catalogs, governance_tooling, tests |
| MOD-80 | scripts, tests, docs | governance_tooling, tests, catalogs |
| MOD-81 | docs, scripts, tests | catalogs, governance_tooling, tests |
| MOD-82 | scripts, tests, docs | governance_tooling, tests, catalogs |
| MOD-83 | reports, sql, ./ | evidence_runs, catalogs, governance_tooling |
