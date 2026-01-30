# OVC Contracts Index

Canonical contract documents governing the OVC pipeline.

## Master Contract

| Document | Scope |
|----------|-------|
| [A_TO_D_CONTRACT_v1.md](A_TO_D_CONTRACT_v1.md) | Master pipeline contract (A->D flow, versioning, dependency matrix) |

## Option A -- Ingest

| Document | Scope |
|----------|-------|
| [option_a1_bar_ingest_contract_v1.md](option_a1_bar_ingest_contract_v1.md) | **Option A1**: 2H bar ingest into `ovc.ovc_blocks_v01_1_min` |
| [option_a2_event_ingest_contract_v1.md](option_a2_event_ingest_contract_v1.md) | **Option A2**: M15 event-level ingest into `ovc.ovc_candles_m15_raw` |
| [option_a_ingest_contract_v1.md](option_a_ingest_contract_v1.md) | Original combined Option A ingest contract (superseded by A1 + A2) |
| [ingest_boundary.md](ingest_boundary.md) | Ingest boundary doctrine (webhook non-responsibilities) |
| [min_contract_alignment.md](min_contract_alignment.md) | MIN v0.1.1 end-to-end flow and test commands |

## Option B -- Derived

| Document | Scope |
|----------|-------|
| [option_b_derived_contract_v1.md](option_b_derived_contract_v1.md) | Derived features (C1/C2/C3 computation boundaries) |
| [derived_layer_boundary.md](derived_layer_boundary.md) | Derived layer immutability rules |
| [c3_semantic_contract_v0_1.md](c3_semantic_contract_v0_1.md) | C3 semantic definitions |
| [c_layer_boundary_spec_v0.1.md](c_layer_boundary_spec_v0.1.md) | C-layer boundary spec |

## Option C -- Outcomes

| Document | Scope |
|----------|-------|
| [option_c_outcomes_contract_v1.md](option_c_outcomes_contract_v1.md) | Outcomes layer contract |
| [option_c_boundary.md](option_c_boundary.md) | Option C boundary rules |
| [outcomes_definitions_v0.1.md](outcomes_definitions_v0.1.md) | Outcome metric definitions |

## Option D -- Evidence

| Document | Scope |
|----------|-------|
| [option_d_evidence_contract_v1.md](option_d_evidence_contract_v1.md) | Evidence pack generation contract |
| [option_d_ops_boundary.md](option_d_ops_boundary.md) | Option D ops boundary |
| [PATH2_CONTRACT_v1_0.md](PATH2_CONTRACT_v1_0.md) | Path2 evidence contract |

## QA

| Document | Scope |
|----------|-------|
| [qa_validation_contract_v1.md](qa_validation_contract_v1.md) | QA validation responsibilities |
