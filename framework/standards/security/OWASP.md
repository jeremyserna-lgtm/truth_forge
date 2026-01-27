# OWASP Top 10

**Industry-standard awareness of critical security risks.**

---

## The Rule

Every developer MUST be aware of OWASP Top 10. Code MUST NOT introduce these vulnerabilities.

---

## OWASP Top 10 (2025)

| Rank | Risk | Our Standard |
|------|------|--------------|
| A01 | Broken Access Control | Authorization checks on every endpoint |
| A02 | Cryptographic Failures | [SECRETS.md](SECRETS.md), use TLS, proper hashing |
| A03 | Injection | [INPUT_VALIDATION.md](INPUT_VALIDATION.md), parameterized queries |
| A04 | Insecure Design | Threat modeling, security reviews |
| A05 | Security Misconfiguration | Secure defaults, no debug in prod |
| A06 | Vulnerable Components | Dependency scanning, updates |
| A07 | Authentication Failures | [AUTHENTICATION.md](AUTHENTICATION.md) |
| A08 | Software Data Integrity | Verify downloads, sign artifacts |
| A09 | Logging Failures | Structured logging, no secrets in logs |
| A10 | SSRF | Validate URLs, whitelist domains |

---

## Quick Reference

### A01: Broken Access Control

```python
# WRONG - No authorization check
@app.get("/users/{user_id}")
def get_user(user_id: str):
    return db.get_user(user_id)  # Anyone can access any user!

# CORRECT - Authorization check
@app.get("/users/{user_id}")
def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized")
    return db.get_user(user_id)
```

### A03: Injection

```python
# WRONG - SQL injection
query = f"SELECT * FROM users WHERE id = '{user_id}'"

# CORRECT - Parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### A05: Security Misconfiguration

```python
# WRONG - Debug in production
app = FastAPI(debug=True)  # Exposes stack traces!

# CORRECT
app = FastAPI(debug=os.getenv("ENV") == "development")
```

### A09: Logging Failures

```python
# WRONG - Logging sensitive data
logger.info(f"User {user.email} logged in with password {password}")

# CORRECT - Structured, safe logging
logger.info("User logged in", extra={"user_id": user.id})
```

---

## Security Review Checklist

- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] All queries parameterized
- [ ] Authorization on every endpoint
- [ ] No debug mode in production
- [ ] Dependencies scanned for vulnerabilities
- [ ] TLS for all external communication
- [ ] No sensitive data in logs

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [ASVS](https://owasp.org/www-project-application-security-verification-standard/)

---

## UP

[INDEX.md](INDEX.md)
