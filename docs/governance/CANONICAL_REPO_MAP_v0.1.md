CANONICAL REPO MAP v0.1 (DRAFT)
Purpose
Single authoritative coordinate map of the OVC repository.
Records existence, location, role, option ownership, and authority alignment.
Does not resolve contradictions.

Authority Model
Repo = physical existence
CURRENT_STATE = declared truth
Maze = conceptual/navigation intent
Legend
Role:

LAW
CONTRACT
WORKFLOW
CODE
ARTIFACT
LEDGER
MAP
LEGACY
UNKNOWN
Status:

ALIGNED
CONTRADICTED
CLAIMED-BUT-MISSING
EXISTS-BUT-UNCLASSIFIED
UNKNOWN
Option:

A | B | C | D | GOV | QA | MULTI | UNKNOWN
Authority:

REPO
CURRENT_STATE
MAZE
MULTIPLE
Canonical Map Entries
| Path | Role | Option | Authority | Status | Notes |
|---|---|---|---|---|---|
| 00_REPO_MAZE.md | MAP | GOV | MAZE | ALIGNED | Maze=PRESENT; CURRENT_STATE=ABSENT; Repo=PRESENT |
| ANCHOR_CATALOG.md | MAP | GOV | MAZE | ALIGNED | Maze=PRESENT; CURRENT_STATE=ABSENT; Repo=PRESENT |
| ROOM__WORKFLOWS.md | MAP | GOV | MAZE | CONTRADICTED | Contains claim “File count: 0” for .github/workflows/; Repo contradicts (Repo has 13 workflow files) |
| CURRENT_STATE_A_TO_D.md | MAP | GOV | CURRENT_STATE | CONTRADICTED | CURRENT_STATE=PRESENT; Repo=PRESENT; Contains multiple claims contradicted by Repo (see Unresolved Contradictions Index) |
| CURRENT_STATE_DEP_GRAPH.md | MAP | GOV | CURRENT_STATE | ALIGNED | CURRENT_STATE=PRESENT; Repo=PRESENT |
| CURRENT_STATE_INVARIANTS.md | MAP | GOV | CURRENT_STATE | CONTRADICTED | CURRENT_STATE=PRESENT; Repo=PRESENT; Contains claims contradicted by Repo (e.g., migration ledger, PATH2 contract path) |
| CURRENT_STATE_TRUST_MAP.md | MAP | GOV | CURRENT_STATE | ALIGNED | CURRENT_STATE=PRESENT; Repo=PRESENT |
| .github/workflows/ | UNKNOWN | UNKNOWN | MAZE | CONTRADICTED | Maze claims “File count: 0”; Repo contains 13 workflow files |
| path1_evidence.yml | WORKFLOW | UNKNOWN | MAZE | CLAIMED-BUT-MISSING | Maze path uses github/... (no leading dot); Repo uses .github/... |
| path1_evidence_queue.yml | WORKFLOW | UNKNOWN | MAZE | CLAIMED-BUT-MISSING | Maze path uses github/... (no leading dot); Repo uses .github/... |
| backfill.yml | WORKFLOW | A | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: A (CURRENT_STATE by name)]; Repo path backfill.yml |
| backfill_m15.yml | WORKFLOW | A | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: A (CURRENT_STATE by name)]; Repo path backfill_m15.yml |
| backfill_then_validate.yml | WORKFLOW | B | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: B (CURRENT_STATE by name)]; Repo path backfill_then_validate.yml |
| ovc_full_ingest.yml | WORKFLOW | A | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: A (CURRENT_STATE by name)]; Repo path ovc_full_ingest.yml |
| ovc_option_c_schedule.yml | WORKFLOW | C | CURRENT_STATE | CONTRADICTED | CURRENT_STATE claims “BROKEN” due to run_option_c.sh; Repo asserts it references run_option_c.sh and it exists (disagreement recorded) |
| path1_evidence.yml | WORKFLOW | D | MULTIPLE | ALIGNED | Maze=PRESENT; CURRENT_STATE=PRESENT; Repo=PRESENT |
| path1_evidence_queue.yml | WORKFLOW | D | MULTIPLE | ALIGNED | Maze=PRESENT; CURRENT_STATE=PRESENT; Repo=PRESENT |
| path1_replay_verify.yml | WORKFLOW | D | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: D (CURRENT_STATE by name)]; Repo path path1_replay_verify.yml |
| ci_workflow_sanity.yml | WORKFLOW | QA | CURRENT_STATE | ALIGNED | [Role: WORKFLOW][Option: QA (CURRENT_STATE by name)]; Repo path ci_workflow_sanity.yml |
| ci_pytest.yml | WORKFLOW | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Absent from Maze and CURRENT_STATE as a referenced workflow name/path; exists in Repo |
| ci_schema_check.yml | WORKFLOW | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Absent from Maze and CURRENT_STATE as a referenced workflow name/path; exists in Repo |
| main.yml | WORKFLOW | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Absent from Maze and CURRENT_STATE; exists in Repo |
| notion_sync.yml | WORKFLOW | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Absent from Maze and CURRENT_STATE; exists in Repo |
| index.ts | CODE | A | CURRENT_STATE | ALIGNED | [Role: CODE][Option: A (CURRENT_STATE)] |
| backfill_oanda_2h_checkpointed.py | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Repo has no scripts/backfill/ directory |
| backfill_oanda_m15_checkpointed.py | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Repo has no scripts/backfill/ directory |
| backfill_oanda_2h_checkpointed.py | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Present in repo; not referenced by CURRENT_STATE under this path |
| run_option_c.sh | CODE | C | CURRENT_STATE | ALIGNED | [Role: CODE][Option: C (CURRENT_STATE)] |
| run_option_c.sh | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Mentioned by CURRENT_STATE (as referenced-by-schedule claim); not present in repo |
| build_evidence_pack_v0_2.py | CODE | D | CURRENT_STATE | ALIGNED | [Role: CODE][Option: D (CURRENT_STATE)] |
| run_evidence_queue.py | CODE | D | CURRENT_STATE | ALIGNED | [Role: CODE][Option: D (CURRENT_STATE)] |
| run_evidence_range.py | CODE | D | CURRENT_STATE | ALIGNED | [Role: CODE][Option: D (CURRENT_STATE)] |
| run_replay_verification.py | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Repo path is run_replay_verification.py |
| run_replay_verification.py | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | [Role: CODE][Option: UNKNOWN] |
| run_seal_manifests.py | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Repo path is run_seal_manifests.py |
| run_seal_manifests.py | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | [Role: CODE][Option: UNKNOWN] |
| applied_migrations.json | LEDGER | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | [Role: LEDGER][Option: UNKNOWN]; Referenced by ci_schema_check.yml |
| PATH2_CONTRACT_v1_0.md | UNKNOWN | UNKNOWN | CURRENT_STATE | CLAIMED-BUT-MISSING | Repo path is PATH2_CONTRACT_v1_0.md |
| PATH2_CONTRACT_v1_0.md | CONTRACT | MULTI | MAZE | ALIGNED | [Role: CONTRACT][Option: QA/Multi (Maze lists under QA_GOVERNANCE and OPT_A)] |
| inventory.txt | ARTIFACT | QA | MAZE | ALIGNED | [Role: ARTIFACT][Option: QA (Maze lists under QA_GOVERNANCE)] |
| patch_m15_raw_20260122.sql | CODE | D | MULTIPLE | ALIGNED | [Role: CODE][Option: D (CURRENT_STATE + Maze A↔D boundary)] |
| backbone_2h.csv | ARTIFACT | D | MAZE | ALIGNED | [Role: ARTIFACT][Option: D (Maze A↔D boundary)] |
| CHANGELOG_overlays_v0_3.md | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Exists in Repo; absent from both Maze and CURRENT_STATE |
| CHANGELOG_overlays_v0_3_hardening.md | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Exists in Repo; absent from both Maze and CURRENT_STATE |
| CHANGELOG_evidence_pack_provenance.md | UNKNOWN | UNKNOWN | REPO | EXISTS-BUT-UNCLASSIFIED | Exists in Repo; absent from both Maze and CURRENT_STATE |
Unresolved Contradictions (Index)
.github/workflows/
path1_evidence.yml
path1_evidence_queue.yml
backfill_oanda_2h_checkpointed.py
backfill_oanda_m15_checkpointed.py
run_option_c.sh
ci_pytest.yml
applied_migrations.json
run_replay_verification.py
run_seal_manifests.py
PATH2_CONTRACT_v1_0.md
Unclassified Reality (Index)
ci_pytest.yml
ci_schema_check.yml
main.yml
notion_sync.yml
applied_migrations.json
run_replay_verification.py
run_seal_manifests.py
CHANGELOG_overlays_v0_3.md
CHANGELOG_overlays_v0_3_hardening.md
CHANGELOG_evidence_pack_provenance.md
Unknowns & Gaps
UNKNOWN: Commit SHA / machine build identifier for CURRENT_STATE freeze “2026-01-23” (CURRENT_STATE docs provide a date but no commit ref in the reviewed files).
UNKNOWN: Commit SHA for inventory.txt snapshot; cannot prove whether divergences from current repo are due to later changes vs snapshot errors.
UNKNOWN: Generation method/version for Maze file counts and workflow discovery (“none found”); only the Maze outputs were provided, not the generator inputs/commands.
UNKNOWN: Any non-repo identifiers in CURRENT_STATE (e.g., tv/YYYY-MM-DD/..., reports/path1/evidence/runs/<run_id>/) are not resolvable as physical repo entities without an explicit mapping artifact.
