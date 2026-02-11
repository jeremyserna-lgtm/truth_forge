# Code Quality

**The Standard** | Every line teaches. Every function is typed. Every module is linted.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Type Hints | Required on all functions (PEP 484) |
| Docstrings | Required on all public functions (Google style) |
| Static Analysis | Must pass mypy, ruff |
| Formatting | Must pass black or ruff format |
| Naming | snake_case functions, PascalCase classes, UPPER_CASE constants |
| Complexity | Max cyclomatic complexity: 10 |

---

## WHY (Theory)

### You Are Learning To Code

**This code is your textbook.** Every pattern you write teaches you something. Every shortcut becomes a habit. Code quality isn't about perfection—it's about building the foundation for growth.

When you read production code six months from now:
- Type hints tell you what flows in and out without reading the implementation
- Docstrings explain WHY, not just WHAT
- Consistent formatting lets you focus on logic, not style
- Static analysis catches bugs before they cost you time

### Industry Alignment

Per [Meta's Python Typing Survey 2025](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/), type hints are now ubiquitous in production Python. Static typing:
- Improves code quality
- Enables better tooling (autocomplete, refactoring)
- Documents code automatically
- Catches bugs at write-time, not runtime

---

## WHAT (Specification)

### Type Hints (MUST)

All functions MUST have type hints per PEP 484:

```python
from typing import Any, Dict, List, Optional, Union

# ✅ CORRECT: Full type hints
def process_records(
    records: List[Dict[str, Any]],
    batch_size: int = 1000,
    skip_empty: bool = True,
) -> tuple[List[Dict[str, Any]], int]:
    """Process records and return results with count."""
    ...

# ❌ WRONG: No type hints
def process_records(records, batch_size=1000, skip_empty=True):
    ...
```

#### Type Hint Requirements

| Context | Requirement |
|---------|-------------|
| Function parameters | Required |
| Function return types | Required |
| Class attributes | Required (use dataclass or explicit) |
| Local variables | Optional (inference works) |
| Module-level constants | Recommended |

#### Common Patterns

```python
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from collections.abc import Iterator, Sequence

# Optional (can be None)
def find_user(user_id: str) -> Optional[User]:
    ...

# Union types (multiple types)
def parse_input(value: Union[str, int]) -> str:
    ...

# Python 3.10+ union syntax
def parse_input(value: str | int) -> str:
    ...

# Callable (functions as arguments)
def apply_transform(
    data: List[Dict],
    transform: Callable[[Dict], Dict],
) -> List[Dict]:
    ...

# Generic types
T = TypeVar('T')
def first_or_none(items: Sequence[T]) -> Optional[T]:
    return items[0] if items else None

# TypedDict for structured dicts
from typing import TypedDict

class UserRecord(TypedDict):
    user_id: str
    email: str
    created_at: str
```

### Docstrings (MUST)

All public functions MUST have docstrings using Google style:

```python
def generate_entity_id(
    session_id: str,
    message_index: int,
    content: str,
) -> str:
    """Generate a deterministic entity ID for a message.

    Creates a stable, unique identifier based on session context and
    content hash. The ID is deterministic: same inputs always produce
    same output.

    Args:
        session_id: The session identifier (e.g., "abc123").
        message_index: Zero-based index of message within session.
        content: The message content to hash.

    Returns:
        A 32-character hexadecimal entity ID.

    Raises:
        ValueError: If session_id is empty or message_index is negative.

    Example:
        >>> generate_entity_id("sess_123", 0, "Hello world")
        'a1b2c3d4e5f6789012345678901234ab'
    """
    if not session_id:
        raise ValueError("session_id cannot be empty")
    if message_index < 0:
        raise ValueError("message_index cannot be negative")
    ...
```

#### Docstring Requirements

| Section | When Required |
|---------|---------------|
| Summary | Always (first line) |
| Args | When function has parameters |
| Returns | When function returns a value |
| Raises | When function raises exceptions |
| Example | Recommended for complex functions |

### Static Analysis (MUST)

All code MUST pass these tools before merge:

#### mypy (Type Checking)

```bash
# Run type checking
mypy src/ --strict

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

#### ruff (Linting)

```bash
# Run linting
ruff check src/

# Configuration in pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ARG", # flake8-unused-arguments
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by formatter)
]
```

#### black or ruff format (Formatting)

```bash
# Format code
black src/
# or
ruff format src/

# Configuration
[tool.black]
line-length = 100
target-version = ["py311"]
```

### Naming Conventions (MUST)

| Type | Convention | Example |
|------|------------|---------|
| Functions | snake_case | `process_batch()` |
| Variables | snake_case | `user_count` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_CASE | `MAX_BATCH_SIZE` |
| Private | _leading_underscore | `_internal_helper()` |
| Module | snake_case | `user_service.py` |

```python
# ✅ CORRECT
MAX_RETRIES = 5

