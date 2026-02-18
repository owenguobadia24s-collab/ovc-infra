import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "repo_cartographer" / "phase_b7_unknown_frontier.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase_b7_module", str(SCRIPT_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for row in rows:
        if isinstance(row, str):
            lines.append(row)
        else:
            lines.append(json.dumps(row, sort_keys=True, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_valid_pointer(run_id: str) -> dict:
    return {
        "LATEST_OK_RUN_ID": run_id,
        "LATEST_OK_RUN_TS": "2026-02-18T14:29:51Z",
        "ok": True,
        "ledger_manifest_match": True,
        "ledger_seal_match": True,
        "manifest_sidecar_match": True,
        "seal_sidecar_match": True,
    }


def pointer_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "baselines" / "LATEST_OK_RUN_POINTER_v0.1.json"


def source_path(tmp_path: Path, run_id: str) -> Path:
    return (
        tmp_path
        / "artifacts"
        / "repo_cartographer"
        / run_id
        / "REPO_FILE_CLASSIFICATION_v0.1.jsonl"
    )


def out_json_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.json"


def out_txt_path(tmp_path: Path) -> Path:
    return tmp_path / "docs" / "catalogs" / "REPO_CARTOGRAPHER_UNKNOWN_FRONTIER_v0.1.txt"


def parse_txt_paths(txt: str) -> list[str]:
    marker_start = "## By path (sorted)"
    marker_end = "## Counts by top-level directory"
    section = txt.split(marker_start, 1)[1].split(marker_end, 1)[0]
    paths = [line.strip() for line in section.splitlines() if line.strip()]
    return paths


def test_success_writes_json_and_txt_consistently(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    rows = [
        {"path": "b/file.py", "module_id": "UNKNOWN"},
        {"path": "README.md", "module": "UNKNOWN"},
        {"path": "a/ok.txt", "module_id": "MOD_A"},
        {"path": r"docs\z.md", "classification": "UNKNOWN"},
        {"path": "naked", "ownership": "UNKNOWN"},
    ]
    write_jsonl(source_path(tmp_path, run_id), rows)

    summary = m.execute(tmp_path)
    assert summary.action == "COPIED"
    assert summary.unknown_count == 4
    assert out_json_path(tmp_path).exists()
    assert out_txt_path(tmp_path).exists()

    payload = json.loads(out_json_path(tmp_path).read_text(encoding="utf-8"))
    assert payload["selected_run_id"] == run_id
    assert payload["selected_run_ts"] == "2026-02-18T14:29:51Z"
    assert payload["unknown_count"] == 4

    unknown_paths = [entry["path"] for entry in payload["unknown_files"]]
    assert unknown_paths == sorted(unknown_paths)
    assert unknown_paths == ["README.md", "b/file.py", "docs/z.md", "naked"]

    txt = out_txt_path(tmp_path).read_text(encoding="utf-8")
    txt_paths = parse_txt_paths(txt)
    assert txt_paths == unknown_paths
    assert "README.md: 1" in txt
    assert "b: 1" in txt
    assert "docs: 1" in txt
    assert "naked: 1" in txt
    assert "md: 2" in txt
    assert "py: 1" in txt
    assert "(none): 1" in txt


def test_fail_pointer_missing(tmp_path: Path):
    m = load_module()
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_POINTER_MISSING"


def test_fail_pointer_parse(tmp_path: Path):
    m = load_module()
    p = pointer_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{bad-json", encoding="utf-8")
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_POINTER_PARSE"


@pytest.mark.parametrize(
    "field",
    [
        "ok",
        "ledger_manifest_match",
        "ledger_seal_match",
        "manifest_sidecar_match",
        "seal_sidecar_match",
    ],
)
def test_fail_pointer_gate_false(field: str, tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    payload = make_valid_pointer(run_id)
    payload[field] = False
    write_json(pointer_path(tmp_path), payload)
    summary = m.execute(tmp_path)
    assert summary.action == f"FAIL_POINTER_GATE_FALSE:{field}"


def test_fail_run_dir_missing(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_RUN_DIR_MISSING"


def test_fail_source_missing(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    (tmp_path / "artifacts" / "repo_cartographer" / run_id).mkdir(parents=True, exist_ok=True)
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_SOURCE_MISSING"
    assert summary.source_path_exists is False


def test_fail_classification_parse_malformed_json_line(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    write_jsonl(
        source_path(tmp_path, run_id),
        [
            {"path": "a.md", "module_id": "UNKNOWN"},
            "{bad-json",
        ],
    )
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_CLASSIFICATION_PARSE"


def test_fail_classification_parse_non_object_line(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    write_jsonl(source_path(tmp_path, run_id), [[1, 2, 3]])
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_CLASSIFICATION_PARSE"


@pytest.mark.parametrize(
    "row",
    [
        {"module_id": "UNKNOWN"},
        {"path": "", "module_id": "UNKNOWN"},
        {"path": 12, "module_id": "UNKNOWN"},
        {"path": "/abs/path.md", "module_id": "UNKNOWN"},
    ],
)
def test_fail_classification_schema_invalid_path(row: dict, tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    write_jsonl(source_path(tmp_path, run_id), [row])
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_CLASSIFICATION_SCHEMA"


def test_fail_atomic_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    m = load_module()
    run_id = "20260218_142951Z"
    write_json(pointer_path(tmp_path), make_valid_pointer(run_id))
    write_jsonl(source_path(tmp_path, run_id), [{"path": "a.md", "module_id": "UNKNOWN"}])

    def fake_replace(_src: Path, _dest: Path) -> None:
        raise OSError("forced replace failure")

    monkeypatch.setattr(m.os, "replace", fake_replace)
    summary = m.execute(tmp_path)
    assert summary.action == "FAIL_ATOMIC_WRITE"

