#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
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
DET_HIGH_SEGMENTS = (
    "/sentinel/",
    "/seal/",
    "/manifest/",
    "/hash/",
    "/ledger/",
    "/verify",
    "/audit",
    "/governance/",
)
DET_HIGH_FILENAME_TOKENS = (
    "sentinel",
    "seal",
    "manifest",
    "sha256",
    "ledger",
    "classify",
    "verify",
    "audit",
)


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


def path_contains_docs_segment(path: str) -> bool:
    lower = path.lower()
    return lower == "docs" or lower.startswith("docs/") or "/docs/" in lower


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

    if not classes:
        classes.add("UNKNOWN")

    return classes


def compute_tags_for_path(path: str, classes_for_path: set[str]) -> list[str]:
    normalized = normalize_path(path)
    lower = normalized.lower()
    tags: set[str] = set()

    # SURFACE tags (accumulate)
    if normalized.startswith("reports/") or normalized.startswith("sql/"):
        tags.add("SURFACE_EVIDENCE")
    if normalized.startswith("docs/"):
        tags.add("SURFACE_DOCS")
    if (
        normalized.startswith("docs/contracts/")
        or normalized.startswith("docs/governance/")
        or normalized.startswith("docs/phase_2_2/")
    ):
        tags.add("SURFACE_GOVERNANCE")
    if normalized.startswith("scripts/") or normalized.startswith("src/"):
        tags.add("SURFACE_RUNTIME")
    if normalized.startswith("tests/"):
        tags.add("SURFACE_TEST")
    if normalized.startswith(".github/workflows/"):
        tags.add("SURFACE_CI")
    if normalized.startswith("tools/phase3_control_panel/"):
        tags.add("SURFACE_UI")
    if normalized.startswith("infra/"):
        tags.add("SURFACE_INFRA")
    if normalized.startswith("data/"):
        tags.add("SURFACE_DATA")

    # POWER tag (exactly one; first match wins)
    suffix = Path(lower).suffix
    if suffix in DOC_EXTENSIONS or path_contains_docs_segment(normalized):
        tags.add("POWER_NONE")
    elif normalized.startswith(".github/workflows/") or normalized.startswith(".codex/CHECKS/"):
        tags.add("POWER_CI_ENFORCING")
    elif normalized.startswith("src/"):
        tags.add("POWER_RUNTIME")
    elif (
        normalized.startswith("scripts/")
        or normalized.startswith("tools/")
        or normalized.startswith("tests/")
    ):
        tags.add("POWER_LOCAL")
    elif normalized.startswith("reports/") or normalized.startswith("sql/"):
        tags.add("POWER_NONE")
    else:
        tags.add("POWER_LOCAL")

    # DET tag (exactly one; first match wins)
    padded = f"/{lower}"
    filename = Path(lower).name
    if any(segment in padded for segment in DET_HIGH_SEGMENTS) or any(
        token in filename for token in DET_HIGH_FILENAME_TOKENS
    ):
        tags.add("DET_HIGH")
    elif normalized.startswith("scripts/") or normalized.startswith("tools/") or normalized.startswith("src/"):
        tags.add("DET_MED")
    else:
        tags.add("DET_LOW")

    # REVIEW tags (accumulate; mirrors class triggers)
    if "B" in classes_for_path:
        tags.add("REVIEW_RATIFICATION")
    if "C" in classes_for_path:
        tags.add("REVIEW_AUDIT_PACK")
    if "D" in classes_for_path:
        tags.add("REVIEW_UI_AUDIT")
    if "E" in classes_for_path:
        tags.add("REVIEW_COMPATIBILITY")
    if classes_for_path == {"UNKNOWN"}:
        tags.add("REVIEW_UNKNOWN_PATH")

    return sorted(tags)


def aggregate_tags(files: list[dict]) -> dict:
    counts: Counter[str] = Counter()
    for row in files:
        for tag in row.get("tags", []):
            counts[tag] += 1
    ordered_tags = sorted(counts)
    ordered_counts = {tag: counts[tag] for tag in ordered_tags}
    return {"tags": ordered_tags, "tag_counts": ordered_counts}


