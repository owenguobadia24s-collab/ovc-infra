# Option B Charter v0.1

> **[STATUS: ACTIVE]**  
> **Created:** 2026-01-20  
> **Purpose:** Defines scope, guarantees, and prohibitions for Option B (Derived Features)  
> **Note:** This document authorizes Option B work but does not freeze it.

---

## 1. Purpose of Option B

### What Option B Is

Option B is the **Meaning Layer** — a set of derived features computed exclusively from canonical facts. It transforms raw 2H block observations into structured, versioned feature sets that downstream layers (Option C evaluation, research queries) can consume.

Option B exists to answer: *"What can be computed from the facts without interpretation?"*

### What Problem Option B Solves

| Problem | How Option B Addresses It |
|---------|---------------------------|
| Raw blocks are too granular for analysis | Computes aggregated features (rolling stats, session context) |
| Ad-hoc queries are inconsistent | Provides versioned, reproducible feature definitions |
| Evaluation requires stable inputs | Guarantees replayable feature computation |
| Research needs structured data | Exposes typed feature vectors with known semantics |

### What Option B Is NOT Solving

| Out of Scope | Reason |
|--------------|--------|
| Trading decisions | Features are inputs, not conclusions |
| Human interpretation | No subjective labels or recommendations |
| Real-time signals | Batch computation only; no streaming |
| Data ingestion | Option A handles all ingest; Option B is read-only |
| Outcome measurement | Option C handles forward returns and hit rates |

---

## 2. Allowed Inputs

### Canonical Sources (Read-Only)

Option B may read from the following sources:

| Source | Schema | Type | Notes |
|--------|--------|------|-------|
| `ovc_blocks_v01_1_min` | `ovc` | table | **PRIMARY** — canonical 2H blocks |
| `ovc_run_reports_v01` | `ovc` | table | Run metadata (for provenance) |
| `v_ovc_min_events_norm` | `ovc` | view | Normalized block projection |
| `v_ovc_min_events_seq` | `ovc` | view | Sequenced blocks with lag/lead |

### Option A Read-Only Guarantee

**Option A artifacts are READ-ONLY to Option B.**

This means:
- ✅ SELECT from `ovc.*` tables and views
- ✅ JOIN canonical facts with derived computations
- ✅ Reference canonical field names in feature definitions
- ❌ INSERT/UPDATE/DELETE on `ovc.*`
- ❌ ALTER any `ovc.*` schema object
- ❌ CREATE objects in `ovc` schema

### External Sources

Option B may also read from:
- `ovc_cfg.threshold_pack` — immutable threshold configurations
- `ovc_cfg.threshold_pack_active` — current threshold pointers

Option B must NOT read from:
- `ops.*` schema (sync state is operational, not factual)
- `ovc_qa.*` schema (validation artifacts are governance, not input)
- External APIs (all data enters via Option A only)

---

## 3. Allowed Outputs

### Target Schema

Option B writes exclusively to the `derived` schema:

```
derived.*
```

No other schema may receive Option B writes.

### Versioning Rules

All Option B tables and views must follow semantic versioning:

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `<name>_v<major>_<minor>` | `ovc_l1_features_v0_1` | New feature set |
| Increment minor | `v0_1` → `v0_2` | Additive changes (new columns) |
| Increment major | `v0_2` → `v1_0` | Breaking changes (column removal, type change) |

**Version coexistence:** Old versions remain until explicitly deprecated. New code must reference the latest version.

### Naming Conventions

| Object Type | Pattern | Example |
|-------------|---------|---------|
| L1 features (single-bar) | `ovc_l1_<name>_v<ver>` | `ovc_l1_features_v0_1` |
| L2 features (multi-bar) | `ovc_l2_<name>_v<ver>` | `ovc_l2_session_features_v0_1` |
| L3 features (semantic) | `ovc_l3_<name>_v<ver>` | `ovc_l3_regime_trend_v0_1` |
| Run metadata | `derived_runs_v<ver>` | `derived_runs_v0_1` |
| Feature views | `v_<name>_v<ver>` | `v_block_features_v0_1` |

### Column Naming

| Type | Convention | Example |
|------|------------|---------|
| Source reference | `block_id` | FK to canonical blocks |
| Computed feature | `<feature>_<window>` | `range_z_12`, `body_ratio` |
| Metadata | `computed_at`, `run_id` | Provenance tracking |
| Version marker | `feature_version` | Schema version reference |

---

## 4. Explicit Prohibitions

### What Option B Must Never Do

| Prohibition | Reason | Consequence |
|-------------|--------|-------------|
| Write to `ovc.*` schema | Canonical facts are immutable | Audit required; rollback mandatory |
| Modify Option A artifacts | Ingest layer is LOCKED | Governance violation |
| Sync to Notion | Features are intermediate, not human-actionable | Data boundary violation |
| Interpret features as signals | Option B computes; it does not decide | Scope creep |
| Create circular dependencies | Derived must flow downstream only | Architecture violation |
| Reference DEPRECATED sources | Legacy artifacts have no stability guarantee | Technical debt |
| Compute forward-looking outcomes | Option C handles all outcome logic | Layer boundary violation |

