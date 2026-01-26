# CURRENT STATE: Trust Map

**Status: CURRENT_STATE (frozen on 2026-01-23)**

Classification of all data products by trustworthiness.

---

## CANONICAL (Authoritative, Trustworthy)

- **R2 raw ingests** (`tv/YYYY-MM-DD/...`) — Unaltered TradingView export strings
- **`ovc.ovc_blocks_v01_1_min`** (OHLC fields only):
  - `block_id`, `sym`, `date_ny`, `block2h`, `block4h`
  - `bar_close_ms`, `o`, `h`, `l`, `c`
  - Upsert idempotency enforced; duplicate keys rejected
- **`ovc.ovc_candles_m15_raw`** — M15 raw candles; no derived fields
- **`ovc_cfg.threshold_pack`** — Static config for L3 regime classification
- **`ovc_cfg.threshold_pack_active`** — Active threshold selection

---

## DERIVED BUT VALID (Regenerable with caution)

- **`derived.ovc_l1_features_v0_1`** (table) — Python-computed, validated by QA scripts
- **`derived.ovc_l2_features_v0_1`** (table) — Python-computed, validated by QA scripts
- **`derived.v_ovc_l1_features_v0_1`** (view) — SQL definition, recomputes from canonical
- **`derived.v_ovc_l2_features_v0_1`** (view) — SQL definition, recomputes from canonical
- **`derived.v_ovc_l3_features_v0_1`** (view) — SQL definition, uses threshold registry
- **`derived.ovc_outcomes_v0_1`** (view) — Option C runner output when run manually
- **`derived.ovc_scores_v0_1`** (view) — Option C scoring view when run manually
- **`derived.v_ovc_c_outcomes_v0_1`** (view) — Feature-based outcomes view (canonical per docs)
- **Path1 evidence packs** — Deterministic when built from consistent views; hashes tracked

---

## AMBIGUOUS (Unclear authority)

- **`state_tag`** in `ovc.ovc_blocks_v01_1_min` — Conceptually L2/L3 derived; stored in canonical table
- **`trend_tag`** in `ovc.ovc_blocks_v01_1_min` — Conceptually L2/L3 derived; stored in canonical table
- **`pred_dir`** in `ovc.ovc_blocks_v01_1_min` — Conceptually L3 derived; stored in canonical table
- **`bias_dir`** in `ovc.ovc_blocks_v01_1_min` — Conceptually L3 derived; stored in canonical table
- **`struct_state`** in `ovc.ovc_blocks_v01_1_min` — Conceptually L2 derived; stored in canonical table
- **Legacy vs split derived** — Both `derived.ovc_block_features_v0_1` AND split L1/L2/L3 exist
- **L3 regime classification** — Compute script unused; only SQL view available
- **Outcome source for evidence** — Path1 uses `v_ovc_c_outcomes_v0_1`; Option C runner creates `ovc_outcomes_v0_1`

---

## INVALID (Unsafe to rely on)

- **`ovc_option_c_schedule.yml`** — References nonexistent script `scripts/run_option_c.sh`
- **Option C automation** — Does not execute; scheduled workflow broken
- **`ovc.ovc_run_reports_v01`** (worker telemetry) — Schema drift: `ended_at`/`meta` vs `finished_at`
- **Any Option separation guarantee** — A stores B fields; B has dual implementations
- **Path2 evidence** — No code exists; only documentation
- **Migration state** — No ledger; cannot verify DB matches repo
- **CI test results** — No pytest execution in workflows