def classify_paths(paths: Iterable[str]) -> dict:
    normalized_paths = sorted({normalize_path(path) for path in paths if normalize_path(path)})
    class_set: set[str] = set()
    unknown_paths: list[str] = []
    file_classifications: list[dict] = []

    for path in normalized_paths:
        path_classes = classify_path(path)
        ordered_path_classes = [name for name in CLASS_ORDER if name in path_classes]
        path_tags = compute_tags_for_path(path, path_classes)
        file_classifications.append(
            {
                "path": path,
                "classes": ordered_path_classes,
                "tags": path_tags,
            }
        )
        class_set.update(path_classes)
        if "UNKNOWN" in path_classes:
            unknown_paths.append(path)

    ordered_classes = [name for name in CLASS_ORDER if name in class_set]
    required = {name: REQUIRED_BY_CLASS[name] for name in ordered_classes}
    tag_payload = aggregate_tags(file_classifications)

    return {
        "classes": ordered_classes,
        "required": required,
        "files": len(normalized_paths),
        "paths": normalized_paths,
        "unknown_paths": unknown_paths,
        "file_classifications": file_classifications,
        "tags": tag_payload["tags"],
        "tag_counts": tag_payload["tag_counts"],
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


def collect_paths_from_stdin() -> list[str]:
    return [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify changed paths by governance change taxonomy.")
    parser.add_argument("--staged", action="store_true", help="Use git diff against index (--cached).")
    parser.add_argument("--base", help="Base ref for diff mode: git diff --name-only <ref>...HEAD.")
    parser.add_argument("--range", dest="range_spec", help="--range A..B (runs git diff --name-only A B)")
    parser.add_argument(
        "--paths-from-stdin",
        action="store_true",
        help="Read newline-separated paths from stdin for classification/testing.",
    )
    parser.add_argument("--allow-unknown", action="store_true", help="Allow UNKNOWN class without failing.")
    parser.add_argument(
        "--fail-on",
        action="append",
        default=[],
        metavar="CLASS",
        help="Exit 3 if computed classes include CLASS. Repeatable.",
    )
    parser.add_argument(
        "--fail-on-tag",
        action="append",
        default=[],
        metavar="TAG",
        help="Exit 1 if computed tags include TAG. Repeatable.",
    )
    parser.add_argument(
        "--deny-tag",
        action="append",
        default=[],
        metavar="TAG",
        help="Alias of --fail-on-tag. Repeatable.",
    )
    parser.add_argument(
        "--require-tag",
        action="append",
        default=[],
        metavar="TAG",
        help="Exit 1 unless at least one changed file emits TAG. Repeatable.",
    )
    parser.add_argument(
        "--verbose-tags",
        action="store_true",
        help="Emit per-file tag lines in text mode.",
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
    if args.paths_from_stdin and (args.staged or args.base or args.range_spec):
        raise ValueError("--paths-from-stdin is mutually exclusive with --staged/--base/--range")
    if args.out and not args.json:
        raise ValueError("--out requires --json")

    normalized_fail_on = []
    for value in args.fail_on:
        class_name = value.upper()
        if class_name not in CLASS_ORDER:
            raise ValueError(f"invalid --fail-on class: {value}")
        normalized_fail_on.append(class_name)
    args.fail_on = normalized_fail_on

    args.fail_on_tag = [value.upper() for value in [*args.fail_on_tag, *args.deny_tag]]
    args.require_tag = [value.upper() for value in args.require_tag]
    return args


def determine_exit_code(
    classes: list[str],
    allow_unknown: bool,
    fail_on: list[str],
    tags: list[str] | None = None,
    fail_on_tag: list[str] | None = None,
    require_tag: list[str] | None = None,
) -> int:
    if "UNKNOWN" in classes and not allow_unknown:
        return 2
    if any(name in classes for name in fail_on):
        return 3

    tag_set = set(tags or [])
    if any(tag in tag_set for tag in (fail_on_tag or [])):
        return 1
    if any(tag not in tag_set for tag in (require_tag or [])):
        return 1
    return 0


def print_text_output(payload: dict, verbose_tags: bool) -> None:
    classes = payload["classes"]
    print(f"CLASS={','.join(classes)}")
    for class_name in classes:
        print(f"REQUIRED({class_name})={payload['required'][class_name]}")
    print(f"TAGS={','.join(payload['tags'])}")
    if verbose_tags:
        for row in payload["file_classifications"]:
            print(f"TAGS({row['path']})={','.join(row['tags'])}")
    print(f"FILES={payload['files']}")


def emit_json(payload: dict, out_path: str | None) -> None:
    if out_path:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        if args.paths_from_stdin:
            paths = collect_paths_from_stdin()
            mode = "stdin"
            base_ref = None
        else:
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
            "file_classifications": result["file_classifications"],
            "tags": result["tags"],
            "tag_counts": result["tag_counts"],
        }

        if args.json:
            emit_json(payload, args.out)
        else:
            print_text_output(payload, verbose_tags=args.verbose_tags)

        return determine_exit_code(
            classes=payload["classes"],
            allow_unknown=args.allow_unknown,
            fail_on=args.fail_on,
            tags=payload["tags"],
            fail_on_tag=args.fail_on_tag,
            require_tag=args.require_tag,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
