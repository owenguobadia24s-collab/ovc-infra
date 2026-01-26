# Immutability Notice

> **Effective Date:** 2026-01-20  
> **Applies To:** All canonical OVC layers  
> **Governing Document:** `docs/ops/GOVERNANCE_RULES_v0.1.md`

---

## Core Principle

**Canonical layers must not be modified in place.**

The OVC epistemic spine—comprising Option B (L1/L2/L3) and Option C (Outcomes)—represents frozen truth. These layers define *what happened* and *what followed*, not *what to do about it*.

---

## Immutability Constraints

### 1. No In-Place Modifications

Canonical specifications, implementations, and meanings are **FROZEN**:

| Layer | Frozen Artifacts |
|-------|------------------|
| Option B – L1 | `OPTION_B_L1_*.md`, `derived.v_ovc_l1_*` |
| Option B – L2 | `OPTION_B_L2_*.md`, `derived.v_ovc_l2_*` |
| Option B – L3 | `OPTION_B_L3_*.md`, `derived.v_ovc_l3_*` |
| Option C | `OPTION_C_*.md`, `derived.v_ovc_c_outcomes_*` |

**Prohibited actions:**
- Editing canonical SQL view definitions
- Changing field semantics or derivation logic
- Renaming or removing canonical columns
- Altering validation thresholds retroactively

### 2. Changes Require New Versions

Any modification to a canonical layer requires:

1. **New version number** — MAJOR bump for breaking changes (e.g., `v0.2`, `v1.0`)
2. **New specification document** — Clearly marked with version suffix
3. **Migration documentation** — How downstream consumers should adapt
4. **Governance approval** — Per `GOVERNANCE_RULES_v0.1.md`

Example: To change L1 feature definitions, create `OPTION_B_L1_FEATURES_v0.2.md` and `derived.v_ovc_l1_features_v0_2`.

### 3. Downstream Experimentation Must Not Alter Truth Layers

Experimental or exploratory work (Option E, research views, strategy prototypes) must:

- **Read from** canonical layers only
- **Write to** non-canonical schemas (e.g., `research.*`, `experimental.*`)
- **Never mutate** the `derived` schema canonical views
- **Never reclassify** canonical facts or outcomes

---

## Rationale

Immutability ensures:

| Property | Benefit |
|----------|---------|
| **Reproducibility** | Any analysis can be replayed with identical inputs |
| **Auditability** | Historical decisions remain traceable |
| **Trust** | Downstream layers can rely on stable foundations |
| **Versioning** | Changes are explicit, not silent |

---

## Enforcement

- SQL views are defined in versioned migration files
- CI checks validate schema consistency
- Governance approval is required for any canonical change
- Release tags mark frozen states (e.g., `ovc-v0.1-spine`)

---

## Questions?

If you are unsure whether a proposed change affects canonical layers, consult:

1. `docs/ops/GOVERNANCE_RULES_v0.1.md` — Change control process
2. `docs/WORKFLOW_STATUS.md` — Current canonical status
3. `releases/ovc-v0.1-spine.md` — Frozen scope definition

**When in doubt, create a new version rather than modifying in place.**

---

**End of Immutability Notice**
