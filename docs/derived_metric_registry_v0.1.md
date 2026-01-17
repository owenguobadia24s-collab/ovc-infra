# Derived Metric Registry v0.1

Scope: metrics exported by Pine script in `pine/ovc_panelsv0.1` (MIN + FULL). Every metric is classified into one class.

Class legend:
- DBF: Deterministic Bar Features (bar-local or micro 2-bar reference).
- WDF: Windowed Derived Features (explicit lookbacks, rolling sums, pivots, or HTF).
- CIX: Composite Indexes (weighted or normalized scores).
- EVO: Event/Decision Outputs (tags, categorical states, decisions).
- QAF: Quality/Assurance Flags (readiness or guard rails).
- PMETA: Process/Identity Metadata (IDs, versioning, config inputs).
## META / IDs
- metric_key: ver; description: Export schema version string.; class: PMETA; inputs: exp_schema (input).; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: profile; description: Export profile literal (MIN or FULL).; class: PMETA; inputs: profile input literal.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: schema_full; description: FULL schema label string.; class: PMETA; inputs: constant OVC_FULL_V0_1.; window_spec: none.; determinism: deterministic (constant).; failure_modes/guards: none.; version: v0.1
- metric_key: scheme_min; description: MIN scheme label string.; class: PMETA; inputs: constant export_contract_v0.1_min_r1.; window_spec: none.; determinism: deterministic (constant).; failure_modes/guards: none.; version: v0.1
- metric_key: sym; description: Symbol ticker.; class: PMETA; inputs: syminfo.ticker.; window_spec: none.; determinism: deterministic (platform input).; failure_modes/guards: none.; version: v0.1
- metric_key: tz; description: Export time zone string.; class: PMETA; inputs: EXP_TZ constant.; window_spec: none.; determinism: deterministic (constant).; failure_modes/guards: none.; version: v0.1
- metric_key: date_ny; description: NY-anchored date (17:00 anchor).; class: PMETA; inputs: bar_close_ms, EXP_TZ.; window_spec: none.; determinism: deterministic (time-derived).; failure_modes/guards: none.; version: v0.1
- metric_key: bar_close_ms; description: 2H container bar close timestamp (ms).; class: PMETA; inputs: time("120").; window_spec: none.; determinism: deterministic (time-derived).; failure_modes/guards: none.; version: v0.1
- metric_key: block2h; description: 2H segment letter A-L.; class: PMETA; inputs: bar_close_ms, EXP_TZ.; window_spec: none.; determinism: deterministic (time-derived).; failure_modes/guards: none.; version: v0.1
- metric_key: block4h; description: 4H block label from 2H segment.; class: PMETA; inputs: block2h.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: block_id; description: Canonical 2H block id (ymd-seg-sym).; class: PMETA; inputs: ymd, seg, sym.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: block2h_id; description: Canonical 2H block id (same format as block_id).; class: PMETA; inputs: ymd, seg, sym.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: block4h_id; description: Canonical 4H block id (ymd-4h-sym).; class: PMETA; inputs: ymd, block4h, sym.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: bid; description: FULL alias of block_id.; class: PMETA; inputs: ymd, seg, sym.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: bid4h; description: FULL 4H block id (ymd-4h-sym).; class: PMETA; inputs: ymd, block4h, sym.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: ymd; description: Compact date (YYYYMMDD) from NY day start.; class: PMETA; inputs: bar_close_ms, EXP_TZ.; window_spec: none.; determinism: deterministic (time-derived).; failure_modes/guards: none.; version: v0.1
- metric_key: seg; description: Segment letter A-L from NY anchor.; class: PMETA; inputs: bar_close_ms, EXP_TZ.; window_spec: none.; determinism: deterministic (time-derived).; failure_modes/guards: none.; version: v0.1
- metric_key: build_id; description: Build id string.; class: PMETA; inputs: exp_buildId input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: source; description: Export source string.; class: PMETA; inputs: exp_source input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: note; description: Optional export note.; class: PMETA; inputs: exp_note input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: news_flag; description: News flag (0/1).; class: PMETA; inputs: exp_news input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1

