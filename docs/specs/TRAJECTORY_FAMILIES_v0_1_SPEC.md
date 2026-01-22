# Trajectory Families v0.1 — Technical Specification

**Status Banner:** DRAFT — Describes intended design; current CLI implements fingerprint generation only (`emit-fingerprint`, `batch-fingerprints`). Clustering, naming, and gallery flows are **NOT IMPLEMENTED** in the CLI.

**Status:** DRAFT
**Version:** 0.1.0
**Author:** Principal Engineer + Research Taxonomist
**Date:** 2026-01-22
**Path:** 1 (Observation & Cataloging Only)

---

## Overview

This specification defines a deterministic taxonomy pipeline for cataloging recurring "shapes of motion" through the state-plane. A **Trajectory Family** is a cluster of days exhibiting similar 12-point trajectories (blocks A→L).

**Scope:** Descriptive cataloging only. No prediction, no signal generation, no edge claims.

**Metaphor:** A museum catalog of day-shapes, not a model.

**Note:** This spec is subordinate to the canonical Path 1 evidence flow; it does not define Path 1 execution.

---

## (1) DayFingerprint v0.1 — JSON Schema

### 1.1 Full JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "$id": "https://ovc.internal/schemas/day_fingerprint_v0_1.json",
  "title": "DayFingerprint",
  "description": "Structural fingerprint of a single trading day's trajectory through state-plane.",
  "type": "object",
  "required": [
    "schema_version",
    "fingerprint_id",
    "date_ny",
    "symbol",
    "timezone",
    "block_labels",
    "points",
    "quadrants",
    "quadrant_string",
    "path_geometry",
    "quadrant_dynamics",
    "source_artifacts",
    "params",
    "generated_at"
  ],
  "additionalProperties": false,
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "day_fingerprint_v0.1",
      "description": "Immutable schema version identifier"
    },
    "fingerprint_id": {
      "type": "string",
      "pattern": "^fp_[A-Z]{6}_[0-9]{8}_[a-f0-9]{8}$",
      "description": "Unique ID: fp_{SYMBOL}_{YYYYMMDD}_{hash8}",
      "examples": ["fp_GBPUSD_20221212_a3f8b2c1"]
    },
    "date_ny": {
      "type": "string",
      "format": "date",
      "description": "New York session date (YYYY-MM-DD)"
    },
    "symbol": {
      "type": "string",
      "pattern": "^[A-Z]{6}$",
      "description": "Currency pair (e.g., GBPUSD)"
    },
    "timezone": {
      "type": "string",
      "const": "America/New_York",
      "description": "Canonical timezone for session boundaries"
    },
    "block_labels": {
      "type": "array",
      "items": {"type": "string", "pattern": "^[A-L]$"},
      "minItems": 12,
      "maxItems": 12,
      "description": "Ordered block labels A through L"
    },
    "points": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["block", "x", "y"],
        "additionalProperties": false,
        "properties": {
          "block": {"type": "string", "pattern": "^[A-L]$"},
          "x": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
          "y": {"type": ["number", "null"], "minimum": -1, "maximum": 1}
        }
      },
      "minItems": 12,
      "maxItems": 12,
      "description": "12-point trajectory: (x_energy, y_shift) per block"
    },
    "quadrants": {
      "type": "array",
      "items": {
        "type": ["string", "null"],
        "enum": ["Q1", "Q2", "Q3", "Q4", null]
      },
      "minItems": 12,
      "maxItems": 12,
      "description": "Quadrant assignment per block (null if coords missing)"
    },
    "quadrant_string": {
      "type": "string",
      "pattern": "^(Q[1-4]|NULL)( (Q[1-4]|NULL)){11}$",
      "description": "Space-separated quadrant sequence",
      "examples": ["Q2 Q2 Q1 Q1 Q3 Q4 Q4 Q4 Q2 Q2 Q1 Q1"]
    },
    "path_geometry": {
      "type": "object",
      "required": [
        "path_length",
        "net_displacement",
        "efficiency",
        "turning",
        "jump_count",
        "energy_mean",
        "energy_std",
        "shift_mean",
        "shift_std"
      ],
      "additionalProperties": false,
      "properties": {
        "path_length": {
          "type": "number",
          "minimum": 0,
          "description": "Σ ||p_t - p_{t-1}|| for t=B..L"
        },
        "net_displacement": {
          "type": "number",
          "minimum": 0,
          "description": "||p_L - p_A|| (start to end distance)"
        },
        "efficiency": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "net_displacement / path_length (0 if path_length=0)"
        },
        "turning": {
          "type": "number",
          "minimum": 0,
          "description": "Σ |angle(v_{t-1}, v_t)| in radians for t=B..K"
        },
        "jump_count": {
          "type": "integer",
          "minimum": 0,
          "maximum": 11,
          "description": "Count of |Δy| > y_jump_threshold"
        },
        "energy_mean": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Mean of x values across 12 blocks"
        },
        "energy_std": {
          "type": "number",
          "minimum": 0,
          "description": "Std dev of x values"
        },
        "shift_mean": {
          "type": "number",
          "minimum": -1,
          "maximum": 1,
          "description": "Mean of y values across 12 blocks"
        },
        "shift_std": {
          "type": "number",
          "minimum": 0,
          "description": "Std dev of y values"
        }
      }
    },
    "quadrant_dynamics": {
      "type": "object",
      "required": [
        "q_counts",
        "q_transitions",
        "q_entropy",
        "q_runs_max"
      ],
      "additionalProperties": false,
      "properties": {
        "q_counts": {
          "type": "object",
          "required": ["Q1", "Q2", "Q3", "Q4"],
          "additionalProperties": false,
          "properties": {
            "Q1": {"type": "integer", "minimum": 0, "maximum": 12},
            "Q2": {"type": "integer", "minimum": 0, "maximum": 12},
            "Q3": {"type": "integer", "minimum": 0, "maximum": 12},
            "Q4": {"type": "integer", "minimum": 0, "maximum": 12}
          },
          "description": "Time spent in each quadrant (block count)"
        },
        "q_transitions": {
          "type": "object",
          "patternProperties": {
            "^Q[1-4]_Q[1-4]$": {"type": "integer", "minimum": 0}
          },
          "additionalProperties": false,
          "description": "Transition counts: Q_i→Q_j (16 possible, stored as Q1_Q1, Q1_Q2, ...)"
        },
        "q_entropy": {
          "type": "number",
          "minimum": 0,
          "maximum": 2,
          "description": "Shannon entropy of q_counts distribution (log base 2)"
        },
        "q_runs_max": {
          "type": "integer",
          "minimum": 1,
          "maximum": 12,
          "description": "Longest consecutive run in same quadrant"
        }
      }
    },
    "source_artifacts": {
      "type": "object",
      "required": ["trajectory_csv", "trajectory_png"],
      "additionalProperties": true,
      "properties": {
        "trajectory_csv": {
          "type": "string",
          "description": "Relative path to source trajectory.csv"
        },
        "trajectory_png": {
          "type": "string",
          "description": "Relative path to source trajectory.png"
        },
        "path_metrics_json": {
          "type": ["string", "null"],
          "description": "Relative path to path_metrics.json if available"
        },
        "evidence_pack_dir": {
          "type": ["string", "null"],
          "description": "Relative path to evidence pack directory if applicable"
        }
      }
    },
    "params": {
      "type": "object",
      "required": [
        "state_plane_version",
        "threshold_pack",
        "E_hi",
        "S_hi",
        "y_jump_threshold",
        "numeric_precision"
      ],
      "additionalProperties": false,
      "properties": {
        "state_plane_version": {
          "type": "string",
          "description": "State plane coordinate system version",
          "examples": ["v0.2"]
        },
        "threshold_pack": {
          "type": "string",
          "description": "Threshold pack identifier",
          "examples": ["state_plane_v0_2_default_v1"]
        },
        "E_hi": {
          "type": "number",
          "description": "Energy threshold for quadrant assignment"
        },
        "S_hi": {
          "type": "number",
          "description": "Shift threshold for quadrant assignment"
        },
        "y_jump_threshold": {
          "type": "number",
          "description": "Threshold for counting jumps in y"
        },
        "numeric_precision": {
          "type": "integer",
          "description": "Decimal places for rounding (6)"
        }
      }
    },
    "generated_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of fingerprint generation"
    },
    "content_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA-256 of canonical fingerprint content (excludes generated_at)"
    }
  }
}
```

### 1.2 Derived Field Specifications

#### y_jump_threshold Derivation Rule

**Definition:** `y_jump_threshold = 0.25` (constant)

**Rationale:** The y-axis range is [-1, +1], total span = 2.0. A jump of 0.25 represents 12.5% of the total range, capturing meaningful shift transitions while filtering noise. This is a fixed constant (not data-derived) to ensure determinism across all days.

**Alternative (data-derived, NOT used):** `y_jump_threshold = median(|Δy|) + 1.5 * IQR(|Δy|)` — rejected because it creates day-dependent thresholds that complicate cross-day comparison.

#### Quadrant Definitions

```
Given: E_hi = 0.6, S_hi = 0.35 (from threshold pack)
Given: x ∈ [0, 1] (energy), y ∈ [-1, 1] (shift)

