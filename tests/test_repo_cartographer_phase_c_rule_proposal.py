import hashlib
import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "repo_cartographer" / "phase_c_rule_proposal.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase_c_module", str(SCRIPT_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows) + "\n"
    path.write_text(body, encoding="utf-8")


def write_sha256_sidecar(path: Path, artifact_name: str, content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()
    path.write_text(f"{digest}  {artifact_name}\n", encoding="utf-8")
    return digest


def make_pointer(run_id: str) -> dict:
    return {
        "LATEST_OK_RUN_ID": run_id,
        "LATEST_OK_RUN_TS": "2026-02-18T14:29:51Z",
        "ok": True,
        "ledger_manifest_match": True,
        "ledger_seal_match": True,
        "manifest_sidecar_match": True,
        "seal_sidecar_match": True,
    }


def setup_common_inputs(tmp_path: Path, run_id: str, classification_rows: list[dict]) -> None:
    write_json(tmp_path / "docs" / "baselines" / "LATEST_OK_RUN_POINTER_v0.1.json", make_pointer(run_id))

    rules = {
        "ruleset_id": "MODULE_OWNERSHIP_RULES_v0.1",
        "modules": {
            "M01": {"kind": "module", "label": "Test Module"},
        },
        "rules": [
            {"owner_id": "M01", "pattern": "pkg/feature/owned/", "type": "prefix"},
            {"owner_id": "UNKNOWN", "pattern": "README.md", "type": "exact"},
        ],
    }
    write_json(tmp_path / "docs" / "baselines" / "MODULE_OWNERSHIP_RULES_v0.1.json", rules)

    run_dir = tmp_path / "artifacts" / "repo_cartographer" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(run_dir / "REPO_FILE_CLASSIFICATION_v0.1.jsonl", classification_rows)
    write_jsonl(
        run_dir / "REPO_FILE_INDEX_v0.1.jsonl",
        [{"path": row["path"], "file_ext": ".py", "tracked_status": "tracked", "size_bytes": 1} for row in classification_rows],
    )

    manifest_bytes = json.dumps(
        {"schema_version": "REPO_CARTOGRAPHER_MANIFEST_v0.1", "run_id": run_id, "artifacts": {}},
        sort_keys=True,
    ).encode("utf-8")
    seal_bytes = json.dumps(
        {"kind": "REPO_CARTOGRAPHER_RUN_SEAL", "run_id": run_id},
        sort_keys=True,
    ).encode("utf-8")
    (run_dir / "MANIFEST.json").write_bytes(manifest_bytes)
    (run_dir / "SEAL.json").write_bytes(seal_bytes)
    write_sha256_sidecar(run_dir / "MANIFEST.sha256", "MANIFEST.json", manifest_bytes)
    write_sha256_sidecar(run_dir / "SEAL.sha256", "SEAL.json", seal_bytes)


def test_fail_when_pointer_missing(tmp_path: Path, monkeypatch):
    m = load_module()
    monkeypatch.setattr(m, "get_repo_root", lambda: tmp_path)
    rc = m.main(["--phase-c-prompt-text", "phase-c prompt"])
    assert rc == 2
    failure_path = tmp_path / "artifacts" / "repo_cartographer_proposals" / "FAILURE_v0.1" / "FAILURE_REPORT.md"
    assert failure_path.exists()
    assert "FAIL_POINTER_MISSING" in failure_path.read_text(encoding="utf-8")


def test_success_writes_staged_pack_and_promotes(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142951Z"
    rows = [{"path": "pkg/feature/owned/a.py", "module_id": "M01", "zone_id": None, "file_ext": ".py", "generated_hint": None}]
    for i in range(1, 6):
        rows.append(
            {
                "path": f"pkg/feature/new/file{i}.py",
                "module_id": "UNKNOWN",
                "zone_id": None,
                "file_ext": ".py",
                "generated_hint": None,
            }
        )
    setup_common_inputs(tmp_path, run_id, rows)

    summary = m.execute(tmp_path, phase_c_prompt_text="phase-c prompt", append_ledger=False)
    assert summary.exit_code == 0
    assert summary.action == "OK"

    proposal_dir = tmp_path / "artifacts" / "repo_cartographer_proposals" / summary.proposal_id
    assert proposal_dir.exists()
    assert not (proposal_dir / ".staging").exists()
    for name in [
        "PROPOSED_RULESET_PATCH_v0.1.json",
        "PREDICTED_CLASSIFICATION_DELTA_v0.1.jsonl",
        "RULE_DIFF_REPORT_v0.1.md",
        "INPUTS.json",
        "POLICY.json",
        "MANIFEST.json",
        "MANIFEST.sha256",
        "SEAL.json",
        "SEAL.sha256",
    ]:
        assert (proposal_dir / name).exists()

    patch = json.loads((proposal_dir / "PROPOSED_RULESET_PATCH_v0.1.json").read_text(encoding="utf-8"))
    ops = patch["operations"]
    assert len(ops) >= 1
    assert all(op["op"] == "insert_rule" for op in ops)


def test_generated_hint_without_documentation_aborts_with_exact_text(tmp_path: Path):
    m = load_module()
    run_id = "20260218_142952Z"
    rows = [
        {
            "path": "pkg/feature/new/file1.py",
            "module_id": "UNKNOWN",
            "zone_id": None,
            "file_ext": ".py",
            "generated_hint": "AUTO",
        }
    ]
    setup_common_inputs(tmp_path, run_id, rows)

    summary = m.execute(tmp_path, phase_c_prompt_text="phase-c prompt", append_ledger=False)
    assert summary.exit_code == 2
    failure_path = tmp_path / "artifacts" / "repo_cartographer_proposals" / "FAILURE_v0.1" / "FAILURE_REPORT.md"
    assert failure_path.exists()
    assert failure_path.read_text(encoding="utf-8") == "UNKNOWN (no evidence)"


def test_verify_failure_cleans_staging_and_writes_failure_only(tmp_path: Path, monkeypatch):
    m = load_module()
    run_id = "20260218_142953Z"
    rows = [{"path": "pkg/feature/owned/a.py", "module_id": "M01", "zone_id": None, "file_ext": ".py", "generated_hint": None}]
    for i in range(1, 6):
        rows.append(
            {
                "path": f"pkg/feature/new/file{i}.py",
                "module_id": "UNKNOWN",
                "zone_id": None,
                "file_ext": ".py",
                "generated_hint": None,
            }
        )
    setup_common_inputs(tmp_path, run_id, rows)

    def force_verify_fail(*_args, **_kwargs):
        raise m.ProposalError("FAIL_VERIFY_FORCED")

    monkeypatch.setattr(m, "verify_stage", force_verify_fail)
    summary = m.execute(tmp_path, phase_c_prompt_text="phase-c prompt", append_ledger=False)
    assert summary.exit_code == 2

    failure_path = tmp_path / "artifacts" / "repo_cartographer_proposals" / "FAILURE_v0.1" / "FAILURE_REPORT.md"
    assert failure_path.exists()
    proposal_dir = tmp_path / "artifacts" / "repo_cartographer_proposals" / summary.proposal_id
    assert proposal_dir.exists()
    assert not (proposal_dir / ".staging").exists()
