# Files

**YAML for config. TOML for Python projects. Never JSON.**

---

## The Rule

Use human-readable config formats that support comments.

---

## Format Selection

| Format | Use For | Why |
|--------|---------|-----|
| YAML | Application config | Comments, hierarchical, readable |
| TOML | Python project config | PEP 518, pyproject.toml |
| JSON | Never for config | No comments, verbose |
| INI | Legacy only | Limited nesting |

---

## YAML Config Example

```yaml
# config/base/settings.yaml
# Application settings - base configuration

database:
  pool_size: 5
  timeout_seconds: 30
  # Retry settings for transient failures
  retry:
    max_attempts: 3
    backoff_multiplier: 2

logging:
  level: INFO
  format: structured
  # See logging/ standard for format details

features:
  # Feature flags - can be overridden per environment
  enable_caching: true
  enable_metrics: true
```

---

## TOML Config Example

```toml
# pyproject.toml
[project]
name = "truth_forge"
version = "0.1.0"
description = "The genesis framework"
requires-python = ">=3.11"

[tool.mypy]
strict = true

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## Config File Structure

```
config/
├── base/
│   └── settings.yaml      # Shared defaults
├── environments/
│   ├── development.yaml   # Dev overrides
│   ├── staging.yaml       # Staging overrides
│   └── production.yaml    # Prod overrides
└── local/                 # Gitignored
    └── settings.yaml      # Personal overrides
```

---

## Loading YAML

```python
from pathlib import Path
import yaml

def load_config(environment: str) -> dict:
    config_dir = Path("config")

    # Load base
    base = yaml.safe_load((config_dir / "base/settings.yaml").read_text())

    # Load environment-specific
    env_file = config_dir / f"environments/{environment}.yaml"
    if env_file.exists():
        env_config = yaml.safe_load(env_file.read_text())
        base = deep_merge(base, env_config)

    # Load local overrides
    local_file = config_dir / "local/settings.yaml"
    if local_file.exists():
        local_config = yaml.safe_load(local_file.read_text())
        base = deep_merge(base, local_config)

    return base
```

---

## Anti-Patterns

```json
// WRONG - JSON config (no comments)
{
    "database": {
        "pool_size": 5
    }
}
```

```yaml
# WRONG - Secrets in config files
database:
  password: "super-secret-password"  # Use env vars!
```

---

## UP

[INDEX.md](INDEX.md)