## BAR
- metric_key: o; description: Open price.; class: DBF; inputs: open.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: h; description: High price.; class: DBF; inputs: high.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: l; description: Low price.; class: DBF; inputs: low.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: c; description: Close price.; class: DBF; inputs: close.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: rng; description: Bar range (high - low).; class: DBF; inputs: h, l.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: body; description: Absolute body size (abs(close - open)).; class: DBF; inputs: o, c.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: dir; description: Direction of close vs open (UP/DN/0 or 1/-1/0).; class: DBF; inputs: o, c.; window_spec: none.; determinism: deterministic.; failure_modes/guards: none.; version: v0.1
- metric_key: ret; description: Return (close - open) / open, open=0 -> 0.; class: DBF; inputs: o, c.; window_spec: none.; determinism: deterministic.; failure_modes/guards: open=0 uses 0.; version: v0.1

## L1 MAIN (tags + composites)
- metric_key: state_tag; description: MOVE/ROTATE classification from OR, RER, CLV_signed and thresholds.; class: CIX; inputs: or, rer, clv, th_rotate_OR, th_move_OR, th_move_RER, th_move_CLV.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr missing or thresholds not met.; version: v0.1
- metric_key: value_tag; description: ACCEPT+/ACCEPT-/NEUTRAL from SD and threshold.; class: CIX; inputs: sd, th_accept_SD.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if sd missing.; version: v0.1
- metric_key: event; description: Dominant event tag from sweeps and outside acceptance.; class: CIX; inputs: took_hi, took_lo, oa.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if oa missing.; version: v0.1
- metric_key: vr; description: Volatility ratio rr / SMA(rr, 20).; class: WDF; inputs: rr.; window_spec: 20-bar SMA of rr.; determinism: deterministic.; failure_modes/guards: null until 20 bars and rr_sma20 != 0.; version: v0.1
- metric_key: ts; description: Trend strength (CleanMove * Commit * TrapPenalty).; class: CIX; inputs: rer, or, clv, took_hi, took_lo.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr or clv missing.; version: v0.1
- metric_key: cp; description: Chop score from OR, MC3, VF3, and wick weight.; class: CIX; inputs: or, mc3, vf3, brb, cp_wOR, cp_wMC, cp_wVF, cp_wWick.; window_spec: 3-bar memory for mc3/vf3.; determinism: deterministic.; failure_modes/guards: null if inputs missing.; version: v0.1
- metric_key: cp_tag; description: Chop tag HIGH/MID/LOW from CP thresholds.; class: CIX; inputs: cp, cp_hi, cp_lo.; window_spec: none.; determinism: deterministic.; failure_modes/guards: null if cp missing.; version: v0.1
- metric_key: tt; description: Trigger flag (1/0) from SD, OR, RER, CLV, OA, sweeps, and flip gate.; class: CIX; inputs: sd, or, rer, clv, oa, took_hi, took_lo, vflip, tt_minSD, tt_orMax, tt_needFlip, th_move_*.; window_spec: 2-bar micro via rr and 1-bar flip.; determinism: deterministic.; failure_modes/guards: null if rr missing; flip gate uses prior bar.; version: v0.1
- metric_key: tis; description: Time-in-state count (bars since StateTag change + 1).; class: WDF; inputs: state_tag history.; window_spec: barssince(StateTag change).; determinism: deterministic.; failure_modes/guards: null if state_tag missing.; version: v0.1

## L1 REF (micro RR2)
- metric_key: rr; description: Micro range from prior two bars.; class: WDF; inputs: h[1], h[2], l[1], l[2].; window_spec: 2-bar lookback.; determinism: deterministic.; failure_modes/guards: null if missing history.; version: v0.1
- metric_key: rm; description: Micro midpoint of rr_high and rr_low.; class: WDF; inputs: rr_high, rr_low.; window_spec: 2-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: q1; description: Lower quartile of micro range.; class: WDF; inputs: rr_low, rr.; window_spec: 2-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: q3; description: Upper quartile of micro range.; class: WDF; inputs: rr_low, rr.; window_spec: 2-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: band; description: Close band 0..3 from (close - rr_low) / rr.; class: WDF; inputs: c, rr_low, rr.; window_spec: 2-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr missing; clamped to 0..3.; version: v0.1

