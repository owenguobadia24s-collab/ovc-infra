-- =============================================================================
-- VIEW: derived.v_ovc_state_plane_v0_2
-- =============================================================================
-- Deterministic state plane coordinates derived from canonical L1/L2/L3 features.
-- Uses threshold pack config (ovc_cfg.threshold_pack) for all thresholds/weights.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS derived;

DROP VIEW IF EXISTS derived.v_ovc_state_plane_v0_2;

CREATE VIEW derived.v_ovc_state_plane_v0_2 AS
WITH active_pack AS (
    SELECT
        p.pack_id,
        p.pack_version,
        p.config_json,
        p.config_hash
    FROM ovc_cfg.threshold_pack_active a
    INNER JOIN ovc_cfg.threshold_pack p
        ON p.pack_id = a.pack_id
        AND p.pack_version = a.active_version
    WHERE a.pack_id = 'state_plane_v0_2_default'
      AND a.scope = 'GLOBAL'
      AND a.symbol = ''
      AND a.timeframe = ''
),
config AS (
    SELECT
        pack_id,
        pack_version,
        config_hash,
        (config_json->'thresholds'->>'E_hi')::DOUBLE PRECISION AS e_hi,
        (config_json->'thresholds'->>'S_hi')::DOUBLE PRECISION AS s_hi,
        (config_json->'weights'->'x_energy'->>'rng_rank_6')::DOUBLE PRECISION AS w_rng,
        (config_json->'weights'->'x_energy'->>'body_ratio')::DOUBLE PRECISION AS w_body,
        (config_json->'weights'->'x_energy'->>'directional_efficiency')::DOUBLE PRECISION AS w_eff,
        (config_json->'weights'->'y_shift'->>'trend_bias')::DOUBLE PRECISION AS w_trend,
        (config_json->'weights'->'y_shift'->>'momentum_state')::DOUBLE PRECISION AS w_momentum,
        (config_json->'y_map'->'trend_bias'->>'sustained')::DOUBLE PRECISION AS tb_sustained,
        (config_json->'y_map'->'trend_bias'->>'nascent')::DOUBLE PRECISION AS tb_nascent,
        (config_json->'y_map'->'trend_bias'->>'neutral')::DOUBLE PRECISION AS tb_neutral,
        (config_json->'y_map'->'trend_bias'->>'fading')::DOUBLE PRECISION AS tb_fading,
        (config_json->'y_map'->'momentum_state'->>'accelerating')::DOUBLE PRECISION AS ms_accelerating,
        (config_json->'y_map'->'momentum_state'->>'steady')::DOUBLE PRECISION AS ms_steady,
        (config_json->'y_map'->'momentum_state'->>'decelerating')::DOUBLE PRECISION AS ms_decelerating,
        (config_json->'y_map'->'momentum_state'->>'reversing')::DOUBLE PRECISION AS ms_reversing
    FROM active_pack
),
base AS (
    SELECT
        c1.block_id,
        c1.sym,
        c2.date_ny,
        c2.block2h,
        c2.bar_close_ms,
        c2.rng_rank_6,
        c1.body_ratio,
        c1.directional_efficiency,
        c3.l3_trend_bias,
        c3.l3_momentum_state
    FROM derived.v_ovc_l1_features_v0_1 c1
    INNER JOIN derived.v_ovc_l2_features_v0_1 c2
        ON c1.block_id = c2.block_id
    LEFT JOIN derived.v_ovc_l3_features_v0_1 c3
        ON c1.block_id = c3.block_id
),
scored AS (
    SELECT
        b.*,
        cfg.pack_id AS threshold_pack_id,
        cfg.pack_version AS threshold_pack_version,
        cfg.config_hash AS threshold_pack_hash,
        cfg.e_hi,
        cfg.s_hi,
        cfg.w_rng,
        cfg.w_body,
        cfg.w_eff,
        cfg.w_trend,
        cfg.w_momentum,
        CASE
            WHEN b.l3_trend_bias IS NULL THEN NULL
            WHEN b.l3_trend_bias = 'sustained' THEN cfg.tb_sustained
            WHEN b.l3_trend_bias = 'nascent' THEN cfg.tb_nascent
            WHEN b.l3_trend_bias = 'neutral' THEN cfg.tb_neutral
            WHEN b.l3_trend_bias = 'fading' THEN cfg.tb_fading
            ELSE NULL
        END AS trend_bias_score,
        CASE
            WHEN b.l3_momentum_state IS NULL THEN NULL
            WHEN b.l3_momentum_state = 'accelerating' THEN cfg.ms_accelerating
            WHEN b.l3_momentum_state = 'steady' THEN cfg.ms_steady
            WHEN b.l3_momentum_state = 'decelerating' THEN cfg.ms_decelerating
            WHEN b.l3_momentum_state = 'reversing' THEN cfg.ms_reversing
            ELSE NULL
        END AS momentum_score,
        CASE
            WHEN b.rng_rank_6 IS NULL
              OR b.body_ratio IS NULL
              OR b.directional_efficiency IS NULL THEN NULL
            WHEN cfg.w_rng IS NULL
              OR cfg.w_body IS NULL
              OR cfg.w_eff IS NULL THEN NULL
            WHEN (cfg.w_rng + cfg.w_body + cfg.w_eff) = 0 THEN NULL
            ELSE GREATEST(0.0, LEAST(1.0,
                (cfg.w_rng * GREATEST(0.0, LEAST(1.0, b.rng_rank_6)) +
                 cfg.w_body * GREATEST(0.0, LEAST(1.0, b.body_ratio)) +
                 cfg.w_eff * GREATEST(0.0, LEAST(1.0, ABS(b.directional_efficiency)))
                ) / (cfg.w_rng + cfg.w_body + cfg.w_eff)
            ))
        END AS x_energy
    FROM base b
    CROSS JOIN config cfg
),
with_shift AS (
    SELECT
        s.*,
        CASE
            WHEN s.trend_bias_score IS NULL OR s.momentum_score IS NULL THEN NULL
            WHEN s.w_trend IS NULL OR s.w_momentum IS NULL THEN NULL
            WHEN (s.w_trend + s.w_momentum) = 0 THEN NULL
            ELSE LEAST(1.0, GREATEST(-1.0,
                (s.w_trend * s.trend_bias_score + s.w_momentum * s.momentum_score)
                / (s.w_trend + s.w_momentum)
            ))
        END AS y_shift
    FROM scored s
)
SELECT
    ws.block_id,
    ws.sym,
    ws.date_ny,
    ws.block2h,
    ws.bar_close_ms,
    ws.x_energy,
    ws.y_shift,
    CASE
        WHEN ws.x_energy IS NULL OR ws.y_shift IS NULL OR ws.e_hi IS NULL OR ws.s_hi IS NULL THEN NULL
        WHEN ws.x_energy >= ws.e_hi AND ABS(ws.y_shift) <= ws.s_hi THEN 'Q1'
        WHEN ws.x_energy < ws.e_hi AND ABS(ws.y_shift) <= ws.s_hi THEN 'Q2'
        WHEN ws.x_energy >= ws.e_hi AND ABS(ws.y_shift) > ws.s_hi THEN 'Q3'
        WHEN ws.x_energy < ws.e_hi AND ABS(ws.y_shift) > ws.s_hi THEN 'Q4'
        ELSE NULL
    END AS quadrant_id,
    CASE
        WHEN ws.x_energy IS NULL OR ws.y_shift IS NULL OR ws.e_hi IS NULL OR ws.s_hi IS NULL THEN NULL
        WHEN ws.x_energy >= ws.e_hi AND ABS(ws.y_shift) <= ws.s_hi THEN 'Expansion'
        WHEN ws.x_energy < ws.e_hi AND ABS(ws.y_shift) <= ws.s_hi THEN 'Consolidation'
        WHEN ws.x_energy >= ws.e_hi AND ABS(ws.y_shift) > ws.s_hi THEN 'Reversal'
        WHEN ws.x_energy < ws.e_hi AND ABS(ws.y_shift) > ws.s_hi THEN 'Retracement'
        ELSE NULL
    END AS quadrant_name,
    CASE
        WHEN ws.x_energy IS NULL OR ws.y_shift IS NULL OR ws.e_hi IS NULL OR ws.s_hi IS NULL THEN NULL
        ELSE LEAST(
            ABS(ws.x_energy - ws.e_hi),
            ABS(ABS(ws.y_shift) - ws.s_hi)
        )
    END AS quadrant_confidence,
    ws.threshold_pack_id,
    ws.threshold_pack_version,
    ws.threshold_pack_hash,
    'v0_2' AS state_plane_version,
    jsonb_build_object(
        'threshold_pack_id', ws.threshold_pack_id,
        'source_view_names', jsonb_build_array(
            'derived.v_ovc_l1_features_v0_1',
            'derived.v_ovc_l2_features_v0_1',
            'derived.v_ovc_l3_features_v0_1'
        )
    ) AS state_plane_meta
FROM with_shift ws;
