# OVC Governance Rules v0.1

> **[STATUS: CANONICAL]**  
> **Created:** 2026-01-20  
> **Purpose:** Defines lifecycle states, modification rules, and review requirements  
> **Scope:** All OVC repository artifacts (code, schemas, docs, configs)

---

## 1. Lifecycle State Definitions

### CANONICAL

**Definition:** Authoritative artifacts that other systems depend upon. These represent frozen contracts that must not change without explicit review and version bumping.

| Attribute | Rule |
|-----------|------|
| **Modification** | PROHIBITED without explicit audit and version bump |
| **Extension** | PROHIBITED — create new versioned artifact instead |
| **Deletion** | PROHIBITED — mark DEPRECATED first, then ORPHANED |
| **Renaming** | PROHIBITED — breaks downstream references |
| **Reinterpretation** | PROHIBITED — meaning must remain stable |

**Examples:**
- `ovc.ovc_blocks_v01_1_min` — canonical facts table (Option A LOCKED)
- `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md` — authoritative data flow reference
- `contracts/export_contract_v0.1.1_min.json` — MIN export schema
- `sql/01_tables_min.sql` — canonical table DDL

### ACTIVE

**Definition:** Operational artifacts that are currently in use and may be updated as needed.

| Attribute | Rule |
|-----------|------|
| **Modification** | ALLOWED with standard code review |
| **Extension** | ALLOWED — add features, fix bugs |
| **Deletion** | Requires transition to DEPRECATED first |
| **Renaming** | ALLOWED with grep verification of all references |

**Examples:**
- `src/derived/compute_l1_v0_1.py` — L1 feature computation
- `.github/workflows/backfill_then_validate.yml` — manual validation workflow
- `docs/ops/PIPELINE_REALITY_MAP_v0.1.md` — pipeline documentation

### DEPRECATED

**Definition:** Superseded artifacts kept intentionally for reference or backward compatibility. Do not extend or rely upon.

| Attribute | Rule |
|-----------|------|
| **Modification** | PROHIBITED — do not fix bugs or add features |
| **Extension** | PROHIBITED — use the replacement instead |
| **Deletion** | ALLOWED after verification of zero consumers |
| **New References** | PROHIBITED — point to replacement |

**Examples:**
- `src/backfill_oanda_2h.py` — legacy backfill (use `_checkpointed` version)
- `docs/ovc_current_workflow.md` — outdated workflow doc
- `.github/workflows/ovc_full_ingest.yml` — FULL ingest stub

### ORPHANED

**Definition:** Artifacts with no current consumers. Candidates for removal after verification.

| Attribute | Rule |
|-----------|------|
| **Modification** | PROHIBITED — do not maintain |
| **Extension** | PROHIBITED |
| **Deletion** | RECOMMENDED after precondition verification |
| **Resurrection** | Requires promotion to ACTIVE with full audit |

**Examples:**
- `public.ovc_blocks_v01` — legacy table
- `sql/schema_v01.sql` — superseded schema file
- `docs/WORKER_PIPELINE.md` — empty file

---

## 2. Modification Authority

### Who May Modify CANONICAL Artifacts

| Artifact Type | Required Approval | Process |
|---------------|-------------------|---------|
| Schema (`sql/01_tables_min.sql`) | Option A owner + audit | New version required (v0.1.2) |
| Contract (`contracts/export_contract_*.json`) | Contract owner + audit | New version required |
| Canon doc (`OVC_DATA_FLOW_CANON_*.md`) | Governance review | Update `Last Updated` + `[CHANGE]` markers |
| Governance rules (this doc) | Governance review | New version required |

### What Triggers a New Audit vs Minor Update

| Change Type | Action Required |
|-------------|-----------------|
| New pipeline added | **NEW AUDIT** — update PIPELINE_REALITY_MAP |
| Schema column added to CANONICAL table | **NEW AUDIT** — requires version bump |
| Workflow schedule changed | **MINOR UPDATE** — update schedules in docs |
| Bug fix in ACTIVE script | **MINOR UPDATE** — standard code review |
| New DEPRECATED status assigned | **MINOR UPDATE** — update PRUNING_CANDIDATES |
| ORPHANED artifact deleted | **MINOR UPDATE** — update PRUNING_CANDIDATES |
| New Option (B2, L2, etc.) started | **NEW AUDIT** — full lifecycle review |

---

## 3. PR Review Requirements (Future CI Enforcement)

The following file paths should trigger **mandatory human review** when modified:

### Critical Paths (Block Merge Without Review)

