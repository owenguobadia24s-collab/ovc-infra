# Post-Path1 Roadmap (v0.1)

Status: draft scaffold (non-canonical)
Scope: Plan and scaffolding for components that read Path1 without modifying it.

---

## 1) Enablement Step (Path1 -> Sensor Mode)

Goal: Move Path1 to scheduled execution (every 6 hours) with stable, low-noise operation.

Description (no code changes required yet):
- Schedule: run Path1 at a 6h cadence (00:00, 06:00, 12:00, 18:00 UTC).
- Normal behavior:
  - SKIPPED is expected frequently when no new evidence is queued.
  - Failure rate should be near-zero; failures indicate data availability or environment drift.
  - Summary appears each run (non-canonical) regardless of outcome.
- Unhealthy signals:
  - Repeated failures across runs (>=2 consecutive failures).
  - Non-deterministic summary outputs for identical inputs.
  - Missing or incomplete run artifacts for EXECUTED outcomes.
  - Unexpected queue mutations or ledger divergence.

---

## 2) Path1 Replay Verification (New Component)

Purpose: prove ledger reproducibility without touching Path1 artifacts.

Modes:
- Structural replay:
  - Validate layout and metadata invariants.
  - Confirm required files exist, checksum manifest is present, metadata matches INDEX.
- Recompute replay (optional, expensive):
  - Re-run studies for a given run_id to confirm reproducibility.
  - Compare fresh outputs to stored outputs (exact or tolerant diff).

Location and entrypoint:
- Location: `scripts/path1_replay/` (new, separate from Path1 runner).
- Entrypoint: `scripts/path1_replay/run_replay_verification.py`

Inputs:
- `--repo-root` (default: `.`)
- `--run-id` (single run) or `--all` (iterate ledger)
- `--mode` (`structural` | `recompute`)
- `--strict` (fail on any mismatch)

Outputs:
- Console report (machine-parseable line prefix)
- Optional JSON report written to `artifacts/path1_replay_report.json`

Invariant:
- Reads Path1 ledger only.
- NEVER writes to Path1 run folders or INDEX.

Example CLI (sketch only):
```
python scripts/path1_replay/run_replay_verification.py --run-id p1_20260120_019 --mode structural --strict
```

---

## 3) Run Hashing / Immutability Seals

Goal: deterministic, boring, auditable seals for each run.

Mechanism:
- Per-run manifest file: `reports/path1/evidence/runs/<run_id>/MANIFEST.sha256`
- Hash algorithm: SHA-256 (fixed, documented)

Included files (example set):
- `RUN.md`
- `*_evidence.md`
- `outputs/*.txt`
- `outputs/evidence_pack_v0_2/*` (if present)

Excluded files:
- Transient logs
- Non-deterministic timestamps outside required metadata
- Any generated cache files

Verification:
- Replay verifier recomputes hashes and compares against MANIFEST.
- Manifest is append-only; never rewritten once created.

Rules:
- Seals do not modify Path1 ledger semantics.
- If a seal is missing, verifier reports it; it never creates or fixes it.
- Manifest canonicalization rule: manifest lines are sorted lexicographically by relative path, format sha256 <relpath> (two spaces), LF endings.
---

## 4) Path2 -- Comparative Scoring Layer (New Ledger)

Role:
- Interpretation/scoring layer that compares or ranks evidence.
- Separate canonical ledger; NOT an extension of Path1.

Canonical storage (proposal):
- `reports/path2/INDEX.md` (append-only)
- `reports/path2/runs/<run_id>/` (Path2 run outputs)
- `reports/path2/scores/<score_id>/` (scoring outputs and notes)

Traceability requirements:
- Each Path2 score must reference:
  - Source Path1 run(s)
  - Scoring formula version
  - Input artifacts used

Allowed changes:
- New scoring specs, formulas, and evaluation logic within Path2 only.

Not allowed:
- Any mutation of Path1 runs, INDEX, or layout.
- Rewriting historical Path1 artifacts.

---

## 5) Versioning & Governance Rules

Versioning:
- Scoring specs: `specs/path2/scoring/<name>_vX_Y.md`
- Formulas: `sql/path2/formulas/<name>_vX_Y.sql` or `scripts/path2/formulas/<name>_vX_Y.py`
- Replay logic: `scripts/path1_replay/` versioned via `VERSION` constant

Breaking changes:
- Require explicit version bump and compatibility note.
- Old results remain immutable; new versions produce new Path2 entries.

Re-evaluation:
- Never overwrite historical results.
- If re-evaluated, create new Path2 run with new version tag and references.

---

## 6) What NOT To Do (Yet)

Out of bounds:
- Premature optimization (risk: obscures determinism).
- Folding Path2 into Path1 (risk: contaminates canonical ledger).
- Expanding cadence too early (risk: operational noise and false failures).
- Storing health/ops data in Path1 ledger (risk: blurs canonical boundary).

Rationale: preserve Path1 as a measurement instrument and keep Path2 as a separate, auditable layer.
