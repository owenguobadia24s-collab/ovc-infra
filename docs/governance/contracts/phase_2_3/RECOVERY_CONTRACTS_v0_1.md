# OVC Recovery Contracts v0.1

**Version**: 0.1  
**Status**: DRAFT — normative  
**Date**: 2026-02-05  
**Phase**: 2.3 — Maintenance Contracts  
**Authority**: This document defines law. It does not define behavior.

---

## 1. Scope

This contract governs recovery of OVC state. **Recovery** is the reconstruction or restoration of valid state from canonical sources after loss, corruption, or inconsistency.

### 1.1 In Scope

- Replay of sealed artifacts
- Rebuild of derived registries
- Reseal of unsealed artifacts
- Reconstruction from git history
- Recovery from pointer inconsistency
- Recovery from schema drift

### 1.2 Out of Scope

- Normal upgrade operations (see Upgrade Contracts v0.1)
- Deprecation (see Deprecation Contracts v0.1)
- Recovery from external system failures (database, network)
- Recovery requiring data not present in the repository

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Recovery** | The process of reconstructing or restoring valid state from canonical sources. |
| **Canon** | The set of artifacts that constitute authoritative truth: git repository contents, sealed artifacts, and governance documents. |
| **Replay** | Re-execution of a deterministic operation to reproduce an output. |
| **Rebuild** | Construction of a derived artifact from its inputs. |
| **Reseal** | Generation of manifest.json and MANIFEST.sha256 for an unsealed artifact set. |
| **Reconstruction** | Recovery of state from git history or other canonical sources. |
| **Recoverable State** | State that can be recovered from canon alone. |
| **Non-Recoverable State** | State that requires external input not present in canon. |
| **Deterministic Recovery** | Recovery that produces identical output given identical canon. |
| **Idempotent Recovery** | Recovery that can be safely repeated without changing the result. |

---

## 3. Recovery Guarantees

### 3.1 Fundamental Recovery Question

> **"Can truth be reconstructed from canon alone?"**

This contract defines when the answer is YES, when it is PARTIAL, and when it is NO.

### 3.2 Recovery Guarantee Levels

| Level | Definition | Verification |
|-------|------------|--------------|
| **FULL** | State can be exactly reproduced from canon | Deterministic replay produces identical output |
| **PARTIAL** | State can be approximately reproduced; some metadata may differ | Rebuild produces semantically equivalent output |
| **NONE** | State cannot be reproduced from canon | External dependency required |

### 3.3 Recovery Guarantees by State Class

| State Class | Recovery Guarantee | Canonical Source | Notes |
|-------------|-------------------|------------------|-------|
| Sealed run folder | FULL | Git + filesystem | Immutable; recovery = access |
| Run.json envelope | FULL | Git + filesystem | Immutable once sealed |
| Manifest.json | FULL | Computable from folder contents | Deterministic hash |
| MANIFEST.sha256 | FULL | Computable from manifest.json | Deterministic hash |
| Active pointers | FULL | Git history | Any historical state recoverable |
| Governance documents | FULL | Git history | Versioned; all versions in git |
| Schema files | FULL | Git history | Versioned; all versions in git |
| Run registry | FULL | Rebuild from filesystem | Deterministic scan |
| Op status table | FULL | Rebuild from run registry + governance | Deterministic derivation |
| Drift signals | FULL | Rebuild from op status table + expected versions | Deterministic derivation |
| Delta log | FULL | Rebuild from sealed runs | Deterministic diff |
| System health report | FULL | Rebuild from drift signals | Deterministic render |
| Threshold registry DB | NONE | External database | Not in canon |
| External API state | NONE | External system | Not in canon |
| Worker runtime state | NONE | External process | Not in canon |

---

## 4. Replay Guarantees

Replay is the re-execution of a deterministic operation to reproduce an output.

