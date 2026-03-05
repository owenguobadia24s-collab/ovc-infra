#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_HEADER = [
    "export_id",
    "chat_id",
    "message_id",
    "created_at",
    "role",
    "content_sha256",
    "shard_file",
    "shard_line_number",
]


def _node_id(export_id: str, chat_id: str, message_id: str) -> str:
    return hashlib.sha256(f"{export_id}:{chat_id}:{message_id}".encode("utf-8")).hexdigest()


def _serialize_json_line(value: dict[str, object]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def run(chat_corpus_root: Path, out_path: Path) -> None:
    index_path = chat_corpus_root / "INDEX_CHAT_EXPORT_v1.csv"
    if not index_path.is_file():
        raise RuntimeError(f"Missing index file: {index_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with index_path.open("r", encoding="utf-8", newline="") as in_handle, out_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as out_handle:
        reader = csv.reader(in_handle)
        header = next(reader, None)
        if header != EXPECTED_HEADER:
            raise RuntimeError(
                "Invalid INDEX_CHAT_EXPORT_v1.csv header. "
                f"Expected {EXPECTED_HEADER!r}, got {header!r}"
            )

        for row_number, row in enumerate(reader, start=2):
            if len(row) != len(EXPECTED_HEADER):
                raise RuntimeError(
                    f"Invalid row length in index at line {row_number}: "
                    f"expected {len(EXPECTED_HEADER)}, got {len(row)}"
                )
            (
                export_id,
                chat_id,
                message_id,
                _created_at,
                _role,
                content_sha256,
                shard_file,
                shard_line_number_raw,
            ) = row
            try:
                shard_line_number = int(shard_line_number_raw)
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid shard_line_number at line {row_number}: {shard_line_number_raw!r}"
                ) from exc
            if shard_line_number < 1:
                raise RuntimeError(
                    f"Invalid shard_line_number at line {row_number}: must be >= 1, got {shard_line_number}"
                )

            node = {
                "chat_id": chat_id,
                "content_sha256": content_sha256,
                "export_id": export_id,
                "message_id": message_id,
                "node_id": _node_id(export_id, chat_id, message_id),
                "shard_file": shard_file,
                "shard_line_number": shard_line_number,
                "type": "chat_message",
            }
            out_handle.write(_serialize_json_line(node))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build chat_message evidence_nodes.jsonl from deterministic chat corpus index."
    )
    parser.add_argument("--chat-corpus-root", required=True, help="Path to evidence/chat_corpus/v1")
    parser.add_argument("--out", required=True, help="Output path for evidence_nodes.jsonl")
    args = parser.parse_args()

    try:
        run(chat_corpus_root=Path(args.chat_corpus_root).resolve(), out_path=Path(args.out).resolve())
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
