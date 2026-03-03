# WAVE_ENFORCEMENT_COVERAGE_v1

Audit Semantics: For this frozen v1 audit, `Validation` means an explicit schema/SQL guard layer only (deterministic validator scripts alone do not satisfy this field).

| Wave | Invariant | Contract | Script | Test | CI | Validation | Seal | Drift | Score | Strength |
|---|---|---|---|---|---|---|---|---|---:|---|
| W1 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✖ | 7 | HARD ENFORCED |
| W2 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✖ | 7 | HARD ENFORCED |
| W3 | ✔ | ✔ | ✔ | ✖ | ✔ | ✔ | ✔ | ✖ | 6 | STRONG |
| W4 | ✔ | ✔ | ✔ | ✔ | ✔ | ✖ | ✔ | ✔ | 7 | HARD ENFORCED |
| W5 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 8 | HARD ENFORCED |
| W6 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | 8 | HARD ENFORCED |

v1 Frozen on 2026-02-28. Future audits must produce v2 rather than modify this file.
