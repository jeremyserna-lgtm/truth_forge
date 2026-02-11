# API Design

**The Standard** | Every interface is consistent, versioned, documented, and designed for evolution.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Versioning | All APIs versioned from day one |
| Naming | RESTful resources, consistent conventions |
| Responses | Standard envelope with status, data, errors |
| Errors | Structured error responses with codes |
| Documentation | OpenAPI/Swagger for all endpoints |
| Rate Limiting | Documented limits with headers |

---

## WHY (Theory)

### The Contract Imperative

APIs are contracts. Once published, they bind you to your consumers. Every endpoint you expose is a promise. Breaking changes break trust. The standard ensures you make promises you can keep.

### The Evolution Principle

From 06_LAW: *"Change is constant. Design for change."*

APIs will evolve. New features will emerge. Old features will deprecate. The standard ensures evolution without breakage.

---

## WHAT (Specification)

### API Versioning

```
/api/v1/users          # Version in URL (preferred)
/api/users             # Version in header (alternative)
  Accept: application/vnd.api+json;version=1
```

| Version Change | When |
|----------------|------|
| Patch (v1.0.1) | Bug fixes, documentation |
| Minor (v1.1.0) | New endpoints, optional fields |
| Major (v2.0.0) | Breaking changes |

### MUST (Required)

#### Naming Conventions

1. **RESTful Resources** — Endpoints MUST represent resources, not actions.

```bash
# ✅ Correct - resource-oriented
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get user
PUT    /api/v1/users/{id}      # Update user
DELETE /api/v1/users/{id}      # Delete user

# Sub-resources
GET    /api/v1/users/{id}/orders

# ❌ Wrong - action-oriented
POST   /api/v1/getUser
POST   /api/v1/createUser
POST   /api/v1/deleteUser
```

2. **Consistent Naming** — Use kebab-case for URLs, snake_case for JSON.

```bash
# URL: kebab-case
GET /api/v1/user-profiles/{id}/payment-methods

# JSON: snake_case
{
    "user_profile": {
        "first_name": "John",
        "payment_methods": []
    }
}
```

3. **Plural Resources** — Collection endpoints MUST be plural.

```bash
# ✅ Correct
/api/v1/users
/api/v1/orders
/api/v1/products

# ❌ Wrong
/api/v1/user
/api/v1/order
```

#### Response Format

4. **Standard Response Envelope** — All responses MUST use consistent structure.

```python
# Success response
{
    "success": true,
    "data": {
        "id": "user_123",
        "email": "user@example.com"
    },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2025-01-18T14:30:00Z"
    }
}

# Error response
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid email format",
        "details": [
            {
                "field": "email",
                "message": "Must be a valid email address"
            }
        ]
    },
    "meta": {
        "request_id": "req_abc123",
        "timestamp": "2025-01-18T14:30:00Z"
    }
}
```

5. **HTTP Status Codes** — Use appropriate status codes consistently.

```python
# Success codes
200  # OK - GET, PUT success
201  # Created - POST success
204  # No Content - DELETE success

# Client errors
400  # Bad Request - Invalid input
401  # Unauthorized - Authentication required
403  # Forbidden - Permission denied
404  # Not Found - Resource doesn't exist
409  # Conflict - Resource state conflict
422  # Unprocessable Entity - Validation failed
429  # Too Many Requests - Rate limited

# Server errors
500  # Internal Server Error
502  # Bad Gateway
503  # Service Unavailable
```

6. **Error Codes** — Errors MUST include machine-readable codes.

```python
class ErrorCode(str, Enum):
    # Validation errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    MISSING_FIELD = "MISSING_FIELD"

    # Authentication errors (401)
    AUTH_REQUIRED = "AUTH_REQUIRED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # Authorization errors (403)
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_FORBIDDEN = "RESOURCE_FORBIDDEN"

    # Not found (404)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # Conflict (409)
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    STATE_CONFLICT = "STATE_CONFLICT"

    # Rate limiting (429)
    RATE_LIMITED = "RATE_LIMITED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
```

#### Pagination

7. **Cursor-Based Pagination** — Collections MUST support pagination.

```python
# Request
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTAwfQ

# Response
{
    "success": true,
    "data": [...],
    "pagination": {
        "limit": 20,
        "has_more": true,
        "next_cursor": "eyJpZCI6MTIwfQ",
        "prev_cursor": "eyJpZCI6ODB9"
    }
}
```

