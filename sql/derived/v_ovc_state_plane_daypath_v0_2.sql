-- =============================================================================
-- VIEW: derived.v_ovc_state_plane_daypath_v0_2
-- =============================================================================
-- Daily trajectory summaries for the state plane (A-L path metrics).
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS derived;

DROP VIEW IF EXISTS derived.v_ovc_state_plane_daypath_v0_2;

CREATE VIEW derived.v_ovc_state_plane_daypath_v0_2 AS
WITH ordered AS (
    SELECT
        sp.*,
        LAG(sp.x_energy) OVER (
            PARTITION BY sp.sym, sp.date_ny
            ORDER BY sp.bar_close_ms
        ) AS prev_x,
        LAG(sp.y_shift) OVER (
            PARTITION BY sp.sym, sp.date_ny
            ORDER BY sp.bar_close_ms
        ) AS prev_y
    FROM derived.v_ovc_state_plane_v0_2 sp
),
steps AS (
    SELECT
        o.*,
        CASE
            WHEN o.prev_x IS NULL OR o.prev_y IS NULL THEN NULL
            WHEN o.x_energy IS NULL OR o.y_shift IS NULL THEN NULL
            ELSE SQRT(POWER(o.x_energy - o.prev_x, 2) + POWER(o.y_shift - o.prev_y, 2))
        END AS step_distance,
        FIRST_VALUE(o.x_energy) OVER (
            PARTITION BY o.sym, o.date_ny
            ORDER BY o.bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_x,
        FIRST_VALUE(o.y_shift) OVER (
            PARTITION BY o.sym, o.date_ny
            ORDER BY o.bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_y,
        LAST_VALUE(o.x_energy) OVER (
            PARTITION BY o.sym, o.date_ny
            ORDER BY o.bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_x,
        LAST_VALUE(o.y_shift) OVER (
            PARTITION BY o.sym, o.date_ny
            ORDER BY o.bar_close_ms
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_y
    FROM ordered o
),
daily AS (
    SELECT
        sym,
        date_ny,
        MIN(bar_close_ms) AS first_bar_close_ms,
        MAX(bar_close_ms) AS last_bar_close_ms,
        COUNT(*) AS block_count,
        SUM(step_distance) AS path_length,
        MIN(first_x) AS first_x,
        MIN(first_y) AS first_y,
        MIN(last_x) AS last_x,
        MIN(last_y) AS last_y,
        SUM(CASE WHEN quadrant_id IN ('Q3', 'Q4') THEN 1 ELSE 0 END) AS jump_count,
        STRING_AGG(COALESCE(quadrant_id, 'NA'), ' ' ORDER BY bar_close_ms) AS quadrant_string,
        MIN(threshold_pack_id) AS threshold_pack_id,
        MIN(threshold_pack_version) AS threshold_pack_version,
        MIN(threshold_pack_hash) AS threshold_pack_hash
    FROM steps
    GROUP BY sym, date_ny
)
SELECT
    d.sym,
    d.date_ny,
    d.first_bar_close_ms,
    d.last_bar_close_ms,
    d.block_count,
    d.path_length,
    CASE
        WHEN d.first_x IS NULL OR d.first_y IS NULL OR d.last_x IS NULL OR d.last_y IS NULL THEN NULL
        ELSE SQRT(POWER(d.last_x - d.first_x, 2) + POWER(d.last_y - d.first_y, 2))
    END AS net_displacement,
    CASE
        WHEN d.path_length IS NULL OR d.path_length = 0 THEN NULL
        WHEN d.first_x IS NULL OR d.first_y IS NULL OR d.last_x IS NULL OR d.last_y IS NULL THEN NULL
        ELSE SQRT(POWER(d.last_x - d.first_x, 2) + POWER(d.last_y - d.first_y, 2)) / d.path_length
    END AS efficiency,
    d.jump_count,
    d.quadrant_string,
    d.threshold_pack_id,
    d.threshold_pack_version,
    d.threshold_pack_hash,
    'v0_2' AS state_plane_version
FROM daily d;
