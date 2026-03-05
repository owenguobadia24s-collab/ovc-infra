Use **one Codex thread per task**. Start every thread by pasting the **Meta Prompt** below, then paste the specific **Task Prompt** (00–10).

This prompt set is aligned to the patched taskpack:
- Phase/Task numbering consistent
- Phase 0 manifest rule fixed (manifest excludes itself)
- Hosted RAG uses **Responses API + file_search** and is **optional mirror**
- Determinism + fail-closed enforced


---

## META PROMPT (paste at the top of EVERY Codex thread)

```text
You are Codex working inside this repo. Follow AGENTS.md and the skill:
.codex/skills/ovc_design_record_engine/skill.md

THREAD RULES (must follow):
1) Restate the Task goal in 1–2 lines.
2) List exact files you will create/edit (repo-relative POSIX paths).
3) Implement with minimal diffs. Do not refactor unrelated code.
4) Run tests locally (or state exactly what you ran and what passed/failed).
5) Report DoD status. If anything is incomplete, list it as TODO with file paths.

GLOBAL CONSTRAINTS:
- Fail-closed: stop and report if inputs are missing or integrity checks fail.
- Deterministic outputs: stable ordering, stable IDs, UTF-8 + LF newlines.
- No renames/deletes unless the task explicitly says so.
- Never mutate sealed evidence under evidence/chat_exports/** after Phase 0.

OUTPUT DISCIPLINE:
- Derived outputs → artifacts/design_record_engine/
- Schemas → schemas/design_record_engine/
- Scripts → scripts/design_record_engine/
- Tests → tests/design_record_engine/

Now execute the Task below exactly as written.
```

---

## TASK 00 — Scaffold + CI + Schemas

```text
TASK 00 — Scaffold Design Record Engine

Implement repo scaffolding for the Design Record Engine.

Rules:
- Minimal diffs.
- Create only new files/dirs listed in docs/design_record_engine/TASKPACK_FULLBUILD.md Task 00.
- Add JSON Schemas (valid JSON, draft-2020-12; be consistent).
- Add tests/design_record_engine/test_schemas.py that validates all *.schema.json against the chosen draft.
- Add tests/design_record_engine/test_determinism.py scaffold (must exist and run; can start minimal).
- Add .github/workflows/design_record_engine_ci.yml that runs:
  - python -m pytest
  - schema validation tests

DoD:
- CI workflow exists and runs locally.
- Schemas are valid and tests pass.

Files to create/update (only these for Task 00):
- schemas/design_record_engine/evidence_nodes.schema.json
- schemas/design_record_engine/evidence_anchors.schema.json
- schemas/design_record_engine/chat_nodes.schema.json
- schemas/design_record_engine/chat_messages.schema.json
- schemas/design_record_engine/anchor_dictionary_v1.json (seed ~30 anchors: Option A–D, fail-closed, pointer gating, sha256, MANIFEST.sha256, LATEST_OK_RUN_POINTER, run envelope, append-only, etc.)
- tests/design_record_engine/test_schemas.py
- tests/design_record_engine/test_determinism.py
- .github/workflows/design_record_engine_ci.yml
- docs/design_record_engine/TASKPACK_FULLBUILD.md (append completion note under Task 00)

After implementing, run tests and report DoD status.
```

---

## TASK 01 — Phase 0 chat export sealing (PowerShell)

```text
TASK 01 — Phase 0 chat export sealing

Implement scripts/design_record_engine/phase0_chat_seal.ps1 to seal:
evidence/chat_exports/2026-02-21_export_raw/

Must write inside that folder:
- MANIFEST.sha256 (sha256  <posix_rel_path>, sorted)
- EXPORT_METADATA.json (counts/bytes, special file lists, export_id)
- SEAL_README.md (verification instructions)

MANIFEST RULE (PATCHED):
- MANIFEST.sha256 must list ALL export files EXCEPT MANIFEST.sha256 itself.
- It MUST include EXPORT_METADATA.json and SEAL_README.md.
- Format: "<sha256>  <posix_rel_path>" (two spaces), POSIX relpaths, lexicographic sort.

Must verify:
- re-hash all listed files and confirm manifest matches; exit non-zero on mismatch.

Rules:
- Do NOT modify any existing export files.
- Deterministic ordering; UTF-8; LF newlines for generated files.
- MANIFEST excludes itself by rule above (do not attempt self-hash entries).

Add tests:
- tests/design_record_engine/test_phase0_manifest_integrity.py
  - should verify MANIFEST.sha256 format + inclusion/exclusion rule.
  - should fail on mismatch (use a temporary fixture directory).

Update docs/design_record_engine/TASKPACK_FULLBUILD.md with completion note.
```

