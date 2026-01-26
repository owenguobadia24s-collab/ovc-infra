# L3 Entry Checklist (v0.1)

> **Purpose**: This checklist MUST be satisfied before any new L3 tag is merged to main.  
> **Authority**: No exceptions without explicit approval and documented rationale.

---

## Pre-Submission Requirements

Before opening a PR for a new L3 tag, verify ALL items are complete:

### 1. Design & Contract Compliance

- [ ] **L3 Semantic Contract reviewed**: Read `docs/l3_semantic_contract_v0_1.md` in full
- [ ] **Tag is semantic**: Classification represents meaningful market state (not a raw metric)
- [ ] **Inputs are L1/L2 only**: No direct B-layer OHLC access in classification logic
- [ ] **Output is discrete**: Finite set of categorical values (e.g., TREND/NON_TREND)
- [ ] **No prohibited behaviors**: No TV dependency, inline heuristics, mutable thresholds, external calls

### 2. Threshold Pack

- [ ] **Config file exists**: `configs/threshold_packs/l3_<tag_name>_v1.json`
- [ ] **Config uses integers**: All thresholds in basis points or counts (no floats)
- [ ] **Pack created in registry**: `threshold_registry_cli create` executed successfully
- [ ] **Pack activated**: `threshold_registry_cli activate` executed successfully
- [ ] **Pack ID matches tag**: e.g., `l3_regime_trend` pack for `l3_regime_trend` tag

### 3. SQL Migration

- [ ] **Migration file exists**: `sql/XX_c3_<tag_name>_v0_1.sql`
- [ ] **Table in derived schema**: `derived.ovc_l3_<tag_name>_v0_1`
- [ ] **Primary key defined**: `PRIMARY KEY (symbol, ts)`
- [ ] **Provenance columns present**: `threshold_pack_id`, `threshold_pack_version`, `threshold_pack_hash`
- [ ] **Provenance columns NOT NULL**: All three have `NOT NULL` constraint
- [ ] **Hash format constraint**: `CHECK (threshold_pack_hash ~ '^[a-f0-9]{64}$')`
- [ ] **Classification constraint**: `CHECK (l3_<tag> IN ('VALUE1', 'VALUE2', ...))`
- [ ] **Required indexes created**: block_id (unique), threshold_pack, run_id
- [ ] **Migration tested locally**: `psql $NEON_DSN -f sql/XX_c3_<tag_name>_v0_1.sql` succeeds

### 4. Compute Script

- [ ] **Script exists**: `src/derived/compute_l3_<tag_name>_v0_1.py`
- [ ] **Reference implementation followed**: Pattern matches `compute_l3_regime_trend_v0_1.py`
- [ ] **Threshold resolution at start**: Pack resolved once, not per-block
- [ ] **Provenance columns populated**: All three from resolved pack, never hardcoded
- [ ] **L1/L2 data fetch only**: No B-layer OHLC queries in classification logic
- [ ] **Upsert semantics**: `ON CONFLICT (symbol, ts) DO UPDATE`
- [ ] **CLI arguments present**: `--symbol`, `--threshold-pack`, `--scope`, `--dry-run`
- [ ] **Script imports cleanly**: `python -c "from src.derived.compute_l3_<tag>_v0_1 import *"`
- [ ] **--help works**: `python src/derived/compute_l3_<tag>_v0_1.py --help`

### 5. Tests

- [ ] **Test file exists**: `tests/test_l3_<tag_name>.py`
- [ ] **Classification logic tests**: Boundary cases for each condition
- [ ] **Determinism test**: Same inputs → same output (100 iterations)
- [ ] **Threshold pack integrity test**: Config hash is SHA256, key order doesn't matter
- [ ] **Provenance validation tests**: Hash format, valid values
- [ ] **All tests pass**: `python -m pytest tests/test_l3_<tag_name>.py -v`

### 6. Validator Coverage

