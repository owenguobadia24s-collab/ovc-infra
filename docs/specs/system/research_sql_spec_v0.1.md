/* ============================================================================
OVC Research Query Pack v0.1 — SQL-ready spec (Postgres / Neon)

ASSUMPTIONS
- Base table name: ovc_min_events
- One row per 2H block close, unique by block_id
- Columns exist per your locked MIN schema, at least:
  block_id, sym, date_ny, bar_close_ms, block2h, block4h,
  o,h,l,c,rng,body,dir,ret,
  state_tag, value_tag, trend_tag, struct_state, space_tag,
  htf_stack, with_htf, rd_state, regime_tag, trans_risk,
  bias_mode, bias_dir, perm_state, rail_loc,
  tradeable, conf_l3,
  play, pred_dir, pred_target, timebox, invalidation,
  source, build_id, note, ready

CONVENTIONS
- Empty strings treated as NULL via NULLIF(x,'')
- "Win" = ret > 0
- state_key is frozen as:
  trend_tag|struct_state|space_tag|bias_mode|bias_dir|perm_state|play|pred_dir|timebox
  (You can change this later, but that becomes a new view version.)
============================================================================ */

/* ----------------------------------------------------------------------------
0) Recommended constraints + indexes (conceptual spec)
---------------------------------------------------------------------------- */

-- Primary key (should already exist)
-- ALTER TABLE ovc_min_events ADD CONSTRAINT ovc_min_events_pk PRIMARY KEY (block_id);

-- Core indexes for sequencing + group-bys
CREATE INDEX IF NOT EXISTS idx_ovc_min_sym_time
  ON ovc_min_events (sym, bar_close_ms);

CREATE INDEX IF NOT EXISTS idx_ovc_min_date_sym
  ON ovc_min_events (date_ny, sym);

CREATE INDEX IF NOT EXISTS idx_ovc_min_session
  ON ovc_min_events (sym, block4h, block2h);

CREATE INDEX IF NOT EXISTS idx_ovc_min_tradeable_ready
  ON ovc_min_events (tradeable, ready);

-- Optional: if you frequently filter on these
CREATE INDEX IF NOT EXISTS idx_ovc_min_state_dims
  ON ovc_min_events (sym, trend_tag, struct_state, space_tag, bias_mode, bias_dir, perm_state, play, pred_dir, timebox);


/* ----------------------------------------------------------------------------
A) Base normalization view (cleans empties, standardizes state_key)
---------------------------------------------------------------------------- */
CREATE OR REPLACE VIEW v_ovc_min_events_norm AS
SELECT
  block_id,
  sym,
  tz,
  date_ny,
  bar_close_ms,
  block2h,
  block4h,

  o, h, l, c,
  rng, body,
  dir,
  ret,

  NULLIF(state_tag, '')     AS state_tag,
  NULLIF(value_tag, '')     AS value_tag,
  NULLIF(event, '')         AS event,
  tt,
  NULLIF(cp_tag, '')        AS cp_tag,
  tis,

  rrc,
  vrc,

  NULLIF(trend_tag, '')     AS trend_tag,
  NULLIF(struct_state, '')  AS struct_state,
  NULLIF(space_tag, '')     AS space_tag,

  NULLIF(htf_stack, '')     AS htf_stack,
  with_htf,

  NULLIF(rd_state, '')      AS rd_state,
  NULLIF(regime_tag, '')    AS regime_tag,
  NULLIF(trans_risk, '')    AS trans_risk,

  NULLIF(bias_mode, '')     AS bias_mode,
  NULLIF(bias_dir, '')      AS bias_dir,      -- enum-ish, still stored as text
  NULLIF(perm_state, '')    AS perm_state,
  NULLIF(rail_loc, '')      AS rail_loc,

  tradeable,
  NULLIF(conf_l3, '')       AS conf_l3,

  NULLIF(play, '')          AS play,
  NULLIF(pred_dir, '')      AS pred_dir,      -- enum-ish, still stored as text
  NULLIF(pred_target, '')   AS pred_target,
  NULLIF(timebox, '')       AS timebox,
  NULLIF(invalidation, '')  AS invalidation,

  NULLIF(source, '')        AS source,
  NULLIF(build_id, '')      AS build_id,
  NULLIF(note, '')          AS note,
  ready,

  -- Frozen state_key (v0.1)
  CONCAT_WS('|',
    NULLIF(trend_tag,''),
    NULLIF(struct_state,''),
    NULLIF(space_tag,''),
    NULLIF(bias_mode,''),
    NULLIF(bias_dir,''),
    NULLIF(perm_state,''),
    NULLIF(play,''),
    NULLIF(pred_dir,''),
    NULLIF(timebox,'')
  ) AS state_key

