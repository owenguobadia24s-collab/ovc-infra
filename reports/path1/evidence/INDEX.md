# Path 1 Evidence Runs Index

**Last Updated:** 2026-01-20

---

## Completed Runs

| Run ID | Date Range | Symbol(s) | n | Status | Link |
|--------|------------|-----------|---|--------|------|
| p1_20260120_001 | 2024-01-08 to 2024-01-12 | GBPUSD | 48 | COMPLETE | [RUN.md](runs/p1_20260120_001/RUN.md) |
| p1_20260120_002 | 2023-12-18 to 2023-12-22 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_002/RUN.md) |
| p1_20260120_003 | 2023-12-11 to 2023-12-15 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_003/RUN.md) |

---

## Run ID Convention

Format: `p1_{YYYYMMDD}_{SEQ}`

- `p1` = Path 1
- `YYYYMMDD` = Run creation date
- `SEQ` = 3-digit sequence number (001, 002, ...)

---

## Directory Structure

```
reports/path1/evidence/
├── INDEX.md              ← This file
├── runs/
│   └── {run_id}/
│       ├── RUN.md        ← Run summary report
│       └── outputs/      ← Raw study outputs
└── EVIDENCE_RUN_TEMPLATE.md
```

---

## Governance

All runs:
- Use **frozen** score versions only
- Produce **observational** summaries only
- Do **not** include thresholds, signals, or trading logic
- Are **append-only** (no retroactive edits)
