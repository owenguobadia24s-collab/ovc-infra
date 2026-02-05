# Phase 3 Control Panel

**Version**: 0.1
**Phase**: 3 — Control Visibility
**Authority**: Read-only. No execution authority.

---

## Purpose

**"Sight without influence."**

The Phase 3 Control Panel provides a read-only view of OVC system state. It renders data from sealed canonical artifacts without any ability to modify, trigger, or reseal anything. The viewer can be deleted with zero loss of truth — all displayed data traces to canonical sources in the registry layer.

---

## Architecture

This is a **Static Viewer** implementation per the Phase 3 Architecture Validation Report:

- Reads from a read-only mounted directory containing all sealed registry artifacts
- Renders views from pre-built canonical sources
- Has no backend capable of write operations
- **No write credentials exist**

---

## Views

The control panel provides exactly six views:

| View | Path | Description |
|------|------|-------------|
| **Runs View** | `/runs` | Timeline of all runs indexed in run_registry. Links to artifact drill-down. |
| **Failures View** | `/failures` | Aggregated failures from op_status_table. No inferred causes. |
| **Artifact Drill-Down** | `/artifacts/[run_id]` | View run.json, manifest.json, MANIFEST.sha256 for a specific run. |
| **Diff View** | `/diff` | Compare two runs via GET params. Shows manifest diffs + delta log (explanatory only). |
| **System Health View** | `/health` | Compute and display H0/H1/H2/H3/H9 per Health Contracts v0.1. |
| **Governance Visibility View** | `/governance` | Active versions, enforcement levels C0-C5, known governance gaps. |

---

## Read-Only Enforcement

### No Write Credentials Exist

The Phase 3 control panel operates with:

- **No `GITHUB_TOKEN`** with push/dispatch scope
- **No database DSN** with INSERT/UPDATE/DELETE grants
- **No filesystem paths** opened in write mode
- **No API credentials** for any system that can mutate state

### Non-Authority Banner

Every page displays:

> "Read-only Control Panel — no actions, no writes, no triggers."

### Allowed Interactions

| Interaction | Allowed |
|-------------|---------|
| Navigation | Yes |
| Filtering | Yes |
| Sorting | Yes |
| Search | Yes |
| Copy to clipboard | Yes |
| Explanation/expand | Yes |

### Forbidden Interactions

| Interaction | Status |
|-------------|--------|
| Trigger/Run | **FORBIDDEN** |
| Fix/Approve/Reject | **FORBIDDEN** |
| Update/Reseal/Promote | **FORBIDDEN** |
| Inline editing | **FORBIDDEN** |
| Form submissions | **FORBIDDEN** |

---

## Source Tracing

Every displayed datum traces to a canonical source. Each page/table shows a source trace including:

```json
{
  "registry_id": "...",
  "pointer_file": "...",
  "active_run_id": "...",
  "artifact_path": "...",
  "sealed": true|false,
  "notes": "..."
}
```

---

## Health State Computation

The `/health` view computes health state **exactly** per Health Contracts v0.1:

1. Check H9 (UNKNOWN) conditions first
2. Check H3 (RECOVERY_REQUIRED) conditions
3. Check H2 (DEGRADED_BLOCKING) conditions
4. Check H1 (DEGRADED_NON_BLOCKING) conditions
5. If no degradation found, state is H0 (HEALTHY)

**No deviations. No scoring. No ML. No custom heuristics.**

---

## Diff Semantics

The `/diff` view provides two types of comparisons:

### Manifest Diffs
- Structural comparison of `{relpath, bytes, sha256}` entries
- Shows added, removed, and changed files

### Delta Log (Explanatory Only)

> **"Delta log is explanatory only; it does not drive control."**

The delta log explains what changed between snapshots but does NOT:
- Drive control
- Trigger actions
- Update pointers

---

## Running the Audits

Three audits enforce Phase 3 invariants:

### 1. Read-Only Audit

```bash
python audits/phase3_read_only_audit.py
```

Fails if it finds:
- File write operations (`open(..., "w")`, `writeFile`, etc.)
- Subprocess execution (`subprocess.run`, `os.system`, etc.)
- Git write commands (`git push`, `git commit`, etc.)
- Sealing module imports
- Database write operations
- Writes to canon paths (`.codex/`, `reports/`, etc.)

### 2. UI Action Audit

```bash
python audits/phase3_ui_action_audit.py
```

Fails if it finds:
- Action buttons (Run, Trigger, Approve, Reject, Fix, Update, Reseal, Promote)
- Forms posting to mutation endpoints
- Non-navigation onClick handlers
- Hidden action controls

### 3. Network Mutation Audit

```bash
python audits/phase3_no_network_mutation_audit.py
```

Fails if it finds:
- HTTP methods other than GET (POST, PUT, PATCH, DELETE)
- WebSocket connections
- GitHub API clients
- Workflow dispatch logic
- AI/Agent integrations

### Audit Policy

**FAIL-CLOSED**: If any audit cannot determine pattern absence, it MUST fail.

Exit codes:
- `0` = PASS
- `1` = FAIL (violations detected)
- `2` = ERROR (audit could not complete — treated as FAIL)

---

## Runtime Harness

The control panel includes a minimal runtime harness for local development and closure validation testing.

### Prerequisites

```bash
# From tools/phase3_control_panel/
npm install
```

### Running the Dev Server

```powershell
# Set the repo root (required)
$env:PHASE3_REPO_ROOT = "C:\path\to\ovc-infra"

# Start the server (port 3311)
npm run dev:server
```

Or on Unix/macOS:

```bash
PHASE3_REPO_ROOT=/path/to/ovc-infra npm run dev:server
```

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/runs` | All runs from run_registry |
| `/api/failures` | Failure aggregations |
| `/api/artifacts/:runId` | Envelope + manifest for a run |
| `/api/diff` | Diff between runs (query: `left`, `right`) |
| `/api/health` | Computed health state |
| `/api/governance` | Governance visibility data |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PHASE3_REPO_ROOT` | Yes | Absolute path to ovc-infra repo root |
| `PORT` | No | Server port (default: 3311) |

### Running the Vite UI (Development)

```bash
# Start Vite dev server (port 5173)
npm run dev
```

The Vite UI proxies API requests to the backend server at port 3311.

### Building for Production

```bash
# Typecheck + build client
npm run build

# Build server
npm run build:server

# Run production server
npm run start
```

### Read-Only Enforcement

The runtime harness enforces read-only semantics:

1. **Server denies all non-GET requests** — Returns 405 Method Not Allowed
2. **Sources open files with `flag: 'r'` only** — No write modes
3. **No mutation endpoints exist** — Only GET handlers registered

---

## Pointing to a Canon Snapshot

To use the control panel with a canon snapshot directory:

```typescript
import { initializeSources } from './src/lib/sources';

// Initialize with the path to your repo root (read-only)
initializeSources('/path/to/ovc-infra');

// All subsequent reads are from this root
```

The sources module reads from:
- `.codex/RUNS/` — Run folders with envelopes and manifests
- `docs/phase_2_2/ACTIVE_REGISTRY_POINTERS_v0_1.json` — Active pointers
- `docs/phase_2_2/REGISTRY_CATALOG_v0_1.json` — Registry catalog
- `docs/governance/` — Governance documents

All reads use `flag: 'r'` only. No write modes.

---

## File Structure

```
tools/phase3_control_panel/
├── README.md                           # This file
├── config/
│   ├── phase3_sources.json             # Canon path configuration
│   └── phase3_forbidden_patterns.json  # Audit pattern definitions
├── src/
│   ├── lib/
│   │   ├── models.ts                   # Type definitions
│   │   ├── trace.ts                    # Source trace helpers
│   │   ├── sources.ts                  # Read-only data loaders
│   │   ├── health_rules.ts             # Health Contracts v0.1 implementation
│   │   └── diff_rules.ts               # Manifest diff + delta log rules
│   ├── ui/
│   │   ├── Layout.tsx                  # Page layout with non-authority banner
│   │   ├── SourceBadge.tsx             # Source trace display
│   │   ├── Table.tsx                   # Read-only data table
│   │   └── ErrorPanel.tsx              # Error display (no fix buttons)
│   └── app/
│       ├── runs/page.tsx               # Runs timeline view
│       ├── failures/page.tsx           # Failure aggregations
│       ├── artifacts/[run_id]/page.tsx # Artifact drill-down
│       ├── diff/page.tsx               # Run comparison
│       ├── health/page.tsx             # System health (H0-H9)
│       └── governance/page.tsx         # Governance visibility
└── audits/
    ├── phase3_read_only_audit.py       # File/subprocess/git write checks
    ├── phase3_ui_action_audit.py       # Action button/form checks
    └── phase3_no_network_mutation_audit.py  # HTTP/WebSocket/GitHub checks
```

---

## Invariants

Per Phase 3 Architecture Validation Report:

| ID | Invariant |
|----|-----------|
| P3-INV-01 | No Phase 3 component can write to registries |
| P3-INV-02 | No Phase 3 component can mutate artifacts |
| P3-INV-03 | No Phase 3 component can update active pointers |
| P3-INV-04 | No Phase 3 component can trigger executions |
| P3-INV-05 | No Phase 3 component can reseal anything |
| P3-INV-06 | All Phase 3 outputs are derived from sealed artifacts only |
| P3-INV-07 | All Phase 3 outputs are reproducible |
| P3-INV-08 | All Phase 3 outputs are discardable without loss of truth |
| P3-INV-09 | Phase 3 introduces zero new authority surfaces |

**Violation of any invariant = Phase 3 failure.**

---

## Contracts

Phase 3 schema contracts document the observed, authoritative artifact structures. These are frozen, versioned specifications derived from evidence extraction.

| Contract | Version | Description |
|----------|---------|-------------|
| [PHASE3_CANON_SCHEMA_CONTRACT_v0.1.md](docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.md) | 0.1 | Human-readable schema contract for all Phase 3 artifacts |
| [PHASE3_CANON_SCHEMA_CONTRACT_v0.1.json](docs/contracts/PHASE3_CANON_SCHEMA_CONTRACT_v0.1.json) | 0.1 | Machine-readable JSON schema contract |

### Contract Principles

1. **Derived from artifacts, not artifacts bent to contract** — Schemas describe what exists, not what we wish existed.
2. **Read-only documentation** — Contracts do not grant authority or modify runtime behavior.
3. **Unknown keys allowed** — Validators pass objects with unrecognized keys.
4. **Version bumps required** — Any schema change (new required field, type change, nullability change) requires a contract version bump.

### Artifacts in Scope (v0.1)

| Artifact | File Pattern |
|----------|-------------|
| Run Registry | `RUN_REGISTRY_v0_1.jsonl` |
| Operation Status Table | `OPERATION_STATUS_TABLE_v0_1.json` |
| Registry Delta Log | `REGISTRY_DELTA_LOG_v0_1.jsonl` |

---

## Success Condition

This implementation is successful only if an auditor can verify:

1. The viewer can be deleted with zero loss of truth
2. Every displayed datum traces to canon (registry/artifact/run_id)
3. Any attempt to add write authority causes audit failure
4. UI contains no decision surfaces

---

*End of Phase 3 Control Panel README*
