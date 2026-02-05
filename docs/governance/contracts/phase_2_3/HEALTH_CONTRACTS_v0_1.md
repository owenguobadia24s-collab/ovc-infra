# OVC Health Contracts v0.1

**Version**: 0.1  
**Status**: DRAFT — normative  
**Date**: 2026-02-05  
**Phase**: 2.3 — Maintenance Contracts  
**Authority**: This document defines law. It does not define behavior.

---

## 1. Scope

This contract defines the legal health states of OVC and the conditions under which each state applies. Health states are **legally defined, not inferred**. System condition is made legible without interpretation.

### 1.1 In Scope

- Definition of named health states
- Invariant violations permitted per state
- Degradation classification (blocking vs non-blocking)
- Mapping from governance gaps to health states
- Health state transition conditions

### 1.2 Out of Scope

- Health monitoring implementation
- Alerting mechanisms
- Automated remediation
- Performance metrics
- Runtime health checks of external systems

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Health State** | A named, legally defined condition of the OVC system. |
| **Invariant** | A property that must hold for the system to be considered fully healthy. |
| **Invariant Violation** | A condition where an invariant does not hold. |
| **Degradation** | A health state below HEALTHY where some invariants are violated. |
| **Blocking Degradation** | Degradation that prevents core operations from proceeding. |
| **Non-Blocking Degradation** | Degradation that permits core operations but with reduced guarantees. |
| **Governance Gap** | A known limitation documented in governance artifacts. |
| **Bounded Gap** | A governance gap with known scope and documented impact. |
| **Unbounded Gap** | A governance gap with unknown scope (forbidden by Phase 2 closure). |

---

## 3. Named Health States

OVC shall exist in exactly one of the following health states at any time:

| State | Code | Definition |
|-------|------|------------|
| **HEALTHY** | H0 | All invariants hold. No degradation. |
| **DEGRADED_NON_BLOCKING** | H1 | Some invariants violated. Core operations permitted. |
| **DEGRADED_BLOCKING** | H2 | Critical invariants violated. Some operations blocked. |
| **RECOVERY_REQUIRED** | H3 | System cannot proceed without recovery action. |
| **UNKNOWN** | H9 | Health cannot be determined from available evidence. |

### 3.1 State Precedence

If multiple conditions apply, the most severe state takes precedence:

```
UNKNOWN > RECOVERY_REQUIRED > DEGRADED_BLOCKING > DEGRADED_NON_BLOCKING > HEALTHY
```

### 3.2 State Exclusivity

The system shall be in exactly one health state. Health state is a function of observable evidence, not judgment.

---

## 4. Health State Definitions

### 4.1 HEALTHY (H0)

**Definition**: All governance invariants hold. All registries are sealed or explicitly justified as non-sealable. All active pointers reference valid sealed artifacts.

**Conditions (ALL must be true)**:

| ID | Condition |
|----|-----------|
| H0-01 | All sealed registries pass seal validation |
| H0-02 | All active pointers with active_ref_known=true reference valid seals |
| H0-03 | All active pointers have manifest_sha256 matching target ROOT_SHA256 |
| H0-04 | No schema drift detected (expected versions match observed) |
| H0-05 | All governance documents are at current version |
| H0-06 | All bounded gaps are documented and justified |
| H0-07 | No RECOVERY_REQUIRED or DEGRADED conditions exist |

**Invariant Violations Allowed**: None.

---

### 4.2 DEGRADED_NON_BLOCKING (H1)

**Definition**: Some invariants are violated but core operations may proceed. The system is functional with reduced guarantees.

**Conditions (ANY triggers H1 if H2/H3 conditions not met)**:

| ID | Condition | Impact |
|----|-----------|--------|
| H1-01 | Schema version drift detected | May produce output with old schema |
| H1-02 | Threshold pack drift detected | May use non-current thresholds |
| H1-03 | Some registries at C2 enforcement (no CI gate) | Reduced enforcement |
| H1-04 | active_ref_known = "unknown" for non-closable registries | Expected limitation |
| H1-05 | Presentation artifacts (system_health_report) unsealed | Presentation-only |
| H1-06 | Deprecated objects still referenced | Transition state |
| H1-07 | Git working_tree_state = "dirty" during operation | Uncommitted changes |

**Invariant Violations Allowed**:
- Schema version mismatch (non-breaking)
- Threshold pack version mismatch
- C2 enforcement level for non-critical operations
- Unknown state for explicitly non-closable registries

**Core Operations Permitted**: All.

---

