# Option B: Derived Features Contract v1

**OPTION_B_CONTRACT_VERSION**: v1.1
**Status**: ACTIVE
**Date**: 2026-01-29
**Supersedes**: v1.0 (2026-01-23, DRAFT)

---

## 1. Purpose & Non-Goals

### Purpose

Option B governs the computation of deterministic derived features from
canonical OHLC facts (Option A outputs).  All Option B outputs are
recomputable, versioned, and tracked with run provenance.

This contract defines:

- The complete read set (allowlist and denylist) from A1 canonical tables.
- The complete write set (all derived tables and views owned by Option B).
- Tier boundaries for C1 / C2 / C3 layers.
- Orchestration entrypoints and their current invocation status.
- Validation gates and enforcement evidence.
- Cross-Option read/write/validate contracts.
- Option B MUST treat A1 legacy/non-authoritative fields as tainted inputs. Any derived feature that depends on them is invalid by definition.
### Non-Goals

This contract MUST NOT govern:

- Raw data ingest or canonical table mutations (Option A).
- Outcome computation from derived features (Option C).
- Evidence pack generation (Option D).
- QA orchestration beyond Option B validation gates.
- Session logic beyond deterministic grouping rules already implemented.
- Market "interpretation" that is not deterministic by definition.
- Any new infrastructure, pipelines, or SQL semantics not already present
  in the repository.

---

## 2. Inputs (READ SET)

### 2.1 A1 Authoritative Inputs (ALLOWLIST)

Option B MAY ONLY read the following fields from
`ovc.ovc_blocks_v01_1_min`:

| Field | SQL Type | Used By | Citation |
|-------|----------|---------|----------|
| `block_id` | TEXT (PK) | C1, C2, C3 | `sql/01_tables_min.sql:3` |
| `sym` | TEXT | C2, C3 | `sql/01_tables_min.sql:4` |
| `date_ny` | DATE | C2 (session windows) | `sql/01_tables_min.sql:6` |
| `bar_close_ms` | BIGINT | C2, C3 (ordering) | `sql/01_tables_min.sql:7` |
| `block2h` | TEXT | C2 view (session index) | `sql/01_tables_min.sql:8` |
| `o` | DOUBLE PRECISION | C1, C2 | `sql/01_tables_min.sql:17` |
| `h` | DOUBLE PRECISION | C1, C2 | `sql/01_tables_min.sql:18` |
| `l` | DOUBLE PRECISION | C1, C2 | `sql/01_tables_min.sql:19` |
| `c` | DOUBLE PRECISION | C1, C2 | `sql/01_tables_min.sql:20` |
| `rng` | DOUBLE PRECISION | C2 view (rolling stats) | `sql/01_tables_min.sql:23` |
| `body` | DOUBLE PRECISION | C2 view (body_rng_pct) | `sql/01_tables_min.sql:24` |
| `dir` | INTEGER | C2 view (streak, session_dir_net) | `sql/01_tables_min.sql:25` |

**Basis**: `docs/contracts/option_a1_bar_ingest_contract_v1.md` sections 4.1-4.4
classify these as identity, OHLC fact, or mechanically derived price fields.
Per `A_TO_D_CONTRACT_v1.md:158`, Option B MAY read from
`ovc.ovc_blocks_v01_1_min` and `ovc_cfg.threshold_*`.

### 2.2 A1 Forbidden Inputs (DENYLIST)

Option B MUST NOT read the following non-authoritative fields from
`ovc.ovc_blocks_v01_1_min`, per
`docs/contracts/option_a1_bar_ingest_contract_v1.md` section 4.5:

| Field | Rationale |
|-------|-----------|
| `state_tag` | Non-authoritative legacy field |
| `value_tag` | Non-authoritative legacy field |
| `event` | Non-authoritative legacy field |
| `tt` | Non-authoritative legacy field |
| `cp_tag` | Non-authoritative legacy field |
| `tis` | Non-authoritative legacy field |
| `rrc` | Non-authoritative legacy field |
| `vrc` | Non-authoritative legacy field |
| `trend_tag` | Non-authoritative legacy field |
| `struct_state` | Non-authoritative legacy field |
| `space_tag` | Non-authoritative legacy field |
| `htf_stack` | Non-authoritative legacy field |
| `with_htf` | Non-authoritative legacy field |
| `rd_state` | Non-authoritative legacy field |
| `regime_tag` | Non-authoritative legacy field |
| `trans_risk` | Non-authoritative legacy field |
| `bias_mode` | Non-authoritative legacy field |
| `bias_dir` | Non-authoritative legacy field |
| `perm_state` | Non-authoritative legacy field |
| `rail_loc` | Non-authoritative legacy field |
| `tradeable` | Non-authoritative legacy field |
| `conf_l3` | Non-authoritative legacy field |
| `play` | Non-authoritative legacy field |
| `pred_dir` | Non-authoritative legacy field |
| `pred_target` | Non-authoritative legacy field |
| `timebox` | Non-authoritative legacy field |
| `invalidation` | Non-authoritative legacy field |

