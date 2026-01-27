# Versioning

**APIs evolve. Versioning protects consumers.**

---

## The Rule

All public APIs must be versioned. Breaking changes require a new version.

---

## Versioning Strategies

| Strategy | Format | When to Use |
|----------|--------|-------------|
| URL path | `/api/v1/users` | Default choice |
| Header | `Accept: application/vnd.api+json;version=1` | Complex scenarios |
| Query param | `/users?version=1` | Avoid (caching issues) |

**Default: URL path versioning.**

---

## URL Path Versioning

```
/api/v1/users
/api/v2/users
```

| Advantage | Reason |
|-----------|--------|
| Explicit | Version visible in URL |
| Cacheable | Different URLs = different cache |
| Simple | Easy to route and document |

---

## What Requires a New Version

| Change Type | New Version Required? |
|-------------|----------------------|
| Remove endpoint | Yes |
| Remove field from response | Yes |
| Change field type | Yes |
| Change required fields | Yes |
| Add optional field | No |
| Add new endpoint | No |
| Fix bug | No |

---

## Version Lifecycle

```
v1 (CURRENT)    → Active development
v2 (PREVIEW)    → Early adopters
v1 (DEPRECATED) → Still works, sunset announced
v1 (SUNSET)     → Removed
```

| State | Support Level |
|-------|---------------|
| CURRENT | Full support |
| DEPRECATED | Maintenance only, sunset date set |
| SUNSET | No longer available |

---

## Deprecation Process

```python
# 1. Announce deprecation (minimum 6 months notice)
# Response header:
Deprecation: true
Sunset: Sat, 01 Jul 2026 00:00:00 GMT

# 2. Document migration path
# 3. Support both versions during transition
# 4. Remove after sunset date
```

---

## Implementation

```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
async def get_users_v1():
    # Original implementation
    pass

@v2_router.get("/users")
async def get_users_v2():
    # New implementation with breaking changes
    pass
```

---

## Anti-Patterns

```python
# WRONG - No versioning
GET /users  # Which version?

# WRONG - Breaking change without version bump
# "We just changed the response format, consumers will adapt"

# WRONG - Too many versions
/api/v1, v2, v3, v4, v5...  # Maintenance nightmare
```

---

## UP

[INDEX.md](INDEX.md)
