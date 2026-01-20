# Path 1 Run Conventions

**Version:** 1.0  
**Created:** 2026-01-20  
**Scope:** Path 1 score studies only

---

## 1. Purpose

This document defines conventions for Path 1 study runs to ensure:

- Reproducibility across time
- Comparability between runs
- Clear provenance of outputs

---

## 2. Run Naming Convention

### 2.1 Format

```
p1_{date}_{symbol}_{scope}_{run_id}
```

### 2.2 Components

| Component | Format | Description |
|-----------|--------|-------------|
| `p1` | Literal | Path 1 prefix |
| `date` | `YYYYMMDD` | Run date (NY timezone) |
| `symbol` | `GBPUSD`, `ALL`, etc. | Target symbol or `ALL` for multi-symbol |
| `scope` | `full`, `q4`, `30d`, etc. | Data scope (full history, quarter, days) |
| `run_id` | Short alphanumeric | Unique run identifier |

### 2.3 Examples

```
p1_20260120_GBPUSD_full_a1b2
p1_20260120_ALL_q4_x9y8
p1_20260115_GBPUSD_30d_test01
```

---

## 3. Output Locations

### 3.1 Directory Structure

```
reports/path1/
├── scores/           # Score definition reports (DIS, RES, LID)
├── studies/          # Study output files
│   ├── sanity/       # Distribution sanity checks
│   ├── outcomes/     # Outcome association tables
│   └── stability/    # Temporal stability analyses
└── runs/             # Run-specific output bundles (optional)
```

### 3.2 Output File Naming

Study outputs should include the run identifier:

```
{score}_{study_type}_{run_id}.csv
{score}_{study_type}_{run_id}.md
```

Examples:
```
dis_sanity_a1b2.csv
res_outcomes_bucketed_x9y8.csv
lid_stability_quarterly_test01.md
```

---

## 4. Valid Run Criteria

A Path 1 run is considered **valid** if and only if:

### 4.1 Uses Frozen Scores Only

- DIS-v1.1
- RES-v1.0
- LID-v1.0

No other scores are permitted in valid Path 1 runs.

### 4.2 References Canonical Views Only

All data must come from:

| View | Usage |
|------|-------|
| `derived.v_ovc_c1_features_v0_1` | Score inputs |
| `derived.v_ovc_c2_features_v0_1` | Score inputs |
| `derived.v_ovc_c3_features_v0_1` | Score inputs (if needed) |
| `derived.v_ovc_c_outcomes_v0_1` | Study joins only |

### 4.3 Produces Deterministic Output

- Same inputs → same outputs
- No random sampling without fixed seed
- No external data dependencies beyond canonical views

---

## 5. Comparability

These conventions exist to enable:

- **Temporal comparison:** Same study, different dates
- **Cross-symbol comparison:** Same study, different symbols
- **Replication:** Independent reproduction of results

All runs following these conventions should produce comparable, reproducible outputs.

---

## 6. What This Is NOT

- NOT a strategy evaluation framework
- NOT a backtesting convention
- NOT a performance tracking system
- NOT an optimization pipeline

Path 1 runs are **descriptive research** only.

---

## 7. References

| Document | Purpose |
|----------|---------|
| [OPTION_B_PATH1_STATUS.md](OPTION_B_PATH1_STATUS.md) | Freeze status and invariants |
| [SCORE_INVENTORY_v1.md](SCORE_INVENTORY_v1.md) | Score manifest |