**Enforcement status**: No CI gate exists to prevent downstream reads of
non-authoritative fields. DEFERRED per
`docs/contracts/option_a1_bar_ingest_contract_v1.md` Alignment Confirmation.

### 2.3 A2 Inputs

Option B does NOT currently read from `ovc.ovc_candles_m15_raw`.
No compute script or SQL view references this table.

**Status**: NOT USED.

### 2.4 Configuration Inputs

| Source | Table | Purpose | Citation |
|--------|-------|---------|----------|
| Threshold packs | `ovc_cfg.threshold_pack` | C3 regime classification thresholds | `sql/04_threshold_registry_v0_1.sql:40-84` |
| Active selectors | `ovc_cfg.threshold_pack_active` | Current active threshold version | `sql/04_threshold_registry_v0_1.sql:90-124` |

**Allowed per**: `A_TO_D_CONTRACT_v1.md:158`.

---

## 3. Outputs (WRITE SET)

### 3.1 Dual Implementation Model

Option B maintains **two parallel output paths**:

1. **SQL Views** -- stateless, computed on read from canonical tables.
2. **Materialized Tables** -- written by Python compute scripts with
   provenance tracking.

Both paths exist in the repository.  The views are the authoritative
interface for downstream Options (C reads from views per
`A_TO_D_CONTRACT_v1.md:159`).  The materialized tables support validation
and offline analysis.

### 3.2 Views (Authoritative Interface)

| Output | Type | Source DDL | Owner | Status |
|--------|------|------------|-------|--------|
| `derived.v_ovc_c1_features_v0_1` | VIEW | `sql/derived/v_ovc_c1_features_v0_1.sql` | B | IMPLEMENTED |
| `derived.v_ovc_c2_features_v0_1` | VIEW | `sql/derived/v_ovc_c2_features_v0_1.sql` | B | IMPLEMENTED |
| `derived.v_ovc_c3_features_v0_1` | VIEW | `sql/derived/v_ovc_c3_features_v0_1.sql` | B | IMPLEMENTED |

#### C1 View Features (`derived.v_ovc_c1_features_v0_1`)

Reads ONLY from `ovc.ovc_blocks_v01_1_min`.  No joins, no window functions.

| Feature | Definition | Domain | Citation |
|---------|-----------|--------|----------|
| `body_ratio` | `abs(c-o) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:55-62` |
| `upper_wick_ratio` | `(h - max(o,c)) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:71-78` |
| `lower_wick_ratio` | `(min(o,c) - l) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:87-94` |
| `wick_symmetry` | `(upper - lower) / (h-l)` | [-1,1] or NULL | `v_ovc_c1_features_v0_1.sql:110-111` |
| `body_position` | `((o+c)/2 - l) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:126-127` |
| `close_position` | `(c-l) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:142-143` |
| `open_position` | `(o-l) / (h-l)` | [0,1] or NULL | `v_ovc_c1_features_v0_1.sql:158-159` |
| `is_doji` | `body_ratio <= 0.1` | BOOLEAN | `v_ovc_c1_features_v0_1.sql:175` |
| `is_full_body` | `body_ratio >= 0.8` | BOOLEAN | `v_ovc_c1_features_v0_1.sql:192-193` |
| `is_hammer_shape` | composite (3 conditions) | BOOLEAN | `v_ovc_c1_features_v0_1.sql:209-218` |
| `is_inverted_hammer_shape` | composite (3 conditions) | BOOLEAN | `v_ovc_c1_features_v0_1.sql:235-244` |
| `directional_efficiency` | `(c-o) / (h-l)` (signed) | [-1,1] or NULL | `v_ovc_c1_features_v0_1.sql:261` |

Zero-range bars: all ratios return NULL; all booleans return FALSE.

#### C2 View Features (`derived.v_ovc_c2_features_v0_1`)

Reads from `ovc.ovc_blocks_v01_1_min`.  Uses window functions.

