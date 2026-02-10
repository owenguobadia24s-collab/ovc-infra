# Backfill Report

## Key Invariants

- Total commits expected: 264 -- **PASS** (got 264)
- No duplicate hashes -- **PASS**
- Chronological order preserved -- **PASS**
- No bad dir tokens (quote-prefixed) -- **PASS**
- Ledger rows == Overlay rows (264) -- **PASS**
- Hash alignment ledger<->overlay -- **PASS**

## UNKNOWN / Notes

- Commits with empty touched_paths: 1
  - `19c9d26e1fa8`
- Commits classified UNKNOWN: 72
  - `456723685af2`
  - `b57a2ecf8ab6`
  - `e069d4d1edb5`
  - `b8d1cfe29816`
  - `ebf848ffdf5a`
  - `2d57db81d46d`
  - `8e1882cb31cf`
  - `40ed50f8b29c`
  - `09d951775170`
  - `1cf568a4e128`
  - `3df870db1e0e`
  - `42bf13666843`
  - `84479bf92ece`
  - `4c6102503f05`
  - `cf5d987444ce`

- Tags not observed in any commit path: chmod_test, data
