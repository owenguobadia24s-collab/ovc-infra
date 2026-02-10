#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


CLASS_ORDER = ["A", "B", "C", "D", "E", "UNKNOWN"]
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}
REQUIRED_BY_CLASS = {
    "A": "none",
    "B": "Ratification required; Attach validator/audit outcome reference",
    "C": "Audit pack required; Determinism required for generators/sealers",
    "D": "Phase3 audits required: read-only, no-network-mutation, UI-action",
    "E": "Declare intent; Run workflow sanity if CI/line-endings affected",
    "UNKNOWN": "Unmapped path patterns detected",
}


def run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed"
        raise RuntimeError(detail)
    return proc.stdout


def ref_exists(ref: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def normalize_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def is_tools_pure_doc(path: str) -> bool:
    lower = path.lower()
    if not lower.startswith("tools/"):
        return False
    if Path(lower).suffix in DOC_EXTENSIONS:
        return True
    parts = lower.split("/")
    return "docs" in parts[1:-1]


def is_tools_compat_shim(path: str) -> bool:
    lower = path.lower()
    if not lower.startswith("tools/"):
        return False
    return any("shim" in part for part in lower.split("/") if part)


def classify_path(path: str) -> set[str]:
    classes: set[str] = set()

    if path.startswith("reports/path1/") or path.startswith("sql/path1/"):
        classes.add("A")

    if (
        path.startswith("docs/contracts/")
        or path.startswith("docs/governance/")
        or path.startswith("docs/phase_2_2/")
    ):
        classes.add("B")

    if (
        path.startswith("scripts/")
        or path.startswith("src/")
        or path.startswith("tests/")
        or path.startswith(".github/workflows/")
        or path.startswith(".codex/CHECKS/")
    ):
        classes.add("C")

    if path.startswith("tools/") and not is_tools_pure_doc(path):
        classes.add("C")

    if path.startswith("tools/phase3_control_panel/"):
        classes.add("D")

    if (
        path == ".gitattributes"
        or path == ".gitignore"
        or path.startswith(".github/workflows/")
        or is_tools_compat_shim(path)
    ):
        classes.add("E")

    # ---- v0.2 additive rules (BEGIN) ----

    # B: all docs/ (contracts/governance/phase_2_2 already matched above)
    if path.startswith("docs/"):
        classes.add("B")

    # B: top-level contracts/
    if path.startswith("contracts/"):
        classes.add("B")

    # B: specs/
    if path.startswith("specs/"):
        classes.add("B")

    # B: reports/ non-path1 (path1 already A above)
    if path.startswith("reports/") and not path.startswith("reports/path1/"):
        classes.add("B")

    # B: releases/
    if path.startswith("releases/"):
        classes.add("B")

    # B: root-level documentation files
    if "/" not in path and Path(path).suffix.lower() in DOC_EXTENSIONS:
        classes.add("B")

    # C: sql/ non-path1 (path1 already A above)
    if path.startswith("sql/") and not path.startswith("sql/path1/"):
        classes.add("C")

    # C: all .codex/ (CHECKS/ already matched above)
    if path.startswith(".codex/"):
        classes.add("C")

    # C: infra/
    if path.startswith("infra/"):
        classes.add("C")

    # C: pine/
    if path.startswith("pine/"):
        classes.add("C")

    # C: Tetsu/
    if path.startswith("Tetsu/"):
        classes.add("C")

    # C: trajectory_families/
    if path.startswith("trajectory_families/"):
        classes.add("C")

    # C: _archive/
    if path.startswith("_archive/"):
        classes.add("C")

    # C: _quarantine/
    if path.startswith("_quarantine/"):
        classes.add("C")

    # C: configs/
    if path.startswith("configs/"):
        classes.add("C")

    # C: schema/
    if path.startswith("schema/"):
        classes.add("C")

    # A: artifacts/ (evidence/validation outputs)
    if path.startswith("artifacts/"):
        classes.add("A")

    # E: .github/ non-workflows (repo config)
    if path.startswith(".github/") and not path.startswith(".github/workflows/"):
        classes.add("E")

    # E: .vscode/
    if path.startswith(".vscode/"):
        classes.add("E")

    # E: ovc-webhook/ (editor config)
    if path.startswith("ovc-webhook/"):
        classes.add("E")

    # ---- v0.2 additive rules (END) ----

    if not classes:
        classes.add("UNKNOWN")

    return classes


def classify_paths(paths: Iterable[str]) -> dict:
    normalized_paths = sorted({normalize_path(path) for path in paths if normalize_path(path)})
    class_set: set[str] = set()
    unknown_paths: list[str] = []

    for path in normalized_paths:
        path_classes = classify_path(path)
        class_set.update(path_classes)
        if "UNKNOWN" in path_classes:
            unknown_paths.append(path)

    ordered_classes = [name for name in CLASS_ORDER if name in class_set]
    required = {name: REQUIRED_BY_CLASS[name] for name in ordered_classes}

    return {
        "classes": ordered_classes,
        "required": required,
        "files": len(normalized_paths),
        "paths": normalized_paths,
        "unknown_paths": unknown_paths,
    }


def resolve_default_base_ref() -> str:
    try:
        upstream = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]).strip()
        if upstream:
            return upstream
    except RuntimeError:
        pass

    for candidate in ("origin/main", "main"):
        if ref_exists(candidate):
            return candidate
    raise RuntimeError("could not resolve base ref from upstream, origin/main, or main")