| Feature | Window Spec | Definition | Domain | Citation |
|---------|-------------|-----------|--------|----------|
| `rng_avg_3` | N=3 (current + 2 prior) | `avg(rng)` over 3 bars | [0,+inf) or NULL | `v_ovc_c2_features_v0_1.sql:355-362` |
| `rng_avg_6` | N=6 (current + 5 prior) | `avg(rng)` over 6 bars | [0,+inf) or NULL | `v_ovc_c2_features_v0_1.sql:372-379` |
| `dir_streak` | N=unbounded within sym | consecutive same-dir count (signed) | [-12,+12] | `v_ovc_c2_features_v0_1.sql:317-323` |
| `session_block_idx` | session=date_ny | block letter -> 1-12 | [1,12] or NULL | `v_ovc_c2_features_v0_1.sql:85-99` |
| `session_rng_cum` | session-to-date | `sum(rng)` within session | [0,+inf) or NULL | `v_ovc_c2_features_v0_1.sql:409-417` |
| `session_dir_net` | session-to-date | `sum(dir)` within session | [-12,+12] or NULL | `v_ovc_c2_features_v0_1.sql:428-435` |
| `rng_rank_6` | N=6 (5 prior) | percentile rank of current rng | [0,1] or NULL | `v_ovc_c2_features_v0_1.sql:445-462` |
| `body_rng_pct_avg_3` | N=3 (current + 2 prior) | `avg(body/rng*100)` over 3 bars | [0,100] or NULL | `v_ovc_c2_features_v0_1.sql:472-479` |

Partial window: NULL for fixed N-bar windows when fewer than N bars exist.

#### C3 View Features (`derived.v_ovc_c3_features_v0_1`)

Reads ONLY from `derived.v_ovc_c1_features_v0_1` and
`derived.v_ovc_c2_features_v0_1`.  Does NOT read from
`ovc.ovc_blocks_v01_1_min` directly.

| Feature | Values | Thresholds | Citation |
|---------|--------|-----------|----------|
| `c3_trend_bias` | `sustained`, `nascent`, `neutral`, `fading` | sustained: abs(dir_streak) >= 3 | `v_ovc_c3_features_v0_1.sql:193-211` |
| `c3_volatility_regime` | `compressed`, `normal`, `expanded` | 2+ consecutive narrowing/widening | `v_ovc_c3_features_v0_1.sql:221-235` |
| `c3_structure_type` | `decisive`, `balanced`, `indecisive` | decisive: body/rng >= 0.7; indecisive: <= 0.3 | `v_ovc_c3_features_v0_1.sql:245-264` |
| `c3_momentum_state` | `accelerating`, `steady`, `decelerating`, `reversing` | accel: body > prev*1.2; decel: body < prev*0.8 | `v_ovc_c3_features_v0_1.sql:274-296` |
| `c3_session_position` | `early`, `mid`, `late` | A-D=early, E-H=mid, I-L=late | `v_ovc_c3_features_v0_1.sql:306-323` |
| `c3_wick_dominance` | `top_heavy`, `balanced`, `bottom_heavy`, `no_wicks` | dominant >= 0.3, non-dominant < 0.15 | `v_ovc_c3_features_v0_1.sql:333-355` |
| `c3_range_context` | `narrow`, `typical`, `wide` | narrow: rng < avg*0.6; wide: rng > avg*1.4 | `v_ovc_c3_features_v0_1.sql:366-385` |

Mutual exclusivity: exactly one label per feature per block.

### 3.3 Materialized Tables (Provenance-Tracked)

| Output | Type | Source DDL | Compute Script | Owner | Status |
|--------|------|------------|----------------|-------|--------|
| `derived.ovc_c1_features_v0_1` | TABLE | `sql/02_derived_c1_c2_tables_v0_1.sql:47-72` | `src/derived/compute_c1_v0_1.py` | B | IMPLEMENTED |
| `derived.ovc_c2_features_v0_1` | TABLE | `sql/02_derived_c1_c2_tables_v0_1.sql:88-130` | `src/derived/compute_c2_v0_1.py` | B | IMPLEMENTED |
| `derived.ovc_c3_regime_trend_v0_1` | TABLE | `sql/05_c3_regime_trend_v0_1.sql:17-47` | `src/derived/compute_c3_regime_trend_v0_1.py` | B | IMPLEMENTED |
| `derived.derived_runs_v0_1` | TABLE | `sql/02_derived_c1_c2_tables_v0_1.sql:17-30` | All compute scripts | B | IMPLEMENTED |

#### Materialized C1 Table Columns

PK: `block_id`.  Provenance: `run_id`, `computed_at`, `formula_hash`, `derived_version`.

