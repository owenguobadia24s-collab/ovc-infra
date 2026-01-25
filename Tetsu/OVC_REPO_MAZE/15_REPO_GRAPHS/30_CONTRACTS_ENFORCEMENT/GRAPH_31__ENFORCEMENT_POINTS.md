# Graph 31 — Enforcement Points

**Question:** Where are contracts validated in the system?

```mermaid
%%─────────────────────────────────────────────────────────────────────────────
%% GRAPH 31 — CONTRACT ENFORCEMENT POINTS
%% Source: CATEGORY_PROCESS_APPENDIX_DRAFT.md, QA__ORG_MAP_DRAFT.md
%%─────────────────────────────────────────────────────────────────────────────
flowchart LR

  %% Contracts
  subgraph CONTRACTS[Contracts]
    C_EXPORT[C_EXPORT: export_contract_v0.1.1_min]
    C_DERIVED[C_DERIVED: derived_feature_set_v0.1]
    C_ARTIFACT[C_ARTIFACT: run_artifact_spec_v0.1]
  end

  %% Enforcement: Worker
  subgraph ENF_WORKER[Worker Parse]
    E_PARSE[E_PARSE: parseExport in index.ts]
  end

  %% Enforcement: Tests
  subgraph ENF_TESTS[Test Suite]
    E_T_CONTRACT[E_T_CONTRACT: test_contract_equivalence.py]
    E_T_DERIVED[E_T_DERIVED: test_derived_features.py]
    E_T_MIN[E_T_MIN: test_min_contract_validation.py]
    E_T_REPLAY[E_T_REPLAY: test_path1_replay_structural.py]
  end

  %% Enforcement: CI
  subgraph ENF_CI[CI Gates]
    E_CI_SCHEMA[E_CI_SCHEMA: ci_schema_check.yml]
    E_CI_PYTEST[E_CI_PYTEST: ci_pytest.yml]
  end

  %% Enforcement: SQL
  subgraph ENF_SQL[SQL Gates]
    E_SQL_GATE2[E_SQL_GATE2: 90_verify_gate2.sql<br/>NOT AUTOMATED]
    E_SQL_PACK[E_SQL_PACK: qa_validation_pack*.sql]
  end

  %% Enforcement: Tools
  subgraph ENF_TOOLS[Validation Tools]
    E_VALIDATE[E_VALIDATE: tools/validate_contract.py]
  end

  %% Schema
  subgraph SCHEMA[Schema Enforcement]
    S_OBJECTS[S_OBJECTS: schema/required_objects.txt]
  end

  %% Contract → Enforcement
  C_EXPORT -->|runtime| E_PARSE
  C_EXPORT -->|test| E_T_CONTRACT
  C_EXPORT -->|test| E_T_MIN
  C_EXPORT -->|tool| E_VALIDATE

  C_DERIVED -->|test| E_T_DERIVED
  C_DERIVED -->|sql| E_SQL_PACK

  C_ARTIFACT -->|test| E_T_REPLAY

  %% CI integrations
  E_T_CONTRACT --> E_CI_PYTEST
  E_T_DERIVED --> E_CI_PYTEST
  E_T_MIN --> E_CI_PYTEST
  E_T_REPLAY --> E_CI_PYTEST

  S_OBJECTS --> E_CI_SCHEMA

  %% SQL gate (not automated)
  E_SQL_GATE2 -.->|NOT AUTOMATED| E_CI_SCHEMA

  %% Styling
  classDef contract fill:#bbdefb,stroke:#1565c0,stroke-width:2px
  classDef enforcement fill:#ffcdd2,stroke:#c62828,stroke-width:2px
  classDef ci fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
  classDef notAutomated fill:#ffcdd2,stroke:#c62828,stroke-width:1px,stroke-dasharray:5
  classDef test fill:#e1bee7,stroke:#6a1b9a,stroke-width:1px

  class C_EXPORT,C_DERIVED,C_ARTIFACT contract
  class E_PARSE,E_VALIDATE enforcement
  class E_CI_SCHEMA,E_CI_PYTEST ci
  class E_SQL_GATE2 notAutomated
  class E_T_CONTRACT,E_T_DERIVED,E_T_MIN,E_T_REPLAY,E_SQL_PACK,S_OBJECTS test
```

## Enforcement Matrix

| Contract | Enforcement Point | Type | Status |
|----------|-------------------|------|--------|
| export_contract_v0.1.1_min.json | Worker parseExport | Runtime | Active |
| export_contract_v0.1.1_min.json | test_contract_equivalence.py | Test | Active |
| export_contract_v0.1.1_min.json | test_min_contract_validation.py | Test | Active |
| export_contract_v0.1.1_min.json | tools/validate_contract.py | Tool | Active |
| derived_feature_set_v0.1.json | test_derived_features.py | Test | Active |
| derived_feature_set_v0.1.json | qa_validation_pack*.sql | SQL | Active |
| run_artifact_spec_v0.1.json | test_path1_replay_structural.py | Test | Active |
| (all) | ci_pytest.yml | CI | Active |
| (schema) | ci_schema_check.yml | CI | Active |
| (schema) | 90_verify_gate2.sql | SQL | NOT AUTOMATED |

## Legend

| Node ID | Full Path |
|---------|-----------|
| C_EXPORT | contracts/export_contract_v0.1.1_min.json |
| C_DERIVED | contracts/derived_feature_set_v0.1.json |
| C_ARTIFACT | contracts/run_artifact_spec_v0.1.json |
| E_PARSE | infra/ovc-webhook/src/index.ts (parseExport function) |
| E_T_CONTRACT | tests/test_contract_equivalence.py |
| E_T_DERIVED | tests/test_derived_features.py |
| E_T_MIN | tests/test_min_contract_validation.py |
| E_T_REPLAY | tests/test_path1_replay_structural.py |
| E_CI_SCHEMA | .github/workflows/ci_schema_check.yml |
| E_CI_PYTEST | .github/workflows/ci_pytest.yml |
| E_SQL_GATE2 | sql/90_verify_gate2.sql |
| E_SQL_PACK | sql/qa_validation_pack*.sql |
| E_VALIDATE | tools/validate_contract.py |
| S_OBJECTS | schema/required_objects.txt |