## L1 STATE
- metric_key: rer; description: Range expansion ratio (bar range / rr).; class: WDF; inputs: rng, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: or; description: Overlap ratio vs rr.; class: WDF; inputs: h, l, rr_high, rr_low, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: clv; description: Signed close location value (2*CLV - 1).; class: DBF; inputs: c, l, rng.; window_spec: none.; determinism: deterministic.; failure_modes/guards: null if rng=0.; version: v0.1
- metric_key: brb; description: Body-to-range ratio.; class: DBF; inputs: body, rng.; window_spec: none.; determinism: deterministic.; failure_modes/guards: null if rng=0.; version: v0.1
- metric_key: bodyrr; description: Body-to-rr ratio.; class: WDF; inputs: body, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1

## L1 VALUE
- metric_key: sd; description: Signed distance to rm in rr units.; class: WDF; inputs: c, rm, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: out; description: OutsideTag (OUT+/OUT-/IN) from OA sign.; class: CIX; inputs: oa.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if oa missing.; version: v0.1
- metric_key: oa; description: Outside acceptance (signed).; class: WDF; inputs: c, rr_high, rr_low, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: mc; description: Midcross flag (1 if l <= rm <= h).; class: WDF; inputs: l, h, rm.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if missing rm.; version: v0.1
- metric_key: mc3; description: 3-bar sum of mc.; class: WDF; inputs: mc and mc history.; window_spec: 3-bar rolling sum.; determinism: deterministic.; failure_modes/guards: missing history treated as 0.; version: v0.1
- metric_key: vflip; description: Value flip flag (sd sign change vs prior bar).; class: WDF; inputs: sd, sd[1].; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: 0 if sd missing.; version: v0.1
- metric_key: vf3; description: 3-bar sum of vflip.; class: WDF; inputs: vflip history.; window_spec: 3-bar rolling sum.; determinism: deterministic.; failure_modes/guards: missing history treated as 0.; version: v0.1

## L1 LIQ
- metric_key: swhi; description: SweepHigh magnitude in rr units.; class: WDF; inputs: h, rr_high, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: swlo; description: SweepLow magnitude in rr units.; class: WDF; inputs: l, rr_low, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr missing.; version: v0.1
- metric_key: took_hi; description: TookHigh flag (1 if swhi > 0).; class: WDF; inputs: swhi.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if swhi null.; version: v0.1
- metric_key: took_lo; description: TookLow flag (1 if swlo > 0).; class: WDF; inputs: swlo.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if swlo null.; version: v0.1
- metric_key: hi_ran; description: HighRan flag (took_hi and close >= rr_high).; class: WDF; inputs: took_hi, c, rr_high.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if rr_high missing.; version: v0.1
- metric_key: hi_rev; description: HighRev flag (took_hi and close < rr_high).; class: WDF; inputs: took_hi, c, rr_high.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if rr_high missing.; version: v0.1
- metric_key: lo_ran; description: LowRan flag (took_lo and close <= rr_low).; class: WDF; inputs: took_lo, c, rr_low.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if rr_low missing.; version: v0.1
- metric_key: lo_rev; description: LowRev flag (took_lo and close > rr_low).; class: WDF; inputs: took_lo, c, rr_low.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: 0 if rr_low missing.; version: v0.1

## L1 D2K
- metric_key: d2rm; description: Distance to rm (same as sd).; class: WDF; inputs: sd.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if sd missing.; version: v0.1
- metric_key: d2q1; description: Distance to q1 in rr units.; class: WDF; inputs: c, q1, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: d2q3; description: Distance to q3 in rr units.; class: WDF; inputs: c, q3, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: d2rrh; description: Distance to rr_high in rr units.; class: WDF; inputs: c, rr_high, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1
- metric_key: d2rrl; description: Distance to rr_low in rr units.; class: WDF; inputs: c, rr_low, rr.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: null if rr=0 or missing.; version: v0.1

## L1 OUT (X-1)
- metric_key: out_ready; description: Outcome readiness flag (has prior rr/rm/sd).; class: QAF; inputs: rr[1], rm[1], sd[1].; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: false if missing history.; version: v0.1
- metric_key: rtrm; description: Return-to-prev-rm flag.; class: WDF; inputs: h, l, rm[1].; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rm[1] missing.; version: v0.1
- metric_key: nxtext; description: Next extension based on sd_prev sign.; class: WDF; inputs: h, l, rm[1], rr[1], sd[1].; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr[1] missing.; version: v0.1
- metric_key: nxtsd; description: Next SD vs previous rm/rr.; class: WDF; inputs: c, rm[1], rr[1].; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: null if rr[1] missing.; version: v0.1
- metric_key: hint1; description: Outcome hint from rtrm (Revert/NoRM).; class: WDF; inputs: rtrm.; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: empty if not ready.; version: v0.1
- metric_key: hint2; description: Outcome hint from nxtext magnitude (Strong/Weak).; class: WDF; inputs: nxtext.; window_spec: 1-bar lookback.; determinism: deterministic.; failure_modes/guards: empty if not ready.; version: v0.1

