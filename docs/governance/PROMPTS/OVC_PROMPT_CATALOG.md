# OVC Prompt Catalog (P1–P7)

**File:** docs/GOVERNANCE/PROMPTS/OVC_PROMPT_CATALOG.md  
**Status:** ACTIVE  

Each prompt below is a starter template. Every prompt begins with the required preface line.

---

## P1 — Contract Baseline (CURRENT_STATE → Contracts)

- Agent: `OVC_Architect`
- Mode: `DOCS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Convert CURRENT_STATE reality into explicit Option A–D Contracts (docs).
Output Contract files per Option (inputs/outputs/paths/naming/invariants). No code.
```

---

## P2 — Change Control Request

- Agent: `OVC_Governor`
- Mode: `DOCS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Propose a change without implementing it; define exact scope and required evidence.
Output: Change Control Record with authorized boundaries and evidence gates.
```

---

## P3 — Determinism & CI Gate Definition

- Agent: `OVC_Validator`
- Mode: `DOCS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Define the minimal CI gates and determinism fingerprints required to prevent drift.
Output: Audit Report specifying pass/fail checks, required hashes, and failure conditions.
```

---

## P4 — Implementation Patch (Authorized Only)

- Agent: `OVC_Implementer`
- Mode: `DIFFS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Apply a pre-approved change as minimal diffs.
Output: Unified diff + Change Record + referenced approval ID + tests/CI evidence hook.
```

---

## P5 — Audit a PR / Diff for Legality

- Agent: `OVC_Validator`
- Mode: `AUDIT-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Determine whether a diff violates the Rulebook or Contracts.
Output: Audit Report: Legal/Illegal verdict, violated clauses, required remediation.
```

---

## P6 — Freeze Snapshot Update

- Agent: `OVC_FreezeScribe`
- Mode: `DOCS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Record a new CURRENT_STATE snapshot after an approved change is merged.
Output: Freeze snapshot doc + updated index of CURRENT_STATE references.
```

---

## P7 — Breach Response (Drift / Leakage / Illegal Output)

- Agent: `OVC_Governor` (with `OVC_Validator` evidence)
- Mode: `DOCS-ONLY`

```text
Read OVC_RULEBOOK.md and the relevant AGENT charter before acting.

Handle an illegal change attempt without redesigning the system.
Output: Breach Record: what violated which clause, restore instruction to last legal state, and required follow-up snapshot action.
```

