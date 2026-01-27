# Planning

**The Standard** | Plans are not done until gates verify EXISTENCE, not just PASSING.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │       planning/INDEX.md               │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
[CLASSIFICATION]        [GATES]           [BLOCKED]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                     [CHECKLISTS]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (testing/, error_handling/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| Classification | MIGRATION / CREATION / RESEARCH / CONFIG | [CLASSIFICATION.md](CLASSIFICATION.md) |
| Gate Verification | Existence before passing | [GATES.md](GATES.md) |
| Blocked Items | DLQ for planning | [BLOCKED.md](BLOCKED.md) |
| Checklists | Verification per task type | [CHECKLISTS.md](CHECKLISTS.md) |
| Idempotency | Same input → same output | Below |
| Completion | "Done" = gates verified | Below |

---

## Layer Definition

For WHY this layer exists and WHAT a planning primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [CLASSIFICATION.md](CLASSIFICATION.md) | 80 | Task type classification |
| [GATES.md](GATES.md) | 100 | Gate verification patterns |
| [BLOCKED.md](BLOCKED.md) | 80 | Blocked item handling |
| [CHECKLISTS.md](CHECKLISTS.md) | 110 | Verification checklists |

---

## WHY (Theory)

### The False Done Problem

**The most dangerous failure is the one that looks like success.**

```
MIGRATION PATH (worked)
Legacy Code → Copy → Transform → Run Existing Tests → PASS ✓

CREATION PATH (failed)
New Code → Write → Transform → Run (no tests) → PASS ← FALSE POSITIVE
                                    0/0 = 100%?
```

When you run `pytest` with no tests, it passes. **The absence of failure is not proof of success.**

This is why planning must verify EXISTENCE before claiming PASSING:
- Tests exist (not just that pytest passed)
- Data arrived (not just that code ran)
- Errors captured (not just that no exceptions surfaced)

### The Furnace Method

```
TRUTH → MEANING → CARE
```

| Phase | Planning Question |
|-------|-------------------|
| **TRUTH** | What actually exists? (Not assumptions) |
| **MEANING** | What matters here? What are the real risks? |
| **CARE** | What does careful execution look like? |

---

## WHAT (Specification)

### Idempotency Requirement

Plans that modify state MUST be idempotent:

```python
# CORRECT: Idempotent
conn.execute("INSERT OR REPLACE INTO table (id, data) VALUES (?, ?)", ...)

# WRONG: Non-idempotent (duplicates on re-run)
conn.execute("INSERT INTO table (data) VALUES (?)", ...)
```

### Data Safety Requirement

Plans that process data MUST never silently discard failures:

```python
# CORRECT: Failures captured
for record in records:
    try:
        process(record)
    except Exception as e:
        dlq.append({"record": record, "error": str(e)})

# WRONG: Silent discard
except Exception:
    pass  # Record lost forever
```

---

## Escape Hatch

For partial completion:

```markdown
# standard:override planning-complete - External blocker in ISSUE-123
## Status: BLOCKED

### Completed
- [x] Task 1 (verified)
- [x] Task 2 (verified)

### Blocked
- [ ] Task 3 - Blocked by: External API not available
```

---

## Pattern Coverage

### ME:NOT-ME

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Creating plans** | Defines WANT | Executes HOW |
| **Tracking progress** | Visual checklists | Automated gates |
| **Handling failures** | Resolution decisions | DLQ capture |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Requirements          → Task execution           → Verified deliverables
Plan document         → Work performed           → Gate-verified artifacts
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | What actually exists? (Not assumptions) |
| **MEANING** | What matters? (Prioritization) |
| **CARE** | Careful execution (Thoroughness) |

---

## Convergence

### Bottom-Up Validation

- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_RECURSION](../STANDARD_RECURSION.md) - SEE:SEE:DO verification

### Top-Down Validation

- [02_PERCEPTION](../../02_PERCEPTION.md) - SEE:SEE:DO for verification
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE
- [06_LAW](../../06_LAW.md) - Idempotency pillar

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [testing/](../testing/) | Test existence verification |
| [error_handling/](../error_handling/) | DLQ implementation |
| [code_quality/](../code_quality/) | Quality gates |

---

## Industry Alignment

- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [The Checklist Manifesto](https://atulgawande.com/book/the-checklist-manifesto/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-26 | Initial standard based on MIGRATION_PLAN lessons | Claude |

---

*Plans are not done until gates verify EXISTENCE, not just PASSING.*
