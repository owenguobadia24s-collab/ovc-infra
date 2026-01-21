# C3 Semantic Contract (v0.1)

> **Status**: FROZEN  
> **Effective**: OVC v0.1  
> **Purpose**: Define invariants and rules for all C3 semantic tags to ensure determinism, provenance, and replay certification.

---

## 1. What Is a C3 Tag?

A **C3 tag** is a **semantic classification** derived from C1/C2 features and versioned threshold packs. C3 tags represent market regime interpretations, not raw metrics.

### Defining Characteristics

| Property | Requirement |
|----------|-------------|
| **Semantic** | Must represent a meaningful market state (e.g., TREND, REVERSAL, BREAKOUT) |
| **Non-primitive** | Cannot be a single arithmetic operation on OHLC |
| **Derived** | Must be computed from C1/C2 features only—never raw B-layer OHLC |
| **Discrete** | Must output a finite set of categorical values (not continuous) |
| **Deterministic** | Same inputs + same threshold pack = identical output, always |

### What C3 Is NOT

- ❌ A raw metric (use C1 for single-block, C2 for multi-block)
- ❌ A prediction or forecast
- ❌ A signal with external dependencies (news, sentiment, calendar)
- ❌ A mutable or adaptive classification

---

## 2. Mandatory Inputs

Every C3 tag MUST derive its classification from:

| Source | Examples | Notes |
|--------|----------|-------|
| **C1 Features** | `direction`, `range`, `body`, `ret`, `logret`, `body_ratio`, `close_pos`, `clv` | Single-block derived metrics |
| **C2 Features** | `hh_12`, `ll_12`, `roll_avg_range_12`, `range_z_12`, `sess_high`, `sess_low` | Multi-block/session features |
| **Threshold Pack** | Versioned config from `ovc_cfg.threshold_pack` | All semantic boundaries |

### Prohibited Inputs

| Source | Why Prohibited |
|--------|----------------|
| Raw OHLC from B-layer | Bypasses C1/C2 abstraction; breaks layering |
| TradingView-computed fields | External dependency; not replay-certifiable |
| Time-of-day heuristics | Leaks non-price information unless in C2 session features |
| External APIs/feeds | Non-deterministic; unavailable during replay |
| Inline magic numbers | Violates threshold provenance requirement |

---

## 3. Mandatory Outputs

Every C3 row MUST contain these columns:

| Column | Type | Purpose |
|--------|------|---------|
| `block_id` | TEXT | FK to B-layer (for joins) |
| `symbol` | TEXT | Trading symbol |
| `ts` | TIMESTAMPTZ | Block timestamp |
| `c3_<tag_name>` | TEXT | Classification value (discrete, finite set) |
| `threshold_pack_id` | TEXT | Pack ID from registry (NOT NULL) |
| `threshold_pack_version` | INT | Pack version used (NOT NULL) |
| `threshold_pack_hash` | TEXT | SHA256 of config (64 hex chars, NOT NULL) |
| `run_id` | UUID | Compute run identifier |
| `created_at` | TIMESTAMPTZ | Row creation timestamp |

### Provenance Columns Are NOT Optional

The `threshold_pack_*` columns enable:
- **Replay certification**: Re-run with same pack version, verify identical output
- **Audit trails**: Which thresholds produced which classifications?
- **Regression detection**: Did a threshold change cause unexpected shifts?

If any provenance column is NULL, the row is **invalid** and will fail B.2 validation.

---

## 4. Determinism Requirements

### The Determinism Guarantee

> Given identical C1/C2 inputs and identical threshold pack (id, version, hash), a C3 classifier MUST produce **byte-identical** output rows.

### Implementation Rules

1. **No randomness**: No `random()`, `uuid4()` in classification logic (run_id is separate)
2. **No floating-point ambiguity**: Use integer basis points, not float percentages
3. **No order-dependent aggregations**: Sort inputs before processing if order matters
4. **No external state**: Classification cannot depend on system time, file contents, or network calls
5. **No mutable thresholds**: All semantic boundaries come from immutable threshold pack

### Verification

Determinism is verified by the B.2 validator's quickcheck:
- Sample N blocks
- Recompute classification
- Compare against stored value
- Any mismatch = FAIL

---

## 5. Threshold Registry Usage Rules

### Rule 1: All Semantic Boundaries From Registry

```python
# ✅ CORRECT: Threshold from registry
if direction_ratio_bp >= config["min_direction_ratio_bp"]:
    return "TREND"

# ❌ WRONG: Inline magic number
if direction_ratio_bp >= 600:  # Where does 600 come from?
    return "TREND"
```

### Rule 2: Resolve Pack Before Compute

```python
# ✅ CORRECT: Resolve at start, use throughout
pack = get_active_pack(conn, pack_id, scope, symbol, timeframe)
config = pack["config_json"]
# ... use config for all decisions ...

# ❌ WRONG: Resolve mid-computation
for block in blocks:
    pack = get_active_pack(...)  # Re-resolving per block!
```

### Rule 3: Store Exact Provenance

