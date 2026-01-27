# Python Developer Maturity: What I Wish I Knew

**Purpose:** Synthesized wisdom for someone 6+ months into a Python project.

**Context:** You've been building Truth Engine since July. You've created a framework, services, patterns. Here's what the collective wisdom says about the stage you're at and what comes next.

---

## The Maturity Curve

### Where You Are (6-12 Months In)

At this stage, developers typically:
- Have established patterns that "work"
- Have accumulated technical debt (knowingly or not)
- Have code that's functional but may not be "Pythonic"
- Are starting to see the consequences of early decisions
- Are ready to recognize what needs to change

**The good news:** You're at the perfect inflection point for a molt.

### The Three Stages

| Stage | Characteristic | Your Code |
|-------|---------------|-----------|
| **Junior** | "Make it work" | Gets the job done, may have anti-patterns |
| **Mid** | "Make it right" | Follows patterns, uses proper tools |
| **Senior** | "Make it sustainable" | Architected for change, maintainable by others |

---

## The "Things I Wish I Knew" Collection

### 1. Configuration Management

**What beginners do:**
```python
# Hardcoded everywhere
PROJECT_ID = "flash-clover-464719-g1"
BUCKET_NAME = "my-bucket"
```

**What experienced developers do:**
```python
# Pydantic Settings - typed, validated, env-aware
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_id: str = "flash-clover-464719-g1"
    bucket_name: str = "my-bucket"

    class Config:
        env_prefix = "APP_"  # APP_PROJECT_ID overrides

settings = Settings()
```

**Why it matters:** When you need to deploy to a different environment, you change environment variables, not code.

### 2. Error Handling

**What beginners do:**
```python
# Silent failure - the debugging nightmare
try:
    result = process(data)
except Exception:
    return None  # What happened? Who knows.
```

**What experienced developers do:**
```python
# Explicit error handling with context
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E
    context: str = ""

Result = Union[Ok[T], Err[E]]

def process(data) -> Result[ProcessedData, ProcessingError]:
    try:
        return Ok(do_processing(data))
    except ValueError as e:
        return Err(ProcessingError(str(e)), context="During validation")
```

**Why it matters:** When something fails at 3 AM, you need to know what and why.

### 3. The Anti-Patterns You Don't Know You Have

#### Mutable Default Arguments
```python
# WRONG - the list is shared across all calls
def add_item(item, items=[]):
    items.append(item)
    return items

# RIGHT
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

#### Wildcard Imports
```python
# WRONG - namespace pollution, unclear dependencies
from module import *

# RIGHT - explicit is better than implicit
from module import specific_function, SpecificClass
```

#### Empty `except` Clauses
```python
# WRONG - catches EVERYTHING including KeyboardInterrupt
try:
    risky_operation()
except:
    pass

# RIGHT - catch what you expect
try:
    risky_operation()
except SpecificError as e:
    logger.warning(f"Expected error: {e}")
```

#### Type Coercion as Validation
```python
# WRONG - hides data problems
value = int(user_input or 0)  # Silently converts None to 0

# RIGHT - fail fast, fix upstream
if user_input is None:
    raise ValueError("user_input required")
value = int(user_input)
```

### 4. Code Organization

**What beginners do:**
```
project/
├── main.py (1000 lines)
├── utils.py (2000 lines of everything)
└── helpers.py (more random functions)
```

**What experienced developers do:**
```
project/
├── core/           # Core business logic
│   ├── __init__.py
│   ├── models.py
│   └── services.py
├── adapters/       # External interfaces
│   ├── __init__.py
│   ├── database.py
│   └── api_client.py
├── config/         # Configuration
│   ├── __init__.py
│   └── settings.py
└── main.py         # Entry point only
```

**The principle:** Each module should have ONE reason to change.

### 5. The Boilerplate Problem

**What beginners do:**
```python
# Copy-paste the same __init__ into every service
class ServiceA:
    def __init__(self):
        self._data_dir = Path(__file__).parent / "data"
        self._pattern = Pattern(
            name="service_a",
            hold1_path=self._data_dir / "service_a_input",
            hold2_path=self._data_dir / "service_a_output",
            # ... 20 more lines
        )
