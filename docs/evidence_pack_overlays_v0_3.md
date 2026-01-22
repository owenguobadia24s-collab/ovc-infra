# Evidence Pack v0.3 Overlays - Liquidity & Microstructure Analysis

**Status Banner:** LIBRARY-ONLY — Not wired into `scripts/path1/build_evidence_pack_v0_2.py` or the canonical Path 1 execution flow.

## Overview

Evidence Pack v0.3 Overlays provide an **observational, read-only layer** of liquidity and microstructure analysis derived from M15 strips and the frozen 2H spine. Overlays are **additive artifacts** that do not mutate any canonical tables or existing v0.2 pack outputs.

**Current status:** library-only. The pack builder does not generate overlays, and no CLI flags or env vars enable them in the builder.

## Design Principles

1. **Read-only**: Overlays observe existing data without modification
2. **Deterministic**: All computations use stable sorting and canonical JSON encoding
3. **Additive**: Outputs are stored under `overlays_v0_3/` subdirectory
4. **Order-stable**: Events and sequences are sorted consistently
5. **Non-invasive**: Library-only; no pack-builder integration
6. **Intrablock-only**: All overlay computation operates within block boundaries (no cross-block lookbacks)
7. **Numeric precision**: All numeric values quantized to fixed precision (1e-5 / 5 decimal places)
8. **Event identity**: All v0.3-B events include deterministic SHA-1 event_id

## Output Structure

**DRAFT (integration not wired):** Intended layout if overlays are ever integrated into the evidence pack builder.

```
evidence_pack_v0_2/
├── backbone_2h.csv
├── strips/2h/
├── context/4h/
├── meta.json (DRAFT: would include overlays_v0_3 metadata if wired)
├── qc_report.json
└── overlays_v0_3/
    ├── micro/
    │   ├── 2h/
    │   │   ├── 20221211-A-GBPUSD.json
    │   │   ├── 20221211-B-GBPUSD.json
    │   │   └── ...
    │   └── liquidity_gradient/
    │       ├── 20221211-A-GBPUSD.json
    │       ├── 20221211-B-GBPUSD.json
    │       └── ...
    └── events/
        └── displacement_fvg.jsonl
```

## Module Descriptions

### v0.3-A: Wick & Sweep Microstructure Overlay

**Output**: Per-block JSON files in `overlays_v0_3/micro/2h/{block_id}.json`

**Features**:
- **Wick dominance sequence**: Classifies each M15 candle as `wick_top`, `wick_bot`, `balanced`, or `no_wick`
- **Sweep detection**: Identifies candles that take out prior highs/lows
  - Deterministic definition: Lookback = 3 prior candles
  - Sweep high: current high > all prior highs within lookback
  - Sweep low: current low < all prior lows within lookback
- **Raid-reclaim patterns**: Detects raid of prior extreme followed by close back within tolerance
  - Threshold: 50% of block range
  - Captures both high and low raids

**Schema**:
```json
{
  "block_id": "20221211-A-GBPUSD",
  "bar_open_ms": 1670760000000,
  "bar_close_ms": 1670767200000,
  "candle_count": 8,
  "block_range": 0.00234,
  "wick_sequence": [
    {
      "bar_start_ms": 1670760000000,
      "wick_dominance": "wick_top"
    }
  ],
  "sweeps": [
    {
      "bar_start_ms": 1670763600000,
      "bar_close_ms": 1670764500000,
      "swept_high": true,
      "swept_low": false,
      "prior_high": 1.21234,
      "sweep_high": 1.21256
    }
  ],
  "raid_reclaims": [
    {
      "type": "raid_high_reclaim",
      "raid_bar_start_ms": 1670763600000,
      "reclaim_bar_start_ms": 1670765400000,
      "prior_high": 1.21234,
      "raid_high": 1.21256,
      "reclaim_close": 1.21240
    }
  ]
}
```

### v0.3-B: Displacement / Imbalance Overlay

**Output**: Global JSONL file at `overlays_v0_3/events/displacement_fvg.jsonl`

**Features**:
- **Fair Value Gap (FVG) detection**: 3-candle rule
  - Bullish FVG: `candle[i-1].high < candle[i+1].low`
  - Bearish FVG: `candle[i-1].low > candle[i+1].high`
  - Minimum gap size: 0.00001 (configurable)
- **Mitigation tracking**: Detects when price revisits gap zone
- **Displacement candles**: Range exceeds threshold * rolling median
  - Window size: 20 candles
  - Threshold multiplier: 2.0x
- **Event identity**: Each event includes deterministic SHA-1 `event_id`

**Schema** (JSONL - one event per line):
```json
{"event_type": "fvg", "type": "bullish_fvg", "start_bar_ms": 1670760000000, "middle_bar_ms": 1670760900000, "end_bar_ms": 1670761800000, "gap_low": 1.21200, "gap_high": 1.21215, "gap_size": 0.00015, "mitigated": true, "mitigation_bar_ms": 1670763600000, "event_id": "a3f8b2c1d5e9..."}
{"event_type": "displacement", "bar_start_ms": 1670765400000, "bar_close_ms": 1670766300000, "range": 0.00123, "rolling_median": 0.00045, "ratio": 2.73, "bullish": true, "event_id": "f7d4e8a2b1c6..."}
```

**Event Ordering**: Events are sorted deterministically by `(start_ms, end_ms, event_type, level_low, level_high)`.

**Event Identity**: The `event_id` field is a SHA-1 hash derived from canonical event fields, ensuring stable identity across runs with identical inputs.

### v0.3-C: Liquidity Gradient Map

