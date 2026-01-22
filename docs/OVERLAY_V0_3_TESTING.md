# Evidence Pack v0.3 Overlays - Testing & Validation Guide (LIBRARY-ONLY)

**Status:** LIBRARY-ONLY — overlays are not wired into `scripts/path1/build_evidence_pack_v0_2.py`.

---

## Active Tests (Library-Only)

### Syntax Validation

```bash
python -m py_compile scripts/path1/overlays_v0_3.py
```

### Determinism Test Suite

```bash
python tests/test_overlays_v0_3_determinism.py
```

### Pack Rebuild Equivalence (Library-Only)

```bash
python tests/test_pack_rebuild_equivalence.py
```

Note: This test exercises the overlay library only. It does **not** indicate pack-builder integration.

---

## Historical (NOT WIRED)

Any prior steps that referenced CLI flags, environment variables, or automatic pack-builder integration are historical and **not supported** in the current codebase.
