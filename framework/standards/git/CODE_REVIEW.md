# Code Review

**All code merges through review. No exceptions.**

---

## The Rule

Every PR requires at least one approval before merge.

---

## PR Requirements

| Requirement | Purpose |
|-------------|---------|
| Descriptive title | Quick understanding |
| Summary of changes | Context for reviewer |
| Test evidence | Proof it works |
| Link to issue/task | Traceability |

---

## PR Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Change 1
- Change 2

## Test Plan
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows standards
- [ ] Documentation updated
```

---

## Reviewer Responsibilities

| Responsibility | Action |
|----------------|--------|
| Correctness | Does the code do what it claims? |
| Standards | Does it follow our patterns? |
| Security | Any vulnerabilities introduced? |
| Performance | Any obvious bottlenecks? |
| Clarity | Is it understandable to others? |

---

## Review Comments

```python
# GOOD - Constructive with suggestion
# Consider using a constant here for clarity:
# MAX_RETRIES = 5
# This makes the intent clear and allows easy updates.

# BAD - Vague criticism
# This is wrong.

# BAD - Style nitpick on unchanged code
# You should also fix line 42 while you're here.
```

---

## Review Etiquette

| Do | Don't |
|----|-------|
| Ask questions | Assume malice |
| Suggest alternatives | Demand rewrites |
| Focus on the code | Criticize the person |
| Approve when ready | Block indefinitely |

---

## Approval Requirements

| Change Type | Required Approvals |
|-------------|-------------------|
| Bug fix | 1 |
| Feature | 1 |
| Architecture change | 2 |
| Security-sensitive | 2 |
| Framework change | 2 + explicit approval |

---

## Anti-Patterns

```bash
# WRONG - Rubber stamp
"LGTM" (without actually reviewing)

# WRONG - Blocking on style
Refusing to approve over formatting (use automated tools)

# WRONG - Scope creep
"While you're here, also fix these 10 unrelated things"
```

---

## Automation

Pre-merge checks (CI) should verify:

| Check | Tool |
|-------|------|
| Type safety | mypy --strict |
| Linting | ruff check |
| Formatting | ruff format --check |
| Tests | pytest |
| Coverage | pytest --cov |

Human review focuses on what automation cannot check.

---

## UP

[INDEX.md](INDEX.md)