Features: `range`, `body`, `direction`, `ret`, `logret`, `body_ratio`,
`close_pos`, `upper_wick`, `lower_wick`, `clv`.
Diagnostics: `range_zero`, `inputs_valid`.

Citation: `sql/02_derived_c1_c2_tables_v0_1.sql:47-72`.

#### Materialized C2 Table Columns

PK: `block_id`.  Provenance: `run_id`, `computed_at`, `formula_hash`,
`derived_version`, `window_spec`.

Features (N=1): `gap`, `took_prev_high`, `took_prev_low`.
Features (session=date_ny): `sess_high`, `sess_low`, `dist_sess_high`,
`dist_sess_low`.
Features (N=12): `roll_avg_range_12`, `roll_std_logret_12`, `range_z_12`,
`hh_12`, `ll_12`.
Features (parameterized=rd_len): `rd_len_used`, `rd_hi`, `rd_lo`, `rd_mid`.
Diagnostics: `prev_block_exists`, `sess_block_count`, `roll_12_count`,
`rd_count`.

Citation: `sql/02_derived_c1_c2_tables_v0_1.sql:88-130`.

#### Materialized C3 Table Columns

PK: `(symbol, ts)`.  Unique index on `block_id`.

| Column | Type | Constraint | Citation |
|--------|------|-----------|----------|
| `block_id` | TEXT NOT NULL | UNIQUE INDEX | `sql/05_c3_regime_trend_v0_1.sql:19` |
| `symbol` | TEXT NOT NULL | PK component | `sql/05_c3_regime_trend_v0_1.sql:20` |
| `ts` | TIMESTAMPTZ NOT NULL | PK component | `sql/05_c3_regime_trend_v0_1.sql:21` |
| `c3_regime_trend` | TEXT NOT NULL | CHECK: `IN ('TREND','NON_TREND')` | `sql/05_c3_regime_trend_v0_1.sql:24,39-41` |
| `threshold_pack_id` | TEXT NOT NULL | provenance | `sql/05_c3_regime_trend_v0_1.sql:27` |
| `threshold_pack_version` | INT NOT NULL | provenance | `sql/05_c3_regime_trend_v0_1.sql:28` |
| `threshold_pack_hash` | TEXT NOT NULL | CHECK: SHA256 64 hex chars | `sql/05_c3_regime_trend_v0_1.sql:29,44-46` |
| `run_id` | UUID NOT NULL | compute run ref | `sql/05_c3_regime_trend_v0_1.sql:32` |
| `created_at` | TIMESTAMPTZ NOT NULL | DEFAULT `now()` | `sql/05_c3_regime_trend_v0_1.sql:33` |

Note: The C3 materialized table does NOT contain a `formula_hash` column.
Threshold pack provenance (id, version, hash) serves as the audit trail.
This differs from C1/C2 tables which store `formula_hash`.

### 3.4 Run Provenance Table

| Column | Type | Purpose | Citation |
|--------|------|---------|----------|
| `run_id` | UUID PK | Unique run identifier | `sql/02_derived_c1_c2_tables_v0_1.sql:18` |
| `run_type` | TEXT NOT NULL | `'c1'`, `'c2'`, `'c3'` | `sql/02_derived_c1_c2_tables_v0_1.sql:19` |
| `version` | TEXT NOT NULL | `'v0.1'` | `sql/02_derived_c1_c2_tables_v0_1.sql:20` |
| `formula_hash` | TEXT NOT NULL | MD5 of computation logic | `sql/02_derived_c1_c2_tables_v0_1.sql:21` |
| `window_spec` | TEXT | NULL for C1; required for C2+ | `sql/02_derived_c1_c2_tables_v0_1.sql:22` |
| `threshold_version` | TEXT | NULL for C1/C2; required for C3 | `sql/02_derived_c1_c2_tables_v0_1.sql:23` |
| `started_at` | TIMESTAMPTZ | Run start | `sql/02_derived_c1_c2_tables_v0_1.sql:24` |
| `completed_at` | TIMESTAMPTZ | Run end | `sql/02_derived_c1_c2_tables_v0_1.sql:25` |
| `block_count` | INTEGER | Blocks processed | `sql/02_derived_c1_c2_tables_v0_1.sql:26` |
| `status` | TEXT | `'running'`/`'completed'`/`'failed'` | `sql/02_derived_c1_c2_tables_v0_1.sql:27` |
| `error_message` | TEXT | Failure detail | `sql/02_derived_c1_c2_tables_v0_1.sql:28` |
| `config_snapshot` | JSONB | Runtime config for reproducibility | `sql/02_derived_c1_c2_tables_v0_1.sql:29` |

### 3.5 DEPRECATED Outputs

