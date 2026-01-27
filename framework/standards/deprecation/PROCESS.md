# Deprecation Process

**Step-by-step process for deprecating components.**

---

## Step 1: Identify Supersession

Before deprecating, identify:
- What supersedes this component?
- Is the molt complete (all functionality transferred)?
- Are there dependencies that need updating?

---

## Step 2: Add Deprecation Header and Move to Archive

Add the deprecation header to the beginning of the file, immediately after any front matter, then immediately move to archive.

```markdown
> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [path/to/new.md]
> - **Deprecated On**: 2026-01-26
> - **Archived On**: 2026-01-26
> - **Reason**: Molted to truth_forge
```

**Then immediately**:
1. Move the file to archive location (local archive folder)
2. Upload to GCS archive bucket (`gs://truth-engine-archive/`)
3. Remove file from original location (no redirect stub)
4. Update archive INDEX.md

---

## Step 3: Update Status

Change the `**Status**:` field to `DEPRECATED`.

---

## Step 4: Update References

Search for references to the deprecated component and update them to point to the superseding component or archive location.

---

## Step 5: Update References

Search for references to the deprecated component and update them to point to the superseding component.

```bash
# Find references
grep -r "old_component" . --include="*.md"

# Update references
sed -i 's|old_path|new_path|g' file.md
```

---

## Step 6: Log the Deprecation

Record in the molt lineage:

```markdown
## Molt Lineage

[Old Component] (DEPRECATED - 2026-01-26)
    └── [New Component] (ACTIVE)
```

---

## Archive Process

**Archive immediately when deprecating**:

```bash
# 1. Create archive folder if needed
mkdir -p archive/YYYY_MM_DD/

# 2. Move deprecated file to archive (preserving original content with deprecation header)
mv deprecated_file.md archive/YYYY_MM_DD/deprecated_file.md

# 3. Update archive INDEX.md
echo "| YYYY-MM-DD | ARCHIVE | deprecated_file.md | Superseded by new.md |" >> archive/INDEX.md

# 4. Update any remaining references
grep -r "old_path" . | xargs sed -i 's|old_path|new_path|g'
```

**Key Points**:
- Archive happens **immediately** when deprecating (no waiting period)
- Original file is moved to local archive with deprecation header intact
- File is uploaded to GCS bucket `gs://truth-engine-archive/` preserving path structure
- Original location is left empty (file removed, **no redirect stub**)
- Archive INDEX.md is updated with audit trail

---

## UP

[INDEX.md](INDEX.md)
