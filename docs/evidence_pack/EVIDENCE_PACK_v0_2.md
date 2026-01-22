# Evidence Pack v0.2 (M15 Overlay)

Evidence Pack v0.2 is a read-only, deterministic overlay that pairs each 2H block
with its underlying M15 candles. It is designed to support auditability and
traceability without changing any canonical tables or frozen views.

## Invariants

- Read-only: consumes `derived.v_path1_evidence_dis_v1_1`,
  `ovc.ovc_blocks_v01_1_min`, and `ovc.ovc_candles_m15_raw` only.
- Canonical 2H spine is never modified.
- Alignment is based on `bar_close_ms` timestamps (UTC milliseconds).
- Each 2H block must map to exactly 8 M15 candles.
- Each 4H context window must map to 16 M15 candles, aggregated to M30 (8 rows)
  or H1 (4 rows) if M30 aggregation fails.

## Alignment Math (bar_close_ms-based)

Let `T` be the 2H block `bar_close_ms` from `derived.v_path1_evidence_dis_v1_1`.

2H window:
- M15 candles are selected where `bar_close_ms` is in `(T - 2h, T]`.
- Each M15 candle has `bar_start_ms = bar_close_ms - 15m`.
- Expected count: 8 candles, contiguous in 15-minute steps (900,000 ms).

4H window:
- Group by `(date_ny, block4h)` from `ovc.ovc_blocks_v01_1_min`.
- Let `T4` be the maximum `bar_close_ms` in the group.
- M15 candles are selected where `bar_close_ms` is in `(T4 - 4h, T4]`.
- Expected count: 16 candles, contiguous in 15-minute steps.
- Aggregate to 8 M30 candles (2 x M15). If that fails, aggregate to 4 H1 candles
  (4 x M15).

## QC Checks

The builder writes `qc_report.json` with these checks:

- Candle count per 2H block (must be 8).
- Continuity checks for 15-minute spacing.
- OHLC sanity checks (high >= low, open/close within range).
- Aggregation match to 2H spine OHLC with tolerance (default `1e-6`).

## Outputs

Pack root (per run):

- `backbone_2h.csv` — `block_id` to strip path and candle counts.
- `meta.json` — pack metadata and sources.
- `qc_report.json` — QC checks and summary.
- `strips/2h/{block_id}.csv` — M15 candles per 2H block.
- `context/4h/{block4h}_{date}.csv` — M30/H1 context for each 4H window.
