# Retroactive Continuity Spine v0.1

**Version**: 0.1  
**Date**: 2026-02-09  
**Status**: DECLARATION

---

## Purpose and Scope

This document formally declares the **retroactive continuity spine** for OVC. The spine is the repository's provable development memory, derived only from:

- Git commit history
- Sealed governance artifacts (ledger + overlay)
- Canonical change taxonomy

This declaration is descriptive and documentary. It does not execute logic, enforce policy, or gate workflow.

---

## Time-Zero and Canonical Anchors

- **Time-zero (GB0):** `39696066e87f82b694bf4f20905f0f3ea3c9cce2`
- GB0 is authoritative and intentionally has **no run artifact**.
- Phase 1 precedes GB0; Phases 2–4 follow GB0.

**Clarification:** This retroactive continuity spine is **not** the OVC epistemic spine. The epistemic spine refers to frozen truth layers (Option B/C). This document only governs *development history* derivable from commits and sealed artifacts.

---

## Spine Layers

### Measurement Layer

- `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl`
- Seals:
- `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.json`
- `docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.sha256`

The ledger is deterministic, sealed, and records commit-level changes over the sealed range.

### Semantic Layer

- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl`
- Seals:
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json`
- `docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256`

The overlay is deterministic, sealed, and provides one classification line per commit in the ledger.

### Semantic Anchor

- `docs/governance/CHANGE_TAXONOMY_v0_1.md`

The taxonomy defines the stable semantic classes (A–E, UNKNOWN) used by the classifier and overlay.

---

## Continuity Across Phases

Continuity is preserved by construction:

- Every development claim is anchored to a Git commit.
- Every commit in the sealed range is recorded in the DEV Change Ledger.
- Every ledger line has a corresponding semantic classification in the overlay.
- The taxonomy provides a stable semantic anchor for classification output.

As of v0.1 seals, the ledger and overlay cover `range.from=39696066e87f82b694bf4f20905f0f3ea3c9cce2` to `range.to=7021c84d722a6782d032dbeccfccc8aa81bd3353`.

---

## Non-Claims and Non-Goals

This spine does **not** claim:

- Correctness of code, data, or results
- Approval, ratification, or governance sign-off
- Enforcement or workflow gating
- Intent beyond repository diffs and sealed classification output

---

## Governance Invariants

- No development claim exists without a commit.
- No semantic claim exists without classifier output.
- No enforcement exists without explicit phase elevation.
- Unknown classifications are preserved, not coerced.

These invariants define the epistemic boundary of the continuity spine.

---

## Validation Hooks (Non-Enforcing)

The following checks are optional, non-blocking, and intended for auditors or future contributors.

```powershell
# 1) Seal JSON hash matches .seal.sha256 (ledger + overlay)
$ledgerSealHash = (Get-FileHash docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.json -Algorithm SHA256).Hash
$ledgerSealExpected = (Get-Content docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.sha256).Split(' ')[0]
$overlaySealHash = (Get-FileHash docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json -Algorithm SHA256).Hash
$overlaySealExpected = (Get-Content docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.sha256).Split(' ')[0]

# 2) Artifact hashes match seal entries (ledger + overlay)
$ledgerSeal = Get-Content docs/catalogs/DEV_CHANGE_LEDGER_v0.1.seal.json | ConvertFrom-Json
$overlaySeal = Get-Content docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.seal.json | ConvertFrom-Json
$ledgerActual = (Get-FileHash docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl -Algorithm SHA256).Hash
$overlayActual = (Get-FileHash docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl -Algorithm SHA256).Hash
$ledgerExpected = $ledgerSeal.artifacts."docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl".sha256
$overlayExpected = $overlaySeal.artifacts."docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl".sha256

# 3) Overlay line count equals ledger line count
$ledgerLines = (Get-Content docs/catalogs/DEV_CHANGE_LEDGER_v0.1.jsonl).Count
$overlayLines = (Get-Content docs/catalogs/DEV_CHANGE_CLASSIFICATION_OVERLAY_v0.1.jsonl).Count

# 4) HEAD equals sealed range.to for full coverage
$head = (git rev-parse HEAD).Trim()
$rangeTo = $ledgerSeal.range.to
# If $head -ne $rangeTo, coverage ends at $rangeTo and must be resealed to extend.
```

These checks are informative only. They do not enforce policy or gate contributions.

---

## Closing Statement

**This repository carries its own developmental memory, anchored, classified, and sealed.**