#### Filtering and Sorting

8. **Query Parameters** — Filtering MUST use query parameters.

```bash
# Filtering
GET /api/v1/users?status=active&role=admin

# Sorting
GET /api/v1/users?sort=created_at:desc,name:asc

# Field selection
GET /api/v1/users?fields=id,name,email
```

#### Rate Limiting

9. **Rate Limit Headers** — Rate limits MUST be communicated in headers.

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705590000
Retry-After: 60  # On 429 response
```

#### Documentation

10. **OpenAPI Specification** — All APIs MUST have OpenAPI documentation.

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
paths:
  /api/v1/users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### SHOULD (Recommended)

1. **HATEOAS Links** — Responses SHOULD include navigational links.

```python
{
    "data": {
        "id": "user_123",
        "email": "user@example.com"
    },
    "links": {
        "self": "/api/v1/users/user_123",
        "orders": "/api/v1/users/user_123/orders",
        "profile": "/api/v1/users/user_123/profile"
    }
}
```

2. **Request IDs** — All requests SHOULD generate unique IDs.

```python
# Request header
X-Request-ID: req_abc123  # Client-provided or server-generated

# Response includes same ID for tracing
```

3. **Idempotency Keys** — Mutating operations SHOULD support idempotency.

```python
# Request
POST /api/v1/payments
Idempotency-Key: payment_12345

# Server stores result keyed by Idempotency-Key
# Repeated requests return same result
```

4. **Conditional Requests** — Support ETags for caching.

```python
# Response includes ETag
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Subsequent request
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# Server returns 304 Not Modified if unchanged
```

### MAY (Optional)

1. **GraphQL** — For complex querying needs.
2. **Webhooks** — For event-driven integrations.
3. **Batch Endpoints** — For bulk operations.

### MUST NOT (Prohibited)

1. **Never Break Backwards Compatibility** — Without version bump.
2. **Never Return HTML from JSON APIs** — Content-type must match.
3. **Never Use 200 for Errors** — Status codes must reflect outcome.
4. **Never Expose Internal Details** — Stack traces, SQL, internal IDs.

---

## HOW (Reference)

### FastAPI Implementation

```python
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional
from enum import Enum
import uuid

T = TypeVar('T')

class ResponseMeta(BaseModel):
    request_id: str
    timestamp: str

class PaginationInfo(BaseModel):
    limit: int
    has_more: bool
    next_cursor: Optional[str]
    prev_cursor: Optional[str]

class ErrorDetail(BaseModel):
    field: Optional[str]
    message: str

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None
    meta: ResponseMeta
    pagination: Optional[PaginationInfo] = None

# Usage
@app.get("/api/v1/users", response_model=APIResponse[list[User]])
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = None,
    request_id: Optional[str] = Header(None, alias="X-Request-ID")
):
    req_id = request_id or str(uuid.uuid4())

    users, has_more, next_cursor = fetch_users(limit, cursor)

    return APIResponse(
        success=True,
        data=users,
        meta=ResponseMeta(
            request_id=req_id,
            timestamp=datetime.utcnow().isoformat()
        ),
        pagination=PaginationInfo(
            limit=limit,
            has_more=has_more,
            next_cursor=next_cursor,
            prev_cursor=cursor
        )
    )
```

### Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": [
                    {"field": e["loc"][-1], "message": e["msg"]}
                    for e in exc.errors()
                ]
            },
            "meta": {
                "request_id": request.state.request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| OpenAPI validator | Schema completeness | error |
| Spectral | API linting rules | warning |
| Contract tests | Response format | error |
| Custom linter | Naming conventions | warning |

### Escape Hatch

For internal/debug endpoints:

```python
# standard:override api-design-versioning - Internal debug endpoint
@app.get("/internal/debug/cache")
async def debug_cache():
    """Internal endpoint - not versioned, not documented."""
    ...
```

---

## Related Standards

- [DEPRECATION.md](DEPRECATION.md) — API deprecation process
- [ERROR_HANDLING.md](ERROR_HANDLING.md) — Error response format
- [SECURITY.md](SECURITY.md) — API authentication/authorization

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-18 | Initial standard | Claude |
