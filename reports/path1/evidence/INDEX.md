# Path 1 Evidence Runs Index

**Last Updated:** 2026-01-22

---

## Completed Runs

| Run ID | Date Range | Symbol(s) | n | Status | Link |
|--------|------------|-----------|---|--------|------|
| p1_20260120_001 | 2024-01-08 to 2024-01-12 | GBPUSD | 48 | COMPLETE | [RUN.md](runs/p1_20260120_001/RUN.md) |
| p1_20260120_002 | 2023-12-18 to 2023-12-22 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_002/RUN.md) |
| p1_20260120_003 | 2023-12-11 to 2023-12-15 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_003/RUN.md) |
| p1_20260120_004 | 2023-12-04 to 2023-12-08 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_004/RUN.md) |
| p1_20260120_005 | 2023-11-27 to 2023-12-01 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_005/RUN.md) |
| p1_20260120_006 | 2023-11-20 to 2023-11-24 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_006/RUN.md) |
| p1_20260120_007 | 2023-11-13 to 2023-11-17 | GBPUSD | 60 | COMPLETE | [RUN.md](runs/p1_20260120_007/RUN.md) |
| p1_20260120_008 | 2023-11-06 to 2023-11-10 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_008/RUN.md) |
| p1_20260120_009 | 2023-10-30 to 2023-11-03 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_009/RUN.md) |
| p1_20260120_010 | 2023-10-23 to 2023-10-27 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_010/RUN.md) |
| p1_20260120_011 | 2023-10-16 to 2023-10-20 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_011/RUN.md) |
| p1_20260120_012 | 2023-10-09 to 2023-10-13 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_012/RUN.md) |
| p1_20260120_013 | 2023-10-02 to 2023-10-06 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_013/RUN.md) |
| p1_20260120_014 | 2023-09-25 to 2023-09-29 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_014/RUN.md) |
| p1_20260120_015 | 2023-09-18 to 2023-09-22 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_015/RUN.md) |
| p1_20260120_031 | 2022-12-12 to 2022-12-14 | GBPUSD | 36 | COMPLETE | [RUN.md](runs/p1_20260120_031/RUN.md) |
| p1_20260120_016 | 2023-09-11 to 2023-09-15 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_016/RUN.md) |
| p1_20260120_017 | 2023-09-04 to 2023-09-08 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_017/RUN.md) |
| p1_20260120_018 | 2023-08-28 to 2023-09-01 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_018/RUN.md) |
| p1_20260120_019 | 2023-08-21 to 2023-08-25 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_019/RUN.md) |
| p1_20260120_020 | 2023-08-14 to 2023-08-18 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_020/RUN.md) |
| p1_20260120_021 | 2023-08-07 to 2023-08-11 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_021/RUN.md) |
| p1_20260120_022 | 2023-07-31 to 2023-08-04 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_022/RUN.md) |
| p1_20260120_023 | 2023-07-24 to 2023-07-28 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_023/RUN.md) |
| p1_20260120_024 | 2023-07-17 to 2023-07-21 | GBPUSD | 59 | COMPLETE | [RUN.md](runs/p1_20260120_024/RUN.md) |

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
