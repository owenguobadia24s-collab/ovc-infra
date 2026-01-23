# OVC Append-Only Governance Changelog

## Purpose
- Canonical, chronological record of “exactly where we stepped” across docs, pipeline, schema, workflows, and evidence.

## Append-Only Rule (Binding)
- Entries are never edited or removed. New information is recorded only by appending a new entry.

## Mandatory Entry Template (verbatim)

```text
## <YYYY-MM-DD> (UTC) — <commit_sha>

- CCR: <CCR-ID | NONE>
- Agents: <comma-separated>
- Modes: <DOCS-ONLY | DIFFS-ONLY | AUDIT-ONLY>
- Options touched: <A | B | C | D | NONE>
- Files changed (high level): <paths or folders>
- Evidence: <CI run link OR docs path(s) OR artifact path(s)>
- Verdict: LEGAL
- Scope (1 line): <mechanical description>
- Notes (optional, max 2 lines)
```

## When an Entry Is Required
- Any verified change to docs, pipeline code, schema/migrations, workflows/CI, evidence/artifacts, or contracts.
- Includes governance-only or audit-only outputs once verified and accepted.

## CCR Requirement
- CCR is REQUIRED for any change under active Change Control; otherwise set CCR to `NONE` (e.g., governance/bootstrap documentation-only additions).
