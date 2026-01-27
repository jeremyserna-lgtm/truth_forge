# Caching

**Cache at boundaries. Invalidate correctly. There are only two hard problems.**

---

## The Rule

Cache expensive operations at system boundaries. Always have an invalidation strategy.

---

## The Two Hard Problems

> "There are only two hard things in Computer Science: cache invalidation and naming things."
> — Phil Karlton

---

## When to Cache

| Cache When | Don't Cache When |
|------------|------------------|
| Expensive computation | Cheap to compute |
| Frequent reads, rare writes | Frequent writes |
| Data can be stale briefly | Must be fresh |
| Clear invalidation exists | Invalidation is complex |

---

## Cache Layers

```
Request → Memory Cache → Redis Cache → Database → Compute
           (fastest)      (shared)      (slower)   (slowest)

Each layer is a HOLD. Caching is HOLD optimization.
```

---

## Memory Cache (Single Process)

```python
from functools import lru_cache
from cachetools import TTLCache

# Simple LRU cache
@lru_cache(maxsize=1000)
def expensive_function(key: str) -> Result:
    return compute(key)

# TTL cache (expires after time)
cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes

def get_user(user_id: str) -> User:
    if user_id in cache:
        return cache[user_id]
    user = db.get_user(user_id)
    cache[user_id] = user
    return user
```

---

## Distributed Cache (Redis)

```python
import redis
import json
from typing import TypeVar, Callable

T = TypeVar("T")
r = redis.Redis()

def cached(key: str, ttl_seconds: int = 300) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            cached_value = r.get(key)
            if cached_value:
                return json.loads(cached_value)
            result = func(*args, **kwargs)
            r.setex(key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## Invalidation Strategies

| Strategy | When to Use |
|----------|-------------|
| TTL (time-to-live) | Data can be stale for known duration |
| Write-through | Write to cache and DB together |
| Write-behind | Write to cache, async write to DB |
| Event-based | Invalidate on specific events |

```python
# Event-based invalidation
def update_user(user_id: str, data: dict) -> None:
    db.update_user(user_id, data)
    cache.delete(f"user:{user_id}")  # Invalidate
```

---

## Cache Keys

```python
# GOOD - Deterministic, namespaced
key = f"user:{user_id}:profile"
key = f"query:{hash(query_params)}"

# BAD - Collision risk
key = str(user_id)  # No namespace
key = f"data:{datetime.now()}"  # Non-deterministic
```

---

## Anti-Patterns

```python
# WRONG - No invalidation strategy
cache[key] = value  # How does this ever update?

# WRONG - Caching mutable objects
cache[key] = user_object  # Mutations affect cache!

# WRONG - Unbounded cache
cache = {}  # Grows forever, memory leak
```

---

## UP

[INDEX.md](INDEX.md)
