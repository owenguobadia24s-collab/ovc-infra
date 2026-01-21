# Option C Charter v0.1

**[STATUS: ACTIVE]**

| Field          | Value                     |
|----------------|---------------------------|
| Version        | 0.1                       |
| Created        | 2026-01-20                |
| Author         | OVC Governance            |
| Depends On     | OPTION_B_CHARTER_v0.1.md  |
| Governed By    | GOVERNANCE_RULES_v0.1.md  |

---

## 1. Purpose of Option C

### 1.1 What Option C Represents

Option C is the **evaluation and outcome layer** of the OVC system. It is responsible for:

- **Outcome labeling**: Attaching forward-looking results to historical signals
- **Evaluation**: Measuring performance, accuracy, and expectancy
- **Consequence analysis**: Understanding what happened after signals occurred

Option C answers the question: *"What were the consequences of conditions described by Option B?"*

### 1.2 How Option C Differs from Option B

| Aspect         | Option B (Descriptive)              | Option C (Evaluative)               |
|----------------|-------------------------------------|-------------------------------------|
| Purpose        | Describe what IS                    | Evaluate what HAPPENED              |
| Temporal Scope | Point-in-time facts                 | Forward-looking outcomes            |
| Mutability     | CANONICAL and frozen                | Versioned and auditable             |
| Data Direction | Past → Present                      | Present → Future (retrospective)    |
| Truth Claim    | "This is the state"                 | "This was the result"               |

Option B is **descriptive**: it captures canonical facts about market state and derived features at a point in time.

Option C is **evaluative**: it measures outcomes, scores performance, and analyzes consequences—always retrospectively.

### 1.3 Why Option C is the ONLY Layer Allowed to Reference Results

Results (forward returns, excursions, outcomes) are fundamentally different from descriptions:

1. **Results require future data**: Outcome labeling necessarily looks forward
2. **Results are context-dependent**: The same signal may have different outcomes under different evaluation windows
3. **Results introduce bias risk**: Mixing results with descriptions enables lookahead contamination

By isolating all result-referencing logic in Option C, we guarantee that Option B remains a pure, replayable description of historical state with no future information leakage.

---

## 2. Allowed Inputs

### 2.1 Explicitly Allowed Sources

Option C MAY consume outputs from:

| Source | Description | Access Type |
|--------|-------------|-------------|
| **C1** | Canonical block-level facts | READ-ONLY |
| **C2** | Canonical derived features | READ-ONLY |
| **C3** | Canonical regime and context | READ-ONLY |

All inputs MUST be sourced from CANONICAL Option B outputs only.

### 2.2 Explicit Prohibition on Raw Block Access

Option C **SHALL NOT** directly access:

- `ovc.ovc_blocks_v01_1_min` (raw ingest table)
- Any raw ingestion artifacts
- R2 archive files
- Any source upstream of C1

**Rationale**: Option C evaluates meaning, not raw data. All semantic interpretation must flow through the canonical Option B pipeline.

### 2.3 Explicit Prohibition on Modifying Option B Outputs

Option C **SHALL NOT**:

- Write to any Option B table or view
- Modify C1, C2, or C3 outputs
- Create derived features that feed back into Option B
- Alter the schema or semantics of Option B artifacts

Option B is **immutable truth** from Option C's perspective.

---

## 3. Allowed Computations

Option C is authorized to perform the following categories of computation:

### 3.1 Outcome Labeling

- Forward return calculations (e.g., 1-block, 2-block, N-block returns)
- Maximum favorable excursion (MFE)
- Maximum adverse excursion (MAE)
- Time-to-target metrics
- Binary outcome classification (win/loss/neutral)

### 3.2 Evaluation Metrics

- Accuracy and hit rate calculations
- Expectancy computation
- Risk-adjusted performance metrics
- Stability and consistency measures
- Drawdown and recovery analysis

### 3.3 Regime-Conditioned Outcome Analysis

- Outcome stratification by C3 regime labels
- Performance breakdown by market context
- Conditional expectancy given regime state

### 3.4 Retrospective Scoring Only

**CRITICAL CONSTRAINT**: All Option C computations are **retrospective**.

Option C evaluates historical signals against known outcomes. It does not:

- Generate real-time scores
- Produce live trading signals
- Make forward-looking predictions

---

## 4. Explicit Prohibitions

### 4.1 No Feedback into Option B

Option C outputs **SHALL NOT** influence Option B computations. The data flow is strictly one-directional:

```
Option B (C1 → C2 → C3) → Option C
          ↑                    ↓
          └────── PROHIBITED ──┘
```

### 4.2 No Mutation of C1/C2/C3

Option C **SHALL NOT**:

- UPDATE any C1, C2, or C3 record
- DELETE any C1, C2, or C3 record
- ALTER any C1, C2, or C3 schema
- INSERT into any C1, C2, or C3 table

### 4.3 No Real-Time Decision Logic

Option C **SHALL NOT** contain:

