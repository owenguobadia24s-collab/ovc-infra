# Path 2 Contract v1.0

**Status:** Non-canonical interpretive workspace  
**Effective:** 2026-01-20  
**Disposition:** Disposable without notice

---

## 1. Purpose

Path 2 is a non-canonical research layer that exists only because Path 1 is stable, automated, and trustworthy. It provides a contained space for questioning, exploration, and interpretation of observational evidence. Path 2 holds no authority over system behavior and produces no artifacts that the system depends on. Its outputs carry no truth claims.

---

## 2. Inputs (Allowed)

Path 2 may read:

- Path 1 evidence reports (finalized `.md` artifacts)
- `RUN.md` metadata files
- `INDEX.md` registry files
- Exported static snapshots explicitly marked for research use

Path 2 is **forbidden** from reading:

- Live database connections
- Canonical views in Option B
- SCORE_LIBRARY_v1 internals
- Any mutable or in-flight pipeline state

---

## 3. Outputs (Allowed)

Path 2 may produce:

- Analysis notes
- Temporary summaries
- Exploratory tables or sketches
- Questions for future investigation

All Path 2 outputs:

- Are non-canonical
- May be deleted at any time
- Carry no truth claims
- Must not be cited as evidence by other system components

---

## 4. Forbidden Actions (Hard Constraints)

Path 2 must **never**:

- Modify Option B or any canonical spine artifact
- Modify SCORE_LIBRARY_v1 or any score definition
- Emit trading signals or actionable recommendations
- Back-propagate conclusions into Path 1
- Claim predictive validity
- Write to any schema outside its designated workspace
- Assert causal relationships as established facts

---

## 5. Epistemic Posture

Path 2 treats all interpretations as provisional. Uncertainty is the default state. Conclusions are hypotheses, not findings. Reversal and invalidation are normal outcomes, not failures. Path 2 operates under the assumption that any pattern it identifies may be noise, coincidence, or artifact of methodology. Skepticism toward its own outputs is required.

---

## 6. Failure Modes

Path 2 can fail by:

- Narrative overfitting (constructing stories that fit past data too well)
- Hindsight bias (treating historical patterns as predictable)
- Metric worship (optimizing interpretations toward favorable numbers)
- Leaking interpretation into canon (allowing Path 2 conclusions to influence Path 1)
- Assuming stability of patterns across regimes
- Treating exploratory findings as confirmed

---

## 7. Invalidation Conditions

Path 2 outputs are invalidated when:

- New Path 1 evidence contradicts them
- They depend on score definitions that have since changed
- They rely on assumptions that cannot be independently verified
- The underlying evidence artifacts are revised or retracted
- Methodology flaws are identified post-hoc

Invalidation is expected and does not indicate system failure.

---

## 8. Relationship to Other Paths

- Path 2 does not write to Path 1.
- Path 2 does not influence Option B.
- Path 2 does not modify SCORE_LIBRARY_v1.
- Path 2 can be entirely deleted without affecting system operation.
- No other component depends on Path 2 outputs.

Path 2 is architecturally isolated. Its existence is optional.

---

*End of contract.*
