# Skill: ovc_design_record_engine

You are implementing the OVC Design Record Engine.

Always:
- Fail-closed on missing inputs or integrity mismatch.
- Prefer minimal diffs. Do not refactor unrelated code.
- Write deterministic artifacts:
  - sorted lexicographically
  - stable IDs
  - UTF-8, LF newlines for generated text
- Never mutate sealed evidence under evidence/chat_exports/** after Phase 0.

Required outputs for each phase:
- Implement script(s)
- Implement schema(s) if needed
- Implement tests
- Update docs/design_record_engine/TASKPACK_FULLBUILD.md with completion notes

If a phase depends on OpenAI API:
- Use Vector Stores + file_search for hosted retrieval (Responses/Assistants lanes). :contentReference[oaicite:4]{index=4}
- Record model/version and run metadata (embedding model, chunking strategy, counts). :contentReference[oaicite:5]{index=5}