# Registry Seal Contract v0.1

**Version**: 0.1
**Status**: DRAFT
**Date**: 2026-02-05
**Phase**: 2.2 — Registry Layer (Canonical Memory)

---

## 1. Purpose

This contract defines what constitutes a **valid sealed registry artifact set** in ovc-infra. Every registry build MUST produce a sealed artifact set conforming to this contract before it can be referenced by an active pointer.

---

## 2. Manifest Format

### 2.1 `manifest.json`

A JSON array of entries. Each entry describes one file in the sealed artifact set.

```json
[
  {
    "relpath": "<relative path within run folder>",
    "bytes": <integer file size>,
    "sha256": "<hex SHA256 digest of file contents>"
  }
]
```

**Rules:**

- Every file in the run folder (except `MANIFEST.sha256` itself) MUST appear in `manifest.json`.
- `manifest.json` MUST include itself (circular seal — the manifest entry for `manifest.json` is computed after all other entries are finalized, then the file is rewritten with its own hash included).
- `relpath` values MUST use forward slashes (`/`), never backslashes.
- `bytes` MUST be the exact byte count of the file on disk.
- `sha256` MUST be the lowercase hex SHA256 digest of the raw file bytes.

### 2.2 `MANIFEST.sha256`

A plain-text file with one line per file, plus a `ROOT_SHA256` line.

```
<sha256>  <relpath>
<sha256>  <relpath>
...
<sha256>  manifest.json
ROOT_SHA256  <root_hash>
```

**Rules:**

- One line per file: `<sha256>  <relpath>` (two spaces between hash and path).
- Lines are sorted **lexicographically by relpath** (ascending, byte-order).
- `manifest.json` MUST be included as a line.
- `MANIFEST.sha256` itself is NOT included in its own listing.
- The `ROOT_SHA256` line MUST be the last line.

---

## 3. Deterministic Ordering Rules

1. `manifest.json` entries: sorted by `relpath` lexicographically (ascending).
2. `MANIFEST.sha256` lines: sorted by `relpath` lexicographically (ascending), with `ROOT_SHA256` always last.
3. JSON files within the artifact set: keys sorted alphabetically, indented with 2 spaces, UTF-8 encoded, no trailing whitespace.

---

## 4. Hashing Algorithm

- **Algorithm**: SHA-256 (FIPS 180-4)
- **Encoding**: lowercase hexadecimal (64 characters)
- **Input**: raw file bytes (no BOM normalization, no line-ending conversion)

### 4.1 ROOT_SHA256 Computation

```
ROOT_SHA256 = SHA256(
  sorted_lines.join("\n") + "\n"
)
```

Where `sorted_lines` is all `<sha256>  <relpath>` lines (including the `manifest.json` line), sorted lexicographically, joined with a single newline character, followed by a trailing newline.

**Note:** The `ROOT_SHA256` line itself is NOT included in the ROOT_SHA256 computation.

---

## 5. Git State Capture

When git state is an input to the registry build:

| Field | Source | Required |
|-------|--------|----------|
| `git_commit` | `git rev-parse HEAD` | Yes (null if not in a git repo) |
| `working_tree_state` | `git status --porcelain` | Yes (`clean` if empty, `dirty` if any output, `null` if not in git repo) |

Git state is recorded in `run.json` (the run envelope), NOT in the manifest itself.

---

## 6. Valid Sealed Registry Artifact Set

A sealed registry artifact set is **valid** if and only if ALL of the following hold:

1. **`run.json` exists** in the run folder and contains at minimum: `run_id`, `created_utc`.
2. **`manifest.json` exists** and is a valid JSON array of `{relpath, bytes, sha256}` entries.
3. **`MANIFEST.sha256` exists** and contains one line per file in `manifest.json` plus a `ROOT_SHA256` line.
4. **Every file** listed in `manifest.json` exists on disk at the stated `relpath` relative to the run folder.
5. **Every `sha256`** in `manifest.json` matches the actual SHA256 digest of the corresponding file.
6. **Every `bytes`** in `manifest.json` matches the actual file size.
7. **Every line** in `MANIFEST.sha256` matches the corresponding entry in `manifest.json`.
8. **`ROOT_SHA256`** in `MANIFEST.sha256` matches the deterministic recomputation per Section 4.1.
9. **No extra files** exist in the run folder that are not listed in `manifest.json` (except `MANIFEST.sha256`).
10. **Ordering** in `manifest.json` is lexicographic by `relpath`.
11. **Ordering** in `MANIFEST.sha256` is lexicographic by `relpath` with `ROOT_SHA256` last.

### 6.1 Failure Conditions

| Check | Failure |
|-------|---------|
| Missing `run.json` | SEAL_INVALID: no envelope |
| Missing `manifest.json` | SEAL_INVALID: no manifest |
| Missing `MANIFEST.sha256` | SEAL_INVALID: no hash file |
| SHA256 mismatch for any file | SEAL_INVALID: hash mismatch on `<relpath>` |
| Byte count mismatch | SEAL_INVALID: size mismatch on `<relpath>` |
| ROOT_SHA256 mismatch | SEAL_INVALID: root hash mismatch |
| Extra unlisted file | SEAL_INVALID: unlisted file `<relpath>` |
| Ordering violation | SEAL_INVALID: ordering violation |

---

## 7. Relationship to Phase 2.1

This contract formalizes the sealing format already implemented by Phase 2.1 builders (`build_run_registry_v0_1.py`, `build_op_status_table_v0_1.py`, `build_drift_signals_v0_1.py`). It does not modify any existing Phase 2.1 artifact. Phase 2.1 sealed artifacts that conform to this contract are valid Phase 2.2 sealed artifacts.

---

## 8. Registries Without Seals (Gap Declaration)

The following registries do NOT currently produce sealed artifact sets:

| Registry | Gap | Remediation |
|----------|-----|-------------|
| `migration_ledger` | No run envelope, no manifest | Wrap in run envelope at next governance review |
| `expected_versions` | No run envelope, no manifest | Governance artifact; seal on version bump |
| `threshold_packs_file` | No run envelope per pack | Add seal step to OP-B07 workflow |
| `validation_range_results` | No manifest | Add seal step to OP-D04 workflow |
| `fingerprint_index` | No manifest | Add seal step to OP-D08 workflow |
| `derived_validation_reports` | LATEST.txt only, no manifest | Add manifest generation to OP-B08 |

These gaps are **known and bounded**. They do not invalidate the seal contract — they identify registries that must be promoted to sealed status.

---

*End of Registry Seal Contract v0.1*
