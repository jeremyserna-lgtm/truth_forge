# Logger Configuration

**Standard configurations for Python logging.**

---

## Standard Library Configuration

```python
# logging_config.py
import logging
import logging.config
import json
from datetime import datetime, timezone

class StructuredFormatter(logging.Formatter):
    """JSON formatter with standard fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id

        # Add any extra fields passed to the logger
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith('_'):
                log_entry[key] = value

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {"()": StructuredFormatter},
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",  # Human-readable for dev
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "structured",  # JSON for production
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console", "file"]}
    }
}

def configure_logging():
    """Initialize logging with standard configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
```

---

## structlog Configuration (Preferred)

```python
# structlog_config.py
import structlog

def configure_structlog(json_logs: bool = True) -> None:
    """Configure structlog for structured logging.

    Args:
        json_logs: True for JSON output (production), False for console (dev).
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(10),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

---

## Escape Hatch

For debugging scenarios requiring temporary verbose logging:

```python
# standard:override logging-level - Temporary debug logging for incident #123
logging.getLogger('module').setLevel(logging.DEBUG)
```

---

## UP

[logging/INDEX.md](INDEX.md)
