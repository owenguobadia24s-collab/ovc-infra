# Evidence Pack v0.3 Overlays - Sample Outputs

This document shows example outputs from the v0.3 overlay system to illustrate the data structure and format.

## v0.3-A: Microstructure Overlay (Per-Block)

**File**: `overlays_v0_3/micro/2h/20221212-A-GBPUSD.json`

```json
{
  "bar_close_ms": 1670849400000,
  "bar_open_ms": 1670842200000,
  "block_id": "20221212-A-GBPUSD",
  "block_range": 0.00187,
  "candle_count": 8,
  "raid_reclaims": [
    {
      "prior_high": 1.21345,
      "raid_bar_start_ms": 1670844000000,
      "raid_high": 1.21367,
      "reclaim_bar_start_ms": 1670846700000,
      "reclaim_close": 1.21348,
      "type": "raid_high_reclaim"
    },
    {
      "prior_low": 1.21158,
      "raid_bar_start_ms": 1670847600000,
      "raid_low": 1.21142,
      "reclaim_bar_start_ms": 1670848500000,
      "reclaim_close": 1.21165,
      "type": "raid_low_reclaim"
    }
  ],
  "sweeps": [
    {
      "bar_close_ms": 1670844900000,
      "bar_start_ms": 1670844000000,
      "prior_high": 1.21345,
      "sweep_high": 1.21367,
      "swept_high": true,
      "swept_low": false
    },
    {
      "bar_close_ms": 1670848500000,
      "bar_start_ms": 1670847600000,
      "prior_low": 1.21158,
      "sweep_low": 1.21142,
      "swept_high": false,
      "swept_low": true
    }
  ],
  "wick_sequence": [
    {
      "bar_start_ms": 1670842200000,
      "wick_dominance": "balanced"
    },
    {
      "bar_start_ms": 1670843100000,
      "wick_dominance": "wick_top"
    },
    {
      "bar_start_ms": 1670844000000,
      "wick_dominance": "wick_top"
    },
    {
      "bar_start_ms": 1670844900000,
      "wick_dominance": "balanced"
    },
    {
      "bar_start_ms": 1670845800000,
      "wick_dominance": "wick_bot"
    },
    {
      "bar_start_ms": 1670846700000,
      "wick_dominance": "balanced"
    },
    {
      "bar_start_ms": 1670847600000,
      "wick_dominance": "wick_bot"
    },
    {
      "bar_start_ms": 1670848500000,
      "wick_dominance": "wick_top"
    }
  ]
}
```

## v0.3-B: Displacement Overlay (Global JSONL)

**File**: `overlays_v0_3/events/displacement_fvg.jsonl`

Each line is a separate JSON event. Events are sorted by timestamp.

```jsonl
{"end_bar_ms": 1670843100000, "event_type": "fvg", "gap_high": 1.21224, "gap_low": 1.21212, "gap_size": 0.00012, "middle_bar_ms": 1670842200000, "mitigated": true, "mitigation_bar_ms": 1670845800000, "start_bar_ms": 1670841300000, "type": "bullish_fvg"}
{"end_bar_ms": 1670846700000, "event_type": "fvg", "gap_high": 1.21358, "gap_low": 1.21340, "gap_size": 0.00018, "middle_bar_ms": 1670845800000, "mitigated": false, "mitigation_bar_ms": null, "start_bar_ms": 1670844900000, "type": "bearish_fvg"}
{"bar_close_ms": 1670844900000, "bar_start_ms": 1670844000000, "bullish": true, "event_type": "displacement", "range": 0.00134, "ratio": 2.51, "rolling_median": 0.00053}
{"bar_close_ms": 1670848500000, "bar_start_ms": 1670847600000, "bullish": false, "event_type": "displacement", "range": 0.00119, "ratio": 2.34, "rolling_median": 0.00051}
{"end_bar_ms": 1670851200000, "event_type": "fvg", "gap_high": 1.21189, "gap_low": 1.21178, "gap_size": 0.00011, "middle_bar_ms": 1670850300000, "mitigated": true, "mitigation_bar_ms": 1670852100000, "start_bar_ms": 1670849400000, "type": "bullish_fvg"}
```

## v0.3-C: Liquidity Gradient (Per-Block)

**File**: `overlays_v0_3/micro/liquidity_gradient/20221212-A-GBPUSD.json`