| Output | Type | Source DDL | Status |
|--------|------|------------|--------|
| `derived.ovc_block_features_v0_1` | VIEW | `sql/derived_v0_1.sql:10-176` | **DEPRECATED** |
| `derived.derived_runs` | TABLE | `sql/derived_v0_1.sql:3-8` | **DEPRECATED** (superseded by `derived.derived_runs_v0_1`) |

**v1 Resolution**: The split C1/C2/C3 views and materialized tables are
authoritative.  The legacy combined view is deprecated and MUST NOT be used
for new code.

---

## 4. Derived Layers & Boundaries

### 4.1 Layer Definitions

Per `docs/contracts/c_layer_boundary_spec_v0.1.md`:

| Layer | Definition | History Allowed | Citation |
|-------|-----------|-----------------|----------|
| **C1** | Single-bar OHLC math. `f(o,h,l,c) -> output`. No lookback, no rolling windows, no joins. | NONE | `c_layer_boundary_spec_v0.1.md` |
| **C2** | Multi-bar structure/context. Requires explicit `window_spec`. Features depend on ordered block sequences. | YES (explicit window) | `c_layer_boundary_spec_v0.1.md` |
| **C3** | Semantic tags derived from C1/C2 features. Discrete categorical outputs. | Via C1/C2 only | `c_layer_boundary_spec_v0.1.md` |

**Forbidden cross-layer dependencies**:
- C1 MUST NOT have rolling windows or lookback.
- C2 MUST NOT access C3 outputs.
- C3 MUST NOT access `ovc.ovc_blocks_v01_1_min` directly (views enforce
  this; materialized C3 joins through C1/C2).
- Reverse dependencies (C1 reading C2, C2 reading C3) are PROHIBITED.

Citation: `docs/contracts/c_layer_boundary_spec_v0.1.md`.

### 4.2 Determinism

**C1**: Fully determined by single-block OHLC values.
`f(o, h, l, c) -> identical output` for all time.
Citation: `src/derived/compute_c1_v0_1.py` formula definitions.

**C2**: Determined by ordered block sequence + window_spec.
`f(ohlc_sequence, window_spec) -> identical output` given same ordering.
Citation: `src/derived/compute_c2_v0_1.py` window definitions.

**C3 (views)**: Determined by C1/C2 outputs + hardcoded thresholds in SQL.
All thresholds are embedded in the view definition.
Citation: `sql/derived/v_ovc_c3_features_v0_1.sql` CASE expressions.

**C3 (materialized)**: Determined by C1/C2 outputs + versioned threshold
pack.  Same inputs + same threshold pack (id, version, hash) = identical
output.  Citation: `src/derived/compute_c3_regime_trend_v0_1.py`,
`docs/contracts/c3_semantic_contract_v0_1.md`.

### 4.3 Immutability

- Materialized C1/C2 tables use `ON CONFLICT (block_id) DO UPDATE` upsert
  semantics.  Rerunning the same inputs produces identical results.
- Materialized C3 table uses `ON CONFLICT (symbol, ts) DO UPDATE`.
- Views are stateless and deterministic by definition.
- Threshold packs are immutable once created (append-only versioning).
  Citation: `sql/04_threshold_registry_v0_1.sql:8`.

### 4.4 Versioning & Registries

| Artifact | Version Scheme | Current Version | Citation |
|----------|---------------|-----------------|----------|
| C1 features (table) | `v{major}.{minor}` | v0.1 | `sql/02_derived_c1_c2_tables_v0_1.sql:55` |
| C2 features (table) | `v{major}.{minor}` | v0.1 | `sql/02_derived_c1_c2_tables_v0_1.sql:96` |
| C3 regime trend (table) | `v{major}.{minor}` | v0.1 | `sql/05_c3_regime_trend_v0_1.sql` |
| Threshold packs | `(pack_id, pack_version)` | per-pack | `sql/04_threshold_registry_v0_1.sql:43-44` |
| Derived runs | `run_type + version` | v0.1 | `sql/02_derived_c1_c2_tables_v0_1.sql:19-20` |
| Formula hash | MD5 of computation spec | per-script | `src/derived/compute_c1_v0_1.py`, `src/derived/compute_c2_v0_1.py` |

**View naming**: `derived.v_ovc_{layer}_features_v{major}_{minor}`.
**Script naming**: `src/derived/compute_{layer}_v{major}_{minor}.py`.
**Table naming**: `derived.ovc_{layer}_features_v{major}_{minor}`.

---

## 5. Orchestration & Invocation Truth

### 5.1 Primary Workflow: `backfill_then_validate.yml`

