# Environments

**Secrets in env vars. Settings in files. Environments are isolated.**

---

## The Rule

Use environment variables for secrets and environment-specific values. Never hardcode.

---

## Environment Variables

| Category | Use Env Vars | Examples |
|----------|--------------|----------|
| Secrets | Always | `DATABASE_PASSWORD`, `API_KEY` |
| Connection strings | Always | `DATABASE_URL`, `REDIS_URL` |
| Feature flags | Sometimes | `ENABLE_DEBUG`, `FEATURE_X` |
| Tuning params | Rarely | Usually in config files |

---

## Loading Environment Variables

```python
import os
from dotenv import load_dotenv

# Load .env file (for local development)
load_dotenv()

# Access with explicit defaults or raise
DATABASE_URL = os.environ["DATABASE_URL"]  # Raises if missing
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

---

## Environment Separation

| Environment | Purpose | Config Source |
|-------------|---------|---------------|
| development | Local dev | `.env` + `config/environments/development.yaml` |
| staging | Pre-prod testing | Platform env vars + `staging.yaml` |
| production | Live system | Platform env vars + `production.yaml` |
| test | Automated tests | Test fixtures + `test.yaml` |

---

## .env Files

```bash
# .env (gitignored - local development only)
DATABASE_URL=postgres://user:pass@localhost:5432/dev_db
API_KEY=sk-dev-key-12345
DEBUG=true

# .env.example (committed - shows required vars)
DATABASE_URL=
API_KEY=
DEBUG=false
```

---

## Environment Detection

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

def is_production() -> bool:
    return ENVIRONMENT == "production"

def is_development() -> bool:
    return ENVIRONMENT == "development"
```

---

## Anti-Patterns

```python
# WRONG - Hardcoded secret
DATABASE_URL = "postgres://user:secret@prod-db:5432/app"

# WRONG - Environment in code
if hostname == "prod-server-1":
    use_production_config()

# WRONG - Optional secrets
API_KEY = os.getenv("API_KEY", "default-key")  # No default for secrets!
```

---

## Correct Pattern

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    api_key: str
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            database_url=os.environ["DATABASE_URL"],  # Required - raises
            api_key=os.environ["API_KEY"],  # Required - raises
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
```

---

## UP

[INDEX.md](INDEX.md)