```json
{
  "bar_close_ms": 1670849400000,
  "bar_open_ms": 1670842200000,
  "block_id": "20221212-A-GBPUSD",
  "breakout_failures": [
    {
      "breakout_bar_ms": 1670844000000,
      "breakout_high": 1.21367,
      "failure_bar_ms": 1670844900000,
      "failure_close": 1.21342,
      "prior_high": 1.21345,
      "type": "breakout_high_failure"
    }
  ],
  "candle_count": 8,
  "compression_zones": [
    {
      "avg_range": 0.00034,
      "candle_count": 3,
      "end_bar_ms": 1670845800000,
      "start_bar_ms": 1670844000000
    }
  ],
  "level_histogram": [
    {
      "level": 1.21140,
      "touches": 2
    },
    {
      "level": 1.21150,
      "touches": 3
    },
    {
      "level": 1.21160,
      "touches": 4
    },
    {
      "level": 1.21170,
      "touches": 2
    },
    {
      "level": 1.21200,
      "touches": 5
    },
    {
      "level": 1.21210,
      "touches": 3
    },
    {
      "level": 1.21220,
      "touches": 4
    },
    {
      "level": 1.21230,
      "touches": 2
    },
    {
      "level": 1.21240,
      "touches": 3
    },
    {
      "level": 1.21250,
      "touches": 2
    },
    {
      "level": 1.21300,
      "touches": 4
    },
    {
      "level": 1.21310,
      "touches": 3
    },
    {
      "level": 1.21320,
      "touches": 2
    },
    {
      "level": 1.21340,
      "touches": 5
    },
    {
      "level": 1.21350,
      "touches": 3
    },
    {
      "level": 1.21360,
      "touches": 2
    }
  ]
}
```

## meta.json Integration

The `meta.json` file includes overlay metadata when overlays are enabled:

```json
{
  "version": "evidence_pack_v0_2",
  "run_id": "p1_20260122_001",
  "symbol": "GBPUSD",
  "date_from": "2022-12-12",
  "date_to": "2022-12-14",
  "generated_at": "2026-01-22T18:30:45Z",

  "overlays_v0_3": {
    "enabled": true,
    "version": "0.3",
    "modules": ["v0.3-A", "v0.3-B", "v0.3-C"],
    "counts": {
      "v0.3-A": 36,
      "v0.3-B": 142,
      "v0.3-C": 36
    }
  },

  "counts": {
    "blocks": 36,
    "strips_written": 36,
    "context_written": 18
  }
}
```

When overlays are disabled:

```json
{
  "overlays_v0_3": {
    "enabled": false,
    "version": "0.3",
    "modules": []
  }
}
```

## Directory Structure Example

Complete pack structure with v0.3 overlays:

```
evidence_pack_v0_2/
├── backbone_2h.csv
├── manifest.json
├── meta.json
├── pack_sha256.txt
├── qc_report.json
├── strips/
│   └── 2h/
│       ├── 20221212-A-GBPUSD.csv
│       ├── 20221212-B-GBPUSD.csv
│       └── ...
├── context/
│   └── 4h/
│       ├── 20221212-0000-GBPUSD.csv
│       └── ...
└── overlays_v0_3/
    ├── micro/
    │   ├── 2h/
    │   │   ├── 20221212-A-GBPUSD.json
    │   │   ├── 20221212-B-GBPUSD.json
    │   │   └── ...
    │   └── liquidity_gradient/
    │       ├── 20221212-A-GBPUSD.json
    │       ├── 20221212-B-GBPUSD.json
    │       └── ...
    └── events/
        └── displacement_fvg.jsonl
```

## Interpretation Guide

### Wick Dominance

- **wick_top**: Upper wick > 2x lower wick (rejection from highs)
- **wick_bot**: Lower wick > 2x upper wick (rejection from lows)
- **balanced**: Wicks roughly equal
- **no_wick**: Body fills entire candle range

### Sweep Events

- **swept_high**: Current candle high exceeds all prior highs in lookback window
- **swept_low**: Current candle low breaks below all prior lows in lookback window
- Indicates liquidity grab or stop hunt behavior

### Raid-Reclaim

- **raid_high_reclaim**: Price breaks above prior high, then later closes back near it
- **raid_low_reclaim**: Price breaks below prior low, then later closes back near it
- Suggests false breakout or liquidity trap

### Fair Value Gaps (FVG)

- **bullish_fvg**: Gap between prior candle high and next candle low
- **bearish_fvg**: Gap between prior candle low and next candle high
- **mitigated**: Price returned to fill (or partially fill) the gap
- Represents inefficient price action or institutional order zones

### Displacement

- Candle range significantly exceeds rolling median
- **ratio > 2.0**: Strong momentum move
- **bullish**: Close > open (green candle)
- Indicates potential trend continuation or reversal

### Liquidity Levels

- **touches**: Number of times price interacted with a quantized level
- Higher touch counts suggest significant support/resistance zones
- Use for identifying potential turning points or magnets

### Compression Zones

- Consecutive candles with below-average range
- Indicates consolidation or accumulation/distribution
- Often precedes breakout or significant move

### Breakout Failures

- Price breaks level then reverses quickly
- **breakout_high_failure**: Takes out high, fails to hold
- **breakout_low_failure**: Takes out low, bounces back
- Classic trap or liquidity grab pattern

---

**Note**: All sample data is illustrative. Actual overlay outputs depend on real M15 candle data from the database.
