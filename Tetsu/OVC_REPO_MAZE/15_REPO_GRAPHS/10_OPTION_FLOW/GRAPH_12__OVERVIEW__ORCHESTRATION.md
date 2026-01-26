# Graph 12 — Overview: Orchestration

**Question:** Which workflows/scripts trigger which option processes?

```mermaid
%%─────────────────────────────────────────────────────────────────────────────
%% GRAPH 12 — ORCHESTRATION OVERVIEW
%% Source: CATEGORY_PROCESS_APPENDIX_DRAFT.md, QA__ORG_MAP_DRAFT.md
%%─────────────────────────────────────────────────────────────────────────────
flowchart LR

  %% Trigger Types
  subgraph TRIGGERS[Trigger Types]
    CRON[CRON: Scheduled]
    MANUAL[MANUAL: workflow_dispatch]
    PUSH[PUSH: on push/PR]
  end

  %% Option A Workflows
  subgraph WF_A[Workflows: Option A]
    WF_BACKFILL[WF_BACKFILL: backfill.yml]
    WF_M15[WF_M15: backfill_m15.yml]
    WF_INGEST[WF_INGEST: ovc_full_ingest.yml]
  end

  %% Option B Workflows
  subgraph WF_B[Workflows: Option B]
    WF_VALIDATE[WF_VALIDATE: backfill_then_validate.yml]
  end

  %% Option C Workflows
  subgraph WF_C[Workflows: Option C]
    WF_OPTC[WF_OPTC: ovc_option_c_schedule.yml]
  end

  %% Option D Workflows
  subgraph WF_D[Workflows: Option D]
    WF_P1[WF_P1: path1_evidence.yml]
    WF_P1Q[WF_P1Q: path1_evidence_queue.yml]
    WF_REPLAY[WF_REPLAY: path1_replay_verify.yml]
    WF_NOTION[WF_NOTION: notion_sync.yml]
  end

  %% QA CI Workflows
  subgraph WF_QA[Workflows: QA CI]
    WF_PYTEST[WF_PYTEST: ci_pytest.yml]
    WF_SCHEMA[WF_SCHEMA: ci_schema_check.yml]
    WF_SANITY[WF_SANITY: ci_workflow_sanity.yml]
  end

  %% Scripts
  subgraph SCRIPTS_A[Scripts: Option A]
    S_BACKFILL_2H[S_BACKFILL_2H: backfill_oanda_2h_checkpointed]
    S_BACKFILL_M15[S_BACKFILL_M15: backfill_oanda_m15_checkpointed]
  end

  subgraph SCRIPTS_B[Scripts: Option B]
    S_C1[S_C1: compute_l1_v0_1.py]
    S_C2[S_C2: compute_l2_v0_1.py]
    S_C3[S_C3: compute_l3_regime_trend]
  end

  subgraph SCRIPTS_C[Scripts: Option C]
    S_OPTC[S_OPTC: run_option_c.sh]
  end

  subgraph SCRIPTS_D[Scripts: Option D]
    S_PACK[S_PACK: build_evidence_pack_v0_2.py]
    S_QUEUE[S_QUEUE: run_evidence_queue.py]
    S_REPLAY[S_REPLAY: run_replay_verification.py]
    S_NOTION[S_NOTION: notion_sync.py]
  end

  %% Trigger → Workflow connections
  CRON -->|17 */6 * * *| WF_BACKFILL
  CRON -->|scheduled| WF_M15
  CRON -->|15 6 * * *| WF_OPTC
  CRON -->|17 */2 * * *| WF_NOTION

  MANUAL --> WF_INGEST
  MANUAL --> WF_VALIDATE
  MANUAL --> WF_P1
  MANUAL --> WF_P1Q
  MANUAL --> WF_REPLAY

  PUSH --> WF_PYTEST
  PUSH --> WF_SCHEMA
  PUSH --> WF_SANITY

  %% Workflow → Script connections
  WF_BACKFILL --> S_BACKFILL_2H
  WF_M15 --> S_BACKFILL_M15
  WF_VALIDATE --> S_C1
  WF_VALIDATE --> S_C2
  WF_OPTC --> S_OPTC
  WF_P1 --> S_PACK
  WF_P1Q --> S_QUEUE
  WF_REPLAY --> S_REPLAY
  WF_NOTION --> S_NOTION

  %% NOT INVOKED markers
  S_C3 -.->|NOT INVOKED by any workflow| WF_VALIDATE
  WF_INGEST -.->|DORMANT - no schedule| S_BACKFILL_2H
  WF_VALIDATE -.->|DORMANT - no schedule| S_C1

  %% Styling
  classDef scheduled fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
  classDef manual fill:#fff3e0,stroke:#ef6c00,stroke-width:1px
  classDef ci fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
  classDef dormant fill:#ffcdd2,stroke:#c62828,stroke-width:1px,stroke-dasharray:5
  classDef script fill:#e3f2fd,stroke:#1565c0,stroke-width:1px

  class WF_BACKFILL,WF_M15,WF_OPTC,WF_NOTION scheduled
  class WF_P1,WF_P1Q,WF_REPLAY manual
  class WF_PYTEST,WF_SCHEMA,WF_SANITY ci
  class WF_INGEST,WF_VALIDATE,S_C3 dormant
  class S_BACKFILL_2H,S_BACKFILL_M15,S_C1,S_C2,S_OPTC,S_PACK,S_QUEUE,S_REPLAY,S_NOTION script
```

## Legend

| Node ID | Description | Status |
|---------|-------------|--------|
| WF_BACKFILL | .github/workflows/backfill.yml | SCHEDULED (cron: 17 */6 * * *) |
| WF_M15 | .github/workflows/backfill_m15.yml | SCHEDULED |
| WF_INGEST | .github/workflows/ovc_full_ingest.yml | DORMANT (workflow_dispatch only) |
| WF_VALIDATE | .github/workflows/backfill_then_validate.yml | DORMANT (workflow_dispatch only) |
| WF_OPTC | .github/workflows/ovc_option_c_schedule.yml | SCHEDULED (cron: 15 6 * * *) |
| WF_P1 | .github/workflows/path1_evidence.yml | MANUAL |
| WF_P1Q | .github/workflows/path1_evidence_queue.yml | MANUAL |
| WF_REPLAY | .github/workflows/path1_replay_verify.yml | MANUAL |
| WF_NOTION | .github/workflows/notion_sync.yml | SCHEDULED (cron: 17 */2 * * *) |
| WF_PYTEST | .github/workflows/ci_pytest.yml | CI (on push/PR) |
| WF_SCHEMA | .github/workflows/ci_schema_check.yml | CI (on push/PR) |
| WF_SANITY | .github/workflows/ci_workflow_sanity.yml | CI (on push/PR) |
| S_BACKFILL_2H | src/backfill_oanda_2h_checkpointed.py | Active |
| S_BACKFILL_M15 | src/backfill_oanda_m15_checkpointed.py | Active |
| S_C1 | src/derived/compute_l1_v0_1.py | Active |
| S_C2 | src/derived/compute_l2_v0_1.py | Active |
| S_C3 | src/derived/compute_l3_regime_trend_v0_1.py | NOT INVOKED |
| S_OPTC | scripts/run/run_option_c.sh | Active |
| S_PACK | scripts/path1/build_evidence_pack_v0_2.py | Active |
| S_QUEUE | scripts/path1/run_evidence_queue.py | Active |
| S_REPLAY | scripts/path1_replay/run_replay_verification.py | Active |
| S_NOTION | scripts/export/notion_sync.py | Active |