```

**What experienced developers do:**
```python
# Factory function eliminates boilerplate
def create_service(name: str, agent_func: Callable) -> Pattern:
    data_dir = Path(__file__).parent / "data"
    return Pattern(
        name=name,
        hold1_path=data_dir / f"{name}_input",
        hold2_path=data_dir / f"{name}_output",
        agent=agent_func,
    )

class ServiceA:
    def __init__(self):
        self._pattern = create_service("service_a", self._process)
```

**Why it matters:** When you need to change the pattern, you change it once.

### 6. Testing Wisdom

**What beginners think:** "Tests slow me down."

**What experienced developers know:**
- Tests are documentation that runs
- Tests let you refactor with confidence
- Tests catch regressions before users do
- The right test is worth 100 manual checks

**The testing progression:**
```
Stage 1: No tests ("it works on my machine")
Stage 2: Tests for new code (partial coverage)
Stage 3: Tests before code (TDD)
Stage 4: Tests as design tool (tests shape architecture)
```

**Minimum viable testing:**
```python
# At minimum: test the contract, not the implementation
def test_process_returns_expected_shape():
    result = process(valid_input)
    assert "id" in result
    assert "status" in result
    assert result["status"] in ["success", "failure"]
```

### 7. Dependency Management

**What beginners do:**
```
pip install whatever
pip freeze > requirements.txt  # 200 transitive deps
```

**What experienced developers do:**
```
# pyproject.toml - declare what you actually use
[project]
dependencies = [
    "pydantic>=2.0",
    "httpx>=0.25",
]

[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]
```

**The wisdom:**
- Pin direct dependencies, let transitives float
- Audit dependencies regularly (security)
- Fewer dependencies = fewer problems

### 8. The Refactoring Decision

**When to refactor:**

| Signal | Action |
|--------|--------|
| Rule of Three | Third time seeing same pattern → extract |
| Bug magnet | Same area keeps breaking → redesign |
| Onboarding friction | New code takes too long to understand → simplify |
| Performance cliff | Bottleneck identified → optimize that one thing |

**When NOT to refactor:**
- Before understanding why it's that way
- Without tests to verify behavior preserved
- In the middle of a feature push
- Just because it's not how you'd write it today

**The Strangler Pattern:**
```
1. Write new implementation alongside old
2. Redirect traffic gradually
3. Monitor for problems
4. Remove old when confident
```

### 9. Documentation That Actually Works

**What beginners do:**
```python
def process(data):
    """Process the data."""  # Useless
    ...
```

**What experienced developers do:**
```python
def process(data: InputData) -> Result[OutputData, ProcessError]:
    """
    Transform raw input into normalized output.

    Args:
        data: Raw input with required fields 'id' and 'content'

    Returns:
        Ok(OutputData) on success
        Err(ProcessError) if validation fails

    Raises:
        ConnectionError: If external service unavailable

    Example:
        >>> process(InputData(id="123", content="hello"))
        Ok(OutputData(id="123", normalized="HELLO"))
    """
```

**The hierarchy:**
1. Type hints (machine-readable documentation)
2. Clear names (self-documenting code)
3. Docstrings (for complex logic)
4. README (for new developers)
5. Architecture docs (for system understanding)

### 10. The Observability Mindset

**What beginners do:**
```python
print("got here")
print(f"value is {value}")
```

**What experienced developers do:**
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "processing_started",
    input_id=data.id,
    input_size=len(data.content),
)

# ... process ...

logger.info(
    "processing_completed",
    input_id=data.id,
    output_size=len(result),
    duration_ms=elapsed,
)
```

**Why it matters:**
- Structured logs are searchable
- Context travels with the log
- You can answer "what happened?" months later

