-- OVC State Plane Threshold Pack (v0.2)
-- Migration: 06_state_plane_threshold_pack_v0_2.sql
-- Purpose: Register default threshold pack for derived.v_ovc_state_plane_v0_2
--
-- Usage:
--   psql $NEON_DSN -f sql/06_state_plane_threshold_pack_v0_2.sql

-- ============================================================================
-- INSERT: Threshold Pack (immutable)
-- ============================================================================

INSERT INTO ovc_cfg.threshold_pack (
    pack_id,
    pack_version,
    scope,
    symbol,
    timeframe,
    config_json,
    config_hash,
    status,
    created_by,
    note
)
VALUES (
    'state_plane_v0_2_default',
    1,
    'GLOBAL',
    NULL,
    NULL,
    '{"columns":{"x_energy":{"body_ratio":"body_ratio","directional_efficiency":"directional_efficiency","rng_intensity":"rng_rank_6"},"y_shift":{"momentum_state":"c3_momentum_state","trend_bias":"c3_trend_bias"}},"scope":"state_plane_v0_2","source_views":["derived.v_ovc_c1_features_v0_1","derived.v_ovc_c2_features_v0_1","derived.v_ovc_c3_features_v0_1"],"thresholds":{"E_hi":0.6,"S_hi":0.35},"version":"v0.2","weights":{"x_energy":{"body_ratio":0.35,"directional_efficiency":0.2,"rng_rank_6":0.45},"y_shift":{"momentum_state":0.5,"trend_bias":0.5}},"y_map":{"momentum_state":{"accelerating":-1,"decelerating":0.5,"reversing":1,"steady":0},"trend_bias":{"fading":0.5,"nascent":-0.5,"neutral":0,"sustained":-1}}}'::jsonb,
    '2e1f8d1476534bd6f94526c7db80c48541cc76bdbe8315f8c95e1548a50461e2',
    'ACTIVE',
    'migration',
    'Default thresholds for state_plane_v0_2'
)
ON CONFLICT (pack_id, pack_version) DO NOTHING;

-- ============================================================================
-- INSERT/UPSERT: Active Pointer
-- ============================================================================

INSERT INTO ovc_cfg.threshold_pack_active (
    pack_id,
    scope,
    symbol,
    timeframe,
    active_version,
    active_hash,
    updated_at
)
VALUES (
    'state_plane_v0_2_default',
    'GLOBAL',
    '',
    '',
    1,
    '2e1f8d1476534bd6f94526c7db80c48541cc76bdbe8315f8c95e1548a50461e2',
    NOW()
)
ON CONFLICT (pack_id, scope, symbol, timeframe)
DO UPDATE SET
    active_version = EXCLUDED.active_version,
    active_hash = EXCLUDED.active_hash,
    updated_at = NOW();
