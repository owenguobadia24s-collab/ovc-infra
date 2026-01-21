# Path 1 State Plane Run: p1_20260121_001

## Run Metadata

| Field | Value |
|-------|-------|
| `run_id` | `p1_20260121_001` |
| `date_ny` | `2026-01-17` |
| `symbol` | `GBPUSD` |
| `generated_at` | `2026-01-21T00:00:00Z` |
| `block_count` | `12` |
| `valid_point_count` | `12` |
| `threshold_pack_id` | `state_plane_v0_2_default` |
| `threshold_pack_version` | `1` |
| `threshold_pack_hash` | `2e1f8d1476534bd6f94526c7db80c48541cc76bdbe8315f8c95e1548a50461e2` |

---

## Invariants Reminder

1. Observational only (no outcomes or decision surfaces).
2. Canonical inputs only (C1/C2/C3 views).
3. Thresholds and weights are versioned in the registry.

---

## Source

- View: `derived.v_ovc_state_plane_v0_2`
- Canonical views: `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1`, `derived.v_ovc_c3_features_v0_1`

---

## Path Metrics (Summary)

| Metric | Value |
|--------|-------|
| `path_length` | `2.9881299338312712` |
| `net_displacement` | `0.25079872407968906` |
| `efficiency` | `0.08393166617026057` |
| `jump_count` | `4` |

---

## Commands Executed

```bash
python scripts/path1/run_state_plane.py --symbol GBPUSD --date 2026-01-17
```

---

## Artifacts Generated

| File | Description |
|------|-------------|
| `outputs/state_plane_v0_2/trajectory.csv` | Block-ordered coordinates (A-L) |
| `outputs/state_plane_v0_2/trajectory.png` | State plane trajectory plot |
| `outputs/state_plane_v0_2/quadrant_string.txt` | Quadrant sequence |
| `outputs/state_plane_v0_2/path_metrics.json` | Path metrics summary |

---

## Execution Log

```
Run executed: 2026-01-21
Output location: reports/path1/evidence/runs/p1_20260121_001/outputs/state_plane_v0_2
```
