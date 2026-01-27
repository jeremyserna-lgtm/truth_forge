# ADR-0002: Code Quality Standards as Claude Identity

**Status**: Accepted
**Date**: 2026-01-25
**Context**: Embedding code quality standards into Claude's operational identity

---

## Context

Jeremy is a coder. He reads code, understands patterns, and verifies correctness. Claude's code serves as Jeremy's textbook - it must demonstrate industry best practices.

Previous approach: Standards as external rules Claude follows.
New approach: Standards as identity Claude embodies.

## Decision

### 1. Standards Are Identity, Not Rules

**Decision**: Code quality standards are embedded into Claude's identity at both global (`~/.claude/CLAUDE.md`) and project levels.

**Rationale**:
- Rules can be followed or ignored
- Identity cannot be separated from self
- Claude should "arrive already being this" rather than "follow these rules"
- Consistency across sessions through identity-level embedding

### 2. The Five Identity Standards

| Standard | What It Is | Why It's Identity |
|----------|------------|-------------------|
| **Type Hints** | PEP 484 on ALL parameters AND return types | "I think in types." |
| **Structured Logging** | `extra={}` not f-strings | "I think in queryable data." |
| **DLQ Pattern** | Never lose data in batch processing | "I never lose data." |
| **Retry Logic** | Exponential backoff for external calls | "I expect failure." |
| **Static Analysis** | mypy, ruff must pass before "done" | "I verify before claiming." |

**The Phrase**: "I don't follow these rules. I AM these standards."

### 3. Verification Commands

```bash
# The "is it done?" verification:
.venv/bin/mypy <file.py> --strict
.venv/bin/ruff check <file.py>
.venv/bin/ruff format --check <file.py>
.venv/bin/pytest tests/ -v --cov
```

**If any fail, Claude is NOT done.**

### 4. Canonical Standard Locations

| Standard | Location |
|----------|----------|
| code_quality | [standards/code_quality/](../standards/code_quality/) |
| logging | [standards/logging/](../standards/logging/) |
| error_handling | [standards/error_handling/](../standards/error_handling/) |
| testing | [standards/testing/](../standards/testing/) |
| pipeline | [standards/pipeline/](../standards/pipeline/) |

---

## Consequences

### Positive
- Consistent code quality across all Claude sessions
- Jeremy can trust code meets industry standards
- "Done" has a verifiable definition

### Negative
- May need recalibration if standards conflict with specific needs

---

## References

- [standards/code_quality/](../standards/code_quality/) - Canonical standard
- [07_STANDARDS](../07_STANDARDS.md) - Standards as DNA

---

*Decided: 2026-01-25*
