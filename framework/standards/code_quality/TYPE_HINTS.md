# Type Hints

**All functions MUST have type hints per PEP 484.**

---

## Requirements

| Context | Requirement |
|---------|-------------|
| Function parameters | Required |
| Function return types | Required |
| Class attributes | Required (use dataclass or explicit) |
| Local variables | Optional (inference works) |
| Module-level constants | Recommended |

---

## Basic Example

```python
from typing import Any, Dict, List, Optional, Union

# CORRECT: Full type hints
def process_records(
    records: List[Dict[str, Any]],
    batch_size: int = 1000,
    skip_empty: bool = True,
) -> tuple[List[Dict[str, Any]], int]:
    """Process records and return results with count."""
    ...

# WRONG: No type hints
def process_records(records, batch_size=1000, skip_empty=True):
    ...
```

---

## Common Patterns

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

---

## Anti-Patterns

### Missing Type Hints

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

### Type: ignore Without Explanation

```python
# WRONG
result = risky_call()  # type: ignore

# CORRECT
result = risky_call()  # type: ignore[no-untyped-call] # Legacy API, tracked in #123
```

### Any Everywhere

```python
# WRONG
def process(data: Any) -> Any:
    ...

# CORRECT
def process(data: List[UserRecord]) -> ProcessResult:
    ...
```

---

## Escape Hatch

```python
# standard:override code-quality-type-hints - Third-party library untyped, tracked in #456
result = untyped_library.call()  # type: ignore[no-untyped-call]
```

---

## UP

[code_quality/INDEX.md](INDEX.md)