### 4.3 DEGRADED_BLOCKING (H2)

**Definition**: Critical invariants are violated. Some operations are blocked until remediation.

**Conditions (ANY triggers H2)**:

| ID | Condition | Blocked Operations |
|----|-----------|-------------------|
| H2-01 | Seal validation fails for active registry | Operations depending on that registry |
| H2-02 | Active pointer references non-existent run folder | Operations using that pointer |
| H2-03 | manifest_sha256 mismatch with target ROOT_SHA256 | Pointer-dependent operations |
| H2-04 | Required governance document missing | Governance-dependent builds |
| H2-05 | Schema file missing for active registry | Schema validation |
| H2-06 | Circular replacement chain detected | Affected upgrade/deprecation |
| H2-07 | Delta log references invalid sealed run | Delta log consumers |

**Invariant Violations Allowed**:
- Violations enumerated in the specific condition

**Blocked Operations**:
- Operations explicitly listed in the condition
- Downstream operations depending on blocked operations

**Permitted Operations**:
- Operations not depending on violated invariants
- Read-only access to unaffected artifacts
- Recovery operations

---

### 4.4 RECOVERY_REQUIRED (H3)

**Definition**: System cannot proceed without explicit recovery action. Automatic remediation is not possible.

**Conditions (ANY triggers H3)**:

| ID | Condition | Required Action |
|----|-----------|-----------------|
| H3-01 | Sealed artifact content corrupted (hash mismatch) | Rebuild from inputs or restore from backup |
| H3-02 | Active pointers file corrupted or invalid JSON | Restore from git history |
| H3-03 | Registry catalog missing or invalid | Restore from git history |
| H3-04 | Git repository state inconsistent | Git fsck and repair |
| H3-05 | Multiple conflicting active states | Manual resolution |
| H3-06 | Phase 0–2 invariant violation detected | Manual investigation |
| H3-07 | Forbidden behavior detected (per Upgrade/Deprecation contracts) | Incident response |

**Invariant Violations**: Critical — system integrity compromised.

**All Operations Blocked** except:
- Diagnostic operations
- Recovery operations per Recovery Contracts v0.1

---

### 4.5 UNKNOWN (H9)

**Definition**: Health cannot be determined from available evidence.

**Conditions (ANY triggers H9)**:

| ID | Condition |
|----|-----------|
| H9-01 | Governance artifacts cannot be read |
| H9-02 | Filesystem access failure |
| H9-03 | Git state cannot be determined |
| H9-04 | Validation tools fail to execute |
| H9-05 | Health check itself produces error |

**Treatment**: UNKNOWN shall be treated as RECOVERY_REQUIRED for operational purposes.

---

## 5. Degraded But Acceptable Conditions

The following conditions are explicitly acceptable degradation (H1):

| Condition | Justification | Reference |
|-----------|---------------|-----------|
| threshold_registry_db active_ref_known = "unknown" | External database; cannot verify from repo | Governance Scorecard v0.2 |
| validation_range_results active_ref_known = "unknown" | Collection registry; no single active | Governance Scorecard v0.2 |
| evidence_pack_registry active_ref_known = "unknown" | Collection registry; individually sealed | Governance Scorecard v0.2 |
| system_health_report active_ref_known = "unknown" | Presentation-only artifact | Governance Scorecard v0.2 |
| Operations at C2 enforcement | No CI gate; runtime validation only | Enforcement Matrix v0.2 |
| 5 ops at C2 (OP-D06, OP-D07, OP-D10, OP-QA05, OP-QA06) | Documented weak governance | Enforcement Matrix v0.2 |
| Migration ledger entries UNVERIFIED | Cannot prove when applied | Governance Scorecard v0.2 |
| Worker deployment UNKNOWN | Cannot prove live ingest | Governance Scorecard v0.2 |
| Git working_tree_state = "dirty" | Uncommitted changes during development | Normal development |

---

## 6. Governance Gap to Health State Mapping

Mapping from Governance Completeness Scorecard v0.2 gaps:

| Gap | Health State | Rationale |
|-----|--------------|-----------|
| 5 ops at C2 | H1 (DEGRADED_NON_BLOCKING) | Reduced enforcement, bounded |
| C3 workflow args | H0 (HEALTHY) | Materialized via CI; not a violation |
| Migration ledger entries UNVERIFIED | H1 (DEGRADED_NON_BLOCKING) | Historical uncertainty, bounded |
| Worker deployment UNKNOWN | H1 (DEGRADED_NON_BLOCKING) | External verification required |
| threshold_registry_db unverifiable | H1 (DEGRADED_NON_BLOCKING) | Non-closable by design |
| validation_range_results no single active | H0 (HEALTHY) | By design; not a violation |
| evidence_pack_registry no single active | H0 (HEALTHY) | By design; not a violation |
| system_health_report no single active | H0 (HEALTHY) | Presentation; not a violation |