| Step | Name | Script Invoked | Arguments | Status |
|------|------|----------------|-----------|--------|
| 3 | Compute C1 Features | `src/derived/compute_c1_v0_1.py` | `--symbol GBPUSD` | IMPLEMENTED |
| 4 | Compute C2 Features | `src/derived/compute_c2_v0_1.py` | `--symbol GBPUSD` | IMPLEMENTED |
| 4.5 | Compute C3 Features | `src/derived/compute_c3_regime_trend_v0_1.py` | `--symbol GBPUSD` | **INCOMPLETE** -- missing `--threshold-pack` and `--scope` arguments |
| 5 | Validate Derived | `src/validate/validate_derived_range_v0_1.py` | `--symbol GBPUSD --start-date ... --end-date ... --mode ...` | IMPLEMENTED |

Citation: `.github/workflows/backfill_then_validate.yml:119-150`.

**Trigger**: Manual `workflow_dispatch` with `start_date`, `end_date`,
`strict`, `missing_facts` inputs.

**Known Issue (Step 4.5)**: The workflow invokes
`compute_c3_regime_trend_v0_1.py` with only `--symbol GBPUSD` but the
script requires `--threshold-pack` and `--scope` arguments.  This step will
FAIL at runtime.
Citation: `.github/workflows/backfill_then_validate.yml:136-138`.

### 5.2 CI Workflows

| Workflow | Purpose | Invokes Option B? | Citation |
|----------|---------|-------------------|----------|
| `ci_pytest.yml` | Runs pytest suite (includes derived feature tests) | YES (unit tests) | `.github/workflows/ci_pytest.yml` |
| `ci_schema_check.yml` | Verifies schema objects exist | YES (checks derived schema) | `.github/workflows/ci_schema_check.yml` |
| `ci_workflow_sanity.yml` | Validates workflows reference existing scripts | YES (checks script existence) | `.github/workflows/ci_workflow_sanity.yml` |

### 5.3 Manual Invocation (Compute Scripts)

| Script | CLI | Status |
|--------|-----|--------|
| `compute_c1_v0_1.py` | `python src/derived/compute_c1_v0_1.py [--dry-run] [--limit N] [--symbol SYM] [--recompute]` | IMPLEMENTED |
| `compute_c2_v0_1.py` | `python src/derived/compute_c2_v0_1.py [--dry-run] [--limit N] [--symbol SYM] [--rd-len N] [--recompute]` | IMPLEMENTED |
| `compute_c3_regime_trend_v0_1.py` | `python src/derived/compute_c3_regime_trend_v0_1.py --symbol SYM --threshold-pack ID --scope SCOPE [--threshold-version N] [--dry-run] [--recompute]` | IMPLEMENTED |

### 5.4 DORMANT Artifacts

| Artifact | Path | Reason | Status |
|----------|------|--------|--------|
| C3 stub | `src/derived/compute_c3_stub_v0_1.py` | Experimental alternative; not integrated into any workflow or test | DORMANT |

---

## 6. Validation & Enforcement

### 6.1 Validation Script

**`src/validate/validate_derived_range_v0_1.py`** -- comprehensive
validation framework covering C1/C2/C3.

| Check | Description | Status |
|-------|-------------|--------|
| Coverage parity | `count(B) == count(C1) == count(C2)` | IMPLEMENTED |
| Key uniqueness | No duplicate `block_id` in C1/C2 | IMPLEMENTED |
| Null rate monitoring | Per-column null rate; flag columns > 10% | IMPLEMENTED |
| NaN/Inf detection | Check for special float values | IMPLEMENTED |
| C2 window_spec enforcement | All C2 rows have valid `window_spec` | IMPLEMENTED |
| C1 determinism quickcheck | Re-compute C1 inline, compare vs stored | IMPLEMENTED |
| C3 provenance verification | `threshold_pack_*` NOT NULL; hash integrity | IMPLEMENTED |
| C3 value validation | Classification values match CHECK constraint | IMPLEMENTED |
| TV reference comparison | Compare C1 vs TV-sourced blocks (optional) | IMPLEMENTED |

Citation: `src/validate/validate_derived_range_v0_1.py`.

Output artifacts: `derived_validation_report.json`,
`derived_validation_report.md`, `derived_validation_diffs.csv` (optional).

### 6.2 Unit Tests

