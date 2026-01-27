# Errors

**Errors are information. Format them consistently.**

---

## The Rule

All API errors use a consistent response format with actionable information.

---

## Error Response Format

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": [
            {
                "field": "email",
                "message": "Invalid email format"
            }
        ],
        "request_id": "req_abc123"
    }
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| code | Yes | Machine-readable error code |
| message | Yes | Human-readable description |
| details | No | Field-level errors or context |
| request_id | Yes | Correlation for debugging |

---

## Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400/422 | Input validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | No auth provided |
| `AUTHENTICATION_FAILED` | 401 | Invalid credentials |
| `FORBIDDEN` | 403 | No permission |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `CONFLICT` | 409 | State conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected error |

---

## Validation Errors

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": [
            {
                "field": "email",
                "code": "INVALID_FORMAT",
                "message": "Must be a valid email address"
            },
            {
                "field": "age",
                "code": "OUT_OF_RANGE",
                "message": "Must be between 0 and 150"
            }
        ],
        "request_id": "req_abc123"
    }
}
```

---

## Security Considerations

| Principle | Implementation |
|-----------|----------------|
| No stack traces | Never expose in production |
| Generic auth errors | Don't reveal if user exists |
| No internal details | Don't expose database errors |
| Log correlation | Use request_id to find details |

```python
# WRONG - Exposes internals
{"error": "psycopg2.IntegrityError: duplicate key value"}

# RIGHT - Safe for consumers
{"error": {"code": "CONFLICT", "message": "User already exists"}}
```

---

## Implementation

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class APIError:
    code: str
    message: str
    status_code: int
    details: list[dict[str, Any]] | None = None

def error_response(error: APIError, request_id: str) -> dict:
    response = {
        "error": {
            "code": error.code,
            "message": error.message,
            "request_id": request_id,
        }
    }
    if error.details:
        response["error"]["details"] = error.details
    return response
```

---

## Related

Links to [error_handling/](../error_handling/) for internal error handling patterns.

---

## UP

[INDEX.md](INDEX.md)
