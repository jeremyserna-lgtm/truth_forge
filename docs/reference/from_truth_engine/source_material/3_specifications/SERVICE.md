# Service Contract

**What you put in a service.**

*A service is a Python class that provides functionality to other code.*

---

## Required Structure

```python
from architect_central_services import (
    get_logger,
    write_event,
)

logger = get_logger(__name__)


class MyService:
    """[Description of what this service provides]."""

    def __init__(self, cache_ttl: int = 60):
        self._cache_ttl = cache_ttl
        self._cache: dict = {}
        self._cache_time: float = 0

    def my_method(self, arg: str) -> Result:
        """[Description of what this method does]."""
        write_event(
            source=f"{self.__class__.__name__}.my_method",
            event_type="call",
            content={"arg": arg}
        )

        try:
            result = self._do_work(arg)

            write_event(
                source=f"{self.__class__.__name__}.my_method",
                event_type="return",
                content={"status": "success"}
            )

            return result

        except Exception as e:
            write_event(
                source=f"{self.__class__.__name__}.my_method",
                event_type="error",
                content={"error": str(e)}
            )
            raise

    def invalidate_cache(self) -> None:
        """Clear the cache."""
        self._cache = {}
        self._cache_time = 0
```

---

## Required Patterns

### Caching with TTL

```python
import time

def _get_cached(self, key: str):
    now = time.time()
    if now - self._cache_time > self._cache_ttl:
        self._cache = {}
        self._cache_time = now
    return self._cache.get(key)

def _set_cached(self, key: str, value):
    self._cache[key] = value
```

### Generators for Large Results

```python
# WRONG - loads all into memory
def get_items(self) -> List[Item]:
    return [process(x) for x in self._query_all()]

# CORRECT - streams results
def iter_items(self) -> Generator[Item, None, None]:
    for x in self._query_all():
        yield process(x)
```

### Input Validation

```python
def my_method(self, value: str) -> Result:
    if not value:
        raise ValueError("value is required")
    if len(value) > 1000:
        raise ValueError("value too long")
    # proceed...
```

---

## Template

```python
"""
[Service Name] Service

Provides: [What this service provides]
"""

import time
from typing import Generator, Optional
from architect_central_services import get_logger, write_event

logger = get_logger(__name__)


class MyService:
    """[Description]."""

    def __init__(self, cache_ttl: int = 60):
        """Initialize the service.

        Args:
            cache_ttl: Cache time-to-live in seconds.
        """
        self._cache_ttl = cache_ttl
        self._cache: dict = {}
        self._cache_time: float = 0

    def do_something(self, input: str) -> str:
        """Do something with input.

        Args:
            input: The input to process.

        Returns:
            The processed result.

        Raises:
            ValueError: If input is invalid.
        """
        # Validate
        if not input:
            raise ValueError("input is required")

        # Log call
        write_event(
            f"{self.__class__.__name__}.do_something",
            "call",
            {"input_length": len(input)}
        )

        try:
            # Check cache
            cached = self._get_cached(input)
            if cached:
                return cached

            # Process
            result = self._process(input)

            # Cache result
            self._set_cached(input, result)

            # Log return
            write_event(
                f"{self.__class__.__name__}.do_something",
                "return",
                {"status": "success"}
            )

            return result

        except Exception as e:
            write_event(
                f"{self.__class__.__name__}.do_something",
                "error",
                {"error": str(e)}
            )
            raise

    def iter_items(self, limit: int = 100) -> Generator[Item, None, None]:
        """Iterate over items.

        Args:
            limit: Maximum items to return.

        Yields:
            Items one at a time.
        """
        count = 0
        for item in self._query():
            if count >= limit:
                break
            yield item
            count += 1

    def invalidate_cache(self) -> None:
        """Clear the cache."""
        self._cache = {}
        self._cache_time = 0

    def _get_cached(self, key: str):
        now = time.time()
        if now - self._cache_time > self._cache_ttl:
            self._cache = {}
            self._cache_time = now
        return self._cache.get(key)

    def _set_cached(self, key: str, value):
        self._cache[key] = value

    def _process(self, input: str) -> str:
        # Implementation
        pass

    def _query(self):
        # Implementation
        pass
```

---

## Checklist

```
[ ] Has clear interface (methods with types)
[ ] Validates inputs
[ ] Returns typed results
[ ] Logs calls via write_event()
[ ] Logs errors via write_event()
[ ] Has cache with TTL
[ ] Has invalidate_cache() method
[ ] Uses generators for large results
[ ] Has docstrings for public methods
```

---

## Writes To

`~/.primitive_engine/service_calls.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Service | writes | call events | to service_calls.jsonl via write_event() |

---

*Derived from [The Entity Contracts](INDEX.md)*