---

## The Molt Checklist

Based on all this wisdom, here's what to check in your codebase:

### Immediate (This Week)

- [ ] **Grep for hardcoded strings** - `flash-clover-464719-g1` etc.
- [ ] **Check for mutable defaults** - `def func(items=[])`
- [ ] **Find empty excepts** - `except:` or `except Exception: pass`
- [ ] **Identify copy-paste boilerplate** - Same 20+ lines in multiple files

### Short-term (This Sprint)

- [ ] **Create settings module** - Pydantic Settings for all config
- [ ] **Add type hints** - At least to public APIs
- [ ] **Create factory functions** - For repeated patterns
- [ ] **Add characterization tests** - Capture current behavior before refactoring

### Medium-term (This Quarter)

- [ ] **Establish code review checklist** - What you check every PR
- [ ] **Set up pre-commit hooks** - Automate style enforcement
- [ ] **Create architecture decision records** - Document why, not just what
- [ ] **Build observability** - Structured logging, metrics

---

## The Wisdom Summary

| Principle | What It Means |
|-----------|---------------|
| **Explicit > Implicit** | Clear code beats clever code |
| **Fail Fast** | Catch errors at the boundary, not in the depths |
| **One Reason to Change** | Each module has a single responsibility |
| **Tests as Documentation** | If you can't test it, you can't trust it |
| **Configuration Not Code** | Environment changes shouldn't require deploys |
| **Structured > Unstructured** | Logs, errors, data - structure enables tooling |
| **Boilerplate is a Smell** | Repetition means abstraction is missing |
| **Rule of Three** | Wait until third occurrence before abstracting |

---

## Applying to Truth Engine

### What You're Doing Right

1. **THE_PATTERN** - You have a canonical pattern (HOLD → AGENT → HOLD)
2. **Service structure** - Clear separation of services
3. **Governance** - Cost tracking, audit trails exist
4. **Framework thinking** - You think in systems, not scripts

### What the Molt Should Address

1. **Hardcodes → Settings** - `flash-clover-464719-g1` in 15+ files
2. **Boilerplate → Factory** - Same `__init__` in every service
3. **Silent errors → Result type** - `return None` becomes explicit
4. **Dead code → Clean removal** - `/tmp` paths that don't exist
5. **Config in code → Config in YAML** - AUTHORIZED_SCRIPTS hardcoded

### The Order of Operations

```
1. Delete dead code (quick win, removes confusion)
2. Add settings module (foundation for everything)
3. Add factory pattern (reduces boilerplate)
4. Add Result type (explicit error handling)
5. Migrate hardcodes (systematic cleanup)
6. Add pre-commit (prevent regression)
```

---

## Sources

This document synthesizes wisdom from:

- [Python Code Review Checklist - Redwerk](https://redwerk.com/blog/python-code-review-checklist/)
- [Python Code Review Checklist - JetBrains Qodana](https://www.jetbrains.com/pages/static-code-analysis-guide/python-code-review-checklist/)
- [Python Code Reviews - Microsoft Engineering Playbook](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/recipes/python/)
- [Code Review Best Practices - Qodo](https://www.qodo.ai/blog/code-review-best-practices/)
- [When to Refactor - Refactoring Guru](https://refactoring.guru/refactoring/when)
- [Technical Debt - Refactoring Guru](https://refactoring.guru/refactoring/technical-debt)
- [Prioritizing Refactoring vs New Features - Revelo](https://www.revelo.com/blog/rethinking-technical-debt-prioritizing-refactoring-vs-new-features)
- [Technical Debt and Refactoring - Aviator](https://www.aviator.co/blog/technical-debt-and-the-role-of-refactoring/)
- [Code Refactoring Best Practices - 5ly](https://5ly.co/blog/code-refactoring/)

---

*"The best time to refactor was when you wrote it. The second best time is now."*

*Created: January 20, 2026*
