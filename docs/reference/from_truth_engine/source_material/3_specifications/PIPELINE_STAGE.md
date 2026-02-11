# Pipeline Stage Contract

**What you put in a pipeline stage.**

*A pipeline stage is a script that is part of a multi-stage data pipeline. It inherits all Script obligations.*

---

## Required Imports

```python
from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_correlation_ids,
    track_cost,
    write_event,
)
from architect_central_services.core.shared import SessionCostLimiter

logger = get_logger(__name__)
run_id = get_current_run_id()
```

---

## Required Structure

### Naming

```
{source}_{type}_stage_{N}.py
```

Examples:
- `text_messages_stage_1.py`
- `chatgpt_web_ingestion_stage_5.py`

### Location

```
pipelines/{source}/scripts/stage_{N}/
```

---

## Required Events

### On Stage Start

```python
write_event(
    source=f"{pipeline_name}_stage_{stage}",
    event_type="stage_start",
    content={"pipeline": pipeline_name, "stage": stage, "config": config}
)
```

### On Stage End

```python
write_event(
    source=f"{pipeline_name}_stage_{stage}",
    event_type="stage_end",
    content={
        "pipeline": pipeline_name,
        "stage": stage,
        "status": "success",
        "items_processed": count,
        "items_failed": failed,
        "items_skipped": skipped
    }
)
```

---

## Template

```python
#!/usr/bin/env python3
"""
Stage {N}: [Description of what this stage does]

Pipeline: {source}
Input: [What this stage reads from]
Output: [What this stage writes to]
"""

import sys
import traceback
from architect_central_services import (
    get_logger,
    get_current_run_id,
    track_cost,
    write_event,
)
from architect_central_services.core.shared import SessionCostLimiter

logger = get_logger(__name__)
run_id = get_current_run_id()

PIPELINE_NAME = "my_pipeline"
STAGE = 1
MAX_COST_USD = 5.0


def main():
    """Main entry point."""
    cost_limiter = SessionCostLimiter(
        max_cost_usd=MAX_COST_USD,
        pipeline_name=f"{PIPELINE_NAME}_stage_{STAGE}",
        run_id=run_id,
        abort_on_exceed=True
    )

    write_event(
        f"{PIPELINE_NAME}_stage_{STAGE}",
        "stage_start",
        {"pipeline": PIPELINE_NAME, "stage": STAGE}
    )

    try:
        # Read from previous stage or source
        input_data = read_input()

        # Process
        processed = 0
        failed = 0
        skipped = 0

        for item in input_data:
            try:
                process_item(item)
                processed += 1
            except Exception as e:
                logger.error(f"Failed to process item: {e}")
                failed += 1

        # Write to next stage
        write_output(results)

        write_event(
            f"{PIPELINE_NAME}_stage_{STAGE}",
            "stage_end",
            {
                "status": "success",
                "items_processed": processed,
                "items_failed": failed,
                "items_skipped": skipped
            }
        )

    except Exception as e:
        write_event(
            f"{PIPELINE_NAME}_stage_{STAGE}",
            "error",
            {"error": str(e), "traceback": traceback.format_exc()}
        )
        raise


if __name__ == "__main__":
    main()
```

---

## Checklist

```
[ ] All Script obligations met
[ ] Named correctly: {source}_{type}_stage_{N}.py
[ ] Located correctly: pipelines/{source}/scripts/stage_{N}/
[ ] Has SessionCostLimiter with max_cost_usd
[ ] Writes stage_start event
[ ] Writes stage_end event with metrics
[ ] Reports: items_processed, items_failed, items_skipped
[ ] Reads from correct input (previous stage or source)
[ ] Writes to correct output (next stage or final)
```

---

## Writes To

`~/.primitive_engine/pipeline_runs.jsonl`

---

## The Sentence

| WHO | DOES | TO | HOW |
|-----|------|----|-----|
| Pipeline stage | writes | stage events | to pipeline_runs.jsonl via write_event() |

---

*Derived from [THE_ENTITY_CONTRACTS.md](../THE_ENTITY_CONTRACTS.md)*
