# Metric Trial Log v0 (NON-CANONICAL)

> **Status**: WORKING DRAFT / NON-CANONICAL  
> **Created**: 2026-01-18  
> **Purpose**: Consolidate metric trial findings, domain coverage, and tier review outcomes  
> **Scope**: L1, L2, L3 trial results; domain coverage map; blocking decisions  
> **Authority**: NONE — this document is advisory only until decisions are ratified

---

## A) Non-Canonical Status

> ⚠️ **WARNING — NOTHING IN THIS DOCUMENT IS LOCKED OR CANONICAL**
>
> This log captures working notes from the metric trial process. All tier assignments,
> verdicts, and recommendations are subject to revision. The document exists to:
>
> 1. Record trial outcomes before design decisions are finalized
> 2. Provide context for decision-makers reviewing D1–D5
> 3. Maintain traceability between trial observations and spec updates
>
> **DO NOT** treat any table or verdict here as authoritative. Refer to the locked
> specifications once approved:
> - `c_layer_boundary_spec_v0.1.md` → Section A (Tier Purpose)
> - `mapping_validation_report_v0.1.md` → Section 1 (Tier Violation Report)
> - `versioned_config_proposal_v0.1.md` → Section 2 (Configs Requiring Versioning)

---

## B) Tier Boundary Reminder (L1/L2/L3)

The following rules summarize the tier boundaries per `c_layer_boundary_spec_v0.1.md` Section A:

- **B-Layer**: Raw OHLC + identity + ingest metadata. Source-agnostic. No derived values.
- **L1 (Single-Bar)**: Formulas operating on `{o, h, l, c}` of ONE block only. No lookback, no history, no rolling windows.
- **L2 (Multi-Bar)**: Features requiring cross-bar relationships, rolling windows, or session context. Must have explicit `window_spec`.
- **L3 (Categorical)**: Categorical/enum outputs derived from L2 numeric features + versioned threshold parameters. Thresholds must be frozen per version.
- **Decision**: Synthesis of L2/L3 evidence into bias/play/prediction objects. Not raw features.
- **Strict Upward Flow**: B → L1 → L2 → L3 → Decision. No tier may depend on outputs from a higher tier.
- **Replay Rule**: All derived metrics (L1–L3) must be replayable from:
  - B-layer facts (`ovc.ovc_blocks_v01_1_min`)
  - Versioned config (formula_hash, window_spec, threshold_version)
  - Provenance-stamped external context streams (if any)
- **No TV as Truth**: TradingView is a reference engine for real-time display; Python/SQL implementations are authoritative for replay.
- **Window Spec Required**: All L2+ fields must document window specification (e.g., `N=12`, `session=date_ny`, `parameterized=rd_len`).
- **Threshold Version Required**: All L3 fields must reference a `threshold_version` for replay certification.

---

## C) Worth Gates (Metric Must Pay Rent)

A metric earns its place in the derived layer by passing four gates:

| Gate | Name | Criterion |
|------|------|-----------|
| **A** | Replay Legitimacy | Has documented `window_spec` (L2) or `threshold_version` (L3). Can be recomputed from B + config. |
| **B** | Uniqueness | Non-redundant; does not duplicate information already captured by another metric at the same tier. |
| **C** | Downstream Usefulness | Supports at least one of: structure detection, classification, validation, or research. |
| **D** | Robustness | Stable under reasonable data variations; not overly sensitive to noise or edge cases. |

**Interpretation**:
- Gate A is **blocking** — a metric that fails replay legitimacy cannot be admitted to the derived schema.
- Gates B–D are **advisory** — metrics that fail may still be kept if downstream value is demonstrated, but should be flagged for review.

---

## D) Domain Coverage Map (v0.1 / OHLC-only)

### D.1 — Domains That Matter (Current Scope)

