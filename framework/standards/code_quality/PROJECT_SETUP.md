# Project Setup

**Complete configuration for code quality in a Python project.**

---

## pyproject.toml (Complete)

```toml
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

---

## Pre-Commit Configuration

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

---

## CI/CD Configuration

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

---

## Editor Configuration (VSCode)

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

## Code Review Checklist

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] No `# type: ignore` without explanation
- [ ] No `Any` types without justification
- [ ] Naming follows conventions
- [ ] Complexity within limits

---

## UP

[code_quality/INDEX.md](INDEX.md)
