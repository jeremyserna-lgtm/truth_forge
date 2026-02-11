# Security

**The Standard** | Every input is untrusted, every boundary is defended, every secret is protected.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Input | Validate all input; sanitize before use |
| Authentication | Multi-factor for sensitive operations |
| Authorization | Principle of least privilege |
| Secrets | Encrypted at rest and in transit |
| Dependencies | Regular vulnerability scanning |
| Audit | Log all security-relevant events |

---

## WHY (Theory)

### Defense in Depth

Security is not a feature; it's a property. It emerges from layers of defense, each assuming the others have failed. No single control is sufficient. Every layer must assume breach.

### The Trust Hierarchy

From 06_LAW: *"Trust flows from identity. Identity must be verified."*

```
┌─────────────────────────────────────────┐
│          Trusted Execution              │
│    (Verified identity, authorized)      │
├─────────────────────────────────────────┤
│        Authentication Boundary          │
│    (Identity verified, not yet authz)   │
├─────────────────────────────────────────┤
│          Untrusted Input                │
│    (Everything from outside)            │
└─────────────────────────────────────────┘
```

---

## WHAT (Specification)

### Security Principles

| Principle | Implementation |
|-----------|----------------|
| Defense in Depth | Multiple independent controls |
| Least Privilege | Minimum necessary permissions |
| Fail Secure | Deny by default on failure |
| Complete Mediation | Check every access |
| Separation of Duties | Critical actions require multiple parties |

### MUST (Required)

#### Input Validation

1. **Validate All Input** — Every input from external sources MUST be validated.

```python
from pydantic import BaseModel, validator, Field
import re

class UserInput(BaseModel):
    email: str = Field(..., max_length=254)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)

    @validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('name')
    def sanitize_name(cls, v):
        # Remove potentially dangerous characters
        return re.sub(r'[<>&"\']', '', v).strip()

# ✅ Correct - validates before use
def create_user(data: dict) -> User:
    validated = UserInput(**data)  # Raises on invalid
    return User.create(validated.dict())

# ❌ Wrong - trusts input directly
def create_user(data: dict) -> User:
    return User.create(data)  # SQL injection, XSS possible
```

2. **Parameterize Queries** — Database queries MUST use parameterized statements.

```python
# ✅ Correct - parameterized
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND status = %s",
    (email, status)
)

# Using ORM
User.objects.filter(email=email, status=status)

# ❌ Wrong - string interpolation (SQL injection)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

3. **Encode Output** — Output MUST be encoded for its context.

```python
from markupsafe import escape
from html import escape as html_escape

# HTML context
def render_user_name(name: str) -> str:
    return f"<span>{escape(name)}</span>"

# JSON context
import json
def api_response(data: dict) -> str:
    return json.dumps(data)  # Automatically escapes

# URL context
from urllib.parse import quote
def build_url(path: str, param: str) -> str:
    return f"/api/{quote(path)}?q={quote(param)}"
```

#### Authentication

4. **Strong Password Requirements** — Passwords MUST meet complexity requirements.

```python
import re
from passlib.hash import argon2

def validate_password(password: str) -> bool:
    """Validate password meets requirements."""
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return argon2.hash(password)

def verify_password(password: str, hash: str) -> bool:
    """Verify password against hash."""
    return argon2.verify(password, hash)
```

5. **Session Security** — Sessions MUST be properly secured.

```python
# Session configuration
SESSION_CONFIG = {
    "cookie_name": "__session",
    "cookie_httponly": True,      # No JavaScript access
    "cookie_secure": True,        # HTTPS only
    "cookie_samesite": "Lax",     # CSRF protection
    "session_lifetime": 3600,     # 1 hour
    "regenerate_on_login": True,  # Prevent fixation
}
```

6. **Rate Limiting** — Authentication endpoints MUST be rate limited.

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=5, period=60)  # 5 attempts per minute
def authenticate(username: str, password: str) -> User | None:
    ...
```

#### Authorization

7. **Explicit Permission Checks** — Every protected operation MUST check permissions.

```python
from functools import wraps
from typing import Callable

def require_permission(permission: str) -> Callable:
    """Decorator to enforce permission check."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user: User, *args, **kwargs):
            if not user.has_permission(permission):
                raise AuthorizationError(f"Missing permission: {permission}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@require_permission("document:delete")
def delete_document(user: User, document_id: str) -> None:
    ...
```

8. **Resource-Level Authorization** — Check access to specific resources, not just actions.

```python
def get_document(user: User, document_id: str) -> Document:
    document = Document.get(document_id)

    # Check resource-level access
    if not document.is_accessible_by(user):
        raise AuthorizationError("Access denied to document")

    return document
```

#### Secrets Management

9. **Never Hardcode Secrets** — Secrets MUST come from secure storage.

