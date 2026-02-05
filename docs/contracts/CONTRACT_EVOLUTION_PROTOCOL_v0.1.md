# CONTRACT_EVOLUTION_PROTOCOL_v0.1

**Version:** 0.1  
**Status:** Draft (Protocol Skeleton)  
**Authority:** Governance — Non-Runtime  
**Applies From:** Phase 3 onward  
**Prime Invariant:** Contracts may evolve; truth may not be rewritten.

---

## 0. Preamble (Non-Interpretive)

### Purpose

- Define the only lawful process by which canonical contracts in `ovc-infra` may change.
- Prevent authority leakage via informal schema drift or ad-hoc evolution.

### Non-Goals

- Does not define runtime behavior.
- Does not authorize execution, mutation, or interpretation.
- Does not replace Phase-specific contracts (e.g., `PHASE3_CANON_SCHEMA_CONTRACT_v0.1`).

---

## 1. Scope of This Protocol

### 1.1 Contracts Governed

This protocol applies to the evolution of the following contract classes within `ovc-infra`:

| Contract Class | Example |
|----------------|---------|
| Schema contracts | `PHASE3_CANON_SCHEMA_CONTRACT_v0.1` |
| Health contracts | `HEALTH_CONTRACTS_v0.1` |
| Registry structure contracts | `REGISTRY_CATALOG_v0_1.json` |
| Governance visibility contracts | `GOVERNANCE_RULES_v0.1.md` |

### 1.2 Explicitly Out of Scope

This protocol does not govern:

- Runtime logic
- UI behavior or semantics
- Agent reasoning or outputs
- Execution workflows
- Scheduling or automation

---

## 2. Version Semantics

### 2.1 Version Format

Contract versions follow: `v{MAJOR}.{MINOR}`

### 2.2 Semantic Meaning

| Version Change | Meaning |
|----------------|---------|
| Minor (v0.1 → v0.2) | Backward-compatible evolution |
| Major (v0.x → v1.0) | Breaking change to contract meaning |

### 2.3 Immutability Declaration

- Once superseded, prior versions remain valid, readable, and authoritative for their time.
- No contract version MAY be altered retroactively.

---

## 3. Change Classification

### 3.1 Changes That Require a Version Bump

| Change Type | Bump Required |
|-------------|---------------|
| New required field | YES |
| Removal of required field | YES |
| Type change | YES |
| Nullability change | YES |
| Field semantic reinterpretation | YES |
| Constraint tightening | YES |

### 3.2 Changes That Do Not Require a Version Bump

| Change Type | Bump Required |
|-------------|---------------|
| New optional field (unknown keys allowed) | NO |
| Documentation clarification | NO |
| Example expansion | NO |

### 3.3 Default Rule

If a change does not clearly belong to §3.2, it MUST require a bump.

---

## 4. Evidence Requirements

### 4.1 Mandatory Evidence Types

Every proposed contract evolution MUST include:

| Evidence Type | Description |
|---------------|-------------|
| Observed artifacts | Real files from `.codex/RUNS/` |
| Counts and nullability statistics | Field presence/null counts |
| Timestamped source runs | Run ID with creation timestamp |
| Explicit extraction method | Script or command used |

### 4.2 Evidence Location

- Evidence MUST reside in canonical repo paths within `ovc-infra`.
- Ad-hoc or external references are FORBIDDEN.

### 4.3 Forbidden Evidence

The following MAY NOT justify evolution:

- Hypothetical structures
- Planned features
- Agent-generated summaries
- Inferred intent

---

## 5. Legacy Preservation Guarantees

### 5.1 Historical Readability

All historical artifacts in `.codex/RUNS/` MUST remain parseable indefinitely.

### 5.2 No Semantic Rewrites

- Evolution MAY NOT reinterpret historical meaning.
- Legacy nulls remain nulls.
- Legacy omissions remain omissions.

### 5.3 Forward Compatibility Rule

New validators MUST accept legacy artifacts unchanged.

