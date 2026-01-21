# Pine Metrics → OVC C-Layer Mapping

> Generated: 2026-01-18
> Purpose: Map Pine script metrics to OVC tiered architecture (B/C1/C2/C3/Decision)

---

## 1. SOURCE FILES USED

| File | Purpose |
|------|---------|
| [pine/OVC_v0_1.pine](../pine/OVC_v0_1.pine) | Main Pine script with `exportMin` and `exportFull` construction |
| [contracts/export_contract_v0.1_min.json](../contracts/export_contract_v0.1_min.json) | MIN profile field order (48 fields) |
| [contracts/export_contract_v0.1.1_min.json](../contracts/export_contract_v0.1.1_min.json) | MIN v0.1.1 contract (50 fields) |
| [contracts/export_contract_v0.1_full.json](../contracts/export_contract_v0.1_full.json) | FULL profile field order (174 fields, 20 groups) |
| [docs/derived_metric_registry_v0.1.md](../docs/derived_metric_registry_v0.1.md) | Metric class definitions (DBF/WDF/CIX/EVO/QAF/PMETA) |
| [docs/ovc_metric_architecture.md](../docs/ovc_metric_architecture.md) | Architecture reference for B/C1/C2/C3 tiers |
| [sql/derived_v0_1.sql](../sql/derived_v0_1.sql) | Implemented C1 SQL view |
| [sql/option_c_v0_1.sql](../sql/option_c_v0_1.sql) | Outcomes/evaluation SQL view |

---

## 2. EXPORT FIELD INVENTORY

### 2.1 exportMin Field List (Exact Order from Pine)

Extracted from `OVC_v0_1.pine` exportMin string construction:

| # | Field | Pine Source |
|---|-------|-------------|
| 0 | `ver` | `exp_schema` |
| 1 | `profile` | literal `"MIN"` |
| 2 | `scheme_min` | literal `"export_contract_v0.1_min_r1"` |
| 3 | `sym` | `exp_sym` (syminfo.ticker) |
| 4 | `tz` | `EXP_TZ` |
| 5 | `date_ny` | `exp_date` |
| 6 | `bar_close_ms` | `t2` (time("120")) |
| 7 | `block2h_id` | `block_2h_id` |
| 8 | `block4h_id` | `block_4h_id` |
| 9 | `bid` | `exp_bid` |
| 10 | `seg` | `exp_seg` |
| 11 | `news_flag` | `exp_news` |
| 12 | `o` | `open` |
| 13 | `h` | `high` |
| 14 | `l` | `low` |
| 15 | `c` | `close` |
| 16 | `dir` | `close > open ? "UP" : close < open ? "DN" : "0"` |
| 17 | `state_tag` | `StateTag` |
| 18 | `value_tag` | `ValueTag` |
| 19 | `event` | `DominantEvent` |
| 20 | `tt` | `TT` |
| 21 | `cp_tag` | `CPTag` |
| 22 | `tis` | `TiS` |
| 23 | `rrc` | `RRc` |
| 24 | `vrc` | `VRc` |
| 25 | `tr` | `TrendTag` |
| 26 | `ss` | `SS` |
| 27 | `sp` | `SpaceTag` |
| 28 | `htf_stack` | `HTFStack` |
| 29 | `with_htf` | `WithHTF` |
| 30 | `rd_state` | `RD_State` |
| 31 | `regime_tag` | `RegimeTag` |
| 32 | `trans_risk` | `TransitionRisk` |
| 33 | `bias_mode` | `BiasMode` |
| 34 | `bias_dir` | `BiasDir` |
| 35 | `perm_state` | `PermissionState` |
| 36 | `rail_loc` | `RailLoc` |
| 37 | `tradeable` | `TradeableNow == "Y" ? "1" : "0"` |
| 38 | `conf_l3` | `Conf_L3` |
| 39 | `play` | `Play` |
| 40 | `pred_dir` | `PredDir` |
| 41 | `pred_target` | `PredTarget` |
| 42 | `timebox` | `Timebox` |
| 43 | `invalidation` | `Invalidation` |
| 44 | `source` | `exp_source` |
| 45 | `build_id` | `exp_buildId` |
| 46 | `note` | `exp_note` |
| 47 | `ready` | `exp_ready == 1 ? "1" : "0"` |

### 2.2 exportFull Group Blocks (g0–g19)

Extracted from `OVC_v0_1.pine` exportFull string construction:

| Group | Label | Content |
|-------|-------|---------|
| g0 | META | `ver`, `profile`, `schema_full`, `sym`, `tz`, `date_ny`, `bar_close_ms`, `block2h_id`, `block4h_id`, `bid`, `bid4h`, `ymd`, `seg`, `news_flag` |
| g1 | BAR | `o`, `h`, `l`, `c`, `rng`, `body`, `dir` |
| g2 | L1_MAIN | `state_tag`, `value_tag`, `event`, `vr`, `ts`, `cp`, `cp_tag`, `tt`, `tis` |
| g3 | L1_REF | `rr`, `rm`, `q1`, `q3`, `band` |
| g4 | L1_STATE | `rer`, `or`, `clv`, `brb`, `bodyrr` |
| g5 | L1_VALUE | `sd`, `out`, `oa`, `mc`, `mc3`, `vflip`, `vf3` |
| g6 | L1_LIQ | `swhi`, `swlo`, `took_hi`, `took_lo`, `hi_ran`, `hi_rev`, `lo_ran`, `lo_rev` |
| g7 | L1_D2K | `d2rm`, `d2q1`, `d2q3`, `d2rrh`, `d2rrl` |
| g8 | L1_OUT | `out_ready`, `rtrm`, `nxtext`, `nxtsd`, `hint1`, `hint2` |
| g9 | L1_KLS | `kls_mode_l1`, `pooln_l1`, `near_lvl`, `near_src`, `near_dr`, `conf_l1`, `age_l1`, `hitsn_l1`, `width_l1`, `decay_l1`, `kscore_l1`, `ktag_l1` |
| g10 | L2_CTX | `rrc`, `vrc` |
| g11 | L2_STRUCT | `lastpivot`, `swingdir`, `phidr`, `plodr`, `struct`, `ss` |
| g12 | L2_TREND | `rmdrift`, `dirrun`, `tr` |
| g13 | L2_SPACE | `sp`, `space_up`, `space_dn`, `space_min`, `up_src`, `dn_src`, `up_lvl`, `dn_lvl` |
| g14 | L2_HTF | `htf4`, `htfd`, `sd4`, `sdd`, `htf_stack`, `with_htf`, `mdir` |
| g15 | L2_KLS | `kt`, `kscore2`, `kup_dr`, `kdn_dr`, `conf2`, `age2`, `hits2`, `decay2`, `width2` |
| g16 | RD | `rd_state`, `rd_brkdir`, `rd_w_rrc`, `rd_hi`, `rd_lo`, `rd_mid`, `rd_why` |
| g17 | BLOCKSTACK | `regime_tag`, `regime_dir`, `regime_conf`, `trans_risk`, `p_campaign`, `p_rdrange`, `p_confmove`, `p_chop`, `p_split`, `p_contra`, `p_spacelow`, `avg_drift`, `avg_space`, `flip_rate` |
| g18 | L3 | `tagstring`, `bias_mode`, `bias_dir`, `bias_why`, `perm_state`, `rail_src`, `rail_loc`, `tradeable`, `conf_l3`, `play`, `pred_dir`, `pred_target`, `timebox`, `invalidation`, `blocker`, `reasons` |
| g19 | FOOTER | `source`, `build_id`, `note`, `ready` |

---

## 3. FIELD → TIER MAPPING TABLE

### Classification Rules

| Tier | Definition |
|------|------------|
| **B** | Identity/time keys + OHLC + ingest metadata. Source-agnostic raw facts. |
| **C1** | Single-bar OHLC math primitives. No history window required. |
| **C2** | Multi-bar structure/context/memory. Rolling windows over OHLC. |
| **C3** | Higher-order regime/model tags synthesized from C2 evidence. |
| **Decision** | Bias/play/prediction/permission objects. Trade-action outputs. |

### 3.1 B-Layer (Canonical Facts)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `ver` | META | B | N/A | NO | Schema version string |
| `profile` | META | B | N/A | NO | Export profile literal |
| `scheme_min` | META | B | N/A | NO | Schema label |
| `sym` | META | B | N/A | NO | `syminfo.ticker` |
| `tz` | META | B | N/A | NO | Export timezone constant |
| `date_ny` | META | B | N/A | NO | NY-anchored date |
| `bar_close_ms` | META | B | N/A | NO | 2H bar close timestamp |
| `block2h_id` | META | B | N/A | NO | Canonical 2H block ID |
| `block4h_id` | META | B | N/A | NO | Canonical 4H block ID |
| `bid` | META | B | N/A | NO | Alias of block_id |
| `bid4h` | META | B | N/A | NO | 4H block alias (FULL) |
| `ymd` | META | B | N/A | NO | Compact YYYYMMDD (FULL) |
| `seg` | META | B | N/A | NO | Segment letter A-L |
| `news_flag` | META | B | N/A | NO | External news flag input |
| `o` | BAR | B | YES | NO | Open price |
| `h` | BAR | B | YES | NO | High price |
| `l` | BAR | B | YES | NO | Low price |
| `c` | BAR | B | YES | NO | Close price |
| `source` | FOOTER | B | N/A | NO | Source identifier |
| `build_id` | FOOTER | B | N/A | NO | Build/run identifier |
| `note` | FOOTER | B | N/A | NO | Optional annotation |
| `ready` | FOOTER | B | N/A | NO | Export readiness flag |

### 3.2 C1-Layer (OHLC Primitives)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rng` | BAR (FULL) | C1 | YES | NO | `h - l` |
| `body` | BAR (FULL) | C1 | YES | NO | `abs(c - o)` |
| `dir` | BAR | C1 | YES | NO | `sign(c - o)` → UP/DN/0 |
| `ret` | (contract v0.1.1) | C1 | YES | NO | `(c - o) / o` |
| `clv` | L1_STATE | C1 | YES | NO | `2*(c-l)/(h-l) - 1` (signed CLV) |
| `brb` | L1_STATE | C1 | YES | NO | `body / range` |

### 3.3 C2-Layer (Structure & Memory)

#### C2a — Micro Reference (2-bar lookback)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rr` | L1_REF | C2 | YES | YES (2) | `max(h[1..2]) - min(l[1..2])` |
| `rm` | L1_REF | C2 | YES | YES (2) | `(rr_high + rr_low) / 2` |
| `q1` | L1_REF | C2 | YES | YES (2) | `rr_low + 0.25 * rr` |
| `q3` | L1_REF | C2 | YES | YES (2) | `rr_low + 0.75 * rr` |
| `band` | L1_REF | C2 | YES | YES (2) | Close quartile 0-3 within rr |

#### C2b — State Metrics (rr-normalized)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rer` | L1_STATE | C2 | YES | YES (2) | Range expansion: `range / rr` |
| `or` | L1_STATE | C2 | YES | YES (2) | Overlap ratio vs micro range |
| `bodyrr` | L1_STATE | C2 | YES | YES (2) | `body / rr` |

#### C2c — Value Metrics

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `sd` | L1_VALUE | C2 | YES | YES (2) | Signed distance to rm in rr units |
| `oa` | L1_VALUE | C2 | YES | YES (2) | Outside acceptance (signed) |
| `out` | L1_VALUE | C2 | YES | YES (2) | OutsideTag from OA sign |
| `mc` | L1_VALUE | C2 | YES | YES (2) | Midcross flag: `l <= rm <= h` |
| `mc3` | L1_VALUE | C2 | YES | YES (3) | 3-bar rolling sum of mc |
| `vflip` | L1_VALUE | C2 | YES | YES (2) | Value flip: sd sign change |
| `vf3` | L1_VALUE | C2 | YES | YES (3) | 3-bar rolling sum of vflip |

