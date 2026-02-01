# TradingView Reference Contract v0.1 (OVC-Aligned)

**TRADINGVIEW_REFERENCE_CONTRACT_VERSION**: v0.1
**Status**: DRAFT
**Date**: 2026-01-30

---

## Scope & Intent

### What this contract governs

This contract governs **TradingView-originated metrics, panels, and overlays** as a **reference-only** layer:

- How TradingView outputs may be ingested (optionally), stored (non-authoritative), and compared against OVC-derived outputs.
- How TradingView outputs may be used for parity checks, visualization, and diagnostics without contaminating Option A truth or Option B/C determinism.
- The explicit boundary that TradingView outputs are **not computation authority** and do not change Option A or Option B contracts.

### What it explicitly does NOT govern

- **Option A1 bar ingest** or **Option A2 event ingest** mechanics beyond the existing contracts.
- Any redefinition of canonical OHLC facts or A1/A2 schema.
- Option B/C computation logic or feature definitions.
- Pine script design, TradingView alert logic, or UI behavior.

### Authoritative Anchors (binding)

This contract is anchored to the following repository artifacts and MUST NOT contradict them:

- `docs/contracts/option_a1_bar_ingest_contract_v1.md`
- `docs/contracts/option_a2_event_ingest_contract_v1.md`
- `docs/contracts/option_b_derived_contract_v1.md`
- `sql/derived/v_ovc_c1_features_v0_1.sql`
- `sql/derived/v_ovc_c2_features_v0_1.sql`
- `sql/derived/v_ovc_c3_features_v0_1.sql`
- `contracts/export_contract_v0.1.1_min.json`
- `.github/workflows/backfill_then_validate.yml`

---

## Classification of TradingView Outputs

### Raw visual artifacts (candles, screenshots)

**Classification**: **REF-ONLY**

**Rationale**: Visual artifacts are not canonical data products. They may be retained for human inspection or evidence but do not participate in Option A ingest or Option B/C computation.

### Computed indicators (VWAP, sessions, structure, etc.)

**Classification**: **REF-ONLY**

**Rationale**: Computed TradingView indicators are external interpretations. They are not part of Option A primitive-only definitions and are not part of Option B C1/C2/C3 derived interfaces. Any such fields present in `export_contract_v0.1.1_min.json` are explicitly non-authoritative per `option_a1_bar_ingest_contract_v1.md` section 4.5.

### Annotations / overlays

**Classification**: **REF-ONLY**

**Rationale**: Overlays are presentation-layer artifacts. They may be used for parity checks or diagnostics but MUST NOT be used as inputs to deterministic computation.

---

## Allowed Uses

- Parity testing vs **C1/C2** features (as optional validation in Option B.2).
- Diagnostic comparison of TradingView outputs vs OVC-derived outputs.
- Visualization and annotation layers (non-authoritative).
- Human-in-the-loop inspection for debugging or drift investigation.

---

## Forbidden Uses

- Feeding Option B logic (C1/C2/C3) with TradingView-derived metrics.
- Acting as fallback truth for Option A or Option B outputs.
- Filling gaps in missing C features or bypassing C1/C2/C3 derivations.
- Masking broken workflows (e.g., missing or failed C3 computation).

---

## TV <-> OVC Mapping Table (Conceptual)

**Note**: This table is **conceptual and incomplete**. Where a mapping is not explicitly implemented or enforced in the repo, it is marked **UNSPECIFIED** or **NONE**.

| TradingView metric name | Closest OVC C-feature (or NONE) | Expected parity tolerance | Known semantic differences |
|---|---|---|---|
| `o`, `h`, `l`, `c` (2H OHLC) | **NONE (A1 primitive)** | UNSPECIFIED | A1 canonical OHLC; TradingView source is identified by `source`, but Option B views do not filter by source. |
| `rng` | C1 view passthrough (`derived.v_ovc_c1_features_v0_1`) | UNSPECIFIED | `rng` is mechanically derived in A1; semantic validation is performed at ingest but tolerance for parity checks is UNSPECIFIED. |
| `body` | C1 view passthrough (`derived.v_ovc_c1_features_v0_1`) | UNSPECIFIED | `body` is mechanically derived in A1; parity thresholds not defined in contracts. |
| `dir` | C1 view passthrough (`derived.v_ovc_c1_features_v0_1`) | Exact match expected | Direction is discrete; parity checks should be exact (no tolerance specified in contracts). |
| `ret` | **NONE (not in C1/C2/C3 views)** | UNSPECIFIED | `ret` exists in A1 and C1 materialized tables; semantic validation is disabled at ingest and not gated downstream. |
| `state_tag`, `value_tag`, `trend_tag`, `struct_state`, `space_tag` | **NONE (non-authoritative A1 legacy fields)** | UNSPECIFIED | Present in MIN export but prohibited as authoritative inputs (A1 contract section 4.5; B contract denylist). |
| `htf_stack`, `with_htf`, `rd_state`, `regime_tag`, `trans_risk` | **NONE (non-authoritative A1 legacy fields)** | UNSPECIFIED | TradingView-derived interpretations; no C1/C2/C3 interface defined for these. |
| `bias_mode`, `bias_dir`, `perm_state`, `rail_loc` | **NONE (non-authoritative A1 legacy fields)** | UNSPECIFIED | Prohibited as Option B inputs; no C1/C2/C3 mapping. |
| `tradeable`, `conf_l3`, `play`, `pred_dir`, `pred_target`, `timebox`, `invalidation` | **NONE (non-authoritative A1 legacy fields)** | UNSPECIFIED | L3 decision outputs; not part of Option B C1/C2/C3 views. |

