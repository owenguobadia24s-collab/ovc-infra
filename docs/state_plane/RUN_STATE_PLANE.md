# Run State Plane (Path 1)

## Purpose

Generate observational state-plane artifacts for a single day (A-L blocks).
Outputs are stored under `reports/path1/evidence/runs/<run_id>/outputs/state_plane_v0_2/`.

## Prerequisites

1. Views deployed:
   - `sql/derived/v_ovc_state_plane_v0_2.sql`
   - `sql/derived/v_ovc_state_plane_daypath_v0_2.sql` (optional)
2. Threshold pack registered and active:
   - `sql/06_state_plane_threshold_pack_v0_2.sql`
3. DB connection available via `DATABASE_URL` or `NEON_DSN`.

## Single-Day Run

```bash
python scripts/path1/run_state_plane.py --symbol GBPUSD --date 2026-01-17
```

## Date Range Run (per-day outputs)

```bash
python scripts/path1/run_state_plane.py --symbol GBPUSD --start-date 2026-01-15 --end-date 2026-01-19
```

## Outputs

Each run produces:

- `trajectory.csv` (block order A-L with x/y and quadrant)
- `trajectory.png` (connected state-plane path)
- `quadrant_string.txt` (sequence of quadrant IDs)
- `path_metrics.json` (path_length, net_displacement, efficiency, jump_count)

## Governance Notes

- Observational only (no outcomes inside the view).
- No score changes, no thresholds embedded in code.
- Thresholds and weights are versioned in `ovc_cfg.threshold_pack`.
