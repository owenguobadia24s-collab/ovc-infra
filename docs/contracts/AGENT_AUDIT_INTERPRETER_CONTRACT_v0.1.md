# AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1

**Version:** 0.1
**Status:** Draft
**Authority:** None — Formatter and Classifier Only
**Applies From:** Phase 4
**Prime Invariant:** Interpretation is derived; truth resides in source artifacts.

---

## 1. Purpose

The Audit Interpreter is a read-only agent that consumes Phase 3 run artifacts and emits a structured interpretation report in canonical JSON format. The agent performs classification, aggregation, and formatting of evidence from sealed run folders. It does not perform validation, mutation, or any operation that modifies repository state.

**This agent is not a source of truth.** All claims in the interpretation report are derived from and must reference the source artifacts. The source artifacts remain authoritative; the interpretation report is a convenience layer for human and downstream consumption.

---

## 2. Non-Authority Declaration

The Audit Interpreter agent CANNOT and MUST NOT:

- Write to any file in the repository
- Create, modify, or delete run artifacts
- Execute any subprocess, shell command, or external process
- Perform git operations (commit, push, checkout, merge, etc.)
- Invoke sealing functions or compute manifest hashes
- Insert, update, or delete database records
- Propose or ratify contract evolution
- Assert facts not present in source artifacts
- Interpret ambiguous evidence as definitive
- Generate synthetic evidence or placeholder data
- Override, contradict, or reinterpret Phase 3 semantics
- Create new authority or governance structures

---

## 3. Inputs (Allowed Evidence Only)

### 3.1 Allowed Filesystem Roots

The agent MAY read from:

| Root | Description |
|------|-------------|
| `.codex/RUNS/<run_id>/` | Sealed run folders |
| `docs/contracts/` | Contract definitions (read-only) |
| `docs/governance/` | Governance rules (read-only) |
| `tools/phase3_control_panel/audits/` | Audit definitions (read-only) |

### 3.2 Admissibility Rule

Only artifacts explicitly referenced within a run folder are admissible as evidence for that run's interpretation. Artifacts from other runs, hypothetical structures, or external sources are inadmissible.

### 3.3 Required Run Artifacts

For a run to be interpretable, it MUST contain:

| Artifact | Required |
|----------|----------|
| `run.json` | YES |
| `manifest.json` | YES (for sealed runs) |
| `MANIFEST.sha256` | YES (for sealed runs) |

---

## 4. Outputs (Canonical Only)

### 4.1 Output Format

The canonical output format is JSON, conforming to `AUDIT_INTERPRETATION_REPORT_v0.1.json` schema.

### 4.2 Output Path

The canonical output path is:

```
.codex/RUNS/<run_id>/audit_interpretation_v0.1.json
```

### 4.3 Output Authority

The output file is NON-AUTHORITATIVE. It is a derived artifact and does not constitute source truth.

---

## 5. Report Structure

The interpretation report MUST contain these top-level JSON fields:

1. `schema_version`
2. `report_id`
3. `generated_utc`
4. `interpreter_version`
5. `run_id`
6. `run_type`
7. `run_created_utc`
8. `seal_status`
9. `interpretation_summary`
10. `failures`
11. `non_claims`
12. `next_actions`
13. `evidence_index`
14. `metadata`

---

## 6. Failure Classification

The `failure_class` field MUST be one of these CLOSED ENUM values:

| Value | Description |
|-------|-------------|
| `SEAL_INVALID` | Manifest hash mismatch or missing seal artifacts |
| `RUN_ENVELOPE_MALFORMED` | run.json missing required fields or invalid structure |
| `AUDIT_FAILED` | Audit exit code non-zero |
| `ARTIFACT_MISSING` | Expected artifact not present |
| `ARTIFACT_MALFORMED` | Artifact present but unparseable |
| `SCHEMA_VIOLATION` | Artifact violates declared schema |
| `EVIDENCE_INCOMPLETE` | Partial evidence insufficient for classification |
| `UNKNOWN` | Failure detected but not classifiable |

---

## 7. Severity Classification

The `severity` field MUST be one of these CLOSED ENUM values:

| Value | Description |
|-------|-------------|
| `CRITICAL` | Blocks downstream processing; integrity compromised |
| `ERROR` | Significant failure; run partially unusable |
| `WARNING` | Non-blocking issue; degraded but usable |
| `INFO` | Observation; no action required |

---

## 8. Confidence Levels

The `confidence` field MUST be one of these CLOSED ENUM values:

| Value | Description |
|-------|-------------|
| `HIGH` | Evidence is complete and unambiguous |
| `MEDIUM` | Evidence supports conclusion but minor gaps exist |
| `LOW` | Evidence is partial; classification is tentative |
| `NONE` | Insufficient evidence; claim withheld |

---

## 9. Evidence Anchoring Rules

### 9.1 Mandatory Reference

Every claim in the interpretation report MUST reference:

- `artifact_path`: Relative path to source artifact within the run folder
- `source_check_id` OR `rule_id`: Identifier linking to specific check or rule

### 9.2 Unsupported Assertions

Assertions without evidence references are FORBIDDEN. The interpreter MUST NOT:

- State facts without artifact path citation
- Infer conclusions not directly supported by artifact content
- Extrapolate from partial evidence to complete conclusions

---

## 10. Fail-Closed Rules

### 10.1 Missing Evidence

If evidence required for a claim is missing, the claim MUST NOT be made. Instead, the condition MUST be recorded in `non_claims` with reason `EVIDENCE_MISSING`.

### 10.2 Ambiguous Evidence

If evidence is present but ambiguous or contradictory, the classification MUST be `UNKNOWN` and confidence MUST be `NONE`.

### 10.3 Parse Failures

If an artifact cannot be parsed, the failure MUST be recorded with `failure_class: ARTIFACT_MALFORMED` and no further interpretation of that artifact is permitted.

---

## 11. Phase 3 Compatibility

This contract does not modify, extend, or reinterpret Phase 3 semantics. The following Phase 3 artifacts and their meanings remain unchanged:

- Run envelope structure per `RUN_ENVELOPE_STANDARD_v0_1.md`
- Audit exit codes (0=PASS, 1=FAIL, 2=ERROR)
- Manifest sealing format
- C-layer boundary definitions per `c_layer_boundary_spec_v0.1.md`
- Outcomes definitions per `outcomes_definitions_v0.1.md`

The Audit Interpreter is a consumer of Phase 3 outputs, not a modifier.

---

## 12. Versioning & Evolution

Evolution of this contract is governed ONLY by `CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` (cited: §1 Scope, §2 Version Semantics, §6 Authority Model).

| Requirement | Reference |
|-------------|-----------|
| Version format | `CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` §2.1 |
| Change classification | `CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` §3 |
| Evidence requirements | `CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` §4 |
| Ratification authority | `CONTRACT_EVOLUTION_PROTOCOL_v0.1.md` §6.2 |

No evolution of this contract may occur outside the defined protocol.

---

*End of Contract.*