| Test File | Coverage | Citation |
|-----------|----------|----------|
| `tests/test_derived_features.py` | C1 determinism, C1 correctness (all 10 metrics), C1 formula hash, C2 window_spec format, C2 determinism, C2 correctness (gap, took_prev_high/low, sess_high, edge cases), C2 formula hash | `tests/test_derived_features.py` |
| `tests/test_validate_derived.py` | compute_c1_inline formulas, values_match tolerance, build_run_id determinism, parse_date validation, ValidationResult defaults, window_spec validation, C1/C2 column lists, edge cases (zero/negative prices) | `tests/test_validate_derived.py` |

**C3 unit tests**: NOT IMPLEMENTED.  No dedicated test file exists for
`compute_c3_regime_trend_v0_1.py`.  C3 validation coverage exists only in
`validate_derived_range_v0_1.py` (provenance checks, not logic tests).

### 6.3 SQL Gates

| Gate | File | Purpose | Wired to CI? | Status |
|------|------|---------|-------------|--------|
| Schema verification | `sql/90_verify_gate2.sql` | Checks table/view existence | YES (`ci_schema_check.yml`) | IMPLEMENTED |
| C3 table verification | `sql/05_c3_regime_trend_v0_1.sql:88-99` | DO block verifies table creation | Only at migration time | EXISTS (NOT ENFORCED at CI) |
| Threshold registry verification | `sql/04_threshold_registry_v0_1.sql:186-196` | DO block verifies table creation | Only at migration time | EXISTS (NOT ENFORCED at CI) |

---

## 7. Cross-Option Contracts

### 7.1 Read/Write/Validate Matrix

| From \ To | Option A | Option B | Option C | Option D | QA |
|-----------|----------|----------|----------|----------|----|
| **Option A** | WRITE `ovc.ovc_blocks_v01_1_min`, `ovc.ovc_candles_m15_raw` | -- | -- | -- | -- |
| **Option B** | READ `ovc.ovc_blocks_v01_1_min` (authoritative fields only), READ `ovc_cfg.threshold_*` | WRITE `derived.*` | -- | -- | -- |
| **Option C** | PROHIBITED | READ `derived.v_ovc_c1_features_v0_1`, `derived.v_ovc_c2_features_v0_1`, `derived.v_ovc_c3_features_v0_1` | WRITE `derived.v_ovc_c_outcomes_v0_1` | -- | -- |
| **Option D** | READ `ovc.ovc_blocks_v01_1_min` (spine), `ovc.ovc_candles_m15_raw` (overlay) | -- | READ `derived.v_ovc_c_outcomes_v0_1` | WRITE evidence packs | -- |
| **QA** | READ (all, validate) | READ (all, validate) | READ (all, validate) | READ (all, validate) | VALIDATE |

Citation: `A_TO_D_CONTRACT_v1.md` section 7.

### 7.2 Critical Boundary Rules

- Option B MUST NOT write to `ovc.*` or `ovc_cfg.*` tables.
- Option B MUST NOT read from `derived.v_ovc_c_outcomes_v0_1` (Option C output).
- Option C MUST NOT read `ovc.ovc_blocks_v01_1_min` directly.
  Citation: `A_TO_D_CONTRACT_v1.md:164`.
- Option C MUST read from Option B views (not tables).
  Citation: `A_TO_D_CONTRACT_v1.md:159`.

---

## 8. Explicit Exclusions

| Exclusion | Rationale | Citation |
|-----------|-----------|----------|
| A2 (`ovc.ovc_candles_m15_raw`) as Option B input | Not used in any B compute script or view | No reference in `src/derived/` or `sql/derived/` |
| Non-authoritative A1 fields as inputs | Prohibited per A1 contract section 4.5 | `option_a1_bar_ingest_contract_v1.md:139-184` |
| Option C outputs as Option B inputs | Reverse dependency prohibited | `A_TO_D_CONTRACT_v1.md:64` |
| Option D outputs as Option B inputs | Reverse dependency prohibited | `A_TO_D_CONTRACT_v1.md:65` |
| Heuristic cleaning or reinterpretation | Option B is deterministic math only | `A_TO_D_CONTRACT_v1.md:49` |
| Non-deterministic classifiers | C3 views use hardcoded thresholds; C3 table uses versioned packs | `c3_semantic_contract_v0_1.md` |
| Stateful or ML-based inference | Not present in any B compute path | No evidence in `src/derived/` |
| `volume` as Option B input | Not present in A1 table DDL | `option_a1_bar_ingest_contract_v1.md` section 10 |
| `ret` as validated input | `ret` semantic validation DEFERRED at ingest; no downstream gate | `option_a1_bar_ingest_contract_v1.md:382-383` |

---

## 9. Alignment Confirmation

### 9.1 Fully Aligned with Repo Reality

