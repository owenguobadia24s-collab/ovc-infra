# Notebooks

> ⚠️ **NON-CANONICAL** — Notebooks are exploratory research artifacts only.  
> **NO FEEDBACK INTO CANONICAL** — Notebook outputs do not modify Option B/C definitions.

## Purpose

Notebooks provide an interactive environment for exploratory data analysis, visualization, and prototyping. They are **not** a substitute for documented, reproducible studies.

## Policy

### Notebooks Are Exploratory

- Notebooks may contain experimental code and analysis
- Notebooks are **not** authoritative sources of truth
- Findings from notebooks must be formalized in `studies/` to be considered valid

### Canonical Read-Only

- Notebooks may **read** from canonical views
- Notebooks must **never** write to canonical schemas
- All queries must be SELECT-only

### Output Handling

If a notebook produces data outputs (CSVs, figures, etc.):

1. Outputs must go to `research/outputs/` (create as needed)
2. Outputs must include metadata (canonical release, timestamp)
3. Outputs are non-canonical and disposable

### Naming Convention

```
nb_<YYYYMMDD>_<slug>.ipynb
```

**Examples:**
- `nb_20260120_mfe_exploration.ipynb`
- `nb_20260125_correlation_matrix.ipynb`

## Requirements

Every notebook **SHOULD**:

1. **Header cell** with:
   - NON-CANONICAL warning
   - Canonical release reference (`ovc-v0.1-spine`)
   - Brief description of purpose

2. **Environment setup** cell documenting:
   - Python version
   - Key package versions
   - Database connection (read-only)

3. **Clean outputs** before committing (or use `.gitignore` for outputs)

## Example Header Cell

```python
"""
⚠️ NON-CANONICAL — This notebook is exploratory research only.
NO FEEDBACK INTO CANONICAL — Findings do not modify Option B/C definitions.

Canonical Release: ovc-v0.1-spine
Purpose: [Brief description]
Author: @handle
Date: YYYY-MM-DD
"""
```

## Forbidden in Notebooks

❌ Writing to canonical schemas (`ovc.*`, `derived.*`)  
❌ Defining canonical metrics or views  
❌ Strategy/execution logic  
❌ Treating notebook outputs as authoritative  

## Promotion Path

If notebook analysis yields valuable insights:

1. Formalize in a study under `studies/`
2. Document inputs, method, results, verdict
3. Follow standard review process

Notebooks themselves are **never** promoted to canonical status.
