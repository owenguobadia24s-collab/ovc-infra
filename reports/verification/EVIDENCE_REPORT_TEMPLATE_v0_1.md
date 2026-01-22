# OVC Evidence Report Template v0.1

## 1. Version Pins
- VERSION_OPTION_C: <version>
- Contracts:
  - export_contract_v0.1.1_min.json
  - eval_contract_v0.1.json
  - run_artifact_spec_v0.1.json
- Threshold packs:
  - <list threshold packs>

## 2. Inputs
- Instrument/date: <instrument> <YYYY-MM-DD>
- Data sources: <describe>
- Configs: <list>

## 3. Procedure
- Commands executed (copy-paste):
  1. Option C run: <command>
  2. Validator: <command or 'not run'>

## 4. Outputs
| Artifact | Path | SHA256 | Size (bytes) |
|----------|------|--------|--------------|
| run_report JSON | <path> | <sha256> | <size> |
| spotchecks TXT | <path> | <sha256> | <size> |
| ... | ... | ... | ... |

## 5. Reproducibility Check
- Compare run_report JSON: must match on all fields except allowed variance (e.g., timestamps)
- Compare spotchecks TXT: must be byte-equal
- If mismatch, localize and classify drift

## 6. Negative Evidence
- What did NOT happen (e.g., no failures, no missing artifacts, no spotcheck WARN/FAIL)

## 7. Next Tests
- One next test or improvement (short, scoped)
