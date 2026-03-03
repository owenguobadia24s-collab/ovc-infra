# TASKPACK — Design Record Engine (Full Build)

This pack is STRICT ORDER. Execute tasks top to bottom.
One Codex thread per task. Do not parallelize tasks that touch same files. :contentReference[oaicite:7]{index=7}

Raw chat export:

evidence/chat_exports/2026-02-21_export_raw/

Derived outputs:

artifacts/design_record_engine/
TASK 00 — Scaffold + Schemas + CI

Create:

Base folder structure

All schema skeletons (valid draft-2020-12)

CI workflow

test_schemas.py

test_determinism.py (empty scaffold)

DoD:

CI passes locally

Schemas validate

Determinism harness scaffolded

TASK 01 — Phase 0 Seal (Deterministic)

Implement:

phase0_chat_seal.ps1
Manifest Rule (Patched)

MANIFEST.sha256 lists ALL export files EXCEPT MANIFEST.sha256 itself.

Seal files (EXPORT_METADATA.json, SEAL_README.md) ARE included in manifest.

Manifest sorted lexicographically by POSIX path.

Format: <sha256> <posix_rel_path>

Verification:

Rehash files

Fail if mismatch

Exit non-zero on failure

No existing export files modified.

Add:

test_phase0_manifest_integrity.py

TASK 02 — Phase 1 Evidence Nodes

Implement:

phase1_build_evidence_nodes.py

Inputs:

git tracked files

Phase 0 manifest

Output:

evidence_nodes.jsonl

Each row:

node_id

kind

rel_path

sha256

size_bytes

origin (repo_tracked | chat_export_sealed)

Deterministic ordering:

lexicographic by node_id

Add determinism test:

Rerun script twice on fixture → byte-identical output.

TASK 03 — Phase 2 Anchor Extraction (Deterministic)

Implement:

phase2_extract_anchors.py

Inputs:

evidence_nodes.jsonl

anchor_dictionary_v1.json

Rules:

Exact match only (case-sensitive).

Word-boundary matching.

Allowed types: term, path, schema, hash.

Outputs:

evidence_anchors.jsonl

anchor_stats.json

Must be byte-identical across reruns.

TASK 04 — Phase 3 Chat Normalization

Implement:

phase3_parse_chat_export.py

Detect:

conversations-*.json OR other known export formats.

Fail closed if unsupported format.

Outputs:

chat_nodes.jsonl

chat_messages.jsonl

Rules:

Stable deterministic IDs.

Deterministic message ordering.

Timestamps parsed if present; else null.

No guessing.

TASK 05 — Phase 4 Chunk + Embed (Local Canonical)

Implement:

phase4_chunk_and_embed.py

Chunking:

Static max length

Fixed overlap

Chunk_version recorded in manifest

chunk_id:

hash(node_id + start_offset + end_offset + chunk_version)

Outputs:

chunks.jsonl

embeddings.jsonl

embedding_run_manifest.json

--dry-run mode:

Writes chunks.jsonl

Writes manifest with embedded=false

Fail closed if embeddings requested but API key missing.

TASK 06 — Phase 6 Evidence Graph

Implement:

phase6_build_graph.py

Edge kinds:

anchor_overlap_v1

embedding_similarity_v1

embedding_similarity_v1 requires:

threshold recorded in graph_stats.json

Outputs:

evidence_edges.jsonl

graph_stats.json

All referenced IDs must exist.

TASK 07 — Phase 7 Cluster Modules

Implement:

phase7_cluster_modules.py

Outputs:

module_candidates.jsonl

borderlands.jsonl

module_stats.json

Every node:

assigned to ≥1 module OR

appears in borderlands with reason_code

Reason codes:

LOW_COHESION

MULTI_HIGH

INSUFFICIENT_ANCHORS

Modules must include:

top anchors

node counts

TASK 08 — Phase 8 Invariants Ledger

Implement:

phase8_invariants_ledger.py

Inputs:

evidence_anchors.jsonl

chat timestamps

git log timestamps

Rules:

first_seen_at = earliest timestamp OR null

If null → record first_seen_source=node_id

No inferred chronology

Outputs:

invariants_ledger.jsonl

chronology.jsonl

TASK 09 — Query Engine (Fail-Closed)

Implement:

query_engine.py

Modes:

local_rag (canonical)

hosted_rag (optional mirror)

Hosted must use:
Responses API + file_search tool.

Rules:

Every claim must cite node_id + chunk_id.

Configurable:

MIN_CITATIONS

MIN_COVERAGE

If below threshold → deterministic refusal.

Add tests:

refusal path

citation formatting

threshold enforcement

TASK 10 — Phase 5 Hosted Vector Store Sync (Optional Mirror but included in full build)

Implement:

phase5_vector_store_sync.py

Uses:
Responses API + file_search tool.

Rules:

Upload normalized derived text only.

Never upload raw sealed evidence binaries.

Write:
vector_store_state.json

Subcommands:

--create

--status

--list