- Live signal generation
- Real-time alerting based on outcomes
- Streaming evaluation pipelines
- Any logic that could influence live trading decisions

### 4.4 No Execution or Order Logic

Option C **SHALL NOT** contain:

- Order generation logic
- Position sizing algorithms
- Execution timing logic
- Broker integration code
- Any reference to order types, fills, or execution venues

### 4.5 No Optimization Loops Without Governance Approval

Option C **SHALL NOT** implement:

- Parameter optimization routines
- Walk-forward optimization
- Genetic algorithms or machine learning training loops
- Any automated search over outcome-maximizing configurations

**Exception**: Optimization may be authorized via explicit governance approval with documented safeguards against overfitting.

---

## 5. Guarantees

### 5.1 Clear Separation Between Description and Evaluation

Option C guarantees that:

- All descriptive logic remains in Option B
- All evaluative logic remains in Option C
- No hybrid computations exist that blur the boundary

### 5.2 Replayability and Auditability

Option C guarantees that:

- All outcome computations are deterministic given fixed inputs
- Outcome definitions are versioned and documented
- Historical evaluations can be reproduced exactly
- Audit trails exist for all outcome methodology changes

### 5.3 Versioned Outcome Definitions

Option C guarantees that:

- Each outcome metric has a unique version identifier
- Changes to outcome definitions create new versions (no in-place edits)
- Historical analyses reference specific outcome definition versions
- Outcome version lineage is maintained

### 5.4 No Leakage of Future Data into Option B

Option C guarantees that:

- No Option C output is consumed by Option B
- No forward-looking information contaminates descriptive layers
- The temporal integrity of Option B is preserved absolutely

---

## 6. Relationship to Option B

### 6.1 Option B is Immutable Truth

From Option C's perspective:

- Option B outputs are **facts**
- Option B outputs are **complete** (no supplementation allowed)
- Option B outputs are **final** (no correction or adjustment by Option C)

### 6.2 Option C May Evaluate But Never Redefine Meaning

Option C may ask: *"How did signals with this C3 regime label perform?"*

Option C may NOT ask: *"Should this signal have a different regime label based on its outcome?"*

Outcomes do not retroactively change descriptions.

### 6.3 Failures in Option C Do Not Invalidate Option B

If Option C:

- Produces incorrect outcome labels
- Has bugs in evaluation logic
- Generates misleading metrics

**Option B remains valid and unaffected.**

Option C failures are isolated. They require Option C fixes, not Option B changes.

---

## 7. Governance & Promotion Path

### 7.1 Outcome Definition Lifecycle

```
DRAFT → ACTIVE → CANONICAL
```

| Stage     | Meaning                                        | Requirements                          |
|-----------|------------------------------------------------|---------------------------------------|
| DRAFT     | Proposed outcome definition under development  | Documentation only                    |
| ACTIVE    | Approved for use in evaluation                 | Governance review, test coverage      |
| CANONICAL | Frozen, authoritative outcome definition       | Validation evidence, audit sign-off   |

### 7.2 Audit Requirements for Outcome Definitions

Before an outcome definition reaches CANONICAL status:

1. **Documentation**: Complete specification of calculation methodology
2. **Edge Cases**: Documented behavior for missing data, holidays, gaps
3. **Temporal Integrity**: Proof of no lookahead bias
4. **Reproducibility**: Evidence that outputs are deterministic
5. **Review**: Governance approval with sign-off record

### 7.3 Validation Evidence Requirements

CANONICAL promotion requires:

- Test cases covering normal and edge conditions
- Comparison against independent calculation (where feasible)
- Sample audit of randomly selected records
- Documentation of known limitations

---

## 8. Authorization

### 8.1 Design Authorization

**Option C is authorized for design.**

This charter establishes the boundary, intent, and constraints for Option C. Design of outcome definitions, evaluation schemas, and analysis pipelines may proceed within these bounds.

### 8.2 Implementation Requires Separate Approval

**Implementation of Option C logic requires separate approval.**

Before any Option C code (SQL, Python, or otherwise) is merged:

1. Specific outcome definitions must be documented
2. Schema designs must be reviewed
3. Governance must approve the implementation scope
4. Test plans must be established

This charter authorizes **what Option C is**. It does not authorize **building Option C**.

---

## Appendix A: Summary of Boundaries

| Category          | Option C MAY                          | Option C SHALL NOT                    |
|-------------------|---------------------------------------|---------------------------------------|
| **Inputs**        | Read C1, C2, C3 outputs               | Access raw blocks, modify Option B    |
| **Computation**   | Label outcomes, compute metrics       | Optimize without approval, predict    |
| **Temporal**      | Evaluate retrospectively              | Generate real-time signals            |
| **Execution**     | Score historical signals              | Generate orders, size positions       |
| **Feedback**      | Consume Option B                      | Feed back into Option B               |

---

## Appendix B: Document Control

| Version | Date       | Change Description              |
|---------|------------|---------------------------------|
| 0.1     | 2026-01-20 | Initial charter creation        |

---

**END OF CHARTER**
