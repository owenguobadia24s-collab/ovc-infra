/* ============================================================================
OVC Outcomes v0.1 — SQL Spec (Postgres / Neon)

GOAL
- Store realized outcomes in a separate table keyed by block_id
- Provide join views to enrich pattern outcomes and session heatmaps

NOTE
- This spec assumes base MIN table: ovc_min_events
- Assumes normalized view exists: v_ovc_min_events_norm (from Query Pack v0.1)
============================================================================ */

/* ----------------------------------------------------------------------------
1) Outcome table DDL
---------------------------------------------------------------------------- */

CREATE TABLE IF NOT EXISTS ovc_outcomes_v01 (
  -- Identity
  block_id          text PRIMARY KEY,
  sym               text NOT NULL,
  bar_close_ms      bigint NOT NULL,

  -- Outcome computation metadata
  outcome_ver       text NOT NULL,                   -- e.g. "out_v0.1.0"
  window_type       text NOT NULL,                   -- e.g. "NEXT_4H"
  window_n          integer,                         -- optional (for NEXT_N_BARS)
  window_end_ms     bigint NOT NULL,

  -- Excursions (direction-agnostic; stored with your mfe_up/mfe_down names)
  mfe_up            double precision NOT NULL,       -- max(H) - ref_price
  mfe_down          double precision NOT NULL,       -- ref_price - min(L)

  -- Optional adverse excursion fields (nullable in v0.1)
  mae_up            double precision,
  mae_down          double precision,

  -- Close position in window [0..1] (nullable if range=0)
  close_pos         double precision,

  -- Your "next move" stats (nullable until defined everywhere)
  next_ext          double precision,
  next_sd           double precision,

  -- Outcome labels
  outcome_dir       text NOT NULL CHECK (outcome_dir IN ('UP','DOWN','NEUTRAL')),
  hit_invalidation  smallint NOT NULL CHECK (hit_invalidation IN (0,1)),
  hit_target        smallint NOT NULL CHECK (hit_target IN (0,1)),

  -- Audit
  computed_at_ms    bigint NOT NULL,
  source            text NOT NULL,
  note              text
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_outcomes_sym_time
  ON ovc_outcomes_v01 (sym, bar_close_ms);

CREATE INDEX IF NOT EXISTS idx_outcomes_window
  ON ovc_outcomes_v01 (window_type, outcome_ver);


/* ----------------------------------------------------------------------------
2) Join view: MIN + outcomes (row-level enrichment)
---------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW v_ovc_min_with_outcomes_v01 AS
SELECT
  m.*,
  o.outcome_ver,
  o.window_type,
  o.window_end_ms,

  o.mfe_up,
  o.mfe_down,
  o.mae_up,
  o.mae_down,
  o.close_pos,
  o.next_ext,
  o.next_sd,
  o.outcome_dir,
  o.hit_invalidation,
  o.hit_target

FROM v_ovc_min_events_norm m
LEFT JOIN ovc_outcomes_v01 o
  ON o.block_id = m.block_id;


/* ----------------------------------------------------------------------------
3) Pattern outcomes WITH outcomes (aggregated)
---------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW v_pattern_outcomes_with_outcomes_v01 AS
SELECT
  sym,
  block4h,
  block2h,

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

  COUNT(*) AS n,

  -- base performance
  AVG(ret) AS avg_ret,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ret) AS med_ret,
  AVG(CASE WHEN ret > 0 THEN 1.0 ELSE 0.0 END) AS winrate,

  -- prediction alignment
  AVG(
    CASE
      WHEN pred_dir IS NULL THEN NULL
      WHEN pred_dir = 'UP' AND dir = 1 THEN 1.0
      WHEN pred_dir = 'DOWN' AND dir = -1 THEN 1.0
      WHEN pred_dir = 'NEUTRAL' AND dir = 0 THEN 1.0
      ELSE 0.0
    END
  ) AS pred_alignment_rate,

  -- outcome-enriched stats (null-safe: if outcomes missing, these stay null)
  AVG(mfe_up) AS avg_mfe_up,
  AVG(mfe_down) AS avg_mfe_down,
  AVG(close_pos) AS avg_close_pos,

  AVG(CASE WHEN hit_target = 1 THEN 1.0 WHEN hit_target = 0 THEN 0.0 ELSE NULL END) AS p_hit_target,
  AVG(CASE WHEN hit_invalidation = 1 THEN 1.0 WHEN hit_invalidation = 0 THEN 0.0 ELSE NULL END) AS p_hit_invalidation

FROM v_ovc_min_with_outcomes_v01
GROUP BY
  sym, block4h, block2h,
  state_key, trend_tag, struct_state, space_tag,
  bias_mode, bias_dir, perm_state,
  play, pred_dir, timebox,
  tradeable, ready;


/* ----------------------------------------------------------------------------
4) Session heatmap WITH outcomes
---------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW v_session_heatmap_with_outcomes_v01 AS
SELECT
  sym,
  block4h,
  block2h,
  tradeable,
  ready,

  COUNT(*) AS n,

  AVG(ret) AS avg_ret,
  AVG(CASE WHEN ret > 0 THEN 1.0 ELSE 0.0 END) AS winrate,

  AVG(mfe_up) AS avg_mfe_up,
  AVG(mfe_down) AS avg_mfe_down,
  AVG(close_pos) AS avg_close_pos,

  AVG(CASE WHEN hit_target = 1 THEN 1.0 WHEN hit_target = 0 THEN 0.0 ELSE NULL END) AS p_hit_target,
  AVG(CASE WHEN hit_invalidation = 1 THEN 1.0 WHEN hit_invalidation = 0 THEN 0.0 ELSE NULL END) AS p_hit_invalidation

FROM v_ovc_min_with_outcomes_v01
GROUP BY sym, block4h, block2h, tradeable, ready;
