W1 — Ingest Sovereignty

Anchor Date: 2026-01-14
Architectural Birth Count: 47

Invariant Introduced

Raw market data must enter through a defined ingest contract.
No downstream layer may bypass Option A.
External tools (TV) are not authoritative.

Structural Artifacts

schema_v01.sql

backfill_oanda_2h pipeline

ingest workflows

export contracts v0.1

contract validation tooling

Nature of Wave

Foundation layer.
System becomes ingestion-sovereign.

W2 — Derived & Boundary Formalization

Anchor Dates: 2026-01-17 → 2026-01-18
Architectural Birth Count: ~86

Invariant Introduced

Derived metrics must be deterministic.
C-layer boundaries must be explicit.
Evaluation must be contract-defined.
QA begins formal enforcement.

Structural Artifacts

derived SQL layers

evaluation contracts

boundary documentation

validation harness

logging doctrine

Nature of Wave

Semantic formalization.
System gains layered structure.

W3 — Structural Crystallization Event

Anchor Date: 2026-01-20
Architectural Birth Count: 255

Invariant Introduced

The system must describe itself.
Contracts must govern each option (A–D).
SQL views align with doctrine.
Governance becomes explicit.

Structural Artifacts

OPTION_B_C1/C2/C3 charters

OPTION_C charter

OVC_DOCTRINE.md

GOVERNANCE_RULES

release spine

formalized derived views

Nature of Wave

Crystallization.
OVC becomes a self-describing governed system.

W4 — Evidence Integration & CI Hardening

Anchor Date: 2026-01-22
Architectural Birth Count: 51

Invariant Introduced

Research must follow protocol.
Evidence runs must be reproducible.
CI enforces pipeline validity.

Structural Artifacts

Evidence Pack v0.2

replay verification

CI workflows

DST mapping checks

m15 expansion

Nature of Wave

Research discipline integration.
Exploration becomes governed.

W5 — Operational Integrity Layer

Anchor Date: 2026-02-05
Architectural Birth Count: 104

Invariant Introduced

Runs must declare expected versions.
Operational drift must be computable.
Registry must track state.
System health must be measurable.

Structural Artifacts

RUN_ENVELOPE_STANDARD

EXPECTED_VERSIONS

run_envelope implementation

run_registry tooling

drift signals

validation pack integration

Nature of Wave

Governance hardening.
System becomes operationally self-verifying.

W6 — Machine Audit & Classification Consciousness

Anchor Date: 2026-02-10
Architectural Birth Count: 43

Invariant Introduced

The repository must be machine-auditable.
Audit must be read-only and fail-closed.
Drift must be classified, not guessed.

Structural Artifacts

.codex CHECKS

PASS_0–PASS_3 prompts

coverage audit

rename planner

classification groundwork

Nature of Wave

Meta-layer emergence.
The system observes itself.

Post-Wave Layer

All architectural births after 2026-02-10 are classified as:

Post-Maturity Consolidation Layer

This includes:

Repo cartographer

Overlay v0.2

Change ledger sealing

Sentinel append-only ingestion

Refinement pulses

These do not introduce new foundational invariants.
They extend W5–W6 governance.