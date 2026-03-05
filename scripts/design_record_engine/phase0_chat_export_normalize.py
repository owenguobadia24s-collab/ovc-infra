#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import re
import zipfile
from pathlib import Path
from typing import Any

DEFAULT_MAX_SHARD_BYTES = 95 * 1024 * 1024
INDEX_HEADER = [
    "export_id",
    "chat_id",
    "message_id",
    "created_at",
    "role",
    "content_sha256",
    "shard_file",
    "shard_line_number",
]
ALLOWED_ROLES = {"user", "assistant", "system", "tool"}
SCHEMA_VERSION = "chat_corpus_v1"
CANONICALIZATION_RULES_VERSION = "v1"
ORDERING = "created_at asc, chat_id asc, message_id asc"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(normalized, encoding="utf-8", newline="\n")


def _write_json(path: Path, value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    _write_text(path, serialized)


def _normalize_posix_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    normalized = re.sub(r"/+", "/", normalized)
    normalized = normalized.lstrip("./")
    return normalized


def _discover_conversations(chat_export_root: Path) -> tuple[bytes, str, list[dict[str, Any]]]:
    direct_path = chat_export_root / "conversations.json"
    if direct_path.is_file():
        rel_path = "conversations.json"
        return (
            direct_path.read_bytes(),
            rel_path,
            [
                {
                    "path": rel_path,
                    "sha256": _sha256_file(direct_path),
                    "size_bytes": direct_path.stat().st_size,
                }
            ],
        )

    zip_paths = sorted(
        [p for p in chat_export_root.iterdir() if p.is_file() and p.suffix.lower() == ".zip"],
        key=lambda item: item.name,
    )
    if not zip_paths:
        raise RuntimeError(f"No conversations.json found in {chat_export_root}")

    selected_zip = zip_paths[0]
    with zipfile.ZipFile(selected_zip, "r") as archive:
        names = [_normalize_posix_path(name) for name in archive.namelist()]
        conversation_paths = sorted([name for name in names if name.split("/")[-1] == "conversations.json"])
        if not conversation_paths:
            raise RuntimeError(f"No conversations.json found in {chat_export_root}")
        if len(conversation_paths) > 1:
            joined = ", ".join(conversation_paths)
            raise RuntimeError(f"Ambiguous conversations.json entries in {selected_zip.name}: {joined}")
        inner_path = conversation_paths[0]
        with archive.open(inner_path, "r") as handle:
            conversations_bytes = handle.read()

    zip_rel = _normalize_posix_path(str(selected_zip.relative_to(chat_export_root)))
    return (
        conversations_bytes,
        f"zip:{selected_zip.name}:{inner_path}",
        [
            {
                "path": zip_rel,
                "sha256": _sha256_file(selected_zip),
                "size_bytes": selected_zip.stat().st_size,
            }
        ],
    )


def _timestamp_to_iso_utc(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            return None
        timestamp = float(value)
        if timestamp >= 1_000_000_000_000:
            timestamp = timestamp / 1000.0
        try:
            instant = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).replace(microsecond=0)
        except (OverflowError, OSError, ValueError):
            return None
        return instant.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        has_timezone = candidate.endswith("Z") or bool(re.search(r"[+-]\d{2}:\d{2}$", candidate))
        if not has_timezone:
            return None
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        try:
            parsed = dt.datetime.fromisoformat(candidate)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return None
        normalized = parsed.astimezone(dt.timezone.utc).replace(microsecond=0)
        return normalized.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(item if isinstance(item, str) else "" for item in content)
    if isinstance(content, dict):
        parts = content.get("parts")
        if isinstance(parts, list):
            return "\n".join(item if isinstance(item, str) else "" for item in parts)
    return ""


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.split("\n"))


def _map_role(message: dict[str, Any]) -> str:
    author = message.get("author")
    role_value: Any = None
    if isinstance(author, dict):
        role_value = author.get("role")
    elif isinstance(author, str):
        role_value = author
    if not isinstance(role_value, str):
        role_value = message.get("role")
    if isinstance(role_value, str) and role_value in ALLOWED_ROLES:
        return role_value
    return "unknown"


def _coerce_required_id(value: Any, context: str) -> str:
    if isinstance(value, str):
        if value == "":
            raise RuntimeError(f"Missing {context}: empty string")
        return value
    if isinstance(value, bool):
        raise RuntimeError(f"Missing {context}: bool is not allowed")
    if isinstance(value, (int, float)):
        return str(value)
    raise RuntimeError(f"Missing {context}: unsupported value type {type(value).__name__}")


