# Blocked Items (Planning DLQ)

**A plan without a DLQ loses failures silently.**

---

## What Gets Blocked

| Blocker Type | Example | Resolution Path |
|--------------|---------|-----------------|
| External dependency | API not available | Wait, find alternative |
| Missing information | Requirements unclear | Ask, document assumption |
| Technical constraint | System incompatible | Workaround, override |
| Resource constraint | Need access/permissions | Request, escalate |

---

## Tracking Blocked Items

```markdown
## DLQ (Blocked Items)

| Item | Blocker | Date | Resolution |
|------|---------|------|------------|
| Task 3 | External API rate limited | 2026-01-26 | Waiting for quota increase |
| Task 7 | Need prod DB access | 2026-01-26 | Access request submitted |
```

---

## Partial Completion

When a plan cannot fully complete:

```markdown
# standard:override planning-complete - External blocker documented in ISSUE-123
## Status: BLOCKED

### Completed
- [x] Task 1 (verified)
- [x] Task 2 (verified)

### Blocked
- [ ] Task 3 - Blocked by: External API not available
  - Resolution: Waiting on vendor, ETA unknown
  - Workaround: None available

### Verification
- Completed tasks: All gates verified
- Blocked tasks: Documented in DLQ with external references
```

---

## DLQ Resolution Protocol

1. **Document** - Capture blocker with full context
2. **Communicate** - Inform stakeholders
3. **Track** - Add to project tracking system
4. **Review** - Periodic check for resolution
5. **Resolve** - Update DLQ when blocker cleared

---

## Anti-Pattern: Silent Discard

```markdown
# WRONG - Blocked items disappear
## Tasks
- [x] Task 1
- [x] Task 2
- [ ] Task 3  ← What happened here? No explanation!

# CORRECT - Blocked items documented
## Tasks
- [x] Task 1 (verified)
- [x] Task 2 (verified)

## Blocked Items
| Task 3 | External API unavailable | 2026-01-26 | ISSUE-123 |
```

---

## UP

[planning/INDEX.md](INDEX.md)