FROM ovc_min_events;


/* ----------------------------------------------------------------------------
B) Sequenced view (adds prev_* context using LAG)
---------------------------------------------------------------------------- */
CREATE OR REPLACE VIEW v_ovc_min_events_seq AS
SELECT
  n.*,

  LAG(block_id)      OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_block_id,
  LAG(bar_close_ms)  OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_bar_close_ms,
  LAG(ret)           OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_ret,
  LAG(dir)           OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_dir,
  LAG(state_key)     OVER (PARTITION BY sym ORDER BY bar_close_ms) AS prev_state_key,

  -- Helpful: how long since previous block (ms)
  (bar_close_ms - LAG(bar_close_ms) OVER (PARTITION BY sym ORDER BY bar_close_ms)) AS delta_ms

FROM v_ovc_min_events_norm n;


/* ----------------------------------------------------------------------------
C) Pattern outcomes (bucketed performance stats)
---------------------------------------------------------------------------- */
CREATE OR REPLACE VIEW v_pattern_outcomes_v01 AS
SELECT
  sym,
  block4h,
  block2h,

  -- bucket dimensions (v0.1)
  state_key,
  trend_tag,
  struct_state,
  space_tag,
  bias_mode,
  bias_dir,
  perm_state,
  play,
  pred_dir,
  timebox,

  tradeable,
  ready,

  COUNT(*)                                  AS n,
  AVG(ret)                                  AS avg_ret,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ret) AS med_ret,
  AVG(rng)                                  AS avg_rng,
  AVG(body)                                 AS avg_body,
  AVG(ABS(ret))                             AS avg_abs_ret,

  -- winrate: ret > 0
  AVG(CASE WHEN ret > 0 THEN 1.0 ELSE 0.0 END) AS winrate,

  -- alignment: pred_dir vs realized dir (only meaningful if pred_dir set)
  AVG(
    CASE
      WHEN pred_dir IS NULL THEN NULL
      WHEN pred_dir = 'UP'   AND dir =  1 THEN 1.0
      WHEN pred_dir = 'DOWN' AND dir = -1 THEN 1.0
      WHEN pred_dir = 'NEUTRAL' AND dir = 0 THEN 1.0
      ELSE 0.0
    END
  ) AS pred_alignment_rate

FROM v_ovc_min_events_norm
GROUP BY
  sym, block4h, block2h,
  state_key, trend_tag, struct_state, space_tag,
  bias_mode, bias_dir, perm_state,
  play, pred_dir, timebox,
  tradeable, ready;


/* ----------------------------------------------------------------------------
D) Transition stats (prev_state_key -> state_key)
---------------------------------------------------------------------------- */
CREATE OR REPLACE VIEW v_transition_stats_v01 AS
WITH x AS (
  SELECT
    sym,
    block4h,
    block2h,
    timebox,
    bar_close_ms,
    prev_state_key,
    state_key,
    tradeable,
    ready
  FROM v_ovc_min_events_seq
  WHERE prev_state_key IS NOT NULL
)
SELECT
  sym,
  block4h,
  block2h,
  timebox,
  tradeable,
  ready,

  prev_state_key,
  state_key,

  COUNT(*) AS n,

  -- conditional probability of next given prev within these slices
  COUNT(*)::double precision
  / NULLIF(SUM(COUNT(*)) OVER (
      PARTITION BY sym, block4h, block2h, timebox, tradeable, ready, prev_state_key
    ), 0) AS p_next_given_prev

FROM x
GROUP BY
  sym, block4h, block2h, timebox, tradeable, ready, prev_state_key, state_key;


/* ----------------------------------------------------------------------------
E) Session heatmap (performance by time segmentation)
---------------------------------------------------------------------------- */
CREATE OR REPLACE VIEW v_session_heatmap_v01 AS
SELECT
  sym,
  block4h,
  block2h,
  tradeable,
  ready,

  COUNT(*) AS n,
  AVG(ret) AS avg_ret,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ret) AS med_ret,
  AVG(CASE WHEN ret > 0 THEN 1.0 ELSE 0.0 END) AS winrate,
  AVG(rng) AS avg_rng,
  AVG(body) AS avg_body

FROM v_ovc_min_events_norm
GROUP BY
  sym, block4h, block2h, tradeable, ready;


/* ----------------------------------------------------------------------------
F) Data quality dashboard (gaps, readiness, empties)
---------------------------------------------------------------------------- */

