# Option B – L2 Charter v0.1

**[STATUS: ACTIVE]**

| Field          | Value                          |
|----------------|--------------------------------|
| Version        | 0.1                            |
| Effective Date | 2026-01-20                     |
| Parent Charter | OPTION_B_CHARTER_v0.1.md       |
| Governance     | GOVERNANCE_RULES_v0.1.md       |
| Predecessor    | L1 (CANONICAL, frozen)         |

---

## 1. Purpose of L2

### 1.1 What L2 Represents

L2 is the **multi-bar / sequence-derived facts** layer within Option B. It computes contextual features that require information from multiple consecutive blocks, enabling temporal patterns and rolling statistics that cannot be expressed within a single-bar scope.

### 1.2 How L2 Differs from L1

| Aspect         | L1                              | L2                                      |
|----------------|--------------------------------|----------------------------------------|
| Scope          | Single-bar facts               | Multi-bar / sequence facts             |
| Input          | Canonical blocks only          | L1 outputs + canonical blocks          |
| Temporality    | Point-in-time                  | Window-based / rolling                 |
| Aggregation    | None                           | Fixed-window aggregations allowed      |
| Context        | Self-contained                 | Session-relative, sequence-aware       |

L1 answers: *"What happened in this block?"*  
L2 answers: *"What is the context surrounding this block?"*

### 1.3 Problem Statement

L2 exists to solve the following problem:

> Many meaningful market structure features require awareness of prior bars—volatility regimes, session position, rolling ranges, and sequence patterns. These cannot be computed within L1's single-bar boundary without violating its immutability and scope guarantees.

L2 provides a controlled, auditable layer where such multi-bar derivations can occur without contaminating the canonical single-bar fact layer.

---

## 2. Allowed Inputs

### 2.1 Explicit Source List

L2 **MAY** consume:

| Source                          | Status    | Justification                                      |
|---------------------------------|-----------|---------------------------------------------------|
| `derived.ovc_l1_*` outputs      | ALLOWED   | Primary input; L1 is canonical upstream           |
| `ovc.ovc_blocks_v01_1_min`      | ALLOWED   | Canonical blocks when L1 does not expose needed fields |

L2 **MAY NOT** consume:

| Source                          | Status     | Reason                                            |
|---------------------------------|------------|--------------------------------------------------|
| Any `ovc_qa.*` artifacts        | PROHIBITED | QA layer is not a fact source                    |
| External APIs at runtime        | PROHIBITED | Breaks replayability                             |
| Any L3 or downstream outputs    | PROHIBITED | Circular dependency                              |
| Raw R2 archives                 | PROHIBITED | Not validated; use canonical tables only         |

### 2.2 Window Size Constraints

| Constraint     | Value       | Rationale                                         |
|----------------|-------------|--------------------------------------------------|
| Minimum window | 2 bars      | Single-bar belongs to L1                         |
| Maximum window | 1 session   | Prevents unbounded memory; session = 12 blocks   |

Window sizes exceeding one session require explicit charter amendment and governance review.

### 2.3 Temporal Direction

**LOOKBACK ONLY.**

L2 computations must use only:
- The current bar
- Prior confirmed bars

L2 **MAY NOT** use:
- Future bars (lookahead)
- Unconfirmed bars
- Speculative data

This guarantees that L2 outputs are replayable from historical data without leakage.

---

## 3. Allowed Computations

L2 is authorized to perform the following computation classes:

### 3.1 Rolling Statistics

- Rolling mean, median, standard deviation
- Rolling min/max over fixed windows
- Rolling percentile ranks
- Exponential moving averages (with decay bounds)

### 3.2 Session-Relative Context

- Position within session (block index 1-12)
- Session open reference values
- Cumulative session metrics (range, direction count)
- Distance from session high/low

### 3.3 Sequence Classification (Non-Semantic)

- Consecutive direction counts (e.g., 3 consecutive up bars)
- Pattern presence flags (no semantic interpretation)
- Streak length calculations

### 3.4 Fixed-Window Aggregations

- N-bar range expansion/contraction
- N-bar directional consistency
- N-bar volume/volatility profiles (when source fields exist)

---

## 4. Explicit Prohibitions

L2 is **PROHIBITED** from the following:

### 4.1 Outcome Computation

- No forward return calculations
- No profit/loss attribution
- No target labeling

*Rationale: Outcomes belong exclusively to Option C.*

### 4.2 Thresholds and Decisions

- No "high volatility" / "low volatility" labels
- No "breakout" / "consolidation" classifications
- No regime determination

*Rationale: Threshold application belongs to L3 or Option C.*

### 4.3 Signals or Labels

