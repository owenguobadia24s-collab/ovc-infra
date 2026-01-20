-- =============================================================================
-- View: v_path1_evidence_res_v1_0
-- Purpose: JOIN frozen RES-v1.0 score with Option C outcomes for evidence runs
-- Governance: READ-ONLY view. No score modification. No computed signals.
-- =============================================================================

-- FROZEN SCORE VERSION: RES-v1.0
-- OUTCOME SOURCE: derived.v_ovc_c_outcomes_v0_1

CREATE OR REPLACE VIEW derived.v_path1_evidence_res_v1_0 AS
SELECT
    -- Identifiers
    s.block_id,
    s.sym,
    s.bar_close_ms,
    
    -- Score raw value (RES-v1.0, frozen)
    s.res_score AS res_v1_0_raw,
    
    -- Outcome fields (as-is from Option C)
    o.outcome_dir,
    o.outcome_rng,
    o.outcome_ret,
    o.outcome_category,
    o.next_block_id,
    o.next_bar_close_ms

FROM derived.v_ovc_b_scores_res_v1_0 s
LEFT JOIN derived.v_ovc_c_outcomes_v0_1 o
    ON s.block_id = o.block_id
    AND s.sym = o.sym;

-- =============================================================================
-- GOVERNANCE NOTES:
-- - This view is READ-ONLY
-- - No thresholds, labels, signals, or binning applied
-- - Score value passed through unchanged from frozen source
-- - Outcome fields passed through unchanged from Option C
-- =============================================================================

COMMENT ON VIEW derived.v_path1_evidence_res_v1_0 IS 
'Path 1 Evidence: RES-v1.0 score joined with Option C outcomes. Read-only, no transformations.';