```python
# ✅ CORRECT: Store what was actually used
row["threshold_pack_id"] = pack["pack_id"]
row["threshold_pack_version"] = pack["version"]
row["threshold_pack_hash"] = pack["config_hash"]

# ❌ WRONG: Hardcoded or missing
row["threshold_pack_id"] = "c3_regime_trend"  # What version?
row["threshold_pack_hash"] = None  # Cannot verify!
```

### Rule 4: Never Modify Active Pack Mid-Stream

If a compute run starts with pack v1, it MUST complete with pack v1. Activating v2 mid-run creates an audit nightmare.

---

## 6. Validation Requirements

Every C3 tag MUST pass B.2+C3 validation:

### Mandatory Checks

| Check | Failure Condition |
|-------|-------------------|
| Table exists | `derived.ovc_c3_<tag>_v*` not found |
| Provenance not null | Any `threshold_pack_*` column is NULL |
| Pack exists in registry | Referenced pack not in `ovc_cfg.threshold_pack` |
| Hash matches registry | Stored hash ≠ registry hash for (pack_id, version) |
| Values valid | Classification value not in allowed set |
| Coverage parity | Row count mismatch vs C1/C2 (if strict mode) |

### Running Validation

```powershell
python src/validate/validate_derived_range_v0_1.py \
  --symbol GBPUSD \
  --start-date 2026-01-13 \
  --end-date 2026-01-17 \
  --validate-c3 \
  --c3-classifiers c3_regime_trend
```

### Validation Artifacts

Successful validation produces:
- `derived_validation_report.json` (machine-readable)
- `derived_validation_report.md` (human-readable)
- Entry in `ovc_qa.derived_validation_run`

---

## 7. Prohibited Behaviors

### 7.1 TradingView Dependency

```python
# ❌ PROHIBITED: Using TV-computed fields
if block["tv_macd_signal"] > 0:
    return "TREND"
```

**Why**: TV fields are not available during historical replay; breaks certification.

### 7.2 Inline Heuristics

```python
# ❌ PROHIBITED: Magic numbers without provenance
TREND_THRESHOLD = 0.6  # Global constant
MIN_RANGE = 30  # Where did this come from?
```

**Why**: Cannot audit, version, or replay. Use threshold pack instead.

### 7.3 Mutable Thresholds

```python
# ❌ PROHIBITED: Thresholds that change during compute
class C3Classifier:
    def __init__(self):
        self.threshold = 0.5
    
    def adapt(self, recent_data):
        self.threshold = calculate_new_threshold(recent_data)  # MUTABLE!
```

**Why**: Non-deterministic; same inputs produce different outputs over time.

### 7.4 External Dependencies

```python
# ❌ PROHIBITED: Network calls, file reads, system state
response = requests.get("https://api.example.com/volatility")
if response.json()["vix"] > 20:
    return "HIGH_VOL"
```

**Why**: External state is non-reproducible.

### 7.5 Order-Dependent Side Effects

```python
# ❌ PROHIBITED: Classification depends on processing order
class StatefulClassifier:
    last_trend = None
    
    def classify(self, block):
        # Depends on what was classified before!
        if self.last_trend == "TREND":
            ...
```

**Why**: Parallel processing or reordering breaks determinism.

---

## 8. Schema Conventions

### Table Naming

```
derived.ovc_c3_<tag_name>_v<major>_<minor>
```

Examples:
- `derived.ovc_c3_regime_trend_v0_1`
- `derived.ovc_c3_reversal_v0_1`

### Primary Key

```sql
PRIMARY KEY (symbol, ts)
```

### Required Indexes

```sql
-- For B-layer joins
CREATE UNIQUE INDEX idx_c3_<tag>_block_id ON derived.ovc_c3_<tag>_v* (block_id);

-- For threshold audit
CREATE INDEX idx_c3_<tag>_threshold_pack ON derived.ovc_c3_<tag>_v* (threshold_pack_id, threshold_pack_version);

-- For run tracking
CREATE INDEX idx_c3_<tag>_run_id ON derived.ovc_c3_<tag>_v* (run_id);
```

### Classification Constraint

```sql
CONSTRAINT chk_c3_<tag>_valid CHECK (
    c3_<tag_name> IN ('VALUE1', 'VALUE2', ...)
)
```

---

## 9. Reference Implementation

The canonical reference for C3 implementation is:

```
src/derived/compute_c3_regime_trend_v0_1.py
```

All future C3 tags MUST follow the same patterns for:
- Threshold pack resolution
- C1/C2 data fetching
- Classification logic structure
- Provenance column population
- Upsert mechanics

---

## 10. Invariants Summary

| Invariant | Enforcement |
|-----------|-------------|
| C3 derives from C1/C2 only | Code review + no B-layer queries in C3 scripts |
| All thresholds from registry | Code review + no magic numbers |
| Provenance columns never NULL | SQL NOT NULL constraint + B.2 validation |
| Hash matches registry | B.2 validation check |
| Classification values finite | SQL CHECK constraint |
| Deterministic output | B.2 determinism quickcheck |
| No external dependencies | Code review + import restrictions |

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-01-18 | Initial contract specification |
