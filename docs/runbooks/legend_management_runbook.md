# Runbook: Legend Management

## Scope

This runbook governs all interaction with:
- LEGEND_MASTER.md
- NodeID lifecycle
- Graph ↔ Legend alignment

## What You Are Allowed To Do

✔ Add a new NodeID **only** as a pipe-table row  
✔ Update semantic fields with explicit evidence  
✔ Remove non-canonical legend content  
✔ Run alignment and audit checks  

## What You Are NOT Allowed To Do

✘ Add bullet or prose legend entries  
✘ Infer NodeIDs from graphs or filenames  
✘ Rename NodeIDs without governance approval  
✘ Guess owner, category, or status  
✘ Modify legend structure for convenience  

## Standard Operations

### Adding a New NodeID
1. Create the pipe-table row in LEGEND_MASTER.md
2. Ensure NodeID is UPPER_SNAKE
3. Run graph ↔ legend alignment audit
4. Confirm missing = 0

### Semantic Updates
1. Collect explicit evidence
2. Draft changes separately
3. Apply via a single commit
4. Verify audits unchanged

### Cleanup / Hygiene
- Remove invalid entries; never “fix” them in place
- If the parser ignores it, it does not exist

## Failure Modes

If audits fail:
- Do not patch around the failure
- Do not add temporary legend entries
- Identify the structural cause
- Resolve at the source

## Final Rule

When in doubt, the legend pipe-table and parser output win.
