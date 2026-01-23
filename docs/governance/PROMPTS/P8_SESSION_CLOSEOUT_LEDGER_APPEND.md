# P8 — Session Closeout Ledger Append

- Intended agent: `OVC_FreezeScribe`
- Allowed mode: `DOCS-ONLY`
- Instruction: append ONE entry only to `docs/GOVERNANCE/CHANGELOG_APPEND_ONLY.md`.
- Refusal: if required inputs are missing, refuse (output INVALID) and list missing fields.
- Ban: no invention and no summarization; use only provided inputs/evidence.

## Prompt Body (verbatim)

```text
Read /AGENTS.md first.
Then read docs/GOVERNANCE/OVC_RULEBOOK.md and docs/GOVERNANCE/AGENTS/OVC_AGENT_SYSTEM.md.

MODE: DOCS-ONLY
AGENT: OVC_FreezeScribe

TASK:
Append exactly ONE new entry to:
docs/GOVERNANCE/CHANGELOG_APPEND_ONLY.md

INPUTS (must all be provided):
- Commit SHA
- CCR ID (or NONE)
- Agent(s) used
- Mode(s) used
- Options touched
- Files changed summary
- Evidence pointers
- Scope one-liner

RULES:
- Append-only: do not modify prior entries.
- Use the exact ledger entry template.
- Do not invent evidence.
- If any required input is missing: output INVALID and list missing fields.
- CCR is REQUIRED for any change that modifies behavior, contracts, schemas, workflows, or determinism gates; otherwise set CCR to `NONE` (e.g., governance/bootstrap documentation-only additions).
- Do not backfill missing history. If an entry was missed, append a new entry noting the omission as a breach/oversight and continue forward.

OUTPUT:
- Unified diff that appends the new entry only.

CONSTRAINTS:
- Do not modify any other file.
- Do not propose fixes or improvements.

OUTPUT:
- Unified diff that adds this file only.
```
