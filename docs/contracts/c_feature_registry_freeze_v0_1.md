# C Feature Registry Freeze v0.1 (C1/C2/C3)

**C_FEATURE_REGISTRY_FREEZE_VERSION**: v0.1
**Status**: FROZEN
**Date**: 2026-01-30

---

## 1. Scope & Authority

This document finalizes and freezes the **C-layer feature registries** for:

- **C1**: single-bar mechanical measurements
- **C2**: multi-bar numeric evidence
- **C3**: semantic classifications

### 1.1 Authoritative Truth (binding)

Computational truth is the SQL currently present in this repository. No
feature definitions, thresholds, or output schemas in this registry are
authoritative unless they match the SQL below.

**Authoritative view definitions (C-layer interfaces):**

- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `sql/derived/v_ovc_c3_features_v0_1.sql`

**Boundary and governance anchors (non-computational, but binding):**

- `docs/contracts/option_a1_bar_ingest_contract_v1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `docs/contracts/c_layer_boundary_spec_v0.1.md`
- `.github/workflows/backfill_then_validate.yml` (enforcement reality)

### 1.2 Explicit Non-Goals

- No Option C design in this document.
- No feature addition/removal/refactor.
- No SQL changes.
- Misclassifications (C1 vs C2 vs C3) are resolved by **documentation only**.

---

## 2. Definitions (used throughout)

### 2.1 Column Classes

- **CANONICAL**: A stable, frozen output intended for downstream consumption
  as part of the C-layer interface. Option C MAY depend on CANONICAL columns
  only (subject to Option C boundary docs).
- **DIAGNOSTIC (NON-CANONICAL)**: Debugging, intermediate, or validation aid.
  DIAGNOSTIC columns MAY exist in views and MAY change without notice, unless
  explicitly frozen (none are frozen here). Downstream dependencies are
  PROHIBITED.
- **PASSTHROUGH (NON-FEATURE)**: Identity or input-fact columns emitted for
  convenience (e.g., `block_id`, `sym`, OHLC). PASSTHROUGH columns are not
  "features" but may be required for joins, ordering, or context. Treat them
  as schema-level fields, not derived outputs.

### 2.2 Downstream Dependency Rules (policy)

- Option C and any deterministic consumer MUST treat this registry as the
  allowlist for C-layer consumption.
- DIAGNOSTIC columns are forbidden as downstream dependencies.

**Enforcement reality**: This prohibition is not enforced by CI or SQL
permissions in the current repo; it is a registry-level rule only.

---

## 3. C1 Registry (derived.v_ovc_c1_features_v0_1)

**Source**: `sql/derived/v_ovc_c1_features_v0_1.sql`

### 3.1 Output Columns (classification)

| Column | Class | Notes |
|---|---|---|
| `block_id`, `sym` | PASSTHROUGH | Identity (from A1 canonical table). |
| `tf` | PASSTHROUGH (NON-CANONICAL) | **Known limitation**: `tf` is a generated alias of `tz` in the database patch `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql`. It is not a timeframe. |
| `o`, `h`, `l`, `c` | PASSTHROUGH | A1 OHLC facts. |
| `rng`, `body`, `dir` | PASSTHROUGH | Mechanically derived fields stored in A1 (not C1-derived in this view). |
| `body_ratio` | CANONICAL | Ratio: `abs(c-o)/(h-l)` with zero-range -> NULL. |
| `upper_wick_ratio` | CANONICAL | Ratio: `(h - max(o,c))/(h-l)` with zero-range -> NULL. |
| `lower_wick_ratio` | CANONICAL | Ratio: `(min(o,c) - l)/(h-l)` with zero-range -> NULL. |
| `wick_symmetry` | CANONICAL | Ratio: `((h - max(o,c)) - (min(o,c) - l))/(h-l)` with zero-range -> NULL. |
| `body_position` | CANONICAL | Ratio: `(((o+c)/2) - l)/(h-l)` with zero-range -> NULL. |
| `close_position` | CANONICAL | Ratio: `(c-l)/(h-l)` with zero-range -> NULL. |
| `open_position` | CANONICAL | Ratio: `(o-l)/(h-l)` with zero-range -> NULL. |
| `is_doji` | CANONICAL | Boolean-like, but **may be NULL** when inputs are NULL. Zero-range -> FALSE. |
| `is_full_body` | CANONICAL | Boolean-like, but **may be NULL** when inputs are NULL. Zero-range -> FALSE. |
| `is_hammer_shape` | CANONICAL | Boolean-like, but **may be NULL** when inputs are NULL. Zero-range -> FALSE. |
| `is_inverted_hammer_shape` | CANONICAL | Boolean-like, but **may be NULL** when inputs are NULL. Zero-range -> FALSE. |
| `directional_efficiency` | CANONICAL | Signed ratio: `(c-o)/(h-l)` with zero-range -> NULL. |

### 3.2 C1 Boundary Statement (binding)

- C1 CANONICAL columns MUST be computable from a **single bar** without
  lookback, windowing, or joins.
- The C1 view complies by construction; it reads from one table and uses no
  window functions.

### 3.3 Null and Zero-Range Semantics (binding)

- For all ratio outputs: if `(h - l) = 0`, output is **NULL** (not 0).
- For C1 boolean-like outputs: if `(h - l) = 0`, output is **FALSE**.
- For NULL input propagation: some boolean-like outputs return **NULL** when
  required inputs are NULL (this is SQL reality and is part of the freeze).

---

## 4. C2 Registry (derived.v_ovc_c2_features_v0_1)

**Source**: `sql/derived/v_ovc_c2_features_v0_1.sql`

### 4.1 Output Columns (classification)

| Column | Class | Notes |
|---|---|---|
| `block_id`, `sym`, `block2h`, `bar_close_ms`, `date_ny` | PASSTHROUGH | Identity + ordering context. |
| `o`, `h`, `l`, `c`, `rng`, `dir` | PASSTHROUGH | A1 facts / mechanically derived fields. |
| `rng_avg_3` | CANONICAL | Fixed 3-bar rolling mean of `rng`. Partial window -> NULL. |
| `rng_avg_6` | CANONICAL | Fixed 6-bar rolling mean of `rng`. Partial window -> NULL. |
| `dir_streak` | CANONICAL | Signed consecutive direction count (cap +/-12); flat bar (`dir=0`) -> 0. |
| `session_block_idx` | CANONICAL | 1..12 derived from `block_id` (A..L mapping). |
| `session_rng_cum` | CANONICAL | Session-to-date cumulative sum of `rng` (partition by `sym` + derived session_date). |
| `session_dir_net` | CANONICAL | Session-to-date sum of `dir` (partition by `sym` + derived session_date). |
| `rng_rank_6` | CANONICAL | Percentile-like rank of `rng` vs prior 5 bars (strict `<`, ties excluded). |
| `body_rng_pct_avg_3` | CANONICAL | Fixed 3-bar rolling mean of `(body/rng*100)`; if any NULL in window -> NULL. |
| `window_3_count` | DIAGNOSTIC (NON-CANONICAL) | Window completeness counter. Forbidden dependency. |
| `window_6_count` | DIAGNOSTIC (NON-CANONICAL) | Window completeness counter. Forbidden dependency. |
| `session_row_num` | DIAGNOSTIC (NON-CANONICAL) | Row number within derived session partition. Forbidden dependency. |
| `streak_group` | DIAGNOSTIC (NON-CANONICAL) | Intermediate grouping id used to compute `dir_streak`. Forbidden dependency. |

### 4.2 C2 Boundary Statement (binding)

- C2 CANONICAL columns MUST use multi-bar evidence (lookback and/or session
  windows) and MUST remain numeric (not semantic labels).
- The C2 view uses window functions and emits only numeric outputs for
  CANONICAL features.

### 4.3 Windowing Semantics (binding)

The following semantics are frozen as implemented:

- Fixed-N windows include the **current bar** and prior bars.
- Fixed-N windows MAY cross session boundaries.
- Session-to-date windows reset by **derived session_date**, which is
  computed as `SUBSTRING(block_id FROM 1 FOR 8)` (not from `date_ny`).
- Partial windows return NULL for fixed-N windows.
- NULL propagation for windowed values is implemented via explicit counts.

**Known limitation**: `session_block_idx` is derived from the **`block_id`
string**, not from the `block2h` column. This assumes `block_id` format
stability (`YYYYMMDD-X-SYMBOL`) as defined in Option A1.

### 4.4 Canonical vs Diagnostic Rule (binding)

Downstream consumers MUST NOT use `window_3_count`, `window_6_count`,
`session_row_num`, or `streak_group` for any deterministic logic, gating, or
fallback decisions. These columns are DIAGNOSTIC only.

---

## 5. C3 Registry (derived.v_ovc_c3_features_v0_1)

**Source**: `sql/derived/v_ovc_c3_features_v0_1.sql`

### 5.1 Output Columns (classification)

| Column | Class | Notes |
|---|---|---|
| `block_id`, `sym`, `bar_close_ms` | PASSTHROUGH | Identity + ordering context from joined C1/C2 views. |
| `c3_trend_bias` | CANONICAL | Semantic label (reference semantics). |
| `c3_volatility_regime` | CANONICAL | Semantic label (reference semantics). |
| `c3_structure_type` | CANONICAL | Semantic label (reference semantics). |
| `c3_momentum_state` | CANONICAL | Semantic label (reference semantics). |
| `c3_session_position` | CANONICAL | Semantic label (reference semantics); may be NULL. |
| `c3_wick_dominance` | CANONICAL | Semantic label (reference semantics). |
| `c3_range_context` | CANONICAL | Semantic label (reference semantics). |

### 5.2 C3 Boundary Statement (binding)

- C3 CANONICAL columns are semantic classifications derived from C1/C2
  numeric evidence.
- The C3 view reads from C1/C2 views only and MUST NOT access
  `ovc.ovc_blocks_v01_1_min` directly (this is enforced in the view SQL).

### 5.3 C3 Threshold Model (binding)

The repository intentionally supports two threshold models:

1. **Inline thresholds in C3 views**: accepted as **reference semantics**
   (human-readable, deterministic, side-effect free).
2. **Threshold-pack governed tables**: accepted as **certified execution**
   where implemented (versioned threshold packs with provenance).

**Known limitation (scope mismatch)**: The only threshold-pack governed C3
table currently defined is `derived.ovc_c3_regime_trend_v0_1`, which produces
`c3_regime_trend` (`TREND`/`NON_TREND`). This is not the same set as the C3
view outputs listed in this registry.

**Enforcement reality**: `.github/workflows/backfill_then_validate.yml` invokes
`compute_c3_regime_trend_v0_1.py` without required arguments (known failure
mode per Option B contract). This means certified execution is not reliably
produced by that workflow today.

### 5.4 Fallback Semantics (binding, as implemented)

This section freezes the implemented default/fallback behavior and
distinguishes "true state" from "insufficient evidence" using observable
preconditions.

#### 5.4.1 c3_trend_bias

Values: `sustained`, `nascent`, `neutral`, `fading`

- If `dir_streak` is NULL -> `neutral` (insufficient evidence).
- Else if `dir_change` is TRUE -> `fading` (direction just changed).
- Else if `abs(dir_streak) >= 3` -> `sustained`.
- Else if `abs(dir_streak) IN (1,2)` -> `nascent`.
- Else -> `neutral` (true state; includes `dir_streak = 0`).

#### 5.4.2 c3_volatility_regime

Values: `compressed`, `normal`, `expanded`

- If `rng` is NULL OR `prev_rng` is NULL -> `normal` (insufficient evidence).
- Else if 2+ consecutive narrowing -> `compressed`.
- Else if 2+ consecutive widening -> `expanded`.
- Else -> `normal` (true state).

#### 5.4.3 c3_structure_type

Values: `decisive`, `balanced`, `indecisive`

- If `rng` is NULL OR `rng = 0` -> `indecisive` (insufficient evidence OR zero-range).
- Else if `body` is NULL -> `balanced` (insufficient evidence).
- Else if `body/rng >= 0.7` -> `decisive`.
- Else if `body/rng <= 0.3` -> `indecisive`.
- Else -> `balanced`.

#### 5.4.4 c3_momentum_state

Values: `accelerating`, `steady`, `decelerating`, `reversing`

- If `dir_change` is TRUE -> `reversing` (true state by precedence).
- Else if `prev_body` is NULL OR `prev_body = 0` -> `steady` (insufficient evidence).
- Else if `body` is NULL -> `steady` (insufficient evidence).
- Else if `body > prev_body * 1.2` -> `accelerating`.
- Else if `body < prev_body * 0.8` -> `decelerating`.
- Else -> `steady` (true state).

#### 5.4.5 c3_session_position

Values: `early`, `mid`, `late` (or NULL)

- If `session_block_idx` is NULL -> NULL (insufficient evidence / invalid row).
- Else if 1..4 -> `early`
- Else if 5..8 -> `mid`
- Else if 9..12 -> `late`

#### 5.4.6 c3_wick_dominance

Values: `top_heavy`, `balanced`, `bottom_heavy`, `no_wicks`

- If `rng` is NULL OR `rng = 0` -> `no_wicks` (zero-range or insufficient evidence).
- Else if `upper_wick_ratio` is NULL OR `lower_wick_ratio` is NULL -> `balanced` (insufficient evidence).
- Else if `(upper_wick_ratio + lower_wick_ratio) < 0.1` -> `no_wicks`.
- Else if `upper_wick_ratio >= 0.3 AND lower_wick_ratio < 0.15` -> `top_heavy`.
- Else if `lower_wick_ratio >= 0.3 AND upper_wick_ratio < 0.15` -> `bottom_heavy`.
- Else -> `balanced`.

#### 5.4.7 c3_range_context

Values: `narrow`, `typical`, `wide`

- If `rng_avg_6` is NULL OR `rng_avg_6 = 0` -> `typical` (insufficient evidence).
- Else if `rng` is NULL -> `typical` (insufficient evidence).
- Else if `rng < rng_avg_6 * 0.6` -> `narrow`.
- Else if `rng > rng_avg_6 * 1.4` -> `wide`.
- Else -> `typical` (true state).

---

## 6. Known Limitations (explicit, frozen as facts)

- **tf mislabeling**: `tf` exists only due to the DB patch
  `sql/path1/db_patches/patch_align_c1_tf_column_20260120.sql` and is an alias
  of `tz`. Do not interpret `tf` as timeframe.
- **C2 relies on block_id parsing**: session/date/position logic depends on
  `block_id` string format stability.
- **C2 view contains diagnostics**: diagnostic columns are present and MUST NOT
  be used downstream (policy-only).
- **C3 dual model is incomplete in automation**: certified execution via
  threshold-pack table computation is not reliably invoked by
  `backfill_then_validate.yml` as currently written.
- **No enforcement gates**: the repo does not currently enforce (via CI or SQL
  permissions) that downstream consumes only CANONICAL columns.

---

## 7. Freeze Declaration (binding)

### 7.1 Freeze Unit

**C1 + C2 + C3 are frozen as a unit** under `C_FEATURE_REGISTRY_FREEZE_VERSION:
v0.1` dated **2026-01-30**.

Any change to:

- output columns (add/remove/rename),
- null/zero-range behavior,
- window definitions,
- label sets,
- precedence rules,
- thresholds used in the C3 view,

MUST be treated as a breaking change and MUST require a new freeze version.

### 7.2 Option C Gate (binding, policy)

Option C design and implementation work is explicitly **blocked** until this
freeze is acknowledged as the current registry baseline.

Acknowledgement mechanism: **UNSPECIFIED** (not enforced in repo). Until a
mechanism exists, this document is the controlling statement of the gate.
