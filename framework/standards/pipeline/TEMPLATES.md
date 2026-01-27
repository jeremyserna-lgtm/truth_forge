# Pipeline Templates

**Stage script templates and pipeline configuration.**

**Status**: ACTIVE
**Owner**: Framework
**Parent**: [INDEX.md](INDEX.md)

---

## Stage Script Template

Every stage script MUST follow this template:

```python
#!/usr/bin/env python3
"""
Stage {N}: {Stage Name} - {Pipeline Name} Pipeline

HOLD₁ ({input_description}) → AGENT ({process_description}) → HOLD₂ ({output_description})

🧠 STAGE FIVE GROUNDING
This stage exists to {primary_purpose}.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))

from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker

logger = get_logger(__name__)

PIPELINE_NAME = "{pipeline_name}"
STAGE_NUMBER = {N}
STAGE_NAME = "{stage_name}"
HOLD_1 = "{project}.{dataset}.{pipeline}_stage_{N-1}"
HOLD_2 = "{project}.{dataset}.{pipeline}_stage_{N}"
BATCH_SIZE = 1000


def read_from_hold_1(client) -> List[Dict[str, Any]]:
    """HOLD₁: Read input data (batch)."""
    query = f"""
    SELECT * FROM `{HOLD_1}`
    WHERE entity_id NOT IN (SELECT entity_id FROM `{HOLD_2}`)
    LIMIT {BATCH_SIZE}
    """
    return [dict(row) for row in client.query(query).result()]


def process_batch(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """AGENT: Transform data."""
    return [transform_record(r) for r in data]


def write_to_hold_2(client, data: List[Dict[str, Any]]) -> None:
    """HOLD₂: Write output (batch)."""
    if not data:
        return
    table_ref = client.get_table(HOLD_2)
    errors = client.insert_rows_json(table_ref, data)
    if errors:
        raise RuntimeError(f"Insert errors: {errors}")


def main():
    """Main execution following THE PATTERN."""
    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=STAGE_NUMBER,
        run_id=run_id,
    ) as tracker:
        client = get_bigquery_client()
        total = 0

        while True:
            data = read_from_hold_1(client)
            if not data:
                break
            output = process_batch(data)
            write_to_hold_2(client, output)
            total += len(output)

        return 0


if __name__ == "__main__":
    exit(main())
```

---

## Pipeline Configuration

Every pipeline MUST have a `pipeline_config.yaml`:

```yaml
pipeline:
  name: pipeline_name
  version: 1.0.0
  source_type: jsonl

  # Cost controls
  cost_limit_per_stage_usd: 5.0
  cost_limit_total_usd: 50.0

  # Execution (BATCH ONLY)
  batch_size: 1000
  parallel_workers: 4
  timeout_minutes: 60

stages:
  0:
    name: assessment
    script: scripts/stage_0/pipeline_stage_0.py
    hold_1: local files
    hold_2: assessment report

  3:
    name: validation
    script: scripts/stage_3/pipeline_stage_3.py
    hold_1: spine.pipeline_stage_2
    hold_2: spine.pipeline_stage_3
    # THE GATE requirements
    gate_validation: true
    identity_service: true
```

---

## Implementation Checklist

### Before Starting

- [ ] Review source data format
- [ ] Identify entity levels (L1, L3, L5, L8)
- [ ] Plan stage sequence
- [ ] Set up pipeline folder structure

### Per Stage

- [ ] Create script following template
- [ ] Define HOLD_1 and HOLD_2 explicitly
- [ ] Implement batch loading
- [ ] Add PipelineTracker
- [ ] Write unit tests

### Stage 3 (THE GATE) Specific

- [ ] Import identity_service
- [ ] Generate entity_ids via standard method
- [ ] Register all IDs
- [ ] Validate 32-char entity_ids

### Final Checklist

- [ ] All stages pass quality gates
- [ ] Pipeline tracker data in monitoring
- [ ] Stage Five Grounding in all scripts
- [ ] Documentation complete

---

## Convergence

### Bottom-Up Validation

This document requires:
- [INDEX.md](INDEX.md) - Parent standard
- [CORE_PATTERN.md](CORE_PATTERN.md) - HOLD:AGENT:HOLD

### Top-Down Validation

This document is shaped by:
- [04_ARCHITECTURE](../../04_ARCHITECTURE.md) - HOLD:AGENT:HOLD
- [code_quality/](../code_quality/) - Code quality requirements

---

*Template. Configure. Execute.*
