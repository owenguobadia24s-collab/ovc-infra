#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POINTER_PATH = Path("docs/baselines/LATEST_OK_RUN_POINTER_v0.1.json")
RUNS_ROOT = Path("artifacts/repo_cartographer")
PROPOSALS_ROOT = Path("artifacts/repo_cartographer_proposals")
BASE_RULESET_PATH = Path("docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json")
FAILURE_REPORT_PATH = Path("artifacts/repo_cartographer_proposals/FAILURE_v0.1/FAILURE_REPORT.md")
OPTIONAL_LEDGER_PATH = Path("docs/catalogs/REPO_CARTOGRAPHER_RULE_PROPOSAL_LEDGER_v0.1.jsonl")

REQUIRED_RUN_INPUTS = [
    "REPO_FILE_CLASSIFICATION_v0.1.jsonl",
    "REPO_FILE_INDEX_v0.1.jsonl",
    "MANIFEST.json",
    "MANIFEST.sha256",
    "SEAL.json",
    "SEAL.sha256",
]
OPTIONAL_RUN_INPUTS = [
    "MODULE_OWNERSHIP_SUMMARY_v0.1.md",
    "UNTRACKED_VISIBLE_REPORT_v0.1.md",
    "BORDERLANDS_PRESSURE_REPORT_v0.1.md",
]
OPTIONAL_CONTEXT_INPUTS = [
    "docs/REPO_MAP/REPO_TOPOLOGY_v0.1.md",
    "docs/REPO_MAP/MODULE_INDEX_v0.1.md",
    "docs/REPO_MAP/BORDERLANDS_v0.1.md",
]
BOOL_GATE_FIELDS = [
    "ok",
    "ledger_manifest_match",
    "ledger_seal_match",
    "manifest_sidecar_match",
    "seal_sidecar_match",
]

POLICY_TEXT = """{
  "allow_new_module_ids": false,
  "allow_reclassify_non_unknown": false,
  "max_new_rules": 10,
  "min_cluster_size": 5,
  "allowed_match_types": ["prefix"],
  "must_target": ["UNKNOWN"],
  "forbidden_paths": [
    "docs/baselines/",
    "scripts/sentinel/",
    "scripts/repo_cartographer/"
  ]
}"""
POLICY_BYTES = POLICY_TEXT.encode("utf-8")
POLICY = json.loads(POLICY_TEXT)

PACK_FILES = [
    "PROPOSED_RULESET_PATCH_v0.1.json",
    "PREDICTED_CLASSIFICATION_DELTA_v0.1.jsonl",
    "RULE_DIFF_REPORT_v0.1.md",
    "INPUTS.json",
    "POLICY.json",
]


class ProposalError(RuntimeError):
    def __init__(self, code: str, details: list[str] | None = None, unknown_no_evidence: bool = False):
        super().__init__(code)
        self.code = code
        self.details = details or []
        self.unknown_no_evidence = unknown_no_evidence


@dataclass
class Summary:
    action: str
    exit_code: int
    proposal_id: str = ""
    proposal_fingerprint: str = ""


@dataclass(frozen=True)
class Row:
    path: str
    module_id: str
    zone_id: str | None
    file_ext: str
    generated_hint: str | None


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_sha_sidecar(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        return ""
    token = text.split()[0].lower()
    if len(token) != 64:
        return ""
    try:
        int(token, 16)
    except ValueError:
        return ""
    return token


def normalize_path(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while "//" in value:
        value = value.replace("//", "/")
    while value.startswith("./"):
        value = value[2:]
    if not value or value.startswith("/") or "\x00" in value:
        raise ProposalError("FAIL_CLASSIFICATION_SCHEMA", [f"invalid path: {path!r}"])
    return value


def serialize_json(obj: Any, sort_keys: bool = True) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=sort_keys) + "\n").encode("utf-8")


