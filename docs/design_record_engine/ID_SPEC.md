# ID_SPEC 

FILE:<posix_repo_path>
CHAT_EXPORT_FILE:<posix_rel_path>
CHAT:<chat_id>
MSG:<chat_id>:<index>
CHUNK:<node_id>:<start_offset>:<end_offset>:v<chunk_version>

Rules:

All IDs deterministic.

Hashes use SHA256 of canonical JSON (sorted keys).

Newlines normalized to LF before hashing.

No timestamps embedded in IDs.