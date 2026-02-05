# OVC Deprecation Contracts v0.1

**Version**: 0.1  
**Status**: DRAFT — normative  
**Date**: 2026-02-05  
**Phase**: 2.3 — Maintenance Contracts  
**Authority**: This document defines law. It does not define behavior.

---

## 1. Scope

This contract governs deprecation of OVC state. **Deprecation** is loss of authority, not erasure. Deprecated state retains meaning, remains auditable, and may be required for replay.

### 1.1 In Scope

- Deprecation of sealed artifacts
- Deprecation of governance documents
- Deprecation of schema versions
- Deprecation of operations
- Deprecation of registries
- Deprecation of threshold packs

### 1.2 Out of Scope

- Deletion or erasure (explicitly forbidden by Phase 2 invariants)
- Upgrade (see Upgrade Contracts v0.1)
- Recovery (see Recovery Contracts v0.1)
- Archival without deprecation (not a state transition)

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Deprecation** | A state transition marking an object as no longer authoritative for new operations while preserving its existence and meaning for historical purposes. |
| **Deprecated Object** | Any object that has undergone deprecation. |
| **Authoritative** | The property of being valid for use in new operations. |
| **Historical Authority** | The property of being valid for replay, audit, and understanding of prior state. |
| **Replacement** | A successor object that supersedes a deprecated object for new operations. |
| **Mandatory Replacement** | A replacement that must exist before deprecation is valid. |
| **Optional Replacement** | A replacement that may exist but is not required for deprecation. |
| **Deprecation Record** | Machine-readable metadata documenting the deprecation. |
| **Soft Deprecation** | Deprecation with optional replacement; deprecated object may still be used with warning. |
| **Hard Deprecation** | Deprecation with mandatory replacement; deprecated object shall not be used for new operations. |

---

## 3. Deprecatable Object Classes

The following object classes may be deprecated:

| Object Class | Deprecation Type | Replacement Requirement |
|--------------|------------------|------------------------|
| **Sealed Run Folder** | Soft | Optional (superseded by newer run) |
| **Governance Document Version** | Hard | Mandatory (superseding version must exist) |
| **Schema Version** | Hard | Mandatory (superseding schema must exist) |
| **Operation (Catalog Entry)** | Soft or Hard | Soft: documented alternative; Hard: replacement operation |
| **Registry** | Hard | Mandatory (migration path must exist) |
| **Threshold Pack** | Soft | Optional (newer pack may exist) |
| **Active Pointer Target** | Soft | Optional (newer target selected) |

### 3.1 Non-Deprecatable Objects

The following objects cannot be deprecated:

| Object | Reason |
|--------|--------|
| Git commits | Immutable historical record |
| MANIFEST.sha256 content | Immutable seal |
| ROOT_SHA256 values | Immutable cryptographic commitment |
| Delta log records | Append-only memory |
| Phase 0–2 invariants | Foundational law |

---

## 4. Deprecation Preconditions

Deprecation shall only proceed if ALL of the following preconditions are satisfied:

### 4.1 General Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| DEP-PRE-01 | Object exists and is valid | Object passes validation for its class |
| DEP-PRE-02 | Object is not already deprecated | Deprecation record does not exist |
| DEP-PRE-03 | Deprecation is intentional | Human or documented governance process initiated |
| DEP-PRE-04 | Replacement exists (if mandatory) | Replacement object passes validation |
| DEP-PRE-05 | Object is not required for active system state | Active pointers do not reference it, or deprecation is explicitly overriding |

### 4.2 Governance Document Deprecation Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| DEP-GOV-01 | Superseding version exists | New version file present |
| DEP-GOV-02 | Superseding version references prior | "Supersedes" field in new version |
| DEP-GOV-03 | Prior version is frozen | Prior version content shall not change |

### 4.3 Schema Deprecation Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| DEP-SCH-01 | Superseding schema exists | New schema file present |
| DEP-SCH-02 | Migration path documented | Documentation exists for data migration |
| DEP-SCH-03 | Catalog updated | Registry catalog references new schema |

---

## 5. Required Deprecation Metadata

Every deprecation shall produce the following metadata:

### 5.1 Deprecation Record Structure

```json
{
  "deprecated_object_id": "<unique identifier>",
  "deprecated_object_class": "<object class from Section 3>",
  "deprecated_object_path": "<path or reference>",
  "deprecation_type": "soft | hard",
  "deprecated_utc": "<ISO8601 UTC timestamp>",
  "deprecated_by": "<actor identifier>",
  "replacement_object_id": "<replacement identifier or null>",
  "replacement_object_path": "<replacement path or null>",
  "deprecation_reason": "<human-readable reason>",
  "replay_guarantee": "full | partial | none",
  "audit_guarantee": "full | partial | none"
}
```

### 5.2 Mandatory Metadata Fields

| Field | Required For | Description |
|-------|--------------|-------------|
| deprecated_object_id | All | Unique identifier within object class |
| deprecated_object_class | All | Classification per Section 3 |
| deprecated_utc | All | Timestamp of deprecation |
| deprecation_type | All | Soft or hard |
| deprecation_reason | All | Human-readable justification |
| replacement_object_id | Hard deprecation | Identifier of replacement |
| replay_guarantee | All | Replay capability post-deprecation |
| audit_guarantee | All | Audit capability post-deprecation |

