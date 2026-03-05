from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


def test_run_all_golden_fixture(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture_export_root = repo_root / "tests" / "fixtures" / "chat_export_minimal"
    export_root = tmp_path / "workspace_root"
    chat_export_root = tmp_path / "chat_export_root"
    artifacts_root = tmp_path / "design_record_engine_artifacts"
    required_scripts = [
        repo_root / "scripts" / "design_record_engine" / "phase0_chat_export_normalize.py",
        repo_root / "scripts" / "design_record_engine" / "phase1_build_evidence_nodes_from_chat_corpus.py",
        repo_root / "scripts" / "design_record_engine" / "phase2_extract_anchors.py",
        repo_root / "scripts" / "design_record_engine" / "phase3_parse_chat_export.py",
        repo_root / "scripts" / "design_record_engine" / "phase4_chunk_and_embed.py",
        repo_root / "scripts" / "design_record_engine" / "phase6_build_graph.py",
        repo_root / "scripts" / "design_record_engine" / "phase7_cluster_modules.py",
        repo_root / "scripts" / "design_record_engine" / "phase8_invariants_ledger.py",
        repo_root / "scripts" / "design_record_engine" / "query_engine.py",
    ]
    missing_scripts = [str(path) for path in required_scripts if not path.is_file()]
    if missing_scripts:
        pytest.skip("Required scripts missing: " + ", ".join(missing_scripts))

    shutil.copytree(fixture_export_root, chat_export_root)

    clean_env = os.environ.copy()
    clean_env.pop("OPENAI_API_KEY", None)

    cmd = [
        "python",
        "scripts/design_record_engine/run_all.py",
        "--export-root",
        str(export_root),
        "--chat-export-root",
        str(chat_export_root),
        "--seal",
        "--stop-after-phase0",
        "--artifacts-root",
        str(artifacts_root),
    ]
    r = subprocess.run(cmd, cwd=str(repo_root), env=clean_env, capture_output=True, text=True)
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"

    corpus_root = export_root / "evidence" / "chat_corpus" / "v1"
    manifest_path = corpus_root / "MANIFEST.sha256"
    metadata_path = corpus_root / "EXPORT_METADATA.json"
    pointers_path = corpus_root / "EXPORT_POINTERS_v1.json"
    index_path = corpus_root / "INDEX_CHAT_EXPORT_v1.csv"
    shards_root = corpus_root / "shards"

    assert manifest_path.is_file(), f"Missing output: {manifest_path}"
    assert manifest_path.stat().st_size > 0, f"Empty output: {manifest_path}"
    manifest_lines = [line.strip() for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest_paths = []
    for line in manifest_lines:
        parts = line.split("  ", 1)
        assert len(parts) == 2, f"Invalid manifest line: {line!r}"
        manifest_paths.append(parts[1])
    assert "EXPORT_METADATA.json" in manifest_paths
    assert "EXPORT_POINTERS_v1.json" in manifest_paths
    assert "INDEX_CHAT_EXPORT_v1.csv" in manifest_paths

    assert metadata_path.is_file(), f"Missing output: {metadata_path}"
    assert metadata_path.stat().st_size > 0, f"Empty output: {metadata_path}"
    json.loads(metadata_path.read_text(encoding="utf-8"))

    assert pointers_path.is_file(), f"Missing output: {pointers_path}"
    assert index_path.is_file(), f"Missing output: {index_path}"
    assert shards_root.is_dir(), f"Missing output directory: {shards_root}"
