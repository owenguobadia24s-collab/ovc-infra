# CHANGE TAXONOMY v0.2

## 1. Purpose

Define deterministic, path-based tag overlays on top of v0.1 classes so contributors and CI can identify review and determinism requirements without changing class trigger behavior.

## 2. Scope

This taxonomy applies to changed file paths in this repository as classified by `scripts/governance/classify_change.py`.

v0.2 is an overlay:

- v0.1 class trigger logic is preserved.
- v0.2 adds tags only.

## 3. Class Compatibility (v0.1 preserved)

Class trigger conditions remain unchanged for:

- `A`
- `B`
- `C`
- `D`
- `E`
- `UNKNOWN`

Classes are emitted in fixed order:

- `A,B,C,D,E,UNKNOWN`

## 4. Tag Families and Rules (Path-Only, Deterministic)

Tag rules are path-only and deterministic.

### A) SURFACE TAGS (accumulate; 0..n per file)

- reports/ or sql/ => SURFACE_EVIDENCE
- docs/ => SURFACE_DOCS
- docs/contracts/ or docs/governance/ or docs/phase_2_2/ => SURFACE_GOVERNANCE
- scripts/ or src/ => SURFACE_RUNTIME
- tests/ => SURFACE_TEST
- .github/workflows/ => SURFACE_CI
- tools/phase3_control_panel/ => SURFACE_UI
- infra/ => SURFACE_INFRA
- data/ => SURFACE_DATA

### B) POWER TAG (choose exactly 1 per file; first-match-wins)

1) ext in {".md",".txt",".rst",".adoc"} OR contains "/docs/" segment => POWER_NONE
2) startswith ".github/workflows/" OR startswith ".codex/CHECKS/" => POWER_CI_ENFORCING
3) startswith "src/" => POWER_RUNTIME
4) startswith "scripts/" OR "tools/" OR "tests/" => POWER_LOCAL
5) startswith "reports/" OR "sql/" => POWER_NONE
6) else => POWER_LOCAL

### C) DET TAG (choose exactly 1 per file; first-match-wins)

1) if path contains any of these segments OR filename contains any of these tokens:
   segments: "/sentinel/","/seal/","/manifest/","/hash/","/ledger/","/verify","/audit","/governance/"
   filename tokens: "sentinel","seal","manifest","sha256","ledger","classify","verify","audit"
   => DET_HIGH
2) else if startswith "scripts/" OR "tools/" OR "src/" => DET_MED
3) else => DET_LOW

### D) REVIEW TAGS (accumulate; mirrors class triggers)

- If Class B triggers => REVIEW_RATIFICATION
- If Class C triggers => REVIEW_AUDIT_PACK
- If Class D triggers => REVIEW_UI_AUDIT
- If Class E triggers => REVIEW_COMPATIBILITY
- If no class triggers (i.e., only UNKNOWN) => REVIEW_UNKNOWN_PATH

## 5. Ordering and Serialization

- Class output ordering is fixed: `A,B,C,D,E,UNKNOWN`.
- Tag output ordering is lexicographic.
- JSON payloads must be serialized deterministically.
- Text and JSON artifacts use LF line endings.

## 6. Enforcement Behavior

- Default exit code behavior is unchanged from v0.1 class enforcement.
- `UNKNOWN` still fails unless `--allow-unknown` is set.
- New optional tag gates may fail on tag conditions only when explicitly enabled by tag flags.
- Tag gates are off by default and do not alter class trigger semantics.

## 7. Output Contract

Text mode:

- Preserve existing v0.1 class output lines.
- Add `TAGS=<comma-separated tags>` after class-required lines.
- Add per-file tags only when `--verbose-tags` is enabled.

JSON mode (`--json`):

- Preserve existing keys.
- Add top-level `tags` and `tag_counts`.
- Add per-file `tags` alongside per-file classification entries.
