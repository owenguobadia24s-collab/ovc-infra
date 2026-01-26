# OVC Evidence Anchor v0.1

**Anchor ID:** ANCHOR_GBPUSD_2026-01-16_optionc_v0.1

## Instrument & Date
- Instrument: GBPUSD
- Anchor Date: 2026-01-16
- Timezone: New York (NY), as per repo docs (bar windows are NY session, e.g., block_id `20260116-I-GBPUSD`)

## Version Pins
- VERSION_OPTION_C: `v0.1`
- Contracts:
  - contracts/export_contract_v0.1.1_min.json
  - contracts/eval_contract_v0.1.json
  - contracts/run_artifact_spec_v0.1.json
- Threshold packs:
  - configs/threshold_packs/l3_example_pack_v1.json
  - configs/threshold_packs/l3_regime_trend_v1.json
  - configs/threshold_packs/state_plane_v0_2_default_v1.json

## Exact Commands

### 1. Option C Run (PowerShell)
```
.\scripts\run\run_option_c.ps1 -RunId ANCHOR_GBPUSD_2026-01-16_optionc_v0.1
```

### 2. Validator Command
```
python src/validate_day.py --symbol GBPUSD --date_ny 2026-01-16
```

## Expected Outputs & Invariants
- `reports/run_report_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.json`: must be identical after normalizing allowed timestamp fields
- `reports/spotchecks_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.txt`: must be byte-equal
- `reports/run_report_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1.md`: not compared (human-readable summary)

## Allowed Variance Rules
- Allowed to differ: `started_at`, `finished_at` fields in JSON
- All other fields must match exactly (byte-equal after normalizing above)

---

*This anchor is grounded in GBPUSD, 2026-01-16, as this date has prior artifacts and is fully covered in the repo.*
