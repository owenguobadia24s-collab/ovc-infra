**Rule:**  
To locate the canonical state-plane trajectory for a given (symbol, date_ny):

1. Enumerate all subdirectories under reports/path1/evidence/runs/ matching p1_*/outputs/state_plane_v0_2/trajectory.csv.
2. For each, read path_metrics.json or RUN.md to extract symbol and date_ny.
3. Select the run with the highest NNN for the matching (symbol, date_ny).
4. Use the files in that directory as the official artifacts for that day.

**Reference Implementation:**  
- See scripts/path1/run_trajectory_families.py (lines 65–80, 181, 202) for the current discovery logic.

---

Trajectory Families PR #2 MUST rely on fingerprint source paths, not rescan evidence runs.
