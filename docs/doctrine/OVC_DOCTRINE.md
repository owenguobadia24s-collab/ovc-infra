# OVC Doctrine

> **Purpose:** Define the epistemic boundaries of OVC to prevent category errors, overreach, and self-deception.

---

## What OVC Is

OVC is a system for recording market facts.

It captures **motion** (price changes), **structure** (candle geometry), **semantics** (named patterns and conditions), and **outcomes** (what happened next). Nothing more.

OVC is:

- **Descriptive** — It says what occurred, not what should occur
- **Evaluative** — It measures consequences, not quality
- **Deterministic** — Given the same inputs, it produces the same outputs
- **Replayable** — Any historical state can be reconstructed exactly
- **Versioned** — Changes are explicit, never silent

OVC is a truth-preserving engine. It does not improve truth. It does not optimize truth. It records truth and keeps it intact.

---

## What OVC Is Not

OVC is **not** a strategy. It does not tell you what to do.

OVC is **not** a signal generator. It does not say "buy" or "sell."

OVC is **not** a decision engine. It has no preferences.

OVC is **not** an optimizer. It does not search for better parameters.

OVC is **not** a trading system. It does not execute, manage risk, or allocate capital.

If you find yourself asking OVC "what should I do?"—you are asking the wrong system.

---

## Epistemic Layers

OVC has exactly two truth layers:

| Layer | Question Answered |
|-------|-------------------|
| **Option B** | "What is happening?" |
| **Option C** | "What happened after?" |

Option B describes the present: structure, motion, context, semantics.

Option C describes the future relative to that present: forward returns, excursions, realized volatility.

**Everything else is interpretation.** Strategy, edge, conviction, action—these belong to humans or to downstream systems that consume OVC outputs. They do not belong inside OVC.

---

## Rules of Engagement

1. **No feedback into canonical layers.** Performance results must never flow backward to change how facts are recorded or classified.

2. **No forward-looking logic outside Option C.** Only Option C is permitted to reference future data, and only for outcome measurement—never for description or classification.

3. **No mutation of truth for convenience.** If a definition is wrong, create a new version. Do not silently edit the past.

---

## Failure Modes to Avoid

**Backfitting outcomes into signals.**
If you notice that a certain pattern "works," you may be tempted to redefine the pattern to capture more of what works. This is fraud against yourself. The pattern meant what it meant before you knew the outcome.

**Letting performance redefine meaning.**
A "strong" candle is strong because of its geometry, not because it preceded a winning trade. If you start calling candles "strong" only when they win, you have destroyed the meaning of "strong."

**Smuggling decisions into descriptors.**
Descriptive layers must not contain hidden judgments. If a field name sounds like advice ("good_entry," "high_probability"), it does not belong in Option B. Names must describe, not prescribe.

---

## Statement of Intent

OVC exists to keep research honest.

Markets reward self-deception in the short term and punish it catastrophically in the long term. OVC is a tool for resisting the short-term reward.

By separating what happened from what we wish had happened, OVC makes it harder to lie to ourselves. By freezing meanings before we see outcomes, OVC prevents us from rewriting history to flatter our intuitions.

**Profit is downstream, not embedded.**

OVC does not promise profit. It does not contain profit. It provides the foundation upon which honest inquiry into profit becomes possible. What you build on that foundation is your responsibility.

---

*This doctrine governs the design, development, and use of OVC. Violations are not technical errors—they are epistemic errors, and they compromise everything downstream.*