### Violation vs Experiment

| Category | Definition | Action Required |
|----------|------------|-----------------|
| **Violation** | Write to forbidden schema, modify Option A, sync to Notion | Immediate rollback + audit |
| **Experiment** | New feature definition in `derived.*` with `_exp` suffix | Document in research log; do not promote without review |
| **Exploration** | SELECT-only queries against canonical facts | No action required |

### Experimental Naming

Experimental features that have not been reviewed must use:
```
derived.ovc_c<N>_<name>_exp_v<ver>
```

Example: `derived.ovc_l2_momentum_exp_v0_1`

Experimental tables:
- May be dropped without audit
- Must not be referenced by production pipelines
- Must not flow to Option C

---

## 5. Relationship to Governance

### Governing Document

Option B operates under the rules defined in:

**[GOVERNANCE_RULES_v0.1.md](GOVERNANCE_RULES_v0.1.md)**

### When a New Audit Is Required

| Event | Audit Type | Reference |
|-------|------------|-----------|
| New C-level feature category (L4, C5, etc.) | Full audit | GOVERNANCE_RULES §2 |
| Breaking change to existing feature table | Schema audit | GOVERNANCE_RULES §5 |
| New dependency on Option A artifact | Boundary audit | GOVERNANCE_RULES §4 |
| Promotion of experimental feature | Feature audit | This document §4 |

### When Standard Review Suffices

| Event | Process |
|-------|---------|
| New feature column (additive) | Standard PR review |
| Bug fix in feature computation | Standard PR review |
| Performance optimization | Standard PR review |
| New experimental table | Document in research log |

---

## 6. Guarantees to Downstream Layers

Option B provides the following guarantees to Option C and research consumers:

### Stability Guarantees

| Guarantee | Meaning |
|-----------|---------|
| **Schema stability** | Column names and types will not change within a version |
| **Replayability** | Given the same canonical facts, features reproduce exactly |
| **Provenance** | Every feature row links to source `block_id` and `run_id` |
| **Versioning** | Breaking changes create new versions; old versions persist |

### Non-Guarantees

| Not Guaranteed | Reason |
|----------------|--------|
| Feature completeness | New features may be added |
| Computation timing | Batch runs may vary in schedule |
| Backfill coverage | Historical coverage depends on canonical facts availability |

---

## 7. Entry Criteria

Before Option B work begins on a new feature category, the following must exist:

| Requirement | Location | Status |
|-------------|----------|--------|
| Canonical facts table | `ovc.ovc_blocks_v01_1_min` | ✅ EXISTS |
| Data Flow Canon | `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` | ✅ EXISTS |
| Governance Rules | `docs/ops/GOVERNANCE_RULES_v0.1.md` | ✅ EXISTS |
| Target schema | `derived` | ✅ EXISTS |
| Run artifact system | `src/ovc_ops/run_artifact.py` | ✅ EXISTS |

**Option B is authorized to proceed.**

---

## [CHANGE][ADDED] 8. L1 Status

**L1 is now CANONICAL** (promoted 2026-01-20).

| Property | Value |
|----------|-------|
| Feature Spec | `OPTION_B_L1_FEATURES_v0.1.md` [CANONICAL] |
| Implementation Contract | `OPTION_B_L1_IMPLEMENTATION_CONTRACT_v0.1.md` [CANONICAL] |
| SQL View | `derived.v_ovc_l1_features_v0_1` |
| Validation Evidence | `reports/validation/C1_v0_1_validation.md` |

### Downstream Authorization

- ✅ **L2** (multi-bar features) may depend on L1 outputs
- ✅ **L3** (signals/classifications) may depend on L1 outputs
- ✅ **Option C** (outcomes/evaluation) may depend on L1 outputs

### Modification Restrictions

- ❌ L1 feature meanings may NOT be changed without governance approval
- ❌ L1 implementation may NOT deviate from spec
- ❌ Breaking changes require MAJOR version bump (v0.1 → v1.0)

---

## 9. Summary

| Aspect | Option B Position |
|--------|-------------------|
| **Reads from** | `ovc.*` (canonical facts), `ovc_cfg.*` (thresholds) |
| **Writes to** | `derived.*` only |
| **Computes** | Features derived from facts (L1, L2, L3) |
| **Does not compute** | Outcomes, signals, recommendations |
| **Syncs to Notion** | ❌ NEVER |
| **Modifies Option A** | ❌ NEVER |
| **Governed by** | GOVERNANCE_RULES_v0.1.md |

---

*End of Option B Charter v0.1*
