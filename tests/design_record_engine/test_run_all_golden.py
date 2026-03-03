from __future__ import annotations

import subprocess
from pathlib import Path


def test_run_all_golden_fixture(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]

    # We run the orchestrator against golden fixture and seal it.
    # Writes go to the repo artifacts path; this is fine if your CI allows it.
    # If you want isolation, adjust run_all.py to accept --artifacts-root under tmp_path.
    cmd = [
        "python",
        "scripts/design_record_engine/run_all.py",
        "--use-golden",
        "--seal",
    ]
    r = subprocess.run(cmd, cwd=str(repo_root))
    assert r.returncode == 0