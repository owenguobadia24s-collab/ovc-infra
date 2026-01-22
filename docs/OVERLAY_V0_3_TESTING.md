# Evidence Pack v0.3 Overlays - Testing & Validation Guide

## Quick Start

### Test 1: Syntax Validation ✅

```bash
# Verify Python syntax
python -m py_compile scripts/path1/overlays_v0_3.py
python -m py_compile scripts/path1/build_evidence_pack_v0_2.py
```

**Expected**: No errors

### Test 2: Build Pack Without Overlays

```bash
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_overlay_test_baseline \
  --sym GBPUSD \
  --date-from 2022-12-12 \
  --date-to 2022-12-14
```

**Verify**:
```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_baseline/outputs/evidence_pack_v0_2"

# Should NOT have overlays_v0_3 directory
test ! -d $PACK_DIR/overlays_v0_3 && echo "✅ No overlays dir" || echo "❌ Overlays dir exists"

# meta.json should show overlays disabled
cat $PACK_DIR/meta.json | jq '.overlays_v0_3.enabled' | grep false && echo "✅ Overlays disabled in meta" || echo "❌ Overlays enabled in meta"
```

### Test 3: Build Pack With Overlays (CLI Flag)

```bash
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_overlay_test_enabled \
  --sym GBPUSD \
  --date-from 2022-12-12 \
  --date-to 2022-12-14 \
  --overlays-v0-3
```

**Verify**:
```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Should have overlays_v0_3 directory
test -d $PACK_DIR/overlays_v0_3 && echo "✅ Overlays dir exists" || echo "❌ No overlays dir"

# Check v0.3-A outputs (micro/2h)
test -d $PACK_DIR/overlays_v0_3/micro/2h && echo "✅ v0.3-A dir exists" || echo "❌ No v0.3-A dir"
ls $PACK_DIR/overlays_v0_3/micro/2h/*.json | head -3

# Check v0.3-B output (events/displacement_fvg.jsonl)
test -f $PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl && echo "✅ v0.3-B file exists" || echo "❌ No v0.3-B file"
wc -l $PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl

# Check v0.3-C outputs (micro/liquidity_gradient)
test -d $PACK_DIR/overlays_v0_3/micro/liquidity_gradient && echo "✅ v0.3-C dir exists" || echo "❌ No v0.3-C dir"
ls $PACK_DIR/overlays_v0_3/micro/liquidity_gradient/*.json | head -3

# meta.json should show overlays enabled
cat $PACK_DIR/meta.json | jq '.overlays_v0_3.enabled' | grep true && echo "✅ Overlays enabled in meta" || echo "❌ Overlays disabled in meta"

# Check counts
cat $PACK_DIR/meta.json | jq '.overlays_v0_3.counts'
```

### Test 4: Build Pack With Overlays (Environment Variable)

```bash
export EVIDENCE_OVERLAYS_V0_3=1
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_overlay_test_env \
  --sym GBPUSD \
  --date-from 2022-12-12 \
  --date-to 2022-12-14
unset EVIDENCE_OVERLAYS_V0_3
```

**Verify**:
```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_env/outputs/evidence_pack_v0_2"

# Should have overlays_v0_3 directory
test -d $PACK_DIR/overlays_v0_3 && echo "✅ Overlays dir exists (env var)" || echo "❌ No overlays dir (env var)"
```

### Test 5: Determinism Check

Build same pack twice and verify outputs are identical:

```bash
# First build
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_determinism_1 \
  --sym GBPUSD \
  --date-from 2022-12-12 \
  --date-to 2022-12-14 \
  --overlays-v0-3

# Second build
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_determinism_2 \
  --sym GBPUSD \
  --date-from 2022-12-12 \
  --date-to 2022-12-14 \
  --overlays-v0-3

# Compare overlays (should be identical)
diff -r reports/path1/evidence/runs/p1_determinism_1/outputs/evidence_pack_v0_2/overlays_v0_3 \
        reports/path1/evidence/runs/p1_determinism_2/outputs/evidence_pack_v0_2/overlays_v0_3

echo $?  # Should be 0 (no differences)
```

