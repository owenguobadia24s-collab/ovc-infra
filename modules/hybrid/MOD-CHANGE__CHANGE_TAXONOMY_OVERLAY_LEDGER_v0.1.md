# MOD-CHANGE — Change Taxonomy Overlay Ledger (v0.1)

## Definition
MOD-CHANGE classifies deterministic change taxonomy, overlay generation, classifier output, append-only ledger, and sentinel ingestion surfaces, grounded in `OVC ARCHITECTURAL WAVES v2.md` sections `W5 — Operational Integrity Layer` and `W6 — Machine Audit & Classification Consciousness`, plus `docs/governance/CHANGE_TAXONOMY_v0_2.md`.

Coverage: FULL
Taxonomy contracts, overlay/ledger artifacts, classifier scripts, sentinel scripts, workflows, and tests are present in tracked active paths.

## Wave Span
- W5 — operational drift computability and registry state tracking are required (`OVC ARCHITECTURAL WAVES v2.md`, W5).
- W6 — drift must be classified deterministically (`OVC ARCHITECTURAL WAVES v2.md`, W6).

## Core Invariants
- MUST classify changes deterministically from path evidence.
- MUST preserve append-only change ledger and sealed overlay artifacts.
- MUST NOT infer undocumented change semantics beyond taxonomy rules.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `docs/governance/CHANGE_TAXONOMY_v0_*.md`
- `docs/catalogs/DEV_CHANGE_*`
- `docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json`
- `scripts/governance/classify_change.py`
- `scripts/governance/build_change_classification_overlay_v0_*.py`
- `scripts/governance/install_precommit_change_classifier.sh`
- `scripts/sentinel/**`
- `.github/workflows/change_classifier.yml`
- `.github/workflows/append_sentinel.yml`
- `tests/test_change_classifier.py`
- `tests/test_change_overlay_builder.py`
- `tests/test_append_sentinel.py`
- `CHANGELOG_overlays_v0_3.md`
- `CHANGELOG_overlays_v0_3_hardening.md`
- `CHANGELOG_evidence_pack_provenance.md`
- `artifacts/change_classifier.json`
- `tools/dev_catalog/**`

### Excludes (Path Patterns)
- `_archive/**`
- CHANGELOG_evidence_pack_provenance.md
- CHANGELOG_overlays_v0_3.md
- CHANGELOG_overlays_v0_3_hardening.md

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `docs/governance/CHANGE_TAXONOMY_v0_*.md`
- Attachment rule: attach when file defines class/tag trigger logic and enforcement behavior.
- Evidence reference: `docs/governance/CHANGE_TAXONOMY_v0_1.md`, `docs/governance/CHANGE_TAXONOMY_v0_2.md`.
- Pattern: `scripts/governance/classify_change.py`
- Attachment rule: attach when script emits class output from deterministic path rules.
- Evidence reference: `.github/workflows/change_classifier.yml`.
- Pattern: `scripts/sentinel/**`
- Attachment rule: attach when file appends and verifies sentinel ingestion/ledger surfaces.
- Evidence reference: `.github/workflows/append_sentinel.yml`.

## Primary Directories
- `docs/governance` — taxonomy law and policy; matched by `docs/governance/CHANGE_TAXONOMY_v0_*.md`.
- `docs/catalogs` — overlay/ledger canonical outputs; matched by `docs/catalogs/DEV_CHANGE_*`.
- `scripts/governance` — classifier and overlay builders; matched by explicit script patterns.
- `scripts/sentinel` — append-only sentinel surfaces; matched by `scripts/sentinel/**`.
- `.github/workflows` — classifier and sentinel CI enforcement; matched by explicit workflow paths.
- `tests` — classifier/overlay/sentinel tests; matched by explicit test paths.

## Canonical Artifacts
- contracts: `docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json`, `docs/governance/CHANGE_TAXONOMY_v0_2.md`.
- SQL migrations/views: none required for MOD-CHANGE core ownership.
- Python entrypoints: `scripts/governance/classify_change.py`, `scripts/governance/build_change_classification_overlay_v0_2.py`, `scripts/sentinel/append_sentinel.py`.
- governance docs: `docs/governance/CHANGE_TAXONOMY_v0_1.md`, `docs/governance/CHANGE_TAXONOMY_v0_2.md`, `CHANGELOG_overlays_v0_3.md`.

## Enforcement Hooks
- test files: `tests/test_change_classifier.py`, `tests/test_change_overlay_builder.py`, `tests/test_append_sentinel.py`.
- CI workflows: `.github/workflows/change_classifier.yml`, `.github/workflows/append_sentinel.yml`.
- validators: classifier validation in `scripts/governance/classify_change.py`, sentinel verify mode in `scripts/sentinel/append_sentinel.py`.
- sha256 / seal checks: `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.2.seal.sha256`, `docs/catalogs/DEV_CHANGE_LEDGER_v0.2.seal.sha256`.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: taxonomy and enforcement intentionally span docs, scripts, tests, and workflows.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: root-level changelog artifacts (`CHANGELOG_overlays_v0_3.md`, `CHANGELOG_overlays_v0_3_hardening.md`, `CHANGELOG_evidence_pack_provenance.md`) remain outside `docs/governance/`.

## Change Policy
Allowed:
- additive taxonomy docs
- additive classifier and sentinel tests
- additive versioned overlay/ledger artifacts
- forward-only classifier rule evolution with explicit changelog

Disallowed:
- breaking contract/schema changes without evolution protocol
- bypassing seal checks on ledger/overlay canon artifacts
- silent mutation of class/tag semantics

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/CHANGE_TAXONOMY_v0_2.md`
- `docs/contracts/DEV_CHANGE_LEDGER_SCHEMA_v0.1.json`

## Unassigned / Edge Cases
- `.codex/_scratch/DEV_CHANGE_*` — simulation/scratch overlays, routed to `MOD-UNASSIGNED`.
- `docs/catalogs/OVC_DEVELOPMENT_TIMELINE_v0.2.md` — timeline artifact with mixed ownership, routed to `MOD-UNASSIGNED` unless ratified into module scope.