| # | Domain | Tier | Description |
|---|--------|------|-------------|
| 1 | Bar geometry | L1 | Single-bar shape: range, body, wicks, ratios |
| 2 | Volatility baseline/dispersion | L2 | Rolling averages and standard deviations of range/return |
| 3 | Volatility anomaly | L2 | Z-scores, extreme flags, deviation from baseline |
| 4 | Session context | L2 | Session-scoped running max/min, distance from session extremes |
| 5 | Range/balance evidence | L2 | RD numeric outputs: rd_hi, rd_lo, rd_mid, rd_w_rrc (confirmed in mapping) |
| 6 | Structure breaks | L2 | Higher-highs, lower-lows, took-prev-high/low |
| 7 | Regime/state semantics | L3 | Categorical tags: state_tag, value_tag, rd_state, rd_brkdir |
| 8 | Event semantics | L3 | Event classification: event_tag, sweep, flip, tis |
| 9 | External context streams | N/A | News, calendar, sentiment. NOT B-layer; provenance required. |

### D.2 — Coverage Score Legend

| Score | Meaning |
|-------|---------|
| **0** | Missing — domain not addressed |
| **1** | Present but underspecified — metric exists but lacks window_spec or threshold_version |
| **2** | Replayable — metric has documented spec, can be recomputed from B + config |
| **3** | Replayable + Validated — metric passes replay and has validation test coverage |

### D.3 — Current Estimated Coverage

| Domain | Score | Notes |
|--------|-------|-------|
| 1. Bar geometry (L1) | **3** | Fully implemented in SQL view; deterministic |
| 2. Volatility baseline (L2) | **2** | `roll_avg_range_12`, `roll_std_logret_12` present; window_spec documented |
| 3. Volatility anomaly (L2) | **2** | `range_z_12`, extreme flags present; depends on rolling stats |
| 4. Session context (L2) | **2** | `sess_high`, `sess_low`, `dist_*` present; `session=date_ny` implicit |
| 5. Range/balance evidence (L2) | **1** | `rd_hi`, `rd_lo`, `rd_mid` present but `rd_len` not versioned |
| 6. Structure breaks (L2) | **2** | `hh_12`, `ll_12`, `took_prev_*` present; `N=12` or `N=1` documented |
| 7. Regime/state semantics (L3) | **1** | Tags present; thresholds not versioned (blocks replay) |
| 8. Event semantics (L3) | **1** | Tags present; thresholds not versioned (blocks replay) |
| 9. External context streams | **0** | `news_flag` exists but violates B-layer; provenance undefined |

**Summary**: L1/L2 domains mostly 2–3. L3 domains 1–2 until threshold registry implemented. Context stream domain incomplete until provenance separation.

> **Note**: L1 domain coverage is complete, but the current L1 SQL view contains 12 L2 metrics (tier violation) pending L1/L2 split, per `mapping_validation_report_v0.1.md` Section 1.1.

---

## E) L1 Trial Results (Compliant Single-Bar Set)

### E.1 — Trialed Metrics

| Metric | Formula | Verdict | Gate Status |
|--------|---------|---------|-------------|
| `range` | `h - l` | **KEEP** | A✅ B✅ C✅ D✅ |
| `body` | `abs(c - o)` | **KEEP** | A✅ B✅ C✅ D✅ |
| `direction` | `sign(c - o)` | **KEEP** | A✅ B✅ C✅ D✅ |
| `ret` | `(c - o) / o` | **KEEP** | A✅ B✅ C✅ D✅ |
| `logret` | `ln(c / o)` | **KEEP** | A✅ B✅ C✅ D✅ |
| `body_ratio` | `body / range` | **KEEP** | A✅ B✅ C✅ D✅ |
| `close_pos` | `(c - l) / range` | **KEEP** | A✅ B✅ C✅ D✅ |
| `upper_wick` | `h - max(o, c)` | **KEEP** | A✅ B✅ C✅ D✅ |
| `lower_wick` | `min(o, c) - l` | **KEEP** | A✅ B✅ C✅ D✅ |
| `clv` | `((c-l)-(h-c))/(h-l)` | **KEEP** | A✅ B✅ C✅ D✅ |
| `brb` | bar-relative-body | **PROVISIONAL** | A✅ B⚠️ C✅ D✅ |

### E.2 — Notes

- All KEEP metrics are strictly single-bar; no lookback.
- `brb` is provisional due to possible redundancy with `body_ratio` (Gate B warning). Retain pending research.
- See `c_layer_boundary_spec_v0.1.md` Section F.2 for canonical examples.

---

## F) L2 Trial Results

### F.1 — Reclassified from L1 View (Should Be L2)

