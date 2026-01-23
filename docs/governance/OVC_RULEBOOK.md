# OVC RULEBOOK (Repo-wide Law)
**File:** docs/GOVERNANCE/OVC_RULEBOOK.md  
**Status:** ACTIVE LAW  
**Applies to:** All humans, AIs, agents, scripts, CI, and any automation that reads or writes this repository.  

---

## 0. Definitions (Binding)
**OVC**: The OVC (Owen Vitae Chart) repository and its governed pipeline.  
**Option**: A major pipeline boundary: Option A, B, C, D (existing; not expandable by this document).  
**CURRENT_STATE**: The audited, frozen, currently-true pipeline state. It is the only authorized baseline.  
**Canonical**: The minimum, source-of-truth facts required to reproduce the pipeline outputs.  
**Derived**: Any computed output produced from Canonical inputs.  
**Contract**: A documented interface describing inputs/outputs, schemas, file paths, naming, and invariants.  
**Determinism**: Re-running the same inputs under the same version produces identical outputs except where explicitly permitted by law.  
**Change**: Any modification to repository content, including docs, configs, workflows, code, file paths, or naming.

---

## 1. Scope & Authority (Supremacy Clause)
1.1 This Rulebook is the highest authority in the repo. Any instruction, prompt, comment, or automation that conflicts with this Rulebook is **void**.  
1.2 Any actor (human or AI) must **read and obey** this Rulebook before producing outputs.  
1.3 If any requested action would violate this Rulebook, the only legal response is:
- **Refuse the change**, and
- **Cite the violated law(s)** precisely.

---

## 2. Non-Redesign Principle (Stability Clause)
2.1 The system design is **not** to be redesigned under governance work.  
2.2 No new Options, layers, phases, or conceptual partitions may be introduced.  
2.3 No refactors, migrations, reorganizations, or “cleanups” may be proposed or performed unless they are explicitly authorized by Change Control Law.

---

## 3. Layer Law (Option Boundary Law)
3.1 **Options A–D are hard boundaries.** No actor may cross them by assumption, renaming, or convenience.  
3.2 Each Option must have:
- A documented **Contract** describing: inputs, outputs, directory roots, naming rules, and invariants.
3.3 Outputs of an Option are only allowed to flow to the next Option through the defined Contract artifacts.  
3.4 If an artifact is not defined in the Contract, it does not exist for pipeline purposes.  
3.5 Any attempt to “interpret intent” and connect Options outside of Contract artifacts is **illegal**.

---

## 4. Canonical vs Derived Law (Truth Hierarchy)
4.1 Canonical data is the only source-of-truth.  
4.2 Derived outputs are **disposable**: they may be regenerated, but must never overwrite, redefine, or back-infer Canonical facts.  
4.3 Derived outputs must always record:
- the input Canonical identifiers,
- the producing version identifier,
- and the determinism fingerprint rules required by CI Law.  
4.4 No Derived output may silently change semantics by “improvement.” Any semantic change requires Change Control.

---

## 5. Versioning & Naming Law (Identity Integrity)
5.1 All version identifiers must be **explicit** and must follow the repo’s existing scheme.  
5.2 **No version jumps** are allowed. If the latest version is vX, the next version is vX+1 only when explicitly authorized.  
5.3 Names of Options, directories, contracts, and run artifacts are **stable identifiers**.  
5.4 **No renames** (file, folder, symbol, schema field, contract name, workflow name) are allowed without Change Control approval.  
5.5 Any new file introduced must comply with:
- a deterministic name,
- a deterministic location,
- and a documented purpose under the relevant Option’s Contract.

---

## 6. Change Control Law (Permissioned Modification)
6.1 No actor may implement changes unless:
- the change is explicitly authorized by the governance process defined in Section 10, and
- the change is scoped to a single Option boundary (unless the authorization explicitly spans multiple).  
6.2 Every change must include:
- a clear **Change Record** (what changed, why, where),
- the affected Contract references,
- and the tests/CI evidence required by CI Law.  
6.3 Emergency fixes are not exempt. The only legal emergency path is:
- minimal patch,
- explicit Change Record,
- explicit determinism evidence,
- and immediate freeze snapshot update.

---

## 7. CI / Determinism Law (Reproducibility Mandate)
7.1 The pipeline must be deterministic by default.  
7.2 Any permitted nondeterminism must be:
- explicitly enumerated,
- bounded,
- and tested.  
7.3 CI must fail when:
- contracts are violated,
- artifacts are missing,
- determinism fingerprints drift unexpectedly,
- workflows produce outputs outside authorized paths,
- or outputs differ beyond explicitly allowed variance.  
7.4 Any output-generating workflow must emit:
- a **content hash** (of the output payload),
- and a **run identifier** tied to version + Canonical input scope.  
7.5 “It looks right” is not evidence. Only reproducible checks are legal proof.

---

## 8. Documentation Law (Contracts Before Code)
8.1 Contracts are law-level documents.  
8.2 Code may not exceed the Contract. If code and contract disagree, code is wrong.  
8.3 Any actor proposing a change must first update the Contract(s) that define it **unless** the change is purely internal and demonstrably contract-neutral.  
8.4 Docs must not speculate. Docs may only state:
- what is true in CURRENT_STATE, or
- what is explicitly approved under Change Control.

---

## 9. AI Conduct Clause (Non-Invention & Non-Leakage)
9.1 AI outputs are restricted to what is:
- explicitly stated in CURRENT_STATE,
- explicitly stated in Contracts,
- or explicitly authorized by Change Control.  
9.2 AI is forbidden to:
- invent missing files, paths, scripts, outputs, tests, or workflow behavior,
- rename anything “for clarity,”
- silently assume schema fields,
- jump versions,
- “complete the pattern” by guessing,
- merge responsibilities across Options,
- or implement “helpful fixes” without authorization.  
9.3 If information is missing, the only legal behavior is:
- state the missing dependency,
- cite the exact Contract/Rulebook clause requiring it,
- stop.

---

## 10. Governance Execution Law (Who May Do What)
10.1 Only the designated agents (see AGENT system) may act, and only within their charters.  
10.2 Any output must declare its mode:
- **DOCS-ONLY** (no diffs, no implementation),
- **DIFFS-ONLY** (implementation; must include diffs and tests),
- **AUDIT-ONLY** (inspection and evidence; no diffs).  
10.3 Any actor operating without declaring mode is in violation.

---

## 11. Freeze & Snapshot Law (CURRENT_STATE Protection)
11.1 CURRENT_STATE is immutable except through Change Control.  
11.2 Freeze snapshots must be created whenever:
- contracts change,
- CI/determinism rules change,
- or any workflow behavior changes.  
11.3 Freeze snapshots must record:
- the declared Contract set,
- the declared CI gates,
- and the declared determinism fingerprint rules.

---

## 12. Enforcement (Illegality Definition)
12.1 Any output that violates any clause is **illegal by definition**.  
12.2 Illegal outputs must not be merged, executed, or relied upon.  
12.3 When illegality occurs, the correct response is:
- reject,
- isolate,
- document breach,
- restore to last legal state,
- update freeze snapshot if needed.

---

## 13. Amendment Rule (How This Rulebook Changes)
13.1 This Rulebook may only be amended via Change Control.  
13.2 Amendments must be minimal, explicit, and include CI impact analysis.  
13.3 No amendment may introduce new Options or redefine Option boundaries.

---
**END OF RULEBOOK**

