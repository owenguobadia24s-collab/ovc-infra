# OVC Infrastructure – Copilot Instructions

> **Purpose:** This file helps GitHub Copilot understand the project structure, conventions, and critical constraints.
> 
> **For new contributors:** Start with [docs/operations/OPERATING_BASE.md](../docs/operations/OPERATING_BASE.md) for onboarding.

## Quick Start

### Essential Reading (in order)
1. **Architecture & Data Flow** (below) – understand the 4 data layers
2. **[Governance Rules](../docs/governance/GOVERNANCE_RULES_v0.1.md)** – CANONICAL artifacts and modification rules
3. **[Branch Policy](../docs/governance/BRANCH_POLICY.md)** – PR naming and workflow conventions

### Development Workflow
1. Create branch: `git checkout -b pr/<area>-<topic>-vX.Y`
2. Make minimal changes following governance rules
3. Test locally: `.\scripts\verify_local.ps1`
4. Create PR (never merge to main directly)
5. Deploy after merge: `.\scripts\deploy_worker.ps1`

### Critical Constraints
- ⛔ **Option A is LOCKED** – Never modify canonical facts, MIN contract, or ingest worker
- ⛔ **Never mix Pine + infra changes** in the same PR
- ⛔ **Never edit contracts in-place** – create new versioned files instead
- ⛔ **Never modify CANONICAL artifacts** without explicit approval (see Governance Rules)

## Architecture Overview
OVC is a trading signal capture and evaluation system with four data layers (Options):
- **Option A (LOCKED)**: Ingest pipeline – raw TradingView exports → R2 + Neon `ovc.ovc_blocks_v01_1_min`
- **Option B**: Meaning layers derived from canonical facts only (replayable, no mutations)
- **Option C**: Evaluation/outcomes – reads canonical facts, writes to `derived` schema only
- **Option D**: Ops/sync tasks (Notion sync, QA artifacts to `ovc_qa` schema)

**Critical boundary**: Option A is LOCKED. Never modify `ovc.ovc_blocks_v01_1_min` schema, worker ingest logic, or MIN contract without explicit approval.

## Data Flow
```
TradingView Alert → POST /tv (raw text) → R2 archive → Neon MIN table
                    POST /tv_secure (JSON + token)        ↓
                                                    derived views (Option C)
OANDA backfill ─────────────────────────────────────────────┘
```

## Project Structure
```
infra/ovc-webhook/src/index.ts       # Cloudflare Worker (MIN v0.1.1 validation)
contracts/export_contract_v0.1.1_min.json  # IMMUTABLE schema (never edit in-place)
sql/01_tables_min.sql                # Neon canonical table definition
sql/derived_v0_1.sql                 # Option B derived features view
sql/option_c_v0_1.sql                # Option C outcomes/eval views
tests/sample_exports/min_001.txt     # Canonical test fixture
tools/validate_contract.py           # Python validator for exports
src/backfill_oanda_2h_checkpointed.py  # P2 historical backfill to MIN table
pine/export_module_v0.1.pine         # TradingView Pine export generator
```

## Developer Commands (PowerShell, from repo root)
```powershell
.\scripts\verify_local.ps1                              # Validate contract + pytest
.\scripts\deploy_worker.ps1                             # Deploy worker to Cloudflare
python .\scripts\pipeline_status.py --mode detect       # Check pipeline health
.\scripts\run_option_c.ps1 -RunId "local_test"          # Run Option C eval

# Local worker testing (run wrangler dev first from infra/ovc-webhook)
curl.exe -X POST http://localhost:8787/tv --data-binary "@tests/sample_exports/min_001.txt"

# OANDA backfill (single day)
$env:BACKFILL_DATE_NY="2026-01-16"; python .\src\backfill_oanda_2h_checkpointed.py
```

**Note**: Use `curl.exe` (not WSL curl) with forward slashes in paths.