class UserService:
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        ...

    def _validate_input(self, data: Dict) -> bool:
        ...

# ❌ WRONG
maxRetries = 5  # camelCase

class userService:  # lowercase
    def GetUserById(self, userId):  # PascalCase method, camelCase param
        ...
```

### Complexity Limits (SHOULD)

| Metric | Limit | Tool |
|--------|-------|------|
| Cyclomatic complexity | ≤ 10 per function | ruff (C901) |
| Function length | ≤ 50 lines | ruff |
| Module length | ≤ 500 lines | ruff |
| Arguments | ≤ 5 per function | ruff (PLR0913) |

```python
# ❌ WRONG: Too complex (cyclomatic complexity > 10)
def process(data, mode, flag1, flag2, flag3, option):
    if mode == "a":
        if flag1:
            if flag2:
                ...
            elif flag3:
                ...
        else:
            ...
    elif mode == "b":
        ...  # 20 more branches

# ✅ CORRECT: Decomposed into smaller functions
def process(data: Data, config: ProcessConfig) -> Result:
    """Process data according to configuration."""
    handler = get_handler(config.mode)
    return handler.process(data, config)
```

---

## HOW (Reference)

### Project Setup

```toml
# pyproject.toml - Complete code quality configuration

[project]
name = "truth-engine"
requires-python = ">=3.11"

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

[tool.black]
line-length = 100
target-version = ["py311"]
```

### Pre-Commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-PyYAML
```

### CI/CD Configuration

```yaml
# .github/workflows/code-quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Type check (mypy)
        run: mypy src/ --strict

      - name: Lint (ruff)
        run: ruff check src/

      - name: Format check (ruff)
        run: ruff format --check src/
```

### Editor Configuration

```json
// .vscode/settings.json
{
    "python.analysis.typeCheckingMode": "strict",
    "python.analysis.autoImportCompletions": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        }
    },
    "ruff.lint.args": ["--config=pyproject.toml"]
}
```

---

## Anti-Patterns

### ❌ Missing Type Hints

```python
# WRONG
def process(data, options=None):
    return [transform(x) for x in data]

# CORRECT
def process(
    data: List[Dict[str, Any]],
    options: Optional[ProcessOptions] = None,
) -> List[Dict[str, Any]]:
    return [transform(x) for x in data]
```

### ❌ Type: ignore Without Explanation

```python
# WRONG
result = risky_call()  # type: ignore

# CORRECT
result = risky_call()  # type: ignore[no-untyped-call] # Legacy API, tracked in #123
```

### ❌ Any Everywhere

```python
# WRONG
def process(data: Any) -> Any:
    ...

# CORRECT
def process(data: List[UserRecord]) -> ProcessResult:
    ...
```

### ❌ Missing Docstrings

```python
# WRONG
def calculate_score(user_id, factors):
    weights = get_weights()
    return sum(f * w for f, w in zip(factors, weights))

# CORRECT
def calculate_score(user_id: str, factors: List[float]) -> float:
    """Calculate user engagement score from weighted factors.

    Args:
        user_id: The user identifier for logging.
        factors: List of factor values (0.0 to 1.0).

    Returns:
        Weighted sum of factors (0.0 to 100.0).
    """
    weights = get_weights()
    return sum(f * w for f, w in zip(factors, weights))
```

---

## Escape Hatches

### Temporary Type Ignore

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

## Enforcement

### Automated Checks

| Tool | Check | Severity | CI Gate |
|------|-------|----------|---------|
| mypy | Type errors | error | Yes |
| ruff | Lint violations | error | Yes |
| ruff format | Format violations | error | Yes |
| coverage | Missing docstrings | warning | No |

### Code Review Checklist

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] No `# type: ignore` without explanation
- [ ] No `Any` types without justification
- [ ] Naming follows conventions
- [ ] Complexity within limits

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [TESTING.md](TESTING.md) | Tests require typed fixtures |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Exception types must be explicit |
| [LOGGING.md](LOGGING.md) | Log calls should use typed extras |
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | Pipeline code quality requirements |

---

## Industry Alignment

This standard aligns with:
- [PEP 484](https://peps.python.org/pep-484/) - Type Hints
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Meta Python Typing Survey 2025](https://engineering.fb.com/2025/12/22/developer-tools/python-typing-survey-2025-code-quality-flexibility-typing-adoption/)
- [Real Python: Code Quality](https://realpython.com/python-code-quality/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Initial standard with industry alignment | Claude |

---

*Every line teaches. Type it. Document it. Lint it.*