def _extract_message_records(
    conversation: dict[str, Any],
    *,
    export_id: str,
    source_path: str,
    conversation_index: int,
) -> list[dict[str, Any]]:
    chat_id = _coerce_required_id(conversation.get("id"), f"chat_id at conversation index {conversation_index}")
    chat_title = conversation.get("title")
    if not isinstance(chat_title, str):
        chat_title = None

    records: list[dict[str, Any]] = []
    seen_message_ids: set[str] = set()

    mapping = conversation.get("mapping")
    if isinstance(mapping, dict):
        iterable = [(node_key, mapping[node_key]) for node_key in sorted(mapping.keys())]
    else:
        messages = conversation.get("messages")
        if isinstance(messages, list):
            iterable = [(f"messages[{i}]", messages[i]) for i in range(len(messages))]
        else:
            raise RuntimeError(f"Conversation {chat_id} is missing both mapping and messages")

    for node_key, node_value in iterable:
        node = node_value if isinstance(node_value, dict) else None
        if node is None:
            raise RuntimeError(f"Conversation {chat_id} has non-object node at {node_key}")
        message_value = node.get("message")
        if message_value is None and node_key.startswith("messages["):
            message = node
        else:
            message = message_value
        if message is None:
            continue
        if not isinstance(message, dict):
            raise RuntimeError(f"Conversation {chat_id} has non-object message at {node_key}")

        message_id_value = message.get("id")
        if message_id_value is None:
            message_id_value = node.get("id")
        message_id = _coerce_required_id(message_id_value, f"message_id in chat {chat_id} at {node_key}")
        if message_id in seen_message_ids:
            raise RuntimeError(f"Duplicate message_id '{message_id}' in chat {chat_id}")
        seen_message_ids.add(message_id)

        content = message.get("content")
        text_raw = _extract_text(content)
        text = _normalize_text(text_raw)
        created_at = _timestamp_to_iso_utc(message.get("create_time"))
        role = _map_role(message)

        records.append(
            {
                "chat_id": chat_id,
                "chat_title": chat_title,
                "content_sha256": _sha256_bytes(text.encode("utf-8")),
                "created_at": created_at,
                "export_id": export_id,
                "message_id": message_id,
                "role": role,
                "source_path": source_path,
                "text": text,
            }
        )
    return records


def _sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda row: (
            row["created_at"] is None,
            row["created_at"] or "",
            row["chat_id"],
            row["message_id"],
        ),
    )


def _serialize_record(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def _compress_lines(lines: list[str]) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, filename="", mtime=0, compresslevel=9, mode="wb") as gz:
        for line in lines:
            gz.write(line.encode("utf-8"))
    return buffer.getvalue()


def _build_shards(
    records: list[dict[str, Any]],
    *,
    max_shard_bytes: int,
    shards_dir: Path,
) -> tuple[list[dict[str, Any]], int]:
    shards_dir.mkdir(parents=True, exist_ok=True)
    current: list[tuple[dict[str, Any], str]] = []
    index_rows: list[dict[str, Any]] = []
    shard_number = 0

    def finalize_shard(items: list[tuple[dict[str, Any], str]]) -> None:
        nonlocal shard_number
        if not items:
            return
        shard_number += 1
        shard_file = f"chat_messages_{shard_number:06d}.jsonl.gz"
        payload = _compress_lines([line for _, line in items])
        if len(payload) > max_shard_bytes:
            raise RuntimeError(f"Internal error: finalized shard exceeds max bytes ({len(payload)} > {max_shard_bytes})")
        (shards_dir / shard_file).write_bytes(payload)
        for line_number, (record, _) in enumerate(items, start=1):
            index_rows.append(
                {
                    "export_id": record["export_id"],
                    "chat_id": record["chat_id"],
                    "message_id": record["message_id"],
                    "created_at": record["created_at"] or "",
                    "role": record["role"],
                    "content_sha256": record["content_sha256"],
                    "shard_file": shard_file,
                    "shard_line_number": line_number,
                }
            )

    for record in records:
        serialized = _serialize_record(record)
        candidate = current + [(record, serialized)]
        candidate_size = len(_compress_lines([line for _, line in candidate]))
        if candidate_size <= max_shard_bytes:
            current = candidate
            continue
        if not current:
            single_size = len(_compress_lines([serialized]))
            raise RuntimeError(
                "Single record exceeds max shard size "
                f"({single_size} > {max_shard_bytes}) for message_id={record['message_id']}"
            )
        finalize_shard(current)
        current = []
        single_size = len(_compress_lines([serialized]))
        if single_size > max_shard_bytes:
            raise RuntimeError(
                "Single record exceeds max shard size "
                f"({single_size} > {max_shard_bytes}) for message_id={record['message_id']}"
            )
        current = [(record, serialized)]

    finalize_shard(current)
    return index_rows, shard_number


