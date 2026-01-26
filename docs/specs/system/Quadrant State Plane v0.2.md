1) Quadrant State Plane v0.2 — Full Spec
1.0 Purpose

Create a deterministic “state space” for each 2H block (A–L) as a point 
(
𝑥
,
𝑦
)
(x,y), where a day becomes a trajectory. This is descriptive, joins to Option C outcomes for studies, and produces Path 1 evidence artifacts (plots + tables). It must not modify or reinterpret the frozen Option B score library or canonical feature views. 

PATH1_EVIDENCE_PROTOCOL_v1_0

OPTION_B_PATH1_STATUS

1.1 Canonical Inputs (read-only)

Must be derived only from canonical inputs:

derived.v_ovc_l1_features_v0_1

derived.v_ovc_l2_features_v0_1

derived.v_ovc_l3_features_v0_1 (optional; only for contextual labeling)

Option C outcomes view is allowed for studies, not for constructing x/y. 

OPTION_B_PATH1_STATUS

WORKFLOW_STATUS

1.2 Output Objects (downstream-only)

Create new view(s) (no breaking changes):

derived.v_ovc_state_plane_v0_2 (block-level coordinates + quadrant)

Optional: derived.v_ovc_state_plane_daypath_v0_2 (day trajectory summary)

No writes to Notion; Notion is a decision surface and must not receive raw facts/features. 

OVC_DATA_FLOW_CANON_v0.1

2) The Axes (x, y)
2.1 X-axis: Energy / Participation score (x_energy)

Goal: measure “how much initiative/impulse is present” (trend impulse vs rotational quiet).

Design constraints: only use existing L1/L2 columns; deterministic; scale 0–1.

Recommended definition (robust + simple):
Compute a weighted blend of three normalized components:

Range intensity (bigger-than-usual movement)

rng_z = z-score of block range vs rolling baseline (use an existing range_z_* if present; otherwise approximate from L2 rolling stats)

rng_comp = clamp01(sigmoid(rng_z))

Body participation (commitment vs wicks)

body_ratio (body / range) already common in L1 primitives

body_comp = clamp01(body_ratio)

Directional efficiency (clean travel vs chop)

If you already have a directional efficiency / displacement proxy in L2: use it

If not, approximate with something like abs(close-open)/range aggregated to block (but prefer existing feature columns)

Then:

𝑥
_
𝑒
𝑛
𝑒
𝑟
𝑔
𝑦
=
clamp01
(
𝑤
𝑟
⋅
𝑟
𝑛
𝑔
_
𝑐
𝑜
𝑚
𝑝
+
𝑤
𝑏
⋅
𝑏
𝑜
𝑑
𝑦
_
𝑐
𝑜
𝑚
𝑝
+
𝑤
𝑒
⋅
𝑒
𝑓
𝑓
_
𝑐
𝑜
𝑚
𝑝
)
x_energy=clamp01(w
r
	​

⋅rng_comp+w
b
	​

⋅body_comp+w
e
	​

⋅eff_comp)

Default weights (v0.2 baseline): w_r=0.45, w_b=0.35, w_e=0.20.

Note: if a required column doesn’t exist, v0.2 spec must explicitly name the substitute column(s) to keep the view buildable.

2.2 Y-axis: Regime-change score (y_shift)

Goal: measure “continuation vs structural shift” (are we flipping or staying in regime).

Recommended definition:
Blend:

Direction flip indicator from L2/L3 (preferred)

e.g., dir_change / CHoCH proxy / trend flip flag if it exists

Displacement against prior bias (if you have a bias direction tag)

e.g., compare current direction to previous N-block direction

Shock / discontinuity proxy

abrupt jump in range or return sign change + large body

Then scale to 
[
−
1
,
+
1
]
[−1,+1] where:

negative = continuation / stability

positive = change / shift

𝑦
_
𝑠
ℎ
𝑖
𝑓
𝑡
=
clamp
[
−
1
,
1
]
(
𝑎
⋅
𝑓
𝑙
𝑖
𝑝
+
𝑏
⋅
𝑐
𝑜
𝑛
𝑡
𝑟
𝑎
+
𝑐
⋅
𝑠
ℎ
𝑜
𝑐
𝑘
)
y_shift=clamp
[−1,1]
	​

(a⋅flip+b⋅contra+c⋅shock)

Baseline weights: a=0.5, b=0.3, c=0.2.

3) Quadrants (4-state classification)

Let:

E_hi threshold for energy (default 0.60)

S_hi threshold for shift magnitude (default 0.35 on |y_shift|)

Define:

Q1 Expansion-like: x_energy >= E_hi and y_shift <= +S_hi (high energy, stable/continuation)

Q2 Consolidation-like: x_energy < E_hi and y_shift <= +S_hi (low energy, stable/acceptance)

Q3 Reversal-like: x_energy >= E_hi and y_shift > +S_hi (high energy, regime shift)

Q4 Retracement-like: x_energy < E_hi and y_shift > +S_hi (lower energy, corrective shift)

Also store:

quadrant_confidence = distance from thresholds (helps debug boundary jitter)

state_plane_version = 'v0_2'

3.1 Threshold governance (no silent magic)

Thresholds must be explicit and versioned. Store them in ovc_cfg.threshold_packs (already exists as config infrastructure). 

OPERATING_BASE

PIPELINE_REALITY_MAP_v0.1

Create a pack e.g.:

state_plane_v0_2_default with parameters: E_hi, S_hi, weights, and column mapping names (so the view is replayable).

4) View Contract: derived.v_ovc_state_plane_v0_2
4.1 Columns (minimum)

block_id (PK identity)

sym, date_ny, block2h (A–L), block_start_ts, block_end_ts (or ms)

x_energy numeric

y_shift numeric

quadrant_id text (Q1–Q4)

quadrant_name text (Expansion/Consolidation/Reversal/Retracement)

quadrant_confidence numeric

threshold_pack_id text

source_views json (names of the v0.1 feature/outcome views pinned)

4.2 Joins

Base join key: block_id (already canonical). 

OPERATING_BASE

Inputs:

join L1/L2/L3 feature views on block_id

do not join outcomes inside the state plane view (keep it pure). Outcomes are for studies.

5) Day Trajectories (Path 1 evidence outputs)
5.1 Path artifacts per day

For a given day (12 blocks), output:

trajectory.csv — ordered A→L with x,y,quadrant

trajectory.png — plotted points connected in time order

quadrant_string.txt — e.g. Q2 Q2 Q1 Q1 Q3 ...

path_metrics.json — simple descriptors:

path_length, net_displacement, efficiency, jump_count (|Δy| > threshold), orbit_score (optional)

5.2 Evidence runs must remain observational

Path 1 governance: no signals, no thresholds optimized to outcomes, no “best model” claims. This stays a descriptive lens that can be joined to outcomes for association studies only. 

PATH1_EVIDENCE_PROTOCOL_v1_0

OPTION_B_PATH1_STATUS

6) Where Option D Models fit (without breaking anything)

Your Phase I/II/III idea is compatible with current governance:

Frozen manifold: 
𝑋
=
𝐶
1
×
𝐶
2
×
𝐶
3
X=L1×L2×L3, 
𝑌
=
Y= Option C outcomes (canonical) 

WORKFLOW_STATUS

WORKFLOW_STATUS

Option D Models: downstream registry + runs (append-only), consuming dataset specs produced from Path 1 artifacts.

Path 2: stays disposable interpretation-only, forbidden from touching live canonical views.