- No buy/sell signals
- No entry/exit markers
- No quality scores or ratings

*Rationale: Signal generation is downstream of Option B entirely.*

### 4.4 Write Scope

- **ALLOWED:** `derived.*` schema only
- **PROHIBITED:** `ovc.*` schema (canonical facts)
- **PROHIBITED:** `ovc_qa.*` schema (QA artifacts)
- **PROHIBITED:** Any external system writes

### 4.5 L1 Mutation

- L2 may not alter, overwrite, or reinterpret L1 outputs
- L2 may not backfill or "correct" L1 values
- L2 must treat L1 as immutable input

---

## 5. Guarantees to Downstream Layers

### 5.1 Stability Guarantees

| Guarantee                        | Commitment                                        |
|----------------------------------|--------------------------------------------------|
| Schema stability                 | Column removals require version bump + migration |
| Computation determinism          | Same inputs → same outputs (no randomness)       |
| Null handling                    | Explicit; nulls propagate predictably            |

### 5.2 Replayability Guarantees

| Guarantee                        | Commitment                                        |
|----------------------------------|--------------------------------------------------|
| Historical replay                | L2 can be fully regenerated from L1 + blocks     |
| No external state                | No runtime API calls or cache dependencies       |
| Idempotent computation           | Re-running produces identical results            |

### 5.3 Versioning Guarantees

| Guarantee                        | Commitment                                        |
|----------------------------------|--------------------------------------------------|
| Semantic versioning              | Breaking changes increment major version         |
| Backward compatibility window    | Prior version available for 30 days post-deprecation |
| Version in output                | All L2 outputs carry version metadata            |

---

## 6. Relationship to L1

### 6.1 L1 Immutability

L1 is the **immutable upstream** for L2. L2:
- Reads L1 outputs as-is
- Does not transform L1 semantics
- Does not override L1 values

### 6.2 Semantic Boundary

L2 **MAY NOT** reinterpret L1 semantics. Examples:

| L1 Field       | L2 Allowed                     | L2 Prohibited                          |
|----------------|-------------------------------|---------------------------------------|
| `dir`          | Count consecutive dirs        | Relabel dir based on context          |
| `rng`          | Rolling avg of rng            | "Normalize" rng to different scale    |
| `body_rng_pct` | Compare across window         | Redefine body/range relationship      |

### 6.3 Failure Isolation

**L2 failures must not invalidate L1.**

- If L2 computation fails, L1 remains intact
- L2 errors are logged to `derived.*` error tables, not `ovc.*`
- Downstream consumers may fall back to L1-only mode

---

## 7. Governance & Audit Triggers

### 7.1 Audit Triggers

A L2 audit is required when:

| Trigger                          | Action Required                                   |
|----------------------------------|--------------------------------------------------|
| New window size > 6 bars         | Justification + performance review               |
| New input source requested       | Charter amendment + governance approval          |
| Computation touches price directly| Review for outcome leakage                       |
| Schema breaking change           | Version bump + migration plan                    |

### 7.2 Experiment vs Violation

| Category    | Definition                                         | Response                              |
|-------------|---------------------------------------------------|---------------------------------------|
| Experiment  | Temporary deviation with explicit scope & expiry  | Document in trial log; time-bounded   |
| Violation   | Unauthorized breach of charter prohibitions       | Immediate rollback; incident review   |

Experiments must:
- Be documented before execution
- Have explicit end date
- Not violate hard prohibitions (§4)

### 7.3 Promotion Path

```
DRAFT → ACTIVE → CANONICAL
```

| Stage     | Meaning                                            | Requirements                          |
|-----------|----------------------------------------------------|---------------------------------------|
| DRAFT     | Under development; not consumed downstream         | None                                  |
| ACTIVE    | Stable; may be consumed by downstream layers       | Passes validation; documented         |
| CANONICAL | Immutable reference; breaking changes prohibited   | 30-day stability + governance sign-off|

L2 features begin as DRAFT and must demonstrate stability before ACTIVE promotion.

---

## 8. Authorization

This charter authorizes the **design** of L2 features under the constraints defined herein.

**What is authorized:**
- Feature specification documents
- Schema design proposals
- Validation criteria definition

**What is NOT authorized by this charter:**
- SQL implementation
- View or table creation
- Production deployment

Implementation authorization requires separate approval per GOVERNANCE_RULES_v0.1.md.

---

## 9. Document Control

| Action         | Date       | Author     | Notes                              |
|----------------|------------|------------|------------------------------------|
| Created        | 2026-01-20 | —          | Initial charter; L2 scope defined  |

---

**END OF CHARTER**