---

## 6. Replay and Audit Guarantees

Deprecated objects shall maintain the following guarantees:

### 6.1 Replay Guarantees

| Guarantee Level | Definition |
|-----------------|------------|
| **Full** | Deprecated object can be used to exactly reproduce historical outputs |
| **Partial** | Deprecated object can be used to understand historical outputs but not reproduce them exactly |
| **None** | Deprecated object provides no replay capability (external dependency lost) |

### 6.2 Audit Guarantees

| Guarantee Level | Definition |
|-----------------|------------|
| **Full** | Deprecated object content is fully preserved and readable |
| **Partial** | Deprecated object existence is documented but content may be summarized |
| **None** | Deprecated object is referenced but not preserved (forbidden for sealed artifacts) |

### 6.3 Minimum Guarantees by Object Class

| Object Class | Minimum Replay | Minimum Audit |
|--------------|----------------|---------------|
| Sealed Run Folder | Full | Full |
| Governance Document | Full | Full |
| Schema Version | Full | Full |
| Operation | Partial | Full |
| Registry | Partial | Full |
| Threshold Pack | Full | Full |

---

## 7. Replacement Semantics

### 7.1 Mandatory Replacement Rules

| ID | Rule |
|----|------|
| REP-01 | Hard deprecation shall not proceed without valid replacement |
| REP-02 | Replacement shall be of the same object class as deprecated object |
| REP-03 | Replacement shall reference the deprecated object it supersedes |
| REP-04 | Replacement shall satisfy all validation for its object class |

### 7.2 Optional Replacement Rules

| ID | Rule |
|----|------|
| REP-OPT-01 | Soft deprecation may proceed without replacement |
| REP-OPT-02 | If replacement exists, it should be documented |
| REP-OPT-03 | Absence of replacement shall be noted in deprecation record |

### 7.3 Replacement Chain Integrity

| ID | Rule |
|----|------|
| REP-CHAIN-01 | Replacement chains shall be traceable |
| REP-CHAIN-02 | Circular replacements are forbidden |
| REP-CHAIN-03 | A deprecated object may have at most one direct replacement |

---

## 8. Machine-Readable Deprecation State

Deprecation state shall be machine-readable through the following mechanisms:

### 8.1 Governance Documents

Governance documents shall declare deprecation state in their header:

```markdown
**Status**: DEPRECATED — superseded by v0.2
**Superseded By**: <document path>
**Deprecated UTC**: <ISO8601 timestamp>
```

### 8.2 Schema Files

Schema files shall declare deprecation in the schema metadata:

```json
{
  "$schema": "...",
  "deprecated": true,
  "superseded_by": "<schema_id>",
  "deprecated_utc": "<ISO8601 timestamp>"
}
```

### 8.3 Registry Catalog

The registry catalog shall track deprecation:

```json
{
  "registry_id": "...",
  "deprecated": true,
  "deprecated_utc": "<ISO8601 timestamp>",
  "replacement_registry_id": "<registry_id or null>"
}
```

### 8.4 Deprecation Index

A deprecation index file may aggregate all deprecation records:

- Path: `docs/governance/DEPRECATION_INDEX_v0_1.json`
- Format: Array of deprecation records per Section 5.1

---

## 9. Forbidden Deprecation Behaviors

The following behaviors are explicitly forbidden:

| ID | Forbidden Behavior | Rationale |
|----|-------------------|-----------|
| DEP-FORBID-01 | Erasing deprecated object | Violates Phase 2 preservation invariant |
| DEP-FORBID-02 | Modifying deprecated sealed artifact | Violates seal integrity |
| DEP-FORBID-03 | Deprecating without record | Silent deprecation; violates audit requirement |
| DEP-FORBID-04 | Hard deprecation without replacement | Leaves gap in operational capability |
| DEP-FORBID-05 | Deprecating active pointer target without pointer update | Inconsistent active state |
| DEP-FORBID-06 | Deprecating Phase 0–2 invariants | Foundational law is immutable |
| DEP-FORBID-07 | Removing deprecated object from git | Violates historical preservation |

---

## 10. Deprecation Failure Conditions

| Condition | Detection | State |
|-----------|-----------|-------|
| DEPRECATION_INVALID: object not found | Pre-deprecation validation | Deprecation shall not proceed |
| DEPRECATION_INVALID: already deprecated | Pre-deprecation check | Double deprecation forbidden |
| DEPRECATION_INVALID: mandatory replacement missing | Pre-deprecation validation | Hard deprecation blocked |
| DEPRECATION_INVALID: record not produced | Post-deprecation audit | Non-compliant deprecation |
| DEPRECATION_INVALID: object erased | Audit detection | Critical violation; recovery required |

---

## 11. Cross-References

| Contract | Relationship |
|----------|--------------|
| Upgrade Contracts v0.1 | Deprecation is not upgrade; deprecated objects may still exist alongside upgrades |
| Recovery Contracts v0.1 | Recovery may use deprecated objects; deprecation does not prevent recovery |
| Health Contracts v0.1 | Use of deprecated objects may affect health state |
| Registry Seal Contract v0.1 | Deprecated sealed artifacts retain valid seals |
| Phase 2.2.3 Delta Log | Delta log may reference deprecated and non-deprecated snapshots |

---

*End of Deprecation Contracts v0.1*
