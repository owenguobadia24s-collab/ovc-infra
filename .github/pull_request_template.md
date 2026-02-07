diff --git a/.github/pull_request_template.md b/.github/pull_request_template.md
new file mode 100644
index 0000000..b7a1c2d
--- /dev/null
+++ b/.github/pull_request_template.md
@@ -0,0 +1,74 @@
+# PR Summary
+<!-- What is changing and why? Keep it factual. -->
+
+## What changed
+- 
+
+## Why it changed
+- 
+
+## Scope / risk
+- 
+
+---
+
+# Change Classification (Required)
+This repo uses a **descriptive** change classifier (not enforcement).  
+Run it locally and paste results below.
+
+## Run command
+```bash
+# default (detect base automatically)
+python scripts/governance/classify_change.py --base origin/main
+
+# staged-only (optional)
+python scripts/governance/classify_change.py --staged
+
+# json output (recommended for copy/paste)
+python scripts/governance/classify_change.py --base origin/main --json
+```
+
+## Reported classification
+**CLASS:** <!-- e.g. A / B / C / D / E or multi: A,C -->
+**REQUIRED(<class>):** <!-- paste REQUIRED(...) lines -->
+**FILES:** <!-- paste FILES=n -->
+
+## Paste classifier output
+<!-- Paste either text output or JSON output verbatim -->
+```text
+<paste output here>
+```
+
+---
+
+# Governance Acknowledgment (Required)
+Check the items your classifier reported as REQUIRED(<class>).  
+Do not check items that are not required for this PR’s classes.
+
+### REQUIRED(A) — Observation-only / low-risk
+- [ ] REQUIRED(A) satisfied (if applicable)
+
+### REQUIRED(B) — Contract / schema / canon-affecting
+- [ ] REQUIRED(B) satisfied (if applicable)
+
+### REQUIRED(C) — Pipeline / workflow / automation-affecting
+- [ ] REQUIRED(C) satisfied (if applicable)
+
+### REQUIRED(D) — Core runtime / behavior / invariants
+- [ ] REQUIRED(D) satisfied (if applicable)
+
+### REQUIRED(E) — Repo hygiene / tooling / tests / docs
+- [ ] REQUIRED(E) satisfied (if applicable)
+
+---
+
+# Evidence / Artifacts
+<!-- Link to runs, manifests, seals, screenshots, or logs. -->
+- 