def serialize_jsonl(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    body = "\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in rows)
    return (body + "\n").encode("utf-8")


def add_input(inputs: list[dict[str, Any]], rel: str, present: bool, sha: str = "") -> None:
    inputs.append({"path": rel, "present": present, "sha256": sha if present else ""})


def read_input(repo_root: Path, rel: str, inputs: list[dict[str, Any]], required: bool, fail_code: str) -> bytes | None:
    path = repo_root / rel
    if not path.exists() or not path.is_file():
        add_input(inputs, rel, False, "")
        if required:
            raise ProposalError(fail_code, [f"missing: {rel}"])
        return None
    data = path.read_bytes()
    add_input(inputs, rel, True, sha256_bytes(data))
    return data


def read_json_obj(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProposalError(code, [path.as_posix()]) from exc
    if not isinstance(value, dict):
        raise ProposalError(code, [path.as_posix()])
    return value


def parse_jsonl(path: Path, code: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProposalError(code, [path.as_posix()]) from exc
    rows: list[dict[str, Any]] = []
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProposalError(code, [f"{path.as_posix()}:{i}"]) from exc
        if not isinstance(obj, dict):
            raise ProposalError(code, [f"{path.as_posix()}:{i}"])
        rows.append(obj)
    return rows


def parse_rows(raw: list[dict[str, Any]]) -> list[Row]:
    out: list[Row] = []
    for i, item in enumerate(raw, start=1):
        path_raw = item.get("path")
        module_id = item.get("module_id")
        if not isinstance(path_raw, str) or not isinstance(module_id, str) or not module_id:
            raise ProposalError("FAIL_CLASSIFICATION_SCHEMA", [f"line:{i}"])
        zone_raw = item.get("zone_id")
        zone_id = zone_raw if isinstance(zone_raw, str) else None
        file_ext = item.get("file_ext")
        if not isinstance(file_ext, str):
            suffix = Path(path_raw).suffix
            file_ext = suffix if suffix else ""
        hint_raw = item.get("generated_hint")
        hint = hint_raw if isinstance(hint_raw, str) and hint_raw else None
        out.append(Row(normalize_path(path_raw), module_id, zone_id, file_ext, hint))
    out.sort(key=lambda r: r.path)
    return out


def match_rule(path: str, rule: dict[str, Any]) -> bool:
    rtype = rule.get("type")
    pattern = rule.get("pattern")
    if not isinstance(rtype, str) or not isinstance(pattern, str):
        return False
    if rtype == "prefix":
        return path.startswith(pattern)
    if rtype == "exact":
        return path == pattern
    if rtype == "glob":
        if rule.get("constraint") == "root_only" and "/" in path:
            return False
        return fnmatch.fnmatch(path, pattern)
    return False


def classify(path: str, rules: list[dict[str, Any]], modules: dict[str, Any]) -> tuple[str, int | None]:
    for idx, rule in enumerate(rules):
        if not match_rule(path, rule):
            continue
        owner = rule.get("owner_id")
        if owner == "UNKNOWN":
            return ("UNKNOWN", idx)
        module = modules.get(owner)
        kind = module.get("kind") if isinstance(module, dict) else None
        if kind == "module":
            return (str(owner), idx)
        if kind == "borderland":
            return ("BORDERLAND", idx)
        return ("UNKNOWN", idx)
    return ("UNKNOWN", None)


def infer_owner(pattern: str, rows: list[Row], modules: dict[str, Any]) -> str | None:
    owners: set[str] = set()
    for row in rows:
        if not row.path.startswith(pattern) or row.module_id == "UNKNOWN":
            continue
        if row.module_id == "BORDERLAND":
            if row.zone_id:
                owners.add(row.zone_id)
        else:
            owners.add(row.module_id)
    if len(owners) != 1:
        return None
    owner = sorted(owners)[0]
    if owner not in modules:
        return None
    return owner


def build_candidates(rows: list[Row], modules: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, int]]:
    unknown = [r for r in rows if r.module_id == "UNKNOWN"]
    clusters: dict[tuple[str, str, str, str], list[Row]] = {}
    for row in unknown:
        parts = row.path.split("/")
        first = parts[0] if parts else ""
        second = parts[1] if len(parts) > 1 else ""
        clusters.setdefault((first, second, row.file_ext, row.generated_hint or ""), []).append(row)

    rejected: dict[str, int] = {}
    merged: dict[tuple[str, str], set[str]] = {}
    forbidden = set(POLICY["forbidden_paths"])
    for key, members in sorted(clusters.items(), key=lambda kv: kv[0]):
        if len(members) < int(POLICY["min_cluster_size"]):
            rejected["cluster_too_small"] = rejected.get("cluster_too_small", 0) + 1
            continue
        first, second, _, _ = key
        if not first:
            rejected["empty_prefix"] = rejected.get("empty_prefix", 0) + 1
            continue
        pattern = f"{first}/{second}/" if second else (None if all("/" not in r.path for r in members) else f"{first}/")
        if pattern is None:
            rejected["root_file_cluster"] = rejected.get("root_file_cluster", 0) + 1
            continue
        if any(pattern.startswith(p) for p in forbidden):
            rejected["forbidden_path"] = rejected.get("forbidden_path", 0) + 1
            continue
        owner = infer_owner(pattern, rows, modules)
        if owner is None:
            rejected["owner_inference_failed"] = rejected.get("owner_inference_failed", 0) + 1
            continue
        support = {r.path for r in unknown if r.path.startswith(pattern)}
        if not support:
            rejected["no_unknown_support"] = rejected.get("no_unknown_support", 0) + 1
            continue
        merged.setdefault((pattern, owner), set()).update(support)

    out: list[dict[str, str]] = []
    for (pattern, owner), support in sorted(merged.items(), key=lambda kv: (-len(kv[0][0]), kv[0][0], kv[0][1])):
        _ = support
        out.append({"owner_id": owner, "pattern": pattern, "type": "prefix"})
    return out, rejected


def simulate(rows: list[Row], base_rules: list[dict[str, Any]], modules: dict[str, Any], appended: list[dict[str, Any]]) -> dict[str, Any]:
    rules = [*base_rules, *appended]
    base_count = len(base_rules)
    delta: list[dict[str, Any]] = []
    churn: list[str] = []
    ambiguity: list[str] = []
    per_rule: dict[str, int] = {}
    unknown_after = 0
    for row in rows:
        new_mid, idx = classify(row.path, rules, modules)
        if new_mid == "UNKNOWN":
            unknown_after += 1
        if row.module_id != "UNKNOWN" and new_mid != row.module_id:
            churn.append(row.path)
            continue
        if row.module_id == "UNKNOWN" and new_mid != "UNKNOWN":
            if idx is None or idx < base_count:
                ambiguity.append(row.path)
                continue
            rule = rules[idx]
            key = f"{rule['pattern']}|{rule['owner_id']}"
            per_rule[key] = per_rule.get(key, 0) + 1
            delta.append(
                {
                    "path": row.path,
                    "old_module_id": "UNKNOWN",
                    "new_module_id": new_mid,
                    "reason_codes": [f"insert_rule_prefix:{rule['pattern']}:{rule['owner_id']}"],
                    "ambiguity_flags": [],
                }
            )
    delta.sort(key=lambda r: r["path"])
    churn.sort()
    ambiguity.sort()
    return {
        "delta": delta,
        "unknown_after": unknown_after,
        "churn": churn,
        "ambiguity": ambiguity,
        "per_rule": dict(sorted(per_rule.items())),
    }


def choose_rules(rows: list[Row], base_rules: list[dict[str, Any]], modules: dict[str, Any], candidates: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    selected: list[dict[str, str]] = []
    unknown_before = sum(1 for r in rows if r.module_id == "UNKNOWN")
    current_unknown = unknown_before
    remaining = list(candidates)
    while remaining and len(selected) < int(POLICY["max_new_rules"]):
        best: tuple[int, int, str, int, dict[str, Any]] | None = None
        best_idx = -1
        for idx, c in enumerate(remaining):
            trial = [*selected, c]
            sim = simulate(rows, base_rules, modules, trial)
            if sim["churn"] or sim["ambiguity"]:
                continue
            gain = current_unknown - int(sim["unknown_after"])
            if gain <= 0:
                continue
            key = (gain, len(c["pattern"]), c["pattern"], -idx, sim)
            if best is None or key[:3] > best[:3]:
                best = key
                best_idx = idx
        if best is None:
            break
        chosen = remaining.pop(best_idx)
        selected.append(chosen)
        current_unknown = int(best[4]["unknown_after"])
    final_sim = simulate(rows, base_rules, modules, selected)
    return selected, final_sim


def build_report(unknown_before: int, final_sim: dict[str, Any], rejected: dict[str, int], selected: list[dict[str, str]]) -> str:
    lines = [
        "# RULE_DIFF_REPORT_v0.1",
        "",
        f"UNKNOWN_BEFORE: {unknown_before}",
        f"UNKNOWN_AFTER_PREDICTED: {final_sim['unknown_after']}",
        "",
        "## PER_RULE_AFFECTED_PATH_COUNTS",
    ]
    if final_sim["per_rule"]:
        for key in sorted(final_sim["per_rule"].keys()):
            lines.append(f"{key}: {final_sim['per_rule'][key]}")
    else:
        lines.append("none")
    lines.extend(["", "## RISKS_AND_AMBIGUITY", f"non_unknown_churn_count: {len(final_sim['churn'])}"])
    lines.append("ambiguity: none" if not final_sim["ambiguity"] else f"ambiguity: {','.join(final_sim['ambiguity'])}")
    lines.append("selection: no_rules_selected" if not selected else f"selection: rules_selected={len(selected)}")
    for key in sorted(rejected.keys()):
        lines.append(f"candidate_rejected_{key}: {rejected[key]}")
    lines.append("")
    return "\n".join(lines)


def write_failure(repo_root: Path, code: str, details: list[str], unknown_no_evidence: bool) -> None:
    out = repo_root / FAILURE_REPORT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    if unknown_no_evidence:
        out.write_text("UNKNOWN (no evidence)", encoding="utf-8")
        return
    lines = ["# FAILURE_REPORT", "", f"code: {code}", "details:"]
    lines.extend(f"- {d}" for d in (details or ["(none)"]))
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def verify_stage(stage: Path, expected_fp: str, expected_base_sha: str, rows: list[Row], base_rules: list[dict[str, Any]], modules: dict[str, Any]) -> None:
    policy_bytes = (stage / "POLICY.json").read_bytes().rstrip(b"\n")
    if policy_bytes != POLICY_BYTES:
        raise ProposalError("FAIL_VERIFY_POLICY_BYTES")
    patch = read_json_obj(stage / "PROPOSED_RULESET_PATCH_v0.1.json", "FAIL_VERIFY_PATCH_PARSE")
    if patch.get("proposal_fingerprint") != expected_fp:
        raise ProposalError("FAIL_VERIFY_FINGERPRINT")
    if patch.get("base_ruleset_sha256") != expected_base_sha:
        raise ProposalError("FAIL_VERIFY_BASE_RULESET_SHA")
    comps = patch.get("fingerprint_components")
    if not isinstance(comps, dict):
        raise ProposalError("FAIL_VERIFY_FINGERPRINT_COMPONENTS")
    recomputed = sha256_bytes(
        "\n".join(
            [
                str(comps.get("LATEST_OK_RUN_ID", "")),
                str(comps.get("latest_ok_run_manifest_sha256", "")),
                str(comps.get("latest_ok_run_seal_sha256", "")),
                str(comps.get("base_ruleset_sha256", "")),
                str(comps.get("proposal_policy_sha256", "")),
                str(comps.get("phase_c_prompt_sha256", "")),
            ]
        ).encode("utf-8")
    )
    if recomputed != expected_fp:
        raise ProposalError("FAIL_VERIFY_FINGERPRINT")
    ops = patch.get("operations")
    if not isinstance(ops, list):
        raise ProposalError("FAIL_VERIFY_PATCH_SCHEMA")
    appended: list[dict[str, Any]] = []
    for op in ops:
        if not isinstance(op, dict) or op.get("op") != "insert_rule":
            raise ProposalError("FAIL_VERIFY_PATCH_SCHEMA")
        rule = op.get("rule")
        if not isinstance(rule, dict):
            raise ProposalError("FAIL_VERIFY_PATCH_SCHEMA")
        appended.append({"owner_id": rule.get("owner_id"), "pattern": rule.get("pattern"), "type": rule.get("type")})
    sim = simulate(rows, base_rules, modules, appended)
    if sim["churn"]:
        raise ProposalError("FAIL_VERIFY_NON_UNKNOWN_CHURN")
    if sim["ambiguity"]:
        raise ProposalError("FAIL_VERIFY_AMBIGUITY")
    stored_delta = parse_jsonl(stage / "PREDICTED_CLASSIFICATION_DELTA_v0.1.jsonl", "FAIL_VERIFY_DELTA_PARSE")
    canonical_stored = [
        {
            "path": d.get("path"),
            "old_module_id": d.get("old_module_id"),
            "new_module_id": d.get("new_module_id"),
            "reason_codes": d.get("reason_codes"),
            "ambiguity_flags": d.get("ambiguity_flags"),
        }
        for d in stored_delta
    ]
    canonical_stored.sort(key=lambda x: x["path"])
    if canonical_stored != sim["delta"]:
        raise ProposalError("FAIL_VERIFY_DELTA_MISMATCH")
    manifest = read_json_obj(stage / "MANIFEST.json", "FAIL_VERIFY_MANIFEST_PARSE")
    arts = manifest.get("artifacts")
    if not isinstance(arts, dict):
        raise ProposalError("FAIL_VERIFY_MANIFEST_SCHEMA")
    for name in PACK_FILES:
        if name not in arts:
            raise ProposalError("FAIL_VERIFY_MANIFEST_SCHEMA")
        info = arts[name]
        if not isinstance(info, dict):
            raise ProposalError("FAIL_VERIFY_MANIFEST_SCHEMA")
        path = stage / name
        if not path.exists():
            raise ProposalError("FAIL_VERIFY_MANIFEST_SCHEMA")
        if info.get("sha256") != sha256_bytes(path.read_bytes()) or info.get("bytes") != path.stat().st_size:
            raise ProposalError("FAIL_VERIFY_MANIFEST_CONTENT")
    if parse_sha_sidecar((stage / "MANIFEST.sha256").read_bytes()) != sha256_bytes((stage / "MANIFEST.json").read_bytes()):
        raise ProposalError("FAIL_VERIFY_MANIFEST_SIDECAR")
    if parse_sha_sidecar((stage / "SEAL.sha256").read_bytes()) != sha256_bytes((stage / "SEAL.json").read_bytes()):
        raise ProposalError("FAIL_VERIFY_SEAL_SIDECAR")
    seal = read_json_obj(stage / "SEAL.json", "FAIL_VERIFY_SEAL_PARSE")
    target = seal.get("target")
    if not isinstance(target, dict) or target.get("sha256") != sha256_bytes((stage / "MANIFEST.json").read_bytes()):
        raise ProposalError("FAIL_VERIFY_SEAL_TARGET")


def execute(repo_root: Path, phase_c_prompt_text: str, append_ledger: bool = False) -> Summary:
    inputs: list[dict[str, Any]] = []
    proposal_id = ""
    proposal_fingerprint = ""
    stage_dir: Path | None = None
    try:
        pointer_bytes = read_input(repo_root, POINTER_PATH.as_posix(), inputs, True, "FAIL_POINTER_MISSING")
        assert pointer_bytes is not None
        try:
            pointer = json.loads(pointer_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ProposalError("FAIL_POINTER_PARSE") from exc
        if not isinstance(pointer, dict):
            raise ProposalError("FAIL_POINTER_PARSE")
        run_id = pointer.get("LATEST_OK_RUN_ID")
        run_ts = pointer.get("LATEST_OK_RUN_TS")
        if not isinstance(run_id, str) or not run_id or not isinstance(run_ts, str) or not run_ts:
            raise ProposalError("FAIL_POINTER_PARSE")
        for field in BOOL_GATE_FIELDS:
            if pointer.get(field) is not True:
                raise ProposalError("FAIL_POINTER_GATE_FALSE", [field])

        run_rel = f"{RUNS_ROOT.as_posix()}/{run_id}"
        run_dir = repo_root / run_rel
        if not run_dir.is_dir():
            raise ProposalError("FAIL_RUN_DIR_MISSING", [run_rel])
        if run_dir.resolve().relative_to(repo_root.resolve()).as_posix() != run_rel:
            raise ProposalError("FAIL_RUN_DIR_MISMATCH", [run_rel])

        run_data: dict[str, bytes] = {}
        for name in REQUIRED_RUN_INPUTS:
            data = read_input(repo_root, f"{run_rel}/{name}", inputs, True, "FAIL_REQUIRED_INPUT_MISSING")
            assert data is not None
            run_data[name] = data
        optional_texts: list[str] = []
        for name in OPTIONAL_RUN_INPUTS:
            data = read_input(repo_root, f"{run_rel}/{name}", inputs, False, "FAIL_OPTIONAL_INPUT")
            if data is not None:
                optional_texts.append(data.decode("utf-8", errors="replace"))
        for rel in OPTIONAL_CONTEXT_INPUTS:
            _ = read_input(repo_root, rel, inputs, False, "FAIL_OPTIONAL_INPUT")

        ruleset_bytes = read_input(repo_root, BASE_RULESET_PATH.as_posix(), inputs, True, "FAIL_BASE_RULESET_MISSING")
        assert ruleset_bytes is not None
        try:
            ruleset = json.loads(ruleset_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ProposalError("FAIL_BASE_RULESET_PARSE") from exc
        if not isinstance(ruleset, dict):
            raise ProposalError("FAIL_BASE_RULESET_PARSE")
        modules = ruleset.get("modules")
        base_rules = ruleset.get("rules")
        if not isinstance(modules, dict) or not isinstance(base_rules, list):
            raise ProposalError("FAIL_BASE_RULESET_SCHEMA")

        if parse_sha_sidecar(run_data["MANIFEST.sha256"]) != sha256_bytes(run_data["MANIFEST.json"]):
            raise ProposalError("FAIL_RUN_MANIFEST_SIDECAR_MISMATCH")
        if parse_sha_sidecar(run_data["SEAL.sha256"]) != sha256_bytes(run_data["SEAL.json"]):
            raise ProposalError("FAIL_RUN_SEAL_SIDECAR_MISMATCH")
        try:
            json.loads(run_data["MANIFEST.json"].decode("utf-8"))
            json.loads(run_data["SEAL.json"].decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ProposalError("FAIL_RUN_MANIFEST_SEAL_PARSE") from exc

        class_raw = parse_jsonl(run_dir / "REPO_FILE_CLASSIFICATION_v0.1.jsonl", "FAIL_CLASSIFICATION_PARSE")
        rows = parse_rows(class_raw)
        _ = parse_jsonl(run_dir / "REPO_FILE_INDEX_v0.1.jsonl", "FAIL_INDEX_PARSE")
        if any(r.generated_hint is not None for r in rows):
            marker = any("generated_hint_semantics:" in t.lower() or "generated_hint semantics:" in t.lower() for t in optional_texts)
            if not marker:
                raise ProposalError("FAIL_GENERATED_HINT_UNDOCUMENTED", unknown_no_evidence=True)

        run_manifest_sha = sha256_bytes(run_data["MANIFEST.json"])
        run_seal_sha = sha256_bytes(run_data["SEAL.json"])
        base_sha = sha256_bytes(ruleset_bytes)
        policy_sha = sha256_bytes(POLICY_BYTES)
        prompt_sha = sha256_bytes(phase_c_prompt_text.encode("utf-8"))
        proposal_fingerprint = sha256_bytes("\n".join([run_id, run_manifest_sha, run_seal_sha, base_sha, policy_sha, prompt_sha]).encode("utf-8"))
        proposal_id = f"rcp_{run_id}_{proposal_fingerprint[:12]}"

        candidates, rejected = build_candidates(rows, modules)
        selected, final_sim = choose_rules(rows, base_rules, modules, candidates)
        if final_sim["churn"]:
            raise ProposalError("FAIL_NON_UNKNOWN_CHURN", final_sim["churn"][:20])
        if final_sim["ambiguity"]:
            raise ProposalError("FAIL_AMBIGUITY", final_sim["ambiguity"][:20])

        unknown_before = sum(1 for r in rows if r.module_id == "UNKNOWN")
        patch = {
            "schema_version": "REPO_CARTOGRAPHER_PROPOSED_RULESET_PATCH_v0.1",
            "base_ruleset_ref": BASE_RULESET_PATH.as_posix(),
            "base_ruleset_sha256": base_sha,
            "proposal_id": proposal_id,
            "proposal_fingerprint": proposal_fingerprint,
            "ordering_rationale": {"strategy": "greedy_max_unknown_reduction", "tie_breakers": ["prefix_length_desc", "pattern_lex_asc"]},
            "fingerprint_components": {
                "LATEST_OK_RUN_ID": run_id,
                "latest_ok_run_manifest_sha256": run_manifest_sha,
                "latest_ok_run_seal_sha256": run_seal_sha,
                "base_ruleset_sha256": base_sha,
                "proposal_policy_sha256": policy_sha,
                "phase_c_prompt_sha256": prompt_sha,
            },
            "operations": [{"op": "insert_rule", "insert_at": "append", "rule": r} for r in selected],
        }
        report_text = build_report(unknown_before, final_sim, rejected, selected)
        inputs_payload = {"proposal_id": proposal_id, "inputs": sorted(inputs, key=lambda x: x["path"])}

        proposal_root = repo_root / PROPOSALS_ROOT / proposal_id
        if proposal_root.exists():
            raise ProposalError("FAIL_PROPOSAL_DIR_EXISTS", [proposal_root.as_posix()])
        proposal_root.mkdir(parents=True, exist_ok=False)
        stage_dir = proposal_root / ".staging"
        stage_dir.mkdir(parents=True, exist_ok=False)

        (stage_dir / "PROPOSED_RULESET_PATCH_v0.1.json").write_bytes(serialize_json(patch))
        (stage_dir / "PREDICTED_CLASSIFICATION_DELTA_v0.1.jsonl").write_bytes(serialize_jsonl(final_sim["delta"]))
        (stage_dir / "RULE_DIFF_REPORT_v0.1.md").write_text(report_text, encoding="utf-8")
        (stage_dir / "INPUTS.json").write_bytes(serialize_json(inputs_payload))
        (stage_dir / "POLICY.json").write_bytes(POLICY_BYTES + b"\n")

        manifest = {"schema_version": "REPO_CARTOGRAPHER_RULE_PROPOSAL_MANIFEST_v0.1", "proposal_id": proposal_id, "artifacts": {}}
        for name in sorted(PACK_FILES):
            content = (stage_dir / name).read_bytes()
            manifest["artifacts"][name] = {"bytes": len(content), "sha256": sha256_bytes(content)}
        manifest_bytes = serialize_json(manifest)
        (stage_dir / "MANIFEST.json").write_bytes(manifest_bytes)
        (stage_dir / "MANIFEST.sha256").write_text(f"{sha256_bytes(manifest_bytes)}  MANIFEST.json\n", encoding="utf-8")
        seal = {
            "kind": "REPO_CARTOGRAPHER_RULE_PROPOSAL_SEAL",
            "version": "0.1",
            "proposal_id": proposal_id,
            "proposal_fingerprint": proposal_fingerprint,
            "target": {"path": "MANIFEST.json", "bytes": len(manifest_bytes), "sha256": sha256_bytes(manifest_bytes)},
            "inputs": {
                POINTER_PATH.as_posix(): sha256_bytes(pointer_bytes),
                f"{run_rel}/MANIFEST.json": run_manifest_sha,
                f"{run_rel}/SEAL.json": run_seal_sha,
                BASE_RULESET_PATH.as_posix(): base_sha,
                "policy_blob": policy_sha,
                "phase_c_prompt": prompt_sha,
            },
        }
        seal_bytes = serialize_json(seal)
        (stage_dir / "SEAL.json").write_bytes(seal_bytes)
        (stage_dir / "SEAL.sha256").write_text(f"{sha256_bytes(seal_bytes)}  SEAL.json\n", encoding="utf-8")

        verify_stage(stage_dir, proposal_fingerprint, base_sha, rows, base_rules, modules)

        for name in [*PACK_FILES, "MANIFEST.json", "MANIFEST.sha256", "SEAL.json", "SEAL.sha256"]:
            os.replace(stage_dir / name, proposal_root / name)
        stage_dir.rmdir()

        if append_ledger:
            line = json.dumps(
                {
                    "proposal_id": proposal_id,
                    "proposal_fingerprint": proposal_fingerprint,
                    "base_ruleset_sha256": base_sha,
                    "run_id": run_id,
                    "status": "OK",
                },
                sort_keys=True,
                separators=(",", ":"),
            ) + "\n"
            ledger = repo_root / OPTIONAL_LEDGER_PATH
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("ab") as f:
                f.write(line.encode("utf-8"))

        return Summary(action="OK", exit_code=0, proposal_id=proposal_id, proposal_fingerprint=proposal_fingerprint)
    except ProposalError as exc:
        if stage_dir is not None:
            shutil.rmtree(stage_dir, ignore_errors=True)
        write_failure(repo_root, exc.code, exc.details, exc.unknown_no_evidence)
        return Summary(action=exc.code, exit_code=2, proposal_id=proposal_id, proposal_fingerprint=proposal_fingerprint)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Phase-C deterministic rule proposal runner.")
    p.add_argument("--phase-c-prompt-text", required=True, help="Exact Phase-C prompt text bytes (UTF-8).")
    p.add_argument("--append-ledger", action="store_true", help="Append one line to optional proposal ledger on success.")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    s = execute(get_repo_root(), phase_c_prompt_text=args.phase_c_prompt_text, append_ledger=args.append_ledger)
    print(f"action={s.action}")
    print(f"proposal_id={s.proposal_id}")
    print(f"proposal_fingerprint={s.proposal_fingerprint}")
    print(f"failure_report_path={FAILURE_REPORT_PATH.as_posix()}")
    return s.exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
