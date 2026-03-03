# MOD-D — Evidence System (v0.1)

## Definition
MOD-D classifies Path1 evidence emission, queue execution, replay verification, sealing, overlays, and trajectory/state-plane analysis surfaces, grounded in `OVC ARCHITECTURAL WAVES v2.md` section `W4 — Evidence Integration & CI Hardening` and `PATH1_EXECUTION_MODEL.md`.

Coverage: FULL
Evidence contracts, scripts, SQL run artifacts, report ledger surfaces, replay checks, and CI workflows exist in tracked active paths.

## Wave Span
- W4 — reproducible evidence runs and CI hardening are explicit in `OVC ARCHITECTURAL WAVES v2.md` (`W4 — Evidence Integration & CI Hardening`).
- W5 — run integrity and health attachment extend evidence governance (`W5 — Operational Integrity Layer`).

## Core Invariants
- MUST emit evidence runs through deterministic queue/range scripts and append-only ledgers.
- MUST verify replay/structural integrity without mutating historical run artifacts.
- MUST preserve per-run manifest/seal immutability for evidence folders where seals are present.

## Membership Rules

### Pattern Syntax
All patterns are:
- repo-root relative
- gitignore-style glob
- `**` allowed
- no regex
- no negative lookaheads

### Includes (Path Patterns)
- `PATH1_EXECUTION_MODEL.md`
- `scripts/path1/**`
- `scripts/path1_replay/**`
- `scripts/path1_seal/**`
- `reports/path1/**`
- `sql/path1/**`
- `sql/derived/v_ovc_state_plane*.sql`
- `trajectory_families/**`
- `docs/evidence_pack/**`
- `docs/history/path1/**`
- `docs/path1/**`
- `docs/option_d/**`
- `.github/workflows/path1_*.yml`
- `.github/workflows/main.yml`
- `tests/test_evidence_pack_manifest.py`
- `tests/test_pack_rebuild_equivalence.py`
- `tests/test_path1_replay_structural.py`
- `tests/test_overlays_v0_3_determinism.py`
- docs/OVERLAY_V0_3_HARDENING_SUMMARY.md
- docs/OVERLAY_V0_3_TESTING.md
- docs/evidence_pack_overlays_v0_3.md
- docs/evidence_pack_provenance.md
- docs/contracts/option_d_evidence_contract_v1.md
- docs/contracts/option_d_ops_boundary.md
- CHANGELOG_evidence_pack_provenance.md
- CHANGELOG_overlays_v0_3.md
- CHANGELOG_overlays_v0_3_hardening.md
- CLAIMS/ANCHOR_INDEX_v0_1.csv
- CLAIMS/CLAIM_BINDING_v0_1.md

### Excludes (Path Patterns)
- `_archive/**`
- docs/state_plane/**
- docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md
- research/**
- reports/**
- tests/test_fingerprint*.py
- tests/test_dst_audit.py
- artifacts/path1_replay_report.json
- docs/examples/overlay_v0_3_sample_outputs.md

### Support Linkage Rules (Docs / Tests / Workflows)
- Pattern: `scripts/path1/**` and `reports/path1/**`
- Attachment rule: attach when script emits or indexes Path1 evidence run folders.
- Evidence reference: `PATH1_EXECUTION_MODEL.md`.
- Pattern: `scripts/path1_replay/**`
- Attachment rule: attach when script performs read-only replay verification.
- Evidence reference: `.github/workflows/path1_replay_verify.yml`.
- Pattern: `scripts/path1_seal/**`
- Attachment rule: attach when script generates or validates run manifest seals.
- Evidence reference: `reports/path1/evidence/runs/p1_20260120_001/MANIFEST.sha256`.

## Primary Directories
- `scripts/path1` — canonical evidence execution and overlays; matched by `scripts/path1/**`.
- `scripts/path1_replay` — replay structural verification; matched by `scripts/path1_replay/**`.
- `scripts/path1_seal` — manifest sealing; matched by `scripts/path1_seal/**`.
- `reports/path1` — append-only evidence ledger and runs; matched by `reports/path1/**`.
- `sql/path1` — per-run and study SQL surfaces; matched by `sql/path1/**`.
- `trajectory_families` — trajectory feature/state-plane family logic; matched by `trajectory_families/**`.
- `.github/workflows` — evidence/replay workflow enforcement; matched by `.github/workflows/path1_*.yml` and `.github/workflows/main.yml`.
- `tests` — replay/manifest/overlay deterministic tests; matched by explicit test paths.

## Canonical Artifacts
- contracts: `docs/contracts/option_d_evidence_contract_v1.md`, `docs/contracts/option_d_ops_boundary.md`, `docs/evidence_pack/EVIDENCE_PACK_v0_2.md`.
- SQL migrations/views: `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql`, `sql/path1/scores/score_dis_v1_1.sql`, `sql/path1/studies/dis_stability_quarterly.sql`.
- Python entrypoints: `scripts/path1/run_evidence_queue.py`, `scripts/path1/run_evidence_range.py`, `scripts/path1/build_evidence_pack_v0_2.py`, `scripts/path1_replay/run_replay_verification.py`, `scripts/path1_seal/run_seal_manifests.py`.
- governance docs: `PATH1_EXECUTION_MODEL.md`, `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md`, `docs/history/path1/PATH1_SEALING_PROTOCOL_v0_1.md`.

## Enforcement Hooks
- test files: `tests/test_evidence_pack_manifest.py`, `tests/test_pack_rebuild_equivalence.py`, `tests/test_path1_replay_structural.py`, `tests/test_overlays_v0_3_determinism.py`.
- CI workflows: `.github/workflows/path1_evidence.yml`, `.github/workflows/path1_evidence_queue.yml`, `.github/workflows/path1_replay_verify.yml`, `.github/workflows/main.yml`.
- validators: `scripts/path1/validate_post_run.py`, `scripts/path1_replay/run_replay_verification.py`.
- sha256 / seal checks: `reports/path1/evidence/runs/p1_20260120_001/MANIFEST.sha256`, `scripts/path1_seal/run_seal_manifests.py`.

## Drift / Debt Notes
- `docs/governance/DRIFT_REPORT_v2.md` / `3. Cross-Wave Directories (LOW)`: evidence enforcement spans `docs/`, `scripts/`, `tests/`, and `.github/` by design.
- `docs/governance/DRIFT_REPORT_v2.md` / `1. Organizational Drift (MEDIUM)`: root-level changelog artifacts (`CHANGELOG_evidence_pack_provenance.md`, `CHANGELOG_overlays_v0_3.md`) are related evidence-history surfaces outside `docs/governance/`.

## Change Policy
Allowed:
- additive evidence docs
- additive replay/validation tests
- additive versioned contracts and SQL studies
- forward-only queue and range runner evolution

Disallowed:
- breaking contract changes without evolution protocol
- bypassing seal checks for existing run folders
- silent mutation of evidence invariants or replay semantics

Grounding:
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/contracts/option_d_evidence_contract_v1.md`
- `PATH1_EXECUTION_MODEL.md`

## Unassigned / Edge Cases
- `reports/verification/**` — historical verification outputs are not canonical evidence-run ledger and route to `MOD-UNASSIGNED`/`MOD-UTIL` by rule.
- `artifacts/path1_replay_report.json` — generated artifact outside canonical run tree, routed to `MOD-RUNOPS`.
