# Claim Binding v0.1

## Scope
This document defines the strongest claims supported by the current evidence anchors, and explicitly lists what is NOT claimed.

## Evidence Anchors
- Anchor A: reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_20260122.md (2026-01-22, run_id=ANCHOR_GBPUSD_2026-01-16_optionc_v0.1_1.._3, tool=Option C v0.1)
- Anchor B: reports/path1/evidence/runs/p1_20260121_001/RUN.md (2026-01-17, run_id=p1_20260121_001, tool=state_plane_v0_2 / threshold_pack state_plane_v0_2_default v1)
- Anchor C: reports/verification/REPRO_REPORT_ANCHOR_GBPUSD_2022-09-26_path1_state_plane_v0_2.md (2026-01-22, run_ids=p1_20260122_001 & p1_20260122_002, tool=state_plane_v0_2 / threshold_pack state_plane_v0_2_default v1)

## Definitions
- “Reproducible”: byte-identical outputs except for fields listed under Allowed Variance.
- “Deterministic”: reruns over identical inputs yield identical outputs under the same tool versions and params.

## Allowed Variance
- run_report JSON `started_at`, `finished_at` (timestamp fields explicitly allowed to differ per Anchor A)

## Claims (We Can Claim C — and Nothing More)
C1. The Option C v0.1 anchor for GBPUSD 2026-01-16 shows byte-identical spotchecks across three runs and run_report JSON equivalence except allowed timestamps.  
C2. The Path 1 state_plane_v0_2 run p1_20260121_001 for GBPUSD 2026-01-17 produced the expected state_plane_v0_2 artifacts and recorded 12 blocks with 12 valid points.  
C3. The state_plane_v0_2 run p1_20260121_001 used threshold pack state_plane_v0_2_default v1 as recorded in the run metadata.  
C4. The paired state_plane_v0_2 runs p1_20260122_001 and p1_20260122_002 for GBPUSD 2022-09-26 are byte-identical across emitted artifacts (trajectory, quadrant string, path metrics, PNG) and share the same normalized fingerprint hash (`content_hash_norm`) under normalization rule v0.1.

## Non-Claims (Explicitly Not Claimed)
N1. No predictive or causal claims about outcomes or future price behavior.  
N2. No claims about symbols, dates, or runs outside the two anchors listed.  
N3. No claims about data completeness beyond what is explicitly recorded in the anchors.  
N4. No claims about trading rules, thresholds, or strategy suitability.

## Next Claim Unlock Conditions
- Add a Path 1 state_plane_v0_2 reproducibility report for a stress-case day with explicit allowed variance.
- Add normalized-hash reproducibility evidence for DayFingerprint v0.1 across reruns.
- Add additional anchors covering other symbols/dates and document their tool versions.
