# Purpose: Legend Canonicalization

This work exists to establish a single, non-negotiable source of truth for NodeIDs
used across OVC graphs, audits, and automation.

Prior state allowed multiple representations of “existence”:
- Graph nodes
- Bullet legends
- Prose notes
- Temporary placeholders

This caused ambiguity between human interpretation and machine truth.

Legend canonicalization resolves this by enforcing:

- Parser supremacy over interpretation
- Pipe-table rows as the sole authority
- Structural truth over semantic completeness
- Minimal, audit-safe representations

The outcome is a system where:
- Node existence is deterministic
- Audits are stable and idempotent
- Agents cannot invent or hallucinate structure
- Future semantic enrichment is safe and reversible

This is a foundation layer.  
It is intentionally strict to protect higher-level reasoning.