---

## 7. Health State Transitions

### 7.1 Valid Transitions

| From | To | Trigger |
|------|----|----|
| H0 | H1 | Non-blocking degradation condition detected |
| H0 | H2 | Blocking degradation condition detected |
| H0 | H3 | Recovery-required condition detected |
| H0 | H9 | Evidence unavailable |
| H1 | H0 | All H1 conditions remediated |
| H1 | H2 | Blocking condition added |
| H1 | H3 | Recovery-required condition detected |
| H1 | H9 | Evidence unavailable |
| H2 | H0 | All H2 and H1 conditions remediated |
| H2 | H1 | Blocking conditions remediated, non-blocking remain |
| H2 | H3 | Recovery-required condition detected |
| H2 | H9 | Evidence unavailable |
| H3 | H0 | Recovery complete, all conditions remediated |
| H3 | H1 | Recovery complete, non-blocking conditions remain |
| H3 | H2 | Recovery partial, blocking conditions remain |
| H3 | H9 | Evidence unavailable during recovery |
| H9 | Any | Evidence becomes available |

### 7.2 Transition Evidence

Every health state transition shall be evidenced by:

| Evidence | Required |
|----------|----------|
| Validation output showing condition | YES |
| Timestamp of detection | YES |
| Git commit if remediation performed | YES (for remediation) |

---

## 8. Health Invariants

The following invariants define HEALTHY state:

### 8.1 Seal Invariants

| ID | Invariant |
|----|-----------|
| SEAL-INV-01 | Every active pointer with active_ref_known=true references a valid seal |
| SEAL-INV-02 | manifest_sha256 in pointer equals ROOT_SHA256 in target |
| SEAL-INV-03 | All files in manifest.json exist with matching hash and size |

### 8.2 Pointer Invariants

| ID | Invariant |
|----|-----------|
| PTR-INV-01 | ACTIVE_REGISTRY_POINTERS_v0_1.json is valid JSON |
| PTR-INV-02 | Every pointer has registry_id matching catalog entry |
| PTR-INV-03 | No duplicate registry_id entries |

### 8.3 Governance Invariants

| ID | Invariant |
|----|-----------|
| GOV-INV-01 | Registry catalog exists and is valid JSON |
| GOV-INV-02 | All referenced schemas exist |
| GOV-INV-03 | Governance document versions are consistent |

### 8.4 Determinism Invariants

| ID | Invariant |
|----|-----------|
| DET-INV-01 | All deterministic operations produce identical output for identical input |
| DET-INV-02 | ROOT_SHA256 is reproducible |

---

## 9. Health State Determination Rules

Health state shall be determined by applying conditions in order of severity:

1. Check for H9 (UNKNOWN) conditions first
2. Check for H3 (RECOVERY_REQUIRED) conditions
3. Check for H2 (DEGRADED_BLOCKING) conditions
4. Check for H1 (DEGRADED_NON_BLOCKING) conditions
5. If no degradation conditions found, state is H0 (HEALTHY)

### 9.1 Determination is Stateless

Health state is determined from current evidence only. Prior health state does not influence determination.

### 9.2 Determination is Deterministic

Given identical evidence, health state determination shall produce identical result.

---

## 10. Failure Conditions

| Condition | Health State |
|-----------|--------------|
| HEALTH_UNDETERMINED: evidence unavailable | H9 |
| HEALTH_DEGRADED: non-blocking violations | H1 |
| HEALTH_BLOCKED: blocking violations | H2 |
| HEALTH_CRITICAL: recovery required | H3 |

---

## 11. Cross-References

| Contract | Relationship |
|----------|--------------|
| Upgrade Contracts v0.1 | Failed upgrade may cause H2 or H3 |
| Deprecation Contracts v0.1 | Use of deprecated objects may cause H1 |
| Recovery Contracts v0.1 | Recovery is required to exit H3 |
| Registry Seal Contract v0.1 | Seal validation failures cause H2 |
| Governance Completeness Scorecard v0.2 | Gap mapping source |
| Enforcement Coverage Matrix v0.2 | Enforcement level source |

---

*End of Health Contracts v0.1*
