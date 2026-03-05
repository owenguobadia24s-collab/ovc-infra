from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _phase0_script() -> Path:
    return _repo_root() / "scripts" / "design_record_engine" / "phase0_chat_export_normalize.py"


def _phase1_script() -> Path:
    return _repo_root() / "scripts" / "design_record_engine" / "phase1_build_evidence_nodes_from_chat_corpus.py"


def _fixture_chat_export_root() -> Path:
    return _repo_root() / "tests" / "fixtures" / "chat_export_minimal"


def _schema_path() -> Path:
    return _repo_root() / "schemas" / "design_record_engine" / "evidence_node_chat_message_v1.schema.json"


def _assert_ok(process: subprocess.CompletedProcess[str]) -> None:
    assert process.returncode == 0, f"stdout={process.stdout}\nstderr={process.stderr}"


def _run_phase0(out_root: Path) -> subprocess.CompletedProcess[str]:
    cmd = [
        "python",
        str(_phase0_script()),
        "--chat-export-root",
        str(_fixture_chat_export_root()),
        "--out-root",
        str(out_root),
    ]
    return subprocess.run(cmd, cwd=str(_repo_root()), capture_output=True, text=True)


def _run_phase1(chat_corpus_root: Path, out_file: Path) -> subprocess.CompletedProcess[str]:
    cmd = [
        "python",
        str(_phase1_script()),
        "--chat-corpus-root",
        str(chat_corpus_root),
        "--out",
        str(out_file),
    ]
    return subprocess.run(cmd, cwd=str(_repo_root()), capture_output=True, text=True)


def _validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    def type_ok(value: Any, type_name: str) -> bool:
        if type_name == "object":
            return isinstance(value, dict)
        if type_name == "array":
            return isinstance(value, list)
        if type_name == "string":
            return isinstance(value, str)
        if type_name == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if type_name == "null":
            return value is None
        if type_name == "boolean":
            return isinstance(value, bool)
        if type_name == "number":
            return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
        return False

    schema_type = schema.get("type")
    if schema_type is not None:
        if isinstance(schema_type, list):
            assert any(type_ok(instance, t) for t in schema_type), f"{path}: invalid type"
        else:
            assert type_ok(instance, schema_type), f"{path}: invalid type"

    if "const" in schema:
        assert instance == schema["const"], f"{path}: const mismatch"
    if "enum" in schema:
        assert instance in schema["enum"], f"{path}: enum mismatch"
    if isinstance(instance, str) and "pattern" in schema:
        import re

        assert re.fullmatch(schema["pattern"], instance) is not None, f"{path}: pattern mismatch"
    if isinstance(instance, int) and "minimum" in schema:
        assert instance >= schema["minimum"], f"{path}: minimum mismatch"

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            assert key in instance, f"{path}: missing {key}"
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        if additional is False:
            for key in instance:
                assert key in properties, f"{path}: unexpected key {key}"
        for key, sub in properties.items():
            if key in instance:
                _validate_schema(instance[key], sub, f"{path}.{key}")


def test_phase1_nodes_are_deterministic_and_ordered(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    _assert_ok(_run_phase0(run_root))

    chat_corpus_root = run_root / "evidence" / "chat_corpus" / "v1"
    out_file = tmp_path / "evidence_nodes.jsonl"
    _assert_ok(_run_phase1(chat_corpus_root, out_file))
    assert out_file.is_file()
    assert out_file.stat().st_size > 0

    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    nodes = [json.loads(line) for line in out_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    for node in nodes:
        _validate_schema(node, schema)

    index_rows: list[dict[str, str]] = []
    with (chat_corpus_root / "INDEX_CHAT_EXPORT_v1.csv").open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            index_rows.append(row)

    assert len(nodes) == len(index_rows)
    for node, index_row in zip(nodes, index_rows):
        expected_node_id = hashlib.sha256(
            f"{index_row['export_id']}:{index_row['chat_id']}:{index_row['message_id']}".encode("utf-8")
        ).hexdigest()
        assert node["node_id"] == expected_node_id
        assert node["export_id"] == index_row["export_id"]
        assert node["chat_id"] == index_row["chat_id"]
        assert node["message_id"] == index_row["message_id"]
        assert node["content_sha256"] == index_row["content_sha256"]
        assert node["shard_file"] == index_row["shard_file"]
        assert node["shard_line_number"] == int(index_row["shard_line_number"])


def test_phase1_rerun_byte_identical(tmp_path: Path) -> None:
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    _assert_ok(_run_phase0(run_a))
    _assert_ok(_run_phase0(run_b))

    out_a = tmp_path / "nodes_a.jsonl"
    out_b = tmp_path / "nodes_b.jsonl"
    _assert_ok(_run_phase1(run_a / "evidence" / "chat_corpus" / "v1", out_a))
    _assert_ok(_run_phase1(run_b / "evidence" / "chat_corpus" / "v1", out_b))

    assert out_a.read_bytes() == out_b.read_bytes()