#### C2d — Liquidity Sweeps

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `swhi` | L1_LIQ | C2 | YES | YES (2) | SweepHigh magnitude in rr units |
| `swlo` | L1_LIQ | C2 | YES | YES (2) | SweepLow magnitude in rr units |
| `took_hi` | L1_LIQ | C2 | YES | YES (2) | Flag: `swhi > 0` |
| `took_lo` | L1_LIQ | C2 | YES | YES (2) | Flag: `swlo > 0` |
| `hi_ran` | L1_LIQ | C2 | YES | YES (2) | High ran: took_hi AND c >= rr_high |
| `hi_rev` | L1_LIQ | C2 | YES | YES (2) | High rev: took_hi AND c < rr_high |
| `lo_ran` | L1_LIQ | C2 | YES | YES (2) | Low ran: took_lo AND c <= rr_low |
| `lo_rev` | L1_LIQ | C2 | YES | YES (2) | Low rev: took_lo AND c > rr_low |

#### C2e — Distance-to-Key

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `d2rm` | L1_D2K | C2 | YES | YES (2) | Distance to rm (same as sd) |
| `d2q1` | L1_D2K | C2 | YES | YES (2) | Distance to q1 in rr units |
| `d2q3` | L1_D2K | C2 | YES | YES (2) | Distance to q3 in rr units |
| `d2rrh` | L1_D2K | C2 | YES | YES (2) | Distance to rr_high in rr units |
| `d2rrl` | L1_D2K | C2 | YES | YES (2) | Distance to rr_low in rr units |

#### C2f — Outcome Lookback (X-1)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `out_ready` | L1_OUT | C2 | YES | YES (1) | Has prior rr/rm/sd |
| `rtrm` | L1_OUT | C2 | YES | YES (1) | Return-to-prev-rm flag |
| `nxtext` | L1_OUT | C2 | YES | YES (1) | Next extension from sd_prev |
| `nxtsd` | L1_OUT | C2 | YES | YES (1) | Next SD vs previous rm/rr |
| `hint1` | L1_OUT | C2 | YES | YES (1) | Outcome hint from rtrm |
| `hint2` | L1_OUT | C2 | YES | YES (1) | Outcome hint from nxtext |

#### C2g — Context Unit (Rolling RR)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rrc` | L2_CTX | C2 | YES | YES (rrcLen) | Context range: SMA(rr) |
| `vrc` | L2_CTX | C2 | YES | YES (rrcLen) | Volatility ratio: `rr / rrc` |
| `vr` | L1_MAIN | C2 | YES | YES (20) | Volatility ratio: `rr / SMA(rr, 20)` |

#### C2h — Structure State

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `lastpivot` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Last pivot label Hi/Lo |
| `swingdir` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Swing direction from pivot |
| `phidr` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Distance to pivot high in RRc |
| `plodr` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Distance to pivot low in RRc |
| `struct` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Raw structure HH/HL/LH/LL |
| `ss` | L2_STRUCT | C2 | YES | YES (pivotL/R) | Simplified: UP/DN/MIX |

