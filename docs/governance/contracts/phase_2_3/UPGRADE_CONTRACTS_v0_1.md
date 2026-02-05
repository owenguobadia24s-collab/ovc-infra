# OVC Upgrade Contracts v0.1

**Version**: 0.1  
**Status**: DRAFT — normative  
**Date**: 2026-02-05  
**Phase**: 2.3 — Maintenance Contracts  
**Authority**: This document defines law. It does not define behavior.

---

## 1. Scope

This contract governs all upgrades to OVC state. An **upgrade** is any transition from one valid state to another valid state that is intended to supersede the prior state for operational purposes.

### 1.1 In Scope

- Active pointer updates
- Schema version transitions
- Registry snapshot supersession
- Governance document version transitions
- Threshold pack version transitions
- Operation catalog additions

### 1.2 Out of Scope

- Initial creation of state (not an upgrade — see Phase 0–2 build contracts)
- Deprecation (see Deprecation Contracts v0.1)
- Recovery from failure (see Recovery Contracts v0.1)
- Deletion or erasure (explicitly forbidden by Phase 2 invariants)

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Upgrade** | A state transition from state S₀ to state S₁ where S₁ is intended to supersede S₀ for operational purposes. |
| **Upgradeable State** | Any state class enumerated in Section 3 that is permitted to undergo upgrade transitions. |
| **Silent Upgrade** | An upgrade that occurs without producing auditable evidence. Silent upgrades are forbidden. |
| **Upgrade Evidence** | The minimal set of artifacts that must exist to prove an upgrade occurred. |
| **Prior State** | The state S₀ being superseded. |
| **Successor State** | The state S₁ that supersedes S₀. |
| **Active Pointer** | The sole mutable artifact in the registry layer that selects which sealed artifact is currently active for a given registry. |
| **Sealed Artifact** | An artifact set with manifest.json, MANIFEST.sha256, and valid ROOT_SHA256 per Registry Seal Contract v0.1. |

---

## 3. Upgradeable State Classes

The following state classes are upgradeable under this contract:

| State Class | Upgrade Mechanism | Evidence Required |
|-------------|-------------------|-------------------|
| **Active Pointer** | Pointer file mutation | Delta log record, prior pointer preserved in git |
| **Registry Snapshot** | New sealed run folder + pointer update | Sealed run folder, delta log record |
| **Schema Version** | New schema file + governance review | Schema file with version increment, catalog update |
| **Governance Document** | New versioned document | Document with version increment, prior version frozen |
| **Threshold Pack** | New pack file + active pointer update | Sealed pack file, registry entry |
| **Operation Catalog Entry** | Catalog version increment | Catalog with changelog, prior catalog frozen |

### 3.1 Non-Upgradeable State Classes

The following state classes are NOT upgradeable. They are immutable once created:

| State Class | Reason |
|-------------|--------|
| Sealed run folder contents | Immutable by Phase 2 invariant |
| MANIFEST.sha256 of sealed run | Immutable by Phase 2 invariant |
| Prior governance document versions | Frozen once superseded |
| Git commit history | Append-only by git semantics |
| Delta log records | Append-only by Phase 2.2.3 contract |

---

## 4. Upgrade Preconditions

An upgrade from S₀ to S₁ shall only proceed if ALL of the following preconditions are satisfied:

### 4.1 General Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| UP-PRE-01 | S₀ exists and is valid | S₀ passes validation for its state class |
| UP-PRE-02 | S₁ is well-formed | S₁ passes schema validation for its state class |
| UP-PRE-03 | S₁ is sealed (if applicable) | S₁ passes seal validation per Registry Seal Contract v0.1 |
| UP-PRE-04 | S₁ does not violate determinism | S₁ was produced by deterministic operation or is manually authored governance |
| UP-PRE-05 | Upgrade is intentional | Human or documented automation initiated the upgrade |

### 4.2 Active Pointer Upgrade Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| UP-PTR-01 | Target run folder exists | Path exists at run_root/run_id |
| UP-PTR-02 | Target run folder is sealed | validate_registry_seals_v0_1.py returns PASS |
| UP-PTR-03 | Target manifest_sha256 matches | ROOT_SHA256 in MANIFEST.sha256 equals pointer value |
| UP-PTR-04 | Prior pointer is committed | Prior state of ACTIVE_REGISTRY_POINTERS_v0_1.json is in git |

### 4.3 Schema Version Upgrade Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| UP-SCH-01 | New version > old version | Semantic versioning comparison |
| UP-SCH-02 | Schema is valid JSON Schema | JSON Schema draft-2020-12 compliance |
| UP-SCH-03 | Catalog entry updated | REGISTRY_CATALOG references new schema_version |

---

## 5. Required Upgrade Evidence

Every upgrade shall produce the following evidence:

### 5.1 Mandatory Evidence

