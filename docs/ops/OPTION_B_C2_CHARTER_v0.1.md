# Option B – C2 Charter v0.1

**[STATUS: ACTIVE]**

| Field          | Value                          |
|----------------|--------------------------------|
| Version        | 0.1                            |
| Effective Date | 2026-01-20                     |
| Parent Charter | OPTION_B_CHARTER_v0.1.md       |
| Governance     | GOVERNANCE_RULES_v0.1.md       |
| Predecessor    | C1 (CANONICAL, frozen)         |

---

## 1. Purpose of C2

### 1.1 What C2 Represents

C2 is the **multi-bar / sequence-derived facts** layer within Option B. It computes contextual features that require information from multiple consecutive blocks, enabling temporal patterns and rolling statistics that cannot be expressed within a single-bar scope.

### 1.2 How C2 Differs from C1

| Aspect         | C1                              | C2                                      |
|----------------|--------------------------------|----------------------------------------|
| Scope          | Single-bar facts               | Multi-bar / sequence facts             |
| Input          | Canonical blocks only          | C1 outputs + canonical blocks          |
| Temporality    | Point-in-time                  | Window-based / rolling                 |
| Aggregation    | None                           | Fixed-window aggregations allowed      |
| Context        | Self-contained                 | Session-relative, sequence-aware       |

C1 answers: *"What happened in this block?"*  
C2 answers: *"What is the context surrounding this block?"*

### 1.3 Problem Statement

C2 exists to solve the following problem:

> Many meaningful market structure features require awareness of prior bars—volatility regimes, session position, rolling ranges, and sequence patterns. These cannot be computed within C1's single-bar boundary without violating its immutability and scope guarantees.

C2 provides a controlled, auditable layer where such multi-bar derivations can occur without contaminating the canonical single-bar fact layer.

---

## 2. Allowed Inputs

### 2.1 Explicit Source List

C2 **MAY** consume:

| Source                          | Status    | Justification                                      |
|---------------------------------|-----------|---------------------------------------------------|
| `derived.ovc_c1_*` outputs      | ALLOWED   | Primary input; C1 is canonical upstream           |
| `ovc.ovc_blocks_v01_1_min`      | ALLOWED   | Canonical blocks when C1 does not expose needed fields |

C2 **MAY NOT** consume:

| Source                          | Status     | Reason                                            |
|---------------------------------|------------|--------------------------------------------------|
| Any `ovc_qa.*` artifacts        | PROHIBITED | QA layer is not a fact source                    |
| External APIs at runtime        | PROHIBITED | Breaks replayability                             |
| Any C3 or downstream outputs    | PROHIBITED | Circular dependency                              |
| Raw R2 archives                 | PROHIBITED | Not validated; use canonical tables only         |

### 2.2 Window Size Constraints

| Constraint     | Value       | Rationale                                         |
|----------------|-------------|--------------------------------------------------|
| Minimum window | 2 bars      | Single-bar belongs to C1                         |
| Maximum window | 1 session   | Prevents unbounded memory; session = 12 blocks   |

Window sizes exceeding one session require explicit charter amendment and governance review.

### 2.3 Temporal Direction

**LOOKBACK ONLY.**

C2 computations must use only:
- The current bar
- Prior confirmed bars

C2 **MAY NOT** use:
- Future bars (lookahead)
- Unconfirmed bars
- Speculative data

This guarantees that C2 outputs are replayable from historical data without leakage.

---

## 3. Allowed Computations

C2 is authorized to perform the following computation classes:

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

C2 is **PROHIBITED** from the following:

### 4.1 Outcome Computation

- No forward return calculations
- No profit/loss attribution
- No target labeling

*Rationale: Outcomes belong exclusively to Option C.*

### 4.2 Thresholds and Decisions

- No "high volatility" / "low volatility" labels
- No "breakout" / "consolidation" classifications
- No regime determination

*Rationale: Threshold application belongs to C3 or Option C.*

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

### 4.5 C1 Mutation

- C2 may not alter, overwrite, or reinterpret C1 outputs
- C2 may not backfill or "correct" C1 values
- C2 must treat C1 as immutable input

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
| Historical replay                | C2 can be fully regenerated from C1 + blocks     |
| No external state                | No runtime API calls or cache dependencies       |
| Idempotent computation           | Re-running produces identical results            |

### 5.3 Versioning Guarantees

| Guarantee                        | Commitment                                        |
|----------------------------------|--------------------------------------------------|
| Semantic versioning              | Breaking changes increment major version         |
| Backward compatibility window    | Prior version available for 30 days post-deprecation |
| Version in output                | All C2 outputs carry version metadata            |

---

## 6. Relationship to C1

### 6.1 C1 Immutability

C1 is the **immutable upstream** for C2. C2:
- Reads C1 outputs as-is
- Does not transform C1 semantics
- Does not override C1 values

### 6.2 Semantic Boundary

C2 **MAY NOT** reinterpret C1 semantics. Examples:

| C1 Field       | C2 Allowed                     | C2 Prohibited                          |
|----------------|-------------------------------|---------------------------------------|
| `dir`          | Count consecutive dirs        | Relabel dir based on context          |
| `rng`          | Rolling avg of rng            | "Normalize" rng to different scale    |
| `body_rng_pct` | Compare across window         | Redefine body/range relationship      |

### 6.3 Failure Isolation

**C2 failures must not invalidate C1.**

- If C2 computation fails, C1 remains intact
- C2 errors are logged to `derived.*` error tables, not `ovc.*`
- Downstream consumers may fall back to C1-only mode

---

## 7. Governance & Audit Triggers

### 7.1 Audit Triggers

A C2 audit is required when:

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

C2 features begin as DRAFT and must demonstrate stability before ACTIVE promotion.

---

## 8. Authorization

This charter authorizes the **design** of C2 features under the constraints defined herein.

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
| Created        | 2026-01-20 | —          | Initial charter; C2 scope defined  |

---

**END OF CHARTER**