- [ ] **C3_TABLES updated**: Entry added to `C3_TABLES` dict in `validate_derived_range_v0_1.py`
- [ ] **Valid values specified**: `valid_values` list matches SQL CHECK constraint
- [ ] **Provenance columns listed**: `provenance_columns` includes all three threshold columns
- [ ] **Validation runs without error**: `--validate-c3 --c3-classifiers l3_<tag_name>`

### 7. Documentation

- [ ] **Runbook section added**: Entry in `docs/option_threshold_registry_runbook.md`
- [ ] **Classification logic documented**: What conditions produce each output value
- [ ] **Threshold parameters documented**: Table with parameter names, types, descriptions

### 8. End-to-End Verification

- [ ] **Migration applied**: Table exists in Neon staging
- [ ] **Pack created and active**: Verified via `threshold_registry_cli show`
- [ ] **Compute executed**: At least one symbol/date range processed
- [ ] **Validation passed**: `--validate-c3` returns PASS status
- [ ] **Artifacts generated**: JSON and MD reports in `artifacts/derived_validation/`

---

## PR Requirements

### Commit Message Format

```
feat(c3): add l3_<tag_name> classifier

- Add SQL migration for derived.ovc_l3_<tag_name>_v0_1
- Add compute script with threshold registry integration
- Add threshold pack config
- Add tests (N passing)
- Extend validator for L3 coverage
```

### PR Description Must Include

1. **Tag purpose**: What market state does this classify?
2. **Classification logic**: Pseudocode or decision tree
3. **Threshold pack config**: Full JSON with explanations
4. **Test results**: pytest output showing all pass
5. **Validation results**: Summary from `--validate-c3`
6. **Checklist completion**: Link to this checklist with all items checked

### Review Requirements

- [ ] **At least one code review** from team member
- [ ] **No merge conflicts** with main
- [ ] **CI passes** (if configured)

---

## Post-Merge

After merge to main:

- [ ] **Verify production migration**: Table exists in prod Neon
- [ ] **Verify pack in prod registry**: `threshold_registry_cli show` in prod
- [ ] **Run initial compute**: Process historical data for all symbols
- [ ] **Run validation**: Full date range validation with `--validate-c3`
- [ ] **Monitor for issues**: Check logs for first 24 hours

---

## Quick Reference Commands

```powershell
# 1. Create threshold pack
python -m src.config.threshold_registry_cli create `
  --pack-id l3_<tag_name> `
  --version 1 `
  --scope GLOBAL `
  --config-file configs/threshold_packs/l3_<tag_name>_v1.json

# 2. Activate threshold pack
python -m src.config.threshold_registry_cli activate `
  --pack-id l3_<tag_name> `
  --version 1 `
  --scope GLOBAL

# 3. Apply migration
psql $env:NEON_DSN -f sql/XX_c3_<tag_name>_v0_1.sql

# 4. Run compute
python src/derived/compute_l3_<tag_name>_v0_1.py `
  --symbol GBPUSD `
  --threshold-pack l3_<tag_name> `
  --scope GLOBAL

# 5. Run tests
python -m pytest tests/test_l3_<tag_name>.py -v

# 6. Run validation
python src/validate/validate_derived_range_v0_1.py `
  --symbol GBPUSD `
  --start-date 2026-01-13 `
  --end-date 2026-01-17 `
  --validate-c3 `
  --c3-classifiers l3_<tag_name>
```

---

## Why This Checklist Exists

L3 tags are **semantic infrastructure**. A broken L3 tag can:

1. **Corrupt downstream analysis**: Evaluations built on faulty classifications are meaningless
2. **Break replay certification**: Non-deterministic tags cannot be audited
3. **Create silent failures**: Missing provenance makes debugging impossible
4. **Undermine trust**: If one tag is unreliable, all tags are suspect

This checklist ensures every L3 tag meets the same quality bar as `l3_regime_trend`, the reference implementation.

**No shortcuts. No exceptions.**