## Contract Validation (MIN v0.1.1)
The worker enforces strict validation in [infra/ovc-webhook/src/index.ts](infra/ovc-webhook/src/index.ts):
- **E_KEY_ORDER**: Keys must appear in exact contract order
- **E_TYPE_COERCION**: Types must match (`int`, `float`, `bool_01`, `string_or_empty`)
- **Semantic checks**: OHLC consistency (`h >= max(o,c)`, `l <= min(o,c)`), `rng = h-l`, `body = abs(c-o)`
- **ret semantic check**: Currently DISABLED for ingest stability

To add new fields: create `export_contract_v0.1.2_min.json` (never edit existing contracts in-place).

## Testing
- **Worker tests**: `cd infra/ovc-webhook && npx vitest` (TypeScript/Vitest)
- **Contract tests**: `pytest tests/` (Python, runs via `verify_local.ps1`)
- Add test exports to `tests/sample_exports/` with `.txt` extension

## SQL Schema Rules
| Schema | Purpose | Allowed Operations |
|--------|---------|-------------------|
| `ovc` | Canonical facts | Option A only (LOCKED) |
| `derived` | Computed features/outcomes | Option B/C writes |
| `ovc_qa` | Validation artifacts | Option D writes |

## Key Pipelines

### P1 – Live Capture (TradingView → Neon)
- **Flow**: TradingView alert → `POST /tv` or `/tv_secure` → R2 archive → `ovc.ovc_blocks_v01_1_min`
- **Worker**: [infra/ovc-webhook/src/index.ts](infra/ovc-webhook/src/index.ts)
- **Config**: [infra/ovc-webhook/wrangler.jsonc](infra/ovc-webhook/wrangler.jsonc) (R2 binding: `RAW_EVENTS`)
- **Status**: PARTIAL (env-dependent, structurally sound)

### P2 – Historical Backfill (OANDA → Neon)
- **Flow**: OANDA API → H1 candles → aggregate to 2H blocks → `ovc.ovc_blocks_v01_1_min`
- **Script**: [src/backfill_oanda_2h_checkpointed.py](src/backfill_oanda_2h_checkpointed.py)
- **Run (single day)**: `$env:BACKFILL_DATE_NY="2026-01-16"; python .\src\backfill_oanda_2h_checkpointed.py`
- **Run (date range)**: `python .\src\backfill_oanda_2h_checkpointed.py --start_ny 2026-01-13 --end_ny 2026-01-17`
- **GitHub Action**: `.github/workflows/backfill_then_validate.yml` (backfill + validate range)
- **Status**: PASS (idempotent upsert, same PK as P1)
- **Note**: Weekends/holidays return 0 candles; use weekday dates

### P3 – Derived Features & Outcomes (SQL views)
- **Features**: [sql/derived_v0_1.sql](sql/derived_v0_1.sql) → `derived.ovc_block_features_v0_1`
- **Outcomes**: [sql/option_c_v0_1.sql](sql/option_c_v0_1.sql) → `derived.ovc_outcomes_v0_1`
- **Runner**: `.\scripts\run_option_c.ps1 -RunId "local_test"`
- **Status**: OPTIONAL/PARTIAL (non-blocking, derived-only writes)

### P4 – Validation (Facts vs Tape)
- **Flow**: Compare `ovc.ovc_blocks_v01_1_min` against tape source → `ovc_qa.*` artifacts
- **Script**: [src/validate_day.py](src/validate_day.py)
- **Schema**: [sql/qa_schema.sql](sql/qa_schema.sql)
- **Status**: PASS (core validation unconditional; derived validation conditional)

## Branch & PR Conventions
- `pr/<area>-<topic>-vX.Y` – PR branches, `wip/<area>-<topic>` – work-in-progress
- **Never mix pine + infra changes in same PR**
- Always work on branches; never commit directly to main

## Pine Script Workflow
The Pine indicator (`pine/export_module_v0.1.pine`) generates MIN exports on TradingView:

