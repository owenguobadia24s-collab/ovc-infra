#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List


def run(cmd: List[str], cwd: Path, env: dict, label: str) -> None:
    print(f"\n=== RUN: {label} ===")
    print("$ " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd), env=env)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def repo_root_from_here() -> Path:
    # scripts/design_record_engine/run_all.py -> repo root is 3 parents up
    return Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description="Run all Design Record Engine phases in strict order.")
    ap.add_argument(
        "--export-root",
        default="evidence/chat_exports/2026-02-21_export_raw",
        help="Chat export root folder (sealed or to be sealed).",
    )
    ap.add_argument(
        "--artifacts-root",
        default="artifacts/design_record_engine",
        help="Artifacts output root.",
    )
    ap.add_argument(
        "--use-golden",
        action="store_true",
        help="Use golden fixture as export-root (overrides --export-root).",
    )
    ap.add_argument(
        "--seal",
        action="store_true",
        help="Run Phase 0 sealing step before other phases.",
    )
    ap.add_argument(
        "--stop-after-phase0",
        action="store_true",
        help="Stop after Phase 0 (valid only with --seal).",
    )
    ap.add_argument(
        "--stop-after-phase1",
        action="store_true",
        help="Stop after Phase 1.",
    )
    ap.add_argument(
        "--embed",
        action="store_true",
        help="Run embedding phase (requires OPENAI_API_KEY).",
    )
    ap.add_argument(
        "--hosted-vector-store",
        action="store_true",
        help="Run hosted vector store sync phase (requires OPENAI_API_KEY).",
    )
    ap.add_argument(
        "--pytest",
        action="store_true",
        help="Run pytest at the end.",
    )
    args = ap.parse_args()

    root = repo_root_from_here()

    if args.stop_after_phase0 and not args.seal:
        print("ERROR: --stop-after-phase0 requires --seal", file=sys.stderr)
        return 2
    if args.stop_after_phase0 and args.stop_after_phase1:
        print("ERROR: --stop-after-phase0 and --stop-after-phase1 are mutually exclusive", file=sys.stderr)
        return 2

    export_root = Path(args.export_root)
    if args.use_golden:
        export_root = Path("tests/fixtures/chat_export_golden/2026-02-21_export_raw")

    if not export_root.is_absolute():
        export_root = (root / export_root).resolve()
    else:
        export_root = export_root.resolve()

    artifacts_root = Path(args.artifacts_root)
    if not artifacts_root.is_absolute():
        artifacts_root = (root / artifacts_root).resolve()
    else:
        artifacts_root = artifacts_root.resolve()

    export_root_str = export_root.as_posix()
    artifacts_root_str = artifacts_root.as_posix()

    env = dict(os.environ)

    if not export_root.exists() or not export_root.is_dir():
        print(f"ERROR: export root does not exist or is not a directory: {export_root_str}", file=sys.stderr)
        return 2

    try:
        artifacts_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: failed to create artifacts root '{artifacts_root_str}': {exc}", file=sys.stderr)
        return 2

    print(f"INFO: export-root={export_root_str}")
    print(f"INFO: artifacts-root={artifacts_root_str}")

    # Strict phase order:
    # 0 (optional), 1, 2, 3, 4, 6, 7, 8, 9, 5 (optional hosted)
    if args.seal:
        # PowerShell script for Phase 0
        # Note: uses -File so it works consistently in CI
        run(
            ["pwsh", "-NoProfile", "-File", "scripts/design_record_engine/phase0_chat_seal.ps1", "-ExportRoot", export_root_str],
            cwd=root,
            env=env,
            label="Phase 0 — Seal chat export",
        )
        if args.stop_after_phase0:
            print("DONE: Design Record Engine RUN_ALL succeeded")
            return 0

    run(
        ["python", "scripts/design_record_engine/phase1_build_evidence_nodes.py", "--export-root", export_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 1 — evidence_nodes.jsonl",
    )
    if args.stop_after_phase1:
        print("DONE: Design Record Engine RUN_ALL succeeded")
        return 0

    run(
        ["python", "scripts/design_record_engine/phase2_extract_anchors.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 2 — evidence_anchors.jsonl",
    )

    run(
        ["python", "scripts/design_record_engine/phase3_parse_chat_export.py", "--export-root", export_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 3 — chat_nodes/messages",
    )

    if args.embed:
        # Embeddings require OPENAI_API_KEY; fail-closed inside script is expected.
        run(
            ["python", "scripts/design_record_engine/phase4_chunk_and_embed.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
            cwd=root,
            env=env,
            label="Phase 4 — chunks + embeddings",
        )
    else:
        # Always produce chunks in dry-run mode so later phases can still run with local RAG-ish flow.
        run(
            ["python", "scripts/design_record_engine/phase4_chunk_and_embed.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str, "--dry-run"],
            cwd=root,
            env=env,
            label="Phase 4 — chunks only (dry-run)",
        )

    run(
        ["python", "scripts/design_record_engine/phase6_build_graph.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 6 — evidence graph",
    )

    run(
        ["python", "scripts/design_record_engine/phase7_cluster_modules.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 7 — module candidates + borderlands",
    )

    run(
        ["python", "scripts/design_record_engine/phase8_invariants_ledger.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 8 — invariants ledger + chronology",
    )

    run(
        ["python", "scripts/design_record_engine/query_engine.py", "--self-test", "--in-root", artifacts_root_str],
        cwd=root,
        env=env,
        label="Phase 9 — query engine self-test",
    )

    if args.hosted_vector_store:
        run(
            ["python", "scripts/design_record_engine/phase5_vector_store_sync.py", "--in-root", artifacts_root_str, "--out-root", artifacts_root_str],
            cwd=root,
            env=env,
            label="Phase 10 — hosted vector store sync",
        )

    if args.pytest:
        run(["python", "-m", "pytest", "-q"], cwd=root, env=env, label="pytest")

    print("DONE: Design Record Engine RUN_ALL succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
