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

## Graph Size Notes

The following graphs exceed the 25-node preference due to dense, cross-cutting coverage:
- `GRAPH_23__OPT_D__PIPELINE.md` (Path1 breadth + reporting outputs)
- `GRAPH_24__QA__PIPELINE.md` (test + validation inventory)
- `GRAPH_40__ARTIFACT_LIFECYCLE.md` (artifact catalog is exhaustive by design)
- `GRAPH_41__VALIDATION_CHAIN.md` (validation + verification chain)

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
| `ovc_cfg.threshold_packs` naming | Option B map vs SQL | Docs use plural; SQL defines `ovc_cfg.threshold_pack` |

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

## DRIFT-DETECTION PROTOCOL

This section defines how the OVC Graph Atlas is used as an **invariant** for repository structure, and how drift between graphs and implementation is detected and resolved.

### A. What Constitutes Drift

Drift occurs when graphs no longer accurately reflect the repository state:

| Drift Type | Description |
|------------|-------------|
| **Schema Drift** | New tables/views added to SQL without corresponding Graph 50 update |
| **Orphaned Nodes** | Graph nodes reference SQL/config that no longer exists |
| **Store Drift** | External stores (R2, Notion, new integrations) added without Graph 51 update |
| **Legend Collision** | Node ID reused with different meaning across graphs |
| **Status Drift** | Component marked DORMANT/NOT INVOKED becomes active (or vice versa) |
| **Ownership Drift** | Component moves between Options without legend update |

### B. Detection Mechanisms (Conceptual)

**Manual Pre-Merge Checklist:**
Before merging PRs that touch schema, stores, or pipelines:

1. **SQL Schema vs Graph 50:**
   - [ ] Any new table/view in `sql/` → add to Graph 50
   - [ ] Any removed table/view → remove from Graph 50
   - [ ] Any renamed table/view → update Graph 50 + legends

2. **External Stores vs Graph 51:**
   - [ ] New R2 bucket paths → update Graph 51
   - [ ] New external integrations (Notion DBs, APIs) → update Graph 51
   - [ ] New artifact/report directories → update Graph 51

3. **Legend Uniqueness:**
   - [ ] No new node ID conflicts with existing IDs
   - [ ] All new nodes added to LEGEND_MASTER.md
   - [ ] All new nodes added to relevant LEGEND_PER_GRAPH.md section

4. **Status Accuracy:**
   - [ ] DORMANT workflows that gain schedules → remove DORMANT marker
   - [ ] NOT INVOKED code now called → remove NOT INVOKED marker
   - [ ] Active components disabled → add appropriate marker

**CI-Style Conceptual Checks (NOT IMPLEMENTED):**
The following checks could be automated but are documented here as manual procedures:

| Check | Procedure |
|-------|-----------|
| SQL-to-Graph-50 | Compare `sql/**/*.sql` CREATE TABLE/VIEW statements against Graph 50 nodes |
| Stores-to-Graph-51 | Compare `wrangler.jsonc` bindings + `scripts/export/` targets against Graph 51 nodes |
| Legend-ID-Uniqueness | Scan LEGEND_MASTER.md for duplicate Node ID entries |
| Graph-Reference-Validity | For each node ID in graphs, verify entry exists in LEGEND_MASTER.md |

### C. Response Protocol

When drift is detected, resolve in this order:

1. **Update graphs FIRST** — Graphs are descriptive truth
2. **Update legends SECOND** — Legends must stay synchronized with graphs
3. **Only then update pipelines/code** — Code changes follow visualization clarity

**Explicit Rule:** Graphs describe reality. They do not drive implementation. If a graph shows something that doesn't exist, the graph is wrong—fix the graph, don't create the component.

### D. Drift Logging

| Location | Purpose |
|----------|---------|
| `00_README__GRAPH_ATLAS.md` → UNPLACED / AMBIGUOUS ITEMS | Items that cannot be cleanly graphed |
| `00_README__GRAPH_ATLAS.md` → UNRESOLVED / IMPLIED ITEMS | Relationships that are unclear or inferred |
| PR comments | Note specific drift findings during review |
| `docs/governance/` | Major architectural drift requiring governance review |

**Unresolved Drift Handling:**
- Document in UNRESOLVED / IMPLIED ITEMS section
- Do NOT block work for minor drift
- Schedule drift resolution as separate task
- Mark affected graph nodes with `(UNVERIFIED)` or `(IMPLIED)` until resolved

---

## UNRESOLVED / IMPLIED ITEMS

The following items have been identified but not fully resolved:

| Item | Graph | Issue | Resolution Status |
|------|-------|-------|-------------------|
| `ovc_cfg.threshold_packs` vs `ovc_cfg.threshold_pack` | Graph 50 | Naming inconsistency between docs and SQL | Documented in UNPLACED, SQL name used |
| Path2 contract | Graph 30 | Referenced but not implemented | Marked as `(IMPLIED / NOT IMPLEMENTED)` |
| `90_verify_gate2.sql` automation | Graph 11, 24, 31 | Exists but not automated | Marked as `(NOT AUTOMATED)` |
| `schema/applied_migrations.json` | Graph 24 | All entries marked UNVERIFIED | Marked as `(UNVERIFIED)` |

---

*End of Graph Atlas README*
