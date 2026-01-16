-- 1) Tables exist
select to_regclass('ovc.ovc_blocks_v01.1_min') as min_table;
select to_regclass('ovc.ovc_run_reports_v01') as run_reports_table;

-- 2) Views compile
select count(*) from ovc.v_ovc_min_events_norm;
select count(*) from ovc.v_ovc_min_events_seq;
select count(*) from ovc.v_pattern_outcomes_v01;
select count(*) from ovc.v_transition_stats_v01;
select count(*) from ovc.v_session_heatmap_v01;
select count(*) from ovc.v_data_quality_ohlc_basic;

-- 3) State key sanity (non-empty)
select count(*) as missing_state_key
from ovc.ovc_blocks_v01.1_min
where state_key is null or length(state_key) = 0;

-- 4) Enum sanity
select bias_dir, count(*) from ovc.ovc_blocks_v01.1_min group by bias_dir;
select pred_dir, count(*) from ovc.ovc_blocks_v01.1_min group by pred_dir;
