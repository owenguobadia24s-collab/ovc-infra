---
type: repo-maze-option
tags: [ovc, repo, maze, option]
---

# OPT_D__PATHS_BRIDGE

## Definition
Path1 evidence runner + Path2 determinism mechanics + evidence pack orchestration.

## Anchors (real repo paths)
- `reports/path1/evidence/README.md`
- `reports/path1/evidence/INDEX.md`
- `scripts/path1_replay/README.md`
- `docs/history/path1/README.md`
- `docs/runbooks/path1_evidence_runner_test.md`
- `docs/history/path1/EVIDENCE_RUNS_HOWTO.md`
- `docs/history/path1/PATH1_EVIDENCE_PROTOCOL_v1_0.md`
- `reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md`
- `github/workflows/path1_evidence.yml`
- `github/workflows/path1_evidence_queue.yml`
- `sql/path1/db_patches/patch_create_evidence_views_20260120.sql`
- `sql/path1/evidence/v_path1_evidence_dis_v1_1.sql`
- `sql/path1/evidence/v_path1_evidence_lid_v1_0.sql`
- `sql/path1/evidence/v_path1_evidence_res_v1_0.sql`
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql`
- `sql/path1/studies/lid_vs_outcomes_bucketed.sql`
- `sql/path1/studies/res_vs_outcomes_bucketed.sql`
- `PATH1_EXECUTION_MODEL.md`

## Key workflows
- none found

## Inputs
- `docs/specs/system/research_query_pack_v0.1.md`
- `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`
- `sql/path1/db_patches/patch_m15_raw_20260122.sql`

## Outputs
- `reports/path1/evidence/README.md`
- `reports/path1/evidence/INDEX.md`
- `reports/path1/evidence/EVIDENCE_RUN_TEMPLATE.md`
- `sql/path1/studies/dis_vs_outcomes_bucketed.sql`
- `sql/path1/studies/lid_vs_outcomes_bucketed.sql`

## Rooms
- [[ROOM__DOCS]]
- [[ROOM__REPORTS]]
- [[ROOM__SQL]]

## Spine
- [[OPT_A__CANONICAL_INGEST]] -> [[OPT_D__PATHS_BRIDGE]] -> [[OPT_B__DERIVED_LAYERS]] -> [[OPT_C__OUTCOMES_EVAL]]

## Boundary Law
- [[A_D_BOUNDARY]]