Q1 (Expansion):    x >= E_hi  AND  |y| <= S_hi
Q2 (Consolidation): x <  E_hi  AND  |y| <= S_hi
Q3 (Reversal):     x >= E_hi  AND  |y| >  S_hi
Q4 (Retracement):  x <  E_hi  AND  |y| >  S_hi

NULL: Assigned when x or y is null/missing
```

**Visual Layout:**
```
        |y| > S_hi        |y| <= S_hi
      +--------------+----------------+
x>=E_hi|     Q3      |       Q1       |
      | (Reversal)   |  (Expansion)   |
      +--------------+----------------+
x<E_hi |     Q4      |       Q2       |
      |(Retracement) |(Consolidation) |
      +--------------+----------------+
```

#### Numeric Precision and Rounding Rules

| Field Category | Precision | Rule |
|----------------|-----------|------|
| Coordinates (x, y) | 6 decimals | `round(value, 6)` |
| Distances (path_length, net_displacement) | 6 decimals | `round(value, 6)` |
| Ratios (efficiency) | 6 decimals | `round(value, 6)` |
| Angles (turning) | 6 decimals | `round(radians, 6)` |
| Statistics (mean, std) | 6 decimals | `round(value, 6)` |
| Entropy | 6 decimals | `round(value, 6)` |
| Counts | Integer | No rounding |

**Canonical JSON serialization:**
```python
json.dumps(obj, sort_keys=True, indent=2, separators=(",", ": "))
```

---

## (2) Two Similarity Modes

**NOT IMPLEMENTED in current CLI.** Design-only specification for future clustering work.

### Mode A: Sequence Similarity (Quadrant Strings)

#### A.1: Levenshtein / Edit Distance

**Definition:** Edit distance on quadrant token sequences.

**Input:** Two quadrant sequences, each length 12, tokens ∈ {Q1, Q2, Q3, Q4, NULL}

**Formula:**
```
lev(s1, s2) = standard Levenshtein distance treating each quadrant as atomic token
normalized_lev(s1, s2) = lev(s1, s2) / max(len(s1), len(s2))
                       = lev(s1, s2) / 12
```

**Range:** [0, 1] where 0 = identical, 1 = completely different

**Distance matrix for similarity:**
```
d_edit(day_i, day_j) = normalized_lev(q_string_i, q_string_j)
```

**Pros:**
- Intuitive interpretation (number of "edits" to transform one day into another)
- Captures insertion/deletion/substitution patterns
- Works with NULL tokens naturally

**Cons:**
- Treats all quadrant swaps equally (Q1→Q2 same cost as Q1→Q4)
- Ignores geometric proximity between quadrants

#### A.2: Markov Transition Distance

**Definition:** Distance between 4×4 transition probability matrices.

**Construction:**
```
For each day, compute T[i,j] = count(Q_i → Q_j) / Σ_k count(Q_i → Q_k)
                             = q_transitions[Qi_Qj] / Σ_k q_transitions[Qi_Qk]

