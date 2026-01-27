# Dead Letter Queue (DLQ)

**Never drop data. Failed records go to DLQ for later analysis and reprocessing.**

---

## Implementation

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, Optional

@dataclass
class DeadLetterRecord:
    """A record that failed processing."""
    original_record: Dict[str, Any]
    error_type: str
    error_message: str
    traceback: str
    pipeline_stage: str
    attempt_count: int
    first_failure: str
    last_failure: str
    record_id: Optional[str] = None

class DeadLetterQueue:
    """Quarantine for failed records. Never lose data."""

    def __init__(self, dlq_path: Path, pipeline_name: str) -> None:
        self.dlq_path = dlq_path / f"{pipeline_name}_dlq.jsonl"
        self.dlq_path.parent.mkdir(parents=True, exist_ok=True)

    def send(
        self,
        record: Dict[str, Any],
        error: Exception,
        stage: str,
        attempt_count: int = 1,
    ) -> None:
        """Send a failed record to the DLQ."""
        import traceback

        now = datetime.now(timezone.utc).isoformat()
        dlq_record = {
            "original_record": record,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "pipeline_stage": stage,
            "attempt_count": attempt_count,
            "first_failure": now,
            "last_failure": now,
            "record_id": record.get("entity_id") or record.get("id"),
            "dlq_timestamp": now,
        }

        with open(self.dlq_path, "a") as f:
            f.write(json.dumps(dlq_record) + "\n")

    def count(self) -> int:
        """Count records in DLQ."""
        if not self.dlq_path.exists():
            return 0
        with open(self.dlq_path) as f:
            return sum(1 for _ in f)

    def replay(self, processor_func) -> tuple[int, int]:
        """Attempt to reprocess DLQ records."""
        if not self.dlq_path.exists():
            return 0, 0

        success_count = 0
        failure_count = 0
        remaining = []

        with open(self.dlq_path) as f:
            for line in f:
                dlq_record = json.loads(line)
                try:
                    processor_func(dlq_record["original_record"])
                    success_count += 1
                except Exception:
                    dlq_record["attempt_count"] += 1
                    dlq_record["last_failure"] = datetime.now(timezone.utc).isoformat()
                    remaining.append(dlq_record)
                    failure_count += 1

        # Rewrite DLQ with remaining failures
        with open(self.dlq_path, "w") as f:
            for record in remaining:
                f.write(json.dumps(record) + "\n")

        return success_count, failure_count
```

---

## DLQ Monitoring

```python
def check_dlq_health(dlq: DeadLetterQueue, threshold: int = 100) -> dict:
    """Check DLQ health and alert if threshold exceeded."""
    count = dlq.count()
    status = "healthy" if count < threshold else "warning" if count < threshold * 2 else "critical"

    return {
        "dlq_count": count,
        "threshold": threshold,
        "status": status,
        "requires_attention": count >= threshold,
    }
```

---

## The Rule

**Every batch pipeline MUST have a DLQ.** Failed records are quarantined, not dropped.

---

## UP

[error_handling/INDEX.md](INDEX.md)