## L1 KLS (full)
- metric_key: kls_mode_l1; description: KLS mode selection string.; class: PMETA; inputs: l1_kls_mode input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: pooln_l1; description: Pool size for KLS levels.; class: WDF; inputs: l1_pool built from micro/meso/macro/day/session levels.; window_spec: lookbacks l1_mesoN, l1_macroN, l1_dayN, session.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: near_lvl; description: Nearest KLS level to close.; class: WDF; inputs: close, l1_pool, rr.; window_spec: lookbacks l1_mesoN, l1_macroN, l1_dayN, session.; determinism: deterministic.; failure_modes/guards: null if KLS disabled or rr=0.; version: v0.1
- metric_key: near_src; description: Source label for near_lvl.; class: CIX; inputs: l1_poolSrc.; window_spec: same as near_lvl.; determinism: deterministic.; failure_modes/guards: "na" if KLS disabled.; version: v0.1
- metric_key: near_dr; description: Distance to near_lvl in rr units.; class: WDF; inputs: close, near_lvl, rr.; window_spec: same as near_lvl.; determinism: deterministic.; failure_modes/guards: null if rr=0 or near_lvl missing.; version: v0.1
- metric_key: conf_l1; description: Confluence count within conf width.; class: WDF; inputs: l1_pool, near_lvl, rr, l1_kls_confW.; window_spec: same as near_lvl.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: age_l1; description: Bars since touching near_lvl.; class: WDF; inputs: near_lvl, rr, l1_kls_confW.; window_spec: barssince touch.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: hitsn_l1; description: Rolling hit count for near_lvl.; class: WDF; inputs: near_lvl, rr, l1_kls_confW.; window_spec: rollsum over l1_kls_hitsN.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: decay_l1; description: Age decay (0.5^(age/halfLife)).; class: WDF; inputs: age_l1, l1_kls_halfLife.; window_spec: barssince-based decay.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: width_l1; description: KLS confluence width parameter.; class: PMETA; inputs: l1_kls_confW input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1
- metric_key: kscore_l1; description: Weighted KLS score.; class: CIX; inputs: conf_l1, near_dr, hitsn_l1, decay_l1, weights l1_kls_w*.; window_spec: same as KLS windows.; determinism: deterministic.; failure_modes/guards: null if inputs missing.; version: v0.1
- metric_key: ktag_l1; description: KLS tag HIGH/MID/LOW from kscore_l1.; class: CIX; inputs: kscore_l1, l1_kls_hiScore, l1_kls_loScore.; window_spec: none.; determinism: deterministic.; failure_modes/guards: "na" if kscore_l1 missing.; version: v0.1

## L2 CONTEXT
- metric_key: rrc; description: Context range (SMA of rr).; class: WDF; inputs: rr.; window_spec: SMA length rrcLen.; determinism: deterministic.; failure_modes/guards: null until rrcLen bars.; version: v0.1
- metric_key: vrc; description: Context volatility ratio (rr / rrc).; class: WDF; inputs: rr, rrc.; window_spec: rrcLen for rrc.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or missing.; version: v0.1

