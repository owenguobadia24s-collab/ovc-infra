# VS Code Preflight Wrappers (Minimal Prompt Pack)

## SECTION 1 — Universal Preflight (verbatim block)

```text
PRE-FLIGHT (MANDATORY):
1) Open and read: AGENTS.md (repo root)
2) Open and read: docs/GOVERNANCE/OVC_RULEBOOK.md
3) Open and read: docs/GOVERNANCE/AGENTS/OVC_AGENT_SYSTEM.md
4) Declare your mode: DOCS-ONLY / DIFFS-ONLY / AUDIT-ONLY
5) If any required file is missing or any action would violate the Rulebook: REFUSE and cite clause(s).

Hard constraint: Do not invent any file paths, scripts, schema fields, or workflow behavior. If evidence is missing, mark UNKNOWN and stop.
```

## SECTION 2 — Wrapper Templates (4 total, concise)

### Wrapper 1 — DOCS-ONLY (Architect)
- Intended agent: Architect
- Allowed mode: DOCS-ONLY
- Paste your task below:
  - [PASTE YOUR TASK HERE]
- Stop condition: refuse if it would cross Options or introduce renames/version jumps.

### Wrapper 2 — DIFFS-ONLY (Implementer)
- Intended agent: Implementer
- Allowed mode: DIFFS-ONLY
- Paste your task below:
  - [PASTE YOUR TASK HERE]
- Stop condition: refuse if it would cross Options or introduce renames/version jumps.

### Wrapper 3 — AUDIT-ONLY (Validator)
- Intended agent: Validator
- Allowed mode: AUDIT-ONLY
- Paste your task below:
  - [PASTE YOUR TASK HERE]
- Stop condition: refuse if it would cross Options or introduce renames/version jumps.

### Wrapper 4 — DOCS-ONLY (Governor / Change Control)
- Intended agent: Governor
- Allowed mode: DOCS-ONLY
- Paste your task below:
  - [PASTE YOUR TASK HERE]
- Stop condition: refuse if it would cross Options or introduce renames/version jumps.
