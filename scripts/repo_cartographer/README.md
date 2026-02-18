# Repo Cartographer

Deterministic, append-only file ownership classification tool for ovc-infra.

**This tool never moves repository files; it proposes only.**

## Purpose

Enumerates all tracked and untracked-visible files via `git ls-files -z`, classifies each file against the ownership rules defined in `docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json`, and produces sealed, auditable per-run artifacts.

## Commands

```bash
# Enumerate files and print counts
python scripts/repo_cartographer/cartographer.py index

# Classify files and print summary (no file writes)
python scripts/repo_cartographer/cartographer.py classify

# Generate reports to stdout (no file writes)
python scripts/repo_cartographer/cartographer.py report

# Full run: classify + write artifacts + seal + append ledger
python scripts/repo_cartographer/cartographer.py run

# Verify last run against current repo state
python scripts/repo_cartographer/cartographer.py verify
python scripts/repo_cartographer/cartographer.py verify --allow-unknown
```

## Options

- `--rules PATH` — Override ownership rules file (default: `docs/baselines/MODULE_OWNERSHIP_RULES_v0.1.json`)
- `--state PATH` — Override state file (default: `scripts/repo_cartographer/cartographer_state.json`)
- `run --run-id ID` — Override run ID (default: UTC timestamp)
- `verify --run-id ID` — Verify a specific run instead of the latest
- `verify --allow-unknown` — Allow UNKNOWN files without failing

## Optional Manual Pre-Push Verification

This repo cartographer chain is not auto-installed as a git hook. Run manually before pushing:

```bash
python scripts/repo_cartographer/cartographer.py run
python scripts/repo_cartographer/cartographer.py verify
python scripts/repo_cartographer/phase_b_latest_ok_run.py --strict-verify
python scripts/repo_cartographer/phase_b6_publish_latest_ownership_summary.py
python scripts/repo_cartographer/phase_b7_unknown_frontier.py
python scripts/repo_cartographer/phase_c_rule_proposal.py --phase-c-prompt-text "<exact phase-c prompt>"
```

## Invariants

- File enumeration uses `git ls-files -z` (NUL-separated, never OS walking)
- All outputs are deterministic given: HEAD commit, ruleset version, tracked file set, untracked-visible file set
- Run fingerprint = `sha256(head_commit + "\n" + ruleset_sha256 + "\n" + tracked_list_sha256 + "\n" + untracked_visible_list_sha256)`
- Run ledger is append-only (one line per run)
- Classification uses first-match-wins rule evaluation
- Python 3.11, stdlib only (no external dependencies)

## Output Artifacts

Each run produces a sealed folder at `artifacts/repo_cartographer/<run_id>/` containing:

| File | Description |
|------|-------------|
| `REPO_FILE_INDEX_v0.1.jsonl` | One line per file with path, tracking status, extension, size |
| `REPO_FILE_CLASSIFICATION_v0.1.jsonl` | Full classification with module/zone assignment |
| `MODULE_OWNERSHIP_SUMMARY_v0.1.md` | Ownership counts by module, zone, and tracking status |
| `BORDERLANDS_PRESSURE_REPORT_v0.1.md` | Per-borderland file counts and extension distribution |
| `UNTRACKED_VISIBLE_REPORT_v0.1.md` | Untracked-visible files grouped by classification |
| `MOVE_PLAN_PROPOSED_v0.1.json` | Proposed file moves (empty in v0.1) |
| `MANIFEST.json` + `MANIFEST.sha256` | Artifact integrity manifest |
| `SEAL.json` + `SEAL.sha256` | Cryptographic seal over manifest |
