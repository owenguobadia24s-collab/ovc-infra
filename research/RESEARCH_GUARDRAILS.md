# Research Guardrails

> ⚠️ **NON-CANONICAL** — This document governs the research layer only.  
> **NO FEEDBACK INTO CANONICAL** — Research findings do not alter canonical definitions.

## Definitions

| Term | Definition |
|------|------------|
| **CANONICAL** | Option B (L1/L2/L3 features) and Option C (outcomes) as frozen in `ovc-v0.1-spine`. Immutable source of truth. |
| **NON-CANONICAL** | Everything under `research/`. Downstream, exploratory, disposable. No authority over canonical semantics. |
| **Score** | A descriptive compression of canonical data. NOT a trading signal. |
| **Study** | A documented, reproducible analysis with explicit inputs, methods, and conclusions. |

---

## Allowed Operations

✅ `SELECT` queries against canonical views  
✅ Aggregations, joins, window functions on canonical data  
✅ Statistical summaries (mean, std, correlation, distribution fitting)  
✅ Score computation that compresses canonical features  
✅ Visualization and exploratory analysis  
✅ Hypothesis documentation and testing  

---

## Forbidden Operations

❌ `INSERT`, `UPDATE`, `DELETE` on any canonical schema (`ovc.*`, `derived.*`)  
❌ Creating objects in canonical schemas  
❌ Redefining canonical metric semantics (e.g., changing how `fwd_ret_3` is computed)  
❌ Strategy rules (entry/exit conditions, position sizing, risk limits)  
❌ Optimization or parameter search for trading performance  
❌ Backtesting engines or equity curve generation  
❌ Any implicit feedback loop into canonical layer  

---

## Reproducibility Minimums

Every study **MUST** document:

| Requirement | Description |
|-------------|-------------|
| `canonical_release` | Exact release tag (e.g., `ovc-v0.1-spine`) |
| `time_window` | Start and end timestamps of data used |
| `dataset_selection` | Instruments, filters, exclusions applied |
| `parameters` | All numeric/categorical parameters used |
| `query_hash` | SHA-256 of the primary analysis query (optional but recommended) |

### Example Manifest Entry

```json
{
  "canonical_release": "ovc-v0.1-spine",
  "window_start": "2025-01-01T00:00:00Z",
  "window_end": "2026-01-15T00:00:00Z",
  "instruments": ["GBPUSD", "EURUSD"],
  "parameters": {
    "lookback_bars": 6,
    "threshold": 0.002
  },
  "query_hash": "sha256:abc123..."
}
```

---

## Naming Conventions

### Studies

```
study_<YYYYMMDD>_<slug>
```

- `YYYYMMDD` = creation date
- `slug` = lowercase, underscore-separated descriptor (max 30 chars)

**Examples:**
- `study_20260120_momentum_decay`
- `study_20260125_mfe_correlation`

### Scores

```
score_<name>_v<major>_<minor>.sql
```

- `name` = lowercase, underscore-separated
- `major.minor` = version (increment major for breaking changes)

**Examples:**
- `score_trend_strength_v1_0.sql`
- `score_volatility_regime_v2_1.sql`

### Notebooks

```
nb_<YYYYMMDD>_<slug>.ipynb
```

Notebooks are exploratory and may not follow strict versioning.

---

## Category Error Checklist

Before committing any research artifact, verify:

| Check | Pass? |
|-------|-------|
| Does this define entry/exit rules? | ❌ Must be NO |
| Does this compute position sizes? | ❌ Must be NO |
| Does this optimize for PnL or Sharpe? | ❌ Must be NO |
| Does this modify canonical tables? | ❌ Must be NO |
| Does this redefine a canonical metric? | ❌ Must be NO |
| Does this reference `ovc-v0.1-spine`? | ✅ Must be YES |
| Are all inputs explicitly documented? | ✅ Must be YES |
| Is the method deterministic and reproducible? | ✅ Must be YES |

**If any ❌ check fails or any ✅ check is missing, the artifact is invalid.**

---

## Boundary Enforcement

### Research → Canonical Promotion

If research findings warrant canonical integration:

1. Open a separate RFC/proposal in `docs/`
2. Do NOT modify canonical code from `research/`
3. Canonical changes require explicit review and versioned release
4. The research artifact remains archived, not merged

### Canonical → Research Consumption

Research may consume canonical data via:

- `derived.ovc_block_features_v0_1` (Option B)
- `derived.ovc_outcomes_v0_1` (Option C)
- Any view explicitly documented in the canonical release

Research **MUST NOT** assume undocumented internal tables are stable.

---

## Violations

Artifacts violating these guardrails will be:

1. Flagged in PR review
2. Moved to `research/_quarantine/` or deleted
3. Documented in a violation log

Repeat violations indicate a process gap requiring team discussion.
