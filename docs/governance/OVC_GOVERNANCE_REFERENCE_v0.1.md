# OVC Governance Reference v0.1

## 1. Purpose
This document introduces no new rules. It formalizes existing authority as observed in `reports/validation/canon_inspection_pass_b__explicit_links.md`.

## 2. Authority Spine
Doctrine (constraints on meaning and time).
- `docs/doctrine/OVC_DOCTRINE.md` - governs design, development, and use of OVC.
- `docs/doctrine/IMMUTABILITY_NOTICE.md` - governs all canonical OVC layers.
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md` - governs data ownership, purpose, and downstream flows.
- `PATH1_EXECUTION_MODEL.md` - governs Path 1 execution ergonomics.
- `docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md` - governs the OVC operating loop.

Governance (constraints on change).
- `docs/governance/GOVERNANCE_RULES_v0.1.md` - governs all OVC repository artifacts (code, schemas, docs, configs).
- `docs/governance/BRANCH_POLICY.md` - governs branch policy (naming, deletion, and usage rules).

Contracts (constraints on computation).
- `docs/contracts/A_TO_D_CONTRACT_v1.md` - governs flow from Option A (Ingest) through Option D (Evidence).
- `docs/contracts/qa_validation_contract_v1.md` - governs QA validation across pipeline layers.
- `docs/contracts/option_a_ingest_contract_v1.md` - governs Option A ingest into canonical fact tables.
- `docs/contracts/option_b_derived_contract_v1.md` - governs Option B derived feature computation.
- `docs/contracts/option_c_outcomes_contract_v1.md` - governs Option C outcomes computation.
- `docs/contracts/option_d_evidence_contract_v1.md` - governs Option D evidence packs.
- `docs/contracts/option_d_ops_boundary.md` - governs Option D ops boundary (automation + operations).

Ledger (constraints on historical truth).
- `docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md` - governs deterministic run artifact directory and files.
- `contracts/run_artifact_spec_v0.1.json` - governs the run artifact schema (run.json/checks.json/run.log).

## 3. Authoritative Artifacts
Doctrine / Canon
- `docs/doctrine/IMMUTABILITY_NOTICE.md`
- `docs/architecture/OVC_DATA_FLOW_CANON_v0.1.md`
- `PATH1_EXECUTION_MODEL.md`
- `docs/workflows/WORKFLOW_OPERATING_LOOP_v0_1.md`

Governance / Rules
- `docs/governance/GOVERNANCE_RULES_v0.1.md`
- `docs/governance/BRANCH_POLICY.md`

Contracts / Specifications
- `docs/contracts/A_TO_D_CONTRACT_v1.md`
- `docs/contracts/qa_validation_contract_v1.md`
- `docs/contracts/option_a_ingest_contract_v1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/contracts/option_c_outcomes_contract_v1.md`
- `docs/contracts/option_d_evidence_contract_v1.md`
- `docs/contracts/option_d_ops_boundary.md`

Ledger
- `docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md`
- `contracts/run_artifact_spec_v0.1.json`

Other Authoritative References (Observed)
- `docs/pipeline/CURRENT_STATE_INVARIANTS.md`
- `CLAIMS/CLAIM_BINDING_v0_1.md`
- `reports/verification/EVIDENCE_ANCHOR_v0_1.md`
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/90_LEGENDS/LEGEND_MASTER.md`

## 4. Run Legitimacy & Ledger Declaration
The canonical run ledger is defined by `docs/runbooks/RUN_ARTIFACT_SPEC_v0.1.md` and `contracts/run_artifact_spec_v0.1.json`. The canonical ledger files are `run.json`, `checks.json`, and `run.log`. A run is considered valid only if it produces a run-artifact directory compliant with these specifications and passes the enforcement mechanisms listed in Section 5.

