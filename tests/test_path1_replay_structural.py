import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = REPO_ROOT / "scripts" / "path1_replay"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from lib import parse_run_md  # noqa: E402


def run_cmd(args):
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_bad_args_exit_code(tmp_path):
    script = REPO_ROOT / "scripts" / "path1_replay" / "run_replay_verification.py"
    result = run_cmd([str(script), "--repo-root", str(tmp_path)])
    assert result.returncode == 3


def test_structural_ok_minimal_run(tmp_path):
    script = REPO_ROOT / "scripts" / "path1_replay" / "run_replay_verification.py"

    runs_root = tmp_path / "reports" / "path1" / "evidence" / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    index_path = tmp_path / "reports" / "path1" / "evidence" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    run_id = "p1_20260101_001"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    run_md = run_dir / "RUN.md"
    run_md.write_text(
        "\n".join(
            [
                "# Path 1 Evidence Run",
                "",
                "| Field | Value |",
                "|-------|-------|",
                "| `run_id` | `p1_20260101_001` |",
                "| `date_range_actual` | `2026-01-01 to 2026-01-05` |",
                "| `symbol(s)` | `GBPUSD` |",
                "| `n_observations` | `10` |",
            ]
        ),
        encoding="utf-8",
    )
    index_path.write_text(f"| {run_id} |", encoding="utf-8")

    result = run_cmd([str(script), "--repo-root", str(tmp_path), "--run-id", run_id])
    assert result.returncode == 0


def test_strict_mode_promotes_warnings_to_failure(tmp_path):
    script = REPO_ROOT / "scripts" / "path1_replay" / "run_replay_verification.py"

    runs_root = tmp_path / "reports" / "path1" / "evidence" / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    index_path = tmp_path / "reports" / "path1" / "evidence" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("| header |", encoding="utf-8")

    run_id = "p1_20260101_002"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    run_md = run_dir / "RUN.md"
    run_md.write_text(
        "\n".join(
            [
                "| Field | Value |",
                "|-------|-------|",
                "| date_range_actual | 2026-01-01 to 2026-01-05 |",
                "| symbol | GBPUSD |",
                "| n_observations | 5 |",
            ]
        ),
        encoding="utf-8",
    )

    result = run_cmd(
        [str(script), "--repo-root", str(tmp_path), "--run-id", run_id, "--strict"]
    )
    assert result.returncode == 2


def test_parse_variants():
    content = "\n".join(
        [
            "| Field | Value |",
            "|-------|-------|",
            "| date_range_actual | 2026-01-01 to 2026-01-05 |",
            "| symbol(s) | GBPUSD |",
            "| n_obs | 10 |",
        ]
    )
    parsed, warnings = parse_run_md(content)
    assert parsed.date_from == "2026-01-01"
    assert parsed.date_to == "2026-01-05"
    assert parsed.symbol == "GBPUSD"
    assert parsed.n_obs == 10
    assert "date_range_actual_missing_using_requested" not in warnings

    content = "\n".join(
        [
            "| Field | Value |",
            "|-------|-------|",
            "| date_start_actual | `2026-02-01` |",
            "| date_end_actual | `2026-02-05` |",
            "| symbol | GBPUSD |",
            "| observations | 7 |",
        ]
    )
    parsed, warnings = parse_run_md(content)
    assert parsed.date_from == "2026-02-01"
    assert parsed.date_to == "2026-02-05"
    assert parsed.n_obs == 7
    assert "date_range_actual_from_start_end" in warnings

    content = "\n".join(
        [
            "| Field | Value |",
            "|-------|-------|",
            "| date_range_start | 2026-04-01 |",
            "| date_range_end | 2026-04-05 |",
            "| symbol | GBPUSD |",
        ]
    )
    parsed, warnings = parse_run_md(content)
    assert parsed.date_from == "2026-04-01"
    assert parsed.date_to == "2026-04-05"
    assert "date_range_actual_from_range_start_end" in warnings

    content = "\n".join(
        [
            "| Field | Value |",
            "|-------|-------|",
            "| date_range_requested | 2026-03-01 to 2026-03-05 |",
            "| symbol | GBPUSD |",
        ]
    )
    parsed, warnings = parse_run_md(content)
    assert parsed.date_from == "2026-03-01"
    assert parsed.date_to == "2026-03-05"
    assert "date_range_actual_missing_using_requested" in warnings
