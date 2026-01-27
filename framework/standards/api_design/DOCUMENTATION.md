# Documentation

**Undocumented APIs don't exist. Document with OpenAPI.**

---

## The Rule

All APIs must have OpenAPI (Swagger) documentation that is auto-generated and always current.

---

## OpenAPI Requirements

| Requirement | Purpose |
|-------------|---------|
| Title and version | API identification |
| Server URLs | Where to call |
| All endpoints | Complete coverage |
| Request/response schemas | Data contracts |
| Authentication | How to authenticate |
| Error responses | Expected failures |

---

## Minimal OpenAPI Example

```yaml
openapi: 3.0.3
info:
  title: Users API
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      required: [id, email]
      properties:
        id:
          type: string
        email:
          type: string
          format: email
```

---

## Auto-Generation (FastAPI)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Users API",
    version="1.0.0",
    description="User management API"
)

class User(BaseModel):
    """User resource."""
    id: str
    email: str
    name: str | None = None

@app.get("/users", response_model=list[User])
async def list_users() -> list[User]:
    """List all users.

    Returns a list of all registered users.
    """
    ...
```

Docs auto-generated at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Documentation Checklist

| Item | Required |
|------|----------|
| Endpoint description | Yes |
| Request body schema | Yes (if applicable) |
| Response schemas | Yes |
| Error responses | Yes |
| Authentication requirements | Yes |
| Example requests/responses | Recommended |
| Rate limiting info | Recommended |

---

## Keeping Docs Current

| Approach | How |
|----------|-----|
| Code-first | Generate from type hints (FastAPI) |
| Contract-first | Write OpenAPI, generate code |
| Validation | CI check that docs match implementation |

```bash
# CI validation
openapi-spec-validator api/openapi.yaml
```

---

## Anti-Patterns

```python
# WRONG - No docstring
@app.get("/users")
async def get_users():
    pass

# WRONG - Outdated manual docs
# Documentation says POST, code uses PUT

# WRONG - No error documentation
# "What does 422 mean? What's in the response?"
```

---

## UP

[INDEX.md](INDEX.md)