#### C2i — Trend Tracking

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rmdrift` | L2_TREND | C2 | YES | YES (driftN) | Drift of dayRM in RRc units |
| `dirrun` | L2_TREND | C2 | YES | YES (var) | Length of micro direction run |

#### C2j — Space to Targets

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `space_up` | L2_SPACE | C2 | YES | YES (session/day) | Nearest upward target in RRc |
| `space_dn` | L2_SPACE | C2 | YES | YES (session/day) | Nearest downward target in RRc |
| `space_min` | L2_SPACE | C2 | YES | YES | `min(space_up, space_dn)` |
| `up_src` | L2_SPACE | C2 | YES | YES | Source label for up target |
| `dn_src` | L2_SPACE | C2 | YES | YES | Source label for down target |
| `up_lvl` | L2_SPACE | C2 | YES | YES | Price level for up target |
| `dn_lvl` | L2_SPACE | C2 | YES | YES | Price level for down target |

#### C2k — HTF Context

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `sd4` | L2_HTF | C2 | YES | YES (HTF) | 4H timeframe SD |
| `sdd` | L2_HTF | C2 | YES | YES (HTF) | Daily timeframe SD |
| `htf4` | L2_HTF | C2 | YES | YES (HTF) | HTF4 direction tag |
| `htfd` | L2_HTF | C2 | YES | YES (HTF) | HTFD direction tag |
| `mdir` | L2_HTF | C2 | YES | YES (2) | Micro direction from sd |

#### C2l — KLS Levels (L1 + L2)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `kls_mode_l1` | L1_KLS | C2 | N/A | NO | Config input |
| `pooln_l1` | L1_KLS | C2 | YES | YES (var) | Pool size for KLS |
| `near_lvl` | L1_KLS | C2 | YES | YES (var) | Nearest KLS level |
| `near_src` | L1_KLS | C2 | YES | YES (var) | Source label for near_lvl |
| `near_dr` | L1_KLS | C2 | YES | YES (var) | Distance to near_lvl in rr |
| `conf_l1` | L1_KLS | C2 | YES | YES (var) | Confluence count |
| `age_l1` | L1_KLS | C2 | YES | YES (var) | Bars since touch |
| `hitsn_l1` | L1_KLS | C2 | YES | YES (var) | Rolling hit count |
| `decay_l1` | L1_KLS | C2 | YES | YES (var) | Age decay |
| `width_l1` | L1_KLS | C2 | N/A | NO | Config input |
| `kscore_l1` | L1_KLS | C2 | YES | YES (var) | Weighted KLS score |
| `ktag_l1` | L1_KLS | C2 | YES | YES (var) | KLS tag HIGH/MID/LOW |
| `kt` | L2_KLS | C2 | YES | YES (var) | KTag2 classification |
| `kscore2` | L2_KLS | C2 | YES | YES (var) | KLS-lite score |
| `kup_dr` | L2_KLS | C2 | YES | YES (var) | Distance to above level |
| `kdn_dr` | L2_KLS | C2 | YES | YES (var) | Distance to below level |
| `conf2` | L2_KLS | C2 | YES | YES (var) | L2 confluence count |
| `age2` | L2_KLS | C2 | YES | YES (var) | L2 age |
| `hits2` | L2_KLS | C2 | YES | YES (var) | L2 hit count |
| `decay2` | L2_KLS | C2 | YES | YES (var) | L2 decay |
| `width2` | L2_KLS | C2 | N/A | NO | Config input |

### 3.4 C3-Layer (Market Model & Regime)

#### C3a — L1 Composite Tags

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `state_tag` | L1_MAIN | C3 | YES | YES (2) | MOVE/ROTATE from OR, RER, CLV + thresholds |
| `value_tag` | L1_MAIN | C3 | YES | YES (2) | ACCEPT+/ACCEPT-/NEUTRAL from SD |
| `event` | L1_MAIN | C3 | YES | YES (2) | Dominant event from sweeps + OA |
| `ts` | L1_MAIN | C3 | YES | YES (2) | Trend strength composite |
| `cp` | L1_MAIN | C3 | YES | YES (3) | Chop score from OR, mc3, vf3, wicks |
| `cp_tag` | L1_MAIN | C3 | YES | YES (3) | Chop tag HIGH/MID/LOW |
| `tt` | L1_MAIN | C3 | YES | YES (2) | Trigger flag composite |
| `tis` | L1_MAIN | C3 | YES | YES (var) | Time-in-state counter |

#### C3b — L2 Context Tags

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `tr` | L2_TREND | C3 | YES | YES | Trend tag from rmdrift + dirrun |
| `sp` | L2_SPACE | C3 | YES | YES | Space tag HIGH/MID/LOW |
| `htf_stack` | L2_HTF | C3 | YES | YES | HTF alignment string |
| `with_htf` | L2_HTF | C3 | YES | YES | WithHTF flag Y/N |

#### C3c — Range Detector (RD)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `rd_state` | RD | C3 | YES | YES (rd_len) | RANGE/SOFT_RANGE/NO_RANGE |
| `rd_brkdir` | RD | C3 | YES | YES (rd_len) | Break direction UP/DN/0 |
| `rd_w_rrc` | RD | C3 | YES | YES (rd_len) | RD width in RRc units |
| `rd_hi` | RD | C3 | YES | YES (rd_len) | RD high level |
| `rd_lo` | RD | C3 | YES | YES (rd_len) | RD low level |
| `rd_mid` | RD | C3 | YES | YES (rd_len) | RD midpoint |
| `rd_why` | RD | C3 | YES | YES (rd_len) | Diagnostic string |

#### C3d — BlockStack (Regime Memory)

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `regime_tag` | BLOCKSTACK | C3 | YES | YES (bs_N) | TREND_STABLE/RANGE_STABLE/TRANSITION |
| `regime_dir` | BLOCKSTACK | C3 | YES | YES (bs_N) | Regime direction from BiasDir counts |
| `regime_conf` | BLOCKSTACK | C3 | YES | YES (bs_N) | Regime confidence A/B/C/D |
| `trans_risk` | BLOCKSTACK | C3 | YES | YES (bs_flipN) | Transition risk from flip_rate |
| `p_campaign` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of CAMPAIGN tags |
| `p_rdrange` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of RD range states |
| `p_confmove` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of confirmed MOVE |
| `p_chop` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of chop states |
| `p_split` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of HTF split |
| `p_contra` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of HTF contra |
| `p_spacelow` | BLOCKSTACK | C3 | YES | YES (bs_N) | Fraction of space low |
| `avg_drift` | BLOCKSTACK | C3 | YES | YES (bs_N) | Average RMdrift |
| `avg_space` | BLOCKSTACK | C3 | YES | YES (bs_N) | Average SpaceMin |
| `flip_rate` | BLOCKSTACK | C3 | YES | YES (bs_flipN) | BiasMode change rate |

### 3.5 Decision Layer

| Field | Origin Module | Tier | OHLC Only | History? | Notes |
|-------|---------------|------|-----------|----------|-------|
| `tagstring` | L3 | Decision | N/A | YES | Composite tag string |
| `bias_mode` | L3 | Decision | N/A | YES | TREND/RANGE/NOISE/TRANSITION |
| `bias_dir` | L3 | Decision | N/A | YES | UP/DN/0 |
| `bias_why` | L3 | Decision | N/A | YES | Rationale string |
| `perm_state` | L3 | Decision | N/A | YES | RED/YELLOW/GREEN/ORANGE |
| `rail_src` | L3 | Decision | N/A | YES | RD or SESS |
| `rail_loc` | L3 | Decision | N/A | YES | UP_RAIL/DN_RAIL/MID/IN_RANGE/OUTSIDE |
| `tradeable` | L3 | Decision | N/A | YES | 1/0 tradeable decision |
| `conf_l3` | L3 | Decision | N/A | YES | L3 confidence grade A/B/C/D |
| `play` | L3 | Decision | N/A | YES | Play label |
| `pred_dir` | L3 | Decision | N/A | YES | Predicted direction |
| `pred_target` | L3 | Decision | N/A | YES | Target string |
| `timebox` | L3 | Decision | N/A | YES | Timebox label |
| `invalidation` | L3 | Decision | N/A | YES | Invalidation criteria |
| `blocker` | L3 | Decision | N/A | YES | Blocker label |
| `reasons` | L3 | Decision | N/A | YES | Reasons string |

---

## 4. DEPENDENCY GRAPH (TEXT)

### 4.1 Tier Dependencies

```
B (OHLC + schedule)
    │
    ├──► C1 (single-bar math: rng, body, dir, clv, brb)
    │        │
    │        ▼
    ├──► C2a (micro reference: rr, rm, q1, q3, band)
    │        │
    │        ├──► C2b (state metrics: rer, or, bodyrr)
    │        │
    │        ├──► C2c (value metrics: sd, oa, out, mc, mc3, vflip, vf3)
    │        │
    │        ├──► C2d (liquidity: swhi, swlo, took_hi/lo, hi_ran/rev, lo_ran/rev)
    │        │
    │        └──► C2e (distance: d2rm, d2q1, d2q3, d2rrh, d2rrl)
    │
    ├──► C2f (outcome lookback: out_ready, rtrm, nxtext, nxtsd)
    │
    ├──► C2g (context unit: rrc = SMA(rr), vrc = rr/rrc)
    │        │
    │        ├──► C2h (structure: pivots, struct, ss)
    │        │
    │        ├──► C2i (trend: rmdrift, dirrun)
    │        │
    │        └──► C2j (space: space_up/dn, targets)
    │
    ├──► C2k (HTF: sd4, sdd, htf4, htfd, mdir)
    │
    └──► C2l (KLS levels: pooln, near_lvl, near_dr, conf, kscore)
             │
             ▼
        C3 (market model tags)
             │
             ├──► C3a (L1 tags: state_tag, value_tag, event, cp_tag, tt, tis)
             │
             ├──► C3b (L2 tags: tr, sp, htf_stack, with_htf)
             │
             ├──► C3c (RD: rd_state, rd_brkdir, rd_hi/lo/mid)
             │
             └──► C3d (regime: regime_tag, regime_dir, trans_risk, p_*)
                      │
                      ▼
                  Decision (L3)
                      │
                      ├──► bias_mode, bias_dir, perm_state
                      │
                      ├──► rail_loc, tradeable, conf_l3
                      │
                      └──► play, pred_dir, pred_target, timebox, invalidation