---

## TASK 02 — Phase 1 evidence_nodes.jsonl

```text
TASK 02 — Build evidence_nodes.jsonl

Implement scripts/design_record_engine/phase1_build_evidence_nodes.py

Inputs:
- git tracked files (git ls-files)
- Phase 0 MANIFEST.sha256 as source of truth for export file list

Output:
- artifacts/design_record_engine/evidence_nodes.jsonl

Constraints:
- Deterministic ordering (lexicographic by node_id).
- node_id scheme:
  - FILE:<posix_path_from_repo_root>
  - CHAT_EXPORT_FILE:<posix_rel_path_under_export_root>

Each JSONL row must include:
- node_id
- kind
- rel_path
- sha256
- size_bytes
- origin (repo_tracked | chat_export_sealed)

Add determinism coverage:
- tests/design_record_engine/test_determinism.py must include a fixture test that runs the script twice on the same fixture and asserts byte-identical output.

Update TASKPACK_FULLBUILD.md completion note.
```

---

## TASK 03 — Phase 2 evidence_anchors.jsonl (deterministic)

```text
TASK 03 — Deterministic anchor extraction

Implement scripts/design_record_engine/phase2_extract_anchors.py

Inputs:
- artifacts/design_record_engine/evidence_nodes.jsonl
- schemas/design_record_engine/anchor_dictionary_v1.json

Output:
- artifacts/design_record_engine/evidence_anchors.jsonl
- artifacts/design_record_engine/anchor_stats.json

Rules:
- Deterministic: same input => byte-identical outputs.
- Allowed anchor types: term, path, schema, hash.
- Term anchors must be exact matches from dictionary list:
  - case-sensitive
  - word-boundary match (no substring hits)
- Include per-node counts and overall stats.

Update schema(s) and tests accordingly.
Update TASKPACK completion note.
```

---

## TASK 04 — Phase 3 parse chat exports into normalized chat nodes/messages

```text
TASK 04 — Parse chat export into normalized nodes/messages

Implement scripts/design_record_engine/phase3_parse_chat_export.py

Inputs:
- evidence/chat_exports/2026-02-21_export_raw/ (discover supported export files)
  - e.g., conversations-*.json if present

Outputs:
- artifacts/design_record_engine/chat_nodes.jsonl
- artifacts/design_record_engine/chat_messages.jsonl

Rules:
- Fail closed if no supported export file format is found; report what files WERE found.
- Stable IDs:
  - use export chat_id if present
  - else deterministic hash of canonicalized conversation object (sorted keys, normalized strings)
- Timestamps:
  - parse if present
  - else null (no guessing)
- Deterministic message ordering.

Add schemas if needed and tests for stability on a small fixture.
Update TASKPACK completion note.
```

---

## TASK 05 — Phase 4 chunk + embed (local portable index)

```text
TASK 05 — Deterministic chunking + embeddings

Implement scripts/design_record_engine/phase4_chunk_and_embed.py

Inputs:
- artifacts/design_record_engine/chat_messages.jsonl
- (optionally) selected repo text files, but do not expand scope without updating Taskpack docs

Chunk deterministically:
- fixed max characters (or tokens if you implement a deterministic tokenizer)
- fixed overlap
- record chunking parameters and chunk_version in embedding_run_manifest.json

Outputs:
- artifacts/design_record_engine/chunks.jsonl
- artifacts/design_record_engine/embeddings.jsonl
- artifacts/design_record_engine/embedding_run_manifest.json

Requirements:
- chunk_id must be deterministic using:
  hash(node_id + start_offset + end_offset + chunk_version)
- Record embedding model name/version in manifest when embeddings are produced.
- Fail closed if embeddings requested but API key missing.
- Provide --dry-run that writes chunks.jsonl AND embedding_run_manifest.json with embedded=false.

Update TASKPACK completion note.
```

