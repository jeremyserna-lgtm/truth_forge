# Secrets Management

**Never hardcode secrets. Never commit secrets. Never log secrets.**

---

## The Rule

Secrets MUST be externalized from code and configuration files.

---

## Secret Types

| Secret | Example | Storage |
|--------|---------|---------|
| API Keys | `sk-abc123...` | Environment variable |
| Database credentials | `postgres://user:pass@...` | Environment variable |
| JWT signing key | Random 256-bit key | Secret manager |
| Service account JSON | GCP credentials | Secret manager |
| Encryption keys | AES keys | Key management service |

---

## Environment Variables

```python
import os
from dotenv import load_dotenv

# Load from .env file (gitignored)
load_dotenv()

# Access secrets from environment
DATABASE_URL = os.environ["DATABASE_URL"]  # Raises if missing
API_KEY = os.getenv("API_KEY", "")  # Returns default if missing
```

---

## .gitignore Requirements

```gitignore
# MUST be gitignored
.env
.env.*
*.pem
*.key
*credentials*.json
config/local/
secrets/
```

---

## Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

---

## Anti-Patterns

```python
# WRONG - Hardcoded secret
API_KEY = "sk-abc123secret456"

# WRONG - Secret in committed config
# config/settings.yaml
# api_key: sk-abc123secret456

# WRONG - Secret in logs
logger.info(f"Connecting with key: {api_key}")

# WRONG - Secret in error message
raise ValueError(f"Auth failed for key {api_key}")
```

---

## Correct Pattern

```python
# config/local/.env (gitignored)
DATABASE_URL=postgres://user:pass@host/db
API_KEY=sk-abc123...

# code
import os
from dotenv import load_dotenv

load_dotenv("config/local/.env")

DATABASE_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ["API_KEY"]

# Logging - never log secrets
logger.info("Connecting to database", extra={
    "host": urlparse(DATABASE_URL).hostname,  # OK - just hostname
    # NOT: "url": DATABASE_URL  # WRONG - contains password
})
```

---

## OWASP A02 - Cryptographic Failures

Exposed secrets enable:
- Unauthorized API access
- Database breaches
- Lateral movement

**Secrets are the keys to the kingdom. Guard them.**

---

## UP

[INDEX.md](INDEX.md)