```

### 4.2 Simplified Chain

```
B → C1 → C2(micro rr/rm) → C2(state/value) → C2(structure/trend/space) → C3(tags) → Decision
```

### 4.3 Critical Path for Tag Derivation

```
[state_tag]  ←  or, rer, clv  ←  rr, rm  ←  h[1..2], l[1..2]
[value_tag]  ←  sd  ←  rm, rr  ←  h[1..2], l[1..2]
[trend_tag]  ←  rmdrift, dirrun  ←  rm, sd, rrc  ←  rr  ←  OHLC
[regime_tag] ←  p_campaign, p_rdrange, avgDrift  ←  trend_tag, rd_state, rmdrift  ←  C2
[bias_mode]  ←  trend_tag, htf_stack, ss, state_tag, cp_tag, tt, rd_state  ←  C2/C3
[bias_dir]   ←  bias_mode, trend_tag, ss, htf_stack, with_htf, mdir, rmdrift  ←  C2/C3
```

---

## 5. GAP ANALYSIS

### 5.1 Metrics NOT Computable from OHLC Alone

| Metric/Feature | Reason | Required Data |
|----------------|--------|---------------|
| `news_flag` | External calendar input | News calendar API |
| True orderflow | Bid/ask imbalance | Tick-level data |
| Volume profile | Volume by price | Tick or volume bars |
| Microstructure metrics | Tick patterns | Sub-bar tick stream |
| Cross-instrument correlation | Multi-symbol | Parallel symbol feeds |

**All other metrics are derivable from OHLC.**

### 5.2 Missing Evidence Fields for Explainability

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **Threshold parameters not logged** | Cannot reproduce tag derivation | Store `th_move_OR`, `th_move_RER`, `th_move_CLV`, `th_accept_SD`, `cp_hi`, `cp_lo`, etc. in derived tables |
| **Intermediate scores not persisted** | Cannot debug composite tags | Store `ts` (trend strength), `cp` (chop score) in C3 tables |
| **KLS pool contents not exported** | Cannot validate level selection | Store `pooln_l1`, `pooln_l2`, `near_lvl`, `near_src` |
| **State change timestamps missing** | Cannot trace `tis` derivation | Store `state_tag_changed_at_ms` |
| **Pivot coordinates not persisted** | Cannot validate structure | Store `lastPH_price`, `lastPL_price`, `lastPH_bar`, `lastPL_bar` |
| **RD rail values not logged** | Cannot audit rail_loc | Store `rd_hi`, `rd_lo`, `sess_hi`, `sess_lo` |
| **Decision inputs not bundled** | Cannot explain play/bias | Store evidence snapshot per block |

### 5.3 Cross-Source Robustness Requirements

| Issue | TV vs OANDA | Mitigation |
|-------|-------------|------------|
| **Price rounding** | TV uses `format.mintick`, OANDA returns raw floats | Round to 5 decimal places (or pip precision per symbol) |
| **OHLC boundary alignment** | TV aggregates per chart bar, OANDA uses server time | Align to NY 2H grid (17:00 anchor) |
| **Tick vs bar close** | TV uses last tick, OANDA may differ by ms | Accept ±1s tolerance on `bar_close_ms` |
| **Hysteresis on tags** | Tags may flip due to threshold proximity | Add hysteresis band (e.g., OR ± 0.05) to prevent churn |
| **Pivot detection timing** | Pine uses `pivothigh()/pivotlow()` with left/right params | Match `pivotL` and `pivotR` settings exactly |
| **HTF request.security()** | TV may repaint on HTF close | Use `lookahead=barmerge.lookahead_off` equivalent |
| **Rolling window edge** | Early blocks lack history | Require minimum history (e.g., 12 blocks) before computing |

---

## 6. IMPLEMENTATION STAGES

### Stage C1 — OHLC Primitives

**Status**: ✅ IMPLEMENTED in `sql/derived_v0_1.sql`

| Item | Value |
|------|-------|
| **Inputs** | `ovc.ovc_blocks_v01_1_min` (OHLC columns) |
| **Outputs** | `derived.ovc_block_features_v0_1` |
| **Metrics** | `range`, `body`, `direction`, `ret`, `logret`, `body_ratio`, `close_pos`, `upper_wick`, `lower_wick`, `gap`, `sess_high`, `sess_low`, `roll_avg_range_12`, `roll_std_logret_12`, `range_z_12`, `hh_12`, `ll_12`, `took_prev_high`, `took_prev_low`, quality flags |
| **Definition of Done** | View deployed, formula_hash stable, tests pass |

---

### Stage C2 — Structure & Memory

**Status**: 🔜 NOT STARTED

#### C2 Phase 1: Micro Reference (Priority HIGH)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_block_features_v0_1` (o, h, l, c with lag) |
| **Outputs** | `derived.ovc_c2_micro_v0_1` |
| **Metrics** | `rr`, `rm`, `q1`, `q3`, `band`, `rr_high`, `rr_low` |
| **Definition of Done** | Python/SQL output matches Pine ±0.01% for validation dataset |

