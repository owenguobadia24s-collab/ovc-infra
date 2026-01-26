# Release: ovc-v0.1-spine

> **Release Name:** ovc-v0.1-spine  
> **Release Date:** 2026-01-20  
> **Release Type:** Foundation Freeze (Archival)

---

## Scope

This release formally freezes the **OVC epistemic spine**—the complete descriptive and evaluative truth layers that form the canonical foundation for all future work.

### Option B (Meaning Layers) — CANONICAL

| Layer | Status | Description |
|-------|--------|-------------|
| L1 | CANONICAL | Block-level descriptive features |
| L2 | CANONICAL | Session-level aggregations |
| L3 | CANONICAL | Cross-session semantic features |

### Option C (Outcomes) — CANONICAL

| Layer | Status | Description |
|-------|--------|-------------|
| Outcomes | CANONICAL | Forward returns, MFE/MAE, realized volatility |

**Canonical Outcomes:**
- `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_6`
- `mfe_3`, `mfe_6`
- `mae_3`, `mae_6`
- `rvol_6`

---

## Explicit Exclusions

This release does **NOT** include and does **NOT** authorize:

- ❌ **No strategy logic** — Signal generation, entry/exit rules, or trading decisions
- ❌ **No execution logic** — Order management, position sizing, or broker integration
- ❌ **No optimization or scoring** — Hyperparameter tuning, backtesting engines, or performance metrics
- ❌ **No experimental features** — Draft outcomes (e.g., `ttt_*`) remain outside canonical scope

---

## Governing Documents

| Document | Purpose |
|----------|---------|
| `docs/ops/GOVERNANCE_RULES_v0.1.md` | Change control and approval requirements |
| `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` | Canonical data flow specification |
| `docs/ops/OPTION_B_CHARTER_v0.1.md` | Option B scope and boundaries |
| `docs/ops/OPTION_C_CHARTER_v0.1.md` | Option C scope and boundaries |
| `docs/IMMUTABILITY_NOTICE.md` | Immutability constraints |

---

## Foundation Statement

> **"This release freezes the descriptive and evaluative truth layers of OVC."**

All canonical layers (Option B L1/L2/L3, Option C Outcomes) are now **FROZEN**.

- Meanings are fixed and must not be reinterpreted
- Implementations are locked and must not be modified in place
- All future work must be **downstream-only**

Breaking changes to any frozen layer require:
1. New versioned specification (MAJOR version bump)
2. Formal governance approval per `GOVERNANCE_RULES_v0.1.md`
3. Migration path documentation

---

## Verification Evidence

Promotion to CANONICAL status was validated through:

- `reports/validation/C1_v0_1_validation.md`
- `reports/validation/C2_v0_1_validation.md`
- `reports/validation/C3_v0_1_validation.md`
- `reports/validation/C_v0_1_promotion.md`

---

## Release Artifacts

```
releases/
└── ovc-v0.1-spine.md          # This document

docs/
├── WORKFLOW_STATUS.md          # Updated with release reference
└── IMMUTABILITY_NOTICE.md      # Immutability constraints

docs/ops/
├── GOVERNANCE_RULES_v0.1.md    # In force
├── OPTION_B_*_v0.1.md          # Frozen specifications
└── OPTION_C_*_v0.1.md          # Frozen specifications
```

---

**End of Release Notes**
