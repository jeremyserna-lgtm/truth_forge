# Test Coverage

**MANDATORY: 90% line coverage minimum, 100% for critical paths. Zero exceptions.**

---

## Coverage Requirements

| Code Type | Minimum Coverage |
|-----------|------------------|
| **All Code** | **90%** |
| Core business logic | 100% |
| Public APIs | 100% |
| Error handling | 100% |
| Utility functions | 90% |
| Pipeline stages | 90% |
| Generated code | Excluded |

---

## Running Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Fail if coverage below threshold (90% MANDATORY)
pytest --cov=src --cov-fail-under=90

# View HTML report
open htmlcov/index.html
```

---

## Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 90
```

---

## What Coverage Doesn't Tell You

Coverage measures **execution**, not **correctness**.

```python
# 100% coverage, but WRONG test
def test_add():
    result = add(2, 2)
    assert result is not None  # Passes but proves nothing!

# Better test
def test_add_two_positives():
    assert add(2, 2) == 4

def test_add_negative_and_positive():
    assert add(-1, 5) == 4
```

---

## Branch Coverage

Line coverage isn't enough. Test all branches.

```python
def process(value: int) -> str:
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    else:
        return "zero"

# Need THREE tests for full branch coverage
def test_process_positive(): assert process(1) == "positive"
def test_process_negative(): assert process(-1) == "negative"
def test_process_zero(): assert process(0) == "zero"
```

---

## Excluding Code

```python
# Exclude from coverage (use sparingly)
if __name__ == "__main__":  # pragma: no cover
    main()

# With justification
def debug_helper():  # pragma: no cover - debug only
    ...
```

---

## UP

[testing/INDEX.md](INDEX.md)
