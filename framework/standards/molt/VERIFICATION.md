# Molt Verification

**Layer**: Specifics (NOT-ME) - how to verify molt success

---

## Verification Command

```bash
python -m truth_forge.molt verify --source {source_dir}
```

---

## Verification Checklist

### 1. Source Shrinkage

| Check | Pass Criteria |
|-------|---------------|
| Stub line count | Each file ≤ 20 lines |
| Total source size | < 10% of original |
| No original content | Stubs only contain redirects |

```bash
# Check line counts
wc -l {source}/*.md

# Compare before/after
# Before: 5000 lines total
# After: 200 lines total (stubs)
```

### 2. Archive Integrity

| Check | Pass Criteria |
|-------|---------------|
| Files present | All originals in archive |
| Structure preserved | Relative paths maintained |
| Content unchanged | MD5 matches original |

```bash
# Verify archive exists
ls -la {archive}/molt_YYYY_MM_DD/

# Count files
find {archive}/molt_YYYY_MM_DD -name "*.md" | wc -l
```

### 3. Stub Validity

| Check | Pass Criteria |
|-------|---------------|
| MOVED marker | Present |
| New Location link | Valid, resolvable |
| Archive link | Valid, resolvable |
| Molted On date | Present, correct format |

```bash
# Check stub markers
grep -l "**MOVED**" {source}/*.md | wc -l
```

### 4. Audit Trail

| Check | Pass Criteria |
|-------|---------------|
| INDEX.md exists | In archive parent |
| Entry present | Molt recorded |
| Counts match | Files = recorded count |

---

## Automated Verification

```bash
# Full verification
python -m truth_forge.molt verify --source {source_dir} --full

# Output:
# ✓ Source shrinkage: 95% reduction (5000 → 200 lines)
# ✓ Archive integrity: 45 files preserved
# ✓ Stub validity: 45/45 stubs valid
# ✓ Audit trail: Entry recorded in INDEX.md
#
# MOLT VERIFIED
```

---

## Failure Recovery

### Stub Missing Required Marker

1. Identify incomplete stubs
2. Regenerate using `--fix-stubs`
3. Re-verify

### Archive Missing Files

1. Check if file was skipped (already stub)
2. Check archive permissions
3. Re-run molt for missing files

### Audit Trail Not Updated

1. Manually add entry to INDEX.md
2. Or re-run molt (will update if missing)

---

## Metrics

After successful molt:

| Metric | Value |
|--------|-------|
| Files molted | Count |
| Lines before | Total |
| Lines after | Total (stubs) |
| Shrinkage | Percentage |
| Archive size | Total bytes |

```bash
# Generate metrics report
python -m truth_forge.molt metrics --source {source_dir}
```

---

## UP

[INDEX.md](INDEX.md) - Molt Standard hub
