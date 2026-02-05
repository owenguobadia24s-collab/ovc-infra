# OVC Infrastructure — AI Agent Instructions

> **Quick Start:** Read [docs/operations/OPERATING_BASE.md](docs/operations/OPERATING_BASE.md) for full onboarding context.

## Project Overview

OVC (Option Validation Chain) is a TradingView-driven forex market observation pipeline:
- **Ingestion**: Cloudflare Worker receives TradingView alerts via `/tv` endpoint → Neon Postgres
- **Backfill**: OANDA API historical data via `src/backfill_oanda_2h_checkpointed.py`
- **Derived Layers**: C1 (single-bar), C2 (multi-bar), C3 (semantic) features
- **Outcomes**: Option C forward returns/MFE/MAE computations

## Critical Governance Rules

### ⛔ CANONICAL Artifacts (NEVER modify without version bump + audit)
| Path | Status |
|------|--------|
| `sql/01_tables_min.sql` | LOCKED |
| `contracts/export_contract_v0.1.1_min.json` | LOCKED |
| `infra/ovc-webhook/src/index.ts` | LOCKED |
| `ovc.ovc_blocks_v01_1_min` (Neon table) | LOCKED |

**Rules:** No in-place edits. Create new versioned files (e.g., `v0.1.2`). See [docs/governance/GOVERNANCE_RULES_v0.1.md](docs/governance/GOVERNANCE_RULES_v0.1.md).

### Branch Policy
- Never develop on `main` — use `pr/<area>-<topic>-vX.Y` or `wip/<area>-<topic>`
- Never mix Pine + infra in the same PR
- See [docs/governance/BRANCH_POLICY.md](docs/governance/BRANCH_POLICY.md)

## Developer Workflows

### Environment Setup
```powershell
pip install -r requirements.txt
# Required env vars: DATABASE_URL or NEON_DSN, OANDA_API_TOKEN, OANDA_ENV
```

### Run Tests
```powershell
python -m pytest tests/
```

### Common Tasks
```powershell
# Validate a day
python src/validate_day.py --symbol GBPUSD --date_ny 2024-06-15

# Backfill single day
$env:BACKFILL_DATE_NY="2024-01-10"
python src/backfill_oanda_2h_checkpointed.py

# Validate contract
python -m tools.validate_contract contracts/export_contract_v0.1.1_min.json tests/sample_exports/min_001.txt

# Worker local dev (from infra/ovc-webhook)
npm run dev
curl.exe -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"
```

## Key Patterns

### Idempotent Upserts
All INSERT statements use `ON CONFLICT (block_id) DO UPDATE SET ...` for safe reruns.

### RunWriter for Pipeline Telemetry
```python
from ovc_ops.run_artifact import RunWriter, detect_trigger
writer = RunWriter("P2-Backfill", "0.1.0", ["NEON_DSN"])
writer.start(*detect_trigger())
writer.check("step_name", "Description", "pass", ["run.log:line:42"])
writer.finish("success")
```

### Naming Conventions
| Entity | Pattern | Example |
|--------|---------|---------|
| Tables | `{schema}.{entity}_v{major}_{minor}` | `ovc.ovc_blocks_v01_1_min` |
| Contracts | `{name}_v{version}.json` | `export_contract_v0.1.1_min.json` |
| Run IDs | `{utc_compact}__{pipeline}__{sha7}` | `20260119T061512Z__P2-Backfill__a1b2c3d` |
| Block IDs | `YYYYMMDD-{A-L}-{SYMBOL}` | `20260116-I-GBPUSD` |

## Architecture Boundaries

| Boundary | Schema | Mutability |
|----------|--------|------------|
| **Option A** (Facts) | `ovc.*` | FROZEN |
| **Option B** (Features) | `derived.*` | Versioned |
| **Option C** (Outcomes) | `derived.ovc_outcomes_*` | Versioned |

Derived layers may READ from `ovc.*` but NEVER write to it.

## Footguns
1. Never edit canonical SQL views in place — version them
2. Date format must be `YYYY-MM-DD` for `BACKFILL_DATE_NY`
3. Never commit `.env` files — they contain secrets
4. Run from repo root (contracts use relative paths)
5. `/tv_secure` endpoint requires JSON envelope — `/tv` accepts raw pipe-delimited

## Key Files
- **Doctrine**: [docs/OVC_DOCTRINE.md](docs/OVC_DOCTRINE.md) — epistemic principles
- **Data Flow**: [docs/ops/OVC_DATA_FLOW_CANON_v0.1.md](docs/ops/OVC_DATA_FLOW_CANON_v0.1.md)
- **Worker**: [infra/ovc-webhook/src/index.ts](infra/ovc-webhook/src/index.ts)
- **Backfill**: [src/backfill_oanda_2h_checkpointed.py](src/backfill_oanda_2h_checkpointed.py)
- **C1 Features**: [src/derived/compute_c1_v0_1.py](src/derived/compute_c1_v0_1.py)
