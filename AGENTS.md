# AGENTS.md — OVC Design Record Engine

Core invariants:
- Fail-closed: if inputs missing / integrity checks fail, stop and report.
- Deterministic outputs where required: stable ordering, explicit encodings, reproducible runs.
- Raw evidence is immutable: never modify files under evidence/chat_exports/* once sealed.

Thread discipline:
- One Codex thread per task file in docs/design_record_engine/TASKPACK_FULLBUILD.md.
- Never run two threads that edit the same files. (Codex threading guidance.) :contentReference[oaicite:3]{index=3}

Output discipline:
- All derived outputs go to artifacts/design_record_engine/.
- All schemas go to schemas/design_record_engine/.
- All scripts go to scripts/design_record_engine/.
- Add tests for invariants and schema validation.

Safety:
- Do not delete or rename existing files unless a task explicitly says so.