#### C2 Phase 2: State + Value (Priority HIGH)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_micro_v0_1` + C1 features |
| **Outputs** | `derived.ovc_c2_state_v0_1` |
| **Metrics** | `rer`, `or`, `clv`, `brb`, `bodyrr`, `sd`, `oa`, `out`, `mc`, `mc3`, `vflip`, `vf3` |
| **Definition of Done** | Match Pine output; `clv` and `sd` within ±0.001 |

#### C2 Phase 3: Sweeps + D2K (Priority MEDIUM)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_micro_v0_1` |
| **Outputs** | `derived.ovc_c2_liq_v0_1` |
| **Metrics** | `swhi`, `swlo`, `took_hi`, `took_lo`, `hi_ran`, `hi_rev`, `lo_ran`, `lo_rev`, `d2rm`, `d2q1`, `d2q3`, `d2rrh`, `d2rrl` |
| **Definition of Done** | Boolean flags match 100%; distances within ±0.01 |

#### C2 Phase 4: Context Unit (Priority HIGH)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_micro_v0_1` (rr series) |
| **Outputs** | `derived.ovc_c2_context_v0_1` |
| **Metrics** | `rrc` (SMA of rr), `vrc` (rr/rrc), `vr` |
| **Definition of Done** | Match Pine rrc/vrc within ±0.001 for blocks with sufficient history |

#### C2 Phase 5: Structure (Priority MEDIUM)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_block_features_v0_1` + pivotL/pivotR params |
| **Outputs** | `derived.ovc_c2_structure_v0_1` |
| **Metrics** | `lastpivot`, `swingdir`, `phidr`, `plodr`, `struct`, `ss` |
| **Definition of Done** | Pivot detection matches Pine logic; struct tags match ≥95% |

#### C2 Phase 6: Trend + Space (Priority MEDIUM)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_context_v0_1` + session/day levels |
| **Outputs** | `derived.ovc_c2_trend_v0_1`, `derived.ovc_c2_space_v0_1` |
| **Metrics** | `rmdrift`, `dirrun`, `space_up`, `space_dn`, `space_min`, `up_src`, `dn_src`, `up_lvl`, `dn_lvl` |
| **Definition of Done** | Space distances within ±0.05 RRc; trend direction matches |

#### C2 Phase 7: HTF + KLS (Priority LOW)

| Item | Value |
|------|-------|
| **Inputs** | Aggregated 4H/D OHLC, C2 features |
| **Outputs** | `derived.ovc_c2_htf_v0_1`, `derived.ovc_c2_kls_v0_1` |
| **Metrics** | `sd4`, `sdd`, `htf4`, `htfd`, `mdir`, KLS pool metrics |
| **Definition of Done** | HTF sd within ±0.01; KLS scores within ±0.1 |

---

### Stage C3 — Market Model Tags

**Status**: 📋 PLANNED (TV reference exists)

#### C3 Phase 1: L1 Tags (Priority HIGH)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_state_v0_1` + thresholds |
| **Outputs** | `derived.ovc_c3_l1_tags_v0_1` |
| **Metrics** | `state_tag`, `value_tag`, `event`, `ts`, `cp`, `cp_tag`, `tt`, `tis` |
| **Definition of Done** | Tag agreement ≥95% vs TV reference; threshold params documented |

#### C3 Phase 2: L2 Context Tags (Priority MEDIUM)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_trend_v0_1`, `derived.ovc_c2_space_v0_1`, `derived.ovc_c2_htf_v0_1` |
| **Outputs** | `derived.ovc_c3_l2_tags_v0_1` |
| **Metrics** | `tr` (trend_tag), `sp` (space_tag), `htf_stack`, `with_htf` |
| **Definition of Done** | Tag agreement ≥95% vs TV reference |

#### C3 Phase 3: RD + Regime (Priority MEDIUM)

| Item | Value |
|------|-------|
| **Inputs** | `derived.ovc_c2_*` + `derived.ovc_c3_l1_tags_v0_1` |
| **Outputs** | `derived.ovc_c3_regime_v0_1` |
| **Metrics** | `rd_state`, `rd_brkdir`, `rd_hi/lo/mid`, `regime_tag`, `regime_dir`, `regime_conf`, `trans_risk`, `p_*`, `avg_drift`, `avg_space`, `flip_rate` |
| **Definition of Done** | Regime tag agreement ≥90%; RD state matches |

---

### Stage Parity QA — TV vs Python

**Status**: 📋 PLANNED

| Item | Value |
|------|-------|
| **Inputs** | TV exports (`derived.tv_reference_c2_v0_1`, `derived.tv_reference_c3_v0_1`) + Python outputs |
| **Outputs** | `ovc_qa.parity_report_v0_1` |
| **Metrics** | Field-level agreement %, deviation distribution, flagged outliers |
| **Definition of Done** | Automated CI check; overall tag parity ≥95%; documented exceptions |

#### Parity Test Cases