## L2 STRUCTURE
- metric_key: lastpivot; description: Last pivot label (Hi/Lo).; class: CIX; inputs: pivot highs/lows.; window_spec: pivotL/pivotR lookback.; determinism: deterministic.; failure_modes/guards: "na" until pivot forms.; version: v0.1
- metric_key: swingdir; description: Swing direction from last pivot (+1/-1).; class: CIX; inputs: lastpivot.; window_spec: pivotL/pivotR lookback.; determinism: deterministic.; failure_modes/guards: "na" until pivot forms.; version: v0.1
- metric_key: phidr; description: Distance to last pivot high in RRc units.; class: WDF; inputs: lastPH, close, rrc.; window_spec: pivotL/pivotR and rrcLen.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or missing.; version: v0.1
- metric_key: plodr; description: Distance to last pivot low in RRc units.; class: WDF; inputs: lastPL, close, rrc.; window_spec: pivotL/pivotR and rrcLen.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or missing.; version: v0.1
- metric_key: struct; description: Raw structure state (HH/LH/HL/LL).; class: CIX; inputs: lastPH, prevPH, lastPL, prevPL.; window_spec: pivotL/pivotR lookback.; determinism: deterministic.; failure_modes/guards: "na" until pivots exist.; version: v0.1
- metric_key: struct_state; description: Alias of struct (MIN key).; class: CIX; inputs: StructState.; window_spec: pivotL/pivotR lookback.; determinism: deterministic.; failure_modes/guards: "na" until pivots exist.; version: v0.1
- metric_key: ss; description: Simplified structure state (UP/DN/MIX).; class: CIX; inputs: struct.; window_spec: pivotL/pivotR lookback.; determinism: deterministic.; failure_modes/guards: "na" if struct is "na".; version: v0.1

## L2 TREND
- metric_key: rmdrift; description: Drift of dayRM over driftN in RRc units.; class: WDF; inputs: dayRM, dayRM[driftN], rrc.; window_spec: driftN bars.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or missing.; version: v0.1
- metric_key: dirrun; description: Length of micro direction run.; class: WDF; inputs: sd, dirMinSD, dir history.; window_spec: variable run length.; determinism: deterministic.; failure_modes/guards: 0 if dir is 0.; version: v0.1
- metric_key: tr; description: TrendTag from rmdrift and dirrun thresholds.; class: CIX; inputs: rmdrift, dirrun, driftThr, runMinCamp, runMaxRng.; window_spec: driftN and run length.; determinism: deterministic.; failure_modes/guards: "na" if rmdrift missing.; version: v0.1
- metric_key: trend_tag; description: Alias of tr (MIN key).; class: CIX; inputs: TrendTag.; window_spec: driftN and run length.; determinism: deterministic.; failure_modes/guards: "na" if rmdrift missing.; version: v0.1

## L2 SPACE
- metric_key: space_up; description: Nearest upward target distance in RRc units.; class: WDF; inputs: pivots, session hi/lo, day/macro levels, KLS levels, rrc.; window_spec: l2_mesoN/l2_macroN/l2_dayN and session.; determinism: deterministic.; failure_modes/guards: null if no targets or rrc=0.; version: v0.1
- metric_key: space_dn; description: Nearest downward target distance in RRc units.; class: WDF; inputs: pivots, session hi/lo, day/macro levels, KLS levels, rrc.; window_spec: l2_mesoN/l2_macroN/l2_dayN and session.; determinism: deterministic.; failure_modes/guards: null if no targets or rrc=0.; version: v0.1
- metric_key: space_min; description: Min of space_up and space_dn.; class: WDF; inputs: space_up, space_dn.; window_spec: same as space_up/space_dn.; determinism: deterministic.; failure_modes/guards: null if both missing.; version: v0.1
- metric_key: sp; description: SpaceTag (HIGH/MID/LOW) from space_min.; class: CIX; inputs: space_min, spaceLo, spaceMd.; window_spec: same as space_up/space_dn.; determinism: deterministic.; failure_modes/guards: "na" if space_min missing.; version: v0.1
- metric_key: space_tag; description: Alias of sp (MIN key).; class: CIX; inputs: SpaceTag.; window_spec: same as space_up/space_dn.; determinism: deterministic.; failure_modes/guards: "na" if space_min missing.; version: v0.1
- metric_key: up_src; description: Source label for nearest upward target.; class: CIX; inputs: candidate sources (pivots, session, day, macro, KLS).; window_spec: same as space_up.; determinism: deterministic.; failure_modes/guards: "na" if no targets.; version: v0.1
- metric_key: dn_src; description: Source label for nearest downward target.; class: CIX; inputs: candidate sources (pivots, session, day, macro, KLS).; window_spec: same as space_dn.; determinism: deterministic.; failure_modes/guards: "na" if no targets.; version: v0.1
- metric_key: up_lvl; description: Price level for nearest upward target.; class: WDF; inputs: chosen target level.; window_spec: same as space_up.; determinism: deterministic.; failure_modes/guards: null if no target.; version: v0.1
- metric_key: dn_lvl; description: Price level for nearest downward target.; class: WDF; inputs: chosen target level.; window_spec: same as space_dn.; determinism: deterministic.; failure_modes/guards: null if no target.; version: v0.1