**Output**: Per-block JSON files in `overlays_v0_3/micro/liquidity_gradient/{block_id}.json`

**Features**:
- **Repeated touches (liquidity pools)**: Histogram of price level touches
  - Price quantization: 0.0001 bucket size
  - Touch threshold: 0.00005 tolerance
- **Compression zones**: Clusters of below-average range candles
  - Minimum cluster size: 3 consecutive candles
  - Threshold: 50% of average range
- **Breakout failures**: Price takes out prior high/low then reverses
  - Lookback: 5 candles
  - Captures both high and low failures

**Schema**:
```json
{
  "block_id": "20221211-A-GBPUSD",
  "bar_open_ms": 1670760000000,
  "bar_close_ms": 1670767200000,
  "candle_count": 8,
  "level_histogram": [
    {"level": 1.21200, "touches": 3},
    {"level": 1.21250, "touches": 5},
    {"level": 1.21300, "touches": 2}
  ],
  "compression_zones": [
    {
      "start_bar_ms": 1670760900000,
      "end_bar_ms": 1670762700000,
      "candle_count": 3,
      "avg_range": 0.00023
    }
  ],
  "breakout_failures": [
    {
      "type": "breakout_high_failure",
      "breakout_bar_ms": 1670763600000,
      "failure_bar_ms": 1670764500000,
      "prior_high": 1.21234,
      "breakout_high": 1.21256,
      "failure_close": 1.21230
    }
  ]
}
```

## Usage (LIBRARY-ONLY)

Overlays are **not wired** into `scripts/path1/build_evidence_pack_v0_2.py`. There are no supported CLI flags or env vars for pack builds.

To exercise overlays, use the library directly (see `tests/test_overlays_v0_3_determinism.py`).

## Configuration Parameters

All parameters are defined in `scripts/path1/overlays_v0_3.py`. Meta.json capture would require pack-builder integration, which is **not wired**.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PRICE_PRECISION` | 5 | Decimal precision for all numeric outputs (1e-5) |
| `SWEEP_LOOKBACK` | 3 | Number of prior candles for sweep detection |
| `RAID_RECLAIM_THRESHOLD` | 0.5 | Fraction of block range for reclaim tolerance |
| `FVG_RULE` | "3_candle" | Fair Value Gap detection rule identifier |
| `FVG_MIN_SIZE` | 0.00001 | Minimum gap size for FVG qualification |
| `DISPLACEMENT_WINDOW` | 20 | Rolling window size for displacement detection |
| `DISPLACEMENT_THRESHOLD_MULTIPLIER` | 2.0 | Multiplier over median for displacement |
| `LIQUIDITY_BUCKET_SIZE` | 0.0001 | Price quantization bucket size |
| `TOUCH_THRESHOLD` | 0.00005 | Tolerance for same-level touches |
| `INTRABLOCK_ONLY` | true | Computation scope restricted to block boundaries |

### Parameter Provenance (HISTORICAL / NOT WIRED)

The example below reflects the **intended** meta.json capture if overlays were wired into the pack builder. This is **not currently generated**.

## Determinism Guarantees

1. **Sorted candles**: All input candles sorted by `bar_start_ms` ascending
2. **Sorted events**: All output events sorted by (start_ms, end_ms, event_type, level_low, level_high)
3. **Canonical JSON**: `sort_keys=True, separators=(",", ":")` used for all JSON output
4. **Stable algorithms**: No random seeds, no hash-dependent ordering
5. **Numeric precision**: All floats quantized to fixed precision (1e-5) before serialization
6. **NaN/Infinity handling**: Non-finite values raise ValueError (never emitted)
7. **Event identity**: v0.3-B events include deterministic SHA-1 `event_id` derived from canonical fields
8. **Intrablock scope**: No cross-block lookbacks (all computation isolated within block boundaries)

## Pack Rebuild Equivalence (LIBRARY-ONLY NOTE)

The rebuild-equivalence tests in `tests/test_pack_rebuild_equivalence.py` exercise the overlay library. They do **not** indicate pack-builder integration.

## Manifest Integration (NOT WIRED)

There is no pack-builder integration, so overlay files are **not** included in evidence pack manifests.

## Performance Impact

Overlay generation adds minimal overhead:
- v0.3-A: O(n) per block where n = candle count
- v0.3-B: O(n) across all candles with small window lookback
- v0.3-C: O(n) per block with histogram aggregation

Typical overhead: < 2 seconds for packs with 30-50 blocks.

## Future Extensions

Potential enhancements (non-normative):
- Order flow imbalance (if tick data becomes available)
- Session-relative liquidity levels
- Multi-timeframe sweep correlation
- Volume profile integration (if volume data is reliable)

## Observational & Non-Canonical Status

**IMPORTANT**: v0.3 overlays are an observational analysis layer only. They are:
- **Non-canonical**: Not part of the canonical v0.2 evidence pack specification
- **Optional**: Library-only (no pack-builder integration)
- **Additive**: Stored separately under `overlays_v0_3/` subdirectory
- **Read-only**: Never mutate canonical spine tables or M15 data
- **Intrablock-only**: All computations isolated within block boundaries

Overlays provide supplemental liquidity and microstructure insights but do NOT modify or replace canonical pack data.

---

**Version**: v0.3 Overlays (2026-01)
**Status**: Observational library - not wired into canonical v0.2 pack builds
**Compatibility**: Library-only; no builder integration
**Determinism**: All outputs bit-identical across runs with identical inputs
**Test Suite**: `tests/test_overlays_v0_3_determinism.py` validates numeric stability and event ordering