---

## 6. Authority Model

### 6.1 Proposal Authority

- Only human actors MAY propose contract evolution (v0.x).
- Proposals MUST be explicit and documented.

### 6.2 Ratification Authority

Ratification requires:

| Requirement | Description |
|-------------|-------------|
| Evidence verification | All §4.1 evidence present and valid |
| Audit re-execution | Phase 3.1 audits pass |
| Explicit approval | Human sign-off recorded |

#### 6.2.1 Ratification Artifact Requirement

Ratification MUST be recorded as a standalone markdown file.

| Property | Requirement |
|----------|-------------|
| Location | `docs/contracts/ratifications/` |
| Filename | `CONTRACT_<contract_name>_v<new_version>__RATIFICATION.md` |

#### 6.2.2 Ratification Artifact Contents

The ratification file MUST include:

| Section | Description |
|---------|-------------|
| Contract Identifier | Contract name and new version |
| Approval Statement | Explicit statement of ratification |
| Evidence Index | Paths and run IDs for all evidence |
| Audit Re-Validation Table | Audit name, run ID, PASS/FAIL for each required audit |
| Human Signatory Block | Name/role + UTC timestamp |

#### 6.2.3 Ratification Enforcement

- Absence of a valid ratification artifact SHALL be treated as non-ratification.
- Non-ratified changes MUST NOT alter canon.

### 6.3 Separation of Powers

No single actor MAY both propose and ratify.

---

## 7. Mandatory Re-Validation

### 7.1 Required Audits

Any contract bump MUST require successful re-execution of:

| Audit | Location |
|-------|----------|
| Read-Only Audit | `tools/phase3_control_panel/audits/phase3_read_only_audit.py` |
| UI Action Audit | `tools/phase3_control_panel/audits/phase3_ui_action_audit.py` |
| No Network Mutation Audit | `tools/phase3_control_panel/audits/phase3_no_network_mutation_audit.py` |
| Schema validation | Against all legacy artifacts in `.codex/RUNS/` |

#### 7.1.1 Audit Execution as Observable Runs

Each required audit MUST be executed as a fresh audit-only run.

| Requirement | Description |
|-------------|-------------|
| Run Location | `.codex/RUNS/` |
| Run Contents | `run.json`, audit output (stdout/log/report), explicit PASS/FAIL result |
| Run Naming | MUST follow standard run naming conventions |

#### 7.1.2 Audit Proof Requirements

- Ratification MUST reference the run IDs of all required audits.
- Any FAIL result or missing run ID results in automatic rejection.
- Partial audit compliance is invalid.

#### 7.1.3 Audit Assertion Prohibition

Assertions of audit success without corresponding run artifacts are invalid and SHALL be rejected.

### 7.2 Failure Conditions

- Any audit failure blocks ratification.
- Partial compliance is invalid.

---

## 8. Failure Handling

### 8.1 Incomplete Evidence

- Proposal is rejected.
- Canon remains unchanged.

### 8.2 Audit Failure

- Proposal is rejected.
- Failure recorded.
- No partial merge permitted.

### 8.3 Rollback Policy

- Canon does not roll forward on failure.
- All failed attempts MUST be logged.

---

## 9. Protocol Constraints

### 9.1 Length Constraint

Protocol MUST remain ≤ 2 pages.

### 9.2 Language Constraint

- Declarative only.
- No speculative language.

---

## 10. Self-Amendment Rules

### 10.1 Protocol Immutability

This protocol is frozen at v0.1.

### 10.2 Conditions for Amendment

- MAY only be amended at Phase 4 or later.
- Requires explicit governance vote and audit.
- Amendment MUST follow this protocol's own rules.

---

## 11. Ratification

**Status:**
- ☐ Draft
- ☐ Evidence-Complete
- ☐ Audited
- ☐ Ratified

**Ratified By:**

| Name / Role | Timestamp |
|-------------|-----------|
| _(pending)_ | _(pending)_ |

---

*End of Protocol.*
