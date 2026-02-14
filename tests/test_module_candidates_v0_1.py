import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = REPO_ROOT / "scripts" / "governance" / "build_module_candidates_v0_1.py"


def load_builder_module():
    spec = importlib.util.spec_from_file_location("module_candidates_builder", str(BUILDER_PATH))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def sha(i: int) -> str:
    return f"{i:040x}"


def ledger_row(
    i: int,
    subject: str,
    directories_touched: list[str],
    tags: list[str],
    *,
    commit_as_string: bool = False,
    commit_value: str | None = None,
) -> dict:
    value = commit_value if commit_value is not None else sha(i)
    commit_field: str | dict
    if commit_as_string:
        commit_field = value
    else:
        commit_field = {"hash": value}
    return {
        "commit": commit_field,
        "subject": subject,
        "directories_touched": directories_touched,
        "tags": tags,
    }


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: Path, payload: object) -> None:
    write_text_lf(path, json.dumps(payload, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    write_text_lf(path, "\n".join(lines) + "\n")


def run_builder(
    tmp_path: Path,
    ledger_rows: list[dict],
    macro_rows: list[dict],
    micro_rows: list[dict] | None = None,
    *,
    strict: bool = False,
    include_labels: bool = False,
) -> tuple[subprocess.CompletedProcess, Path]:
    if micro_rows is None:
        micro_rows = [{"micro_epoch": 0, "range_start": sha(1), "range_end": sha(1)}]

    ledger_path = tmp_path / "ledger.jsonl"
    macro_path = tmp_path / "macro.json"
    micro_path = tmp_path / "micro.json"
    labels_path = tmp_path / "labels.json"
    out_path = tmp_path / "out.md"

    write_jsonl(ledger_path, ledger_rows)
    write_json(macro_path, macro_rows)
    write_json(micro_path, micro_rows)
    if include_labels:
        write_json(labels_path, [{"micro_epoch": 0, "label": "demo"}])

    cmd = [
        sys.executable,
        str(BUILDER_PATH),
        "--ledger",
        str(ledger_path),
        "--macro-epochs",
        str(macro_path),
        "--micro-epochs",
        str(micro_path),
        "--micro-labels",
        str(labels_path),
        "--out",
        str(out_path),
    ]
    if strict:
        cmd.append("--strict")
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc, out_path


def test_directory_normalization_and_casefold_and_no_filename_detection():
    module = load_builder_module()

    assert module.normalize_prefix("foo.d/bar.py") == ("foo.d/bar.py", "foo.d/bar.py")
    assert module.normalize_prefix("SRC\\Core\\Main") == ("src/core", "SRC/Core")
    assert module.normalize_prefix("./a/b/c.txt") == ("a/b", "a/b")
    assert module.normalize_prefix("/") == ("./", "./")
    assert module.normalize_prefix("./") == ("./", "./")


def test_tag_normalization_and_empty_drop():
    module = load_builder_module()

    assert module.normalize_tag("  Alpha  ") == ("alpha", "Alpha")
    assert module.normalize_tag("   ") is None
    assert module.normalize_tag(42) == ("42", "42")


def test_subject_phrase_top10_order_and_bigrams_first():
    module = load_builder_module()

    bigrams = module.Counter({"alpha beta": 4, "beta gamma": 4, "delta epsilon": 2})
    unigrams = module.Counter({"alpha": 9, "beta": 8, "gamma": 7})
    phrases = module.top_phrases_for_candidate(unigrams, bigrams)
    assert phrases[:3] == [("alpha beta", 4), ("beta gamma", 4), ("delta epsilon", 2)]

    phrases_fallback = module.top_phrases_for_candidate(module.Counter({"alpha": 2, "beta": 3}), module.Counter())
    assert phrases_fallback == [("beta", 3), ("alpha", 2)]


def test_builder_byte_stable_lf_and_trailing_newline(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha module", ["A/X"], ["T1"]),
        ledger_row(2, "alpha module", ["A/X"], ["T1"]),
    ]
    macro = [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(2)}]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr

    first = out_path.read_bytes()
    proc, _ = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    second = out_path.read_bytes()

    assert first == second
    assert b"\r\n" not in first
    assert first.endswith(b"\n")


def test_unresolved_reason_enum_strict_coercion_precedence(tmp_path: Path):
    rows = [ledger_row(1, "alpha", ["A/X"], ["T1"])]
    # Coercion required (start_hash/end_hash) and boundary missing, strict must win.
    macro = [{"macro_epoch": 0, "start_hash": sha(99), "end_hash": sha(99)}]
    proc, out_path = run_builder(tmp_path, rows, macro, strict=True)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")
    assert "Unresolved Reason: EPOCH_COERCION_REQUIRED_STRICT" in text


def test_unresolved_reason_commit_hash_precedence(tmp_path: Path):
    rows = [
        ledger_row(
            1,
            "alpha",
            ["A/X"],
            ["T1"],
            commit_value="NOT_A_SHA",
        )
    ]
    macro = [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(1)}]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")
    # Boundary SHA lookup precedence remains before commit-hash invalidation.
    assert "Unresolved Reason: EPOCH_BOUNDARY_SHA_NOT_FOUND" in text