## L2 HTF
- metric_key: sd4; description: Higher timeframe SD (tf4).; class: WDF; inputs: HTF OHLC via request.security.; window_spec: tf4 timeframe.; determinism: deterministic (HTF data).; failure_modes/guards: null if HTF disabled or missing.; version: v0.1
- metric_key: sdd; description: Daily timeframe SD (tfD).; class: WDF; inputs: HTF OHLC via request.security.; window_spec: tfD timeframe.; determinism: deterministic (HTF data).; failure_modes/guards: null if HTF disabled or missing.; version: v0.1
- metric_key: htf4; description: HTF4 direction tag from sd4.; class: CIX; inputs: sd4, htf_on.; window_spec: tf4 timeframe.; determinism: deterministic.; failure_modes/guards: "na" if sd4 missing.; version: v0.1
- metric_key: htfd; description: HTFD direction tag from sdd.; class: CIX; inputs: sdd, htf_on.; window_spec: tfD timeframe.; determinism: deterministic.; failure_modes/guards: "na" if sdd missing.; version: v0.1
- metric_key: htf_stack; description: HTF alignment string (ALIGNED/SPLIT/CONTRA/NA).; class: CIX; inputs: sd4, sdd, microDir.; window_spec: tf4/tfD timeframe.; determinism: deterministic.; failure_modes/guards: "NA" if HTF missing.; version: v0.1
- metric_key: with_htf; description: WithHTF flag (Y/N).; class: CIX; inputs: microDir, sd4.; window_spec: tf4 timeframe.; determinism: deterministic.; failure_modes/guards: "N" if not aligned.; version: v0.1
- metric_key: mdir; description: Micro direction string (UP/DN/0).; class: CIX; inputs: microDir from sd.; window_spec: 2-bar micro via rr.; determinism: deterministic.; failure_modes/guards: "0" if sd missing.; version: v0.1

## L2 KLS-LITE
- metric_key: kt; description: KTag2 tag HIGH/MID/LOW from KScore2.; class: CIX; inputs: kscore2, l2_kls_hiScore, l2_kls_loScore.; window_spec: l2_kls windows.; determinism: deterministic.; failure_modes/guards: "na" if kscore2 missing.; version: v0.1
- metric_key: kscore2; description: Weighted KLS-lite score.; class: CIX; inputs: l2_Conf, l2_NearDR, hits2, decay2, weights l2_kls_w*.; window_spec: l2_kls_hitsN, l2_mesoN/l2_macroN/l2_dayN and session.; determinism: deterministic.; failure_modes/guards: null if inputs missing.; version: v0.1
- metric_key: kup_dr; description: Distance to nearest above level in RRc units.; class: WDF; inputs: l2_pool, close, rrc.; window_spec: l2_kls_mode and lookbacks.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or no levels.; version: v0.1
- metric_key: kdn_dr; description: Distance to nearest below level in RRc units.; class: WDF; inputs: l2_pool, close, rrc.; window_spec: l2_kls_mode and lookbacks.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or no levels.; version: v0.1
- metric_key: conf2; description: Confluence count for KLS-lite.; class: WDF; inputs: l2_pool, l2_NearLvl, rrm, l2_kls_confW.; window_spec: l2_kls windows.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: age2; description: Bars since touch of l2_NearLvl.; class: WDF; inputs: l2_NearLvl, rrm, l2_kls_confW.; window_spec: barssince touch.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: hits2; description: Rolling hit count for l2_NearLvl.; class: WDF; inputs: l2_NearLvl, rrm, l2_kls_confW.; window_spec: rollsum over l2_kls_hitsN.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: decay2; description: Age decay (0.5^(age/halfLife)).; class: WDF; inputs: age2, l2_kls_halfLife.; window_spec: barssince-based decay.; determinism: deterministic.; failure_modes/guards: null if KLS disabled.; version: v0.1
- metric_key: width2; description: KLS-lite confluence width parameter.; class: PMETA; inputs: l2_kls_confW input.; window_spec: none.; determinism: deterministic (config input).; failure_modes/guards: none.; version: v0.1

