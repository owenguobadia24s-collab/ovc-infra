from __future__ import annotations

import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _phase0_script() -> Path:
    return _repo_root() / "scripts" / "design_record_engine" / "phase0_chat_export_normalize.py"


def _fixture_chat_export_root() -> Path:
    return _repo_root() / "tests" / "fixtures" / "chat_export_minimal"


def _chat_schema_path() -> Path:
    return _repo_root() / "schemas" / "design_record_engine" / "chat_corpus_record_v1.schema.json"


def _run_phase0(out_root: Path, max_shard_bytes: int | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        "python",
        str(_phase0_script()),
        "--chat-export-root",
        str(_fixture_chat_export_root()),
        "--out-root",
        str(out_root),
    ]
    if max_shard_bytes is not None:
        cmd.extend(["--max-shard-bytes", str(max_shard_bytes)])
    return subprocess.run(cmd, cwd=str(_repo_root()), capture_output=True, text=True)


def _corpus_root(out_root: Path) -> Path:
    return out_root / "evidence" / "chat_corpus" / "v1"


def _snapshot_files(base: Path) -> dict[str, bytes]:
    snapshot: dict[str, bytes] = {}
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rel = path.relative_to(base).as_posix()
            snapshot[rel] = path.read_bytes()
    return snapshot


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_ok(process: subprocess.CompletedProcess[str]) -> None:
    assert process.returncode == 0, f"stdout={process.stdout}\nstderr={process.stderr}"


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
        if type_name == "number":
            return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
        if type_name == "boolean":
            return isinstance(value, bool)
        if type_name == "null":
            return value is None
        return False

    schema_type = schema.get("type")
    if schema_type is not None:
        if isinstance(schema_type, list):
            if not any(type_ok(instance, t) for t in schema_type):
                raise AssertionError(f"{path}: expected one of types {schema_type}, got {type(instance).__name__}")
        else:
            if not type_ok(instance, schema_type):
                raise AssertionError(f"{path}: expected type {schema_type}, got {type(instance).__name__}")

    if "const" in schema and instance != schema["const"]:
        raise AssertionError(f"{path}: expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise AssertionError(f"{path}: value {instance!r} not in enum")
    if isinstance(instance, str) and "pattern" in schema:
        if re.fullmatch(schema["pattern"], instance) is None:
            raise AssertionError(f"{path}: string does not match pattern {schema['pattern']!r}")
    if isinstance(instance, int) and "minimum" in schema and instance < schema["minimum"]:
        raise AssertionError(f"{path}: integer {instance} is below minimum {schema['minimum']}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise AssertionError(f"{path}: missing required key {key!r}")
        properties = schema.get("properties", {})
        additional_properties = schema.get("additionalProperties", True)
        if additional_properties is False:
            for key in instance:
                if key not in properties:
                    raise AssertionError(f"{path}: unexpected key {key!r}")
        for key, subschema in properties.items():
            if key in instance:
                _validate_schema(instance[key], subschema, f"{path}.{key}")

    if isinstance(instance, list):
        items_schema = schema.get("items")
        if isinstance(items_schema, dict):
            for i, value in enumerate(instance):
                _validate_schema(value, items_schema, f"{path}[{i}]")


def test_phase0_deterministic_rerun_byte_identical(tmp_path: Path) -> None:
    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"

    _assert_ok(_run_phase0(out_a))
    _assert_ok(_run_phase0(out_b))

    files_a = _snapshot_files(_corpus_root(out_a))
    files_b = _snapshot_files(_corpus_root(out_b))
    assert files_a == files_b


def test_phase0_shard_cap_1024_bytes(tmp_path: Path) -> None:
    out_root = tmp_path / "small_cap"
    _assert_ok(_run_phase0(out_root, max_shard_bytes=1024))

    shards = sorted((_corpus_root(out_root) / "shards").glob("*.jsonl.gz"))
    assert len(shards) >= 2
    for shard in shards:
        assert shard.stat().st_size <= 1024


def test_phase0_schema_and_manifest_integrity(tmp_path: Path) -> None:
    out_root = tmp_path / "schema_manifest"
    _assert_ok(_run_phase0(out_root))

    corpus_root = _corpus_root(out_root)
    schema = json.loads(_chat_schema_path().read_text(encoding="utf-8"))
    first_shard = sorted((corpus_root / "shards").glob("*.jsonl.gz"))[0]
    with gzip.open(first_shard, "rt", encoding="utf-8", newline="\n") as handle:
        sample_record = json.loads(handle.readline())
    _validate_schema(sample_record, schema)

    manifest_path = corpus_root / "MANIFEST.sha256"
    lines = [line for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries: list[tuple[str, str]] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        assert match is not None, f"invalid manifest line format: {line!r}"
        entries.append((match.group(1), match.group(2)))

    rel_paths = [rel for _, rel in entries]
    assert rel_paths == sorted(rel_paths)
    assert len(rel_paths) == len(set(rel_paths))
    assert "MANIFEST.sha256" not in rel_paths
    assert all("\\" not in rel for rel in rel_paths)

    for expected_hash, rel in entries:
        actual_hash = _sha256_file(corpus_root / rel)
        assert actual_hash == expected_hash
