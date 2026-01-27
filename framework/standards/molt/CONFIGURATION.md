# Molt Configuration

**Layer**: Specifics (NOT-ME) - molt.yaml specification

---

## Configuration File

Molt uses `molt.yaml` in the project root (or specified path).

### Location Priority

1. `--config` flag (explicit)
2. `./molt.yaml` (current directory)
3. `{project_root}/molt.yaml` (project root)
4. `~/.config/truth_forge/molt.yaml` (user default)

---

## Schema

```yaml
# molt.yaml - Molt Configuration
# Version: 1.0.0

# Organism identity
organism:
  name: truth_forge
  type: genesis  # genesis | offspring

# Source configurations
sources:
  # Each source defines a molt mapping
  - name: technical
    source: Truth_Engine/docs/04_technical
    destination: docs/technical
    archive: Truth_Engine/docs/archive
    patterns:
      - "*.md"
      - "**/*.md"
    exclude:
      - "**/archive/**"
      - "**/.git/**"

  - name: business
    source: Truth_Engine/docs/03_business
    destination: docs/business
    archive: Truth_Engine/docs/archive
    patterns:
      - "*.md"

# Archive settings
archive:
  # Date format for batch folders
  date_format: "%Y_%m_%d"
  # Index file name
  index_file: INDEX.md
  # Preserve relative structure
  preserve_structure: true

# Stub settings
stub:
  # Stub template (supports {title}, {dest_path}, {archive_path}, {date})
  template: |
    # {title}

    > **MOVED**: This document has been molted to truth_forge.
    >
    > **New Location**: [{dest_name}]({dest_path})
    >
    > **Archive**: [{archive_name}]({archive_path})
    >
    > **Molted On**: {date}

# Verification settings
verification:
  # Maximum stub size (lines)
  max_stub_lines: 20
  # Required stub markers
  required_markers:
    - "**MOVED**"
    - "**New Location**"
    - "**Archive**"
    - "**Molted On**"

# Tracking settings
tracking:
  # Track molt history
  enabled: true
  # History file location
  history_file: .molt/history.jsonl
```

---

## Minimal Configuration

```yaml
organism:
  name: my_project

sources:
  - name: docs
    source: old_location/docs
    destination: new_location/docs
```

All other settings use defaults.

---

## Configuration Validation

```bash
# Validate configuration
python -m truth_forge.molt config validate

# Show resolved configuration
python -m truth_forge.molt config show
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MOLT_CONFIG` | Config file path | `./molt.yaml` |
| `MOLT_DRY_RUN` | Force dry run | `false` |
| `MOLT_VERBOSE` | Verbose output | `false` |

---

## UP

[INDEX.md](INDEX.md) - Molt Standard hub