## RD (Range Detector)
- metric_key: rd_state; description: Range detector state (RANGE/SOFT_RANGE/NO_RANGE).; class: CIX; inputs: rd_w_rrc, RMdrift, StateTag, rd thresholds.; window_spec: rd_len and driftN.; determinism: deterministic.; failure_modes/guards: "na" if rd disabled or rrc missing.; version: v0.1
- metric_key: rd_brkdir; description: Range break direction (UP/DN/0).; class: CIX; inputs: close, rd_hi, rd_lo, rd_breakTol, StateTag, TT.; window_spec: rd_len.; determinism: deterministic.; failure_modes/guards: "0" if break conditions not met.; version: v0.1
- metric_key: rd_w_rrc; description: RD width in RRc units.; class: WDF; inputs: rd_hi, rd_lo, rrc.; window_spec: rd_len.; determinism: deterministic.; failure_modes/guards: null if rrc=0 or rd disabled.; version: v0.1
- metric_key: rd_hi; description: RD high level (highest high over rd_len).; class: WDF; inputs: high history.; window_spec: rd_len lookback.; determinism: deterministic.; failure_modes/guards: null if rd disabled.; version: v0.1
- metric_key: rd_lo; description: RD low level (lowest low over rd_len).; class: WDF; inputs: low history.; window_spec: rd_len lookback.; determinism: deterministic.; failure_modes/guards: null if rd disabled.; version: v0.1
- metric_key: rd_mid; description: RD midpoint (avg of rd_hi and rd_lo).; class: WDF; inputs: rd_hi, rd_lo.; window_spec: rd_len lookback.; determinism: deterministic.; failure_modes/guards: null if rd_hi/rd_lo missing.; version: v0.1
- metric_key: rd_why; description: RD diagnostic string (width/drift/rot/break flags).; class: CIX; inputs: rd_w_rrc, RMdrift, StateTag.; window_spec: rd_len and driftN.; determinism: deterministic.; failure_modes/guards: "na" if rd disabled.; version: v0.1

## BLOCKSTACK (2H memory)
- metric_key: regime_tag; description: Regime tag (TREND_STABLE/RANGE_STABLE/TRANSITION).; class: CIX; inputs: pCampaign, pRDRange, pChop, pSplit, avgDrift, driftThr.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: "na" if bs disabled.; version: v0.1
- metric_key: regime_dir; description: Regime direction from BiasDir counts.; class: CIX; inputs: BiasDir history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: "na" if bs disabled.; version: v0.1
- metric_key: regime_conf; description: Regime confidence (A/B/C/D).; class: CIX; inputs: pCampaign, pRDRange, pChop, pSplit, pSpaceLow.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: "na" if bs disabled.; version: v0.1
- metric_key: trans_risk; description: Transition risk from flip_rate thresholds.; class: CIX; inputs: flip_rate.; window_spec: bs_flipN lookback.; determinism: deterministic.; failure_modes/guards: "na" if flip_rate missing.; version: v0.1
- metric_key: p_campaign; description: Fraction of CAMPAIGN trend tags.; class: WDF; inputs: TrendTag history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_rdrange; description: Fraction of RD range states.; class: WDF; inputs: RD_State history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_confmove; description: Fraction of confirmed MOVE states.; class: WDF; inputs: TT, StateTag, CPTag history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_chop; description: Fraction of chop states.; class: WDF; inputs: CPTag, StateTag, TT history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_split; description: Fraction of HTF split states.; class: WDF; inputs: HTFStack history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_contra; description: Fraction of HTF contra states.; class: WDF; inputs: HTFStack history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: p_spacelow; description: Fraction of SpaceLow states.; class: WDF; inputs: SpaceMin history.; window_spec: bs_N lookback.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: avg_drift; description: Average RMdrift over bs_N.; class: WDF; inputs: RMdrift history.; window_spec: bs_N SMA.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: avg_space; description: Average SpaceMin over bs_N.; class: WDF; inputs: SpaceMin history.; window_spec: bs_N SMA.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1
- metric_key: flip_rate; description: BiasMode change rate over bs_flipN.; class: WDF; inputs: BiasMode history.; window_spec: bs_flipN rollsum.; determinism: deterministic.; failure_modes/guards: null if bs disabled.; version: v0.1

