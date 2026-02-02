TASK: PASS 1 — INVENTORY (NO INTERPRETATION)

Target graph:
Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/10_OPTION_FLOW/GRAPH_10__OVERVIEW__DATA_FLOW.md

Reference files:
@ Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md
@ Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_PER_GRAPH.md

Rules:
- READ-ONLY. No file edits.
- Do not interpret edges or purpose. Only enumerate and resolve.
- If a node ID is not in LEGEND_MASTER.md, flag as LEGEND_MISSING.
- If LEGEND entry points to a glob (e.g., src/backfill_*.py), enumerate actual matches.
- If LEGEND entry points to a database object (e.g., ovc.ovc_blocks_v01_1_min), find the SQL file(s) defining it (CREATE TABLE/VIEW) using ripgrep, and cite the defining file path(s).
- For external-only items (e.g., Notion, R2), mark EXISTS: EXTERNAL (UNVERIFIABLE IN REPO).

Steps:
1) Open the target graph file and extract all node IDs used in the Mermaid diagram(s).
Node extraction must include node declarations AND all edge endpoints (union set). De-dup preserving first occurrence order.
Add CHECK section: nodes_in_edges_minus_nodes_declared.

2) For each node ID:
   a) Resolve via LEGEND_MASTER.md: record Full Path/Name, Owning Option, Category, Status.
   b) Verify existence:
      - For paths: confirm the file/folder exists.
      - For globs: list matched files.
      - For SQL objects: locate definitions in sql/**/*.sql.
3) Produce a Markdown report with:
   - Header: PASS 1 — <graph filename>
   - Section A: Node List (IDs in diagram order if possible)
   - Section B: Resolution Table:
       NodeID | Legend path/name | Owner | Category | Status | Exists? | Evidence (path or grep hit)
   - Section C: Problems
       - LEGEND_MISSING
       - PATH_MISSING
       - SQL_OBJECT_NOT_FOUND
       - DUPLICATE_ID_COLLISION (if same ID maps to multiple different meanings)
   - Section D: Minimal summary (<=8 bullets) of what is VERIFIED vs UNKNOWN.

IMPORTANT: Evidence format:
- For a file/folder: show the exact path + a one-line ls confirmation.
- For SQL objects: show grep snippets (1–3 lines) with file path, but keep quotes short.
Return only the report.
