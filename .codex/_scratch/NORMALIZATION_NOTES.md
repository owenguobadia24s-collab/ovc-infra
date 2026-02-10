# Path Normalization Notes

## Rules (applied in order)

1. **Strip whitespace**: `p = p.strip()`
2. **Remove wrapping quotes**:
   - If `p` starts with `"` and ends with `"` -> `p = p[1:-1]`
   - If `p` starts with `'` and ends with `'` -> `p = p[1:-1]`
3. **Replace backslashes**: `\` -> `/`
4. **Collapse repeated slashes**: `//+` -> `/`
5. **Remove leading `./`** if present
6. **Keep case unchanged**

## Observed Quoted Paths in Git Output

Two quoted/backslash paths were found in the full git history:

| Before (raw git output)           | After (normalized)            |
|-----------------------------------|-------------------------------|
| `"\\tools\\validate_contract.py"` | `tools/validate_contract.py`  |
| `"tools\\validate_contract.py"`   | `tools/validate_contract.py`  |

## Additional Before -> After Examples (from real git output samples)

| # | Before                                                         | After                                                          |
|---|----------------------------------------------------------------|----------------------------------------------------------------|
| 1 | `"\\tools\\validate_contract.py"`                              | `tools/validate_contract.py`                                   |
| 2 | `"tools\\validate_contract.py"`                                | `tools/validate_contract.py`                                   |
| 3 | `.github/workflows/ci_workflow_sanity.yml`                     | `.github/workflows/ci_workflow_sanity.yml` (unchanged)         |
| 4 | `reports/path1/evidence/runs/p1_20260205_GBPUSD/RUN.md`       | `reports/path1/evidence/runs/p1_20260205_GBPUSD/RUN.md` (unchanged) |
| 5 | `docs/governance/EXPECTED_VERSIONS_v0_1.json`                  | `docs/governance/EXPECTED_VERSIONS_v0_1.json` (unchanged)      |
| 6 | `scripts/governance/classify_change.py`                        | `scripts/governance/classify_change.py` (unchanged)            |
| 7 | `tools/phase3_control_panel/src/app/runs/page.tsx`             | `tools/phase3_control_panel/src/app/runs/page.tsx` (unchanged) |
| 8 | `.gitignore`                                                   | `.gitignore` (unchanged)                                       |
| 9 | `README.md`                                                    | `README.md` (unchanged)                                        |
| 10| `sql/path1/evidence/runs/p1_20260205/study_dis_v1_1.sql`      | `sql/path1/evidence/runs/p1_20260205/study_dis_v1_1.sql` (unchanged) |

## Notes

- Only 2 paths in the entire git history required quote/backslash normalization.
- Both resolve to `tools/validate_contract.py` after normalization.
- No paths starting with `./` were observed.
- No paths with repeated slashes (`//`) were observed.
- Without normalization, these would produce bad top-level dir tokens like `"tools/` or `"\tools/`.
