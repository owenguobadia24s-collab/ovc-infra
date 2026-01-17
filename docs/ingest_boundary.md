# Ingest Boundary Doctrine (OVC v0.1)

## Purpose (what ingest does)
- Receive raw MIN export payloads.
- Perform structural validation against the MIN contract.
- Persist accepted records to Neon.
- Archive the raw export to R2.

## Non-responsibilities (what ingest does NOT do)
- Semantic enforcement (e.g., ret correctness, strategy truth, signal policing).
- Derived correctness checks beyond structural validation.
- QA, analytics, or downstream business logic gating.

## Endpoint contract
- `POST /tv`: raw text body only (pipe-delimited export string).
- `POST /tv_secure`: JSON body only.

## Category error warning
Semantics belong downstream (views/QA/analytics), not in the webhook gate.

## Regression guardrails
- Do not add semantic checks to ingest.
- If a semantic check is needed, implement it downstream (QA/tests/analytics).

## Ingest Stability Notes
- MIN v0.1.1 is immutable; supersede only with a new version file.
- `/tv` stays raw text; `/tv_secure` stays JSON.
- Ret semantic enforcement remains disabled in ingest.
