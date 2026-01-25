# Canvas Layout Specification

**Canvas Title:** OVC Atlas — Repo Graph Family
**Generated:** 2026-01-25

---

## Overview

The canvas organizes all OVC graphs into explorable regions arranged left-to-right following data flow:

```
[External] → [Option A] → [Option B] → [Option C] → [Option D] → [QA Overlay]
```

A **Legend Dock** at bottom-left provides reference material.
A **Controls / How to Use** note at top-left provides navigation guidance.

---

## Region Layout (Left to Right)

### Region 1: CONTROLS (Top-Left Corner)
**Position:** x: 0, y: 0
**Size:** 400 x 200

Contents:
- Text card: "HOW TO USE THIS CANVAS"
- Navigation instructions
- Link to `00_README__GRAPH_ATLAS.md`

---

### Region 2: EXTERNAL (Left Edge)
**Position:** x: 0, y: 250
**Size:** 300 x 400

Contents:
- Index card: "EXTERNAL SOURCES"
- Description of TradingView, OANDA, R2, Notion

Graphs embedded: None (sources are entry points)

---

### Region 3: OPTION A (Column 1)
**Position:** x: 350, y: 250
**Size:** 500 x 600

Contents:
- Index card: "OPTION A — Canonical Ingest"
- Scope: Raw ingest, C0/C1 foundations, canonical tables

Graphs embedded:
1. `10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md` (shared)
2. `20_INTERNAL_PIPELINES/GRAPH_20__OPT_A__PIPELINE.md`

---

### Region 4: OPTION B (Column 2)
**Position:** x: 900, y: 250
**Size:** 500 x 600

Contents:
- Index card: "OPTION B — Derived Features"
- Scope: C1/C2/C3 computations, registries, trajectory families

Graphs embedded:
1. `20_INTERNAL_PIPELINES/GRAPH_21__OPT_B__PIPELINE.md`
2. `50_STORES_TOPOLOGY/GRAPH_50__NEON_SCHEMA_TOPOLOGY.md` (shared)

---

### Region 5: OPTION C (Column 3)
**Position:** x: 1450, y: 250
**Size:** 500 x 600

Contents:
- Index card: "OPTION C — Outcomes"
- Scope: Labels, outcome definitions, backtests

Graphs embedded:
1. `20_INTERNAL_PIPELINES/GRAPH_22__OPT_C__PIPELINE.md`

---

### Region 6: OPTION D (Column 4)
**Position:** x: 2000, y: 250
**Size:** 500 x 600

Contents:
- Index card: "OPTION D — Paths / Bridge"
- Scope: Path1 workflows, reports, evidence packs, integrations

Graphs embedded:
1. `20_INTERNAL_PIPELINES/GRAPH_23__OPT_D__PIPELINE.md`
2. `40_ARTIFACTS_VALIDATION/GRAPH_40__ARTIFACT_LIFECYCLE.md`
3. `50_STORES_TOPOLOGY/GRAPH_51__EXTERNAL_STORES.md`

---

### Region 7: QA OVERLAY (Right Edge)
**Position:** x: 2550, y: 250
**Size:** 600 x 700

Contents:
- Index card: "QA — Validation, Governance, Enforcement"
- Scope: Tests, validation harness, contracts, doctrine

Graphs embedded:
1. `10_OPTION_FLOW/GRAPH_11__OVERVIEW__QA_GATES.md`
2. `10_OPTION_FLOW/GRAPH_12__OVERVIEW__ORCHESTRATION.md`
3. `20_INTERNAL_PIPELINES/GRAPH_24__QA__PIPELINE.md`
4. `30_CONTRACTS_ENFORCEMENT/GRAPH_30__CONTRACTS_MAP.md`
5. `30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md`
6. `40_ARTIFACTS_VALIDATION/GRAPH_41__VALIDATION_CHAIN.md`

---

### Region 8: LEGEND DOCK (Bottom-Left)
**Position:** x: 0, y: 900
**Size:** 400 x 300

Contents:
- Index card: "LEGENDS & REFERENCE"
- Link to `90_LEGENDS/LEGEND_MASTER.md`
- Link to `90_LEGENDS/LEGEND_PER_GRAPH.md`

---

## Card Specifications

### Index Cards (Text)
Each region has one index card with:
- Region title (bold)
- 1-2 sentence scope description
- List of embedded graph files

### File Cards (Embedded)
Each graph is embedded as a file card pointing to:
- Relative path: `./10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md`
- Obsidian will render Mermaid blocks inline

---

## Canvas Grid Summary

| Region | X | Y | Width | Height | Cards |
|--------|---|---|-------|--------|-------|
| CONTROLS | 0 | 0 | 400 | 200 | 1 text |
| EXTERNAL | 0 | 250 | 300 | 400 | 1 text |
| OPTION A | 350 | 250 | 500 | 600 | 1 text + 2 file |
| OPTION B | 900 | 250 | 500 | 600 | 1 text + 2 file |
| OPTION C | 1450 | 250 | 500 | 600 | 1 text + 1 file |
| OPTION D | 2000 | 250 | 500 | 600 | 1 text + 3 file |
| QA OVERLAY | 2550 | 250 | 600 | 700 | 1 text + 6 file |
| LEGEND DOCK | 0 | 900 | 400 | 300 | 1 text + 2 file |

**Total Cards:** 8 index cards + 17 file cards = 25 cards

---

## Edge Connections on Canvas

The canvas may include edges connecting regions to show data flow:
- EXTERNAL → OPTION A (TradingView/OANDA input)
- OPTION A → OPTION B (canonical → derived)
- OPTION B → OPTION C (derived → outcomes)
- OPTION C → OPTION D (outcomes → evidence)
- QA OVERLAY -.-> all regions (validation overlay)

These edges are optional visual aids and do not replace the Mermaid graph edges.

---

*End of Canvas Layout Specification*