Per `mapping_validation_report_v0.1.md` Section 1.1, the following 12 fields are currently in the "L1" SQL view but require history:

| Field | Current Tier | Correct Tier | Required window_spec |
|-------|--------------|--------------|----------------------|
| `gap` | L1 (impl) | **L2** | `N=1` (prev_c) |
| `sess_high` | L1 (impl) | **L2** | `session=date_ny` |
| `sess_low` | L1 (impl) | **L2** | `session=date_ny` |
| `dist_sess_high` | L1 (impl) | **L2** | `session=date_ny` (inherits) |
| `dist_sess_low` | L1 (impl) | **L2** | `session=date_ny` (inherits) |
| `roll_avg_range_12` | L1 (impl) | **L2** | `N=12` |
| `roll_std_logret_12` | L1 (impl) | **L2** | `N=12` |
| `range_z_12` | L1 (impl) | **L2** | `N=12` (inherits) |
| `hh_12` | L1 (impl) | **L2** | `N=12` |
| `ll_12` | L1 (impl) | **L2** | `N=12` |
| `took_prev_high` | L1 (impl) | **L2** | `N=1` |
| `took_prev_low` | L1 (impl) | **L2** | `N=1` |

### F.2 — RD Numeric Outputs (Should Be L2)

Per `mapping_validation_report_v0.1.md` Section 1.2, the following 3 RD fields are classified as L3 but are numeric rolling-window outputs:

| Field | Current Tier | Correct Tier | Required window_spec |
|-------|--------------|--------------|----------------------|
| `rd_hi` | L3 | **L2** | `parameterized=rd_len` |
| `rd_lo` | L3 | **L2** | `parameterized=rd_len` |
| `rd_mid` | L3 | **L2** | `parameterized=rd_len` (derived) |

### F.3 — Paperwork Gaps (Missing window_spec / params)

Per `mapping_validation_report_v0.1.md` Section 2, the following L2 fields lack explicit window specification:

| Field Family | Fields | Required window_spec Format |
|--------------|--------|----------------------------|
| Rolling mean | `rm` | `N=<rm_len>` (parameterized) |
| Rolling stddev | `sd` | `N=<sd_len>` (parameterized) |
| Open ratio | `or` | `N=<or_len>` (parameterized) |
| Ret ratio | `rer` | `N=<rer_len>` (parameterized) |
| Multi-close | `mc3` | `N=3` |
| Volatility factor | `vf3` | `N=3` |
| Space features | `space_*` | `N=<space_len>` (parameterized) |
| Bar count | `bar_count_*` | `session=<scope>` or `N=<count>` |
| HTF features | `htf_*` | `resolution=<htf_resolution>` |

**Parameters requiring versioning** (per `versioned_config_proposal_v0.1.md` Section 2.5):

| Parameter | Used By | Must Be Versioned |
|-----------|---------|-------------------|
| `rd_len` | rd_hi, rd_lo, rd_mid | YES |
| `kls_lookback` | KLS features | YES |
| `bs_depth` | BlockStack | YES |
| `htf_resolution` | HTF features | YES |
| `rm_len`, `sd_len` | rolling stats | YES |

---

## G) L3 Trial Results (Worthy but Admissibility Blocked)

### G.1 — Trialed Metrics

| Metric | Verdict | Gate Status | Notes |
|--------|---------|-------------|-------|
| `state_tag` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `value_tag` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `event_tag` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `rd_state` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `rd_brkdir` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `tis` | **KEEP** | A⛔ B✅ C✅ D✅ | Depends on state_tag |
| `flip` | **KEEP** | A⛔ B✅ C✅ D✅ | Depends on state_tag |
| `sweep` | **KEEP** | A⛔ B✅ C✅ D✅ | Blocked by threshold_version |
| `cp_tag` | **PROVISIONAL** | A⛔ B⚠️ C✅ D✅ | May overlap with state_tag |
| `tt` | **PROVISIONAL** | A⛔ B⚠️ C✅ D✅ | Composite; needs decomposition review |

### G.2 — Blocking Statement

> **L3 outputs are NOT replay-certifiable until `threshold_version` is implemented and persisted per run.**

