# Option B — Path 1 Status

**Status:** FROZEN  
**Freeze Date:** 2026-01-20  
**Library Version:** SCORE_LIBRARY_v1

---

## 1. Freeze Declaration

Option B Path 1 is **FROZEN** as of 2026-01-20.

No modifications to score definitions, formulas, joins, input columns, or semantics are permitted within this library version.

---

## 2. Frozen Scores

| Score | Version | Status |
|-------|---------|--------|
| DIS | v1.1 | FROZEN |
| RES | v1.0 | FROZEN |
| LID | v1.0 | FROZEN |

### Withdrawn Scores

| Score | Version | Reason |
|-------|---------|--------|
| DIS | v1.0 | Non-canonical dependency (`directional_efficiency`); replaced by v1.1 |

---

## 3. Invariants

All frozen scores in this library adhere to the following invariants:

### 3.1 Descriptive-Only

- Scores describe past bar characteristics
- Scores do NOT predict future price movement
- Scores do NOT constitute trading signals

### 3.2 Canonical-Input-Only

- All inputs come from canonical views:
  - `derived.v_ovc_c1_features_v0_1`
  - `derived.v_ovc_c2_features_v0_1`
  - `derived.v_ovc_c3_features_v0_1`
- Outcome views (`derived.v_ovc_c_outcomes_v0_1`) are used in studies only, not in score construction

### 3.3 Association ≠ Predictability

- Any correlation with outcomes is historical co-occurrence only
- Correlation does not imply causation, persistence, or actionability
- Study results are descriptive observations, not predictions

### 3.4 No Upstream Mutation

- Score SQL is SELECT-only
- No INSERT, UPDATE, DELETE operations
- No modification of canonical spine objects

---

## 4. Future Additions

Any new score additions require:

1. A **new library version** (e.g., `SCORE_LIBRARY_v2`)
2. A new `SCORE_INVENTORY_v2.md`
3. Updated `OPTION_B_PATH1_STATUS.md` freeze declaration

New scores **cannot** be added to `SCORE_LIBRARY_v1`.

Modifications to existing frozen scores (DIS-v1.1, RES-v1.0, LID-v1.0) are **not permitted**. If a score definition must change, it must be:
- Withdrawn from the current library
- Re-introduced under a new version in a new library

---

## 5. Completed Runs Location

Evidence run artifacts are stored in:

```
reports/path1/evidence/runs/<run_id>/
```

See [EVIDENCE_RUNS_HOWTO.md](EVIDENCE_RUNS_HOWTO.md) for operational instructions.

---

## 6. References

| Document | Purpose |
|----------|---------|
| [SCORE_LIBRARY_v1.md](scores/SCORE_LIBRARY_v1.md) | Full score definitions and formulas |
| [SCORE_INVENTORY_v1.md](SCORE_INVENTORY_v1.md) | Compact score manifest |
| [RUN_CONVENTIONS.md](RUN_CONVENTIONS.md) | Run naming and output conventions |
| [EVIDENCE_RUNS_HOWTO.md](EVIDENCE_RUNS_HOWTO.md) | Evidence run execution guide |

---

**This document is authoritative for Path 1 freeze status.**
