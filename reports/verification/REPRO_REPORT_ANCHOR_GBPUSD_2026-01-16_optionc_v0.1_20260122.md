# OVC Reproducibility Report: ANCHOR_GBPUSD_2026-01-16_optionc_v0.1

**Anchor Reference:** [reports/verification/EVIDENCE_ANCHOR_v0_1.md](EVIDENCE_ANCHOR_v0_1.md)

**Date:** 2026-01-22

## Commands Executed
```
./scripts/run/run_option_c.ps1 -RunId ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_1
./scripts/run/run_option_c.ps1 -RunId ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_2
./scripts/run/run_option_c.ps1 -RunId ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_3
```

## Run Table
| Run # | run_id                                      | run_report JSON SHA256                  | spotchecks TXT SHA256                   | JSON size | TXT size | Notes |
|-------|---------------------------------------------|------------------------------------------|------------------------------------------|-----------|----------|-------|
| 1     | ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_1     | F514FBCEA7238319351C278E658B571184648E78662E645A865BFAB11888B784 | 0B1521244BAC740F41B78EEFEBFC343A1F5F90D68638F898772BEF873899C2C7 | 630       | 5514     |       |
| 2     | ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_2     | A999F75F67AF32FF1B321A938F6F62911F807FA378FEC15530D7844450D0D2CF | 0B1521244BAC740F41B78EEFEBFC343A1F5F90D68638F898772BEF873899C2C7 | 630       | 5514     |       |
| 3     | ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_3     | A264FDD77FFB115612ACCD75380DF63009A2780F2C950C130CB2A27F2180336D | 0B1521244BAC740F41B78EEFEBFC343A1F5F90D68638F898772BEF873899C2C7 | 630       | 5514     |       |

## Results
- **spotchecks TXT**: All three runs are byte-equal (identical SHA256 and size).
- **run_report JSON**: All three runs have identical content except for the `started_at` and `finished_at` fields (allowed variance). All other fields are byte-equal.

## Repro Verdict
**PASS** — All invariants hold. Only allowed timestamp fields differ in run_report JSON. No drift in any other field. Spotchecks are strictly reproducible.

## Negative Evidence
- No spotcheck failures or warnings.
- No missing artifacts.
- No unexpected output files.
- No validator command was run (not required for Option C anchor).

## Next Action
- (If stricter reproducibility is desired, consider normalizing timestamps in run_report JSON for future hash checks, but this is not required for current acceptance.)
