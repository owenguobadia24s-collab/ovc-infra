# Pine Export Consistency Notes

This update aligns the full Pine indicator export block with the MIN contract v0.1.1 while keeping existing visuals and logic intact.

Changes
- MIN export keys/order now match the frozen v0.1.1 contract (scheme_min and block_id/block2h/block4h, derived fields, bool_01 tradeable/ready).
- Export string sanitization uses the same separator rules as the MIN module.
- Added a toggleable Export Readiness view to surface missing/na critical fields and a contract/scheme/block_id preview.

Export Readiness toggle
- Use the `Show Export Readiness` checkbox in the `EXPORT (OVC_LOG_V0.1)` group.
- The view shows `ready`, any missing required fields, and `contract` + `scheme_min` + `block_id` preview.