## 5. Enforcement Surfaces
- `docs/doctrine/ovc_logging_doctrine_v0.1.md`: Invalidates run. Where: Not stated. Severity: invalid.
- `docs/doctrine/IMMUTABILITY_NOTICE.md`: CI checks validate schema consistency. Where: Not stated. Severity: unspecified.
- `docs/governance/GOVERNANCE_RULES_v0.1.md`: Mandatory human review (critical paths). Where: `sql/01_tables_min.sql`, `contracts/export_contract_v0.1.1_min.json`, `docs/ops/OVC_DATA_FLOW_CANON_v0.1.md`, `docs/ops/GOVERNANCE_RULES_v0.1.md`, `infra/ovc-webhook/src/index.ts`. Severity: invalid.
- `docs/contracts/qa_validation_contract_v1.md`: CI gates (HARD FAIL). Where: `ci_workflow_sanity.yml`, `ci_pytest.yml`, `ci_schema_check.yml`. Severity: invalid.
- `docs/contracts/qa_validation_contract_v1.md`: Validation scripts. Where: `src/validate_day.py`, `src/validate_range.py`, `src/validate/validate_derived_range_v0_1.py`, `sql/qa_validation_pack_core.sql`, `sql/03_qa_derived_validation_v0_1.sql`. Severity: unspecified.
- `docs/contracts/option_b_derived_contract_v1.md`: Validation script. Where: `src/validate/validate_derived_range_v0_1.py`. Severity: unspecified.
- `docs/contracts/option_b_derived_contract_v1.md`: SQL gate. Where: `sql/90_verify_gate2.sql`. Severity: unspecified.
- `docs/contracts/option_c_outcomes_contract_v1.md`: Workflow requirement. Where: `ovc_option_c_schedule.yml`. Severity: unspecified.
- `docs/contracts/option_d_ops_boundary.md`: Exit code policy. Where: Not stated. Severity: warn/invalid.
- `Tetsu/OVC_REPO_MAZE/15_REPO_GRAPHS/30_CONTRACTS_ENFORCEMENT/GRAPH_31__ENFORCEMENT_POINTS.md`: Test/CI/Tool enforcement points. Where: `tests/test_contract_equivalence.py`, `tests/test_derived_features.py`, `tests/test_min_contract_validation.py`, `tests/test_path1_replay_structural.py`, `.github/workflows/ci_pytest.yml`, `.github/workflows/ci_schema_check.yml`, `tools/validate_contract.py`, `sql/90_verify_gate2.sql`. Severity: unspecified.

## 6. Non-Authoritative Artifacts
Per `reports/validation/canon_inspection_pass_b__explicit_links.md`, these artifacts are not referenced by canon or governance documents and are classified here as non-authoritative.
- `.codex/`: Purpose: Not Observable. Not allowed to decide canonical truth, contract validity, or run legitimacy.
- `artifacts/derived_validation/`: Purpose: Not Observable. Not allowed to decide canonical truth, contract validity, or run legitimacy.
- `reports/path1/evidence/runs/`: Purpose: Not Observable. Not allowed to decide canonical truth, contract validity, or run legitimacy.
- `reports/verification/`: Purpose: Not Observable. Not allowed to decide canonical truth, contract validity, or run legitimacy.

## 7. Change Control & Versioning
Change control and versioning requirements are defined by the following observed statements.
- `docs/governance/GOVERNANCE_RULES_v0.1.md`: "frozen contracts that must not change without explicit review".
- `docs/governance/GOVERNANCE_RULES_v0.1.md`: "Modification PROHIBITED without explicit audit and version bump".
- `docs/governance/GOVERNANCE_RULES_v0.1.md`: "Deletion PROHIBITED — mark DEPRECATED first, then ORPHANED".
- `docs/doctrine/IMMUTABILITY_NOTICE.md`: "Governance approval is required for any canonical change."
- `docs/contracts/option_d_ops_boundary.md`: "Option C computation semantics are sealed and must not change without a version bump."
- `docs/doctrine/OVC_DOCTRINE.md`: "Do not silently edit the past."
Invalidation of prior runs is Not Observable. Run-level invalidation is explicitly stated only for mixing sources inside a single `run_id` in `docs/doctrine/ovc_logging_doctrine_v0.1.md`.

## 8. Scope Limits & Non-Goals
This document does not define execution workflows. It does not replace contracts. It does not govern experimental or research work (as referenced in `docs/doctrine/IMMUTABILITY_NOTICE.md` via `research.*` and `experimental.*`). It does not imply completeness of enforcement; only observed enforcement surfaces are listed.
