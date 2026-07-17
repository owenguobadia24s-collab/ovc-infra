# OVC R1 Drift Matrix

**Evidence commit:** `59db182dfbdd1eaf467ee91ac79a6bd385697450`

| Governed surface | Declared authority | Repository implementation | Deployed or observed reality | R1 finding |
|---|---|---|---|---|
| A1 canonical table | Operator ruling temporarily tolerates physical semantic legacy but denies it to B/C/D | Worker and backfill write `ovc.ovc_blocks_v01_1_min` | R0: 59,875 rows; semantic columns live | Physical legacy tolerated; downstream semantic use forbidden |
| A2 M15 table | ACTIVE A2 contract | Checkpointed OANDA M15 backfill | R0: 384 rows | AUTHORITATIVE; deployment verified |
| Worker raw archive | A1 contract requires R2 archive | Wrangler binds `RAW_EVENTS` to `ovc-raw-events` | Cloudflare unavailable | UNVERIFIED_DEPLOYMENT |
| Worker run reports | Data-flow canon and DDL define run telemetry | Worker inserts `ended_at`, `meta`; DDL uses `finished_at`, no `meta` | R0: table exists, zero rows | CONFLICTING |
| B C1/C2/C3 views | FROZEN C feature registry | SQL view definitions match declared interface | R0: all three live, 59,875 rows | AUTHORITATIVE |
| B materialized C1/C2 | ACTIVE Option B contract | Python compute plus DDL | Not sampled by R0 | UNVERIFIED_DEPLOYMENT |
| B materialized C3 | FROZEN C3 contract | Script requires threshold pack and scope | Workflow omits both; live table not sampled | CONFLICTING |
| Threshold registry | ACTIVE Option B/C3 contracts | SQL registry plus Python API | R0: both tables live, two rows each | AUTHORITATIVE |
| C required outcomes target | Operator ruling selects B-backed view; governing v1 contract remains DRAFT | `sql/derived/v_ovc_c_outcomes_v0_1.sql` | R0: live, 59,875 rows | Required for new operations; full authority pending contract ratification |
| C legacy outcomes | Historical boundary and eval contract use direct A reads | `sql/option_c_v0_1.sql` creates legacy view | R0: legacy view also live, 59,875 rows | SUPPORTING_LEGACY; no new operations or consumers |
| Option C workflow | AOC authorizes OP-C02; v1 contract requires correct script and authoritative view | Correct script path, but runner applies legacy SQL | R0: scheduled failure; local cron removed only | CONFLICTING |
| Path1 DIS evidence | D contract requires B-backed outcomes | DIS evidence view joins authoritative C view | R0: live, 59,875 rows; recent Path1 success | AUTHORITATIVE |
| Path1 RES/LID evidence | D operation catalog includes all score families | SQL and runner reference RES/LID views | Not sampled by R0 | UNVERIFIED_DEPLOYMENT |
| Path1 range workflow | Canonical operating loop selects range runner | Scheduled range workflow writes evidence ledger | R0: recent success | AUTHORITATIVE |
| Path1 queue workflows | Operator rejects queue production; range loop is canonical | Manual queue workflow and scheduled `main.yml` exist | R0: active | Historical/recovery-only; current schedule is nonconforming |
| Path1 replay | QA/D contracts require replay verification | Structural replay workflow and script exist | R0: latest run failed | AUTHORITATIVE but DEGRADED |
| Notion script path | AOC OP-D11 binds `scripts/export/notion_sync.py` | Workflow calls `scripts/notion_sync.py` | R0: scheduled failure | CONFLICTING |
| Notion outcomes source | Data-flow canon v0.2 requires B-backed C view | Script reads `derived.ovc_outcomes_v0_1` | Notion state unverified | CONFLICTING implementation; no new production execution authorized |
| Notion schedule | Historical docs declare two-hour cron | Local R0 edit leaves manual dispatch only | R0 observed remote scheduled run | CONFLICTING local/deployed state |
| Migration ledger | Master contract requires applied timestamps and hashes | Ledger has null actor/time and UNVERIFIED status; one file missing | R0 object hashes captured separately | UNVERIFIED_DEPLOYMENT |
| Schema CI | QA contract requires object and ledger verification | Object checks are live DB reads; ledger check is syntax-only | GitHub workflow active | CONFLICTING coverage claim |
| Workflow sanity CI | QA contract says script paths must exist | Current Notion workflow references a missing script | Workflow active; current check coverage insufficient | CONFLICTING |
| Workflow catalog | v0.2 records all repository workflow files and operator disposition | Repository contains 16 workflow files, including one zero-byte scaffold | Deployed trigger truth remains partly conflicting with local containment | AUTHORITATIVE current inventory; runtime conformance still mixed |
| Operations catalog v0.2 | Operator approved a filtered additive extension | Formal catalog adds OP-QA07, OP-QA09, and OP-QA11 only | QA08 remains conditional; QA10 remains deferred; v0.1 remains the base authority | AUTHORITATIVE additive extension with carried unresolved items |
| Sentinel | README assigns authority to maintenance branch | Workflow, state, ledger, overlay, tests exist | No R0 runtime evidence | UNRESOLVED |
| Repo Cartographer | Local baseline defines deterministic chain | Scripts, workflow, ledger exist | Required stable published outputs absent | UNRESOLVED |
| Repo Maze | Conceptual navigation surface | Large Tetsu map set exists | Multiple path/count claims contradicted by repo | SUPPORTING only |
| Current-state snapshot | Frozen 2026-01-23 maps retained as historical evidence | Several paths and claims stale | R0 delta and R1 packet are commit-bound | SUPPORTING historical snapshot; current claims withdrawn |
| Change Taxonomy v0.2 | PS-11 requires implementation and ratification evidence | Classifier and PR workflow implement v0.2 | No ratification record found | UNRESOLVED / IMPLEMENTED_UNRATIFIED |
| Design Record Engine CI | Documentation and tests imply a CI component | `.github/workflows/design_record_engine_ci.yml` is zero bytes | No executable workflow exists | UNRESOLVED scaffold, not active CI |
