# Registry Layer Runbook v0.1

**Version**: 0.1
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2 — Registry Layer (Canonical Memory)

---

## 1. Purpose

This runbook defines the **only allowed workflow** for building, sealing, validating, and activating registry artifacts. No shortcuts. No implied state.

---

## 2. Workflow Steps (Strict Order)

### Step 1: Build Registry (Append-Only)

**Action:** Execute the builder script for the target registry.

| Registry | Builder | Command |
|----------|---------|---------|
| `run_registry` | `tools/run_registry/build_run_registry_v0_1.py` | `python tools/run_registry/build_run_registry_v0_1.py` |
| `op_status_table` | `tools/run_registry/build_op_status_table_v0_1.py` | `python tools/run_registry/build_op_status_table_v0_1.py` |
| `drift_signals` | `tools/run_registry/build_drift_signals_v0_1.py` | `python tools/run_registry/build_drift_signals_v0_1.py` |
| `system_health_report` | `tools/run_registry/render_system_health_v0_1.py` | `python tools/run_registry/render_system_health_v0_1.py` |

**Constraints:**

- The builder MUST create a **new run folder** under `.codex/RUNS/<run_id>/`.
- The builder MUST NOT modify any existing run folder.
- The builder MUST be deterministic: same filesystem state = same output (excluding timestamps).
- The builder MUST use only stdlib (no third-party dependencies).
- The builder MUST NOT make network or database calls.

**Output:** A new run folder containing the registry artifact + `run.json`.

### Step 2: Seal Artifacts

**Action:** The builder script produces sealing artifacts as part of the build.

Each build MUST produce:

1. `run.json` — run envelope with `run_id`, `created_utc`, `git_commit`, `working_tree_state`, `outputs[]`.
2. `manifest.json` — array of `{relpath, bytes, sha256}` for every file in the run folder.
3. `MANIFEST.sha256` — text file with per-file hashes + `ROOT_SHA256`.

**Seal validity** is defined by `REGISTRY_SEAL_CONTRACT_v0_1.md`.

### Step 3: Validate Schema + Hashes

**Action:** Run validation against the sealed artifact set.

```
python docs/phase_2_2/validators/validate_registry_seals_v0_1.py   <run_folder>
python docs/phase_2_2/validators/validate_registry_schema_v0_1.py  <run_folder>
```

**Checks:**

1. All SHA256 hashes match actual file contents.
2. ROOT_SHA256 is correctly computed.
3. All required files are present.
4. No extra unlisted files exist.
5. Registry data conforms to the declared schema.
6. `run.json` contains all required keys.

**Outcome:** PASS or FAIL with explicit failure reasons.

### Step 4: Select Active via Pointer Mutation Only

**Action:** Update `ACTIVE_REGISTRY_POINTERS_v0_1.json` to point to the newly validated artifact set.

**Rules:**

- The pointer file is the **ONLY** mutable artifact in the registry layer.
- The pointer MUST reference a **sealed and validated** artifact set.
- The pointer MUST include:
  - `registry_id`
  - `active_ref.run_id`
  - `active_ref.run_root`
  - `active_ref.relpath`
  - `active_ref.manifest_sha256` (ROOT_SHA256 from MANIFEST.sha256)
  - `active_ref_known`: `true`
  - `active_asof_utc`: current UTC timestamp

**This is the only step that changes what is considered "active."**

### Step 5: Optional Render (Read-Only)

**Action:** Optionally produce human-readable output from the active registry.

```
python tools/run_registry/render_system_health_v0_1.py
```

**Constraints:**

- Render is read-only — it reads from the active registry and produces presentation output.
- Render output is itself sealed in a new run folder.
- Render MUST NOT modify the source registry.

---

## 3. Dependency Order

When building the full registry stack, execute in this order:

```
1. build_run_registry_v0_1.py          (no dependencies)
2. build_op_status_table_v0_1.py       (depends on: run_registry)
3. build_drift_signals_v0_1.py         (depends on: op_status_table, run_registry, expected_versions)
4. render_system_health_v0_1.py        (depends on: op_status_table, drift_signals, run_registry)
```

Each step MUST complete and be sealed before the next step begins.

---

## 4. Prohibited Actions

| Action | Why Prohibited |
|--------|---------------|
| Edit a file inside an existing run folder | Violates append-only / immutability |
| Delete a run folder | Destroys evidence history |
| Set a pointer to an unsealed artifact | Violates seal contract |
| Set a pointer without validation | May reference corrupt data |
| Imply "active" via file naming or recency | Only explicit pointer mutation is valid |
| Run a builder with network/DB calls | Breaks determinism constraint |
| Modify Phase 2.1 artifacts | Violates Phase 2.2 non-regression constraint |

---

## 5. Error Recovery

| Scenario | Action |
|----------|--------|
| Build fails | Do not create partial run folder. Retry from scratch. |
| Validation fails on a sealed artifact | Do NOT fix in place. Rebuild from scratch. Old run folder is evidence of the failure. |
| Pointer update fails | Pointer file remains at previous state. Retry pointer update. |
| Schema drift detected | Investigate via drift_signals. Do NOT auto-remediate. |

---

## 6. Registries Without Builders

The following registries do not have automated builders:

| Registry | Current Update Mechanism | Phase 2.2 Status |
|----------|-------------------------|-------------------|
| `migration_ledger` | Manual edit of `schema/applied_migrations.json` | Gap: needs run envelope wrapper |
| `expected_versions` | Manual governance edit | Gap: needs version-bump seal |
| `threshold_packs_file` | Manual file creation under `configs/threshold_packs/` | Gap: needs seal step |
| `validation_range_results` | Produced by OP-D04 range runner | Gap: needs manifest |
| `fingerprint_index` | Produced by OP-D08 fingerprint builder | Gap: needs manifest |
| `derived_validation_reports` | Produced by OP-B08 | Gap: needs manifest, pointer upgrade |
| `evidence_pack_registry` | Produced by OP-D01 | Partially sealed (pack_sha256.txt exists) |

---

*End of Registry Layer Runbook v0.1*
