# Graph 21 — Option B Pipeline

**Question:** What are Option B's derived compute pipelines and outputs?

```mermaid
%%─────────────────────────────────────────────────────────────────────────────
%% GRAPH 21 — OPTION B INTERNAL PIPELINE
%% Source: OPT_B__ORG_MAP_DRAFT.md
%%─────────────────────────────────────────────────────────────────────────────
flowchart TB

  %% Workflows
  subgraph WF[Workflows]
    WF_VALIDATE[WF_VALIDATE: backfill_then_validate.yml<br/>DORMANT]
  end

  %% Input
  subgraph INPUT[Input: Option A]
    I_BLOCKS[I_BLOCKS: ovc.ovc_blocks_v01_1_min]
  end

  %% Compute Scripts
  subgraph COMPUTE[src/derived/ compute]
    S_C1[S_C1: compute_l1_v0_1.py]
    S_C2[S_C2: compute_l2_v0_1.py]
    S_C3[S_C3: compute_l3_regime_trend_v0_1.py<br/>NOT INVOKED]
    S_STUB[S_STUB: compute_l3_stub_v0_1.py]
  end

  %% SQL Views
  subgraph VIEWS[sql/derived/ views]
    V_C1[V_C1: v_ovc_l1_features_v0_1.sql]
    V_C2[V_C2: v_ovc_l2_features_v0_1.sql]
    V_C3[V_C3: v_ovc_l3_features_v0_1.sql]
    V_SP[V_SP: v_ovc_state_plane_v0_2.sql]
  end

  %% Trajectory Families
  subgraph TF[trajectory_families/]
    TF_FP[TF_FP: fingerprint.py]
    TF_CLUSTER[TF_CLUSTER: clustering.py]
    TF_PARAMS[TF_PARAMS: params_v0_1.json]
  end

  %% Threshold Registry
  subgraph REG[Threshold Registry]
    R_PACKS[R_PACKS: configs/threshold_packs/*.json]
    R_CODE[R_CODE: src/config/threshold_registry_v0_1.py]
    R_DB[R_DB: ovc_cfg.threshold_packs]
  end

  %% SQL Tables
  subgraph SQL[sql/ tables]
    SQL_C1C2[SQL_C1C2: 02_derived_c1_c2_tables_v0_1.sql]
    SQL_C3[SQL_C3: 05_c3_regime_trend_v0_1.sql]
    SQL_REG[SQL_REG: 04_threshold_registry_v0_1.sql]
    SQL_SP[SQL_SP: 06_state_plane_threshold_pack_v0_2.sql]
  end

  %% Outputs
  subgraph OUT[Derived Outputs]
    O_C1[O_C1: derived.ovc_l1_features]
    O_C2[O_C2: derived.ovc_l2_features]
    O_C3[O_C3: derived.ovc_l3_features]
  end

  %% Workflow → Compute
  WF_VALIDATE -.->|DORMANT| S_C1
  WF_VALIDATE -.->|DORMANT| S_C2

  %% Input → Compute
  I_BLOCKS --> S_C1
  I_BLOCKS --> S_C2
  I_BLOCKS -.-> S_C3

  %% Compute → Views
  S_C1 --> V_C1
  S_C2 --> V_C2
  S_C3 -.->|NOT INVOKED| V_C3

  %% Views → Outputs
  V_C1 --> O_C1
  V_C2 --> O_C2
  V_C3 -.-> O_C3

  %% Registry flow
  R_PACKS --> R_CODE
  R_CODE --> R_DB
  R_DB --> S_C3
  SQL_REG --> R_DB

  %% SQL definitions
  SQL_C1C2 --> V_C1
  SQL_C1C2 --> V_C2
  SQL_C3 --> V_C3
  SQL_SP --> V_SP

  %% TF flow
  TF_FP --> TF_CLUSTER
  TF_PARAMS --> TF_FP

  %% Styling
  classDef dormant fill:#ffcdd2,stroke:#c62828,stroke-width:1px,stroke-dasharray:5
  classDef canonical fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
  classDef notInvoked fill:#ffcdd2,stroke:#c62828,stroke-width:1px,stroke-dasharray:5
  classDef code fill:#e3f2fd,stroke:#1565c0,stroke-width:1px
  classDef registry fill:#fff9c4,stroke:#f9a825,stroke-width:2px

  class WF_VALIDATE dormant
  class S_C3 notInvoked
  class O_C1,O_C2,O_C3 canonical
  class I_BLOCKS canonical
  class S_C1,S_C2,S_STUB,V_C1,V_C2,V_C3,V_SP,TF_FP,TF_CLUSTER,TF_PARAMS,SQL_C1C2,SQL_C3,SQL_SP code
  class R_PACKS,R_CODE,R_DB,SQL_REG registry
```

## Legend

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_VALIDATE | .github/workflows/backfill_then_validate.yml | Orchestration (DORMANT) |
| I_BLOCKS | ovc.ovc_blocks_v01_1_min | Input (Option A) |
| S_C1 | src/derived/compute_l1_v0_1.py | Pipelines |
| S_C2 | src/derived/compute_l2_v0_1.py | Pipelines |
| S_C3 | src/derived/compute_l3_regime_trend_v0_1.py | Pipelines (NOT INVOKED) |
| S_STUB | src/derived/compute_l3_stub_v0_1.py | Pipelines |
| V_C1 | sql/derived/v_ovc_l1_features_v0_1.sql | Data Stores |
| V_C2 | sql/derived/v_ovc_l2_features_v0_1.sql | Data Stores |
| V_C3 | sql/derived/v_ovc_l3_features_v0_1.sql | Data Stores |
| V_SP | sql/derived/v_ovc_state_plane_v0_2.sql | Data Stores |
| TF_FP | trajectory_families/fingerprint.py | Models |
| TF_CLUSTER | trajectory_families/clustering.py | Models |
| TF_PARAMS | trajectory_families/params_v0_1.json | Models |
| R_PACKS | configs/threshold_packs/*.json | Registries |
| R_CODE | src/config/threshold_registry_v0_1.py | Registries |
| R_DB | ovc_cfg.threshold_packs | Registries |
| SQL_C1C2 | sql/02_derived_c1_c2_tables_v0_1.sql | Data Stores |
| SQL_C3 | sql/05_c3_regime_trend_v0_1.sql | Data Stores |
| SQL_REG | sql/04_threshold_registry_v0_1.sql | Registries |
| SQL_SP | sql/06_state_plane_threshold_pack_v0_2.sql | Data Stores |
| O_C1 | derived.ovc_l1_features | Data Stores (CANONICAL) |
| O_C2 | derived.ovc_l2_features | Data Stores (CANONICAL) |
| O_C3 | derived.ovc_l3_features | Data Stores (CANONICAL) |
