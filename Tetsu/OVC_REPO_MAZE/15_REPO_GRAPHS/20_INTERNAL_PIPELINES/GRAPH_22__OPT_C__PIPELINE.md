# Graph 22 — Option C Pipeline

**Question:** What are Option C's outcomes pipelines and outputs?

```mermaid
%%─────────────────────────────────────────────────────────────────────────────
%% GRAPH 22 — OPTION C INTERNAL PIPELINE
%% Source: OPT_C__ORG_MAP_DRAFT.md
%%─────────────────────────────────────────────────────────────────────────────
flowchart TB

  %% Workflows
  subgraph WF[Workflows]
    WF_OPTC[WF_OPTC: ovc_option_c_schedule.yml<br/>cron: 15 6 * * *]
  end

  %% Input
  subgraph INPUT[Input: Option B]
    I_VIEWS[I_VIEWS: derived.v_ovc_c*_features]
  end

  %% Scripts
  subgraph SCRIPTS[scripts/run/]
    S_SH[S_SH: run_option_c.sh]
    S_PS1[S_PS1: run_option_c.ps1]
    S_WRAPPER[S_WRAPPER: run_option_c_wrapper.py]
    S_ART[S_ART: run_option_c_with_artifact.sh]
    S_MIG[S_MIG: run_migration.py]
  end

  %% SQL
  subgraph SQL[sql/]
    SQL_OPTC[SQL_OPTC: option_c_v0_1.sql]
    SQL_RPT[SQL_RPT: option_c_run_report.sql]
    SQL_OUT[SQL_OUT: derived/v_ovc_c_outcomes_v0_1.sql]
  end

  %% Artifacts
  subgraph ART[artifacts/option_c/]
    A_SANITY[A_SANITY: sanity_local/]
    A_REPORT[A_REPORT: run_report_sanity_local.json]
    A_SPOT[A_SPOT: spotchecks_sanity_local.txt]
  end

  %% Outputs
  subgraph OUT[Canonical Outputs]
    O_OUTCOMES[O_OUTCOMES: derived.v_ovc_c_outcomes_v0_1]
  end

  %% Reports (in reports/)
  subgraph RPT[reports/]
    R_REPORT[R_REPORT: run_report_*.json]
    R_SPOT[R_SPOT: spotchecks_*.txt]
  end

  %% Workflow → Scripts
  WF_OPTC --> S_SH

  %% Input → SQL
  I_VIEWS --> SQL_OPTC

  %% Scripts → SQL/Artifacts
  S_SH --> SQL_OPTC
  S_SH --> SQL_RPT
  S_WRAPPER --> S_SH
  S_ART --> A_SANITY

  %% SQL → Output
  SQL_OPTC --> SQL_OUT
  SQL_OUT --> O_OUTCOMES

  %% Scripts → Reports
  S_SH --> R_REPORT
  S_SH --> R_SPOT

  %% Artifacts
  S_ART --> A_REPORT
  S_ART --> A_SPOT

  %% Styling
  classDef workflow fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
  classDef canonical fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
  classDef code fill:#e3f2fd,stroke:#1565c0,stroke-width:1px
  classDef artifact fill:#c8e6c9,stroke:#2e7d32,stroke-width:1px

  class WF_OPTC workflow
  class O_OUTCOMES canonical
  class I_VIEWS canonical
  class S_SH,S_PS1,S_WRAPPER,S_ART,S_MIG,SQL_OPTC,SQL_RPT,SQL_OUT code
  class A_SANITY,A_REPORT,A_SPOT,R_REPORT,R_SPOT artifact
```

## Legend

| Node ID | Full Path | Category |
|---------|-----------|----------|
| WF_OPTC | .github/workflows/ovc_option_c_schedule.yml | Orchestration |
| I_VIEWS | derived.v_ovc_c*_features | Input (Option B) |
| S_SH | scripts/run/run_option_c.sh | Orchestration |
| S_PS1 | scripts/run/run_option_c.ps1 | Orchestration |
| S_WRAPPER | scripts/run/run_option_c_wrapper.py | Orchestration |
| S_ART | scripts/run/run_option_c_with_artifact.sh | Orchestration |
| S_MIG | scripts/run/run_migration.py | Orchestration |
| SQL_OPTC | sql/option_c_v0_1.sql | Data Stores |
| SQL_RPT | sql/option_c_run_report.sql | Data Stores |
| SQL_OUT | sql/derived/v_ovc_c_outcomes_v0_1.sql | Data Stores |
| A_SANITY | artifacts/option_c/sanity_local/ | Artifacts |
| A_REPORT | artifacts/option_c/run_report_sanity_local.json | Artifacts |
| A_SPOT | artifacts/option_c/spotchecks_sanity_local.txt | Artifacts |
| O_OUTCOMES | derived.v_ovc_c_outcomes_v0_1 | Data Stores (CANONICAL) |
| R_REPORT | reports/run_report_*.json | Artifacts |
| R_SPOT | reports/spotchecks_*.txt | Artifacts |