def parse_range_spec(range_spec: str) -> tuple[str, str]:
    if "..." in range_spec:
        raise ValueError("--range must use two-dot syntax A..B; triple-dot is not allowed")
    if range_spec.count("..") != 1:
        raise ValueError("--range must be in A..B form")
    start, end = range_spec.split("..", 1)
    start = start.strip()
    end = end.strip()
    if not start or not end:
        raise ValueError("--range must be in A..B form")
    if start.endswith(".") or end.startswith("."):
        raise ValueError("--range must be in A..B form")
    return start, end


def collect_changed_paths(
    staged: bool,
    base_ref: str | None,
    range_spec: str | None,
) -> tuple[list[str], str, str | None]:
    if staged:
        output = run_git(["diff", "--name-only", "--cached"])
        mode = "staged"
        resolved_base = None
    elif range_spec:
        range_start, range_end = parse_range_spec(range_spec)
        output = run_git(["diff", "--name-only", range_start, range_end])
        mode = "range"
        resolved_base = range_start
    else:
        resolved_base = base_ref or resolve_default_base_ref()
        output = run_git(["diff", "--name-only", f"{resolved_base}...HEAD"])
        mode = "base"

    paths = [line.strip() for line in output.splitlines() if line.strip()]
    return paths, mode, resolved_base


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify changed paths by governance change taxonomy.")
    parser.add_argument("--staged", action="store_true", help="Use git diff against index (--cached).")
    parser.add_argument("--base", help="Base ref for diff mode: git diff --name-only <ref>...HEAD.")
    parser.add_argument("--range", dest="range_spec", help="--range A..B (runs git diff --name-only A B)")
    parser.add_argument("--allow-unknown", action="store_true", help="Allow UNKNOWN class without failing.")
    parser.add_argument(
        "--fail-on",
        action="append",
        default=[],
        metavar="CLASS",
        help="Exit 3 if computed classes include CLASS. Repeatable.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    parser.add_argument("--out", help="Write JSON payload to this path (requires --json).")

    args = parser.parse_args(argv)

    if args.staged and args.base:
        raise ValueError("--staged and --base are mutually exclusive")
    if args.staged and args.range_spec:
        raise ValueError("--staged and --range are mutually exclusive")
    if args.base and args.range_spec:
        raise ValueError("--base and --range are mutually exclusive")
    if args.out and not args.json:
        raise ValueError("--out requires --json")

    normalized_fail_on = []
    for value in args.fail_on:
        class_name = value.upper()
        if class_name not in CLASS_ORDER:
            raise ValueError(f"invalid --fail-on class: {value}")
        normalized_fail_on.append(class_name)
    args.fail_on = normalized_fail_on
    return args


def determine_exit_code(classes: list[str], allow_unknown: bool, fail_on: list[str]) -> int:
    if "UNKNOWN" in classes and not allow_unknown:
        return 2
    if any(name in classes for name in fail_on):
        return 3
    return 0


def print_text_output(payload: dict) -> None:
    classes = payload["classes"]
    print(f"CLASS={','.join(classes)}")
    for class_name in classes:
        print(f"REQUIRED({class_name})={payload['required'][class_name]}")
    print(f"FILES={payload['files']}")


def emit_json(payload: dict, out_path: str | None) -> None:
    if out_path:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        paths, mode, base_ref = collect_changed_paths(
            staged=args.staged,
            base_ref=args.base,
            range_spec=args.range_spec,
        )
        result = classify_paths(paths)

        payload = {
            "classes": result["classes"],
            "required": result["required"],
            "files": result["files"],
            "paths": result["paths"],
            "unknown_paths": result["unknown_paths"],
            "mode": mode,
            "base_ref": base_ref,
        }

        print_text_output(payload)
        if args.json:
            emit_json(payload, args.out)

        return determine_exit_code(
            classes=payload["classes"],
            allow_unknown=args.allow_unknown,
            fail_on=args.fail_on,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