---

## TASK 06 — Phase 6 build evidence graph

```text
TASK 06 — Evidence graph build

Implement scripts/design_record_engine/phase6_build_graph.py

Inputs:
- artifacts/design_record_engine/evidence_nodes.jsonl
- artifacts/design_record_engine/evidence_anchors.jsonl
- artifacts/design_record_engine/embeddings.jsonl (optional)

Outputs:
- artifacts/design_record_engine/evidence_edges.jsonl
- artifacts/design_record_engine/graph_stats.json

Rules:
- Edge kinds must be explicit + versioned:
  - anchor_overlap_v1 (deterministic)
  - embedding_similarity_v1 (optional; requires recorded threshold + embedding model in stats)
- All referenced IDs must exist; fail closed if dangling references.
- Deterministic ordering of edges (lexicographic by (edge_kind, src_id, dst_id)).

Update TASKPACK completion note.
```

---

## TASK 07 — Phase 7 cluster modules + borderlands

```text
TASK 07 — Cluster module candidates + borderlands

Implement scripts/design_record_engine/phase7_cluster_modules.py

Inputs:
- artifacts/design_record_engine/evidence_edges.jsonl
- artifacts/design_record_engine/evidence_anchors.jsonl

Outputs:
- artifacts/design_record_engine/module_candidates.jsonl
- artifacts/design_record_engine/borderlands.jsonl
- artifacts/design_record_engine/module_stats.json

DoD:
- Every node assigned to >=1 module OR placed in borderlands with reason_code.
- Each module includes top anchors and node counts.

Borderlands reason_code taxonomy (must use one):
- LOW_COHESION
- MULTI_HIGH
- INSUFFICIENT_ANCHORS

Update TASKPACK completion note.
```

---

## TASK 08 — Phase 8 invariants ledger + chronology

```text
TASK 08 — Invariants ledger + chronology

Implement scripts/design_record_engine/phase8_invariants_ledger.py

Inputs:
- artifacts/design_record_engine/evidence_anchors.jsonl
- artifacts/design_record_engine/chat_nodes.jsonl (timestamps)
- git log timestamps (use subprocess git)

Outputs:
- artifacts/design_record_engine/invariants_ledger.jsonl
- artifacts/design_record_engine/chronology.jsonl

Rules:
- first-seen per invariant:
  - if timestamp known => earliest timestamp
  - if unknown => first_seen_at=null AND record first_seen_source=node_id
- No inferred chronology; no guessing.
- Deterministic ordering by (invariant_id, first_seen_at|null, first_seen_source).

Update TASKPACK completion note.
```

---

## TASK 09 — Query Engine (fail-closed, citation required)

```text
TASK 09 — Query Engine (fail-closed, citation required)

Implement scripts/design_record_engine/query_engine.py

Modes:
- local_rag: chunks+embeddings cosine similarity (canonical)
- hosted_rag: optional hook (mirror), using Responses API + file_search

Rules:
- Every claim must cite node_id + chunk_id(s).
- Enforce configurable thresholds:
  - MIN_CITATIONS (e.g., 2)
  - MIN_COVERAGE (e.g., 0.6)
- If thresholds not met => deterministic refusal response.

Add tests:
- refusal path
- citation formatting
- threshold enforcement

Update TASKPACK completion note.
```

---

## TASK 10 — Phase 5 Hosted vector store sync (OPTIONAL mirror)

```text
TASK 10 — Hosted Vector Store Sync (OpenAI file_search) — OPTIONAL MIRROR

Implement scripts/design_record_engine/phase5_vector_store_sync.py

Goal:
- Create vector store
- Upload selected DERIVED TEXT outputs only (normalized chat text + key docs)
- Poll until ready
- Write artifacts/design_record_engine/vector_store_state.json with IDs/status/counts

Requirements:
- Do NOT upload raw sealed evidence binaries; upload derived text only.
- Use Responses API + file_search tool conventions (not custom ad-hoc calls).
- Provide subcommands:
  - --create
  - --status
  - --list
- Record selection manifest (which files uploaded) and counts.

Update TASKPACK completion note.
```
