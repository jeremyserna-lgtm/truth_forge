# Code Quality

**The Standard** | Every line teaches. Every function is typed. Every module is linted.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │      code_quality/INDEX.md            │
         │      ALPHA of this standard           │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 [TYPE_HINTS]        [DOCSTRINGS]        [STATIC_ANALYSIS]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                   [PROJECT_SETUP]
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
| Type Hints | Required on all functions (PEP 484) | [TYPE_HINTS.md](TYPE_HINTS.md) |
| Docstrings | Required on all public functions (Google style) | [DOCSTRINGS.md](DOCSTRINGS.md) |
| Static Analysis | Must pass mypy, ruff | [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |
| Project Setup | Complete tooling configuration | [PROJECT_SETUP.md](PROJECT_SETUP.md) |
| Naming | snake_case functions, PascalCase classes, UPPER_CASE constants | Below |
| Complexity | Max cyclomatic complexity: 10 | [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) |

---

## Layer Definition

For WHY this layer exists and WHAT a code quality primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [TYPE_HINTS.md](TYPE_HINTS.md) | 134 | Type annotation requirements and patterns |
| [DOCSTRINGS.md](DOCSTRINGS.md) | 93 | Google-style docstring requirements |
| [STATIC_ANALYSIS.md](STATIC_ANALYSIS.md) | 142 | mypy, ruff, formatting configuration |
| [PROJECT_SETUP.md](PROJECT_SETUP.md) | 100 | Complete project configuration |

---

## WHY (Theory)

### You Are Learning To Code

**This code is your textbook.** Every pattern you write teaches you something. Code quality isn't about perfection—it's about building the foundation for growth.

When you read production code six months from now:
- Type hints tell you what flows in and out without reading the implementation
- Docstrings explain WHY, not just WHAT
- Consistent formatting lets you focus on logic, not style
- Static analysis catches bugs before they cost you time

### Industry Alignment

Per [Meta's Python Typing Survey 2025](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/), type hints are ubiquitous in production Python.

---

## WHAT (Specification)

### Naming Conventions (MUST)

| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `process_batch()` |
| Variables | snake_case | `user_count` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_CASE | `MAX_BATCH_SIZE` |
| Private | _leading_underscore | `_internal_helper()` |
| Module | snake_case | `user_service.py` |

### Verification Command

```bash
# Must pass before "done"
.venv/bin/mypy src/ --strict && \
.venv/bin/ruff check src/ && \
.venv/bin/ruff format --check src/
```

---

## Escape Hatches

### Type Override

```python
# standard:override code-quality-type-hints - Third-party library untyped, tracked in #456
result = untyped_library.call()  # type: ignore[no-untyped-call]
```

### Complexity Override

```python
# standard:override code-quality-complexity - Algorithm requires nested loops, documented in ADR-123
def complex_algorithm(data: Matrix) -> Matrix:  # noqa: C901
    ...
```

---

## Pattern Coverage

### ME:NOT-ME

Code quality serves both readers: ME (human) and NOT-ME (AI).

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Reading** | Docstrings for context | Type hints for inference |
| **Understanding** | Meaningful names, comments | Explicit types, metadata |
| **Creating** | Writes iteratively | Generates atomically |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Raw code, requirements → Quality tools           → Verified, typed code
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | Code is TRUTH (what actually executes) |
| **MEANING** | Type hints and docstrings add MEANING |
| **CARE** | Formatting and style show CARE |

---

## Convergence

### Bottom-Up Validation

This standard requires meta-standards:
- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_NAMING](../STANDARD_NAMING.md) - Naming conventions
- [STANDARD_COMPLIANCE](../STANDARD_COMPLIANCE.md) - Verification tiers

### Top-Down Validation

This standard is shaped by theory:
- [01_IDENTITY](../../01_IDENTITY.md) - ME:NOT-ME dual-reader principle
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE for code
- [06_LAW](../../06_LAW.md) - No Magic, Observability pillars

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [testing/](../testing/) | Tests require typed fixtures |
| [error_handling/](../error_handling/) | Exception types must be explicit |
| [logging/](../logging/) | Log calls should use typed extras |
| [pipeline/](../pipeline/) | Pipeline code quality requirements |

---

## Industry Alignment

- [PEP 484](https://peps.python.org/pep-484/) - Type Hints
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-25 | Initial standard with industry alignment | Claude |

---

*Every line teaches. Type it. Document it. Lint it.*