### 4.1 Replay Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| REP-PRE-01 | Operation is deterministic | Operation spec declares determinism = YES |
| REP-PRE-02 | All inputs are available | Inputs exist in canon |
| REP-PRE-03 | Operation executable exists | Builder script present in git |
| REP-PRE-04 | No external dependencies | Operation does not require network/DB |

### 4.2 Replay Rules

| ID | Rule |
|----|------|
| REPLAY-01 | Replay of deterministic operation shall produce identical output given identical inputs |
| REPLAY-02 | Replay shall use the same operation version as original execution |
| REPLAY-03 | Timestamp fields in run.json are exempt from identity requirement |
| REPLAY-04 | Git commit in run.json may differ if replay occurs at different commit |
| REPLAY-05 | ROOT_SHA256 shall be identical if all content is identical |

### 4.3 Replay-Eligible Operations

| Operation | Replay Eligible | Reason |
|-----------|-----------------|--------|
| OP-QA07 Run Registry Build | YES | Deterministic filesystem scan |
| OP-QA08 Op Status Table Build | YES | Deterministic derivation |
| OP-QA09 Drift Signals Build | YES | Deterministic derivation |
| OP-QA10 System Health Render | YES | Deterministic render |
| OP-QA11 Delta Log Build | YES | Deterministic diff |
| All Phase 2.1/2.2 builders | YES | All declared deterministic |

---

## 5. Rebuild Guarantees

Rebuild is the construction of a derived artifact from its inputs.

### 5.1 Rebuild Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| REB-PRE-01 | Inputs are available | Input artifacts exist |
| REB-PRE-02 | Builder is available | Builder script in git |
| REB-PRE-03 | Input seals are valid | Input artifacts pass seal validation |

### 5.2 Rebuild Rules

| ID | Rule |
|----|------|
| REBUILD-01 | Rebuild produces new run folder; does not modify existing |
| REBUILD-02 | Rebuild output is sealed per Registry Seal Contract v0.1 |
| REBUILD-03 | Rebuild may produce different run_id (timestamp-based) |
| REBUILD-04 | Rebuild content shall be identical to prior build given identical inputs |
| REBUILD-05 | Rebuild shall update active pointer if designated as active |

### 5.3 Rebuild Order (Dependency Chain)

Rebuilds shall respect the following dependency order:

```
1. run_registry (no dependencies)
2. op_status_table (depends on: run_registry)
3. drift_signals (depends on: op_status_table, expected_versions)
4. system_health_report (depends on: drift_signals, op_status_table, run_registry)
5. delta_log (depends on: all sealed runs)
```

---

## 6. Reseal Guarantees

Reseal is the generation of manifest.json and MANIFEST.sha256 for an artifact set.

### 6.1 Reseal Preconditions

| ID | Precondition | Verification |
|----|--------------|--------------|
| RESEAL-PRE-01 | Artifact set exists | Files present in folder |
| RESEAL-PRE-02 | run.json exists | Envelope is present |
| RESEAL-PRE-03 | No prior seal exists | manifest.json and MANIFEST.sha256 absent |

### 6.2 Reseal Rules

| ID | Rule |
|----|------|
| RESEAL-01 | Reseal shall not modify any file except manifest.json and MANIFEST.sha256 |
| RESEAL-02 | Reseal shall produce deterministic manifest per Registry Seal Contract v0.1 |
| RESEAL-03 | Reseal of identical content shall produce identical ROOT_SHA256 |
| RESEAL-04 | Reseal shall not be applied to already-sealed folders (use rebuild instead) |

### 6.3 Reseal Prohibition

| ID | Prohibition |
|----|-------------|
| RESEAL-FORBID-01 | Resealing an already-sealed folder is forbidden |
| RESEAL-FORBID-02 | Modifying content before resealing invalidates provenance |
| RESEAL-FORBID-03 | Resealing to change ROOT_SHA256 is forbidden |

---

## 7. Determinism Expectations

