# Path 1 Score Inventory v1

**STATUS: HISTORICAL (REFERENCE ONLY)**  
This inventory reflects the frozen score set at the time it was written.  
Execution ergonomics are defined in `PATH1_EXECUTION_MODEL.md`.  
Canonical facts remain in `reports/path1/evidence/INDEX.md`.

**Status:** FROZEN  
**Freeze Date:** 2026-01-20  
**Library:** SCORE_LIBRARY_v1

---

## Score Manifest

### DIS-v1.1 — Directional Imbalance Score

| Attribute | Value |
|-----------|-------|
| Version | v1.1 |
| Description | Measures body utilization relative to bar range |
| Domain | [0, 1] |

**Input Columns:**

| Column | Source View |
|--------|-------------|
| `block_id` | `derived.v_ovc_c1_features_v0_1` |
| `sym` | `derived.v_ovc_c1_features_v0_1` |
| `body_ratio` | `derived.v_ovc_c1_features_v0_1` |
| `bar_close_ms` | `derived.v_ovc_c2_features_v0_1` |

**Output Fields:**

| Field | Type |
|-------|------|
| `block_id` | TEXT |
| `sym` | TEXT |
| `bar_close_ms` | BIGINT |
| `raw_score` | DOUBLE PRECISION |
| `z_score` | DOUBLE PRECISION |

**SQL File:** `sql/path1/scores/score_dis_v1_1.sql`

---

### RES-v1.0 — Rotation Efficiency Score

| Attribute | Value |
|-----------|-------|
| Version | v1.0 |
| Description | Measures range efficiency relative to recent average, weighted by body utilization |
| Domain | [0, ∞) |

**Input Columns:**

| Column | Source View |
|--------|-------------|
| `block_id` | `derived.v_ovc_c1_features_v0_1` |
| `sym` | `derived.v_ovc_c1_features_v0_1` |
| `rng` | `derived.v_ovc_c1_features_v0_1` |
| `body_ratio` | `derived.v_ovc_c1_features_v0_1` |
| `rng_avg_6` | `derived.v_ovc_c2_features_v0_1` |
| `bar_close_ms` | `derived.v_ovc_c2_features_v0_1` |

**Output Fields:**

| Field | Type |
|-------|------|
| `block_id` | TEXT |
| `sym` | TEXT |
| `bar_close_ms` | BIGINT |
| `raw_score` | DOUBLE PRECISION |
| `z_score` | DOUBLE PRECISION |

**SQL File:** `sql/path1/scores/score_res_v1_0.sql`

---

### LID-v1.0 — Liquidity Interaction Density

| Attribute | Value |
|-----------|-------|
| Version | v1.0 |
| Description | Measures wick activity relative to body |
| Domain | [0, ∞) |

**Input Columns:**

| Column | Source View |
|--------|-------------|
| `block_id` | `derived.v_ovc_c1_features_v0_1` |
| `sym` | `derived.v_ovc_c1_features_v0_1` |
| `upper_wick_ratio` | `derived.v_ovc_c1_features_v0_1` |
| `lower_wick_ratio` | `derived.v_ovc_c1_features_v0_1` |
| `body_ratio` | `derived.v_ovc_c1_features_v0_1` |
| `bar_close_ms` | `derived.v_ovc_c2_features_v0_1` |

**Output Fields:**

| Field | Type |
|-------|------|
| `block_id` | TEXT |
| `sym` | TEXT |
| `bar_close_ms` | BIGINT |
| `raw_score` | DOUBLE PRECISION |
| `z_score` | DOUBLE PRECISION |

**SQL File:** `sql/path1/scores/score_lid_v1_0.sql`

---

## Summary Table

| Score | Version | Inputs | Domain | SQL File |
|-------|---------|--------|--------|----------|
| DIS | v1.1 | 4 columns | [0, 1] | `score_dis_v1_1.sql` |
| RES | v1.0 | 6 columns | [0, ∞) | `score_res_v1_0.sql` |
| LID | v1.0 | 6 columns | [0, ∞) | `score_lid_v1_0.sql` |

---

## References

| Document | Purpose |
|----------|---------|
| [SCORE_LIBRARY_v1.md](scores/SCORE_LIBRARY_v1.md) | Full definitions and formulas |
| [OPTION_B_PATH1_STATUS.md](OPTION_B_PATH1_STATUS.md) | Freeze status |
