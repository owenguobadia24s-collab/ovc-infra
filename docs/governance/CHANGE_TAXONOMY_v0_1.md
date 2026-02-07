# CHANGE TAXONOMY v0.1

## 1. Purpose

Define a deterministic, path-based change taxonomy for repository changes so contributors and CI can consistently identify governance and audit requirements.

## 2. Scope

This taxonomy applies to changed file paths in this repository as classified by `scripts/governance/classify_change.py`.

## 3. Change Classes (A–E)

### Class A — Operational Evidence Emission

- Triggers:
  - `reports/path1/**`
  - `sql/path1/**`
- Governance review:
  - Allowed without governance review.
- Required checks:
  - `none`

### Class B — Governance / Contracts / Canon Rules

- Triggers:
  - `docs/contracts/**`
  - `docs/governance/**`
  - `docs/phase_2_2/**`
- Governance review:
  - Ratification-required class.
- Required checks:
  - `Ratification required`
  - `Attach validator/audit outcome reference`

### Class C — Tooling / Pipelines / Enforcement Mechanisms

- Triggers:
  - `scripts/**`
  - `src/**`
  - `tests/**`
  - `.github/workflows/**`
  - `.codex/CHECKS/**`
  - `tools/**` except pure docs
- Pure docs exclusion for `tools/**`:
  - Files with extension `.md`, `.txt`, `.rst`, `.adoc`
  - Files under `tools/**/docs/**`
- Required checks:
  - `Audit pack required`
  - `Determinism required for generators/sealers`

### Class D — UI / Observability Surfaces (Read-Only)

- Triggers:
  - `tools/phase3_control_panel/**`
- Required checks:
  - `Phase3 audits required: read-only, no-network-mutation, UI-action`

### Class E — Repo Hygiene / Compatibility

- Triggers:
  - `.gitattributes`
  - `.gitignore`
  - `.github/workflows/**`
  - Compatibility shims under `tools/**` (path segment or filename contains `shim`, case-insensitive)
- Required checks:
  - `Declare intent`
  - `Run workflow sanity if CI/line-endings affected`

## 4. Enforcement Policy

1. Multi-class output is allowed and expected when paths span categories.
2. If Class D triggers, output must include `D` (not only `C`).
3. If any path matches Class B triggers, output must include `B` even when other classes also match.
4. If any path matches no known pattern, output must include `UNKNOWN`.
   - Default behavior: exit non-zero.
   - With `--allow-unknown`: include `UNKNOWN` and exit success.

Classifier output format:

- First line: `CLASS=<comma-separated classes in stable order A,B,C,D,E,UNKNOWN>`
- Then: `REQUIRED(<class>)=<text>` per class in stable order
- Final line: `FILES=<n>`

## 5. Examples

### Example A-only Path1 run

Changed paths:

- `reports/path1/evidence/runs/p1_20260207_001/RUN.md`
- `sql/path1/evidence/runs/p1_20260207_001/study_res_v1_0.sql`

Expected classes:

- `A`

### Example B contract edit

Changed paths:

- `docs/contracts/option_c_outcomes_contract_v1.md`

Expected classes:

- `B`

### Example mixed A+C requiring split

Changed paths:

- `reports/path1/evidence/runs/p1_20260207_001/RUN.md` (Class A)
- `scripts/path1/build_evidence_pack_v0_2.py` (Class C)

Expected classes:

- `A,C`

Recommended handling:

- Split operational evidence emission changes and tooling/enforcement changes into separate PRs when practical to reduce review scope.

## 6. Tooling

Local staged diff:

```bash
python scripts/governance/classify_change.py --staged
```

CI-style base diff:

```bash
python scripts/governance/classify_change.py --base origin/main
```

Allow unknown paths (non-failing):

```bash
python scripts/governance/classify_change.py --base origin/main --allow-unknown
```

Fail gate on classes:

```bash
python scripts/governance/classify_change.py --base origin/main --fail-on B --fail-on C
```

Machine-readable JSON:

```bash
python scripts/governance/classify_change.py --base origin/main --json --out artifacts/change_classifier.json
```

## 7. Limitations

- The classifier only inspects paths and emits required checks.
- It does not validate PR text, ratification artifacts, or audit references.
- It cannot prove determinism or audit pass/fail results; it only flags when those checks are required.