-- F1) Missing blocks per day (expects 12 blocks/day; tune for weekends/market closures later)
CREATE OR REPLACE VIEW v_data_quality_missing_blocks_v01 AS
WITH daily AS (
  SELECT
    sym,
    date_ny,
    COUNT(*) AS blocks_seen,
    COUNT(*) FILTER (WHERE ready = 0) AS blocks_ready0,
    COUNT(*) FILTER (WHERE tradeable = 0) AS blocks_tradeable0
  FROM v_ovc_min_events_norm
  GROUP BY sym, date_ny
)
SELECT
  sym,
  date_ny,
  blocks_seen,
  12 - blocks_seen AS blocks_missing_assuming_12,
  blocks_ready0,
  blocks_tradeable0
FROM daily;

-- F2) Empty-rate for key fields (to spot systematic non-population)
CREATE OR REPLACE VIEW v_data_quality_empty_rates_v01 AS
SELECT
  sym,
  COUNT(*) AS n,

  AVG(CASE WHEN state_tag   IS NULL THEN 1.0 ELSE 0.0 END) AS p_state_tag_null,
  AVG(CASE WHEN value_tag   IS NULL THEN 1.0 ELSE 0.0 END) AS p_value_tag_null,
  AVG(CASE WHEN trend_tag   IS NULL THEN 1.0 ELSE 0.0 END) AS p_trend_tag_null,
  AVG(CASE WHEN struct_state IS NULL THEN 1.0 ELSE 0.0 END) AS p_struct_state_null,
  AVG(CASE WHEN space_tag   IS NULL THEN 1.0 ELSE 0.0 END) AS p_space_tag_null,

  AVG(CASE WHEN bias_mode   IS NULL THEN 1.0 ELSE 0.0 END) AS p_bias_mode_null,
  AVG(CASE WHEN bias_dir    IS NULL THEN 1.0 ELSE 0.0 END) AS p_bias_dir_null,
  AVG(CASE WHEN perm_state  IS NULL THEN 1.0 ELSE 0.0 END) AS p_perm_state_null,
  AVG(CASE WHEN play        IS NULL THEN 1.0 ELSE 0.0 END) AS p_play_null,
  AVG(CASE WHEN pred_dir    IS NULL THEN 1.0 ELSE 0.0 END) AS p_pred_dir_null,
  AVG(CASE WHEN timebox     IS NULL THEN 1.0 ELSE 0.0 END) AS p_timebox_null,

  AVG(CASE WHEN build_id    IS NULL THEN 1.0 ELSE 0.0 END) AS p_build_id_null,
  AVG(CASE WHEN source      IS NULL THEN 1.0 ELSE 0.0 END) AS p_source_null

FROM v_ovc_min_events_norm
GROUP BY sym;

-- F3) Basic sanity checks (range/body consistency, impossible values)
CREATE OR REPLACE VIEW v_data_quality_sanity_v01 AS
SELECT
  sym,
  COUNT(*) AS n,

  -- rng should be >= 0
  COUNT(*) FILTER (WHERE rng < 0) AS n_rng_negative,

  -- body should be >= 0
  COUNT(*) FILTER (WHERE body < 0) AS n_body_negative,

  -- price sanity: h>=max(o,c,l) and l<=min(o,c,h)
  COUNT(*) FILTER (WHERE h < GREATEST(o,c,l) OR l > LEAST(o,c,h)) AS n_ohlc_inconsistent,

  -- dir sanity vs o/c
  COUNT(*) FILTER (
    WHERE (c > o AND dir <>  1)
       OR (c < o AND dir <> -1)
       OR (c = o AND dir <>  0)
  ) AS n_dir_inconsistent,

  -- ready/tradeable sanity (optional: tradeable implies ready)
  COUNT(*) FILTER (WHERE tradeable = 1 AND ready = 0) AS n_tradeable_but_not_ready

FROM v_ovc_min_events_norm
GROUP BY sym;


/* ----------------------------------------------------------------------------
OPTIONAL: Materialized views for speed (only if volume grows)
----------------------------------------------------------------------------
-- CREATE MATERIALIZED VIEW mv_pattern_outcomes_v01 AS SELECT * FROM v_pattern_outcomes_v01;
-- REFRESH MATERIALIZED VIEW mv_pattern_outcomes_v01;
============================================================================ */


DoD (for this deliverable)

 State bucketing formula state_key is explicit and frozen in SQL

 Sequencing rule is explicit (PARTITION BY sym ORDER BY bar_close_ms)

 Pattern outcomes, transitions, heatmap, and quality views are fully specified

 Index spec included for performance