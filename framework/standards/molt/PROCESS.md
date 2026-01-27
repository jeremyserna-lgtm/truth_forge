# Molt Process

**Layer**: Specifics (NOT-ME) - how to execute a molt

---

## Prerequisites

Before molting:

1. **Content has moved** - Files exist in destination
2. **Destination verified** - Structure is correct
3. **Archive location chosen** - Usually `{source}/../archive/molt_YYYY_MM_DD/`

---

## The Process

### Phase 1: Discovery

```bash
# List source files
python -m truth_forge.molt discover --source {source_dir}

# Compare to destination
python -m truth_forge.molt compare --source {source_dir} --dest {dest_dir}
```

Output:
- Files found in source
- Files present in destination
- Files to migrate
- Files to skip (already stubs)

### Phase 2: Dry Run

```bash
python -m truth_forge.molt run \
    --source {source_dir} \
    --dest {dest_dir} \
    --dry-run
```

Review output. Verify:
- Correct files identified
- Archive path is appropriate
- No unexpected skips

### Phase 3: Execute

```bash
python -m truth_forge.molt run \
    --source {source_dir} \
    --dest {dest_dir} \
    --execute
```

This will:
1. Create archive directory if needed
2. Move source files to archive
3. Create redirect stubs in source
4. Update archive INDEX.md

### Phase 4: Verify

```bash
python -m truth_forge.molt verify --source {source_dir}
```

Verify:
- Source files are now stubs
- Archive files are originals
- Audit trail is updated
- Total content preserved

---

## Batch Molt (All Standard Mappings)

For standard folder mappings:

```bash
python -m truth_forge.molt run --all --dry-run
python -m truth_forge.molt run --all --execute
```

This processes all mappings defined in `molt.yaml`.

---

## Manual Steps (If Needed)

### Create Archive Directory

```bash
mkdir -p {source}/../archive/molt_YYYY_MM_DD
```

### Move File to Archive

```bash
mv {source}/file.md {archive}/file.md
```

### Create Stub

```bash
cat > {source}/file.md << 'EOF'
# File Title

> **MOVED**: This document has been molted to truth_forge.
>
> **New Location**: [path](relative/path/to/new)
>
> **Archive**: [path](relative/path/to/archive)
>
> **Molted On**: YYYY-MM-DD
EOF
```

### Update Audit Trail

Add entry to `{archive}/../INDEX.md`:

```markdown
| YYYY-MM-DD | MOLT | {source_name} | {file_count} |
```

---

## Error Recovery

### Stub Created But Archive Failed

1. Check archive directory exists
2. Manually move file
3. Re-run verification

### Partial Molt

1. Re-run molt (idempotent—skips already-molted)
2. Verify all files processed

### Wrong Destination

1. Remove incorrect stubs
2. Restore from archive
3. Re-run with correct destination

---

## UP

[INDEX.md](INDEX.md) - Molt Standard hub
