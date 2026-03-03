TASK 00 — Scaffold Design Record Engine

Implement repo scaffolding for the Design Record Engine.

Rules:
- Minimal diffs.
- Create only new files/dirs listed in docs/design_record_engine/TASKPACK_FULLBUILD.md Task 00.
- Add JSON Schemas (valid JSON, draft-07 or 2020-12; pick one and be consistent).
- Add tests/design_record_engine/test_schemas.py that validates all *.schema.json against the chosen draft.
- Add .github/workflows/design_record_engine_ci.yml that runs:
  - python -m pytest
  - schema validation

DoD:
- CI workflow exists and runs locally.
- schemas are valid and tests pass.

Files to create/update:
- schemas/design_record_engine/evidence_nodes.schema.json
- schemas/design_record_engine/evidence_anchors.schema.json
- schemas/design_record_engine/anchor_dictionary_v1.json (seed with ~30 anchors: Option A–D, fail-closed, pointer gating, sha256, MANIFEST.sha256, LATEST_OK_RUN_POINTER, run envelope, append-only, etc.)
- tests/design_record_engine/test_schemas.py
- .github/workflows/design_record_engine_ci.yml
- docs/design_record_engine/TASKPACK_FULLBUILD.md (append completion note under Task 00)

TASK 01 — Phase 0 chat export sealing

Implement scripts/design_record_engine/phase0_chat_seal.ps1 to seal:
evidence/chat_exports/2026-02-21_export_raw/

Must write inside that folder:
- MANIFEST.sha256 (sha256  <posix_rel_path>, sorted)
- EXPORT_METADATA.json (counts/bytes, special file lists, export_id)
- SEAL_README.md (verification instructions)

Must verify:
- re-hash all files and confirm manifest matches; exit non-zero on mismatch.

Rules:
- Do NOT modify any existing export files.
- Deterministic ordering; UTF-8; LF newlines for generated files.
- Include seal files in the final manifest.

Add tests:
- tests/design_record_engine/test_phase0_manifest_integrity.py
  - should verify MANIFEST.sha256 format + includes required files if present.
  - should fail if manifest mismatches (use a temporary fixture directory).

Update docs/design_record_engine/TASKPACK_FULLBUILD.md with completion note.

TASK 02 — Build evidence_nodes.jsonl

Implement scripts/design_record_engine/phase1_build_evidence_nodes.py

Inputs:
- git tracked files (git ls-files)
- all files under evidence/chat_exports/2026-02-21_export_raw/ (recursive)
- Phase 0 MANIFEST.sha256 must exist and be used as source of truth for export file list

Output:
- artifacts/design_record_engine/evidence_nodes.jsonl

Constraints:
- Deterministic ordering (lexicographic by node_id).
- node_id scheme:
  - FILE:<posix_path_from_repo_root>
  - CHAT_EXPORT_FILE:<posix_rel_path_under_export_root>

Each row must include: node_id, kind, rel_path, sha256, size_bytes.

Add/update schema validation tests accordingly.

Update TASKPACK_FULLBUILD.md completion note.

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
- Term anchors must be exact matches from dictionary list.
- Include per-node counts.

Update schema(s) and tests.

Update TASKPACK completion note.

TASK 04 — Parse chat export into normalized nodes/messages

Implement scripts/design_record_engine/phase3_parse_chat_export.py

Inputs:
- evidence/chat_exports/2026-02-21_export_raw/conversations-*.json (if present)

Outputs:
- artifacts/design_record_engine/chat_nodes.jsonl
- artifacts/design_record_engine/chat_messages.jsonl

Rules:
- Stable IDs: chat_id from export if present; otherwise deterministic hash of conversation object.
- Timestamps: parse if present; else null (no guessing).
- Deterministic message ordering.

Add schemas if needed and tests for stability on a small fixture.

Update TASKPACK completion note.

TASK 05 — Deterministic chunking + embeddings

Implement scripts/design_record_engine/phase4_chunk_and_embed.py

Inputs:
- artifacts/design_record_engine/chat_messages.jsonl (and optionally selected repo text files)
- Chunk deterministically (static max tokens/characters + overlap; document settings)

Outputs:
- artifacts/design_record_engine/chunks.jsonl
- artifacts/design_record_engine/embeddings.jsonl
- artifacts/design_record_engine/embedding_run_manifest.json

Requirements:
- Record embedding model name in manifest.
- Fail closed if API key missing when embeddings requested.
- Provide a --dry-run mode that only writes chunks.jsonl.

Update TASKPACK completion note.

TASK 06 — Evidence graph build

Implement scripts/design_record_engine/phase6_build_graph.py

Inputs:
- evidence_nodes.jsonl
- evidence_anchors.jsonl
- embeddings.jsonl (if present)

Outputs:
- evidence_edges.jsonl
- graph_stats.json

Rules:
- anchor_overlap edges deterministic
- embedding_similarity edges versioned with threshold recorded in graph_stats

Update TASKPACK completion note.

TASK 07 — Cluster module candidates + borderlands

Implement scripts/design_record_engine/phase7_cluster_modules.py

Inputs:
- evidence_edges.jsonl
- evidence_anchors.jsonl

Outputs:
- module_candidates.jsonl
- borderlands.jsonl
- module_stats.json

DoD:
- Every node assigned to >=1 module or in borderlands with reason.
- Each module includes top anchors.

Update TASKPACK completion note.

TASK 08 — Invariants ledger + chronology

Implement scripts/design_record_engine/phase8_invariants_ledger.py

Inputs:
- evidence_anchors.jsonl
- chat_nodes.jsonl timestamps
- git log timestamps (use subprocess git)

Outputs:
- invariants_ledger.jsonl
- chronology.jsonl

Rules:
- first-seen per invariant
- if timestamp unknown => explicit null and marked

Update TASKPACK completion note.

TASK 09 — Query Engine (fail-closed, citation required)

Implement scripts/design_record_engine/query_engine.py

Modes:
- local_rag: chunks+embeddings cosine similarity
- hosted_rag (optional hook): vector store + file_search

Rules:
- Every claim must cite node_id + chunk_id(s).
- If citation coverage below threshold => refuse.

Add tests for refusal and citation formatting.

Update TASKPACK completion note.

TASK 10 — Hosted Vector Store Sync (OpenAI file_search)

Implement scripts/design_record_engine/phase5_vector_store_sync.py

Goal:
- Create vector store
- Upload selected files (normalized chat text + key docs)
- Poll until ready
- Write artifacts/design_record_engine/vector_store_state.json with IDs/status/counts

Requirements:
- Do not upload raw sealed evidence binaries; upload derived text only.
- Record chunking strategy if configured.
- Provide --list and --status subcommands.

Update TASKPACK completion note.