**Export generation:**
- Fires on 2H bar close when `exp_ready == 1` and `barstate.isconfirmed`
- Uses `alert()` with `alert.freq_once_per_bar_close` to send to webhook
- `block_id` format: `YYYYMMDD-{A-L}-{SYM}` (e.g., `20260116-I-GBPUSD`)
- Block letters A-L map to NY session 2H windows (A=00:00-02:00, B=02:00-04:00, etc.)

**Key field derivations in Pine:**
```pine
exp_dir = close > open ? 1 : close < open ? -1 : 0
exp_rng = high - low
exp_body = math.abs(close - open)
exp_ret = open != 0 ? (close - open) / open : 0
```

**Sanitization rules** (`f_s` function):
- `|` → `/` (pipe is delimiter)
- `=` → `:` (equals is key-value separator)  
- `na` → empty string

**Profiles:** MIN (webhook-safe ~50 fields) vs FULL (debug/copy ~150 fields)

**Testing Pine changes:**
1. Update Pine script in TradingView
2. Verify export string matches contract order via Export Readiness view
3. Test locally: copy export → save to `tests/sample_exports/` → run `.\scripts\verify_local.ps1`
4. Do NOT merge pine + infra changes in same PR

## Environment Variables
```powershell
$env:DATABASE_URL = 'postgresql://...'   # Required for SQL scripts
$env:NEON_DSN = 'postgresql://...'       # For backfill scripts
$env:OANDA_API_TOKEN = '...'             # For OANDA backfill
# Worker secrets (via wrangler): OVC_TOKEN, DATABASE_URL
```

## Common Gotchas
| Issue | Fix |
|-------|-----|
| "contract not found" | Run from repo root |
| "column does not exist" (Neon) | Sync `FIELDS` array in `index.ts` with `sql/01_tables_min.sql` |
| Worker deploy fails | Check `wrangler.jsonc` and secrets via `wrangler secret list` |
| Backfill returns 0 candles | Use weekday dates; weekends/holidays return empty |
| `curl: (26) Failed to open` | Use `curl.exe` with forward slashes in paths |

## Security & Governance

### Critical Path Protection
Changes to these files require **mandatory human review** and governance approval:
- `sql/01_tables_min.sql` – CANONICAL schema (LOCKED)
- `contracts/export_contract_v0.1.1_min.json` – CANONICAL contract (LOCKED)
- `infra/ovc-webhook/src/index.ts` – P1 ingest worker (LOCKED)
- `docs/governance/GOVERNANCE_RULES_v0.1.md` – Governance rules

See [GOVERNANCE_RULES_v0.1.md](../docs/governance/GOVERNANCE_RULES_v0.1.md) for complete modification authority matrix.

### Lifecycle States
- **CANONICAL**: Frozen contracts, never modify in-place (version bump required)
- **ACTIVE**: Operational code, modifiable with standard review
- **DEPRECATED**: Legacy artifacts, do not extend or rely upon
- **ORPHANED**: No consumers, candidate for removal

### Security Practices
- Never commit secrets (use `wrangler secret` for worker env vars)
- Validate all TradingView exports before database insert
- Use parameterized SQL queries to prevent injection
- Environment variables: Store in `.env` (gitignored) or wrangler secrets

## Getting Help

### Documentation Index
- **Operations**: [docs/operations/OPERATING_BASE.md](../docs/operations/OPERATING_BASE.md)
- **Architecture**: [docs/architecture/](../docs/architecture/)
- **Runbooks**: [docs/runbooks/](../docs/runbooks/)
- **Validation**: [docs/validation/](../docs/validation/)

### Issue Reporting
- Pipeline failures: Check `.\scripts\pipeline_status.py --mode detect`
- Test failures: Review `pytest` output and check `tests/sample_exports/`
- Worker issues: Check Cloudflare dashboard logs

---

*Last updated: 2026-01-22 | For questions, see [governance/decisions.md](../docs/governance/decisions.md)*