def test_invalid_commit_sha_is_epoch_scoped(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha run", ["A/X"], ["T1"]),
        ledger_row(2, "alpha run", ["A/X"], ["T1"], commit_value="NOT_A_SHA"),
        ledger_row(3, "alpha run", ["A/X"], ["T1"]),
        ledger_row(4, "beta run", ["B/Y"], ["T2"]),
    ]
    macro = [
        {"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(3)},
        {"epoch_id": "E-2", "range_start": sha(4), "range_end": sha(4)},
    ]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    assert "| E-1 | 0 | — | 0.00% | — | 0.00% | UNRESOLVED |" in text
    assert "| E-2 | 1 | B/Y | 100.00% | T2 | 100.00% | OK |" in text
    epoch_1_section = text.split("### Epoch E-1", 1)[1].split("### Epoch E-2", 1)[0]
    assert "Unresolved Reason: COMMIT_HASH_MISSING_OR_INVALID" in epoch_1_section
    epoch_2_section = text.split("### Epoch E-2", 1)[1]
    assert "Unresolved Reason:" not in epoch_2_section
    assert "#### MOD-" in epoch_2_section


def test_rule_thresholds_and_cluster_k_trigger(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha build", ["A/X", "B/Y"], ["T1"]),
        ledger_row(2, "alpha build", ["A/X", "B/Y"], ["T1"]),
        ledger_row(3, "alpha build", ["A/X", "B/Y", "C/Z"], []),
        ledger_row(4, "gamma patch", ["A/X"], []),
        ledger_row(5, "delta patch", ["C/Z"], []),
    ]
    macro = [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(5)}]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    assert "DIR:a/x" in text
    assert "DIR:b/y" in text
    assert "DIR:c/z" in text  # exactly 2/5 => 40%
    assert "TAG:t1" in text   # exactly 2/5 => 40%
    assert "CLUSTER:a/x|b/y" in text  # pair appears in 3 commits


def test_rule_c_match_uses_cluster_edge_set_any_edge(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha beta", ["A/X", "B/Y"], []),
        ledger_row(2, "alpha beta", ["A/X", "B/Y"], []),
        ledger_row(3, "alpha beta", ["A/X", "B/Y"], []),
        ledger_row(4, "beta gamma", ["B/Y", "C/Z"], []),
        ledger_row(5, "beta gamma", ["B/Y", "C/Z"], []),
        ledger_row(6, "beta gamma", ["B/Y", "C/Z"], []),
    ]
    macro = [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(6)}]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    assert "CLUSTER:a/x|b/y|c/z" in text
    # Edge-based support should include all six commits.
    assert "(support: 6/6)" in text


def test_summary_tie_break_and_empty_handling(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha", ["B/Y"], ["y"]),
        ledger_row(2, "beta", ["A/X"], ["x"]),
    ]
    macro = [
        {"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(2)},
        {"epoch_id": "E-2", "range_start": sha(99), "range_end": sha(99)},
    ]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    # For E-1 ties, lexicographic canonical key asc selects a/x and x.
    assert "| E-1 | 2 | A/X | 50.00% | x | 50.00% | OK |" in text
    assert "| E-2 | 0 | — | 0.00% | — | 0.00% | UNRESOLVED |" in text


def test_module_ids_global_monotonic_across_epochs(tmp_path: Path):
    rows = [
        ledger_row(1, "alpha run", ["A/X"], ["T1"]),
        ledger_row(2, "alpha run", ["A/X"], ["T1"]),
        ledger_row(3, "beta run", ["B/Y"], ["T2"]),
        ledger_row(4, "beta run", ["B/Y"], ["T2"]),
    ]
    macro = [
        {"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(2)},
        {"epoch_id": "E-2", "range_start": sha(3), "range_end": sha(4)},
    ]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    assert "#### MOD-01" in text
    assert "#### MOD-02" in text
    assert text.count("#### MOD-01") == 1


def test_dominant_tables_top10_and_order(tmp_path: Path):
    rows: list[dict] = []
    for i in range(1, 12):
        rows.append(ledger_row(i, f"commit {i}", [f"D{i}/X"], ["COMMON"]))
    macro = [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(11)}]
    proc, out_path = run_builder(tmp_path, rows, macro)
    assert proc.returncode == 0, proc.stderr
    text = out_path.read_text(encoding="utf-8")

    block = text.split("Dominant Directories", 1)[1]
    table_rows = re.findall(r"^\| D\d+/X \| 1 \| 9\.09% \|$", block, flags=re.MULTILINE)
    assert len(table_rows) == 10
    # Canonical lexical key order keeps D11/X and drops D9/X when limiting to top 10.
    assert "| D11/X | 1 | 9.09% |" in block
    assert "| D9/X | 1 | 9.09% |" not in block


def test_input_json_invalid_error(tmp_path: Path):
    ledger_path = tmp_path / "ledger.jsonl"
    macro_path = tmp_path / "macro.json"
    micro_path = tmp_path / "micro.json"
    out_path = tmp_path / "out.md"
    write_text_lf(ledger_path, "{bad-json}\n")
    write_json(macro_path, [{"epoch_id": "E-1", "range_start": sha(1), "range_end": sha(1)}])
    write_json(micro_path, [{"micro_epoch": 0, "range_start": sha(1), "range_end": sha(1)}])

    proc = subprocess.run(
        [
            sys.executable,
            str(BUILDER_PATH),
            "--ledger",
            str(ledger_path),
            "--macro-epochs",
            str(macro_path),
            "--micro-epochs",
            str(micro_path),
            "--out",
            str(out_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.returncode == 1
    assert "INPUT_JSON_INVALID" in proc.stderr
