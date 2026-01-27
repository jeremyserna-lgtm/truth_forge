# Pipeline Architecture

**The universal pipeline pattern for all data processing.**

---

## The Pattern

```
ADAPTER (config) → HOLD₁ (source) → UNIVERSAL PIPELINE → HOLD₂ (destination)
```

---

## Core Pipeline Structure

```
pipelines/
├── core/                     # THE universal pipeline (one to maintain)
│   ├── stages/
│   │   ├── __init__.py
│   │   ├── stage_0_ingest.py
│   │   ├── stage_1_transform.py
│   │   ├── stage_2_enrich.py
│   │   └── stage_3_output.py
│   ├── runner.py
│   └── base_config.py
│
└── adapters/                 # Project-specific configurations
    └── {project_name}/
        ├── config.yaml
        └── hooks.py          # Optional custom hooks
```

---

## Core Runner

```python
# pipelines/core/runner.py
def run_pipeline(adapter: str):
    config = load_adapter(f"adapters/{adapter}/config.yaml")

    data = stage_0.ingest(config.source)
    data = stage_1.transform(data, config)
    data = stage_2.enrich(data, config)
    stage_3.output(data, config.destination)
```

---

## Adapter Configuration

```yaml
# pipelines/adapters/claude_code/config.yaml
name: claude_code
source:
  type: jsonl
  path: projects/claude_code/data/raw/
destination:
  type: duckdb
  path: data/output/knowledge.duckdb
  table: claude_code_atoms
stages:
  transform:
    extract_fields: [content, metadata, timestamp]
  enrich:
    embedding_model: text-embedding-3-small
```

---

## Running Pipelines

```bash
# Run pipeline for a specific project
python -m pipelines.core.runner --adapter claude_code
```

---

## NEVER

```
✗ Duplicate pipeline code (use adapters)
✗ Put pipeline logic in adapters
✗ Hardcode paths in core pipeline
```

## ALWAYS

```
✓ One universal pipeline in core/
✓ Configuration in adapters/
✓ Follow HOLD:AGENT:HOLD pattern
```

---

## UP

[INDEX.md](INDEX.md)