| Test | Expectation |
|------|-------------|
| `state_tag` agreement | ≥95% match |
| `value_tag` agreement | ≥95% match |
| `sd` numeric deviation | ≤0.01 |
| `rrc` numeric deviation | ≤0.001 |
| `trend_tag` agreement | ≥95% match |
| `regime_tag` agreement | ≥90% match |
| `bias_mode` agreement | ≥90% match |

---

---

## Design Note: C-layer Tier Validity Review

> **Status**: ANALYTICAL — No tier changes implemented  
> **Date**: 2026-01-18  
> **Purpose**: Assess proposed corrections to C-layer classifications before any refactoring

This section documents a critical review of potential tier misclassifications identified in the current mapping. Each issue is analyzed against Pine implementation, stated OVC architecture, and intended layer semantics. **No changes are made to existing classifications pending explicit design decisions.**

---

### Issue A: L1 Composite Tags May Be Misclassified as C3

**Observation**: The fields `state_tag`, `value_tag`, `event`, `cp_tag`, `tt`, and `tis` are currently classified as C3 (Section 3.4, "C3a — L1 Composite Tags"). However, these tags are derived directly from C2 numeric features (e.g., `or`, `rer`, `clv`, `sd`, `swhi`, `swlo`, `mc3`, `vf3`) via threshold comparisons—not from higher-order regime synthesis.

**Analysis**:

The stated C3 definition is: *"Higher-order regime/model tags synthesized from C2 evidence."*

Examining the derivation chains:
- `state_tag` ← `or`, `rer`, `clv` + thresholds (all C2 inputs)
- `value_tag` ← `sd` + threshold (C2 input)
- `event` ← `took_hi`, `took_lo`, `oa` (all C2 inputs)
- `cp_tag` ← `or`, `mc3`, `vf3`, wicks (all C2 inputs)
- `tt` ← `sd`, `or`, `rer`, `clv`, `oa`, sweeps, flip (all C2 inputs)
- `tis` ← barssince(`state_tag` change) (depends on state_tag)

These are **immediate categorical interpretations of C2 numeric features**, not multi-block regime patterns. They operate at the same temporal granularity as their inputs (single bar, with 2-3 bar lookback for some).

**Assessment**:

A reasonable interpretation is that these constitute a **sub-tier between C2 and C3**—call it "C2 tags" or "C2.5"—representing:
- C2: Raw computed features (numeric/boolean)
- C2-tags: Immediate categorical interpretations via thresholds
- C3: Multi-block regime patterns with memory/persistence

An alternative interpretation is that **any categorical synthesis** qualifies as C3, regardless of temporal scope. This would retain the current classification but dilute the "regime" semantic.

The Pine script groups these under "L1_MAIN" (g2), suggesting the original implementation treats them as L1-level (local bar context), not regime-level.

**Verdict**: The proposed reclassification has merit. These tags are closer to C2 in both derivation chain and temporal scope. However, this requires an explicit design decision on whether C3 means "any categorical synthesis" or specifically "regime-level multi-block synthesis."

---

### Issue B: Range Detector Outputs May Span C2 and C3

**Observation**: All RD fields (`rd_state`, `rd_brkdir`, `rd_w_rrc`, `rd_hi`, `rd_lo`, `rd_mid`, `rd_why`) are classified as C3 (Section 3.4, "C3c — Range Detector"). However, some RD outputs are raw rolling-window computations that resemble C2, while others are categorical interpretations.

**Analysis**:

Examining RD field types:
- `rd_hi`: `highest(high, rd_len)` — rolling window computation over OHLC
- `rd_lo`: `lowest(low, rd_len)` — rolling window computation over OHLC
- `rd_mid`: `(rd_hi + rd_lo) / 2` — arithmetic from rd_hi/rd_lo
- `rd_w_rrc`: `(rd_hi - rd_lo) / rrc` — normalized width (numeric)
- `rd_state`: Categorical tag (RANGE/SOFT_RANGE/NO_RANGE) from width + drift + state evidence
- `rd_brkdir`: Categorical tag (UP/DN/0) from close vs rails + TT + StateTag
- `rd_why`: Diagnostic string combining multiple signals

The first four fields (`rd_hi`, `rd_lo`, `rd_mid`, `rd_w_rrc`) are structurally identical to session-based features like `sess_high`/`sess_low`, which are considered C2 in other contexts. They are **numeric rolling-window outputs**, not categorical interpretations.

The latter three fields (`rd_state`, `rd_brkdir`, `rd_why`) involve **categorical synthesis** from multiple evidence sources, which aligns with C3 semantics.

**Assessment**:

A reasonable interpretation is to split RD:
- **C2**: `rd_hi`, `rd_lo`, `rd_mid`, `rd_w_rrc` (raw rolling outputs)
- **C3**: `rd_state`, `rd_brkdir`, `rd_why` (categorical regime interpretation)

An alternative would be to treat RD as a **cohesive module** where all outputs are grouped together for implementation simplicity, accepting that C3 contains some numeric evidence alongside tags.

The Pine script groups all RD fields under "g16=RD" without distinguishing evidence from interpretation.

**Verdict**: The proposed split is architecturally cleaner but creates implementation complexity. A design decision is required on whether **module cohesion** or **tier purity** takes precedence.

---

### Issue C: Rolling/Session Features May Be Misclassified as C1

**Observation**: The C1 definition is "single-bar OHLC math primitives. No history window required." However, the Stage C1 implementation (`derived.ovc_block_features_v0_1`) includes features that require history windows:
- `sess_high`, `sess_low` (session running max/min)
- `roll_avg_range_12`, `roll_std_logret_12` (12-bar rolling stats)
- `range_z_12` (z-score requiring rolling mean/std)
- `hh_12`, `ll_12` (12-bar structural breaks)
- `gap` (requires prior close)

**Analysis**:

Strictly speaking, these violate the C1 definition. They should be classified as C2 ("multi-bar structure/context/memory").

However, there may be a pragmatic distinction:
- **Pure C1**: `range`, `body`, `direction`, `ret`, `body_ratio`, `close_pos`, `clv`, `brb` (single-bar)
- **Simple C2**: `gap`, `sess_high`, `sess_low`, rolling stats (windowed but trivial computation)
- **Complex C2**: `rr`, `rm`, `sd`, pivot detection (windowed with non-trivial logic)

