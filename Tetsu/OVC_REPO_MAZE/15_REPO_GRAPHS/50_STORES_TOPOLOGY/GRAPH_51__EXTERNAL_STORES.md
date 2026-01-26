# Graph 51 — External Stores

**Question:** What external stores exist and what writes/reads them?


```mermaid
graph LR

  %% Options
  subgraph OPTS["Options"]
    OPT_A["OPT_A Option A"]
    OPT_B["OPT_B Option B"]
    OPT_C["OPT_C Option C"]
    OPT_D["OPT_D Option D"]
    OPT_QA["OPT_QA QA"]
  end

  %% External stores
  subgraph EXT["External or Shared Stores"]
    EXT_R2["EXT_R2 R2 raw archive"]
    EXT_NOTION["EXT_NOTION Notion databases"]
    EXT_VERIF["EXT_VERIF verification_private"]
  end

  %% Artifacts
  subgraph ART["Artifacts filesystem"]
    EXT_ART_C["EXT_ART_C option_c"]
    EXT_ART_DERIVED["EXT_ART_DERIVED derived_validation"]
    EXT_ART_REPLAY["EXT_ART_REPLAY path1_replay_report"]
  end

  %% Reports
  subgraph RPTS["Reports filesystem"]
    EXT_RPT_OPTC["EXT_RPT_OPTC run_report and spotchecks"]
    EXT_RPT_RUNS["EXT_RPT_RUNS runs"]
    EXT_RPT_PATH1["EXT_RPT_PATH1 path1 evidence scores trajectories"]
    EXT_RPT_VALID["EXT_RPT_VALID validation"]
    EXT_RPT_VERIF["EXT_RPT_VERIF verification"]
    EXT_RPT_AUDIT["EXT_RPT_AUDIT pipeline_audit"]
  end

  %% Writes / reads
  OPT_A -->|write| EXT_R2
  OPT_D -->|sync| EXT_NOTION
  OPT_QA -.->|manual inputs| EXT_VERIF

  OPT_C -->|write| EXT_ART_C
  OPT_B -->|write| EXT_ART_DERIVED
  OPT_D -->|write| EXT_ART_REPLAY

  OPT_C -->|write| EXT_RPT_OPTC
  OPT_D -->|write| EXT_RPT_RUNS
  OPT_D -->|write| EXT_RPT_PATH1
  OPT_QA -->|write| EXT_RPT_VALID
  OPT_QA -->|write| EXT_RPT_VERIF
  OPT_QA -->|write| EXT_RPT_AUDIT
```

## Legend

| Node ID         | Full name / notes |
|-----------------|-------------------|
| OPT_A           | Option A (canonical ingest) |
| OPT_B           | Option B (derived features) |
| OPT_C           | Option C (outcomes) |
| OPT_D           | Option D (Path1/bridge) |
| OPT_QA          | QA (validation/governance) |
| EXT_R2          | R2 raw archive (Option A writes reports in tv/YYYY-MM-DD/ partition) |
| EXT_NOTION      | Notion databases (sync target) |
| EXT_VERIF       | data/verification_private/ (local/private verification store) |
| EXT_ART_C       | artifacts/option_c/ |
| EXT_ART_DERIVED | artifacts/derived_validation/ |
| EXT_ART_REPLAY  | artifacts/path1_replay_report.json |
| EXT_RPT_OPTC    | reports/run_report_*.json; reports/spotchecks_*.txt |
| EXT_RPT_RUNS    | reports/runs/run_id/ |
| EXT_RPT_PATH1   | reports/path1/evidence/; reports/path1/scores/; reports/path1/trajectory_families/ |
| EXT_RPT_VALID   | reports/validation/ |
| EXT_RPT_VERIF   | reports/verification/ |
| EXT_RPT_AUDIT   | reports/pipeline_audit/ |

