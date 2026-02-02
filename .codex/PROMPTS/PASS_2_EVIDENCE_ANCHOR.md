TASK: PASS 2 — FLOW TRUTH (EVIDENCE OF EXECUTION)

Target graph:
Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md

Reference files:
Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md
Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_PER_GRAPH.md

Rules:
- READ-ONLY. No edits.
- Interpret ONLY edge status (solid vs dashed) and whether execution/flow is proven by repo evidence.
- “Proven” means at least one of:
   a) GitHub workflow calls script
   b) script imports/calls module
   c) SQL view depends on table/view (references)
   d) Docs can support interpretation BUT do not qualify an edge as PROVEN without code/workflow/SQL evidence.
   Add ProofType column: {workflow_call, script_call, python_import_call, sql_dependency}.
- If you cannot prove, mark as IMPLIED.

Steps:
1) Parse the Mermaid diagram and extract all edges.
2) Classify each edge by style:
   - Solid (-->)
   - Dashed (-.->)
   - Other (note it)
3) For each edge A -> B:
   a) Map A and B using LEGEND_MASTER where possible.
   b) Find evidence:
      - Workflows: .github/workflows/*.yml referencing scripts or python modules
      - Scripts: scripts/**/*.py, scripts/**/*.sh referencing modules or SQL
      - SQL: sql/**/*.sql references (FROM, JOIN, CREATE VIEW dependencies)
      - Python: imports and function calls (ripgrep)
4) Output Markdown report:
   - Header: PASS 2 — <graph filename>
   - Section A: Edge Table:
       Edge | Style | Claimed Flow | Proven? (YES/NO) | Evidence (paths/grep) | Notes
   - Section B: “Proven Flow Chain” (if possible):
       External -> A -> B -> C -> D, listing only edges that are PROVEN.
   - Section C: Gaps:
       - Edges shown but not provable
       - Nodes marked NOT INVOKED / DORMANT (cross-check legend Status)
   - Section D: Minimal summary (<=10 bullets) of what is actually running vs just mapped.

Evidence constraints:
- Quote only tiny grep snippets (<=3 lines).
- Always include file paths for each claim.
Return only the report.
