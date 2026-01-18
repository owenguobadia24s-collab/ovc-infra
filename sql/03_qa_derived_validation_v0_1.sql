-- OVC Option B.2: QA schema extension for derived feature validation
-- Migration: 03_qa_derived_validation_v0_1.sql
-- Version: v0.1
-- 
-- This migration adds the derived_validation_run table to track C1/C2
-- validation results, complementing the existing ovc_qa.validation_run
-- table used for B-layer OHLC validation.

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS ovc_qa;

-- Derived validation run tracking
CREATE TABLE IF NOT EXISTS ovc_qa.derived_validation_run (
    run_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    symbol TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Coverage counts
    b_block_count INTEGER,
    c1_row_count INTEGER,
    c2_row_count INTEGER,
    
    -- Integrity check results
    coverage_parity BOOLEAN,
    c1_duplicates INTEGER DEFAULT 0,
    c2_duplicates INTEGER DEFAULT 0,
    c2_window_spec_valid BOOLEAN,
    
    -- Determinism check
    determinism_sample_size INTEGER,
    determinism_mismatches INTEGER DEFAULT 0,
    
    -- TV comparison (optional)
    tv_comparison_enabled BOOLEAN DEFAULT FALSE,
    tv_reference_available BOOLEAN DEFAULT FALSE,
    tv_matched_blocks INTEGER DEFAULT 0,
    
    -- Overall status
    status TEXT NOT NULL,  -- PASS, FAIL, PASS_WITH_WARNINGS
    errors JSONB DEFAULT '[]'::jsonb,
    warnings JSONB DEFAULT '[]'::jsonb
);

-- Index for querying by symbol and date range
CREATE INDEX IF NOT EXISTS idx_derived_validation_symbol_dates 
ON ovc_qa.derived_validation_run (symbol, start_date, end_date);

-- Index for querying by status
CREATE INDEX IF NOT EXISTS idx_derived_validation_status 
ON ovc_qa.derived_validation_run (status);

COMMENT ON TABLE ovc_qa.derived_validation_run IS 
'Tracks validation results for C1/C2 derived feature packs (Option B.2)';

COMMENT ON COLUMN ovc_qa.derived_validation_run.coverage_parity IS 
'TRUE if B-layer block count equals C1 and C2 row counts';

COMMENT ON COLUMN ovc_qa.derived_validation_run.c2_window_spec_valid IS 
'TRUE if all C2 rows have valid window_spec with required components';

COMMENT ON COLUMN ovc_qa.derived_validation_run.determinism_mismatches IS 
'Number of blocks where recomputed C1 values differ from stored values';