```python
# ✅ Correct - from environment/secrets manager
API_KEY = os.environ["API_KEY"]
DB_PASSWORD = secrets_manager.get("database/password")

# ❌ Wrong - hardcoded
API_KEY = "sk-1234567890abcdef"
```

10. **Encrypt Secrets at Rest** — Stored secrets MUST be encrypted.

```python
from cryptography.fernet import Fernet

class SecretStore:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def store(self, name: str, value: str) -> None:
        encrypted = self.cipher.encrypt(value.encode())
        self.db.set(name, encrypted)

    def retrieve(self, name: str) -> str:
        encrypted = self.db.get(name)
        return self.cipher.decrypt(encrypted).decode()
```

11. **Rotate Secrets Regularly** — Secrets MUST have rotation policies.

```python
# Secret rotation schedule
SECRET_ROTATION = {
    "api_keys": "90 days",
    "database_passwords": "90 days",
    "encryption_keys": "365 days",
    "session_keys": "24 hours",
}
```

### SHOULD (Recommended)

1. **Content Security Policy** — Web applications SHOULD implement CSP.

```python
CSP_HEADER = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' api.example.com"
    )
}
```

2. **Security Headers** — HTTP responses SHOULD include security headers.

```python
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
```

3. **Dependency Scanning** — Dependencies SHOULD be scanned for vulnerabilities.

```bash
# Run regularly in CI
pip-audit
safety check
npm audit
```

4. **Penetration Testing** — Applications SHOULD undergo regular security testing.

### MAY (Optional)

1. **Bug Bounty Program** — Public applications may benefit from bounty programs.
2. **Hardware Security Modules** — Critical secrets may use HSMs.
3. **Zero Trust Architecture** — Internal services may implement zero trust.

### MUST NOT (Prohibited)

1. **Never Store Plaintext Passwords** — Always hash with approved algorithms.
2. **Never Disable Security Controls** — Even in development.
3. **Never Trust Client-Side Validation** — Server must re-validate.
4. **Never Log Secrets** — Even "masked" secrets leak information.
5. **Never Use Deprecated Crypto** — MD5, SHA1, DES are prohibited.

---

## HOW (Reference)

### Security Checklist

```markdown
## Pre-Deployment Security Checklist

### Authentication
- [ ] Passwords hashed with Argon2/bcrypt
- [ ] Session tokens are cryptographically random
- [ ] Sessions expire and can be invalidated
- [ ] Rate limiting on auth endpoints
- [ ] MFA available for sensitive accounts

### Authorization
- [ ] Every endpoint checks permissions
- [ ] Resource-level access controls
- [ ] Admin functions require elevated auth
- [ ] Audit log for privilege changes

### Input/Output
- [ ] All input validated
- [ ] SQL uses parameterized queries
- [ ] Output encoded for context
- [ ] File uploads validated and sandboxed

### Secrets
- [ ] No secrets in code or version control
- [ ] Secrets encrypted at rest
- [ ] Rotation policy defined
- [ ] Access to secrets audited

### Infrastructure
- [ ] HTTPS everywhere
- [ ] Security headers configured
- [ ] Dependencies scanned
- [ ] Backups encrypted
```

### Common Vulnerability Prevention

```python
# XSS Prevention
from markupsafe import escape

def safe_render(user_input: str) -> str:
    return f"<div>{escape(user_input)}</div>"

# CSRF Prevention
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# SQL Injection Prevention
from sqlalchemy import text

result = db.execute(
    text("SELECT * FROM users WHERE id = :user_id"),
    {"user_id": user_id}
)

# Path Traversal Prevention
import os

def safe_file_access(filename: str, base_dir: str) -> str:
    # Resolve to absolute path
    requested_path = os.path.abspath(os.path.join(base_dir, filename))

    # Ensure it's within base_dir
    if not requested_path.startswith(os.path.abspath(base_dir)):
        raise SecurityError("Path traversal attempt detected")

    return requested_path
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| bandit | Python security linting | error |
| safety | Dependency vulnerabilities | error |
| git-secrets | Secrets in commits | error |
| SAST tools | Static analysis | warning |
| DAST tools | Dynamic testing | varies |

### CI Configuration

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - name: Security scan
      run: |
        pip install bandit safety
        bandit -r src/
        safety check
```

### Escape Hatch

For security testing only:

```python
# standard:override security-validation - Penetration testing endpoint
# SECURITY WARNING: This endpoint bypasses validation for testing
# Must be disabled in production
@app.route("/test/bypass")
def bypass_endpoint():
    if not settings.TESTING_MODE:
        abort(404)
    ...
```

---

## Related Standards

- [CONFIGURATION.md](CONFIGURATION.md) — Secrets management
- [LOGGING.md](LOGGING.md) — Security event logging
- [ERROR_HANDLING.md](ERROR_HANDLING.md) — Secure error messages

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-18 | Initial standard | Claude |
