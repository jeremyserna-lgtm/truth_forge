# Testing

**The Standard** | Every behavior is verified, every edge case anticipated, every regression prevented.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL

---

## THIS IS THE HUB

```
         ┌───────────────────────────────────────┐
         │       testing/INDEX.md                │
         │       ALPHA of this standard          │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 [UNIT_TESTS]      [INTEGRATION_TESTS]    [FIXTURES]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                       [COVERAGE]
```

| Direction | Where It Goes |
|-----------|---------------|
| **UP** | [standards/INDEX.md](../INDEX.md) (parent ALPHA) |
| **DOWN** | Primitives within this standard |
| **ACROSS** | Related standards (code_quality/, error_handling/) |

---

## Quick Reference

| Requirement | Rule | Details |
|-------------|------|---------|
| Unit Tests | Fast, focused, AAA pattern | [UNIT_TESTS.md](UNIT_TESTS.md) |
| Integration Tests | Component boundaries | [INTEGRATION_TESTS.md](INTEGRATION_TESTS.md) |
| Fixtures | Reusable test setup | [FIXTURES.md](FIXTURES.md) |
| Coverage | **Min 90%, 100% critical** | [COVERAGE.md](COVERAGE.md) |
| Naming | `test_<fn>_<scenario>_<expected>` | [UNIT_TESTS.md](UNIT_TESTS.md) |
| Isolation | Tests must not depend on each other | Below |

---

## Layer Definition

For WHY this layer exists and WHAT a testing primitive IS, see [README.md](README.md).

---

## Documents

| Document | Lines | Purpose |
|----------|-------|---------|
| [UNIT_TESTS.md](UNIT_TESTS.md) | 100 | Unit test patterns and examples |
| [INTEGRATION_TESTS.md](INTEGRATION_TESTS.md) | 110 | Integration test patterns |
| [FIXTURES.md](FIXTURES.md) | 110 | Fixtures and mocking |
| [COVERAGE.md](COVERAGE.md) | 90 | Coverage requirements (80% → 90%) |
| [COVERAGE_REQUIREMENT.md](COVERAGE_REQUIREMENT.md) | 400+ | **Non-negotiable 90% standard with blocker removal** |

---

## WHY (Theory)

### The Hardening Imperative

Tests are not about proving code works. Tests are about **hardening** code against future change. Every test is a specification. Every passing test is a guarantee. Every failing test is a gift—a bug caught before production.

### The Cost Equation

| Without Tests | With Tests |
|---------------|------------|
| Bugs found in production | Bugs found in development |
| Debugging time: hours | Debugging time: minutes |
| Confidence in refactoring: zero | Confidence in refactoring: high |

---

## WHAT (Specification)

### Test Pyramid

```
          ╱╲
         ╱  ╲          E2E Tests (few, slow, broad)
        ╱────╲
       ╱      ╲        Integration Tests (some, medium)
      ╱────────╲
     ╱          ╲      Unit Tests (many, fast, focused)
    ╱────────────╲
```

| Layer | Quantity | Speed | Scope |
|-------|----------|-------|-------|
| Unit | 70% | < 100ms | Single function/class |
| Integration | 20% | < 5s | Component boundaries |
| E2E | 10% | < 30s | Full user flows |

### Core Rules

| Level | Rule |
|-------|------|
| **MUST** | Test every public interface |
| **MUST** | Follow Arrange-Act-Assert pattern |
| **MUST** | Use descriptive test names |
| **MUST** | Achieve 90%+ coverage (MANDATORY) |
| **MUST NOT** | Write flaky tests |
| **MUST NOT** | Share mutable state between tests |
| **MUST NOT** | Skip error path testing |

### The False Done Problem

**Tests MUST EXIST before claiming "done".**

```bash
# WRONG: Assumes tests exist because pytest passed
pytest tests/  # If no tests exist, this passes!

# CORRECT: Verify existence first
test_count=$(find tests/ -name "test_*.py" | wc -l)
if [ "$test_count" -eq 0 ]; then
    echo "FAIL: No tests exist"
    exit 1
fi
pytest tests/ --cov-fail-under=90
```

---

## Escape Hatch

```python
# standard:override testing-coverage - Legacy code, tracked in ISSUE-123
@pytest.mark.skip(reason="Legacy code pending refactor")
def test_legacy_function():
    ...
```

---

## Enforcement

| Tool | Check | Severity |
|------|-------|----------|
| pytest | Test pass/fail | error |
| pytest-cov | Coverage threshold | error |
| ruff | Test file structure | warning |

---

## Pattern Coverage

### ME:NOT-ME

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Writing tests** | Knows intent, edge cases | Generates comprehensive coverage |
| **Reading tests** | Understands context | Parses assertions |
| **Debugging** | Visual inspection | Stack trace analysis |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Test input            → Code under test          → Assertion result
Fixture data          → Processing logic         → Expected output
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | The test executes (input → output) |
| **MEANING** | Assertions verify behavior |
| **CARE** | Edge cases covered, regressions prevented |

---

## Convergence

### Bottom-Up Validation

- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_RECURSION](../STANDARD_RECURSION.md) - SEE:SEE:DO verification

### Top-Down Validation

- [06_LAW](../../06_LAW.md) - Idempotency pillar (same input = same output)
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [code_quality/](../code_quality/) | Tests require typed fixtures |
| [error_handling/](../error_handling/) | Error paths must be tested |
| [planning/](../planning/) | Tests EXIST before claiming done |

---

## Industry Alignment

- [pytest Documentation](https://docs.pytest.org/)
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Split into primitives (INDEX + 4 files) | Claude |
| 2026-01-25 | Initial standard | Claude |

---

*Every behavior verified. Every edge case anticipated. Every regression prevented.*
