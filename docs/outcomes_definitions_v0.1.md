# Outcomes Definitions v0.1

## Scope
- Inputs: `ovc.ovc_blocks_v01_1_min` only.
- Reference price: `c` (block close).
- Horizons (K): 1, 2, 6, 12 (2H blocks).
- Partitioning: `PARTITION BY sym ORDER BY bar_close_ms`.

## Forward returns and direction
For each horizon K:

- `fwd_ret_k = (c[i+k] / c[i]) - 1`
- `fwd_dir_k = sign(c[i+k] - c[i])` mapped to:
  - `UP` if `c[i+k] > c[i]`
  - `DOWN` if `c[i+k] < c[i]`
  - `FLAT` if equal

## Excursions (next K blocks)
Using highs/lows in the next K bars (`i+1` through `i+K`):

- `mfe_k = max(h[i+1..i+k]) - c[i]`
- `mae_k = min(l[i+1..i+k]) - c[i]`

These are direction-agnostic excursions relative to the entry reference `c[i]`.

## Prediction evaluation (read-only)
For each horizon K:

- `hit_k` compares `pred_dir` to `fwd_dir_k`.
- Mapping: `pred_dir = NEUTRAL` is treated as a match to `fwd_dir_k = FLAT`.
- If `pred_dir` is NULL or `fwd_dir_k` is NULL, then `hit_k` is NULL.

## Missing future handling
- If the K-th future bar does not exist, all K-horizon outputs are NULL:
  - `fwd_ret_k`, `fwd_dir_k`, `mfe_k`, `mae_k`, `hit_k`.

## Guardrails
- Outcomes never write back into ingest.
- Outcomes are fully recomputable from MIN + formula.
- `eval_version` and `formula_hash` are embedded in every output.
