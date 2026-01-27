# Deprecation Verification

**SEE:DO phase - verifying deprecation is complete.**

---

## The SEE:SEE:DO Cycle

```
SEE ────→ SEE:SEE ────→ DO ────→ SEE:DO
```

| Phase | Application |
|-------|-------------|
| **SEE** | "Old standards exist in prior location" |
| **SEE:SEE** | "These are superseded by new standards" |
| **DO** | Mark deprecated, move to `_archive/` |
| **SEE:DO** | Verify files moved, headers added, references updated |

**The cycle is not complete until SEE:DO confirms the DO.**

---

## Verification Checklist

After deprecation, verify:

- [ ] All deprecated files have deprecation header
- [ ] Header has all required fields (Superseded By, Date, Sunset, Reason)
- [ ] Status field updated to DEPRECATED
- [ ] Superseding document exists and is ACTIVE
- [ ] References updated to point to new location
- [ ] Molt lineage updated

---

## After Archival, Verify

- [ ] All deprecated files moved to `_archive/`
- [ ] Redirect stubs in place (if applicable)
- [ ] No broken links remain
- [ ] Molt lineage shows ARCHIVED status

---

## Automated Verification

```bash
# Find deprecated files
grep -r "DEPRECATED" --include="*.md" .

# Verify deprecation headers are complete
grep -A 5 "DEPRECATED" *.md | grep -c "Superseded By"

# Verify no references to deprecated paths
grep -r "Truth_Engine/framework/0" . --include="*.md" | grep -v "_archive"

# Find orphaned references (custom script needed)
python scripts/check_deprecation_refs.py
```

---

## Common Failures

| Failure | Detection | Fix |
|---------|-----------|-----|
| Missing header | `grep -L "DEPRECATED"` | Add header |
| Broken successor link | Link checker | Update link |
| Orphaned references | Reference grep | Update refs |
| Missing lineage | Manual check | Add to lineage |

---

## UP

[INDEX.md](INDEX.md)