```
sql/01_tables_min.sql                    # CANONICAL schema
contracts/export_contract_v0.1.1_min.json # CANONICAL contract
docs/ops/OVC_DATA_FLOW_CANON_v0.1.md     # CANONICAL doc
docs/ops/GOVERNANCE_RULES_v0.1.md        # This file
infra/ovc-webhook/src/index.ts           # P1 ingest worker
```

### High-Attention Paths (Request Review)

```
sql/0*.sql                               # Any schema change
contracts/*.json                         # Any contract change
.github/workflows/*.yml                  # Workflow changes
src/backfill_oanda_2h_checkpointed.py    # CANONICAL backfill
scripts/notion_sync.py                   # CANONICAL sync
```

### CI Enforcement Status

| Rule | Status |
|------|--------|
| Automated path-based review assignment | **FUTURE WORK** |
| Block merge without CANONICAL approval | **FUTURE WORK** |
| Lint for `[STATUS: *]` markers | **FUTURE WORK** |
| Schema drift detection | **FUTURE WORK** |

> **Note:** Until CI enforcement is implemented, reviewers must manually verify that CANONICAL artifacts are not modified without proper process.

---

## 4. Boundary Enforcement

### Option A Boundary (LOCKED)

The following are **frozen** under Option A:

| Artifact | Path | Status |
|----------|------|--------|
| Canonical facts table | `ovc.ovc_blocks_v01_1_min` | LOCKED |
| MIN contract | `contracts/export_contract_v0.1.1_min.json` | LOCKED |
| Table DDL | `sql/01_tables_min.sql` | LOCKED |
| Worker ingest logic | `infra/ovc-webhook/src/index.ts` | LOCKED |

**Prohibited Actions:**
- Adding columns to `ovc_blocks_v01_1_min`
- Changing MIN contract field order or types
- Modifying worker validation logic
- Renaming or moving any Option A artifact

**Allowed Actions:**
- Reading from canonical facts (downstream only)
- Creating new derived tables that reference canonical facts
- Adding new validation without modifying ingest

### Derived Layer Boundary (Option B/C)

Derived layers (`derived.*` schema) may:
- Read from `ovc.ovc_blocks_v01_1_min` (canonical facts)
- Write to `derived.*` tables only
- Create new versioned tables/views

Derived layers must NOT:
- Write to `ovc.*` schema
- Modify canonical facts
- Create circular dependencies back to Option A

---

## 5. Version Bump Requirements

### When to Create a New Version

| Scenario | Current | New Version | Example |
|----------|---------|-------------|---------|
| Schema column added | `v0.1` | `v0.2` | `01_tables_min_v0_2.sql` |
| Contract field added | `v0.1.1` | `v0.1.2` | `export_contract_v0.1.2_min.json` |
| Breaking change | `v0.1` | `v1.0` | Major version bump |
| Canon doc restructure | `v0.1` | `v0.2` | `OVC_DATA_FLOW_CANON_v0.2.md` |

### Version Coexistence Rules

- Old versions remain in repo (DEPRECATED, not deleted)
- New code must reference new version
- Migration path must be documented
- Downstream consumers must be notified

---

## 6. Audit Trail Requirements

### Required Documentation for Changes

| Change Type | Documentation Required |
|-------------|----------------------|
| CANONICAL modification | Audit report + `[CHANGE]` markers + version bump |
| New pipeline | PIPELINE_REALITY_MAP update |
| Deprecation | PRUNING_CANDIDATES update |
| Deletion | PRUNING_CANDIDATES verification record |

### Audit Report Location

All audit artifacts go to: `docs/ops/`

Naming convention: `<TYPE>_<DATE>.md`
- `WORKFLOW_AUDIT_2026-01-20.md`
- `SCHEMA_AUDIT_2026-02-15.md`
- `CONTRACT_AUDIT_2026-03-01.md`

---

## 7. Summary: Foundation Freeze for Option B

This governance framework freezes the Option A foundation:

| Layer | Status | Implication |
|-------|--------|-------------|
| Canonical Facts (`ovc.*`) | **FROZEN** | No modifications without new audit |
| MIN Contract | **FROZEN** | No field changes without version bump |
| Ingest Pipeline (P1/P2) | **FROZEN** | No logic changes without audit |
| Data Flow Canon | **FROZEN** | Authoritative reference for all downstream |

**Option B may now proceed** with the guarantee that:
1. Canonical facts schema will not change
2. MIN contract fields are stable
3. All derived work reads from a frozen source
4. No upstream changes will invalidate derived computations

---

*End of Governance Rules v0.1*