### 7.1 Deterministic Recovery Guarantees

| Guarantee | Condition |
|-----------|-----------|
| Given identical git state, rebuild produces identical content | All inputs from git |
| Given identical filesystem state, run registry scan is identical | Filesystem is input |
| Given identical sealed inputs, delta log is identical | Sealed manifests are input |

### 7.2 Non-Deterministic Elements (Exempt)

| Element | Reason |
|---------|--------|
| run_id | Contains timestamp of execution |
| created_utc in run.json | Timestamp of execution |
| git_commit in run.json | May differ if rebuilt at different commit |
| working_tree_state in run.json | May differ based on git state |

### 7.3 Determinism Verification

| ID | Verification |
|----|--------------|
| DET-01 | Content hash (excluding run.json) shall be identical across replays |
| DET-02 | ROOT_SHA256 may differ only due to run.json changes |
| DET-03 | If content is byte-identical, ROOT_SHA256 shall be identical |

---

## 8. Out-of-Scope Recovery Cases

The following recovery cases are explicitly out of scope for this contract:

| Case | Reason | Mitigation |
|------|--------|------------|
| **Lost git repository** | Canon is lost | External backup required |
| **Corrupted git history** | Canon is corrupted | Git fsck, backup restore |
| **External database state** | Not in canon | Database backup/restore procedures |
| **Runtime process state** | Ephemeral | Restart process |
| **Network service state** | External | Service-specific recovery |
| **Hardware failure** | Infrastructure | Infrastructure recovery procedures |
| **Malicious modification** | Adversarial | Incident response, audit trail |

### 8.1 Recovery Boundaries

| Boundary | Within Canon | Outside Canon |
|----------|--------------|---------------|
| Git repository | All committed files | Uncommitted changes |
| Filesystem | .codex/RUNS, reports | External paths |
| Configuration | Committed configs | Runtime environment |
| Database | SQL DDL in repo | Live database state |

---

## 9. Recovery Procedures (Normative Constraints)

This section defines constraints on recovery procedures, not the procedures themselves.

### 9.1 Recovery Procedure Requirements

| ID | Requirement |
|----|-------------|
| REC-PROC-01 | Recovery shall be documented before execution |
| REC-PROC-02 | Recovery shall not modify sealed artifacts |
| REC-PROC-03 | Recovery outputs shall be sealed |
| REC-PROC-04 | Recovery shall be auditable via git history |
| REC-PROC-05 | Recovery shall satisfy Upgrade Contracts if producing new state |

### 9.2 Recovery Evidence

| Evidence | Required |
|----------|----------|
| Recovery run folder | YES |
| run.json with recovery metadata | YES |
| Git commit documenting recovery | YES |
| Prior state preservation | YES |

---

## 10. Recovery Failure Conditions

| Condition | Detection | State |
|-----------|-----------|-------|
| RECOVERY_IMPOSSIBLE: input not in canon | Pre-recovery validation | Recovery cannot proceed |
| RECOVERY_IMPOSSIBLE: external dependency | Dependency analysis | Out of scope for this contract |
| RECOVERY_FAILED: determinism violated | Post-recovery verification | Output differs from expected |
| RECOVERY_FAILED: seal invalid | Seal validation | Rebuilt artifact failed sealing |
| RECOVERY_PARTIAL: metadata differs | Content comparison | Acceptable if content identical |

---

## 11. Cross-References

| Contract | Relationship |
|----------|--------------|
| Upgrade Contracts v0.1 | Recovery that produces new state is an upgrade |
| Deprecation Contracts v0.1 | Deprecated objects are still recoverable |
| Health Contracts v0.1 | Recovery may restore healthy state |
| Registry Seal Contract v0.1 | All recovery outputs must satisfy seal contract |
| Phase 2.2.3 Delta Log | Delta log is rebuilt from sealed runs |

---

*End of Recovery Contracts v0.1*