| Evidence Class | Requirement |
|----------------|-------------|
| **Git Commit** | The upgrade shall be captured in a git commit |
| **Commit Message** | The commit message shall identify the upgrade type and affected state |
| **Prior State Preservation** | The prior state S₀ shall remain accessible in git history |
| **Timestamp** | The upgrade shall record created_utc or equivalent ISO8601 UTC timestamp |

### 5.2 State-Class-Specific Evidence

| State Class | Additional Evidence |
|-------------|---------------------|
| Active Pointer | Delta log record (if delta log builder executed post-upgrade) |
| Registry Snapshot | Sealed run folder with run.json envelope |
| Schema Version | Schema file with schema_version field |
| Governance Document | Document with version in header |
| Threshold Pack | Pack file with version in filename or content |
| Operation Catalog Entry | Catalog changelog section |

---

## 6. Upgrade Postconditions (Invariants)

After any upgrade, the following invariants shall hold:

| ID | Invariant | Failure Consequence |
|----|-----------|---------------------|
| UP-POST-01 | Prior state S₀ is not erased | Upgrade is invalid; recovery required |
| UP-POST-02 | Prior sealed artifacts are unmodified | Upgrade is invalid; seal contract violated |
| UP-POST-03 | Git history contains both S₀ and S₁ | Audit trail is incomplete |
| UP-POST-04 | S₁ is reachable via current active pointer (if applicable) | Active state is inconsistent |
| UP-POST-05 | No sealed run folder was mutated | Phase 2 invariant violated |
| UP-POST-06 | Determinism is preserved | Non-deterministic upgrade detected |

---

## 7. Active Pointer Upgrade Rules

Active pointers are the sole mechanism for changing which sealed artifact is considered "active" for a registry.

### 7.1 Pointer Update Rules

| ID | Rule |
|----|------|
| PTR-01 | An active pointer update shall only reference a sealed run folder that exists |
| PTR-02 | An active pointer update shall only reference a run folder with valid seal |
| PTR-03 | The manifest_sha256 field shall contain the ROOT_SHA256 from the target MANIFEST.sha256 |
| PTR-04 | The active_asof_utc field shall be updated to reflect the upgrade time |
| PTR-05 | The active_ref_known field shall be set to true only if the seal is validated |
| PTR-06 | The notes field should document the upgrade reason |

### 7.2 Pointer Rollback

| ID | Rule |
|----|------|
| PTR-ROLL-01 | Pointer rollback is a valid upgrade (S₁ may reference an older run than S₀) |
| PTR-ROLL-02 | Rollback shall satisfy all upgrade preconditions |
| PTR-ROLL-03 | Rollback shall produce upgrade evidence |
| PTR-ROLL-04 | Rollback does not modify any sealed artifact |

---

## 8. Forbidden Upgrade Behaviors

The following behaviors are explicitly forbidden:

| ID | Forbidden Behavior | Rationale |
|----|-------------------|-----------|
| UP-FORBID-01 | Modifying contents of a sealed run folder | Violates Phase 2 immutability invariant |
| UP-FORBID-02 | Recomputing MANIFEST.sha256 for existing run | Violates seal integrity |
| UP-FORBID-03 | Deleting prior state from git history | Violates audit requirements |
| UP-FORBID-04 | Upgrading without git commit | Silent upgrade; violates evidence requirement |
| UP-FORBID-05 | Changing active pointer without seal validation | Pointer may reference invalid state |
| UP-FORBID-06 | Backdating timestamps | Violates temporal integrity |
| UP-FORBID-07 | Modifying frozen governance documents | Violates version immutability |
| UP-FORBID-08 | Automated pointer updates without governance review | Introduces execution authority |

---

## 9. Upgrade Failure Conditions

| Condition | Detection | State |
|-----------|-----------|-------|
| UPGRADE_INVALID: precondition not met | Pre-upgrade validation | Upgrade shall not proceed |
| UPGRADE_INVALID: evidence not produced | Post-upgrade audit | Upgrade is non-compliant |
| UPGRADE_INVALID: invariant violated | Post-upgrade validation | Upgrade requires reversal |
| UPGRADE_INVALID: forbidden behavior detected | Audit | Upgrade is void; investigation required |

---

## 10. Cross-References

| Contract | Relationship |
|----------|--------------|
| Deprecation Contracts v0.1 | Deprecation is not upgrade; deprecated state may still be upgraded if not yet replaced |
| Recovery Contracts v0.1 | Recovery may produce upgrades; recovery upgrades must satisfy this contract |
| Health Contracts v0.1 | Upgrade failure may trigger health state transition |
| Registry Seal Contract v0.1 | All sealed state upgrades must satisfy seal contract |
| Phase 2.2.3 Delta Log | Delta log records upgrade transitions for sealed registries |

---

*End of Upgrade Contracts v0.1*