## L3 / Decision Object
- metric_key: tagstring; description: Composite tag string from L1/L2 tags.; class: CIX; inputs: TrendTag, SS, HTFStack, SpaceTag, KTag2, StateTag, ValueTag, DominantEvent, CPTag, TT.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "na" if inputs missing.; version: v0.1
- metric_key: bias_mode; description: Bias mode (TREND/RANGE/NOISE/TRANSITION).; class: CIX; inputs: TrendTag, HTFStack, SS, StateTag, CPTag, TT, RD_State.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "na" if inputs missing.; version: v0.1
- metric_key: bias_dir; description: Bias direction (UP/DN/0).; class: CIX; inputs: BiasMode, TrendTag, SS, HTFStack, WithHTF, mDir, RMdrift.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "0" if gates fail.; version: v0.1
- metric_key: bias_why; description: Bias rationale string.; class: CIX; inputs: BiasMode, BiasDir, TrendTag, SS, HTFStack, SpaceTag, KTag2, StateTag, ValueTag, DominantEvent, CPTag, TT, WithHTF.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "SYS_OK" with missing parts.; version: v0.1
- metric_key: perm_state; description: Permission state (RED/YELLOW/GREEN/ORANGE).; class: CIX; inputs: BiasMode, HTFStack, SpaceTag, KTag2, StateTag, CPTag, TT.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: defaults to YELLOW.; version: v0.1
- metric_key: rail_src; description: Rail source (RD or SESS).; class: CIX; inputs: rd_hi, rd_lo, l2_sessHi, l2_sessLo, rd_useForL3.; window_spec: rd_len and session.; determinism: deterministic.; failure_modes/guards: "na" if rails invalid.; version: v0.1
- metric_key: rail_loc; description: Rail location (UP_RAIL/DN_RAIL/MID/IN_RANGE/OUTSIDE).; class: CIX; inputs: close, RangeHi, RangeLo, l3_zRailPct, l3_zMidPct.; window_spec: rd_len or session rails.; determinism: deterministic.; failure_modes/guards: "na" if rails invalid.; version: v0.1
- metric_key: tradeable; description: Tradeable decision (Y/N or 1/0).; class: CIX; inputs: PermissionState, BiasDir, RailLoc, targets, CONF_MOVE/CONF_RANGE.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "N" if gates fail.; version: v0.1
- metric_key: conf_l3; description: L3 confidence grade (A/B/C/D).; class: CIX; inputs: PermissionState, SpaceTag, KTag2, Play, targets.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "D" if gates fail.; version: v0.1
- metric_key: play; description: L3 play label.; class: CIX; inputs: PermissionState, BiasDir, RailLoc, DominantEvent.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "NONE" if gates fail.; version: v0.1
- metric_key: pred_dir; description: L3 predicted direction.; class: CIX; inputs: BiasDir, RailLoc, Play.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: "0" if gates fail.; version: v0.1
- metric_key: pred_target; description: L3 predicted target string.; class: CIX; inputs: UpSrc/UpLvl, DnSrc/DnLvl, PredDir.; window_spec: L2 Space windows.; determinism: deterministic.; failure_modes/guards: "na" if target missing.; version: v0.1
- metric_key: timebox; description: L3 timebox label.; class: CIX; inputs: PermissionState, Play.; window_spec: none.; determinism: deterministic.; failure_modes/guards: default TB_0.; version: v0.1
- metric_key: invalidation; description: L3 invalidation label.; class: CIX; inputs: PermissionState, Play, CONF_MOVE/CONF_RANGE, targets.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: default INV_SYS_NA.; version: v0.1
- metric_key: blocker; description: L3 blocker label.; class: CIX; inputs: PermissionState, Play, targets, CONF_MOVE/CONF_RANGE.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: default BLK_DIR_NA.; version: v0.1
- metric_key: reasons; description: L3 reasons string.; class: CIX; inputs: PermissionState, Play, RailLoc, CONF_MOVE/CONF_RANGE.; window_spec: L1/L2 windows as defined above.; determinism: deterministic.; failure_modes/guards: default SYS_NA.; version: v0.1

## QUALITY FLAGS
- metric_key: ready; description: Export readiness flag (is2H and hasHist).; class: QAF; inputs: timeframe and prior bars.; window_spec: 2-bar history.; determinism: deterministic.; failure_modes/guards: false if not 2H or missing history.; version: v0.1