### Test 6: JSON Validity

```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Validate all v0.3-A JSON files
for file in $PACK_DIR/overlays_v0_3/micro/2h/*.json; do
  jq empty "$file" 2>/dev/null && echo "✅ Valid: $file" || echo "❌ Invalid: $file"
done

# Validate all v0.3-C JSON files
for file in $PACK_DIR/overlays_v0_3/micro/liquidity_gradient/*.json; do
  jq empty "$file" 2>/dev/null && echo "✅ Valid: $file" || echo "❌ Invalid: $file"
done

# Validate v0.3-B JSONL (each line must be valid JSON)
while IFS= read -r line; do
  echo "$line" | jq empty 2>/dev/null || echo "❌ Invalid JSONL line"
done < "$PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl"
```

### Test 7: Manifest Integration

```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Check if overlay files are in manifest.json
cat $PACK_DIR/manifest.json | jq '.files[] | select(.relative_path | startswith("overlays_v0_3")) | .relative_path' | head -10

# Count overlay files in manifest
OVERLAY_FILE_COUNT=$(cat $PACK_DIR/manifest.json | jq '[.files[] | select(.relative_path | startswith("overlays_v0_3"))] | length')
echo "Overlay files in manifest: $OVERLAY_FILE_COUNT"
```

### Test 8: Schema Validation

```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Check v0.3-A schema (pick first file)
MICRO_FILE=$(ls $PACK_DIR/overlays_v0_3/micro/2h/*.json | head -1)
echo "Checking v0.3-A schema: $MICRO_FILE"
cat "$MICRO_FILE" | jq 'has("block_id") and has("wick_sequence") and has("sweeps") and has("raid_reclaims")' | grep true && echo "✅ v0.3-A schema valid" || echo "❌ v0.3-A schema invalid"

# Check v0.3-C schema (pick first file)
GRADIENT_FILE=$(ls $PACK_DIR/overlays_v0_3/micro/liquidity_gradient/*.json | head -1)
echo "Checking v0.3-C schema: $GRADIENT_FILE"
cat "$GRADIENT_FILE" | jq 'has("block_id") and has("level_histogram") and has("compression_zones") and has("breakout_failures")' | grep true && echo "✅ v0.3-C schema valid" || echo "❌ v0.3-C schema invalid"

# Check v0.3-B schema (pick first event)
head -1 $PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl | jq 'has("event_type")' | grep true && echo "✅ v0.3-B schema valid" || echo "❌ v0.3-B schema invalid"
```

### Test 9: Empty Pack Edge Case

```bash
# Build pack for date range with no data
python scripts/path1/build_evidence_pack_v0_2.py \
  --run-id p1_overlay_test_empty \
  --sym GBPUSD \
  --date-from 1999-01-01 \
  --date-to 1999-01-02 \
  --overlays-v0-3

PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_empty/outputs/evidence_pack_v0_2"

# Empty pack should still have overlay metadata (but no overlay files)
cat $PACK_DIR/meta.json | jq '.overlays_v0_3.enabled' | grep false && echo "✅ Empty pack: overlays disabled" || echo "❌ Empty pack: overlays enabled"

# Should NOT have overlays directory for empty pack
test ! -d $PACK_DIR/overlays_v0_3 && echo "✅ Empty pack: no overlays dir" || echo "❌ Empty pack: has overlays dir"
```

### Test 10: Output Ordering

Verify deterministic ordering of events:

```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Check if wick_sequence is sorted by bar_start_ms
MICRO_FILE=$(ls $PACK_DIR/overlays_v0_3/micro/2h/*.json | head -1)
cat "$MICRO_FILE" | jq '.wick_sequence | [.[].bar_start_ms] | . == (. | sort)' | grep true && echo "✅ Wick sequence sorted" || echo "❌ Wick sequence not sorted"

# Check if level_histogram is sorted by level
GRADIENT_FILE=$(ls $PACK_DIR/overlays_v0_3/micro/liquidity_gradient/*.json | head -1)
cat "$GRADIENT_FILE" | jq '.level_histogram | [.[].level] | . == (. | sort)' | grep true && echo "✅ Level histogram sorted" || echo "❌ Level histogram not sorted"

# Check if JSONL events are sorted by timestamp
# Extract all timestamps and verify sorting
cat $PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl | jq -r '.start_bar_ms // .bar_start_ms // .middle_bar_ms' > /tmp/event_times.txt
sort -n /tmp/event_times.txt > /tmp/event_times_sorted.txt
diff /tmp/event_times.txt /tmp/event_times_sorted.txt && echo "✅ Events sorted by timestamp" || echo "❌ Events not sorted"
rm /tmp/event_times.txt /tmp/event_times_sorted.txt
```

## Comprehensive Test Checklist

- [ ] Syntax validation (py_compile)
- [ ] Pack builds without overlays (baseline)
- [ ] Pack builds with overlays (--overlays-v0-3 flag)
- [ ] Pack builds with overlays (EVIDENCE_OVERLAYS_V0_3=1 env var)
- [ ] Determinism verified (two identical builds produce identical overlays)
- [ ] All JSON files are valid
- [ ] All JSONL lines are valid JSON
- [ ] Overlay files appear in manifest.json
- [ ] v0.3-A schema validated (block_id, wick_sequence, sweeps, raid_reclaims)
- [ ] v0.3-B schema validated (event_type, timestamps)
- [ ] v0.3-C schema validated (block_id, level_histogram, compression_zones, breakout_failures)
- [ ] Empty pack handled correctly (no overlays generated, metadata shows disabled)
- [ ] All sequences and events are properly sorted
- [ ] meta.json includes overlays_v0_3 metadata
- [ ] Counts in meta.json match actual output files

## Success Criteria

All tests pass with ✅ markers and no ❌ markers.

## Troubleshooting

### Issue: Import error for overlays_v0_3

**Solution**: Ensure `scripts/path1/overlays_v0_3.py` exists and has no syntax errors.

```bash
python -m py_compile scripts/path1/overlays_v0_3.py
```

### Issue: No overlay files generated despite --overlays-v0-3 flag

**Solution**: Check console output for errors. Verify database connection and M15 data availability.

### Issue: JSON parsing errors in overlay files

**Solution**: Check for edge cases in candle data (empty lists, None values). Review overlay generation logic for proper null handling.

### Issue: Determinism test fails (diff shows differences)

**Solution**: Check for:
- Unsorted sequences (should sort by bar_start_ms)
- Non-deterministic algorithms (should use stable sorting)
- Timestamp fields without stable encoding
- JSON keys not using sort_keys=True

### Issue: Overlay counts in meta.json don't match actual files

**Solution**: Verify write_overlay_outputs() return value. Count files manually and compare.

```bash
PACK_DIR="reports/path1/evidence/runs/p1_overlay_test_enabled/outputs/evidence_pack_v0_2"

# Count v0.3-A files
ls $PACK_DIR/overlays_v0_3/micro/2h/*.json | wc -l

# Count v0.3-B events
wc -l $PACK_DIR/overlays_v0_3/events/displacement_fvg.jsonl

# Count v0.3-C files
ls $PACK_DIR/overlays_v0_3/micro/liquidity_gradient/*.json | wc -l

# Compare with meta.json counts
cat $PACK_DIR/meta.json | jq '.overlays_v0_3.counts'
```

---

**Testing Date**: Run tests after any changes to overlay logic or pack builder
**Test Environment**: Requires DATABASE_URL with M15 data for GBPUSD 2022-12-12 to 2022-12-14