def _write_index(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(INDEX_HEADER)
        for row in rows:
            writer.writerow(
                [
                    row["export_id"],
                    row["chat_id"],
                    row["message_id"],
                    row["created_at"],
                    row["role"],
                    row["content_sha256"],
                    row["shard_file"],
                    row["shard_line_number"],
                ]
            )


def _write_manifest(corpus_root: Path) -> None:
    manifest_path = corpus_root / "MANIFEST.sha256"
    rel_paths: list[str] = []
    for file_path in corpus_root.rglob("*"):
        if not file_path.is_file():
            continue
        rel = _normalize_posix_path(str(file_path.relative_to(corpus_root)))
        if rel == "MANIFEST.sha256":
            continue
        rel_paths.append(rel)
    rel_paths.sort()

    lines = []
    for rel in rel_paths:
        digest = _sha256_file(corpus_root / rel)
        lines.append(f"{digest}  {rel}")
    _write_text(manifest_path, "\n".join(lines) + ("\n" if lines else ""))


def run(chat_export_root: Path, out_root: Path, max_shard_bytes: int) -> None:
    if not chat_export_root.is_dir():
        raise RuntimeError(f"Chat export root does not exist or is not a directory: {chat_export_root}")
    if max_shard_bytes <= 0:
        raise RuntimeError(f"--max-shard-bytes must be > 0 (got {max_shard_bytes})")

    corpus_root = out_root / "evidence" / "chat_corpus" / "v1"
    if corpus_root.exists():
        raise RuntimeError(f"Output path already exists; fail-closed: {corpus_root}")
    shards_dir = corpus_root / "shards"

    conversations_bytes, conversations_json_path, source_inputs = _discover_conversations(chat_export_root)
    source_inputs_sorted = sorted(source_inputs, key=lambda row: row["path"])
    pointer_basis = {
        "conversations_json_path": conversations_json_path,
        "source_inputs": source_inputs_sorted,
    }
    export_id = _sha256_bytes(json.dumps(pointer_basis, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8"))

    try:
        conversations = json.loads(conversations_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"conversations.json is not valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"conversations.json is not valid JSON: {exc}") from exc

    if not isinstance(conversations, list):
        raise RuntimeError("conversations.json must be a JSON array at top level")

    source_path = _normalize_posix_path(conversations_json_path)
    records: list[dict[str, Any]] = []
    for idx, conversation in enumerate(conversations):
        if not isinstance(conversation, dict):
            raise RuntimeError(f"Conversation at index {idx} is not an object")
        records.extend(
            _extract_message_records(
                conversation,
                export_id=export_id,
                source_path=source_path,
                conversation_index=idx,
            )
        )
    records_sorted = _sort_records(records)

    index_rows, shard_count = _build_shards(records_sorted, max_shard_bytes=max_shard_bytes, shards_dir=shards_dir)

    _write_index(corpus_root / "INDEX_CHAT_EXPORT_v1.csv", index_rows)
    _write_json(
        corpus_root / "EXPORT_POINTERS_v1.json",
        {
            "conversations_json_path": conversations_json_path,
            "export_id": export_id,
            "source_inputs": source_inputs_sorted,
        },
    )
    _write_json(
        corpus_root / "EXPORT_METADATA.json",
        {
            "canonicalization_rules_version": CANONICALIZATION_RULES_VERSION,
            "export_id": export_id,
            "index_rows": len(index_rows),
            "max_shard_size_bytes": max_shard_bytes,
            "ordering": ORDERING,
            "record_count": len(records_sorted),
            "schema_version": SCHEMA_VERSION,
            "shard_count": shard_count,
        },
    )
    _write_manifest(corpus_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize ChatGPT export into deterministic chat corpus shards.")
    parser.add_argument("--chat-export-root", required=True, help="Path to raw ChatGPT export directory.")
    parser.add_argument("--out-root", required=True, help="Workspace output root.")
    parser.add_argument(
        "--max-shard-bytes",
        type=int,
        default=DEFAULT_MAX_SHARD_BYTES,
        help=f"Maximum compressed shard size in bytes (default: {DEFAULT_MAX_SHARD_BYTES}).",
    )
    args = parser.parse_args()

    try:
        run(
            chat_export_root=Path(args.chat_export_root).resolve(),
            out_root=Path(args.out_root).resolve(),
            max_shard_bytes=args.max_shard_bytes,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
