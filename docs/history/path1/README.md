# Path 1 — Descriptive Score Research (Historical Overview)

**STATUS: HISTORICAL (REFERENCE ONLY)**  
This overview reflects Path 1 context at the time it was written.  
Current execution ergonomics are defined in `PATH1_EXECUTION_MODEL.md`.  
Canonical facts remain in `reports/path1/evidence/INDEX.md`.

**Canonical Path 1 entrypoint:** see repo root `README.md` → “Path 1 (FROZEN) — Descriptive Score Research”.

---

## What Path 1 Is

Path 1 is a collection of **descriptive, non-predictive scores** derived from canonical OVC features. These scores:

- Describe past bar characteristics
- Use canonical input views only
- Are SELECT-only (no data mutation)
- Support repeatable, deterministic studies

Path 1 exists to build **observational evidence** about score-outcome associations without making predictions or strategy claims.

---

## What Path 1 Is NOT

- **NOT** a trading system or strategy framework
- **NOT** a signal generation pipeline
- **NOT** a prediction or forecasting tool
- **NOT** an optimization or tuning environment
- **NOT** a place for thresholds, triggers, or decision logic

Any correlation between scores and outcomes observed in Path 1 studies describes **historical co-occurrence only** and does not imply predictability, causation, or actionable information.

---

## Current Status

**FROZEN** as of 2026-01-20

Frozen scores:
- DIS-v1.1
- RES-v1.0
- LID-v1.0

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [OPTION_B_PATH1_STATUS.md](OPTION_B_PATH1_STATUS.md) | Freeze declaration and invariants |
| [SCORE_INVENTORY_v1.md](SCORE_INVENTORY_v1.md) | Compact score manifest |
| [SCORE_LIBRARY_v1.md](scores/SCORE_LIBRARY_v1.md) | Full score definitions |
| [RUN_CONVENTIONS.md](RUN_CONVENTIONS.md) | Run naming and output conventions |

---

## Directory Structure (Historical Reference)

```
docs/history/path1/
├── README.md                    # This file
├── OPTION_B_PATH1_STATUS.md     # Freeze status
├── SCORE_INVENTORY_v1.md        # Score manifest
├── RUN_CONVENTIONS.md           # Run conventions
└── scores/
    └── SCORE_LIBRARY_v1.md      # Full definitions

sql/path1/
├── scores/                      # Score computation SQL
│   ├── score_dis_v1_1.sql
│   ├── score_res_v1_0.sql
│   └── score_lid_v1_0.sql
└── studies/                     # Study SQL files
    ├── dis_*.sql
    ├── res_*.sql
    └── lid_*.sql

reports/path1/
└── scores/                      # Score reports
    ├── DIS_v1_1.md
    ├── RES_v1_0.md
    └── LID_v1_0.md
```

---

## Post-Run Validation

After generating an evidence run, validate its structural integrity using the post-run validator. This script checks for required directories, files, content sanity (no psql errors, non-empty outputs), and cross-file consistency without interpreting results or querying the database.

```powershell
# Basic validation
python scripts/path1/validate_post_run.py --run-id p1_20260120_001

# Strict mode (additional SQL header and INDEX.md checks)
python scripts/path1/validate_post_run.py --run-id p1_20260120_001 --strict

# JSON output for CI/automation
python scripts/path1/validate_post_run.py --run-id p1_20260120_001 --json
```

Exit code 0 = PASS, exit code 1 = FAIL with detailed violation report.

---

## Next Steps

Work within Path 1 should focus on:

1. **Evidence-building:** Running studies to observe score-outcome associations
2. **Documentation:** Recording study results in reports

Work **outside** Path 1 scope:

- New scores → require `SCORE_LIBRARY_v2`
- Strategy development → prohibited in Path 1
- Score modifications → prohibited (library is frozen)