If row sum = 0 (quadrant never visited), use uniform: T[i,:] = [0.25, 0.25, 0.25, 0.25]
```

**Distance (Jensen-Shannon Divergence per row, averaged):**
```
JSD(P, Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
where M = 0.5 * (P + Q)
KL(P || Q) = Σ P(i) * log2(P(i) / Q(i))

d_markov(day_i, day_j) = (1/4) * Σ_{q ∈ {Q1,Q2,Q3,Q4}} JSD(T_i[q,:], T_j[q,:])
```

**Range:** [0, 1] where 0 = identical transition dynamics

**Pros:**
- Captures transition dynamics, not just sequence
- Robust to phase shifts (same pattern starting at different blocks)
- Handles sparse transitions gracefully

**Cons:**
- Loses temporal ordering information
- Two days with same transition frequencies but different sequences have distance 0
- Requires handling of zero-count rows

### Mode B: Shape Similarity (Point Paths)

#### B.1: Dynamic Time Warping (DTW) on 2D Sequences

**Definition:** DTW aligns two sequences allowing temporal warping.

**Input:** Two 12-point sequences P = [(x_1,y_1), ..., (x_12,y_12)]

**Point distance:**
```
d_point(p_i, q_j) = sqrt((p_i.x - q_j.x)² + (p_i.y - q_j.y)²)
```

**DTW computation:**
```
DTW[0,0] = 0
DTW[i,0] = ∞ for i > 0
DTW[0,j] = ∞ for j > 0
DTW[i,j] = d_point(P[i], Q[j]) + min(DTW[i-1,j], DTW[i,j-1], DTW[i-1,j-1])

d_dtw(P, Q) = DTW[12,12] / 12  (normalized by sequence length)
```

**Normalization (applied BEFORE DTW):**
- **Translation:** Translate centroid to origin: `p'_i = p_i - centroid(P)`
- **Scale:** Optional, **NOT applied by default** to preserve energy/shift magnitude information
- **Rotation:** **NOT applied** (coordinate axes are semantically meaningful)

**Pros:**
- Handles phase shifts and tempo variations
- Captures shape similarity even with timing differences
- Well-established algorithm with efficient implementations

**Cons:**
- Computationally more expensive (O(n²) per pair)
- May over-align dissimilar sequences
- Normalization choices affect results

#### B.2: Mean Squared Distance (MSD)

**Definition:** Point-wise Euclidean distance, averaged.

**Formula:**
```
d_msd(P, Q) = (1/12) * Σ_{t=1}^{12} ||P[t] - Q[t]||²
            = (1/12) * Σ_{t=1}^{12} ((P[t].x - Q[t].x)² + (P[t].y - Q[t].y)²)

For similarity, use RMSD:
d_rmsd(P, Q) = sqrt(d_msd(P, Q))
```

**Normalization:** Same as DTW (translate to centroid, no scale/rotation by default)

**Pros:**
- Simple, fast (O(n) per pair)
- Deterministic, no algorithmic choices
- Directly comparable to coordinate scales

**Cons:**
- Phase-sensitive (shift in timing = large distance)
- No tolerance for tempo variations

### Mode Selection for Clustering

**Primary:** Mode B.1 (DTW) with centroid translation
**Secondary:** Mode A.2 (Markov) for quadrant-dynamics clustering

**Rationale:** DTW captures geometric shape while tolerating minor phase variations between sessions. Markov provides a complementary view of transition dynamics.

---

## (3) Feature Vector for Clustering

**NOT IMPLEMENTED in current CLI.** Design-only specification for future clustering work.

### 3.1 Explicit Feature Vector Definition

The feature vector `X_day` is a 26-dimensional vector:

```python
X_day = [
    # Path geometry (8 features)
    path_length,           # [0] raw, then standardized
    net_displacement,      # [1] raw, then standardized
    efficiency,            # [2] already 0..1, standardize anyway
    turning,               # [3] raw radians, then standardized
    jump_count,            # [4] raw int → float, standardized
    energy_mean,           # [5] already 0..1, standardize
    energy_std,            # [6] raw, standardized
    shift_mean,            # [7] already -1..1, standardize
    shift_std,             # [8] raw, standardized

    # Quadrant counts (4 features) — normalized to proportions
    q1_proportion,         # [9]  q_counts.Q1 / 12
    q2_proportion,         # [10] q_counts.Q2 / 12
    q3_proportion,         # [11] q_counts.Q3 / 12
    q4_proportion,         # [12] q_counts.Q4 / 12

    # Quadrant dynamics (3 features)
    q_entropy,             # [13] already 0..2, standardize
    q_runs_max,            # [14] raw int → float / 12 (normalized)
    transition_entropy,    # [15] entropy of transition matrix (derived)

    # Dominant transition features (4 features) — top transition proportions
    self_transition_rate,  # [16] Σ T[i,i] / 4 (diagonal dominance)
    adjacent_trans_rate,   # [17] rate of "adjacent" transitions (Q1↔Q2, Q2↔Q4, etc.)
    diagonal_trans_rate,   # [18] rate of Q1↔Q4, Q2↔Q3 (opposite quadrant)
    stability_index,       # [19] q_runs_max / 12 * (1 - q_entropy/2)

    # Trajectory shape features (6 features)
    start_quadrant_enc,    # [20] one-hot proxy: Q1=0, Q2=0.33, Q3=0.67, Q4=1
    end_quadrant_enc,      # [21] same encoding for final quadrant
    x_trend,               # [22] linear regression slope of x over blocks (standardized)
    y_trend,               # [23] linear regression slope of y over blocks (standardized)
    x_range,               # [24] max(x) - min(x), standardized
    y_range,               # [25] max(y) - min(y), standardized
]
```

### 3.2 Standardization Rules

```python
# Standardization applied per-feature across the full dataset
for feature_idx in [0,1,2,3,4,5,6,7,8,13,22,23,24,25]:
    X[:, feature_idx] = (X[:, feature_idx] - mean) / std
    # If std = 0, set all values to 0

# Proportion features [9..12, 14, 16..19] are already normalized,
# but standardize for consistent scale:
for feature_idx in [9,10,11,12,14,16,17,18,19]:
    X[:, feature_idx] = (X[:, feature_idx] - mean) / std

# Categorical encodings [20, 21] are ordinal, standardize:
for feature_idx in [20, 21]:
    X[:, feature_idx] = (X[:, feature_idx] - mean) / std
```

### 3.3 Derived Feature Computations

```python
def compute_transition_entropy(q_transitions: dict) -> float:
    """Shannon entropy of flattened transition counts."""
    counts = [q_transitions.get(f"Q{i}_Q{j}", 0) for i in range(1,5) for j in range(1,5)]
    total = sum(counts)
    if total == 0:
        return 0.0
    probs = [c / total for c in counts]
    return -sum(p * math.log2(p) if p > 0 else 0 for p in probs)

def compute_self_transition_rate(q_transitions: dict) -> float:
    """Proportion of transitions that stay in same quadrant."""
    diagonal = sum(q_transitions.get(f"Q{i}_Q{i}", 0) for i in range(1,5))
    total = sum(q_transitions.values())
    return diagonal / total if total > 0 else 0.0

def compute_adjacent_transition_rate(q_transitions: dict) -> float:
    """Adjacent = Q1↔Q2, Q1↔Q3, Q2↔Q4, Q3↔Q4 (share edge in quadrant layout)."""
    adjacent_pairs = [("Q1","Q2"),("Q2","Q1"),("Q1","Q3"),("Q3","Q1"),
                      ("Q2","Q4"),("Q4","Q2"),("Q3","Q4"),("Q4","Q3")]
    adjacent = sum(q_transitions.get(f"{a}_{b}", 0) for a,b in adjacent_pairs)
    total = sum(q_transitions.values())
    return adjacent / total if total > 0 else 0.0

def compute_diagonal_transition_rate(q_transitions: dict) -> float:
    """Diagonal = Q1↔Q4, Q2↔Q3 (opposite corners)."""
    diagonal_pairs = [("Q1","Q4"),("Q4","Q1"),("Q2","Q3"),("Q3","Q2")]
    diag = sum(q_transitions.get(f"{a}_{b}", 0) for a,b in diagonal_pairs)
    total = sum(q_transitions.values())
    return diag / total if total > 0 else 0.0

def compute_trend_slope(values: list) -> float:
    """Linear regression slope over block indices 0..11."""
    n = len(values)
    x_indices = list(range(n))
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in x_indices)
    return numerator / denominator if denominator > 0 else 0.0
```

### 3.4 Feature Vector Index Reference

| Index | Name | Source | Normalization |
|-------|------|--------|---------------|
| 0 | path_length | path_geometry | z-score |
| 1 | net_displacement | path_geometry | z-score |
| 2 | efficiency | path_geometry | z-score |
| 3 | turning | path_geometry | z-score |
| 4 | jump_count | path_geometry | z-score |
| 5 | energy_mean | path_geometry | z-score |
| 6 | energy_std | path_geometry | z-score |
| 7 | shift_mean | path_geometry | z-score |
| 8 | shift_std | path_geometry | z-score |
| 9 | q1_proportion | q_counts.Q1 / 12 | z-score |
| 10 | q2_proportion | q_counts.Q2 / 12 | z-score |
| 11 | q3_proportion | q_counts.Q3 / 12 | z-score |
| 12 | q4_proportion | q_counts.Q4 / 12 | z-score |
| 13 | q_entropy | quadrant_dynamics | z-score |
| 14 | q_runs_max_norm | q_runs_max / 12 | z-score |
| 15 | transition_entropy | derived | z-score |
| 16 | self_transition_rate | derived | z-score |
| 17 | adjacent_trans_rate | derived | z-score |
| 18 | diagonal_trans_rate | derived | z-score |
| 19 | stability_index | derived | z-score |
| 20 | start_quadrant_enc | quadrants[0] | z-score |
| 21 | end_quadrant_enc | quadrants[11] | z-score |
| 22 | x_trend | derived | z-score |
| 23 | y_trend | derived | z-score |
| 24 | x_range | derived | z-score |
| 25 | y_range | derived | z-score |

---

## (4) Clustering Strategy

**NOT IMPLEMENTED in current CLI.** Design-only specification for future clustering work.

### 4.1 Primary Algorithm: k-Medoids (PAM)

**Choice:** k-Medoids via PAM (Partitioning Around Medoids)

**Rationale:**
- Medoids are actual data points → interpretable representatives
- Robust to outliers (unlike k-means)
- Stable under re-runs with fixed seed
- Works with precomputed distance matrices

### 4.2 Algorithm Parameters

```python
CLUSTERING_PARAMS = {
    "algorithm": "kmedoids_pam",
    "n_clusters": "auto",           # See selection rule below
    "n_clusters_range": (5, 15),    # Search range for automatic selection
    "distance_metric": "euclidean", # On standardized feature vector
    "max_iter": 300,
    "random_state": 42,             # FIXED SEED for determinism
    "init": "k-medoids++",          # Deterministic initialization with seed
}
```

### 4.3 Cluster Count Selection

**Method:** Silhouette score maximization within range

```python
def select_optimal_k(X: np.ndarray, k_range: tuple) -> int:
    """Select k that maximizes average silhouette score."""
    scores = {}
    for k in range(k_range[0], k_range[1] + 1):
        labels = kmedoids(X, n_clusters=k, random_state=42)
        scores[k] = silhouette_score(X, labels)

    # Select k with highest silhouette, prefer smaller k on ties
    best_k = min(k for k, s in scores.items() if s == max(scores.values()))
    return best_k
```

**Override:** User can specify `--n-clusters N` to bypass automatic selection.

### 4.4 Output Requirements

#### Family Assignment Output

```json
{
  "family_id": "TF-03",
  "family_name": "TF-03: Consolidation-Dominant / Low-Volatility",
  "medoid_day": "fp_GBPUSD_20221214_b7c9d3e1",
  "medoid_date_ny": "2022-12-14",
  "family_size": 47,
  "family_proportion": 0.156,
  "members": ["fp_GBPUSD_20221212_a3f8b2c1", "fp_GBPUSD_20221214_b7c9d3e1", ...],
  "centroid_features": {
    "efficiency_mean": 0.342,
    "q2_proportion_mean": 0.583,
    ...
  },
  "intra_cluster_distance_mean": 2.341,
  "intra_cluster_distance_std": 0.892
}
```

#### Medoid Selection

**Definition:** The medoid is the family member minimizing sum of distances to all other members.

```python
def find_medoid(member_indices: list, distance_matrix: np.ndarray) -> int:
    """Return index of member with minimum total distance to others."""
    min_dist = float('inf')
    medoid_idx = member_indices[0]
    for i in member_indices:
        total_dist = sum(distance_matrix[i, j] for j in member_indices if j != i)
        if total_dist < min_dist:
            min_dist = total_dist
            medoid_idx = i
    return medoid_idx
```

### 4.5 Outlier / Noise Handling

**Strategy:** Silhouette-based outlier detection

```python
OUTLIER_THRESHOLD = -0.1  # Silhouette score below this = outlier

def identify_outliers(X: np.ndarray, labels: np.ndarray) -> list:
    """Identify points with negative silhouette scores."""
    sample_scores = silhouette_samples(X, labels)
    return [i for i, score in enumerate(sample_scores) if score < OUTLIER_THRESHOLD]
```

**Outlier Family:**
- `family_id`: `TF-00`
- `family_name`: `TF-00: Unclustered / Atypical`
- `medoid_day`: `null` (no representative)
- Members are listed but not used for family characterization

---

## (5) Family Naming Scheme

**NOT IMPLEMENTED in current CLI.** Design-only specification for future clustering work.

### 5.1 Canonical Naming Format

```
TF-{NN}: {PrimaryShape} / {KeySignature}
```

- `TF`: Trajectory Family prefix
- `NN`: Two-digit family ID (01-99), 00 reserved for outliers
- `PrimaryShape`: Dominant geometric/behavioral pattern (1-3 words)
- `KeySignature`: Distinguishing characteristic (1-3 words)

### 5.2 Algorithmic Naming Rules

```python
def generate_family_name(family_stats: dict) -> str:
    """Deterministic name generation from family centroid statistics."""

    # Extract centroid features
    q1_prop = family_stats["q1_proportion_mean"]
    q2_prop = family_stats["q2_proportion_mean"]
    q3_prop = family_stats["q3_proportion_mean"]
    q4_prop = family_stats["q4_proportion_mean"]
    efficiency = family_stats["efficiency_mean"]
    turning = family_stats["turning_mean"]
    path_length = family_stats["path_length_mean"]
    x_trend = family_stats["x_trend_mean"]
    y_trend = family_stats["y_trend_mean"]
    q_entropy = family_stats["q_entropy_mean"]
    self_trans = family_stats["self_transition_rate_mean"]

    # Determine PrimaryShape
    dominant_q = max([("Q1", q1_prop), ("Q2", q2_prop),
                      ("Q3", q3_prop), ("Q4", q4_prop)], key=lambda x: x[1])

    if dominant_q[1] >= 0.5:
        # Single quadrant dominance
        shape_map = {
            "Q1": "Expansion-Dominant",
            "Q2": "Consolidation-Dominant",
            "Q3": "Reversal-Dominant",
            "Q4": "Retracement-Dominant"
        }
        primary_shape = shape_map[dominant_q[0]]
    elif efficiency >= 0.6:
        primary_shape = "Directional-Trend"
    elif turning >= 6.0:  # ~3.4 radians = high turning
        primary_shape = "Oscillating"
    elif path_length <= 1.0:  # Low total movement
        primary_shape = "Stationary"
    elif q_entropy >= 1.8:  # High entropy = visits all quadrants
        primary_shape = "Wandering"
    else:
        primary_shape = "Mixed-Regime"

    # Determine KeySignature
    signatures = []

    if self_trans >= 0.6:
        signatures.append("Sticky")
    elif self_trans <= 0.2:
        signatures.append("Volatile")

    if abs(x_trend) >= 0.05:
        signatures.append("Energy-Trending" if x_trend > 0 else "Energy-Fading")

    if abs(y_trend) >= 0.05:
        signatures.append("Shift-Trending" if y_trend > 0 else "Shift-Fading")

    if efficiency <= 0.2:
        signatures.append("Low-Efficiency")
    elif efficiency >= 0.7:
        signatures.append("High-Efficiency")

    if path_length >= 3.0:
        signatures.append("High-Activity")
    elif path_length <= 1.0:
        signatures.append("Low-Activity")

    # Select top signature (priority order above)
    key_signature = signatures[0] if signatures else "Typical"

    return f"{primary_shape} / {key_signature}"
```

### 5.3 Example Family Names

| ID | Name | Triggering Criteria |
|----|------|---------------------|
| TF-00 | Unclustered / Atypical | Silhouette score < -0.1 |
| TF-01 | Consolidation-Dominant / Sticky | Q2 proportion ≥ 0.5, self_trans ≥ 0.6 |
| TF-02 | Expansion-Dominant / High-Activity | Q1 proportion ≥ 0.5, path_length ≥ 3.0 |
| TF-03 | Directional-Trend / High-Efficiency | efficiency ≥ 0.6, efficiency ≥ 0.7 |
| TF-04 | Oscillating / Volatile | turning ≥ 6.0, self_trans ≤ 0.2 |
| TF-05 | Reversal-Dominant / Shift-Trending | Q3 proportion ≥ 0.5, y_trend ≥ 0.05 |
| TF-06 | Wandering / Low-Efficiency | q_entropy ≥ 1.8, efficiency ≤ 0.2 |
| TF-07 | Stationary / Low-Activity | path_length ≤ 1.0, path_length ≤ 1.0 |
| TF-08 | Retracement-Dominant / Energy-Fading | Q4 proportion ≥ 0.5, x_trend < -0.05 |
| TF-09 | Mixed-Regime / Typical | No dominant pattern, no strong signature |

### 5.4 ID Assignment Stability

**Rule:** Family IDs are assigned by descending family size, then by lexicographic order of medoid fingerprint_id on ties.

```python
def assign_stable_family_ids(clusters: dict) -> dict:
    """Assign TF-NN IDs in stable, deterministic order."""
    # Sort by (-size, medoid_fingerprint_id) for stability
    sorted_clusters = sorted(
        clusters.items(),
        key=lambda x: (-x[1]["size"], x[1]["medoid_fingerprint_id"])
    )

    result = {}
    for idx, (_, cluster_data) in enumerate(sorted_clusters):
        family_id = f"TF-{idx+1:02d}"  # TF-01, TF-02, ...
        result[family_id] = cluster_data
    return result
```

---

## (6) File Layout + Artifacts

**PARTIALLY IMPLEMENTED.** Fingerprint outputs and index.csv exist; clustering/gallery artifacts are **NOT IMPLEMENTED** in the CLI.

### 6.1 Directory Structure

```
reports/path1/trajectory_families/
├── v0.1/                              # Version directory
│   ├── README.md                       # Version documentation
│   ├── params.json                     # Frozen parameters for this version
│   │
│   ├── fingerprints/                   # Per-day fingerprints
│   │   ├── index.csv                   # Master index (one row per day)
│   │   ├── GBPUSD/                     # Per-symbol subdirectory
│   │   │   ├── 2022/                   # Per-year subdirectory
│   │   │   │   ├── fp_GBPUSD_20221212_a3f8b2c1.json
│   │   │   │   ├── fp_GBPUSD_20221213_c4e9f2d3.json
│   │   │   │   └── ...
│   │   │   └── 2023/
│   │   │       └── ...
│   │   └── EURUSD/
│   │       └── ...
│   │
│   ├── clusters/                       # Clustering outputs
│   │   ├── GBPUSD/                     # Per-symbol clustering
│   │   │   ├── cluster_run_20260122_143052.json   # Timestamped run metadata
│   │   │   ├── families_summary.json              # Canonical summary (latest)
│   │   │   ├── families_table.csv                 # Flat table export
│   │   │   └── assignments.csv                    # fingerprint_id → family_id mapping
│   │   └── EURUSD/
│   │       └── ...
│   │
│   ├── gallery/                        # Visualization outputs
│   │   ├── GBPUSD/
│   │   │   ├── by_family/              # Grouped by family
│   │   │   │   ├── TF-01/
│   │   │   │   │   ├── medoid_fp_GBPUSD_20221214_b7c9d3e1.png
│   │   │   │   │   ├── fp_GBPUSD_20221212_a3f8b2c1.png
│   │   │   │   │   └── ...
│   │   │   │   ├── TF-02/
│   │   │   │   │   └── ...
│   │   │   │   └── TF-00/              # Outliers
│   │   │   │       └── ...
│   │   │   ├── medoids/                # One plot per family medoid
│   │   │   │   ├── TF-01_medoid.png
│   │   │   │   ├── TF-02_medoid.png
│   │   │   │   └── ...
│   │   │   └── overview/               # Summary visualizations
│   │   │       ├── family_sizes.png
│   │   │       ├── feature_distributions.png
│   │   │       └── cluster_scatter.png
│   │   └── EURUSD/
│   │       └── ...
│   │
│   └── audit/                          # Reproducibility artifacts
│       ├── feature_matrix.npy          # Raw feature matrix (for verification)
│       ├── distance_matrix.npy         # Pairwise distances
│       ├── standardization_params.json # Mean/std per feature
│       └── run_log.jsonl               # Append-only execution log
```

### 6.2 File Specifications

#### fingerprints/index.csv

```csv
fingerprint_id,date_ny,symbol,trajectory_csv_path,fingerprint_json_path,path_length,efficiency,dominant_quadrant,family_id,content_hash
fp_GBPUSD_20221212_a3f8b2c1,2022-12-12,GBPUSD,runs/p1_20260120_031/outputs/state_plane_v0_2/trajectory.csv,fingerprints/GBPUSD/2022/fp_GBPUSD_20221212_a3f8b2c1.json,2.341567,0.456789,Q2,TF-03,a3f8b2c1d5e9f7a2...
```

**Columns:**
- `fingerprint_id`: Unique identifier
- `date_ny`: Session date
- `symbol`: Currency pair
- `trajectory_csv_path`: Relative path to source trajectory
- `fingerprint_json_path`: Relative path to fingerprint JSON
- `path_length`: Quick-reference metric
- `efficiency`: Quick-reference metric
- `dominant_quadrant`: Mode of quadrant sequence
- `family_id`: Assigned family (may be empty if not yet clustered)
- `content_hash`: SHA-256 of fingerprint content

#### families_summary.json

```json
{
  "schema_version": "trajectory_families_v0.1",
  "symbol": "GBPUSD",
  "generated_at": "2026-01-22T14:30:52Z",
  "clustering_params": {
    "algorithm": "kmedoids_pam",
    "n_clusters": 8,
    "distance_metric": "euclidean",
    "random_state": 42
  },
  "dataset_stats": {
    "total_days": 301,
    "date_range": ["2022-12-01", "2023-12-31"],
    "days_with_missing_blocks": 5,
    "days_excluded": 2
  },
  "silhouette_score": 0.423,
  "families": [
    {
      "family_id": "TF-01",
      "family_name": "TF-01: Consolidation-Dominant / Sticky",
      "medoid_fingerprint_id": "fp_GBPUSD_20221214_b7c9d3e1",
      "medoid_date_ny": "2022-12-14",
      "size": 47,
      "proportion": 0.156,
      "centroid_features": {...},
      "intra_cluster_stats": {...}
    },
    ...
  ],
  "outliers": {
    "family_id": "TF-00",
    "family_name": "TF-00: Unclustered / Atypical",
    "size": 12,
    "proportion": 0.040,
    "member_ids": [...]
  }
}
```

#### families_table.csv

```csv
family_id,family_name,medoid_id,medoid_date,size,proportion,efficiency_mean,path_length_mean,q1_prop,q2_prop,q3_prop,q4_prop,silhouette_mean
TF-01,Consolidation-Dominant / Sticky,fp_GBPUSD_20221214_b7c9d3e1,2022-12-14,47,0.156,0.342,1.876,0.083,0.583,0.125,0.208,0.512
TF-02,Expansion-Dominant / High-Activity,fp_GBPUSD_20230115_d8e7f6a5,2023-01-15,39,0.130,0.567,3.214,0.487,0.231,0.154,0.128,0.478
...
```

### 6.3 Naming Conventions

| Artifact Type | Convention | Example |
|---------------|------------|---------|
| Fingerprint JSON | `fp_{SYMBOL}_{YYYYMMDD}_{hash8}.json` | `fp_GBPUSD_20221212_a3f8b2c1.json` |
| Cluster run | `cluster_run_{YYYYMMDD}_{HHMMSS}.json` | `cluster_run_20260122_143052.json` |
| Medoid plot | `TF-{NN}_medoid.png` | `TF-01_medoid.png` |
| Gallery plot | `{fingerprint_id}.png` or `medoid_{fingerprint_id}.png` | `fp_GBPUSD_20221212_a3f8b2c1.png` |

**Canonical vs Generated:**
- `families_summary.json` — canonical (represents current state)
- `cluster_run_*.json` — generated (historical record of each run)
- `index.csv` — canonical (single source of truth, updated in place)

---

## (7) Implementation Plan

### 7.1 Modules / Files

```
trajectory_families/
├── fingerprint.py              # DayFingerprint computation
├── distance.py                 # Similarity utilities (library-only)
├── features.py                 # Feature vector utilities (library-only)
├── clustering.py               # Clustering utilities (library-only)
├── naming.py                   # Naming utilities (library-only)
├── gallery.py                  # Gallery utilities (library-only)
├── schema.py                   # Fingerprint schema + validation
└── params_v0_1.json             # Default parameters

scripts/path1/
└── run_trajectory_families.py  # CLI entry point (emit-fingerprint, batch-fingerprints only)

tests/
├── test_fingerprint.py
├── test_fingerprint_determinism.py
└── fixtures/
    ├── golden_fingerprint_v0_1.json
    ├── golden_feature_vector.npy
    └── golden_cluster_assignments.csv

# NOT IMPLEMENTED: test_trajectory_similarity.py, test_trajectory_clustering.py, test_trajectory_naming.py
```

### 7.2 CLI Commands

**Current CLI scope:** `emit-fingerprint` and `batch-fingerprints` only. Other commands below are **NOT IMPLEMENTED** in the CLI.

#### emit-fingerprint (single day)

```bash
python scripts/path1/run_trajectory_families.py emit-fingerprint \
    --symbol GBPUSD \
    --date 2022-12-12 \
    --trajectory-csv reports/path1/evidence/runs/p1_20260120_031/outputs/state_plane_v0_2/trajectory.csv \
    --output-dir reports/path1/trajectory_families/v0.1/fingerprints/GBPUSD/2022/ \
    --params-file trajectory_families/params_v0_1.json
```

**Output:** Single fingerprint JSON + updates index.csv

#### batch-fingerprints (date range)

```bash
python scripts/path1/run_trajectory_families.py batch-fingerprints \
    --symbol GBPUSD \
    --date-from 2022-12-01 \
    --date-to 2023-12-31 \
    --evidence-dir reports/path1/evidence/runs/ \
    --output-dir reports/path1/trajectory_families/v0.1/ \
    --params-file trajectory_families/params_v0_1.json \
    --parallel 4
```

**Output:** Multiple fingerprint JSONs + updates index.csv

#### cluster (build families) — NOT IMPLEMENTED

This command is not wired in `scripts/path1/run_trajectory_families.py`.

#### generate-gallery — NOT IMPLEMENTED

This command is not wired in `scripts/path1/run_trajectory_families.py`.

### 7.3 Determinism Controls

```python
# trajectory_families/params_v0_1.json
{
  "version": "trajectory_families_v0.1",
  "fingerprint": {
    "state_plane_version": "v0.2",
    "threshold_pack": "state_plane_v0_2_default_v1",
    "y_jump_threshold": 0.25,
    "numeric_precision": 6
  },
  "clustering": {
    "algorithm": "kmedoids_pam",
    "n_clusters_range": [5, 15],
    "distance_metric": "euclidean",
    "random_state": 42,
    "outlier_threshold": -0.1
  },
  "feature_vector": {
    "version": "v0.1",
    "dimension": 26,
    "standardize": true
  }
}
```

**Determinism guarantees:**
1. Fixed `random_state=42` for all stochastic operations
2. Sorted outputs (by fingerprint_id, by date, by family_id)
3. Fixed numeric precision (6 decimals)
4. Canonical JSON serialization (`sort_keys=True`)
5. Stable family ID assignment (by size desc, then medoid_id)

### 7.4 Unit Tests + Golden Fixtures

#### Test Strategy

| Test File | Coverage |
|-----------|----------|
| `test_fingerprint.py` | Field computation, schema validation, edge cases |
| `test_fingerprint_determinism.py` | Re-run produces identical output |
| `test_trajectory_similarity.py` | DTW, Levenshtein, Markov distance correctness |
| `test_trajectory_clustering.py` | k-medoids, family assignment, outlier detection |
| `test_trajectory_naming.py` | Deterministic name generation |

#### Golden Fixtures

```python
# tests/fixtures/golden_fingerprint_v0_1.json
# Pre-computed fingerprint for known trajectory data
# Used to verify computation stability across code changes

def test_fingerprint_matches_golden():
    trajectory = load_test_trajectory("fixtures/sample_trajectory.csv")
    fp = compute_fingerprint(trajectory, params=FROZEN_PARAMS)
    golden = json.load(open("fixtures/golden_fingerprint_v0_1.json"))

    # Compare all fields except generated_at
    fp_comparable = {k: v for k, v in fp.items() if k != "generated_at"}
    golden_comparable = {k: v for k, v in golden.items() if k != "generated_at"}
    assert fp_comparable == golden_comparable

def test_feature_vector_determinism():
    fp = json.load(open("fixtures/golden_fingerprint_v0_1.json"))
    fv = compute_feature_vector(fp)
    golden_fv = np.load("fixtures/golden_feature_vector.npy")
    np.testing.assert_array_almost_equal(fv, golden_fv, decimal=6)
```

### 7.5 Definition of Done

**HISTORICAL planning checklist — not authoritative for current implementation.**

**PR #1: Fingerprint Infrastructure**
- [ ] `fingerprint.py` with `compute_fingerprint()` function
- [ ] JSON schema validation against `day_fingerprint_v0_1.json`
- [ ] `fingerprint_batch.py` with parallel processing
- [ ] CLI commands: `emit-fingerprint`, `batch-fingerprints`
- [ ] `index.csv` generation and update logic
- [ ] Unit tests with >90% coverage
- [ ] Golden fixture test passing
- [ ] Determinism test (re-run over same data = identical output)
- [ ] Documentation in `docs/specs/TRAJECTORY_FAMILIES_v0_1_SPEC.md`

**PR #2: Clustering + Gallery (NOT IMPLEMENTED)**
- [ ] `trajectory_similarity.py` with DTW, Levenshtein, Markov
- [ ] `trajectory_clustering.py` with k-medoids, silhouette selection
- [ ] `trajectory_naming.py` with deterministic naming
- [ ] `trajectory_gallery.py` with plot organization
- [ ] CLI commands: `cluster`, `generate-gallery`
- [ ] `families_summary.json`, `families_table.csv` generation
- [ ] Outlier handling (TF-00 family)
- [ ] Unit tests for clustering stability
- [ ] Integration test: full pipeline from trajectories → gallery
- [ ] Audit artifacts (feature_matrix.npy, standardization_params.json)

---

## (8) Pseudocode / Code Skeletons

### 8.1 compute_fingerprint

```python
def compute_fingerprint(
    points: List[Dict[str, float]],
    energy_values: List[float],
    shift_values: List[float],
    params: Dict,
    source_artifacts: Dict[str, str],
    date_ny: str,
    symbol: str,
) -> Dict:
    """
    Compute DayFingerprint v0.1 from trajectory data.

    Args:
        points: List of 12 dicts with keys 'block', 'x', 'y'
        energy_values: List of 12 x (energy) values (for validation)
        shift_values: List of 12 y (shift) values (for validation)
        params: Parameter dict with thresholds and precision
        source_artifacts: Paths to source files
        date_ny: Session date (YYYY-MM-DD)
        symbol: Currency pair (e.g., GBPUSD)

    Returns:
        Dict conforming to DayFingerprint v0.1 schema
    """
    precision = params["numeric_precision"]
    E_hi = params["E_hi"]
    S_hi = params["S_hi"]
    y_jump_thr = params["y_jump_threshold"]

    # Validate input
    assert len(points) == 12, f"Expected 12 points, got {len(points)}"

    # Extract coordinates
    x_vals = [p["x"] for p in points]
    y_vals = [p["y"] for p in points]

    # Compute quadrants
    quadrants = compute_quadrant_sequence(x_vals, y_vals, E_hi, S_hi)
    quadrant_string = " ".join(q if q else "NULL" for q in quadrants)

    # Compute path geometry
    path_length = compute_path_length(x_vals, y_vals, precision)
    net_displacement = compute_net_displacement(x_vals, y_vals, precision)
    efficiency = round(net_displacement / path_length, precision) if path_length > 0 else 0.0
    turning = compute_turning(x_vals, y_vals, precision)
    jump_count = compute_jump_count(y_vals, y_jump_thr)

    energy_mean = round(safe_mean(x_vals), precision)
    energy_std = round(safe_std(x_vals), precision)
    shift_mean = round(safe_mean(y_vals), precision)
    shift_std = round(safe_std(y_vals), precision)

    # Compute quadrant dynamics
    q_counts = compute_quadrant_counts(quadrants)
    q_transitions = compute_transition_counts(quadrants)
    q_entropy = compute_quadrant_entropy(q_counts, precision)
    q_runs_max = compute_max_run_length(quadrants)

    # Build fingerprint
    fingerprint = {
        "schema_version": "day_fingerprint_v0.1",
        "fingerprint_id": generate_fingerprint_id(symbol, date_ny),
        "date_ny": date_ny,
        "symbol": symbol,
        "timezone": "America/New_York",
        "block_labels": ["A","B","C","D","E","F","G","H","I","J","K","L"],
        "points": [
            {"block": p["block"], "x": round(p["x"], precision) if p["x"] is not None else None,
             "y": round(p["y"], precision) if p["y"] is not None else None}
            for p in points
        ],
        "quadrants": quadrants,
        "quadrant_string": quadrant_string,
        "path_geometry": {
            "path_length": path_length,
            "net_displacement": net_displacement,
            "efficiency": efficiency,
            "turning": turning,
            "jump_count": jump_count,
            "energy_mean": energy_mean,
            "energy_std": energy_std,
            "shift_mean": shift_mean,
            "shift_std": shift_std,
        },
        "quadrant_dynamics": {
            "q_counts": q_counts,
            "q_transitions": q_transitions,
            "q_entropy": q_entropy,
            "q_runs_max": q_runs_max,
        },
        "source_artifacts": source_artifacts,
        "params": {
            "state_plane_version": params["state_plane_version"],
            "threshold_pack": params["threshold_pack"],
            "E_hi": E_hi,
            "S_hi": S_hi,
            "y_jump_threshold": y_jump_thr,
            "numeric_precision": precision,
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    # Compute content hash (excludes generated_at)
    fingerprint["content_hash"] = compute_content_hash(fingerprint)

    return fingerprint
```

### 8.2 compute_quadrant_string

```python
def compute_quadrant_sequence(
    x_vals: List[Optional[float]],
    y_vals: List[Optional[float]],
    E_hi: float,
    S_hi: float,
) -> List[Optional[str]]:
    """
    Assign quadrant labels to each point.

    Q1 (Expansion):    x >= E_hi AND |y| <= S_hi
    Q2 (Consolidation): x <  E_hi AND |y| <= S_hi
    Q3 (Reversal):     x >= E_hi AND |y| >  S_hi
    Q4 (Retracement):  x <  E_hi AND |y| >  S_hi
    """
    quadrants = []
    for x, y in zip(x_vals, y_vals):
        if x is None or y is None:
            quadrants.append(None)
            continue

        high_energy = x >= E_hi
        low_shift = abs(y) <= S_hi

        if high_energy and low_shift:
            quadrants.append("Q1")
        elif not high_energy and low_shift:
            quadrants.append("Q2")
        elif high_energy and not low_shift:
            quadrants.append("Q3")
        else:  # not high_energy and not low_shift
            quadrants.append("Q4")

    return quadrants
```

### 8.3 compute_transition_counts

```python
def compute_transition_counts(quadrants: List[Optional[str]]) -> Dict[str, int]:
    """
    Count transitions between quadrants.

    Returns dict with keys like "Q1_Q1", "Q1_Q2", etc.
    Only counts transitions between non-null quadrants.
    """
    # Initialize all 16 possible transitions to 0
    transitions = {}
    for q_from in ["Q1", "Q2", "Q3", "Q4"]:
        for q_to in ["Q1", "Q2", "Q3", "Q4"]:
            transitions[f"{q_from}_{q_to}"] = 0

    # Count transitions
    for i in range(len(quadrants) - 1):
        q_from = quadrants[i]
        q_to = quadrants[i + 1]
        if q_from is not None and q_to is not None:
            transitions[f"{q_from}_{q_to}"] += 1

    return transitions
```

### 8.4 compute_feature_vector

```python
def compute_feature_vector(fingerprint: Dict) -> np.ndarray:
    """
    Extract 26-dimensional feature vector from fingerprint.

    Returns raw (unstandardized) feature vector.
    """
    pg = fingerprint["path_geometry"]
    qd = fingerprint["quadrant_dynamics"]
    points = fingerprint["points"]
    quadrants = fingerprint["quadrants"]

    # Path geometry features [0-8]
    features = [
        pg["path_length"],
        pg["net_displacement"],
        pg["efficiency"],
        pg["turning"],
        float(pg["jump_count"]),
        pg["energy_mean"],
        pg["energy_std"],
        pg["shift_mean"],
        pg["shift_std"],
    ]

    # Quadrant proportions [9-12]
    qc = qd["q_counts"]
    total_q = sum(qc.values())
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        features.append(qc[q] / 12.0)  # Normalize by max possible

    # Quadrant dynamics [13-15]
    features.append(qd["q_entropy"])
    features.append(qd["q_runs_max"] / 12.0)
    features.append(compute_transition_entropy(qd["q_transitions"]))

    # Transition features [16-19]
    qt = qd["q_transitions"]
    features.append(compute_self_transition_rate(qt))
    features.append(compute_adjacent_transition_rate(qt))
    features.append(compute_diagonal_transition_rate(qt))
    features.append(compute_stability_index(qd["q_runs_max"], qd["q_entropy"]))

    # Trajectory shape features [20-25]
    features.append(encode_quadrant(quadrants[0]))   # Start quadrant
    features.append(encode_quadrant(quadrants[11]))  # End quadrant

    x_vals = [p["x"] for p in points if p["x"] is not None]
    y_vals = [p["y"] for p in points if p["y"] is not None]

    features.append(compute_trend_slope(x_vals))
    features.append(compute_trend_slope(y_vals))
    features.append(max(x_vals) - min(x_vals) if x_vals else 0.0)
    features.append(max(y_vals) - min(y_vals) if y_vals else 0.0)

    return np.array(features, dtype=np.float64)


def encode_quadrant(q: Optional[str]) -> float:
    """Encode quadrant as ordinal value."""
    encoding = {"Q1": 0.0, "Q2": 0.333, "Q3": 0.667, "Q4": 1.0, None: 0.5}
    return encoding.get(q, 0.5)


def compute_stability_index(q_runs_max: int, q_entropy: float) -> float:
    """Stability = normalized run length * inverse entropy."""
    return (q_runs_max / 12.0) * (1.0 - q_entropy / 2.0)
```

### 8.5 cluster_days

```python
def cluster_days(
    feature_matrix: np.ndarray,
    fingerprint_ids: List[str],
    params: Dict,
) -> Dict:
    """
    Cluster days using k-medoids.

    Args:
        feature_matrix: (N, 26) array of feature vectors
        fingerprint_ids: List of N fingerprint IDs
        params: Clustering parameters

    Returns:
        Dict with cluster assignments and metadata
    """
    from sklearn_extra.cluster import KMedoids
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score, silhouette_samples

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feature_matrix)

    # Determine optimal k
    k_range = params["n_clusters_range"]
    random_state = params["random_state"]

    if params.get("n_clusters") == "auto":
        best_k, best_score = None, -1
        for k in range(k_range[0], k_range[1] + 1):
            km = KMedoids(n_clusters=k, metric="euclidean",
                          random_state=random_state, method="pam")
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            if score > best_score:
                best_k, best_score = k, score
        n_clusters = best_k
    else:
        n_clusters = params["n_clusters"]

    # Final clustering
    km = KMedoids(n_clusters=n_clusters, metric="euclidean",
                  random_state=random_state, method="pam")
    labels = km.fit_predict(X_scaled)

    # Identify outliers
    sample_silhouettes = silhouette_samples(X_scaled, labels)
    outlier_threshold = params.get("outlier_threshold", -0.1)
    outlier_mask = sample_silhouettes < outlier_threshold

    # Build cluster info
    clusters = {}
    for cluster_id in range(n_clusters):
        member_mask = (labels == cluster_id) & ~outlier_mask
        member_indices = np.where(member_mask)[0]
        member_ids = [fingerprint_ids[i] for i in member_indices]

        if len(member_indices) == 0:
            continue

        # Find medoid (actual data point minimizing intra-cluster distance)
        medoid_idx = find_medoid_index(X_scaled, member_indices)

        clusters[cluster_id] = {
            "member_indices": member_indices.tolist(),
            "member_ids": member_ids,
            "medoid_index": medoid_idx,
            "medoid_id": fingerprint_ids[medoid_idx],
            "size": len(member_ids),
            "centroid_features": X_scaled[member_indices].mean(axis=0).tolist(),
            "silhouette_mean": sample_silhouettes[member_indices].mean(),
        }

    # Outliers
    outlier_indices = np.where(outlier_mask)[0]
    outlier_ids = [fingerprint_ids[i] for i in outlier_indices]

    return {
        "clusters": clusters,
        "outliers": {
            "member_indices": outlier_indices.tolist(),
            "member_ids": outlier_ids,
            "size": len(outlier_ids),
        },
        "n_clusters": n_clusters,
        "silhouette_score": silhouette_score(X_scaled, labels),
        "standardization": {
            "mean": scaler.mean_.tolist(),
            "std": scaler.scale_.tolist(),
        },
    }
```

### 8.6 assign_family_ids

```python
def assign_family_ids(cluster_result: Dict) -> Dict:
    """
    Assign stable family IDs (TF-01, TF-02, ...) based on size and medoid ID.

    Outliers are assigned TF-00.
    """
    clusters = cluster_result["clusters"]

    # Sort clusters by (-size, medoid_id) for stable ordering
    sorted_items = sorted(
        clusters.items(),
        key=lambda x: (-x[1]["size"], x[1]["medoid_id"])
    )

    families = {}

    # Assign TF-01, TF-02, ... to regular clusters
    for idx, (old_id, cluster_data) in enumerate(sorted_items):
        family_id = f"TF-{idx + 1:02d}"
        families[family_id] = {
            **cluster_data,
            "family_id": family_id,
        }

    # Assign TF-00 to outliers
    outliers = cluster_result["outliers"]
    if outliers["size"] > 0:
        families["TF-00"] = {
            **outliers,
            "family_id": "TF-00",
            "medoid_id": None,
            "medoid_index": None,
        }

    return families
```

### 8.7 generate_gallery

```python
def generate_gallery(
    families: Dict,
    fingerprint_index: pd.DataFrame,
    source_plots_dir: Path,
    output_dir: Path,
) -> Dict[str, int]:
    """
    Organize trajectory plots into family galleries.

    Returns count of plots organized per family.
    """
    counts = {}

    for family_id, family_data in families.items():
        family_dir = output_dir / "by_family" / family_id
        family_dir.mkdir(parents=True, exist_ok=True)

        member_ids = family_data.get("member_ids", [])
        medoid_id = family_data.get("medoid_id")

        for fp_id in member_ids:
            # Look up source plot path
            row = fingerprint_index[fingerprint_index["fingerprint_id"] == fp_id]
            if row.empty:
                continue

            source_plot = find_trajectory_plot(row.iloc[0], source_plots_dir)
            if source_plot is None or not source_plot.exists():
                continue

            # Determine destination name
            if fp_id == medoid_id:
                dest_name = f"medoid_{fp_id}.png"
            else:
                dest_name = f"{fp_id}.png"

            dest_path = family_dir / dest_name
            shutil.copy2(source_plot, dest_path)

        counts[family_id] = len(list(family_dir.glob("*.png")))

        # Also copy medoid to medoids/ directory
        if medoid_id:
            medoids_dir = output_dir / "medoids"
            medoids_dir.mkdir(parents=True, exist_ok=True)
            medoid_source = family_dir / f"medoid_{medoid_id}.png"
            if medoid_source.exists():
                shutil.copy2(medoid_source, medoids_dir / f"{family_id}_medoid.png")

    return counts
```

---

## (9) Failure Modes + Mitigations

### 9.1 Missing Blocks

**Failure:** Day has fewer than 12 blocks (missing A-L).

**Detection:**
```python
if len(points) != 12:
    raise ValueError(f"Expected 12 blocks, got {len(points)} for {date_ny}")
```

**Mitigation:**
- **Option A (strict):** Exclude day from fingerprinting. Log to `excluded_days.csv` with reason.
- **Option B (lenient):** Fill missing blocks with `null` coordinates. Mark in fingerprint metadata.

**Default:** Option A (strict). Days with missing blocks are not comparable.

### 9.2 NaN/Null Coordinates

**Failure:** Block exists but x or y is null/NaN.

**Detection:**
```python
null_count = sum(1 for p in points if p["x"] is None or p["y"] is None)
```

**Mitigation:**
- If `null_count <= 2`: Proceed with null quadrants, exclude nulls from geometry calculations.
- If `null_count > 2`: Exclude day (too many missing points for meaningful fingerprint).

**In geometry calculations:**
```python
def safe_mean(values: List[Optional[float]]) -> float:
    valid = [v for v in values if v is not None and math.isfinite(v)]
    return sum(valid) / len(valid) if valid else 0.0
```

### 9.3 Degenerate path_length = 0

**Failure:** All points identical (no movement).

**Detection:**
```python
if path_length == 0:
    efficiency = 0.0  # Avoid division by zero
```

**Mitigation:**
- Set `efficiency = 0.0` (convention: stationary path has zero efficiency).
- Day is still valid for clustering (represents "stationary" family).
- Log warning but do not exclude.

### 9.4 Drift in Scaling/Thresholds

**Failure:** Threshold pack changes between runs, breaking comparability.

**Detection:**
```python
if fingerprint["params"]["threshold_pack"] != current_params["threshold_pack"]:
    raise ValueError("Threshold pack mismatch: fingerprints not comparable")
```

**Mitigation:**
- Fingerprints store their `params` block, enabling version checks.
- Clustering validates all fingerprints use identical params before proceeding.
- Different threshold packs require separate `v0.1a/`, `v0.1b/` version directories.

### 9.5 Unstable Cluster Ordering

**Failure:** Re-running clustering produces different family IDs.

**Detection:**
```python
# Compare assignments.csv between runs
diff_count = (old_assignments["family_id"] != new_assignments["family_id"]).sum()
```

**Mitigation:**
- Fixed `random_state=42` in k-medoids.
- Family ID assignment by deterministic sort key: `(-size, medoid_fingerprint_id)`.
- Store `cluster_run_*.json` for each run to audit changes.

### 9.6 Silhouette Score Instability

**Failure:** Different k selected on slightly different data.

**Detection:**
- Log silhouette scores for all k in range.
- Alert if top-2 scores are within 0.01.

**Mitigation:**
- When scores are tied within tolerance (0.01), prefer smaller k.
- Allow manual `--n-clusters N` override for stability.

### 9.7 Empty Clusters

**Failure:** k-medoids produces cluster with 0 members.

**Detection:**
```python
if len(member_indices) == 0:
    continue  # Skip empty cluster
```

**Mitigation:**
- Empty clusters are dropped from output.
- Family IDs are assigned only to non-empty clusters.
- Final n_clusters in output may be less than requested.

### 9.8 Extreme Outliers Dominating

**Failure:** Many days flagged as outliers (TF-00 > 20% of data).

**Detection:**
```python
outlier_proportion = outliers["size"] / total_days
if outlier_proportion > 0.2:
    log_warning(f"High outlier rate: {outlier_proportion:.1%}")
```

**Mitigation:**
- Review outlier threshold parameter.
- Consider: data quality issues, insufficient k, or genuine diversity.
- TF-00 members are preserved for manual review.

### 9.9 Feature Vector Dimension Mismatch

**Failure:** Code change alters feature vector dimension.

**Detection:**
```python
assert feature_vector.shape == (26,), f"Expected 26 features, got {feature_vector.shape}"
```

**Mitigation:**
- Version bump required for any feature vector change.
- Golden fixture tests catch dimension changes.
- Schema includes `feature_vector.dimension: 26`.

### 9.10 Filesystem Path Issues (Windows/Unix)

**Failure:** Path separators cause cross-platform issues.

**Mitigation:**
```python
from pathlib import Path

# Always use forward slashes in stored paths
relative_path = str(path.relative_to(base)).replace("\\", "/")
```

- All stored paths use forward slashes (POSIX style).
- `pathlib.Path` handles OS conversion on read.

---

## Appendix A: Constants and Magic Numbers

| Constant | Value | Rationale |
|----------|-------|-----------|
| `BLOCK_COUNT` | 12 | Fixed NY session structure (A-L) |
| `NUMERIC_PRECISION` | 6 | Balance between precision and reproducibility |
| `Y_JUMP_THRESHOLD` | 0.25 | 12.5% of y-axis range [-1, +1] |
| `E_HI_DEFAULT` | 0.6 | Energy threshold from state_plane_v0_2 |
| `S_HI_DEFAULT` | 0.35 | Shift threshold from state_plane_v0_2 |
| `OUTLIER_THRESHOLD` | -0.1 | Silhouette score below this = outlier |
| `K_RANGE_DEFAULT` | (5, 15) | Reasonable family count for ~300 days |
| `RANDOM_STATE` | 42 | Fixed seed for reproducibility |
| `FEATURE_DIMENSION` | 26 | Current feature vector size |

---

## Appendix B: Schema Evolution Policy

1. **Non-breaking changes** (e.g., adding optional fields): Increment patch version (v0.1.0 → v0.1.1).
2. **Breaking changes** (e.g., changing field semantics, removing fields): Increment minor version (v0.1 → v0.2).
3. **Old fingerprints remain valid** in their version directory.
4. **Cross-version clustering is prohibited.** All fingerprints in a cluster run must share schema_version.

---

*End of Specification*
