-- QA validation pack (legacy wrapper)
-- This wrapper runs the core pack only. The derived pack is executed
-- conditionally by src/validate_day.py when derived views exist.

\i sql/qa_validation_pack_core.sql
