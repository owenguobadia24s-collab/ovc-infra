# Tooling

> ⚠️ **NON-CANONICAL** — Tooling supports research workflows only.  
> **NO FEEDBACK INTO CANONICAL** — Tools do not modify Option B/C definitions.

## Purpose

This directory will contain helper utilities for research workflows. Tools are designed to support reproducibility and standardization without being authoritative.

## Planned Utilities

The following utilities are planned for future implementation:

### 1. Sampling Utilities

**Purpose:** Consistent data sampling for studies

- Time-based windowing
- Stratified sampling by instrument
- Train/validation/holdout splits
- Reproducible random sampling with seed control

### 2. Query Hashing

**Purpose:** Generate deterministic hashes of SQL queries for reproducibility

- Normalize whitespace and formatting
- SHA-256 hash of canonical query form
- Hash verification for audit trails

### 3. Visualization Helpers

**Purpose:** Standardized plotting for research outputs

- Score distribution plots
- Feature vs outcome scatter plots
- Time series visualizations
- Correlation matrices

### 4. Manifest Validation

**Purpose:** Validate study manifests against schema

- JSON schema validation
- Required field checks
- Canonical release verification

### 5. Study Scaffolding

**Purpose:** CLI to create new studies from template

```powershell
python -m research.tooling.scaffold study_20260120_my_analysis
```

## Implementation Status

| Utility | Status | Notes |
|---------|--------|-------|
| Sampling | Not started | — |
| Query hashing | Not started | — |
| Visualization | Not started | — |
| Manifest validation | Not started | — |
| Study scaffolding | Not started | — |

## Development Guidelines

When implementing tools:

1. **Read-only to canonical** — Tools must not modify canonical data
2. **Deterministic** — Same inputs must produce same outputs
3. **Documented** — Each tool needs usage docs and examples
4. **Tested** — Unit tests for all utilities
5. **Versioned** — Tools follow semantic versioning

## Directory Structure (Future)

```
tooling/
├── README.md           # This file
├── __init__.py
├── sampling.py         # Sampling utilities
├── hashing.py          # Query hashing
├── plotting.py         # Visualization helpers
├── validation.py       # Manifest validation
├── scaffold.py         # Study scaffolding CLI
└── tests/
    ├── test_sampling.py
    ├── test_hashing.py
    └── ...
```

## Usage (Future)

```python
from research.tooling import sampling, hashing

# Sample data
sample = sampling.time_window(
    start='2025-01-01',
    end='2026-01-01',
    instruments=['GBPUSD']
)

# Hash a query
query_hash = hashing.sha256_query("""
    SELECT * FROM derived.ovc_block_features_v0_1
    WHERE ts >= '2025-01-01'
""")
```
