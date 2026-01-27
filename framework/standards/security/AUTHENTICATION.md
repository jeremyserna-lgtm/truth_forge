# Authentication

**Verify identity before granting access. Never roll your own crypto.**

---

## The Rule

Use established authentication libraries and patterns. Never implement authentication from scratch.

---

## Authentication Methods

| Method | Use Case | Security Level |
|--------|----------|----------------|
| API Keys | Service-to-service, simple apps | LOW |
| JWT | Stateless auth, microservices | MEDIUM |
| OAuth 2.0 | Third-party integration | HIGH |
| Session + Cookie | Traditional web apps | MEDIUM |
| mTLS | Service mesh, high-security | HIGH |

---

## Password Requirements

If storing passwords (prefer OAuth when possible):

```python
from passlib.context import CryptContext

# Use bcrypt or argon2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

| Requirement | Value |
|-------------|-------|
| Minimum length | 12 characters |
| Hashing | bcrypt or argon2id |
| Salt | Automatic (built into bcrypt) |
| Never store | Plaintext passwords |

---

## JWT Best Practices

```python
from datetime import datetime, timedelta
import jwt

def create_token(user_id: str, secret: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),  # Short expiry
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=["HS256"])
```

| Requirement | Value |
|-------------|-------|
| Algorithm | HS256 minimum, RS256 preferred |
| Expiry | Short-lived (1 hour or less) |
| Refresh | Use refresh tokens for longer sessions |
| Storage | HttpOnly cookies or secure storage |

---

## Anti-Patterns

```python
# WRONG - Plaintext password storage
user.password = request.password

# WRONG - Weak hashing
user.password = hashlib.md5(password).hexdigest()

# WRONG - No expiry on tokens
token = jwt.encode({"user": user_id}, secret)  # Never expires!

# WRONG - Rolling your own auth
def my_custom_auth(username, password):  # Don't do this
    ...
```

---

## OWASP A07 - Authentication Failures

Authentication failures enable:
- Credential stuffing
- Brute force attacks
- Session hijacking

**Use established libraries. Never roll your own.**

---

## UP

[INDEX.md](INDEX.md)