---

## Ingest & Storage Posture

- **Option A1 (2H bars)**: TradingView payloads MAY be ingested via the MIN export contract (`export_contract_v0.1.1_min.json`). This path writes into `ovc.ovc_blocks_v01_1_min` with overwrite-by-reingest semantics (last write wins) per `option_a1_bar_ingest_contract_v1.md`.
- **Option A2 (M15 candles)**: TradingView ingest is **NOT IMPLEMENTED** for M15; no TradingView webhook or CSV adapter exists for A2 per `option_a2_event_ingest_contract_v1.md`.
- **REF-only labeling**: If TradingView data is stored, it must be identifiable as REF-only via provenance fields (e.g., `source`, `build_id`) in A1. The repo does **not** define a dedicated REF-only schema for TradingView outputs.
- **Explicit boundary**: TradingView-derived fields present in the MIN export contract are **non-authoritative** and **MUST NOT** be treated as A1/A2 primitives. Their presence in A1 is legacy-only and does not confer authority.

---

## Validation & Drift Detection

- **Allowed use**: TradingView reference metrics may be compared against OVC-derived outputs as an **optional parity check** in Option B validation (see `option_b_derived_contract_v1.md` Validation & Enforcement).
- **Mismatch definition**: Any differences flagged by the optional reference comparison are treated as **drift indicators**, not overrides. Exact tolerance thresholds are **UNSPECIFIED** in contracts and must be treated as implementation detail.
- **Action on mismatch**: Investigate input data, compute logic, or source alignment. **Do not overwrite** Option A or Option B outputs with TradingView reference values.

---

## Enforcement Reality Check

### Enforced today (repo reality)

- MIN export schema enforcement for A1 webhook ingest exists and is required by `export_contract_v0.1.1_min.json` and `option_a1_bar_ingest_contract_v1.md`.
- C1/C2/C3 **authoritative interfaces** exist as SQL views (`v_ovc_c1_features_v0_1.sql`, `v_ovc_c2_features_v0_1.sql`, `v_ovc_c3_features_v0_1.sql`) and are the only sanctioned derived interfaces per `option_b_derived_contract_v1.md`.
- A2 has **no TradingView ingest path**, per `option_a2_event_ingest_contract_v1.md`.

### Policy-only (not enforced in code)

- No CI gate prevents reads of non-authoritative A1 legacy fields (A1 contract alignment notes; B contract denylist).
- No CI gate enforces `source != 'tv'` filtering in Option B views or tables.
- `backfill_then_validate.yml` does **not** enable TradingView parity checks (no `--compare-tv` flag), so REF checks are **not executed** by default.
- Overwrite-by-reingest semantics mean TV-sourced rows can overwrite earlier rows with the same `block_id`; no guard exists to prevent this.

### Non-binding / Future (explicitly not enforced)

- A dedicated REF-only schema or table set for TradingView outputs.
- CI gates to enforce REF-only usage (e.g., block Option B from reading TV-sourced rows).
- Automated fail-fast parity thresholds for TradingView drift checks.

---

## Canon Freeze & Versioning

- This contract is **versioned independently** as `TRADINGVIEW_REFERENCE_CONTRACT_VERSION` and must be updated if any of its anchors change.
- **Option A1/A2** contract versions (v1.0) govern ingest authority and primitives. This document does not override them.
- **Option B** contract version (v1.1) governs derived feature authority and read/write boundaries. This document does not override it.
- **C1/C2/C3 view versions** are fixed at `v0_1` in the current repo; any change to those view definitions requires a review of TradingView parity semantics.
- **MIN export contract** (`export_contract_v0.1.1_min.json`) is immutable; any changes must be introduced as new versioned files and then reflected here.

---

End of contract.
