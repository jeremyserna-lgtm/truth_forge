# Input Validation

**Never trust input. Validate everything at system boundaries.**

---

## The Rule

All data entering the system from external sources MUST be validated before use.

---

## Validation Boundaries

| Boundary | Examples | Trust Level |
|----------|----------|-------------|
| User input | Forms, CLI args, file uploads | NONE |
| API requests | HTTP bodies, query params, headers | NONE |
| External APIs | Third-party responses | LOW |
| Database reads | Previously stored data | MEDIUM |
| Internal calls | Between trusted modules | HIGH |

---

## Validation Pattern

```python
from pydantic import BaseModel, validator, constr
from typing import Annotated

class UserInput(BaseModel):
    """Validated user input with constraints."""

    email: constr(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', max_length=254)
    name: constr(min_length=1, max_length=100)
    age: Annotated[int, Field(ge=0, le=150)]

    @validator('name')
    def sanitize_name(cls, v: str) -> str:
        # Remove any HTML/script injection attempts
        import html
        return html.escape(v.strip())
```

---

## What To Validate

| Input Type | Validations |
|------------|-------------|
| Strings | Length, pattern, encoding, sanitization |
| Numbers | Range, type, precision |
| Emails | Format, domain (optionally) |
| URLs | Protocol whitelist, domain whitelist |
| Files | Type, size, content scanning |
| IDs | Format, existence, authorization |

---

## Anti-Patterns

```python
# WRONG - Direct use of unsanitized input
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# WRONG - Trust external data
external_data = api_response.json()
execute_command(external_data['command'])  # Command injection!

# CORRECT - Validate and sanitize
validated = UserInput(**raw_input)  # Raises ValidationError if invalid
```

---

## OWASP A03 - Injection

Input validation prevents injection attacks:
- SQL Injection
- Command Injection
- XSS (Cross-Site Scripting)
- LDAP Injection

**Every input is a potential attack vector.**

---

## UP

[INDEX.md](INDEX.md)
