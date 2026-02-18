# Repo Cartographer Run Ledger Schema v0.1

This note applies to future appended lines in `docs/catalogs/REPO_CARTOGRAPHER_RUN_LEDGER_v0.1.jsonl`.

- Required selector fields:
  - `run_id` (string)
  - `run_ts` (UTC ISO-8601 string, `YYYY-MM-DDTHH:MM:SSZ`)
  - `status` (`"OK"` or `"FAIL"`)

`run_ts` derivation:
- Use `generated_utc` when it is a valid UTC ISO-8601 string.
- Otherwise use current UTC time at ledger emission.

`status` criteria:
- `status = "OK"` only when all files exist under `artifacts/repo_cartographer/<run_id>/`:
  - `MANIFEST.json`
  - `MANIFEST.sha256`
  - `SEAL.json`
  - `SEAL.sha256`
- And SHA-256 values in `MANIFEST.sha256` / `SEAL.sha256` match `MANIFEST.json` / `SEAL.json`.
- Otherwise `status = "FAIL"`.

Existing historical ledger lines are not modified or backfilled.