All L3 metrics fail Gate A (Replay Legitimacy) because:
1. Threshold parameters (`th_move_OR`, `th_move_RER`, `th_accept_SD`, `cp_hi`, `cp_lo`, `rd_width_th`, `rd_drift_th`) are Pine script inputs, not persisted.
2. Without `threshold_version`, the same formula can produce different categorical outputs.
3. See `versioned_config_proposal_v0.1.md` Section 1 (Problem Statement) and Section 3 (Proposed Storage Path).

**Remediation**: Implement threshold registry before L3 implementation in Python/SQL.

---

## H) Blocking Decisions & Next Steps (NON-CANONICAL)

### H.1 — Design Decisions Required

Per `c_layer_boundary_spec_v0.1.md` Section H, five decisions block implementation:

| ID | Question | Recommended Direction |
|----|----------|----------------------|
| **D1** | Should L1 include trivial rolling features? | **No** — keep strict L1 (single-bar only); split view into `ovc_l1_pure_*` and `ovc_l2_simple_*` |
| **D2** | Should immediate categorical tags be L2.5 or L3? | **Conceptual L2.5 only** — no physical tier; document as "L2-tags" in mapping but keep in L3 schema |
| **D3** | Should RD module be split by output type? | **Yes** — split RD numeric (L2) vs categorical (L3) for tier purity |
| **D4** | How to version threshold parameters? | **Threshold registry required** — implement `derived.threshold_registry` per versioned_config_proposal |
| **D5** | Where does `news_flag` belong? | **Not B-layer** — becomes external/context stream with explicit provenance; store in `ovc.external_context` or similar |

### H.2 — Immediate Doc-Only Actions

The following actions require NO code changes; documentation edits only:

1. **Add window_spec entries** for all L2+ fields in `metric_map_pine_to_c_layers.md`
   - Format: `window_spec: N=12` or `window_spec: session=date_ny` or `window_spec: parameterized=rd_len`

2. **Mark tier violations** in `metric_map_pine_to_c_layers.md`
   - Add annotation `[VIOLATES: L1 boundary]` to fields in L1 section that require history
   - Add annotation `[SHOULD BE: L2]` to RD numeric fields currently in L3 section

3. **Add threshold inventory** to `metric_map_pine_to_c_layers.md`
   - Reference `versioned_config_proposal_v0.1.md` Section 2 for parameter list
   - Add `threshold_ref: <param_name>` to L3 fields

4. **Define context stream provenance** (doc-only)
   - Create section in `ovc_metric_architecture.md` or new doc: "External Context Streams"
   - Specify: source, update cadence, staleness policy, storage location
   - Move `news_flag` specification to this section

### H.3 — Deferred Until Decisions Approved

The following require code/schema changes and are **blocked until D1–D5 are ratified**:

- Restructure `derived.ovc_block_features_v0_1` to split L1/L2 (blocked by D1)
- Create `derived.threshold_registry` table (blocked by D4)
- Relocate `news_flag` from B-layer (blocked by D5)
- Update tier assignments in SQL comments (blocked by D1–D3)

---

## Cross-Reference Index

This document references the following sections in existing docs:

| Reference | Document | Section |
|-----------|----------|---------|
| Tier definitions | `c_layer_boundary_spec_v0.1.md` | Section A — Tier Purpose |
| Allowed/Forbidden inputs | `c_layer_boundary_spec_v0.1.md` | Section B, Section C |
| L1 violations | `mapping_validation_report_v0.1.md` | Section 1.1 |
| L3 violations | `mapping_validation_report_v0.1.md` | Section 1.2 |
| B-layer violations | `mapping_validation_report_v0.1.md` | Section 1.3 |
| Window spec gaps | `mapping_validation_report_v0.1.md` | Section 2 |
| Threshold gaps | `mapping_validation_report_v0.1.md` | Section 3 |
| Threshold inventory | `versioned_config_proposal_v0.1.md` | Section 2 |
| Threshold registry design | `versioned_config_proposal_v0.1.md` | Section 3 |
| Design decisions | `c_layer_boundary_spec_v0.1.md` | Section H |
| Pine field mapping | `metric_map_pine_to_c_layers.md` | Section 3 (Field → Tier Mapping) |
| B-layer contract | `ovc_metric_architecture.md` | B-Layer Definition |

---

*Trial Log Version: v0 | Status: NON-CANONICAL WORKING DRAFT | Last Updated: 2026-01-18*
