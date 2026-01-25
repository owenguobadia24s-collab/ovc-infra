# OVC Graph Atlas — README

**Status:** CANONICAL VISUALIZATION
**Generated:** 2026-01-25
**Authority:** Descriptive only. Does not alter system semantics.

---

## Purpose

The OVC Graph Atlas provides a navigable, explorable visualization of the OVC repository structure organized around the **5 Options** (A, B, C, D, QA). Each graph answers a specific question about the system.

**This atlas is DESCRIPTIVE, not PRESCRIPTIVE.**
- Graphs reflect what EXISTS in the repository
- Implied/unimplemented relationships are marked with dashed lines
- No graph should be used to justify adding new components

---

## How to Open the Canvas

1. Open Obsidian with this vault (`Tetsu/`)
2. Navigate to `OVC_REPO_MAZE/15_REPO_GRAPHS/`
3. Open `02_CANVAS__OVC_ATLAS.canvas`
4. Use Obsidian's canvas navigation (pan/zoom) to explore regions

Alternatively, view individual graphs as standalone markdown files with Mermaid rendering.

---

## Index of All Graphs by Folder

### 10_OPTION_FLOW/ — Data Flow Overview
| File | Graph Question |
|------|----------------|
| `GRAPH_10__OVERVIEW__DATA_FLOW.md` | How does data flow from External → A → B → C → D? |
| `GRAPH_11__OVERVIEW__QA_GATES.md` | Where does QA validation intercept and enforce? |
| `GRAPH_12__OVERVIEW__ORCHESTRATION.md` | Which workflows/scripts trigger which option processes? |

### 20_INTERNAL_PIPELINES/ — Per-Option Pipelines
| File | Graph Question |
|------|----------------|
| `GRAPH_20__OPT_A__PIPELINE.md` | What are Option A's ingest pipelines and outputs? |
| `GRAPH_21__OPT_B__PIPELINE.md` | What are Option B's derived compute pipelines and outputs? |
| `GRAPH_22__OPT_C__PIPELINE.md` | What are Option C's outcomes pipelines and outputs? |
| `GRAPH_23__OPT_D__PIPELINE.md` | What are Option D's Path1/bridge pipelines and outputs? |
| `GRAPH_24__QA__PIPELINE.md` | What are QA's validation pipelines and outputs? |

### 30_CONTRACTS_ENFORCEMENT/ — Contract Layer
| File | Graph Question |
|------|----------------|
| `GRAPH_30__CONTRACTS_MAP.md` | How are contracts organized and related? |
| `GRAPH_31__ENFORCEMENT_POINTS.md` | Where are contracts validated in the system? |

### 40_ARTIFACTS_VALIDATION/ — Artifact Lifecycle
| File | Graph Question |
|------|----------------|
| `GRAPH_40__ARTIFACT_LIFECYCLE.md` | How do artifacts flow from runs to evidence packs to reports? |
| `GRAPH_41__VALIDATION_CHAIN.md` | How does validation produce audit artifacts and verification reports? |

### 50_STORES_TOPOLOGY/ — Data Stores
| File | Graph Question |
|------|----------------|
| `GRAPH_50__NEON_SCHEMA_TOPOLOGY.md` | What tables/views exist in Neon and how are they related? |
| `GRAPH_51__EXTERNAL_STORES.md` | What external stores (R2, Notion) exist and how are they accessed? |

### 90_LEGENDS/ — Reference Material
| File | Purpose |
|------|---------|
| `LEGEND_MASTER.md` | Master lookup: node ID → full path, Option, category |
| `LEGEND_PER_GRAPH.md` | Per-graph node ID listings |

---

## Graph Conventions

### Node ID Format
All nodes use short IDs (e.g., `A_WORKER`, `B_C1`, `QA_TESTS`). Full paths are in `90_LEGENDS/`.

### Edge Types
| Edge Style | Meaning |
|------------|---------|
| Solid arrow `-->` | Canonical data flow (implemented) |
| Dashed arrow `-.->` | Implied/not-implemented OR validation overlay |
| Dotted `···` | Governance/policy relationship |

### Status Markers
| Marker | Meaning |
|--------|---------|
| `(DORMANT)` | Workflow/script exists but has no schedule or is never invoked |
| `(NOT INVOKED)` | Code exists but no workflow calls it |
| `(UNVERIFIED)` | State cannot be verified from repo alone |
| `(IMPLIED)` | Relationship inferred but not explicit in code |

### Styling Classes
| Class | Color | Meaning |
|-------|-------|---------|
| `canonical` | Green | Canonical/authoritative component |
| `supporting` | Orange | Supporting/secondary component |
| `experimental` | Red dashed | Experimental/not production |
| `qaStyle` | Purple | QA/validation component |
| `external` | Blue | External system/source |

---

## Strict Note: Graphs Are Descriptive Only

**DO NOT:**
- Use graphs to argue for adding new components
- Treat implied relationships as canonical
- Modify code based on graph layout preferences

**DO:**
- Use graphs to understand existing structure
- Verify graph accuracy against actual files
- Report discrepancies as issues

---

## UNPLACED / AMBIGUOUS ITEMS

The following items from the original Graph 1/2/3 could not be cleanly placed in the refactored structure:

| Item | Source | Issue |
|------|--------|-------|
| `pine/` folder | Graph 2 (Option D) | External tooling, not part of pipeline flow |
| `releases/` folder | QA Map | Single file, unclear integration |
| `CLAIMS/` folder | QA Map | Unique structure, not part of standard flow |
| `specs/` (top-level) | QA Map | Possibly empty/duplicate of `docs/specs/` |
| `.github/workflows/main.yml` | QA Map | Purpose unclear, name too generic |

These items are documented but not visualized in the main graph family.

---

## Sources of Truth

All graphs derive from:
- `docs/REPO_MAP/OPT_A__ORG_MAP_DRAFT.md`
- `docs/REPO_MAP/OPT_B__ORG_MAP_DRAFT.md`
- `docs/REPO_MAP/OPT_C__ORG_MAP_DRAFT.md`
- `docs/REPO_MAP/OPT_D__ORG_MAP_DRAFT.md`
- `docs/REPO_MAP/QA__ORG_MAP_DRAFT.md`
- `docs/REPO_MAP/CATEGORY_PROCESS_APPENDIX_DRAFT.md`

---

*End of Graph Atlas README*
