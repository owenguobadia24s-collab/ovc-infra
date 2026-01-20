# Path 1 — Research & Scoring Layer

> ⚠️ **NON-CANONICAL** — This directory contains downstream research artifacts only.  
> **NO FEEDBACK INTO CANONICAL** — Nothing in `research/` may modify, redefine, or semantically influence Option B/C layers.

## Purpose

Path 1 provides a structured space for **exploratory research and descriptive scoring** built atop the frozen canonical truth layer (`ovc-v0.1-spine`). This is a read-only consumer of canonical data.

## Scope

| Allowed | Forbidden |
|---------|-----------|
| SELECT queries against canonical views | Any mutation of canonical schemas |
| Descriptive statistics and correlations | Strategy definition or signal generation |
| Score computation (compression, not signals) | Execution logic or position sizing |
| Hypothesis testing and documentation | Optimization / backtesting engines |
| Exploratory notebooks | Redefining canonical metric semantics |

## Canonical Read-Only Rule

All research artifacts **MUST**:

1. Reference the canonical release tag explicitly: `ovc-v0.1-spine`
2. Treat canonical tables/views as immutable inputs
3. Never write back to `ovc.*`, `derived.*`, or any canonical schema
4. Document the exact canonical objects consumed

## Version Anchoring

Every study and score **MUST** declare which canonical release it targets. If the canonical layer is updated, studies must be re-validated or archived.

```
canonical_release: ovc-v0.1-spine
```

## Canonical Outcomes Available

The following outcomes from Option C are available for research (read-only):

- `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_6` — Forward returns
- `mfe_3`, `mfe_6` — Maximum favorable excursion
- `mae_3`, `mae_6` — Maximum adverse excursion
- `rvol_6` — Realized volatility

## Directory Structure

```
research/
├── README.md                 # This file
├── RESEARCH_GUARDRAILS.md    # Hard constraints and naming rules
├── studies/
│   └── TEMPLATE/             # Copy this to start a new study
├── scores/
│   ├── README.md             # Score layer documentation
│   └── score_template.sql    # SQL skeleton for new scores
├── notebooks/
│   └── README.md             # Notebook usage policy
└── tooling/
    └── README.md             # Future helper utilities
```

## How to Start a Study

1. **Copy the template:**
   ```powershell
   Copy-Item -Recurse research/studies/TEMPLATE research/studies/study_<YYYYMMDD>_<slug>
   ```

2. **Fill out required files:**
   - `spec.md` — Define question, hypothesis, success criteria
   - `inputs.md` — List exact canonical tables/columns
   - `method.md` — Document transformations and statistics
   - `manifest.json` — Machine-readable metadata

3. **Run analysis** (read-only queries only)

4. **Document results:**
   - `results.md` — Tables, figures, summary
   - `verdict.md` — Interpretation and limitations

5. **Review against guardrails** before committing

## Governance

- This layer is **non-canonical** and has no authority over Option B/C definitions
- Studies may inform future canonical work but require explicit, documented promotion
- All research must pass the "category error" checklist in `RESEARCH_GUARDRAILS.md`