The current SQL view conflates pure C1 and simple C2 for implementation convenience—a single view is easier to maintain than splitting into `derived.ovc_c1_v0_1` and `derived.ovc_c2_simple_v0_1`.

**Assessment**:

The proposed correction is **technically correct**—rolling features are not C1 by the stated definition. However, splitting them may not yield practical benefit if the distinction between "simple C2" and "complex C2" is more meaningful than "C1 vs C2."

An alternative would be to **amend the C1 definition** to include "single-bar primitives + trivial session/rolling context" while reserving C2 for features with non-trivial cross-bar logic (micro reference, pivots, etc.).

**Verdict**: This is a definitional ambiguity. The implementation is pragmatically sound but violates the stated tier definition. Either the definition should be amended or the view should be restructured. This requires an explicit design decision.

---

### Issue D: Feature Thresholds Appear Implicit and Unversioned

**Observation**: The document references threshold parameters (e.g., `th_move_OR`, `th_move_RER`, `th_accept_SD`, `cp_hi`, `cp_lo`) as inputs to tag derivation, but these values are Pine script input parameters—not persisted or versioned alongside derived metrics.

**Analysis**:

For deterministic replay, the formula hash alone is insufficient. The same formula with different thresholds produces different results. Currently:
- Pine thresholds are script inputs (user-configurable)
- SQL/Python thresholds would be hardcoded or config-file based
- No mechanism exists to store "threshold snapshot" per block

This undermines the claim that C-layer metrics are "derived, versioned, and replayable." They are replayable only if thresholds are frozen.

**Assessment**:

This is **not a tier classification issue** but an **architectural gap** affecting all categorical tiers (C2-tags and C3). Options include:
1. Freeze thresholds in code and document as part of version string
2. Store threshold snapshot in a config table linked to formula_hash
3. Export thresholds alongside each block (increases payload)

**Verdict**: Valid concern requiring resolution before C3 implementation in Python. Does not affect tier assignments but affects replay guarantees. Recommend adding a `derived.threshold_registry_v0_1` table.

---

### Issue E: `news_flag` Provenance Is Unspecified

**Observation**: The field `news_flag` is classified as B-layer (canonical facts) with the note "External news flag input." However:
- B-layer is defined as "source-agnostic raw facts"
- `news_flag` is a manual/external input in Pine, not derivable from OHLC
- OANDA backfill cannot reproduce this field
- Provenance and update mechanism are not documented

**Analysis**:

If `news_flag` is truly B-layer, it must be reproducible from any source. Currently it cannot be, which violates source-agnosticism.

Options:
1. **Demote to C-layer**: Treat as derived/optional annotation, not canonical fact
2. **Define provenance**: Specify external news calendar source, make it deterministic
3. **Remove from B-layer**: Exclude from canonical table, store in auxiliary table

The Pine script shows `exp_news` as a script input, suggesting it's operator-provided context, not market data.

**Assessment**:

The proposed concern is valid. `news_flag` does not meet B-layer criteria as currently specified. A reasonable interpretation is that it belongs in **ingest metadata** (like `source` and `build_id`) rather than canonical facts—present when provided, absent otherwise, and explicitly non-deterministic.

An alternative is to require an **external news calendar table** (`ovc.news_calendar`) that can be joined, making news_flag deterministically derivable for any block.

**Verdict**: `news_flag` requires provenance specification or reclassification. It should not remain in B-layer without addressing source-agnosticism.

---

### Summary of Findings

| Issue | Proposed Change | Assessment | Requires Decision? |
|-------|-----------------|------------|-------------------|
| A | Reclassify L1 tags from C3 to C2/C2.5 | Architecturally valid; depends on C3 definition | YES |
| B | Split RD into C2 (numeric) and C3 (tags) | Architecturally valid; trades cohesion for purity | YES |
| C | Reclassify rolling features from C1 to C2 | Technically correct; pragmatically disruptive | YES |
| D | Version/persist threshold parameters | Valid gap; not a tier issue | YES (before C3 impl) |
| E | Clarify or reclassify `news_flag` | Valid concern; B-layer purity violated | YES |

---

### Decision Required Before Implementation

The following tier changes should be explicitly approved before refactoring this document or implementing derived tables:

1. **Define C2-tags vs C3 boundary**: Are immediate categorical interpretations of C2 features (state_tag, value_tag, etc.) considered C2 or C3? Recommend defining C3 as "multi-block regime patterns with persistence/memory" and creating C2-tags sub-tier.

2. **RD module cohesion**: Should RD outputs be split by type (numeric → C2, categorical → C3) or kept together? Recommend split for architectural consistency.

3. **C1 definition scope**: Should C1 include trivial rolling features (session, 12-bar stats) or strictly single-bar? Recommend amending definition to "C1 = single-bar; C1+ = trivial rolling" or restructuring views.

4. **Threshold versioning strategy**: How will threshold parameters be versioned for replay? Must be resolved before C3 Python implementation.

5. **`news_flag` disposition**: Retain in B-layer with provenance spec, move to metadata, or require external calendar? Recommend provenance documentation or reclassification to metadata.

**Action**: These decisions should be recorded in `docs/decisions.md` before any tier restructuring is applied to this document.

---

## Appendix: Field Count Summary

| Tier | Field Count | Derivable from OHLC |
|------|-------------|---------------------|
| B (identity + OHLC + meta) | 22 | N/A (raw inputs) |
| C1 (single-bar math) | 6 | YES |
| C2 (structure/memory) | ~65 | YES |
| C3 (tags/regime) | ~30 | YES |
| Decision (L3) | 16 | N/A (synthesized) |
| **Total** | ~139 | |

> **Note**: Field counts may change pending resolution of Design Note issues A–C.

---

*Document generated from Pine script analysis and repository inspection.*
