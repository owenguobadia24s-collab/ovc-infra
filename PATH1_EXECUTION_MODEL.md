# Path 1 Execution Model (Canonical)

**Contract:** This document is the canonical source of truth for Path 1 execution ergonomics. It documents **current behavior only** (no planned features).

---

## 1) The Three-Layer Model

- `reports/path1/evidence/RUN_QUEUE.csv` = **intent** (what is requested to run)
- Workflow = **execution** (what actually runs and under what gating rules)
  - `.github/workflows/path1_evidence_queue.yml`
  - `scripts/path1/run_evidence_queue.py`
- `reports/path1/evidence/INDEX.md` = **fact** (append-only ledger of what actually happened)

If it is not in `INDEX.md`, it did not happen.

---

## 2) What Happens Before Execution

- The workflow reads `RUN_QUEUE.csv` and selects rows that are **pending** (empty status or `pending`).
- Optional filters (`--run-id`, `--max-runs`) further reduce the set that will execute.
- Runs are executed **sequentially** by the runner.

Relationship:
- The queue is intent only; it is not authoritative and is not auto-committed by the workflow.
- The workflow is the execution path; it runs the runner with the selected queue rows.
- The ledger (`INDEX.md`) is the authoritative record of completed runs.

---

## 3) Skip Reasons (Non-Errors)

A run can be **skipped without error** for these reasons:

- **Queue empty** or no rows match `--run-id` filter.
- **Row status is not pending** (e.g., `complete` or `failed`) — the runner skips it.
- **Run folder already complete** (required artifacts already present) — the runner skips and can update `INDEX.md`.
- **Dry run mode** (`--dry-run`) — validates inputs and data availability without executing.
- **Max-runs limit** — rows beyond `--max-runs` are left unexecuted (not a failure).

**Not a skip (hard stop):** Missing prerequisites (e.g., no `DATABASE_URL`/`NEON_DSN`, missing `psql`) cause execution to stop with an error, not a skip.

---

## 4) Output Locations

- Run artifacts: `reports/path1/evidence/runs/<run_id>/`
- Canonical ledger (fact): `reports/path1/evidence/INDEX.md`
- The ledger is the authoritative pointer for what was executed and where to find outputs.

---

## 5) Date Normalization / Automatic Substitution

**Automatic substitution exists.**

If a requested date range has **zero rows**, the runner automatically substitutes a **nearest non-overlapping 5-day weekday range** with data.

Canonical dates are the **actual dates recorded in artifacts and `INDEX.md`**. The queue preserves the **requested** dates, which may differ.

This substitution is non-interactive (no prompt) and is recorded in run artifacts.

---

## 6) Evidence Pack Build Status

Evidence pack generation is **optional**.

- The runner can build Evidence Pack v0.2 when explicitly enabled (`--evidence-pack-v0-2` or `EVIDENCE_PACK_V0_2=1`).
- The workflow does **not** enable this by default.
- Some runs may therefore produce **partial artifacts** (no evidence pack directory).

No enforcement exists today; optional means optional.

---

## 7) Trajectory Family Selection (Canonical Rule)

When locating a trajectory for a given `(symbol, date_ny)`:

- Match on **symbol** and **date_ny**.
- Select the run with the **highest numeric NNN suffix** in the run_id (e.g., `p1_20260120_031` beats `p1_20260120_019`).

This is the canonical selection rule.