| Item | Evidence |
|------|----------|
| C1 view exists and reads only from `ovc.ovc_blocks_v01_1_min` | `sql/derived/v_ovc_c1_features_v0_1.sql:264` |
| C2 view exists and reads only from `ovc.ovc_blocks_v01_1_min` | `sql/derived/v_ovc_c2_features_v0_1.sql:104` |
| C3 view exists and reads only from C1 and C2 views | `sql/derived/v_ovc_c3_features_v0_1.sql:73-76` |
| C1 materialized table DDL matches compute script output | `sql/02_derived_c1_c2_tables_v0_1.sql:47-72`, `src/derived/compute_c1_v0_1.py` |
| C2 materialized table DDL matches compute script output | `sql/02_derived_c1_c2_tables_v0_1.sql:88-130`, `src/derived/compute_c2_v0_1.py` |
| C3 materialized table DDL matches compute script output | `sql/05_c3_regime_trend_v0_1.sql:17-47`, `src/derived/compute_c3_regime_trend_v0_1.py` |
| Threshold registry DDL defines immutable versioned packs | `sql/04_threshold_registry_v0_1.sql:40-84` |
| Derived runs provenance table exists with all required fields | `sql/02_derived_c1_c2_tables_v0_1.sql:17-30` |
| C1/C2 compute scripts invoked in `backfill_then_validate.yml` Steps 3-4 | `.github/workflows/backfill_then_validate.yml:119-131` |
| Validation script invoked in `backfill_then_validate.yml` Step 5 | `.github/workflows/backfill_then_validate.yml:140-150` |
| Unit tests cover C1/C2 determinism and correctness | `tests/test_derived_features.py` |
| Validation tests cover inline recompute and edge cases | `tests/test_validate_derived.py` |
| CI runs pytest | `.github/workflows/ci_pytest.yml` |
| CI verifies schema | `.github/workflows/ci_schema_check.yml` |
| Legacy combined view deprecated | `sql/derived_v0_1.sql:10` |
| Window_spec documented per C2 column | `sql/02_derived_c1_c2_tables_v0_1.sql:137-152` |

### 9.2 Deferred Items

| Item | Status | Rationale |
|------|--------|-----------|
| C3 workflow invocation arguments (`--threshold-pack`, `--scope`) | **INCOMPLETE** | `.github/workflows/backfill_then_validate.yml:136-138` -- missing required args |
| C3 unit tests | **NOT IMPLEMENTED** | No `test_c3_regime_trend.py` exists |
| C3 `formula_hash` in materialized table | **NOT IMPLEMENTED** | `sql/05_c3_regime_trend_v0_1.sql` lacks `formula_hash` column |
| `config_snapshot` population in compute scripts | **NOT IMPLEMENTED** | `derived_runs_v0_1.config_snapshot` field exists but is not populated |
| CI gate preventing reads of A1 non-authoritative fields | **DEFERRED** | Per `option_a1_bar_ingest_contract_v1.md` Alignment Confirmation |
| Threshold pack pre-population | **NOT IMPLEMENTED** | Registry tables exist but no default packs are seeded |
| Removal of legacy `derived.ovc_block_features_v0_1` view | **DEFERRED** | Marked deprecated; removal planned for v2 |
| `ret` semantic validation downstream | **DEFERRED** | Disabled at ingest; no B-layer gate exists |

### 9.3 What Would BREAK This Contract If Changed

| Change | Impact |
|--------|--------|
| Removing or renaming `ovc.ovc_blocks_v01_1_min` | Breaks all Option B views and compute scripts |
| Changing A1 OHLC field types (`o`, `h`, `l`, `c`) | Breaks C1 arithmetic; cascading C2/C3 failures |
| Removing mechanically derived fields (`rng`, `body`, `dir`) from A1 | Breaks C2 view which uses these as passthrough inputs |
| Altering `block_id` format | Breaks PK references in all materialized tables |
| Removing `date_ny` or `block2h` from A1 | Breaks C2 session grouping and `session_block_idx` |
| Changing `bar_close_ms` from UTC epoch ms | Breaks C2 temporal ordering |
| Modifying C1 view feature formulas without version bump | Silently changes C2/C3 outputs (C3 reads from C1/C2 views) |
| Modifying C2 view window specifications | Changes C3 inputs; breaks all downstream determinism guarantees |
| Promoting A1 non-authoritative fields to authoritative | Violates canonical/derived boundary |
| Changing threshold pack schema in `ovc_cfg.threshold_pack` | Breaks C3 materialized compute script |
| Altering `derived` schema name | Breaks all view and table references |
