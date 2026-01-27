# Static Analysis

**All code MUST pass mypy, ruff check, and ruff format before merge.**

---

## Quick Reference

```bash
# Must pass before "done"
.venv/bin/mypy src/ --strict
.venv/bin/ruff check src/
.venv/bin/ruff format --check src/
```

---

## mypy (Type Checking)

```bash
# Run type checking
mypy src/ --strict
```

### Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

---

## ruff (Linting)

```bash
# Run linting
ruff check src/
```

### Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # Pyflakes
    "I",     # isort
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
    "ARG",   # flake8-unused-arguments
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate (commented code)
    "PL",    # Pylint
    "RUF",   # Ruff-specific
]
ignore = [
    "PLR0913",  # Too many arguments (use dataclass instead)
]

[tool.ruff.lint.isort]
known-first-party = ["src"]
```

---

## Formatting

```bash
# Format code
ruff format src/

# Check formatting
ruff format --check src/
```

### Configuration

```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

---

## Complexity Limits

| Metric | Limit | Tool |
|--------|-------|------|
| Cyclomatic complexity | <= 10 per function | ruff (C901) |
| Function length | <= 50 lines | ruff |
| Module length | <= 500 lines | ruff |
| Arguments | <= 5 per function | ruff (PLR0913) |

### Complexity Override

```python
# standard:override code-quality-complexity - Algorithm requires nested loops, documented in ADR-123
def complex_algorithm(data: Matrix) -> Matrix:  # noqa: C901
    ...
```

---

## Enforcement

| Tool | Check | Severity | CI Gate |
|------|-------|----------|---------|
| mypy | Type errors | error | Yes |
| ruff | Lint violations | error | Yes |
| ruff format | Format violations | error | Yes |
| coverage | Missing docstrings | warning | No |

---

## UP

[code_quality/INDEX.md](INDEX.md)
