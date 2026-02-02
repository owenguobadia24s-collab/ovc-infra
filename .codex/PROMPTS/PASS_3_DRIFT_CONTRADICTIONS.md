TASK: PASS 3 — BOUNDARY CHECK (OWNERSHIP + CATEGORY CONSISTENCY)

Targets:
- Use the same graph as Pass 1/2:
  Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md
- Use these mapping docs:
  docs/REPO_MAP/OPT_A__ORG_MAP_DRAFT.md
  docs/REPO_MAP/OPT_B__ORG_MAP_DRAFT.md
  docs/REPO_MAP/OPT_C__ORG_MAP_DRAFT.md
  docs/REPO_MAP/OPT_D__ORG_MAP_DRAFT.md
  docs/REPO_MAP/QA__ORG_MAP_DRAFT.md
  docs/REPO_MAP/CATEGORY_PROCESS_APPENDIX_DRAFT.md
- Legends:
  Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md

Rules:
- READ-ONLY. No edits.
- Goal: Identify ownership/category mismatches and “leaks” (components doing multiple option jobs).
- Do NOT propose refactors. Only flag mismatches and cite where they appear.

Steps:
1) Extract node IDs from the target graph (reuse from Pass 1).
2) For each node:
   a) Get Owner/Category/Status from LEGEND_MASTER.
   b) Search the Option org maps for that path/node and record how the maps classify it.
   c) Use CATEGORY_PROCESS_APPENDIX_DRAFT.md to verify that its category usage is consistent.
3) Flag issues:
   - OWNER_MISMATCH: legend owner vs org map owner
   - CATEGORY_MISMATCH: legend category vs appendix meaning vs org map category
   - CROSS_OPTION_LEAK: a component in Option A doing Option D orchestration, etc.
   - DUPLICATE_DEFINITION: same thing defined in two places with different meanings
4) Output Markdown report:
   - Header: PASS 3 — <graph filename>
   - Section A: Node Consistency Table:
       NodeID | Legend Owner/Category | OrgMap Owner/Category (cite) | Consistent? | Issue Tag | Evidence
   - Section B: Boundary Violations (grouped)
   - Section C: “Needs Decision” list (<=12 items), phrased as factual tensions (not solutions)

Evidence rules:
- Cite exact doc file path + heading or nearby text lines via small snippets.
- If doc is silent, mark DOC_SILENT.
- Do not use fuzzy matching. If org maps do not mention the node/path explicitly, mark DOC_SILENT. Evidence line format required: EVIDENCE: doc | <path> | "<snippet>"
Return only the report.
